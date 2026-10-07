"""Gera a carteira de demonstração com Priority Score a partir dos CSVs."""

import csv
import json
import math
import sys
from collections import Counter
from datetime import date
from pathlib import Path


# O dataset termina em 2017; usar a data atual tornaria todos os deals obsoletos.
AS_OF = date(2017, 12, 31)
SECTOR_PRIOR_DEALS = 100
ACCOUNT_PRIOR_DEALS = 50


def read_csv(folder: Path, name: str):
    with (folder / name).open(newline="", encoding="utf-8-sig") as source:
        return list(csv.DictReader(source))


def as_int(value):
    return int(value) if value else None


def as_float(value):
    return float(value) if value else None


def normalized_product(value):
    return "GTX Pro" if value == "GTXPro" else value


def normalized_sector(value):
    return value.replace("technolgy", "technology") if value else None


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def employee_points(value, thresholds):
    if value is None:
        return 1.25
    quartile = 1 + sum(value > threshold for threshold in thresholds)
    return quartile * 0.5


def momentum_points(stage, engage_date):
    if stage == "Prospecting":
        return 30, None
    if not engage_date:
        return 30, None
    days = max(0, (AS_OF - date.fromisoformat(engage_date)).days)
    if days <= 104:
        return 60, days
    if days <= 138:
        return 35, days
    return 10, days


def main(folder: Path):
    accounts = {row["account"]: row for row in read_csv(folder, "accounts.csv")}
    products = {row["product"]: row for row in read_csv(folder, "products.csv")}
    sellers = {row["sales_agent"]: row for row in read_csv(folder, "sales_teams.csv")}
    pipeline = read_csv(folder, "sales_pipeline.csv")

    closed = [
        row for row in pipeline
        if row["deal_stage"] in {"Won", "Lost"}
        and row["close_date"]
        and date.fromisoformat(row["close_date"]) <= AS_OF
    ]
    global_rate = sum(row["deal_stage"] == "Won" for row in closed) / len(closed)
    product_count = Counter(normalized_product(row["product"]) for row in closed)
    product_wins = Counter(normalized_product(row["product"]) for row in closed if row["deal_stage"] == "Won")
    account_count = Counter(row["account"] for row in closed)
    account_wins = Counter(row["account"] for row in closed if row["deal_stage"] == "Won")
    sector_product_count = Counter(
        (normalized_sector(accounts[row["account"]]["sector"]), normalized_product(row["product"]))
        for row in closed if row["account"] in accounts
    )
    sector_product_wins = Counter(
        (normalized_sector(accounts[row["account"]]["sector"]), normalized_product(row["product"]))
        for row in closed if row["account"] in accounts and row["deal_stage"] == "Won"
    )

    prices = sorted(int(row["sales_price"]) for row in products.values())
    min_price, max_price = prices[0], prices[-1]
    employees = sorted(int(row["employees"]) for row in accounts.values())
    employee_thresholds = [employees[index] for index in (20, 41, 62)]

    opportunities = []
    for row in pipeline:
        if row["deal_stage"] not in {"Engaging", "Prospecting"}:
            continue

        product_name = normalized_product(row["product"])
        account = accounts.get(row["account"])
        product = products.get(product_name)
        seller = sellers.get(row["sales_agent"])
        sector = normalized_sector(account["sector"]) if account else None
        price = as_int(product["sales_price"]) if product else None
        employee_count = as_int(account["employees"]) if account else None

        momentum, days_in_engaging = momentum_points(row["deal_stage"], row["engage_date"])
        value = (
            25 * clamp(math.log(price / min_price) / math.log(max_price / min_price), 0, 1)
            if price else 12.5
        )

        # A média do produto serve de referência para combinações setor × produto.
        product_rate = product_wins[product_name] / product_count[product_name] if product_count[product_name] else global_rate
        cell = (sector, product_name)
        cell_count = sector_product_count[cell]
        cell_rate = (
            (sector_product_wins[cell] + SECTOR_PRIOR_DEALS * product_rate)
            / (cell_count + SECTOR_PRIOR_DEALS)
        )
        sector_fit = clamp(4 + 50 * (cell_rate - product_rate), 0, 8) if sector else 4
        size_fit = employee_points(employee_count, employee_thresholds)
        fit = sector_fit + size_fit if account else 5

        if account:
            account_name = row["account"]
            historical_rate = (
                account_wins[account_name] + ACCOUNT_PRIOR_DEALS * global_rate
            ) / (account_count[account_name] + ACCOUNT_PRIOR_DEALS)
            history = clamp(2.5 + 20 * (historical_rate - global_rate), 0, 5)
        else:
            history = 2.5

        score = int(math.floor(momentum + value + fit + history + 0.5))
        opportunities.append(
            {
                "id": row["opportunity_id"],
                "stage": row["deal_stage"],
                "engageDate": row["engage_date"] or None,
                "daysInEngaging": days_in_engaging,
                "account": row["account"] or None,
                "sector": sector,
                "companyRevenueM": as_float(account["revenue"]) if account else None,
                "employees": employee_count,
                "country": account["office_location"] if account else None,
                "product": product_name,
                "series": product["series"] if product else None,
                "listPrice": price,
                "agent": row["sales_agent"],
                "manager": seller["manager"] if seller else None,
                "office": seller["regional_office"] if seller else None,
                "priority_score": score,
                "score_confidence": "partial" if account else "limited",
                "score_components": {
                    "momentum": momentum,
                    "value": round(value, 2),
                    "fit": round(fit, 2),
                    "history": round(history, 2),
                },
            }
        )

    destination = Path(__file__).resolve().parents[1] / "data.json"
    destination.write_text(
        json.dumps(opportunities, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    scored = {item["id"]: item for item in opportunities}
    export_path = destination.with_name("sales_pipeline_scored.csv")
    fields = [*pipeline[0].keys(), "priority_score", "score_confidence", "score_as_of"]
    with export_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in pipeline:
            item = scored.get(row["opportunity_id"])
            writer.writerow({
                **row,
                "priority_score": item["priority_score"] if item else "",
                "score_confidence": item["score_confidence"] if item else "",
                "score_as_of": AS_OF.isoformat() if item else "",
            })
    print(f"{len(opportunities)} oportunidades com Priority Score gravadas em {destination} e {export_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("uso: python3 scripts/build_data.py /pasta/dos/csvs")
    main(Path(sys.argv[1]))
