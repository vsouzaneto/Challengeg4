# Auditoria dos números do material de partida (TypeScript)

Gerado por `npm run auditoria` a partir de `solution/data/`. Data de referência: 31/12/2017. Faixas: 0, 30, 60, 90, 104, 120.

| ID | Afirmação | Declarado | Recalculado | Status |
|---|---|---|---|---|
| N01 | vendedores; oportunidades | 35; ~8.800 | 35; 8.800 | confere |
| N02 | close_value = 0 nos perdidos; vazio nos abertos | 2.473 de 2.473; vazio | 2.473 de 2.473; vazio em 2.089 de 2.089 | confere |
| N03 | negócios; empresas; produtos; vendedores | 8.800; 85; 7; 35 | 8.800; 85; 7; 35 | confere |
| N04 | Won · Lost · Engaging · Prospecting | 4.238 · 2.473 · 1.589 · 500 | 4.238 · 2.473 · 1.589 · 500 | confere |
| N05 | linhas com "GTXPro" | 1.480 | 1.480 | confere |
| N06 | Prospecting com alguma data | 0 | 0 | confere |
| N07 | em andamento sem empresa; concluídos sem empresa | 1.425 de 2.089; 0 | 1.425 de 2.089; 0 | confere |
| N08 | primeira data; última; 1º concluído; maior ciclo | 20/10/2016; 31/12/2017; 01/03/2017; 138 | 20/10/2016; 31/12/2017; 01/03/2017; 138 (ganhos 138, perdidos 138) | confere |
| N09 | vendedores sem nenhum negócio | 5: Carl Lin, Carol Thompson, Elizabeth Anderson, Mei-Mei Johns, Natalya Ivanova | 5: Carl Lin, Carol Thompson, Elizabeth Anderson, Mei-Mei Johns, Natalya Ivanova | confere |
| N10 | sem negócio recente em 31/12 (dos com histórico): só parados/prospecção; nada aberto | 9 de 30: 6; 3 | 9 de 30: 6; 3 | confere |
| N12 | chance por faixa 0·30·60·90·104·120 | 49,8 · 46,4 · 44,0 · 32,9 · 21,2 · 9,1 | 49,8 · 46,4 · 44,0 · 32,9 · 21,2 · 9,1 | confere |
| N12 | coorte: negócios; último início | 5.991; 15/08/2017 | 5.991; 15/08/2017 | confere |
| N13 | só concluídos: aos 14 e aos 90 dias | 68,7% · 71,1% | 68,7% · 71,1% | confere |
| N14 | no prazo · esfriando · parados (dos Engaging) | 110 · 188 · 1.291 | 110 · 188 · 1.291 | confere |
| N15 | preço de lista dos Engaging; % parado (do valor); prospecção | US$ 3,89 mi; 82%; US$ 1,07 mi | US$ 3,89 mi; 82%; US$ 1,07 mi | confere |
| N16 | valor ponderado (no prazo + esfriando) | ≈ US$ 195 mil | US$ 195.380 | confere |
| N20 | US$ no prazo · esfriando · parado · prospecção | 227.651 · 465.914 · 3.198.664 · 1.073.986 | 227.651 · 465.914 · 3.198.664 · 1.073.986 | confere |
| N20 | "82% dos negócios com data" (P5): % dos negócios × % do valor | 82% dos negócios | 81,2% dos negócios; 82,2% do valor | **diverge** |
| N21 | nenhum concluído depois de 138 dias | 0 | 0 | confere |
| N24 | taxa de ganho entre concluídos; IC 95% | 63,15%; 62,0–64,3% | 63,15%; Wilson 62,0–64,3% (normal 62,0–64,3%) | confere |
| N25 | de cada 100 iniciados: ganhos · perdidos · nunca concluídos | 50 · 29 · 22 | 49,8 · 28,5 · 21,7 (coorte de 5.991) | confere |
| N26 | p do qui-quadrado: vendedor | 0,264 | 0,264 (χ² = 33,35, 29 g.l.) | confere |
| N26 | p do qui-quadrado: gestor | 0,786 | 0,786 (χ² = 2,44, 5 g.l.) | confere |
| N26 | p do qui-quadrado: regional | 0,604 | 0,604 (χ² = 1,01, 2 g.l.) | confere |
| N26 | p do qui-quadrado: produto | 0,372 | 0,372 (χ² = 6,48, 6 g.l.) | confere |
| N26 | p do qui-quadrado: setor | 0,971 | 0,971 (χ² = 2,83, 9 g.l.) | confere |
| N26 | p do qui-quadrado: empresa | 0,943 | 0,943 (χ² = 64,55, 84 g.l.) | confere |
| N27 | melhor − pior vendedor; % dos sorteios ≥ | 15,4 p.p.; 36–38% | 15,4 p.p.; 38,1% (10.000 sorteios, semente 20171231) | confere |
| N28 | em valor: diferença; % dos sorteios ≥ | 23,5 p.p.; ~41% | 23,5 p.p.; 42,3% | confere |
| N29 | receita: maior ÷ menor; Spearman com volume; com taxa | 9,3×; 0,62; −0,21 | 9,3×; 0,62; -0,21 | confere |
| N30 | taxa por mês do trimestre: 1º · 2º · 3º | 49,0 · 54,7 · 80,7 | 49,0 · 54,7 · 80,7 | confere |
| N17 | backtest: valor ponderado | 44,41% | 44,41% | confere |
| N17 | backtest: situação e preço ("faixas e preço") | 43,35% | 43,16% | **diverge** |
| N17 | backtest: preço sem parados | 40,10% | 40,10% | confere |
| N17 | backtest: só preço | 36,17% | 36,17% | confere |
| N17 | backtest: chance só com concluídos | 32,23% | 32,23% | confere |
| N17 | backtest: aleatório | 15,40% | 15,40% | confere |
| N39 | métodos no backtest | 6 | 6 | confere |
| N18 | ML 45,0% × valor ponderado 44,6% (exploratório) | 45,0 · 44,6 | ML 45,03% = 45,03% = 45,03% = 45,03% = 45,03% (5 sementes) · valor ponderado por dia exato 44,65%; mesmo universo do backtest: sim | confere |
| N40 | "21 consultas" em auditoria_sql.py | 21 | 21 (Q01–Q21, mais a Q12b) | confere |

Conferem: 38. Divergem: 2. Pendentes: 0.

## Hipóteses

### H1, H2, H11 e sensibilidade: o backtest muda com as escolhas?

| Variante | valor ponderado | situação e preço ("faixas e preço") | preço sem parados | só preço | chance só com concluídos | aleatório |
|---|---|---|---|---|---|---|
| reconciliado (faixas do AGENTS, corte 138, em risco com >) | 44,41% | 43,16% | 40,10% | 36,17% | 32,23% | 15,40% |
| H1: faixas de 30 em 30 dias | 44,14% | 43,16% | 40,10% | 36,17% | 32,23% | 15,40% |
| H1: chance por dia exato | 44,65% | 43,16% | 40,10% | 36,17% | 32,23% | 15,40% |
| H2: corte = maior ciclo observado em T | 44,41% | 43,16% | 40,10% | 36,17% | 32,23% | 15,40% |
| pré-registrado no C1: em risco com ≥ | 44,25% | 43,16% | 40,10% | 36,17% | 32,23% | 15,40% |
| situação com a fronteira da preparação (esfriando a partir de 91) | 44,41% | 43,35% | 40,10% | 36,17% | 32,23% | 15,40% |
| H11: só as fotos de 31/08 e 30/09 | 42,97% | 40,99% | 36,70% | 31,59% | 24,74% | 14,17% |
| H11: curva só com iniciados a partir de 01/03/2017 | 36,02% | 43,16% | 40,10% | 36,17% | 32,23% | 15,40% |

H2: maior ciclo observado em cada foto: 30/06/2017 = 138; 31/07/2017 = 138; 31/08/2017 = 138; 30/09/2017 = 138; em 31/12/2017 = 138.
H11: maior ciclo entre os iniciados a partir de 01/03/2017 = 138 (5.739 concluídos).
H11: iniciados em 2016 = 358; em jan–fev/2017 = 827.
H11: curva em 31/12 só com iniciados a partir de 01/03/2017: 0: 47,3% (4.806) · 30: 41,7% (2.899) · 60: 38,6% (2.565) · 90: 25,6% (1.740) · 104: 13,5% (1.378) · 120: 4,3% (1.163).
Curva reconciliada (>) em 31/12, com n em risco: 0: 49,8% (5.991) · 30: 46,4% (4.021) · 60: 44,0% (3.621) · 90: 32,9% (2.465) · 104: 21,2% (1.881) · 120: 9,1% (1.480).
Pré-registrado no C1 (≥): 0: 49,8% · 30: 46,4% · 60: 44,2% · 90: 33,6% · 104: 22,1% · 120: 9,9%.
Pré-registrado no C1 (≥) nos números que divergiam: N13 só concluídos aos 14 e 90 dias = 68,64% · 71,26%; N16 valor ponderado = US$ 199.308.
H11: coorte de cada foto com a curva só de iniciados a partir de 01/03/2017: 30/06/2017 = 0; 31/07/2017 = 379; 31/08/2017 = 1.258; 30/09/2017 = 2.022 (coorte vazia = chance 0 para todos = ordem pelo ID).
| H11: curva limpa (iniciados a partir de 01/03/2017), só 31/08 e 30/09 | 43,10% | 40,99% | 36,70% | 31,59% | 24,74% | 14,17% |

Calibração: chance prevista pela curva em T para os abertos com até 138 dias × fração ganha até 31/12/2017

| Foto | Curva | Coorte | Abertos | Prevista | Realizada | Por faixa (prevista → realizada, n) |
|---|---|---|---|---|---|---|
| 31/07/2017 | cheia | 1.564 | 1.982 | 55,2% | 37,4% | 0: 60% → 28% (702) · 30: 57% → 54% (519) · 60: 56% → 46% (474) · 90: 50% → 32% (116) · 104: 39% → 11% (85) · 120: 22% → 1% (86) |
| 31/07/2017 | limpa (desde 01/03/2017) | 379 | 1.982 | 51,3% | 37,4% | 0: 60% → 28% (702) · 30: 53% → 54% (519) · 60: 52% → 46% (474) · 90: 46% → 32% (116) · 104: 22% → 11% (85) · 120: 2% → 1% (86) |
| 31/08/2017 | cheia | 2.443 | 1.857 | 51,7% | 34,3% | 0: 56% → 43% (625) · 30: 55% → 22% (615) · 60: 54% → 50% (314) · 90: 44% → 44% (118) · 104: 32% → 25% (102) · 120: 17% → 4% (83) |
| 31/08/2017 | limpa (desde 01/03/2017) | 1.258 | 1.857 | 45,3% | 34,3% | 0: 52% → 43% (625) · 30: 51% → 22% (615) · 60: 49% → 50% (314) · 90: 31% → 44% (118) · 104: 11% → 25% (102) · 120: 1% → 4% (83) |

H11: inícios e conclusões por mês

| Mês | Inícios | Ganhos concluídos | Perdidos concluídos |
|---|---|---|---|
| 2016-10 | 7 | 0 | 0 |
| 2016-11 | 115 | 0 | 0 |
| 2016-12 | 236 | 0 | 0 |
| 2017-01 | 312 | 0 | 0 |
| 2017-02 | 515 | 0 | 0 |
| 2017-03 | 792 | 531 | 116 |
| 2017-04 | 874 | 285 | 301 |
| 2017-05 | 722 | 438 | 367 |
| 2017-06 | 792 | 531 | 110 |
| 2017-07 | 1.198 | 308 | 319 |
| 2017-08 | 793 | 446 | 339 |
| 2017-09 | 779 | 503 | 132 |
| 2017-10 | 761 | 279 | 287 |
| 2017-11 | 283 | 406 | 362 |
| 2017-12 | 121 | 511 | 140 |

Curva "só concluídos" nas mesmas faixas: 0: 63,2% · 30: 68,2% · 60: 68,6% · 90: 71,1% · 104: 70,4% · 120: 75,6%.

### H3 e H4: o ganho do valor ponderado é real? A métrica discrimina?

| Comparação (unidade = vendedor, 4 fotos somadas) | Diferença | IC 95% (bootstrap) | p (troca de sinais) |
|---|---|---|---|
| valor ponderado − preço sem parados | 4,31 p.p. | 1,99 a 7,21 p.p. | 0,0006 |
| valor ponderado − situação e preço ("faixas e preço") | 1,25 p.p. | -0,19 a 2,91 p.p. | 0,1253 |
| valor ponderado − só preço | 8,23 p.p. | 4,58 a 12,67 p.p. | 0,0001 |
| valor ponderado − chance só com concluídos | 12,17 p.p. | 6,65 a 18,59 p.p. | 0,0001 |
| ML (semente 0) − valor ponderado por dia exato (mesmo script) | 0,38 p.p. | -3,24 a 3,48 p.p. | 0,8292 |
| ML (semente 0) − valor ponderado por faixas (D5) | 0,62 p.p. | -3,32 a 3,98 p.p. | 0,7402 |

H4 30/06/2017: 30 vendedores; abertos por vendedor de 18 a 118 (mediana 48); com 10 ou menos: 0. Corte: 138.
H4 31/07/2017: 30 vendedores; abertos por vendedor de 22 a 166 (mediana 71); com 10 ou menos: 0. Corte: 138.
H4 31/08/2017: 30 vendedores; abertos por vendedor de 17 a 144 (mediana 69); com 10 ou menos: 0. Corte: 138.
H4 30/09/2017: 30 vendedores; abertos por vendedor de 17 a 153 (mediana 76); com 10 ou menos: 0. Corte: 138.

### H5 e H9: as dimensões no desfecho da coorte, e o tamanho da empresa

| Dimensão | p (concluídos) | p (coorte) | grupos | sem o atributo (concluídos) | maior − menor taxa |
|---|---|---|---|---|---|
| vendedor | 0,264 | 0,000 | 30 | 0 | 15,4 p.p. |
| gestor | 0,786 | 0,002 | 6 | 0 | 2,3 p.p. |
| regional | 0,604 | 0,000 | 3 | 0 | 1,4 p.p. |
| produto | 0,372 | 0,718 | 7 | 0 | 4,8 p.p. |
| setor | 0,971 | 0,490 | 10 | 0 | 3,7 p.p. |
| empresa | 0,943 | 0,643 | 85 | 0 | 21,9 p.p. |
| receita da empresa (quartis) | 0,144 | 0,056 | 4 | 0 | 3,6 p.p. |
| funcionários da empresa (quartis) | 0,103 | 0,035 | 4 | 0 | 4,0 p.p. |

H5: coorte de 31/12 por vendedor (o efeito está no que fica aberto, não na taxa entre concluídos)

| Vendedor | Coorte | Ganho | Aberto | Ganho entre concluídos |
|---|---|---|---|---|
| Donn Cantrell | 195 | 61,0% | 0,0% | 61,0% |
| Garret Kinder | 89 | 65,2% | 0,0% | 65,2% |
| Reed Clapper | 174 | 66,7% | 0,0% | 66,7% |
| Cecily Lampkin | 128 | 57,8% | 14,8% | 67,9% |
| Jonathan Berthelot | 214 | 57,5% | 15,4% | 68,0% |
| Darcel Schlecht | 473 | 52,9% | 17,5% | 64,1% |
| Moses Frase | 181 | 52,5% | 18,8% | 64,6% |
| Gladys Colclough | 190 | 47,9% | 18,9% | 59,1% |
| Niesha Huffines | 158 | 50,6% | 19,0% | 62,5% |
| Versie Hillebrand | 225 | 53,3% | 19,1% | 65,9% |
| Lajuana Vencill | 209 | 44,5% | 19,1% | 55,0% |
| Anna Snelling | 296 | 49,7% | 19,3% | 61,5% |
| Marty Freudenburg | 155 | 52,9% | 21,3% | 67,2% |
| Zane Levy | 239 | 43,9% | 24,3% | 58,0% |
| Cassey Cress | 251 | 46,6% | 25,1% | 62,2% |
| James Ascencio | 189 | 47,6% | 25,4% | 63,8% |
| Vicki Laflamme | 317 | 47,3% | 25,6% | 63,6% |
| Kami Bicknell | 252 | 46,4% | 25,8% | 62,6% |
| Maureen Marcano | 209 | 52,2% | 25,8% | 70,3% |
| Kary Hendrixson | 315 | 45,7% | 26,0% | 61,8% |
| Daniell Hammack | 188 | 46,3% | 27,1% | 63,5% |
| Violet Mclelland | 184 | 46,2% | 27,7% | 63,9% |
| Markita Hansen | 220 | 41,8% | 27,7% | 57,9% |
| Corliss Cosme | 221 | 48,0% | 28,5% | 67,1% |
| Rosie Papadopoulos | 115 | 47,0% | 28,7% | 65,9% |
| Elease Gluck | 134 | 44,0% | 29,1% | 62,1% |
| Hayden Neloms | 147 | 48,3% | 29,9% | 68,9% |
| Rosalina Dieter | 110 | 44,5% | 30,9% | 64,5% |
| Boris Faz | 142 | 44,4% | 31,0% | 64,3% |
| Wilburn Farren | 71 | 49,3% | 31,0% | 71,4% |

H9: negócios em andamento sem empresa (logo, sem receita e funcionários): 1.425 de 2.089 (68,2%). Por etapa: Won 0/4.238; Lost 0/2.473; Engaging 1.088/1.589; Prospecting 337/500.
Mês do trimestre: χ² p = 3.76e-123.

### H6, H7, H8, H10

H6: close_value ÷ preço de lista nos 4.238 ganhos: mínimo 0,66, máximo 1,34, média 0,996; dentro de ±10%: 68,9%.
H7: maior ciclo dos ganhos = 138; dos perdidos = 138. Engaging com data de conclusão: 0.
H8: "de cada 10" por faixa: 0: 49,8% → 5 · 30: 46,4% → 5 · 60: 44,0% → 4 · 90: 32,9% → 3 · 104: 21,2% → 2 · 120: 9,1% → 1.
H10 (31/12): vendedores com "Foque agora" não vazia = 21; tamanho da lista de 1 a 31; dos 10 primeiros por valor ponderado, em média 88,6% também são os 10 mais caros; listas idênticas em 9 vendedores.
Setores grafados no accounts.csv: employment, entertainment, finance, marketing, medical, retail, services, software, technolgy, telecommunications.

## Regra final (G1): a coorte e o corte da base

Data disponível = toda faixa com IC 95% (Wilson) de no máximo ±5 p.p.

| Regra | 30/06/2017 | 31/07/2017 | 31/08/2017 | 30/09/2017 | 31/12/2017 |
|---|---|---|---|---|---|
| entrada tardia: todos, cada um a partir da idade que tinha em 01/03/2017 (regra final) | faixa 0: 0 em risco; faixa vazia | faixa 0: 379 em risco; ±4,91 p.p. ✓ | faixa 0: 1.258 em risco; ±3,40 p.p. ✓ | faixa 0: 2.022 em risco; ±2,95 p.p. ✓ | faixa 0: 4.806 em risco; ±1,87 p.p. ✓ |
| limpa: só iniciados a partir da primeira conclusão observada (sensibilidade) | faixa 0: 0 em risco; faixa vazia | faixa 0: 379 em risco; ±8,57 p.p. | faixa 0: 1.258 em risco; ±5,01 p.p. | faixa 0: 2.022 em risco; ±3,72 p.p. ✓ | faixa 0: 4.806 em risco; ±2,05 p.p. ✓ |
| sem correção (regra da preparação) | faixa 0: 852 em risco; ±5,68 p.p. | faixa 0: 1.564 em risco; ±4,15 p.p. ✓ | faixa 0: 2.443 em risco; ±3,37 p.p. ✓ | faixa 0: 3.207 em risco; ±2,94 p.p. ✓ | faixa 0: 5.991 em risco; ±1,85 p.p. ✓ |

Curva em 31/12/2017 (chance por faixa 0 · 30 · 60 · 90 · 104 · 120):

- entrada tardia: todos, cada um a partir da idade que tinha em 01/03/2017 (regra final): 47,3% · 42,9% · 41,2% · 30,8% · 19,9% · 8,6%; valor ponderado (no prazo + esfriando) US$ 182.928
- limpa: só iniciados a partir da primeira conclusão observada (sensibilidade): 47,3% · 41,7% · 38,6% · 25,6% · 13,5% · 4,3%; valor ponderado (no prazo + esfriando) US$ 154.880
- sem correção (regra da preparação): 49,8% · 46,4% · 44,0% · 32,9% · 21,2% · 9,1%; valor ponderado (no prazo + esfriando) US$ 195.380

Backtest só nas datas disponíveis, e teste pareado (unidade = vendedor). O CA3 pede o ganho sobre "só preço", com IC.

| Regra | Fotos | Valor ponderado | Situação e preço | Só preço | Ponderado − só preço | Ponderado − situação e preço | Ponderado − preço sem parados |
|---|---|---|---|---|---|---|---|
| entrada tardia: todos, cada um a partir da idade que tinha em 01/03/2017 (regra final) | 31/07/2017, 31/08/2017, 30/09/2017 | 40,86% | 40,74% | 33,20% | 7,66 p.p. (IC 3,49 a 12,62; p 0,0004) | 0,12 p.p. (IC -1,51 a 2,11; p 0,9032) | 3,22 p.p. (IC 0,63 a 6,41; p 0,0220) |
| limpa: só iniciados a partir da primeira conclusão observada (sensibilidade) | 30/09/2017 | 47,70% | 42,11% | 29,01% | 18,69 p.p. (IC 12,28 a 25,57; p 0,0000) | 5,58 p.p. (IC 1,82 a 9,50; p 0,0083) | 12,56 p.p. (IC 7,70 a 17,85; p 0,0000) |
| sem correção (regra da preparação) | 30/06/2017, 31/07/2017, 31/08/2017, 30/09/2017 | 44,41% | 43,16% | 36,17% | 8,23 p.p. (IC 4,58 a 12,67; p 0,0001) | 1,25 p.p. (IC -0,19 a 2,91; p 0,1253) | 4,31 p.p. (IC 1,99 a 7,21; p 0,0006) |

Modelo de ML na regra final (31/07/2017, 31/08/2017, 30/09/2017): 43,18% contra 40,86% do valor ponderado; ML − ponderado = 2,32 p.p. (IC -2,46 a 6,39; p 0,3347). Captura na regra final: weighted 40,86% · situationThenPrice 40,74% · priceNoStale 37,64% · price 33,20% · concludedOnly 29,09% · aleatório 14,07%. Por data, ponderado · só preço · aleatório: 31/07/2017 37,77% · 35,56% · 13,92%; 31/08/2017 38,52% · 34,00% · 14,35%; 30/09/2017 47,70% · 29,01% · 13,97%.

Por regional em 31/12/2017 (vendedores; negócios quentes e esfriando; vendedores sem nenhum; prospecção; % frio do valor em andamento com data):

| Regional | Vendedores | Quentes e esfriando | Sem prioridade | Prospecção | Frio |
|---|---|---|---|---|---|
| Central | 11 | 5 | 7 | 500 | 99,2% |
| East | 12 | 107 | 5 | 0 | 75,6% |
| West | 12 | 186 | 2 | 0 | 78,7% |

Calibração: prevista pela curva em T × ganha até 31/12/2017, para os abertos com até 138 dias. "Ainda podiam concluir" são os que, em 31/12, estavam abertos com até 138 dias: o teto supõe que todos virariam venda.

| Foto | Abertos | Realizada | Ainda podiam concluir | Teto | Prevista: limpa | Prevista: entrada tardia | Prevista: sem correção |
|---|---|---|---|---|---|---|---|
| 31/07/2017 | 1.982 | 37,4% | 0 (0,0%) | 37,4% | 51,3% | 52,1% | 55,2% |
| 31/08/2017 | 1.857 | 34,3% | 81 (4,4%) | 38,7% | 45,3% | 47,7% | 51,7% |
| 30/09/2017 | 1.879 | 29,7% | 183 (9,7%) | 39,5% | 45,1% | 46,8% | 50,5% |

