#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
HOOKS_DIR="$ROOT_DIR/.git/hooks"
TARGET="$HOOKS_DIR/pre-push"

if [ ! -d "$ROOT_DIR/.git" ]; then
  echo "Not a git repository: $ROOT_DIR" >&2
  exit 1
fi

mkdir -p "$HOOKS_DIR"

cat > "$TARGET" <<'HOOK'
#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SCRIPT="$ROOT_DIR/.claude/hooks/pre-push-social-lint.sh"
if [ -x "$SCRIPT" ]; then
  exec "$SCRIPT" "$@"
fi
exit 0
HOOK

chmod +x "$TARGET"
echo "Installed pre-push hook: $TARGET"
