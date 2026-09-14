# Backend Task 5 — Channels, Claim Flow, Follows API

```
1. When Task 3's submit endpoint receives a channel_name that doesn't
   match an existing active Channel (case-insensitive slug match), create
   a new Channel with status="pending" and let the Post's channel FK
   point to it. Generate the claim_token automatically (already a model
   default from backend Task 1).

2. PUBLIC ENDPOINTS:
   - GET /api/channels/ — paginated, only status="active", includes
     follower_count, is_verified, category_focus, institution.
   - GET /api/channels/<slug>/ — channel detail + its approved posts.
   - GET /api/channels/claim/<uuid:token>/ — validates the token exists
     and the channel is still status="pending"; returns channel name/bio
     for the frontend to display on a confirmation page.
   - POST /api/channels/claim/<uuid:token>/confirm/ — marks the claim as
     confirmed (add a `claimed_at` field via migration if not already
     present) but leaves status="pending" for a super_admin's final
     approval (Task 4's admin endpoints can be reused/extended to include
     a channel approve/reject/verify/suspend set — add those now if they
     weren't included in Task 4's scope).
   - POST /api/follow/ — accepts follower_contact plus either channel
     (slug/id) or category+institution. Creates a Follow row. Return a
     clear 409 if that exact follow already exists (respecting the
     unique constraints from the model).
   - DELETE /api/follow/ — allow unfollowing by follower_contact +
     channel/category (no auth needed, matches the no-login model, but
     rate-limit this endpoint too since it takes arbitrary contact input).

3. On any post being approved (hook into Task 4's approve action), find
   all matching Follow rows (exact channel match, or category match with
   optional institution match) and create a NotificationQueue row for
   each with status="queued".

Acceptance criteria:
- Submitting a post with a brand-new channel name creates exactly one
  pending Channel and links the post to it.
- Claiming an already-claimed or invalid token returns a clear 404/410,
  not a generic error.
- Approving a post creates the correct number of NotificationQueue rows
  for a test setup with one channel follower, one category-only
  follower, and one category+institution follower that should not match
  a post from a different institution.
- follower_count on Channel stays accurate after follow/unfollow
  (increment/decrement in the same transaction as the Follow row
  create/delete, not a separate recalculation step).
```
