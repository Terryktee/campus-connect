# Campus Loop ZW — Development Plan (Decoupled Architecture)

This is the master index. It maps to your three repo folders — `/frontend`,
`/backend`, `/infrastructure` — and points to one task file per unit of
work. Give the agent **one task file at a time**, in order within each
folder; don't paste multiple tasks in one go.

## Architecture

```
┌─────────────────┐        REST API (JSON)        ┌──────────────────┐
│    frontend/     │ ───────────────────────────▶  │     backend/      │
│  Next.js + Tailwind│ ◀───────────────────────────  │  Django + DRF      │
│  (public site +   │                                │  + MySQL           │
│   admin UI)        │                                │  + Celery + Redis  │
└─────────────────┘                                └──────────────────┘
         │                                                    │
         └───────────────── deployed via ───────────────────┘
                                    │
                          ┌──────────────────┐
                          │ infrastructure/   │
                          │ Docker, CI/CD,     │
                          │ hosting configs    │
                          └──────────────────┘
```

- **backend/** — Django REST Framework API + MySQL. Owns all data, all
  moderation logic, all business rules. The admin/moderation panel is a
  set of authenticated API endpoints consumed by the frontend's `/admin`
  section (not Django's built-in template-based Admin, since the frontend
  is decoupled — see backend Task 2).
- **frontend/** — Next.js (from the earlier v0 scaffold, currently built
  against mock data). These tasks replace the mock data with real calls to
  the backend API, add real admin auth, and wire up submission/follow/
  moderation flows end to end.
- **infrastructure/** — Docker Compose for local dev (Django + MySQL +
  Redis + Next.js together), CI/CD pipeline, and production deployment
  configs.

## Suggested Build Order

1. **infrastructure/task-01** — Docker Compose local dev environment first,
   so `backend/` and `frontend/` have somewhere to actually run against
   each other from day one instead of each dev guessing at ports/env vars.
2. **backend/task-01 → task-08** — build the API in order; each depends on
   the last (auth before submission validation, submission before the
   public read API, etc.).
3. **frontend/task-01 → task-05** — can start as soon as backend task-01
   (project setup) and task-04 (public read API) exist; doesn't need to
   wait for the entire backend to finish. Realistically these two tracks
   run in parallel once the API contract for a given feature is stable.
4. **infrastructure/task-02, task-03** — CI/CD and production deployment,
   once both sides are feature-complete.

## Folder Contents

### `backend/`
| File | Covers |
|---|---|
| `task-01-project-setup.md` | Django + DRF + MySQL project scaffold, models, migrations |
| `task-02-admin-auth-roles.md` | Token/JWT auth for admins, role + institution scoping |
| `task-03-submission-api.md` | Public submission endpoint: validation, rate limiting, auto-filter |
| `task-04-public-read-api.md` | Public feed/post-detail/category endpoints, private-field exclusion |
| `task-05-channels-follows-api.md` | Channel claim flow, follow endpoints, notification enqueueing |
| `task-06-celery-email.md` | Celery + Redis, real email delivery, digest batching |
| `task-07-orientation-api.md` | Orientation Hub CRUD + public endpoints |
| `task-08-sponsored-listings-api.md` | Sponsored listings, featured/verified badges, sponsor analytics endpoint |

### `frontend/`
| File | Covers |
|---|---|
| `task-01-connect-api.md` | Replace mock data with real fetch calls to the backend API |
| `task-02-admin-dashboard-auth.md` | Admin login UI, token storage, protected `/admin` routes, role-based UI |
| `task-03-submission-form-integration.md` | Wire the public submit form to the real API, handle validation/rate-limit errors |
| `task-04-channels-follow-ui.md` | Channel pages, claim-link page, follow buttons wired to the API |
| `task-05-orientation-hub-integration.md` | Orientation Hub pulling real data, institution picker |

### `infrastructure/`
| File | Covers |
|---|---|
| `task-01-docker-compose-local-dev.md` | Docker Compose: MySQL, Redis, Django, Next.js, one command to run everything |
| `task-02-ci-cd-pipeline.md` | GitHub Actions: lint/test both apps, build images on merge |
| `task-03-production-deployment.md` | Production hosting config, env/secrets management, health checks |

## Repo-Level Copilot Instructions

Also create `.github/copilot-instructions.md` at the **repo root** (covers
all three folders) using the content in `_shared/copilot-instructions.md`
in this plan. Copilot's agent reads this automatically on every task
regardless of which folder you're working in.

## Progress Tracking

Check these off as each task file is completed and merged:

**Infrastructure**
- [ ] infra-01 Docker Compose local dev

**Backend**
- [ ] backend-01 Project setup
- [ ] backend-02 Admin auth + roles
- [ ] backend-03 Submission API
- [ ] backend-04 Public read API
- [ ] backend-05 Channels + follows API
- [ ] backend-06 Celery + email
- [ ] backend-07 Orientation API
- [ ] backend-08 Sponsored listings API

**Frontend**
- [ ] frontend-01 Connect to API
- [ ] frontend-02 Admin dashboard auth
- [ ] frontend-03 Submission form integration
- [ ] frontend-04 Channels/follow UI
- [ ] frontend-05 Orientation Hub integration

**Infrastructure (later)**
- [ ] infra-02 CI/CD pipeline
- [ ] infra-03 Production deployment
