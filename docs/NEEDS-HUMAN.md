# NEEDS-HUMAN.md — Things only a human can provide

The build agent cannot set up accounts or obtain keys itself. Everything below is blocked until the human adds it.
Once a value is provided, delete the line from this file (or mark it `[done]`) and the agent will pick it up.

## Active blockers

### Object Storage (required for Task 03 — Images and Audio)
- **Cloudflare R2** (preferred) or AWS S3 bucket for media files.
  - `R2_ACCOUNT_ID`
  - `R2_ACCESS_KEY_ID`
  - `R2_SECRET_ACCESS_KEY`
  - `R2_BUCKET_NAME`
  - `R2_PUBLIC_URL` (the public CDN URL of the bucket)
- Add these to Railway environment variables (web and worker services) and to `.env` locally.

### CSAM / NSFW scanning provider (required for Task 03)
- A vetted provider account for image hash-matching against known CSAM databases (e.g. PhotoDNA or Thorn).
  - Provider endpoint URL
  - API key / credentials
- Without this the pipeline stubs quarantine, which is safe but blocks media approval.

### CI/CD secrets (required for Task 12)
- `RAILWAY_TOKEN` — Railway project token (Project Settings → Tokens)
- `VERCEL_TOKEN` — Vercel personal access token
- `VERCEL_ORG_ID` — found in Vercel project settings
- `VERCEL_PROJECT_ID` — found in Vercel project settings
- Add all four as GitHub repository secrets.

### Railway services (required for Task 12)
- Create three Railway services from this repo: **web** (gunicorn), **worker** (celery worker), **beat** (celery beat).
- Set the web service pre-deploy command to: `python manage.py migrate --noinput`

### Vercel project (required for Task 12)
- Link the Vercel project with root directory set to `frontend/`.

## Completed

_(none yet)_
