from django.contrib import admin
from django.db import models

from .models import (
    Admin as AdminProfile,
)
from .models import (
    AllowlistedDomain,
    BlocklistKeyword,
    Category,
    Channel,
    Follow,
    Institution,
    ModerationAction,
    NotificationQueue,
    OrientationGuide,
    Post,
    Report,
    SponsoredListing,
)


class InstitutionScopedAdmin(admin.ModelAdmin):
    institution_lookup = "institution_id"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        profile = getattr(request.user, "admin", None)
        if profile and profile.role == AdminProfile.Role.MODERATOR and profile.institution_id:
            return queryset.filter(**{self.institution_lookup: profile.institution_id})
        return queryset


@admin.register(Post)
class PostAdmin(InstitutionScopedAdmin):
    list_display = ("title", "status", "institution", "is_flagged", "created_at")
    list_filter = ("status", "is_flagged", "institution")
    search_fields = ("title", "content")


@admin.register(Channel)
class ChannelAdmin(InstitutionScopedAdmin):
    list_display = ("name", "status", "institution", "is_verified")
    list_filter = ("status", "is_verified", "institution")
    search_fields = ("name", "slug")


@admin.register(ModerationAction)
class ModerationActionAdmin(InstitutionScopedAdmin):
    list_display = ("action", "admin", "post", "channel", "created_at")
    list_filter = ("action", "created_at")
    readonly_fields = ("post", "channel", "admin", "action", "reason", "note", "created_at")

    def get_queryset(self, request):
        queryset = admin.ModelAdmin.get_queryset(self, request)
        profile = getattr(request.user, "admin", None)
        if profile and profile.role == AdminProfile.Role.MODERATOR and profile.institution_id:
            return queryset.filter(
                models.Q(post__institution_id=profile.institution_id)
                | models.Q(channel__institution_id=profile.institution_id)
            )
        return queryset

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Report)
class ReportAdmin(InstitutionScopedAdmin):
    institution_lookup = "post__institution_id"
    list_display = ("post", "status", "created_at")
    list_filter = ("status",)


for model in (
    AdminProfile,
    AllowlistedDomain,
    BlocklistKeyword,
    Category,
    Follow,
    Institution,
    NotificationQueue,
    OrientationGuide,
    SponsoredListing,
):
    admin.site.register(model)
