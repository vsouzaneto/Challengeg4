#!/usr/bin/env bash
# Stage the submission folder safely and fast.
# The repo root ignores `submissions/`, so plain `git add` adds nothing and `git add -f` bypasses
# EVERY .gitignore (including ours) — it would drag node_modules/.venv into the PR.
# Strategy: list untracked files with explicit excludes, then force-add only that list; refresh tracked files with -u.
set -euo pipefail
repo="$(cd "$(dirname "$0")/../../.." && pwd)"
rel="submissions/bernardo-couto"
cd "$repo"
if git ls-files --error-unmatch -- "$rel" >/dev/null 2>&1; then git add -u -- "$rel"; fi
git ls-files -o -z \
  --exclude='node_modules' --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='dist' --exclude='site' --exclude='.pytest_cache' --exclude='.ruff_cache' --exclude='.mypy_cache' \
  --exclude='.DS_Store' --exclude='spark-warehouse' --exclude='metastore_db' --exclude='derby.log' \
  --exclude='bronze' --exclude='silver' --exclude='**/data/feedback' --exclude='pipeline_model' \
  --exclude='.env' --exclude='.env.*' --exclude='CLAUDE.local.md' --exclude='settings.local.json' --exclude='.private' \
  --exclude='*.tsbuildinfo' --exclude='*.local' --exclude='kaggle.json' --exclude='credentials.json' \
  --exclude='coverage' --exclude='playwright-report' --exclude='test-results' \
  -- "$rel" | git add -f --pathspec-from-file=- --pathspec-file-nul
# gold: keep only the committed snapshot partition
git diff --cached --name-only -z -- "$rel/solution/data/gold" | tr '\0' '\n' | grep -v 'scores/as_of=2017-12-31/' | grep -v '\.gitkeep$' | tr '\n' '\0' | xargs -0 -r git reset -q -- || true
total=$(git diff --cached --name-only | wc -l | tr -d ' ')
bad=$(git diff --cached --name-only | grep -cE 'node_modules/|/\.venv/|__pycache__|/site/|/dist/|\.private/|/\.env|kaggle\.json|credentials\.json|\.tsbuildinfo$' || true)
outside=$(git diff --cached --name-only | grep -vc "^$rel/" || true)
echo "staged: $total · generated: $bad · outside submission folder: $outside"
if [ "$bad" != "0" ] || [ "$outside" != "0" ]; then echo "ERRO: stage inválido"; exit 1; fi
