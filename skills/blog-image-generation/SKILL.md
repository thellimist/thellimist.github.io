---
name: blog-image-generation
description: Generate and edit blog images for kanyilmaz.me posts using Gemini APIs (Imagen for new images, Gemini Flash Image for edits). Use when a blog needs a header image, inline visual, or image refinement.
---

# Blog Image Generation Skill

Generate or edit blog images for kanyilmaz.me.

## House Style (from existing headers)

Use only these recent (non-1000x) images as style anchors:
- `assets/posts/cli_vs_mcp.png`
- `assets/posts/five_stages.png`
- `assets/posts/pain_barbar.jpeg`
- `assets/posts/code_evolution.png`
- `assets/posts/land_with_no_aunties.png`
- `assets/posts/emotional_support_tree.png`

Observed patterns to preserve:
- Concept-first visuals; each image communicates one clear idea.
- Strong metaphor or symbolic scene (tree, staged flow, conflict image), not generic stock moments.
- Clear focal subject with simple scene geometry and readable background.
- Palette is limited and intentional: either soft neutrals + one cool accent, or earthy warm tones.
- Minimal/no embedded text in generated art.

Quantitative guardrails (derived from these 6 images only):
- Aspect ratio median is `~1.64`. Prefer wide headers in `1.5` to `1.91`; use `1:1` only when the concept requires a centered emblematic scene.
- Saturation median is moderate (`~0.26`): keep base tones restrained and let one area carry stronger color.
- Brightness median is high (`~0.86`), but dark/earthy scenes are acceptable for intense topics.
- Contrast median is medium-high (`~0.23`): subject separation should stay readable at social preview size.

Use one of two visual modes from this 6-image baseline:
- **Light editorial mode**: bright neutral backgrounds, clean shapes, muted cool accents. Best for process/framework posts.
- **Earthy dramatic mode**: warm earth palette (amber/olive/brown), stronger subject lighting, emotional tension. Best for struggle/transformation themes.

Avoid:
- Generic corporate stock-photo look.
- Overcrowded scenes with many focal points.
- Neon/rainbow palettes and overly glossy 3D icon packs.
- Flat clip-art style unless the post is explicitly diagram-focused.

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

Prompt structure:
- Subject/metaphor (one sentence)
- Environment + lighting
- Palette direction (light editorial or earthy dramatic)
- Composition notes (foreground/mid/background, negative space)
- Style constraints (editorial illustration, cinematic digital painting, minimal text)

Prompt template:

```text
Create a blog header image for: "<POST TITLE>".
Core metaphor: <ONE clear metaphor>.
Scene: <environment and subject action>.
Style: editorial digital illustration, cinematic lighting, high depth, clean composition.
Palette: <light editorial OR earthy dramatic>, 2-4 dominant colors with one accent.
Composition: wide hero frame, clear central focal point, strong negative space for title overlay.
Do not add logos, UI chrome, or visible text.
```

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
- [ ] Style matches house patterns (single metaphor, restrained palette, clear focal point)
- [ ] Frontmatter `image:` points to the final header image path
