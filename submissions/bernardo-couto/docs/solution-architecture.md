# Arquitetura da solução

## Decisão de arquitetura (e sua justificativa honesta)

O dataset do challenge tem 8.800 oportunidades e caberia em pandas. Spark **não** foi escolhido por volume. Foi escolhido porque o pedido real da Head de RevOps é uma ferramenta que **sempre execute a classificação**: um pipeline reexecutável por data (`--as-of`), com modelo versionado e monitorado, que o time de dados possa agendar e que escale ao CRM inteiro sem reescrita. A experiência do vendedor, por outro lado, precisa abrir em segundos e rodar em qualquer máquina: por isso a API e o web **não** usam Spark em runtime e `docker compose up` sobe tudo com artefatos já gerados.

Trade-offs assumidos: JVM (JDK 17/21) como pré-requisito **apenas** para reexecutar o pipeline; mais peças (API, web, docs) do que um app monolítico. Contrapartidas: contrato único (`ScoredDeal`) do parquet ao navegador, Swagger completo, documentação navegável e um caminho direto para produção.

## Visão geral

```mermaid
flowchart LR
  subgraph batch["Pipeline batch · PySpark local[*] · perfil docker `pipeline` (JDK 17)"]
    RAW[("raw CSV<br/>imutável · SHA256")] --> BRONZE["bronze<br/>schema explícito · FAILFAST"]
    BRONZE --> SILVER["silver<br/>limpo · conformado · flags"]
    SILVER --> FEAT["gold/opportunity_features<br/>as_of=T"]
    SILVER --> HIST["gold/history_stats<br/>as_of=T · close_date ≤ T"]
    SILVER --> LAB["gold/labels<br/>as_of=T · só avaliação"]
    FEAT & HIST --> TRAIN["job train --as-of T"]
    LAB --> TRAIN
    TRAIN --> MODEL[("models/&lt;version&gt;<br/>PipelineModel · model card · metrics")]
    FEAT & HIST & MODEL --> SCORE["job score --as-of T"]
    SCORE --> SCORES[("gold/scores/as_of=T<br/>ScoredDeal · manifest · PSI")]
  end

  subgraph serve["Entrega · docker compose up · sem JVM"]
    API["API FastAPI<br/>/api/v1 · Swagger"]
    WEB["Web React + Vite<br/>design system G4"]
    DOCS["Docs MkDocs Material<br/>Markdown → HTML navegável"]
  end

  SCORES --> API
  MODEL --> API
  API --> WEB
  WEB -->|POST /feedback| FB[("data/feedback/actions")]
  FB -.-> SCORE
  API -->|openapi.json| DOCS

  SELLER(["Vendedor"]) --> WEB
  MANAGER(["Manager"]) --> WEB
  HEAD(["Head de RevOps"]) --> WEB
  DEV(["Avaliador / dev"]) --> DOCS
```

## Camadas de dados

| Camada | Conteúdo | Garantias |
|---|---|---|
| raw | 4 CSVs CC0 + `SHA256SUMS` | Imutável; verificado a cada job |
| bronze | Leitura com `StructType` explícito, `FAILFAST` | Nenhuma transformação; rastreabilidade por checksum |
| silver | Tabelas limpas e conformadas (`GTXPro→GTX Pro`, `technolgy→technology`, datas tipadas, flags `account_known`, `product_matched`) | Checks de qualidade falham o job; nenhuma linha perdida em join |
| gold | `opportunity_features`, `history_stats`, `labels`, `scores`, particionados por `as_of` | Point-in-time: só informação conhecida em `as_of`; labels fisicamente separados das features |

## Scoring em duas camadas

```mermaid
flowchart TD
  F["features do deal em as_of<br/>(produto, preço, idade em Engaging, Prospecting?)"] --> P["p_win = taxa de Won do produto (suavizada, α=20)<br/>× 0,5 se parado > 138 d"]
  F --> V["valor = sales_price × razão histórica × p_win<br/>(escala log normalizada)"]
  F --> U["urgência = hazard de Won em 14 d dada a idade<br/>parado = 0,2 · Prospecting = 0,5"]
  P --> S["priority_score = 25·p_win + 35·valor + 40·urgência<br/>tier A–D · confiança"]
  V --> S
  U --> S
  F -.-> C["Contexto (peso 0, informativo):<br/>agente, agente×produto, setor, conta, carga, sobrevivência"]
  M["Spark ML · LogisticRegression em modo sombra<br/>peso 0 até bater taxa-base (AUC-PR +0,02 e Brier ≤)"] -.-> S
  S --> X["reasons com pontos (PRODUCT_BASE_RATE, HIGH/LOW_TICKET,<br/>URGENCY_WINDOW, ZOMBIE_RISK) + contexto · next_action · score_breakdown"]
```

Por que assim: o backtest temporal mostrou que agente, setor, conta, carga e idade **não** preveem fechamento melhor que o acaso (AUC-ROC 0,44–0,53). Esses sinais ficam visíveis como contexto, mas não movem o score. O que a ferramenta entrega é ordenação por valor esperado × janela de decisão e a separação do pipeline parado.

Cada regra é uma função pura testada que emite um reason code. As contribuições do modelo entram na explicação apenas quando exatas (coeficiente × valor padronizado). `confidence` cai quando `account_known = false` ou o histórico do grupo é pequeno.

## Validação

```mermaid
gantt
  title Backtest temporal (walk-forward)
  dateFormat YYYY-MM-DD
  axisFormat %b/%y
  section Corte T1 = 2017-06-30
  histórico e treino (close_date ≤ T1) :a1, 2016-10-20, 2017-06-30
  avaliação (desfechos após T1)        :a2, 2017-07-01, 2017-12-31
  section Corte T2 = 2017-09-30
  histórico e treino (close_date ≤ T2) :b1, 2016-10-20, 2017-09-30
  avaliação (desfechos após T2)        :b2, 2017-10-01, 2017-12-31
```

Métricas: AUC-PR, Brier e calibração, lift do top decil, precision@k por vendedor, receita capturada no top 20%, com intervalos de confiança por bootstrap. Baselines: aleatório, preço, preço excluindo parados, mais novo, mais antigo, taxa-base por produto. `randomSplit`/`CrossValidator` são bloqueados por hook. Resultado: nenhum método prevê fechamento melhor que o acaso; a documentação diz isso e a tela Qualidade mostra o empate como frase padrão.

## Contrato único: `ScoredDeal`

```mermaid
flowchart LR
  P["Pydantic `ScoredDeal`<br/>(api/schemas.py)"] -->|gera| O["openapi.json"]
  O -->|openapi-typescript| T["schema.d.ts (web)"]
  Q["parquet gold/scores"] -->|validado no boot| P
```

Campos (schema 1.1.0+): `opportunity_id, sales_agent, manager, regional_office, product, sales_price, account, deal_stage, days_in_engaging, priority_score, tier, p_win, expected_value, urgency, confidence, reasons[], next_action, score_breakdown, as_of, model_version`.

## Operação

```mermaid
sequenceDiagram
  participant Cron as Agendador (cron / Airflow)
  participant Jobs as Jobs Spark
  participant Store as data/gold · models/
  participant API as API
  participant Web as Web
  Cron->>Jobs: build_features --as-of D
  Jobs->>Store: gold/*/as_of=D + manifest
  Cron->>Jobs: score --as-of D --model models/latest
  Jobs->>Store: gold/scores/as_of=D (+ PSI)
  API->>Store: recarrega as_of disponíveis
  Web->>API: GET /deals?as_of=D&sales_agent=…
  Web->>API: POST /feedback (ação do vendedor)
  API->>Store: data/feedback/actions
  Note over Jobs,Store: retreino = train --as-of D → nova versão → promover models/latest
```

- Jobs idempotentes; `manifest.json` por execução (parâmetros, git sha, checksums, contagens, duração, PSI).
- `models/<version>/` com `PipelineModel`, `model_card.md`, `metrics.json`, `feature_list.json`; `models/latest` é um ponteiro.
- Ambiente: uv + Python 3.12 + PySpark 3.5 + JDK 17/21 no host, ou perfil `pipeline` do Compose.

## Segurança e uso responsável

Dados públicos sem PII real, mas a ferramenta expõe desempenho individual: visão de manager contextualizada, sem ranking punitivo. Dependências auditadas (`pip-audit`, `npm audit`), segredos varridos, API com validação estrita e CORS restrito, imagens slim não-root. Detalhes em `security-review.md`.

## Decisões registradas (ADRs em `adr/`)

0001 Spark como pipeline batch · 0002 FastAPI + React · 0003 Docker Compose como forma de entrega · 0004 MkDocs Material · 0005 Sem LLM no scoring · 0006 Artefatos commitados para rodar sem JDK · 0007 Contrato `ScoredDeal` em pacote compartilhado.

## O que fica explicitamente fora

Sem dados de atividade (e-mails, reuniões); Prospecting sem datas; ~68% dos deals abertos sem conta; variância modesta entre agentes/produtos limita o poder preditivo; autenticação e multi-tenant fora do MVP. Ver `limitations.md`.
