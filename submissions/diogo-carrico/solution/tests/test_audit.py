import numpy as np
import pandas as pd

from support_triage.audit import cramers_v, spearman_with_permutation, uniformity


def test_cramers_v_is_one_for_identical_and_near_zero_for_independent():
    rng = np.random.default_rng(0)
    a = pd.Series(rng.choice(list("abcd"), size=4000))
    assert cramers_v(a, a)["cramers_v"] > 0.99
    b = pd.Series(rng.choice(list("wxyz"), size=4000))
    assert cramers_v(a, b)["cramers_v"] < 0.05


def test_uniformity_accepts_equal_counts_and_rejects_skewed_ones():
    assert uniformity(pd.Series([1000, 1000, 1000, 1000]))["p_value_vs_uniform"] > 0.99
    skewed = uniformity(pd.Series([4000, 1000, 1000, 1000]))
    assert skewed["p_value_vs_uniform"] < 0.001
    assert skewed["max_min_share_ratio"] == 4.0


def test_spearman_permutation_detects_signal_and_its_absence():
    rng = np.random.default_rng(1)
    x = rng.normal(size=500)
    strong = spearman_with_permutation(
        x, x + rng.normal(scale=0.5, size=500), n_perm=500
    )
    assert strong["rho"] > 0.8 and strong["permutation_p_value"] < 0.01
    none = spearman_with_permutation(x, rng.normal(size=500), n_perm=500)
    lo, hi = none["null_95pct_band"]
    assert lo < 0 < hi
    assert none["permutation_p_value"] > 0.01


def test_spearman_permutation_is_reproducible():
    rng = np.random.default_rng(2)
    x, y = rng.normal(size=200), rng.normal(size=200)
    assert spearman_with_permutation(x, y, n_perm=300) == spearman_with_permutation(
        x, y, n_perm=300
    )
