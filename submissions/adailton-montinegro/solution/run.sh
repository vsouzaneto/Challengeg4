#!/usr/bin/env bash
# ==============================================================================
# run.sh - Script de Execução Autônoma da Solução RavenStack Churn Analytics
# ==============================================================================

set -e

echo "=========================================================="
echo "   INICIALIZANDO PLATAFORMA RAVENSTACK CHURN INTELLIGENCE"
echo "=========================================================="

# 1. Ativação do Virtualenv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "[!] Criando virtualenv isolado com python 3.12..."
    uv venv .venv --python 3.12
    source .venv/bin/activate
    uv pip install -r submissions/adailton-montinegro/solution/requirements.txt
fi

# 2. Execução do Pipeline DuckDB
echo "[*] Executando pipeline determinístico DuckDB (Bronze -> Silver -> Gold)..."
python3 submissions/adailton-montinegro/solution/src/pipeline.py

# 3. Inicialização da Interface Streamlit
echo "=========================================================="
echo "   INICIANDO DASHBOARD INTERATIVO STREAMLIT (PORTA 8501)"
echo "=========================================================="
streamlit run submissions/adailton-montinegro/solution/src/app.py --server.headless true --server.port 8501
