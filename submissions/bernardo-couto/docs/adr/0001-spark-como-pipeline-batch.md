# ADR 0001 — Spark como pipeline batch de dados e ML

**Status:** aceito · **Data:** 2026-09-23

## Contexto
A Head de RevOps pediu algo que "sempre execute a classificação". O dataset tem 8.800 deals e caberia em pandas; o requisito, porém, é um pipeline reexecutável por data, com modelo versionado, que escale ao CRM inteiro.

## Decisão
PySpark 3.5 em `local[*]` para bronze → silver → gold (parquet particionado por `as_of`) e Spark ML `Pipeline` persistido em `models/<version>/`. Jobs idempotentes `build_features`, `train`, `score` com `--as-of`. API e web não usam Spark.

## Alternativas
pandas + scikit-learn (mais simples, sem caminho de escala nem particionamento point-in-time nativo); DuckDB (ótimo localmente, sem Spark ML). Delta Lake e MLflow adiados: ganho marginal frente ao custo no protótipo.

## Consequências
JDK 17/21 necessário só para reexecutar o pipeline (perfil `pipeline` do Compose ou host). Documentar que Spark é decisão de arquitetura, não necessidade de volume.
