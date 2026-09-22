# LAB 03 — Dashboard AI/BI

Notebook: `lab03_dashboard.ipynb` — diagnóstico, automação e roteador (SPEC-002 / ENTREGAVEIS).

Publicado: [lab-002-support-ops](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611c9d4161bac29737cf1c07d47/published?o=7474644277755368) (`lab-002-support-ops.lvdash.json`).

Pré-requisito: tabela `customer_support_tickets` do Lab 01.

Sugestão de tiles (colunas reais):

- Volume por `Ticket Status` / `Ticket Channel` / `Ticket Priority` / `Ticket Type`
- Horas de resolução (TTR − FRT) em Closed — média e p95 por canal × prioridade
- CSAT médio (`Customer Satisfaction Rating`) só Closed
- Fila aberta: Critical / High sem `Time to Resolution`
- Contagem de `route` (`HUMAN_NOW`, `HUMAN_REVIEW`, `AI_SUGGEST`, `HUMAN_QUEUE`) em Open / Pending

Não use CSAT de Open/Pending (é nulo). Não invente `Topic_group`.

Painéis gráficos (Run All no notebook + página **Paineis** no `.lvdash.json`):

| Seção | Dado real |
| --- | --- |
| Ranking de benchmark | p95 horas por `Ticket Channel` (Closed, TTR − FRT) |
| Galeria de entrada | Fila Open/Pending sem e-mail |
| Classificação | `Ticket Type` (5 valores) |
| Segmentação | Canal × prioridade × tipo |
| Segmentação de imagem | Indisponível |
| Estatísticas / matriz / curva / viés | Baseline logístico, label = CSAT ≥ 4 |

Cabeçalho opcional:

```
![Image](https://raw.githubusercontent.com/Databricks-BR/lab_agosto_2025/refs/heads/main/images/head_lab.png)
```
