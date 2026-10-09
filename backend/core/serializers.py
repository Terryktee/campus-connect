"""Separate public and admin serializer modules prevent accidental private-field leaks."""

import re

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils import timezone
from rest_framework import serializers

from .models import (
    Category,
    Channel,
    Institution,
    ModerationAction,
    OrientationGuide,
    Post,
    Report,
    SponsoredListing,
)


class CategoryReferenceField(serializers.RelatedField):
    def to_internal_value(self, data):
        if isinstance(data, int) or (isinstance(data, str) and data.isdigit()):
            try:
                return Category.objects.get(pk=int(data))
            except Category.DoesNotExist as exc:
                raise serializers.ValidationError("Category does not exist.") from exc
        if isinstance(data, str):
            try:
                return Category.objects.get(slug=data)
            except Category.DoesNotExist as exc:
                raise serializers.ValidationError("Category does not exist.") from exc
        raise serializers.ValidationError("Provide a category ID or slug.")

    def to_representation(self, value):
        return value.pk


class InstitutionReferenceField(serializers.RelatedField):
    def to_internal_value(self, data):
        if isinstance(data, int) or (isinstance(data, str) and data.isdigit()):
            try:
                return Institution.objects.get(pk=int(data), is_active=True)
            except Institution.DoesNotExist as exc:
                raise serializers.ValidationError("Institution does not exist.") from exc
        if isinstance(data, str):
            try:
                return Institution.objects.get(short_code=data, is_active=True)
            except Institution.DoesNotExist as exc:
                raise serializers.ValidationError("Institution does not exist.") from exc
        raise serializers.ValidationError("Provide an institution ID or short code.")

    def to_representation(self, value):
        return value.pk


def validate_submitter_contact(value):
    normalized = value.strip()
    try:
        EmailValidator()(normalized)
        return normalized
    except ValidationError:
        pass

    cleaned_phone = normalized.replace(" ", "").replace("-", "")
    if re.fullmatch(r"\+?[0-9]{7,15}", cleaned_phone):
        return normalized
    raise serializers.ValidationError(
        "Enter a valid email address or phone number."
    )


class PublicInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ("id", "name", "short_code", "city", "logo_url", "is_active", "created_at")


class PublicOrientationGuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrientationGuide
        fields = ("id", "guide_type", "title", "content", "contact_info", "sort_order")


class AdminOrientationGuideSerializer(PublicOrientationGuideSerializer):
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.filter(is_active=True)
    )

    class Meta(PublicOrientationGuideSerializer.Meta):
        fields = PublicOrientationGuideSerializer.Meta.fields + (
            "institution",
            "is_published",
            "created_at",
            "updated_at",
        )


class PublicCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "sort_order", "created_at")


class PublicChannelSerializer(serializers.ModelSerializer):
    is_verified = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = (
            "id",
            "slug",
            "name",
            "bio",
            "category_focus",
            "institution",
            "status",
            "is_verified",
            "follower_count",
            "created_at",
            "approved_at",
        )

    def get_is_verified(self, channel):
        if channel.is_verified:
            return True
        return SponsoredListing.objects.filter(
            channel=channel,
            placement_type=SponsoredListing.PlacementType.VERIFIED_CHANNEL,
            starts_at__lte=timezone.now(),
            ends_at__gte=timezone.now(),
        ).exists()


class PublicChannelDetailSerializer(PublicChannelSerializer):
    posts = serializers.SerializerMethodField()

    class Meta(PublicChannelSerializer.Meta):
        fields = PublicChannelSerializer.Meta.fields + ("posts",)

    def get_posts(self, channel):
        return PublicPostSerializer(
            channel.post_set.filter(status=Post.Status.APPROVED).select_related(
                "category", "institution", "channel"
            ),
            many=True,
        ).data


class FollowSerializer(serializers.Serializer):
    follower_contact = serializers.CharField(max_length=255)
    channel = serializers.CharField(required=False)
    category = serializers.CharField(required=False)
    institution = serializers.CharField(required=False, allow_null=True)

    def validate_follower_contact(self, value):
        return validate_submitter_contact(value)

    def validate(self, attrs):
        has_channel = bool(attrs.get("channel"))
        has_category = bool(attrs.get("category"))
        if has_channel == has_category:
            raise serializers.ValidationError(
                "Provide either a channel or a category target."
            )
        if has_channel and attrs.get("institution") is not None:
            raise serializers.ValidationError(
                "Channel follows cannot include an institution."
            )
        if has_category:
            attrs["category"] = CategoryReferenceField(
                queryset=Category.objects.all()
            ).to_internal_value(attrs["category"])
            institution = attrs.get("institution")
            if institution is not None:
                attrs["institution"] = InstitutionReferenceField(
                    queryset=Institution.objects.filter(is_active=True)
                ).to_internal_value(institution)
        return attrs


class PublicPostSerializer(serializers.ModelSerializer):
    is_featured = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "category",
            "institution",
            "channel",
            "image_url",
            "link_url",
            "submitter_name",
            "submitter_institution",
            "is_featured",
            "view_count",
            "created_at",
        )

    def get_is_featured(self, post):
        if post.is_featured:
            return True
        return SponsoredListing.objects.filter(
            post=post,
            placement_type=SponsoredListing.PlacementType.FEATURED_POST,
            starts_at__lte=timezone.now(),
            ends_at__gte=timezone.now(),
        ).exists()


class AdminChannelSerializer(PublicChannelSerializer):
    class Meta(PublicChannelSerializer.Meta):
        fields = PublicChannelSerializer.Meta.fields + ("claim_contact", "claim_token")


class AdminPostSerializer(PublicPostSerializer):
    class Meta(PublicPostSerializer.Meta):
        fields = (
            "id",
            "title",
            "content",
            "category",
            "institution",
            "channel",
            "image_url",
            "link_url",
            "submitter_name",
            "submitter_institution",
            "submitter_contact",
            "status",
            "is_flagged",
            "is_featured",
            "featured_until",
            "view_count",
            "created_at",
            "approved_at",
            "taken_down_at",
            "rejection_reason",
        )


class AdminReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ("id", "post", "reason", "reporter_contact", "status", "created_at")


class AdminSponsoredListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SponsoredListing
        fields = (
            "id",
            "post",
            "channel",
            "sponsor_name",
            "sponsor_email",
            "placement_type",
            "amount_paid",
            "currency",
            "starts_at",
            "ends_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        post = attrs.get("post", getattr(self.instance, "post", None))
        channel = attrs.get("channel", getattr(self.instance, "channel", None))
        placement = attrs.get(
            "placement_type", getattr(self.instance, "placement_type", None)
        )
        if bool(post) == bool(channel):
            raise serializers.ValidationError("Provide exactly one post or channel.")
        if placement == SponsoredListing.PlacementType.FEATURED_POST and not post:
            raise serializers.ValidationError(
                "featured_post listings must target a post."
            )
        if placement == SponsoredListing.PlacementType.VERIFIED_CHANNEL and not channel:
            raise serializers.ValidationError(
                "verified_channel listings must target a channel."
            )
        if attrs.get("ends_at", getattr(self.instance, "ends_at", None)) <= attrs.get(
            "starts_at", getattr(self.instance, "starts_at", None)
        ):
            raise serializers.ValidationError("ends_at must be after starts_at.")
        return attrs


class PublicReportSerializer(serializers.ModelSerializer):
    reporter_contact = serializers.CharField(
        max_length=255, required=False, allow_blank=True, write_only=True, default=""
    )

    class Meta:
        model = Report
        fields = ("reason", "reporter_contact")


class ModerationActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationAction
        fields = ("id", "post", "channel", "admin", "action", "reason", "note", "created_at")


class PublicSubmissionSerializer(serializers.ModelSerializer):
    category = CategoryReferenceField(queryset=Category.objects.all())
    institution = InstitutionReferenceField(
        queryset=Institution.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    channel_name = serializers.CharField(max_length=200, required=False, allow_blank=True, write_only=True)
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)
    submitter_name = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")
    submitter_contact = serializers.CharField(
        max_length=255, validators=[validate_submitter_contact]
    )

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
            "category",
            "institution",
            "channel_name",
            "image_url",
            "link_url",
            "submitter_name",
            "submitter_institution",
            "submitter_contact",
            "website",
        )

    def validate(self, attrs):
        if attrs.get("website"):
            self.context["honeypot_triggered"] = True
        return attrs
