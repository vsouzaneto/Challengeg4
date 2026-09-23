from hashlib import sha256
from pathlib import Path

import pandas as pd

RAW_FILE_SHA256 = {
    "ravenstack_accounts.csv": "348d8ba906b7776894b5236b2e7aa91a503d41670dbc9aad30c37b503c9abef5",
    "ravenstack_churn_events.csv": "6391c41d8291b7b4845ec9a84d3837c2ed230a33a32a854ec33d4e66dc150940",
    "ravenstack_feature_usage.csv": "c081da2be8caf987d07f0f79ceb0619aba523d819529230ed6df77984fa21d4e",
    "ravenstack_subscriptions.csv": "dcf1d93ca9a35e0dcba0ab686d255f0e9ec26512970bbf0944cf19cbef2d751a",
    "ravenstack_support_tickets.csv": "ba0006951479771ee9f93c98789c96bc5fec892cf11f867afb28194f0b76d220",
}
RAW_TABLE_NAMES = tuple(
    name.removeprefix("ravenstack_").removesuffix(".csv") for name in RAW_FILE_SHA256
)
DEFAULT_WINDOWS = (7, 30, 90)
DEFAULT_CUTOFFS = pd.date_range("2023-04-30", "2024-11-30", freq="ME")
SCORING_CUTOFF = pd.Timestamp("2024-12-31")
OBSERVATION_END = pd.Timestamp("2024-12-31")
HISTORICAL_START = pd.Timestamp("2023-04-01")
REFERENCE_PERIOD = (pd.Timestamp("2023-07-01"), pd.Timestamp("2023-12-31"))
RECENT_PERIOD = (pd.Timestamp("2024-06-01"), pd.Timestamp("2024-11-30"))
MIN_SEGMENT_ACCOUNTS = 30
MIN_SEGMENT_CHURNS = 10
MIN_COVERAGE = 0.70
RANDOM_SEED = 42
BOOTSTRAP_REPLICATES = 2_000


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()
