<img src="https://raw.githubusercontent.com/Databricks-BR/lab_agosto_2025/main/images/head_lab.png">

# Hands-On LAB — Challenge 002 (SupportIQ / suporte)

Pacote Databricks do [challenge 002](../challenges/process-002-support/README.md): ingestão do Dataset 1, Assistant e análise operacional (gargalo, CSAT, horas).

Não use a massa da Receita Federal deste template. Fonte: [Customer Support Ticket Dataset](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) (CC0), arquivo em `dados/`.

Dataset 2 (IT Service Ticket Classification, `Document` + `Topic_group`) **não está** neste disco — o zip do challenge só traz o mesmo CSV. Não inventar essa tabela.

## Estrutura

| Pasta | Papel |
| --- | --- |
| `dados/` | `customer_support_tickets.csv` — 8469 × 17; contrato no README da pasta |
| `01_LAB_importando_dados/` | Ingestão CSV → Delta (`workspace.supportiq.customer_support_tickets`) |
| `02_LAB_Assistant/` | Perguntas ao Assistant só com colunas reais + [Genie](https://dbc-0dea39b3-be1e.cloud.databricks.com/genie/rooms/01f1b6165bac181a9836cde73e8e7556?o=7474644277755368) |
| `03_LAB_Dashboard/` | Entregável Operações — `lab03_dashboard.ipynb` |
| `04_ANALISE_supportiq/` | Kernel Kaggle SupportIQ adaptado para Databricks |
| `images/` | Artefatos opcionais do lab |

## Ementa

| # | Tópico | Duração |
| -- | -- | -- |
| 01 | Contexto de suporte + pedido do Diretor de Operações | 20 min |
| 02 | Databricks + AI/BI | 20 min |
| 03 | Lab 01 — ingestão do CSV (8 469 tickets) | 30 min |
| 04 | Lab 02 — Assistant (gargalo, CSAT, horas TTR−FRT) | 30 min |
| 05 | Lab 03 — Dashboard AI/BI | 40 min |
| 06 | Lab 04 — SupportIQ (kernel adaptado) | 40 min |

## Como rodar no Databricks

1. Importe `notebook-process-002-support` para o Workspace (a pasta `dados/` precisa ir junto).
2. Widgets iguais em todos os labs: `catalog_name=workspace`, `schema_name=supportiq`.
3. **Run All** no Lab 01. Sem isso o Lab 02 e o 04 não acham a tabela.
4. Se o auto-path falhar, `data_path` = `/Workspace/Users/<voce>/notebook-process-002-support/dados`.
5. SQL: colunas com espaço usam backtick — `` `Ticket ID` ``, `` `Time to Resolution` ``.

Armadilhas do dump (CSV ganha o brief): 8469 linhas (não ~30k); `Ticket Type` tem 5 valores; `Time to Resolution` é datetime, não horas; CSAT/TTR só em Closed. Ver [SPEC-002](../.ai/specs/SPEC-002-support.md).

`Customer Name` / `Customer Email` são PII — não commitar dumps identificáveis.

## Referências

- [CSV no Databricks](https://docs.databricks.com/aws/en/query/formats/csv)
- [Delta](https://docs.databricks.com/aws/en/delta/tutorial)
- [Assistant](https://docs.databricks.com/aws/en/notebooks/databricks-assistant-faq)
- [AI/BI Dashboards](https://docs.databricks.com/aws/en/ai-bi/)
- Kernel de partida: [SupportIQ – Customer Support Intelligence Platform](https://www.kaggle.com/code/hanumathureddygari/supportiq-customer-support-intelligence-platform)

## Comunidade Databricks Brasil

<a href="https://github.com/Databricks-BR"><img src="https://raw.githubusercontent.com/Databricks-BR/Databricks-BR/main/images/databricks-br.png" style="width: 40px; height: 40px;"></a>
