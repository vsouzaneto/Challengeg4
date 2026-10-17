from pathlib import Path
import pandas as pd
from src.diagnostics import OperationalDiagnostics


def test_unresolved_snapshot_count_counts_non_closed_rows(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    df = pd.DataFrame({
        "Ticket ID": [1, 2, 3, 4],
        "Ticket Type": ["A"] * 4,
        "Ticket Status": ["Closed", "Open", "Pending Customer Response", "Closed"],
        "Ticket Priority": ["Low"] * 4,
        "Ticket Channel": ["Email"] * 4,
        "Customer Satisfaction Rating": [3, None, None, 4],
        "First Response Time": [None, None, None, None],
        "Time to Resolution": [None, None, None, None],
    })
    df.to_csv(raw_dir / "tickets.csv", index=False)

    result = OperationalDiagnostics(raw_dir).run()

    assert result["waste"]["unresolved_snapshot_count"] == 2
    assert result["waste"]["unresolved_snapshot_pct"] == 50.0

def test_scope_normalization_keeps_observed_base_separate_from_annual_context(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    n = 8469
    df = pd.DataFrame({
        "Ticket ID": range(1, n + 1),
        "Ticket Type": ["A"] * n,
        "Ticket Status": ["Closed"] * n,
        "Ticket Priority": ["Low"] * n,
        "Ticket Channel": ["Email"] * n,
        "Customer Satisfaction Rating": [3] * n,
        "First Response Time": [None] * n,
        "Time to Resolution": [None] * n,
    })
    df.to_csv(raw_dir / "tickets.csv", index=False)

    result = OperationalDiagnostics(raw_dir, annual_context=30000).run()
    scope = result["scope"]

    assert scope["observed_tickets"] == 8469
    assert scope["observed_base_pct"] == 100.0
    assert scope["annual_context_tickets"] == 30000
    assert scope["relative_to_annual_context_pct"] == 28.23
    assert scope["equivalent_volume_days"] == 103.04
    assert scope["period_observed"] is None
