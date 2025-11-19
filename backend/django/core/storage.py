"""
S3/MinIO Object Storage Integration
ENTERPRISE PATTERN: Artifact storage for generated timetables

Stores PDF, ICS, CSV, and Excel exports in object storage instead of filesystem.

**Supported Backends:**
- AWS S3
- MinIO (S3-compatible, self-hosted)
- Google Cloud Storage (via S3 compatibility)
- Azure Blob Storage (via S3 compatibility)
"""
import io
import logging
import os
from datetime import datetime, timedelta
from typing import BinaryIO, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class ObjectStorageClient:
    """
    ENTERPRISE PATTERN: Unified object storage interface

    Supports both AWS S3 and MinIO (self-hosted S3-compatible storage).
    """

    def __init__(self):
        # Read from environment
        self.storage_backend = os.getenv("STORAGE_BACKEND", "s3")  # "s3" or "minio"
        self.bucket_name = os.getenv("STORAGE_BUCKET", "timetable-artifacts")

        # S3/MinIO configuration
        self.endpoint_url = os.getenv(
            "STORAGE_ENDPOINT_URL"
        )  # For MinIO: http://localhost:9000
        self.access_key = os.getenv("STORAGE_ACCESS_KEY")
        self.secret_key = os.getenv("STORAGE_SECRET_KEY")
        self.region = os.getenv("STORAGE_REGION", "us-east-1")

        # Initialize client
        self.client = self._init_client()

        # Ensure bucket exists
        self._ensure_bucket_exists()

    def _init_client(self):
        """Initialize boto3 S3 client."""
        config = {
            "aws_access_key_id": self.access_key,
            "aws_secret_access_key": self.secret_key,
            "region_name": self.region,
        }

        # MinIO requires endpoint_url
        if self.endpoint_url:
            config["endpoint_url"] = self.endpoint_url

        return boto3.client("s3", **config)

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' exists")
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                logger.info(f"Creating bucket '{self.bucket_name}'...")
                self.client.create_bucket(Bucket=self.bucket_name)

                # Set bucket lifecycle (auto-delete old artifacts after 90 days)
                lifecycle_config = {
                    "Rules": [
                        {
                            "ID": "DeleteOldArtifacts",
                            "Status": "Enabled",
                            "Expiration": {"Days": 90},
                            "Prefix": "",
                        }
                    ]
                }
                self.client.put_bucket_lifecycle_configuration(
                    Bucket=self.bucket_name, LifecycleConfiguration=lifecycle_config
                )
            else:
                logger.error(f"Failed to check bucket: {e}")

    def upload_artifact(
        self,
        job_id: str,
        organization_id: str,
        file_content: bytes,
        file_type: str,  # "pdf", "ics", "csv", "xlsx"
        variant_id: Optional[str] = None,
    ) -> str:
        """
        Upload timetable artifact to object storage.

        Args:
            job_id: Generation job identifier
            organization_id: Organization identifier (for multi-tenant isolation)
            file_content: Binary file content
            file_type: File type extension
            variant_id: Optional variant identifier

        Returns:
            S3 object key (path)
        """
        try:
            # Build object key with hierarchical structure
            timestamp = datetime.utcnow().strftime("%Y/%m/%d")
            filename = f"{job_id}_variant_{variant_id}" if variant_id else job_id
            object_key = f"organizations/{organization_id}/timetables/{timestamp}/{filename}.{file_type}"

            # Determine content type
            content_type_map = {
                "pdf": "application/pdf",
                "ics": "text/calendar",
                "csv": "text/csv",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
            content_type = content_type_map.get(file_type, "application/octet-stream")

            # Upload to S3/MinIO
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_content,
                ContentType=content_type,
                Metadata={
                    "job_id": job_id,
                    "organization_id": organization_id,
                    "variant_id": variant_id or "",
                    "uploaded_at": datetime.utcnow().isoformat(),
                },
            )

            logger.info(f"Uploaded artifact: {object_key} ({len(file_content)} bytes)")

            return object_key

        except ClientError as e:
            logger.error(f"Failed to upload artifact: {e}", exc_info=True)
            raise

    def download_artifact(self, object_key: str) -> bytes:
        """
        Download artifact from object storage.

        Args:
            object_key: S3 object key (returned from upload_artifact)

        Returns:
            Binary file content
        """
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=object_key)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"Failed to download artifact {object_key}: {e}")
            raise

    def generate_presigned_url(self, object_key: str, expiration: int = 3600) -> str:
        """
        Generate temporary signed URL for artifact download.

        Args:
            object_key: S3 object key
            expiration: URL expiration in seconds (default: 1 hour)

        Returns:
            Presigned URL (valid for 1 hour by default)
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_key},
                ExpiresIn=expiration,
            )

            logger.debug(
                f"Generated presigned URL for {object_key} (expires in {expiration}s)"
            )

            return url

        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise

    def delete_artifact(self, object_key: str) -> None:
        """Delete artifact from object storage."""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_key)
            logger.info(f"Deleted artifact: {object_key}")
        except ClientError as e:
            logger.error(f"Failed to delete artifact {object_key}: {e}")
            raise

    def list_artifacts(self, organization_id: str, prefix: str = "") -> list:
        """
        List all artifacts for an organization.

        Args:
            organization_id: Organization identifier
            prefix: Optional prefix filter

        Returns:
            List of object keys
        """
        try:
            prefix_full = f"organizations/{organization_id}/timetables/{prefix}"

            response = self.client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix_full
            )

            if "Contents" not in response:
                return []

            return [obj["Key"] for obj in response["Contents"]]

        except ClientError as e:
            logger.error(f"Failed to list artifacts: {e}")
            raise


# Singleton instance
_storage_client = None


def get_storage_client() -> ObjectStorageClient:
    """Get singleton storage client instance."""
    global _storage_client
    if _storage_client is None:
        _storage_client = ObjectStorageClient()
    return _storage_client
