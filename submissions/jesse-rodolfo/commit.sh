#!/usr/bin/env bash
# Commit seguro da submissão.
# Força a adição (o .gitignore da raiz do G4 ignora submissions/), mas exclui dados brutos, venv e caches.
# Uso, de qualquer pasta:  bash commit.sh "mensagem do commit"
set -e
if [ -z "$1" ]; then echo "Uso: bash commit.sh \"mensagem do commit\""; exit 1; fi
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
git add -f submissions/jesse-rodolfo \
  ':!submissions/jesse-rodolfo/solution/data/raw' \
  ':!submissions/jesse-rodolfo/.venv' \
  ':!submissions/jesse-rodolfo/solution/prototipo/modelo.joblib' \
  ':(exclude,glob)submissions/jesse-rodolfo/**/__pycache__/**' \
  ':(exclude,glob)submissions/jesse-rodolfo/**/.pytest_cache/**' \
  ':(exclude,glob)submissions/jesse-rodolfo/**/*.pyc' \
  ':(exclude,glob)submissions/jesse-rodolfo/**/.ipynb_checkpoints/**'
echo "=== arquivos no commit ==="
git diff --cached --stat
if git diff --cached --name-only | grep -qi '\.csv$'; then
  echo "ERRO: ha CSV no commit. Verifique antes de continuar."; exit 1
fi
# --diff-filter=d ignora remocoes, para permitir tirar do indice cache ja rastreado
if git diff --cached --name-only --diff-filter=d | grep -Eq '\.pyc$|(^|/)__pycache__/|(^|/)\.pytest_cache/'; then
  echo "ERRO: ha .pyc ou .pytest_cache no commit. Verifique antes de continuar."; exit 1
fi
if git diff --cached --name-only | grep -v '^submissions/jesse-rodolfo/' | grep -q .; then
  echo "ERRO: ha arquivo fora de submissions/jesse-rodolfo no commit."; exit 1
fi
git commit -m "$1"
echo "=== pronto. para enviar: git push ==="
