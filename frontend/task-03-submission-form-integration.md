# Frontend Task 3 — Submission Form Integration

Depends on backend Task 3.

```
1. Wire the existing /submit form UI to POST /api/posts/submit/. Add the
   hidden honeypot field the backend expects.

2. Handle backend validation errors field-by-field (e.g. invalid
   submitter_contact format) by mapping the API's error response to the
   matching form field, not a generic toast.

3. Handle the 429 rate-limit response with a clear, friendly message
   (reuse the backend's returned message rather than writing a generic
   one, so copy stays consistent in one place).

4. On success, show the existing confirmation screen ("Thanks — your post
   is in review...").

5. If the user filled in a channel_name, and the API response or a
   follow-up call indicates a new channel was created pending claim,
   show a note on the confirmation screen: "We've also started a channel
   called '[name]' — check your email/phone for a link to claim it."

Acceptance criteria:
- Submitting invalid data shows errors next to the relevant fields, not
  just at the top of the form.
- Hitting the rate limit twice in testing shows the backend's message
  verbatim, not a hardcoded frontend string that could drift out of sync.
```
