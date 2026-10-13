from support_triage.classifier import wilson_interval
from support_triage.pilot import tickets_needed


def test_tickets_needed_is_the_minimum_that_proves_the_target():
    n = tickets_needed(0.97, 0.95)
    assert wilson_interval(round(0.97 * n), n)[0] >= 0.95
    assert wilson_interval(round(0.97 * (n - 1)), n - 1)[0] < 0.95


def test_higher_precision_needs_fewer_tickets():
    assert tickets_needed(0.99) < tickets_needed(0.97) < tickets_needed(0.96)


def test_precision_at_or_below_target_cannot_be_proved():
    assert tickets_needed(0.95) is None
    assert tickets_needed(0.94) is None
