"""
Row-Level Security (RLS) Middleware
ENTERPRISE PATTERN: Automatic multi-tenant isolation at database level

Sets PostgreSQL session variable 'app.current_organization_id' for every request.
All queries automatically scoped to the user's organization.
"""
import logging

from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class TenantIsolationMiddleware(MiddlewareMixin):
    """
    ENTERPRISE PATTERN: Database-level tenant isolation

    Automatically sets the current organization ID in PostgreSQL session.
    RLS policies use this to scope all queries.

    **Benefits:**
    - Cannot accidentally query other organizations' data
    - Works at DB level (bulletproof)
    - No code changes needed in views/serializers
    - Prevents SQL injection attacks on organization_id

    **Setup:**
    1. Add to MIDDLEWARE in settings.py (after AuthenticationMiddleware)
    2. Run: python manage.py enable_rls
    3. All queries automatically scoped
    """

    def process_request(self, request):
        """
        Set organization_id in PostgreSQL session before processing request.
        """
        # Skip for anonymous users
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return None

        # Get organization from user profile
        try:
            if hasattr(request.user, "profile") and hasattr(
                request.user.profile, "organization"
            ):
                organization_id = str(request.user.profile.organization.id)

                # Set PostgreSQL session variable
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SET LOCAL app.current_organization_id = %s", [organization_id]
                    )

                logger.debug(
                    f"RLS: Set organization_id = {organization_id} for user {request.user.username}"
                )

                # Store in request for easy access
                request.organization_id = organization_id

            else:
                logger.warning(f"User {request.user.username} has no organization")

        except Exception as e:
            logger.error(f"Failed to set RLS organization_id: {e}", exc_info=True)

        return None

    def process_response(self, request, response):
        """
        Clean up PostgreSQL session variable after request.
        """
        try:
            # Reset session variable (optional, connection pool will reset anyway)
            with connection.cursor() as cursor:
                cursor.execute("RESET app.current_organization_id")
        except Exception as e:
            logger.error(f"Failed to reset RLS organization_id: {e}")

        return response


class SuperuserBypassMiddleware(MiddlewareMixin):
    """
    Allow superusers to bypass RLS for admin operations.

    **Usage:**
    Add after TenantIsolationMiddleware in settings.py
    Superusers can access all organizations' data in Django admin.
    """

    def process_request(self, request):
        """Disable RLS for superusers."""
        if hasattr(request, "user") and request.user.is_superuser:
            try:
                with connection.cursor() as cursor:
                    # Set a special flag that RLS policies can check
                    cursor.execute("SET LOCAL app.is_superuser = 'true'")

                logger.debug(f"RLS: Bypassed for superuser {request.user.username}")
            except Exception as e:
                logger.error(f"Failed to bypass RLS for superuser: {e}")

        return None
