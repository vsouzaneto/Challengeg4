"""Statistical checks used to avoid promoting random variation to a finding."""

from __future__ import annotations

import math
from typing import Any

from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu


def _interpret(p_value: float) -> str:
    return "Evidence of association" if p_value < 0.05 else "No statistical evidence of association"


def _cramers_v(chi2: float, observed: list[list[int]]) -> float:
    n = sum(sum(row) for row in observed)
    rows = len(observed)
    columns = len(observed[0]) if rows else 0
    denominator = n * min(rows - 1, columns - 1)
    return math.sqrt(chi2 / denominator) if denominator > 0 else 0.0


def _chi_square(observed: list[list[int]]) -> tuple[float, float, float]:
    if len(observed) < 2 or not observed or len(observed[0]) < 2:
        return 0.0, 1.0, 0.0
    if any(sum(row) == 0 for row in observed):
        return 0.0, 1.0, 0.0
    columns = list(zip(*observed, strict=True))
    if any(sum(column) == 0 for column in columns):
        return 0.0, 1.0, 0.0
    chi2, p_value, _, _ = chi2_contingency(observed, correction=False)
    return float(chi2), float(p_value), _cramers_v(float(chi2), observed)


def _fisher(matrix: list[list[int]]) -> tuple[float, float]:
    if any(sum(row) == 0 for row in matrix) or any(sum(column) == 0 for column in zip(*matrix, strict=True)):
        return float("nan"), 1.0
    odds_ratio, p_value = fisher_exact(matrix)
    return float(odds_ratio), float(p_value)


def _phi(matrix: list[list[int]]) -> float:
    a, b = matrix[0]
    c, d = matrix[1]
    denominator = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    return (a * d - b * c) / denominator if denominator else 0.0


def _cohens_kappa(matrix: list[list[int]]) -> float:
    total = sum(sum(row) for row in matrix)
    if total == 0:
        return 0.0
    observed = (matrix[0][0] + matrix[1][1]) / total
    row_totals = [sum(row) for row in matrix]
    col_totals = [matrix[0][0] + matrix[1][0], matrix[0][1] + matrix[1][1]]
    expected = sum(r * c for r, c in zip(row_totals, col_totals, strict=True)) / (total * total)
    return (observed - expected) / (1 - expected) if expected != 1 else 0.0


def _contingency(con: Any, dimension: str) -> tuple[list[list[int]], int]:
    rows = con.execute(
        """
        SELECT snapshot_churned_accounts,
               total_accounts - snapshot_churned_accounts AS retained_accounts
        FROM gold.segment_snapshot
        WHERE dimension_name = ?
        ORDER BY segment_value
        """,
        [dimension],
    ).fetchall()
    observed = [[int(churned), int(retained)] for churned, retained in rows]
    return observed, sum(sum(row) for row in observed)


def build_statistical_tests(con: Any) -> None:
    """Create gold.statistical_tests and enrich segment_snapshot in place."""

    con.execute(
        """
        CREATE TABLE gold.statistical_tests (
            test_id VARCHAR,
            analysis VARCHAR,
            universe VARCHAR,
            outcome VARCHAR,
            exposure VARCHAR,
            test_name VARCHAR,
            n BIGINT,
            statistic DOUBLE,
            p_value DOUBLE,
            effect_name VARCHAR,
            effect_value DOUBLE,
            secondary_effect_name VARCHAR,
            secondary_effect_value DOUBLE,
            interpretation VARCHAR,
            confidence_state VARCHAR,
            notes VARCHAR
        )
        """
    )
    results: list[tuple[Any, ...]] = []

    # Competing churn universes: snapshot flag versus presence of a valid event.
    counts = {
        (bool(flag), bool(event)): int(count)
        for flag, event, count in con.execute(
            """
            SELECT snapshot_churn_flag, has_valid_churn_event, COUNT(*)
            FROM gold.account_snapshot GROUP BY 1, 2
            """
        ).fetchall()
    }
    matrix = [
        [counts.get((True, True), 0), counts.get((True, False), 0)],
        [counts.get((False, True), 0), counts.get((False, False), 0)],
    ]
    odds_ratio, p_value = _fisher(matrix)
    results.append(
        (
            "snapshot_flag_vs_event", "Agreement between churn universes",
            "Eligible accounts and valid churn-event ledger", "Snapshot churn flag",
            "Presence of a valid historical churn event", "Fisher exact", sum(map(sum, matrix)),
            float(odds_ratio), float(p_value), "Phi", _phi(matrix), "Cohen kappa",
            _cohens_kappa(matrix), _interpret(float(p_value)), "Observed",
            "Historical events do not automatically represent current state.",
        )
    )

    # Global snapshot comparisons. P-values/effects are repeated on segment rows
    # so the UI cannot show a segment rate without its global-test context.
    for dimension in ("plan_tier", "industry", "referral_source", "country"):
        observed, n = _contingency(con, dimension)
        chi2, p_value, effect = _chi_square(observed)
        interpretation = _interpret(p_value)
        con.execute(
            """
            UPDATE gold.segment_snapshot
            SET global_p_value = ?, cramers_v = ?, global_interpretation = ?
            WHERE dimension_name = ?
            """,
            [p_value, effect, interpretation, dimension],
        )
        results.append(
            (
                f"snapshot_churn_by_{dimension}", f"Snapshot churn by {dimension}",
                "Eligible account snapshot", "Snapshot churn flag", dimension,
                "Chi-square", n, chi2, p_value, "Cramer's V", effect,
                None, None, interpretation, "Observed",
                "Cross-sectional association; not a causal estimate.",
            )
        )

    # Declared reason versus literal feedback category.
    reason_rows = con.execute(
        """
        SELECT reason_code, COALESCE(feedback_text, '[missing]') AS feedback, COUNT(*)
        FROM stage.churn_events WHERE is_eligible GROUP BY 1, 2 ORDER BY 1, 2
        """
    ).fetchall()
    reasons = sorted({row[0] for row in reason_rows})
    feedbacks = sorted({row[1] for row in reason_rows})
    lookup = {(row[0], row[1]): int(row[2]) for row in reason_rows}
    observed = [[lookup.get((reason, feedback), 0) for feedback in feedbacks] for reason in reasons]
    chi2, p_value, effect = _chi_square(observed)
    results.append(
        (
            "churn_reason_vs_feedback", "Declared reason versus feedback text",
            "Valid historical churn events", "Reason code", "Literal feedback category",
            "Chi-square", sum(map(sum, observed)), chi2, p_value,
            "Cramer's V", effect, None, None, _interpret(float(p_value)), "Derived",
            "Synthetic low-cardinality text; no semantic causal interpretation.",
        )
    )

    # Corrected pre-event comparison: each ticket is linked only to its next future churn.
    windows = {
        row[0]: (int(row[1]), int(row[2]))
        for row in con.execute(
            "SELECT window_label, escalated_tickets, support_tickets FROM gold.pre_event_signals"
        ).fetchall()
    }
    near_e, near_n = windows.get("0-14", (0, 0))
    reference_windows = (windows.get("15-30", (0, 0)), windows.get("31-60", (0, 0)))
    far_e = sum(item[0] for item in reference_windows)
    far_n = sum(item[1] for item in reference_windows)
    matrix = [[near_e, near_n - near_e], [far_e, far_n - far_e]]
    odds_ratio, p_value = _fisher(matrix)
    results.append(
        (
            "pre_event_escalation_0_14", "Escalations in the 0-14 day pre-event window",
            "Eligible tickets linked to their next future valid churn event", "Escalation flag",
            "0-14 days versus 15-60 days", "Fisher exact", near_n + far_n,
            float(odds_ratio), float(p_value), "Odds ratio", float(odds_ratio), None, None,
            _interpret(float(p_value)), "Derived",
            f"Exploratory: {near_e}/{near_n} escalations in the 0-14 day window.",
        )
    )

    # Valid support rows: snapshot groups, with no claim that current state caused service outcomes.
    escalation_rows = con.execute(
        """
        SELECT a.snapshot_churn_flag, t.escalation_flag, COUNT(*)
        FROM stage.support_tickets t
        JOIN gold.account_snapshot a USING (account_id)
        WHERE t.is_eligible
        GROUP BY 1, 2
        """
    ).fetchall()
    support_counts = {(bool(a), bool(e)): int(n) for a, e, n in escalation_rows}
    matrix = [
        [support_counts.get((True, True), 0), support_counts.get((True, False), 0)],
        [support_counts.get((False, True), 0), support_counts.get((False, False), 0)],
    ]
    odds_ratio, p_value = _fisher(matrix)
    results.append(
        (
            "support_escalation_by_snapshot", "Valid support escalation by snapshot state",
            "Eligible support tickets", "Escalation flag", "Snapshot churn flag",
            "Fisher exact", sum(map(sum, matrix)), float(odds_ratio), float(p_value),
            "Odds ratio", float(odds_ratio), None, None, _interpret(float(p_value)), "Observed",
            "Ticket-level association; repeated accounts are not independent.",
        )
    )

    for metric, column in (("first_response", "first_response_time_minutes"), ("csat", "satisfaction_score")):
        churned = [
            float(row[0]) for row in con.execute(
                f"""
                SELECT t.{column} FROM stage.support_tickets t
                JOIN gold.account_snapshot a USING (account_id)
                WHERE t.is_eligible AND a.snapshot_churn_flag AND t.{column} IS NOT NULL
                """
            ).fetchall()
        ]
        retained = [
            float(row[0]) for row in con.execute(
                f"""
                SELECT t.{column} FROM stage.support_tickets t
                JOIN gold.account_snapshot a USING (account_id)
                WHERE t.is_eligible AND NOT a.snapshot_churn_flag AND t.{column} IS NOT NULL
                """
            ).fetchall()
        ]
        if churned and retained:
            statistic, p_value = mannwhitneyu(churned, retained, alternative="two-sided")
            statistic_value: float | None = float(statistic)
            p_value_value: float | None = float(p_value)
            interpretation = _interpret(p_value_value)
        else:
            statistic_value = None
            p_value_value = None
            interpretation = "Insufficient sample"
        results.append(
            (
                f"support_{metric}_by_snapshot", f"Valid support {metric} by snapshot state",
                "Eligible support tickets", column, "Snapshot churn flag", "Mann-Whitney U",
                len(churned) + len(retained), statistic_value, p_value_value, None, None,
                None, None, interpretation, "Observed",
                "Ticket-level association; repeated accounts are not independent.",
            )
        )

    con.executemany(
        "INSERT INTO gold.statistical_tests VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        results,
    )
