"""Validação cronológica da afinidade histórica; não valida os bônus heurísticos de estágio/idade."""
import json
import sys
from datetime import date
from pathlib import Path
from scoring import CLOSED_STAGES, affinity, fit_history, load_data


def auc(pairs):
    # Mann–Whitney com empates: probabilidade de um Won ter score maior que um Lost.
    wins = [score for score, label in pairs if label]
    losses = [score for score, label in pairs if not label]
    if not wins or not losses:
        return None
    comparisons = sum((w > l) + 0.5 * (w == l) for w in wins for l in losses)
    return comparisons / (len(wins) * len(losses))


def evaluate(rows):
    closed = sorted((row for row in rows if row["deal_stage"] in CLOSED_STAGES), key=lambda row: (row["close_date"], row["opportunity_id"]))
    cutoff = closed[int(len(closed) * 0.8)]["close_date"]
    train = [row for row in closed if row["close_date"] < cutoff]
    test = [row for row in closed if row["close_date"] >= cutoff]
    model = fit_history(train)
    scored = sorted(((affinity(model, row)[0], row["deal_stage"] == "Won") for row in test), reverse=True)
    quartile = max(1, len(scored) // 4)
    top = scored[:quartile]
    return {
        "cutoff": cutoff, "train_rows": len(train), "test_rows": len(test),
        "train_win_rate": round(model["base"], 4),
        "test_win_rate": round(sum(label for _, label in scored) / len(scored), 4),
        "top_quartile_win_rate": round(sum(label for _, label in top) / len(top), 4),
        "auc_affinity_only": round(auc(scored), 4),
        "scope": "Apenas afinidade por produto/setor; estágio e idade não podem ser retrotestados com este dataset sem histórico de estágios.",
    }


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "data"
    print(json.dumps(evaluate(load_data(root)), ensure_ascii=False, indent=2))
