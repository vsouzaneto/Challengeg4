# Backtest temporal da ordenação

Gerado por `scripts/backtest.py` (não editar à mão).

## Desenho

- **População em cada corte T:** toda negociação engajada até T e ainda aberta em T, inclusive as que nunca fecham na base. É a carteira que o vendedor via em T.
- **Desfecho:** ganhou em até 90 dias depois de T. Como T + 90 dias cai dentro da base, "não ganhou" é observado, também para as que seguem abertas no fim.
- **Reconstrução:** sem histórico de estágio nem data de criação, a negociação conta como em andamento de `engage_date` até `close_date`. Prospecting não tem data e fica de fora: o grupo Qualificar não é avaliado aqui.
- **O que os ordenadores veem:** vendedor, produto, preço de tabela, data de engajamento e as fechadas até T. O mês de fechamento entra só na armadilha marcada como vazamento.
- **Lista do vendedor:** as 10 primeiras da ordem de cada vendedor com pelo menos 10 abertas em T, com empates pelo ID. P@10 = ganhas entre as 10 ÷ 10. Lift@10 = ganhas ÷ ganhas esperadas ao acaso na carteira do vendedor. Val@10 = valor ganho nas 10 ÷ valor ganho nas 10 melhores da carteira sabendo o futuro (o oráculo). As somas cobrem todos os vendedor-cortes.
- **Dependência:** os cortes se sobrepõem (13100 observações para 5021 negociações únicas) e o mesmo vendedor aparece em todos. Os Δ contra a regra servida têm IC95% por bootstrap de vendedores (2000 reamostragens, cada vendedor com todos os seus cortes).

## Cortes

| Corte | Fechadas até T | Abertas em T | Sem desfecho até o fim da base | Ganharam em 90 d | Maior ciclo em T (L2) | P90 das ganhas em T (L1) | Acima do maior ciclo | Vendedores com 10+ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2017-03-31 | 647 | 1330 | 26,3% | 45,8% | 138 d | 114 d | 0,2% | 30 |
| 2017-04-30 | 1233 | 1618 | 29,1% | 44,4% | 138 d | 106 d | 1,5% | 30 |
| 2017-05-31 | 2038 | 1535 | 39,4% | 40,1% | 138 d | 105 d | 5,3% | 30 |
| 2017-06-30 | 2679 | 1686 | 42,5% | 35,4% | 138 d | 109 d | 8,8% | 30 |
| 2017-07-31 | 3306 | 2257 | 49,5% | 31,5% | 138 d | 107 d | 12,2% | 30 |
| 2017-08-31 | 4091 | 2265 | 60,6% | 24,4% | 138 d | 105 d | 18,0% | 30 |
| 2017-09-30 | 4726 | 2409 | 61,2% | 22,5% | 138 d | 107 d | 22,0% | 30 |

## Habilidade: AUC (IC95%) por corte

| Ordenador | 2017-03-31 | 2017-04-30 | 2017-05-31 | 2017-06-30 | 2017-07-31 | 2017-08-31 | 2017-09-30 | Média |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Taxa global | 0,500 (0,500–0,500) | 0,500 (0,500–0,500) | 0,500 (0,500–0,500) | 0,500 (0,500–0,500) | 0,500 (0,500–0,500) | 0,500 (0,500–0,500) | 0,500 (0,500–0,500) | 0,500 |
| Taxa por produto | 0,463 (0,432–0,489) | 0,495 (0,466–0,522) | 0,492 (0,465–0,524) | 0,523 (0,495–0,556) | 0,498 (0,472–0,522) | 0,486 (0,462–0,511) | 0,498 (0,471–0,525) | 0,494 |
| Aleatório | 0,519 (0,490–0,548) | 0,488 (0,463–0,522) | 0,507 (0,478–0,539) | 0,521 (0,493–0,545) | 0,508 (0,483–0,533) | 0,503 (0,478–0,531) | 0,523 (0,496–0,548) | 0,510 |
| Só valor de tabela | 0,528 (0,499–0,556) | 0,518 (0,489–0,543) | 0,491 (0,464–0,518) | 0,488 (0,457–0,514) | 0,509 (0,480–0,534) | 0,511 (0,482–0,541) | 0,488 (0,461–0,513) | 0,505 |
| Idade: mais nova primeiro | 0,561 (0,531–0,593) | 0,508 (0,481–0,534) | 0,538 (0,508–0,568) | 0,725 (0,704–0,748) | 0,558 (0,537–0,581) | 0,597 (0,572–0,623) | 0,826 (0,810–0,841) | 0,616 |
| Regra anterior: só até o maior ciclo → preço | 0,530 (0,500–0,558) | 0,532 (0,501–0,558) | 0,537 (0,511–0,565) | 0,558 (0,526–0,585) | 0,596 (0,572–0,621) | 0,630 (0,606–0,657) | 0,636 (0,614–0,657) | 0,574 |
| Regra servida (A): até o P90 das ganhas → até o maior ciclo → preço | 0,539 (0,512–0,568) | 0,562 (0,531–0,588) | 0,550 (0,522–0,578) | 0,610 (0,584–0,635) | 0,638 (0,614–0,662) | 0,657 (0,634–0,681) | 0,672 (0,651–0,692) | 0,604 |
| [VAZAMENTO] fechou no 3º mês do trimestre | 0,661 (0,640–0,685) | 0,704 (0,682–0,725) | 0,757 (0,736–0,778) | 0,653 (0,632–0,676) | 0,705 (0,689–0,726) | 0,813 (0,794–0,829) | 0,687 (0,668–0,708) | 0,711 |

## Lista do vendedor (10 primeiras), todos os cortes somados

| Ordenador | AUC média | P@10 | Lift@10 | Val@10 | Δ Val@10 em pp (IC95%) | Δ P@10 em pp (IC95%) |
| --- | --- | --- | --- | --- | --- | --- |
| Taxa global | 0,500 | 36,0% | 0,945 | 25,7% | -32,7 (-36,8 a -28,7) | -7,0 (-10,1 a -3,8) |
| Taxa por produto | 0,494 | 37,7% | 0,989 | 14,0% | -44,5 (-50,6 a -38,2) | -5,3 (-8,8 a -2,0) |
| Aleatório | 0,510 | 38,9% | 1,021 | 23,2% | -35,2 (-41,1 a -29,7) | -4,0 (-7,9 a -0,5) |
| Só valor de tabela | 0,505 | 38,7% | 1,015 | 53,8% | -4,6 (-6,8 a -2,5) | -4,3 (-6,0 a -2,7) |
| Idade: mais nova primeiro | 0,616 | 41,8% | 1,097 | 26,6% | -31,8 (-37,2 a -26,4) | -1,1 (-4,0 a +1,6) |
| Regra anterior: só até o maior ciclo → preço | 0,574 | 41,2% | 1,082 | 56,9% | -1,5 (-2,7 a -0,2) | -1,7 (-2,6 a -0,9) |
| Regra servida (A): até o P90 das ganhas → até o maior ciclo → preço | 0,604 | 43,0% | 1,127 | 58,4% | — | — |

## Val@10 por corte

| Ordenador | 2017-03-31 | 2017-04-30 | 2017-05-31 | 2017-06-30 | 2017-07-31 | 2017-08-31 | 2017-09-30 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Taxa global | 32,6% | 31,3% | 31,4% | 25,9% | 22,3% | 16,4% | 16,2% |
| Taxa por produto | 7,0% | 20,1% | 24,3% | 31,4% | 2,4% | 6,6% | 4,3% |
| Aleatório | 27,6% | 26,3% | 24,9% | 27,4% | 18,6% | 16,5% | 19,9% |
| Só valor de tabela | 67,5% | 63,1% | 57,9% | 57,1% | 48,5% | 41,6% | 35,5% |
| Idade: mais nova primeiro | 31,2% | 23,1% | 31,4% | 30,0% | 15,3% | 22,9% | 34,3% |
| Regra anterior: só até o maior ciclo → preço | 67,5% | 63,1% | 60,5% | 60,1% | 53,2% | 46,6% | 43,0% |
| Regra servida (A): até o P90 das ganhas → até o maior ciclo → preço | 67,5% | 63,7% | 59,8% | 61,8% | 55,9% | 48,5% | 48,2% |

## Sensibilidade ao limite do primeiro grupo

Os limites fixos foram escolhidos depois de olhar a base (106 d é o P90 das ganhas em 31/12/2017). Só a regra servida calcula o limite com o que se sabia em T.

| Ordenador | AUC média | P@10 | Lift@10 | Val@10 | Δ Val@10 em pp (IC95%) | Δ P@10 em pp (IC95%) | Ganhas fora do 1º grupo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Regra anterior: só até o maior ciclo → preço | 0,574 | 41,2% | 1,082 | 56,9% | -1,5 (-2,7 a -0,2) | -1,7 (-2,6 a -0,9) | 0,0% |
| Até 90 d → até o maior ciclo → preço | 0,614 | 43,8% | 1,150 | 58,5% | +0,1 (-1,2 a +1,4) | +0,9 (+0,1 a +1,7) | 6,5% |
| Até 100 d → até o maior ciclo → preço | 0,612 | 43,8% | 1,149 | 59,3% | +0,8 (+0,3 a +1,4) | +0,8 (+0,3 a +1,3) | 2,8% |
| Até 106 d → até o maior ciclo → preço | 0,607 | 43,0% | 1,127 | 58,4% | -0,0 (-0,2 a +0,1) | +0,0 (-0,1 a +0,1) | 1,6% |
| Até 115 d → até o maior ciclo → preço | 0,598 | 42,5% | 1,116 | 58,0% | -0,4 (-0,9 a -0,0) | -0,4 (-0,8 a -0,1) | 0,8% |
| Até 120 d → até o maior ciclo → preço | 0,593 | 42,4% | 1,112 | 58,1% | -0,3 (-1,1 a +0,6) | -0,6 (-1,0 a -0,2) | 0,4% |
| Regra servida (A): até o P90 das ganhas → até o maior ciclo → preço | 0,604 | 43,0% | 1,127 | 58,4% | — | — | 1,8% |

### Escolha do limite sem olhar o teste (walk-forward)

| Corte | Limite escolhido nos cortes anteriores | Val@10 do escolhido | Val@10 da regra servida | Val@10 da regra anterior |
| --- | --- | --- | --- | --- |
| 2017-04-30 | Até 90 d → até o maior ciclo → preço | 63,2% | 63,7% | 63,1% |
| 2017-05-31 | Até 90 d → até o maior ciclo → preço | 54,2% | 59,8% | 60,5% |
| 2017-06-30 | Até 120 d → até o maior ciclo → preço | 61,5% | 61,8% | 60,1% |
| 2017-07-31 | Até 120 d → até o maior ciclo → preço | 54,8% | 55,9% | 53,2% |
| 2017-08-31 | Até 100 d → até o maior ciclo → preço | 51,4% | 48,5% | 46,6% |
| 2017-09-30 | Até 100 d → até o maior ciclo → preço | 50,0% | 48,2% | 43,0% |
| Média | | 55,8% | 56,3% | 54,4% |

## Sensibilidade: sem as negociações que nunca fecham

Mesmos cortes, tirando as que seguem abertas no fim da base. Mostra quanto da diferença entre as regras depende delas.

| Ordenador | AUC média | P@10 | Lift@10 | Val@10 | Δ Val@10 em pp (IC95%) | Δ P@10 em pp (IC95%) |
| --- | --- | --- | --- | --- | --- | --- |
| Só valor de tabela | 0,510 | 64,8% | 1,033 | 79,1% | +1,0 (+0,3 a +1,9) | +0,2 (+0,0 a +0,5) |
| Regra anterior: só até o maior ciclo → preço | 0,510 | 64,8% | 1,033 | 79,1% | +1,0 (+0,3 a +1,9) | +0,2 (+0,0 a +0,5) |
| Regra servida (A): até o P90 das ganhas → até o maior ciclo → preço | 0,505 | 64,5% | 1,030 | 78,1% | — | — |

## Leitura

- A regra anterior (só o maior ciclo) fica -1,5 pp em relação à regra servida em Val@10 (IC95% -2,7 a -0,2) e -1,7 pp em P@10, com Val@10 acima da servida em 1 de 7 cortes.
- Sem as negociações que nunca fecham: "Só valor de tabela" fica +1,0 pp à frente da regra servida em Val@10 (IC95% +0,3 a +1,9). A vantagem das regras por idade depende desses registros, e a auditoria indica que eles podem vir da construção da base.
- Escolher o limite olhando só os cortes anteriores rende 55,8% de Val@10, contra 56,3% da regra servida: nenhum limite fixo escolhido assim supera o P90 calculado em T.
- Ordenar por preço captura valor por construção, sem acertar mais. Por isso P@10 e Val@10 aparecem lado a lado.
- O backtest mede quem teria ganhado de qualquer forma. Não mede o efeito de trabalhar a lista: isso só um piloto com grupo de controle mostra.
