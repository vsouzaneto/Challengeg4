#!/usr/bin/env bash
# Stageia arquivos da submissão apesar do `submissions/` no .gitignore da raiz.
# Uso (de qualquer pasta dentro do repo):  bash submissions/ricardo-dias/scripts/git-add.sh <caminhos...>
# Aplica submissions/ricardo-dias/.gitignore para não incluir node_modules, .env, CSVs etc.
set -euo pipefail
root="$(cd "$(git rev-parse --show-toplevel)" && pwd)"
sub="submissions/ricardo-dias"
[ "$#" -gt 0 ] || { echo "informe caminhos (nunca a pasta toda sem revisar)"; exit 1; }
rel=()
for p in "$@"; do
  abs="$(cd "$(dirname "$p")" && pwd)/$(basename "$p")"
  r="$(realpath --relative-to="$root" "$abs")"
  case "$r" in "$sub"*) rel+=("$r") ;; *) echo "recusado (fora de $sub): $r"; exit 1 ;; esac
done
cd "$root"
# arquivos novos (não rastreados), filtrados pelo .gitignore da submissão
git ls-files -z --others --exclude-from="$sub/.gitignore" -- "${rel[@]}" | xargs -0 -r git add -f --
# arquivos já rastreados (modificados/removidos)
git add -u -- "${rel[@]}"
git status --short -- "${rel[@]}"
