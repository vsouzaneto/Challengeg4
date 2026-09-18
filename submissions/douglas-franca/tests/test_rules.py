import pytest

from src.decision.rules import (
    CycleResult,
    break_even_fee,
    ci_from_arms,
    contract_gaps,
    cycle_decision,
    engagement_value_ceiling,
    sample_size_per_arm,
)


def test_break_even_fee():
    assert break_even_fee(incremental_sales=200, unit_margin=30, production_cost=1_000) == 5_000


def test_break_even_rejects_negative_inputs():
    with pytest.raises(ValueError):
        break_even_fee(-1, 30)


def test_engagement_value_ceiling_matches_hand_calculation():
    # 10.000 views × 0,01 p.p. = 1 interação; × R$ 2 = R$ 2
    assert engagement_value_ceiling(10_000, 0.01, 2.0) == pytest.approx(2.0)


def test_sample_size_grows_with_noise_and_shrinks_with_delta():
    assert sample_size_per_arm(5, 1) == 393
    assert sample_size_per_arm(10, 1) > sample_size_per_arm(5, 1)
    assert sample_size_per_arm(5, 2) < sample_size_per_arm(5, 1)


def test_equivalent_effect_stops():
    decision, _ = cycle_decision(CycleResult(effect_pp=-0.003, ci95_low=-0.014, ci95_high=0.008))
    assert decision == "Parar"


def test_relevant_effect_that_pays_scales():
    r = CycleResult(effect_pp=2.0, ci95_low=1.2, ci95_high=2.8, return_over_break_even=5_000)
    assert cycle_decision(r)[0] == "Escalar"


def test_scale_reason_does_not_mention_money_when_test_has_no_cost():
    decision, reason = cycle_decision(CycleResult(effect_pp=2.0, ci95_low=1.2, ci95_high=2.8))
    assert decision == "Escalar"
    assert "break-even" not in reason and "sem custo" in reason


def test_relevant_effect_below_break_even_stops():
    r = CycleResult(effect_pp=2.0, ci95_low=1.2, ci95_high=2.8, return_over_break_even=-100)
    assert cycle_decision(r)[0] == "Parar"


def test_wide_interval_replicates():
    assert cycle_decision(CycleResult(effect_pp=1.5, ci95_low=0.2, ci95_high=2.8))[0] == "Replicar"


def test_clear_harm_stops():
    assert cycle_decision(CycleResult(effect_pp=-2.0, ci95_low=-3.0, ci95_high=-1.2))[0] == "Parar"


def test_wide_negative_interval_is_not_promising():
    assert cycle_decision(CycleResult(effect_pp=-1.5, ci95_low=-2.8, ci95_high=-0.2))[0] == "Parar"


def test_bad_execution_iterates_even_with_good_numbers():
    r = CycleResult(effect_pp=2.0, ci95_low=1.2, ci95_high=2.8, completeness=0.80)
    assert cycle_decision(r)[0] == "Iterar"


def test_contract_gaps_lists_missing_fields():
    gaps = contract_gaps({"campaign_id": "C1", "custo_total": 1000, "cupom": ""})
    assert "cupom" in gaps and "campaign_id" not in gaps and "utm" in gaps


def test_ci_from_arms():
    diff, low, high = ci_from_arms(20, 5, 400, 19, 5, 400)
    assert diff == pytest.approx(1.0)
    assert low < diff < high
