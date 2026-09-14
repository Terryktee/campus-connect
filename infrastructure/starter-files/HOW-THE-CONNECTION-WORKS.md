# How the Frontend/Backend Connection Actually Works

## The short version

Docker Compose gives every service a hostname equal to its name in
`docker-compose.yml` (`mysql`, `redis`, `backend`, `frontend`), reachable
only from **other containers on the same Compose network** — not from your
browser or your host machine. That's the one thing that trips people up.

So there are two different "backend URLs" depending on who's asking:

| Who's asking | URL to use | Why |
|---|---|---|
| The `backend` container talking to `mysql`/`redis` | `mysql:3306`, `redis:6379` | Container-to-container, internal Compose network |
| `celery-worker`/`celery-beat` talking to `redis`/`backend`'s DB | `redis:6379`, `mysql:3306` | Same as above |
| Your **browser** (client-side JS in the Next.js app) talking to the backend | `http://localhost:8000` | The browser runs on your host machine, outside Docker entirely — it can only reach backend through the **published port** (`ports: "8000:8000"` in compose) |
| Server-side Next.js code (Route Handlers, Server Components) talking to the backend | either works, but `http://backend:8000` is slightly more efficient since it skips the host network round-trip | Server-side code runs inside the frontend container, so it CAN see other Compose services by name |

This is why `docker-compose.yml` sets `NEXT_PUBLIC_API_URL=http://localhost:8000`
— anything prefixed `NEXT_PUBLIC_` gets baked into client-side JS that runs
in the browser, so it must be a URL the browser can actually reach.

## What makes it "self-connecting"

1. **`depends_on` with healthchecks** — `backend` won't start until `mysql`
   and `redis` report healthy, so you never hit a race condition where
   Django tries to connect before MySQL has finished booting.
2. **The backend's startup command runs migrations automatically** —
   `docker-compose.yml`'s `command:` for the `backend` service runs
   `migrate` and `seed_data` before `runserver`, every time the container
   starts. So a fresh `docker compose up` ends with a fully migrated,
   seeded database with no manual step.
3. **Environment variables are overridden at the Compose level** — even
   though `backend/.env` has `DB_HOST=localhost` (for running outside
   Docker), `docker-compose.yml`'s `environment:` block overrides it to
   `DB_HOST=mysql` when running via Compose. You don't have to maintain
   two versions of `.env` for the two ways of running it.
4. **CORS is explicit, not wildcarded** — `backend/.env`'s
   `CORS_ALLOWED_ORIGINS=http://localhost:3000` matches exactly where the
   frontend is published, so the browser's CORS preflight succeeds without
   opening the API to every origin.

## How to bring it up

```bash
# one-time setup
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
# edit the three files above and fill in real secrets

# every time after that
docker compose up
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- MySQL: localhost:3306 (from your host, e.g. for a GUI client)
- Redis: localhost:6379

## If something doesn't connect

- **Frontend can't reach the backend, "Failed to fetch"** — almost always
  `NEXT_PUBLIC_API_URL` pointing at the wrong place. It should be
  `http://localhost:8000`, never `http://backend:8000`, for anything that
  runs client-side.
- **CORS error in the browser console** — `backend/.env`'s
  `CORS_ALLOWED_ORIGINS` doesn't match the frontend's actual origin
  exactly (including port). Update it and restart the `backend` container.
- **Backend can't reach MySQL** — check `docker compose logs mysql` for
  startup errors first; the healthcheck should stop `backend` from even
  trying until MySQL is ready, but a bad `MYSQL_ROOT_PASSWORD` mismatch
  between `.env` and an already-existing `mysql_data` volume will still
  fail. If you changed DB credentials after the first run, remove the
  volume: `docker compose down -v` then `docker compose up` again.
