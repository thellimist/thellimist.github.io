#!/usr/bin/env bash
set -u

SCRIPT_NAME="${1:-}"
shift || true

[ -z "$SCRIPT_NAME" ] && exit 0

ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
HOOK_DIR="$ROOT_DIR/.claude/hooks"
TARGET="$HOOK_DIR/$SCRIPT_NAME"

if [ ! -f "$TARGET" ]; then
  exit 0
fi

# Claude Code passes hook payload on stdin.
INPUT=$(cat 2>/dev/null || true)

if [ -n "$INPUT" ]; then
  printf '%s' "$INPUT" | bash "$TARGET" "$@"
else
  bash "$TARGET" "$@"
fi
RC=$?

# exit 2 is intentional block; propagate it.
if [ "$RC" -eq 2 ]; then
  exit 2
fi

# Any other hook failure should not break the session.
if [ "$RC" -ne 0 ]; then
  LOG="$ROOT_DIR/.claude/.hook-errors.log"
  TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date +"%s")
  echo "[$TS] $SCRIPT_NAME exit=$RC" >> "$LOG" 2>/dev/null || true
  exit 0
fi

exit 0
