# Frontend Task 1 — Connect to the Real Backend API

Assumes the Next.js scaffold already exists (from the earlier v0 build)
with mock data. This task swaps that mock data for real calls to the
Django backend.

```
1. Add an API client module (lib/api.ts) that wraps fetch calls to the
   backend, reading the base URL from an env var (NEXT_PUBLIC_API_URL for
   client-side-safe public reads; keep any admin-token-bearing requests
   server-side only — see Task 2).

2. Replace the mock data powering the home feed, post detail, category
   filters, channels directory, and channel pages with real calls to:
   GET /api/posts/, GET /api/posts/<id>/, GET /api/categories/,
   GET /api/institutions/, GET /api/channels/, GET /api/channels/<slug>/.

3. Add loading and empty states for each of these (the mock-data version
   likely didn't need them since data was always present instantly).

4. Add basic error handling: if the backend is unreachable or returns a
   5xx, show a friendly fallback rather than a blank page or raw error.

5. Confirm CORS works end-to-end against the backend's configured
   CORS_ALLOWED_ORIGINS (from backend Task 1) — coordinate the exact
   frontend dev URL/port with what's in the backend's env.

Acceptance criteria:
- The home feed, post detail, categories filter, and channels pages all
  render real data from a locally running backend instead of the mock
  data file.
- Stopping the backend and reloading the frontend shows a friendly error
  state, not a crash or blank screen.
```
