"""Run the data audit for both datasets and write the results to outputs/audit/.

Run from the solution folder:  uv run python scripts/run_audit.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from support_triage.audit import audit_d1, audit_d2
from support_triage.paths import IT_TICKETS_DIR, OUTPUTS_DIR, TICKETS_DIR

OUT = OUTPUTS_DIR / "audit"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    d1 = audit_d1(TICKETS_DIR / "customer_support_tickets.csv")
    (OUT / "audit_d1.json").write_text(
        json.dumps(d1, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    d2 = audit_d2(IT_TICKETS_DIR / "all_tickets_processed_improved_v3.csv")
    (OUT / "audit_d2.json").write_text(
        json.dumps(d2, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"wrote {OUT / 'audit_d1.json'} and {OUT / 'audit_d2.json'}")


if __name__ == "__main__":
    main()
