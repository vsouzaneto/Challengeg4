# Walkthrough comentado (equivalente notebook)

Passo a passo do raciocínio — reproduza com `python run_analysis.py`.

1. **Load** — 5 CSVs; manifest SHA256.
2. **QA joins** — `integration_qa.csv` (4 checks).
3. **Master** — grain conta; MRR da última subscription; agregados usage/tickets/events.
4. **Paradoxo** — compare `churn_events` vs `churn_flag`; calcule `revolving_active`.
5. **Uso CEO** — médias iguais; export `usage_by_industry_month.csv` para segmentos.
6. **Segmentos** — `segment_net_churn.csv`; DevTools/event.
7. **Risco** — score explicável; fila CSV/XLSX.
8. **Modelo** — LogReg; reportar AUC sem overselling.
9. **Relatórios** — CEO one-pager, playbook, causality register.

Comentários inline em `run_analysis.py` (funções nomeadas por etapa).
