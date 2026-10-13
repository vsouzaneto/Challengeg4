import numpy as np
import pytest

from support_triage.classifier import per_class_thresholds, route, routed_quality
from support_triage.waste import ASSUMPTIONS, with_measured_routing


def test_per_class_thresholds_and_route():
    rng = np.random.default_rng(0)
    n = 6000
    predicted = rng.choice(["easy", "hard"], n)
    confidence = rng.uniform(0.3, 1.0, n)
    # "easy" is right whenever confident; "hard" is right only half the time at any confidence
    correct = np.where(
        predicted == "easy", rng.uniform(size=n) < confidence, rng.uniform(size=n) < 0.5
    )
    t = per_class_thresholds(confidence, predicted, correct, ["easy", "hard"], 0.95)
    assert t["easy"] < 1.0
    assert t["hard"] == 1.0  # can never reach 95%, so never auto-routed
    routed = route(confidence, predicted, t)
    assert not routed[predicted == "hard"].any()
    q = routed_quality(routed, correct)
    assert q["precision_ci95"][0] > 0.9
    assert q["routed"] == routed.sum()


def test_with_measured_routing_replaces_share_and_misroute_rate():
    metrics = {
        "end_to_end_dataset2_test": {
            "coverage": 0.45,
            "precision": 0.97,
            "precision_ci95": [0.96, 0.98],
            "if_every_class_is_enabled": {"coverage": 0.64},
        }
    }
    a = with_measured_routing(metrics)
    assert a["auto_route_share"].base == 0.45
    assert a["auto_route_share"].low == ASSUMPTIONS["auto_route_share"].low
    assert a["auto_route_share"].high == 0.64
    assert a["misroute_rate"].base == pytest.approx(0.03)
    assert a["misroute_rate"].low == pytest.approx(0.02)
    assert a["misroute_rate"].high == pytest.approx(0.04)
    assert a["triage_minutes"] == ASSUMPTIONS["triage_minutes"]
