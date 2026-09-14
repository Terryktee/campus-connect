import logging
import json
import re
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .authentication import AdminJWTAuthentication
from .mixins import InstitutionScopedQuerysetMixin
from .models import (
    Admin,
    AllowlistedDomain,
    BlocklistKeyword,
    Category,
    Institution,
    ModerationAction,
    Post,
    Report,
)
from .permissions import IsScopedAdmin, IsSuperAdmin
from .serializers import (
    AdminPostSerializer,
    AdminReportSerializer,
    PublicCategorySerializer,
    PublicInstitutionSerializer,
    PublicPostSerializer,
    PublicReportSerializer,
    PublicSubmissionSerializer,
    ModerationActionSerializer,
)

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


def _submitter_contact_key(group, request):
    if request.content_type == "application/json":
        try:
            payload = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            payload = {}
    else:
        payload = request.POST
    return str(payload.get("submitter_contact", "")).strip().lower() or "missing"


def _reporter_contact_key(group, request):
    if request.content_type == "application/json":
        try:
            payload = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            payload = {}
    else:
        payload = request.POST
    return str(payload.get("reporter_contact", "")).strip().lower() or "missing"


def _extract_urls(value):
    return re.findall(r"https?://[^\s<>\"]+", value or "", flags=re.IGNORECASE)


def _domain_is_allowlisted(hostname):
    hostname = hostname.lower().rstrip(".")
    domains = AllowlistedDomain.objects.values_list("domain", flat=True)
    return any(
        hostname == domain.lower().lstrip("*.").rstrip(".")
        or hostname.endswith(f".{domain.lower().lstrip('*.').rstrip('.')}")
        for domain in domains
    )


def _submission_is_flagged(validated_data):
    text = f"{validated_data['title']} {validated_data['content']}".casefold()
    if BlocklistKeyword.objects.filter(keyword__isnull=False).exists():
        if any(keyword.casefold() in text for keyword in BlocklistKeyword.objects.values_list("keyword", flat=True)):
            return True

    urls = _extract_urls(validated_data["content"])
    if validated_data.get("link_url"):
        urls.append(validated_data["link_url"])
    return any(
        not _domain_is_allowlisted(urlsplit(url).hostname or "")
        for url in urls
    )


@method_decorator(ratelimit(key="ip", rate="20/h", method="POST", block=False), name="dispatch")
@method_decorator(
    ratelimit(key=_submitter_contact_key, rate="5/h", method="POST", block=False),
    name="dispatch",
)
class PublicSubmissionView(CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = PublicSubmissionSerializer

    def create(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            return Response(
                {"error": "Submission limit reached. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.context.get("honeypot_triggered"):
            return Response({"status": "received"}, status=status.HTTP_200_OK)

        validated_data = serializer.validated_data
        validated_data.pop("channel_name", None)
        validated_data.pop("website", None)
        post = Post.objects.create(
            **validated_data,
            status=Post.Status.PENDING,
            is_flagged=_submission_is_flagged(validated_data),
        )
        return Response(
            {"id": post.pk, "status": post.status},
            status=status.HTTP_201_CREATED,
        )


class PublicPostPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class PublicPostListView(ListAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = PublicPostSerializer
    pagination_class = PublicPostPagination

    def get_queryset(self):
        queryset = Post.objects.filter(status=Post.Status.APPROVED).select_related(
            "category", "institution", "channel"
        ).order_by("-is_featured", "-created_at")
        if self.request.query_params.get("category"):
            queryset = queryset.filter(category__slug=self.request.query_params["category"])
        if self.request.query_params.get("institution"):
            institution = self.request.query_params["institution"]
            queryset = queryset.filter(
                institution__short_code=institution
            ) if not institution.isdigit() else queryset.filter(institution_id=institution)
        if self.request.query_params.get("search"):
            term = self.request.query_params["search"]
            queryset = queryset.filter(Q(title__icontains=term) | Q(content__icontains=term))
        return queryset


class PublicPostDetailView(RetrieveAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = PublicPostSerializer

    def get_queryset(self):
        return Post.objects.filter(status=Post.Status.APPROVED).select_related(
            "category", "institution", "channel"
        )

    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()
        Post.objects.filter(pk=post.pk).update(view_count=F("view_count") + 1)
        post.refresh_from_db()
        return Response(self.get_serializer(post).data)


@method_decorator(ratelimit(key="ip", rate="20/h", method="POST", block=False), name="dispatch")
@method_decorator(ratelimit(key=_reporter_contact_key, rate="5/h", method="POST", block=False), name="dispatch")
class PublicPostReportView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request, pk):
        if getattr(request, "limited", False):
            return Response(
                {"error": "Report limit reached. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        post = get_object_or_404(Post, pk=pk, status=Post.Status.APPROVED)
        serializer = PublicReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = Report.objects.create(post=post, **serializer.validated_data)
        return Response({"id": report.pk, "status": report.status}, status=status.HTTP_201_CREATED)


class PublicCategoryListView(ListAPIView):
    authentication_classes = ()
    permission_classes = ()
    queryset = Category.objects.all()
    serializer_class = PublicCategorySerializer
    pagination_class = None


class PublicInstitutionListView(ListAPIView):
    authentication_classes = ()
    permission_classes = ()
    queryset = Institution.objects.filter(is_active=True)
    serializer_class = PublicInstitutionSerializer
    pagination_class = None


class AdminPostListView(InstitutionScopedQuerysetMixin, ListAPIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsScopedAdmin,)
    serializer_class = AdminPostSerializer
    queryset = Post.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset().select_related("category", "institution", "channel")
        for field in ("status", "category", "institution"):
            value = self.request.query_params.get(field)
            if value:
                lookup = f"{field}__slug" if field == "category" and not value.isdigit() else field
                lookup = f"{field}__short_code" if field == "institution" and not value.isdigit() else lookup
                queryset = queryset.filter(**{lookup: value})
        flagged = self.request.query_params.get("is_flagged")
        if flagged in {"true", "false"}:
            queryset = queryset.filter(is_flagged=flagged == "true")
        return queryset.order_by("-is_flagged", "-created_at")


class AdminPostActionView(InstitutionScopedQuerysetMixin, APIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsScopedAdmin,)
    action = None

    def get_queryset(self):
        queryset = Post.objects.all()
        profile = self.request.admin_profile
        if profile.role == Admin.Role.MODERATOR:
            queryset = queryset.filter(institution_id=profile.institution_id)
        return queryset

    def post(self, request, pk):
        post = get_object_or_404(self.get_queryset(), pk=pk)
        profile = request.admin_profile
        reason = str(request.data.get("reason", "")).strip()
        if self.action == ModerationAction.Action.REJECT and not reason:
            return Response({"reason": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)
        now = timezone.now()
        with transaction.atomic():
            if self.action == ModerationAction.Action.APPROVE:
                post.status, post.approved_at = Post.Status.APPROVED, now
            elif self.action == ModerationAction.Action.REJECT:
                post.status, post.rejection_reason = Post.Status.REJECTED, reason
            elif self.action == ModerationAction.Action.TAKE_DOWN:
                if post.status != Post.Status.APPROVED:
                    return Response({"detail": "Only approved posts can be taken down."}, status=400)
                post.status, post.taken_down_at = Post.Status.TAKEN_DOWN, now
            elif self.action in (ModerationAction.Action.FEATURE, ModerationAction.Action.UNFEATURE):
                post.is_featured = self.action == ModerationAction.Action.FEATURE
            post.save()
            ModerationAction.objects.create(post=post, admin=profile, action=self.action, reason=reason)
        return Response(AdminPostSerializer(post).data)


class AdminApprovePostView(AdminPostActionView):
    action = ModerationAction.Action.APPROVE


class AdminRejectPostView(AdminPostActionView):
    action = ModerationAction.Action.REJECT


class AdminTakeDownPostView(AdminPostActionView):
    action = ModerationAction.Action.TAKE_DOWN


class AdminFeaturePostView(AdminPostActionView):
    action = ModerationAction.Action.FEATURE


class AdminUnfeaturePostView(AdminPostActionView):
    action = ModerationAction.Action.UNFEATURE


class AdminReportListView(InstitutionScopedQuerysetMixin, ListAPIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsScopedAdmin,)
    serializer_class = AdminReportSerializer
    queryset = Report.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset().select_related("post")
        return queryset.order_by("-created_at")


class AdminReportActionView(InstitutionScopedQuerysetMixin, APIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsScopedAdmin,)

    def get_queryset(self):
        queryset = Report.objects.select_related("post")
        profile = self.request.admin_profile
        if profile.role == Admin.Role.MODERATOR:
            queryset = queryset.filter(post__institution_id=profile.institution_id)
        return queryset

    def post(self, request, pk, action):
        if action not in {"dismiss", "escalate"}:
            return Response({"detail": "Unknown report action."}, status=status.HTTP_404_NOT_FOUND)
        report = get_object_or_404(self.get_queryset(), pk=pk)
        profile = request.admin_profile
        with transaction.atomic():
            report.status = Report.Status.RESOLVED
            report.save(update_fields=("status",))
            action_name = (
                ModerationAction.Action.ESCALATE_REPORT
                if action == "escalate"
                else ModerationAction.Action.DISMISS_REPORT
            )
            ModerationAction.objects.create(
                admin=profile,
                post=report.post,
                action=action_name,
                reason=request.data.get("reason", ""),
            )
            if action == "escalate":
                post = report.post
                post.status, post.taken_down_at = Post.Status.TAKEN_DOWN, timezone.now()
                post.save(update_fields=("status", "taken_down_at"))
                ModerationAction.objects.create(
                    admin=profile, post=post, action=ModerationAction.Action.TAKE_DOWN
                )
        return Response({"id": report.pk, "status": report.status})


class AdminModerationActionListView(InstitutionScopedQuerysetMixin, ListAPIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsScopedAdmin,)
    serializer_class = ModerationActionSerializer

    def get_queryset(self):
        queryset = ModerationAction.objects.select_related("admin", "post", "channel")
        profile = self.request.admin_profile
        if profile.role == Admin.Role.MODERATOR:
            queryset = queryset.filter(
                Q(post__institution_id=profile.institution_id)
                | Q(channel__institution_id=profile.institution_id)
            )
        if self.request.query_params.get("admin"):
            queryset = queryset.filter(admin_id=self.request.query_params["admin"])
        if self.request.query_params.get("action"):
            queryset = queryset.filter(action=self.request.query_params["action"])
        if self.request.query_params.get("date_from"):
            queryset = queryset.filter(created_at__date__gte=self.request.query_params["date_from"])
        if self.request.query_params.get("date_to"):
            queryset = queryset.filter(created_at__date__lte=self.request.query_params["date_to"])
        return queryset.order_by("-created_at")
