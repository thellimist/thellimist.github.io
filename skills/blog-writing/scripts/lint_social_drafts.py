#!/usr/bin/env python3

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

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

TITLE_STOPWORDS: Set[str] = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "me",
    "my",
    "of",
    "on",
    "or",
    "so",
    "that",
    "the",
    "this",
    "to",
    "was",
    "we",
    "with",
    "you",
    "your",
}


@dataclass
class Issue:
    level: str
    file: Path
    message: str


@dataclass
class SourcePost:
    path: Path
    title: str
    image: str
    body: str
    markdown_table_count: int
    html_table_count: int
    custom_block_count: int
    code_fence_count: int


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def post_slug_from_dir_name(name: str) -> str:
    parts = name.split("-", 3)
    if len(parts) == 4:
        return parts[3]
    return name


def parse_social_date(name: str) -> Optional[str]:
    if len(name) < 10:
        return None
    candidate = name[:10]
    if re.match(r"^\d{4}-\d{2}-\d{2}$", candidate):
        return candidate
    return None


def should_enforce_for_dir(social_dir_name: str, cutoff_date: Optional[str]) -> bool:
    if not cutoff_date:
        return True
    social_date = parse_social_date(social_dir_name)
    # Unknown format: enforce checks.
    if not social_date:
        return True
    return social_date > cutoff_date


def split_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return {}, text
    lines = stripped.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break
    if end_index is None:
        return {}, text

    frontmatter: Dict[str, str] = {}
    for line in lines[1:end_index]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip().lower()] = value.strip().strip('"').strip("'")
    body = "\n".join(lines[end_index + 1 :])
    return frontmatter, body


def count_markdown_tables(body: str) -> int:
    lines = body.splitlines()
    count = 0
    separator_pattern = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$")
    for i in range(1, len(lines)):
        prev = lines[i - 1].strip()
        cur = lines[i].strip()
        if "|" not in prev or "|" not in cur:
            continue
        if separator_pattern.match(cur):
            count += 1
    return count


def extract_title_tokens(title: str) -> Set[str]:
    tokens = {
        token
        for token in re.findall(r"[a-z0-9]+", title.lower())
        if len(token) >= 4 and token not in TITLE_STOPWORDS
    }
    return tokens


def find_source_post(posts_root: Path, social_dir_name: str) -> Optional[Path]:
    for ext in (".md", ".markdown"):
        candidate = posts_root / f"{social_dir_name}{ext}"
        if candidate.exists():
            return candidate
    return None


def load_source_post(social_dir: Path, posts_root: Path, issues: List[Issue]) -> Optional[SourcePost]:
    source_path = find_source_post(posts_root, social_dir.name)
    if source_path is None:
        add_issue(issues, "warning", social_dir, f"Could not find source post in {posts_root} for social dir")
        return None

    text = read_text(source_path)
    frontmatter, body = split_frontmatter(text)
    title = frontmatter.get("title", "").strip()
    image = frontmatter.get("image", "").strip()
    if not title:
        add_issue(issues, "warning", source_path, "Missing title in source frontmatter")
    if not image:
        add_issue(issues, "warning", source_path, "Missing image in source frontmatter")
    else:
        image_rel = image.lstrip("/")
        image_path = source_path.parents[1] / image_rel if source_path.parents else Path(image_rel)
        if not image_path.exists():
            add_issue(issues, "warning", source_path, f"Source frontmatter image path does not exist: {image}")

    markdown_table_count = count_markdown_tables(body)
    html_table_count = len(re.findall(r"<table\b", body, flags=re.IGNORECASE))
    custom_block_count = len(re.findall(r"<div\b[^>]*class=", body, flags=re.IGNORECASE))
    code_fence_count = len(re.findall(r"^```", body, flags=re.MULTILINE))

    return SourcePost(
        path=source_path,
        title=title,
        image=image,
        body=body,
        markdown_table_count=markdown_table_count,
        html_table_count=html_table_count,
        custom_block_count=custom_block_count,
        code_fence_count=code_fence_count,
    )


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


def check_x(
    path: Path,
    text: str,
    issues: List[Issue],
    social_dir: Path,
    assets_root: Path,
    social_dir_name: str,
    source_post: Optional[SourcePost],
) -> None:
    stripped = text.lstrip()
    if not stripped.startswith("# "):
        add_issue(issues, "error", path, "x-article.md should start with an H1 line")

    if re.search(r"\[[^\]]+\]\((?:https?://|mailto:)", text):
        add_issue(issues, "error", path, "Markdown link syntax found; use plain URLs in x-article.md")

    placeholders = re.findall(r"\[IMAGE:\s*([^\]]+?)\s*\]", text)
    required_visuals = 0
    if source_post:
        required_visuals = source_post.markdown_table_count + source_post.html_table_count + source_post.custom_block_count
        if source_post.code_fence_count > 0 and "```" not in text:
            add_issue(
                issues,
                "error",
                path,
                "Source post has fenced code blocks; x-article.md must preserve code blocks with ``` fences",
            )

    if not placeholders:
        if required_visuals > 0:
            add_issue(
                issues,
                "error",
                path,
                f"Source post has {required_visuals} tables/custom blocks; add [IMAGE: ...] placeholders for captures",
            )
        else:
            add_issue(issues, "warning", path, "No [IMAGE: ...] placeholders found")
        return

    if required_visuals > len(placeholders):
        add_issue(
            issues,
            "error",
            path,
            f"Only {len(placeholders)} image placeholders found but source has {required_visuals} tables/custom blocks",
        )

    manifest_path = social_dir / "x-image-manifest.json"
    if not manifest_path.exists():
        add_issue(issues, "error", path, "Missing x-image-manifest.json for X placeholder captures")
    else:
        try:
            raw = read_text(manifest_path)
            payload = json.loads(raw)
            items = payload if isinstance(payload, list) else payload.get("items", [])
            if not isinstance(items, list):
                raise ValueError("items is not a list")
            manifest_placeholders = {
                str(item.get("placeholder", "")).strip()
                for item in items
                if isinstance(item, dict) and str(item.get("placeholder", "")).strip()
            }
            missing_in_manifest = [name.strip() for name in placeholders if name.strip() not in manifest_placeholders]
            if missing_in_manifest:
                add_issue(
                    issues,
                    "error",
                    manifest_path,
                    f"Manifest missing placeholders from x-article.md: {', '.join(missing_in_manifest)}",
                )
        except Exception as exc:
            add_issue(issues, "error", manifest_path, f"Invalid x-image-manifest.json: {exc}")

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


def check_linkedin(path: Path, text: str, issues: List[Issue], source_post: Optional[SourcePost]) -> None:
    count = len(text.strip())
    if count < 500 or count > 1300:
        add_issue(issues, "warning", path, f"Length is {count} chars; target band is 600-1200")

    if re.search(r"\[[^\]]+\]\((?:https?://|mailto:)", text):
        add_issue(issues, "error", path, "Markdown links found in linkedin.md")

    if re.search(r"https?://|www\.", text):
        add_issue(issues, "error", path, "External link found in linkedin.md body; keep URL for first comment")

    markdown_markers = [r"^#+\s", r"^\|", r"^>\s", r"^\s*[-*]\s"]
    for marker in markdown_markers:
        if re.search(marker, text, flags=re.MULTILINE):
            add_issue(issues, "warning", path, "Possible markdown formatting found in linkedin.md")
            break

    non_empty_lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(non_empty_lines) < 2:
        add_issue(issues, "error", path, "LinkedIn draft should have at least 2 non-empty hook lines")
    else:
        if len(non_empty_lines[0]) > 120:
            add_issue(issues, "warning", path, "First hook line is long; keep line 1 short and punchy")

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if len(paragraphs) < 4:
        add_issue(issues, "warning", path, "LinkedIn draft is dense; use at least 4 short paragraphs")
    for paragraph in paragraphs:
        if len(paragraph) > 380:
            add_issue(issues, "warning", path, "LinkedIn paragraph too long; split into shorter chunks")
            break

    if source_post and source_post.title and len(non_empty_lines) >= 2:
        title_tokens = extract_title_tokens(source_post.title)
        if title_tokens:
            hook_tokens = extract_title_tokens(" ".join(non_empty_lines[:2]))
            overlap = title_tokens.intersection(hook_tokens)
            if len(overlap) < 2:
                add_issue(
                    issues,
                    "error",
                    path,
                    "LinkedIn first 2 lines should preserve the blog title claim (low title token overlap)",
                )


def check_reddit(path: Path, text: str, issues: List[Issue]) -> None:
    if "## Target Subreddits" not in text:
        add_issue(issues, "error", path, "Missing '## Target Subreddits' section")

    target_lines = re.findall(r"^\s*-\s+r/[A-Za-z0-9_]+.*$", text, flags=re.MULTILINE)
    if len(target_lines) < 3 or len(target_lines) > 4:
        add_issue(issues, "error", path, f"Expected 3-4 selected target subreddits, found {len(target_lines)}")
    for line in target_lines:
        if not re.search(r"rules checked\s+\d{4}-\d{2}-\d{2}", line, flags=re.IGNORECASE):
            add_issue(issues, "error", path, f"Target line missing rules check date: {line.strip()}")
        if "link placement:" not in line.lower():
            add_issue(issues, "error", path, f"Target line missing link placement note: {line.strip()}")

    candidate_count_match = re.search(r"candidates reviewed:\s*(\d+)", text, flags=re.IGNORECASE)
    if not candidate_count_match:
        add_issue(issues, "error", path, "Missing 'Candidates reviewed: N' line in reddit.md")
    else:
        candidate_count = int(candidate_count_match.group(1))
        if candidate_count < 25:
            add_issue(issues, "error", path, f"Candidates reviewed is {candidate_count}; must be at least 25")

    post_sections = re.findall(r"^##\s+Post\s+for\s+r/[A-Za-z0-9_]+", text, flags=re.MULTILINE)
    if not post_sections:
        add_issue(issues, "error", path, "Missing per-subreddit post sections: '## Post for r/...' ")
    if target_lines and post_sections and len(post_sections) != len(target_lines):
        add_issue(
            issues,
            "error",
            path,
            f"Target subreddit count ({len(target_lines)}) does not match post section count ({len(post_sections)})",
        )

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
    source_post: Optional[SourcePost],
) -> None:
    comment_kit = social_dir / "comment-kit.md"
    if not comment_kit.exists():
        if files["x"].exists() or files["linkedin"].exists() or files["reddit"].exists():
            add_issue(issues, "error", social_dir, "Missing comment-kit.md")
        return

    text = read_text(comment_kit)
    x_notes = section_body(text, "X publish notes")
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
    if files["x"].exists() and not x_notes:
        add_issue(issues, "error", comment_kit, "Missing '## X publish notes' section")
    if files["linkedin"].exists() and not li_section:
        add_issue(issues, "error", comment_kit, "Missing '## LinkedIn first comment' section")

    if files["x"].exists() and source_post and source_post.image and x_notes and source_post.image not in x_notes:
        add_issue(
            issues,
            "error",
            comment_kit,
            f"X publish notes should include source cover image path from frontmatter: {source_post.image}",
        )

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


def run_checks(social_dir: Path, assets_root: Path, posts_root: Path, blog_url: Optional[str]) -> List[Issue]:
    issues: List[Issue] = []
    source_post = load_source_post(social_dir=social_dir, posts_root=posts_root, issues=issues)
    files: Dict[str, Path] = {
        "x": social_dir / "x-article.md",
        "linkedin": social_dir / "linkedin.md",
        "reddit": social_dir / "reddit.md",
        "hn": social_dir / "hn.md",
    }

    for key, path in files.items():
        if not path.exists():
            continue
        text = read_text(path)
        check_common(path, text, issues)

        if key == "x":
            check_x(path, text, issues, social_dir, assets_root, social_dir.name, source_post)
        elif key == "linkedin":
            check_linkedin(path, text, issues, source_post)
        elif key == "reddit":
            check_reddit(path, text, issues)
        elif key == "hn":
            check_hn(path, text, issues)

    check_comment_kit(
        social_dir=social_dir,
        files=files,
        issues=issues,
        blog_url=blog_url,
        source_post=source_post,
    )

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
    parser.add_argument("--posts-root", default="_posts", help="Posts root containing source blog posts")
    parser.add_argument("--blog-url", help="Canonical blog URL for link-placement checks")
    parser.add_argument("--cutoff-date", help="Only enforce for social dirs dated after this (YYYY-MM-DD)")
    parser.add_argument("--strict-warnings", action="store_true", help="Fail on warnings as well as errors")
    args = parser.parse_args()

    social_dir = Path(args.social_dir)
    assets_root = Path(args.assets_root)
    posts_root = Path(args.posts_root)

    if not social_dir.exists() or not social_dir.is_dir():
        print(f"Error: social dir does not exist: {social_dir}", file=sys.stderr)
        return 1

    if args.cutoff_date and not re.match(r"^\d{4}-\d{2}-\d{2}$", args.cutoff_date):
        print(f"Error: --cutoff-date must be YYYY-MM-DD, got: {args.cutoff_date}", file=sys.stderr)
        return 1

    if not should_enforce_for_dir(social_dir.name, args.cutoff_date):
        print(f"Skipped lint for {social_dir} (<= cutoff {args.cutoff_date})")
        return 0

    issues = run_checks(social_dir=social_dir, assets_root=assets_root, posts_root=posts_root, blog_url=args.blog_url)
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
