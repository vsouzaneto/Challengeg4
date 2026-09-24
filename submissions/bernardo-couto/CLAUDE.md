# Lead Scorer — G4 AI Master Challenge 003

Projeto de submissão de **Bernardo Couto** para o Challenge 003 (Vendas / RevOps).
Este diretório é a raiz do projeto Claude Code: rode `claude` **a partir daqui**, nunca da raiz do repositório.

## Missão

Construir uma ferramenta **funcional** que um vendedor abre na segunda-feira de manhã e sabe em quais deals focar.
Cada deal tem um score **explicável** (o vendedor entende POR QUE), com filtros por vendedor, manager e região.
Deliverables obrigatórios: software rodando + documentação (setup, lógica, limitações) + process log com evidências.

Referências obrigatórias (leia antes de decidir qualquer coisa de produto):
- Brief do challenge: `../../challenges/build-003-lead-scorer/README.md`
- Regras de submissão: `../../CONTRIBUTING.md`, `../../submission-guide.md`, `../../templates/submission-template.md`

## O que "supreender" significa aqui

O G4 já rodou este brief em Claude/GPT/Gemini. **Igual ao baseline = reprovado.** Superamos o baseline com:
1. **Julgamento sobre os dados** (achados verificados, não suposições): ver skill `crm-dataset`.
2. **Scoring honesto**: probabilidade × valor × urgência, backtest temporal, calibração, zero leakage. Ver skill `scoring-methodology`.
3. **UX para decisão**, não para exibir dados: "o que fazer hoje" antes de qualquer tabela.
4. **Process log que mostra iteração e onde a IA errou**, não um prompt único.

## O que é baseline e o que é diferencial

Soma ponderada de fatores + tabela filtrável + os achados do dataset abaixo são o **mínimo esperado**, não diferencial. Diferencial: walk-forward temporal com baselines (aleatório, preço, **mais novo primeiro**) e intervalos de confiança; testes anti-leakage; hipóteses registradas antes da análise com refutações; erros da IA com causa-raiz; controle as-of na UI; pipeline reproduzível com artefatos versionados e execução agendada; API documentada; guardrails reais (hooks) versionados. `gold/scores/as_of=2017-12-31` e `models/latest` ficam commitados para a UI abrir sem JDK.

## Fatos do dataset que NÃO podem ser esquecidos

- Snapshot dos dados: **2017-12-31**. Toda idade/tempo é ancorada em `SNAPSHOT_DATE`, jamais em `today()`.
- 2.089 deals abertos (1.589 Engaging + 500 Prospecting). **~68% deles não têm `account`** → scoring degrada com elegância; nunca descartar.
- `close_value` e `close_date` só existem depois do desfecho → **leakage**. Proibidos como feature. Valor esperado vem de `products.sales_price` e histórico de Won por produto.
- Deals Lost morrem rápido (mediana 14 dias); Won demoram (mediana 57). Idade em Engaging é sinal de sobrevivência até ~90 dias, depois vira risco de deal zumbi (ciclo máx. observado: 138 dias).
- Sujeira: `GTXPro` (pipeline) ≠ `GTX Pro` (catálogo); setor `technolgy`. Corrigir em código, nunca no CSV.
- Win rate global 63%; variância por produto (60–65%) e agente (55–70%) é modesta → não superestimar poder preditivo; comunicar incerteza.

## Stack e convenções

- **Entrega**: `docker compose up` sobe **API FastAPI** (Swagger em `/docs`), **web React** (Vite + TS + Tailwind com tokens do G4) e **docs MkDocs Material** (documentação navegável gerada dos `.md`). Perfil `pipeline` (imagem com JDK 17) roda os jobs Spark. Caminho curto sem JDK graças aos artefatos commitados (`gold/scores/as_of=2017-12-31`, `models/latest`).
- **Pipeline de dados e ML em PySpark 3.5** (`local[*]`, JDK 17/21 — o JDK 23 padrão desta máquina não é suportado; `lead_scorer/spark.py` resolve `JAVA_HOME`). Bronze → silver → gold em parquet particionado por `as_of`; Spark ML `Pipeline` versionado em `models/<version>/` com model card. Ver skill `spark-ml-practices`. Spark é decisão de arquitetura (pipeline reexecutável, escalável ao CRM inteiro), não necessidade de volume: dizer isso na documentação.
- **Scoring em duas camadas**: regras transparentes (reason codes) + modelo Spark ML (LogisticRegression por padrão; GBT só se bater com margem). Validação **temporal**; `randomSplit`/`CrossValidator` proibidos. **Sem LLM no scoring** (ADR 0005: Jev/LLMs avaliados e rejeitados — dados tabulares próprios, explicabilidade exata e execução offline valem mais).
- **API** só lê artefatos e serve (`ScoredDeal` Pydantic = contrato único; tipos TS gerados do OpenAPI). **Web** só apresenta. Nenhuma lógica de score fora do pipeline.
- Python 3.12 via **uv** (`pipeline/`, `api/`, `docs-site/`); Node 20 via npm (`web/`). Testes: pytest (fixture `spark`), pytest + httpx, Vitest. Lint: ruff + mypy, eslint + tsc. Segurança: `pip-audit`, `detect-secrets`, `npm audit` via `uvx`/`npx`.
- Layout: `solution/{pipeline,api,web,docs-site,data,models,docker-compose.yml,Makefile}`; `pipeline/src/lead_scorer/{data,ml,scoring,jobs,spark.py}`.
- Código, identificadores, commits e comentários em **inglês**. Documentação para humanos (README, docs, process log, UI, model card) em **português do Brasil**. Diagramas **sempre em Mermaid**.
- Design: tokens do G4 na skill `g4-design-system`; sem logo do G4 embutido; contraste AA.
- Cada regra de score é uma função pura, testada, com um `reason code` legível na UI. Contribuições do modelo só entram na explicação se exatas ou por método testado.

## Regras de git e submissão (invioláveis)

- Só alterar arquivos dentro de `submissions/bernardo-couto/`. PR que toca fora é rejeitado.
- A raiz do repositório ignora `submissions/` no `.gitignore`. **Nunca** use `git add -f` direto (ele ignora também o nosso `.gitignore` e arrasta `node_modules`/`.venv`): use `tools/git-stage.sh`, que adiciona só o que deve entrar e valida. Nunca editar o `.gitignore` da raiz.
- Branch `submission/bernardo-couto`; PR para `main` com título `[Submission] Bernardo Couto — Challenge 003`.
- Commits pequenos e frequentes: o git history é evidência de processo. Nunca `--force`, nunca `--no-verify`.
- Nunca commitar segredos, `.env`, credenciais do Kaggle ou dados processados.

## Como trabalhar neste projeto

Fluxo padrão: **produto (product-manager → product-owner → revops-engineer) → arquitetura (tech-lead, ADRs) → dados (data-engineer) → scoring (data-scientist → machine-learning-engineer) → API (backend-engineer) ∥ design (product-designer) → web (application-engineer) → testes (quality-engineer) → revisão (code-reviewer + security-engineer + g4-evaluator) → docs (tech-writer)**. O `tech-lead` desempata; o `product-owner` corta escopo.

- Delegue para os subagents em `.claude/agents/` quando a tarefa casar com a especialidade; passe contexto e o critério de pronto.
- Antes de afirmar qualquer número, rode o código que o produz. Sem "provavelmente".
- Toda decisão não óbvia vira uma entrada em `process-log/decisions.md` (use `/log-process`). Erros da IA que você corrigiu vão para lá com destaque.
- Antes de abrir/atualizar PR, rode `/pr-check`.
- Hooks em `.claude/settings.json` bloqueiam: edição fora desta pasta, escrita em `data/raw/`, comandos destrutivos, leakage em código de scoring, relógio real (`today()`, `current_date()`) e split aleatório (`randomSplit`, `CrossValidator`) em código de solução. Se um hook bloquear, ele está certo até prova em contrário; explique no log se discordar.

## Definição de pronto (DoD)

- `make test` e `make lint` verdes (pipeline, api, web); `mkdocs build --strict` sem avisos.
- `build_features → train → score` rodam do zero por `uv run python -m lead_scorer.jobs.<job> --as-of 2017-12-31`; reexecução idempotente; `models/latest` com model card.
- `docker compose up` do zero em máquina limpa sobe web, API (Swagger completo, `openapi.json` válido) e docs, sem JDK e sem chave de API.
- Um vendedor entende o top 10 e o motivo de cada score em menos de 1 minuto; UI segue os tokens do G4 com contraste AA.
- `docs/security-review.md` sem achados críticos; `pip-audit`/`npm audit` limpos ou justificados.
- README da submissão segue o template do G4; process log tem ≥1 erro da IA corrigido documentado; ADRs para cada decisão estrutural.
