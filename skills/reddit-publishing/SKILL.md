---
name: reddit-publishing
description: Research and rank relevant subreddits for a blog post, audit each subreddit's posting rules (self-promo, link/text format, flair, karma/account limits), and draft subreddit-specific Reddit posts without publishing.
---

# Reddit Publishing Skill

Find subreddits that are both relevant and actually postable, then draft per-subreddit posts.
Read `VOICE.md` in repo root before drafting.
Read `skills/blog-writing/references/social-draft-contract.md` before drafting.

## Tools Required

- `python3`
- `browser` (OpenClaw browser tool) for final rule verification and drafting
- Discovery tool: `skills/reddit-publishing/scripts/research_subreddits.py`

## File Location

Save output as `social/YYYY-MM-DD-slug/reddit.md`.
If any subreddit uses comment-first linking, also update `social/YYYY-MM-DD-slug/comment-kit.md`.

## Step -1: Prepare Artifacts (Required, Do Not Assume Files Exist)

Run this first, every time:

```bash
python3 skills/blog-writing/scripts/prepare_social_artifacts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --platform reddit \
  --blog-url https://YOUR_BLOG_URL
```

This creates/updates if missing:
- `social/YYYY-MM-DD-slug/reddit.md`
- `social/YYYY-MM-DD-slug/comment-kit.md`

## Step 1: Generate Query Angles

Create 4-6 query angles from the blog:
- Core topic
- Technical topic
- Audience/profession
- Adjacent broader topic
- Contrarian framing keyword (if relevant)
- Exact protocol/product/acronym terms from title/slug (for example: `MCP`, `CLIHub`)

Example:
- `ai agents`
- `llm tool use`
- `developer productivity`
- `startup automation`

## Step 2: Run Discovery + Rule Audit Script

```bash
python3 skills/reddit-publishing/scripts/research_subreddits.py \
  --queries "ai agents" "llm tool use" "developer productivity" "startup automation" \
  --source-post _posts/YYYY-MM-DD-slug.md \
  --limit-per-query 14 \
  --max-candidates 28 \
  --require-analyzed 25 \
  --min-subscribers 1000 \
  --min-exact-subscribers 200 \
  --sample-posts 20 \
  --request-timeout 8 \
  --request-retries 1 \
  --prefer-old-reddit \
  --max-rate-limit-errors 8 \
  --cache-file ~/.cache/reddit-publishing/subreddit-research-cache.json \
  --cache-ttl-hours 2160 \
  --max-runtime-seconds 420 \
  --max-consecutive-failures 10 \
  --json-out /tmp/reddit-research.json \
  --md-out /tmp/reddit-research.md
```

The script outputs:
- Candidate list ranked by `target / maybe / avoid`
- Exact-seeded subreddit candidates from title/slug acronyms (for example `r/mcp`) when available
- Activity metrics (posts/day, median comments)
- Rule risk summary (self-promo, AI policy, post type, requirements)
- Rule evidence + confidence fields for each classification

Reliability notes:
- Script now prints live progress (`[query ...]`, `[candidate ...]`) so it does not look hung.
- Script prefers `old.reddit.com` first to avoid slow anonymous API stalls on `www`.
- If Reddit returns many `429 Too Many Requests`, it fails fast by design.
- Script caches per-query search results and per-subreddit (`about`, `rules`, `new`) snapshots.
- Cache is reused automatically before making network calls (default: `~/.cache/reddit-publishing/subreddit-research-cache.json`, TTL 90 days).
- On rate-limit bursts, retry with fewer candidates first, then expand:
  - first pass: `--max-candidates 12 --require-analyzed 8 --sleep-ms 600 --no-infer-from-source`
  - second pass (if healthy): increase back to 24-28 candidates.

## Step 3: Manual Verification for Top Candidates

For top 5-8 `target`/`maybe` subreddits, manually verify with `browser` before drafting:

1. Open `https://www.reddit.com/r/SUBREDDIT/about/rules`
2. Open `https://www.reddit.com/r/SUBREDDIT/new`
3. Check top pinned/mod posts from last 30 days

Mandatory checks:
- Self-promo policy (ban, limited ratio, allowed with conditions)
- Link post vs text post requirement
- Flair requirement
- Title format requirements (`[D]`, prefixes, etc.)
- Karma/account age limits
- Posting frequency limits (weekly promo threads, one-per-X-days)

If rules conflict or are unclear, mark as `maybe` and avoid auto-selecting it.
If confidence is low (<0.65), require manual browser verification before selection.

## Step 4: Select Subreddits with Go/No-Go Rules

Use this filter:
- `NO-GO`: explicit self-promo ban, or hard mismatch with required post format
- `GO (text)`: allows self-promo but requires text posts
- `GO (link)`: allows link posts with no blocking constraints

Pick 3-4 best targets from the ~30 analyzed pool.
If a high-relevance exact-match subreddit exists (example: `r/mcp` for MCP posts), prefer including it unless rules clearly block posting.
For each selected subreddit, choose link placement:
- `body_end` if subreddit expects/permits links in body
- `first_comment` if subreddit discourages self-promo links in body

## Step 5: Draft `reddit.md`

```markdown
# Reddit Draft

## Target Subreddits
Candidates reviewed: 30
Selection criteria: relevance + activity + comments + self-promo policy + post type fit + rule confidence
- r/SubredditA - GO (text), rules checked YYYY-MM-DD, flair required: Discussion, link placement: first_comment
- r/SubredditB - GO (link), rules checked YYYY-MM-DD, no flair needed, link placement: body_end
- r/SubredditC - GO (text), rules checked YYYY-MM-DD, flair required: Discussion, link placement: first_comment

## Post for r/SubredditA
**Type:** text post
**Title:** ...
**Body:**
...

Blog URL: ...

## Post for r/SubredditB
**Type:** link post
**Title:** ...
**URL:** ...

## Post for r/SubredditC
**Type:** text post
**Title:** ...
**Body:**
...
```

Writing rules:
- Match subreddit tone and title style from current top posts
- For text posts, provide value first and link last
- No marketing phrasing
- If `link placement: first_comment`, do not include blog URL in post body

If any target uses `first_comment`, add copy-paste text to `comment-kit.md`:

```markdown
## Reddit first comment (r/SubredditA)
Blog URL: https://YOUR_BLOG_URL
```

## Step 6: Draft in Reddit UI (Do Not Publish)

1. Open `https://www.reddit.com/r/SUBREDDIT/submit`
2. Choose required post type (link/text)
3. Add required flair and title format
4. Fill content from `reddit.md`
5. Leave as draft, do not click `Post`
6. Capture screenshot for review
7. When handing off, include copy-paste Reddit first-comment lines for any `first_comment` targets

## Checklist

- [ ] Discovery script run with 4-6 query angles
- [ ] Analyzed candidate pool is ~30 (minimum 25)
- [ ] Top candidates manually rule-verified in browser
- [ ] Self-promo policy explicitly checked for each chosen subreddit
- [ ] 3-4 final subreddits selected
- [ ] Required post type/flair/title format respected
- [ ] `reddit.md` includes per-subreddit rule notes and draft copy
- [ ] UI drafts prepared but not published
- [ ] `comment-kit.md` updated for any `first_comment` targets
- [ ] Lint check passes:

```bash
python3 skills/blog-writing/scripts/lint_social_drafts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --blog-url https://YOUR_BLOG_URL \
  --cutoff-date 2026-02-20
```
