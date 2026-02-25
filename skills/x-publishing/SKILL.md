---
name: x-publishing
description: Adapt a blog post into an X (Twitter) long-form article and preserve unsupported visuals by capturing tables/custom sections as images, then inserting each image at matching [IMAGE: ...] placeholders in the X editor.
---

# X (Twitter) Publishing Skill

Adapt a blog post into an X article without losing tables or custom-styled blocks.
Read `skills/blog-writing/references/social-draft-contract.md` before drafting.

## Tools Required

- `browser` (OpenClaw browser tool) - draft and review in X editor
- `node` + `npm`
- Local Chromium (default path usually `/opt/homebrew/bin/chromium`)

## Non-Negotiable Rule

X Articles do not render markdown tables/custom HTML blocks reliably. Convert each unsupported section into an image and place it exactly where `[IMAGE: filename.png]` appears in `x-article.md`.

## File Locations

- Article draft: `social/YYYY-MM-DD-slug/x-article.md`
- Comment templates: `social/YYYY-MM-DD-slug/comment-kit.md`
- Capture manifest: `social/YYYY-MM-DD-slug/x-image-manifest.json`
- Captured images: `assets/posts/slug/x-article/`
- Example manifest: `skills/x-publishing/assets/section-manifest.example.json`
- Capture tool: `skills/x-publishing/scripts/capture_x_article_images.mjs`

## Step 1: Add Placeholders in `x-article.md`

Use this exact syntax where visuals should appear:

```markdown
[IMAGE: table_five_stages.png]
[IMAGE: pricing_matrix.png]
[IMAGE: custom_workflow_block.png]
```

Keep placeholder names stable. The tool and insertion order depend on them.

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
- Run lint:

```bash
python3 skills/blog-writing/scripts/lint_social_drafts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --blog-url https://YOUR_BLOG_URL
```

## Step 5: Draft in X (Do Not Publish)

1. Open `https://x.com/compose/article` with `browser`
2. Add cover image (blog header)
3. Paste article content from `x-article.md`
4. For each placeholder in order:
- Insert matching image file from `assets/posts/slug/x-article/`
- Remove placeholder line after successful upload
5. Preview and verify visual placement
6. Leave as draft and take screenshot for review

## Step 6: Prepare First Comment Text

Create/update `social/YYYY-MM-DD-slug/comment-kit.md` with:

```markdown
## X first comment
Full blog post: https://YOUR_BLOG_URL
```

When handing off, include this exact line in the response so user can copy-paste directly.

## Checklist

- [ ] Every `[IMAGE: ...]` placeholder has a captured file
- [ ] Every captured file is inserted at correct placeholder location
- [ ] No placeholder text remains in final draft
- [ ] No markdown link syntax remains
- [ ] Main blog URL is not in X article body
- [ ] Cover image set
- [ ] Draft saved, not published
- [ ] `comment-kit.md` includes X first-comment text
