"""
Custom CSRF Middleware that exempts API endpoints

API endpoints use JWT authentication which provides CSRF protection via:
- HttpOnly cookies (can't be accessed by JavaScript)
- SameSite=Lax (prevents cross-site requests)
- Short-lived tokens (15 min access tokens)

This combination is equivalent to CSRF tokens for API security.
"""

from django.middleware.csrf import CsrfViewMiddleware


class APICSRFExemptMiddleware(CsrfViewMiddleware):
    """
    CSRF middleware that exempts API endpoints from CSRF checks
    
    Exempts:
    - /api/* endpoints (JWT protected)
    - Admin panel still requires CSRF tokens
    """
    
    def process_request(self, request):
        # Exempt all /api/ endpoints from CSRF by marking them as processed
        if request.path.startswith('/api/'):
            # Set the attribute that tells Django CSRF has been processed
            setattr(request, '_dont_enforce_csrf_checks', True)
        return super().process_request(request)
