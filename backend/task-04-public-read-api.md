# Backend Task 4 — Public Read API + Admin Moderation Endpoints

```
Build both the public-facing read API and the authenticated moderation
endpoints for Post/Channel/Report, since they share the same underlying
querysets.

PUBLIC ENDPOINTS (no auth, read-only):
1. GET /api/posts/ — paginated, filterable by category, institution.
   Only returns status="approved" posts. Order by is_featured desc, then
   created_at desc. Use a PublicPostSerializer that explicitly whitelists
   fields (id, title, content, category, institution, channel, image_url,
   link_url, is_featured, view_count, created_at) — never include
   submitter_contact, submitter_name is fine to include since it's meant
   to display, but re-check the design doc if in doubt about which
   fields are meant to be public vs private before assuming.
2. GET /api/posts/<id>/ — same serializer, 404 if not approved. Increment
   view_count on retrieve (simple counter increment, no unique-visitor
   logic needed yet).
3. POST /api/posts/<id>/report/ — no auth, creates a Report row (reason,
   optional reporter_contact). Rate-limit similarly to Task 3's submit
   endpoint (5 per reporter_contact-or-IP per hour) to prevent abuse of
   the report system itself.
4. GET /api/categories/ and GET /api/institutions/ — simple lookup lists
   for the frontend's filter UI.

ADMIN ENDPOINTS (IsScopedAdmin required, built on Task 2's mixin):
5. GET /api/admin/posts/ — all statuses, filterable by status, category,
   institution, is_flagged, scoped by moderator's institution via
   InstitutionScopedQuerysetMixin. Sort flagged posts to the top by
   default.
6. POST /api/admin/posts/<id>/approve/ — sets status="approved",
   approved_at=now, creates a ModerationAction(action="approve").
7. POST /api/admin/posts/<id>/reject/ — requires a `reason` in the
   request body (400 if missing), sets status="rejected",
   rejection_reason=reason, creates a ModerationAction(action="reject",
   reason=reason).
8. POST /api/admin/posts/<id>/take_down/ — same pattern as reject but for
   already-approved posts (status="taken_down").
9. POST /api/admin/posts/<id>/feature/ and /unfeature/ — toggles
   is_featured, logs the matching ModerationAction.
10. GET /api/admin/reports/ — Report rows joined with their post, scoped
    the same way. POST /api/admin/reports/<id>/dismiss/ and
    /escalate/ (escalate = takes down the linked post and logs both a
    dismiss/escalate action and the take_down action on the post).
11. GET /api/admin/moderation-actions/ — read-only, paginated, filterable
    by admin, action, date range. No PATCH/DELETE route exists for this
    resource at all — not even for super_admin.

Acceptance criteria:
- Requesting /api/posts/<id>/ for a pending or rejected post returns 404.
- No public endpoint response ever contains submitter_contact,
  claim_contact, or reporter_contact in any field, including nested
  serializers.
- A moderator token scoped to one institution gets a 403 or empty result
  (your choice, but be consistent) when calling any /api/admin/* action
  endpoint on a post outside their institution — verify this can't be
  bypassed by guessing the post ID.
- Rejecting without a reason returns 400, not a silent no-op.
```
