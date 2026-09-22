---
status: passing
canonical: true
area: dados
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-001 Diagnóstico de Churn (`data-001-churn`)

## Comportamento visível

O candidato atua como AI Master da **RavenStack** (SaaS B2B, ~500 contas, assinatura mensal/anual). O CEO vê churn subir enquanto CS diz satisfação ok e Produto diz que o uso cresceu. A entrega responde **o que está acontecendo de verdade**, cruzando as cinco tabelas.

Persona da saída: CEO não-técnico.

## Contrato

### Entrada

Cinco CSVs do dataset Kaggle declarado em [DATA-SOURCES.md](../architecture/DATA-SOURCES.md). Joins: `account_id`, `subscription_id`. Análise em uma tabela só = fora de contrato.

### Obrigatório

Relatório (formato livre: PDF, Markdown, Notion, notebook, dashboard) com:

1. **Causa raiz do churn** — não a resposta óbvia; evidência no cruzamento.
2. **Segmentos em risco** — com dados; contas específicas, não só média.
3. **Ações** — concretas, priorizadas, com impacto estimado.

### Diferencial (não gate)

Modelo preditivo; dashboard; automação para CS; análise não pedida que muda a conversa.

### Process log

Obrigatório. Ver [SPEC-005-submission.md](SPEC-005-submission.md).

## Critérios de qualidade (aceitação)

| # | Critério | Fora |
|---|----------|------|
| Q1 | 5 tabelas cruzadas | Olhar uma tabela |
| Q2 | Insights verificáveis (números) | Feeling / “CS diz que…” |
| Q3 | Recomendações acionáveis | “Melhorar a experiência do cliente” |
| Q4 | Distingue correlação de causalidade | “Uso caiu, logo causou churn” sem controle |
| Q5 | CEO lê e age | Jargão sem executive summary |

Peso: perder conta de $5K/mês ≠ $50/mês (dica do brief). “Uso cresceu” deve ser testado **por segmento**.

## Verificação

Não há teste automatizado neste git. Banca / maintainer confere:

- [ ] README do challenge ainda cita as 5 tabelas e o quote do CEO.
- [ ] Submissão mostra joins (não só `churn_events`).
- [ ] Recomendações têm dono/ação/impacto, não slogan.
- [ ] Process log presente.

## Evidência

2026-09-21: `challenges/data-001-churn/README.md` (área Dados / Analytics, tipo Análise, 4–6 h).

## Notas

Empresa **RavenStack** é cenário. Não ligar a Cloud SQL / glam / Bfluence.

Disco 2026-09-21: 5 CSVs batem o n do brief. Schema extra no dump (`account_name`, `seats`, `usage_id` com 21 dups). **`accounts.churn_flag` ≠ `churn_events`** — label canônico = evento. ERD: [erd/data-001-churn.md](../erd/data-001-churn.md).

Lab Databricks (mesmo contrato de colunas): [notebook-data-001-churn](../../notebook-data-001-churn/README.md) — ingestão Lab 01, Assistant Lab 02, **entregável Lab 03**, análise Lab 04. Spec do pacote: [SPEC-009-lab-001-databricks.md](SPEC-009-lab-001-databricks.md). Entregável: [SPEC-014](SPEC-014-lab-03-entregaveis.md).

## Sucesso / falha

- Sucesso: “Contas anuais do canal X com downgrade + tickets de feature Y churnam 3,1×; lista de N contas e playbook CS nesta semana.”
- Falha: “O churn aumentou porque a satisfação caiu” sem cruzar usage × tickets × MRR.

## Migração e compatibilidade

Nomes de arquivo `ravenstack_*.csv` e chaves `account_id` / `subscription_id` são o contrato público. Trocar dataset = bump desta spec + DATA-SOURCES + ERD.
