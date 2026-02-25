#!/usr/bin/env python3

import argparse
import json
from pathlib import Path


def default_tracker(timezone: str) -> dict:
    return {
        "review_plan": {
            "updates_per_day": 3,
            "days": 3,
            "timezone": timezone,
            "times_local": ["09:00", "14:00", "20:00"],
        },
        "posts": [],
        "snapshots": [],
    }


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_snapshot_template(tracker: dict) -> dict:
    items = []
    for post in tracker.get("posts", []):
        post_id = str(post.get("post_id", "")).strip()
        if not post_id:
            continue
        items.append(
            {
                "post_id": post_id,
                "likes": 0,
                "comments": 0,
            }
        )
    return {"timestamp": "YYYY-MM-DDTHH:MM:SS±HH:MM", "items": items}


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare result-review artifacts for social post performance tracking.")
    parser.add_argument("--social-dir", required=True, help="Path like social/YYYY-MM-DD-slug")
    parser.add_argument("--timezone", default="America/Los_Angeles", help="Local timezone label")
    args = parser.parse_args()

    social_dir = Path(args.social_dir)
    social_dir.mkdir(parents=True, exist_ok=True)

    tracker_path = social_dir / "results-tracking.json"
    updates_dir = social_dir / "results-updates"
    updates_dir.mkdir(parents=True, exist_ok=True)

    if tracker_path.exists():
        tracker = json.loads(tracker_path.read_text(encoding="utf-8"))
    else:
        tracker = default_tracker(args.timezone)
        write_json(tracker_path, tracker)

    template_path = social_dir / "results-snapshot.template.json"
    template = build_snapshot_template(tracker)
    write_json(template_path, template)

    print(f"Prepared: {tracker_path}")
    print(f"Prepared: {template_path}")
    print(f"Prepared: {updates_dir}")
    print("Next: fill results-tracking.json posts[] with every published destination URL.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
