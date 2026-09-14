# Campus Loop ZW — Agent Instructions

Copy this file to `.github/copilot-instructions.md` at the repo root.

## What this project is
A Zimbabwean student platform with a **decoupled architecture**:
- `backend/` — Django + Django REST Framework + MySQL. Owns all data and
  business logic, exposed as a JSON API.
- `frontend/` — Next.js. Public site + admin dashboard, consumes the
  backend API only — no direct database access, no server-rendered Django
  templates for end users.
- `infrastructure/` — Docker Compose (local dev), CI/CD, and production
  deployment configuration for both apps together.

Anyone can submit a post to the platform WITHOUT logging in. Every
submission goes into a moderation queue and only becomes public after an
admin approves it via the frontend's `/admin` dashboard, which calls
authenticated backend endpoints. Admins/moderators have real accounts;
public posters/followers never do.

## Core rules — do not violate these
- Never serialize `submitter_contact`, `claim_contact`, or
  `reporter_contact` in any public-facing API response. These fields are
  admin-only and must be excluded at the DRF serializer level (separate
  public vs. admin serializers per model, not a single serializer with
  conditional field hiding).
- Never auto-publish a post. The automated filter may only set
  `is_flagged = True` — it must never change `status` to `approved`.
- Every moderation action (approve/reject/take_down/edit/feature/verify/
  suspend/dismiss_report) must create a `ModerationAction` row via the
  API, and that model must be append-only (no PATCH/DELETE endpoint or
  admin permission for it, ever).
- Public API endpoints must filter to `status="approved"` (posts) or
  `status="active"` (channels) at the queryset level — never rely on the
  frontend to hide unapproved content.
- Scope moderator access by `Admin.institution` on the backend, enforced
  in the view/permission class — never trust the frontend to only request
  scoped data; the backend must reject out-of-scope requests even if the
  frontend UI wouldn't normally send them.
- All cross-origin requests from `frontend/` to `backend/` must go through
  `django-cors-headers`, explicitly scoped to the frontend's known
  origin(s) — never `CORS_ALLOW_ALL_ORIGINS = True` outside local dev.

## Stack conventions
- **Backend:** MySQL via `django.db.backends.mysql`, utf8mb4 charset.
  DRF serializers + viewsets. Token or JWT auth (`djangorestframework-
  simplejwt` is a reasonable default) for admin endpoints only. Celery +
  Redis for background jobs (email, notification digesting).
  `django-ratelimit` for public endpoint rate limiting.
- **Frontend:** Next.js App Router, TypeScript, Tailwind, shadcn/ui.
  Server Actions or route handlers may proxy to the backend API where it
  helps hide the API base URL/keep tokens server-side — never expose an
  admin auth token to client-side JS.
- **Infrastructure:** Docker Compose for local dev with one command to
  bring up MySQL + Redis + backend + frontend together. Environment
  variables for all secrets in both apps — never committed.

## When in doubt
Prefer the smaller, safer implementation. This platform accepts anonymous
public input by design — treat every new backend endpoint as a potential
abuse vector and validate/rate-limit accordingly. When frontend and backend
disagree on validation, the backend's check is the one that actually
matters; frontend validation is a UX nicety, not a security boundary.
