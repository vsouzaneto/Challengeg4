# API (FastAPI)

Serviço **somente leitura** sobre os artefatos do pipeline: lê `data/gold/scores/as_of=*`
(parquet) e `models/latest/{metrics.json,feature_list.json,model_card.md}` e os expõe em
`/api/v1`. Não usa Spark e **não recalcula nenhum score** — se um campo falta, ele é adicionado
no pipeline, nunca aqui. O contrato `ScoredDeal` vem do pacote compartilhado
`shared/lead_scorer_contracts` (ADR 0007); cada linha do parquet é validada contra ele no boot.

```bash
uv sync
uv run uvicorn api.main:app --reload --port 8000   # Swagger em http://localhost:8000/docs
uv run pytest -q
uv run ruff check . && uv run mypy src
uv run python -m api.export_openapi > ../docs-site/docs/api/openapi.json   # ou `make openapi` em solution/
```

## Endpoints

| Método | Rota | Descrição | Erros |
| --- | --- | --- | --- |
| GET | `/api/v1/health` | Liveness (não toca em disco). | — |
| GET | `/api/v1/meta` | Partições `as_of` disponíveis, versão do modelo, contagem de deals. Nunca 503. | — |
| GET | `/api/v1/deals` | Lista paginada. Filtros: `sales_agent`, `manager`, `regional_office`, `deal_stage`, `tier`, `min_score`, `account_known`, `queue=work\|confirm` (vivos + Prospecting vs. parados > 138 dias), `min_days_in_engaging`/`max_days_in_engaging`, `as_of`; `sort=-priority_score,...`; `limit`/`offset`. Resposta `{items, total, limit, offset, sort, as_of, model_version}`. | 404 (`AS_OF_NOT_FOUND`), 422, 503 |
| GET | `/api/v1/deals/{opportunity_id}` | Detalhe: score, `reasons`, `next_action`, `confidence`. | 404 (`DEAL_NOT_FOUND`), 422, 503 |
| GET | `/api/v1/agents` | Vendedores com deal aberto: gerente, região, contagem, valor esperado, tiers. | 404, 503 |
| GET | `/api/v1/managers` | Gerentes com time e totais. | 404, 503 |
| GET | `/api/v1/regions` | Escritórios regionais com gerentes e totais. | 404, 503 |
| GET | `/api/v1/pipeline/summary` | Visão do gerente: `group_by=manager\|sales_agent\|regional_office`, zumbis (> 138 dias) com valor esperado e nominal (`nominal_zombie_value`, soma de `sales_price`; nulo se a partição não tem a coluna), esfriando (101–138 dias: `cooling_count`/`cooling_value`), cobertura de conta, tiers. Filtros `sales_agent`, `manager`, `regional_office`, `as_of`. | 404, 422, 503 |
| GET | `/api/v1/model/metrics` | `metrics.json` (backtest vs. baselines), `feature_list.json`, model card. | 503 (`MODEL_ARTIFACTS_MISSING`) |
| POST | `/api/v1/feedback` | Registra ação do vendedor (`contacted`, `meeting_scheduled`, `proposal_sent`, `discard`, `account_fixed`, `closed_in_crm`, `note`; `note` ≤ 500 chars; `actor`). Append atômico em `data/feedback/actions.parquet`. Retorna 201 com o registro. | 404, 422, 503 |
| GET | `/api/v1/feedback` | Ações registradas (mais recente primeiro), filtro `opportunity_id`. | — |

Convenções:

- Toda resposta com dados de score traz `X-As-Of` e `X-Model-Version`.
- Erros sempre em `{"error": {"code", "message", "hint", "details?"}}`. `503` = pipeline ainda
  não rodou; o `hint` traz o comando (`make pipeline` ou `docker compose --profile pipeline run --rm pipeline`).
- `as_of` omitido = partição mais recente. Cortes de backtest (ex.: `2017-09-30`) são servidos
  igual, para a UI mostrar "o que o vendedor teria visto".
- `recorded_at` do feedback é o único relógio real do sistema (auditoria); nunca entra em score.

## Exemplos

```bash
# Top 10 de um vendedor
curl -s 'localhost:8000/api/v1/deals?sales_agent=Darcel%20Schlecht&limit=10' | jq '.items[] | {opportunity_id, priority_score, tier}'

# Time de um gerente sem conta cadastrada, mais antigos primeiro
curl -s 'localhost:8000/api/v1/deals?manager=Melvin%20Marxen&account_known=false&sort=-days_in_engaging'

# Fila "Confirmar ou encerrar": parados > 138 dias, mais valiosos primeiro; primeira onda 139-180 dias
curl -s 'localhost:8000/api/v1/deals?queue=confirm&sort=-expected_value&min_days_in_engaging=139&max_days_in_engaging=180'

# Detalhe com explicações
curl -s localhost:8000/api/v1/deals/Z063OYW0 | jq '.reasons[] | .text_pt'

# Visão do gerente por vendedor
curl -s 'localhost:8000/api/v1/pipeline/summary?manager=Melvin%20Marxen&group_by=sales_agent' | jq '.groups[] | {key, open_deals, zombie_count, account_coverage}'

# Snapshot de backtest (headers mostram a partição servida)
curl -si 'localhost:8000/api/v1/deals?as_of=2017-09-30&limit=1' | grep -i '^x-'

# Métricas do modelo
curl -s localhost:8000/api/v1/model/metrics | jq '.metrics'

# Registrar uma ação
curl -s -X POST localhost:8000/api/v1/feedback -H 'Content-Type: application/json' \
  -d '{"opportunity_id":"Z063OYW0","action":"contacted","note":"Reunião na quinta.","actor":"Darcel Schlecht"}'
```

## Configuração

Variáveis `LEAD_SCORER_*` (ver `src/api/settings.py`): `SCORES_DIR`, `MODELS_DIR`,
`FEEDBACK_DIR`, `CORS_ORIGINS` (JSON, padrão `http://localhost:5173` e `:4173`), `API_PREFIX`,
`VALIDATE_ON_BOOT` (padrão `true`: parquet fora do contrato derruba o boot com a linha inválida
no log).

`models/latest` pode ser um arquivo de uma linha com o nome da versão **ou** um
diretório/symlink para `models/<versão>/`; os dois formatos são aceitos.

## O que o parquet precisa ter

Colunas como em `ScoredDeal` (`lead_scorer_contracts.contracts`, schema 1.1.0). `sales_price` é opcional (partições anteriores sem a coluna são lidas com `null`; `nominal_zombie_value` fica nulo nelas). `reasons` pode ser
`array<struct<code,direction,weight,text_pt>>` ou uma string JSON; `as_of` pode estar ausente
dos arquivos (Spark remove a coluna de partição) — é preenchido pelo nome da pasta.
Arquivos `_SUCCESS`/`.crc` são ignorados.

## Testes

`tests/fixtures/` gera partições sintéticas a partir de `EXAMPLE_SCORED_DEAL` em um diretório
temporário do pytest (dois formatos de `reasons`, uma partição sem coluna `as_of`, um zumbi,
deals em Prospecting, contas ausentes). Nenhum parquet é commitado.
