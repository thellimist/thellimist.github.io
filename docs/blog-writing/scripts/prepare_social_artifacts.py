#!/usr/bin/env python3

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


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


def find_source_post(posts_root: Path, social_dir_name: str) -> Path:
    for ext in (".md", ".markdown"):
        candidate = posts_root / f"{social_dir_name}{ext}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No source post found for {social_dir_name} in {posts_root}")


def ensure_section(lines: List[str], title: str, body_lines: List[str]) -> List[str]:
    pattern = re.compile(rf"^##\s+{re.escape(title)}\s*$")
    start = None
    end = None
    for i, line in enumerate(lines):
        if pattern.match(line.strip()):
            start = i
            break
    if start is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(f"## {title}")
        lines.extend(body_lines)
        lines.append("")
        return lines

    for i in range(start + 1, len(lines)):
        if lines[i].startswith("## "):
            end = i
            break
    if end is None:
        end = len(lines)

    replacement = [f"## {title}", *body_lines, ""]
    return lines[:start] + replacement + lines[end:]


def ensure_comment_kit(comment_kit_path: Path, post_title: str, header_image: str, blog_url: str) -> None:
    if comment_kit_path.exists():
        lines = comment_kit_path.read_text(encoding="utf-8").splitlines()
    else:
        lines = ["# Comment Kit", ""]

    lines = ensure_section(lines, "X publish notes", [f"Cover image: {header_image}"])
    lines = ensure_section(lines, "X first comment", [f"Full blog post: {blog_url}"])
    lines = ensure_section(lines, "LinkedIn first comment", [f"Full blog post with detailed breakdown: {blog_url}"])
    lines = ensure_section(
        lines,
        "Vibecoding WhatsApp",
        [
            f"Just published: {post_title}",
            "Main takeaway: [add one-sentence takeaway]",
            f"Link: {blog_url}",
        ],
    )
    lines = ensure_section(
        lines,
        "Bookface post",
        [
            f"New post: {post_title}",
            "Short take: [add 1-2 sentence summary in your style]",
            f"Read: {blog_url}",
        ],
    )
    comment_kit_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def ensure_x_article(path: Path, title: str) -> None:
    if path.exists():
        return
    content = f"# {title}\n\nWrite X long-form article content here.\n"
    path.write_text(content, encoding="utf-8")


def ensure_x_manifest(path: Path) -> None:
    if path.exists():
        return
    payload = {"items": []}
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def ensure_linkedin(path: Path, title: str) -> None:
    if path.exists():
        return
    content = (
        f"{title}\n\n"
        "Add LinkedIn hook + compressed summary here.\n"
    )
    path.write_text(content, encoding="utf-8")


def ensure_reddit(path: Path) -> None:
    if path.exists():
        return
    content = (
        "# Reddit Draft\n\n"
        "## Target Subreddits\n"
        "Candidates reviewed: 30\n"
        "Selection criteria: relevance + activity + comments + self-promo policy + post type fit + rule confidence\n"
        "- r/SubredditA - GO (text), rules checked YYYY-MM-DD, flair required: Discussion, link placement: first_comment\n"
        "- r/SubredditB - GO (link), rules checked YYYY-MM-DD, no flair needed, link placement: body_end\n"
        "- r/SubredditC - GO (text), rules checked YYYY-MM-DD, flair required: Discussion, link placement: first_comment\n\n"
        "## Post for r/SubredditA\n"
        "**Type:** text post\n"
        "**Title:** \n"
        "**Body:**\n\n\n"
        "## Post for r/SubredditB\n"
        "**Type:** link post\n"
        "**Title:** \n"
        "**URL:** \n\n"
        "## Post for r/SubredditC\n"
        "**Type:** text post\n"
        "**Title:** \n"
        "**Body:**\n"
    )
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare required social artifacts (comment-kit, drafts, x manifest) before platform publishing."
    )
    parser.add_argument("--social-dir", required=True, help="Path like social/YYYY-MM-DD-slug")
    parser.add_argument("--platform", required=True, choices=["x", "linkedin", "reddit", "hn"])
    parser.add_argument("--blog-url", default="https://YOUR_BLOG_URL")
    parser.add_argument("--posts-root", default="_posts")
    args = parser.parse_args()

    social_dir = Path(args.social_dir)
    social_dir.mkdir(parents=True, exist_ok=True)
    posts_root = Path(args.posts_root)

    source_post = find_source_post(posts_root=posts_root, social_dir_name=social_dir.name)
    text = source_post.read_text(encoding="utf-8")
    frontmatter, _body = split_frontmatter(text)
    title = frontmatter.get("title", "Untitled Post").strip()
    header_image = frontmatter.get("image", "/assets/posts/your-header-image.png").strip()
    if not header_image:
        header_image = "/assets/posts/your-header-image.png"

    comment_kit = social_dir / "comment-kit.md"
    ensure_comment_kit(
        comment_kit_path=comment_kit,
        post_title=title,
        header_image=header_image,
        blog_url=args.blog_url,
    )

    if args.platform == "x":
        ensure_x_article(social_dir / "x-article.md", title)
        ensure_x_manifest(social_dir / "x-image-manifest.json")
    elif args.platform == "linkedin":
        ensure_linkedin(social_dir / "linkedin.md", title)
    elif args.platform == "reddit":
        ensure_reddit(social_dir / "reddit.md")

    print(f"Prepared artifacts for platform '{args.platform}' in {social_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
