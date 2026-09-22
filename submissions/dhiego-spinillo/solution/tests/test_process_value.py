import pytest
from pydantic import ValidationError
from process_value import ProcessAssumptions, process_estimate
from test_app import client


def test_failure_cost_is_counted_and_lanes_are_disjoint():
    r=process_estimate(ProcessAssumptions())
    assert r['autonomous_expected_net_minutes']==pytest.approx(8.4)
    assert r['autonomous_completed_month']==32
    assert r['autonomous_failed_month']==pytest.approx(8)
    assert r['autonomous_hours']==pytest.approx(5.6)
    assert r['prepared_hours']==pytest.approx(66.6666667)
    assert r['human_tickets']==1450
    assert r['hours_month']==pytest.approx(72.2666667)
    assert r['roi_12m_pct']==pytest.approx(53.5666667)


def test_reset_alone_does_not_justify_project():
    r=process_estimate(ProcessAssumptions(prepared_tickets=0))
    assert r['hours_month']==pytest.approx(5.6)
    assert r['net_cash_month']<0
    assert r['payback_months'] is None


def test_all_failures_and_slower_review_can_destroy_value():
    r=process_estimate(ProcessAssumptions(success_pct=0,prepared_after=15))
    assert r['hours_month']<0
    assert r['avoided_expense_month']==0
    assert r['additional_work_value_month']>0


def test_zero_adoption_has_no_benefit():
    assert process_estimate(ProcessAssumptions(adoption_pct=0))['hours_month']==0


@pytest.mark.parametrize('changes',[{'autonomous_tickets':2000,'prepared_tickets':1000}, {'salary':float('nan')},{'success_pct':101},{'failure_extra':-1}])
def test_invalid_portfolio_rejected(changes):
    with pytest.raises(ValidationError): ProcessAssumptions(**changes)


def test_api_returns_both_lane_contributions(client):
    r=client.post('/api/process-economics',json={})
    assert r.status_code==200
    assert r.json()['result']['prepared_hours']>r.json()['result']['autonomous_hours']
    assert client.post('/api/process-economics',json={'monthly_tickets':0}).status_code==422
