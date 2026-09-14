# Frontend Task 4 — Channels, Claim Page, Follow UI

Depends on backend Task 5.

```
1. Build /channels/claim/[token] — calls
   GET /api/channels/claim/<token>/ to show the channel name/bio, and a
   confirm button that calls POST /api/channels/claim/<token>/confirm/.
   Show a clear success state explaining a super_admin still needs to
   give final approval before the channel goes live.

2. Wire the "Follow" button on channel pages and category filter bars to
   POST /api/follow/ — since there's no login, prompt for an
   email/phone in a small inline form the first time someone follows
   anything, and remember it in a cookie/localStorage for subsequent
   follows in the same browser (not shared across devices — that's
   expected given the no-account model).

3. Add an "Unfollow" affordance calling DELETE /api/follow/ using the
   same remembered contact.

4. Handle the 409 (already following) response gracefully — show
   "Already following" state rather than an error.

Acceptance criteria:
- Following a channel for the first time in a fresh browser prompts for
  contact info once, then reuses it for later follows in the same
  session without re-prompting.
- Attempting to follow the same channel twice shows "Already following"
  rather than a raw error.
```
