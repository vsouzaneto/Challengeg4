"""Carga, validação de schema e junção das quatro tabelas do CRM.

Regras que este módulo garante (cada uma tem teste em tests/test_data.py):
- as colunas esperadas existem em cada CSV; qualquer divergência falha com a lista real de colunas;
- nomes de produto são normalizados (o pipeline usa "GTXPro", o catálogo usa "GTX Pro");
- datas são convertidas; texto vazio vira NaT/NaN, nunca string vazia;
- a data de referência do dataset é max(close_date) dos deals fechados, nunca a data de hoje;
- a junção com accounts/products/sales_teams é do tipo left e não perde nenhuma oportunidade.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

SCHEMA = {
    "accounts.csv": ["account", "sector", "year_established", "revenue", "employees", "office_location", "subsidiary_of"],
    "products.csv": ["product", "series", "sales_price"],
    "sales_teams.csv": ["sales_agent", "manager", "regional_office"],
    "sales_pipeline.csv": ["opportunity_id", "sales_agent", "product", "account", "deal_stage", "engage_date", "close_date", "close_value"],
}
OPEN_STAGES = ("Prospecting", "Engaging")
CLOSED_STAGES = ("Won", "Lost")

# Divergências conhecidas entre o nome no pipeline e o nome no catálogo de produtos.
PRODUCT_ALIASES = {"GTXPro": "GTX Pro"}


class SchemaError(ValueError):
    pass


@dataclass(frozen=True)
class Tables:
    accounts: pd.DataFrame
    products: pd.DataFrame
    teams: pd.DataFrame
    pipeline: pd.DataFrame


def _read(path: Path, name: str) -> pd.DataFrame:
    df = pd.read_csv(path / name)
    expected = SCHEMA[name]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise SchemaError(f"{name}: colunas ausentes {missing}; colunas reais: {list(df.columns)}")
    return df


def normalize_product(name: object) -> object:
    if isinstance(name, str):
        return PRODUCT_ALIASES.get(name.strip(), name.strip())
    return name


def load_tables(raw_dir: Path | str) -> Tables:
    """Lê os 4 CSVs e aplica normalizações mínimas (sem inventar dados)."""
    raw_dir = Path(raw_dir)
    accounts = _read(raw_dir, "accounts.csv")
    products = _read(raw_dir, "products.csv")
    teams = _read(raw_dir, "sales_teams.csv")
    pipeline = _read(raw_dir, "sales_pipeline.csv")

    for df, col in ((accounts, "account"), (products, "product"), (teams, "sales_agent"),
                    (pipeline, "account"), (pipeline, "sales_agent"), (pipeline, "product")):
        df[col] = df[col].where(df[col].isna(), df[col].astype(str).str.strip())

    pipeline["product"] = pipeline["product"].map(normalize_product)
    products["product"] = products["product"].map(normalize_product)
    pipeline["engage_date"] = pd.to_datetime(pipeline["engage_date"], errors="coerce")
    pipeline["close_date"] = pd.to_datetime(pipeline["close_date"], errors="coerce")
    pipeline["close_value"] = pd.to_numeric(pipeline["close_value"], errors="coerce")
    return Tables(accounts=accounts, products=products, teams=teams, pipeline=pipeline)


def reference_date(pipeline: pd.DataFrame) -> pd.Timestamp:
    """'Hoje' para o dataset: a última data de fechamento observada.

    O dataset é histórico (2016-2017). Usar a data real de hoje faria todo deal parecer
    parado há anos; a review pública do challenge reprovou exatamente esse erro.
    """
    closed = pipeline.loc[pipeline["deal_stage"].isin(CLOSED_STAGES), "close_date"].dropna()
    if closed.empty:
        raise ValueError("não há deals fechados com close_date; impossível ancorar a data de referência")
    return closed.max().normalize()


def enrich(tables: Tables) -> pd.DataFrame:
    """Junta pipeline + accounts + products + teams com left joins que preservam todas as linhas."""
    p = tables.pipeline
    n = len(p)
    out = (p.merge(tables.products, on="product", how="left", validate="many_to_one")
            .merge(tables.accounts, on="account", how="left", validate="many_to_one")
            .merge(tables.teams, on="sales_agent", how="left", validate="many_to_one"))
    if len(out) != n:
        raise AssertionError(f"junção alterou o número de linhas: {n} -> {len(out)}")
    out["is_open"] = out["deal_stage"].isin(OPEN_STAGES)
    out["is_closed"] = out["deal_stage"].isin(CLOSED_STAGES)
    out["has_account"] = out["account"].notna()
    return out
