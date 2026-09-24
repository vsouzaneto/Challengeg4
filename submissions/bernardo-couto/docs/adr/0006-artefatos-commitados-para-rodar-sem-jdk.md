# ADR 0006 — Artefatos de saída commitados para rodar sem JDK

**Status:** aceito · **Data:** 2026-09-23

## Contexto
Spark exige JVM. O avaliador pode não ter JDK nem querer instalá-lo; a rubrica pune setup frágil.

## Decisão
Commitar `data/gold/scores/as_of=2017-12-31/` (parquet pequeno, contrato `ScoredDeal`) e `models/latest/` (model card, métricas, lista de features; o `PipelineModel` binário fica fora do git). Com isso `docker compose up` sobe API, web e docs sem JDK. O pipeline completo continua reproduzível via perfil `pipeline`.

## Consequências
Artefatos precisam ser regenerados e commitados a cada mudança de regra/modelo; `manifest.json` com git sha e checksums garante rastreabilidade. `/pr-check` verifica coerência entre código e artefatos.
