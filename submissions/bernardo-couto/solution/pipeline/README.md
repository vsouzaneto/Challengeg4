# Pipeline (PySpark)

Jobs `build_features`, `train` e `score`, todos com `--as-of`. Precisa de JDK 17 ou 21 no host
(`lead_scorer/spark.py` resolve `JAVA_HOME`) ou do perfil `pipeline` do Docker Compose.

```bash
uv sync
uv run pytest -q
uv run python -m lead_scorer.jobs build-features --as-of 2017-12-31
```

Camadas de dados (`lead_scorer/data/`): `schemas.py` (StructType dos 4 CSVs) → `load.py` (bronze,
checksums) → `clean.py` (única fonte de correções) → `silver.py` (joins com flags) → `checks.py`
(expectativas que falham o job) → `gold.py` (`opportunity_features`, `history_stats`, `labels` por
`as_of`, com `_manifest.json`). Achados e decisões em `../../docs/data-quality-report.md`.

Ver `../README.md` e a skill `spark-ml-practices`.
