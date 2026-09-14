from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from core.models import AllowlistedDomain, BlocklistKeyword, Category, Post


class PublicSubmissionApiTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.category = Category.objects.create(name="News", slug="news")
        self.url = reverse("post-submit")
        self.payload = {
            "title": "Campus update",
            "content": "The library is open today.",
            "category": "news",
            "submitter_name": "Student",
            "submitter_contact": "student@example.com",
        }

    def test_submission_is_pending_and_response_is_minimal(self):
        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response.data), {"id", "status"})
        self.assertEqual(response.data["status"], "pending")
        self.assertNotIn("submitter_contact", response.data)
        self.assertEqual(Post.objects.get(pk=response.data["id"]).status, Post.Status.PENDING)

    def test_blocklisted_submission_is_flagged_but_not_blocked(self):
        BlocklistKeyword.objects.create(keyword="scam")
        response = self.client.post(
            self.url,
            {**self.payload, "title": "Possible SCAM alert"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        post = Post.objects.get(pk=response.data["id"])
        self.assertEqual(post.status, Post.Status.PENDING)
        self.assertTrue(post.is_flagged)

    def test_unallowlisted_url_is_flagged_and_allowlisted_url_is_not(self):
        AllowlistedDomain.objects.create(domain="trusted.example")
        flagged = self.client.post(
            self.url,
            {**self.payload, "link_url": "https://untrusted.example/item"},
            format="json",
        )
        allowed = self.client.post(
            self.url,
            {
                **self.payload,
                "submitter_contact": "other@example.com",
                "link_url": "https://trusted.example/item",
            },
            format="json",
        )

        self.assertTrue(Post.objects.get(pk=flagged.data["id"]).is_flagged)
        self.assertFalse(Post.objects.get(pk=allowed.data["id"]).is_flagged)

    def test_sixth_submission_for_contact_is_rate_limited(self):
        for index in range(5):
            response = self.client.post(
                self.url,
                {**self.payload, "title": f"Update {index}"},
                format="json",
            )
            self.assertEqual(response.status_code, 201)

        response = self.client.post(self.url, self.payload, format="json")

        self.assertEqual(response.status_code, 429)
        self.assertEqual(
            response.data["error"],
            "Submission limit reached. Please try again later.",
        )

    def test_invalid_contact_is_rejected(self):
        response = self.client.post(
            self.url,
            {**self.payload, "submitter_contact": "not-a-contact"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("submitter_contact", response.data)

    def test_honeypot_returns_success_without_saving(self):
        response = self.client.post(
            self.url,
            {**self.payload, "website": "https://bot.example"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "received"})
        self.assertEqual(Post.objects.count(), 0)
