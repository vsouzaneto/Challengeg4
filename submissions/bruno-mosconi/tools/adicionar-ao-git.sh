#!/bin/sh
# Coloca no índice do git só os arquivos desta submissão, respeitando o .gitignore desta pasta.
#
# Por que existe: o .gitignore da raiz do repositório ignora submissions/. A saída comum seria
# `git add -f submissions/<nome>`, mas o -f ignora TODAS as regras de ignore e levaria
# node_modules/, dist/ e .env junto.
#
# Regra: esta pasta tem um único .gitignore (na raiz da submissão), sem "/" no início ou no meio dos padrões.
# Pode ser rodado de qualquer lugar dentro do repositório.
set -eu

PASTA=$(cd "$(dirname "$0")/.." && pwd -P)
RAIZ=$(cd "$PASTA" && git rev-parse --show-toplevel)
RAIZ=$(cd "$RAIZ" && pwd -P)
SUB=${PASTA#"$RAIZ"/}
case "$SUB" in
  submissions/*) ;;
  *) echo "Este script precisa estar em <repositório>/submissions/<nome>/tools/ (encontrado: $SUB)" >&2; exit 1 ;;
esac
cd "$RAIZ"
[ -f "$SUB/.gitignore" ] || { echo "Faltou $SUB/.gitignore" >&2; exit 1; }

ancorados=$(grep -nE '^/|^[^#].*/.' "$SUB/.gitignore" || true)
if [ -n "$ancorados" ]; then
  echo "Padrões com \"/\" no início ou no meio não funcionam aqui (seriam lidos a partir da raiz do repositório):" >&2
  echo "$ancorados" >&2
  exit 1
fi

extra=$(find "$SUB" -name .gitignore -not -path "$SUB/.gitignore" -not -path "*/node_modules/*" | head -n 5)
if [ -n "$extra" ]; then
  echo "Há outro .gitignore dentro da submissão (junte as regras em $SUB/.gitignore e apague-o):" >&2
  echo "$extra" >&2
  exit 1
fi

# Arquivos já versionados: modificações e remoções.
# (Na primeira vez não há nenhum, e versões novas do git dão erro com "git add -u" sem arquivos.)
if [ -n "$(git ls-files -- "$SUB")" ]; then
  git add -u -- "$SUB"
fi
# Arquivos novos, filtrados só pelo .gitignore da submissão.
novos=$(git ls-files -o --exclude-from="$SUB/.gitignore" -- "$SUB")
if [ -n "$novos" ]; then
  printf '%s\n' "$novos" | git add -f --pathspec-from-file=-
fi

# Trava final: nada proibido pode estar no índice.
proibidos=$(git diff --cached --name-only | grep -E '(^|/)(node_modules|dist|coverage|\.vercel)/|(^|/)\.env($|\.)|settings\.local\.json$|(^|/)\.mcp\.json$' || true)
if [ -n "$proibidos" ]; then
  echo "Arquivos que não podem ir para o repositório foram parar no índice:" >&2
  echo "$proibidos" >&2
  echo "Tire com: git restore --staged <arquivo>" >&2
  exit 1
fi
# Trava do PR: nada fora da pasta.
fora=$(git diff --cached --name-only | grep -v "^$SUB/" || true)
if [ -n "$fora" ]; then
  echo "Há arquivos fora de $SUB no índice (o PR seria rejeitado):" >&2
  echo "$fora" >&2
  exit 1
fi

git diff --cached --name-status
