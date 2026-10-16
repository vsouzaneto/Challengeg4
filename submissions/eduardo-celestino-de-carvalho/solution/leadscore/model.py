"""Experimento temporal de potencial, separado da prioridade operacional.

As entradas permitidas são produto e vendedor, ambos presentes nos abertos.
O resultado final só é usado como rótulo ou métrica, nunca como feature.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from itertools import groupby
from statistics import mean

from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import make_pipeline

from .data import Dataset, Opportunity


TRAIN_END = date(2017, 6, 30)
VALIDATION_START = date(2017, 7, 1)
VALIDATION_END = date(2017, 8, 31)
VALIDATION_LABEL_END = date(2017, 9, 30)
TEST_START = date(2017, 10, 1)
TEST_END = date(2017, 11, 30)
TEST_LABEL_END = date(2017, 12, 30)
HORIZON_DAYS = 30
ALLOWED_FEATURES = frozenset({"product", "sales_agent"})


def known_outcomes(dataset: Dataset, cutoff: date) -> list[Opportunity]:
    """Engaging com 30 dias completos e desfecho observado nesse prazo."""
    return [o for o in dataset.opportunities
            if o.engage_date is not None
            and o.engage_date + timedelta(days=HORIZON_DAYS) <= cutoff
            and o.close_date is not None
            and o.close_date <= o.engage_date + timedelta(days=HORIZON_DAYS)]


def resolved_cohort(dataset: Dataset, start: date, end: date,
                    observed_through: date) -> list[Opportunity]:
    """Novos Engaging resolvidos em até 30 dias, com janela inteira observada."""
    if observed_through < end + timedelta(days=HORIZON_DAYS):
        raise ValueError("Janela de resultados incompleta para o último negócio")
    return [o for o in dataset.opportunities
            if o.engage_date is not None and start <= o.engage_date <= end
            and o.close_date is not None
            and o.close_date <= o.engage_date + timedelta(days=HORIZON_DAYS)]


def features(opportunity: Opportunity, names: frozenset[str]) -> dict[str, str]:
    if not names or not names <= ALLOWED_FEATURES:
        raise ValueError(f"Features não permitidas: {sorted(names - ALLOWED_FEATURES)}")
    return {name: getattr(opportunity, name) for name in sorted(names)}


def labels(rows: list[Opportunity]) -> list[int]:
    if any(o.deal_stage not in {"Won", "Lost"} for o in rows):
        raise ValueError("Rótulo de negócio aberto não é conhecido")
    return [int(o.deal_stage == "Won") for o in rows]


def product_rate(train: list[Opportunity], score: list[Opportunity], strength: int = 20) -> list[float]:
    """Taxa histórica por produto suavizada em direção à média do treino."""
    target = labels(train)
    global_rate = mean(target)
    grouped: dict[str, list[int]] = defaultdict(list)
    for opportunity, won in zip(train, target):
        grouped[opportunity.product].append(won)
    return [(sum(grouped[o.product]) + strength * global_rate)
            / (len(grouped[o.product]) + strength) for o in score]


def logistic_rate(train: list[Opportunity], score: list[Opportunity], names: frozenset[str]) -> list[float]:
    pipeline = make_pipeline(DictVectorizer(), LogisticRegression(C=1.0, max_iter=1000))
    pipeline.fit([features(o, names) for o in train], labels(train))
    return [float(value) for value in pipeline.predict_proba([features(o, names) for o in score])[:, 1]]


def evaluate(rows: list[Opportunity], probabilities: list[float]) -> dict:
    """Métricas de desfecho e fila curta de cinco negócios por vendedor."""
    if len(rows) != len(probabilities) or not rows:
        raise ValueError("Avaliação requer uma previsão por oportunidade")
    y = labels(rows)
    portfolios: dict[str, list[int]] = defaultdict(list)
    for index, opportunity in enumerate(rows):
        portfolios[opportunity.sales_agent].append(index)
    # Valores iguais não contêm informação para desempatar. Distribuir
    # frações da última posição evita ganhar desempenho pela ordem do CSV/ID.
    selected: dict[int, float] = {}
    for indices in portfolios.values():
        remaining = min(5, len(indices))
        ordered = sorted(indices, key=lambda i: -probabilities[i])
        for _, group in groupby(ordered, key=lambda i: probabilities[i]):
            tied = list(group)
            if remaining <= 0:
                break
            weight = min(1.0, remaining / len(tied))
            selected.update({index: weight for index in tied})
            remaining -= min(remaining, len(tied))
    revenue = sum(float(rows[i].close_value or 0) * weight
                  for i, weight in selected.items())
    total_revenue = sum(float(o.close_value or 0) for o in rows)
    chosen_n = sum(selected.values())
    chosen_wins = sum(y[i] * weight for i, weight in selected.items())
    return {
        "n": len(rows), "won": sum(y), "win_rate": round(mean(y), 4),
        "agents": len(portfolios), "selected_at_5": round(chosen_n, 4),
        "wins_at_5": round(chosen_wins, 4),
        "win_rate_at_5": round(chosen_wins / chosen_n, 4),
        "revenue_at_5": round(revenue, 2),
        "revenue_share_at_5": round(revenue / total_revenue, 4) if total_revenue else None,
        "roc_auc": round(float(roc_auc_score(y, probabilities)), 4),
        "brier": round(float(brier_score_loss(y, probabilities)), 4),
        "log_loss": round(float(log_loss(y, probabilities)), 4),
    }


def score_methods(dataset: Dataset, train: list[Opportunity], cohort: list[Opportunity]) -> dict:
    if not train or not cohort:
        raise ValueError("Treino e coorte de avaliação devem conter negócios")
    price = [float(dataset.products[o.product].sales_price) for o in cohort]
    top_price = max(price)
    candidates = {
        "taxa_global": [mean(labels(train))] * len(cohort),
        "preco_catalogo": [value / top_price for value in price],
        "taxa_produto_suavizada": product_rate(train, cohort),
        "logistica_produto": logistic_rate(train, cohort, frozenset({"product"})),
        "logistica_produto_vendedor": logistic_rate(
            train, cohort, frozenset({"product", "sales_agent"})),
    }
    # A comparação de receita usa o mesmo tamanho de fila e o valor realizado
    # apenas como desfecho. A ordenação "preço" não é uma probabilidade.
    results = {name: evaluate(cohort, predictions)
               for name, predictions in candidates.items()}
    results["preco_catalogo"].pop("brier")
    results["preco_catalogo"].pop("log_loss")
    return results
