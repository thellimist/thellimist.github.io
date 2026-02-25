---
name: x-publishing
description: Adapt a blog post into an X (Twitter) long-form article and preserve unsupported visuals by capturing tables/custom sections as images, then inserting each image at matching [IMAGE: ...] placeholders in the X editor.
---

# X (Twitter) Publishing Skill

Adapt a blog post into an X article without losing tables or custom-styled blocks.
Read `VOICE.md` in repo root before drafting.
Read `skills/blog-writing/references/social-draft-contract.md` before drafting.

## Tools Required

- `browser` (OpenClaw browser tool) - draft and review in X editor
- `node` + `npm`
- Local Chromium (default path usually `/opt/homebrew/bin/chromium`)

## Non-Negotiable Rules

1. X Articles do not reliably render markdown tables/custom HTML blocks.
Convert each unsupported section into an image and place it exactly where `[IMAGE: filename.png]` appears in `x-article.md`.
2. X Articles do support code blocks. Preserve source code snippets using fenced triple-backtick blocks in `x-article.md` (do not rasterize code unless explicitly requested).
3. Cover image must be the source post header image from `_posts/YYYY-MM-DD-slug.md` frontmatter `image:`.

## File Locations

- Article draft: `social/YYYY-MM-DD-slug/x-article.md`
- Comment templates: `social/YYYY-MM-DD-slug/comment-kit.md`
- Capture manifest: `social/YYYY-MM-DD-slug/x-image-manifest.json`
- Captured images: `assets/posts/slug/x-article/`
- Example manifest: `skills/x-publishing/assets/section-manifest.example.json`
- Capture tool: `skills/x-publishing/scripts/capture_x_article_images.mjs`

## Step -1: Prepare Artifacts (Required, Do Not Assume Files Exist)

Run this first, every time:

```bash
python3 skills/blog-writing/scripts/prepare_social_artifacts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --platform x \
  --blog-url https://YOUR_BLOG_URL
```

This creates/updates if missing:
- `social/YYYY-MM-DD-slug/x-article.md`
- `social/YYYY-MM-DD-slug/x-image-manifest.json`
- `social/YYYY-MM-DD-slug/comment-kit.md`

## Step 0: Source Audit (Required)

Identify:
- Source post: `_posts/YYYY-MM-DD-slug.md`
- Header image path from frontmatter `image:`
- Table count in source post
- Custom HTML block count in source post (`<div ...>`, custom sections)
- Fenced code blocks in source post

Before drafting in X editor:
- Ensure `x-article.md` includes image placeholders for every table/custom block you need preserved.
- Ensure `x-article.md` keeps code examples in fenced code blocks.

## Step 1: Add Placeholders in `x-article.md`

Use this exact syntax where visuals should appear:

```markdown
[IMAGE: table_five_stages.png]
[IMAGE: pricing_matrix.png]
[IMAGE: custom_workflow_block.png]
```

Keep placeholder names stable. The tool and insertion order depend on them.
If source has 3 unsupported blocks, there should be at least 3 placeholders.

## Step 2: Create the Selector Manifest

Create `social/YYYY-MM-DD-slug/x-image-manifest.json`:

```json
{
  "items": [
    {
      "placeholder": "table_five_stages.png",
      "selector": "article table:nth-of-type(1)",
      "note": "Five stages table"
    },
    {
      "placeholder": "custom_workflow_block.png",
      "selector": ".workflow-comparison",
      "wait_ms": 400,
      "note": "Custom styled section"
    }
  ]
}
```

Guidance:
- Use wrapper selectors (not just `table`) when title/caption/context must be visible.
- Use `wait_ms` for animated or late-rendering components.
- For comparison grids/custom components, target parent wrapper (`.comparison-grid`, `.comparison-block`, etc.), not child text nodes.

## Step 3: Capture Images with the Tool

Start the local blog:

```bash
cd /Users/kan/Code/Projects/thellimist.github.io
bundle exec jekyll serve --port 4000
```

In another shell:

```bash
node skills/x-publishing/scripts/capture_x_article_images.mjs \
  --url http://localhost:4000/post-slug \
  --article social/YYYY-MM-DD-slug/x-article.md \
  --manifest social/YYYY-MM-DD-slug/x-image-manifest.json \
  --out-dir assets/posts/slug/x-article \
  --chromium-path /opt/homebrew/bin/chromium
```

What the tool does:
- Validate manifest placeholders against `[IMAGE: ...]` in `x-article.md`
- Capture each selector as PNG
- Print insertion order matching article placeholder order
- Auto-install Playwright into `~/.cache/x-publishing-playwright` when missing

## Step 4: Quality Check Captures

Before opening X editor:
- Confirm each expected file exists in `assets/posts/slug/x-article/`
- Confirm no clipping/truncation
- Re-capture with better selector if needed (usually use a larger wrapper selector)
- Confirm capture count is enough to cover all source tables/custom blocks
- Run lint:

```bash
python3 skills/blog-writing/scripts/lint_social_drafts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --blog-url https://YOUR_BLOG_URL \
  --cutoff-date 2026-02-20
```

## Step 5: Draft in X (Do Not Publish)

1. Open `https://x.com/compose/article` with `browser`
2. Add cover image from source frontmatter `image:` path
3. Paste article content from `x-article.md` (keep fenced code blocks)
4. For each placeholder in order:
- Insert matching image file from `assets/posts/slug/x-article/`
- Remove placeholder line after successful upload
5. Preview and verify visual placement
6. Leave as draft and take screenshot for review

## Step 6: Prepare First Comment Text

Create/update `social/YYYY-MM-DD-slug/comment-kit.md` with:

```markdown
## X publish notes
Cover image: /assets/posts/your-header-image.png

## X first comment
Full blog post: https://YOUR_BLOG_URL
```

When handing off, include this exact line in the response so user can copy-paste directly.

## Checklist

- [ ] Every `[IMAGE: ...]` placeholder has a captured file
- [ ] Every captured file is inserted at correct placeholder location
- [ ] Source code snippets remain fenced code blocks in X draft
- [ ] No placeholder text remains in final draft
- [ ] No markdown link syntax remains
- [ ] Main blog URL is not in X article body
- [ ] Cover image set from source post frontmatter image
- [ ] Draft saved, not published
- [ ] `comment-kit.md` includes X first-comment text
