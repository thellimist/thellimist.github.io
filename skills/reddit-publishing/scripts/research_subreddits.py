#!/usr/bin/env python3

import argparse
import json
import math
import os
import re
import statistics
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class Candidate:
    name: str
    matched_queries: List[str]


@dataclass
class RequestConfig:
    timeout_seconds: int
    retries: int
    backoff_seconds: float
    prefer_old_reddit: bool
    max_rate_limit_errors: int


def default_subreddit_notes_file() -> str:
    return str(Path(__file__).resolve().parents[1] / "references" / "subreddit-notes.json")


def load_subreddit_notes(notes_file: str) -> Dict[str, Dict]:
    if not notes_file:
        return {}
    path = Path(os.path.expanduser(notes_file))
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

    if isinstance(payload, dict):
        entries = payload.get("subreddits", [])
    elif isinstance(payload, list):
        entries = payload
    else:
        return {}

    if not isinstance(entries, list):
        return {}

    notes: Dict[str, Dict] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        raw_name = str(entry.get("name") or entry.get("subreddit") or "").strip().lower()
        if not raw_name:
            continue
        name = raw_name[2:] if raw_name.startswith("r/") else raw_name
        notes[name] = entry
    return notes


def add_candidate(discovered: Dict[str, Candidate], name: str, marker: str) -> None:
    key = name.strip().lower()
    if not key:
        return
    if key not in discovered:
        discovered[key] = Candidate(name=name.strip(), matched_queries=[marker])
        return
    if marker not in discovered[key].matched_queries:
        discovered[key].matched_queries.append(marker)


def parse_frontmatter_title(post_path: str) -> str:
    with open(post_path, "r", encoding="utf-8") as handle:
        text = handle.read()
    match = re.search(r"^title:\s*(.+)$", text, flags=re.MULTILINE)
    if not match:
        return ""
    raw = match.group(1).strip()
    return raw.strip('"').strip("'")


def infer_queries_from_post(post_path: str) -> List[str]:
    title = parse_frontmatter_title(post_path)
    filename = post_path.rsplit("/", 1)[-1]
    stem = re.sub(r"\.(md|markdown)$", "", filename)
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)

    inferred: List[str] = []
    seen = set()

    def add_query(value: str) -> None:
        q = value.strip()
        if not q:
            return
        key = q.lower()
        if key in seen:
            return
        seen.add(key)
        inferred.append(q)

    for acronym in re.findall(r"\b[A-Z][A-Z0-9]{1,9}\b", title):
        add_query(acronym)
    for token in re.split(r"[^a-z0-9]+", slug.lower()):
        if len(token) >= 3:
            add_query(token)

    return inferred


def exact_seed_names_from_queries(queries: List[str]) -> List[str]:
    seeds: List[str] = []
    seen = set()
    short_technical = {
        "mcp",
        "llm",
        "gpt",
        "api",
        "sdk",
        "cli",
        "ga4",
        "gsc",
        "seo",
        "devops",
        "saas",
    }

    def add_seed(value: str) -> None:
        v = value.strip().lower()
        if len(v) < 2 or len(v) > 24:
            return
        if v.isdigit():
            return
        if v in seen:
            return
        seen.add(v)
        seeds.append(v)

    for query in queries:
        for token in re.findall(r"\b[A-Z][A-Z0-9]{1,9}\b", query):
            add_seed(token)

        split_tokens = [tok for tok in re.split(r"[^a-z0-9_]+", query.lower()) if tok]
        if len(split_tokens) == 1 and len(split_tokens[0]) >= 3:
            add_seed(split_tokens[0])
        for token in split_tokens:
            if token in short_technical:
                add_seed(token)

    return seeds


def now_ts() -> int:
    return int(time.time())


def cache_template() -> Dict:
    return {"version": 1, "updated_at": now_ts(), "queries": {}, "subreddits": {}}


def load_cache(cache_file: str) -> Dict:
    path = Path(os.path.expanduser(cache_file))
    if not path.exists():
        return cache_template()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return cache_template()
    if not isinstance(payload, dict):
        return cache_template()
    payload.setdefault("queries", {})
    payload.setdefault("subreddits", {})
    payload.setdefault("version", 1)
    payload.setdefault("updated_at", now_ts())
    return payload


def save_cache(cache_file: str, cache_payload: Dict) -> None:
    path = Path(os.path.expanduser(cache_file))
    path.parent.mkdir(parents=True, exist_ok=True)
    cache_payload["updated_at"] = now_ts()
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(cache_payload, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def is_fresh(entry: Dict, ttl_seconds: int) -> bool:
    fetched_at = entry.get("fetched_at")
    if not isinstance(fetched_at, (int, float)):
        return False
    return (time.time() - float(fetched_at)) <= ttl_seconds


def query_cache_key(query: str, limit: int) -> str:
    return f"{query.strip().lower()}|{limit}"


def get_cached_query_names(cache_payload: Dict, query: str, limit: int, ttl_seconds: int) -> List[str]:
    entry = cache_payload.get("queries", {}).get(query_cache_key(query, limit))
    if not isinstance(entry, dict):
        return []
    if not is_fresh(entry, ttl_seconds):
        return []
    names = entry.get("names")
    if not isinstance(names, list):
        return []
    return [str(name) for name in names if str(name).strip()]


def set_cached_query_names(cache_payload: Dict, query: str, limit: int, names: List[str]) -> None:
    cache_payload.setdefault("queries", {})[query_cache_key(query, limit)] = {
        "fetched_at": now_ts(),
        "names": names,
    }


def subreddit_cache_key(name: str) -> str:
    return name.strip().lower()


def get_cached_subreddit_bundle(
    cache_payload: Dict,
    name: str,
    sample_posts: int,
    ttl_seconds: int,
) -> Tuple[Dict, List[Dict], List[Dict]]:
    entry = cache_payload.get("subreddits", {}).get(subreddit_cache_key(name))
    if not isinstance(entry, dict):
        return {}, [], []
    if not is_fresh(entry, ttl_seconds):
        return {}, [], []
    about = entry.get("about")
    rules = entry.get("rules")
    posts = entry.get("posts")
    if not isinstance(about, dict) or not isinstance(rules, list) or not isinstance(posts, list):
        return {}, [], []
    if len(posts) < sample_posts:
        return {}, [], []
    return about, rules, posts[:sample_posts]


def set_cached_subreddit_bundle(cache_payload: Dict, name: str, about: Dict, rules: List[Dict], posts: List[Dict]) -> None:
    cache_payload.setdefault("subreddits", {})[subreddit_cache_key(name)] = {
        "fetched_at": now_ts(),
        "about": about,
        "rules": rules,
        "posts": posts,
    }


def fetch_json(url: str, user_agent: str, config: RequestConfig) -> Dict:
    last_error = None
    urls = [url]
    if "www.reddit.com" in url:
        old_url = url.replace("www.reddit.com", "old.reddit.com")
        urls = [old_url, url] if config.prefer_old_reddit else [url, old_url]

    for candidate_url in urls:
        for attempt in range(max(config.retries, 1)):
            try:
                result = subprocess.run(
                    [
                        "curl",
                        "-sS",
                        "-fL",
                        "--http1.1",
                        "--max-time",
                        str(config.timeout_seconds),
                        "-A",
                        user_agent,
                        "-H",
                        "Accept: application/json",
                        candidate_url,
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=max(config.timeout_seconds + 2, 4),
                )
                return json.loads(result.stdout)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc

            try:
                req = urllib.request.Request(
                    candidate_url,
                    headers={
                        "User-Agent": user_agent,
                        "Accept": "application/json",
                    },
                )
                with urllib.request.urlopen(req, timeout=config.timeout_seconds) as response:
                    body = response.read().decode("utf-8", errors="replace")
                return json.loads(body)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
            if attempt < max(config.retries, 1) - 1:
                wait_seconds = config.backoff_seconds * (attempt + 1)
                time.sleep(wait_seconds)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def is_rate_limited_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "429" in text or "too many requests" in text


def search_subreddits(
    query: str,
    limit: int,
    user_agent: str,
    config: RequestConfig,
    cache_payload: Dict,
    cache_ttl_seconds: int,
) -> Tuple[List[str], bool]:
    cached_names = get_cached_query_names(cache_payload, query, limit, cache_ttl_seconds)
    if cached_names:
        return cached_names, True

    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.reddit.com/subreddits/search.json?q={encoded}&limit={limit}&include_over_18=off"
    data = fetch_json(url, user_agent, config)
    names = []
    for child in data.get("data", {}).get("children", []):
        info = child.get("data", {})
        name = info.get("display_name")
        if name:
            names.append(name)
    set_cached_query_names(cache_payload, query, limit, names)
    return names, False


def fetch_about(name: str, user_agent: str, config: RequestConfig) -> Dict:
    url = f"https://www.reddit.com/r/{name}/about.json"
    data = fetch_json(url, user_agent, config)
    return data.get("data", {})


def fetch_rules(name: str, user_agent: str, config: RequestConfig) -> List[Dict]:
    url = f"https://www.reddit.com/r/{name}/about/rules.json"
    data = fetch_json(url, user_agent, config)
    return data.get("rules", [])


def fetch_new_posts(name: str, user_agent: str, limit: int, config: RequestConfig) -> List[Dict]:
    url = f"https://www.reddit.com/r/{name}/new.json?limit={limit}"
    data = fetch_json(url, user_agent, config)
    posts = []
    for child in data.get("data", {}).get("children", []):
        posts.append(child.get("data", {}))
    return posts


def combine_rules_text(rules: List[Dict], description: str, public_description: str) -> str:
    parts = [description or "", public_description or ""]
    for rule in rules:
        parts.append(rule.get("short_name", ""))
        parts.append(rule.get("description", ""))
        parts.append(rule.get("violation_reason", ""))
    return "\n".join(parts)


def make_snippet(text: str, index: int, span: int = 220) -> str:
    if index < 0 or not text.strip():
        return "No explicit evidence found."
    start = max(0, index - 70)
    end = min(len(text), index + span)
    snippet = text[start:end]
    return re.sub(r"\s+", " ", snippet).strip()


def find_first_index(text: str, patterns: List[str]) -> int:
    for pattern in patterns:
        idx = text.find(pattern)
        if idx >= 0:
            return idx
    return -1


def classify_self_promo(text: str) -> Tuple[str, str, float]:
    t = text.lower()
    allow_patterns = [
        "self promotion is allowed",
        "self-promotion is allowed",
        "self promo allowed",
    ]
    limited_patterns = [
        "self promotion is limited",
        "self-promotion is limited",
        "limit self promotion",
        "10%",
        "9:1",
        "1:10",
        "once per",
        "weekly self-promotion",
    ]
    ban_patterns = [
        "no self promotion",
        "no self-promotion",
        "no self promo",
        "self promotion is not allowed",
        "self-promotion is not allowed",
        "no promotion",
        "no advertising",
        "no blogspam",
        "do not promote",
    ]

    idx_allow = find_first_index(t, allow_patterns)
    if idx_allow >= 0:
        return "allow", make_snippet(text, idx_allow), 0.88

    idx_ban = find_first_index(t, ban_patterns)
    if idx_ban >= 0:
        return "ban", make_snippet(text, idx_ban), 0.94

    idx_limited = find_first_index(t, limited_patterns)
    if idx_limited >= 0:
        return "limited", make_snippet(text, idx_limited), 0.84

    mention = re.search(r"self[- ]?(promo|promotion)", t)
    if mention:
        return "limited", make_snippet(text, mention.start()), 0.66

    return "unknown", "No explicit self-promotion phrase detected in fetched rules/description.", 0.34


def classify_ai_policy(text: str) -> Tuple[str, str, float]:
    t = text.lower()
    ai_mentions = ["ai-generated", "ai generated", "chatgpt", "llm", "machine-generated"]
    mention_idx = find_first_index(t, ai_mentions)
    if mention_idx < 0:
        return "unknown", "No explicit AI-content rule phrase detected.", 0.34

    ban_patterns = ["no ai", "ban ai", "ai content is not allowed", "no chatgpt"]
    restricted_patterns = ["disclose ai", "label ai", "ai content must"]
    idx_ban = find_first_index(t, ban_patterns)
    if idx_ban >= 0:
        return "ban", make_snippet(text, idx_ban), 0.90

    idx_restricted = find_first_index(t, restricted_patterns)
    if idx_restricted >= 0:
        return "restricted", make_snippet(text, idx_restricted), 0.80

    return "mentioned", make_snippet(text, mention_idx), 0.64


def classify_post_type(text: str) -> Tuple[str, str, float]:
    t = text.lower()
    text_only_patterns = ["text posts only", "no link posts", "links are not allowed", "link posts are not allowed"]
    link_only_patterns = ["link posts only", "must post a link"]
    idx_text = find_first_index(t, text_only_patterns)
    if idx_text >= 0:
        return "text_only", make_snippet(text, idx_text), 0.90

    idx_link = find_first_index(t, link_only_patterns)
    if idx_link >= 0:
        return "link_only", make_snippet(text, idx_link), 0.88

    return "either_or_unknown", "No explicit link-vs-text requirement phrase detected.", 0.36


def extract_requirements(text: str) -> List[str]:
    requirements = []
    lowered = text.lower()

    if "account age" in lowered or "days old" in lowered or "new accounts" in lowered:
        requirements.append("Account age requirement")
    if "karma" in lowered:
        requirements.append("Karma requirement")
    if "flair" in lowered:
        requirements.append("Flair requirement")
    if "title" in lowered and ("must" in lowered or "format" in lowered):
        requirements.append("Title format requirement")

    bracket_pattern = re.search(r"\[[A-Za-z]{1,3}\]", text)
    if bracket_pattern:
        requirements.append(f"Possible title prefix {bracket_pattern.group(0)}")

    deduped = []
    seen = set()
    for item in requirements:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def compute_post_metrics(posts: List[Dict]) -> Tuple[float, float, float, float]:
    if not posts:
        return 0.0, 0.0, 0.0, float("inf")

    now = time.time()
    created = [post.get("created_utc", now) for post in posts if post.get("created_utc")]
    comments = [post.get("num_comments", 0) for post in posts]
    scores = [post.get("score", 0) for post in posts]

    if len(created) < 2:
        span_days = 1.0
    else:
        span_days = max((max(created) - min(created)) / 86400.0, 1.0)

    posts_per_day = len(posts) / span_days
    median_comments = float(statistics.median(comments)) if comments else 0.0
    median_score = float(statistics.median(scores)) if scores else 0.0

    newest = max(created) if created else now
    hours_since_last_post = (now - newest) / 3600.0
    return posts_per_day, median_comments, median_score, hours_since_last_post


def compute_relevance(name: str, about: Dict, queries: List[str]) -> float:
    haystack = " ".join(
        [
            name.lower(),
            (about.get("title") or "").lower(),
            (about.get("public_description") or "").lower(),
            (about.get("description") or "").lower(),
        ]
    )

    score = 0.0
    for query in queries:
        tokens = [token for token in re.split(r"[^a-z0-9]+", query.lower()) if len(token) > 2]
        token_hits = sum(1 for token in tokens if token in haystack)
        if token_hits > 0:
            score += min(8.0, 2.0 + token_hits * 1.5)
    return min(score, 30.0)


def compute_risk(self_promo: str, ai_policy: str, post_type: str, requirements: List[str], posts_per_day: float) -> float:
    risk = 0.0

    if self_promo == "ban":
        risk += 100
    elif self_promo == "limited":
        risk += 35
    elif self_promo == "unknown":
        risk += 15

    if ai_policy == "ban":
        risk += 30
    elif ai_policy == "restricted":
        risk += 15

    if post_type == "text_only":
        risk += 8

    if requirements:
        risk += min(20, len(requirements) * 5)

    if posts_per_day < 0.5:
        risk += 20

    return min(risk, 120)


def recommendation_from_risk(risk: float, self_promo: str, posts_per_day: float, median_comments: float) -> str:
    if self_promo == "ban":
        return "avoid"
    if risk >= 75:
        return "avoid"
    if posts_per_day < 0.5 or median_comments < 1.5:
        return "maybe"
    if risk >= 35:
        return "maybe"
    return "target"


def fmt(value: float) -> str:
    if math.isinf(value):
        return "inf"
    return f"{value:.1f}"


def rank_value(rec: str) -> int:
    return {"target": 0, "maybe": 1, "avoid": 2}.get(rec, 9)


def print_table(results: List[Dict]) -> None:
    header = (
        "Recommendation | Subreddit | Subs | Posts/day | Median comments | Self promo | Post type | Risk | Rule conf | Manual note"
    )
    print(header)
    print("-" * len(header))
    for row in results:
        print(
            f"{row['recommendation']:>13} | r/{row['name']:<20} | {row['subscribers']:>8} | "
            f"{fmt(row['posts_per_day']):>9} | {fmt(row['median_comments']):>15} | {row['self_promo']:<10} | "
            f"{row['post_type']:<15} | {fmt(row['risk']):>4} | {row['rule_confidence']:.2f} | {row['manual_note_stance']:<11}"
        )


def to_markdown(results: List[Dict], queries: List[str]) -> str:
    lines = []
    lines.append("# Reddit Subreddit Research")
    lines.append("")
    lines.append(f"Queries: {', '.join(queries)}")
    lines.append("")
    lines.append("| Recommendation | Subreddit | Subscribers | Posts/day | Median comments | Self-promo policy | AI policy | Post type | Requirements | Manual notes |")
    lines.append("|---|---|---:|---:|---:|---|---|---|---|---|")
    for row in results:
        requirements = "; ".join(row["requirements"]) if row["requirements"] else "-"
        manual_note = row["manual_note_stance"] if row["manual_note_stance"] != "-" else "-"
        lines.append(
            f"| {row['recommendation']} | r/{row['name']} | {row['subscribers']} | {fmt(row['posts_per_day'])} | "
            f"{fmt(row['median_comments'])} | {row['self_promo']} | {row['ai_policy']} | {row['post_type']} | {requirements} | {manual_note} |"
        )

    lines.append("")
    lines.append("## Rule Notes")
    lines.append("")
    for row in results:
        lines.append(f"### r/{row['name']} ({row['recommendation']})")
        lines.append(f"- Rule risk score: {fmt(row['risk'])}")
        lines.append(f"- Rule confidence: {row['rule_confidence']:.2f}")
        lines.append(f"- Self-promo: {row['self_promo']} (confidence {row['self_promo_confidence']:.2f})")
        lines.append(f"  Evidence: {row['self_promo_evidence']}")
        lines.append(f"- AI policy: {row['ai_policy']} (confidence {row['ai_policy_confidence']:.2f})")
        lines.append(f"  Evidence: {row['ai_policy_evidence']}")
        lines.append(f"- Post type: {row['post_type']} (confidence {row['post_type_confidence']:.2f})")
        lines.append(f"  Evidence: {row['post_type_evidence']}")
        if row["manual_note_stance"] != "-":
            lines.append(f"- Manual note: {row['manual_note_stance']} (risk +{fmt(row['manual_note_penalty'])})")
            lines.append(f"  Context: {row['manual_note']}")
            if row["manual_note_override"] != "-":
                lines.append(f"  Recommendation override: {row['manual_note_override']}")
        else:
            lines.append("- Manual note: -")
        lines.append(f"- Rule excerpt: {row['rule_excerpt']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Find and rank candidate subreddits, then audit posting rules.")
    parser.add_argument("--queries", nargs="+", required=True, help="Search queries (space-separated).")
    parser.add_argument("--source-post", help="Optional source post path (_posts/YYYY-MM-DD-slug.md) to infer extra queries.")
    parser.add_argument(
        "--no-infer-from-source",
        action="store_true",
        help="Do not append inferred queries/acronyms from --source-post (fewer network calls).",
    )
    parser.add_argument("--limit-per-query", type=int, default=14, help="Search result count per query.")
    parser.add_argument("--max-candidates", type=int, default=28, help="Max subreddits to analyze in detail.")
    parser.add_argument("--require-analyzed", type=int, default=25, help="Fail if fewer than this many subreddits are analyzed.")
    parser.add_argument("--sample-posts", type=int, default=20, help="Recent posts to sample for activity metrics.")
    parser.add_argument("--sleep-ms", type=int, default=350, help="Delay between subreddit API calls.")
    parser.add_argument("--min-subscribers", type=int, default=1000, help="Skip tiny subreddits below this count.")
    parser.add_argument("--min-exact-subscribers", type=int, default=200, help="Lower subscriber floor for exact-match seeded subreddits.")
    parser.add_argument("--request-timeout", type=int, default=8, help="Per-request timeout in seconds.")
    parser.add_argument("--request-retries", type=int, default=1, help="Retry count per URL before skipping.")
    parser.add_argument("--request-backoff-ms", type=int, default=500, help="Linear retry backoff in milliseconds.")
    parser.add_argument(
        "--prefer-old-reddit",
        action="store_true",
        default=True,
        help="Try old.reddit.com before www.reddit.com to avoid slow anonymous API stalls.",
    )
    parser.add_argument(
        "--no-prefer-old-reddit",
        dest="prefer_old_reddit",
        action="store_false",
        help="Try www.reddit.com first.",
    )
    parser.add_argument(
        "--max-rate-limit-errors",
        type=int,
        default=8,
        help="Abort early after this many 429 responses to avoid long stalled runs.",
    )
    parser.add_argument(
        "--cache-file",
        default="~/.cache/reddit-publishing/subreddit-research-cache.json",
        help="Cache file for query + subreddit rule snapshots.",
    )
    parser.add_argument(
        "--cache-ttl-hours",
        type=int,
        default=2160,
        help="Reuse cached subreddit/query data newer than this many hours.",
    )
    parser.add_argument("--max-runtime-seconds", type=int, default=420, help="Soft cap for total runtime.")
    parser.add_argument(
        "--max-consecutive-failures",
        type=int,
        default=10,
        help="Abort candidate loop if this many subreddits fail in a row.",
    )
    parser.add_argument("--user-agent", default="kanyilmaz-blog-research/1.0", help="User-Agent header for Reddit requests.")
    parser.add_argument(
        "--subreddit-notes",
        default=default_subreddit_notes_file(),
        help="Optional JSON file with manual subreddit sentiment/risk notes.",
    )
    parser.add_argument("--json-out", help="Optional JSON output path.")
    parser.add_argument("--md-out", help="Optional markdown report path.")
    args = parser.parse_args()

    request_config = RequestConfig(
        timeout_seconds=max(args.request_timeout, 2),
        retries=max(args.request_retries, 1),
        backoff_seconds=max(args.request_backoff_ms, 0) / 1000.0,
        prefer_old_reddit=args.prefer_old_reddit,
        max_rate_limit_errors=max(args.max_rate_limit_errors, 1),
    )
    start_time = time.time()
    rate_limit_errors = 0
    cache_ttl_seconds = max(args.cache_ttl_hours, 1) * 3600
    cache_payload = load_cache(args.cache_file)
    manual_notes = load_subreddit_notes(args.subreddit_notes)
    query_cache_hits = 0
    subreddit_cache_hits = 0

    queries = [query.strip() for query in args.queries if query.strip()]
    if args.source_post and not args.no_infer_from_source:
        inferred = infer_queries_from_post(args.source_post)
        query_keys = {q.lower() for q in queries}
        for query in inferred:
            key = query.lower()
            if key not in query_keys:
                queries.append(query)
                query_keys.add(key)

    if not queries:
        raise RuntimeError("At least one non-empty query is required")

    discovered: Dict[str, Candidate] = {}

    for query_index, query in enumerate(queries, start=1):
        print(f"[query {query_index}/{len(queries)}] searching '{query}'", file=sys.stderr, flush=True)
        try:
            names, from_cache = search_subreddits(
                query,
                args.limit_per_query,
                args.user_agent,
                request_config,
                cache_payload,
                cache_ttl_seconds,
            )
            if from_cache:
                query_cache_hits += 1
        except Exception as exc:
            print(f"Warning: search failed for query '{query}': {exc}", file=sys.stderr)
            if is_rate_limited_error(exc):
                rate_limit_errors += 1
                if rate_limit_errors >= request_config.max_rate_limit_errors:
                    raise RuntimeError(
                        "Reddit is globally rate-limiting this environment (multiple 429 responses). "
                        "Retry later, use OAuth credentials, or run from a different IP."
                    )
            continue
        for name in names:
            add_candidate(discovered, name, query)

    exact_seeds = exact_seed_names_from_queries(queries)
    for seed in exact_seeds:
        marker = f"exact:{seed}"
        add_candidate(discovered, seed, marker)

        try:
            about = fetch_about(seed, args.user_agent, request_config)
        except Exception:
            # Seed lookups are optional; ignore failures.
            continue
        display_name = about.get("display_name") or seed
        add_candidate(discovered, str(display_name), marker)

    if not discovered:
        raise RuntimeError("No subreddit candidates found")

    # Higher priority to subreddits matched by multiple query angles.
    ordered = sorted(discovered.values(), key=lambda item: (-len(item.matched_queries), item.name.lower()))
    selected = ordered[: args.max_candidates]

    results: List[Dict] = []
    consecutive_failures = 0

    for index, candidate in enumerate(selected):
        elapsed = time.time() - start_time
        if elapsed > args.max_runtime_seconds:
            print(
                f"Warning: stopping early at {index}/{len(selected)} candidates after {elapsed:.1f}s runtime cap.",
                file=sys.stderr,
            )
            break

        print(
            f"[candidate {index + 1}/{len(selected)}] r/{candidate.name}",
            file=sys.stderr,
            flush=True,
        )
        try:
            about, rules, posts = get_cached_subreddit_bundle(
                cache_payload,
                candidate.name,
                args.sample_posts,
                cache_ttl_seconds,
            )
            if about and rules and posts:
                subreddit_cache_hits += 1
            else:
                about = fetch_about(candidate.name, args.user_agent, request_config)
                subscribers = int(about.get("subscribers") or 0)
                has_exact_seed = any(marker.startswith("exact:") for marker in candidate.matched_queries)
                if subscribers < args.min_subscribers:
                    if not has_exact_seed or subscribers < args.min_exact_subscribers:
                        consecutive_failures = 0
                        continue
                rules = fetch_rules(candidate.name, args.user_agent, request_config)
                posts = fetch_new_posts(candidate.name, args.user_agent, args.sample_posts, request_config)
                set_cached_subreddit_bundle(cache_payload, candidate.name, about, rules, posts)

            subscribers = int(about.get("subscribers") or 0)
            has_exact_seed = any(marker.startswith("exact:") for marker in candidate.matched_queries)
            if subscribers < args.min_subscribers:
                if not has_exact_seed or subscribers < args.min_exact_subscribers:
                    consecutive_failures = 0
                    continue

            resolved_name = str(about.get("display_name") or candidate.name).strip().lower()
            manual_note_entry = manual_notes.get(candidate.name.strip().lower()) or manual_notes.get(resolved_name)
            manual_note_stance = "-"
            manual_note = "-"
            manual_note_penalty = 0.0
            manual_note_override = "-"
            if isinstance(manual_note_entry, dict):
                manual_note_stance = str(manual_note_entry.get("stance") or "-").strip() or "-"
                manual_note = str(manual_note_entry.get("note") or "-").strip() or "-"
                try:
                    manual_note_penalty = max(0.0, float(manual_note_entry.get("risk_penalty", 0)))
                except (TypeError, ValueError):
                    manual_note_penalty = 0.0
                override_value = str(manual_note_entry.get("recommendation_override") or "").strip().lower()
                if override_value in {"target", "maybe", "avoid"}:
                    manual_note_override = override_value

            rule_text = combine_rules_text(rules, about.get("description", ""), about.get("public_description", ""))
            rule_excerpt = re.sub(r"\s+", " ", rule_text).strip()[:240]

            self_promo, self_promo_evidence, self_promo_confidence = classify_self_promo(rule_text)
            ai_policy, ai_policy_evidence, ai_policy_confidence = classify_ai_policy(rule_text)
            post_type, post_type_evidence, post_type_confidence = classify_post_type(rule_text)
            requirements = extract_requirements(rule_text)
            posts_per_day, median_comments, median_score, hours_since_last_post = compute_post_metrics(posts)

            relevance = compute_relevance(candidate.name, about, candidate.matched_queries)
            size_score = min(20.0, math.log10(max(1, subscribers)) * 3.2)
            activity_score = min(25.0, posts_per_day * 5.0 + median_comments * 1.1)
            engagement_score = min(15.0, median_score / 20.0 + median_comments)

            base_risk = compute_risk(self_promo, ai_policy, post_type, requirements, posts_per_day)
            risk = min(120.0, base_risk + manual_note_penalty)
            quality = relevance + size_score + activity_score + engagement_score - (risk * 0.4)
            recommendation = recommendation_from_risk(risk, self_promo, posts_per_day, median_comments)
            if manual_note_override != "-":
                recommendation = manual_note_override
            rule_confidence = round((self_promo_confidence + ai_policy_confidence + post_type_confidence) / 3.0, 2)

            results.append(
                {
                    "name": candidate.name,
                    "matched_queries": candidate.matched_queries,
                    "subscribers": subscribers,
                    "active_users": int(about.get("active_user_count") or 0),
                    "posts_per_day": round(posts_per_day, 2),
                    "median_comments": round(median_comments, 2),
                    "median_score": round(median_score, 2),
                    "hours_since_last_post": round(hours_since_last_post, 1),
                    "self_promo": self_promo,
                    "self_promo_evidence": self_promo_evidence,
                    "self_promo_confidence": round(self_promo_confidence, 2),
                    "ai_policy": ai_policy,
                    "ai_policy_evidence": ai_policy_evidence,
                    "ai_policy_confidence": round(ai_policy_confidence, 2),
                    "post_type": post_type,
                    "post_type_evidence": post_type_evidence,
                    "post_type_confidence": round(post_type_confidence, 2),
                    "requirements": requirements,
                    "risk": round(risk, 1),
                    "base_risk": round(base_risk, 1),
                    "rule_confidence": rule_confidence,
                    "quality": round(quality, 2),
                    "recommendation": recommendation,
                    "rule_excerpt": rule_excerpt if rule_excerpt else "No explicit rule text fetched.",
                    "manual_note_stance": manual_note_stance,
                    "manual_note": manual_note,
                    "manual_note_penalty": round(manual_note_penalty, 1),
                    "manual_note_override": manual_note_override,
                }
            )
            consecutive_failures = 0
        except Exception as exc:
            print(f"Warning: skipping r/{candidate.name} due to fetch/parse error: {exc}", file=sys.stderr)
            if is_rate_limited_error(exc):
                rate_limit_errors += 1
                if rate_limit_errors >= request_config.max_rate_limit_errors:
                    raise RuntimeError(
                        "Reddit is globally rate-limiting this environment (multiple 429 responses). "
                        "Retry later, use OAuth credentials, or run from a different IP."
                    )
            consecutive_failures += 1
            if consecutive_failures >= args.max_consecutive_failures:
                print(
                    f"Warning: aborting after {consecutive_failures} consecutive candidate failures.",
                    file=sys.stderr,
                )
                break
            continue

        # Respect Reddit rate limits for unauthenticated API access.
        if index < len(selected) - 1:
            time.sleep(max(args.sleep_ms, 0) / 1000.0)

    if not results:
        save_cache(args.cache_file, cache_payload)
        raise RuntimeError("All candidates were filtered out. Lower --min-subscribers or increase queries.")

    if len(results) < args.require_analyzed:
        save_cache(args.cache_file, cache_payload)
        raise RuntimeError(
            f"Only analyzed {len(results)} subreddits; require at least {args.require_analyzed}. "
            "Increase --max-candidates or lower --min-subscribers."
        )

    results.sort(key=lambda row: (rank_value(row["recommendation"]), -row["quality"], -row["subscribers"]))

    if exact_seeds:
        print(f"Exact subreddit seeds: {', '.join(exact_seeds)}")
    print(f"Manual subreddit notes loaded: {len(manual_notes)}")
    print(f"Query cache hits: {query_cache_hits}/{len(queries)}")
    print(f"Subreddit cache hits: {subreddit_cache_hits}/{len(selected)}")
    print(f"Analyzed subreddits: {len(results)}")
    print_table(results)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as handle:
            json.dump(results, handle, indent=2)
            handle.write("\n")

    if args.md_out:
        with open(args.md_out, "w", encoding="utf-8") as handle:
            handle.write(to_markdown(results, queries))
            handle.write("\n")

    save_cache(args.cache_file, cache_payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
