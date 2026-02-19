---
name: blog-writing
description: Write, edit, and format blog posts for kanyilmaz.me (Jekyll on GitHub Pages).
---

# Blog Writing Skill

Write and edit blog posts for kanyilmaz.me.

## Before Writing

Read `VOICE.md` in the repo root. It defines Kan's tone, structure, content patterns, and anti-AI-slop rules. Every draft must follow it.

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

- Header images go in `assets/posts/`
- Use Gemini API for image generation (key at `~/.config/gemini/api_key`)
- Imagen 4.0 for standalone images: `imagen-4.0-generate-001` endpoint
- Gemini Flash for image editing: `gemini-2.5-flash-image` endpoint
- Default aspect ratio: `16:9` for social-friendly blog headers

```bash
# Generate image
GEMINI_KEY=$(cat ~/.config/gemini/api_key)
curl -s -X POST \
  "https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict" \
  -H "x-goog-api-key: $GEMINI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "instances": [{"prompt": "YOUR PROMPT"}],
    "parameters": {"sampleCount": 1, "aspectRatio": "16:9"}
  }' | python3 -c "
import json, sys, base64
data = json.load(sys.stdin)
img = data.get('predictions', [{}])[0].get('bytesBase64Encoded', '')
if img:
    open('output.png', 'wb').write(base64.b64decode(img))
    print('saved')
"
```

```bash
# Edit existing image
GEMINI_KEY=$(cat ~/.config/gemini/api_key)
python3 << 'PYEOF'
import json, base64, urllib.request
key = open("/Users/kan/.config/gemini/api_key").read().strip()
with open("input.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()
body = json.dumps({
    "contents": [{"parts": [
        {"text": "YOUR EDIT INSTRUCTIONS"},
        {"inline_data": {"mime_type": "image/png", "data": img_b64}}
    ]}],
    "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]}
}).encode()
req = urllib.request.Request(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={key}",
    data=body, headers={"Content-Type": "application/json"})
resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
for candidate in resp.get("candidates", []):
    for part in candidate.get("content", {}).get("parts", []):
        if "inlineData" in part:
            open("output.png", "wb").write(base64.b64decode(part["inlineData"]["data"]))
            print("saved")
PYEOF
```

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
| X | `skills/x-publishing/SKILL.md` | `_posts/SLUG/x-article.md` |
| LinkedIn | `skills/linkedin-publishing/SKILL.md` | `_posts/SLUG/linkedin.md` |
| HN | `skills/hn-publishing/SKILL.md` | (no file needed) |
| Reddit | `skills/reddit-publishing/SKILL.md` | `_posts/SLUG/reddit.md` |

Read the relevant skill before creating each social version.
