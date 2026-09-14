# Campus Loop ZW

Campus Loop ZW is a moderated student platform for Zimbabwean institutions.

## Local Development

Docker Compose runs the complete local stack: MySQL, Redis, Django, Celery
worker, Celery beat, and Next.js.

1. Copy the example environment file and replace its placeholder values:

   ```bash
   cp .env.example .env
   ```

2. Start the stack:

   ```bash
   docker compose up
   ```

   The backend container applies migrations and seeds initial data before
   starting Django. The frontend is available at
   [http://localhost:3000](http://localhost:3000), and the backend API is
   available at [http://localhost:8000](http://localhost:8000).

The browser uses `http://localhost:8000` for API requests. Containers use
the Compose service names `mysql` and `redis` for internal connections, so
those values must not be replaced with `localhost` in container
configuration.

Email settings are optional for local development. Compose defaults the SMTP
backend, host, port (`25`), and disabled TLS/SSL when those variables are not
present in the root `.env`; configure the `EMAIL_*` variables there when
testing real email delivery.
