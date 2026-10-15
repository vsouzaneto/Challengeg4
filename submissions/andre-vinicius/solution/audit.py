"""Auditoria reproduzível dos CSVs do case 003, sem dependências externas."""
import csv
import hashlib
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

FILES = ("accounts", "products", "sales_teams", "sales_pipeline", "metadata")


def load(root: Path, name: str):
    path = root / f"{name}.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    return path, rows


def audit(root: Path):
    tables = {}
    summary = {"source": "Kaggle agungpambudi/crm-sales-predictive-analytics", "tables": {}}
    for name in FILES:
        path, rows = load(root, name)
        tables[name] = rows
        fields = list(rows[0]) if rows else []
        summary["tables"][name] = {
            "rows": len(rows),
            "columns": fields,
            "missing": {field: sum(not row[field].strip() for row in rows) for field in fields},
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    pipeline = tables["sales_pipeline"]
    ids = [row["opportunity_id"] for row in pipeline]
    accounts = {row["account"] for row in tables["accounts"]}
    products = {row["product"] for row in tables["products"]}
    agents = {row["sales_agent"] for row in tables["sales_teams"]}
    dates = [date.fromisoformat(row[field]) for row in pipeline for field in ("engage_date", "close_date") if row[field]]
    invalid_order = sum(bool(row["engage_date"] and row["close_date"] and row["close_date"] < row["engage_date"]) for row in pipeline)
    closed = [row for row in pipeline if row["deal_stage"] in ("Won", "Lost")]
    open_rows = [row for row in pipeline if row["deal_stage"] in ("Prospecting", "Engaging")]
    summary["pipeline_quality"] = {
        "stages": dict(Counter(row["deal_stage"] for row in pipeline)),
        "duplicate_opportunity_ids": len(ids) - len(set(ids)),
        "blank_accounts_by_stage": dict(Counter(row["deal_stage"] for row in pipeline if not row["account"])),
        "product_names_outside_catalog": dict(Counter(row["product"] for row in pipeline if row["product"] not in products)),
        "unknown_accounts": sum(bool(row["account"] and row["account"] not in accounts) for row in pipeline),
        "unknown_products": sum(row["product"] not in products for row in pipeline),
        "unknown_agents": sum(row["sales_agent"] not in agents for row in pipeline),
        "closed_without_close_date": sum(not row["close_date"] for row in closed),
        "open_with_close_date": sum(bool(row["close_date"]) for row in open_rows),
        "open_with_close_value": sum(bool(row["close_value"]) for row in open_rows),
        "close_before_engage": invalid_order,
        "first_date": min(dates).isoformat(),
        "last_date": max(dates).isoformat(),
    }
    return summary


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "data"
    print(json.dumps(audit(root), ensure_ascii=False, indent=2))
