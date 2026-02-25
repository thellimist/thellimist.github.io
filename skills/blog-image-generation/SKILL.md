---
name: blog-image-generation
description: Generate and edit blog images for kanyilmaz.me posts using Gemini APIs (Imagen for new images, Gemini Flash Image for edits). Use when a blog needs a header image, inline visual, or image refinement.
---

# Blog Image Generation Skill

Generate or edit blog images for kanyilmaz.me.

## Before Generating

- Read `VOICE.md` in repo root to match the post's tone and visual direction.
- Confirm target path in advance.

## Output Paths

- Header images: `assets/posts/<file-name>.png`
- Inline images: `assets/posts/<slug>/<file-name>.png`

Use lowercase, hyphen/underscore file names. Prefer `.png`.

## Defaults

- Default aspect ratio for headers: `16:9`
- Keep images social-friendly and title-consistent.

## Required Key

Gemini API key must exist at:

`~/.config/gemini/api_key`

## Generate New Image (Imagen)

```bash
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
    print('saved output.png')
"
```

Move output to target path after review.

## Edit Existing Image (Gemini Flash Image)

```bash
python3 << 'PYEOF'
import json, base64, urllib.request

key = open('/Users/kan/.config/gemini/api_key').read().strip()
with open('input.png', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

body = json.dumps({
    'contents': [{'parts': [
        {'text': 'YOUR EDIT INSTRUCTIONS'},
        {'inline_data': {'mime_type': 'image/png', 'data': img_b64}}
    ]}],
    'generationConfig': {'responseModalities': ['TEXT', 'IMAGE']}
}).encode()

req = urllib.request.Request(
    f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={key}',
    data=body,
    headers={'Content-Type': 'application/json'}
)

resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
for candidate in resp.get('candidates', []):
    for part in candidate.get('content', {}).get('parts', []):
        if 'inlineData' in part:
            open('output.png', 'wb').write(base64.b64decode(part['inlineData']['data']))
            print('saved output.png')
PYEOF
```

## Post-Generation Checklist

- [ ] Output path is correct (`assets/posts/...`)
- [ ] File name is stable and readable
- [ ] Image matches post thesis and tone
- [ ] Frontmatter `image:` points to the final header image path
