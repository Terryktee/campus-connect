## Summary

<!-- Brief description of changes made and the problem being solved -->

## Task Reference

- Resolves / Implements Task: [e.g. Loop Task 12]

## Type of Change

- [ ] New feature
- [ ] Bug fix
- [ ] Refactor / Code quality
- [ ] Security / Privacy enhancement
- [ ] CI/CD / Infrastructure
- [ ] Documentation update

## Verification & Checks

All checks must pass before merging to `main`:

- [ ] `cd backend && ruff check .`
- [ ] `cd backend && python manage.py makemigrations --check --dry-run`
- [ ] `cd backend && python manage.py test` (or `pytest`)
- [ ] `cd frontend && npm run lint`
- [ ] `cd frontend && npx tsc --noEmit`
- [ ] `cd frontend && npm run build`

## Safety & Standing Rules Compliance

- [ ] No secrets or real credentials committed (only placeholder `.env.example`).
- [ ] No raw IPs stored long term; privacy preserved.
- [ ] EXIF/GPS stripped from media upload pipelines.
- [ ] No direct `UPDATE count = count + 1` on high-traffic hot database rows.
- [ ] Database tables and existing migrations not broken or renamed.
- [ ] Moderation and reportability audit logging preserved.
