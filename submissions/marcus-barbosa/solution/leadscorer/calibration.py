"""Calibração da chance de ganho por painel de snapshots.

Pergunta que o vendedor faz: "este deal, aberto hoje com esta idade, fecha ganho nos próximos
90 dias?" A taxa Won/(Won+Lost) não responde isso: ignora a fatia do pipeline que nunca fecha.

Método:
1. Para cada fim de mês t de 2017-03-31 até (as_of − H), reconstrói-se o pipeline em Engaging
   aberto em t (engajado entre 2017-03-01 e t, não fechado até t) e observa-se se fechou ganho
   até t + H. Como t + H <= as_of, nenhum desfecho posterior à data de referência entra.
   Deals engajados antes de 2017-03-01 ficam fora: são sobreviventes do truncamento à esquerda
   da base (H21), cujas derrotas rápidas não existem nos dados.
2. Faixas de idade fixadas antes de olhar os dados: 0-14 (metade das derrotas acontece aí),
   15-90, 91-120, 121-138 (maior ciclo já concluído nesta base).
3. A taxa principal usa TODOS os deals abertos em t. A conta cadastrada não filtra a calibração:
   o campo só é conhecido no estado final da base, e todo deal fechado tem conta, então filtrar
   por ele seria olhar o futuro. A taxa "entre deals que têm conta hoje" fica como sensibilidade
   otimista, declarada como tal.
4. O mesmo deal aparece em vários snapshots; por isso o intervalo de confiança é por bootstrap
   de deals (reamostra deals, não linhas) e o n é reportado como deals únicos e observações.
5. Faixa com menos de MIN_BAND_DEALS deals únicos é agrupada com as faixas MAIS VELHAS
   (P(ganhar | idade >= limite inferior)), nunca com a mais jovem. Se nem assim houver amostra,
   a faixa fica sem chance nessa data e o deal não recebe score.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

WINDOW_START = pd.Timestamp("2017-03-01")   # primeiro close_date da base (H21)
FIRST_SNAPSHOT = pd.Timestamp("2017-03-31")
MAX_SUPPORT_DAYS = 138                       # maior ciclo já concluído, Won e Lost (H9)
HORIZON_DAYS = 90
AGE_BANDS: tuple[tuple[int, int, str], ...] = ((0, 14, "0-14"), (15, 90, "15-90"), (91, 120, "91-120"), (121, MAX_SUPPORT_DAYS, "121-138"))
MIN_BAND_DEALS = 30
MIN_PANEL_DEALS = 200
BOOTSTRAP_ROUNDS = 200
BOOTSTRAP_SEED = 7


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


def open_engaging_at(enriched: pd.DataFrame, t: pd.Timestamp, window_start: pd.Timestamp = WINDOW_START) -> pd.DataFrame:
    """Deals em Engaging abertos em t, engajados dentro da janela limpa."""
    e = enriched
    mask = e["engage_date"].notna() & (e["engage_date"] >= window_start) & (e["engage_date"] <= t) & (e["close_date"].isna() | (e["close_date"] > t))
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
            "band": op["age_days"].map(band_name).values, "has_account_final": op["account"].notna().values,
            "list_value": op["sales_price"].values,
            "won_h": ((op["deal_stage"] == "Won") & (op["close_date"] <= end)).values,
            "closed_h": (op["deal_stage"].isin(("Won", "Lost")) & (op["close_date"] <= end)).values,
        }))
    cols = ["snapshot", "opportunity_id", "age_days", "band", "has_account_final", "list_value", "won_h", "closed_h"]
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame(columns=cols)


@dataclass(frozen=True)
class BandStats:
    p: float
    p_close: float
    deals: int
    obs: int
    ci: tuple[float, float]


def _band_stats(panel: pd.DataFrame, bands: list[str], rounds: int = BOOTSTRAP_ROUNDS, seed: int = BOOTSTRAP_SEED) -> BandStats:
    sub = panel[panel["band"].isin(bands)]
    if sub.empty:
        return BandStats(float("nan"), float("nan"), 0, 0, (float("nan"), float("nan")))
    per_deal = sub.groupby("opportunity_id").agg(k=("won_h", "sum"), c=("closed_h", "sum"), n=("won_h", "size"))
    k, c, n = per_deal["k"].to_numpy(float), per_deal["c"].to_numpy(float), per_deal["n"].to_numpy(float)
    p = float(k.sum() / n.sum()); p_close = float(c.sum() / n.sum())
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(per_deal), size=(rounds, len(per_deal)))
    boots = k[idx].sum(axis=1) / n[idx].sum(axis=1)
    lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    return BandStats(p, p_close, int(len(per_deal)), int(n.sum()), (lo, hi))


@dataclass(frozen=True)
class Calibration:
    as_of: pd.Timestamp
    horizon_days: int
    snapshots: tuple[str, ...]
    n_obs: int                                  # linhas deal × data no painel
    n_deals: int                                # deals únicos no painel
    p_by_band: dict[str, float | None]          # None = sem suporte nesta data
    p_close_by_band: dict[str, float | None]    # P(fechar, ganho ou perda, em H dias)
    n_deals_by_band: dict[str, int]
    n_obs_by_band: dict[str, int]
    ci_by_band: dict[str, tuple[float, float]]
    pooled_from: dict[str, str] = field(default_factory=dict)   # faixa -> faixas agrupadas (P(ganhar | idade >= limite))
    p_with_account_by_band: dict[str, float] = field(default_factory=dict)  # sensibilidade otimista (look-ahead na conta)
    mode: str = "painel"
    max_support_days: int = MAX_SUPPORT_DAYS

    def band_for(self, age_days) -> str | None:
        return band_name(age_days)

    def p_win(self, age_days) -> float | None:
        b = self.band_for(age_days)
        return None if b is None else self.p_by_band.get(b)

    def n_for(self, age_days) -> tuple[int, int]:
        b = self.band_for(age_days)
        return (0, 0) if b is None else (self.n_deals_by_band.get(b, 0), self.n_obs_by_band.get(b, 0))


def calibrate(enriched: pd.DataFrame, as_of: pd.Timestamp, horizon_days: int = HORIZON_DAYS) -> Calibration:
    dates = snapshot_dates(as_of, horizon_days)
    panel = build_panel(enriched, dates, horizon_days)
    if not panel.empty and panel["opportunity_id"].nunique() >= MIN_PANEL_DEALS:
        p, pc, nd, no, ci, pooled, pacc = {}, {}, {}, {}, {}, {}, {}
        for lo, _hi, name in AGE_BANDS:
            s = _band_stats(panel, [name])
            if s.deals < MIN_BAND_DEALS:
                older = [b for l, _h, b in AGE_BANDS if l >= lo]
                if len(older) > 1:
                    s = _band_stats(panel, older)
                    pooled[name] = "+".join(older)
            if s.deals < MIN_BAND_DEALS:
                p[name] = None; pc[name] = None; nd[name] = s.deals; no[name] = s.obs; ci[name] = (float("nan"), float("nan"))
                continue
            p[name] = s.p; pc[name] = s.p_close; nd[name] = s.deals; no[name] = s.obs; ci[name] = s.ci
            acc = panel[panel["has_account_final"] & panel["band"].isin(pooled.get(name, name).split("+"))]
            pacc[name] = float(acc["won_h"].mean()) if len(acc) else float("nan")
        return Calibration(as_of=as_of, horizon_days=horizon_days, snapshots=tuple(str(d.date()) for d in dates), n_obs=int(len(panel)),
                           n_deals=int(panel["opportunity_id"].nunique()), p_by_band=p, p_close_by_band=pc, n_deals_by_band=nd, n_obs_by_band=no,
                           ci_by_band=ci, pooled_from=pooled, p_with_account_by_band=pacc, mode="painel")
    # Fallback declarado: sem painel suficiente antes de as_of, usa a taxa condicionada a fechar
    # (Won/(Won+Lost)) dos fechados até as_of na janela limpa, que superestima a chance.
    closed = enriched[enriched["deal_stage"].isin(("Won", "Lost")) & (enriched["close_date"] <= as_of) & (enriched["engage_date"] >= WINDOW_START)]
    if len(closed) < MIN_BAND_DEALS:
        closed = enriched[enriched["deal_stage"].isin(("Won", "Lost")) & (enriched["close_date"] <= as_of)]
    if len(closed) == 0:
        raise ValueError("sem histórico até a data de referência; impossível calibrar")
    won = closed["deal_stage"].eq("Won")
    cycle = (closed["close_date"] - closed["engage_date"]).dt.days
    p, pc, nd, no, ci = {}, {}, {}, {}, {}
    for lo, _hi, name in AGE_BANDS:
        surv = won[cycle >= lo]
        m = int(len(surv)); k = int(surv.sum())
        p[name] = (k / m) if m else float(won.mean()); pc[name] = 1.0; nd[name] = m; no[name] = m
        se = np.sqrt(p[name] * (1 - p[name]) / m) if m else 0.5
        ci[name] = (max(0.0, p[name] - 1.96 * se), min(1.0, p[name] + 1.96 * se))
    return Calibration(as_of=as_of, horizon_days=horizon_days, snapshots=(), n_obs=int(len(closed)), n_deals=int(len(closed)), p_by_band=p, p_close_by_band=pc,
                       n_deals_by_band=nd, n_obs_by_band=no, ci_by_band=ci, mode="fallback: taxa condicional a fechar (Won/(Won+Lost)) dos fechados até a data; superestima a chance")
