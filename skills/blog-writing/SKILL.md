---
name: blog-writing
description: Write, edit, and format blog posts for kanyilmaz.me (Jekyll on GitHub Pages).
---

# Blog Writing Skill

Write and edit blog posts for kanyilmaz.me.

## Before Writing

Read `VOICE.md` in the repo root. It defines Kan's tone, structure, content patterns, and anti-AI-slop rules. Every draft must follow it.
Read `skills/blog-writing/references/social-draft-contract.md` before generating any social format draft.
If the task includes generating or editing blog images, use `skills/blog-image-generation/SKILL.md`.

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

## Images

- Header images go in `assets/posts/`.
- For generation/editing workflow and commands, use `skills/blog-image-generation/SKILL.md`.

## Publishing

After the blog post is ready:

```bash
cd /Users/kan/Code/Projects/thellimist.github.io
git add -A
git commit -m "Add blog: POST TITLE"
git push
```

GitHub Pages builds automatically. Blog appears at kanyilmaz.me within minutes.

## Social Versions

After publishing the blog, create social versions using the publishing skills:

| Platform | Skill | File |
|----------|-------|------|
| X | `skills/x-publishing/SKILL.md` | `social/YYYY-MM-DD-slug/x-article.md` |
| LinkedIn | `skills/linkedin-publishing/SKILL.md` | `social/YYYY-MM-DD-slug/linkedin.md` |
| HN | `skills/hn-publishing/SKILL.md` | (no file needed) |
| Reddit | `skills/reddit-publishing/SKILL.md` | `social/YYYY-MM-DD-slug/reddit.md` |

Read the relevant skill before creating each social version.

## Social Draft Quality Gate

Run lint before handoff:

```bash
python3 skills/blog-writing/scripts/lint_social_drafts.py \
  --social-dir social/YYYY-MM-DD-slug \
  --blog-url https://YOUR_BLOG_URL \
  --cutoff-date 2026-02-20
```

When handing off prepared drafts, include copy-paste first-comment text in the response (from `comment-kit.md`) for each platform that prefers links in comments.

## Enforcement Hooks

- Claude hook config: `.claude/settings.json`
- Hook scripts: `.claude/hooks/`
- Install git pre-push gate once:

```bash
bash .claude/hooks/install-git-hooks.sh
```
