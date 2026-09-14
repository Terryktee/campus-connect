from rest_framework.permissions import BasePermission

from .models import Admin


class IsScopedAdmin(BasePermission):
    """Allow authenticated users that have an Admin profile."""

    message = "A valid admin account is required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            admin_profile = request.user.admin
        except Admin.DoesNotExist:
            return False

        request.admin_profile = admin_profile
        view.admin_profile = admin_profile
        return True


class IsSuperAdmin(IsScopedAdmin):
    message = "Only super admins may perform this action."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.admin_profile.role == "super_admin"
