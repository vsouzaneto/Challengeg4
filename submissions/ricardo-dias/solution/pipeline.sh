#!/usr/bin/env bash
# Reproduz toda a análise e verifica o protótipo.
# Requer: uv (Python 3.12), Node 24, CSVs do Kaggle em ../../../../data/raw (ou DATA_DIR).
set -euo pipefail
cd "$(dirname "$0")"

echo "== 01 auditoria";            (cd analysis && uv run python 01_audit.py)
echo "== 03 classificador";        (cd analysis && uv run python 03_classifier.py)
echo "== roteamento (funções da API)"; (cd app && npm run --silent eval:routing)
echo "== 02 diagnóstico";          (cd analysis && uv run python 02_diagnostico.py)
echo "== 05 documentos";           (cd analysis && uv run python 05_report.py)
echo "== testes, tipos, lint";     (cd app && npm test && npx tsc --noEmit && npm run lint)
echo "OK"
