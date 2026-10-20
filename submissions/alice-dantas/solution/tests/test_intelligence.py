"""Inteligência comercial (ADR-007): números que fecham, a mesma política da Equipe e regras
determinísticas de diagnósticos e descobertas. Sintético primeiro; os oráculos reais no fim."""
import math

import pytest

from api import schemas
from leadscorer import codes, data, intelligence, policy, triage, views
from leadscorer.errors import PolicyError
from leadscorer.intelligence import Filters

from conftest import INTEL_TABLES, write_raw

ROWS = INTEL_TABLES["sales_pipeline"]
CLOSED = [r for r in ROWS if r["deal_stage"] in policy.CLOSED_STAGES]
WON = [r for r in CLOSED if r["deal_stage"] == "Won"]


@pytest.fixture(scope="module")
def intel(tmp_path_factory):
    return data.load(write_raw(tmp_path_factory.mktemp("intel"), **INTEL_TABLES))


@pytest.fixture(scope="module")
def page(intel):
    return intelligence.payload(intel)


def by_dimension(payload, dimension):
    return next(b for b in payload["breakdowns"] if b["dimension"] == dimension)


def walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def test_history_is_computed_from_the_rows(page):
    history = page["history"]
    assert (history["closed"], history["won"], history["lost"]) == (len(CLOSED), len(WON), len(CLOSED) - len(WON))
    assert history["revenue"] == sum(int(r["close_value"]) for r in WON)
    assert history["ticket"] == round(history["revenue"] / len(WON), 2)
    assert history["win_rate"]["value"] == round(len(WON) / len(CLOSED), 6)
    assert history["win_rate"]["low"] < history["win_rate"]["value"] < history["win_rate"]["high"]
    assert page["history_empty"] is None


def test_wilson_matches_the_real_reference():
    assert intelligence.wilson(4238, 6711) == {"value": 0.631501, "low": 0.619887, "high": 0.642964}
    assert intelligence.wilson(0, 0) is None


@pytest.mark.parametrize("manager, office, as_of", [
    (None, None, None), ("Mara Um", None, None), (None, "East", None), ("Ninguem", None, None),
    (None, None, "2030-01-01"),
])
def test_open_deals_follow_the_team_policy(intel, manager, office, as_of):
    """Os grupos das abertas são os da Equipe para o mesmo recorte e as_of (mesma política)."""
    page = intelligence.payload(intel, Filters(manager=manager, office=office), as_of)
    team = views.team_pipeline(intel, manager, office, as_of)
    assert page["open"]["summary"] == team["summary"]
    assert page["meta"] == team["meta"] and page["ordering"] == team["ordering"]


def test_every_breakdown_adds_up_to_the_totals(page):
    totals = {**{k: page["history"][k] for k in ("closed", "won", "lost", "revenue")},
              "open": page["open"]["summary"]["total"]}
    assert [b["dimension"] for b in page["breakdowns"]] == list(codes.DIMENSIONS)
    for b in page["breakdowns"]:
        sums = {k: sum(s["history"][k] for s in b["segments"]) for k in ("closed", "won", "lost", "revenue")}
        sums["open"] = sum(s["open"] for s in b["segments"])
        assert sums == totals, b["dimension"]
        shares = [s["revenue_share"] for s in b["segments"]]
        assert math.isclose(sum(shares), 1, abs_tol=1e-3), b["dimension"]


def test_people_are_alphabetical_with_zeros_and_never_ranked(page):
    for dimension in codes.PEOPLE_DIMENSIONS:
        b = by_dimension(page, dimension)
        keys = [s["key"] for s in b["segments"]]
        assert b["order"] == codes.ORDER_ALPHABETICAL and keys == sorted(keys), dimension
    sellers = {s["key"]: s for s in by_dimension(page, codes.DIM_SELLER)["segments"]}
    assert sellers["Fabio Zeta"]["history"]["closed"] == 0  # da equipe, sem oportunidade: aparece com zero
    products = by_dimension(page, codes.DIM_PRODUCT)
    revenues = [s["history"]["revenue"] for s in products["segments"]]
    assert products["order"] == codes.ORDER_REVENUE_DESC and revenues == sorted(revenues, reverse=True)


def test_account_rows_carry_the_profile_and_the_unknown_client_row(page):
    accounts = by_dimension(page, codes.DIM_ACCOUNT)["segments"]
    assert accounts[-1]["key"] is None and accounts[-1]["open"] == 3 and accounts[-1]["profile"] is None
    first = next(s for s in accounts if s["key"] == "Cliente 7")
    assert first["profile"]["sector"] == "finance" and first["profile"]["products_total"] == 4
    assert all(s["profile"]["sellers"] >= 1 for s in accounts if s["key"])


def test_chance_verdicts_and_bonferroni(page):
    verdicts = {b["dimension"]: b["chance"]["verdict"] for b in page["breakdowns"]}
    assert verdicts[codes.DIM_PRODUCT] == codes.CHANCE_BEYOND
    assert verdicts[codes.DIM_SELLER] == codes.CHANCE_WITHIN
    assert verdicts[codes.DIM_SECTOR] == codes.CHANCE_TOO_FEW  # só o varejo tem 20 fechadas
    assert all(b["chance"]["alpha"] == round(0.05 / 7, 6) for b in page["breakdowns"])


def test_drivers_add_up_and_need_enough_segments(page):
    for b in page["breakdowns"]:
        d = b["drivers"]
        if d is None:
            assert len([s for s in b["segments"] if s["key"] and s["history"]["revenue"]]) < 4, b["dimension"]
            continue
        assert math.isclose(d["volume_share"] + d["conversion_share"] + d["ticket_share"], 1, abs_tol=1e-3)
    assert by_dimension(page, codes.DIM_OFFICE)["drivers"] is None
    assert by_dimension(page, codes.DIM_PRODUCT)["drivers"]["main"] == [codes.DRIVER_TICKET]


def test_matrix_is_the_seller_mix(page):
    sellers = {s["key"]: s["history"]["closed"] for s in by_dimension(page, codes.DIM_SELLER)["segments"]}
    matrix = page["matrix"]
    assert [r["seller"] for r in matrix["rows"]] == sorted(sellers)
    assert matrix["products"] == ["Alfa Pro", "Beta Plus", "Gama Basic", "Delta Mini"]  # do maior preço ao menor
    for row in matrix["rows"]:
        assert row["closed"] == sellers[row["seller"]] == sum(c["closed"] for c in row["cells"])
        if row["closed"]:
            assert math.isclose(sum(c["mix_share"] for c in row["cells"]), 1, abs_tol=1e-3)
        assert not {"won", "win_rate", "revenue"} & set().union(*(c.keys() for c in row["cells"]))


def test_crosstabs_split_each_row_without_a_rate(page):
    assert [c["id"] for c in page["crosstabs"]] == [
        "account_product", "sector_product", "seller_sector", "sector_office", "location_office"]
    sellers = {s["key"]: s["history"]["closed"] for s in by_dimension(page, codes.DIM_SELLER)["segments"]}
    for table in page["crosstabs"]:
        assert len(table["columns"]) == len(set(table["columns"]))
        for row in table["rows"]:
            assert [c["key"] for c in row["cells"]] == table["columns"]
            assert row["closed"] == sum(c["closed"] for c in row["cells"])
            if row["closed"]:
                assert math.isclose(sum(c["share"] for c in row["cells"]), 1, abs_tol=1e-3)
            assert not {"won", "win_rate", "revenue"} & set().union(*(c.keys() for c in row["cells"]))
        if table["row_dimension"] == "seller":
            assert [r["key"] for r in table["rows"]] == sorted(sellers)
            assert {r["key"]: r["closed"] for r in table["rows"]}.keys() == sellers.keys()
        else:
            closed = [r["closed"] for r in table["rows"]]
            assert closed == sorted(closed, reverse=True)


def test_cycle_bands_end_at_the_rule_limits(page):
    bands, meta = page["cycle_bands"], page["meta"]
    assert sum(b["won"] + b["lost"] for b in bands) == page["history"]["closed"]
    assert [b["high"] for b in bands][-2:] == [meta["won_cycle_limit_days"], meta["cycle_limit_days"]]
    assert all(b["low"] == previous["high"] + 1 for previous, b in zip(bands, bands[1:]))


def test_monthly_adds_up(page, intel):
    months = page["monthly"]
    assert sum(m["won"] for m in months) == page["history"]["won"]
    assert sum(m["lost"] for m in months) == page["history"]["lost"]
    assert sum(m["engaged"] for m in months) == int(intel.opportunities["engage_date"].notna().sum())
    assert [m["month"] for m in months] == sorted(m["month"] for m in months)


def test_every_diagnostic_and_finding_fires_on_the_rich_base(page):
    assert [d["code"] for d in page["diagnostics"]] == list(codes.DIAGNOSTIC_CODES)
    assert {f["code"] for f in page["findings"]} == set(codes.FINDING_CODES)
    diag = {d["code"]: d["params"] for d in page["diagnostics"]}
    summary = page["open"]["summary"]
    beyond = diag[codes.DIAG_ENGAGING_BEYOND_LONGEST_CYCLE]
    assert (beyond["count"], beyond["group"]) == (summary[policy.REVISAR], policy.REVISAR)
    assert diag[codes.DIAG_OPEN_WITHOUT_ACCOUNT]["count"] == summary["without_account"]
    assert diag[codes.DIAG_SELLERS_WITHOUT_OPPORTUNITIES]["sellers"] == ["Fabio Zeta"]
    assert diag[codes.DIAG_QUARTER_END_OUTCOME_MIX]["quarter_end_win_rate"] == 1.0
    assert [m["engaged"] for m in diag[codes.DIAG_ENGAGEMENT_INFLOW_DROP]["recent"]] == [0, 1]


def test_filters_narrow_everything_the_same_way(intel, page):
    product = intelligence.payload(intel, Filters(product="Alfa Pro"))
    segment = next(s for s in by_dimension(page, codes.DIM_PRODUCT)["segments"] if s["key"] == "Alfa Pro")
    assert product["history"] == segment["history"]
    assert product["open"]["summary"]["total"] == segment["open"]
    assert product["filter"] == {**dict.fromkeys(product["filter"]), "product": "Alfa Pro"}


def test_account_filters_report_the_open_deals_without_client(intel, page):
    retail = intelligence.payload(intel, Filters(sector="retail"))
    assert retail["open"]["excluded_without_account"] == page["open"]["summary"]["without_account"] == 3
    assert retail["open"]["summary"]["without_account"] == 0
    assert page["open"]["excluded_without_account"] is None


def test_unknown_values_are_empty_not_errors(intel):
    nothing = intelligence.payload(intel, Filters(account="Ninguem"))
    assert nothing["history_empty"] == {"code": codes.NO_CLOSED_FOR_FILTER, "params": {}}
    assert nothing["open"]["empty"] == {"code": codes.NO_OPEN_FOR_FILTER, "params": {}}
    assert nothing["history"]["win_rate"] is None
    # Só o fato da equipe continua: quem não tem oportunidade não depende do recorte de cliente.
    assert [d["code"] for d in nothing["diagnostics"]] == [codes.DIAG_SELLERS_WITHOUT_OPPORTUNITIES]
    deals = intelligence.deals(intel, Filters(account="Ninguem"), codes.OUTCOME_WON)
    assert deals["total"] == 0 and deals["empty"] == {"code": codes.NO_DEALS_FOR_FILTER, "params": {}}


@pytest.mark.parametrize("outcome, group, name", [(None, None, "outcome"), ("ganhas", None, "outcome"),
                                                  ("open", "focus", "group"), ("won", "focar", "group")])
def test_bad_deal_parameters_are_named(intel, outcome, group, name):
    with pytest.raises(PolicyError) as error:
        intelligence.deals(intel, outcome=outcome, group=group)
    assert error.value.code == codes.INVALID_PARAMETER and error.value.params["name"] == name


def test_deals_are_the_numbers_behind_the_page(intel, page):
    won = intelligence.deals(intel, outcome=codes.OUTCOME_WON)
    lost = intelligence.deals(intel, outcome=codes.OUTCOME_LOST)
    opened = intelligence.deals(intel, outcome=codes.OUTCOME_OPEN)
    assert (won["total"], lost["total"]) == (page["history"]["won"], page["history"]["lost"])
    assert sum(d["close_value"] for d in won["deals"]) == page["history"]["revenue"]
    assert opened["total"] == page["open"]["summary"]["total"]
    ctx = views.context(intel, None)
    expected = triage.order(triage.classify(intel.opportunities, ctx))["opportunity_id"].tolist()
    assert [d["opportunity_id"] for d in opened["deals"]] == expected  # a ordem da regra
    for state in policy.STATES:
        assert intelligence.deals(intel, outcome="open", group=state)["total"] == page["open"]["summary"][state]
    dates = [d["close_date"] for d in won["deals"]]
    assert dates == sorted(dates, reverse=True)
    cell = intelligence.deals(intel, Filters(seller="Ana Alfa", product="Alfa Pro"), codes.OUTCOME_WON)
    assert all((d["sales_agent"], d["product"]) == ("Ana Alfa", "Alfa Pro") for d in cell["deals"])


def test_payload_is_codes_and_numbers_only(page):
    text_keys = {"label", "text", "message", "detail", "description", "title", "explanation"}
    assert not any(text_keys & set(node) for node in walk(page))
    assert not any("score" in node or "probability" in node for node in walk(page))


def test_realized_revenue_and_list_value_never_mix(page):
    assert page["open"]["list_value"] == sum(int(p["sales_price"]) for p in INTEL_TABLES["products"]
                                            for r in ROWS if r["deal_stage"] in policy.OPEN_STAGES
                                            and r["product"] == p["product"])
    assert "list_value" not in page["history"] and "revenue" not in page["open"]


def test_payloads_pass_through_the_models(intel, page):
    for payload in (page, intelligence.payload(intel, Filters(sector="retail")),
                    intelligence.payload(intel, Filters(account="Ninguem"))):
        schemas.Intelligence.model_validate(payload)
    schemas.IntelligenceDeals.model_validate(intelligence.deals(intel, outcome="open", group="revisar"))


# Oráculos nos CSVs reais (31/12/2017).
@pytest.fixture(scope="module")
def real_page(real_dataset):
    return intelligence.payload(real_dataset)


@pytest.mark.real_data
def test_real_history_and_open(real_page):
    history = real_page["history"]
    assert (history["closed"], history["won"], history["revenue"]) == (6711, 4238, 10005534)
    assert history["win_rate"] == {"value": 0.631501, "low": 0.619887, "high": 0.642964}
    assert (history["median_won_cycle_days"], history["median_lost_cycle_days"]) == (57, 14)
    summary = real_page["open"]["summary"]
    assert (summary["total"], summary["revisar"], summary["without_account"]) == (2089, 1291, 1425)
    assert real_page["open"]["list_value"] == 4966215


@pytest.mark.real_data
def test_real_breakdowns(real_page):
    products = by_dimension(real_page, codes.DIM_PRODUCT)
    assert [s["revenue_share"] for s in products["segments"][:3]] == [0.350864, 0.26282, 0.221516]
    p_values = {b["dimension"]: b["chance"]["p_value"] for b in real_page["breakdowns"]}
    assert p_values == {"product": 0.3719, "seller": 0.2639, "manager": 0.7861, "office": 0.6042,
                        "sector": 0.9706, "account": 0.9432, "size": 0.1443}
    assert {b["chance"]["verdict"] for b in real_page["breakdowns"]} == {codes.CHANCE_WITHIN}
    shares = {b["dimension"]: b["drivers"] and (b["drivers"]["volume_share"], b["drivers"]["conversion_share"],
                                                b["drivers"]["ticket_share"]) for b in real_page["breakdowns"]}
    assert shares["seller"] == (0.614719, -0.013776, 0.399058)
    assert shares["product"] == (0.108678, -0.00458, 0.895901)
    assert shares["size"] == (0.760161, -0.001327, 0.241166)
    assert shares["office"] is None
    assert [s["key"] for s in by_dimension(real_page, codes.DIM_SECTOR)["segments"]][:2] == ["retail", "technology"]
    sizes = real_page["options"]["sizes"]
    assert [(b["key"], b["accounts"]) for b in sizes] == [("1", 22), ("2", 21), ("3", 21), ("4", 21)]


@pytest.mark.real_data
def test_real_diagnostics_and_findings(real_page):
    diag = {d["code"]: d["params"] for d in real_page["diagnostics"]}
    assert list(diag) == list(codes.DIAGNOSTIC_CODES)
    assert (diag["engaging_beyond_longest_cycle"]["count"], diag["engaging_beyond_longest_cycle"]["engaging"]) == \
        (1291, 1589)
    assert (diag["open_without_account"]["count"], diag["open_without_account"]["closed_without_account"]) == (1425, 0)
    assert diag["prospecting_without_engage_date"] == {"group": "qualificar", "count": 500, "prospecting": 500}
    assert diag["sellers_without_opportunities"]["sellers"] == [
        "Carl Lin", "Carol Thompson", "Elizabeth Anderson", "Mei-Mei Johns", "Natalya Ivanova"]
    assert (diag["quarter_end_outcome_mix"]["quarter_end_win_rate"],
            diag["quarter_end_outcome_mix"]["other_win_rate"]) == (0.806527, 0.522601)
    assert diag["engagement_inflow_drop"]["recent"] == [{"month": "2017-11", "engaged": 283},
                                                       {"month": "2017-12", "engaged": 121}]
    assert diag["engagement_inflow_drop"]["base_average"] == 864.6
    assert diag["accounts_shared_by_sellers"] == {"median_sellers": 10, "max_sellers": 30, "accounts": 85}
    found = {f["code"]: f["params"] for f in real_page["findings"]}
    assert codes.FIND_WIN_RATE_BEYOND_CHANCE not in found
    assert found["win_rate_within_chance"]["dimensions"] == list(codes.DIMENSIONS)
    assert found["revenue_concentrated"] == {"dimension": "product", "top": 3, "of": 7, "share": 0.835199,
                                             "keys": ["GTX Pro", "GTX Plus Pro", "MG Advanced"]}
    assert found["fast_losses"]["median_lost_cycle_days"] == 14
    assert found["account_product_coverage"]["distribution"] == [{"bought": 6, "accounts": 73},
                                                                {"bought": 7, "accounts": 12}]
    assert found["account_product_coverage"]["most_missing"] == "GTK 500"


@pytest.mark.real_data
def test_real_cycle_bands(real_page):
    assert [(b["low"], b["high"], b["won"], b["lost"]) for b in real_page["cycle_bands"]] == [
        (0, 15, 1613, 1264), (16, 30, 204, 82), (31, 60, 377, 192), (61, 90, 1078, 543),
        (91, 106, 556, 227), (107, 138, 410, 165)]


@pytest.mark.real_data
def test_real_open_deals_match_the_team_for_every_manager_and_office(real_dataset):
    for name, column in (("manager", "manager"), ("office", "regional_office")):
        for value in sorted(real_dataset.teams[column].unique()):
            page = intelligence.payload(real_dataset, Filters(**{name: value}))
            team = views.team_pipeline(real_dataset, **{name: value})
            assert page["open"]["summary"] == team["summary"], value
