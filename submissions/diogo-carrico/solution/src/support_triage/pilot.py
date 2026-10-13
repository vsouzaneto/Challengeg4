"""Pilot sizing: how many routed tickets a shadow pilot must observe to prove the precision target."""

from __future__ import annotations

from support_triage.classifier import wilson_interval


def tickets_needed(
    precision: float, target: float = 0.95, limit: int = 100_000
) -> int | None:
    """Smallest number of routed tickets whose Wilson lower bound clears the target,
    if the pilot sees the same precision as the test set. None when the precision is at or
    below the target (no sample size can prove it)."""
    if precision <= target:
        return None
    n = 10
    while n <= limit:
        if wilson_interval(round(precision * n), n)[0] >= target:
            # step back to the exact minimum
            lo = max(10, n // 2)
            for m in range(lo, n + 1):
                if wilson_interval(round(precision * m), m)[0] >= target:
                    return m
        n *= 2
    return None
