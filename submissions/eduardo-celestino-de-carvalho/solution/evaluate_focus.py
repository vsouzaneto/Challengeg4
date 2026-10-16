"""Backtest exploratório da regra do Lead Kanban contra a regra de atenção anterior.

Em cada data de corte, reconstrói os negócios que estavam em ``Engaging``
(entrada até o corte e sem fechamento até o corte), calcula a referência de
ciclo só com negócios concluídos até o corte e observa o desfecho até
31/12/2017. ``Prospecting`` não tem datas e fica fora. O teste do G2 já foi
visto, então o resultado é exploratório, não uma validação independente.

Dois controles de robustez acompanham o resultado: o prazo trocado por
percentis dos ciclos (p99, p95, p90) e o desempate comparado separadamente
nos três primeiros cortes e nos dois últimos. Todos os cortes já tinham sido
vistos, então a separação mostra estabilidade, não validação independente.

    python evaluate_focus.py --output experiments/g3-focus-backtest.json
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import replace
from datetime import date
from decimal import Decimal
from pathlib import Path
import argparse
import json
import math
import random

from leadscore.data import ARCHIVE_NAME, Dataset, download_archive, load_dataset
from leadscore.priority import LANES, PriorityItem, build_reference, score_opportunity


CUTOFFS = (date(2017, 5, 31), date(2017, 6, 30), date(2017, 7, 31),
           date(2017, 8, 31), date(2017, 9, 30))
END_OF_DATA = date(2017, 12, 31)
TOP_N = 5
SELECTION_CUTOFFS = 3      # desempate comparado nos 3 primeiros cortes e, à parte, nos 2 últimos
THRESHOLDS = (("max", None), ("p99", 0.99), ("p95", 0.95), ("p90", 0.90))
BOOTSTRAP_REPS = 5000


def previous_attention_score(dataset: Dataset, item: PriorityItem) -> int:
    """Regra da primeira versão do G3, restrita a Engaging (etapa + preço + idade + conta)."""
    prices = sorted({product.sales_price for product in dataset.products.values()})
    share = (prices.index(item.catalog_price) + 1) / len(prices)
    value = 10 if share <= 1 / 3 else 20 if share <= 2 / 3 else 30
    days = item.days_in_engaging
    age = 20 if days >= 90 else 15 if days >= 30 else 5
    return 35 + value + age + (5 if item.account_missing else 0)


def open_at(dataset: Dataset, cutoff: date):
    """Pares (negócio como estava no corte, desfecho real) para Engaging no corte."""
    for deal in dataset.opportunities:
        if deal.engage_date is None or deal.engage_date > cutoff:
            continue
        if deal.close_date is not None and deal.close_date <= cutoff:
            continue
        as_seen = replace(deal, deal_stage="Engaging", close_date=None, close_value=None)
        yield as_seen, deal


def survival_rates(dataset: Dataset, cutoff: date, starts=(0, 15, 30, 60, 90, 120)):
    """Variante descartada: taxa de ganho entre concluídos que passaram de N dias."""
    cycles = [((deal.close_date - deal.engage_date).days, deal.deal_stage == "Won")
              for deal in dataset.opportunities
              if deal.close_date is not None and deal.close_date <= cutoff]
    rates = {}
    for start in starts:
        alive = [won for days, won in cycles if days > start]
        rates[start] = Decimal(sum(alive)) / Decimal(len(alive)) if len(alive) >= 30 else None

    def rate(days: int) -> Decimal:
        usable = [start for start in starts if start <= days and rates[start] is not None]
        return rates[max(usable)]
    return rate


def outcome(deal) -> str:
    return {"Won": "won", "Lost": "lost"}.get(deal.deal_stage, "open")


def quantile_days(dataset: Dataset, cutoff: date, share: float) -> int:
    """Percentil (posto mais próximo) dos ciclos concluídos até o corte."""
    cycles = sorted((deal.close_date - deal.engage_date).days for deal in dataset.opportunities
                    if deal.close_date is not None and deal.close_date <= cutoff)
    return cycles[max(0, math.ceil(share * len(cycles)) - 1)]


def picks(pairs, key):
    """Top-N de um vendedor como (item, desfecho, peso); empates na vaga de corte dividem a vaga (como no G2)."""
    groups = defaultdict(list)
    for pair in pairs:
        groups[key(pair)].append(pair)
    remaining = TOP_N
    for group_key in sorted(groups):
        if remaining <= 0:
            break
        group = groups[group_key]
        weight = min(1.0, remaining / len(group))
        remaining -= len(group)
        for item, real in group:
            yield item, real, weight


def won_revenue(real, weight: float) -> float:
    return weight * float(real.close_value) if real.deal_stage == "Won" else 0.0


def top(by_agent, key) -> dict:
    """Totais do top-N por vendedor."""
    totals = defaultdict(float)
    for pairs in by_agent.values():
        for item, real, weight in picks(pairs, key):
            totals["slots"] += weight
            totals[outcome(real) if outcome(real) != "open" else "still_open"] += weight
            totals["beyond_cycle_slots"] += weight * (item.lane == "encerrar")
            totals["won_revenue"] += won_revenue(real, weight)
    return {name: round(totals[name], 2) for name in
            ("slots", "won", "lost", "still_open", "won_revenue", "beyond_cycle_slots")}


def revenue_by_agent(by_agent, key) -> dict[str, float]:
    """Receita ganha no top-N de cada vendedor: a unidade do bootstrap."""
    return {agent: sum(won_revenue(real, weight) for _, real, weight in picks(pairs, key))
            for agent, pairs in by_agent.items()}


def bootstrap(units: list[tuple[float, float]], reps: int = BOOTSTRAP_REPS, seed: int = 2017) -> dict:
    """Bootstrap pareado sobre pares (vendedor, data): ganho relativo de A sobre B, com IC de 95%."""
    rng = random.Random(seed)
    total_a, total_b = sum(a for a, _ in units), sum(b for _, b in units)
    lifts = []
    for _ in range(reps):
        sample = [units[rng.randrange(len(units))] for _ in units]
        sa, sb = sum(a for a, _ in sample), sum(b for _, b in sample)
        lifts.append(sa / sb - 1 if sb else 0.0)
    lifts.sort()
    return {
        "units": len(units), "reps": reps,
        "revenue_a": round(total_a, 2), "revenue_b": round(total_b, 2),
        "lift": round(total_a / total_b - 1, 4),
        "ci95": [round(lifts[int(0.025 * reps)], 4), round(lifts[int(0.975 * reps) - 1], 4)],
        "share_reps_a_better": round(sum(l > 0 for l in lifts) / reps, 4),
    }


LANE_RANK = {lane: index for index, lane in enumerate(LANES)}


def focus_rule(pair, recent_first: bool = True):
    item = pair[0]
    days = item.days_in_engaging
    tie = days if (item.lane == "negociar") == recent_first else -days
    return (LANE_RANK[item.lane], -item.catalog_price, tie)


def score_rows(dataset: Dataset, cutoff: date, reference):
    return [(score_opportunity(dataset, as_seen, reference, cutoff), real)
            for as_seen, real in open_at(dataset, cutoff)]


def group_by_agent(rows):
    by_agent = defaultdict(list)
    for item, real in rows:
        by_agent[item.opportunity.sales_agent].append((item, real))
    return by_agent


def robustness(dataset: Dataset, cutoff: date, reference, by_agent) -> dict:
    """Prazo por percentil e desempate alternativo, com a mesma métrica top-N."""
    thresholds = {}
    for name, share in THRESHOLDS:
        limit = reference.max_cycle_days if share is None else quantile_days(dataset, cutoff, share)
        rows = score_rows(dataset, cutoff, replace(reference, max_cycle_days=limit))
        beyond = [real for item, real in rows if item.lane == "encerrar"]
        thresholds[name] = {
            "limit_days": limit,
            "beyond_deals": len(beyond),
            "beyond_won": sum(real.deal_stage == "Won" for real in beyond),
            "beyond_won_revenue": int(sum(real.close_value for real in beyond if real.deal_stage == "Won")),
            "focus_rule": top(group_by_agent(rows), focus_rule),
        }
    return {
        "tie_break": {"recent_first": top(by_agent, focus_rule),
                      "oldest_first": top(by_agent, lambda pair: focus_rule(pair, recent_first=False))},
        "threshold": thresholds,
    }


def evaluate_cutoff(dataset: Dataset, cutoff: date) -> dict:
    reference = build_reference(dataset, cutoff)
    rows = score_rows(dataset, cutoff, reference)

    lanes = {}
    for lane in ("negociar", "encerrar"):
        subset = [real for item, real in rows if item.lane == lane]
        counts = defaultdict(int)
        for real in subset:
            counts[outcome(real)] += 1
        resolved = counts["won"] + counts["lost"]
        lanes[lane] = {
            "deals": len(subset), **{k: counts[k] for k in ("won", "lost", "open")},
            "won_revenue": int(sum(real.close_value for real in subset if real.deal_stage == "Won")),
            "win_rate_resolved": round(counts["won"] / resolved, 4) if resolved else None,
        }

    # Desfecho da coluna Negociar por fase: mostra quanto dela ainda trava depois.
    phases = defaultdict(lambda: {"deals": 0, "won": 0, "lost": 0, "open": 0})
    for item, real in rows:
        if item.lane == "negociar":
            phases[item.phase]["deals"] += 1
            phases[item.phase][outcome(real)] += 1

    by_agent = group_by_agent(rows)
    rate_by_age = survival_rates(dataset, cutoff)

    # Chaves sem ID: empates na vaga de corte dividem a vaga proporcionalmente.
    def previous_rule(pair):
        item = pair[0]
        return (-previous_attention_score(dataset, item), -item.catalog_price)

    def expected_value(pair):
        item = pair[0]
        if item.lane != "negociar":
            return (LANE_RANK[item.lane], -item.catalog_price)
        return (LANE_RANK["negociar"], -item.catalog_price * rate_by_age(item.days_in_engaging))

    return {
        "cutoff": cutoff.isoformat(),
        "horizon_days": (END_OF_DATA - cutoff).days,
        "reference": {"closed": reference.closed, "max_cycle_days": reference.max_cycle_days,
                      "base_rate": round(float(reference.base_rate), 4)},
        "engaging_open": len(rows),
        "lanes": lanes,
        "focus_outcome_by_phase": dict(phases),
        f"top{TOP_N}_per_agent": {
            "previous_attention_rule": top(by_agent, previous_rule),
            "price_only_no_lanes": top(by_agent, price_only),
            "lanes_expected_value_rejected": top(by_agent, expected_value),
            "focus_rule": top(by_agent, focus_rule),
            # Decomposição: de onde vem a diferença para "só valor"?
            "price_recency_no_lanes": top(by_agent, price_recency),
            "lanes_price_no_recency": top(by_agent, lanes_price),
        },
        "robustness": robustness(dataset, cutoff, reference, by_agent),
        "_per_agent": {name: revenue_by_agent(by_agent, key) for name, key in DECOMPOSITION.items()},
    }


# Chaves sem ID: empates na vaga de corte dividem a vaga proporcionalmente.
def price_only(pair):
    return (-pair[0].catalog_price,)


def price_recency(pair):
    """Só valor e, no empate, o negócio mais novo; sem colunas (parados podem entrar)."""
    return (-pair[0].catalog_price, pair[0].days_in_engaging)


def lanes_price(pair):
    """Colunas e valor, sem desempate por idade: isola o efeito de tirar os parados."""
    return (LANE_RANK[pair[0].lane], -pair[0].catalog_price)


DECOMPOSITION = {
    "price_only_no_lanes": price_only,
    "lanes_price_no_recency": lanes_price,
    "price_recency_no_lanes": price_recency,
    "focus_rule": focus_rule,
}


def summarize(cutoffs: list[dict]) -> dict:
    """Totais dos controles de robustez; o desempate é somado em duas partes de cortes."""
    def total(rows, path):
        result = defaultdict(float)
        for row in rows:
            node = row
            for step in path:
                node = node[step]
            for name in ("won", "won_revenue", "beyond_cycle_slots"):
                result[name] += node[name]
        return {name: round(value, 2) for name, value in result.items()}

    split = {"first_cutoffs": cutoffs[:SELECTION_CUTOFFS], "last_cutoffs": cutoffs[SELECTION_CUTOFFS:]}
    return {
        "tie_break": {part: {order: total(rows, ("robustness", "tie_break", order))
                             for order in ("recent_first", "oldest_first")}
                      for part, rows in split.items()},
        "price_only": {part: total(rows, (f"top{TOP_N}_per_agent", "price_only_no_lanes"))
                       for part, rows in split.items()},
        "threshold": {name: {**total(cutoffs, ("robustness", "threshold", name, "focus_rule")),
                             "beyond_deals": sum(c["robustness"]["threshold"][name]["beyond_deals"]
                                                 for c in cutoffs),
                             "beyond_won": sum(c["robustness"]["threshold"][name]["beyond_won"]
                                               for c in cutoffs)}
                      for name, _ in THRESHOLDS},
    }


def decompose(cutoffs: list[dict], per_agent: list[dict]) -> dict:
    """Totais das variantes da decomposição e bootstrap pareado da regra contra cada uma."""
    totals = {}
    for name in DECOMPOSITION:
        rows = [c[f"top{TOP_N}_per_agent"][name] for c in cutoffs]
        totals[name] = {field: round(sum(r[field] for r in rows), 2)
                        for field in ("won", "won_revenue", "beyond_cycle_slots")}

    def units(a: str, b: str) -> list[tuple[float, float]]:
        return [(p[a][agent], p[b][agent]) for p in per_agent for agent in p[a]]

    return {
        "totals": totals,
        "bootstrap": {f"focus_rule_vs_{other}": bootstrap(units("focus_rule", other))
                      for other in DECOMPOSITION if other != "focus_rule"},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    dataset = load_dataset(download_archive(root / "data" / ARCHIVE_NAME))
    cutoffs = [evaluate_cutoff(dataset, cutoff) for cutoff in CUTOFFS]
    per_agent = [c.pop("_per_agent") for c in cutoffs]
    result = {
        "note": "Exploratório. Outcomes observados até 31/12/2017; Prospecting excluído por falta de datas.",
        "robustness_summary": summarize(cutoffs),
        "decomposition": decompose(cutoffs, per_agent),
        "cutoffs": cutoffs,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
