"""Calibração da chance de ganho por painel de snapshots.

Pergunta que o vendedor faz: "este deal, aberto hoje com esta idade, fecha ganho nos
próximos 90 dias?" A taxa condicionada a "deals que fecharam" (Won/(Won+Lost)) não responde
isso, porque ignora a fatia do pipeline que nunca fecha (process-log/hypotheses.md, H11).

Método:
1. Para cada fim de mês t entre 2017-03-31 e (as_of − H), reconstrói o pipeline em Engaging
   aberto em t (engajado até t, não fechado até t) e observa se fechou ganho até t + H.
   Como t + H <= as_of, nenhum resultado posterior à data de referência entra.
2. Agrupa por faixa de idade fixa, definida antes de olhar os dados: 0-14 (janela em que
   metade das derrotas acontece), 15-90, 91-120, 121-138 (limite do suporte histórico).
3. Usa só deals com conta cadastrada: nos dados, nenhum deal sem conta fechou, mas não é
   possível saber se a conta é preenchida no fechamento ou se deals sem conta não são
   trabalhados. Por isso a conta é ação de higiene, não fator de probabilidade (decisão 13).

Bordas da base (H21): fechamentos só a partir de 2017-03-01, logo o primeiro snapshot é
2017-03-31. Faixa com menos de MIN_BAND_N linhas é fundida com a vizinha anterior.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt

import pandas as pd

WINDOW_START = pd.Timestamp("2017-03-01")
FIRST_SNAPSHOT = pd.Timestamp("2017-03-31")
MAX_SUPPORT_DAYS = 138   # maior ciclo já concluído na base, Won e Lost (H9)
HORIZON_DAYS = 90
AGE_BANDS: tuple[tuple[int, int, str], ...] = ((0, 14, "0-14"), (15, 90, "15-90"), (91, 120, "91-120"), (121, MAX_SUPPORT_DAYS, "121-138"))
MIN_BAND_N = 50
MIN_PANEL_ROWS = 300


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def band_name(age_days) -> str | None:
    if age_days is None or pd.isna(age_days) or age_days < 0:
        return None
    for lo, hi, name in AGE_BANDS:
        if lo <= age_days <= hi:
            return name
    return None


def snapshot_dates(as_of: pd.Timestamp, horizon_days: int = HORIZON_DAYS) -> list[pd.Timestamp]:
    """Fins de mês a partir de 2017-03-31 cujo horizonte cabe inteiro antes de as_of."""
    dates = []
    d = FIRST_SNAPSHOT
    while d + pd.Timedelta(days=horizon_days) <= as_of:
        dates.append(d)
        d = (d + pd.Timedelta(days=1)) + pd.offsets.MonthEnd(0)
    return dates


def open_engaging_at(enriched: pd.DataFrame, t: pd.Timestamp) -> pd.DataFrame:
    """Deals em Engaging abertos em t: engajados até t e (ainda abertos ou fechados depois de t)."""
    e = enriched
    mask = e["engage_date"].notna() & (e["engage_date"] <= t) & (e["close_date"].isna() | (e["close_date"] > t))
    op = e.loc[mask].copy()
    op["age_days"] = (t - op["engage_date"]).dt.days
    return op


def build_panel(enriched: pd.DataFrame, dates: list[pd.Timestamp], horizon_days: int = HORIZON_DAYS) -> pd.DataFrame:
    rows = []
    for t in dates:
        op = open_engaging_at(enriched, t)
        op = op[op["age_days"] <= MAX_SUPPORT_DAYS]
        end = t + pd.Timedelta(days=horizon_days)
        rows.append(pd.DataFrame({
            "snapshot": t, "opportunity_id": op["opportunity_id"].values, "age_days": op["age_days"].values,
            "band": op["age_days"].map(band_name).values, "has_account": op["account"].notna().values,
            "list_value": op["sales_price"].values,
            "won_h": ((op["deal_stage"] == "Won") & (op["close_date"] <= end)).values,
            "closed_h": (op["deal_stage"].isin(("Won", "Lost")) & (op["close_date"] <= end)).values,
        }))
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=["snapshot", "opportunity_id", "age_days", "band", "has_account", "list_value", "won_h", "closed_h"])


@dataclass(frozen=True)
class Calibration:
    as_of: pd.Timestamp
    horizon_days: int
    snapshots: tuple[str, ...]
    n_rows: int                       # linhas deal×snapshot com conta cadastrada usadas
    p_by_band: dict[str, float]       # P(ganhar em H dias | aberto, idade na faixa, com conta)
    n_by_band: dict[str, int]
    ci_by_band: dict[str, tuple[float, float]]
    merged_into: dict[str, str] = field(default_factory=dict)   # faixa -> faixa com que foi fundida
    p_all_deals_by_band: dict[str, float] = field(default_factory=dict)  # referência: incluindo deals sem conta
    mode: str = "painel"
    max_support_days: int = MAX_SUPPORT_DAYS

    def band_for(self, age_days) -> str | None:
        return band_name(age_days)

    def p_win(self, age_days) -> float | None:
        b = self.band_for(age_days)
        return None if b is None else self.p_by_band[b]

    def n_for(self, age_days) -> int:
        b = self.band_for(age_days)
        return 0 if b is None else self.n_by_band[b]


def _rates_with_merge(panel: pd.DataFrame) -> tuple[dict, dict, dict, dict]:
    """Taxa por faixa; faixa com n < MIN_BAND_N é fundida com a anterior (pool de contagens)."""
    p, n, ci, merged = {}, {}, {}, {}
    pool_k = pool_n = 0
    pool_name = None
    for _lo, _hi, name in AGE_BANDS:
        sub = panel[panel["band"] == name]
        k, m = int(sub["won_h"].sum()), int(len(sub))
        if m >= MIN_BAND_N or pool_name is None:
            pool_k, pool_n, pool_name = k, m, name
        else:
            pool_k += k; pool_n += m
            merged[name] = pool_name
        p[name] = pool_k / pool_n if pool_n else float("nan")
        n[name] = pool_n
        ci[name] = wilson(pool_k, pool_n)
        # faixas anteriores fundidas recebem a taxa atualizada do pool
        for other, target in merged.items():
            if target == pool_name:
                p[other], n[other], ci[other] = p[name], n[name], ci[name]
        if name in merged:
            p[merged[name]], n[merged[name]], ci[merged[name]] = p[name], n[name], ci[name]
    return p, n, ci, merged


def calibrate(enriched: pd.DataFrame, as_of: pd.Timestamp, horizon_days: int = HORIZON_DAYS) -> Calibration:
    dates = snapshot_dates(as_of, horizon_days)
    panel = build_panel(enriched, dates, horizon_days)
    with_acc = panel[panel["has_account"]]
    if len(with_acc) >= MIN_PANEL_ROWS:
        p, n, ci, merged = _rates_with_merge(with_acc)
        p_all = {name: float(panel.loc[panel["band"] == name, "won_h"].mean()) if (panel["band"] == name).any() else float("nan") for _l, _h, name in AGE_BANDS}
        return Calibration(as_of=as_of, horizon_days=horizon_days, snapshots=tuple(str(d.date()) for d in dates), n_rows=int(len(with_acc)),
                           p_by_band=p, n_by_band=n, ci_by_band=ci, merged_into=merged, p_all_deals_by_band=p_all, mode="painel")
    # Fallback: sem painel suficiente antes de as_of, usa a taxa condicionada a fechar (Won/(Won+Lost))
    # dos deals fechados até as_of, o que superestima a chance (ignora quem nunca fecha) e é dito na UI.
    closed = enriched[enriched["deal_stage"].isin(("Won", "Lost")) & (enriched["close_date"] <= as_of) & (enriched["engage_date"] >= WINDOW_START)]
    if len(closed) < MIN_BAND_N:
        closed = enriched[enriched["deal_stage"].isin(("Won", "Lost")) & (enriched["close_date"] <= as_of)]
    if len(closed) == 0:
        raise ValueError("sem histórico até a data de referência; impossível calibrar")
    won = closed["deal_stage"].eq("Won")
    cycle = (closed["close_date"] - closed["engage_date"]).dt.days
    p, n, ci = {}, {}, {}
    for lo, _hi, name in AGE_BANDS:
        surv = won[cycle >= lo]
        k, m = int(surv.sum()), int(len(surv))
        p[name] = k / m if m else float(won.mean()); n[name] = m; ci[name] = wilson(k, m)
    return Calibration(as_of=as_of, horizon_days=horizon_days, snapshots=(), n_rows=int(len(closed)), p_by_band=p, n_by_band=n, ci_by_band=ci,
                       mode="fallback: taxa condicional a fechar (Won/(Won+Lost)) dos fechados até a data")
