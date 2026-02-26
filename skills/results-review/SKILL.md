---
name: results-review
description: Review published social post performance across platforms, record snapshots 3 times per day for 3 days, and report metric deltas from the previous update.
---

# Results Review Skill

Track post performance after publishing and send structured updates.
Use this when posts are already live and you need recurring outcome reporting.

## Tools Required

- `python3`
- `browser` (OpenClaw browser tool) for reading live metrics on each platform

## Cadence (Mandatory)

- Frequency: 3 updates per day
- Duration: 3 consecutive days
- Total updates: 9

Suggested times (local): `09:00`, `14:00`, `20:00`

## Required Files

- Tracker file: `social/YYYY-MM-DD-slug/results-tracking.json`
- Snapshot template: `social/YYYY-MM-DD-slug/results-snapshot.template.json`
- Update outputs: `social/YYYY-MM-DD-slug/results-updates/*.md`
- Latest summary: `social/YYYY-MM-DD-slug/results-latest.md`

## Step 1: Prepare Tracking Artifacts

Run once before the first update:

```bash
python3 skills/results-review/scripts/prepare_results_review.py \
  --social-dir social/YYYY-MM-DD-slug \
  --timezone America/Los_Angeles
```

Then fill `results-tracking.json` `posts` array with every live post URL:
- X article post
- LinkedIn post
- HN post
- Every Reddit post (each subreddit is separate)

Do not skip any destination where the content was published.

## Step 2: Collect Live Metrics (OpenClaw Browser)

For each post URL in `results-tracking.json`:

1. Open URL in browser
2. Capture visible engagement metrics
3. Write them into a snapshot JSON payload

Use this shape:

```json
{
  "timestamp": "2026-02-26T09:00:00-08:00",
  "items": [
    {
      "post_id": "x_main",
      "likes": 120,
      "comments": 18,
      "reposts": 7,
      "bookmarks": 12,
      "views": 12400
    },
    {
      "post_id": "reddit_claudeai",
      "upvotes": 52,
      "comments": 14,
      "score": 51
    }
  ]
}
```

Tip: start from `results-snapshot.template.json` and fill numbers.

## Step 3: Record Snapshot + Generate Diff Report

```bash
python3 skills/results-review/scripts/record_results_snapshot.py \
  --social-dir social/YYYY-MM-DD-slug \
  --snapshot social/YYYY-MM-DD-slug/results-snapshot.template.json
```

This appends the snapshot, computes deltas from prior update, and writes:
- timestamped report under `results-updates/`
- `results-latest.md`

Do not manually patch `results-tracking.json` snapshots with text replacement.
Always use the script above so updates are JSON-safe and schema-compatible (`post_id` or legacy `id`).

If an update failed and you only need to re-sync the latest report from already-stored snapshots:

```bash
python3 skills/results-review/scripts/record_results_snapshot.py \
  --social-dir social/YYYY-MM-DD-slug \
  --refresh-latest-only
```

## Step 4: Send Update to User

Use `results-latest.md` content in the update message.

Required format per row:
- `post`
- `source` (for example `X`, `r/ClaudeAI`, `HN`, `LinkedIn`)
- engagement metrics
- diff from last update

## Checklist

- [ ] Tracker includes every published destination URL
- [ ] Snapshot collected for all tracked posts
- [ ] Diff report generated from previous snapshot
- [ ] Update count remains on cadence (3/day, 3 days)
- [ ] User update sent with clear per-post rows
