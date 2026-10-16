# Playbook CS — Contas revolving (uso amanhã)

_Gerado por `run_analysis.py`. Importe `outputs/cs_action_queue.xlsx` no CRM._

## Ritual semanal (30 min)

1. Filtrar fila `Ligar esta semana` + ordenar por `mrr_priority`.
2. Para cada conta: ler `why_risk` + último ticket.
3. Registrar outcome (retenção / downgrade / churn) — alimentar modelo futuro.

## Top 10 contas por MRR (com histórico de churn)

| account_id | MRR | eventos | industry |
|------------|-----|---------|----------|
| A-56962b | 32,437 | 2 | EdTech |
| A-afa505 | 13,930 | 1 | DevTools |
| A-7e0a10 | 13,930 | 1 | FinTech |
| A-09316c | 13,930 | 1 | FinTech |
| A-c58f49 | 13,930 | 3 | EdTech |
| A-0651a4 | 12,935 | 2 | HealthTech |
| A-d792a6 | 12,935 | 2 | DevTools |
| A-158f4e | 12,139 | 2 | FinTech |
| A-855a48 | 11,940 | 1 | EdTech |
| A-c37601 | 10,746 | 1 | EdTech |

## Script de ligação (60s)

- "Notamos que vocês já passaram por cancelamento antes — queremos garantir que o valor está claro."
- "Há algo no suporte (escalações) ou no rollout que podemos destravar esta semana?"

## O que NÃO fazer

- Não usar `reason_code` do último churn como verdade — autoreporte é ruidoso.
- Não prometer feature roadmap baseado só em usage agregado (uso médio é igual entre grupos).
