"""Separate public and admin serializer modules prevent accidental private-field leaks."""

import re

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from rest_framework import serializers

from .models import Channel, Category, Institution, ModerationAction, Post, Report


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

    if re.fullmatch(r"(?:\+263|00263|263|0)7\d{8}", normalized.replace(" ", "").replace("-", "")):
        return normalized
    raise serializers.ValidationError(
        "Enter a valid email address or Zimbabwean phone number."
    )


class PublicInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ("id", "name", "short_code", "city", "logo_url", "is_active", "created_at")


class PublicCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "sort_order", "created_at")


class PublicChannelSerializer(serializers.ModelSerializer):
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


class PublicPostSerializer(serializers.ModelSerializer):
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
