# Loop: Autonomous Task Queue

Put this file at `docs/TASKS.md`. The agent reads it, works through the unchecked tasks in order, ticks them off, and logs progress. Nobody should need to paste prompts.

**Sources of truth:** `docs/LOOP_PLAN.md` (what to build, algorithms, prompts in section 10) and `AGENTS.md` at the repo root (standing rules). This file says *in what order* and *how to run*.

## How to run (the agent must follow this)

1. Read `AGENTS.md`, `docs/LOOP_PLAN.md`, `docs/RUN-LOG.md`, and this file.
2. Work on the single branch `loop/build` (create it from `main` if missing). Never touch `main`. Never force-push.
3. Take the first unchecked task whose model tag matches the model you are running as:
   - `[S]` = Claude Sonnet 4.6
   - `[O]` = Claude Opus 4.6
   - `[G]` = GPT-OSS
   - `[F]` = Gemini 3.8 Flash 
   If the first unchecked task is tagged for a different model, **stop** and write one line in `docs/RUN-LOG.md`: `Next task is NN, needs [X] model.` Do not skip ahead.
4. For each task: implement it fully using the matching prompt in `docs/LOOP_PLAN.md` section 10 (the prompt text is the spec), add tests, run the checks below, fix failures, then make one commit: `loop(NN): <task name>`.
5. After the commit: tick the box here, append a dated entry to `docs/RUN-LOG.md` (what changed, assumptions, follow-up risks), then continue to the next matching task without waiting for me.
6. **Never stop to ask questions.** If something is ambiguous, pick the safest assumption and record it in `docs/RUN-LOG.md`. If you need something only a human can provide (API keys, R2 bucket, scanner provider account, Railway/Vercel secrets), build against a stub or interface, then add a line to `docs/NEEDS-HUMAN.md` and keep going.
7. If a check cannot pass after 3 honest attempts, revert that task's uncommitted changes, log the blocker in `docs/RUN-LOG.md`, mark the task `BLOCKED` here, and move on.

### Checks before every commit

```bash
cd backend && ruff check . && python manage.py makemigrations --check --dry-run && python manage.py test   # use pytest if configured
cd ../frontend && npm run lint && npx tsc --noEmit && npm run build
```

If a tool is missing (for example `ruff`), add it to the dev requirements rather than skipping the check.

## Real repo layout (overrides the generic paths in LOOP_PLAN.md)

- Django project: `backend/campusloop/` (settings in `settings.py`, `settings_production.py`; there is no `config/` package). Rename it to `loop` only if the audit says it is safe, otherwise keep it and only change user-facing names.
- Single app today: `backend/core/` (models, views, serializers, tasks, `authentication.py`, `permissions.py`, tests in `core/tests/`). **Add new Django apps** instead of bloating `core`: `identity`, `media`, `social` (reactions, comments, snapshots), `analytics`, `rewards`, `market`, `news`. Keep the existing `core` models (channels, follows, sponsored listings, moderation actions, events, orientation) unless the audit finds a reason to migrate them.
- Existing admin auth lives in `core/authentication.py` and `frontend/app/admin/*` and `app/api/admin-proxy`. Keep it for admins and moderators (add TOTP). Public users use the new account-less identity.
- Frontend: `frontend/app/` (Next.js app router). Big components are `components/campus-app.tsx`, `components/admin-dashboard.tsx`, `components/public-api-pages.tsx`. Break these into smaller components as you touch them. API helpers are in `lib/api.ts`.
- Deployment files: `backend/Dockerfile`, `backend/Procfile`, `backend/entrypoint.sh`, `frontend/Dockerfile`, `infrastructure/starter-files/`, and `docs/docker-compose.yml`. Make Docker Compose live at the repo root and make the README commands match.
- Docs live in `docs/`. Do not duplicate: merge `docs/00-README.md` and `docs/README.md` into the root `README.md`, and move `docs/AGENTS.md`/`docs/CLAUDE.md` content into the root `AGENTS.md`.

## Task 0: Hygiene (do this first, tag [S])

- [x] **00 Hygiene.** Add a proper root `.gitignore` (Python caches, `__pycache__`, `*.pyc`, `celerybeat-schedule`, `.env*` except examples, `node_modules`, `.next`). Run `git rm -r --cached` on tracked `__pycache__` and `backend/celerybeat-schedule`. Make sure no real secrets exist in tracked files, and list any in `docs/NEEDS-HUMAN.md` for rotation. Commit.

## Queue (order matters; do not reorder)

- [x] **01 [F] Audit and rename.** Prompt 1. Rename to Loop in user-facing names, replace ZW-only assumptions with a configurable country/community model, write `docs/AUDIT.md`, rewrite root `README.md`.
- [x] **12 [F] CI/CD.** Prompt 12 adapted to the real paths above (`backend/`, `frontend/`, Railway services web/worker/beat, Vercel root `frontend`). Add `docs/DEPLOY.md`.
- [ ] **02 [O] Account-less identity.** Prompt 2. Includes recovery phrase, device transfer, `.loopkey` backup, device list, abuse controls, admin TOTP, `docs/IDENTITY.md`.
- [ ] **03 [S] Images and audio.** Prompt 3.
- [ ] **04 [S] Reactions, comments, snapshots.** Prompt 4.
- [ ] **05 [S] Per-post analytics (public + admin).** Prompt 5.
- [ ] **06 [O] Pulse, Aura, Ama2K Fame Status, Loop Points rewards.** Prompt 6. Use `docs/LOOP_PLAN.md` sections 2.1 to 2.4 directly.
- [ ] **07 [S] Marketplace.** Prompt 7.
- [ ] **08 [F] News.** Prompt 8.
- [ ] **09 [S] Admin panel redo (UI/UX).** Prompt 9. Replace the monolithic `admin-dashboard.tsx` with routed pages and small components.
- [ ] **10 [F] Brand and design system.** Prompt 10. Wordmark SVGs go in `frontend/public/brand/`.
- [ ] **11 [F] SEO and performance.** Prompt 11. Extend the existing `robots.ts` and `sitemap.ts`.
- [ ] **13 [F] Global search and moderation completeness.** Prompt 13.
- [ ] **14 [O] Open-source readiness and secrets review.** Prompt 14. Docs may be drafted with `[G]`, but the secrets review and the final checklist are `[O]`.

## Definition of done for the whole build

- All boxes above ticked or marked BLOCKED with a reason in `docs/RUN-LOG.md`.
- `docs/NEEDS-HUMAN.md` lists every key, account, or provider I must set up.
- The checks above pass on `loop/build`.
- `docs/RUN-LOG.md` ends with a short "What to test manually" list.