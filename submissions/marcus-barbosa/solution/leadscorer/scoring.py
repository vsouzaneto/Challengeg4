"""Score e categoria de ação por oportunidade. Funções puras: recebem DataFrames, devolvem DataFrames.

Lógica (cada regra tem a hipótese ou decisão que a sustenta em process-log/):
- chance = P(ganhar em 90 dias | aberto hoje, faixa de idade), calibrada por painel de snapshots
  só com o passado e sem filtro de conta (calibration.py; H10b, H11, decisões 12 e 18);
- valor esperado = chance × preço de lista (H7: close_value fica em 0,998 do preço). O produto
  pesa pelo preço, não por taxa de fechamento (H4);
- score 0-100 = posição do valor esperado entre os deals acionáveis (percentil): "score 88"
  significa "vale mais que 88% do pipeline acionável"; dentro de uma mesma faixa de idade, o
  score ordena como o preço;
- sem chance e sem score: Engaging além de 138 dias (nenhum deal desta base fechou depois disso),
  Prospecting (não há histórico de prospecção → engajamento) e faixas sem amostra na data;
- vendedor e setor não entram (H1, H2b, H15): sem sinal contra o acaso;
- conta ausente vira ação (todo deal fechado, ganho ou perdido, tem conta; H17, decisão 13),
  não fator;
- categorias nascem da idade (H8b: metade das derrotas acontece em até 14 dias; o painel mostra a
  chance caindo depois de 90 dias) e do suporte histórico.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .calibration import Calibration, calibrate
from .data import OPEN_STAGES

CRITICAL_WINDOW_DAYS = 14
LAST_WINDOW_START = 91
FOCUS_SCORE = 70

CAT_ALIVE = "Confirmar se está vivo"
CAT_LAST = "Última janela: decidir esta semana"
CAT_CRITICAL = "Primeiras duas semanas: contato agora"
CAT_FOCUS = "Focar agora"
CAT_FOLLOW = "Manter follow-up"
CAT_QUALIFY = "Qualificar ou descartar"
CATEGORY_ORDER = [CAT_FOCUS, CAT_CRITICAL, CAT_FOLLOW, CAT_LAST, CAT_ALIVE, CAT_QUALIFY]

SUPPORT_OK = "ok"
SUPPORT_BEYOND = "além do histórico"
SUPPORT_NONE = "sem histórico"
SUPPORT_THIN = "amostra insuficiente na data"


def money(v: float) -> str:
    return f"US$ {v:,.0f}".replace(",", ".")


def fmt_n(n: int) -> str:
    return f"{int(n):,}".replace(",", ".")


def _pct_rank(s: pd.Series) -> pd.Series:
    return (s.rank(pct=True, method="average") * 100).round(0)


def open_pipeline_at(enriched: pd.DataFrame, as_of: pd.Timestamp, include_prospecting: bool = True) -> pd.DataFrame:
    """Deals abertos em as_of.

    Engaging: engajados até as_of e não fechados até as_of (inclui os que fecharam depois, para o
    backtest). Prospecting: deals sem engage_date no estado final da base; como não há data de
    criação, essa fatia só é conhecida para a data de referência, e o backtest a exclui.
    """
    df = enriched
    engaging = df["engage_date"].notna() & (df["engage_date"] <= as_of) & (df["close_date"].isna() | (df["close_date"] > as_of))
    prospecting = df["deal_stage"].isin(OPEN_STAGES) & df["engage_date"].isna() if include_prospecting else pd.Series(False, index=df.index)
    op = df[prospecting | engaging].copy()
    op["stage_at_asof"] = np.where(op["engage_date"].isna(), "Prospecting", "Engaging")
    op["age_days"] = (as_of - op["engage_date"]).dt.days
    return op


def score_pipeline(enriched: pd.DataFrame, as_of: pd.Timestamp, calibration: Calibration | None = None, include_prospecting: bool = True) -> tuple[pd.DataFrame, Calibration]:
    cal = calibration or calibrate(enriched, as_of)
    op = open_pipeline_at(enriched, as_of, include_prospecting)
    op["list_value"] = op["sales_price"].astype(float)
    op["age_band"] = op["age_days"].map(cal.band_for)
    op["p_win"] = op["age_days"].map(lambda a: cal.p_win(a) if cal.p_win(a) is not None else np.nan)
    op.loc[op["stage_at_asof"] == "Prospecting", "p_win"] = np.nan
    in_range = (op["stage_at_asof"] == "Engaging") & (op["age_days"] <= cal.max_support_days)
    op["support"] = np.select(
        [op["stage_at_asof"] == "Prospecting", op["age_days"] > cal.max_support_days, in_range & op["p_win"].isna()],
        [SUPPORT_NONE, SUPPORT_BEYOND, SUPPORT_THIN], default=SUPPORT_OK)
    op["expected_value"] = op["p_win"] * op["list_value"]

    scoreable = op["support"] == SUPPORT_OK
    op["score"] = np.nan
    op.loc[scoreable, "score"] = _pct_rank(op.loc[scoreable, "expected_value"])
    op["value_rank"] = _pct_rank(op["list_value"])

    op["category"] = np.select(
        [op["support"] == SUPPORT_NONE, op["support"] == SUPPORT_BEYOND, op["age_days"] >= LAST_WINDOW_START,
         op["age_days"] <= CRITICAL_WINDOW_DAYS, op["score"] >= FOCUS_SCORE],
        [CAT_QUALIFY, CAT_ALIVE, CAT_LAST, CAT_CRITICAL, CAT_FOCUS], default=CAT_FOLLOW)
    op["needs_account"] = op["account"].isna()
    op["explanation"] = [explain(r, cal) for r in op.to_dict("records")]
    op["next_step"] = [next_step(r) for r in op.to_dict("records")]

    # Ordem: score (sem chance vai para o fim), valor de lista, conta cadastrada, idade menor.
    # Vendedor e setor não participam.
    op = op.sort_values(["score", "value_rank", "needs_account", "age_days"], ascending=[False, False, True, True], na_position="last")
    return op, cal


def _pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def explain(r: dict, cal: Calibration) -> str:
    """Frases por fator, em linguagem de vendedor, com número e denominador."""
    parts = []
    idade = None if pd.isna(r["age_days"]) else int(r["age_days"])
    if r["support"] == SUPPORT_NONE:
        parts.append("Em prospecção, sem data de engajamento. O histórico não registra quantas prospecções viram engajamento, então não há chance estimável.")
        parts.append(f"Valor de lista {money(r['list_value'])}, acima de {int(r['value_rank'])}% dos deals abertos.")
    elif r["support"] == SUPPORT_BEYOND:
        parts.append(f"Engajado há {idade} dias. Nesta base nenhum deal fechou, ganho ou perdido, depois de {cal.max_support_days} dias; entre 121 e 138 dias, a chance de fechar em 90 dias já é de {_pct(cal.p_close_by_band.get('121-138') or 0)}.")
        parts.append(f"Valor de lista {money(r['list_value'])}, acima de {int(r['value_rank'])}% dos deals abertos: confirmar antes de investir tempo.")
    elif r["support"] == SUPPORT_THIN:
        parts.append(f"Engajado há {idade} dias. Nesta data ainda não há amostra suficiente de deals com essa idade para estimar a chance; sem score.")
        parts.append(f"Valor de lista {money(r['list_value'])}, acima de {int(r['value_rank'])}% dos deals abertos.")
    else:
        band = r["age_band"]; p = r["p_win"]; deals, obs = cal.n_for(r["age_days"]); lo, hi = cal.ci_by_band[band]
        if cal.mode == "painel":
            faixa = f"idade de {cal.pooled_from[band].split('+')[0].split('-')[0]} dias ou mais" if band in cal.pooled_from else f"{band} dias"
            k = len(cal.snapshots); datas = "1 fim de mês" if k == 1 else f"{k} fins de mês"
            parts.append(f"Engajado há {idade} dias. De cada 100 deals abertos com {faixa} nesta base, {p * 100:.0f} fecharam ganhos nos 90 dias seguintes "
                         f"(entre {_pct(lo)} e {_pct(hi)}; {fmt_n(deals)} deals em {fmt_n(obs)} observações, {datas} de 2017).")
        else:
            parts.append(f"Engajado há {idade} dias. Taxa de ganho entre deals que fecharam: {p * 100:.0f}% (n={fmt_n(deals)}); sem painel suficiente antes desta data, a chance está superestimada.")
        if band == "0-14":
            parts.append("É a janela em que metade das derrotas acontece: contato agora é o que mais muda o resultado.")
        elif band in ("91-120", "121-138"):
            parts.append("Depois de 90 dias a chance cai; depois de 138, nesta base, ninguém fechou.")
        parts.append(f"Valor de lista {money(r['list_value'])} × chance {p * 100:.0f}% = valor esperado {money(r['expected_value'])}, maior que {int(r['score'])}% dos deals acionáveis. Score {int(r['score'])}.")
    if r["needs_account"]:
        parts.append("Sem conta no CRM: todo deal fechado, ganho ou perdido, tem conta; cadastre para o deal ser acompanhado.")
    return " ".join(parts)


def next_step(r: dict) -> str:
    cat = r["category"]
    base = {
        CAT_ALIVE: "Ligar ou escrever hoje para confirmar se a oportunidade ainda existe; se não, encerrar como Lost para limpar o pipeline.",
        CAT_LAST: "Última janela: pedir a decisão do cliente nesta semana ou encerrar.",
        CAT_CRITICAL: "Contato nesta semana, com próximo passo e data combinados: é a janela em que o deal mais morre.",
        CAT_FOCUS: "Prioridade da semana: avançar para proposta ou fechamento; é um dos deals de maior valor esperado.",
        CAT_QUALIFY: "Decidir nesta semana: qualificar (registrar engajamento) ou descartar.",
    }.get(cat, "Follow-up regular; sem urgência acima da média.")
    if r["needs_account"]:
        return "Cadastrar a conta no CRM hoje; depois, " + base[0].lower() + base[1:]
    return base


def summarize_categories(scored: pd.DataFrame) -> pd.DataFrame:
    g = scored.groupby("category").agg(deals=("opportunity_id", "size"), valor_lista=("list_value", "sum"), valor_esperado=("expected_value", "sum"), sem_conta=("needs_account", "sum"))
    return g.reindex([c for c in CATEGORY_ORDER if c in g.index])
