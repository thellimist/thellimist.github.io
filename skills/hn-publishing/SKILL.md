---
name: hn-publishing
description: Submit a blog post to Hacker News with optimal title and timing.
---

# Hacker News Publishing Skill

Submit a blog post to Hacker News. Minimal adaptation — HN readers click through to the original.

## Tools Required

- **browser** (OpenClaw browser tool) — for navigating HN and submitting

## Format Rules

### Title
- Use the blog title as-is if it's concrete and non-clickbait.
- HN penalizes hype words. Remove "revolutionary," "game-changing," etc.
- Factual, specific titles win. "Show HN:" prefix only if it's a project you built.
- Keep under 80 characters.

### Submission
- **URL:** Link directly to the blog post.
- **No self-post text.** Just title + URL.
- **Don't editorialize** in the title beyond what the blog says.

### Timing
- Weekday mornings US time: 9-11am ET for best traction.
- Avoid weekends and holidays.
- Check current time:
```bash
TZ="America/New_York" date "+%A %H:%M ET"
```

### No Blog Adaptation Needed
- HN readers expect full blog posts. Don't dumb it down.
- Tables, markdown, technical depth — all fine. HN audience is technical.
- The blog post itself is the HN-ready version.

## File Location
No separate file needed. Optionally note the submission title in `_posts/YYYY-MM-DD-slug/hn-title.md` if it differs from the blog title.

## Publishing Steps

Use the browser tool for all steps.

1. **Check timing:**
```bash
TZ="America/New_York" date "+%A %H:%M ET"
# Ideal: weekday, 9-11am ET
```
2. **Open HN:** `browser navigate` to `https://news.ycombinator.com/submit` (use profile="openclaw", logged in as thellimist)
3. **Fill title:** Type the blog title (or adapted version under 80 chars) into the title field
4. **Fill URL:** Paste the blog post URL into the url field
5. **Leave text field empty** — this is a link submission, not a self-post
6. **DO NOT click Submit** — leave the form filled for Kan to review
7. **Take a screenshot** of the filled form
8. **After Kan submits:** Monitor Check `https://news.ycombinator.com/newest` to confirm it appeared
9. **Engage: Be ready to reply to comments. HN rewards authors who respond thoughtfully and directly.

## Checklist Before Submitting
- [ ] Title is factual, under 80 chars, no hype
- [ ] URL goes to the blog post directly
- [ ] Current time is 9-11am ET on a weekday (or schedule for later)
- [ ] Logged in as thellimist
- [ ] Ready to engage in comments
