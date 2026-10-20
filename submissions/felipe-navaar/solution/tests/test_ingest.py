from pathlib import Path

import pandas as pd
import pytest

from src.ingest import load_and_prepare


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_real_csvs_reconcile_and_preserve_missing_accounts():
    result = load_and_prepare(PROJECT_ROOT / "data" / "raw")

    assert len(result.enriched) == 8800
    assert result.enriched["opportunity_id"].nunique() == 8800
    assert result.diagnostics["open_rows"] == 2089
    assert result.diagnostics["product_alias_counts"]["GTXPro"] == 1480
    assert result.diagnostics["unmatched_product_join_rows"] == 0
    assert result.diagnostics["missing_account_rows"] == 1425
    assert result.enriched["account"].isna().sum() == 1425
    assert result.enriched["product_raw"].eq("GTXPro").sum() == 1480
    assert result.enriched.loc[result.enriched["product_raw"] == "GTXPro", "product"].eq("GTX Pro").all()


def test_missing_required_file_is_reported(tmp_path):
    with pytest.raises(FileNotFoundError, match="Arquivo obrigatório ausente"):
        load_and_prepare(tmp_path)


def test_duplicate_dimension_key_is_reported(tmp_path):
    raw = PROJECT_ROOT / "data" / "raw"
    for name in ("accounts", "products", "sales_pipeline", "sales_teams"):
        (tmp_path / f"{name}.csv").write_bytes((raw / f"{name}.csv").read_bytes())
    teams = pd.read_csv(tmp_path / "sales_teams.csv")
    teams = pd.concat([teams, teams.iloc[[0]]], ignore_index=True)
    teams.to_csv(tmp_path / "sales_teams.csv", index=False)

    with pytest.raises(ValueError, match="chave 'sales_agent' duplicada"):
        load_and_prepare(tmp_path)


def test_unknown_product_is_diagnosed_without_dropping_opportunity(tmp_path):
    raw = PROJECT_ROOT / "data" / "raw"
    for name in ("accounts", "products", "sales_pipeline", "sales_teams"):
        (tmp_path / f"{name}.csv").write_bytes((raw / f"{name}.csv").read_bytes())
    pipeline = pd.read_csv(tmp_path / "sales_pipeline.csv")
    pipeline.loc[0, "product"] = "Produto inexistente"
    pipeline.to_csv(tmp_path / "sales_pipeline.csv", index=False)

    result = load_and_prepare(tmp_path)

    assert len(result.enriched) == 8800
    assert result.diagnostics["unmatched_products"] == ["Produto inexistente"]
    assert result.diagnostics["unmatched_product_join_rows"] == 1

