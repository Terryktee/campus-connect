---
applyTo: "infrastructure/**"
---

# Infrastructure Instructions — Docker, CI/CD, Deployment

## Stack conventions
- Docker Compose for local dev, bringing up MySQL, Redis, backend,
  celery-worker, celery-beat, and frontend together with one command.
- Service-to-service communication inside Compose uses service names
  (`mysql`, `redis`, `backend`) as hostnames — never `localhost` between
  containers. Anything the browser needs to reach (`NEXT_PUBLIC_API_URL`)
  must use the published host port instead.
- Environment variables for all secrets in both apps, documented in
  `.env.example` files — never committed with real values.
- CI (GitHub Actions) should path-filter so backend-only changes don't
  trigger frontend test runs and vice versa.

## Task order in this folder
`task-01-docker-compose-local-dev.md` comes first, before most backend or
frontend work starts, so both apps have a consistent environment to run
against. `task-02-ci-cd-pipeline.md` and `task-03-production-deployment.md`
come last, once backend and frontend are both feature-complete — don't
build a pipeline around code that's still changing shape.

## When in doubt
Favor the smaller, more explicit configuration over a clever one — these
files get read by whoever deploys this next, and clarity here prevents
production incidents more than almost anything else in the repo.
