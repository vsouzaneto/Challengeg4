"""Parâmetros e premissas da solução, sem lógica.

Faixas de valor e percentil do primeiro limite são política provisória (U-06): sem
validação da Head de RevOps, editáveis aqui sem tocar no motor. A regra de grupos
é a regra A (ADR-006).
"""
from __future__ import annotations

from pathlib import Path

from . import codes

SOLUTION_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = SOLUTION_DIR / "data" / "raw"
# Resultado do backtest (scripts/backtest.py), servido em /api/evidence.
EVIDENCE_PATH = SOLUTION_DIR / "data" / "processed" / "backtest_results.json"
DATASET_URL = "https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics"

# Colunas que a solução usa de cada tabela; as demais são ignoradas. `close_value` e os
# atributos do cliente só servem à Inteligência (ADR-007): a classificação não os enxerga.
REQUIRED_COLUMNS = {
    "sales_pipeline": (
        "opportunity_id", "sales_agent", "product", "account",
        "deal_stage", "engage_date", "close_date", "close_value",
    ),
    "products": ("product", "sales_price"),
    "sales_teams": ("sales_agent", "manager", "regional_office"),
    "accounts": ("account", "sector", "revenue", "office_location"),
}

# SHA-256 da versão auditada (data-audit.md, A§7).
AUDITED_SHA256 = {
    "sales_pipeline": "825ce8f6c32d4009548b468df3173d55a46fd73f2531f532c5459371dc52adf2",
    "products": "7c1c8cbbdb6d4c286902e1985eeb529a36366d6a43f43cd4a93c4b1da2a6eb84",
    "sales_teams": "aeff1272ebe196f5a27e3fc0578aa27abf48ed9ae461aa344fb95990e5ad8bd1",
    "accounts": "e5242324768a563fc632cddfed49a29acbbf2892b8a3c6453cc9650de9ae0358",
}

# Grafias do pipeline que não batem com o catálogo (A§2.4).
PRODUCT_MAP = {"GTXPro": "GTX Pro"}
# Grafias erradas nos atributos do cliente (A§2.6, "revisão obrigatória"), corrigidas na carga.
LABEL_MAPS = {"sector": {"technolgy": "technology"}, "office_location": {"Philipines": "Philippines"}}

OPEN_STAGES = ("Engaging", "Prospecting")
CLOSED_STAGES = ("Won", "Lost")

# Únicos campos que a classificação enxerga (RD-02). `close_date` entra só
# nos dois limites de idade, e só de fechadas até o as_of.
CLASSIFICATION_FIELDS = (
    "opportunity_id", "sales_agent", "manager", "regional_office",
    "product", "sales_price", "account", "deal_stage", "engage_date",
)

# Estados (grupos), na ordem da lista. São chaves: o nome de cada grupo é de quem apresenta.
# Engaging (regra A): focar até L1; acompanhar acima de L1 até L2; revisar acima de L2.
# Qualificar (Prospecting) vem logo depois de focar, antes de acompanhar e revisar (ADR-009): as Engaging acima de
# L1 já passaram do tempo em que a maioria das ganhas fechou e as acima de L2, de qualquer ganha. É uma decisão de
# produto: o backtest não avalia a Prospecting, então a posição dela não tem prova de desfecho.
FOCAR, ACOMPANHAR, REVISAR = "focar", "acompanhar", "revisar"
QUALIFICAR, NAO_PONTUAVEL = "qualificar", "nao_pontuavel"
STATES = (FOCAR, QUALIFICAR, ACOMPANHAR, REVISAR, NAO_PONTUAVEL)

# Campos necessários para pontuar; a ordem define qual é citado primeiro (RD-03).
MISSING_FIELDS = ("product", "sales_price", "engage_date")

# Primeiro limite de idade (L1): o piso deste percentil (quantil linear) do ciclo das
# ganhas até o as_of, um número só para todos os produtos. O segundo (L2) é o maior
# ciclo fechado até o as_of.
CYCLE_PERCENTILE = 90

# Faixa de valor de tabela: alto >= 3.000; médio de 500 a 2.999; baixo < 500.
VALUE_BANDS = (("alto", 3000), ("médio", 500), ("baixo", 0))

# O que verificar por estado (PRD, P0-3; ADR-008), como código. A ferramenta só lê o CRM (RE-03) e não vê
# atividades: a orientação é uma verificação com base nos dados disponíveis, não uma ação comercial.
NEXT_ACTIONS = {
    FOCAR: codes.CHECK_STATUS,
    ACOMPANHAR: codes.CHECK_PROGRESS,
    REVISAR: codes.CONFIRM_STILL_ACTIVE,
    QUALIFICAR: codes.CHECK_PROSPECTING,
}
# Focar vazio aponta o primeiro grupo seguinte que tem oportunidades (Q-01), com esta ação.
START_ACTION_CODES = {
    ACOMPANHAR: codes.CHECK_PROGRESS,
    REVISAR: codes.CONFIRM_STILL_ACTIVE,
    QUALIFICAR: codes.CHECK_PROSPECTING,
    NAO_PONTUAVEL: codes.FIX_MISSING_FIELDS,
}

# Nenhum texto mostrado ao vendedor pode conter palavras que comecem por estes termos (AC-3.8):
# a checagem é por início de palavra, então "parad" pega "paradas" mas não "comparado". Os
# catálogos da tela e da CLI são verificados contra esta lista (a tela a lê de uma fixture).
# Além de prometer chance, nenhum texto apresenta um limite de idade como prazo ou afirma
# inatividade: o sistema não vê ligações nem reuniões.
FORBIDDEN_TERMS = ("probabilidade", "perdida", "encerre", "prioridade alta", "chance alta", "score",
                   "prazo", "vence", "vencid", "atrasad", "expir", "faltam", "parad", "inativ", "chance zero")

# Inteligência comercial (ADR-007): descreve o histórico, não prevê. Parâmetros das regras
# determinísticas de diagnósticos e descobertas, editáveis aqui sem tocar no módulo.
CHANCE_ALPHA = 0.05            # nível do teste de acaso da taxa de ganho, dividido pelas dimensões (Bonferroni)
MIN_CLOSED_PER_SEGMENT = 20    # segmento com menos fechadas fica fora do teste de acaso
MIN_SEGMENTS_FOR_DRIVERS = 4   # decomposição da receita só com pelo menos 4 segmentos (3 escritórios não bastam)
DRIVER_MAIN_SHARE = 0.25       # fator que explica ao menos isto da diferença de receita é citado como principal
DRIVER_NEGLIGIBLE_SHARE = 0.05  # fator que explica no máximo isto (em módulo) é citado como desprezível
CONCENTRATION_SHARE = 0.80     # receita concentrada: o menor topo de segmentos que passa desta fatia...
CONCENTRATION_MAX_FRACTION = 0.5  # ...desde que seja no máximo metade dos segmentos
CYCLE_BAND_EDGES = (15, 30, 60, 90)  # faixas de ciclo das fechadas, completadas por L1 e L2 do as_of
INFLOW_DROP_RATIO = 0.5        # queda de entrada: média dos 2 últimos meses abaixo desta fração dos 5 anteriores
INFLOW_RECENT_MONTHS, INFLOW_BASE_MONTHS = 2, 5
SHARED_ACCOUNT_MIN_SELLERS = 3  # cliente compartilhado: mediana de vendedores por cliente a partir disto
SIZE_QUANTILES = 4             # porte do cliente: quartis dos clientes pela receita anual
