---
status: passing
canonical: true
area: revops
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-003 Lead Scorer (`build-003-lead-scorer`)

## Comportamento visível

O candidato atua como AI Master de Vendas: 35 vendedores, ~8.800 oportunidades, priorização “no feeling”. A Head de RevOps quer **ferramenta que o vendedor abre na segunda** — não modelo morto em notebook.

Este é o único serviço cujo deliverable principal é **software funcionando**.

Persona da saída: vendedor não-técnico + Head de RevOps.

## Contrato

### Entrada

Quatro CSVs do CRM em [DATA-SOURCES.md](../architecture/DATA-SOURCES.md). Hub: `sales_pipeline.csv` (`opportunity_id`). Stages declarados: Prospecting, Engaging, Won, Lost.

### Obrigatório — solução

Válido: web (Streamlit, React, HTML+JS), Dash/Retool/Metabase, CLI, API de score, planilha com fórmulas, bot Slack/email.

Requisitos mínimos (todos):

1. **Roda** — não mockup, wireframe ou PowerPoint.
2. Usa os **dados reais** do dataset.
3. Tem **lógica de scoring/priorização** — ordenar só por valor **não** cumpre.
4. O vendedor entende **por que** o score é alto ou baixo (explainability).

### Obrigatório — docs

- Setup: dependências, comandos, URL.
- Lógica: critérios e por quê.
- Limitações: o que não faz e o que falta para escalar.

### Process log

Obrigatório. Vibe coding (Cursor, Claude Code, etc.) é esperado — o processo precisa aparecer.

### Diferencial

Filtro por vendedor / manager / região (dica do brief: fica imediatamente mais útil).

## Critérios de qualidade (aceitação)

| # | Critério | Fora |
|---|----------|------|
| Q1 | Dá para rodar pelas instruções | README sem comando / binário quebrado |
| Q2 | Scoring usa features além do óbvio raso | Só `close_value` desc |
| Q3 | Vendedor usa e entende | Score 0–100 sem razão |
| Q4 | UI ajuda decisão | Dump de tabela |
| Q5 | Código sustentável o bastante | Script único indecifrável |

Regra + heurística bem apresentada **vale mais** que XGBoost sem interface (texto do brief).

## Verificação

- [ ] README do challenge ainda diz “software funcionando” como principal.
- [ ] Submissão tem setup reproduzível e dados do Kaggle (não 10 rows fake).
- [ ] Cada deal priorizado tem explicação.
- [ ] Process log presente.

Não há porta oficial. Localhost do candidato é detalhe de setup, não contrato da plataforma.

## Evidência

2026-09-21: `challenges/build-003-lead-scorer/README.md` (Vendas / RevOps; Build; 4–6 h).

## Notas

Head não pediu ML perfeito. Pediu útil. Features óbvias (stage, tempo no pipe, tamanho da conta, produto, vendedor) são ponto de partida — a spec cobra o que **além** disso os dados sustentam.

Disco 2026-09-21: 85 / 7 / 35 / 8 800. `GTXPro` (1 480) não junta em `GTX Pro`. Account null em 1 425 deals abertos. Extra `metadata.csv`. ERD: [erd/build-003-lead-scorer.md](../erd/build-003-lead-scorer.md).

Lab Databricks (mesmo contrato de colunas): [notebook-build-003-lead-scorer](../../notebook-build-003-lead-scorer/README.md) — ingestão Lab 01, Assistant Lab 02, **entregável Lab 03** (ferramenta do vendedor), análise Lab 04. Spec do pacote: [SPEC-011-lab-003-databricks.md](SPEC-011-lab-003-databricks.md). Entregável: [SPEC-014](SPEC-014-lab-03-entregaveis.md).

## Sucesso / falha

- Sucesso: app filtra “meu pipe”, lista top N com score + 3 fatores (“stage Engaging + 40 dias + conta enterprise no setor Y”) e setup de 2 comandos.
- Falha: `model.pkl` + notebook sem UI, ou ranking = `close_value` sort.

## Migração e compatibilidade

Nomes `accounts.csv`, `products.csv`, `sales_teams.csv`, `sales_pipeline.csv` e stages Prospecting/Engaging/Won/Lost são o contrato público.
