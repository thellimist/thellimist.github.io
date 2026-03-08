---
summary: "Add or update chocolates in the tier list with reliable image sourcing and explicit user confirmation checkpoints."
read_when:
  - Adding, updating, or fixing entries in chocolate/chocolates.json.
  - Sourcing chocolate images from Notes, local files, prompts, or online references.
---

# Chocolate Maintenance Skill

Use this workflow whenever adding or updating chocolates in the tier list.

## Files

- `chocolate/chocolates.json` - source of truth for entries.
- `assets/chocolate-images/` - chocolate item images.
- `chocolate/index.html` - rendering logic and filters.

## Data Contract For Each Chocolate

Each JSON object should include:

- `name` - full display name, including variant and percentage when known.
- `tier` - one of `S`, `A`, `B`, `C`, `D`.
- `brand` - brand/manufacturer.
- `picture` - path like `/assets/chocolate-images/<file>.jpg` or fallback `/assets/no_image.png`.
- `country` - where Kan bought it or where he wants to classify it (must confirm).
- `location` - optional URL (store google maps link. Used exclusively for shops that are boutique, has one shop only. Not used for chains)
- `comments` - optional short tasting note.

## Mandatory Clarifications To Ask Kan

If any of these are unknown, ask before finalizing:

- Exact chocolate variant name.
- Tier.
- Country label preference.
- Comments/tasting note.
- Location URL.
- Whether an entry is new or should replace/update an existing one.

First try to get all these information, before asking. 

## Image Source Paths

Choose one path based on what Kan provides.

### Path A - Apple Notes Image

Use when user says image is in Notes.

1. Find the note by keyword:
   - `notes list chocolate`
2. Read note text and metadata:
   - `notes cat "<note name>" --json --plaintext`
3. Find recent media attachments in Apple Notes container:
   - `find ~/Library/Group\\ Containers/group.com.apple.notes/Accounts -type f \\( -iname '*.heic' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \\) -mmin -300`
4. Convert `.heic` to `.jpg` if needed:
   - `sips -s format jpeg input.heic --out output.jpg`
5. Visually inspect to identify exact variant names before writing JSON.

### Path B - User-Provided Local Image File

1. Copy into `assets/chocolate-images/`.
2. Rename to stable lowercase slug.
3. Re-encode and resize (see normalization section).

### Path C - Find Original Image Online

Use when no usable local/Notes image exists or when it exists, but user asks for a more professional image.

1. Prefer official/primary sources first:
   - Brand official product page.
   - Brand official store listing.
   - Brand official press/media kit.
2. Secondary sources if official not available:
   - Reputable retailers with clear front-pack shots.
   - Google images
3. Prepare exactly 1 or 2 candidate image options. Never provide more than 2.
4. Share options with Kan and ask him to confirm exactly one option before download/use.
5. Record chosen source URL in task notes (and optionally use `location` if useful).

Required confirmation format to Kan:

0. Original photo (reference only, if provided) - `<short label>`
1. Candidate 1 - `<short label>` - `<why this is likely correct>`
2. Candidate 2 (optional) - `<short label>` - `<why this is likely correct>`

If only one candidate is shown, ask:
"Reply with `use-original`, `use-1`, or `keep-searching`."

If two candidates are shown, ask:
"Reply with `use-original`, `use-1`, `use-2`, or `keep-searching`."

If you realize original and option are not the exact same chocolate, continue searching until you find an option that is worth asking

### Path D - No Image For Now

Use when Kan says to proceed without an image.

1. Do not run online image search unless Kan explicitly asks.
2. Set `picture` to `/assets/no_image.png`.
3. Add/update the chocolate entry normally (tier, name, brand, country, comments, location as available).
4. Call out in handoff that placeholder image is being used.

## Image Normalization

Before commit, normalize each new image:

1. Convert to JPEG if needed.
2. Resize longest edge to about `900px`:
   - `sips -Z 900 <file>`
3. Compress to manageable quality:
   - `sips -s format jpeg -s formatOptions 68 <file> --out <file>`
4. Fix orientation if sideways:
   - Rotate counterclockwise 90: `sips -r 270 <file>`
5. Verify visually after processing.

## Naming Convention

Use descriptive lowercase filenames with hyphens:

- `<brand>-<variant>-<cacao-percent>.jpg`
- Examples:
  - `alain-ducasse-perou-75.jpg`
  - `yves-thuries-noir-noisettes-entieres.jpg`

## JSON Update Workflow

1. Append or edit entry in `chocolate/chocolates.json`.
2. Keep JSON formatting consistent with existing file.
3. Validate:
   - `jq empty chocolate/chocolates.json`
4. Spot-check entry:
   - `jq '.[] | select(.name | test("Brand or Variant"))' chocolate/chocolates.json`

## Quality Gate Before Handoff

- Chocolate is exact same chocolate that was asked. 
- JSON valid.
- Image path exists on disk.
- Image is upright and readable.
- Tier and comments match Kan's latest instruction.
- Country/brand filters still make sense.
- `git diff` only includes intended chocolate changes.

## Handoff Format

When reporting back, include:

1. What was added/updated.
2. Final tier per item.
3. Exact new image filenames.
4. Any unresolved fields that need Kan confirmation.
