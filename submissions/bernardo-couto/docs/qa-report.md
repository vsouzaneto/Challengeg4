# Relatório de QA — Lead Scorer (Challenge 003)

**Data:** 2026-09-23 · **Autor:** quality-engineer (Claude Code) · **Commit base:** `4aed364` + árvore de trabalho
**Escopo:** simular o avaliador do G4 (clonar → seguir `solution/README.md`), testes automatizados,
adversarial do scoring, leakage, contrato da API, higiene do repositório, docs e web.

## Veredito

**Pronto para PR**, com as correções de documentação/staging aplicadas neste relatório (README e
`tools/git-stage.sh`) e 4 recomendações não bloqueantes abaixo.

## Tabela de verificações

Severidade: **crítica** (avaliador não consegue rodar) · **alta** (DoD violado) · **média** · **baixa**.

| # | Verificação | Resultado | Evidência (comando → trecho) | Severidade | Correção |
|---|---|---|---|---|---|
| 1a | Clean-room: staging reproduz a árvore | **FAIL → corrigido** | `bash tools/git-stage.sh` → 274 arquivos; `diff` staged × árvore: faltavam `web/src/features/feedback/{FeedbackProvider.tsx,feedbackStore.ts}`. `docker compose up --build` na cópia → `web: Cannot find module '../features/feedback/feedbackStore'` (exit 2) | crítica | `--exclude='feedback'` (não ancorado) casava `web/src/features/feedback`; trocado por `--exclude='**/data/feedback'` em `tools/git-stage.sh:15`. Re-stage: 276 arquivos, web compila |
| 1b | Clean-room caminho curto: `docker compose up --build -d` | PASS | `api Up (healthy)`, `docs Up`, `web Up`; `GET /api/v1/health` → `{"status":"ok","version":"1.0.0"}` | — | — |
| 1c | `/api/v1/meta` | PASS | `{"schema_version":"1.1.0","as_of_available":["2017-12-31"],"model_version":"2017-12-31-rules-v1","artifacts_present":true,"open_deals":2089}` | — | — |
| 1d | `/api/v1/deals?queue=confirm&limit=2` | PASS | 2 itens, tier C, `days_in_engaging=161`, `urgency=0.2`, reasons `HIGH_TICKET`, `ZOMBIE_RISK`, …; `sort=-sales_price,days_in_engaging` → HTTP 200 | — | — |
| 1e | `/api/v1/pipeline/summary`, `/api/v1/model/metrics` | PASS | summary: `open_deals=2089, zombie_count=1291, tiers A67/B516/C771/D735`; metrics: `spearman_score_price=0.4609`, backtest 2017-06-30 `auc_pr=0.661 [0.6115,0.6996]` | — | — |
| 1f | `/openapi.json` válido | PASS | `uvx openapi-spec-validator openapi-live.json` → `OK` (48 274 bytes) | — | — |
| 1g | Web raiz contém "Lead Scorer"; proxy `/api` | PASS | `docker exec web wget -qO- http://127.0.0.1/` → `<title>Lead Scorer · Vendas</title>`; `curl :5174/api/v1/health` → 200 (porta 5173 do host estava ocupada por Vite do usuário; usado override `5174:80`) | — | README ganhou seção "Porta ocupada?" |
| 1h | Docs raiz servida | PASS | `curl :8001/` → 200, `<title>Lead Scorer — Documentação</title>` | — | — |
| 1i | Imagens `api`/`web` sem pyspark | PASS | `ls site-packages \| grep -i pyspark\|py4j` na `api` → vazio; `find / -iname '*pyspark*'` na `web` → vazio. Tamanhos: api 666 MB, web 93 MB, docs 109 MB, pipeline 4,83 GB | — | — |
| 1j | Clean-room caminho completo: `--profile pipeline run --rm pipeline` | **FAIL → corrigido (doc)** | 1ª execução usou imagem `lead-scorer-pipeline` de 5 h atrás (stubs): `[build_features] not implemented yet`, exit 2. Com `--build`: `build_features → train (acceptance=passed, 75 s) → score (rows=2089, 7,85 s)`, exit 0 | alta | README: `docker compose --profile pipeline run --build --rm pipeline` |
| 1k | `docker compose --profile pipeline down -v` | PASS | containers/rede removidos; `docker ps -a --filter name=lead-scorer` → 0 | — | — |
| 1l | README fiel ao estado | **FAIL → corrigido** | Parágrafo "Estado atual: `train` e `score` são stubs" estava obsoleto; faltavam `-d`/espera por `healthy`, curls de verificação, `down -v`, aviso sobre `part-*` duplicado | média | `solution/README.md` reescrito (pt-BR) |
| 2a | `make test` — shared / api / pipeline | PASS | `5 passed in 0.05s` · `57 passed, 1 warning in 0.64s` · `64 passed in 60.02s` (JDK 21) | — | — |
| 2b | `make test` — web (vitest) | PASS | `Test Files 7 passed (7) · Tests 33 passed (33)` | — | — |
| 2c | `make lint` — python | PASS (após correção concorrente) | 1ª rodada: pipeline `ruff check` → `Found 160 errors` (todos em `pipeline/analysis/*.py`, E501/N816/I001). `pyproject.toml:44 extend-exclude=["analysis"]` adicionado às 22:28 por outro agente → `All checks passed!`, `39 files already formatted`; mypy `Success: 38 source files`. api/shared: limpos | — | — |
| 2d | `make lint` — web | PASS | eslint `0 errors, 3 warnings` (`react-refresh/only-export-components` em `App.tsx:13`, `Toast.tsx:28`, `test/utils.tsx:6`); prettier OK; `tsc -b --noEmit` OK | baixa | opcional: mover constantes exportadas para arquivo próprio |
| 3a | Spearman(priority_score, sales_price) < 0,9 | PASS | **0,4609** (rank-based, 2 089 linhas) | — | — |
| 3b | Zumbis (>138 d): tier ∈ {C,D}, score ≤ 49, ZOMBIE_RISK | PASS | 1 291 deals; `tier in C/D: True`; `max score 43.24`; `all ZOMBIE_RISK: True`; `urgency==0.2: True` | — | — |
| 3c | Sem conta ⇒ confidence ≠ alta, ACCOUNT_UNKNOWN | PASS | 1 425 deals sem conta; `alta` entre eles: **0**; `ACCOUNT_UNKNOWN all: True` | — | — |
| 3d | ≥1 reason por linha; sem NaN | PASS | `min reasons 5`; `NaN priority: 0`; único numérico com nulos: `days_in_engaging` (500 = Prospecting, por contrato) | — | — |
| 3e | Determinismo | PASS | hash das linhas (ordenadas por `opportunity_id`, reasons serializados) host `c266f60b8cdf11dd` = Docker `c266f60b8cdf11dd`; manifesto difere só em `generated_at`, `duration_seconds`, `git_sha`, `model_dir` | — | — |
| 3f | Point-in-time `history_stats/as_of=2017-09-30` | PASS | pandas sobre raw: `GTX Basic` fechados com `close_date ≤ 2017-09-30` → n=1025, won=658, rate=0,6420; gold → `n=1025 wins=658 win_rate=0.641951`. Global n=4726 (dos 6711 fechados; 1 985 posteriores excluídos) | — | — |
| 3g | Grep `now()\|today()\|current_date\|current_timestamp\|randomSplit\|CrossValidator\|TrainValidationSplit` em `pipeline/src api/src web/src` | PASS | único hit: `ml/model_card.py:119` (texto do model card dizendo que não usa) | — | — |
| 4a | `close_value\|close_date\|label_won` em `scoring/`, `ml/features.py`, `ml/pipeline.py` | PASS | hits só em `features.py:44-46` — entradas da **deny-list** `FORBIDDEN`, marcadas `# leakage-ok` (`label_won` na l.44 está na mesma lista) | — | — |
| 4b | idem em `ml/frame.py`, `ml/evaluate.py`, `data/gold.py` só com `# leakage-ok` | PASS | todos os usos de código marcados (24 marcações); hits não marcados são docstrings (`gold.py:8,13,93,118,231`, `frame.py:5`) | — | — |
| 5a | `openapi.json` tem `ScoredDeal.sales_price` | PASS | `anyOf [number ≥0, null]`, "Preço de tabela do produto…"; `python -m api.export_openapi` == `docs-site/docs/api/openapi.json` | — | — |
| 5b | `web/src/api/schema.d.ts` em sincronia | PASS | `openapi-typescript openapi-export.json -o /tmp/schema.d.ts; diff` → **IN SYNC** | — | — |
| 6a | Staged: contagem, tamanho, lixo, fora da pasta | PASS | 276 arquivos, **5,4 MB**; `generated: 0 · outside submission folder: 0`; nenhum `node_modules/.venv/dist/site` | — | — |
| 6b | Segredos (`uvx detect-secrets scan --all-files` no staged) | PASS (falsos positivos) | 7 arquivos com "Hex High Entropy String": SHA-256 dos CSVs (`_manifest.json`, `training_manifest.json`, chat-export — batem com `data/raw/SHA256SUMS`), id de exemplo do OpenAPI (`schemas.py:363`, `schema.d.ts:440`), `INTEGRITY_CHECKSUM` do MSW | — | — |
| 6c | `shasum -a 256 -c data/raw/SHA256SUMS` | PASS | 5× `OK` | — | — |
| 7 | `mkdocs build --strict` | PASS | `Documentation built in 4.47 seconds`, sem WARNING (re-executado após incluir esta página no nav) | — | — |
| 8 | Web (por último): `npm ci && typecheck && lint && test && build` | PASS | `added 470 packages`; tsc OK; eslint 0 erros; 33 testes; `dist/assets/index-*.js 303 kB (gzip 95 kB)`, `✓ built in 841ms` | — | — |

## Recomendações (não bloqueantes)

1. **Partição com `part-*` duplicado** (média) — `api/src/api/repository.py:160` lê **todos** os
   parquet da partição (`pq.read_table(path)`). Se o avaliador rodar o pipeline e depois
   `git checkout -- data/gold`, ficam dois `part-00000-*.parquet` e a API responde `open_deals: 4178`
   (reproduzido nesta QA). Sugestão: falhar com `ArtifactsInvalidError` quando houver
   `opportunity_id` duplicado, ou ler só os arquivos listados no `_manifest.json`. README já avisa.
2. **Imagem stale do perfil `pipeline`** (média) — `docker compose run` não reconstrói a imagem;
   além do `--build` no README, considere `pull_policy: build` no serviço `pipeline`
   (`solution/docker-compose.yml:70`).
3. **`git_sha=unknown` dentro do container** (baixa) — o manifesto gerado pelo perfil `pipeline`
   não tem o SHA (não há `.git` no contexto). Passar `GIT_SHA` como variável de ambiente no
   compose (`environment: GIT_SHA: ${GIT_SHA:-unknown}`) e ler em `lead_scorer/jobs`.
4. **eslint warnings `react-refresh/only-export-components`** (baixa) — `web/src/App.tsx:13`,
   `web/src/components/Toast.tsx:28`, `web/src/test/utils.tsx:6`.

## Erros da IA/processo encontrados nesta rodada

- `tools/git-stage.sh` excluía `feedback` sem âncora e deixou o módulo `web/src/features/feedback`
  fora do PR — o build da web falharia **exatamente na máquina do avaliador**, enquanto passava na
  máquina do autor. Corrigido e verificado em clean-room.
- README declarava `train`/`score` como stubs depois de os jobs estarem implementados.

## Comandos de reprodução

```bash
# 0. ambiente
export JAVA_HOME=$(/usr/libexec/java_home -v 21); docker info >/dev/null

# 1. clean-room: só o que o stage script sobe
cd <raiz-do-repo>; bash submissions/bernardo-couto/tools/git-stage.sh
CR=$TMPDIR/leadscorer-cleanroom; rm -rf "$CR"; mkdir -p "$CR"
git diff --cached --name-only -z | rsync -a --files-from=- --from0 . "$CR/"; git reset -q
cd "$CR/submissions/bernardo-couto/solution"
docker compose up --build -d && docker compose ps
curl -s localhost:8000/api/v1/health; curl -s localhost:8000/api/v1/meta
curl -s 'localhost:8000/api/v1/deals?queue=confirm&limit=2'
curl -s localhost:8000/api/v1/pipeline/summary; curl -s localhost:8000/api/v1/model/metrics
curl -s localhost:8000/openapi.json > /tmp/openapi.json && uvx openapi-spec-validator /tmp/openapi.json
docker compose exec web wget -qO- http://127.0.0.1/ | grep -c 'Lead Scorer'; curl -sI localhost:8001/
docker compose exec api sh -c 'ls /app/api/.venv/lib/python3.12/site-packages | grep -i pyspark || echo sem-pyspark'
docker compose --profile pipeline run --build --rm pipeline
docker compose --profile pipeline down -v

# 2. testes e lint na árvore real
cd submissions/bernardo-couto/solution && make test && make lint

# 3. adversarial (pipeline/.venv tem pandas+pyarrow)
cd pipeline && uv run python - <<'PY'
import pandas as pd, numpy as np
df = pd.read_parquet("../data/gold/scores/as_of=2017-12-31")
print(np.corrcoef(df.priority_score.rank(), df.sales_price.rank())[0, 1])          # 0.4609
z = df[df.days_in_engaging > 138]; print(len(z), z.tier.isin(["C","D"]).all(), z.priority_score.max())
na = df[df.account.isna()]; print(len(na), (na.confidence == "alta").sum())
print(df.reasons.apply(len).min(), df.priority_score.isna().sum())
PY

# 4. leakage / relógio
grep -rnE 'now\(\)|today\(\)|current_date|current_timestamp|randomSplit|CrossValidator|TrainValidationSplit' pipeline/src api/src web/src
grep -rnE 'close_value|close_date|label_won' pipeline/src/lead_scorer/scoring pipeline/src/lead_scorer/ml/features.py pipeline/src/lead_scorer/ml/pipeline.py

# 5. contrato
(cd api && uv run python -m api.export_openapi > /tmp/o.json) && diff <(python3 -m json.tool /tmp/o.json) <(python3 -m json.tool docs-site/docs/api/openapi.json)
(cd web && npx openapi-typescript /tmp/o.json -o /tmp/schema.d.ts && diff -q src/api/schema.d.ts /tmp/schema.d.ts)

# 6–8. higiene, docs, web
(cd data/raw && shasum -a 256 -c SHA256SUMS); uvx detect-secrets scan --all-files "$CR/submissions/bernardo-couto"
(cd docs-site && uv run mkdocs build --strict)
(cd web && npm ci && npm run typecheck && npm run lint && npm run test && npm run build)
```
