---
summary: "Prepare Hacker News link submissions with required account-health checks and timing/title rules."
read_when:
  - Preparing an HN submission for a published blog post.
---

# Hacker News Publishing Skill

Submit a blog post to Hacker News. Minimal adaptation — HN readers click through to the original.
Read `docs/blog-writing/references/social-draft-contract.md` before drafting optional HN notes.

## Tools Required

- Browser automation (choose one):
  - **browser** (OpenClaw browser tool)
  - **browser-tools** CLI (`bin/browser-tools` in agent-skill repo)

## Account Health Checks (Required)

Run these checks before preparing any self-link submission.

### Submission mix check
- Open `https://news.ycombinator.com/submitted?id=thellimist`.
- Inspect last 20 submissions (or all if fewer than 20).
- Classify each as:
  - Own link (your domain/projects)
  - Unrelated link (good external story)
  - Major-site link (YouTube, X/Twitter, Medium, etc.)
  - Ask HN / Show HN (text posts)

### Go / no-go rules
- **No-go for self-link** if own links are >40% of last 20.
- **No-go for self-link** if there are fewer than 5 unrelated external links in last 20.
- **No-go for self-link** if history is sparse (`<8` total submissions) and most recent 3 are self-links.
- In no-go state, do not submit your own post that day.

### Recovery actions (when in no-go state)
- Submit 5-10 unrelated, intellectually interesting links over multiple days.
- Prefer niche/novel sources; avoid major sites for this recovery set.
- Avoid Ask HN / Show HN during recovery.
- Re-check submission mix before next self-link.

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
No separate file needed. Optionally note submission title candidates in `social/YYYY-MM-DD-slug/hn.md` if title differs from the blog title.

## Publishing Steps

Use browser automation for all steps (`browser` or `browser-tools`).

1. **Run account health checks:** verify Go state from the required checks above.
2. **Check timing:**
```bash
TZ="America/New_York" date "+%A %H:%M ET"
# Ideal: weekday, 9-11am ET
```
3. **Open HN:** open `https://news.ycombinator.com/submit`
   - `browser`: `browser navigate`
   - `browser-tools`: `browser-tools nav`
   - Use profile/session logged in as `thellimist`
4. **Fill title:** Type the blog title (or adapted version under 80 chars) into the title field
5. **Fill URL:** Paste the blog post URL into the url field
6. **Leave text field empty** — this is a link submission, not a self-post
7. **DO NOT click Submit** — leave the form filled for Kan to review
8. **Take a screenshot** of the filled form
9. **After Kan submits:** Monitor `https://news.ycombinator.com/newest` to confirm it appeared
10. **Engage:** Be ready to reply to comments. HN rewards authors who respond thoughtfully and directly.

## Checklist Before Submitting
- [ ] Account health check passed (Go state for self-link)
- [ ] Submission history is mixed (not mostly own links)
- [ ] Title is factual, under 80 chars, no hype
- [ ] URL goes to the blog post directly
- [ ] Current time is 9-11am ET on a weekday (or schedule for later)
- [ ] Logged in as thellimist
- [ ] Ready to engage in comments
