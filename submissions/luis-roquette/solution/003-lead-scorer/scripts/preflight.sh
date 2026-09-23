#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
UV_VERSION=0.10.10
PYTHON_VERSION=3.11
TMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/lead-scorer-preflight.XXXXXX")
ENV_ROOT="$TMP_ROOT/venv"
CHILD_PID=""
export PIP_NO_CACHE_DIR=1
export PLAYWRIGHT_BROWSERS_PATH="$TMP_ROOT/ms-playwright"
export UV_CACHE_DIR="$TMP_ROOT/uv-cache"
export UV_PYTHON_INSTALL_DIR="$TMP_ROOT/python"

cleanup() {
  status=$?
  if [[ -n "$CHILD_PID" ]] && kill -0 "$CHILD_PID" 2>/dev/null; then
    kill "$CHILD_PID" 2>/dev/null || true
    wait "$CHILD_PID" 2>/dev/null || true
  fi
  rm -rf "$TMP_ROOT"
  exit "$status"
}
trap cleanup EXIT HUP INT TERM

run_gate() {
  local name=$1
  shift
  if [[ "${LEAD_SCORER_PREFLIGHT_FAIL_GATE:-}" == "$name" ]]; then
    printf 'falha injetada no gate %s\n' "$name" >&2
    return 97
  fi
  printf '\n[%s]\n' "$name"
  "$@"
}

if [[ "${LEAD_SCORER_PREFLIGHT_FAILURE_PROBE:-}" == "1" ]]; then
  for gate in dependencies imports tests evaluation startup; do
    run_gate "$gate" true
  done
  printf 'probe inválido: uma falha obrigatória não foi injetada\n' >&2
  exit 98
fi

cd "$ROOT"
if [[ -n "${CODESPACES:-}" ]]; then
  BOOTSTRAP="$TMP_ROOT/bootstrap"
  python3 -m venv "$BOOTSTRAP"
  "$BOOTSTRAP/bin/python" -m pip install --disable-pip-version-check "uv==$UV_VERSION"
  "$BOOTSTRAP/bin/uv" python install "$PYTHON_VERSION"
  "$BOOTSTRAP/bin/uv" venv --seed --python "$PYTHON_VERSION" "$ENV_ROOT"
else
  PYTHON311=$(command -v python3.11 || true)
  [[ -n "$PYTHON311" ]] || { printf 'Python 3.11 não encontrado\n' >&2; exit 66; }
  "$PYTHON311" -m venv "$ENV_ROOT"
fi

PYTHON="$ENV_ROOT/bin/python"
[[ "$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')" == "3.11" ]] || {
  printf 'Ambiente precisa usar Python 3.11\n' >&2
  exit 66
}

run_gate dependencies "$PYTHON" -m pip install --disable-pip-version-check -r requirements.txt
if [[ -n "${CODESPACES:-}" ]]; then
  # O gerenciador executa o preflight como job remoto. O helper `--with-deps`
  # tenta controlar o TTY ao elevar privilegios e suspende esse job; `sudo -n`
  # mantem a instalacao reproduzivel e explicitamente nao interativa.
  run_gate dependencies sudo -n "$PYTHON" -m playwright install-deps chromium
fi
run_gate dependencies "$PYTHON" -m playwright install chromium
run_gate dependencies "$PYTHON" -m pip check
run_gate imports "$PYTHON" -c 'import app, data, scoring, pandas, sklearn, streamlit, playwright'
run_gate tests "$PYTHON" -m unittest discover -s tests -p 'test_*.py' -v

evaluate_real_data() {
  "$PYTHON" - <<'PY'
import json
from pathlib import Path
import data
import scoring

root = Path.cwd()
dataset = data.load_dataset(data.read_snapshot(root / "data/raw", root / "data/manifest.json"))
bundle = scoring.build_scoring_bundle(dataset)
evaluations = bundle.candidate_evaluations
expected = {(candidate, route) for candidate in ("logistic", "boosting") for route in ("full", "fallback")}
actual = {(item.candidate, item.route) for item in evaluations}
if actual != expected or len(evaluations) != 4 or any(item.status not in ("passed", "rejected", "failed") for item in evaluations):
    raise SystemExit("avaliação de quatro rotas incompleta")
if any(item.status == "failed" for item in evaluations):
    raise SystemExit("rota falhou tecnicamente; rejeição estatística seria aceita")
print("REAL_EVALUATION", json.dumps({
    "counts": dataset.counts,
    "fingerprint": bundle.fingerprint,
    "source_identity": scoring.serialize(bundle.source_identity),
    "routes": [{"candidate": item.candidate, "route": item.route, "status": item.status,
                "evaluation_id": item.evaluation_id, "brier": item.brier,
                "baseline_brier": item.baseline_brier, "log_loss": item.log_loss,
                "baseline_log_loss": item.baseline_log_loss, "reasons": item.reasons}
               for item in evaluations],
    "active": {"total": len(bundle.scores),
               "relative": sum(item.state == "relative" for item in bundle.scores),
               "insufficient": sum(item.state == "insufficient_data" for item in bundle.scores)},
}, sort_keys=True, allow_nan=False))
PY
}
run_gate evaluation evaluate_real_data

startup_gate() {
  local port log
  port=$($PYTHON -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')
  log="$TMP_ROOT/streamlit.log"
  STREAMLIT_BROWSER_GATHER_USAGE_STATS=false "$PYTHON" -m streamlit run app.py \
    --server.headless=true --server.address=127.0.0.1 --server.port="$port" \
    --browser.gatherUsageStats=false >"$log" 2>&1 &
  CHILD_PID=$!
  "$PYTHON" - "$port" <<'PY'
import sys, time
from urllib.request import urlopen
port = sys.argv[1]
deadline = time.monotonic() + 120
while time.monotonic() < deadline:
    try:
        if urlopen(f"http://127.0.0.1:{port}/_stcore/health", timeout=1).status == 200:
            break
    except OSError:
        time.sleep(.2)
else:
    raise SystemExit("Streamlit real não ficou pronto")
PY
  if ! "$PYTHON" - "$port" <<'PY'
import sys
from playwright.sync_api import sync_playwright
url = f"http://127.0.0.1:{sys.argv[1]}"
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    try:
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=120_000)
        # O app real calcula quatro rotas no cold start. Health prova que o
        # servidor está pronto; a UI recebe seu próprio limite explícito.
        page.get_by_role("heading", name="Prioridades comerciais explicáveis").wait_for(
            timeout=120_000)
        for stage in ("Engaging", "Prospecting"):
            page.get_by_role("tab", name=stage, exact=True).wait_for(timeout=120_000)
        text = page.locator("body").inner_text()
        if "fingerprint " not in text or "fonte " not in text or "revisão " not in text:
            raise AssertionError("identidade completa não foi renderizada")
        print("REAL_RENDERED_JOURNEY", " | ".join(text.splitlines()[:10]))
    finally:
        browser.close()
PY
  then
    printf 'Falha ao renderizar o app real; log do processo filho:\n' >&2
    cat "$log" >&2
    return 1
  fi
  kill "$CHILD_PID"
  wait "$CHILD_PID" || true
  CHILD_PID=""
}
run_gate startup startup_gate

printf '\nPREFLIGHT OK python=%s requirements_sha256=%s source_revision=%s\n' \
  "$($PYTHON --version 2>&1)" \
  "$($PYTHON -c 'import hashlib; print(hashlib.sha256(open("requirements.txt", "rb").read()).hexdigest())')" \
  "$(git rev-parse HEAD 2>/dev/null || printf unavailable)"
