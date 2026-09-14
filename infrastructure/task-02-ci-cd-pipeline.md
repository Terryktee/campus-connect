# Infrastructure Task 2 — CI/CD Pipeline

Do this once both backend and frontend have their core tasks merged.

```
Add GitHub Actions workflows:

1. .github/workflows/backend-ci.yml — on push/PR touching backend/**:
   spin up a MySQL service container, install backend/requirements.txt,
   run `python manage.py migrate --check` and the test suite (add a
   basic smoke test suite now if one doesn't exist yet — at minimum,
   test that the public endpoints exclude private fields, since that's
   the highest-stakes regression to catch automatically).

2. .github/workflows/frontend-ci.yml — on push/PR touching frontend/**:
   npm install, run lint, run `next build` to catch build-time errors.

3. .github/workflows/docker-build.yml — on merge to main: build and push
   both backend and frontend Docker images to a registry (GitHub Container
   Registry is a reasonable default unless another registry is already
   configured), tagged with the commit SHA.

Acceptance criteria:
- Opening a PR that changes only frontend/ does not trigger the backend
  test suite, and vice versa (path filtering works correctly).
- A PR that removes the private-field exclusion in a public serializer
  fails CI (prove this by temporarily introducing that regression on a
  test branch and confirming the workflow catches it, then revert).
```
