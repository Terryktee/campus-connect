# Backend Task 7 — Orientation Hub API

```
1. PUBLIC ENDPOINT: GET /api/orientation/<institution_short_code>/ —
   returns OrientationGuide rows for that institution where
   is_published=True, grouped by guide_type, ordered by sort_order. 404
   if the institution short_code doesn't exist or is_active=False.

2. ADMIN ENDPOINTS (IsScopedAdmin, scoped by institution like Task 4's
   pattern): full CRUD on OrientationGuide at /api/admin/orientation/ —
   moderators can only manage guides for their own institution;
   super_admin can manage any.

Acceptance criteria:
- Toggling is_published=False on a guide via the admin endpoint removes
  it from the public endpoint's response immediately.
- A moderator scoped to one institution gets 403/404 attempting to
  create or edit a guide for a different institution.
```
