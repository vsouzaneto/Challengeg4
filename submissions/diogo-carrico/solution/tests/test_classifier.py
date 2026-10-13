import numpy as np
import pandas as pd
import pytest

from support_triage.classifier import (
    cost_threshold,
    expected_calibration_error,
    near_duplicate_groups,
    normalize_text,
    split_indices,
    threshold_for_precision,
    wilson_interval,
)


def test_normalize_text_matches_dataset2_form():
    assert (
        normalize_text("Hi! My laptop (Dell XPS 15) won't boot.\n\nRegards")
        == "hi my laptop dell xps won t boot regards"
    )
    assert normalize_text(None) == "none"
    assert normalize_text("already clean text") == "already clean text"


def test_wilson_interval_known_values():
    lo, hi = wilson_interval(95, 100)
    assert lo == pytest.approx(0.888, abs=0.002)
    assert hi == pytest.approx(0.978, abs=0.002)
    assert np.isnan(wilson_interval(0, 0)[0])


def test_cost_threshold():
    assert cost_threshold(4, 10) == pytest.approx(0.6)
    assert cost_threshold(10, 5) == 0.0


def test_threshold_for_precision_uses_the_lower_bound():
    rng = np.random.default_rng(0)
    confidence = rng.uniform(0.3, 1.0, 20000)
    correct = rng.uniform(size=confidence.size) < confidence
    t = threshold_for_precision(confidence, correct, 0.95)
    routed = confidence >= t
    lo, _ = wilson_interval(int(correct[routed].sum()), int(routed.sum()))
    assert lo >= 0.95
    assert t < 1.0


def test_expected_calibration_error_is_small_when_calibrated():
    rng = np.random.default_rng(1)
    confidence = rng.uniform(0.2, 1.0, 50000)
    correct = rng.uniform(size=confidence.size) < confidence
    assert expected_calibration_error(confidence, correct) < 0.01
    assert expected_calibration_error(confidence, np.ones_like(correct)) > 0.3


def test_near_duplicates_grouped_and_split_keeps_groups_together():
    rng = np.random.default_rng(2)
    words = [f"w{i}" for i in range(400)]
    base = [" ".join(rng.choice(words, 30)) for _ in range(300)]
    texts = base + [
        b + " extra" for b in base[:50]
    ]  # 50 near-duplicates of the first 50
    groups = near_duplicate_groups(pd.Series(texts))
    for i in range(50):
        assert groups[i] == groups[300 + i]
    labels = pd.Series(rng.choice(["a", "b", "c"], len(texts)))
    parts = split_indices(labels, groups)
    seen = np.concatenate(list(parts.values()))
    assert len(seen) == len(texts) == len(set(seen))
    where = {i: k for k, v in parts.items() for i in v}
    for i in range(50):
        assert where[i] == where[300 + i]
