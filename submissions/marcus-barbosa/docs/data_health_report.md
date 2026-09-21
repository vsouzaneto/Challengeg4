# Relatório de saúde dos dados

## Arquivos usados (procedência)

| Arquivo | Bytes | Linhas | SHA-256 |
|---|---:|---:|---|
| accounts.csv | 4,670 | 85 | `e5242324768a563fc632cddfed49a29acbbf2892b8a3c6453cc9650de9ae0358` |
| products.csv | 171 | 7 | `7c1c8cbbdb6d4c286902e1985eeb529a36366d6a43f43cd4a93c4b1da2a6eb84` |
| sales_teams.csv | 1,284 | 35 | `aeff1272ebe196f5a27e3fc0578aa27abf48ed9ae461aa344fb95990e5ad8bd1` |
| sales_pipeline.csv | 637,773 | 8,800 | `825ce8f6c32d4009548b468df3173d55a46fd73f2531f532c5459371dc52adf2` |

## Tamanho das tabelas

| Tabela | Linhas | Colunas |
|---|---:|---:|
| accounts | 85 | 7 |
| products | 7 | 3 |
| sales_teams | 35 | 3 |
| sales_pipeline | 8,800 | 8 |

## Estágios do pipeline

| Estágio | Deals | % |
|---|---:|---:|
| Won | 4,238 | 48.2% |
| Lost | 2,473 | 28.1% |
| Engaging | 1,589 | 18.1% |
| Prospecting | 500 | 5.7% |

## Nulos por coluna do pipeline

| Coluna | Nulos | % |
|---|---:|---:|
| opportunity_id | 0 | 0.0% |
| sales_agent | 0 | 0.0% |
| product | 0 | 0.0% |
| account | 1,425 | 16.2% |
| deal_stage | 0 | 0.0% |
| engage_date | 500 | 5.7% |
| close_date | 2,089 | 23.7% |
| close_value | 2,089 | 23.7% |

## Nulos por estágio (o que falta em cada fase)

| deal_stage   |   account |   engage_date |   close_date |   close_value |
|:-------------|----------:|--------------:|-------------:|--------------:|
| Engaging     |      68.5 |             0 |          100 |           100 |
| Lost         |       0   |             0 |            0 |             0 |
| Prospecting  |      67.4 |           100 |          100 |           100 |
| Won          |       0   |             0 |            0 |             0 |

## Integridade das chaves (após normalização de produto)

- Produtos do pipeline sem correspondência no catálogo: 0 linhas {}
- Vendedores do pipeline sem correspondência em sales_teams: 0 linhas {}
- Contas do pipeline sem correspondência em accounts: 0 linhas
- Oportunidades sem conta (campo vazio): 1,425 (16.2%); entre abertas: 1,425 (68.2%)

## Datas

- Data de referência (max close_date dos fechados): **2017-12-31**
- engage_date: 2016-10-20 → 2017-12-27; close_date: 2017-03-01 → 2017-12-31
- Ciclo (close − engage) dos fechados: mediana 45 dias; negativos: 0
- Deals abertos com close_date preenchida: 0; com close_value > 0: 0
- Lost com close_value > 0: 0; Won com close_value ≤ 0 ou vazio: 0

## Idade dos deals em Engaging na data de referência

- Quartis (dias): P25=148, P50=165, P75=263, P90=319
- Engaging mais velhos que a mediana do ciclo dos fechados (45 d): 1,558 de 1,589

## Win rate global e por dimensão (apenas fechados: Won / (Won + Lost))

- Global: 63.2% em 6,711 deals fechados
- product: 7 grupos, win rate de 60.0% a 64.8% (spread 4.8%), menor grupo n=25
- sector: 10 grupos, win rate de 61.2% a 64.8% (spread 3.7%), menor grupo n=286
- regional_office: 3 grupos, win rate de 62.6% a 63.9% (spread 1.4%), menor grupo n=1858
- manager: 6 grupos, win rate de 62.1% a 64.4% (spread 2.3%), menor grupo n=745
- sales_agent: 30 grupos, win rate de 55.0% a 70.4% (spread 15.4%), menor grupo n=79

## Valor

- close_value dos Won: mediana 1,117, P90 5,284, máximo 30,288
- sales_price do catálogo: de 55 a 26,768 (razão 487x)
