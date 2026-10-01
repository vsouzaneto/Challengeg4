# Dados congelados

Fonte: https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics

A API pública do Kaggle declarou **CC0: Public Domain**, versão 1, na consulta de 30/09/2026. Evidência consultada: https://www.kaggle.com/api/v1/datasets/list?search=crm-sales-predictive-analytics. A licença é registrada como declaração da fonte. Última atualização indicada: 14/04/2024. Trata-se de dataset público de demonstração com empresas fictícias.

Os cinco CSVs estão em `solution/data/raw/`, com bytes originais preservados. `.gitattributes` impede normalização dos CSVs pelo Git. `provenance.json` registra fonte, licença e obtenção. `prepare:data` calcula hashes completos e deriva a versão `kaggle-v1-8bd8fd425edacdf2`.

| Arquivo | Registros | SHA-256 |
| --- | ---: | --- |
| sales_pipeline.csv | 8.800 | 825ce8f6c32d4009548b468df3173d55a46fd73f2531f532c5459371dc52adf2 |
| accounts.csv | 85 | e5242324768a563fc632cddfed49a29acbbf2892b8a3c6453cc9650de9ae0358 |
| products.csv | 7 | 7c1c8cbbdb6d4c286902e1985eeb529a36366d6a43f43cd4a93c4b1da2a6eb84 |
| sales_teams.csv | 35 | aeff1272ebe196f5a27e3fc0578aa27abf48ed9ae461aa344fb95990e5ad8bd1 |
| metadata.csv | 21 | 22b34e498d07e3d7f322afdbf81d70a5dc0a389792944e50ca2af86a3597f0af |

## Integridade observada

| Estágio | Registros |
| --- | ---: |
| Prospecting | 500 |
| Engaging | 1.589 |
| Won | 4.238 |
| Lost | 2.473 |

8.800 IDs únicos, 1.425 contas ausentes e 500 datas de engajamento ausentes. O alias GTXPro → GTX Pro corrigiu 1.480 vínculos; o nome original permanece em `originalProduct`. Zero contas não vazias, produtos ou vendedores desconhecidos. Estes resultados não equivalem a uma auditoria completa de todos os campos.

O parser valida cabeçalhos usados, cardinalidade por linha, aspas escapadas, BOM, datas e números consumidos pelo pipeline. Chaves duplicadas, estágios inválidos e fechamento anterior ao engajamento interrompem a preparação. Vínculos desconhecidos preservam a oportunidade e são reportados; contas ausentes ficam `null`.

`engage_date` é entrada em Engaging, não criação nem último contato. `close_value` é receita realizada e fica somente no contrato de dados históricos. Preço de catálogo é USD por unidade; receita anual da conta, no dicionário original, é milhões de USD. Receita e tamanho da conta não entram no score.

## Regerar

Em `solution/`, executar `npm run prepare:data`. Saídas: `raw-manifest.json`, `quality-report.json`, `historical-statistics.json` e `src/data/opportunities.generated.json`. `npm run evaluate` gera o relatório histórico e o resumo exibido no método. Saídas são ignoradas pelo Git e reconstruídas localmente; os CSVs/proveniência são incluídos no pacote de fonte.
