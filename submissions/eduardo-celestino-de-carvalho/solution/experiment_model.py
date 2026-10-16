"""Executa a comparação do G2 sem gravar o dataset nem um modelo serializado."""

from __future__ import annotations

import json
import argparse
from pathlib import Path

from leadscore.data import ARCHIVE_NAME, download_archive, load_dataset
from leadscore.model import (
    HORIZON_DAYS, TEST_END, TEST_LABEL_END, TEST_START, TRAIN_END,
    VALIDATION_END, VALIDATION_LABEL_END, VALIDATION_START,
    known_outcomes, resolved_cohort, score_methods,
)


def run() -> dict:
    dataset = load_dataset(download_archive(Path("data") / ARCHIVE_NAME))
    initial_train = known_outcomes(dataset, TRAIN_END)
    validation = resolved_cohort(dataset, VALIDATION_START, VALIDATION_END,
                                 VALIDATION_LABEL_END)
    validation_results = score_methods(dataset, initial_train, validation)

    # A regra de escolha está fixada antes de consultar as métricas do teste.
    # Ganhos nos cinco primeiros por vendedor é o critério principal.
    choice = max(validation_results,
                 key=lambda name: (validation_results[name]["wins_at_5"],
                                   validation_results[name]["revenue_at_5"],
                                   -validation_results[name].get("brier", 1.0)))
    final_train = known_outcomes(dataset, VALIDATION_LABEL_END)
    test = resolved_cohort(dataset, TEST_START, TEST_END, TEST_LABEL_END)
    test_results = score_methods(dataset, final_train, test)

    def unresolved(start, end):
        return sum(o.engage_date is not None and start <= o.engage_date <= end
                   and (o.close_date is None or
                        (o.close_date - o.engage_date).days > HORIZON_DAYS)
                   for o in dataset.opportunities)

    return {
        "source_sha256": dataset.archive_sha256,
        "design": {
            "train_close_by": TRAIN_END.isoformat(),
            "validation_engage_from": VALIDATION_START.isoformat(),
            "validation_engage_through": VALIDATION_END.isoformat(),
            "validation_labels_available_by": VALIDATION_LABEL_END.isoformat(),
            "retrain_close_by": VALIDATION_LABEL_END.isoformat(),
            "test_engage_from": TEST_START.isoformat(),
            "test_engage_through": TEST_END.isoformat(),
            "test_labels_available_by": TEST_LABEL_END.isoformat(),
            "outcome_horizon_days": HORIZON_DAYS,
            "initial_train_n": len(initial_train),
            "retrain_n": len(final_train),
            "validation_not_resolved_within_horizon": unresolved(VALIDATION_START, VALIDATION_END),
            "test_not_resolved_within_horizon": unresolved(TEST_START, TEST_END),
        },
        "selected_on_validation": choice,
        "validation": validation_results,
        "test": test_results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="salva resultados agregados em JSON")
    args = parser.parse_args()
    report = json.dumps(run(), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
