# Apêndice técnico

## Grão analítico

Conta (`account_id`) enriquecida com última assinatura, agregados de `feature_usage` via `subscription_id`, tickets e histórico de `churn_events`.

## Modelo

LogisticRegression (balanced), hold-out 25%, **AUC = 0.623**.
Coeficientes: `outputs/model_top_coefficients.csv`.

## Artefatos

| Arquivo | Conteúdo |
|---------|----------|
| `cs_action_queue.csv` | Todas as contas ativas scored |
| `pre_churn_usage_window.csv` | Janela 30/60d antes do 1º churn |
| `segment_net_churn.csv` | Taxas por dimensão |
| `figures/*.png` | Gráficos para CEO |
| `usage_by_industry_month.csv` | Uso por indústria/mês |
| `recommendations_impact.csv` | Cenários de impacto MRR/ARR |
| `causality_register.md` | Correlação vs causalidade |

## Linhagem (5 tabelas)

Ver `../../docs/METODOLOGIA.md` (linhagem de dados).
