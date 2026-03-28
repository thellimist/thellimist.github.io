---
summary: "Generate and edit blog header/inline images using Gemini APIs and house style constraints."
read_when:
  - Generating or editing blog visuals, or updating post frontmatter image assets.
---

# Blog Image Generation Skill

Generate or edit blog images for kanyilmaz.me.

## Required Workflow

This skill always runs in 2 phases:

## 1. Ideation

Before generating any image, propose exactly 10 image ideas for the post.

Ideation rules:
- Capture the single core takeaway of the post in one visual.
- Keep the image simple: one focal idea, low clutter, easy to parse in 2 seconds.
- Prefer minimal text or no text.
- If the post compares two approaches, prefer left/right comparison panels.
- If comparison is not suitable, use one simple image and optional short text summary.
- Optional text overlay must be very short (max 5 words).

Ideation output format (use this shape):
1. `Idea 1`
Main idea: ...
Image: ...
Layout: `left/right comparison` or `single scene`
Text: `none` or `...`

Repeat through `Idea 10`.

Stop after ideation and wait for user selection.

### Ideation Examples

Use these as pattern references in future ideation. Format: `main idea ..., image ...`

- main idea: CLI and MCP do the same job, but CLI 94% cheaper. image: left/right comparison; left a stressed stick-monster wrapped in JSON-like cables labeled MCP, right a relaxed cool stick figure in sunglasses labeled CLI.
- main idea: coding agents complete work while most other agents return task lists. image: left/right comparison; left relaxed person at desk with checked tasks under "CODING AGENTS", right stressed person with long to-do paper under "EVERY OTHER AGENT".
- main idea: future generations will judge today’s accepted pain as barbaric. image: simple dark-on-amber scene with two human silhouettes arguing around a monitor pedestal, with headline text "Our kids will call us Barbaric".
- main idea: coding has evolved through clear eras into agentic engineering. image: single clean timeline labeled "Evolution of Coding" with five dated stages/icons (1940 to 2025+).
- main idea: a culture without "aunties" (social enforcers) becomes a distinct place. image: single illustrated scene with a large road-sign reading "LAND WITH NO AUNTIES" (no-auntie symbol), SF skyline and Golden Gate bridge in background.
- main idea: durable partnerships depend on three foundations. image: single centered tree composition labeled "Emotional Support" with roots/ground labels: Communication, Longevity, Shared values.

## 2. Creation

After user picks one or more ideas, generate images only for selected ideas.

Creation rules:
- For each selected idea, convert the ideation entry into a concrete generation prompt.
- Keep composition simple and centered on the selected main idea.
- Preserve house style (below).
- Generate one primary version first; generate alternates only if requested.
- Save output to the correct path and update frontmatter `image:` for header image tasks.

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

Before ideation and creation:
- Read `docs/voice/voice.md` to match tone and intent.
- Confirm target path in advance.

## Output Paths

- Header images: `assets/posts/<file-name>.png`
- Inline images: `assets/posts/<slug>/<file-name>.png`

Use lowercase, hyphen/underscore file names. Prefer `.png`.

## Defaults

- Default aspect ratio for headers: `16:9`
- Keep images social-friendly and title-consistent.
- X/Twitter banner (cover) guidance:
  - Generate/export a dedicated X Article cover image if needed.
  - Use `5:2` aspect ratio for X Article cover (empirically reliable).
  - Recommended export target: `2500x1000` (or any clean 5:2 variant).
  - Prefer extending/padding with white space to reach 5:2 instead of cropping key content.
  - Use `.jpg` for cover when upload reliability matters.
  - Keep file size under `2 MB` (hard max `5 MB`).

## Required Key

Gemini API key must be available via `GEMINI_API_KEY` env var or configured in `~/.openclaw/openclaw.json` under `skills."nano-banana-pro".apiKey`.

## Generate New Image (Nano Banana Pro / Gemini 3 Pro Image)

Uses the `nano-banana-pro` OpenClaw skill script for all image generation and editing.

Prompt structure:
- Subject/metaphor (one sentence)
- Environment + lighting
- Palette direction (light editorial or earthy dramatic)
- Composition notes (foreground/mid/background, negative space)
- Style constraints (editorial illustration, cinematic digital painting, minimal text)
- Optional micro text (0-5 words only; prefer none)

Prompt template:

```text
Create a blog header image for: "<POST TITLE>".
Core metaphor: <ONE clear metaphor>.
Scene: <environment and subject action>.
Style: editorial digital illustration, cinematic lighting, high depth, clean composition.
Palette: <light editorial OR earthy dramatic>, 2-4 dominant colors with one accent.
Composition: wide hero frame, clear central focal point, strong negative space for title overlay.
Do not add logos or UI chrome. Keep text minimal (prefer none; max 5 words if needed).
```

```bash
uv run /opt/homebrew/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py \
  --prompt "YOUR PROMPT" \
  --filename "output.png" \
  --aspect-ratio 16:9 \
  --resolution 1K
```

Move output to target path after review.

## Edit Existing Image (Nano Banana Pro)

```bash
uv run /opt/homebrew/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py \
  --prompt "YOUR EDIT INSTRUCTIONS" \
  --filename "output.png" \
  -i input.png \
  --resolution 2K
```

Multi-image composition (up to 14 images):

```bash
uv run /opt/homebrew/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py \
  --prompt "combine these into one scene" \
  --filename "output.png" \
  -i img1.png -i img2.png -i img3.png
```

## Post-Generation Checklist

- [ ] Output path is correct (`assets/posts/...`)
- [ ] File name is stable and readable
- [ ] Image matches post thesis and tone
- [ ] Style matches house patterns (single metaphor, restrained palette, clear focal point)
- [ ] Frontmatter `image:` points to the final header image path
