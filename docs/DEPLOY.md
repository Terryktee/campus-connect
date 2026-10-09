# Loop: Deployment Guide (Railway & Vercel)

This document describes how Loop is deployed to production using **Railway** (backend services) and **Vercel** (frontend application).

---

## Architecture Overview

- **Backend Web:** Gunicorn serving Django REST Framework on Railway (`web` service).
- **Celery Worker:** Asynchronous task processing for media, notifications, and analytics (`worker` service).
- **Celery Beat:** Scheduled tasks including notification queue processing and metrics aggregation (`beat` service).
- **Database & Cache:** Managed MySQL 8.0 and Redis instances on Railway.
- **Frontend Web App:** Next.js App Router deployed on Vercel.

---

## 1. Secrets & Environment Variables

### GitHub Actions Secrets

Add the following secrets to your GitHub repository (`Settings -> Secrets and variables -> Actions`):

| Secret | Description | Where to find |
|---|---|---|
| `RAILWAY_TOKEN` | Railway Project Token | Railway Project Dashboard -> Settings -> Tokens |
| `VERCEL_TOKEN` | Vercel Personal Access Token | Vercel Account Settings -> Tokens |
| `VERCEL_ORG_ID` | Vercel Organization / Team ID | Vercel Project Settings -> General |
| `VERCEL_PROJECT_ID` | Vercel Project ID | Vercel Project Settings -> General |

---

## 2. Railway Configuration (Backend Services)

Create a single Railway project connected to the GitHub repository and configure three separate services:

### Service 1: `web`
- **Root Directory:** `/` (or `backend/`)
- **Build Command:** Uses `backend/Dockerfile` or nixpacks / requirements.txt.
- **Pre-Deploy Command:**
  ```bash
  python manage.py migrate --noinput
  ```
  *(Crucial: ensures database migrations run before traffic hits new instances)*
- **Start Command:**
  ```bash
  gunicorn campusloop.wsgi:application --bind 0.0.0.0:$PORT --workers 3
  ```
- **Environment Variables:**
  - `DJANGO_SECRET_KEY`: Long, random secret string.
  - `DJANGO_DEBUG`: `False`
  - `DJANGO_ALLOWED_HOSTS`: `.railway.app,api.yourdomain.com`
  - `CORS_ALLOWED_ORIGINS`: `https://yourdomain.com,https://your-vercel-app.vercel.app`
  - `CSRF_TRUSTED_ORIGINS`: `https://yourdomain.com,https://api.yourdomain.com`
  - `DATABASE_URL`: Linked from Railway MySQL service (`${{MySQL.DATABASE_URL}}`)
  - `REDIS_URL`: Linked from Railway Redis service (`${{Redis.REDIS_URL}}`)
  - `FRONTEND_URL`: Public URL of the frontend (e.g., `https://yourdomain.com`)
  - `DEFAULT_FROM_EMAIL`: `noreply@loop.example` (or your verified domain email)
  - `DJANGO_SETTINGS_MODULE`: `campusloop.settings_production`

### Service 2: `worker`
- **Root Directory:** `/`
- **Start Command:**
  ```bash
  celery -A campusloop worker -l info --concurrency 2
  ```
- **Environment Variables:** Same `DATABASE_URL`, `REDIS_URL`, `DJANGO_SECRET_KEY`, and `DJANGO_SETTINGS_MODULE` as `web`.

### Service 3: `beat`
- **Root Directory:** `/`
- **Start Command:**
  ```bash
  celery -A campusloop beat -l info
  ```
- **Environment Variables:** Same as `worker`.

---

## 3. Vercel Configuration (Frontend)

1. **Import Repository:** In Vercel, import the repository.
2. **Set Root Directory:** In Project Settings -> General, set **Root Directory** to `frontend`.
3. **Framework Preset:** Next.js (automatically detected).
4. **Environment Variables:**
   - `NEXT_PUBLIC_API_URL`: Public HTTPS URL of the backend Railway web service (e.g., `https://api.yourdomain.com` or `https://backend-production.up.railway.app`).

---

## 4. CI/CD Deployment Flow

Deployments are automated through `.github/workflows/ci-cd.yml`:
1. Every commit or pull request to `main` runs:
   - Backend linting with `ruff`
   - Migration integrity check (`makemigrations --check --dry-run`)
   - Backend unit tests with `pytest` against MySQL & Redis service containers
   - Frontend linting, TypeScript typecheck (`tsc --noEmit`), and production build (`npm run build`)
   - Secret leak detection with `gitleaks`
2. When changes merge into `main`:
   - Railway CLI updates the `web`, `worker`, and `beat` services in Railway.
   - Vercel CLI prebuilds and deploys the production frontend artifact.

---

## 5. Branch Protection Rules

To prevent broken builds or unauthorized pushes:
1. Navigate to GitHub -> Settings -> Branches -> Branch protection rules -> Add rule for `main`.
2. Check:
   - **Require a pull request before merging**.
   - **Require status checks to pass before merging**:
     - `backend`
     - `frontend`
     - `secrets-scan`
   - **Do not allow force pushes**.
   - **Do not allow deletions**.
