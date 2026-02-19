---
name: x-publishing
description: Adapt a blog post into an X (Twitter) long-form article optimized for skimmability and mobile reading.
---

# X (Twitter) Publishing Skill

Adapt a blog post into an X long-form article. X Articles support rich text on Premium accounts.

## Tools Required

- **browser** (OpenClaw browser tool) — for screenshots, navigating X, publishing
- **wkhtmltoimage** — for rendering HTML tables to images from CLI

Install if missing:
```bash
brew install wkhtmltopdf  # includes wkhtmltoimage
```

## Format Rules

### Structure for Skimmability
- **Short paragraphs:** 2-4 lines max. One idea per paragraph.
- **Subheadings:** Every 3-5 paragraphs. Bold text as headers (X Articles don't render markdown headers).
- **Lists over walls of text:** Use bullet points and numbered lists aggressively.
- **Bold the key insight** in almost every section. Readers skim bold text first.
- **Mobile-first:** Most X users read on mobile. If a paragraph looks long on a phone screen, break it up.

### Content Adaptation
- **Replace tables with images.** Screenshot the rendered tables from the blog post and embed them as inline images in the article. X Articles don't render markdown tables — images are the only way to preserve table formatting.
- **Include visual elements throughout.** Break up text with images every 3-5 paragraphs. Screenshots, diagrams, charts from the blog all work. Visual elements increase time-on-post and engagement.
- **Links:** Use plain text URLs. The X editor will auto-link them.
- **Rich formatting is supported.** X Articles have a native editor with headings (H1, H2), bold, italic, bullet lists, numbered lists, blockquotes, and inline media. Use them. The `x-article.md` file uses markdown as a 1:1 mapping to the X editor — apply the same formatting when pasting into the editor.
- **Keep the full argument.** This is the complete post republished natively, not a summary.
- **Header image:** Upload the blog header image as the article cover.

### Tone
- Identical to the blog. No softening for the platform.
- Direct, opinionated, first-person.

### CTA
- Plain email address, no mailto links.
- Keep it one line at the end.

## File Location
Save as `_posts/YYYY-MM-DD-slug/x-article.md` alongside the main blog post.

## Step 1: Generate Table Screenshots

The X article uses `[IMAGE: filename.png]` placeholders where tables should go. Before publishing, generate an image for each placeholder.

### Option A: Screenshot from the live blog (preferred)

```bash
# Serve blog locally
cd /Users/kan/Code/Projects/thellimist.github.io
bundle exec jekyll serve --port 4000 &
sleep 5
```

Then use the browser tool:
1. `browser navigate` to `http://localhost:4000/post-slug`
2. For each table, use `browser screenshot` with `element="table"` (or `selector="table:nth-of-type(N)"` for specific tables)
3. Save each screenshot to `assets/posts/SLUG/table_name.png`

```bash
# Kill Jekyll after screenshots
kill %1
```

### Option B: Render tables as standalone HTML images

```bash
ASSETS_DIR="assets/posts/SLUG"
mkdir -p "$ASSETS_DIR"

# For each table, create a minimal HTML file with the table content
# Then render to image
cat > /tmp/table.html << 'EOF'
<html><head><style>
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; background: white; }
  table { border-collapse: collapse; width: 100%; font-size: 15px; }
  th { background: #1a1a2e; color: white; padding: 12px 16px; text-align: left; }
  td { padding: 10px 16px; border-bottom: 1px solid #eee; }
  tr:nth-child(even) { background: #f8f9fa; }
  strong { color: #1a1a2e; }
</style></head><body>
<!-- PASTE TABLE HTML HERE FROM THE BLOG POST -->
</body></html>
EOF

wkhtmltoimage --width 800 --quality 95 /tmp/table.html "$ASSETS_DIR/table_name.png"
```

### Placeholder Format

In the X article, tables are marked as:
```
[IMAGE: table_five_stages.png]
[IMAGE: table_grades.png]
[IMAGE: table_workflows.png]
```

Each `[IMAGE: X]` corresponds to a screenshot that must be generated and inserted inline when drafting in the X editor.

## Step 2: Serve Blog Locally (if needed for screenshots)

```bash
cd /Users/kan/Code/Projects/thellimist.github.io
bundle exec jekyll serve --port 4000 &
# Blog available at http://localhost:4000
# Kill after screenshots: kill %1
```

## Step 3: Publish to X

Use the browser tool for all steps.

1. **Open X:** `browser navigate` to `https://x.com` (use profile="openclaw", logged in as Kan)
2. **Create Article:** Navigate to `https://x.com/compose/article` or click compose → "Write Article"
3. **Add cover image:** `browser upload` the blog header image from `assets/posts/`
4. **Paste content:** Type/paste the `x-article.md` content into the article editor using `browser act`
5. **Insert table images inline:** Find each `[IMAGE: filename.png]` placeholder in the article. At each one, use the editor's image insert to upload the corresponding screenshot from `assets/posts/SLUG/`. Remove the placeholder text after inserting.
6. **Add any other visuals** from the blog (diagrams, charts) to break up long text
7. **Preview the article** — DO NOT publish. Leave as draft for Kan to review
8. **Take a screenshot** of the draft for review
9. **After Kan approves and publishes:** First comment: Reply to the published article with: "Full blog post: [BLOG_URL]"
10. **Do NOT put the blog link in the article itself** — it goes in the first comment only

## Checklist Before Publishing
- [ ] All tables converted to screenshot images and embedded
- [ ] No markdown link syntax remains
- [ ] Every section has a bold key insight
- [ ] No paragraph longer than 4 lines
- [ ] Subheading every 3-5 paragraphs
- [ ] Cover image set (blog header image)
- [ ] Visuals every 3-5 paragraphs
- [ ] CTA at the end with plain email
- [ ] Blog URL is in first comment, NOT in the article
