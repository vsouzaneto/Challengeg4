from leadscorer import data, policy, triage

from conftest import PIPELINE, write_raw


def test_every_join_keeps_all_rows(raw_dir):
    dataset = data.load(raw_dir)
    assert [step.rows for step in dataset.steps] == [len(PIPELINE)] * 4
    assert len(dataset.opportunities) == len(PIPELINE)


def test_gtxpro_is_normalized_and_priced(raw_dir):
    frame = data.load(raw_dir).opportunities
    assert "GTXPro" not in set(frame["product"])
    assert frame["sales_price"].notna().all()
    assert frame.loc[frame["opportunity_id"] == "EGP", "sales_price"].item() == 4821


def test_gtxpro_regression_without_map(raw_dir):
    gtxpro_rows = sum(row["product"] == "GTXPro" for row in PIPELINE)
    dataset = data.load(raw_dir)
    assert dataset.unmatched_without_map == gtxpro_rows
    raw = {t: data.read_table(raw_dir, t) for t in data.TABLES}
    assert data.unmatched_products(raw["sales_pipeline"], raw["products"], policy.PRODUCT_MAP).empty


def test_load_is_read_only(raw_dir):
    before = {t: data.sha256(raw_dir / f"{t}.csv") for t in data.TABLES}
    data.load(raw_dir)
    assert {t: data.sha256(raw_dir / f"{t}.csv") for t in data.TABLES} == before


def test_fixture_is_not_the_audited_version(raw_dir):
    assert data.load(raw_dir).audited is False


def test_dates_are_parsed_and_empty_stays_null(raw_dir):
    frame = data.load(raw_dir).opportunities.set_index("opportunity_id")
    assert str(frame.loc["E138", "engage_date"].date()) == "2017-08-15"
    assert frame.loc[["P1"], "engage_date"].isna().all()
    assert frame.loc[["EPP"], "account"].isna().all()


def test_close_value_is_loaded_but_never_classified(raw_dir):
    dataset = data.load(raw_dir)
    values = dataset.opportunities.set_index("opportunity_id")["close_value"]
    assert (values["W1"], values["L1"]) == (100, 0) and values[["E138", "P1"]].isna().all()
    classified = triage.classify(dataset.opportunities, triage.resolve_context(dataset.opportunities))
    assert "close_value" not in classified.columns  # a regra só enxerga CLASSIFICATION_FIELDS


def test_won_without_value_is_not_an_error(tmp_path):
    rows = [dict(row) for row in PIPELINE]
    rows[0]["close_value"] = ""
    values = data.load(write_raw(tmp_path / "raw", sales_pipeline=rows)).opportunities["close_value"]
    assert values.isna().sum() == 1 + sum(not row["close_value"] for row in PIPELINE)


def test_account_attributes_stay_out_of_the_scoring_frame(raw_dir):
    dataset = data.load(raw_dir)
    assert not {"sector", "revenue", "office_location"} & set(dataset.opportunities.columns)
    accounts = dataset.accounts.set_index("account")
    assert accounts.loc["Acme", "sector"] == "technology"           # grafia corrigida (LABEL_MAPS)
    assert accounts.loc["Acme", "office_location"] == "Philippines"
    assert accounts.loc["Beta Corp", "revenue"] == 250.5
