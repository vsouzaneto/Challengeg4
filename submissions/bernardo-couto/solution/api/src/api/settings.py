"""Runtime settings. Everything is overridable via ``LEAD_SCORER_*`` environment variables."""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# api/src/api/settings.py -> parents[3] == solution/
SOLUTION_DIR = Path(__file__).resolve().parents[3]

# Longest Won cycle observed in the snapshot (days). Above it a deal is a "zombie" (methodology
# skill). The API only uses it to aggregate; the pipeline is the one that emits ZOMBIE_RISK.
ZOMBIE_DAYS = 138
# Deals between p90 of the Won cycle and the zombie threshold are "cooling" (101-138 days).
COOLING_MIN_DAYS = 101


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LEAD_SCORER_", extra="ignore")

    scores_dir: Path = SOLUTION_DIR / "data" / "gold" / "scores"
    models_dir: Path = SOLUTION_DIR / "models"
    feedback_dir: Path = SOLUTION_DIR / "data" / "feedback"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:4173"]
    api_prefix: str = "/api/v1"
    # Fail the boot when the latest partition does not satisfy ``ScoredDeal``.
    validate_on_boot: bool = True

    @property
    def latest_model_pointer(self) -> Path:
        """``models/latest``: a one-line pointer file or a directory/symlink to ``models/<v>/``."""
        return self.models_dir / "latest"

    @property
    def feedback_file(self) -> Path:
        return self.feedback_dir / "actions.parquet"


settings = Settings()
