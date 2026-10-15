"""Motor explicável de priorização do case 003, usando apenas sinais disponíveis antes do fechamento."""
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

PRODUCT_ALIASES = {"GTXPro": "GTX Pro"}
OPEN_STAGES = {"Prospecting", "Engaging"}
CLOSED_STAGES = {"Won", "Lost"}
# Data de corte fixa do conjunto histórico. Não inferir a referência de close_date,
# pois mudanças nos desfechos não podem alterar a posição das oportunidades abertas.
DATASET_AS_OF = date(2017, 12, 31)


def read_csv(root: Path, name: str):
    with (root / f"{name}.csv").open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def canonical_product(value: str):
    return PRODUCT_ALIASES.get(value, value)


def load_data(root: Path):
    pipeline = read_csv(root, "sales_pipeline")
    accounts = {row["account"]: row for row in read_csv(root, "accounts")}
    products = {row["product"]: row for row in read_csv(root, "products")}
    agents = {row["sales_agent"]: row for row in read_csv(root, "sales_teams")}
    for row in pipeline:
        row["product_key"] = canonical_product(row["product"])
        row["sector"] = accounts.get(row["account"], {}).get("sector", "")
        row["manager"] = agents.get(row["sales_agent"], {}).get("manager", "")
        row["region"] = agents.get(row["sales_agent"], {}).get("regional_office", "")
        row["catalog_price"] = float(products.get(row["product_key"], {}).get("sales_price", 0) or 0)
    return pipeline


def _counts(rows, field):
    result = defaultdict(lambda: [0, 0])
    for row in rows:
        key = row[field]
        if key:
            result[key][0] += 1 if row["deal_stage"] == "Won" else 0
            result[key][1] += 1
    return result


def fit_history(closed, smoothing=30):
    """Média suavizada por produto e setor; sem agente/manager para evitar prêmio circular."""
    rows = [row for row in closed if row["deal_stage"] in CLOSED_STAGES]
    base = sum(row["deal_stage"] == "Won" for row in rows) / len(rows) if rows else 0.5
    return {"base": base, "smoothing": smoothing, "product": _counts(rows, "product_key"), "sector": _counts(rows, "sector")}


def smoothed(model, field, key):
    wins, n = model[field].get(key, [0, 0])
    strength = model["smoothing"]
    return (wins + strength * model["base"]) / (n + strength), n


def affinity(model, row):
    product_rate, product_n = smoothed(model, "product", row["product_key"])
    sector_rate, sector_n = smoothed(model, "sector", row.get("sector", ""))
    # Sem conta, o setor não existe; o produto recebe todo o peso.
    value = 0.65 * product_rate + 0.35 * sector_rate if sector_n else product_rate
    return value, {"product_rate": product_rate, "product_n": product_n, "sector_rate": sector_rate if sector_n else None, "sector_n": sector_n}


def prioritize(row, as_of: date):
    if row["deal_stage"] not in OPEN_STAGES:
        raise ValueError("Somente oportunidades abertas podem ser priorizadas")
    age_days = (as_of - date.fromisoformat(row["engage_date"])).days if row["engage_date"] else None
    stale = age_days is not None and age_days > 90
    if row["deal_stage"] == "Prospecting":
        queue, base, action = "Qualificar", 35, "Fazer primeiro contato e registrar resposta"
    elif stale:
        queue, base, action = "Revisar", 50, "Confirmar interesse; atualizar data do próximo passo ou encerrar"
    else:
        queue, base, action = "Avançar", 65, "Retomar conversa e combinar próximo passo com data"
    # Preço de catálogo é um proxy de impacto, não valor previsto de fechamento.
    price_bonus = 10 if row["catalog_price"] >= 4000 else 0
    account_bonus = 10 if row["account"] else 0
    timing_bonus = 10 if queue == "Avançar" and age_days is not None and age_days <= 30 else 0
    timing_bonus += 10 if queue == "Revisar" and age_days is not None and age_days >= 180 else 0
    priority = min(100, base + price_bonus + account_bonus + timing_bonus)
    if stale:
        timing_reason = f"{age_days} dias desde o engajamento; negócio precisa de confirmação"
    elif age_days is not None:
        timing_reason = f"{age_days} dias desde o engajamento"
    else:
        timing_reason = "Ainda sem data de engajamento"
    reasons = [f"Fila {queue}: {row['deal_stage']}", timing_reason]
    reasons.append("Conta identificada" if row["account"] else "Conta ausente: preencher antes de avançar")
    if price_bonus:
        reasons.append("Produto de maior preço de catálogo; impacto potencial, não previsão")
    else:
        reasons.append("Preço de catálogo usado apenas como contexto")
    return {
        "id": row["opportunity_id"], "account": row["account"] or "Conta não informada",
        "product": row["product_key"], "agent": row["sales_agent"], "manager": row["manager"],
        "region": row["region"], "sector": row["sector"], "stage": row["deal_stage"],
        "queue": queue, "priority": priority, "catalog_price": row["catalog_price"],
        "days_engaged": age_days, "next_action": action, "reasons": reasons,
    }


def rank_open(rows, as_of=None):
    as_of = as_of or DATASET_AS_OF
    ranked = [prioritize(row, as_of) for row in rows if row["deal_stage"] in OPEN_STAGES]
    queue_order = {"Avançar": 0, "Revisar": 1, "Qualificar": 2}
    ranked.sort(key=lambda row: (queue_order[row["queue"]], -row["priority"], row["id"]))
    return as_of, ranked
