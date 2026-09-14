# Infrastructure Task 1 — Docker Compose Local Dev

Do this first, before backend or frontend tasks — gives both apps
somewhere to run against each other consistently.

```
Create a docker-compose.yml at the repo root (referencing backend/ and
frontend/ as build contexts) that brings up:

1. mysql — MySQL 8, utf8mb4 charset, with a named volume for data
   persistence, exposing 3306, environment variables for root password
   and the app database name/user/password (matching what backend
   Task 1 expects: DB_HOST=mysql, DB_PORT=3306, DB_NAME, DB_USER,
   DB_PASSWORD).

2. redis — for Celery, exposing 6379.

3. backend — builds from backend/Dockerfile (create a simple
   multi-stage Dockerfile: install requirements, run migrations on
   container start via an entrypoint script, then runserver or gunicorn
   for dev), depends_on mysql and redis, reads env from
   backend/.env (gitignored, based on backend/.env.example from Task 1).

4. celery-worker and celery-beat — same image as backend, different
   command, both depends_on backend/redis so migrations run first.

5. frontend — builds from frontend/Dockerfile (Node, npm install, npm
   run dev), depends_on backend, reads NEXT_PUBLIC_API_URL pointing at
   the backend service.

Add a root-level .env.example documenting every variable used across
services, and a short "Local Development" section in the root README
explaining `docker compose up` brings up the whole stack, with the
frontend reachable at localhost:3000 and the backend API at
localhost:8000.

Acceptance criteria:
- `docker compose up` from a fresh clone (after copying .env.example to
  .env and filling in local values) brings up all five services with no
  manual steps beyond that.
- The frontend at localhost:3000 can successfully call the backend API
  at localhost:8000 without a CORS error.
```
