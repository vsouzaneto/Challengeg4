# ERD — 003 Lead Scorer (CRM) — schema observado

Fonte: `datasets/build-003-lead-scorer/*.csv` + `metadata.csv`. Leitura 2026-09-21.

```
                 sales_pipeline (8800)
                    PK opportunity_id
                          │
          account         │         product
          (nullable)      │         (GTXPro quebra)
              ▲           │            ▲
              │ 1425 null │            │ 1480 órfãos
         accounts        │         products
           (85)          │            (7)
                         │
                    sales_agent
                         │ 5 agentes sem deal
                         ▼
                   sales_teams (35)
                   manager (6) · office (3)
```

## accounts — 85 × 7

| Coluna | nunique | Notas |
|--------|---------|-------|
| `account` | 85 PK | nome da empresa — chave natural |
| `sector` | 10 | inclui typo **`technolgy`** (12) |
| `year_established` | 1979–2017 | |
| `revenue` | 85 | **milhões USD** (metadata) · 4.54–11 698 |
| `employees` | 9–34 288 | |
| `office_location` | 15 | US 71; typo **`Philipines`** |
| `subsidiary_of` | 7 + 70 null | Acme, Sonron, Bubba Gump, Inity, Golddex, Massive Dynamic, Warephase — **não** são rows de `accounts` |

## products — 7 × 3

| product | series | sales_price |
|---------|--------|-------------|
| GTX Basic | GTX | 550 |
| GTX Plus Basic | GTX | 1 096 |
| GTX Pro | GTX | 4 821 |
| GTX Plus Pro | GTX | 5 482 |
| MG Special | MG | 55 |
| MG Advanced | MG | 3 393 |
| GTK 500 | GTK | 26 768 |

## sales_teams — 35 × 3

| Coluna | Notas |
|--------|-------|
| `sales_agent` | PK 35 |
| `manager` | 6 managers · 5–6 agentes cada |
| `regional_office` | East 12, West 12, Central 11 |

Sem pipeline: Carl Lin, Carol Thompson, Elizabeth Anderson, Mei-Mei Johns, Natalya Ivanova.

## sales_pipeline — 8 800 × 8

| Coluna | Null | Notas |
|--------|------|-------|
| `opportunity_id` | 0 | PK |
| `sales_agent` | 0 | 30 valores (⊂ teams) |
| `product` | 0 | 7 strings; **`GTXPro` = 1 480** sem match no catálogo |
| `account` | 1 425 | null só Prospecting (337) + Engaging (1 088) |
| `deal_stage` | 0 | Won 4 238 · Lost 2 473 · Engaging 1 589 · Prospecting 500 |
| `engage_date` | 500 | null ⇔ Prospecting; 2016-10-20 … 2017-12-27 |
| `close_date` | 2 089 | null ⇔ aberto; 2017-03-01 … 2017-12-31 |
| `close_value` | 2 089 | Lost **sempre 0**; Won 38–30 288; aberto null |

## metadata.csv

Dicionário canônico do dump (Table, Field, Description). Não é fato. Stage documentado: Prospecting → Engaging → Won \| Lost.

## Regras de scoring (dado, não modelo)

- Pipe aberto = Prospecting + Engaging (2 089). Conta pode ser null — scoring não pode exigir inner join em account.
- Normalizar produto **antes** de usar `sales_price`.
- `close_value` em aberto é null, não zero (zero = Lost).
