<img src="https://raw.githubusercontent.com/Databricks-BR/lab_agosto_2025/main/images/head_lab.png">

# LAB 03 — Dashboard AI/BI

Notebook: `lab03_dashboard.ipynb` — entregável do CEO (SPEC-001 / ENTREGAVEIS).

Publicado: [lab-001-churn-ceo](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611c23d1c1d8abb2e1d9847d535/published?o=7474644277755368) (`lab-001-churn-ceo.lvdash.json`).

Pré-requisito: tabelas `ravenstack_*` do Lab 01.

Sugestão de tiles (colunas reais):

- Contas com `churn_event` vs total (`ravenstack_churn_events` × `ravenstack_accounts`)
- `arr_amount` vigente (`end_date` nulo) por `industry` / `country`
- `reason_code` e `refund_amount_usd`
- País ordenado por volume de `churn_events` (taxa ao lado, não no ORDER BY)
- `resolution_time_hours` e `satisfaction_score` por `priority`

Não use `accounts.churn_flag` como KPI principal.

Painéis gráficos (Run All no notebook + página **Paineis** no `.lvdash.json`):

| Seção | Dado real |
| --- | --- |
| Ranking de benchmark | Eventos por `country` |
| Galeria de entrada | Amostra de contas com `churn_event` |
| Classificação | `reason_code` |
| Segmentação | `industry` × `plan_tier` |
| Segmentação de imagem | Indisponível (sem pixels) |
| Estatísticas / matriz / curva / viés | Baseline logístico, label = evento, não `churn_flag` |

Cabeçalho opcional:

```
![Image](https://raw.githubusercontent.com/Databricks-BR/lab_agosto_2025/refs/heads/main/images/head_lab.png)
```
