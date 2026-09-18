import json
import re
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Exists, F, OuterRef, Q
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
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
    Channel,
    Follow,
    NotificationQueue,
    OrientationGuide,
    SponsoredListing,
)
from .permissions import IsScopedAdmin, IsSuperAdmin
from .tasks import send_admin_invite_email, send_channel_claim_email
from .serializers import (
    AdminPostSerializer,
    AdminReportSerializer,
    AdminChannelSerializer,
    AdminOrientationGuideSerializer,
    PublicCategorySerializer,
    PublicChannelDetailSerializer,
    PublicChannelSerializer,
    FollowSerializer,
    PublicInstitutionSerializer,
    PublicOrientationGuideSerializer,
    PublicPostSerializer,
    PublicReportSerializer,
    PublicSubmissionSerializer,
    ModerationActionSerializer,
    AdminSponsoredListingSerializer,
)

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


class FailedNotificationSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source="post.title", read_only=True)

    class Meta:
        model = NotificationQueue
        fields = ("id", "post", "post_title", "status", "retry_count", "created_at", "sent_at")


class AdminFailedNotificationListView(ListAPIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsSuperAdmin,)
    serializer_class = FailedNotificationSerializer

    def get_queryset(self):
        return NotificationQueue.objects.filter(
            status=NotificationQueue.Status.FAILED
        ).select_related("post").order_by("-created_at")


class AdminSponsoredListingListView(ListCreateAPIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsSuperAdmin,)
    serializer_class = AdminSponsoredListingSerializer
    queryset = SponsoredListing.objects.all()

    def get_queryset(self):
        return super().get_queryset().select_related("post", "channel").order_by("-created_at")


class AdminSponsoredListingDetailView(RetrieveUpdateDestroyAPIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsSuperAdmin,)
    serializer_class = AdminSponsoredListingSerializer
    queryset = SponsoredListing.objects.all()

    def get_queryset(self):
        return super().get_queryset().select_related("post", "channel")


class SponsorListingAnalyticsView(RetrieveAPIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsScopedAdmin,)
    serializer_class = AdminSponsoredListingSerializer
    queryset = SponsoredListing.objects.all()

    def get_queryset(self):
        profile = self.request.admin_profile
        if profile.role != Admin.Role.SPONSOR_VIEWER:
            return SponsoredListing.objects.none()
        return SponsoredListing.objects.filter(
            sponsor_email__iexact=profile.user.email
        ).select_related("post", "channel")

    def retrieve(self, request, *args, **kwargs):
        listing = self.get_object()
        if listing.post:
            view_count = listing.post.view_count
            follower_count = None
        else:
            view_count = None
            follower_count = listing.channel.follower_count
        return Response(
            {
                "listing_id": listing.pk,
                "post": listing.post_id,
                "channel": listing.channel_id,
                "view_count": view_count,
                "follower_count": follower_count,
            }
        )


class PublicOrientationGuideView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, institution_short_code):
        institution = get_object_or_404(
            Institution, short_code=institution_short_code, is_active=True
        )
        guides = OrientationGuide.objects.filter(
            institution=institution, is_published=True
        ).order_by("sort_order", "id")
        grouped = {guide_type: [] for guide_type, _ in OrientationGuide.GuideType.choices}
        for guide in guides:
            grouped[guide.guide_type].append(
                PublicOrientationGuideSerializer(guide).data
            )
        return Response(grouped)


class AdminOrientationGuideListView(InstitutionScopedQuerysetMixin, ListCreateAPIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsScopedAdmin,)
    serializer_class = AdminOrientationGuideSerializer
    queryset = OrientationGuide.objects.all()

    def get_queryset(self):
        return super().get_queryset().select_related("institution").order_by(
            "sort_order", "id"
        )

    def perform_create(self, serializer):
        institution = serializer.validated_data["institution"]
        profile = self.request.admin_profile
        if (
            profile.role == Admin.Role.MODERATOR
            and institution.pk != profile.institution_id
        ):
            raise PermissionDenied("You can only manage guides for your institution.")
        serializer.save()


class AdminOrientationGuideDetailView(
    InstitutionScopedQuerysetMixin, RetrieveUpdateDestroyAPIView
):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsScopedAdmin,)
    serializer_class = AdminOrientationGuideSerializer
    queryset = OrientationGuide.objects.all()

    def get_queryset(self):
        return super().get_queryset().select_related("institution")

    def perform_update(self, serializer):
        institution = serializer.validated_data.get(
            "institution", serializer.instance.institution
        )
        profile = self.request.admin_profile
        if (
            profile.role == Admin.Role.MODERATOR
            and institution.pk != profile.institution_id
        ):
            raise PermissionDenied("You can only manage guides for your institution.")
        serializer.save()


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
        transaction.on_commit(
            lambda: send_admin_invite_email.delay(
                recipient=user.email,
                invite_link=invite_link,
                recipient_name=user.get_full_name() or user.username,
            )
        )
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
        channel_name = validated_data.pop("channel_name", "").strip()
        validated_data.pop("website", None)
        with transaction.atomic():
            channel = None
            if channel_name:
                channel_slug = slugify(channel_name)
                channel = Channel.objects.filter(slug__iexact=channel_slug).first()
                if channel is None:
                    channel = Channel.objects.create(
                        slug=channel_slug,
                        name=channel_name,
                        claim_contact=validated_data["submitter_contact"],
                        institution=validated_data.get("institution"),
                        category_focus=validated_data.get("category"),
                        status=Channel.Status.PENDING,
                    )
            post = Post.objects.create(
                **validated_data,
                channel=channel,
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
        now = timezone.now()
        active_sponsored_post = SponsoredListing.objects.filter(
            post=OuterRef("pk"),
            placement_type=SponsoredListing.PlacementType.FEATURED_POST,
            starts_at__lte=now,
            ends_at__gte=now,
        )
        queryset = Post.objects.filter(status=Post.Status.APPROVED).select_related(
            "category", "institution", "channel"
        ).annotate(sponsored_featured=Exists(active_sponsored_post)).order_by(
            "-is_featured", "-sponsored_featured", "-created_at"
        )
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


class PublicChannelListView(ListAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = PublicChannelSerializer
    pagination_class = PublicPostPagination

    def get_queryset(self):
        now = timezone.now()
        active_verified_channel = SponsoredListing.objects.filter(
            channel=OuterRef("pk"),
            placement_type=SponsoredListing.PlacementType.VERIFIED_CHANNEL,
            starts_at__lte=now,
            ends_at__gte=now,
        )
        return Channel.objects.filter(status=Channel.Status.ACTIVE).select_related(
            "category_focus", "institution"
        ).annotate(sponsored_verified=Exists(active_verified_channel)).order_by(
            "-is_verified", "-sponsored_verified", "name"
        )


class PublicChannelDetailView(RetrieveAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = PublicChannelDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Channel.objects.filter(status=Channel.Status.ACTIVE).select_related(
            "category_focus", "institution"
        )


@method_decorator(ratelimit(key="ip", rate="10/h", method="POST", block=False), name="dispatch")
class PublicChannelClaimView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def get_channel(self, token):
        return get_object_or_404(
            Channel, claim_token=token, status=Channel.Status.PENDING, claimed_at__isnull=True
        )

    def get(self, request, token):
        channel = self.get_channel(token)
        return Response({"name": channel.name, "bio": channel.bio})

    @transaction.atomic
    def post(self, request, token):
        channel = self.get_channel(token)
        channel.claimed_at = timezone.now()
        channel.save(update_fields=("claimed_at",))
        transaction.on_commit(
            lambda: send_channel_claim_email.delay(
                recipient=channel.claim_contact,
                channel_name=channel.name,
                claim_link=(
                    f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}"
                    f"/channels/claim/{channel.claim_token}"
                ),
            )
        )
        return Response({"name": channel.name, "status": channel.status})


def _contact_key(group, request):
    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        payload = request.POST
    return str(payload.get("follower_contact", "")).strip().lower() or "missing"


@method_decorator(ratelimit(key="ip", rate="20/h", method=("POST", "DELETE"), block=False), name="dispatch")
@method_decorator(ratelimit(key=_contact_key, rate="5/h", method=("POST", "DELETE"), block=False), name="dispatch")
class PublicFollowView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def _limited(self, request):
        if getattr(request, "limited", False):
            return Response(
                {"error": "Follow limit reached. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

    def _target(self, serializer):
        data = serializer.validated_data
        if data.get("channel"):
            channel_lookup = Q(slug__iexact=data["channel"])
            if str(data["channel"]).isdigit():
                channel_lookup |= Q(pk=int(data["channel"]))
            return get_object_or_404(
                Channel, channel_lookup, status=Channel.Status.ACTIVE
            ), None, None
        return None, data["category"], data.get("institution")

    def post(self, request):
        limited = self._limited(request)
        if limited:
            return limited
        serializer = FollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        channel, category, institution = self._target(serializer)
        contact = serializer.validated_data["follower_contact"].lower()
        with transaction.atomic():
            if channel:
                follow, created = Follow.objects.get_or_create(
                    follower_contact=contact, channel=channel
                )
                if created:
                    Channel.objects.filter(pk=channel.pk).update(
                        follower_count=F("follower_count") + 1
                    )
            else:
                existing = Follow.objects.filter(
                    follower_contact=contact, category=category, institution=institution
                ).first()
                if existing:
                    return Response({"error": "This follow already exists."}, status=409)
                follow = Follow.objects.create(
                    follower_contact=contact, category=category, institution=institution
                )
                created = True
        if not created:
            return Response({"error": "This follow already exists."}, status=409)
        return Response({"id": follow.pk}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        limited = self._limited(request)
        if limited:
            return limited
        serializer = FollowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        channel, category, institution = self._target(serializer)
        filters = {"follower_contact": serializer.validated_data["follower_contact"].lower()}
        if channel:
            filters["channel"] = channel
        else:
            filters.update(category=category, institution=institution)
        with transaction.atomic():
            follow = Follow.objects.filter(**filters).first()
            if not follow:
                return Response({"error": "Follow not found."}, status=404)
            follow.delete()
            if channel:
                Channel.objects.filter(pk=channel.pk, follower_count__gt=0).update(
                    follower_count=F("follower_count") - 1
                )
        return Response(status=status.HTTP_204_NO_CONTENT)


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
            if self.action == ModerationAction.Action.APPROVE:
                follow_query = (
                    Q(category=post.category, institution__isnull=True)
                    | Q(category=post.category, institution=post.institution)
                )
                if post.channel_id:
                    follow_query |= Q(channel_id=post.channel_id)
                follows = Follow.objects.filter(follow_query)
                NotificationQueue.objects.bulk_create(
                    [
                        NotificationQueue(
                            follow=follow,
                            post=post,
                            channel=(
                                NotificationQueue.Channel.EMAIL
                                if "@" in follow.follower_contact
                                else NotificationQueue.Channel.WHATSAPP
                            ),
                        )
                        for follow in follows
                    ]
                )
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


class AdminChannelActionView(InstitutionScopedQuerysetMixin, APIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsScopedAdmin,)

    def get_queryset(self):
        queryset = Channel.objects.all()
        profile = self.request.admin_profile
        if profile.role == Admin.Role.MODERATOR:
            queryset = queryset.filter(institution_id=profile.institution_id)
        return queryset

    def post(self, request, pk, action):
        action_map = {
            "approve": (Channel.Status.ACTIVE, ModerationAction.Action.APPROVE),
            "reject": (Channel.Status.SUSPENDED, ModerationAction.Action.SUSPEND_CHANNEL),
            "verify": (None, ModerationAction.Action.VERIFY_CHANNEL),
            "suspend": (Channel.Status.SUSPENDED, ModerationAction.Action.SUSPEND_CHANNEL),
        }
        if action not in action_map:
            return Response({"detail": "Unknown channel action."}, status=404)
        channel = get_object_or_404(self.get_queryset(), pk=pk)
        profile = request.admin_profile
        new_status, audit_action = action_map[action]
        with transaction.atomic():
            if action == "verify":
                channel.is_verified = True
                channel.save(update_fields=("is_verified",))
            else:
                channel.status = new_status
                if action == "approve":
                    channel.approved_at = timezone.now()
                channel.save(update_fields=("status", "approved_at") if action == "approve" else ("status",))
            ModerationAction.objects.create(
                channel=channel,
                admin=profile,
                action=audit_action,
                reason=str(request.data.get("reason", ""))[:255],
            )
        return Response(AdminChannelSerializer(channel).data)


class AdminReportListView(InstitutionScopedQuerysetMixin, ListAPIView):
    authentication_classes = (AdminJWTAuthentication,)
    permission_classes = (IsScopedAdmin,)
    serializer_class = AdminReportSerializer
    queryset = Report.objects.all()

    institution_lookup = "post__institution_id"

    def get_queryset(self):
        queryset = (
            super()
            .get_queryset()
            .select_related("post", "post__institution")
        )
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
