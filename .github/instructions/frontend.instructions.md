---
applyTo: "frontend/**"
---

# Frontend Instructions — Next.js

## Stack conventions
- Next.js App Router, TypeScript, Tailwind, shadcn/ui — matches the
  existing scaffold, don't introduce a different UI library or CSS
  approach.
- `NEXT_PUBLIC_API_URL` must point to a URL the **browser** can reach
  (e.g. `http://localhost:8000`) — never a Docker-internal service name
  like `http://backend:8000` for anything used in client-side code. Only
  server-side code (Route Handlers, Server Components) may use the
  internal address.
- Admin auth tokens are never stored in localStorage or exposed to
  client-side JS — use an httpOnly cookie set via a server-side Route
  Handler.
- Every `/admin/*` route must be protected by `middleware.ts`, not just
  conditionally rendered — an unauthenticated direct request to an admin
  URL must redirect server-side before any admin data is fetched.
- Role-based UI (super_admin vs moderator vs sponsor_viewer) must hide
  screens by not fetching/rendering them, not just via CSS/conditional
  display.

## Task order in this folder
`task-01-connect-api.md` can start once `backend/task-01` (project setup)
and `backend/task-04` (public read API) are merged — it doesn't need the
full backend finished. `task-02` through `task-05` each depend on their
matching backend task (auth, submission API, channels/follows API,
orientation API respectively) being merged first — check the backend
folder's progress before starting.

## When in doubt
Any validation done here is a UX nicety, not a security boundary — the
backend's checks are what actually matter. Don't skip backend-side
verification on the assumption the frontend already validated something.
