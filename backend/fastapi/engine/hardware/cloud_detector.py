"""
Cloud and Distributed Environment Detection
Detects AWS, GCP, Azure, Kubernetes, Docker Swarm
Following Google/Meta standards: One file = Cloud detection only
"""
import logging
import subprocess
import os
from typing import Dict, List

logger = logging.getLogger(__name__)


def detect_aws() -> bool:
    """Check if running on AWS EC2 instance"""
    try:
        result = subprocess.run(
            ['curl', '-s', '--max-time', '2', 
             'http://169.254.169.254/latest/meta-data/instance-id'],
            capture_output=True,
            text=True,
            timeout=3
        )
        if result.returncode == 0 and result.stdout.strip():
            logger.info("[Cloud] Detected AWS EC2 instance")
            return True
    except Exception as e:
        logger.debug(f"AWS detection failed: {e}")
    
    return False


def detect_gcp() -> bool:
    """Check if running on Google Cloud Platform"""
    try:
        result = subprocess.run(
            ['curl', '-s', '--max-time', '2',
             'http://metadata.google.internal/computeMetadata/v1/instance/id',
             '-H', 'Metadata-Flavor: Google'],
            capture_output=True,
            text=True,
            timeout=3
        )
        if result.returncode == 0 and result.stdout.strip():
            logger.info("[Cloud] Detected Google Cloud Platform instance")
            return True
    except Exception as e:
        logger.debug(f"GCP detection failed: {e}")
    
    return False


def detect_azure() -> bool:
    """Check if running on Microsoft Azure"""
    try:
        result = subprocess.run(
            ['curl', '-s', '--max-time', '2',
             'http://169.254.169.254/metadata/instance?api-version=2021-02-01',
             '-H', 'Metadata: true'],
            capture_output=True,
            text=True,
            timeout=3
        )
        if result.returncode == 0 and result.stdout.strip():
            logger.info("[Cloud] Detected Microsoft Azure instance")
            return True
    except Exception as e:
        logger.debug(f"Azure detection failed: {e}")
    
    return False


def detect_cloud_provider() -> str:
    """
    Detect which cloud provider we're running on
    Returns 'AWS', 'GCP', 'Azure', or None
    """
    if detect_aws():
        return 'AWS'
    elif detect_gcp():
        return 'GCP'
    elif detect_azure():
        return 'Azure'
    else:
        return None


def detect_kubernetes() -> bool:
    """Check if running in Kubernetes cluster"""
    if 'KUBERNETES_SERVICE_HOST' in os.environ:
        logger.info("[Distributed] Detected Kubernetes cluster")
        return True
    return False


def detect_docker_swarm() -> bool:
    """Check if running in Docker Swarm"""
    try:
        result = subprocess.run(
            ['docker', 'node', 'ls'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info("[Distributed] Detected Docker Swarm")
            return True
    except Exception as e:
        logger.debug(f"Docker Swarm detection failed: {e}")
    
    return False


def detect_distributed_nodes() -> List[str]:
    """
    Detect distributed computing nodes (Kubernetes, Docker Swarm, etc.)
    Returns list of detected distributed systems
    """
    nodes = []
    
    if detect_kubernetes():
        nodes.append('kubernetes')
    
    if detect_docker_swarm():
        nodes.append('docker_swarm')
    
    return nodes


def detect_cloud_and_distributed() -> Dict:
    """
    Comprehensive cloud and distributed environment detection
    Returns dict with is_cloud, provider, and nodes
    """
    provider = detect_cloud_provider()
    nodes = detect_distributed_nodes()
    
    return {
        'is_cloud': provider is not None,
        'provider': provider,
        'nodes': nodes
    }
