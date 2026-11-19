# Loop: Repository Architecture & Security Audit

**Date:** 2026-10-09  
**Branch:** `loop/build`  
**Auditor:** Loop Build Agent  
**Scope:** Full repository (`backend/`, `frontend/`, `infrastructure/`, `docs/`)

---

## 1. Executive Summary

Loop (formerly Campus Loop ZW / CampusConnect ZW) is transitioning from a Zimbabwe-specific university noticeboard to an open-source, no-account social platform for youth worldwide. This audit inspects the current codebase, identifies architectural strengths, highlights security vulnerabilities and technical debt, and lays out a prioritized remediation plan.

---

## 2. Architecture & Component Inventory

### 2.1 Backend (`backend/`)
- **Framework:** Django 5.2.6 + Django REST Framework (DRF) 3.16.1
- **Project package:** `backend/campusloop/`
  - Settings: `settings.py` (local/compose) and `settings_production.py` (production overrides with WhiteNoise, secure cookies, HSTS)
  - Async/Task processing: Celery 5.5.3 (`celery.py`) with Redis 6.4.0 broker/backend
  - ASGI/WSGI: `asgi.py`, `wsgi.py`
- **Application Apps:**
  - `core`: Single monolithic app handling models, views, serializers, tasks, and permissions.
  - Future planned apps per `LOOP_PLAN.md`: `identity`, `media`, `social`, `analytics`, `rewards`, `market`, `news`.
- **Database:** MySQL 8.0 (`utf8mb4`) as primary production/docker engine; SQLite used for local fast testing.

### 2.2 Data Models (`core/models.py`)
1. **`Institution`**: Educational institutions/campuses (`name`, `short_code`, `city`, `logo_url`, `is_active`).
2. **`Category`**: Post classifications (`name`, `slug`, `description`, `sort_order`).
3. **`Channel`**: Verified or student-managed channels (`slug`, `name`, `bio`, `claim_contact`, `claim_token`, `status`, `is_verified`, `follower_count`).
4. **`Admin`**: Staff profile attached to Django `User` (`role`: `super_admin`, `moderator`, `sponsor_viewer`).
5. **`Post`**: Content items (`title`, `content`, `status`, `is_flagged`, `is_featured`, `view_count`, submitter metadata).
6. **`ModerationAction`**: Audit log of moderation decisions (`approve`, `reject`, `take_down`, `feature`, `verify_channel`, etc.).
7. **`Report`**: Content flags submitted by users.
8. **`Follow`**: Follow subscriptions linking a contact to channel, category, and institution.
9. **`NotificationQueue`**: Outbound email and WhatsApp delivery queue processed by Celery.
10. **`OrientationGuide`**: Campus guides (`how_to`, `directory_entry`, `campus_map_note`).
11. **`SponsoredListing`**: Paid promotions with analytics.
12. **`BlocklistKeyword`** & **`AllowlistedDomain`**: Simple content filter lists.

### 2.3 API Endpoints (`backend/campusloop/urls.py`)
- **System:** `GET /api/health/` (database probe)
- **Admin Authentication:** `POST /api/auth/login/`, `POST /api/auth/refresh/` (SimpleJWT)
- **Admin Management:** `GET /api/admin/me/`, `POST /api/admin/invite/`, `GET /api/admin/notifications/failed/`
- **Public Posts:**
  - `POST /api/posts/submit/` (anonymous post submission with rate limiting and honeypot)
  - `GET /api/posts/` (feed filtering by category, institution, search)
  - `GET /api/posts/<id>/` (increments `view_count`)
  - `POST /api/posts/<id>/report/`
- **Public Catalogs:** `GET /api/categories/`, `GET /api/institutions/`, `GET /api/orientation/<short_code>/`
- **Channels & Follows:** `GET /api/channels/`, `GET/POST /api/channels/claim/<token>/`, `GET /api/channels/<slug>/`, `POST/DELETE /api/follow/`
- **Admin Moderation & Management:**
  - Posts: `GET /api/admin/posts/`, `/approve/`, `/reject/`, `/take_down/`, `/feature/`, `/unfeature/`
  - Channels: `POST /api/admin/channels/<id>/<action>/`
  - Reports: `GET /api/admin/reports/`, `POST /api/admin/reports/<id>/<action>/`
  - Audit log: `GET /api/admin/moderation-actions/`
  - Sponsored listings: `GET/POST /api/admin/sponsored-listings/`, `GET /api/sponsor/my-listing/<id>/`

### 2.4 Frontend (`frontend/`)
- **Framework:** Next.js 16.3.3 (App Router) + React 19 + TypeScript 5.7.3 + Tailwind CSS v4.
- **Routing:**
  - Public pages: `/`, `/post/[id]`, `/channels`, `/channels/new`, `/channels/claim/[token]`, `/events`, `/orientation`, `/profiles`, `/submit`, `/guidelines`, `/privacy`, `/contact`
  - Admin: `/admin/login`, `/admin` (dashboard, reports, moderation queue)
  - API proxy: `/api/admin-proxy/[...path]` (handles HTTP-only cookie JWT translation)
- **Components:**
  - `campus-app.tsx`: monolithic historical client component
  - `public-api-pages.tsx`: API-integrated client view
  - `admin-dashboard.tsx`: admin desk view

---

## 3. Vulnerability & Security Findings

| Severity | Issue | Location | Remediation |
|---|---|---|---|
| **HIGH** | **Hot row counter race condition (`view_count`)** | `core/views.py:PublicPostDetailView` | Direct database `UPDATE` on post views locks rows under load. Must be replaced with Redis HyperLogLog / atomic Redis counters and Celery batched flush (planned for Task 05). |
| **HIGH** | **Lack of 2FA / TOTP for Admin accounts** | `core/authentication.py`, `/api/auth/login/` | Admin logins currently use single-factor password authentication. Standing Rule 12 and Task 02 require TOTP 2FA. |
| **MEDIUM** | **Hardcoded regional phone validation** | `core/serializers.py:validate_submitter_contact` | Validation regex strictly checked Zimbabwean `+263` numbers, rejecting global users. Must support international formats. |
| **MEDIUM** | **Hardcoded Timezone** | `backend/campusloop/settings.py` | `TIME_ZONE = "Africa/Harare"` hardcoded in settings without env fallback. Made configurable via `DJANGO_TIME_ZONE`. |
| **LOW** | **Package namespace coupling** | `backend/campusloop/` | Project package named `campusloop`. Renaming the directory would break imports, wsgi, asgi, Dockerfiles, and Celery worker commands across production deployments. Keep internal module name `campusloop` while renaming all user-facing branding. |
| **LOW** | **Missing dev dependency configurations** | `backend/` | Missing `requirements-dev.txt` for `ruff`, `pytest`, `pytest-django`, `pytest-cov`. |

---

## 4. Renaming & Brand Alignment Assessment

- **Internal Django project directory:** Kept as `campusloop` to preserve deployment compatibility, imports, and migrations.
- **Frontend package:** Renamed from placeholder `my-project` to `loop` in `package.json`.
- **Public UI and Meta tags:** All references to "CampusConnect ZW", "Campus Loop ZW", and Zimbabwe-specific taglines updated to "Loop" and global youth messaging.
- **Email notifications:** Default sender changed to `noreply@loop.example`, subjects updated to "Loop admin invitation", "Claim your Loop channel", "New Loop post".
- **Database tables:** Preserved without renaming (`core_*`) per Standing Rule 11.

---

## 5. Prioritized Remediation Roadmap

1. **Phase 1 (Immediate - Tasks 01 & 12):**
   - Generalize country/community assumptions; update brand copy across frontend and backend.
   - Establish CI/CD pipeline (`.github/workflows/ci-cd.yml`), Dependabot, dev dependencies (`requirements-dev.txt`), and deployment guide (`docs/DEPLOY.md`).
2. **Phase 2 (Identity & Crypto - Task 02):**
   - Account-less Ed25519 cryptographic identity, BIP-39 recovery phrase, device transfer, admin TOTP.
3. **Phase 3 (Media & Content - Tasks 03 to 05):**
   - S3/R2 direct uploads, EXIF stripping, CSAM/NSFW scanning stub, audio transcription.
   - Reactions (Like/Nah), snapshots (`/s/{id}`), Redis view counters and analytics.
4. **Phase 4 (Engagement & Commerce - Tasks 06 to 08):**
   - Pulse algorithm, Aura scoring, Ama2K Fame Status ladder, Loop Points rewards ledger.
   - Marketplace and News modules.
5. **Phase 5 (Polish & Release - Tasks 09 to 14):**
   - Admin UI overhaul, Loop wordmark brand kit, SEO/JSON-LD, full-text search, secrets audit.
