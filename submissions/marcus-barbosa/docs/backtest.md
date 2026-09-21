# Backtest walk-forward por snapshot

Em cada data, a chance é calibrada só com snapshots cujo horizonte de 90 dias terminou antes da data; o pipeline em Engaging aberto naquele dia é pontuado e observam-se os 90 dias seguintes. Datas principais, sem sobreposição de desfechos: 2017-06-30, 2017-09-30. Datas de estabilidade: 2017-07-31, 2017-08-31. Nas quatro datas juntas, 2402 ganhos contados correspondem a 1403 deals únicos; 779 aparecem em duas ou mais datas. A fatia Prospecting não é reconstruível em datas passadas e fica fora.

| Data | Tipo | Snapshots de calibração | Deals / observações | Faixas agrupadas | Sem suporte | Engaging em t | Com score | Ganhos em 90 d | Valor ganho |
|---|---|---|---|---|---|---:|---:|---:|---:|
| 2017-06-30 | principal | 2017-03-31 | 684 / 684 | 91-120→91-120+121-138, 121-138→121-138 | 91-120, 121-138 | 1,686 | 1,336 | 597 | 1,421,254 |
| 2017-07-31 | estabilidade | 2017-03-31, 2017-04-30 | 1,096 / 1,656 | 91-120→91-120+121-138, 121-138→121-138 | 91-120, 121-138 | 2,257 | 1,703 | 711 | 1,719,442 |
| 2017-08-31 | estabilidade | 2017-03-31, 2017-04-30, 2017-05-31 | 1,663 / 2,851 | 91-120→91-120+121-138, 121-138→121-138 | 91-120, 121-138 | 2,265 | 1,566 | 553 | 1,298,386 |
| 2017-09-30 | principal | 2017-03-31, 2017-04-30, 2017-05-31, 2017-06-30 | 2,334 / 4,324 | 121-138→121-138 | 121-138 | 2,409 | 1,802 | 541 | 1,219,993 |

## Win rate em 90 dias por faixa de score

| Data | Com score | 0-20 | 21-40 | 41-60 | 61-80 | 81-100 |
|---|---:|---|---|---|---|---|
| 2017-06-30 | 1336 | 48% (n=238) | 44% (n=280) | 49% (n=278) | 42% (n=269) | 41% (n=271) |
| 2017-07-31 | 1703 | 37% (n=305) | 39% (n=356) | 35% (n=387) | 37% (n=316) | 48% (n=339) |
| 2017-08-31 | 1566 | 29% (n=315) | 31% (n=331) | 27% (n=299) | 36% (n=295) | 31% (n=326) |
| 2017-09-30 | 1802 | 30% (n=372) | 30% (n=403) | 25% (n=310) | 37% (n=327) | 29% (n=390) |

## Captura do valor ganho em 90 dias pelo top-N (denominador: todo o Engaging aberto em t, inclusive além de 138 dias)

| Data | N | Score | Só preço, no mesmo conjunto do score | Só preço, no pipeline inteiro | Aleatório |
|---|---:|---:|---:|---:|---:|
| 2017-06-30 | 10 | 7% | 7% | 7% | 1% |
| 2017-06-30 | 30 | 13% | 13% | 11% | 2% |
| 2017-06-30 | 50 | 18% | 18% | 18% | 3% |
| 2017-06-30 | 100 | 23% | 23% | 23% | 6% |
| 2017-07-31 | 10 | 6% | 6% | 6% | 0% |
| 2017-07-31 | 30 | 9% | 9% | 9% | 1% |
| 2017-07-31 | 50 | 14% | 14% | 12% | 2% |
| 2017-07-31 | 100 | 24% | 24% | 24% | 4% |
| 2017-08-31 | 10 | 3% | 3% | 2% | 0% |
| 2017-08-31 | 30 | 5% | 5% | 4% | 1% |
| 2017-08-31 | 50 | 8% | 8% | 7% | 2% |
| 2017-08-31 | 100 | 20% | 20% | 20% | 4% |
| 2017-09-30 | 10 | 4% | 3% | 2% | 0% |
| 2017-09-30 | 30 | 8% | 8% | 5% | 1% |
| 2017-09-30 | 50 | 12% | 12% | 10% | 2% |
| 2017-09-30 | 100 | 19% | 19% | 19% | 4% |

## Chance prevista vs. observada por faixa de idade (ganhar em 90 d; fechar em 90 d)

| Data | Faixa | n | Prevista | Observada | Fechou (ganho ou perda) |
|---|---|---:|---:|---:|---:|
| 2017-06-30 | 0-14 | 389 | 46% | 49% | 82% |
| 2017-06-30 | 15-90 | 947 | 53% | 43% | 67% |
| 2017-07-31 | 0-14 | 533 | 40% | 16% | 25% |
| 2017-07-31 | 15-90 | 1170 | 51% | 50% | 74% |
| 2017-08-31 | 0-14 | 315 | 41% | 38% | 57% |
| 2017-08-31 | 15-90 | 1251 | 47% | 29% | 41% |
| 2017-09-30 | 0-14 | 371 | 44% | 47% | 86% |
| 2017-09-30 | 15-90 | 1313 | 46% | 28% | 45% |
| 2017-09-30 | 91-120 | 118 | 7% | 0% | 2% |

## Categorias

| Data | Primeiras 2 semanas: n / win 90 d | 15-90 dias: n / win 90 d | Última janela (91-138): n / win 90 d / fechou | Focar agora: n (% dos com score) / win 90 d / % do valor ganho |
|---|---|---|---|---|
| 2017-06-30 | 389 / 49% | 947 / 43% | 201 / 0% / 0% | 270 (20%) / 42% / 46% |
| 2017-07-31 | 533 / 16% | 1170 / 50% | 279 / 16% / 26% | 337 (20%) / 48% / 53% |
| 2017-08-31 | 315 / 38% | 1251 / 29% | 291 / 24% / 32% | 326 (21%) / 31% / 42% |
| 2017-09-30 | 371 / 47% | 1313 / 28% | 195 / 0% / 1% | 338 (19%) / 27% / 39% |

## Bloco "Confirmar se está vivo" (mais de 138 dias em t)

Nesta base nenhum ciclo concluído passa de 138 dias, então um deal aberto há mais de 138 dias não pode ter fechado depois: a coluna de fechamentos é zero por construção. O que a tabela informa é o tamanho do bloco em cada data.

| Data | n | Valor de lista | Ganhou depois | Perdeu depois | Ainda aberto no fim da base |
|---|---:|---:|---:|---:|---:|
| 2017-06-30 | 149 | 409,466 | 0 | 0 | 149 |
| 2017-07-31 | 275 | 697,655 | 0 | 0 | 275 |
| 2017-08-31 | 408 | 1,038,920 | 0 | 0 | 408 |
| 2017-09-30 | 530 | 1,373,138 | 0 | 0 | 530 |
