"""Backtest temporal da ordenação (PRD, seção 5; ADR-001, validações 7 e 8).

Para cada corte T, a população é toda negociação engajada até T e ainda aberta em T,
inclusive as que nunca fecham na base: é a carteira que o vendedor via em T. O desfecho
é "ganhou em até HORIZON_DAYS dias depois de T". T + horizonte cai dentro da base, então
uma negociação que segue aberta no fim não ganhou na janela (fato da base, não imputação).

Reconstrução: sem histórico de estágio nem data de criação, a negociação conta como em
andamento de `engage_date` até `close_date`. Prospecting não tem data e fica de fora, ou
seja, o grupo Qualificar não é avaliado aqui.

Os ordenadores legítimos só recebem o que se sabia em T: vendedor, produto, preço de
tabela, data de engajamento e o histórico de fechadas até T. O desfecho (ganho, valor e
data de fechamento) fica à parte e só serve para medir. A única exceção, marcada como
vazamento, é a armadilha do mês de fechamento.

A regra servida (regra A, ADR-006) não é reescrita aqui: o grupo de cada negociação em T
vem de `triage.engaging_group`, com os limites de `triage.resolve_context(frame, T)`, a
mesma função e os mesmos limites que a lista usa. Ela é a referência das diferenças.

Habilidade (AUC, com IC95% por bootstrap) e lista do vendedor ficam separadas. A lista
mede o que cada vendedor veria nas TOP_K primeiras: acertos (P@K), acertos sobre o
esperado ao acaso (Lift@K) e valor ganho sobre o da melhor lista possível sabendo o
futuro (Val@K). Os cortes se sobrepõem e o mesmo vendedor está em todos, então as
diferenças contra a regra atual têm IC por bootstrap de vendedores. A sensibilidade sem
as negociações que nunca fecham mostra quanto da conclusão depende delas.

Rodar (em solution/): `.venv/bin/python scripts/backtest.py`
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

SOLUTION_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOLUTION_DIR))

from leadscorer import codes, data, policy, triage  # noqa: E402
from leadscorer.errors import LeadScorerError, PolicyError  # noqa: E402

SEED = 20260101
CUTS = ("2017-03-31", "2017-04-30", "2017-05-31", "2017-06-30", "2017-07-31", "2017-08-31", "2017-09-30")
HORIZON_DAYS = 90
TOP_K = 10
SMOOTH_M = 20
N_BOOT = 300
N_BOOT_SELLERS = 2000
FIXED_LIMITS = (90, 100, 106, 115, 120)
OUT_DIR = SOLUTION_DIR / "data" / "processed"


@dataclass(frozen=True)
class Cut:
    as_of: pd.Timestamp
    ctx: triage.Context
    train: pd.DataFrame      # fechadas até T: product, won, cycle_days
    features: pd.DataFrame   # o que se sabia em T sobre cada negociação aberta
    outcome: pd.DataFrame    # desfecho, só para medir


def close_values(raw_dir: Path) -> pd.Series:
    """`close_value` vem direto do CSV: a regra nunca enxerga esse campo (`triage.classify`)."""
    pipeline = data.read_table(raw_dir, "sales_pipeline")
    return pd.to_numeric(pipeline.set_index("opportunity_id")["close_value"])


def build_cut(frame: pd.DataFrame, values: pd.Series, as_of: str) -> Cut:
    stamp = pd.Timestamp(as_of)
    end = stamp + pd.Timedelta(days=HORIZON_DAYS)
    last = frame["close_date"].max()
    if end > last:
        raise PolicyError(f"Corte {stamp.date().isoformat()} + {HORIZON_DAYS} d passa do último fechamento "
                          f"registrado ({last.date().isoformat()}): o desfecho não seria observável.",
                          code="backtest_horizon_after_last_close")  # só do script, fora do contrato da API
    closed = frame[frame["deal_stage"].isin(policy.CLOSED_STAGES) & (frame["close_date"] <= stamp)]
    train = pd.DataFrame({"product": closed["product"], "won": (closed["deal_stage"] == "Won").astype(int),
                          "cycle_days": (closed["close_date"] - closed["engage_date"]).dt.days})
    still_open = frame["close_date"].isna() | (frame["close_date"] > stamp)
    test = frame[(frame["engage_date"] <= stamp) & still_open]
    test = test.sort_values("opportunity_id").reset_index(drop=True)
    features = test.loc[:, ["opportunity_id", "sales_agent", "product", "sales_price", "engage_date"]]
    won = (test["deal_stage"] == "Won") & (test["close_date"] <= end)
    outcome = pd.DataFrame({
        "won": won.astype(int),
        "won_value": test["opportunity_id"].map(values).where(won, 0).fillna(0).astype(float),
        "close_date": test["close_date"],
        "no_outcome": test["close_date"].isna(),
    })
    return Cut(stamp, triage.resolve_context(frame, stamp), train, features, outcome)


def without_no_outcome(cut: Cut) -> Cut:
    """O mesmo corte sem as negociações que nunca fecham na base (sensibilidade)."""
    keep = ~cut.outcome["no_outcome"].to_numpy()
    return Cut(cut.as_of, cut.ctx, cut.train, cut.features[keep].reset_index(drop=True),
               cut.outcome[keep].reset_index(drop=True))


def age_days(cut: Cut) -> np.ndarray:
    return (cut.as_of - cut.features["engage_date"]).dt.days.to_numpy()


GROUP_RANK = {policy.FOCAR: 2, policy.ACOMPANHAR: 1, policy.REVISAR: 0}


def served_order(cut: Cut, ctx: Optional[triage.Context] = None) -> np.ndarray:
    """A ordem da lista em T: o grupo de `triage.engaging_group` (com os limites de `ctx`,
    por padrão os do corte) e, dentro dele, maior preço de tabela primeiro."""
    groups = triage.engaging_group(age_days(cut), cut.ctx if ctx is None else ctx)
    rank = pd.Series(groups).map(GROUP_RANK).to_numpy(float)
    return rank * 1e6 + cut.features["sales_price"].to_numpy(float)


# Ordenadores legítimos: recebem a negociação como era em T, nunca o desfecho.
def global_rate(cut: Cut) -> np.ndarray:
    return np.full(len(cut.features), cut.train["won"].mean())


def product_rate(cut: Cut) -> np.ndarray:
    p0 = cut.train["won"].mean()
    grouped = cut.train.groupby("product")["won"].agg(["sum", "count"])
    smoothed = (grouped["sum"] + SMOOTH_M * p0) / (grouped["count"] + SMOOTH_M)
    return cut.features["product"].map(smoothed).fillna(p0).to_numpy(float)


def random_order(cut: Cut) -> np.ndarray:
    return np.random.default_rng(SEED + cut.as_of.month).random(len(cut.features))


def table_value(cut: Cut) -> np.ndarray:
    return cut.features["sales_price"].to_numpy(float)


def youngest_first(cut: Cut) -> np.ndarray:
    return -age_days(cut).astype(float)


def served_rule(cut: Cut) -> np.ndarray:
    """A regra servida (A): até o P90 das ganhas em T, depois até o maior ciclo, depois acima."""
    return served_order(cut)


def max_cycle_only(cut: Cut) -> np.ndarray:
    """A regra até a v4: um corte só, no maior ciclo fechado até T (L1 = L2)."""
    return served_order(cut, replace(cut.ctx, won_cycle_limit_days=cut.ctx.cycle_limit_days))


def fixed_limit(days: int) -> Callable[[Cut], np.ndarray]:
    """Primeiro limite fixo em `days` (nunca acima do maior ciclo em T)."""
    def ranker(cut: Cut) -> np.ndarray:
        return served_order(cut, replace(cut.ctx, won_cycle_limit_days=min(days, cut.ctx.cycle_limit_days)))
    return ranker


# Armadilha: usa a data de fechamento, que só existe depois do resultado.
def closing_month_trap(cut: Cut) -> np.ndarray:
    month_of_quarter = (cut.outcome["close_date"].dt.month - 1) % 3 + 1
    return (month_of_quarter == 3).astype(float).to_numpy()


SERVED = "Regra servida (A): até o P90 das ganhas → até o maior ciclo → preço"
MAX_CYCLE = "Regra anterior: só até o maior ciclo → preço"
REFERENCE = SERVED  # as diferenças são sempre contra a regra que a lista serve
LIST_PRICE = "Só valor de tabela"
RANKERS: List[Tuple[str, Callable[[Cut], np.ndarray], bool]] = [
    ("Taxa global", global_rate, False),
    ("Taxa por produto", product_rate, False),
    ("Aleatório", random_order, False),
    (LIST_PRICE, table_value, False),
    ("Idade: mais nova primeiro", youngest_first, False),
    (MAX_CYCLE, max_cycle_only, False),
    (SERVED, served_rule, False),
    ("[VAZAMENTO] fechou no 3º mês do trimestre", closing_month_trap, True),
]
LIMITS: List[Tuple[str, Callable[[Cut], np.ndarray], bool]] = [
    (f"Até {days} d → até o maior ciclo → preço", fixed_limit(days), False) for days in FIXED_LIMITS]
# Código estável de cada estratégia no JSON (o nome é do relatório; a API serve os códigos).
CODES = {
    "Taxa global": codes.RANKER_GLOBAL_RATE,
    "Taxa por produto": codes.RANKER_PRODUCT_RATE,
    "Aleatório": codes.RANKER_RANDOM,
    LIST_PRICE: codes.RANKER_LIST_PRICE_ONLY,
    "Idade: mais nova primeiro": codes.RANKER_AGE_NEWEST_FIRST,
    MAX_CYCLE: codes.RANKER_AGE_MAX_CYCLE_ONLY,
    SERVED: codes.RANKER_AGE_P90_THEN_MAX_CYCLE,
    "[VAZAMENTO] fechou no 3º mês do trimestre": codes.RANKER_LEAK_QUARTER_END,
    **{name: f"limit_{days}_days" for (name, _, _), days in zip(LIMITS, FIXED_LIMITS)},
}
# Sem as que nunca fecham, só os que ordenam por preço e idade interessam.
SENSITIVE = [(name, ranker, leak) for name, ranker, leak in RANKERS if name in (LIST_PRICE, MAX_CYCLE, SERVED)]


def auc(y: np.ndarray, scores: np.ndarray) -> float:
    """AUC por soma de postos (Mann-Whitney); empates contam 0,5."""
    positives = int(y.sum())
    negatives = len(y) - positives
    ranks = stats.rankdata(scores)
    return float((ranks[y == 1].sum() - positives * (positives + 1) / 2) / (positives * negatives))


def auc_ci(y: np.ndarray, scores: np.ndarray) -> Tuple[float, float]:
    if np.all(scores == scores[0]):
        return 0.5, 0.5
    rng = np.random.default_rng(SEED)
    values = []
    for _ in range(N_BOOT):
        idx = rng.integers(0, len(y), len(y))
        if 0 < y[idx].sum() < len(idx):
            values.append(auc(y[idx], scores[idx]))
    return float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))


def top_k(cut: Cut, scores: np.ndarray, k: int = TOP_K) -> pd.DataFrame:
    """Uma linha por vendedor com pelo menos k negociações abertas em T: ganhas e valor
    ganho nas k primeiras da ordem (empates pelo ID, como na ferramenta), ganhas
    esperadas ao acaso e o oráculo, a soma dos k maiores valores ganhos da carteira
    (a melhor lista possível, sabendo o futuro)."""
    frame = pd.DataFrame({"seller": cut.features["sales_agent"], "id": cut.features["opportunity_id"],
                          "score": scores, "won": cut.outcome["won"], "value": cut.outcome["won_value"]})
    rows = []
    for seller, group in frame.groupby("seller"):
        if len(group) < k:
            continue
        top = group.sort_values(["score", "id"], ascending=[False, True]).head(k)
        rows.append({"seller": seller, "hits": int(top["won"].sum()), "expected_hits": k * float(group["won"].mean()),
                     "value": float(top["value"].sum()), "oracle": float(group["value"].nlargest(k).sum())})
    return pd.DataFrame(rows, columns=["seller", "hits", "expected_hits", "value", "oracle"])


def list_metrics(lists: pd.DataFrame, k: int = TOP_K) -> Dict[str, float]:
    """P@K, Lift@K e Val@K somando todas as listas (vendedor × corte)."""
    return {"p_at_k": float(lists["hits"].sum() / (k * len(lists))),
            "lift_at_k": float(lists["hits"].sum() / lists["expected_hits"].sum()),
            "val_at_k": float(lists["value"].sum() / lists["oracle"].sum())}


def delta_ci(mine: pd.DataFrame, ref: pd.DataFrame, k: int = TOP_K) -> Dict[str, float]:
    """Δ (mine − ref) de P@K e Val@K, com IC95% por bootstrap de vendedores. A mesma
    negociação aparece em vários cortes e o vendedor em todos: cada reamostragem leva
    o vendedor com todos os seus cortes."""
    columns = ["hits", "value", "oracle"]
    a = mine.groupby("seller")[columns].sum()
    b = ref.groupby("seller")[columns].sum().reindex(a.index)
    n = mine.groupby("seller").size().reindex(a.index).to_numpy()
    idx = np.random.default_rng(SEED).integers(0, len(a), (N_BOOT_SELLERS, len(a)))
    d_p = (a["hits"].to_numpy()[idx].sum(1) - b["hits"].to_numpy()[idx].sum(1)) / (k * n[idx].sum(1))
    d_v = (a["value"].to_numpy()[idx].sum(1) / a["oracle"].to_numpy()[idx].sum(1)
           - b["value"].to_numpy()[idx].sum(1) / b["oracle"].to_numpy()[idx].sum(1))
    mine_m, ref_m = list_metrics(mine, k), list_metrics(ref, k)
    return {"d_p_at_k": mine_m["p_at_k"] - ref_m["p_at_k"],
            "d_p_low": float(np.percentile(d_p, 2.5)), "d_p_high": float(np.percentile(d_p, 97.5)),
            "d_val_at_k": mine_m["val_at_k"] - ref_m["val_at_k"],
            "d_val_low": float(np.percentile(d_v, 2.5)), "d_val_high": float(np.percentile(d_v, 97.5))}


def evaluate(cuts: List[Cut], rankers: List[Tuple[str, Callable[[Cut], np.ndarray], bool]],
             with_ci: bool = True) -> Tuple[List[Dict], Dict[str, pd.DataFrame]]:
    """Linhas por corte × ordenador e as listas de cada vendedor, por ordenador."""
    rows, lists = [], {}
    for cut in cuts:
        y = cut.outcome["won"].to_numpy()
        for name, ranker, leak in rankers:
            scores = ranker(cut)
            top = top_k(cut, scores).assign(cut=cut.as_of.date().isoformat())
            lists.setdefault(name, []).append(top)
            row = {"cut": cut.as_of.date().isoformat(), "ranker": name, "code": CODES[name], "leak": leak,
                   "auc": round(auc(y, scores), 3)}
            if with_ci:
                low, high = auc_ci(y, scores)
                row.update(ci_low=round(low, 3), ci_high=round(high, 3))
            row.update({key: round(value, 3) for key, value in list_metrics(top).items()})
            rows.append(row)
    return rows, {name: pd.concat(parts, ignore_index=True) for name, parts in lists.items()}


def summarize(rows: List[Dict], lists: Dict[str, pd.DataFrame],
              rankers: List[Tuple[str, Callable[[Cut], np.ndarray], bool]],
              reference: Optional[pd.DataFrame]) -> List[Dict]:
    by_cut_ref = {r["cut"]: r["val_at_k"] for r in rows if r["ranker"] == REFERENCE}
    summary = []
    for name, _, leak in rankers:
        mine = [r for r in rows if r["ranker"] == name]
        entry = {"ranker": name, "code": CODES[name], "leak": leak,
                 "auc_mean": round(float(np.mean([r["auc"] for r in mine])), 3),
                 "auc_min": min(r["auc"] for r in mine), "auc_max": max(r["auc"] for r in mine)}
        if "ci_low" in mine[0]:
            entry["cuts_ci_above_half"] = sum(r["ci_low"] > 0.5 for r in mine)
            entry["cuts_ci_below_half"] = sum(r["ci_high"] < 0.5 for r in mine)
        entry.update({key: round(value, 3) for key, value in list_metrics(lists[name]).items()})
        if by_cut_ref and name != REFERENCE:
            entry["cuts_val_above_reference"] = sum(r["val_at_k"] > by_cut_ref[r["cut"]] for r in mine)
        if reference is not None and name != REFERENCE and not leak:
            entry.update({key: round(value, 3) for key, value in delta_ci(lists[name], reference).items()})
        summary.append(entry)
    return summary


def wins_outside_first_group(cuts: List[Cut], first_limit: Callable[[Cut], int]) -> float:
    """Parcela das ganhas na janela que a regra deixa fora do primeiro grupo."""
    outside = sum(int(cut.outcome["won"].to_numpy()[age_days(cut) > first_limit(cut)].sum()) for cut in cuts)
    return outside / sum(int(cut.outcome["won"].sum()) for cut in cuts)


def walk_forward(rows: List[Dict], lists: Dict[str, pd.DataFrame], candidates: List[str]) -> Dict:
    """Em cada corte, escolhe o limite com melhor Val@K nos cortes anteriores e mede no
    corte seguinte: o limite deixa de ser escolhido olhando o próprio teste."""
    cuts = sorted({r["cut"] for r in rows})
    steps = []
    for i, cut in enumerate(cuts[1:], 1):
        past = {name: list_metrics(lists[name][lists[name]["cut"] < cut])["val_at_k"] for name in candidates}
        chosen = max(candidates, key=lambda name: past[name])
        now = {name: list_metrics(lists[name][lists[name]["cut"] == cut])["val_at_k"] for name in (chosen, SERVED, MAX_CYCLE)}
        steps.append({"cut": cut, "chosen": chosen, "val_walk_forward": round(now[chosen], 3),
                      "val_served": round(now[SERVED], 3), "val_max_cycle": round(now[MAX_CYCLE], 3)})
    mean = {key: round(float(np.mean([s[key] for s in steps])), 3)
            for key in ("val_walk_forward", "val_served", "val_max_cycle")}
    return {"steps": steps, "mean": mean}


def run(raw_dir: Path = policy.RAW_DIR) -> Dict:
    dataset = data.load(raw_dir)
    values = close_values(raw_dir)
    cuts = [build_cut(dataset.opportunities, values, as_of) for as_of in CUTS]
    cut_rows = []
    for cut in cuts:
        age = age_days(cut)
        cut_rows.append({
            "cut": cut.as_of.date().isoformat(), "n_train": len(cut.train), "n_test": len(cut.features),
            "share_no_outcome": round(float(cut.outcome["no_outcome"].mean()), 3),
            "test_win_rate": round(float(cut.outcome["won"].mean()), 3),
            "cycle_limit_days": cut.ctx.cycle_limit_days, "won_cycle_limit_days": cut.ctx.won_cycle_limit_days,
            "share_above_limit": round(float((age > cut.ctx.cycle_limit_days).mean()), 3),
            "sellers_with_k": int((cut.features["sales_agent"].value_counts() >= TOP_K).sum())})
    observations = sum(len(cut.features) for cut in cuts)
    unique = int(pd.concat([cut.features["opportunity_id"] for cut in cuts]).nunique())

    rows, lists = evaluate(cuts, RANKERS)
    summary = summarize(rows, lists, RANKERS, lists[REFERENCE])

    limit_rows, limit_lists = evaluate(cuts, LIMITS, with_ci=False)
    all_rows, all_lists = rows + limit_rows, {**lists, **limit_lists}
    first_limits = {SERVED: lambda cut: cut.ctx.won_cycle_limit_days, MAX_CYCLE: lambda cut: cut.ctx.cycle_limit_days,
                    **{name: (lambda cut, d=days: d) for (name, _, _), days in zip(LIMITS, FIXED_LIMITS)}}
    limit_names = [MAX_CYCLE, *[name for name, _, _ in LIMITS], SERVED]
    limits = summarize(all_rows, all_lists, [(n, None, False) for n in limit_names], lists[REFERENCE])
    for entry in limits:
        entry["wins_outside_first_group"] = round(wins_outside_first_group(cuts, first_limits[entry["ranker"]]), 3)
    forward = walk_forward(all_rows, all_lists, [*[name for name, _, _ in LIMITS], MAX_CYCLE])

    trimmed = [without_no_outcome(cut) for cut in cuts]
    trim_rows, trim_lists = evaluate(trimmed, SENSITIVE, with_ci=False)
    without = summarize(trim_rows, trim_lists, SENSITIVE, trim_lists[REFERENCE])

    today = triage.resolve_context(dataset.opportunities)
    return {"design": {"cuts": list(CUTS), "horizon_days": HORIZON_DAYS, "top_k": TOP_K, "seed": SEED,
                       "smooth_m": SMOOTH_M, "n_boot": N_BOOT, "n_boot_sellers": N_BOOT_SELLERS,
                       "fixed_limits": list(FIXED_LIMITS), "observations": observations,
                       "unique_opportunities": unique, "audited_data": dataset.audited,
                       "served_rule": codes.SERVED_RANKER, "as_of": today.as_of.date().isoformat(),
                       "won_cycle_limit_days": today.won_cycle_limit_days},
            "cuts": cut_rows, "rows": rows, "summary": summary, "limits": limits,
            "walk_forward": forward, "without_no_outcome": without}


def pct(value: float) -> str:
    return f"{100 * value:.1f}%".replace(".", ",")


def dec(value: float) -> str:
    return f"{value:.3f}".replace(".", ",")


def pp(value: float) -> str:
    return f"{100 * value:+.1f}".replace(".", ",")


def delta_cell(entry: Dict, key: str) -> str:
    low, high = {"d_val_at_k": ("d_val_low", "d_val_high"), "d_p_at_k": ("d_p_low", "d_p_high")}[key]
    if key not in entry:
        return "—"
    return f"{pp(entry[key])} ({pp(entry[low])} a {pp(entry[high])})"


def list_table(entries: List[Dict], extra: Optional[Tuple[str, str]] = None) -> List[str]:
    head = "| Ordenador | AUC média | P@10 | Lift@10 | Val@10 | Δ Val@10 em pp (IC95%) | Δ P@10 em pp (IC95%) |"
    sep = "| --- | --- | --- | --- | --- | --- | --- |"
    if extra:
        head += f" {extra[1]} |"
        sep += " --- |"
    lines = [head, sep]
    for e in entries:
        line = (f"| {e['ranker']} | {dec(e['auc_mean'])} | {pct(e['p_at_k'])} | {dec(e['lift_at_k'])} | "
                f"{pct(e['val_at_k'])} | {delta_cell(e, 'd_val_at_k')} | {delta_cell(e, 'd_p_at_k')} |")
        if extra:
            line += f" {pct(e[extra[0]])} |"
        lines.append(line)
    return lines


def markdown(result: Dict) -> str:
    design, cuts = result["design"], result["design"]["cuts"]
    summary = {s["ranker"]: s for s in result["summary"]}
    previous, forward = summary[MAX_CYCLE], result["walk_forward"]["mean"]
    lines = ["# Backtest temporal da ordenação", "",
             "Gerado por `scripts/backtest.py` (não editar à mão).", "",
             "## Desenho", "",
             f"- **População em cada corte T:** toda negociação engajada até T e ainda aberta em T, inclusive as que "
             f"nunca fecham na base. É a carteira que o vendedor via em T.",
             f"- **Desfecho:** ganhou em até {design['horizon_days']} dias depois de T. Como T + {design['horizon_days']} "
             f"dias cai dentro da base, \"não ganhou\" é observado, também para as que seguem abertas no fim.",
             "- **Reconstrução:** sem histórico de estágio nem data de criação, a negociação conta como em andamento "
             "de `engage_date` até `close_date`. Prospecting não tem data e fica de fora: o grupo Qualificar não é "
             "avaliado aqui.",
             "- **O que os ordenadores veem:** vendedor, produto, preço de tabela, data de engajamento e as fechadas "
             "até T. O mês de fechamento entra só na armadilha marcada como vazamento.",
             f"- **Lista do vendedor:** as {design['top_k']} primeiras da ordem de cada vendedor com pelo menos "
             f"{design['top_k']} abertas em T, com empates pelo ID. P@10 = ganhas entre as 10 ÷ 10. Lift@10 = ganhas "
             "÷ ganhas esperadas ao acaso na carteira do vendedor. Val@10 = valor ganho nas 10 ÷ valor ganho nas 10 "
             "melhores da carteira sabendo o futuro (o oráculo). As somas cobrem todos os vendedor-cortes.",
             f"- **Dependência:** os cortes se sobrepõem ({design['observations']} observações para "
             f"{design['unique_opportunities']} negociações únicas) e o mesmo vendedor aparece em todos. Os Δ contra a "
             f"regra servida têm IC95% por bootstrap de vendedores ({design['n_boot_sellers']} reamostragens, cada "
             "vendedor com todos os seus cortes).",
             "", "## Cortes", "",
             "| Corte | Fechadas até T | Abertas em T | Sem desfecho até o fim da base | Ganharam em 90 d "
             "| Maior ciclo em T (L2) | P90 das ganhas em T (L1) | Acima do maior ciclo | Vendedores com 10+ |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    lines += [f"| {c['cut']} | {c['n_train']} | {c['n_test']} | {pct(c['share_no_outcome'])} | "
              f"{pct(c['test_win_rate'])} | {c['cycle_limit_days']} d | {c['won_cycle_limit_days']} d | "
              f"{pct(c['share_above_limit'])} | {c['sellers_with_k']} |" for c in result["cuts"]]
    lines += ["", "## Habilidade: AUC (IC95%) por corte", "",
              "| Ordenador | " + " | ".join(cuts) + " | Média |", "| --- |" + " --- |" * (len(cuts) + 1)]
    for s in result["summary"]:
        cells = [f"{dec(r['auc'])} ({dec(r['ci_low'])}–{dec(r['ci_high'])})"
                 for r in result["rows"] if r["ranker"] == s["ranker"]]
        lines.append(f"| {s['ranker']} | " + " | ".join(cells) + f" | {dec(s['auc_mean'])} |")
    lines += ["", "## Lista do vendedor (10 primeiras), todos os cortes somados", ""]
    lines += list_table([s for s in result["summary"] if not s["leak"]])
    lines += ["", "## Val@10 por corte", "",
              "| Ordenador | " + " | ".join(cuts) + " |", "| --- |" + " --- |" * len(cuts)]
    for s in result["summary"]:
        if not s["leak"]:
            cells = [pct(r["val_at_k"]) for r in result["rows"] if r["ranker"] == s["ranker"]]
            lines.append(f"| {s['ranker']} | " + " | ".join(cells) + " |")
    lines += ["", "## Sensibilidade ao limite do primeiro grupo", "",
              f"Os limites fixos foram escolhidos depois de olhar a base ({design['won_cycle_limit_days']} d é o P90 "
              f"das ganhas em {pd.Timestamp(design['as_of']).strftime('%d/%m/%Y')}). Só a regra servida calcula o "
              "limite com o que se sabia em T.", ""]
    lines += list_table(result["limits"], ("wins_outside_first_group", "Ganhas fora do 1º grupo"))
    lines += ["", "### Escolha do limite sem olhar o teste (walk-forward)", "",
              "| Corte | Limite escolhido nos cortes anteriores | Val@10 do escolhido | Val@10 da regra servida | "
              "Val@10 da regra anterior |", "| --- | --- | --- | --- | --- |"]
    lines += [f"| {s['cut']} | {s['chosen']} | {pct(s['val_walk_forward'])} | {pct(s['val_served'])} | "
              f"{pct(s['val_max_cycle'])} |" for s in result["walk_forward"]["steps"]]
    lines += [f"| Média | | {pct(forward['val_walk_forward'])} | {pct(forward['val_served'])} | "
              f"{pct(forward['val_max_cycle'])} |"]
    lines += ["", "## Sensibilidade: sem as negociações que nunca fecham", "",
              "Mesmos cortes, tirando as que seguem abertas no fim da base. Mostra quanto da diferença entre as "
              "regras depende delas.", ""]
    lines += list_table(result["without_no_outcome"])
    ahead = [s for s in result["without_no_outcome"] if s.get("d_val_low", 0) > 0]
    if ahead:
        best = max(ahead, key=lambda s: s["d_val_at_k"])
        depends = (f"\"{best['ranker']}\" fica {pp(best['d_val_at_k'])} pp à frente da regra servida em Val@10 "
                   f"(IC95% {pp(best['d_val_low'])} a {pp(best['d_val_high'])}). A vantagem das regras por idade "
                   "depende desses registros, e a auditoria indica que eles podem vir da construção da base")
    else:
        depends = "nenhuma alternativa fica à frente da regra servida com o IC95% acima de zero"
    beats = ("nenhum limite fixo escolhido assim supera o P90 calculado em T"
             if forward["val_walk_forward"] <= forward["val_served"] else
             "um limite fixo escolhido assim supera o P90 calculado em T")
    lines += ["", "## Leitura", "",
              f"- A regra anterior (só o maior ciclo) fica {pp(previous['d_val_at_k'])} pp em relação à regra servida "
              f"em Val@10 (IC95% {pp(previous['d_val_low'])} a {pp(previous['d_val_high'])}) e "
              f"{pp(previous['d_p_at_k'])} pp em P@10, com Val@10 acima da servida em "
              f"{previous['cuts_val_above_reference']} de {len(cuts)} cortes.",
              f"- Sem as negociações que nunca fecham: {depends}.",
              f"- Escolher o limite olhando só os cortes anteriores rende {pct(forward['val_walk_forward'])} de Val@10, "
              f"contra {pct(forward['val_served'])} da regra servida: {beats}.",
              "- Ordenar por preço captura valor por construção, sem acertar mais. Por isso P@10 e Val@10 aparecem "
              "lado a lado.",
              "- O backtest mede quem teria ganhado de qualquer forma. Não mede o efeito de trabalhar a lista: isso "
              "só um piloto com grupo de controle mostra."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", type=Path, default=policy.RAW_DIR, help="pasta com os CSVs")
    parser.add_argument("--no-write", action="store_true", help="só imprime, sem gravar em data/processed/")
    args = parser.parse_args()
    try:
        result = run(args.raw)
    except LeadScorerError as error:
        print(f"Erro: {error}", file=sys.stderr)
        return 1
    report = markdown(result)
    print(report)
    if not args.no_write:
        (OUT_DIR / "backtest_results.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (OUT_DIR / "backtest_report.md").write_text(report, encoding="utf-8")
        print(f"Gravado em {data.display_path(OUT_DIR)}/backtest_results.json e backtest_report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
