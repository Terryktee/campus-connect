# Frontend Task 2 — Admin Dashboard Auth + Wiring

Depends on backend Task 2 (auth endpoints) and Task 4 (admin moderation
endpoints) existing.

```
1. Build a real login page at /admin/login that calls
   POST /api/auth/login/ and stores the returned access/refresh tokens
   securely — prefer an httpOnly cookie set via a Next.js Route Handler
   (server-side) over localStorage, so the token is never readable by
   client-side JS.

2. Add middleware.ts protecting everything under /app/admin/* — check for
   a valid session cookie server-side and redirect to /admin/login if
   missing, refreshing the access token via /api/auth/refresh/ when
   expired.

3. Call GET /api/admin/me/ after login to get the admin's role and
   institution, and use it to conditionally render UI: hide
   super_admin-only screens (Moderators, Audit Log, Sponsored Listings)
   from moderator and sponsor_viewer roles entirely, not just
   client-side hidden but actually not rendered/fetched.

4. Wire the Pending Queue, Live Posts, Reported Posts, and Channels admin
   screens to the real /api/admin/* endpoints from backend Task 4 and
   Task 5: approve/reject/take-down/feature actions, with the reject/
   take-down flows requiring a reason input before the request is sent
   (matching the backend's 400-if-missing validation).

5. Build the Audit Log screen (super_admin only) against
   GET /api/admin/moderation-actions/, with filters for admin, action
   type, and date range.

Acceptance criteria:
- Visiting any /admin/* route while logged out redirects to /admin/login.
- A moderator-role login never sees or can navigate to super_admin-only
  screens, even by typing the URL directly.
- Rejecting a post without entering a reason is blocked in the UI before
  the request is even sent (not just relying on the backend's 400).
```
