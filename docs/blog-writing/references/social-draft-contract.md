---
summary: "Contract and quality gates for generating social drafts from a published blog post."
read_when:
  - Preparing social drafts (X, LinkedIn, Reddit, HN) from a source post.
---
# Social Draft Contract

Canonical contract for all social format outputs.

## Canonical Paths

- Blog post: `_posts/YYYY-MM-DD-slug.md`
- Social drafts: `social/YYYY-MM-DD-slug/`
- Comment templates: `social/YYYY-MM-DD-slug/comment-kit.md`
- X capture manifest: `social/YYYY-MM-DD-slug/x-image-manifest.json`
- X captured assets: `assets/posts/slug/x-article/`
- Results tracker: `social/YYYY-MM-DD-slug/results-tracking.json`
- Results updates: `social/YYYY-MM-DD-slug/results-updates/*.md`

`slug` for assets means the post slug without date prefix.
Example: `2026-02-19-five-stages-of-ai-agents` -> `five-stages-of-ai-agents`.

## Artifact Preparation (Mandatory)

Agents must never assume social artifacts already exist.
Before platform drafting, run:

```bash
python3 docs/blog-writing/scripts/prepare_social_artifacts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --platform <x|linkedin|reddit> \
  --blog-url https://YOUR_BLOG_URL
```

Then continue with platform-specific drafting/publishing steps.

## `x-article.md`

- Full argument, not summary.
- Must start with H1 line (`# ...`).
- No markdown link syntax (`[text](url)`); use plain URLs.
- If source blog has fenced code blocks, preserve them with triple-backtick code fences in `x-article.md`.
- Unsupported visuals must use placeholders: `[IMAGE: filename.png]`.
- Placeholder coverage must match source unsupported visuals (tables + custom HTML blocks).
- Each placeholder must map to a captured image under `assets/posts/slug/x-article/`.
- Do not include the main blog URL in the article body.
- Put the main blog URL in the first comment after publishing.
- In X editor draft, cover image must be the source post frontmatter `image:` asset.

## `linkedin.md`

- Target length: 600-1200 chars.
- No markdown syntax (headers, tables, markdown links).
- No external links in body. Blog URL goes in first comment after publish.
- Strong first two lines. Preserve the blog title's core claim in the hook.
- Keep density low: short paragraphs, fast summary.

## `comment-kit.md`

- Must include copy-paste ready comment text for platforms that prefer links in comments.
- Minimum sections:
  - `## X publish notes` (must include cover image path from source frontmatter)
  - `## X first comment`
  - `## LinkedIn first comment`
- Recommended manual-post sections:
  - `## Vibecoding WhatsApp`
  - `## Bookface post`
- Use plain text and include the full blog URL.
- Example template: `docs/blog-writing/assets/comment-kit.example.md`

## `reddit.md`

- Must include `## Target Subreddits` section.
- Must include `Candidates reviewed: N` with `N >= 25`.
- Must include one or more `## Post for r/Subreddit` sections.
- Must include 3-4 selected target subreddits.
- Each target must note rule check date and go/no-go status.
- Draft must match subreddit-required post type (link vs text).
- For text posts, decide link placement per subreddit:
  - `body_end` if subreddit expects link in body
  - `first_comment` if subreddit discourages promo links in body
- If `first_comment`, add a Reddit section in `comment-kit.md` for that subreddit.

## `hn.md` (optional)

- Most HN submissions need no file.
- If present, include title candidate(s), each <= 80 chars.

## Results Review (optional)

- For live performance tracking, use `docs/results-review.md`.
- Track all published destinations (X, LinkedIn, HN, each Reddit subreddit URL).
- Cadence target: 3 updates/day for 3 days.
- Update rows must include: post, source, metrics, diff from last update.

## Shared Quality Floor

- Avoid banned AI-slop phrasing in `VOICE.md`.
- Fix obvious grammar breakages before draft handoff.
- When handing off drafts, include copy-paste first-comment text in the agent response.
- Hook enforcement (Claude Code): `.claude/settings.json` runs social lint automatically after `Write|Edit|MultiEdit` on social files.
- Git enforcement (pre-push): install with:

```bash
bash .claude/hooks/install-git-hooks.sh
```

- Pre-push hook lints changed `social/YYYY-MM-DD-slug/` folders and blocks push on failures.
- Run social lint before final handoff:

```bash
python3 docs/blog-writing/scripts/lint_social_drafts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --blog-url https://YOUR_BLOG_URL \
  --cutoff-date 2026-02-20
```
