---
name: crm-dataset
description: Fatos verificados sobre o dataset CRM Sales (Kaggle, CC0) usado no Lead Scorer — schema das 4 tabelas, contagens, nulos, armadilhas de join, leakage e a data de snapshot. Use sempre que for carregar, limpar, analisar ou pontuar dados do pipeline.
user-invocable: false
---

# Dataset CRM Sales — fatos verificados em 2026-09-22

Fonte: https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics (CC0). Cópia imutável em `solution/data/raw/`, checksums em `SHA256SUMS`. Todos os números abaixo foram produzidos com pandas sobre essa cópia; se o código mostrar algo diferente, o código manda e esta skill deve ser corrigida.

## Tabelas

| Tabela | Linhas | Chave | Colunas |
|---|---|---|---|
| `sales_pipeline.csv` | 8.800 | `opportunity_id` (único, 0 duplicatas) | `sales_agent, product, account, deal_stage, engage_date, close_date, close_value` |
| `accounts.csv` | 85 | `account` | `sector, year_established, revenue (USD mi), employees, office_location, subsidiary_of` |
| `products.csv` | 7 | `product` | `series (GTX/MG/GTK), sales_price` |
| `sales_teams.csv` | 35 | `sales_agent` | `manager (6), regional_office (Central/East/West)` |

Integridade referencial: todos os `sales_agent` e todos os `account` não-nulos do pipeline existem nas tabelas de dimensão.

## Estágios e desfecho

| deal_stage | n | engage_date | close_date | account nulo | close_value |
|---|---|---|---|---|---|
| Won | 4.238 | 100% | 100% | 0% | 38 – 30.288 (mediana 1.117) |
| Lost | 2.473 | 100% | 100% | 0% | **sempre 0** |
| Engaging | 1.589 | 100% | **nulo** | **68,5%** | nulo |
| Prospecting | 500 | **nulo** | nulo | **67,4%** | nulo |

- Alvo do scorer: 2.089 deals abertos (Engaging + Prospecting).
- Win rate global (fechados): 63,2%. Por produto: 60,0–64,8%. Por agente: 55,0–70,4%. Variância modesta.
- Ciclo (close − engage) em dias: Lost mediana 14 (p75 79), Won mediana 57 (p75 88), máximo 138 em ambos. Sobrevivência: P(Won | aberto após d dias) sobe de 63% (d=0) para 71% (d=91) e 76% (d=126); sem dado a partir de 140. **Mas em corte temporal fixo a idade não discrimina entre deals vivos (AUC-ROC 0,50)**: a curva descreve o histórico, não prevê o próximo fechamento. "Mais novo primeiro" só parece forte quando censurados são tratados como Lost (efeito zumbi). Razão mediana `close_value/sales_price` dos Won ≈ 1,0 em todo produto (0,967–1,004): `sales_price` domina o valor esperado.
- 5 dos 35 agentes de `sales_teams` não têm nenhum deal.
- Datas: `engage_date` 2016-10-20 → 2017-12-27; `close_date` 2017-03-01 → 2017-12-31. **SNAPSHOT_DATE = 2017-12-31.**

## O que o backtest temporal mostrou (cortes 2017-06-30 e 2017-09-30)

- **Ninguém prevê fechamento melhor que o aleatório**: regras, taxa-base por produto, idade, preço e regressão logística ficam com AUC-ROC 0,44–0,53, ICs sobrepostos. Spreads de win rate por agente (13,9 pp), produto (4,4) e setor (3,6) não se sustentam fora do tempo.
- **Calendário de fechamento é o padrão mais forte** (fim de trimestre: 81% vs 52%), mas depende de `close_date` → leakage; só como reason code informativo (`QUARTER_END_WINDOW`).
- **Posicionamento honesto da ferramenta**: valor esperado × timing + higiene do pipeline (fila de zumbis com R$ 3,19 mi nominais vs R$ 0,69 mi nos 298 Engaging vivos). Em receita realizada no top 20%, o score faz 1,8× o aleatório e fica abaixo de "ordenar por preço" — custo assumido de não virar lista de preços (Spearman score×preço 0,46–0,54).

## Armadilhas

1. **Leakage:** `close_value` e `close_date` só existem após o desfecho (Lost = 0). Jamais como feature. Valor esperado vem de `products.sales_price` × ajuste por histórico de Won do produto (razão mediana `close_value / sales_price`).
2. **Join de produto:** pipeline usa `GTXPro`; catálogo usa `GTX Pro`. Normalizar antes do join ou 1 produto some.
3. **Setor:** `technolgy` (12 contas) é typo de `technology`.
4. **Conta ausente em 68% dos abertos, 0% dos fechados — artefato temporal, não sinal.** A hipótese "a conta é preenchida ao longo do ciclo" foi **refutada** pelo pipeline: a fração de deals Engaging com conta é ~0,3 para todo mês de engajamento (0,21–0,54, sem tendência); a conta só aparece 100% preenchida em deals já fechados. Consequências: (a) `account_known` **nunca** pode ser feature para prever fechamento (prevê "já fechou"); (b) no backtest, os deals rotulados têm 100% de conta enquanto o lote a pontuar tem 32% → rodar avaliação com e sem features de conta e reportar; PSI vai disparar em `account_*`; (c) features de conta só entram quando disponíveis, com `confidence` reduzida quando ausentes; a UI orienta a completar o CRM. Nunca descartar deals sem conta.
4b. **Lote zumbi:** no snapshot, `days_in_engaging` tem mínimo 9, mediana 165 e máximo 423; **1.291 de 1.589 Engaging (81%) ultrapassam 138 dias**, o maior ciclo já observado. A curva de sobrevivência não tem dado para d ≥ 140. Picos de `engage_month` em 2017-07 (402) e 2017-08 (254) sugerem um lote nunca atualizado no CRM. Não podem ser todos "agir agora": tratar como fila de decisão/limpeza com valor nominal em risco quantificado — é achado de negócio (higiene do CRM), não só regra de score.
5. **Prospecting não tem data alguma:** não dá para medir idade. Score usa produto, agente, conta (se houver) e histórico; urgência é desconhecida, não zero.
6. **`revenue` está em milhões de USD**; `employees` de 9 a 34.288; 15 contas são subsidiárias (`subsidiary_of` preenchido).
7. **`sales_price` vai de 55 (MG Special) a 26.768 (GTK 500)**: ordenar por preço concentra tudo em GTK 500. Baseline a ser batido, não imitado.

## Produtos

| product | series | sales_price |
|---|---|---|
| MG Special | MG | 55 |
| GTX Basic | GTX | 550 |
| GTX Plus Basic | GTX | 1.096 |
| MG Advanced | MG | 3.393 |
| GTX Pro | GTX | 4.821 |
| GTX Plus Pro | GTX | 5.482 |
| GTK 500 | GTK | 26.768 |

## Times

Central: Dustin Brinkmann (5), Melvin Marxen (6) · East: Cara Losch (6), Rocco Neubert (6) · West: Celia Rouche (6), Summer Sewald (6).
