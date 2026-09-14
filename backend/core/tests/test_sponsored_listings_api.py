from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Admin, Category, Channel, Institution, Post, SponsoredListing


class SponsoredListingsApiTests(APITestCase):
    def setUp(self):
        self.institution = Institution.objects.create(
            name="One", short_code="ONE", city="Harare"
        )
        self.category = Category.objects.create(name="News", slug="news")
        self.post = Post.objects.create(
            title="Sponsored", content="Content", category=self.category,
            institution=self.institution, status=Post.Status.APPROVED,
            submitter_contact="private@example.com",
        )
        self.other_post = Post.objects.create(
            title="Other", content="Content", category=self.category,
            institution=self.institution, status=Post.Status.APPROVED,
            submitter_contact="private2@example.com",
        )
        self.new_post = Post.objects.create(
            title="New", content="Content", category=self.category,
            institution=self.institution, status=Post.Status.APPROVED,
            submitter_contact="private3@example.com",
        )
        self.channel = Channel.objects.create(
            slug="club", name="Club", claim_contact="club@example.com",
            status=Channel.Status.ACTIVE, institution=self.institution,
        )
        self.super_user = get_user_model().objects.create_user(
            username="super", email="super@example.com", password="password"
        )
        Admin.objects.create(user=self.super_user, role=Admin.Role.SUPER_ADMIN)
        self.sponsor_user = get_user_model().objects.create_user(
            username="sponsor", email="sponsor@example.com", password="password"
        )
        Admin.objects.create(user=self.sponsor_user, role=Admin.Role.SPONSOR_VIEWER)
        self.other_sponsor = get_user_model().objects.create_user(
            username="other", email="other@example.com", password="password"
        )
        Admin.objects.create(user=self.other_sponsor, role=Admin.Role.SPONSOR_VIEWER)
        now = timezone.now()
        self.listing = SponsoredListing.objects.create(
            post=self.post, sponsor_name="Sponsor", sponsor_email="sponsor@example.com",
            placement_type=SponsoredListing.PlacementType.FEATURED_POST,
            amount_paid="100.00", starts_at=now - timedelta(days=1),
            ends_at=now + timedelta(days=1),
        )
        self.other_listing = SponsoredListing.objects.create(
            post=self.other_post, sponsor_name="Other", sponsor_email="other@example.com",
            placement_type=SponsoredListing.PlacementType.FEATURED_POST,
            amount_paid="50.00", starts_at=now - timedelta(days=1),
            ends_at=now + timedelta(days=1),
        )

    def authenticate(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_only_super_admin_can_crud_listings(self):
        self.authenticate(self.super_user)
        response = self.client.post(
            reverse("admin-sponsored-listing-list"),
            {
                "post": self.new_post.pk,
                "sponsor_name": "New Sponsor",
                "sponsor_email": "new@example.com",
                "placement_type": "featured_post",
                "amount_paid": "25.00",
                "starts_at": "2030-01-01T00:00:00Z",
                "ends_at": "2030-01-02T00:00:00Z",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        listing_id = response.data["id"]
        self.assertEqual(
            self.client.patch(
                reverse("admin-sponsored-listing-detail", args=(listing_id,)),
                {"sponsor_name": "Updated"},
                format="json",
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.delete(
                reverse("admin-sponsored-listing-detail", args=(listing_id,))
            ).status_code,
            204,
        )

        self.authenticate(self.sponsor_user)
        self.assertEqual(
            self.client.get(reverse("admin-sponsored-listing-list")).status_code, 403
        )

    def test_active_listing_features_post_and_expiry_is_checked_per_request(self):
        response = self.client.get(reverse("post-list"))
        featured = next(
            item for item in response.data["results"] if item["id"] == self.post.pk
        )
        self.assertTrue(featured["is_featured"])
        self.listing.ends_at = timezone.now() - timedelta(seconds=1)
        self.listing.save(update_fields=("ends_at",))
        response = self.client.get(reverse("post-list"))
        featured = next(
            item for item in response.data["results"] if item["id"] == self.post.pk
        )
        self.assertFalse(featured["is_featured"])

    def test_active_verified_channel_badge_and_expiry(self):
        listing = SponsoredListing.objects.create(
            channel=self.channel, sponsor_name="Sponsor",
            sponsor_email="sponsor@example.com",
            placement_type=SponsoredListing.PlacementType.VERIFIED_CHANNEL,
            amount_paid="100.00", starts_at=timezone.now() - timedelta(hours=1),
            ends_at=timezone.now() + timedelta(hours=1),
        )
        response = self.client.get(reverse("channel-list"))
        self.assertTrue(response.data["results"][0]["is_verified"])
        listing.ends_at = timezone.now() - timedelta(seconds=1)
        listing.save(update_fields=("ends_at",))
        self.assertFalse(self.client.get(reverse("channel-list")).data["results"][0]["is_verified"])

    def test_sponsor_analytics_is_limited_to_owned_listing(self):
        self.authenticate(self.sponsor_user)
        response = self.client.get(
            reverse("sponsor-listing-analytics", args=(self.listing.pk,))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["view_count"], self.post.view_count)
        self.assertEqual(
            self.client.get(
                reverse("sponsor-listing-analytics", args=(self.other_listing.pk,))
            ).status_code,
            404,
        )
