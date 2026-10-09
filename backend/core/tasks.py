from collections import defaultdict
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from .models import NotificationQueue


def _send_template_email(subject, template, recipient, context):
    send_mail(
        subject,
        render_to_string(template, context),
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        fail_silently=False,
    )


@shared_task
def send_admin_invite_email(recipient, invite_link, recipient_name=""):
    _send_template_email(
        "Loop admin invitation",
        "emails/admin_invite.txt",
        recipient,
        {"invite_link": invite_link, "recipient_name": recipient_name},
    )


@shared_task
def send_channel_claim_email(recipient, channel_name, claim_link):
    _send_template_email(
        "Claim your Loop channel",
        "emails/channel_claim.txt",
        recipient,
        {"channel_name": channel_name, "claim_link": claim_link},
    )


@shared_task
def send_post_notification_email(recipient, post_id, title, content):
    _send_template_email(
        "New Loop post",
        "emails/post_notification.txt",
        recipient,
        {"post_id": post_id, "title": title, "content": content},
    )


def _notification_context(rows):
    return {
        "notifications": [
            {"title": row.post.title, "content": row.post.content, "post_id": row.post_id}
            for row in rows
        ]
    }


@shared_task
def process_notification_queue(now=None):
    now = now or timezone.now()
    window_start = now - timedelta(days=1)
    rows = list(
        NotificationQueue.objects.filter(
            status=NotificationQueue.Status.QUEUED,
            channel=NotificationQueue.Channel.EMAIL,
            created_at__gte=window_start,
        ).select_related("follow", "post")
    )
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row.follow.follower_contact, row.created_at.date())].append(row)

    sent = 0
    failed = 0
    for (recipient, _created_date), batch in grouped.items():
        try:
            template = (
                "emails/post_notification.txt"
                if len(batch) == 1
                else "emails/notification_digest.txt"
            )
            subject = (
                "New Loop post"
                if len(batch) == 1
                else f"{len(batch)} new Loop posts"
            )
            context = (
                {
                    "post_id": batch[0].post_id,
                    "title": batch[0].post.title,
                    "content": batch[0].post.content,
                }
                if len(batch) == 1
                else _notification_context(batch)
            )
            _send_template_email(subject, template, recipient, context)
        except Exception:
            for row in batch:
                row.retry_count += 1
                if row.retry_count >= 2:
                    row.status = NotificationQueue.Status.FAILED
                    failed += 1
                row.save(update_fields=("retry_count", "status"))
            continue

        NotificationQueue.objects.filter(pk__in=[row.pk for row in batch]).update(
            status=NotificationQueue.Status.SENT, sent_at=now
        )
        sent += len(batch)
    return {"sent": sent, "failed": failed}
