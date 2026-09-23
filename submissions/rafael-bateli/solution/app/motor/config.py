"""Caminhos, premissas e variáveis de ambiente do protótipo.

Os caminhos são funções (e não constantes) para que testes e tela troquem a
pasta de dados por variável de ambiente sem reimportar o módulo.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
SOL = APP.parent
OUT_APP = APP / "outputs"
OUT_AUTOMACAO = SOL / "automacao" / "outputs"
OUT_DIAG = SOL / "diagnostico" / "outputs"
KB = APP / "kb"

# Módulos das Entregas 1–2 importados como fonte da verdade (não copiados).
for _p in (SOL / "automacao", SOL / "diagnostico" / "solucao"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

KAGGLE_D1 = "https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset"
KAGGLE_D2 = "https://www.kaggle.com/datasets/adisongoh/it-service-ticket-classification-dataset"

# Premissas (não vêm do dataset; trocáveis).
SLA_HORAS = {"Critical": 1, "High": 4, "Medium": 8, "Low": 24, "Sem sinal": 8}
LIMITE_TEXTO = 5_000
MIN_PALAVRAS = 3
LLM_TIMEOUT_S = 20
RETRY_AFTER_MAX_S = 5
RASCUNHO_MAX_CHARS = 1_200
LIMIAR_DUPLICATA = 0.9


def dados_dir() -> Path:
    return Path(os.environ.get("DADOS_DIR", SOL / "data"))


def csv_d1() -> Path:
    return dados_dir() / "support_tickets.csv"


def csv_d2() -> Path:
    return dados_dir() / "it_tickets.csv"


def local_dir() -> Path:
    p = Path(os.environ.get("LOCAL_DIR", APP / "dados_locais"))
    p.mkdir(parents=True, exist_ok=True)
    return p


def dados_faltando() -> list[Path]:
    return [p for p in (csv_d1(), csv_d2()) if not p.exists()]


def carregar_env(caminho: Path = APP / ".env") -> None:
    """Lê KEY=VALOR do .env local sem sobrescrever o que já está no ambiente."""
    if not caminho.exists():
        return
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        k, v = linha.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
