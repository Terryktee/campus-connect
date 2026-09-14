from rest_framework_simplejwt.authentication import JWTAuthentication


class AdminJWTAuthentication(JWTAuthentication):
    """JWT authentication used by the admin API endpoints."""
