# G2 — Experimento temporal e decisão de scoring

**Status:** concluído em 15/10/2026. Código em [`solution/experiment_model.py`](../solution/experiment_model.py), resultados agregados em [`solution/experiments/g2-results.json`](../solution/experiments/g2-results.json). Nenhum modelo treinado foi aceito como probabilidade operacional.

## Pergunta de negócio

O histórico de negócios ganhos e perdidos permite encontrar, para cada vendedor, cinco negócios com maior chance de ganho e maior valor comercial do que uma referência simples? A unidade de decisão é a **oportunidade aberta**. A avaliação retrospectiva só pode usar oportunidades com resultado observado.

## Desenho reproduzível

O teste mais defensável com estas tabelas é condicional: entre oportunidades que entraram em `Engaging` e **foram resolvidas em até 30 dias**, prever `Won` versus `Lost`. Os 30 dias dão a mesma janela de observação em validação e teste. Isso **não mede a chance de uma oportunidade aberta eventualmente fechar**: negócios que continuam em andamento ou demoram mais de 30 dias não têm rótulo neste experimento.

| Etapa | Coorte e disponibilidade do rótulo | Registros |
|---|---|---:|
| Treino inicial | `engage_date + 30 dias <= 30/06/2017`; fechamento dentro desses 30 dias | 1.049 |
| Validação | Entrada de 01/07 a 31/08; resultado até 30 dias após entrada, observável até 30/09 | 762 |
| Retreino | Mesma regra do treino inicial, com corte em 30/09 | 2.081 |
| Teste posterior | Entrada de 01/10 a 30/11; resultado até 30 dias após entrada, observável até 30/12 | 737 |

Na validação, **1.229 de 1.991** entradas não se resolveram em 30 dias; no teste, **307 de 1.044**. Esse filtro cria viés de seleção e limita a extrapolação para a carteira aberta. A data de entrada em `Engaging` é a única data inicial disponível; negócios em `Prospecting` nem a possuem. O dataset não tem histórico de etapas ou de atividade comercial para reconstruir uma fila real passada.

**Entradas do modelo:** produto normalizado e, em uma variante, vendedor. Ambos cobrem os 2.089 negócios abertos. Dados da conta foram excluídos porque faltam em 1.425 abertos. `deal_stage` final, `close_date` e `close_value` são proibidos como entradas. O preço de catálogo entra apenas na referência de ordenação por valor; a receita realizada (`close_value`) entra apenas na **métrica de avaliação**. Transformações do modelo são ajustadas só no treino. A regressão logística usa `DictVectorizer` e `LogisticRegression(C=1)` em um pipeline; a taxa por produto aplica suavização de 20 negócios em direção à taxa global do treino. Nenhum parâmetro foi ajustado com o teste.

**Métrica principal fixada antes do teste:** ganhos esperados nas cinco primeiras posições de cada vendedor. Foram 30 vendedores e 150 posições em cada coorte. Quando vários negócios têm exatamente o mesmo score, a vaga de corte é dividida proporcionalmente entre eles; isso impede que a ordem do CSV ou o ID determine o resultado. Métricas secundárias: proporção da receita realizada nessas posições, AUC e Brier. A escolha pela validação foi a maior quantidade de ganhos nas cinco primeiras posições, com receita e Brier como desempate.

## Resultados

| Método | Validação: ganhos em 150 | Teste: ganhos em 150 | Teste: AUC | Teste: Brier | Teste: parcela da receita |
|---|---:|---:|---:|---:|---:|
| Taxa global, sem ordenação | 81,84 | 82,43 | 0,500 | 0,2484 | 20,36% |
| Preço de catálogo | 73,04 | 81,01 | 0,511 | — | 43,31% |
| Taxa por produto suavizada | 87,65 | 84,06 | 0,498 | 0,2498 | 6,03% |
| Logística: produto | 87,65 | 84,06 | 0,500 | 0,2499 | 6,03% |
| Logística: produto + vendedor | **88,15** | **83,40** | **0,513** | **0,2512** | **4,60%** |

Os ganhos fracionários são o valor esperado do desempate entre scores iguais, não negócios parcialmente fechados. O modelo de produto + vendedor foi escolhido na validação. No teste, acrescentou **menos de um ganho esperado** sobre a taxa global em 150 posições e teve Brier pior que ela. AUC 0,513 indica discriminação muito fraca neste recorte. A referência por preço concentrou a maior receita observada, mas também não discriminou ganho de forma relevante; ela sozinha não atende à necessidade de uma fila de ação contextualizada.

O sinal por produto também mudou: por exemplo, `MG Advanced` teve taxa de ganho de 44,4% na validação e 53,7% no teste; `MG Special`, que custa 55 no catálogo, teve 58,6% e 52,9%. O modelo tende a favorecer produtos de baixo preço pela taxa de ganho, prejudicando a utilidade comercial medida em receita. O item `GTK 500` custa 26.768, mas teve somente 3 exemplos no treino inicial; sua taxa isolada não é confiável. Estes preços são unidades monetárias do catálogo, sem inferir moeda além do que os dados fornecem.

## Decisão para G3

**Reprovar a hipótese de usar a saída da regressão logística como “potencial de sucesso” ou como motor da fila.** O resultado posterior não sustenta ganho preditivo útil, e a amostra é selecionada por velocidade de fechamento. Não exibir percentuais do modelo como probabilidade de ganhar negócios abertos. A taxa histórica por produto pode aparecer como **contexto descritivo**, com tamanho amostral e aviso de que não prevê o desfecho individual.

Construir uma **prioridade comercial heurística e explicável** que combine o valor indicativo de catálogo, a etapa atual, o tempo desde a entrada em `Engaging` quando disponível e pendências de informação. A fórmula, pesos e texto de cada motivo serão definidos e testados no G3; qualquer resultado retrospectivo dessa nova regra será exploratório, porque o teste deste gate já foi observado. O produto deve permitir que o vendedor entenda e altere seu julgamento, sem promessa causal de que uma ação elevará a conversão.

Para um modelo operacional real, precisaríamos de snapshots datados do CRM, criação da oportunidade, histórico de etapa e atividades, valor estimado no momento da decisão, desfechos posteriores inclusive dos abertos atuais e validação em períodos recentes. Só então haveria base para calibrar e monitorar uma probabilidade.

## Reproduzir

A partir de `solution/`, criar ambiente Python e instalar `requirements-model.txt`; executar `python experiment_model.py --output experiments/g2-results.json` e `python -m unittest discover -s tests -v`. O script verifica o SHA-256 do ZIP público antes de executar. Esta versão passou em **11 testes**. A decisão de separar treino e teste antes de ajustar transformações segue a [orientação oficial de scikit-learn sobre vazamento de dados](https://scikit-learn.org/stable/common_pitfalls.html); o [guia oficial de instalação](https://scikit-learn.org/stable/install) recomenda ambiente isolado.
