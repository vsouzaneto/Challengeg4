---
status: passing
canonical: true
area: dados
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-007 Domínios de dado (CSVs observados)

## Comportamento visível

Análise e apps leem os CSVs em `datasets/<serviço>/`. O modelo lógico em `.ai/erd/` reflete o **disco**, não só o brief. Quatro silos; zero join cruzado.

## Contrato

1. Schema canônico = ERD + [erd/SPEC-REVERSE.md](../erd/SPEC-REVERSE.md).
2. Joins só os de [erd/SPEC-DRIVEN.md](../erd/SPEC-DRIVEN.md).
3. Divergência brief × CSV: CSV para o modelo; brief para o deliverable; divergência escrita no ERD.
4. 002 Dataset 2 e coluna `engagement_rate` **não existem** neste dump — não documentar como se existissem.
5. 001: label de churn = `churn_events`, não `accounts.churn_flag`.
6. 003: ETL `GTXPro` → `GTX Pro` antes de join de preço. Conta null em pipe aberto é válida.
7. 004: grain = `id`; creator = `creator_id`; engagement é derivado.

## Verificação

```text
python -c "import pandas as pd; from pathlib import Path; p=Path('datasets')"
```

Casos: n 500/5000/25000/2000/600 (001); 8469 (002); 85/7/35/8800 (003); 52214×27 (004); 0 órfãos nas FKs 001; 1480 `GTXPro`; Dataset 2 ausente.

## Evidência

2026-09-21: inspeção local dos CSVs listados em DATA-SOURCES. `usage_id` 21 dups; churn_flag ≠ eventos; FRT/CSAT alinhados a status no 002.

## Notas

`datasets/` continua gitignored. Este `.ai/` não copia PII. Reamostrar se o Kaggle for baixado de novo.

## Sucesso / falha

- Sucesso: dashboard 003 inner-join produto **depois** do remap; churn 001 segmenta pelos 600 eventos.
- Falha: “30k tickets + 8 classes” sem o CSV #2; “engagement_rate no dataset”; join RavenStack ↔ CRM.

## Migração e compatibilidade

Nomes de arquivo `ravenstack_*.csv`, `customer_support_tickets.csv`, `sales_*.csv` / `accounts.csv` / `products.csv`, `social_media_dataset.csv` são estáveis neste dump. Coluna nova = bump + ERD.
