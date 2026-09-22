# Arquitetura — quatro serviços + pipeline compartilhado

Reverse-spec da leitura 2026-09-21. Não há processo, container ou porta. “Serviço” = challenge isolado com brief, contrato de dados e deliverable próprio.

## Topologia

```
                    README.md (proposta + FAQ)
                              │
                              ▼
                    challenges/README.md
                              │
        ┌──────────┬──────────┼──────────┬──────────┐
        ▼          ▼          ▼          ▼
     001-churn  002-support  003-scorer  004-social
     Dados      Ops / CX     Vendas      Marketing
        │          │          │          │
        └──────────┴────┬─────┴──────────┘
                        ▼
              Kaggle (datasets/ local, gitignored)
                        │
                        ▼
         submissions/<nome>/   (só no fork)
           README.md  (template)
           solution/
           process-log/
           docs/
                        │
                        ▼
              PR → main   [Submission] Nome — Challenge XXX
                        │
                        ▼
              banca  (_internal/ fora do git)
```

Os quatro serviços **não** compartilham schema, conta fictícia nem output. Compartilham só: time budget, process log, canal PR, template e a régua “superar o baseline”.

## Contratos por serviço

| Serviço | Entrada | Processamento esperado | Saída mínima |
|---------|---------|------------------------|--------------|
| **001** `data-001-churn` | 5 CSVs RavenStack (`account_id` / `subscription_id`) | Join entre tabelas; causa raiz ≠ correlação óbvia; peso de MRR | Relatório: causa + segmentos em risco + ações priorizadas |
| **002** `process-002-support` | ~30K tickets com métricas + ~48K textos classificados | Gargalos, drivers de CSAT, o que IA pode / não pode; ROI em horas | Diagnóstico + fluxo de automação; protótipo é diferencial |
| **003** `build-003-lead-scorer` | 4 tabelas CRM (~8.8K opps) | Scoring com features além de `close_value`; explainability | App/CLI/dashboard/API/planilha **que roda** + setup + limitações |
| **004** `marketing-004-social` | ~52K posts cross-platform | Engagement real, orgânico vs patrocinado controlado, o que parar | Análise + estratégia (foco, política de sponsor, quick wins) |

## Fronteiras

```
candidato ──baixa──► Kaggle ──CSV──► máquina local
                              │
                              X  este git não serve dado
                              X  este git não sobe app
                              X  este git não pontua
```

Runtime de cada solução (Streamlit, notebook, CLI, etc.) **nasce no fork**, em `submissions/<nome>/solution/`. Porta, stack e host são escolha do candidato (003 exige só: roda + dados reais + scoring explicável).

## O que não passa por aqui

- Orquestração 001→002→003→004.
- Auth, billing, Cloud Run, Firebase, Cloud SQL.
- Baseline dos modelos internos (não está no clone).
- Correção automática pública.

## Paths estáveis

| Recurso | Path |
|---------|------|
| Índice de serviços | `challenges/README.md` |
| Serviço 001 | `challenges/data-001-churn/` |
| Serviço 002 | `challenges/process-002-support/` |
| Serviço 003 | `challenges/build-003-lead-scorer/` |
| Serviço 004 | `challenges/marketing-004-social/` |
| Template | `templates/submission-template.md` |
| Pasta do candidato | `submissions/<nome>/` (gitignored no origin) |
| Downloads | `datasets/` (gitignored) |
