---
summary: "Safely add or change Supabase anime ratings, defaulting every update to Kan."
read_when:
  - "Adding or changing a vote in the Kan Anime Tier List."
  - "Updating a Supabase anime rating for Kan or another family member."
  - "Determining whether Kan has already watched an anime."
---

# Anime tier list updates

## Identity and watched history

Kan Yilmaz is the user and maps to the Supabase profile named `Kan`. Unless Kan
explicitly names another person, “I” and “my” always mean the `Kan` profile.

The Furk Anime Tier Google Sheet is the legacy watched-history source. Titles in
its Tier 1 through Tier 5 columns count as watched by Kan. Titles in `To Watch`
do not. When producing an unwatched list, require both:

- No Kan rating in Supabase.
- No matching title in the Sheet's Tier 1 through Tier 5 columns.

A missing Kan rating alone does not prove that Kan has not watched a title.

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
- Cross-check the Sheet before describing a title as unwatched by Kan.
- Keep the personal access token only in the ignored repository `.env`.
- Never put a personal access token, service-role key, or database password in
  `animelist/anime-config.js` or other browser code.

## Checklist

- [ ] Copy the exact anime title from the tier list or Supabase.
- [ ] Run `update-rating` with the title and 1–5 score.
- [ ] Confirm the command reports the intended profile and title.
- [ ] Confirm the verified score matches the request.
- [ ] Refresh `/animelist/` and inspect the card under the intended voter filter.
