# ADR 0007 — Contrato `ScoredDeal` em pacote Python compartilhado

**Status:** aceito · **Data:** 2026-09-23

## Contexto
O pipeline (PySpark) grava `gold/scores` e a API (FastAPI) o serve e gera o OpenAPI de onde saem os tipos TS. Os dois são projetos uv separados (o pipeline exige JDK; a API não pode depender de pyspark). O contrato `ScoredDeal` precisa ser **um só**: duplicá-lo em `pipeline/` e `api/` inevitavelmente diverge.

## Decisão
Pacote mínimo `solution/shared/lead_scorer_contracts/` (só `pydantic`) contendo `ScoredDeal`, `Reason`, `ReasonCode` e `SCHEMA_VERSION`. `pipeline` e `api` o declaram como dependência por caminho (`[tool.uv.sources] … path = "../shared/lead_scorer_contracts", editable = true`). `lead_scorer.contracts` e `api.schemas` apenas reexportam. Nos Dockerfiles o contexto de build é `solution/` para que o pacote esteja disponível.

## Alternativas
- A API importar `lead_scorer.contracts` do pipeline: arrastaria `pyspark` (e a JVM) para a imagem da API.
- Duplicar o modelo nos dois lados com um teste de igualdade de JSON Schema: funciona, mas é atrito permanente e o teste só falha depois da divergência.
- Gerar os modelos a partir de um JSON Schema versionado: mais infraestrutura do que o protótipo justifica.

## Consequências
Uma mudança de contrato é um commit em um único arquivo + bump de `SCHEMA_VERSION` + regeneração dos artefatos e do `schema.d.ts`. Custo: um `pyproject.toml` a mais e contexto de build do Docker na raiz de `solution/`.
