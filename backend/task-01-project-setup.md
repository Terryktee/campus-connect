# Backend Task 1 — Project Setup + Models + MySQL

Paste this into Copilot agent mode with the repo's `backend/` folder open
(currently empty).

```
Set up a new Django project in this backend/ folder using Django REST
Framework and MySQL.

1. Initialize a Django project (`campusloop`) with a single app
   (`core`) containing the models below. Install: django,
   djangorestframework, mysqlclient, django-environ, django-cors-headers,
   django-filter.

2. Create these models in core/models.py:

   Institution: name, short_code (unique), city, logo_url, is_active,
   created_at

   Category: name (unique), slug (unique), description, sort_order,
   created_at

   Channel: slug (unique), name, bio, category_focus (FK Category,
   nullable), institution (FK Institution, nullable), claim_contact
   (private), claim_token (UUID, unique, auto-generated), status
   (pending/active/suspended), is_verified, follower_count, created_at,
   approved_at

   Admin: OneToOne to Django's User, role (super_admin/moderator/
   sponsor_viewer), institution (FK, nullable)

   Post: title, content, category (FK, required), institution (FK,
   nullable), channel (FK, nullable), image_url, link_url,
   submitter_name, submitter_institution, submitter_contact (required,
   private), status (pending/approved/rejected/taken_down), is_flagged,
   rejection_reason, is_featured, featured_until, view_count, created_at,
   approved_at, taken_down_at

   ModerationAction: post (FK, nullable), channel (FK, nullable), admin
   (FK Admin, required), action (approve/reject/take_down/edit/feature/
   unfeature/verify_channel/suspend_channel/dismiss_report), reason,
   note, created_at

   Report: post (FK, required), reason, reporter_contact (private),
   status (open/resolved), created_at

   Follow: follower_contact, channel (FK, nullable), category (FK,
   nullable), institution (FK, nullable), created_at — with a unique
   constraint preventing duplicate follows of the same channel or
   category+institution combo by the same follower_contact

   NotificationQueue: follow (FK), post (FK), channel
   (email/whatsapp), status (queued/sent/failed), retry_count, created_at,
   sent_at

   OrientationGuide: institution (FK, required), guide_type
   (how_to/directory_entry/campus_map_note), title, content,
   contact_info, sort_order, is_published, created_at, updated_at

   SponsoredListing: post (OneToOne, nullable), channel (FK, nullable),
   sponsor_name, placement_type (featured_post/verified_channel/banner),
   amount_paid, currency, starts_at, ends_at, created_at

   BlocklistKeyword: keyword (unique)
   AllowlistedDomain: domain (unique)

3. Configure settings.py to read all config (DB credentials, SECRET_KEY,
   DEBUG, ALLOWED_HOSTS) from environment variables via django-environ,
   with a .env.example file showing the required variable names (no real
   values committed). Configure DATABASES for MySQL with utf8mb4 charset,
   pointing at host/port/db name that will come from Docker Compose
   (see infrastructure/task-01) — use env var names DB_HOST, DB_PORT,
   DB_NAME, DB_USER, DB_PASSWORD.

4. Add django-cors-headers, configured but with CORS_ALLOWED_ORIGINS left
   as an env-driven list (empty/localhost by default), not
   CORS_ALLOW_ALL_ORIGINS.

5. Generate and apply migrations. Write a management command
   `seed_data` that idempotently creates: Institutions (UZ, NUST, MSU,
   CUT, HIT, Africa University, Chinhoyi University of Technology) and
   Categories (University News, Student Opportunities, Internships,
   Scholarships, Tech Events, Student Businesses, Coding, Careers,
   Campus Life, Orientation, Entrepreneurship, Technology).

6. Add a requirements.txt (or pyproject.toml, whichever this repo
   convention prefers) pinning the installed packages.

Acceptance criteria:
- `python manage.py migrate` runs clean against a MySQL database created
  with utf8mb4 charset.
- `python manage.py seed_data` populates institutions/categories and is
  safe to run more than once without duplicating rows.
- No secrets are hard-coded anywhere in settings.py; a fresh .env from
  .env.example plus real values is all that's needed to run locally.
```
