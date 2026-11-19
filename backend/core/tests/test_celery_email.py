from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import (
    Admin,
    Category,
    Follow,
    Institution,
    NotificationQueue,
    Post,
)
from core.tasks import process_notification_queue


class CeleryEmailTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name="News", slug="news")
        self.institution = Institution.objects.create(
            name="One", short_code="ONE", city="Harare"
        )
        self.post = Post.objects.create(
            title="Campus update",
            content="A useful update",
            category=self.category,
            institution=self.institution,
            submitter_contact="private@example.com",
        )
        self.follow = Follow.objects.create(
            follower_contact="student@example.com", category=self.category
        )
        self.admin_user = get_user_model().objects.create_user(
            username="superadmin", password="secret123"
        )
        Admin.objects.create(user=self.admin_user, role=Admin.Role.SUPER_ADMIN)
        token = RefreshToken.for_user(self.admin_user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    @patch("core.tasks.send_mail")
    def test_queued_notification_is_sent_and_marked_sent(self, send_mail):
        NotificationQueue.objects.create(
            follow=self.follow, post=self.post, channel=NotificationQueue.Channel.EMAIL
        )

        result = process_notification_queue()

        self.assertEqual(result["sent"], 1)
        row = NotificationQueue.objects.get()
        self.assertEqual(row.status, NotificationQueue.Status.SENT)
        self.assertIsNotNone(row.sent_at)
        send_mail.assert_called_once()

    @patch("core.tasks.send_mail")
    def test_same_follower_notifications_are_batched(self, send_mail):
        second_post = Post.objects.create(
            title="Second update",
            content="Another useful update",
            category=self.category,
            institution=self.institution,
            submitter_contact="private@example.com",
        )
        NotificationQueue.objects.bulk_create(
            [
                NotificationQueue(
                    follow=self.follow,
                    post=post,
                    channel=NotificationQueue.Channel.EMAIL,
                )
                for post in (self.post, second_post)
            ]
        )

        process_notification_queue()

        self.assertEqual(send_mail.call_count, 1)
        self.assertIn("2 new Loop posts", send_mail.call_args.args[0])
        self.assertEqual(
            NotificationQueue.objects.filter(status=NotificationQueue.Status.SENT).count(), 2
        )

    @patch("core.tasks.send_mail", side_effect=RuntimeError("SMTP unavailable"))
    def test_notification_fails_after_exactly_two_attempts(self, send_mail):
        NotificationQueue.objects.create(
            follow=self.follow, post=self.post, channel=NotificationQueue.Channel.EMAIL
        )

        process_notification_queue()
        row = NotificationQueue.objects.get()
        self.assertEqual(row.status, NotificationQueue.Status.QUEUED)
        self.assertEqual(row.retry_count, 1)

        process_notification_queue()
        row.refresh_from_db()
        self.assertEqual(row.status, NotificationQueue.Status.FAILED)
        self.assertEqual(row.retry_count, 2)
        self.assertEqual(send_mail.call_count, 2)

        response = self.client.get(reverse("admin-notifications-failed"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertNotIn("follower_contact", response.data[0])

    def test_failed_notifications_require_super_admin(self):
        moderator_user = get_user_model().objects.create_user(
            username="moderator", password="secret123"
        )
        Admin.objects.create(
            user=moderator_user,
            role=Admin.Role.MODERATOR,
            institution=self.institution,
        )
        token = RefreshToken.for_user(moderator_user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(reverse("admin-notifications-failed"))

        self.assertEqual(response.status_code, 403)
