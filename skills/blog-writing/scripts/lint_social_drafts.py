#!/usr/bin/env python3

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

BANNED_PHRASES = [
    "delve",
    "unpack",
    "navigate",
    "leverage",
    "foster",
    "harness",
    "elevate",
    "revolutionize",
    "unleash",
    "embark",
    "underscores",
    "moreover",
    "furthermore",
    "it is worth noting",
    "in today's fast-paced world",
    "at the end of the day",
]


@dataclass
class Issue:
    level: str
    file: Path
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def post_slug_from_dir_name(name: str) -> str:
    parts = name.split("-", 3)
    if len(parts) == 4:
        return parts[3]
    return name


def add_issue(issues: List[Issue], level: str, file: Path, message: str) -> None:
    issues.append(Issue(level=level, file=file, message=message))


def check_common(path: Path, text: str, issues: List[Issue]) -> None:
    lower = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lower:
            add_issue(issues, "warning", path, f"Contains banned/weak phrase: '{phrase}'")

    repeated_word = re.search(r"\b([A-Za-z]{2,})\s+\1\b", text, flags=re.IGNORECASE)
    if repeated_word:
        add_issue(issues, "warning", path, f"Possible repeated word: '{repeated_word.group(0)}'")

    if "  " in text:
        add_issue(issues, "warning", path, "Contains double spaces")

    for sentence in re.split(r"(?<=[.!?])\s+", text):
        words = re.findall(r"\b\w+\b", sentence)
        if len(words) > 45:
            excerpt = " ".join(words[:12])
            add_issue(issues, "warning", path, f"Very long sentence ({len(words)} words): {excerpt}...")
            break


def candidate_asset_dirs(assets_root: Path, social_dir_name: str) -> List[Path]:
    slug = post_slug_from_dir_name(social_dir_name)
    return [
        assets_root / slug / "x-article",
        assets_root / social_dir_name / "x-article",
    ]


def check_x(path: Path, text: str, issues: List[Issue], assets_root: Path, social_dir_name: str) -> None:
    stripped = text.lstrip()
    if not stripped.startswith("# "):
        add_issue(issues, "error", path, "x-article.md should start with an H1 line")

    if re.search(r"\[[^\]]+\]\((?:https?://|mailto:)", text):
        add_issue(issues, "error", path, "Markdown link syntax found; use plain URLs in x-article.md")

    placeholders = re.findall(r"\[IMAGE:\s*([^\]]+?)\s*\]", text)
    if not placeholders:
        add_issue(issues, "warning", path, "No [IMAGE: ...] placeholders found")
        return

    search_dirs = candidate_asset_dirs(assets_root, social_dir_name)
    missing = []
    for name in placeholders:
        name = name.strip()
        found = any((directory / name).exists() for directory in search_dirs)
        if not found:
            missing.append(name)

    if missing:
        dirs = ", ".join(str(directory) for directory in search_dirs)
        add_issue(issues, "error", path, f"Missing image files for placeholders: {', '.join(missing)} (searched: {dirs})")


def check_linkedin(path: Path, text: str, issues: List[Issue]) -> None:
    count = len(text.strip())
    if count < 1100 or count > 1700:
        add_issue(issues, "warning", path, f"Length is {count} chars; target band is 1300-1500")

    if re.search(r"\[[^\]]+\]\((?:https?://|mailto:)", text):
        add_issue(issues, "error", path, "Markdown links found in linkedin.md")

    if re.search(r"https?://|www\.", text):
        add_issue(issues, "error", path, "External link found in linkedin.md body; keep URL for first comment")

    markdown_markers = [r"^#+\s", r"^\|", r"^>\s", r"^\s*[-*]\s"]
    for marker in markdown_markers:
        if re.search(marker, text, flags=re.MULTILINE):
            add_issue(issues, "warning", path, "Possible markdown formatting found in linkedin.md")
            break


def check_reddit(path: Path, text: str, issues: List[Issue]) -> None:
    if "## Target Subreddits" not in text:
        add_issue(issues, "error", path, "Missing '## Target Subreddits' section")

    post_sections = re.findall(r"^##\s+Post\s+for\s+r/[A-Za-z0-9_]+", text, flags=re.MULTILINE)
    if not post_sections:
        add_issue(issues, "error", path, "Missing per-subreddit post sections: '## Post for r/...' ")

    if "rules checked" not in text.lower():
        add_issue(issues, "warning", path, "No explicit 'rules checked' notes found for target subreddits")


def check_hn(path: Path, text: str, issues: List[Issue]) -> None:
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped) > 80:
            add_issue(issues, "warning", path, f"HN title candidate over 80 chars: {stripped[:80]}...")


def section_body(text: str, title: str) -> str:
    pattern = rf"^##\s+{re.escape(title)}\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    next_section = re.search(r"^##\s+.+$", text[start:], flags=re.MULTILINE)
    end = start + next_section.start() if next_section else len(text)
    return text[start:end].strip()


def check_comment_kit(
    social_dir: Path,
    files: Dict[str, Path],
    issues: List[Issue],
    blog_url: Optional[str],
) -> None:
    comment_kit = social_dir / "comment-kit.md"
    if not comment_kit.exists():
        if files["x"].exists() or files["linkedin"].exists() or files["reddit"].exists():
            add_issue(issues, "warning", social_dir, "Missing comment-kit.md")
        return

    text = read_text(comment_kit)
    x_section = section_body(text, "X first comment")
    li_section = section_body(text, "LinkedIn first comment")
    reddit_match = re.search(r"^##\s+Reddit first comment.*$", text, flags=re.MULTILINE)
    reddit_section = ""
    if reddit_match:
        start = reddit_match.end()
        next_section = re.search(r"^##\s+.+$", text[start:], flags=re.MULTILINE)
        end = start + next_section.start() if next_section else len(text)
        reddit_section = text[start:end].strip()

    if files["x"].exists() and not x_section:
        add_issue(issues, "error", comment_kit, "Missing '## X first comment' section")
    if files["linkedin"].exists() and not li_section:
        add_issue(issues, "error", comment_kit, "Missing '## LinkedIn first comment' section")

    reddit_text = read_text(files["reddit"]) if files["reddit"].exists() else ""
    reddit_needs_comment = "first_comment" in reddit_text
    if reddit_needs_comment and not reddit_section:
        add_issue(issues, "error", comment_kit, "Missing '## Reddit first comment' section while reddit.md uses first_comment")

    if blog_url:
        if files["x"].exists():
            x_body = read_text(files["x"])
            if blog_url in x_body:
                add_issue(issues, "error", files["x"], "Blog URL appears in X article body; keep it in first comment")
            if x_section and blog_url not in x_section:
                add_issue(issues, "error", comment_kit, "X first comment section does not include --blog-url")

        if files["linkedin"].exists():
            li_body = read_text(files["linkedin"])
            if blog_url in li_body:
                add_issue(issues, "error", files["linkedin"], "Blog URL appears in LinkedIn body; keep it in first comment")
            if li_section and blog_url not in li_section:
                add_issue(issues, "error", comment_kit, "LinkedIn first comment section does not include --blog-url")

        if reddit_needs_comment and reddit_section and blog_url not in reddit_section:
            add_issue(issues, "error", comment_kit, "Reddit first comment section does not include --blog-url")


def run_checks(social_dir: Path, assets_root: Path, blog_url: Optional[str]) -> List[Issue]:
    issues: List[Issue] = []
    files: Dict[str, Path] = {
        "x": social_dir / "x-article.md",
        "linkedin": social_dir / "linkedin.md",
        "reddit": social_dir / "reddit.md",
        "hn": social_dir / "hn.md",
    }

    for key in ("x", "linkedin", "reddit"):
        if not files[key].exists():
            add_issue(issues, "warning", social_dir, f"Missing optional draft file: {files[key].name}")

    for key, path in files.items():
        if not path.exists():
            continue
        text = read_text(path)
        check_common(path, text, issues)

        if key == "x":
            check_x(path, text, issues, assets_root, social_dir.name)
        elif key == "linkedin":
            check_linkedin(path, text, issues)
        elif key == "reddit":
            check_reddit(path, text, issues)
        elif key == "hn":
            check_hn(path, text, issues)

    check_comment_kit(social_dir=social_dir, files=files, issues=issues, blog_url=blog_url)

    return issues


def print_issues(issues: List[Issue]) -> None:
    if not issues:
        print("No lint issues found.")
        return

    for issue in issues:
        print(f"[{issue.level}] {issue.file}: {issue.message}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint social drafts against project contract rules.")
    parser.add_argument("--social-dir", required=True, help="Path like social/YYYY-MM-DD-slug")
    parser.add_argument("--assets-root", default="assets/posts", help="Assets root containing post image folders")
    parser.add_argument("--blog-url", help="Canonical blog URL for link-placement checks")
    parser.add_argument("--strict-warnings", action="store_true", help="Fail on warnings as well as errors")
    args = parser.parse_args()

    social_dir = Path(args.social_dir)
    assets_root = Path(args.assets_root)

    if not social_dir.exists() or not social_dir.is_dir():
        print(f"Error: social dir does not exist: {social_dir}", file=sys.stderr)
        return 1

    issues = run_checks(social_dir=social_dir, assets_root=assets_root, blog_url=args.blog_url)
    print_issues(issues)

    errors = [issue for issue in issues if issue.level == "error"]
    warnings = [issue for issue in issues if issue.level == "warning"]

    if errors:
        return 1
    if warnings and args.strict_warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
