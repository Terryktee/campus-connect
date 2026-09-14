---
applyTo: "backend/**"
---

# Backend Instructions — Django + DRF + MySQL

## Stack conventions
- MySQL via `django.db.backends.mysql`, utf8mb4 charset, all config from
  environment variables via django-environ — never hard-coded, never
  committed.
- DRF serializers + viewsets. Maintain **separate public and admin
  serializers per model** — never one serializer with conditionally
  hidden fields, since that pattern is how private fields accidentally
  leak later.
- Token/JWT auth (djangorestframework-simplejwt) for admin endpoints
  only. No public registration endpoint for the `Admin` model, ever.
- Celery + Redis for background jobs (email sending, notification
  digesting) — never send email synchronously inside a request/response
  cycle.
- `django-ratelimit` on every public-facing write endpoint (submissions,
  reports, follows).
- All cross-origin requests are handled via `django-cors-headers`, scoped
  explicitly to the frontend's known origin(s) — never
  `CORS_ALLOW_ALL_ORIGINS = True` outside local dev.

## Task order in this folder
Work through `task-01-project-setup.md` through
`task-08-sponsored-listings-api.md` in numeric order — each depends on
models/auth/endpoints established in the previous task. Do not skip ahead
to a later task's endpoints before its prerequisites are merged.

## When in doubt
This platform accepts anonymous public input by design — treat every new
endpoint as a potential abuse vector. Prefer the smaller, safer
implementation, and re-check the relevant task file's acceptance criteria
before considering any endpoint finished.
