#!/usr/bin/env python3

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


METRIC_KEYS = [
    "likes",
    "comments",
    "reposts",
    "bookmarks",
    "views",
    "shares",
    "clicks",
    "upvotes",
    "downvotes",
    "score",
]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def metric_dict(item: dict) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for key in METRIC_KEYS:
        value = item.get(key)
        if value is None:
            continue
        try:
            out[key] = int(value)
        except (TypeError, ValueError):
            continue
    return out


def compact_metrics(metrics: Dict[str, int]) -> str:
    if not metrics:
        return "-"
    return ", ".join(f"{k} {v}" for k, v in metrics.items())


def compact_diff(current: Dict[str, int], previous: Dict[str, int]) -> str:
    deltas: List[str] = []
    for key in METRIC_KEYS:
        if key not in current:
            continue
        delta = current[key] - previous.get(key, 0)
        if delta == 0:
            continue
        sign = "+" if delta > 0 else ""
        deltas.append(f"{key} {sign}{delta}")
    return ", ".join(deltas) if deltas else "no change"


def render_report(tracker: dict, current_snapshot: dict, previous_snapshot: dict, update_index: int, total_updates: int) -> str:
    posts_by_id = {str(post.get("post_id", "")).strip(): post for post in tracker.get("posts", [])}
    cur_items = {str(item.get("post_id", "")).strip(): item for item in current_snapshot.get("items", [])}
    prev_items = {}
    if previous_snapshot:
        prev_items = {str(item.get("post_id", "")).strip(): item for item in previous_snapshot.get("items", [])}

    lines = []
    lines.append(f"# Results Update {update_index}/{total_updates}")
    lines.append("")
    lines.append(f"Timestamp: {current_snapshot.get('timestamp', '')}")
    lines.append("")
    lines.append("| Post | Source | Metrics | Diff from last update |")
    lines.append("|---|---|---|---|")

    for post_id, post in posts_by_id.items():
        source = str(post.get("source", "")).strip() or str(post.get("platform", "")).strip() or "-"
        label = str(post.get("label", "")).strip() or post_id
        current_metrics = metric_dict(cur_items.get(post_id, {}))
        previous_metrics = metric_dict(prev_items.get(post_id, {}))
        lines.append(
            f"| {label} | {source} | {compact_metrics(current_metrics)} | {compact_diff(current_metrics, previous_metrics)} |"
        )

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Record one results snapshot and generate a diff report.")
    parser.add_argument("--social-dir", required=True, help="Path like social/YYYY-MM-DD-slug")
    parser.add_argument("--snapshot", required=True, help="Snapshot JSON file path")
    args = parser.parse_args()

    social_dir = Path(args.social_dir)
    tracker_path = social_dir / "results-tracking.json"
    updates_dir = social_dir / "results-updates"
    updates_dir.mkdir(parents=True, exist_ok=True)

    if not tracker_path.exists():
        raise SystemExit(f"Missing tracker file: {tracker_path}")

    tracker = read_json(tracker_path)
    snapshot = read_json(Path(args.snapshot))
    if "timestamp" not in snapshot or not snapshot.get("timestamp"):
        snapshot["timestamp"] = datetime.now().astimezone().isoformat(timespec="seconds")

    snapshots = tracker.setdefault("snapshots", [])
    previous_snapshot = snapshots[-1] if snapshots else {}
    snapshots.append(snapshot)
    write_json(tracker_path, tracker)

    plan = tracker.get("review_plan", {})
    total_updates = int(plan.get("updates_per_day", 3)) * int(plan.get("days", 3))
    update_index = len(snapshots)
    report = render_report(
        tracker=tracker,
        current_snapshot=snapshot,
        previous_snapshot=previous_snapshot,
        update_index=update_index,
        total_updates=total_updates,
    )

    safe_ts = snapshot["timestamp"].replace(":", "").replace("+", "_plus_").replace("-", "_")
    report_path = updates_dir / f"{safe_ts}.md"
    report_path.write_text(report, encoding="utf-8")
    (social_dir / "results-latest.md").write_text(report, encoding="utf-8")

    print(f"Recorded snapshot #{update_index}/{total_updates}")
    print(f"Wrote report: {report_path}")
    print(f"Wrote latest: {social_dir / 'results-latest.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
