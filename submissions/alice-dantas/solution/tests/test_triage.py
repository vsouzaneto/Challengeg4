import numpy as np
import pandas as pd
import pytest

from leadscorer import codes, data, policy, triage
from leadscorer.errors import DataError

from conftest import L1_DAYS, L2_DAYS, PIPELINE, opp, write_raw


def classified(raw_dir):
    frame = data.load(raw_dir).opportunities
    ctx = triage.resolve_context(frame)
    return ctx, triage.order(triage.classify(frame, ctx))


def test_default_context_has_both_limits(raw_dir):
    ctx, _ = classified(raw_dir)
    assert ctx.as_of == pd.Timestamp("2017-12-31")
    # L1 só com as ganhas (10 e 110 d); com todas as fechadas seria 132.
    assert (ctx.won_cycle_limit_days, ctx.cycle_limit_days) == (L1_DAYS, L2_DAYS) == (100, 138)


# Regra A (ADR-006): a tabela de fronteiras foi escrita antes da regra.
@pytest.mark.parametrize("opportunity_id, group", [
    ("E100", policy.FOCAR),        # idade = L1
    ("E101", policy.ACOMPANHAR),   # L1 + 1
    ("E138", policy.ACOMPANHAR),   # idade = L2
    ("E139", policy.REVISAR),      # L2 + 1
    ("P1", policy.QUALIFICAR),     # Prospecting, sem data
])
def test_boundaries_l1_l2(raw_dir, opportunity_id, group):  # AC-1.9
    _, opps = classified(raw_dir)
    assert opps.set_index("opportunity_id").loc[opportunity_id, "state"] == group


def test_won_limit_is_the_floor_of_the_p90_of_wins_until_as_of(tmp_path):
    rows = [dict(row) for row in PIPELINE]
    rows[1]["close_date"] = (pd.Timestamp(rows[1]["engage_date"]) + pd.Timedelta(days=115)).date().isoformat()
    later_win = opp("X1", "Ana Alfa", "GTXPro", "Won", engaged=10, closed=-400)  # fecha depois do as_of
    extra = [opp("A104", "Ana Alfa", "GTX Basic", "Engaging", engaged=104),
             opp("A105", "Ana Alfa", "GTX Basic", "Engaging", engaged=105)]
    frame = data.load(write_raw(tmp_path / "raw", sales_pipeline=rows + extra + [later_win])).opportunities
    ctx = triage.resolve_context(frame, "2017-12-31")
    assert ctx.won_cycle_limit_days == 104  # P90 de [10, 115] = 104,5: idade inteira, então o piso
    states = triage.classify(frame, ctx).set_index("opportunity_id")["state"]
    assert (states["A104"], states["A105"]) == (policy.FOCAR, policy.ACOMPANHAR)


def test_no_won_history_is_a_coded_data_error(tmp_path):
    rows = [dict(row, deal_stage="Lost") if row["deal_stage"] == "Won" else row for row in PIPELINE]
    frame = data.load(write_raw(tmp_path / "raw", sales_pipeline=rows)).opportunities
    with pytest.raises(DataError) as error:
        triage.resolve_context(frame)
    assert (error.value.code, error.value.params) == (codes.NO_WON_HISTORY, {"as_of": "2017-12-31"})


def test_context_rejects_a_first_limit_above_the_second():
    with pytest.raises(ValueError):
        triage.Context(as_of=pd.Timestamp("2017-12-31"), won_cycle_limit_days=139, cycle_limit_days=138,
                       won_cycle_median_days=57)


def test_engaging_group_matches_classify(raw_dir):
    frame = data.load(raw_dir).opportunities
    ctx = triage.resolve_context(frame)
    opps = triage.classify(frame, ctx)
    engaging = opps[opps["deal_stage"] == "Engaging"]
    groups = triage.engaging_group(engaging["age_days"].astype(float).to_numpy(), ctx)
    assert list(groups) == list(engaging["state"])
    assert list(triage.engaging_group(np.array([0, 100, 101, 138, 139]), ctx)) == [
        policy.FOCAR, policy.FOCAR, policy.ACOMPANHAR, policy.ACOMPANHAR, policy.REVISAR]


def test_partition_covers_every_open_once(raw_dir):
    _, opps = classified(raw_dir)
    open_ids = [row["opportunity_id"] for row in PIPELINE if row["deal_stage"] in policy.OPEN_STAGES]
    assert sorted(opps["opportunity_id"]) == sorted(open_ids)
    assert sum(triage.summary(opps).values()) == len(open_ids)


def test_declared_order_state_band_price_id(raw_dir):
    _, opps = classified(raw_dir)
    assert list(opps["opportunity_id"]) == ["EPP", "EGP", "E050", "E100", "EMG", "P1", "E101", "E138", "E139"]
    assert list(opps["value_band"][:5]) == ["alto", "alto", "médio", "médio", "baixo"]


def test_classification_never_sees_close_fields(raw_dir):
    frame = data.load(raw_dir).opportunities
    ctx = triage.resolve_context(frame)
    opps = triage.classify(frame, ctx)
    assert not {"close_date", "close_value"} & set(opps.columns)


def test_age_does_not_order_inside_the_group(tmp_path):  # AC-2.2
    def ordered_ids(rows, name):
        frame = data.load(write_raw(tmp_path / name, sales_pipeline=rows)).opportunities
        ctx = triage.resolve_context(frame)
        return list(triage.order(triage.classify(frame, ctx))["opportunity_id"])

    swapped = [dict(row) for row in PIPELINE]
    by_id = {row["opportunity_id"]: row for row in swapped}
    for first, second in (("E050", "E100"), ("E101", "E138")):  # cada par no mesmo grupo
        by_id[first]["engage_date"], by_id[second]["engage_date"] = (
            by_id[second]["engage_date"], by_id[first]["engage_date"])
    assert ordered_ids(swapped, "swapped") == ordered_ids(PIPELINE, "original")


def test_same_state_and_product_is_a_tie(raw_dir):  # AC-2.3
    _, opps = classified(raw_dir)
    ties = opps.set_index("opportunity_id")["tie_size"]
    assert ties["E050"] == ties["E100"] == 2  # Focar, GTX Basic
    assert ties["E101"] == ties["E138"] == 2  # Acompanhar, GTX Basic
    assert ties["EPP"] == ties["E139"] == 1


@pytest.mark.parametrize("price, band", [(3000, "alto"), (2999, "médio"), (500, "médio"), (499, "baixo")])
def test_value_band_thresholds(price, band):
    assert triage.value_band(pd.Series([price])).item() == band


@pytest.mark.real_data
def test_real_partition_and_bands(real_dataset):  # AC-1.1
    frame = real_dataset.opportunities
    ctx = triage.resolve_context(frame)
    opps = triage.order(triage.classify(frame, ctx))
    assert ctx.as_of == pd.Timestamp("2017-12-31")
    assert (ctx.won_cycle_limit_days, ctx.cycle_limit_days) == (106, 138)
    assert triage.summary(opps) == {policy.FOCAR: 157, policy.ACOMPANHAR: 141, policy.REVISAR: 1291,
                                    policy.QUALIFICAR: 500, policy.NAO_PONTUAVEL: 0}
    focar = opps[opps["state"] == policy.FOCAR]["value_band"].value_counts().to_dict()
    assert focar == {"alto": 69, "médio": 56, "baixo": 32}
    assert opps.groupby("sales_agent")["state"].size().sum() == 2089


@pytest.mark.real_data
def test_real_order_is_monotonic_within_each_state(real_dataset):
    frame = real_dataset.opportunities
    opps = triage.order(triage.classify(frame, triage.resolve_context(frame)))
    for _, group in opps.groupby("state", sort=False):
        prices = list(group["sales_price"])
        assert prices == sorted(prices, reverse=True)
