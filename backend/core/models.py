import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Institution(models.Model):
    name = models.CharField(max_length=200)
    short_code = models.CharField(max_length=20, unique=True)
    city = models.CharField(max_length=100)
    logo_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("sort_order", "name")

    def __str__(self):
        return self.name


class Channel(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"

    slug = models.SlugField(max_length=160, unique=True)
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    category_focus = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    institution = models.ForeignKey(Institution, null=True, blank=True, on_delete=models.SET_NULL)
    claim_contact = models.CharField(max_length=255)
    claim_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_verified = models.BooleanField(default=False)
    follower_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    claimed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Admin(models.Model):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super admin"
        MODERATOR = "moderator", "Moderator"
        SPONSOR_VIEWER = "sponsor_viewer", "Sponsor viewer"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.MODERATOR)
    institution = models.ForeignKey(Institution, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.user.get_username()


class Post(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        TAKEN_DOWN = "taken_down", "Taken down"

    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    institution = models.ForeignKey(Institution, null=True, blank=True, on_delete=models.SET_NULL)
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.SET_NULL)
    image_url = models.URLField(blank=True)
    link_url = models.URLField(blank=True)
    submitter_name = models.CharField(max_length=200)
    submitter_institution = models.CharField(max_length=200, blank=True)
    submitter_contact = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    is_flagged = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    taken_down_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class ModerationAction(models.Model):
    class Action(models.TextChoices):
        APPROVE = "approve", "Approve"
        REJECT = "reject", "Reject"
        TAKE_DOWN = "take_down", "Take down"
        EDIT = "edit", "Edit"
        FEATURE = "feature", "Feature"
        UNFEATURE = "unfeature", "Unfeature"
        VERIFY_CHANNEL = "verify_channel", "Verify channel"
        SUSPEND_CHANNEL = "suspend_channel", "Suspend channel"
        DISMISS_REPORT = "dismiss_report", "Dismiss report"
        ESCALATE_REPORT = "escalate_report", "Escalate report"

    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.SET_NULL)
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.SET_NULL)
    admin = models.ForeignKey(Admin, on_delete=models.PROTECT)
    action = models.CharField(max_length=30, choices=Action.choices)
    reason = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class Report(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        RESOLVED = "resolved", "Resolved"

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reason = models.TextField()
    reporter_contact = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    follower_contact = models.CharField(max_length=255)
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("follower_contact", "channel"), name="unique_channel_follow"
            ),
            models.UniqueConstraint(
                fields=("follower_contact", "category", "institution"),
                name="unique_category_institution_follow",
            ),
            models.CheckConstraint(
                condition=(
                    (models.Q(channel__isnull=False) & models.Q(category__isnull=True) & models.Q(institution__isnull=True))
                    | (models.Q(channel__isnull=True) & models.Q(category__isnull=False))
                ),
                name="follow_has_one_valid_target",
            ),
        ]


class NotificationQueue(models.Model):
    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        WHATSAPP = "whatsapp", "WhatsApp"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    follow = models.ForeignKey(Follow, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    channel = models.CharField(max_length=20, choices=Channel.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    retry_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)


class OrientationGuide(models.Model):
    class GuideType(models.TextChoices):
        HOW_TO = "how_to", "How to"
        DIRECTORY_ENTRY = "directory_entry", "Directory entry"
        CAMPUS_MAP_NOTE = "campus_map_note", "Campus map note"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    guide_type = models.CharField(max_length=30, choices=GuideType.choices)
    title = models.CharField(max_length=255)
    content = models.TextField()
    contact_info = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SponsoredListing(models.Model):
    class PlacementType(models.TextChoices):
        FEATURED_POST = "featured_post", "Featured post"
        VERIFIED_CHANNEL = "verified_channel", "Verified channel"
        BANNER = "banner", "Banner"

    post = models.OneToOneField(Post, null=True, blank=True, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.CASCADE)
    sponsor_name = models.CharField(max_length=200)
    placement_type = models.CharField(max_length=30, choices=PlacementType.choices)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="USD")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)


class BlocklistKeyword(models.Model):
    keyword = models.CharField(max_length=100, unique=True)


class AllowlistedDomain(models.Model):
    domain = models.CharField(max_length=255, unique=True)
