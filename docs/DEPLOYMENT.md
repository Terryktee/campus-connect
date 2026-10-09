# Production deployment

This deployment uses a managed MySQL database and Redis instance, a
backend web service plus two Celery worker services on Railway or Render,
and a Next.js service on Vercel. The same commands work on a VPS when each
process is run from the repository's `backend/` or `frontend/` directory.

## 1. Create the database

Create a MySQL 8 database and an application user before deploying the
backend. Run this as a MySQL administrator, replacing the password and
database name with the values you will configure below:

```sql
CREATE DATABASE campus_loop_zw
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
CREATE USER 'campus_loop_app'@'%' IDENTIFIED BY 'replace-with-a-long-password';
GRANT ALL PRIVILEGES ON campus_loop_zw.* TO 'campus_loop_app'@'%';
FLUSH PRIVILEGES;
```

Use the provider's private MySQL hostname in `DB_HOST`; do not use
`localhost` for a hosted database.

## 2. Configure environment variables

Never commit a production `.env` file. Set these variables in the backend
service and copy the values to the worker and beat services:

| Variable | Required value |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `campusloop.settings_production` |
| `DJANGO_SECRET_KEY` | A unique, long random secret |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated backend hostname(s) |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated `https://` frontend origin(s) |
| `CORS_ALLOWED_ORIGINS` | The frontend origin only, for example `https://app.example.com` |
| `SECURE_SSL_REDIRECT` | `True` when TLS terminates at the platform |
| `SECURE_HSTS_SECONDS` | `31536000` after confirming HTTPS is permanent |
| `DB_NAME` | `campus_loop_zw` |
| `DB_USER` | `campus_loop_app` |
| `DB_PASSWORD` | The database user's password |
| `DB_HOST` | Managed MySQL hostname |
| `DB_PORT` | `3306` |
| `REDIS_URL` | Managed Redis connection URL |
| `FRONTEND_URL` | Public frontend URL |
| `DEFAULT_FROM_EMAIL` | Verified sender address |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP provider settings |
| `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | SMTP security flags |

`DATABASE_URL` may be used instead of the `DB_*` variables if the host
provides a Django-compatible database URL. The backend's
`CORS_ALLOWED_ORIGINS` must not include a wildcard or an admin URL.

Set these variables in the Vercel frontend project:

| Variable | Required value |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | Public backend URL, with no trailing slash |
| `NEXT_PUBLIC_SITE_URL` | Public frontend URL, for example `https://app.example.com` |

The public frontend health check is `GET /api/health`; the backend check is
`GET /api/health/`. Both return HTTP 200 only when the service is available.

## 3. Deploy and initialize the backend

Create a web service from the repository with `backend/` as its root
directory. Install dependencies with `pip install -r requirements.txt`.
Set the production settings module above and run the `web` process from
`backend/Procfile`:

```bash
python manage.py collectstatic --noinput
gunicorn campusloop.wsgi:application --bind 0.0.0.0:$PORT --access-logfile -
```

Run these one-time release commands against the production database before
opening the frontend:

```bash
python manage.py migrate --noinput
python manage.py seed_data
python manage.py collectstatic --noinput
python manage.py check --deploy
```

The commands are safe to repeat; `seed_data` is idempotent. Configure the
platform's release/prepare command to run migrations and `seed_data` on every
release so new migrations are applied before the web process starts.

## 4. Run background services

Create two additional services from the same `backend/` image and with the
same environment variables. They must be separate long-running processes:

```bash
# celery-worker
celery -A campusloop worker -l info

# celery-beat (run exactly one beat instance)
celery -A campusloop beat -l info
```

Both services require network access to the same Redis broker and MySQL
database. Do not run Celery synchronously inside web requests.

## 5. Deploy the frontend

Create a Vercel project rooted at `frontend/`, set the two `NEXT_PUBLIC_*`
variables, and use:

```bash
npm ci
npm run build
npm run start
```

The Next.js server exposes `/api/health`, `/robots.txt`, and `/sitemap.xml`.
The generated sitemap contains only public routes. `/admin/` is explicitly
disallowed in `robots.txt` and no `/admin` URL is emitted in the sitemap.
Admin authentication remains handled by the protected frontend routes and
the backend JWT API; search engines must not index the admin interface.

## VPS alternative

On a VPS, install Python 3.12, Node.js, MySQL 8, and Redis 7, then use the
same environment variables and commands above. Run the backend web,
`celery-worker`, `celery-beat`, and `npm run start` as separate supervised
systemd processes (or equivalent). Put a TLS reverse proxy in front of the
backend and frontend, forward `X-Forwarded-Proto`, and set
`SECURE_SSL_REDIRECT=True`. Open only the public HTTP/HTTPS ports; keep
MySQL and Redis private.
