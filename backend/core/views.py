import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .authentication import AdminJWTAuthentication
from .models import Admin, Institution
from .permissions import IsScopedAdmin, IsSuperAdmin

logger = logging.getLogger(__name__)


class AdminTokenObtainPairView(TokenObtainPairView):
    authentication_classes = ()


class AdminTokenRefreshView(TokenRefreshView):
    authentication_classes = ()


class AdminMeView(APIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsScopedAdmin,)

    def get(self, request):
        profile = request.admin_profile
        return Response(
            {
                "name": request.user.get_full_name() or request.user.get_username(),
                "role": profile.role,
                "institution": profile.institution.name if profile.institution else None,
            }
        )


class AdminInviteSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=Admin.Role.choices)
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.filter(is_active=True), allow_null=True, required=False
    )

    def validate_username(self, value):
        if get_user_model().objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate(self, attrs):
        if attrs["role"] == Admin.Role.SUPER_ADMIN and attrs.get("institution") is not None:
            raise serializers.ValidationError(
                {"institution": "Super admins cannot be assigned to an institution."}
            )
        if attrs["role"] == Admin.Role.MODERATOR and attrs.get("institution") is None:
            raise serializers.ValidationError({"institution": "Moderators require an institution."})
        return attrs


def log_admin_invitation(user, invite_link):
    logger.info("Admin invitation prepared for %s: %s", user.email, invite_link)


class AdminInviteView(CreateAPIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsSuperAdmin,)
    serializer_class = AdminInviteSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = get_user_model().objects.create_user(
            username=data["username"],
            email=data["email"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
        )
        user.set_unusable_password()
        user.save(update_fields=["password"])
        profile = Admin.objects.create(
            user=user,
            role=data["role"],
            institution=data.get("institution"),
        )
        invite_link = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/admin/invite/{user.pk}"
        log_admin_invitation(user, invite_link)
        return Response(
            {"id": profile.pk, "username": user.username, "role": profile.role},
            status=status.HTTP_201_CREATED,
        )
