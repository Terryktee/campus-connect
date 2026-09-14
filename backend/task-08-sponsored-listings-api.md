# Backend Task 8 — Sponsored Listings API

```
1. ADMIN ENDPOINTS (super_admin only — sponsored listings are a revenue
   feature, not something moderators manage): full CRUD on
   SponsoredListing at /api/admin/sponsored-listings/.

2. Update Task 4's public post list/detail serializers to check for an
   active SponsoredListing (starts_at <= now <= ends_at) linked to
   placement_type="featured_post" and apply the same featured sort/badge
   behavior as the existing is_featured field — support both a
   manually-toggled is_featured flag and a paid listing driving the same
   visible badge. Same pattern for channels: an active
   verified_channel listing OR Channel.is_verified=True both render the
   "Verified" badge.

3. GET /api/sponsor/my-listing/<id>/ — role="sponsor_viewer" only,
   returns view_count and basic engagement data for the specific
   post/channel tied to that sponsor's own SponsoredListing only (not
   site-wide data, not other sponsors' listings — enforce by checking the
   listing's ownership, e.g. a sponsor_email field you may need to add
   via migration if one doesn't already exist to tie a sponsor_viewer
   Admin account to their specific listing(s)).

Acceptance criteria:
- An expired SponsoredListing (ends_at in the past) stops affecting sort
  order and badge rendering on the next request — checked at query time,
  not cached from creation time.
- A sponsor_viewer token can only ever retrieve data for their own
  listing(s), verified by attempting to request another sponsor's
  listing ID and confirming it's rejected.
```
