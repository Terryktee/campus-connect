# Campus Loop ZW — Agent Instructions

## What this project is
A Zimbabwean student platform (Django, MySQL) where anyone can submit posts
WITHOUT logging in. Every submission goes into a moderation queue and only
becomes public after an admin approves it. Admins/moderators use Django's
real auth system via the `Admin` profile model.

## Core rules — do not violate these
- Never expose `submitter_contact`, `claim_contact`, or `reporter_contact`
  in any public view, template context, or API serializer. These fields
  are admin-only.
- Never auto-publish a post. The automated filter may only set
  `is_flagged = True` — it must never change `status` to `approved`.
- Every moderation action (approve/reject/take_down/edit/feature/verify/
  suspend/dismiss_report) must create a `ModerationAction` row. Deny
  `change`/`delete` permission on `ModerationAction` in Django Admin —
  it is an append-only audit log.
- Public views/querysets must filter to `status="approved"` (posts) or
  `status="active"` (channels) — never trust a template to hide
  unapproved content; filter at the queryset level.
- Scope moderator queryset access by `Admin.institution` — a moderator
  should never see or act on another institution's pending content, even
  via a guessed URL/object ID. Enforce this in view `get_queryset()`
  methods and in Django Admin's `get_queryset()` override, not just in
  templates.

## Stack conventions
- MySQL via `django.db.backends.mysql`, utf8mb4 charset.
- Django forms + `django.core.validators` (or `django-formtools` if useful)
  for input validation on the public submission form.
- Use Django's `django-ratelimit` package (or an equivalent) for rate
  limiting public endpoints — don't hand-roll this if a maintained package
  is already installed.
- Background jobs (email sending, notification digesting) use Celery with
  Redis as the broker, not synchronous requests.
- Environment variables via `django-environ` or `python-decouple` —
  never commit secrets to settings.py.

## When in doubt
Prefer the smaller, safer implementation. This platform accepts anonymous
public input by design — treat every new endpoint as a potential abuse
vector and validate/rate-limit accordingly.