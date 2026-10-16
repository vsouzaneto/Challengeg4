# Modelo, limites e o que a telemetria não vê

## Modelo preditivo

- **Algoritmo:** regressão logística (balanced), hold-out 25%.
- **AUC teste:** **0.623** — **triagem humana**, não automação de cancelamento.
- Coeficientes: `outputs/model_top_coefficients.csv`.

## O que os dados **não** provam

- Causa única de churn (correlação ≠ causalidade — ver `causality_register.md`).
- Churn futuro com precisão alta nesta base (AUC moderado).
- Motivações **humanas** invisíveis (saída de champion, build vs buy) — complementar com entrevistas, como em análises de mercado B2B.

## Como usar na operação

1. **Board:** KPI líquido + eventos + MRR revolving (não só volume de eventos).
2. **CS:** fila `fila_cs_top50.csv` + `motivo_risco` + playbook revolving.
3. **Dados:** reconciliar flags vs eventos (`data_quality_ceo.md`).

## Complemento à tese revolving

Telemetria estável + CSAT alto **coexistem** com churn porque métricas de **evento** e **reativação** mascaram a **porta giratória** — não porque o modelo “falhou”.
