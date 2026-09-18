#!/usr/bin/env bash
# O .gitignore da raiz do repositório oficial ignora `submissions/`, e ele não pode ser alterado.
# `git add -f` puro forçaria também data/, .venv/ e .intel/. Este script força só o que o
# .gitignore desta pasta permite e depois mostra o que foi para o stage.
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
SUB="submissions/douglas-franca"
cd "$ROOT"

git ls-files --others -X "$SUB/.gitignore" -- "$SUB" | while IFS= read -r f; do
  git add -f -- "$f"
done
git add -u -- "$SUB"

echo "--- staged:"
git diff --cached --name-status
if git diff --cached --name-only | grep -vq "^$SUB/"; then
  echo "ERRO: há arquivos fora de $SUB no stage" >&2
  exit 1
fi
if git diff --cached --name-only | grep -Eq "^$SUB/(data|\.venv|\.intel)/"; then
  echo "ERRO: dado bruto, venv ou .intel no stage" >&2
  exit 1
fi
