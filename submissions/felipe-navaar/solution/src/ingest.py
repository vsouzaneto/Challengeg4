"""Leitura, validação e enriquecimento das tabelas originais do CRM."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


RAW_FILES = ("accounts", "products", "sales_pipeline", "sales_teams")
REQUIRED_COLUMNS = {
    "accounts": {"account", "sector", "year_established", "revenue", "employees", "office_location", "subsidiary_of"},
    "products": {"product", "series", "sales_price"},
    "sales_pipeline": {"opportunity_id", "sales_agent", "product", "account", "deal_stage", "engage_date", "close_date", "close_value"},
    "sales_teams": {"sales_agent", "manager", "regional_office"},
}
PRODUCT_ALIASES = {"GTXPro": "GTX Pro"}
DATE_COLUMNS = ("engage_date", "close_date")


@dataclass(frozen=True)
class IngestionResult:
    """Tabela preparada e diagnóstico reproduzível da ingestão."""

    enriched: pd.DataFrame
    tables: dict[str, pd.DataFrame]
    diagnostics: dict[str, Any]


def _required_columns(table_name: str, frame: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_COLUMNS[table_name] - set(frame.columns))
    if missing:
        raise ValueError(f"{table_name}.csv: colunas obrigatórias ausentes: {', '.join(missing)}")


def _read_tables(data_dir: Path) -> dict[str, pd.DataFrame]:
    tables: dict[str, pd.DataFrame] = {}
    for table_name in RAW_FILES:
        path = data_dir / f"{table_name}.csv"
        if not path.is_file():
            raise FileNotFoundError(f"Arquivo obrigatório ausente: {path}")
        frame = pd.read_csv(path)
        _required_columns(table_name, frame)
        tables[table_name] = frame
    return tables


def _validate_dimension_keys(tables: dict[str, pd.DataFrame]) -> None:
    for table_name, key in (("accounts", "account"), ("products", "product"), ("sales_teams", "sales_agent")):
        frame = tables[table_name]
        if frame[key].isna().any():
            raise ValueError(f"{table_name}.csv: chave {key!r} contém valores ausentes")
        if frame[key].duplicated().any():
            duplicates = frame.loc[frame[key].duplicated(), key].astype(str).tolist()
            raise ValueError(f"{table_name}.csv: chave {key!r} duplicada: {duplicates[:5]}")


def _parse_dates(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    parsed = frame.copy()
    invalid: dict[str, int] = {}
    for column in DATE_COLUMNS:
        original_non_null = parsed[column].notna()
        parsed[column] = pd.to_datetime(parsed[column], errors="coerce")
        invalid[column] = int((original_non_null & parsed[column].isna()).sum())
    return parsed, invalid


def load_and_prepare(data_dir: str | Path | None = None) -> IngestionResult:
    """Carrega os CSVs reais, valida chaves e faz os left joins do pipeline.

    Quando ``data_dir`` não é informado, o caminho é resolvido a partir da raiz
    do projeto (e não do diretório corrente). Os arquivos de ``data/raw`` nunca
    são escritos ou alterados.
    """

    project_root = Path(__file__).resolve().parents[1]
    raw_dir = Path(data_dir) if data_dir is not None else project_root / "data" / "raw"
    tables = _read_tables(raw_dir)
    _validate_dimension_keys(tables)

    pipeline, invalid_dates = _parse_dates(tables["sales_pipeline"])
    if pipeline["opportunity_id"].isna().any():
        raise ValueError("sales_pipeline.csv: opportunity_id contém valores ausentes")
    close_value_non_null = pipeline["close_value"].notna()
    close_value_numeric = pd.to_numeric(pipeline["close_value"], errors="coerce")
    pipeline["close_value"] = pd.to_numeric(pipeline["close_value"], errors="coerce")
    pipeline["product_raw"] = pipeline["product"]
    pipeline["product"] = pipeline["product"].replace(PRODUCT_ALIASES)

    product_keys = set(tables["products"]["product"])
    agent_keys = set(tables["sales_teams"]["sales_agent"])
    account_keys = set(tables["accounts"]["account"])
    diagnostics: dict[str, Any] = {
        "raw_rows": {name: int(len(frame)) for name, frame in tables.items()},
        "pipeline_unique_ids": int(pipeline["opportunity_id"].nunique(dropna=False)),
        "duplicate_opportunity_ids": int(pipeline["opportunity_id"].duplicated().sum()),
        "product_alias_counts": {alias: int((pipeline["product_raw"] == alias).sum()) for alias in PRODUCT_ALIASES},
        "missing_account_rows": int(pipeline["account"].isna().sum()),
        "missing_engage_date_rows": int(pipeline["engage_date"].isna().sum()),
        "invalid_dates": invalid_dates,
        "invalid_close_value_rows": int((close_value_non_null & close_value_numeric.isna()).sum()),
        "unmatched_products": sorted(set(pipeline["product"].dropna()) - product_keys),
        "unmatched_sales_agents": sorted(set(pipeline["sales_agent"].dropna()) - agent_keys),
        "unmatched_accounts": sorted(set(pipeline["account"].dropna()) - account_keys),
    }
    if diagnostics["duplicate_opportunity_ids"]:
        raise ValueError("sales_pipeline.csv: opportunity_id duplicado")

    enriched = pipeline.merge(
        tables["products"].rename(columns={"product": "product_key"}),
        left_on="product",
        right_on="product_key",
        how="left",
        validate="many_to_one",
        indicator="product_join",
    ).drop(columns=["product_key"])
    enriched = enriched.merge(
        tables["sales_teams"],
        on="sales_agent",
        how="left",
        validate="many_to_one",
        indicator="sales_team_join",
    )
    enriched = enriched.merge(
        tables["accounts"].add_prefix("account_"),
        left_on="account",
        right_on="account_account",
        how="left",
        validate="many_to_one",
        indicator="account_join",
    ).drop(columns=["account_account"])

    diagnostics.update(
        {
            "rows_after_joins": int(len(enriched)),
            "unmatched_product_join_rows": int((enriched["product_join"] == "left_only").sum()),
            "unmatched_sales_team_join_rows": int((enriched["sales_team_join"] == "left_only").sum()),
            "unmatched_account_join_rows": int((enriched["account_join"] == "left_only").sum()),
            "open_rows": int(enriched["deal_stage"].isin(["Engaging", "Prospecting"]).sum()),
        }
    )
    return IngestionResult(enriched=enriched, tables=tables, diagnostics=diagnostics)


def ingest(data_dir: str | Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Atalho compatível com o contrato: retorna tabela enriquecida e diagnóstico."""

    result = load_and_prepare(data_dir)
    return result.enriched, result.diagnostics
