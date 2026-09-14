"""Separate public and admin serializer modules prevent accidental private-field leaks."""

from rest_framework import serializers

from .models import Channel, Category, Institution, Post


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
            "status",
            "is_flagged",
            "is_featured",
            "featured_until",
            "view_count",
            "created_at",
            "approved_at",
            "taken_down_at",
        )


class AdminChannelSerializer(PublicChannelSerializer):
    class Meta(PublicChannelSerializer.Meta):
        fields = PublicChannelSerializer.Meta.fields + ("claim_contact", "claim_token")


class AdminPostSerializer(PublicPostSerializer):
    class Meta(PublicPostSerializer.Meta):
        fields = PublicPostSerializer.Meta.fields + (
            "submitter_contact",
            "rejection_reason",
        )
