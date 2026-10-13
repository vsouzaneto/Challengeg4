#!/usr/bin/env bash
# Stage this submission despite the upstream rule that ignores submissions/.
# Force-adds new and changed files under this folder, skipping anything matched by ./.gitignore,
# then refuses to continue if a staged path falls outside the folder, is over 2 MB or looks like a secret.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
root="$(git -C "$here" rev-parse --show-toplevel)"
# Ask git for the folder's repo-relative path: on Windows, pwd (/d/...) and git (D:/...) spell paths differently.
rel="$(git -C "$here" rev-parse --show-prefix)"
rel="${rel%/}"
cd "$root"

mapfile -t files < <(git ls-files --others --modified --exclude-from="$rel/.gitignore" -- "$rel")
if ((${#files[@]})); then
  git add -f -- "${files[@]}"
fi

outside=$(git diff --cached --name-only | grep -v "^$rel/" || true)
if [[ -n "$outside" ]]; then
  echo "Refusing: staged files outside $rel/ (G4 rejects PRs that touch other files):" >&2
  echo "$outside" >&2
  exit 1
fi

big=""
while IFS= read -r f; do
  size=$(git cat-file -s ":$f" 2>/dev/null || echo 0)
  limit=2000000
  [[ "$f" == *.pdf ]] && limit=5000000 # documents may be larger; models and data may not
  if ((size > limit)); then big+="$f ($size bytes)"$'\n'; fi
done < <(git diff --cached --name-only --diff-filter=AM)
if [[ -n "$big" ]]; then
  echo "Refusing: staged files over 2 MB (models and data stay out of git):" >&2
  printf '%s' "$big" >&2
  exit 1
fi

# Key prefixes must start a token: "zendesk-ai-pricing" contains "sk-" but is not a key.
secrets=$(git diff --cached -U0 | grep -nE '(^|[^A-Za-z0-9])(sk-[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{35}|KGAT_[0-9A-Za-z]{16,}|gh[opsu]_[A-Za-z0-9]{30,})|"key"\s*:\s*"[0-9a-f]{32}"' || true)
if [[ -n "$secrets" ]]; then
  echo "Refusing: something that looks like an API key is staged:" >&2
  echo "$secrets" >&2
  exit 1
fi

git diff --cached --stat
