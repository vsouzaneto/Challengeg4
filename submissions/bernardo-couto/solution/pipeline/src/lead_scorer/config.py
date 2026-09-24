"""Project-wide constants. Time is always anchored on the data snapshot, never on the clock."""

from __future__ import annotations

from datetime import date
from pathlib import Path

# The CRM extract is a snapshot taken at this date. Every age/duration derives from it or from
# the ``--as-of`` cut of a backtest. Wall-clock time is forbidden in solution code.
SNAPSHOT_DATE = date(2017, 12, 31)

# Minimum backtest cuts required by the scoring-methodology skill.
BACKTEST_CUTS: tuple[date, ...] = (date(2017, 6, 30), date(2017, 9, 30))

# Paths are relative to ``solution/``, three levels above this file
# (lead_scorer/ -> src/ -> pipeline/ -> solution/).
SOLUTION_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = SOLUTION_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"
FEEDBACK_DIR = DATA_DIR / "feedback"
MODELS_DIR = SOLUTION_DIR / "models"
LATEST_MODEL_POINTER = MODELS_DIR / "latest"

RAW_FILES: tuple[str, ...] = (
    "sales_pipeline.csv",
    "accounts.csv",
    "products.csv",
    "sales_teams.csv",
)


def partition_dir(layer_dir: Path, table: str, as_of: date) -> Path:
    """Return ``<layer>/<table>/as_of=YYYY-MM-DD`` (Hive-style partition of every gold table)."""
    return layer_dir / table / f"as_of={as_of.isoformat()}"
