"""Run the diagnosis (bottlenecks, satisfaction drivers, waste) and write outputs/diagnosis/diagnosis.json.

Run from the solution folder:  uv run python scripts/run_diagnosis.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from support_triage.diagnosis import bottlenecks, csat_drivers, prepare
from support_triage.paths import OUTPUTS_DIR, TICKETS_DIR
from support_triage.waste import ASSUMPTIONS, estimate, with_measured_routing

OUT = OUTPUTS_DIR / "diagnosis"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = prepare(pd.read_csv(TICKETS_DIR / "customer_support_tickets.csv"))
    # Routing share and misroute rate come from the classifier once it has been trained (train_classifier.py).
    metrics_path = OUTPUTS_DIR / "classifier" / "metrics.json"
    assumptions = ASSUMPTIONS
    if metrics_path.exists():
        assumptions = with_measured_routing(
            json.loads(metrics_path.read_text(encoding="utf-8"))
        )
    result = {
        "bottlenecks": bottlenecks(df),
        "csat_drivers": csat_drivers(df),
        "waste": estimate(assumptions),
    }
    (OUT / "diagnosis.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"wrote {OUT / 'diagnosis.json'}")


if __name__ == "__main__":
    main()
