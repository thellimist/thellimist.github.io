---
summary: "Write, edit, and format blog posts for kanyilmaz.me"
read_when:
  - Writing or editing blog posts, markdown structure, or social artifact prep workflows.
  - Starting a new blog post (interactive discovery, outline, and drafting workflow).
---

# Blog Writing Skill

Write and edit blog posts for kanyilmaz.me.

## Before Writing

Read `docs/voice/voice.md`. It defines Kan's tone, structure, content patterns, and anti-AI-slop rules. Every draft must follow it.
Read `docs/blog-writing/references/social-draft-contract.md` before generating any social format draft.
If the task includes generating or editing blog images, use `docs/blog-image-generation/blog-image-generation.md`.

## Writing Process

**Do not write prose until Kan approves an outline.** No exceptions - not even "just a rough draft." Follow these phases in order.

### Phase 1: Discovery Questions

Before anything else, ask Kan these questions and wait for answers:

1. **Thesis** - What's the core claim in one sentence?
2. **Audience** - Who's the reader? (developers, founders, general public, mixed?)
3. **Takeaway** - What's the one thing the reader should walk away with?
4. **Angle** - What's the contrarian or non-obvious take? Why would someone disagree?
5. **Anchors** - Any specific experiences, anecdotes, or data to build around?
6. **Comparisons** - Any existing blog posts this should feel closest to in style/structure?
7. **Scope** - Short and punchy (~800 words) or long-form deep dive (~2000+ words)?

Don't ask all seven if Kan already provided context. Skip what's already clear, ask what's missing.

### Phase 2: Outline Options

Before outlining, read 2-3 recent posts in `_posts/` to calibrate tone and structure beyond what `voice.md` describes. Match the actual writing, not just the rules.

After getting answers, present **2-3 outline options** with different structures. For each option show:

- Opening hook (the actual first line, not a description of it)
- Section headings with 1-line summary of each
- Where tables, quotes, or visuals would go
- Estimated word count

Example structures to draw from:
- **Claim-first:** Bold opener → evidence → implications → punch ending
- **Story-in:** Anecdote → zoom out to principle → apply broadly → land it
- **Framework:** Taxonomy/model → walk through each part → synthesis
- **Contrast:** Show the wrong way → flip to the right way → why it matters

### Phase 3: Outline Approval

Wait for Kan to pick an outline (or mix elements from multiple). He may also:
- Reorder sections
- Add/remove sections
- Change the hook
- Adjust scope

If Kan explicitly says to skip phases, respect that. The gate is a default, not a cage.

If Kan rejects all outlines:
- If the feedback is specific ("too listicle-y", "wrong angle"), generate a new round incorporating that feedback.
- If the feedback is vague ("none of these work"), ask what's missing or what feels off before generating more. Don't just throw 3 more random options at the wall.

Incorporate feedback and confirm the final outline before proceeding.

### Phase 4: Draft

Only now write the full post. Follow the approved outline and `docs/voice/voice.md` strictly.

After drafting, self-review against the anti-slop rules in VOICE.md before presenting.

## Blog Post Format

Jekyll markdown with frontmatter:

```markdown
---
layout: default
title: "Your Title Here"
date: YYYY-MM-DD
image: "/assets/posts/image_name.png"
---

# Your Title Here

![](/assets/posts/image_name.png)

Content here...
```

## File Structure

```
_posts/
  YYYY-MM-DD-slug.md                    # blog post (Jekyll reads this)

social/
  YYYY-MM-DD-slug/                      # social versions (NOT in _posts — Jekyll would index them)
    x-article.md
    linkedin.md
    reddit.md
    comment-kit.md

assets/posts/
  image_name.png                        # header images
  SLUG/                                 # table screenshots and inline images
    table_name.png
```

## CSS / Styling

The blog uses a custom stylesheet. Key classes available:

```html
<details><summary>Collapsible section</summary>
  Content here
</details>

<span class="spoiler">Hidden text revealed on hover/click</span>
```

Tables render natively from markdown. Use standard markdown table syntax.

### Internal Blog Link Cards

Use `.blog-link-card` to link to related posts. Thin bordered rectangle with title and arrow. Max 3 per post.

```html
<a href="/YYYY/MM/DD/post-slug" class="blog-link-card">
<span class="blog-link-card-title">Post Title Here</span>
<span class="blog-link-card-arrow">↗</span>
</a>
```

**Important:** Use `<span>` not `<p>` inside the `<a>` tag. Do not indent the inner tags - Kramdown will break the HTML.

Placement rules:
- **Highly related**: place inline near the relevant section (mid-post)
- **Less related**: place at the end, before the CTA line

## Images

- Header images go in `assets/posts/`.
- For generation/editing workflow and commands, use `docs/blog-image-generation/blog-image-generation.md`.

## Publishing

After the blog post is ready:

```bash
cd /Users/kan/Projects/code/thellimist.github.io
git add -A
git commit -m "Add blog: POST TITLE"
git push
```

GitHub Pages builds automatically. Blog appears at kanyilmaz.me within minutes.

## Social Versions

After publishing the blog, create social versions using the publishing skills:

| Platform | Skill | File |
|----------|-------|------|
| X | `docs/x-publishing/x-publishing.md` | `social/YYYY-MM-DD-slug/x-article.md` |
| LinkedIn | `docs/linkedin-publishing/linkedin-publishing.md` | `social/YYYY-MM-DD-slug/linkedin.md` |
| HN | `docs/hn-publishing/hn-publishing.md` | (no file needed) |
| Reddit | `docs/reddit-publishing/reddit-publishing.md` | `social/YYYY-MM-DD-slug/reddit.md` |

Read the relevant skill before creating each social version.
Do not assume social draft files already exist; run:

```bash
python3 docs/blog-writing/scripts/prepare_social_artifacts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --platform <x|linkedin|reddit> \
  --blog-url https://YOUR_BLOG_URL
```

before platform-specific drafting.

## Social Draft Quality Gate

Run lint before handoff:

```bash
python3 docs/blog-writing/scripts/lint_social_drafts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --blog-url https://YOUR_BLOG_URL \
  --cutoff-date 2026-02-20
```

When handing off prepared drafts, include copy-paste first-comment text in the response (from `comment-kit.md`) for each platform that prefers links in comments.
Also include copy-paste manual-post blocks for `Vibecoding WhatsApp` and `Bookface post` from `comment-kit.md` when present.

## Enforcement Hooks

- Claude hook config: `.claude/settings.json`
- Hook scripts: `.claude/hooks/`
- Install git pre-push gate once:

```bash
bash .claude/hooks/install-git-hooks.sh
```
