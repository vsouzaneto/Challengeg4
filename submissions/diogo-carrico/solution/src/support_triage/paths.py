"""Filesystem locations shared by scripts, notebooks and the app."""

from pathlib import Path

SOLUTION_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = SOLUTION_DIR.parents[2]

# The upstream .gitignore excludes datasets/, so raw data stays out of git.
DATASETS_DIR = REPO_ROOT / "datasets"
TICKETS_DIR = DATASETS_DIR / "customer-support-tickets"
IT_TICKETS_DIR = DATASETS_DIR / "it-service-tickets"

OUTPUTS_DIR = SOLUTION_DIR / "outputs"
