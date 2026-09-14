# Frontend Task 5 — Orientation Hub Integration

Depends on backend Task 7.

```
1. Replace the Orientation Hub's static content with real data from
   GET /api/orientation/<institution_short_code>/, keyed off the
   institution picker already in the UI.

2. Render the three guide_type groups (how_to, directory_entry,
   campus_map_note) as the existing accordion / "Who Do I Ask?" table /
   campus map sections respectively, matching the original mock-data
   layout.

3. Add a loading state while switching between institutions in the
   picker, and an empty state for an institution with no guides yet
   ("Orientation content for [University] is coming soon").

Acceptance criteria:
- Switching the institution picker shows that institution's real guides,
  correctly grouped, with no stale content briefly flashing from the
  previous selection.
```
