import pytest
from pydantic import ValidationError
from economics import Assumptions, estimate
from test_app import client


def test_base_separates_capacity_from_avoided_expense():
    r = estimate(Assumptions())
    assert r['effective_tickets_month'] == 800
    assert r['hours_month'] == pytest.approx(53.333333)
    assert r['capacity_value_month'] == pytest.approx(2266.666667)
    assert r['avoided_expense_month'] == pytest.approx(1133.333333)
    assert r['first_year_net_cash'] == pytest.approx(1600)
    assert r['roi_12m_pct'] == pytest.approx(13.333333)
    assert r['payback_months'] == pytest.approx(9.473684)


def test_capacity_without_realization_has_no_financial_saving():
    r = estimate(Assumptions(realization_pct=0))
    assert r['hours_month'] > 0
    assert r['avoided_expense_month'] == 0
    assert r['first_year_net_cash'] == -12000
    assert r['roi_12m_pct'] == -100
    assert r['payback_months'] is None
    assert r['break_even_minutes_12m'] is None


def test_negative_gain_exposes_additional_work():
    r = estimate(Assumptions(net_minutes=-4))
    assert r['hours_month'] < 0
    assert r['additional_work_value_month'] == pytest.approx(2266.666667)
    assert r['avoided_expense_month'] == 0
    assert r['payback_months'] is None


@pytest.mark.parametrize('field', ['annual_tickets', 'eligible_pct', 'adoption_pct', 'salary'])
def test_zero_benefit_has_no_break_even(field):
    r = estimate(Assumptions(**{field: 0}))
    assert r['avoided_expense_month'] == 0
    assert r['break_even_minutes_12m'] is None


def test_free_project_has_undefined_roi():
    assert estimate(Assumptions(monthly_cost=0, setup_cost=0))['roi_12m_pct'] is None


def test_break_even_recovers_all_first_year_costs():
    minutes = estimate(Assumptions())['break_even_minutes_12m']
    assert estimate(Assumptions(net_minutes=minutes))['first_year_net_cash'] == pytest.approx(0, abs=1e-8)


@pytest.mark.parametrize('values', [
    {'productive_hours': 0}, {'eligible_pct': 101}, {'adoption_pct': -1},
    {'net_minutes': float('nan')}, {'salary': float('inf')},
    {'salary': True}, {'setup_cost': -1}, {'realization_pct': 101},
])
def test_invalid_assumptions_rejected(values):
    with pytest.raises(ValidationError):
        Assumptions(**values)


def test_api_returns_assumptions_and_result(client):
    response = client.post('/api/economics', json={'realization_pct': 0})
    assert response.status_code == 200
    assert response.json()['result']['avoided_expense_month'] == 0
    assert response.json()['assumptions']['salary'] == 4000
    assert client.post('/api/economics', json={'productive_hours': 0}).status_code == 422
