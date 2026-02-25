# Social Draft Contract

Canonical contract for all social format outputs.

## Canonical Paths

- Blog post: `_posts/YYYY-MM-DD-slug.md`
- Social drafts: `social/YYYY-MM-DD-slug/`
- Comment templates: `social/YYYY-MM-DD-slug/comment-kit.md`
- X capture manifest: `social/YYYY-MM-DD-slug/x-image-manifest.json`
- X captured assets: `assets/posts/slug/x-article/`

`slug` for assets means the post slug without date prefix.
Example: `2026-02-19-five-stages-of-ai-agents` -> `five-stages-of-ai-agents`.

## `x-article.md`

- Full argument, not summary.
- Must start with H1 line (`# ...`).
- No markdown link syntax (`[text](url)`); use plain URLs.
- Unsupported visuals must use placeholders: `[IMAGE: filename.png]`.
- Each placeholder must map to a captured image under `assets/posts/slug/x-article/`.
- Do not include the main blog URL in the article body.
- Put the main blog URL in the first comment after publishing.

## `linkedin.md`

- Target length: 1300-1500 chars.
- No markdown syntax (headers, tables, markdown links).
- No external links in body. Blog URL goes in first comment after publish.
- Strong first two lines. Personal angle + clear takeaway.

## `comment-kit.md`

- Must include copy-paste ready comment text for platforms that prefer links in comments.
- Minimum sections:
  - `## X first comment`
  - `## LinkedIn first comment`
- Use plain text and include the full blog URL.
- Example template: `skills/blog-writing/assets/comment-kit.example.md`

## `reddit.md`

- Must include `## Target Subreddits` section.
- Must include one or more `## Post for r/Subreddit` sections.
- Each target must note rule check date and go/no-go status.
- Draft must match subreddit-required post type (link vs text).
- For text posts, decide link placement per subreddit:
  - `body_end` if subreddit expects link in body
  - `first_comment` if subreddit discourages promo links in body
- If `first_comment`, add a Reddit section in `comment-kit.md` for that subreddit.

## `hn.md` (optional)

- Most HN submissions need no file.
- If present, include title candidate(s), each <= 80 chars.

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
python3 skills/blog-writing/scripts/lint_social_drafts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --blog-url https://YOUR_BLOG_URL \
  --cutoff-date 2026-02-20
```
