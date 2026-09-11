"""Diagnostic analysis of Dataset 1 (operational customer support tickets).

Answers the three mandatory questions from the challenge brief:
  1. Where does the flow get stuck? (bottlenecks by channel/priority/type)
  2. What drives satisfaction?
  3. How much are we wasting, in hours and R$?

Writes submissions/cleiton/solution/output/diagnostic.json,
which feeds the dashboard directly (no server round-trip needed).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_regression
from sklearn.preprocessing import OrdinalEncoder

DATA_PATH = Path(__file__).resolve().parents[3] / "datasets" / "customer_support_tickets.csv"
OUT_PATH = Path(__file__).resolve().parent / "output" / "diagnostic.json"


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["First Response Time"] = pd.to_datetime(df["First Response Time"], errors="coerce")
    df["Time to Resolution"] = pd.to_datetime(df["Time to Resolution"], errors="coerce")
    return df


def data_quality_report(df: pd.DataFrame) -> dict:
    total = len(df)
    has_both_timestamps = df["First Response Time"].notna() & df["Time to Resolution"].notna()
    negative_or_zero = has_both_timestamps & (df["Time to Resolution"] <= df["First Response Time"])
    valid = has_both_timestamps & (df["Time to Resolution"] > df["First Response Time"])
    return {
        "total_rows": int(total),
        "rows_with_resolution_and_rating": int(df["Customer Satisfaction Rating"].notna().sum()),
        "rows_with_both_timestamps": int(has_both_timestamps.sum()),
        "rows_with_invalid_or_zero_duration": int(negative_or_zero.sum()),
        "rows_valid_for_cycle_time": int(valid.sum()),
        "pct_valid_for_cycle_time": round(100 * valid.sum() / total, 1),
        "note": (
            "O ticket status Open/Pending nunca tem Time to Resolution preenchido "
            "(esperado). Entre os Closed, uma fração tem Time to Resolution anterior "
            "ao First Response Time; a origem dessa inconsistência não foi verificada. "
            "Durações zero também são excluídas por convenção, sem serem tratadas "
            "como necessariamente impossíveis. Só resolução > primeira resposta entra nas "
            "métricas de tempo de ciclo abaixo."
        ),
    }


def valid_cycle_time_frame(df: pd.DataFrame) -> pd.DataFrame:
    mask = (
        df["First Response Time"].notna()
        & df["Time to Resolution"].notna()
        & (df["Time to Resolution"] > df["First Response Time"])
    )
    v = df.loc[mask].copy()
    v["cycle_hours"] = (v["Time to Resolution"] - v["First Response Time"]).dt.total_seconds() / 3600
    return v


def group_stats(v: pd.DataFrame, group_cols: list[str], min_n: int = 5) -> list[dict]:
    rows = []
    for key, g in v.groupby(group_cols, observed=True):
        if len(g) < min_n:
            continue
        key_tuple = key if isinstance(key, tuple) else (key,)
        row = dict(zip(group_cols, key_tuple))
        row["n"] = int(len(g))
        row["median_hours"] = round(float(g["cycle_hours"].median()), 1)
        row["p90_hours"] = round(float(g["cycle_hours"].quantile(0.9)), 1)
        sat = g["Customer Satisfaction Rating"].dropna()
        row["avg_satisfaction"] = round(float(sat.mean()), 2) if len(sat) else None
        rows.append(row)
    return rows


def satisfaction_drivers(df: pd.DataFrame, v: pd.DataFrame) -> dict:
    """Mutual information between candidate drivers and CSAT, computed on the
    subset of tickets that actually have a rating (Closed tickets only).
    Mutual info (not plain correlation) so nonlinear/categorical relationships
    are captured, and it is reported honestly as association, not causation.
    """
    rated = df[df["Customer Satisfaction Rating"].notna()].copy()
    rated = rated.merge(
        v[["Ticket ID", "cycle_hours"]], on="Ticket ID", how="left"
    )
    cat_cols = ["Ticket Channel", "Ticket Priority", "Ticket Type", "Product Purchased"]
    features = rated[cat_cols].copy()
    enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    encoded = enc.fit_transform(features.astype(str))
    has_cycle = rated["cycle_hours"].notna()
    X_cat = encoded
    y = rated["Customer Satisfaction Rating"].to_numpy()

    mi_cat = mutual_info_regression(X_cat, y, discrete_features=True, random_state=42)

    cycle_vals = rated.loc[has_cycle, "cycle_hours"].to_numpy().reshape(-1, 1)
    y_cycle = rated.loc[has_cycle, "Customer Satisfaction Rating"].to_numpy()
    mi_cycle = mutual_info_regression(cycle_vals, y_cycle, discrete_features=False, random_state=42)[0] if len(cycle_vals) > 5 else 0.0

    age_vals = rated[["Customer Age"]].to_numpy()
    mi_age = mutual_info_regression(age_vals, y, discrete_features=False, random_state=42)[0]

    scores = {col: round(float(v_), 4) for col, v_ in zip(cat_cols, mi_cat)}
    scores["Time to Resolution (cycle_hours)"] = round(float(mi_cycle), 4)
    scores["Customer Age"] = round(float(mi_age), 4)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    by_channel = rated.groupby("Ticket Channel", observed=True)["Customer Satisfaction Rating"].mean().round(2).to_dict()
    by_priority = rated.groupby("Ticket Priority", observed=True)["Customer Satisfaction Rating"].mean().round(2).to_dict()
    by_type = rated.groupby("Ticket Type", observed=True)["Customer Satisfaction Rating"].mean().round(2).to_dict()

    rng = np.random.default_rng(42)
    def rating_summary(column):
        result = []
        for label, group in rated.groupby(column, observed=True):
            values = group["Customer Satisfaction Rating"].to_numpy()
            means = rng.choice(values, size=(2000, len(values)), replace=True).mean(axis=1)
            low, high = np.quantile(means, [0.025, 0.975])
            result.append({"label": label, "n": len(values), "mean": round(float(values.mean()), 2),
                           "ci95_low": round(float(low), 2), "ci95_high": round(float(high), 2)})
        return sorted(result, key=lambda row: row["mean"])

    return {
        "mutual_information_ranked": [{"feature": k, "mutual_info": v_} for k, v_ in ranked],
        "avg_satisfaction_by_channel": by_channel,
        "avg_satisfaction_by_priority": by_priority,
        "avg_satisfaction_by_type": by_type,
        "n_rated_tickets": int(len(rated)),
        "n_valid_for_time_association": int(has_cycle.sum()),
        "summaries": {"by_type": rating_summary("Ticket Type"), "by_channel": rating_summary("Ticket Channel"), "by_priority": rating_summary("Ticket Priority")},
        "uncertainty_method": "Intervalos de confiança de 95% por bootstrap: 2.000 reamostragens, seed 42. Exploratórios, sem correção por múltiplas comparações; não corrigem viés de seleção dos respondentes.",
        "interpretation": (
            "Nesta análise exploratória, a informação mútua estimada foi baixa para as variáveis "
            "avaliadas. Isso não prova independência nem ausência de efeito causal. "
            "As comparações de satisfação usam todas as 2.769 avaliações; a associação com duração "
            "usa somente os 1.402 pares positivos. Falta a abertura do chamado para avaliar "
            "a demora até a primeira resposta. Diferenças pequenas de médias não comprovam "
            "uma prioridade de melhoria; os intervalos mostram a incerteza amostral."
        ),
    }


def cycle_time_tail(v: pd.DataFrame) -> dict:
    """Describes the long tail in hours only — no cost conversion here.

    Cycle time (first response -> resolution) is calendar/queue time, not
    agent labor time, so pricing it directly at a loaded hourly rate would
    overstate recoverable cost (the exact "creative accounting" trap the
    brief warns against). The labor-cost ROI estimate lives in
    04_roi_model.py, where it is grounded in the classifier's measured
    auto-routable coverage instead of an arbitrary multiplier.
    """
    median = float(v["cycle_hours"].median())
    p90 = float(v["cycle_hours"].quantile(0.9))
    tail_excess = v.loc[v["cycle_hours"] > median, "cycle_hours"] - median
    share_in_tail = round(100 * len(tail_excess) / len(v), 1)

    # Hours only — real, measured, no cost conversion (see module docstring for why).
    sample_total_excess_hours = float(tail_excess.sum())
    avg_excess_per_tail_ticket = float(tail_excess.mean()) if len(tail_excess) else 0.0

    # Explicitly-labelled illustrative projection to the brief's stated annual volume,
    # in HOURS ONLY — no R$ attached here. It carries the same generalization risk as
    # any projection from a 1.402-ticket sample to 30.000/year, and is presented as such.
    annual_volume_assumed = 30_000
    projected_tail_tickets_per_year = annual_volume_assumed * (len(tail_excess) / len(v))
    projected_excess_hours_per_year = projected_tail_tickets_per_year * avg_excess_per_tail_ticket

    return {
        "median_cycle_hours": round(median, 1),
        "p90_cycle_hours": round(p90, 1),
        "p90_minus_median_hours": round(p90 - median, 1),
        "pct_tickets_above_median_in_long_tail": share_in_tail,
        "sample_size": int(len(v)),
        "sample_total_excess_hours_above_median": round(sample_total_excess_hours, 1),
        "avg_excess_hours_per_tail_ticket": round(avg_excess_per_tail_ticket, 1),
        "projected_annual_volume_assumed": annual_volume_assumed,
        "projected_excess_hours_per_year": round(projected_excess_hours_per_year, 0),
        "interpretation": (
            "O intervalo medido começa na primeira resposta e termina na resolução. "
            "A mediana é 6,4h e o P90 é 16h; cerca de metade dos tickets passa da mediana, "
            "e juntos esses casos somam horas de espera muito acima do típico. "
            "Não mede o tempo desde a abertura nem identifica a causa da demora. "
            "Espera, trabalho ativo e transferências não estão separados — são hipóteses "
            "a investigar, não uma medição de causa. Convertemos essa cauda em horas, "
            "nunca em R$: tempo de calendário não é hora de agente, e custeá-lo direto "
            "infla o número artificialmente. A única estimativa em R$ desta submissão "
            "fica na seção de ROI, ancorada na cobertura medida do classificador — uma "
            "pergunta diferente (potencial de automação, não desperdício observado)."
        ),
    }


def worst_offenders(v: pd.DataFrame) -> list[dict]:
    combos = group_stats(v, ["Ticket Channel", "Ticket Priority", "Ticket Type"], min_n=8)
    return sorted(combos, key=lambda r: r["p90_hours"], reverse=True)[:10]


def main() -> None:
    df = load()
    v = valid_cycle_time_frame(df)

    payload = {
        "data_quality": data_quality_report(df),
        "overall": {
            "n_valid": int(len(v)),
            "median_hours": round(float(v["cycle_hours"].median()), 1),
            "p90_hours": round(float(v["cycle_hours"].quantile(0.9)), 1),
            "avg_satisfaction": round(float(v["Customer Satisfaction Rating"].dropna().mean()), 2),
        },
        "by_channel": sorted(group_stats(v, ["Ticket Channel"]), key=lambda r: r["p90_hours"], reverse=True),
        "by_priority": sorted(group_stats(v, ["Ticket Priority"]), key=lambda r: r["p90_hours"], reverse=True),
        "by_type": sorted(group_stats(v, ["Ticket Type"]), key=lambda r: r["p90_hours"], reverse=True),
        "worst_combinations": worst_offenders(v),
        "satisfaction_drivers": satisfaction_drivers(df, v),
        "cycle_time_tail": cycle_time_tail(v),
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
