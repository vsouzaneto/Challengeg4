# Diagnóstico operacional

> Gerado por `solution/scripts/write_diagnosis_report.py` a partir de `solution/outputs/diagnosis/diagnosis.json`.
> Não editar à mão: rode `uv run python scripts/run_diagnosis.py` e depois este script.

Nesta base não há gargalo nem fator de satisfação detectável, e o desperdício não pode ser medido. A estimativa paramétrica dá 68 horas de triagem recuperáveis por mês (R$ 3.075) no cenário base. O maior desperdício de uma operação real, transferências e espera, não está registrado nos dados.

## As três perguntas do Diretor

**1. Onde o fluxo trava?** Em nenhum ponto detectável. Foram 36 testes: 4 indicadores em 9 cortes. Só um se destacou dentro do próprio corte: Low · Cancellation request, em “prioridade × tipo”, com +7,3 p.p. de tickets sem solução (p = 0,02). Corrigido para os 36 testes, o p vira 0,86: é o que se espera do acaso quando se testa tanto. A “pior combinação” de canal, prioridade e tipo (Phone · Low · Cancellation request, +13,3 p.p. de tickets sem solução) fica dentro do que o sorteio produz (15,7 p.p. em 95% dos sorteios). Os testes teriam detectado um canal com 3,4 p.p. a mais de tickets sem solução.

**2. O que impacta a satisfação?** Nada que se possa medir aqui. Nenhuma das 8 variáveis se associa à nota (o maior q é 0,83). Um modelo com todas as variáveis erra mais do que chutar a média (1,22 contra 1,19 pontos de erro médio). Uma diferença de 0,27 ponto entre dois canais teria sido detectada.

**3. Quanto estamos desperdiçando?** A base não permite medir: não há data de abertura, e em 49,3% dos tickets fechados a resolução vem antes da primeira resposta. A estimativa paramétrica do tempo de triagem que a IA pode recuperar vai de 7 a 158 horas por mês (R$ 230 a R$ 9.475), com 68 horas (R$ 3.075, 0,43 pessoa em tempo integral) no cenário base. A premissa que mais pesa é “minutos de triagem manual por ticket”, que nunca foi medida. Triagem é uma parte pequena do problema: na experiência do Diogo (hipótese 0.2), o tempo some em transferências, falta de contexto e espera por autorização.

## Como ler os testes

Para cada corte, o teste embaralha os rótulos dos segmentos 5.000 vezes e registra a maior diferença em relação à média que o sorteio produz. Se o segmento mais distante dos dados reais não passa desse limite, a diferença é compatível com o acaso. O “p da família” já considera todos os segmentos do corte. O “menor efeito detectável” é a diferença que o teste encontraria com 80% de chance, corrigida para o número de segmentos.

## Gargalos

### Tickets sem solução (Open ou Pending), todos os tickets

Média geral: 67,3%.

| Corte | Segmentos (mediana de tickets) | Segmento mais distante da média | Diferença | Limite do acaso (95%) | p da família | Menor efeito detectável |
| --- | --- | --- | --- | --- | --- | --- |
| Canal | 4 (2.126) | Email | −0,9 p.p. | 2,2 p.p. | 0,704 | 3,4 p.p. |
| Prioridade | 4 (2.107) | Low | +1,5 p.p. | 2,2 p.p. | 0,291 | 3,4 p.p. |
| Tipo | 5 (1.695) | Cancellation request | +2,3 p.p. | 2,6 p.p. | 0,121 | 3,9 p.p. |
| Assunto | 16 (530) | Network problem | −4,6 p.p. | 5,9 p.p. | 0,280 | 7,7 p.p. |
| Produto | 42 (200) | Nintendo Switch Pro Controller | +8,6 p.p. | 10,6 p.p. | 0,312 | 13,5 p.p. |
| Canal × prioridade | 16 (526) | Phone · Low | +5,0 p.p. | 5,8 p.p. | 0,150 | 7,8 p.p. |
| Canal × tipo | 20 (425) | Social media · Cancellation request | +6,5 p.p. | 6,7 p.p. | 0,060 | 8,8 p.p. |
| Prioridade × tipo | 20 (422) | Low · Cancellation request | +7,3 p.p. | 6,8 p.p. | 0,024 | 8,8 p.p. |
| Canal × prioridade × tipo | 80 (106) | Phone · Low · Cancellation request | +13,3 p.p. | 15,7 p.p. | 0,264 | 19,4 p.p. |

### Tickets nunca respondidos (Open), todos os tickets

Média geral: 33,3%.

| Corte | Segmentos (mediana de tickets) | Segmento mais distante da média | Diferença | Limite do acaso (95%) | p da família | Menor efeito detectável |
| --- | --- | --- | --- | --- | --- | --- |
| Canal | 4 (2.126) | Phone | +1,2 p.p. | 2,2 p.p. | 0,465 | 3,4 p.p. |
| Prioridade | 4 (2.107) | Critical | −0,8 p.p. | 2,2 p.p. | 0,785 | 3,4 p.p. |
| Tipo | 5 (1.695) | Technical issue | +1,2 p.p. | 2,6 p.p. | 0,717 | 3,9 p.p. |
| Assunto | 16 (530) | Cancellation request | +4,3 p.p. | 5,9 p.p. | 0,400 | 7,8 p.p. |
| Produto | 42 (200) | Nintendo Switch Pro Controller | +7,1 p.p. | 10,7 p.p. | 0,725 | 13,6 p.p. |
| Canal × prioridade | 16 (526) | Phone · Low | +5,6 p.p. | 5,9 p.p. | 0,076 | 7,8 p.p. |
| Canal × tipo | 20 (425) | Social media · Refund request | −3,1 p.p. | 6,7 p.p. | 0,970 | 8,8 p.p. |
| Prioridade × tipo | 20 (422) | High · Cancellation request | +4,7 p.p. | 6,7 p.p. | 0,534 | 8,9 p.p. |
| Canal × prioridade × tipo | 80 (106) | Phone · High · Billing inquiry | +11,4 p.p. | 15,7 p.p. | 0,649 | 19,5 p.p. |

### Nota média de satisfação (1 a 5), tickets fechados

Média geral: 2,99.

| Corte | Segmentos (mediana de tickets) | Segmento mais distante da média | Diferença | Limite do acaso (95%) | p da família | Menor efeito detectável |
| --- | --- | --- | --- | --- | --- | --- |
| Canal | 4 (688) | Chat | +0,09 ponto | 0,11 ponto | 0,167 | 0,18 ponto |
| Prioridade | 4 (700) | Low | +0,06 ponto | 0,12 ponto | 0,492 | 0,18 ponto |
| Tipo | 5 (544) | Refund request | −0,06 ponto | 0,14 ponto | 0,758 | 0,21 ponto |
| Assunto | 16 (176) | Installation support | +0,19 ponto | 0,31 ponto | 0,643 | 0,40 ponto |
| Produto | 42 (65) | Fitbit Versa Smartwatch | −0,45 ponto | 0,57 ponto | 0,332 | 0,71 ponto |
| Canal × prioridade | 16 (174) | Chat · Low | +0,19 ponto | 0,31 ponto | 0,642 | 0,40 ponto |
| Canal × tipo | 20 (138) | Social media · Cancellation request | +0,25 ponto | 0,35 ponto | 0,485 | 0,46 ponto |
| Prioridade × tipo | 20 (140) | High · Product inquiry | +0,22 ponto | 0,35 ponto | 0,694 | 0,46 ponto |
| Canal × prioridade × tipo | 80 (35) | Phone · High · Refund request | −0,70 ponto | 0,85 ponto | 0,304 | 1,01 ponto |

### Horas entre primeira resposta e resolução, como registradas, tickets fechados

Medida inválida (resolução antes da primeira resposta em 49,3% dos casos), mostrada só para registrar que nem tomada ao pé da letra ela revela um padrão. Média geral: −0,06 h.

| Corte | Segmentos (mediana de tickets) | Segmento mais distante da média | Diferença | Limite do acaso (95%) | p da família | Menor efeito detectável |
| --- | --- | --- | --- | --- | --- | --- |
| Canal | 4 (688) | Phone | −0,5 h | 0,8 h | 0,327 | 1,2 h |
| Prioridade | 4 (700) | Low | +0,4 h | 0,8 h | 0,442 | 1,2 h |
| Tipo | 5 (544) | Refund request | +0,3 h | 0,9 h | 0,922 | 1,4 h |
| Assunto | 16 (176) | Battery life | −1,3 h | 2,1 h | 0,698 | 2,7 h |
| Produto | 42 (65) | Samsung Soundbar | −2,9 h | 3,9 h | 0,429 | 4,8 h |
| Canal × prioridade | 16 (174) | Chat · Low | +1,8 h | 2,1 h | 0,167 | 2,8 h |
| Canal × tipo | 20 (138) | Email · Product inquiry | −1,3 h | 2,4 h | 0,891 | 3,2 h |
| Prioridade × tipo | 20 (140) | High · Billing inquiry | −1,6 h | 2,4 h | 0,646 | 3,1 h |
| Canal × prioridade × tipo | 80 (35) | Email · Critical · Product inquiry | −4,1 h | 5,8 h | 0,679 | 6,9 h |

## Satisfação

2.769 tickets fechados, nota média 2,99 (desvio padrão 1,41). q (BH) é o p corrigido para os 8 testes pelo método de Benjamini-Hochberg.

| Variável | Teste | p | q (BH) | Médias por grupo |
| --- | --- | --- | --- | --- |
| Canal | Kruskal-Wallis | 0,28 | 0,83 | 2,95 a 3,08 |
| Prioridade | Kruskal-Wallis | 0,63 | 0,83 | 2,96 a 3,05 |
| Tipo | Kruskal-Wallis | 0,70 | 0,83 | 2,93 a 3,03 |
| Assunto | Kruskal-Wallis | 0,81 | 0,83 | 2,80 a 3,18 |
| Produto | Kruskal-Wallis | 0,67 | 0,83 | 2,54 a 3,22 |
| Gênero | Kruskal-Wallis | 0,63 | 0,83 | 2,97 a 3,03 |
| Idade | Spearman | 0,83 | 0,83 | ρ = −0,004 |
| Horas até a resolução (como registradas) | Spearman | 0,25 | 0,83 | ρ = 0,022 |

Modelo: floresta aleatória com todas as variáveis, validação cruzada em 5 partes. Erro médio de 1,222 ponto, contra 1,189 chutando sempre a média.

## Desperdício: estimativa paramétrica

Horas recuperadas por mês = tickets × parcela roteada pela IA × minutos de triagem ÷ 60 − tickets roteados × parcela roteada errado × minutos de retrabalho ÷ 60. O custo multiplica as horas pelo custo por hora. O cenário pessimista combina todos os valores que reduzem a economia; o otimista, todos os que a aumentam.

| Premissa | Baixo | Base | Alto | Fonte |
| --- | --- | --- | --- | --- |
| Tickets por mês (tickets/mês) | 706 | 2.500 | 2.500 | Brief: 30.000/ano. Baixo: os 8.469 registros do Dataset 1 tratados como um ano |
| Parcela roteada automaticamente (fração) | 40% | 44% | 64% | Medido no Dataset 2 (tickets de TI): fluxo completo da demo no teste, só com as classes que provaram 95% de precisão. Numa operação de suporte ao cliente só vale depois de treinar com os tickets dela. Baixo: premissa original. Alto: o mesmo fluxo se o piloto comprovar as classes que faltam |
| Minutos de triagem manual por ticket (min/ticket) | 2 | 4 | 6 | Premissa: tempo de ler, classificar e encaminhar um ticket. Não medido; validar cronometrando uma semana de triagem |
| Parcela roteada errado pela IA (fração) | 2% | 2% | 3% | Medido no Dataset 2: 1 − precisão dos tickets roteados pelo fluxo completo no teste, com o intervalo de 95% |
| Minutos de retrabalho por erro (min/erro) | 5 | 10 | 20 | Premissa: retriagem e transferência de um ticket mal roteado |
| Custo por hora de um agente (R$/hora) | R$ 35 | R$ 45 | R$ 60 | Premissa: custo por hora de um agente, com encargos. Validar com RH |

| Cenário | Horas por mês | R$ por mês | Pessoas em tempo integral |
| --- | --- | --- | --- |
| Pessimista | 7 | R$ 230 | 0,04 |
| Base | 68 | R$ 3.075 | 0,43 |
| Otimista | 158 | R$ 9.475 | 0,99 |

Sensibilidade: cada premissa variada sozinha, com as outras no valor base (R$ 3.075 por mês).

| Premissa | R$/mês no valor baixo | R$/mês no valor alto | Variação |
| --- | --- | --- | --- |
| Minutos de triagem manual por ticket | R$ 1.443 | R$ 4.707 | R$ 3.263 |
| Tickets por mês | R$ 868 | R$ 3.075 | R$ 2.207 |
| Custo por hora de um agente | R$ 2.392 | R$ 4.100 | R$ 1.708 |
| Parcela roteada automaticamente | R$ 2.827 | R$ 4.530 | R$ 1.704 |
| Minutos de retrabalho por erro | R$ 3.169 | R$ 2.886 | R$ 283 |
| Parcela roteada errado pela IA | R$ 3.119 | R$ 3.017 | R$ 102 |

Fora da conta, por falta de dados: redução de transferências quando o primeiro roteamento acerta, tempo de espera e retrabalho por falta de contexto. Na hipótese 0.2 do Diogo, é aí que está o maior desperdício.

## O que medir numa operação real

Lista da hipótese 1.3 do Diogo, comparada com o que o Dataset 1 traz.

| O que medir | No Dataset 1 | Por quê |
| --- | --- | --- |
| Abertura do ticket (data e hora) | Não existe | Sem ela não há tempo de primeira resposta nem de resolução |
| Primeira resposta | Só um carimbo, sem abertura para comparar | Mede quanto o cliente espera pelo primeiro contato |
| Transferências: quantas e por quê | Não existe | É onde o tempo some, segundo a experiência do Diogo |
| Tempo parado esperando o cliente ou outra equipe | Não existe | Separa espera de esforço |
| Tempo de trabalho do agente | Não existe | Base do custo real por ticket |
| Resolução e reabertura | Resolução contraditória em 49,3% dos fechados; reabertura não existe | Mostra se o problema foi resolvido de fato |
| Motivo do contato | Tipo e assunto existem, mas não têm relação com o texto | Base para classificar e rotear |
| Taxa de resposta à pesquisa de satisfação | Não existe; só há a nota dos fechados | Sem ela não se sabe quem a nota representa |
