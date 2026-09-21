import pandas as pd
import pytest

from leadscorer.data import SchemaError, enrich, load_tables, normalize_product, reference_date


def test_schema_error_lists_real_columns(tmp_path):
    (tmp_path / "accounts.csv").write_text("a,b\n1,2\n")
    with pytest.raises(SchemaError) as exc:
        load_tables(tmp_path)
    assert "colunas reais" in str(exc.value)


def test_product_alias_is_normalized(raw_dir):
    t = load_tables(raw_dir)
    assert "GTXPro" not in set(t.pipeline["product"])
    assert (t.pipeline["product"] == "GTX Pro").sum() == 3
    assert normalize_product(" GTXPro ") == "GTX Pro"
    assert normalize_product(None) is None


def test_dates_and_values_are_typed(raw_dir):
    t = load_tables(raw_dir)
    assert pd.api.types.is_datetime64_any_dtype(t.pipeline["engage_date"])
    assert pd.api.types.is_datetime64_any_dtype(t.pipeline["close_date"])
    assert t.pipeline["close_value"].dtype.kind == "f"
    assert t.pipeline.loc[t.pipeline["opportunity_id"] == "P1", "engage_date"].isna().all()


def test_reference_date_is_max_close_of_closed_deals_not_today(raw_dir):
    t = load_tables(raw_dir)
    ref = reference_date(t.pipeline)
    # E1 é aberto com close_date 2017-11-15 preenchida por engano: não pode ancorar a referência
    assert ref == pd.Timestamp("2017-05-01")
    assert ref < pd.Timestamp.today().normalize()


def test_enrich_keeps_every_row_and_flags(raw_dir):
    t = load_tables(raw_dir)
    e = enrich(t)
    assert len(e) == len(t.pipeline)
    assert e["is_open"].sum() == 5 and e["is_closed"].sum() == 4
    assert e.loc[e["opportunity_id"] == "E2", "has_account"].item() is False
    # após normalização, todo produto encontra preço
    assert e["sales_price"].notna().all()
    # vendedor fora de sales_teams fica sem manager, mas a linha permanece
    assert e.loc[e["opportunity_id"] == "E3", "manager"].isna().item()
