#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT_DIR"
CUTOFF_DATE="${SOCIAL_LINT_CUTOFF_DATE:-2026-02-20}"

collect_files_for_ref() {
  local local_sha="$1"
  local remote_sha="$2"
  local zero="0000000000000000000000000000000000000000"

  if [ "$local_sha" = "$zero" ] || [ -z "$local_sha" ]; then
    return 0
  fi

  if [ "$remote_sha" != "$zero" ] && git cat-file -e "$remote_sha^{commit}" 2>/dev/null; then
    git diff --name-only "$remote_sha..$local_sha" 2>/dev/null || true
    return 0
  fi

  local commits
  commits=$(git rev-list "$local_sha" --not --remotes 2>/dev/null || true)
  if [ -n "$commits" ]; then
    git show --pretty='' --name-only $commits 2>/dev/null || true
  else
    git show --pretty='' --name-only "$local_sha" 2>/dev/null || true
  fi
}

declare -A DIRS=()

while read -r local_ref local_sha remote_ref remote_sha; do
  [ -z "${local_ref:-}" ] && continue

  while IFS= read -r file; do
    [ -z "$file" ] && continue
    case "$file" in
      social/*/*)
        d=$(printf '%s' "$file" | cut -d/ -f1-2)
        DIRS["$d"]=1
        ;;
    esac
  done < <(collect_files_for_ref "$local_sha" "$remote_sha")
done

if [ "${#DIRS[@]}" -eq 0 ]; then
  exit 0
fi

echo "Running social lint pre-push checks..."
FAIL=0
for d in "${!DIRS[@]}"; do
  if [ ! -d "$d" ]; then
    continue
  fi
  echo "- $d"
  if ! python3 skills/blog-writing/scripts/lint_social_drafts.py --social-dir "$d" --cutoff-date "$CUTOFF_DATE"; then
    FAIL=1
  fi
done

if [ "$FAIL" -ne 0 ]; then
  echo "Push blocked: social lint failed for one or more social directories." >&2
  exit 1
fi

exit 0
