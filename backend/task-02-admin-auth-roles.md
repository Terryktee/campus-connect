# Backend Task 2 — Admin Auth, Roles, and Scoping (DRF)

```
Add authentication for the admin/moderator side of the API. The public
site never authenticates — this is only for the frontend's /admin
dashboard.

1. Install and configure djangorestframework-simplejwt for token auth.
   Add /api/auth/login/ (returns access + refresh token given
   username/password) and /api/auth/refresh/.

2. Create a custom DRF permission class `IsScopedAdmin` that:
   - Rejects any request without a valid token attached to a User that
     has a related Admin profile.
   - Exposes the requesting user's Admin.role and Admin.institution to
     the view so querysets can be scoped.

3. Create a base ViewSet mixin `InstitutionScopedQuerysetMixin` that
   moderators (role="moderator") can use to auto-filter querysets to
   their Admin.institution, while super_admin sees everything, applied
   consistently across Post, Channel, and Report admin viewsets (built in
   later tasks) — build this mixin now so those tasks can reuse it.

4. Add a /api/admin/me/ endpoint returning the logged-in admin's role,
   institution, and name — the frontend needs this to render the right
   admin UI (Task frontend-02 depends on this).

5. Do NOT expose any public registration/signup endpoint for Admin
   accounts. New admins are created via Django's createsuperuser for the
   first super_admin, and via an authenticated-only /api/admin/invite/
   endpoint (super_admin role required) for everyone after that — this
   endpoint creates a User with an unusable password and emails an
   invite link (stub the email as a console.log function for now,
   matching backend Task 6's real implementation later).

Acceptance criteria:
- A request to any endpoint using IsScopedAdmin without a valid token
  returns 401.
- A logged-in moderator's queryset, once InstitutionScopedQuerysetMixin
  is applied in later tasks, only ever returns rows for their assigned
  institution — verify this with a quick test endpoint or unit test now
  even though the real viewsets come later, so the mixin itself is
  proven correct in isolation.
- /api/admin/invite/ returns 403 for any role other than super_admin.
```
