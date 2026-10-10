# O que a análise exploratória mostrou

Achados da análise dos dados que fundamentam a regra do app. Todos os números saem do `npm run auditoria`, que grava `../solution/analysis/saidas/auditoria-ts.md`. A maior parte também é conferida pelos scripts Python de `../solution/analysis/` (consultas SQL e backtest).

Cada achado abaixo diz o número, como foi conferido e que decisão ele mudou. O vocabulário é o da interface (D40): quente (até 89 dias), esfriando (90 a 138), frio (mais de 138) e potencial (preço de lista × chance de fechar, pelo histórico).

## 1. Os negócios com data somam US$ 3,9 mi a preço de lista, mas o potencial é de cerca de US$ 183 mil

| Situação em 31/12/2017 | Negócios | Valor a preço de lista |
|---|---|---|
| Quente, até 89 dias | 110 | US$ 227.651 |
| Esfriando, 90 a 138 dias | 188 | US$ 465.914 |
| Frio, mais de 138 dias | 1.291 (81% dos negócios com data) | US$ 3.198.664 (82% do valor dos negócios com data) |
| Prospecção (sem datas, fora dos 82%) | 500 | US$ 1.073.986 |

O potencial dos quentes e esfriando soma US$ 182.928. É critério de ordem, não previsão de receita (seção 2).

Nenhum negócio da base foi ganho ou perdido depois de 138 dias.
- Conferido com SQL: maior ciclo observado = 138 dias.
- Decisão: D2, lista "Atualize ou dê perda".

## 2. A chance de fechar cai com a idade do negócio

Na regra final (D27), a coorte em 31/12/2017 tem os 5.991 negócios iniciados até 138 dias antes (o último em 15/08/2017). Como a base começa cortada (seção 6), os iniciados antes de 01/03/2017 entram na conta a partir da idade que tinham nessa data. Por isso a primeira faixa tem 4.806 negócios.

| Faixa de idade | Chance de fechar, pelo histórico |
|---|---|
| 0–29 dias | 47,3% |
| 30–59 dias | 42,9% |
| 60–89 dias | 41,2% |
| 90–103 dias | 30,8% |
| 104–119 dias | 19,9% |
| 120–138 dias | 8,6% |
| mais de 138 dias | 0% |

- **O erro que quase entrou:** calcular a chance só com negócios concluídos dá o contrário, uma chance que sobe com a idade (de 63,2% na primeira faixa a 75,6% na última; 68,7% aos 14 dias e 71,1% aos 90, por dia exato). É viés de sobrevivência: os que nunca fecham ficam fora da conta.
- **Sensibilidade:** só com os iniciados a partir de 01/03/2017 (coorte limpa), a curva é 47,3 · 41,7 · 38,6 · 25,6 · 13,5 · 4,3%. Sem nenhuma correção (regra da preparação), 49,8 · 46,4 · 44,0 · 32,9 · 21,2 · 9,1%. No backtest, a coorte limpa chega à mesma conclusão da regra final (seção 7).
- **Calibração:** a curva ordena bem, mas como previsão superestima. Em 31/07/2017, a chance média dos negócios em andamento era 52,1% e 37,4% viraram venda até 31/12; em 31/08, 47,7% contra 34,3%; em 30/09, 46,8% contra 29,7% (com 9,7% ainda em andamento em 31/12). Por isso a chance aparece como histórico (D28).
- Decisão: D5, potencial = chance pela idade × preço de lista.

## 3. 63% não é a chance de um negócio novo

- 63,15% é a taxa de ganho entre concluídos (IC 95%: 62,0–64,3%).
- De cada 100 negócios iniciados, cerca de 50 são ganhos, 29 perdidos e 22 nunca são concluídos (coorte de 5.991).

## 4. Vendedor, produto, região, setor e porte não mudam a taxa de ganho

| Comparação, entre os concluídos | p-valor do qui-quadrado |
|---|---|
| Vendedor | 0,264 |
| Gestor | 0,786 |
| Regional | 0,604 |
| Produto | 0,372 |
| Setor | 0,971 |
| Empresa | 0,943 |
| Porte: funcionários (quartis) | 0,103 |
| Porte: receita (quartis) | 0,144 |

- A diferença entre o melhor e o pior vendedor (15,4 p.p.) aparece em 38% dos sorteios aleatórios (10.000 sorteios).
- Em valor, a diferença é de 23,5 p.p. e aparece em 42% dos sorteios.
- A receita varia 9,3 vezes entre vendedores, mas acompanha o volume de negócios (Spearman 0,62), não a taxa de ganho (−0,21).
- **O que o vendedor muda:** quanto fica parado. Na coorte de 31/12 (sem a correção de entrada tardia), a parte dos negócios que continua aberta vai de 0% a 31% conforme o vendedor (p < 0,001). Os dados não separam o efeito do vendedor do efeito da carteira e da região (a regional também dá p < 0,001 na coorte). Esse efeito multiplica todos os negócios do vendedor e não muda a ordem da lista dele.
- Decisão: D3 e D29, vendedor e produto fora do score; na visão do gestor, a parte fria de cada carteira aparece como retrato, não como ranking.

## 5. O calendário pesa, mas não serve para o score

| Mês do trimestre em que o negócio foi concluído | Taxa de ganho |
|---|---|
| 1º | 49,0% |
| 2º | 54,7% |
| 3º | 80,7% |

- Para um negócio em andamento, ainda não se sabe em que mês ele vai ser concluído. Por isso o padrão fica como contexto, fora da regra.
- O mesmo efeito explica a falsa impressão de que "o não vem rápido e o sim demora".

## 6. Qualidade dos dados

- A base começa cortada: a primeira conclusão é de 01/03/2017, e 1.185 negócios foram iniciados antes disso. Eles só estão na base porque ainda estavam abertos naquela data. Tratamento: entrada tardia (D27, seção 2).
- O nome do produto aparece como "GTXPro" em 1.480 linhas, contra "GTX Pro" no catálogo.
- 1.425 de 2.089 negócios em andamento (68%) não têm empresa. Nenhum negócio concluído está sem empresa, então "sem empresa" denuncia o desfecho e não pode entrar no score.
- Os 500 negócios em prospecção não têm data.
- 5 dos 35 vendedores não têm nenhum negócio.
- Dos 30 com histórico, 9 ficam sem nenhum negócio quente ou esfriando em 31/12/2017: 6 só têm negócios frios e prospecção, e 3 não têm nada aberto. A interface precisa de estados vazios que digam o que fazer.

## 7. A regra simples fica no mesmo patamar de um modelo de machine learning

Backtest da regra final, nas 3 datas com histórico suficiente (31/07, 31/08 e 30/09/2017): os 10 primeiros negócios de cada vendedor e a receita que eles trouxeram nos 90 dias seguintes, sobre a receita ganha de todos os negócios em andamento do vendedor.

| Método | Receita capturada |
|---|---|
| Gradient boosting (`solution/analysis/significancia_ml.py`) | 43,2% |
| Potencial (a regra do app) | 40,9% |
| Situação e preço (quente, depois esfriando, depois frio; dentro de cada um, por preço) | 40,7% |
| Preço, com os frios no fim | 37,6% |
| Só preço | 33,2% |
| Chance só com concluídos (o erro da seção 2) | 29,1% |
| Aleatório | 14,1% |

- **Potencial contra só preço:** +7,66 p.p. (IC 95% de 3,49 a 12,62; p = 0,0004), num teste pareado com o vendedor como unidade. O potencial ganha do preço em cada uma das 3 datas (37,8% contra 35,6%; 38,5% contra 34,0%; 47,7% contra 29,0%).
- **Gradient boosting contra o potencial:** +2,32 p.p. (IC 95% de −2,46 a +6,39; p = 0,33): **não significativa**. O modelo fica fora: não ganha além do acaso, e a regra dá a frase de motivo de cada negócio.
- **Potencial contra situação e preço:** empate, +0,12 p.p. (IC 95% de −1,51 a 2,11; p = 0,90). O ganho vem de separar quente, esfriando e frio. O potencial fica porque dá a frase de motivo e o score (D30).
- **Coorte limpa (sensibilidade):** sobra só 30/09, com +18,69 p.p. sobre só preço (IC 95% de 12,28 a 25,57).
- **Histórico:** no backtest da preparação (4 datas, sem a correção do corte), os números eram 44,4% para o potencial e 45,0% para o gradient boosting (+0,62 p.p.; p = 0,74). As duas versões chegam à mesma conclusão.

Fonte: `npm run auditoria`, seção "Regra final (G1)" e a linha "Modelo de ML na regra final".
