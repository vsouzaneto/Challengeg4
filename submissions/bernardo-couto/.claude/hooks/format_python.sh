#!/usr/bin/env bash
# PostToolUse (Edit|Write): auto-format Python files under solution/ with ruff (best effort, never blocks).
set -u
payload="$(cat)"
file="$(printf '%s' "$payload" | python3 -c 'import json,sys; d=json.load(sys.stdin); print((d.get("tool_input") or {}).get("file_path",""))' 2>/dev/null)"
case "$file" in
  *.py) ;;
  *) exit 0 ;;
esac
root="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
case "$file" in
  "$root"/solution/*) ;;
  *) exit 0 ;;
esac
proj=""
for d in pipeline api shared/lead_scorer_contracts docs-site; do
  case "$file" in "$root/solution/$d/"*) proj="$root/solution/$d";; esac
done
if [ -n "$proj" ] && [ -f "$proj/pyproject.toml" ] && command -v uv >/dev/null 2>&1; then
  (cd "$proj" && uv run --quiet ruff format "$file" >/dev/null 2>&1 && uv run --quiet ruff check --fix --quiet "$file" >/dev/null 2>&1) || true
elif command -v uvx >/dev/null 2>&1; then
  (uvx --quiet ruff format "$file" >/dev/null 2>&1 && uvx --quiet ruff check --fix --quiet "$file" >/dev/null 2>&1) || true
fi
exit 0
