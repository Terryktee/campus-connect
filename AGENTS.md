# AGENTS.md: Loop

Loop (formerly Campus Loop ZW) is an open-source, no-account social platform for youth worldwide. Moderated, low-bandwidth friendly, safe by default.

## Stack and layout

- Backend: Django + DRF + Celery + Redis + MySQL in `backend/` (project `campusloop/`, app `core/`; new features go in new apps).
- Frontend: Next.js (app router) + TypeScript + React in `frontend/`.
- Deploy: Railway (backend: web, worker, beat) and Vercel (frontend, root `frontend/`). CI/CD in `.github/workflows/`.
- Specs: `docs/LOOP_PLAN.md`. Work queue: `docs/TASKS.md`. Progress log: `docs/RUN-LOG.md`. Human-only to-dos: `docs/NEEDS-HUMAN.md`.

## Standing rules

1. Work only on branch `loop/build`. Small commits, one per task. Never push to or modify `main`. Never force-push.
2. Never commit secrets. Use env vars and keep `.env.example` files placeholder-only.
3. Every feature ships with tests. Backend: `python manage.py test` (or pytest if configured). Frontend: lint, `tsc --noEmit`, build, plus Vitest/Playwright where relevant.
4. Run all checks before each commit and fix failures. Do not skip a check because a tool is missing; install it as a dev dependency.
5. Never store raw IPs beyond short rate-limit windows. Strip EXIF/GPS from uploaded images. Never expose a minor's exact location.
6. Hot counters go through Redis and are aggregated in batches. No `UPDATE count = count + 1` on busy rows.
7. All user content (posts, comments, profiles, products, news) must be reportable and moderatable (delete, hide, suspend, ban) and every moderation action is audit-logged.
8. Mobile-first, low-data friendly, accessible (WCAG AA), strings ready for translation (English, Shona, Ndebele first).
9. Do not bloat `core`. Create focused Django apps and small React components; split files over about 400 lines.
10. Do not ask the human questions mid-task. Choose the safest assumption, log it in `docs/RUN-LOG.md`, and continue. Needs from a human go in `docs/NEEDS-HUMAN.md`.
11. Do not rename database tables or break existing migrations. Add new migrations only.
12. Admin and moderator accounts keep real authentication (password + TOTP). Public users are account-less (key-based identity).

## When finishing any task

Update the checkbox in `docs/TASKS.md`, append to `docs/RUN-LOG.md` (what changed, assumptions, follow-up risks), and move to the next task that matches your model tag.