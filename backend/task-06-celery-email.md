# Backend Task 6 — Celery + Real Email Delivery

```
1. Add Celery with Redis as the broker (Redis will be provided by
   infrastructure/task-01's Docker Compose — read REDIS_URL from env).
   Configure a celery.py app instance wired into the Django project.

2. Add a periodic task (Celery Beat, every 5 minutes) that processes
   NotificationQueue rows with status="queued":
   - Groups queued rows by follower to batch same-follower notifications
     from a short window (e.g. same day) into a single digest email
     rather than one email per post.
   - Sends via Django's configured email backend (check for existing
     provider env vars — e.g. RESEND_API_KEY or SENDGRID_API_KEY —
     before assuming one; ask if neither is present rather than guessing
     a provider).
   - On success, sets status="sent", sent_at=now for every row included
     in that send.
   - On failure, increments retry_count; after 2 failed retries, sets
     status="failed" permanently.

3. Replace the stub claim-link email (Task 2's admin invite and Task 5's
   channel claim flow both need real emails) with real Celery tasks using
   the same email backend. Write simple, plain-text-leaning templates
   for: admin invite email, channel claim-link email, single-post
   notification, and batched digest.

4. Add GET /api/admin/notifications/failed/ (super_admin only) listing
   permanently-failed NotificationQueue rows for troubleshooting.

Acceptance criteria:
- A queued notification is delivered to a real test inbox within one
  Celery Beat interval and flips to status="sent".
- Two notifications queued for the same follower within the batching
  window arrive as one email, not two.
- A simulated send failure retries exactly twice before being marked
  "failed" permanently and appearing in the failed-notifications
  endpoint.
```
