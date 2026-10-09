# Loop

> **Your voice. Your loop. No youth left behind.**  
> Loop is an open-source, no-account social platform for youth worldwide. Moderated, low-bandwidth friendly, and safe by default.

---

## Overview

Loop is designed to give every young person a voice without the barriers, data harvesting, or lock-in of traditional social networks:

- **No accounts required:** Public users authenticate cryptographically via keypairs stored locally in the browser (Ed25519) with 12-word recovery phrases. No phone numbers, passwords, or emails required for everyday users.
- **Controlled by statements:** Feeds are ranked organically by **Pulse** (surprise, velocity, ripple, and quality) rather than closed follow-graphs or follower counts.
- **Safe by default:** Mandatory media screening, EXIF/GPS stripping, no stranger private DMs, and comprehensive audit-logged moderation.
- **Low-bandwidth friendly:** Mobile-first, deferred media loading, and designed to perform gracefully on slow 3G/4G connections.
- **Community & Campus aware:** Configurable support for educational institutions, cities, and topical communities globally.

---

## Architecture

```
┌─────────────────────────────────┐           REST API            ┌──────────────────────────────────┐
│           frontend/             │ ────────────────────────────▶ │            backend/              │
│    Next.js 16 (App Router)      │ ◀──────────────────────────── │      Django 5.2 + DRF            │
│   React 19 + TypeScript         │                               │     MySQL 8.0 (utf8mb4)          │
│   Tailwind CSS                  │                               │     Celery + Redis               │
└─────────────────────────────────┘                               └──────────────────────────────────┘
                 │                                                                  │
                 └─────────────────────── deployed via ────────────────────────────┘
                                                    │
                                      ┌───────────────────────────┐
                                      │   Railway (backend/worker)│
                                      │   Vercel (frontend)       │
                                      │   Docker Compose (local)  │
                                      └───────────────────────────┘
```

- **`backend/`**: Django REST Framework backend (`campusloop/` project, `core/` app). Manages content, moderation, Celery background tasks, and notifications.
- **`frontend/`**: Next.js App Router application with responsive components, accessible UI, and administrative moderation tools.
- **`docs/`**: Master build plans (`LOOP_PLAN.md`), autonomous task queues (`TASKS.md`), build run log (`RUN-LOG.md`), audits (`AUDIT.md`), and operator guides.

---

## Local Development with Docker Compose

Docker Compose runs the complete local environment: MySQL, Redis, Django, Celery worker, Celery beat, and Next.js.

### 1. Configure environment variables

Copy the example environment file at the repository root:

```bash
cp .env.example .env
```

Review the values in `.env`. The defaults are configured to work with Docker Compose out of the box.

### 2. Start the full stack

```bash
docker compose up
```

Once running:
- **Frontend web app:** [http://localhost:3000](http://localhost:3000)
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **API Health Check:** [http://localhost:8000/api/health/](http://localhost:8000/api/health/)

The browser connects to `http://localhost:8000` for public API requests. Within Docker, services communicate using service names (`mysql`, `redis`, `backend`).

---

## Local Development (Without Docker)

### Backend setup

Prerequisites: Python 3.12+, Redis running locally, and MySQL or SQLite.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Run migrations (using SQLite for rapid local dev if desired):
export DJANGO_SECRET_KEY="local-dev-secret-key"
export DATABASE_URL="sqlite:///local.sqlite3"
python manage.py migrate
python manage.py seed_data

# Run tests
python manage.py test

# Start the server
python manage.py runserver 8000
```

### Frontend setup

Prerequisites: Node.js 20+.

```bash
cd frontend
npm install
npm run dev
```

---

## Pre-Commit Verification Checks

Before each commit, all automated checks must pass:

```bash
# Backend checks
cd backend
ruff check .
python manage.py makemigrations --check --dry-run
python manage.py test

# Frontend checks
cd ../frontend
npm run lint
npx tsc --noEmit
npm run build
```

---

## Documentation & References

| File | Purpose |
|---|---|
| [`AGENTS.md`](./AGENTS.md) | Standing development rules and AI agent guidelines |
| [`docs/AUDIT.md`](./docs/AUDIT.md) | System architecture audit and security evaluation |
| [`docs/LOOP_PLAN.md`](./docs/LOOP_PLAN.md) | Master product specifications and algorithmic designs |
| [`docs/TASKS.md`](./docs/TASKS.md) | Autonomous implementation queue and task statuses |
| [`docs/RUN-LOG.md`](./docs/RUN-LOG.md) | Historical progress log and changelog per task |
| [`docs/NEEDS-HUMAN.md`](./docs/NEEDS-HUMAN.md) | External provider credentials and operator setup items |
| [`docs/DEPLOY.md`](./docs/DEPLOY.md) | Production deployment instructions for Railway and Vercel |

---

## License

Open source under the [AGPL-3.0 License](./LICENSE) (see documentation).
