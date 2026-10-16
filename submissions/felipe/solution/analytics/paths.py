"""Caminhos padronizados da submissão."""
from pathlib import Path

ANALYTICS = Path(__file__).resolve().parent
SOLUTION = ANALYTICS.parent
SUBMISSION = SOLUTION.parent

DATA = SUBMISSION / "data"
OUT = SOLUTION / "outputs"
REPORTS = SOLUTION / "reports"
FIG = OUT / "figures"
DASH_PUBLIC = SOLUTION / "command-center" / "public" / "data"
COMMAND_CENTER_DIST = SOLUTION / "command-center" / "dist"
