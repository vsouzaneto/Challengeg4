# Auditoria SQL — Desafio 003 (DuckDB sobre os CSVs originais)

### Q01 Contagem por estágio
```sql
SELECT deal_stage, count(*) n FROM raw GROUP BY 1 ORDER BY 2 DESC
```
| deal_stage   |    n |
|:-------------|-----:|
| Won          | 4238 |
| Lost         | 2473 |
| Engaging     | 1589 |
| Prospecting  |  500 |


### Q02 Abertos sem conta
```sql
SELECT count(*) FILTER (WHERE account IS NULL) sem_conta, count(*) abertos, round(100.0*count(*) FILTER (WHERE account IS NULL)/count(*),1) pct FROM raw WHERE deal_stage IN ('Prospecting','Engaging')
```
|   sem_conta |   abertos |   pct |
|------------:|----------:|------:|
|        1425 |      2089 |  68.2 |


### Q03 Produtos fora do catálogo
```sql
SELECT product, count(*) n FROM raw WHERE product NOT IN (SELECT product FROM products) GROUP BY 1
```
| product   |    n |
|:----------|-----:|
| GTXPro    | 1480 |


### Q04 Vendedores sem deals
```sql
SELECT sales_agent FROM teams WHERE sales_agent NOT IN (SELECT DISTINCT sales_agent FROM raw)
```
| sales_agent        |
|:-------------------|
| Mei-Mei Johns      |
| Elizabeth Anderson |
| Natalya Ivanova    |
| Carol Thompson     |
| Carl Lin           |


### Q05 Datas, IDs e consistência
```sql
SELECT min(engage_date) eng_min, max(engage_date) eng_max, min(close_date) close_min, max(close_date) close_max,
 count(*) FILTER (WHERE close_date < engage_date) fecha_antes, count(*) - count(DISTINCT opportunity_id) ids_dup,
 count(*) FILTER (WHERE deal_stage='Prospecting' AND engage_date IS NOT NULL) prosp_com_data,
 count(*) FILTER (WHERE deal_stage IN ('Won','Lost') AND close_date IS NULL) fechado_sem_data,
 count(*) FILTER (WHERE deal_stage='Lost' AND close_value<>0) lost_valor_nao_zero FROM raw
```
| eng_min             | eng_max             | close_min           | close_max           |   fecha_antes |   ids_dup |   prosp_com_data |   fechado_sem_data |   lost_valor_nao_zero |
|:--------------------|:--------------------|:--------------------|:--------------------|--------------:|----------:|-----------------:|-------------------:|----------------------:|
| 2016-10-20 00:00:00 | 2017-12-27 00:00:00 | 2017-03-01 00:00:00 | 2017-12-31 00:00:00 |             0 |         0 |                0 |                  0 |                     0 |


### Q06 Taxa de vitória entre fechados (com IC de Wilson)
```sql
WITH c AS (SELECT count(*) n, count(*) FILTER (WHERE deal_stage='Won') w FROM raw WHERE deal_stage IN ('Won','Lost'))
SELECT n, w, round(w/n,4) taxa,
 round(((w/n + 1.96^2/(2*n)) - 1.96*sqrt((w/n)*(1-w/n)/n + 1.96^2/(4*n*n)))/(1+1.96^2/n),4) ic_inf,
 round(((w/n + 1.96^2/(2*n)) + 1.96*sqrt((w/n)*(1-w/n)/n + 1.96^2/(4*n*n)))/(1+1.96^2/n),4) ic_sup FROM c
```
|    n |    w |   taxa |   ic_inf |   ic_sup |
|-----:|-----:|-------:|---------:|---------:|
| 6711 | 4238 | 0.6315 |   0.6199 |    0.643 |


### Q07 Taxa de vitória por dimensão (qui-quadrado, só fechados)
| dimensao    |   grupos |   taxa_min |   taxa_max |   chi2 |   gl |      p |
|:------------|---------:|-----------:|-----------:|-------:|-----:|-------:|
| sales_agent |       30 |      0.55  |      0.704 |  33.35 |   29 | 0.2639 |
| manager     |        6 |      0.621 |      0.644 |   2.44 |    5 | 0.7861 |
| region      |        3 |      0.626 |      0.639 |   1.01 |    2 | 0.6042 |
| prod        |        7 |      0.6   |      0.648 |   6.48 |    6 | 0.3719 |
| sector      |       10 |      0.612 |      0.648 |   2.83 |    9 | 0.9706 |
| account     |       85 |      0.531 |      0.75  |  64.55 |   84 | 0.9432 |

### Q08 Percentis do ciclo (só fechados)
```sql
SELECT deal_stage, count(*) n, quantile_cont(cycle,0.25) p25, quantile_cont(cycle,0.5) p50, quantile_cont(cycle,0.75) p75, quantile_cont(cycle,0.9) p90, max(cycle) mx
FROM p WHERE deal_stage IN ('Won','Lost') GROUP BY ROLLUP(deal_stage) ORDER BY 1
```
| deal_stage   |    n |   p25 |   p50 |   p75 |   p90 |   mx |
|:-------------|-----:|------:|------:|------:|------:|-----:|
| Lost         | 2473 |     7 |    14 |    79 |   100 |  138 |
| Won          | 4238 |     9 |    57 |    88 |   106 |  138 |
| nan          | 6711 |     8 |    45 |    85 |   104 |  138 |


### Q09 Três formas de medir 'chance pela idade' (X dias)
```sql
WITH x AS (SELECT unnest([0,14,30,60,90,104,120,130,138]) X),
e AS (SELECT *, coalesce(cycle, age_end) t, engage_date <= DATE '2017-08-15' coorte FROM p WHERE deal_stage <> 'Prospecting')
SELECT X,
 round(avg(CASE WHEN deal_stage='Won' THEN 1.0 ELSE 0 END) FILTER (WHERE deal_stage IN ('Won','Lost') AND t > X),3) so_fechados_ERRADO,
 count(*) FILTER (WHERE t > X) em_risco_todos,
 round(avg(CASE WHEN deal_stage='Won' THEN 1.0 ELSE 0 END) FILTER (WHERE t > X),3) ganho_entre_todos,
 count(*) FILTER (WHERE t > X AND coorte) em_risco_coorte,
 round(avg(CASE WHEN deal_stage='Won' THEN 1.0 ELSE 0 END) FILTER (WHERE t > X AND coorte),3) ganho_coorte,
 round(avg(CASE WHEN deal_stage='Lost' THEN 1.0 ELSE 0 END) FILTER (WHERE t > X AND coorte),3) perda_coorte,
 round(avg(CASE WHEN deal_stage='Engaging' THEN 1.0 ELSE 0 END) FILTER (WHERE t > X AND coorte),3) nunca_fechou_coorte
FROM x, e GROUP BY X ORDER BY X
```
|   X |   so_fechados_ERRADO |   em_risco_todos |   ganho_entre_todos |   em_risco_coorte |   ganho_coorte |   perda_coorte |   nunca_fechou_coorte |
|----:|---------------------:|-----------------:|--------------------:|------------------:|---------------:|---------------:|----------------------:|
|   0 |                0.632 |             8300 |               0.511 |              5991 |          0.498 |          0.285 |                 0.217 |
|  14 |                0.687 |             5487 |               0.489 |              4222 |          0.477 |          0.215 |                 0.308 |
|  30 |                0.682 |             5119 |               0.473 |              4021 |          0.464 |          0.213 |                 0.324 |
|  60 |                0.686 |             4511 |               0.453 |              3621 |          0.44  |          0.2   |                 0.359 |
|  90 |                0.711 |             2837 |               0.341 |              2465 |          0.329 |          0.143 |                 0.528 |
| 104 |                0.704 |             2082 |               0.218 |              1881 |          0.212 |          0.096 |                 0.692 |
| 120 |                0.756 |             1569 |               0.093 |              1480 |          0.091 |          0.03  |                 0.879 |
| 130 |                0.774 |             1382 |               0.03  |              1352 |          0.029 |          0.009 |                 0.962 |
| 138 |              nan     |             1291 |               0     |              1291 |          0     |          0     |                 1     |
coorte = início até 15/08/2017 (todos tiveram ≥138 dias para fechar até 31/12/2017).

### Q10 Idade dos Engaging abertos em 31/12/2017
```sql
SELECT count(*) engaging, count(*) FILTER (WHERE age_end <= 104) ate_104, count(*) FILTER (WHERE age_end BETWEEN 105 AND 138) d105_138,
 count(*) FILTER (WHERE age_end > 138) acima_138, round(100.0*count(*) FILTER (WHERE age_end > 138)/count(*),1) pct_acima_138, min(age_end) idade_min, max(age_end) idade_max FROM p WHERE deal_stage='Engaging'
```
|   engaging |   ate_104 |   d105_138 |   acima_138 |   pct_acima_138 |   idade_min |   idade_max |
|-----------:|----------:|-----------:|------------:|----------------:|------------:|------------:|
|       1589 |       152 |        146 |        1291 |            81.2 |           9 |         423 |


### Q11 Desfecho da coorte com janela completa
```sql
SELECT count(*) n, round(avg((deal_stage='Won')::INT),3) ganhou, round(avg((deal_stage='Lost')::INT),3) perdeu, round(avg((deal_stage='Engaging')::INT),3) nunca_fechou
FROM p WHERE deal_stage <> 'Prospecting' AND engage_date <= DATE '2017-08-15'
```
|    n |   ganhou |   perdeu |   nunca_fechou |
|-----:|---------:|---------:|---------------:|
| 5991 |    0.498 |    0.285 |          0.217 |


### Q12 '% nunca fechou' por sales_agent (coorte)
grupos=30, min=0.000, max=0.310, chi2=208.0, gl=29, p=5.71e-29

### Q12 '% nunca fechou' por manager (coorte)
grupos=6, min=0.166, max=0.279, chi2=64.8, gl=5, p=1.23e-12

### Q12 '% nunca fechou' por region (coorte)
grupos=3, min=0.183, max=0.265, chi2=47.2, gl=2, p=5.72e-11

### Q12 '% nunca fechou' por prod (coorte)
grupos=7, min=0.199, max=0.438, chi2=11.9, gl=6, p=6.34e-02

### Q12b '% nunca fechou' por vendedor (coorte), extremos
```sql
SELECT sales_agent, manager, count(*) n, round(avg((deal_stage='Engaging')::INT),3) nunca_fechou, round(avg((deal_stage='Won')::INT),3) ganhou
FROM p WHERE deal_stage<>'Prospecting' AND engage_date <= DATE '2017-08-15' GROUP BY 1,2 ORDER BY nunca_fechou LIMIT 6
```
| sales_agent        | manager          |   n |   nunca_fechou |   ganhou |
|:-------------------|:-----------------|----:|---------------:|---------:|
| Donn Cantrell      | Rocco Neubert    | 195 |          0     |    0.61  |
| Reed Clapper       | Rocco Neubert    | 174 |          0     |    0.667 |
| Garret Kinder      | Cara Losch       |  89 |          0     |    0.652 |
| Cecily Lampkin     | Dustin Brinkmann | 128 |          0.148 |    0.578 |
| Jonathan Berthelot | Melvin Marxen    | 214 |          0.154 |    0.575 |
| Darcel Schlecht    | Melvin Marxen    | 473 |          0.175 |    0.529 |


### Q13 Prospecting por gerente
```sql
SELECT manager, region, count(*) n FROM p WHERE deal_stage='Prospecting' GROUP BY 1,2 ORDER BY 3 DESC
```
| manager          | region   |   n |
|:-----------------|:---------|----:|
| Melvin Marxen    | Central  | 296 |
| Dustin Brinkmann | Central  | 204 |


### Q14 Valor fechado (ganhos) x preço de tabela
```sql
SELECT prod, any_value(price) preco, count(*) ganhos, median(close_value) mediana, round(100*(median(close_value)-any_value(price))/any_value(price),2) dif_pct,
 min(close_value) minimo, max(close_value) maximo FROM p WHERE deal_stage='Won' GROUP BY 1 ORDER BY preco DESC
```
| prod           |   preco |   ganhos |   mediana |   dif_pct |   minimo |   maximo |
|:---------------|--------:|---------:|----------:|----------:|---------:|---------:|
| GTK 500        |   26768 |       15 |   25897   |     -3.25 |    23746 |    30288 |
| GTX Plus Pro   |    5482 |      479 |    5503   |      0.38 |     3704 |     7356 |
| GTX Pro        |    4821 |      729 |    4828   |      0.15 |     3169 |     6166 |
| MG Advanced    |    3393 |      654 |    3382.5 |     -0.31 |     2477 |     4456 |
| GTX Plus Basic |    1096 |      653 |    1083   |     -1.19 |      752 |     1374 |
| GTX Basic      |     550 |      915 |     547   |     -0.55 |      365 |      716 |
| MG Special     |      55 |      793 |      55   |      0    |       38 |       72 |


### Q15 Maior ciclo por mês de início (fechados)
```sql
SELECT strftime(engage_date,'%Y-%m') mes, count(*) fechados, max(cycle) maior_ciclo FROM p WHERE deal_stage IN ('Won','Lost') GROUP BY 1 ORDER BY 1
```
| mes     |   fechados |   maior_ciclo |
|:--------|-----------:|--------------:|
| 2016-10 |          7 |           137 |
| 2016-11 |        102 |           138 |
| 2016-12 |        196 |           119 |
| 2017-01 |        247 |           137 |
| 2017-02 |        420 |           137 |
| 2017-03 |        655 |           121 |
| 2017-04 |        753 |           132 |
| 2017-05 |        588 |           136 |
| 2017-06 |        681 |           124 |
| 2017-07 |        796 |           138 |
| 2017-08 |        539 |           137 |
| 2017-09 |        677 |           118 |
| 2017-10 |        703 |            90 |
| 2017-11 |        244 |            58 |
| 2017-12 |        103 |            24 |


### Q16 Taxa de vitória por mês de FECHAMENTO
```sql
SELECT strftime(close_date,'%Y-%m') mes, count(*) fechados, count(*) FILTER (WHERE deal_stage='Won') ganhos, round(avg((deal_stage='Won')::INT),3) taxa
FROM p WHERE deal_stage IN ('Won','Lost') GROUP BY 1 ORDER BY 1
```
| mes     |   fechados |   ganhos |   taxa |
|:--------|-----------:|---------:|-------:|
| 2017-03 |        647 |      531 |  0.821 |
| 2017-04 |        586 |      285 |  0.486 |
| 2017-05 |        805 |      438 |  0.544 |
| 2017-06 |        641 |      531 |  0.828 |
| 2017-07 |        627 |      308 |  0.491 |
| 2017-08 |        785 |      446 |  0.568 |
| 2017-09 |        635 |      503 |  0.792 |
| 2017-10 |        566 |      279 |  0.493 |
| 2017-11 |        768 |      406 |  0.529 |
| 2017-12 |        651 |      511 |  0.785 |


### Q17 Fim de trimestre x demais meses
```sql
SELECT month(close_date) IN (3,6,9,12) fim_trimestre, count(*) fechados, round(avg((deal_stage='Won')::INT),3) taxa,
 round(avg(cycle),1) ciclo_medio FROM p WHERE deal_stage IN ('Won','Lost') GROUP BY 1
```
| fim_trimestre   |   fechados |   taxa |   ciclo_medio |
|:----------------|-----------:|-------:|--------------:|
| True            |       2574 |  0.807 |          65.9 |
| False           |       4137 |  0.523 |          36.9 |


### Q18 Perdas nas 2 primeiras semanas
```sql
SELECT count(*) FILTER (WHERE deal_stage='Lost' AND cycle<=14) perdas_ate14, count(*) FILTER (WHERE deal_stage='Lost') perdas,
 count(*) FILTER (WHERE cycle<=14) fechados_ate14, round(avg((deal_stage='Lost')::INT) FILTER (WHERE cycle<=14),3) pct_perdidos_entre_ate14 FROM p WHERE deal_stage IN ('Won','Lost')
```
|   perdas_ate14 |   perdas |   fechados_ate14 |   pct_perdidos_entre_ate14 |
|---------------:|---------:|-----------------:|---------------------------:|
|           1249 |     2473 |             2806 |                      0.445 |


### Q19 Deals abertos por vendedor
```sql
WITH a AS (SELECT sales_agent, count(*) n FROM raw WHERE deal_stage IN ('Prospecting','Engaging') GROUP BY 1)
SELECT count(*) vendedores_com_abertos, round(avg(n),1) media, median(n) mediana, min(n) minimo, max(n) maximo FROM a
```
|   vendedores_com_abertos |   media |   mediana |   minimo |   maximo |
|-------------------------:|--------:|----------:|---------:|---------:|
|                       27 |    77.4 |        79 |       31 |      194 |


### Q20 Vendedores sem nenhum Engaging com até 138 dias
```sql
WITH a AS (SELECT sales_agent, count(*) FILTER (WHERE deal_stage='Engaging' AND age_end<=138) vivos, count(*) abertos FROM p WHERE deal_stage IN ('Prospecting','Engaging') GROUP BY 1)
SELECT count(*) vendedores, count(*) FILTER (WHERE vivos=0) sem_deal_vivo, list(sales_agent ORDER BY sales_agent) FILTER (WHERE vivos=0) quem FROM a
```
|   vendedores |   sem_deal_vivo | quem                                                     |
|-------------:|----------------:|:---------------------------------------------------------|
|           27 |               6 | ['Cecily Lampkin' 'Darcel Schlecht' 'Gladys Colclough'   |
|              |                 |  'Jonathan Berthelot' 'Marty Freudenburg' 'Moses Frase'] |


### Q21 Abertos por mês de início (Engaging)
```sql
SELECT strftime(engage_date,'%Y-%m') mes, count(*) engaging_abertos FROM p WHERE deal_stage='Engaging' GROUP BY 1 ORDER BY 1
```
| mes     |   engaging_abertos |
|:--------|-------------------:|
| 2016-11 |                 13 |
| 2016-12 |                 40 |
| 2017-01 |                 65 |
| 2017-02 |                 95 |
| 2017-03 |                137 |
| 2017-04 |                121 |
| 2017-05 |                134 |
| 2017-06 |                111 |
| 2017-07 |                402 |
| 2017-08 |                254 |
| 2017-09 |                102 |
| 2017-10 |                 58 |
| 2017-11 |                 39 |
| 2017-12 |                 18 |

