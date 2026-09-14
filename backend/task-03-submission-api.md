# Backend Task 3 — Public Submission API

```
Build the public, no-login POST endpoint that the frontend's /submit form
calls.

1. POST /api/posts/submit/ — accepts title, content, category (slug or
   id), institution (optional), channel_name (optional free text — see
   Task 5 for how this becomes a real Channel), image_url, link_url,
   submitter_name (optional), submitter_institution (optional),
   submitter_contact (required).

2. Validate with a DRF serializer:
   - submitter_contact must match an email pattern OR a Zimbabwean phone
     pattern (write a custom validator).
   - category must reference an existing Category.
   - A hidden honeypot field (e.g. `website`) must be empty — if filled,
     return a 200 success response (so bots don't learn it failed) but
     silently discard the submission without saving.

3. Apply django-ratelimit to this view: 5 requests per submitter_contact
   per hour, 20 requests per IP per hour. On limit hit, return a 429 with
   a clear JSON error message the frontend can display directly to the
   user.

4. On successful save, run the automated pre-filter:
   - Check title + content (case-insensitive substring match) against
     BlocklistKeyword rows.
   - Check any URL found in link_url or embedded in content against
     AllowlistedDomain rows.
   - If either check fails, set is_flagged=True on the new Post. Never
     block the submission or alter status — it is always created with
     status="pending" regardless of the filter result.

5. Response on success: 201 with a minimal payload (id, status) — do not
   echo back submitter_contact or any private field in the response body.

Acceptance criteria:
- A 6th submission within an hour from the same submitter_contact returns
  429 with a friendly message.
- A submission containing a blocklisted keyword saves with
  status="pending", is_flagged=True.
- The 201 response body never includes submitter_contact or any other
  private field.
```
