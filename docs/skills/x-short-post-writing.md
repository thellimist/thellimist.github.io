---
summary: "Convert rough thoughts into short, high-signal X posts in Kan's voice."
read_when:
  - Writing a tweet or short X post from notes, ideas, or spoken thoughts.
---

# X Short Post Writing Skill

Turn raw thoughts into short X posts that feel native to the platform without losing Kan's voice.
Read `VOICE.md` in repo root before drafting.

Use this for short posts only (single-post or short thread style). For long-form X Articles, use `docs/skills/x-publishing.md`.

## Calibration Source (Style Benchmark)

Calibration snapshot:
- Source account: `@gregisenberg`
- Pull date: `2026-03-01` (X API)

Observed patterns to borrow:
- Strong hook in line 1, often claim-first.
- Heavy line-break usage (around 4-5 short lines/post).
- Specificity over abstraction (numbers, names, concrete examples).
- Plain language, minimal hashtags, minimal fluff.
- Tactical lists for "how-to" posts.
- Practical, specific, and immediately usable.
- Engagement bait is lower; concrete utility is higher.

Borrow structure and pacing, not voice or slang.

## Good Post Examples

Use these as structural references, not copy templates. (add good examples here with prompt and result)

## Non-Negotiables

- Keep output under 280 chars unless user explicitly asks for a thread.
- Target 120-250 chars for most posts.
- One core idea per post.
- No hashtags unless user asks.
- No AI-slop phrasing banned in `VOICE.md`.
- No em dash.
- Avoid generic motivational filler.

## Input Contract

Expected input can be messy:
- A raw thought
- A voice note transcript
- A draft paragraph
- A link with one sentence of context

If input is long, compress to one claim + one proof point + one payoff line.

## Output Contract

Return:
1. One recommended post
2. Two alternates with different angles

Angles:
- `Direct`: bold claim + concrete proof
- `Tactical`: short steps or framework
- `Contrarian`: opinion against default consensus

## Writing Workflow

1. Distill
- Convert user input into one sentence: `Claim`.
- Add one concrete `Proof` (number, example, short story detail).
- Add one `Payoff` (what this changes).

2. Choose structure
- Use one structure: `Claim -> Proof -> Payoff`
- Use one structure: `Mini-story -> Lesson`
- Use one structure: `How-to -> 3 steps`
- Use one structure: `Data point -> Interpretation`

3. Draft with line breaks
- Put the hook in line 1.
- Keep each line short and skimmable.
- 3-6 lines total.

4. Tighten
- Remove filler transitions.
- Replace generic nouns with specifics.
- Cut any repeated sentence.

5. Final QA
- Reads like Kan.
- No banned wording.
- Clear in one screen without "see more" dependence.

## Templates

### Direct
`[Bold claim].`

`[Concrete proof point].`

`[Short payoff line].`

### Tactical
`How to [result] without [pain]:`

`1) [step]`
`2) [step]`
`3) [step]`

### Contrarian
`Everyone says [common belief].`

`I think the opposite: [counter-claim].`

`Because [concrete evidence].`

## Quick Quality Checklist

- [ ] Hook lands in line 1
- [ ] Includes at least one concrete detail
- [ ] One idea only
- [ ] 120-250 chars target (unless user wants longer)
- [ ] No hashtags (unless requested)
- [ ] No em dash
- [ ] No banned AI wording from `VOICE.md`
