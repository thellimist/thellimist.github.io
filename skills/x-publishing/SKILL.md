---
name: x-publishing
description: Adapt a blog post into an X (Twitter) long-form article and preserve unsupported visuals by capturing tables/custom sections as images, then inserting each image at matching [IMAGE: ...] placeholders in the X editor.
---

# X (Twitter) Publishing Skill

Adapt a blog post into an X article without losing tables or custom-styled blocks.
Read `VOICE.md` in repo root before drafting.
Read `skills/blog-writing/references/social-draft-contract.md` before drafting.

## Tools Required

- Browser automation for drafting/review (choose one):
  - `browser` (OpenClaw browser tool)
  - `browser-tools` CLI (`bin/browser-tools` in agent-skill repo)
- `node` + `npm`
- `python3` (for clipboard fallback script)
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

1. Open `https://x.com/compose/article` with browser automation (`browser` or `browser-tools nav`)
2. Add cover image from source frontmatter `image:` path
   - For X Article cover, use a dedicated `5:2` image (`2500x1000` preferred, `.jpg`, <2MB)
   - If source header is not `5:2`, create a dedicated X cover variant and use it
   - Prefer white side-padding to reach `5:2` rather than cropping important edges/corners
3. Paste article content from `x-article.md` (keep fenced code blocks)
4. For each placeholder in order:
- Insert matching image file from `assets/posts/slug/x-article/`
- Remove placeholder line after successful upload
5. Preview and verify visual placement
6. Leave as draft and take screenshot for review

## Step 5b: Fallback for Inline Image Insert (Known Working)

Use this when normal inline image insert fails in DraftJS.

Known-working method:
1. Connect Playwright to browser instance over CDP:
   - `playwright.chromium.connect_over_cdp("http://localhost:18800")`
2. Bring target page to front (`page.bring_to_front()`)
3. Move cursor to the correct DraftJS block via `page.evaluate(...)`
4. Read local PNG file, base64 encode it
5. In `page.evaluate(...)`, decode base64 to `Blob("image/png")`
6. Write image to clipboard:
   - `navigator.clipboard.write([new ClipboardItem({"image/png": blob})])`
7. Trigger real keyboard paste:
   - `page.keyboard.press("Meta+v")`
8. Verify image appears inline, then remove matching `[IMAGE: ...]` placeholder line

Why this works:
- X DraftJS ignores synthetic JS paste events.
- Native clipboard write + real keyboard paste uses browser paste pipeline that DraftJS accepts.

What usually fails (avoid):
- `setInputFiles` on hidden file input for inline images (cover-only path)
- "Add media" upload flows that never open a file chooser
- Synthetic `ClipboardEvent("paste")` + `DataTransfer`
- Fetching localhost image from `https://x.com` context (CORS/mixed content)
- Programmatically created `<input type=file>` with artificial file assignment

If you already have a working helper at `/tmp/clipboard_paste.py`, reuse it.

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
