from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Admin, Category, Institution, ModerationAction, Post


class PublicReadApiTests(APITestCase):
    def setUp(self):
        self.institution = Institution.objects.create(name="One", short_code="ONE", city="Harare")
        self.category = Category.objects.create(name="News", slug="news")
        self.approved = Post.objects.create(
            title="Approved", content="Visible", category=self.category,
            institution=self.institution, submitter_contact="private@example.com",
            status=Post.Status.APPROVED,
        )
        self.pending = Post.objects.create(
            title="Pending", content="Hidden", category=self.category,
            submitter_contact="pending@example.com",
        )

    def test_feed_and_detail_only_return_approved_posts(self):
        response = self.client.get(reverse("post-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["id"] for item in response.data["results"]], [self.approved.pk])
        self.assertNotIn("submitter_contact", response.data["results"][0])

        self.assertEqual(
            self.client.get(reverse("post-detail", args=(self.pending.pk,))).status_code, 404
        )
        detail = self.client.get(reverse("post-detail", args=(self.approved.pk,)))
        self.assertEqual(detail.status_code, 200)
        self.assertNotIn("submitter_contact", detail.data)
        self.assertEqual(detail.data["view_count"], 1)

    def test_feed_filters_by_category_and_institution_and_search(self):
        self.assertEqual(
            self.client.get(reverse("post-list"), {"category": "missing"}).data["count"], 0
        )
        self.assertEqual(
            self.client.get(reverse("post-list"), {"institution": "ONE"}).data["count"], 1
        )
        self.assertEqual(
            self.client.get(reverse("post-list"), {"search": "visible"}).data["count"], 1
        )

    def test_public_report_response_does_not_echo_reporter_contact(self):
        response = self.client.post(
            reverse("post-report", args=(self.approved.pk,)),
            {"reason": "This is not appropriate.", "reporter_contact": "reporter@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("reporter_contact", response.data)


class ScopedModerationApiTests(APITestCase):
    def setUp(self):
        self.one = Institution.objects.create(name="One", short_code="ONE", city="Harare")
        self.two = Institution.objects.create(name="Two", short_code="TWO", city="Bulawayo")
        category = Category.objects.create(name="News", slug="news")
        self.foreign_post = Post.objects.create(
            title="Foreign", content="Content", category=category,
            institution=self.two, submitter_contact="x@example.com",
        )
        user = get_user_model().objects.create_user(username="moderator", password="secret123")
        self.profile = Admin.objects.create(user=user, role=Admin.Role.MODERATOR, institution=self.one)
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_moderator_cannot_act_on_foreign_post_by_id(self):
        response = self.client.post(
            reverse("admin-post-approve", args=(self.foreign_post.pk,)), format="json"
        )
        self.assertEqual(response.status_code, 404)
        self.foreign_post.refresh_from_db()
        self.assertEqual(self.foreign_post.status, Post.Status.PENDING)
        self.assertFalse(ModerationAction.objects.exists())

    def test_reject_requires_reason(self):
        own_post = Post.objects.create(
            title="Own", content="Content", category=self.foreign_post.category,
            institution=self.one, submitter_contact="own@example.com",
        )
        response = self.client.post(
            reverse("admin-post-reject", args=(own_post.pk,)), {}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(ModerationAction.objects.exists())
