from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import (
    Admin,
    Category,
    Channel,
    Follow,
    Institution,
    ModerationAction,
    NotificationQueue,
    Post,
)


class ChannelsAndFollowsApiTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.institution = Institution.objects.create(
            name="One", short_code="ONE", city="Harare"
        )
        self.other_institution = Institution.objects.create(
            name="Two", short_code="TWO", city="Bulawayo"
        )
        self.category = Category.objects.create(name="News", slug="news")
        self.channel = Channel.objects.create(
            name="Campus News", slug="campus-news", claim_contact="owner@example.com",
            status=Channel.Status.ACTIVE, institution=self.institution,
        )
        user = get_user_model().objects.create_user(username="admin")
        profile = Admin.objects.create(
            user=user, role=Admin.Role.SUPER_ADMIN
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}"
        )
        self.profile = profile
        self.admin_authorization = self.client._credentials["HTTP_AUTHORIZATION"]

    def test_new_channel_submission_creates_one_pending_channel_and_links_post(self):
        self.client.credentials()
        payload = {
            "title": "New channel post",
            "content": "Content",
            "category": "news",
            "institution": "ONE",
            "channel_name": "Student Voice",
            "submitter_contact": "student@example.com",
        }
        first = self.client.post(reverse("post-submit"), payload, format="json")
        second = self.client.post(
            reverse("post-submit"),
            {**payload, "title": "Another", "submitter_contact": "other@example.com"},
            format="json",
        )
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        channel = Channel.objects.get(slug="student-voice")
        self.assertEqual(channel.status, Channel.Status.PENDING)
        self.assertEqual(Post.objects.filter(channel=channel).count(), 2)

    def test_claim_token_can_only_be_confirmed_once(self):
        self.client.credentials()
        pending = Channel.objects.create(
            name="Pending", slug="pending", claim_contact="owner@example.com"
        )
        token_url = reverse("channel-claim", args=(pending.claim_token,))
        self.assertEqual(self.client.get(token_url).status_code, 200)
        self.assertEqual(
            self.client.post(
                reverse("channel-claim-confirm", args=(pending.claim_token,)),
                {},
                format="json",
            ).status_code,
            200,
        )
        self.assertEqual(self.client.get(token_url).status_code, 404)
        self.assertEqual(self.client.post(token_url, {}, format="json").status_code, 404)

    def test_follow_unfollow_updates_channel_count_and_duplicate_is_conflict(self):
        self.client.credentials()
        payload = {"follower_contact": "student@example.com", "channel": self.channel.slug}
        self.assertEqual(self.client.post(reverse("follow"), payload, format="json").status_code, 201)
        self.channel.refresh_from_db()
        self.assertEqual(self.channel.follower_count, 1)
        self.assertEqual(self.client.post(reverse("follow"), payload, format="json").status_code, 409)
        self.assertEqual(self.client.delete(reverse("follow"), payload, format="json").status_code, 204)
        self.channel.refresh_from_db()
        self.assertEqual(self.channel.follower_count, 0)

    def test_approval_queues_matching_followers_only(self):
        self.client.credentials()
        Follow.objects.create(follower_contact="channel@example.com", channel=self.channel)
        Follow.objects.create(follower_contact="category@example.com", category=self.category)
        Follow.objects.create(
            follower_contact="same@example.com",
            category=self.category,
            institution=self.institution,
        )
        Follow.objects.create(
            follower_contact="different@example.com",
            category=self.category,
            institution=self.other_institution,
        )
        post = Post.objects.create(
            title="Approved", content="Content", category=self.category,
            institution=self.institution, channel=self.channel,
            submitter_contact="private@example.com",
        )
        self.client.credentials(HTTP_AUTHORIZATION=self.admin_authorization)
        response = self.client.post(
            reverse("admin-post-approve", args=(post.pk,)), {}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(NotificationQueue.objects.filter(post=post).count(), 3)
        self.assertEqual(
            NotificationQueue.objects.filter(post=post, status="queued").count(), 3
        )
        self.assertEqual(
            ModerationAction.objects.filter(post=post, action="approve").count(), 1
        )

    def test_public_channel_responses_never_include_private_contact_fields(self):
        self.client.credentials()
        response = self.client.get(reverse("channel-list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("claim_contact", response.data["results"][0])
