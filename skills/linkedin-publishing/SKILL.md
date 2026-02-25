---
name: linkedin-publishing
description: Adapt a blog post into a compressed LinkedIn native post that hooks readers and drives clicks to the full article.
---

# LinkedIn Publishing Skill

Adapt a blog post into a LinkedIn native post. Not the full blog — a compressed version that drives engagement and puts the blog link in the first comment.
Read `VOICE.md` in repo root before drafting.
Read `skills/blog-writing/references/social-draft-contract.md` before drafting.

## Tools Required

- **browser** (OpenClaw browser tool) — for navigating LinkedIn and publishing

## Format Rules

### The Hook (First 2 Lines)
- These appear before "see more." They decide if anyone reads the rest.
- Keep the blog title's core claim in line 1 (exact title or very close derivative).
- Use the blog's strongest contrast or most provocative claim.
- No greetings, no preamble. Start with the punch.

### Structure
- **600-1200 characters** total. Tight.
- **No markdown.** LinkedIn renders plain text only.
- **No tables.** Use numbered lists with emoji markers (1️⃣ 2️⃣ etc).
- **No headers.** Use line breaks and whitespace for visual structure.
- **One blank line between every paragraph.** LinkedIn collapses multiple line breaks, so use them deliberately.
- **Low density by design.** Keep paragraphs short (1-3 sentences) and easy to skim.

### Content Adaptation
- **Personal angle first.** "I built X" beats "X is important." LinkedIn rewards personal experience.
- **Compress the argument hard.** Hit thesis, one key proof point, takeaway. Skip deep details.
- **End with a question OR a CTA.** Questions drive comments (LinkedIn algo rewards comments). CTA drives traffic.
- **No external links in the post body.** LinkedIn throttles reach on posts with external links. Blog URL goes in the first comment.
- **Attach the blog header image from source post frontmatter `image:`** for visual engagement.

### Tone
- Slightly more personal than the blog. First person throughout.
- Still direct, not corporate. No "I'm excited to share" or "Thrilled to announce."
- Conversational but sharp. Like explaining it to a smart colleague.

## File Location
Save as `social/YYYY-MM-DD-slug/linkedin.md` alongside the main blog post.
Also save/update `social/YYYY-MM-DD-slug/comment-kit.md`.

## Step -1: Prepare Artifacts (Required, Do Not Assume Files Exist)

Run this first, every time:

```bash
python3 skills/blog-writing/scripts/prepare_social_artifacts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --platform linkedin \
  --blog-url https://YOUR_BLOG_URL
```

This creates/updates if missing:
- `social/YYYY-MM-DD-slug/linkedin.md`
- `social/YYYY-MM-DD-slug/comment-kit.md`

## Publishing Steps

Use the browser tool for all steps.

1. **Open LinkedIn:** `browser navigate` to `https://www.linkedin.com` (use profile="openclaw", logged in as Kan Yilmaz)
2. **Create post:** Click "Start a post" on the feed
3. **Paste content:** Type/paste the `linkedin.md` content into the post editor using `browser act`
4. **Add image:** Click the image icon and upload the blog header image from `assets/posts/`
5. **Review:** Check first 2 lines carry title claim + hook before "see more"
6. **DO NOT click Post** — leave as draft for Kan to review
7. **Take a screenshot** of the draft for review
8. **After Kan approves and publishes:** First comment: Immediately comment on your own post with: "Full blog post with detailed breakdown: [BLOG_URL]"
9. **Do NOT put the blog link in the post itself** — LinkedIn penalizes external links in post body
10. **Prepare copy-paste comment text:** add to `comment-kit.md`:

```markdown
## LinkedIn first comment
Full blog post with detailed breakdown: https://YOUR_BLOG_URL
```

When handing off, include this exact line in the response so user can copy-paste directly.

## Checklist Before Publishing
- [ ] First 2 lines hook without context
- [ ] Line 1 preserves blog title's core claim
- [ ] 600-1200 characters
- [ ] No markdown syntax
- [ ] No external links in post body
- [ ] Personal angle present ("I built/tested/found")
- [ ] Low-density structure (short paragraphs, fast takeaway)
- [ ] Ends with question or CTA
- [ ] Header image attached
- [ ] Blog URL in first comment only
- [ ] No more than one emoji per line
- [ ] `comment-kit.md` includes LinkedIn first-comment text
- [ ] Lint check passes:

```bash
python3 skills/blog-writing/scripts/lint_social_drafts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --blog-url https://YOUR_BLOG_URL \
  --cutoff-date 2026-02-20
```
