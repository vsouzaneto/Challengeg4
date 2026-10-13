# Classificador de tickets

> Gerado por `solution/scripts/write_classifier_report.py` a partir de `solution/outputs/classifier/`.
> Não editar à mão: rode `uv run python scripts/train_classifier.py` e depois este script.

Um classificador TF-IDF + SVM linear acerta 86,7% dos tickets de TI do Dataset 2 (macro-F1 86,5%). A demo completa (política, guarda de domínio, limiar por classe e só as classes que provaram 95% de precisão no teste) roteia sozinha 43,5% dos tickets de teste com 97,7% de precisão (IC 95% 97,0% a 98,2%), e o resto vai para a triagem humana. Nos tickets do Dataset 1, de outra operação, ele não serve: a política, o guarda de vocabulário e os limiares mandam 98,1% deles para humanos.

## Dados e divisão

- 47.837 tickets em 8 classes.
- Quase-duplicatas (similaridade de cosseno TF-IDF de pelo menos 0,9): 1.286 grupos com 5.630 tickets. Cada grupo fica inteiro de um lado da divisão, para o teste não ver textos quase iguais aos do treino.
- 105 desses grupos (617 tickets) têm rótulos diferentes para textos quase iguais. É a primeira evidência de ruído de rótulo (X1); a lista está em `solution/outputs/classifier/near_duplicate_conflicts.csv`.
- Divisão estratificada: treino 33.185, calibração 4.740, escolha de limiar 4.741 e teste 5.171. O teste foi usado uma única vez, no fim; ele também decidiu quais classes roteiam sozinhas, então o piloto precisa confirmá-las.

## Escolha do modelo

| Modelo | Macro-F1 na validação |
| --- | --- |
| TF-IDF + SVM linear (C = 1,0) (escolhido) | 86,5% |
| TF-IDF + regressão logística (C = 16) | 85,9% |
| TF-IDF + regressão logística (C = 4) | 85,6% |
| TF-IDF + SVM linear (C = 0,25) | 85,3% |
| TF-IDF + regressão logística (C = 1) | 83,6% |
| TF-IDF + Naive Bayes complementar (alfa 0,5) | 80,7% |
| TF-IDF + Naive Bayes complementar (alfa 0,1) | 79,6% |

## Resultado no teste

Acurácia 86,7% (IC 95% 85,8% a 87,6%); macro-F1 86,5% (IC 95% 85,5% a 87,6%). A classe mais difícil é Administrative rights, com F1 de 78,9%.

| Classe | Precisão | Recall | F1 | Tickets no teste |
| --- | --- | --- | --- | --- |
| Administrative rights | 88,7% | 71,0% | 78,9% | 176 |
| Miscellaneous | 87,4% | 77,8% | 82,3% | 706 |
| Hardware | 79,5% | 89,2% | 84,0% | 1.361 |
| HR Support | 86,3% | 84,6% | 85,5% | 1.091 |
| Internal Project | 87,4% | 85,3% | 86,3% | 211 |
| Storage | 89,5% | 86,3% | 87,9% | 277 |
| Access | 91,0% | 86,7% | 88,8% | 712 |
| Purchase | 97,4% | 100,0% | 98,7% | 637 |

Matriz de confusão do teste (linhas: classe real; colunas: classe prevista). Hardware é o destino mais comum dos erros.

| Real \ Previsto | Access | Administrative rights | HR Support | Hardware | Internal Project | Miscellaneous | Purchase | Storage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Access** | **617** | 3 | 28 | 46 | 0 | 11 | 0 | 7 |
| **Administrative rights** | 1 | **125** | 5 | 37 | 1 | 6 | 0 | 1 |
| **HR Support** | 16 | 2 | **923** | 110 | 6 | 22 | 1 | 11 |
| **Hardware** | 24 | 8 | 61 | **1.214** | 8 | 27 | 13 | 6 |
| **Internal Project** | 3 | 0 | 8 | 14 | **180** | 4 | 1 | 1 |
| **Miscellaneous** | 16 | 2 | 36 | 88 | 11 | **549** | 2 | 2 |
| **Purchase** | 0 | 0 | 0 | 0 | 0 | 0 | **637** | 0 |
| **Storage** | 1 | 1 | 8 | 19 | 0 | 9 | 0 | **239** |

## Calibração

Probabilidades calibradas pelo método sigmoide, ajustado só na parte de calibração. Erro de calibração esperado no teste: 3,6%.

## Regras de roteamento

O alvo é o da hipótese 3.2 do Diogo: pelo menos 95% de precisão nos tickets que a IA roteia sozinha, olhando por categoria. Cada limiar foi escolhido na parte de validação de modo que o limite inferior do intervalo de 95% da precisão fique acima do alvo.

| Regra | Limiar | Cobertura | Precisão (IC 95%) | Ponto fraco |
| --- | --- | --- | --- | --- |
| Limiar único escolhido para 95% de precisão | 0,735 | 74,2% | 95,9% (95,2% a 96,4%) | Hardware com 92,9% |
| Limiares por classe, só o classificador | um por classe | 64,9% | 97,0% (96,4% a 97,5%) | Três classes sem prova de 95% no teste |
| **Fluxo completo da demo** (adotado) | um por classe | **43,5%** | **97,7%** (97,0% a 98,2%) | Só 4 classes roteiam sozinhas até o piloto |
| Limiar pelo custo do erro (4 min de triagem contra 10 min de retrabalho) | 0,60 | 85,8% | 92,4% (91,6% a 93,2%) | Abaixo dos 95% exigidos |

Limiares por classe, medidos no teste:

| Classe | Limiar | Previstos | Acima do limiar | Precisão (IC 95%) | Na demo |
| --- | --- | --- | --- | --- | --- |
| Access | 0,65 | 678 | 571 | 97,0% (95,3% a 98,1%) | roteia sozinha |
| Administrative rights | — | 141 | 0 | não roteado | nunca roteada |
| HR Support | 0,75 | 1.069 | 752 | 95,6% (93,9% a 96,9%) | em piloto |
| Hardware | 0,86 | 1.528 | 760 | 96,8% (95,3% a 97,9%) | roteia sozinha |
| Internal Project | 0,84 | 206 | 106 | 99,1% (94,8% a 99,8%) | em piloto |
| Miscellaneous | 0,86 | 628 | 298 | 99,3% (97,6% a 99,8%) | roteia sozinha |
| Purchase | 0,63 | 654 | 648 | 98,3% (97,0% a 99,0%) | roteia sozinha |
| Storage | 0,68 | 267 | 219 | 94,5% (90,7% a 96,8%) | em piloto |

A validação garantia 95% para todas as classes, mas no teste o limite inferior ficou abaixo do alvo em HR Support (93,9%), Internal Project (94,8%), Storage (90,7%). Essas classes ficam **em piloto**: a demo manda os tickets delas para a triagem humana, mesmo acima do limiar, até o piloto provar a precisão com tickets novos. Como o teste escolheu as classes habilitadas, o piloto também precisa confirmá-las.

## Fluxo completo da demo no teste

Cada um dos 5.171 tickets de teste passou pela mesma função da demo (`support_triage.triage`): política, guarda, classificador, limiar e classes habilitadas. É esse o número que vale para a proposta. O texto do Dataset 2 já vem pré-processado, então a política roda sobre ele como está.

Roteados sozinhos: 2.250 (43,5%), com 97,7% de precisão (IC 95% 97,0% a 98,2%).

| Classe | Roteados sozinhos | Precisão (IC 95%) |
| --- | --- | --- |
| Access | 564 | 97,0% (95,2% a 98,1%) |
| Hardware | 744 | 97,0% (95,6% a 98,0%) |
| Miscellaneous | 294 | 99,3% (97,6% a 99,8%) |
| Purchase | 648 | 98,3% (97,0% a 99,0%) |

| Por que foi para uma pessoa | Tickets |
| --- | --- |
| Confiança abaixo do limiar | 1.637 |
| Classe em piloto | 1.065 |
| Classe nunca roteada sozinha | 138 |
| Fora do domínio | 54 |
| Política | 27 |

Se o piloto comprovar todas as classes menos Administrative rights, o mesmo fluxo roteia 64,1% com 97,0% de precisão (IC 95% 96,4% a 97,6%).

**Pedidos de privilégio fora da classe Administrative rights.** Bloquear a classe prevista não basta: um pedido de privilégio previsto como outra classe seria roteado sozinho. No teste, 5 dos 176 tickets rotulados como Administrative rights foram roteados sozinhos (Hardware 5). Os textos estão abaixo; lidos um a um, relatam falhas (patch, atualização do Windows, boot, monitor, publicação de vagas), sem pedido de acesso ou de privilégio, o que sugere ruído de rótulo (X1). Ainda assim, no piloto todo ticket roteado sozinho que um agente reclassificar como pedido de privilégio conta como violação da política.

- “kb patches with big issues kb patches big issues hello please take consideration article decline two kb kb big impact users where cells form word disappear arti”
- “social synchronizing issues friday pm social synchronizing issues dear facing issues regarding social job advertisements posted visible has happened several cas”
- “builds not working builds working dear please log ticket with or help get boot back up currently working have tried over last couple days rebuild couple even on”
- “action required apply windows updates immediately sent wednesday re action required apply updates immediately hello have requested updates thought failed instal”
- “one of the monitors are not working correctly problem middle screen”

## Desvio de domínio: o modelo nos tickets do Dataset 1

O modelo aprendeu com tickets de TI e não com suporte ao cliente. Aplicado às 8.469 descrições do Dataset 1, ele prevê Hardware 83,5%, Access 7,7%, Miscellaneous 5,8%, com confiança mediana de 73,8%. Sem proteção, 50,6% passariam do limiar único e 20,8% dos limiares por classe: confiança alta não garante que o ticket seja do domínio.

O guarda mede quanto das palavras de conteúdo do ticket o modelo viu no treino; palavras gramaticais como “my” ou “the” não contam, porque o pré-processamento do Dataset 2 removeu umas e manteve outras. Na validação, a mediana é 100%; no Dataset 1, 81,8%. Com o corte em 91,0% (o 1º percentil da validação), o guarda manda para humanos 93,2% dos tickets do Dataset 1 e só 1,1% dos tickets de teste do Dataset 2.

De ponta a ponta (política, guarda, classificador e limiares), 161 dos 8.469 tickets do Dataset 1 (1,9%) ainda seriam roteados sozinhos: Hardware 94, Access 67. São em geral textos genéricos com palavras de TI, como “suspeito de um problema de hardware”. A fila escolhida não é absurda, mas é a de outra operação: por isso o modelo precisa ser retreinado com os tickets da própria operação antes de qualquer uso real.
