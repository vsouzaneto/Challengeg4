# Hipóteses e o que os dados disseram

Regra do método: um fator só entra no scoring se a hipótese que o sustenta sobreviveu aqui. Origem: **MB** = formulada pelo Marcus; **IA** = proposta pelo Claude Code; **MB?** = proposta pela IA como candidata, aguardando o Marcus dizer se a formularia por conta própria (será reclassificada para MB ou IA na revisão final).

Dados: 8.800 oportunidades; 6.711 fechadas; data de referência 2017-12-31. Números completos em `docs/exploration_results.md`; código em `solution/02_explore.py`.

| # | Hipótese | Origem | Veredito | Número que decide |
|---|---|---|---|---|
| H1 | Vendedores diferem de verdade na taxa de conversão (não é ruído) | MB? | **refutada** | spread 15,4 pp entre vendedores, mas χ² p=0,26: compatível com ruído |
| H2 | O encaixe vendedor × produto separa mais do que o vendedor sozinho | IA | **confirmada** | gap entre quartis 8,7 pp (combo) vs 3,8 pp (vendedor) |
| H3 | Vendedor com muitos deals abertos (sobrecarga) converte pior | MB? | **confirmada** | Spearman ρ=−0,45 (p=0,019) entre deals abertos e win rate do vendedor |
| H4 | Produtos diferem na taxa de conversão | IA | **refutada** | spread 4,8 pp, p=0,37 |
| H5 | Deal mais caro (preço de lista) tem menor chance de fechar | MB? | **refutada** | ρ=−0,01, p=0,41; win rate de 60% a 65% em todos os preços |
| H6 | Produtos diferem no tempo de ciclo (dias de engage a close) | IA | **refutada** | medianas de 37 a 59 dias, Kruskal p=0,087 |
| H7 | Desconto: o valor fechado (close_value) fica abaixo do preço de lista, e o desconto varia por vendedor | IA | **refutada** | close_value/preço mediana 0,998 (P10 0,87, P90 1,12); spread entre vendedores 0,04 |
| H8 | Deal parado há muito tempo não fecha: quanto maior o ciclo, menor a taxa de ganho | MB? | **refutada** | ciclo 0–14 d: 55% de ganho (n=2.806); 15–30 d: 73%; 121–138 d: 76%: o inverso da hipótese |
| H9 | Existe um teto de ciclo acima do qual ninguém ganha (linha dos 138 dias) | IA | **refutada** | ciclo máximo é 138 d tanto para Won quanto para Lost; 0 Lost além disso |
| H10 | Sobreviver às primeiras semanas aumenta a chance: P(ganhar | ciclo >= a) sobe antes de cair | IA | **confirmada** | P(ganhar | ciclo ≥ 14 d) = 68,6% vs 63,2% na base; 71% a partir de 90 d |
| H11 | Os deals em Engaging hoje estão, em sua maioria, além de qualquer ciclo histórico de vitória | IA | **confirmada** | 1.291 de 1.589 Engaging (81%) com idade > 138 d; idade mediana 165 d |
| H12 | Sazonalidade: o mês de engajamento muda a taxa de ganho | IA | **confirmada** | spread 44,6 pp, p=10⁻¹⁹, mas inclui meses truncados e censurados |
| H13 | Quem já comprou compra de novo: conta com vitórias anteriores converte melhor | MB? | **refutada** | 0 vitórias anteriores: 72% (n=1.098); >10: 61% (n=4.233): sinal invertido |
| H14 | Conta grande (receita/funcionários) fecha menos, mas paga mais | MB? | **refutada** | 62,8% / 64,1% / 62,5% por tercil de receita, p=0,50 |
| H15 | Setor da conta muda a taxa de ganho | IA | **refutada** | spread 3,7 pp, p=0,97 |
| H16 | Subsidiária de outra conta se comporta diferente de conta independente | IA | **refutada** | 63,1% vs 63,6%, p=0,74 |
| H17 | Deals abertos sem conta são um problema de processo, não uma característica de estágio | IA | **confirmada** | 68,5% (Engaging) e 67,4% (Prospecting) sem conta; 0 fechados sem conta; por vendedor de 9,7% a 39,1% com conta |
| H18 | Há vendedores sem nenhum deal fechado no histórico (impossível calibrar por vendedor) | IA | **confirmada** | 5 vendedores cadastrados sem nenhum deal (fechado ou aberto) |
| H19 | É possível reconstruir o pipeline aberto em datas passadas (base do backtest por snapshot) | IA | **confirmada** | cerca de 950 deals abertos em cada fim de trimestre de 2017 e fechados depois, cerca de 60% ganhos |
| H2b | O gap vendedor × produto é maior do que o acaso produziria com esses tamanhos de amostra (teste de permutação binomial) | MB? | **refutada** | gap observado 8,7 pp; nulo binomial 9,9 pp; p=0,89: ruído puro |
| H12b | A sazonalidade sobrevive quando se remove a censura (só meses em que todo deal teve 138 dias para fechar) | MB? | **confirmada** | sem censura à direita ainda dá 44,6 pp, mas os meses de 2016 seguem inflados por truncamento à esquerda |
| H8b | Ciclo curto = derrota rápida: a relação ciclo × ganho não é 'parado não fecha', é 'quem morre, morre cedo' | MB? | **confirmada** | Lost mediana 14 d vs Won 57 d; 50% dos Lost morrem em ≤14 d; Mann-Whitney p=10⁻²⁶ |
| H13b | O efeito negativo de 'muitas vitórias anteriores' desaparece quando se controla o período (é confusão com o tempo) | MB? | **refutada** | dentro de 2017Q1 a diferença cai para 6 pp, e Q1 ainda é truncado; inconclusiva |
| H20 | O valor esperado (preço × probabilidade) concentra o pipeline: poucos deals carregam a maior parte do valor | MB? | **confirmada** | 417 de 2.089 deals abertos (20%) concentram 50% do valor de lista |
| H21 | A base é truncada à esquerda: só há fechamentos a partir de 2017-03-01, então derrotas rápidas de deals engajados antes disso estão ausentes e inflam a win rate dos primeiros meses | MB? | **confirmada** | 972 deals engajados antes de 2017-03-01 (primeiro fechamento na base) com ciclo mínimo 5 d e 72,8% de ganho, contra 56% de Lost em ≤14 d na janela limpa: derrotas rápidas ausentes |
| H12c | Na janela limpa (engajados entre 2017-03-01 e ref − 138 d, sem truncamento nem censura) ainda há variação mensal relevante | MB? | **confirmada** | janela limpa mar–ago/2017 (n=3.718): 55% a 67% por mês, p=9×10⁻⁷: variação mensal real, porém não é atributo do deal |
| H10b | Na janela limpa, P(ganhar | ciclo >= a) continua subindo com a idade do deal | MB? | **confirmada** | na janela limpa: 61,1% na base, 67,2% a partir de 14 d, estável até 120 d |

## Leitura consolidada (2026-09-21)

1. **Quem morre, morre cedo.** Metade das derrotas acontece em até 14 dias; um deal que passa de duas semanas tem cerca de 67% de chance, e isso não cai com a idade dentro do histórico observado (até 138 dias).
2. **Não há sinal em vendedor, vendedor × produto, produto, setor, porte ou subsidiária** quando se testa contra o acaso. O gap que outros candidatos chamaram de fit vendedor × produto é o que amostras de 20 a 30 deals produzem por sorte.
3. **A base tem duas bordas que enganam.** Só há fechamentos a partir de 2017-03-01 (truncamento à esquerda: derrotas rápidas de 2016 não existem na base) e nada além de 138 dias (censura à direita). Toda taxa histórica usada no scoring vem da janela limpa 2017-03-01 a 2017-08-15 (3.718 deals).
4. **O pipeline aberto está fora do suporte do histórico.** 81% dos Engaging têm idade maior que qualquer ciclo já concluído. Isso é um achado de RevOps (higiene de pipeline), não um input para momentum.
5. **68% dos deals abertos não têm conta, em ambos os estágios, e nenhum fechado fica sem conta.** A conta é preenchida no fechamento: ausência é processo, não sinal.
6. **O valor manda.** 20% dos deals abertos carregam 50% do valor de lista; com probabilidade quase plana, a priorização vira valor esperado × urgência de ação, e o produto precisa dizer o que fazer, não fingir precisão.
