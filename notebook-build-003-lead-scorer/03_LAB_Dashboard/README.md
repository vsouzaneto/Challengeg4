# LAB 03 — Dashboard AI/BI

Notebook: `lab03_dashboard.ipynb` — priorização do pipe aberto com `score` + `why` (SPEC-003 / ENTREGAVEIS).

Publicado: [lab-003-crm-seller](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611cd0118a78e40dc8a5f8a3609/published?o=7474644277755368) (`lab-003-crm-seller.lvdash.json`).

Pré-requisito: tabelas `accounts` / `products` / `sales_teams` / `sales_pipeline` do Lab 01.

Sugestão de tiles (colunas reais):

- Volume por `deal_stage` (aberto = Prospecting + Engaging)
- Win rate Won/(Won+Lost) por `regional_office` / `manager` (join `sales_teams`)
- Órfãos: `sales_pipeline.product` sem match em `products` depois de `GTXPro` → `GTX Pro`, no pipe aberto
- Pipe aberto **sem** inner join de conta (1425 `account` null)

Não use `close_value` como KPI do pipe aberto (é null). Não trate `metadata` como fato.

Painéis gráficos (Run All no notebook + página **Paineis** no `.lvdash.json`):

| Seção | Dado real |
| --- | --- |
| Ranking de benchmark | Win rate do agente (só Won/Lost) |
| Galeria de entrada | Pipe aberto sem `close_value` |
| Classificação | `deal_stage` |
| Segmentação | `sector` |
| Segmentação de imagem | Indisponível |
| Estatísticas / matriz / curva / viés | Baseline logístico Won vs Lost, sem `close_value` no X |

Cabeçalho opcional:

```
![Image](https://raw.githubusercontent.com/Databricks-BR/lab_agosto_2025/refs/heads/main/images/head_lab.png)
```
