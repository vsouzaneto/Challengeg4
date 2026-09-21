"""Score e categoria de ação por oportunidade. Funções puras: recebem DataFrames, devolvem DataFrames.

Lógica (cada regra tem a hipótese ou decisão que a sustenta em process-log/):
- chance = P(ganhar em 90 dias | aberto hoje, idade do deal), calibrada por painel de snapshots
  só com o passado (calibration.py; H10b, H11, painel);
- valor esperado = chance × preço de lista (H7: close_value fica em 0,998 do preço);
- score 0-100 = posição do valor esperado entre os deals abertos com chance estimável
  (percentil): "score 88" significa "vale mais que 88% do pipeline acionável";
- deals além de 138 dias não recebem chance (H9/H11): nenhum deal na história fechou depois
  disso; deals em Prospecting não recebem chance (não há histórico de prospecção → engajamento);
- vendedor, produto, setor e porte NÃO entram (H1, H2b, H4, H14, H15): sem sinal contra o acaso;
- conta ausente vira ação de higiene (H17, decisão 13), não fator: nos dados nenhum deal sem
  conta fechou, mas não dá para separar causa de preenchimento no fechamento;
- categorias nascem da idade (H8b: metade das derrotas acontece em até 14 dias) e do suporte.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .calibration import Calibration, calibrate
from .data import CLOSED_STAGES, OPEN_STAGES

CRITICAL_WINDOW_DAYS = 14
FOCUS_SCORE = 70

CAT_ALIVE = "Confirmar se está vivo"
CAT_CRITICAL = "Primeiras duas semanas: contato agora"
CAT_FOCUS = "Focar agora"
CAT_FOLLOW = "Manter follow-up"
CAT_QUALIFY = "Qualificar ou descartar"
CATEGORY_ORDER = [CAT_FOCUS, CAT_CRITICAL, CAT_FOLLOW, CAT_ALIVE, CAT_QUALIFY]

SUPPORT_OK = "ok"
SUPPORT_BEYOND = "além do histórico"
SUPPORT_NONE = "sem histórico"


def money(v: float) -> str:
    return f"US$ {v:,.0f}".replace(",", ".")


def _pct_rank(s: pd.Series) -> pd.Series:
    return (s.rank(pct=True, method="average") * 100).round(0)


def open_pipeline_at(enriched: pd.DataFrame, as_of: pd.Timestamp) -> pd.DataFrame:
    """Deals abertos em as_of: Prospecting (sem engage_date) + Engaging engajados até as_of e
    não fechados até as_of (inclui os que fecharam depois, para o backtest)."""
    df = enriched
    prospecting = df["deal_stage"].isin(OPEN_STAGES) & df["engage_date"].isna()
    engaging = df["engage_date"].notna() & (df["engage_date"] <= as_of) & (df["close_date"].isna() | (df["close_date"] > as_of))
    op = df[prospecting | engaging].copy()
    op["stage_at_asof"] = np.where(op["engage_date"].isna(), "Prospecting", "Engaging")
    op["age_days"] = (as_of - op["engage_date"]).dt.days
    return op


def score_pipeline(enriched: pd.DataFrame, as_of: pd.Timestamp, calibration: Calibration | None = None) -> tuple[pd.DataFrame, Calibration]:
    cal = calibration or calibrate(enriched, as_of)
    op = open_pipeline_at(enriched, as_of)
    op["list_value"] = op["sales_price"].astype(float)

    op["p_win"] = op["age_days"].map(cal.p_win)
    op.loc[op["stage_at_asof"] == "Prospecting", "p_win"] = np.nan
    op["support"] = np.select(
        [op["stage_at_asof"] == "Prospecting", op["age_days"] > cal.max_support_days],
        [SUPPORT_NONE, SUPPORT_BEYOND], default=SUPPORT_OK)
    op["age_band"] = op["age_days"].map(cal.band_for)
    op["expected_value"] = op["p_win"] * op["list_value"]

    scoreable = op["support"] == SUPPORT_OK
    op["score"] = np.nan
    op.loc[scoreable, "score"] = _pct_rank(op.loc[scoreable, "expected_value"])
    op["value_rank"] = _pct_rank(op["list_value"])

    op["category"] = np.select(
        [op["support"] == SUPPORT_NONE, op["support"] == SUPPORT_BEYOND, op["age_days"] <= CRITICAL_WINDOW_DAYS, op["score"] >= FOCUS_SCORE],
        [CAT_QUALIFY, CAT_ALIVE, CAT_CRITICAL, CAT_FOCUS], default=CAT_FOLLOW)
    op["needs_account"] = op["account"].isna()
    op["explanation"] = [explain(r, cal) for r in op.to_dict("records")]
    op["next_step"] = [next_step(r) for r in op.to_dict("records")]

    # Ordem: score (sem chance estimável vai para o fim), depois valor de lista; empates por conta
    # cadastrada (dá para agir) e idade menor. Nada aqui usa vendedor, produto ou setor.
    op = op.sort_values(["score", "value_rank", "needs_account", "age_days"], ascending=[False, False, True, True], na_position="last")
    return op, cal


def _fmt_n(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def explain(r: dict, cal: Calibration) -> str:
    """Frase por fator, em linguagem de vendedor, sem inflar o que é fraco."""
    parts = []
    if r["support"] == SUPPORT_NONE:
        parts.append("Ainda em prospecção, sem data de engajamento. O histórico não registra quantas prospecções viram engajamento, então não há chance estimável.")
        parts.append(f"Valor de lista {money(r['list_value'])} (acima de {int(r['value_rank'])}% dos deals abertos).")
    elif r["support"] == SUPPORT_BEYOND:
        parts.append(f"Engajado há {int(r['age_days'])} dias. Nenhum deal no histórico fechou, ganho ou perdido, depois de {cal.max_support_days} dias.")
        parts.append(f"Valor de lista {money(r['list_value'])} (acima de {int(r['value_rank'])}% dos deals abertos): vale confirmar antes de investir tempo.")
    else:
        band = r["age_band"]; p = r["p_win"]; n = _fmt_n(cal.n_for(r["age_days"]))
        lo, hi = cal.ci_by_band[band]
        if cal.mode == "painel":
            parts.append(f"Engajado há {int(r['age_days'])} dias. Deals com conta cadastrada, abertos com {band} dias, fecharam ganhos nos 90 dias seguintes em {p*100:.0f}% dos casos "
                         f"(entre {lo*100:.0f}% e {hi*100:.0f}%, n={n} em {len(cal.snapshots)} datas de 2017).")
        else:
            parts.append(f"Engajado há {int(r['age_days'])} dias. Taxa histórica de ganho entre deals que fecharam: {p*100:.0f}% (n={n}); sem painel suficiente antes desta data, a chance está superestimada.")
        if band == "0-14":
            parts.append("É a janela em que metade das derrotas acontece: contato agora é o que mais muda o resultado.")
        elif band == "121-138":
            parts.append("Está no fim do prazo em que deals ainda fecham; depois de 138 dias nenhum fechou.")
        parts.append(f"Valor de lista {money(r['list_value'])} × chance {p*100:.0f}% = valor esperado {money(r['expected_value'])}, maior que {int(r['score'])}% dos deals abertos com chance estimável. Score {int(r['score'])}.")
    if r["needs_account"]:
        parts.append("Sem conta cadastrada: nos dados, nenhum deal fechou sem conta. Cadastre antes do próximo passo.")
    parts.append("Vendedor, produto e setor não mudam o score: nos dados, nenhum deles separa ganho de perda além do acaso.")
    return " ".join(parts)


def next_step(r: dict) -> str:
    cat = r["category"]
    if cat == CAT_ALIVE:
        return "Ligar ou escrever hoje para confirmar se a oportunidade ainda existe; se não, encerrar como Lost para limpar o pipeline."
    if cat == CAT_CRITICAL:
        return "Contato nesta semana, com próximo passo e data combinados: é a janela em que o deal mais morre."
    if cat == CAT_FOCUS:
        return "Prioridade da semana: avançar para proposta ou fechamento; é um dos deals de maior valor esperado."
    if cat == CAT_QUALIFY:
        return "Decidir nesta semana: qualificar (registrar engajamento) ou descartar. Cadastrar a conta se for qualificar."
    return "Follow-up regular; sem urgência acima da média."


def summarize_categories(scored: pd.DataFrame) -> pd.DataFrame:
    g = scored.groupby("category").agg(deals=("opportunity_id", "size"), valor_lista=("list_value", "sum"), valor_esperado=("expected_value", "sum"), sem_conta=("needs_account", "sum"))
    return g.reindex([c for c in CATEGORY_ORDER if c in g.index])
