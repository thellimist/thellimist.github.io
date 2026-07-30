---
summary: "Safely add or change Supabase anime ratings, defaulting every update to Kan."
read_when:
  - "Adding or changing a vote in the Furk Anime Tier List."
  - "Updating a Supabase anime rating for Kan or another family member."
---

# Anime tier list updates

Use the checked-in command to add or change one rating:

```sh
docs/anime-tier-list-updates/scripts/update-rating "Arcane" 1
```

The profile defaults to `Kan`. Only pass a third argument when the request
explicitly names someone else:

```sh
docs/anime-tier-list-updates/scripts/update-rating "Arcane" 2 Demi
```

The command reads `SUPABASE_ACCESS_TOKEN` from the repository's ignored `.env`.
Both `SUPABASE_ACCESS_TOKEN=value` and `SUPABASE_ACCESS_TOKEN: value` work.
It prints the resolved title, profile, old score, and verified new score without
printing the token.

## Guardrails

- Default every rating update to `Kan`.
- Update another profile only when the user explicitly names that person.
- Accept integer scores from 1 through 5 only.
- Require one case-insensitive exact anime-title match and one exact profile
  match before writing.
- Stop on missing or duplicate matches instead of guessing.
- Read the current vote before writing and verify the stored vote afterward.
- Keep the personal access token only in the ignored repository `.env`.
- Never put a personal access token, service-role key, or database password in
  `animelist/anime-config.js` or other browser code.

## Checklist

- [ ] Copy the exact anime title from the tier list or Supabase.
- [ ] Run `update-rating` with the title and 1–5 score.
- [ ] Confirm the command reports the intended profile and title.
- [ ] Confirm the verified score matches the request.
- [ ] Refresh `/animelist/` and inspect the card under the intended voter filter.
