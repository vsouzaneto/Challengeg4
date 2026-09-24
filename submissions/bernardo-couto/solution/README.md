# Lead Scorer — como rodar

Ferramenta que o vendedor abre na segunda-feira e sabe em quais deals focar, com o motivo de cada
score. Snapshot dos dados: **2017-12-31** (nada aqui usa o relógio da máquina).

## Caminho curto (só Docker)

```bash
cd solution
docker compose up --build -d          # ~2 min na primeira vez (3 imagens)
docker compose ps                     # espere `api` ficar (healthy); `web` só sobe depois disso
```

| Serviço | URL | O que é |
|---|---|---|
| web | http://localhost:5173 | Tela do vendedor (React + tokens do G4) |
| api | http://localhost:8000/docs | Swagger da API FastAPI (`/api/v1`) |
| docs | http://localhost:8001 | Documentação navegável (MkDocs Material) |

Sobe sem JDK e sem chave de API porque os artefatos (`data/gold/scores/as_of=2017-12-31`,
`models/latest`) ficam commitados (ADR 0006). Para conferir que subiu certo:

```bash
curl -s localhost:8000/api/v1/health                      # {"status":"ok",...}
curl -s localhost:8000/api/v1/meta                        # "artifacts_present":true,"open_deals":2089
curl -s 'localhost:8000/api/v1/deals?queue=confirm&limit=2'
curl -s localhost:5173/ | grep -c 'Lead Scorer'           # 1
```

**Porta ocupada?** Se já existe algo em `5173`/`8000`/`8001`, crie um override sem editar o
compose (exemplo para a web):

```bash
printf 'services:\n  web:\n    ports: ["5174:80"]\n' > /tmp/ports.yml
docker compose -f docker-compose.yml -f /tmp/ports.yml up --build -d
```

Para derrubar tudo (containers, rede e volumes): `docker compose --profile pipeline down -v`.

## Caminho completo (reexecutar o pipeline Spark)

Com Docker (imagem com JDK 17; `--build` garante que a imagem reflete o código atual):

```bash
docker compose --profile pipeline run --build --rm pipeline
```

O job grava em `data/{bronze,silver,gold}` e `models/` do host (bind mount) e leva ~2 min
(`build_features → train → score`). A reexecução é idempotente: o `score` reescreve a partição
`gold/scores/as_of=2017-12-31` com **linhas idênticas** às commitadas (mesmo hash; só mudam
`generated_at`/`git_sha` no `_manifest.json`). Como o Spark gera um novo nome de arquivo
`part-*.parquet`, o `git status` mostra o arquivo antigo como removido e o novo como não rastreado;
**não** use `git checkout -- data/gold` depois de rodar o pipeline sem apagar o `part-*` novo, senão a
partição fica com dois arquivos e a API passa a contar 4.178 deals.

No host (uv + JDK 17 ou 21; o JDK 23 não é suportado pelo Spark 3.5 e `lead_scorer/spark.py`
aborta com instrução em português se só houver 23+):

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21)   # macOS
make install
make pipeline AS_OF=2017-12-31   # build_features -> train -> score
```

## Sem Docker (desenvolvimento)

```bash
make install
(cd api && uv run uvicorn api.main:app --reload --port 8000)
(cd web && npm run dev)                          # http://localhost:5173, proxy /api -> :8000
(cd docs-site && uv run mkdocs serve -a localhost:8001)
```

## Testes e lint

```bash
make test     # pytest (contracts 5, pipeline 64 com fixture Spark, api 57) + vitest (web 33)
make lint     # ruff + mypy + eslint + prettier + tsc
make docs     # exporta openapi.json e roda mkdocs build --strict
make gen-api  # regenera web/src/api/schema.d.ts a partir do OpenAPI
```

`make test` e `make pipeline` exigem `JAVA_HOME` apontando para JDK 17/21 (o `Makefile` tenta
`/usr/libexec/java_home -v 21` sozinho no macOS). O relatório de QA da entrega está em
`../docs/qa-report.md`.

## Layout

```
solution/
├── shared/lead_scorer_contracts/  contrato ScoredDeal (fonte única, ADR 0007)
├── pipeline/                      PySpark: lead_scorer/{data,ml,scoring,jobs}
├── api/                           FastAPI: lê gold/scores + models/latest
├── web/                           React + Vite + TS + Tailwind
├── docs-site/                     MkDocs Material (inclui ../docs e ../process-log)
├── data/  models/                 artefatos (raw imutável)
├── docker-compose.yml  Makefile
```

Documentação de produto, dados, scoring e arquitetura em `../docs/`; processo e decisões em
`../process-log/`.
