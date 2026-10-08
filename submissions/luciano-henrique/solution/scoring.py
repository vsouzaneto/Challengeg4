"""Heurística de priorização. Nenhum score é probabilidade calibrada."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from math import isfinite

from data import Dataset

SHRINKAGE = 50
REFERENCE_DATE = date(2017, 12, 31)


@dataclass(frozen=True)
class GroupEvidence:
    count: int
    wins: int
    adjusted_rate: float


@dataclass
class ScoringResult:
    opportunities: list[dict]
    historical_count: int
    historical_win_rate: float
    reference_date: date
    watchlist_price_threshold: float | None

    @property
    def confidence_counts(self):
        counts = Counter(row["confidence"] for row in self.opportunities)
        return {label: counts[label] for label in ("Alta", "Média", "Baixa")}


def historical_evidence(rows, field, baseline):
    groups = defaultdict(lambda: [0, 0])
    for row in rows:
        groups[row[field]][0] += 1
        groups[row[field]][1] += row["deal_stage"] == "Won"
    return {
        key: GroupEvidence(n, wins, (wins + SHRINKAGE * baseline) / (n + SHRINKAGE))
        for key, (n, wins) in groups.items()
    }


def confidence(n_product: int, n_sales_agent: int) -> str:
    support = min(n_product, n_sales_agent)
    return "Alta" if support >= 200 else "Média" if support >= 50 else "Baixa"


def percentile(values, fraction):
    """Percentil com interpolação linear, igual à análise exploratória."""
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def assign_priority_scores(rows):
    """Percentil global com posição média dos empates, sem arredondar."""
    ordered = sorted(rows, key=lambda row: row["balanced_priority"])
    total = len(ordered)
    start = 0
    while start < total:
        end = start + 1
        while end < total and ordered[end]["balanced_priority"] == ordered[start]["balanced_priority"]:
            end += 1
        # Posição média em base zero equivale a (rank médio - 1).
        score = 50.0 if total == 1 else 100 * ((start + end - 1) / 2) / (total - 1)
        for row in ordered[start:end]:
            row["priority_score"] = score
        start = end


def score_open_opportunities(dataset: Dataset, reference_date: date = REFERENCE_DATE) -> ScoringResult:
    """Pontua o snapshot aberto fornecido; não reconstrói snapshots passados.

    close_date somente controla disponibilidade do resultado histórico.
    close_value nunca é lido. As features são exclusivamente produto,
    vendedor e preço de catálogo. Cadastros não têm versões temporais.
    """
    history = []
    for row in dataset.closed_opportunities:
        if not row["close_date"]:
            raise ValueError(f"Encerrada sem close_date: {row['opportunity_id']}")
        closed_on = date.fromisoformat(row["close_date"])
        engaged_on = date.fromisoformat(row["engage_date"])
        if closed_on < engaged_on:
            raise ValueError(f"Fechamento anterior ao engajamento: {row['opportunity_id']}")
        if closed_on <= reference_date:
            history.append(row)
    if not history:
        raise ValueError("Sem resultados históricos disponíveis; não é possível estimar a taxa geral.")
    baseline = sum(row["deal_stage"] == "Won" for row in history) / len(history)
    products = historical_evidence(history, "product", baseline)
    agents = historical_evidence(history, "sales_agent", baseline)
    fallback = GroupEvidence(0, 0, baseline)
    scored = []
    for row in dataset.open_opportunities:
        if row["engage_date"] and date.fromisoformat(row["engage_date"]) > reference_date:
            raise ValueError(f"Aberta com engajamento posterior à referência: {row['opportunity_id']}")
        product = products.get(row["product"], fallback)
        agent = agents.get(row["sales_agent"], fallback)
        price = float(dataset.products[row["product"]]["sales_price"])
        if not isfinite(price) or price < 0:
            raise ValueError(f"Preço inválido: {row['product']}")
        fit = (product.adjusted_rate + agent.adjusted_rate) / 2
        # Allowlist explícita: nenhum resultado de fechamento é exposto como feature.
        scored.append({
            "opportunity_id": row["opportunity_id"],
            "deal_stage": row["deal_stage"],
            "product": row["product"],
            "sales_agent": row["sales_agent"],
            "account": row["account"] or None,
            "sales_price": price,
            "product_adjusted_rate": product.adjusted_rate,
            "sales_agent_adjusted_rate": agent.adjusted_rate,
            "historical_fit": fit,
            "balanced_priority": price * fit,
            "n_product": product.count,
            "n_sales_agent": agent.count,
            "confidence": confidence(product.count, agent.count),
        })
    threshold = percentile([row["sales_price"] for row in scored], 0.8) if scored else None
    assign_priority_scores(scored)
    for row in scored:
        row["watchlist"] = row["sales_price"] >= threshold and row["confidence"] == "Baixa"
    # O ID apenas estabiliza a exibição entre empates; não muda o score.
    scored.sort(key=lambda row: (-row["balanced_priority"], row["opportunity_id"]))
    return ScoringResult(scored, len(history), baseline, reference_date, threshold)
