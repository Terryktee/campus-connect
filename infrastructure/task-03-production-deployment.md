# Infrastructure Task 3 — Production Deployment

Do this last, once both apps are feature-complete and CI is green.

```
1. Write production settings overrides for the backend: DEBUG=False,
   ALLOWED_HOSTS from env, CORS_ALLOWED_ORIGINS scoped to the real
   frontend domain only, static files served via whitenoise or an
   equivalent, gunicorn as the WSGI server (add a Procfile or equivalent
   depending on the chosen host).

2. Add a health-check endpoint GET /api/health/ on the backend (checks DB
   connectivity with a trivial query) for uptime monitoring, and confirm
   the frontend has an equivalent /api/health route if the hosting
   platform needs one.

3. Document deployment targets: e.g. backend + MySQL + Redis + Celery on
   a platform that supports background workers (Railway, Render, or a
   VPS via the Docker Compose setup from infra Task 1 with a production
   compose override), frontend on Vercel (most natural fit for Next.js)
   pointed at the backend's public API URL.

4. Add robots.txt and a sitemap on the frontend covering only public
   routes, explicitly excluding /admin/*.

5. Write DEPLOYMENT.md at the repo root covering: required environment
   variables for both apps, the MySQL database-creation SQL, how to run
   migrations + seed_data against production, and how backend, celery-
   worker, celery-beat, and frontend are deployed/started in production
   (as separate services/processes).

Acceptance criteria:
- A fresh production environment, following only DEPLOYMENT.md, can be
  brought to a fully working state with no undocumented manual steps.
- /admin/* is confirmed absent from the frontend's sitemap and disallowed
  in robots.txt.
```
