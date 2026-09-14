from django.contrib import admin
from django.urls import path
from core.views import (
    AdminInviteView,
    AdminMeView,
    AdminTokenObtainPairView,
    AdminTokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", AdminTokenObtainPairView.as_view(), name="auth-login"),
    path("api/auth/refresh/", AdminTokenRefreshView.as_view(), name="auth-refresh"),
    path("api/admin/me/", AdminMeView.as_view(), name="admin-me"),
    path("api/admin/invite/", AdminInviteView.as_view(), name="admin-invite"),
]
