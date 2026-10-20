"""Inteligência comercial (ADR-007): o histórico descrito, com diagnósticos do processo e descobertas.

Funções puras sobre o `Dataset`. Descreve e compara o histórico até o `as_of`; não prevê
nem ordena oportunidades: nada daqui entra na classificação (`triage`). As abertas vêm
de `triage.classify` com o recorte de `views.scope`, então os grupos são os mesmos da
Equipe. Entrega chaves, códigos e números; o texto é de quem apresenta (ADR-004).

Taxa de ganho = ganhas ÷ fechadas, com a faixa provável de Wilson (95%). Toda comparação
de taxa entre segmentos passa por um teste de acaso (qui-quadrado) com Bonferroni sobre as
dimensões. A receita de um segmento é fechadas × taxa de ganho × ticket; a decomposição diz
quanto da diferença de receita entre segmentos vem de cada fator.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from . import codes, policy, triage, views
from .data import Dataset
from .errors import PolicyError

Payload = Dict[str, Any]

# Coluna de cada dimensão no frame enriquecido.
DIM_COLUMNS = {
    codes.DIM_PRODUCT: "product", codes.DIM_SELLER: "sales_agent", codes.DIM_MANAGER: "manager",
    codes.DIM_OFFICE: "regional_office", codes.DIM_SECTOR: "sector", codes.DIM_ACCOUNT: "account",
    codes.DIM_SIZE: "size",
}
# Atributos do cliente: filtrar por eles tira do recorte as abertas sem cliente registrado.
ACCOUNT_DIMENSIONS = (codes.DIM_SECTOR, codes.DIM_ACCOUNT, codes.DIM_SIZE)
# Concentração só em recortes que não são pessoas (RD-06).
CONCENTRATION_DIMENSIONS = (codes.DIM_PRODUCT, codes.DIM_SECTOR, codes.DIM_ACCOUNT, codes.DIM_SIZE)
DRIVER_FINDING_DIMENSIONS = (codes.DIM_SELLER, codes.DIM_PRODUCT, codes.DIM_SIZE)
QUARTER_END_MONTHS = (3, 6, 9, 12)
WILSON_Z = 1.959963984540054


@dataclass(frozen=True)
class Filters:
    """Recorte da página. Um valor inexistente não é erro: dá recorte vazio (padrão AC-2.10)."""
    product: Optional[str] = None
    seller: Optional[str] = None
    manager: Optional[str] = None
    office: Optional[str] = None
    sector: Optional[str] = None
    account: Optional[str] = None
    size: Optional[str] = None

    def value(self, dimension: str) -> Optional[str]:
        return getattr(self, dimension) or None

    def without_account_attributes(self) -> "Filters":
        return Filters(product=self.product, seller=self.seller, manager=self.manager, office=self.office)

    @property
    def by_account_attribute(self) -> bool:
        return any(self.value(d) for d in ACCOUNT_DIMENSIONS)


# Números: proporções com 6 casas (a tela arredonda a porcentagem uma vez só), valores com 2 e
# medianas inteiras (meio para cima).
RATE_DIGITS = 6


def _ratio(part: float, whole: float, digits: int = RATE_DIGITS) -> Optional[float]:
    return round(float(part) / float(whole), digits) if whole else None


def _median_days(days: pd.Series) -> Optional[int]:
    days = days.dropna()
    return int(math.floor(float(days.median()) + 0.5)) if len(days) else None


def wilson(won: int, n: int) -> Optional[Dict[str, float]]:
    """Taxa de ganho com a faixa provável (Wilson, 95%); nula sem fechadas."""
    if not n:
        return None
    p, z2 = won / n, WILSON_Z ** 2
    center = (p + z2 / (2 * n)) / (1 + z2 / n)
    half = WILSON_Z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n)) / (1 + z2 / n)
    return {"value": round(p, RATE_DIGITS), "low": round(center - half, RATE_DIGITS),
            "high": round(center + half, RATE_DIGITS)}


def size_bands(accounts: pd.DataFrame) -> Tuple[pd.Series, List[Payload]]:
    """Porte do cliente: quantis da receita anual entre os clientes cadastrados. Devolve o porte
    de cada cliente ("1" é o menor) e os limites de cada porte, em US$ milhões."""
    revenue = accounts["revenue"]
    known = revenue.dropna()
    if known.nunique() < 2:
        return pd.Series(None, index=accounts.index, dtype="object"), []
    codes_, edges = pd.qcut(known, policy.SIZE_QUANTILES, labels=False, retbins=True, duplicates="drop")
    keys = pd.Series(None, index=accounts.index, dtype="object")
    keys[known.index] = (codes_ + 1).astype(int).astype(str)
    bands = [{"key": str(i + 1), "low": round(float(edges[i]), 2), "high": round(float(edges[i + 1]), 2),
              "accounts": int((keys == str(i + 1)).sum())} for i in range(len(edges) - 1)]
    return keys, bands


def _accounts(dataset: Dataset) -> Tuple[pd.DataFrame, List[Payload]]:
    keys, bands = size_bands(dataset.accounts)
    table = dataset.accounts.assign(size=keys).rename(columns={"office_location": "location"})
    return table[["account", "sector", "location", "size"]], bands


def _enrich(frame: pd.DataFrame, accounts: pd.DataFrame) -> pd.DataFrame:
    return frame.merge(accounts, on="account", how="left", validate="m:1")


@dataclass(frozen=True)
class Frames:
    """O recorte já aplicado: fechadas até o as_of, abertas classificadas, as engajadas (todas as
    que têm data de engajamento até o as_of) e a equipe do recorte."""
    closed: pd.DataFrame
    open: pd.DataFrame
    engaged: pd.DataFrame
    teams: pd.DataFrame
    open_excluded_without_account: Optional[int]


def _apply(frame: pd.DataFrame, teams: pd.DataFrame, filters: Filters) -> Tuple[pd.DataFrame, pd.DataFrame]:
    frame, teams = views.scope(frame, teams, seller=filters.seller, manager=filters.manager, office=filters.office)
    for dimension in (codes.DIM_PRODUCT, *ACCOUNT_DIMENSIONS):
        value = filters.value(dimension)
        if value:
            frame = frame[frame[DIM_COLUMNS[dimension]] == value]
    return frame, teams


def frames(dataset: Dataset, ctx: triage.Context, filters: Filters, accounts: pd.DataFrame) -> Frames:
    everything = _enrich(dataset.opportunities, accounts)
    closed = everything[everything["deal_stage"].isin(policy.CLOSED_STAGES) & (everything["close_date"] <= ctx.as_of)]
    closed = closed.assign(won=closed["deal_stage"] == "Won",
                           cycle_days=(closed["close_date"] - closed["engage_date"]).dt.days)
    engaged = everything[everything["engage_date"] <= ctx.as_of]
    opened = _enrich(triage.classify(dataset.opportunities, ctx), accounts)

    closed, teams = _apply(closed, dataset.teams, filters)
    engaged, _ = _apply(engaged, dataset.teams, filters)
    excluded = None
    if filters.by_account_attribute:
        before, _ = _apply(opened, dataset.teams, filters.without_account_attributes())
        excluded = int(before["account"].isna().sum())
    opened, _ = _apply(opened, dataset.teams, filters)
    return Frames(closed, opened, engaged, teams, excluded)


def closed_metrics(closed: pd.DataFrame) -> Payload:
    """Métricas do histórico de um recorte de fechadas. Receita = Σ close_value das ganhas;
    ticket = receita ÷ ganhas, para que receita = fechadas × taxa × ticket."""
    won = closed[closed["won"]]
    n, k = len(closed), len(won)
    revenue = int(won["close_value"].sum())
    return {
        "closed": n,
        "won": k,
        "lost": n - k,
        "win_rate": wilson(k, n),
        "revenue": revenue,
        "won_without_value": int(won["close_value"].isna().sum()),
        "ticket": _ratio(revenue, k, 2),
        "revenue_per_closed": _ratio(revenue, n, 2),
        "median_won_cycle_days": _median_days(won["cycle_days"]),
        "median_lost_cycle_days": _median_days(closed.loc[~closed["won"], "cycle_days"]),
        "without_account": int(closed["account"].isna().sum()),
    }


def open_snapshot(f: Frames) -> Payload:
    """A carteira aberta do recorte, com os grupos da regra. Valor de tabela não é receita."""
    opened = f.open
    return {
        "summary": views.summary(opened),
        "list_value": int(opened["sales_price"].sum()),
        "without_list_price": int(opened["sales_price"].isna().sum()),
        "excluded_without_account": f.open_excluded_without_account,
        "empty": None if len(opened) else {"code": codes.NO_OPEN_FOR_FILTER, "params": {}},
    }


def chance_test(closed: pd.DataFrame, column: str) -> Payload:
    """A taxa de ganho difere entre os segmentos mais do que o acaso explicaria? Qui-quadrado nos
    segmentos com pelo menos MIN_CLOSED_PER_SEGMENT fechadas; α dividido pelas dimensões."""
    alpha = round(policy.CHANCE_ALPHA / len(codes.DIMENSIONS), 6)
    counts = closed.dropna(subset=[column]).groupby(column)["won"].agg(["sum", "size"])
    tested = counts[counts["size"] >= policy.MIN_CLOSED_PER_SEGMENT]
    rates = tested["sum"] / tested["size"]
    result = {"verdict": codes.CHANCE_TOO_FEW, "segments_tested": len(tested),
              "segments_small": int(len(counts) - len(tested)), "closed_tested": int(tested["size"].sum()),
              "min_win_rate": None, "max_win_rate": None, "p_value": None, "alpha": alpha}
    if len(tested) < 2:
        return result
    table = np.array([tested["sum"], tested["size"] - tested["sum"]], dtype=float)
    p_value = 1.0 if (table.sum(axis=1) == 0).any() else float(chi2_contingency(table, correction=False)[1])
    result.update(verdict=codes.CHANCE_BEYOND if p_value < alpha else codes.CHANCE_WITHIN,
                  min_win_rate=round(float(rates.min()), RATE_DIGITS),
                  max_win_rate=round(float(rates.max()), RATE_DIGITS), p_value=round(p_value, 4))
    return result


def revenue_drivers(segments: List[Payload]) -> Optional[Payload]:
    """Quanto da diferença de receita entre segmentos vem do volume (fechadas), da conversão
    (taxa de ganho) e do ticket: cov(log receita, log fator) ÷ var(log receita), soma 1.
    Só segmentos com receita; nulo com menos de MIN_SEGMENTS_FOR_DRIVERS."""
    rows = [s["history"] for s in segments if s["key"] is not None and s["history"]["revenue"] > 0]
    if len(rows) < policy.MIN_SEGMENTS_FOR_DRIVERS:
        return None
    revenue = np.log([r["revenue"] for r in rows])
    factors = {
        codes.DRIVER_VOLUME: np.log([r["closed"] for r in rows]),
        codes.DRIVER_CONVERSION: np.log([r["won"] / r["closed"] for r in rows]),
        codes.DRIVER_TICKET: np.log([r["revenue"] / r["won"] for r in rows]),
    }
    variance = float(np.var(revenue, ddof=1))
    if variance <= 0:
        return None
    shares = {d: float(np.cov(revenue, factors[d], ddof=1)[0, 1] / variance) for d in codes.DRIVERS}
    values = [r["revenue"] for r in rows]
    return {
        "segments_used": len(rows),
        "spread_ratio": round(max(values) / min(values), 2),
        "volume_share": round(shares[codes.DRIVER_VOLUME], RATE_DIGITS),
        "conversion_share": round(shares[codes.DRIVER_CONVERSION], RATE_DIGITS),
        "ticket_share": round(shares[codes.DRIVER_TICKET], RATE_DIGITS),
        "main": [d for d in codes.DRIVERS if shares[d] >= policy.DRIVER_MAIN_SHARE],
        "negligible": [d for d in codes.DRIVERS if abs(shares[d]) <= policy.DRIVER_NEGLIGIBLE_SHARE],
    }


def _keys(dimension: str, f: Frames) -> List[Optional[str]]:
    """Segmentos de uma dimensão. Pessoas: todo membro da equipe do recorte, inclusive sem
    fechadas, em ordem alfabética (AC-2.9). Demais: o que aparece nas fechadas ou nas abertas."""
    column = DIM_COLUMNS[dimension]
    present = pd.concat([f.closed[column], f.open[column]])
    keys = set(present.dropna())
    if dimension in codes.PEOPLE_DIMENSIONS:
        keys |= set(f.teams[column].dropna())
    ordered: List[Optional[str]] = sorted(keys)
    return ordered + ([None] if present.isna().any() else [])


def _profile(account: str, closed: pd.DataFrame, accounts: pd.DataFrame, catalog: int) -> Payload:
    row = accounts[accounts["account"] == account]
    won = closed[closed["won"]]
    attribute = (lambda c: None if row.empty or pd.isna(row[c].iloc[0]) else row[c].iloc[0])
    return {"sector": attribute("sector"), "location": attribute("location"), "size": attribute("size"),
            "products_bought": int(won["product"].nunique()), "products_total": catalog,
            "sellers": int(closed["sales_agent"].nunique())}


def breakdown(dimension: str, f: Frames, accounts: pd.DataFrame, catalog: int) -> Payload:
    column = DIM_COLUMNS[dimension]
    total_revenue = int(f.closed.loc[f.closed["won"], "close_value"].sum())
    open_counts = f.open[column].value_counts()
    segments = []
    for key in _keys(dimension, f):
        if key is None:
            closed = f.closed[f.closed[column].isna()]
            opened = int(f.open[column].isna().sum())
        else:
            closed = f.closed[f.closed[column] == key]
            opened = int(open_counts.get(key, 0))
        history = closed_metrics(closed)
        segments.append({
            "key": key,
            "history": history,
            "revenue_share": _ratio(history["revenue"], total_revenue),
            "open": opened,
            "profile": _profile(key, closed, accounts, catalog) if dimension == codes.DIM_ACCOUNT and key else None,
        })
    if dimension in codes.PEOPLE_DIMENSIONS:
        order = codes.ORDER_ALPHABETICAL
    else:
        order = codes.ORDER_REVENUE_DESC
        segments.sort(key=lambda s: (s["key"] is None, -s["history"]["revenue"], s["key"] or ""))
    return {"dimension": dimension, "order": order, "segments": segments,
            "chance": chance_test(f.closed, column), "drivers": revenue_drivers(segments)}


def seller_product_matrix(f: Frames, products: List[str]) -> Payload:
    """O mix de cada vendedor: fechadas por produto e a fatia de cada produto nas fechadas dele.
    Sem taxa por célula: com ~30 fechadas por célula, a diferença não se repete no tempo."""
    columns = [p for p in products if p in set(f.closed["product"].dropna())]
    counts = f.closed.groupby(["sales_agent", "product"]).size()
    rows = []
    for seller in sorted(set(f.teams["sales_agent"]) | set(f.closed["sales_agent"])):
        total = int((f.closed["sales_agent"] == seller).sum())
        cells = [{"product": p, "closed": int(counts.get((seller, p), 0)),
                  "mix_share": _ratio(int(counts.get((seller, p), 0)), total)} for p in columns]
        rows.append({"seller": seller, "closed": total, "cells": cells})
    return {"products": columns, "rows": rows}


# Cruzamentos de "quem compra o quê e quem atende quem": linhas, colunas e a coluna de cada um nas fechadas.
# O cliente traz setor e país da sede; o vendedor traz o escritório. Sem taxa por célula (a mesma regra da matriz).
CROSSTABS = (
    ("account_product", "account", "product", "account", "product"),
    ("sector_product", "sector", "product", "sector", "product"),
    ("seller_sector", "seller", "sector", "sales_agent", "sector"),
    ("sector_office", "sector", "office", "sector", "regional_office"),
    ("location_office", "location", "office", "location", "regional_office"),
)


def crosstab(f: Frames, products: List[str], spec: Tuple[str, str, str, str, str]) -> Payload:
    """Fechadas por linha e coluna, com a fatia de cada coluna nas fechadas da linha. Vendedores: todos da equipe do
    recorte, em ordem alfabética (nunca um ranking); o resto, do que mais fechou ao que menos fechou."""
    ident, row_dim, col_dim, row_col, col_col = spec
    closed = f.closed.dropna(subset=[row_col, col_col])
    if col_dim == codes.DIM_PRODUCT:
        columns = [p for p in products if p in set(closed[col_col])]
    else:
        columns = sorted(set(closed[col_col]))
    counts = closed.groupby([row_col, col_col]).size()
    totals = closed.groupby(row_col).size()
    keys = set(totals.index)
    people = row_dim == codes.DIM_SELLER
    if people:
        keys |= set(f.teams["sales_agent"])
    ordered = sorted(keys) if people else sorted(keys, key=lambda k: (-int(totals[k]), k))
    rows = []
    for key in ordered:
        total = int(totals.get(key, 0))
        cells = [{"key": c, "closed": int(counts.get((key, c), 0)),
                  "share": _ratio(int(counts.get((key, c), 0)), total)} for c in columns]
        rows.append({"key": key, "closed": total, "cells": cells})
    return {"id": ident, "row_dimension": row_dim, "column_dimension": col_dim, "columns": columns, "rows": rows}


def cycle_bands(f: Frames, ctx: triage.Context) -> List[Payload]:
    """Fechadas por faixa de ciclo: as bordas fixas abaixo de L1, depois L1 e L2 do as_of (os mesmos
    limites da regra), para a última faixa ser exatamente a de Acompanhar."""
    edges = sorted({e for e in policy.CYCLE_BAND_EDGES if e < ctx.won_cycle_limit_days}
                   | {ctx.won_cycle_limit_days, ctx.cycle_limit_days})
    cycles = f.closed.dropna(subset=["cycle_days"])
    bands, low = [], 0
    for high in edges:
        rows = cycles[(cycles["cycle_days"] >= low) & (cycles["cycle_days"] <= high)]
        won = int(rows["won"].sum())
        bands.append({"low": low, "high": high, "won": won, "lost": len(rows) - won,
                      "win_rate": _ratio(won, len(rows))})
        low = high + 1
    return bands


def _month_range(first: pd.Timestamp, last: pd.Timestamp) -> List[pd.Period]:
    return list(pd.period_range(first.to_period("M"), last.to_period("M"), freq="M"))


def monthly(f: Frames, everything_dates: Tuple[pd.Timestamp, pd.Timestamp]) -> List[Payload]:
    """Novas negociações por mês de engajamento e fechamentos por mês, do primeiro ao último mês com dados."""
    first, last = everything_dates
    engaged = f.engaged["engage_date"].dt.to_period("M").value_counts()
    closes = f.closed.assign(month=f.closed["close_date"].dt.to_period("M")).groupby(["month", "won"]).size()
    return [{"month": str(m), "engaged": int(engaged.get(m, 0)), "won": int(closes.get((m, True), 0)),
             "lost": int(closes.get((m, False), 0))} for m in _month_range(first, last)]


# Diagnósticos do processo: cada um só aparece quando a condição vale no recorte.
def _diag(code: str, **params: Any) -> Payload:
    return {"code": code, "params": params}


def _inflow_drop(f: Frames, ctx: triage.Context, first: pd.Timestamp) -> Optional[Payload]:
    last_complete = (ctx.as_of + pd.Timedelta(days=1)).to_period("M") - 1
    months = [m for m in _month_range(first, last_complete.to_timestamp()) if m <= last_complete]
    needed = policy.INFLOW_RECENT_MONTHS + policy.INFLOW_BASE_MONTHS
    if len(months) < needed:
        return None
    counts = f.engaged["engage_date"].dt.to_period("M").value_counts()
    recent = months[-policy.INFLOW_RECENT_MONTHS:]
    base = months[-needed:-policy.INFLOW_RECENT_MONTHS]
    recent_mean = sum(int(counts.get(m, 0)) for m in recent) / len(recent)
    base_mean = sum(int(counts.get(m, 0)) for m in base) / len(base)
    if not base_mean or recent_mean >= policy.INFLOW_DROP_RATIO * base_mean:
        return None
    return _diag(codes.DIAG_ENGAGEMENT_INFLOW_DROP,
                 recent=[{"month": str(m), "engaged": int(counts.get(m, 0))} for m in recent],
                 base_average=round(base_mean, 1), base_first_month=str(base[0]), base_last_month=str(base[-1]))


def _quarter_end(closed: pd.DataFrame) -> Optional[Payload]:
    at_end = closed["close_date"].dt.month.isin(QUARTER_END_MONTHS)
    sides = [closed[at_end], closed[~at_end]]
    if min(len(s) for s in sides) < policy.MIN_CLOSED_PER_SEGMENT:
        return None
    table = np.array([[s["won"].sum(), (~s["won"]).sum()] for s in sides], dtype=float)
    if (table.sum(axis=0) == 0).any() or chi2_contingency(table, correction=False)[1] >= policy.CHANCE_ALPHA:
        return None
    return _diag(codes.DIAG_QUARTER_END_OUTCOME_MIX,
                 quarter_end_closed=len(sides[0]), quarter_end_win_rate=_ratio(sides[0]["won"].sum(), len(sides[0])),
                 other_closed=len(sides[1]), other_win_rate=_ratio(sides[1]["won"].sum(), len(sides[1])))


def diagnostics(dataset: Dataset, f: Frames, ctx: triage.Context, first: pd.Timestamp) -> List[Payload]:
    found: List[Optional[Payload]] = []
    summary = views.summary(f.open)
    engaging = int((f.open["deal_stage"] == "Engaging").sum())
    beyond = summary[policy.REVISAR]
    found.append(_diag(codes.DIAG_ENGAGING_BEYOND_LONGEST_CYCLE, group=policy.REVISAR, count=beyond,
                       engaging=engaging, share=_ratio(beyond, engaging), cycle_limit_days=ctx.cycle_limit_days)
                 if beyond else None)
    without = summary["without_account"]
    found.append(_diag(codes.DIAG_OPEN_WITHOUT_ACCOUNT, count=without, open=summary["total"],
                       share=_ratio(without, summary["total"]),
                       closed_without_account=int(f.closed["account"].isna().sum()), closed=len(f.closed))
                 if without else None)
    prospecting = f.open[f.open["deal_stage"] == "Prospecting"]
    undated = int(prospecting["engage_date"].isna().sum())
    found.append(_diag(codes.DIAG_PROSPECTING_WITHOUT_ENGAGE_DATE, group=policy.QUALIFICAR, count=undated,
                       prospecting=len(prospecting))
                 if undated else None)
    idle = sorted(set(f.teams["sales_agent"]) - set(dataset.opportunities["sales_agent"]))
    found.append(_diag(codes.DIAG_SELLERS_WITHOUT_OPPORTUNITIES, count=len(idle), team=len(f.teams), sellers=idle)
                 if idle else None)
    found.append(_quarter_end(f.closed))
    found.append(_inflow_drop(f, ctx, first))
    per_account = f.closed.dropna(subset=["account"]).groupby("account")["sales_agent"].nunique()
    median = _median_days(per_account)
    found.append(_diag(codes.DIAG_ACCOUNTS_SHARED_BY_SELLERS, median_sellers=median,
                       max_sellers=int(per_account.max()), accounts=len(per_account))
                 if median is not None and median >= policy.SHARED_ACCOUNT_MIN_SELLERS else None)
    return [d for d in found if d]


def _concentration(b: Payload) -> Optional[Payload]:
    segments = [s for s in b["segments"] if s["key"] is not None and s["history"]["revenue"] > 0]
    total = sum(s["history"]["revenue"] for s in segments)
    if len(segments) < 2 or not total:
        return None
    ranked = sorted(segments, key=lambda s: -s["history"]["revenue"])
    running = 0
    for top, s in enumerate(ranked, start=1):
        running += s["history"]["revenue"]
        if running / total >= policy.CONCENTRATION_SHARE:
            break
    if top > policy.CONCENTRATION_MAX_FRACTION * len(segments):
        return None
    return _diag(codes.FIND_REVENUE_CONCENTRATED, dimension=b["dimension"], top=top, of=len(segments),
                 share=_ratio(running, total), keys=[s["key"] for s in ranked[:top]])


def _coverage(f: Frames, products: List[str], filters: Filters) -> Optional[Payload]:
    won = f.closed[f.closed["won"]].dropna(subset=["account"])
    if filters.product or len(products) < 2 or won.empty:
        return None
    bought = won.groupby("account")["product"].apply(set)
    counts = bought.apply(len).value_counts()
    missing = pd.Series([p for s in bought for p in products if p not in s]).value_counts()
    return _diag(codes.FIND_ACCOUNT_PRODUCT_COVERAGE, accounts=len(bought), products=len(products),
                 distribution=[{"bought": int(k), "accounts": int(counts[k])} for k in sorted(counts.index)],
                 most_missing=None if missing.empty else str(missing.index[0]),
                 most_missing_accounts=0 if missing.empty else int(missing.iloc[0]))


def findings(f: Frames, breakdowns: List[Payload], history: Payload, products: List[str],
             filters: Filters) -> List[Payload]:
    by_dim = {b["dimension"]: b for b in breakdowns}
    found: List[Optional[Payload]] = []
    within = [d for d in codes.DIMENSIONS if by_dim[d]["chance"]["verdict"] == codes.CHANCE_WITHIN]
    found.append(_diag(codes.FIND_WIN_RATE_WITHIN_CHANCE, dimensions=within, closed=history["closed"])
                 if within else None)
    found += [_diag(codes.FIND_WIN_RATE_BEYOND_CHANCE, dimension=d, chance=by_dim[d]["chance"])
              for d in codes.DIMENSIONS if by_dim[d]["chance"]["verdict"] == codes.CHANCE_BEYOND]
    found += [_concentration(by_dim[d]) for d in CONCENTRATION_DIMENSIONS]
    found += [_diag(codes.FIND_REVENUE_GAP_DRIVERS, dimension=d, drivers=by_dim[d]["drivers"])
              for d in DRIVER_FINDING_DIMENSIONS if by_dim[d]["drivers"]]
    lost_median, won_median = history["median_lost_cycle_days"], history["median_won_cycle_days"]
    found.append(_diag(codes.FIND_FAST_LOSSES, median_lost_cycle_days=lost_median,
                       median_won_cycle_days=won_median, lost=history["lost"], won=history["won"])
                 if lost_median is not None and won_median is not None and lost_median < won_median else None)
    found.append(_coverage(f, products, filters))
    return [x for x in found if x]


def _catalog(dataset: Dataset) -> List[str]:
    """Produtos negociados, do maior preço de tabela para o menor (a ordem das faixas)."""
    prices = dataset.opportunities.dropna(subset=["product"]).groupby("product")["sales_price"].max()
    return sorted(prices.index, key=lambda p: (-(0 if pd.isna(prices[p]) else int(prices[p])), p))


def _options(dataset: Dataset, accounts: pd.DataFrame, bands: List[Payload]) -> Payload:
    table = accounts.sort_values("account")
    return {
        "products": sorted(dataset.opportunities["product"].dropna().unique()),
        "sectors": sorted(accounts["sector"].dropna().unique()),
        "accounts": [{"name": r.account, "sector": None if pd.isna(r.sector) else r.sector,
                      "location": None if pd.isna(r.location) else r.location,
                      "size": None if pd.isna(r.size) else r.size} for r in table.itertuples(index=False)],
        "sizes": bands,
    }


def _dates(dataset: Dataset, ctx: triage.Context) -> Tuple[pd.Timestamp, pd.Timestamp]:
    frame = dataset.opportunities
    stamps = pd.concat([frame["engage_date"], frame["close_date"]]).dropna()
    stamps = stamps[stamps <= ctx.as_of]
    return stamps.min(), stamps.max()


def payload(dataset: Dataset, filters: Optional[Filters] = None,
            as_of: Optional[triage.DateLike] = None) -> Payload:
    """A página inteira para um recorte: histórico, carteira aberta, diagnósticos, descobertas,
    os sete recortes, o mix vendedor × produto, as faixas de ciclo e o ritmo mensal."""
    filters = filters or Filters()
    ctx = views.context(dataset, as_of)
    accounts, bands = _accounts(dataset)
    f = frames(dataset, ctx, filters, accounts)
    products = _catalog(dataset)
    first, last = _dates(dataset, ctx)
    history = closed_metrics(f.closed)
    breakdowns = [breakdown(d, f, accounts, len(products)) for d in codes.DIMENSIONS]
    return {
        "meta": views.meta(dataset, ctx),
        "ordering": views.ordering(),
        "filter": asdict(filters),
        "options": _options(dataset, accounts, bands),
        "history": history,
        "history_empty": None if len(f.closed) else {"code": codes.NO_CLOSED_FOR_FILTER, "params": {}},
        "open": open_snapshot(f),
        "diagnostics": diagnostics(dataset, f, ctx, first),
        "findings": findings(f, breakdowns, history, products, filters),
        "breakdowns": breakdowns,
        "matrix": seller_product_matrix(f, products),
        "crosstabs": [crosstab(f, products, spec) for spec in CROSSTABS],
        "cycle_bands": cycle_bands(f, ctx),
        "monthly": monthly(f, (first, last)),
    }


def _invalid(name: str, value: Optional[str], allowed: List[str]) -> PolicyError:
    accepted = f"Valores aceitos: {', '.join(allowed)}." if allowed else "Só vale com outcome=open."
    return PolicyError(f"Parâmetro {name} inválido: '{value or ''}'. {accepted}",
                       code=codes.INVALID_PARAMETER, name=name, value=value or "", allowed=allowed)


def _iso(value: Any) -> Optional[str]:
    return None if pd.isna(value) else value.date().isoformat()


def _int(value: Any) -> Optional[int]:
    return None if pd.isna(value) else int(value)


def _text(value: Any) -> Optional[str]:
    return None if pd.isna(value) else str(value)


def _deal(row: Dict[str, Any], is_open: bool) -> Payload:
    return {
        "opportunity_id": row["opportunity_id"],
        "sales_agent": row["sales_agent"],
        "manager": _text(row["manager"]),
        "office": _text(row["regional_office"]),
        "product": _text(row["product"]),
        "account": _text(row["account"]),
        "sector": _text(row["sector"]),
        "deal_stage": row["deal_stage"],
        "engage_date": _iso(row["engage_date"]),
        "close_date": None if is_open else _iso(row["close_date"]),
        "close_value": None if is_open else _int(row["close_value"]),
        "sales_price": _int(row["sales_price"]),
        "cycle_days": None if is_open else _int(row["cycle_days"]),
        "age_days": _int(row["age_days"]) if is_open else None,
        "group": row["state"] if is_open else None,
    }


def deals(dataset: Dataset, filters: Optional[Filters] = None, outcome: Optional[str] = None,
          group: Optional[str] = None, as_of: Optional[triage.DateLike] = None) -> Payload:
    """As negociações por trás de um número da página: o mesmo recorte, um desfecho e, nas
    abertas, opcionalmente um grupo. Abertas na ordem da regra; fechadas da mais recente para a
    mais antiga."""
    filters = filters or Filters()
    if outcome not in codes.OUTCOMES:
        raise _invalid("outcome", outcome, list(codes.OUTCOMES))
    if group and (outcome != codes.OUTCOME_OPEN or group not in policy.STATES):
        raise _invalid("group", group, list(policy.STATES) if outcome == codes.OUTCOME_OPEN else [])
    ctx = views.context(dataset, as_of)
    accounts, _ = _accounts(dataset)
    f = frames(dataset, ctx, filters, accounts)
    if outcome == codes.OUTCOME_OPEN:
        rows = triage.order(f.open)
        rows = rows[rows["state"] == group] if group else rows
    else:
        rows = f.closed[f.closed["won"] == (outcome == codes.OUTCOME_WON)]
        rows = rows.sort_values(["close_date", "opportunity_id"], ascending=[False, True], kind="mergesort")
    is_open = outcome == codes.OUTCOME_OPEN
    items = [_deal(row, is_open) for row in rows.to_dict("records")]
    return {
        "meta": views.meta(dataset, ctx),
        "filter": asdict(filters),
        "outcome": outcome,
        "group": group or None,
        "total": len(items),
        "deals": items,
        "empty": None if items else {"code": codes.NO_DEALS_FOR_FILTER, "params": {}},
    }
