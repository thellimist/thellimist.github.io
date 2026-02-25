#!/usr/bin/env bash
set -u

ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT_DIR" || exit 0
CUTOFF_DATE="${SOCIAL_LINT_CUTOFF_DATE:-2026-02-20}"

is_enforced_social_dir() {
  local dir="$1"
  local leaf="${dir#social/}"
  local date="${leaf:0:10}"
  # If format is unexpected, fail-safe by enforcing checks.
  if [[ ! "$date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    return 0
  fi
  [[ "$date" > "$CUTOFF_DATE" ]]
}

INPUT=$(cat 2>/dev/null || true)
[ -z "$INPUT" ] && exit 0

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // ""' 2>/dev/null)
case "$TOOL_NAME" in
  Write|Edit|MultiEdit)
    ;;
  *)
    exit 0
    ;;
esac

PATHS=$(echo "$INPUT" | jq -r '
  [
    .tool_input.file_path?,
    .tool_input.path?,
    .tool_input.target_file?,
    (.tool_input.files[]? // empty),
    (.tool_input.file_paths[]? // empty)
  ]
  | .[]
  | select(type=="string" and length>0)
' 2>/dev/null)

[ -z "$PATHS" ] && exit 0

declare -A SOCIAL_DIRS=()

normalize_rel_path() {
  local p="$1"
  p="${p#./}"
  if [[ "$p" == "$ROOT_DIR"/* ]]; then
    p="${p#"$ROOT_DIR"/}"
  fi
  printf '%s' "$p"
}

while IFS= read -r raw_path; do
  [ -z "$raw_path" ] && continue
  rel=$(normalize_rel_path "$raw_path")

  case "$rel" in
    social/*/*)
      social_dir=$(printf '%s' "$rel" | cut -d/ -f1-2)
      if is_enforced_social_dir "$social_dir"; then
        SOCIAL_DIRS["$social_dir"]=1
      fi
      ;;
    social/*)
      social_dir=$(printf '%s' "$rel" | cut -d/ -f1-2)
      if is_enforced_social_dir "$social_dir"; then
        SOCIAL_DIRS["$social_dir"]=1
      fi
      ;;
    *)
      ;;
  esac
done <<< "$PATHS"

if [ "${#SOCIAL_DIRS[@]}" -eq 0 ]; then
  exit 0
fi

FAIL=0
for dir in "${!SOCIAL_DIRS[@]}"; do
  if [ ! -d "$dir" ]; then
    continue
  fi

  if ! python3 skills/blog-writing/scripts/lint_social_drafts.py --social-dir "$dir"; then
    FAIL=1
  fi
done

if [ "$FAIL" -ne 0 ]; then
  echo "Hook blocked: social draft lint failed. Fix issues above, then continue." >&2
  exit 2
fi

exit 0
