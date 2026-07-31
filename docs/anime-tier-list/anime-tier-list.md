---
summary: "How the public Furk Anime Tier List reads and ranks shared Supabase data."
read_when:
  - "Changing the anime tier list UI, score logic, or Supabase reads."
  - "Debugging missing anime, votes, comments, or cover images."
---

# Anime tier list

The page at `/animelist/` is a read-only view of the same Supabase data used by
`demiculus/demiculus.github.io`.

## Data source

`animelist/anime-config.js` contains the Supabase project URL and public anon
key. Public browser keys are expected to be shipped to clients. Never put a
Supabase personal access token, service-role key, or database password there.

The page reads:

- `profiles`: voter names.
- `animes`: titles, source links, and poster URLs.
- `ratings`: each person's 1–5 vote.
- `anime_tags`: short comments such as `unique`.

Writes and authentication remain in the source anime app. This page does not
insert, update, or delete data.

## Ranking

With `All` selected, each anime score is the arithmetic mean of all available
votes, rounded to two decimal places for tier placement. Named voter selections
limit both the visible titles and the average to those people. A single selected
voter shows that person's integer score.

- S: 1 through 1.50.
- A: 1.51 through 2.50.
- B: 2.51 through 3.50.
- C: 3.51 through 4.50.
- D: 4.51 through 5.
- Unrated titles are omitted from the chart.

Within a tier, titles sort by average score ascending, then vote count
descending, then title alphabetically.

Individual votes use these tooltip labels:

- Tier 1 (Masterpiece).
- Tier 2 (Awesome).
- Tier 3 (Suggestable).
- Tier 4 (Watchable).
- Tier 5 (Not worth watching).

## UI behavior

- Rows and cards render through the shared tier-list component documented in
  `docs/tier-list-component/tier-list-component.md`.
- Tier labels show the letter and title count. Hovering or keyboard-focusing
  the full colored rail shows its matching Masterpiece through Not worth
  watching label.
- Hover or keyboard focus shows each vote and every tagged comment.
- Clicking a card opens its stored source URL when present.
- Missing or broken covers fall back to `/assets/no_image.png`.
- The voter multiselect starts at `All`. Choosing one or more people shows
  titles watched by at least one of them and calculates scores from only their
  votes. `All` is mutually exclusive with named voters.
- Vote details and comments are limited to the selected voters.
- Search and voter filters combine without changing score order.
