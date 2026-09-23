# RavenStack raw data

The five CSV files in `raw/` are immutable inputs from the public Kaggle dataset
[SaaS Subscription and Churn Analytics Dataset](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset),
published by Rivalytics and retrieved on 2026-09-21.

The dataset is synthetic and contains no real customer PII. Kaggle's dataset metadata reports the
license as MIT and the owner as `Riv`; the challenge credits River @ Rivalytics. The files are
vendored to make this challenge submission reproducible, with source attribution preserved.

## Reproduction

```bash
work_dir=$(mktemp -d /tmp/ravenstack-data.XXXXXX)
curl -fsSL 'https://www.kaggle.com/api/v1/datasets/download/rivalytics/saas-subscription-and-churn-analytics-dataset' -o "$work_dir/data.zip"
unzip -q "$work_dir/data.zip" -d "$work_dir/data"
cp "$work_dir"/data/ravenstack_*.csv data/raw/
```

## SHA-256

| File | SHA-256 |
|---|---|
| `ravenstack_accounts.csv` | `348d8ba906b7776894b5236b2e7aa91a503d41670dbc9aad30c37b503c9abef5` |
| `ravenstack_churn_events.csv` | `6391c41d8291b7b4845ec9a84d3837c2ed230a33a32a854ec33d4e66dc150940` |
| `ravenstack_feature_usage.csv` | `c081da2be8caf987d07f0f79ceb0619aba523d819529230ed6df77984fa21d4e` |
| `ravenstack_subscriptions.csv` | `dcf1d93ca9a35e0dcba0ab686d255f0e9ec26512970bbf0944cf19cbef2d751a` |
| `ravenstack_support_tickets.csv` | `ba0006951479771ee9f93c98789c96bc5fec892cf11f867afb28194f0b76d220` |
