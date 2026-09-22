#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONT="$ROOT/src/frontend"
CHAT="$ROOT/src/monorepos/e2e-chatbot-app-next"
DASH="$ROOT/src/monorepos/aibi-dashboards-external-embedding"

need_dir() {
  if [[ ! -d "$1" ]]; then
    echo "pasta ausente: $1" >&2
    exit 1
  fi
}

need_dir "$FRONT"
need_dir "$CHAT"
need_dir "$DASH"

if [[ ! -d "$FRONT/node_modules" ]]; then
  (cd "$FRONT" && npm install)
fi
if [[ ! -d "$CHAT/node_modules" ]]; then
  (cd "$CHAT" && npm install)
fi
if [[ ! -d "$DASH/frontend/node_modules" ]]; then
  (cd "$DASH/frontend" && npm install)
fi
if ! python -c "import flask" >/dev/null 2>&1 && ! python3 -c "import flask" >/dev/null 2>&1; then
  PY=python3
  command -v python3 >/dev/null || PY=python
  (cd "$DASH/backend" && "$PY" -m pip install -r requirements.txt)
fi

PY=python3
command -v python3 >/dev/null || PY=python

echo "3020 institucional  http://localhost:3020/"
echo "3030 chats          http://localhost:3030/  (via /sdk/chatbot)"
echo "3010 paineis        http://localhost:3010/  (via /sdk/dashboards)"
echo "Ctrl+C para parar."

"$PY" "$DASH/backend/app.py" &
(cd "$DASH/frontend" && npm run dev) &
(
  cd "$CHAT"
  export CHAT_APP_PORT=3031
  export PORT=3030
  export BACKEND_URL=http://localhost:3031
  npm run dev
) &
(cd "$FRONT" && npx next dev -p 3020) &

trap 'kill 0' EXIT INT TERM
wait
