# Metodologia para o Lead Scorer

> **Registro de planejamento.** Este documento descreve o plano inicial, com interface em Streamlit. A entrega final é o Lead Kanban: servidor em Python e interface web em [`solution/`](../solution/README.md), com a regra descrita no [doc 09](09-g3-revisao-fila-foco.md). Ver o [índice](README.md).

## Objetivo e enquadramento

Adotaremos o ciclo **CRISP-DM**, adaptado a uma decisão concreta: ordenar a carteira aberta para apoiar a agenda do vendedor. As seis fases são entendimento do negócio, entendimento dos dados, preparação, modelagem, avaliação e entrega. A passagem entre fases é iterativa; um problema descoberto na validação pode exigir redefinir alvo ou variáveis. [Fonte: guia CRISP-DM da IBM](https://www.ibm.com/docs/en/spss-modeler/saas?topic=dm-crisp-help-overview).

O **critério principal** será utilidade da ordenação em uma lista curta de trabalho, comparada com uma referência simples e verificável. Acurácia global, isoladamente, não responde à decisão do vendedor. A proporção histórica de `Won` entre negócios concluídos é alta; sempre mostrar a referência para que uma métrica aparentemente boa não esconda ausência de ganho real.

## Fases, entregas e critérios de passagem

| Fase | Trabalho | Evidência necessária para avançar |
|---|---|---|
| 1. Negócio | Definir usuário, decisão, capacidade de contato e o que significa prioridade. | Problema e métricas de decisão documentados; não confundir potencial de ganho com prioridade de ação. |
| 2. Dados | Auditar quatro CSVs, chaves, cronologia, nulos, distribuição dos desfechos e diferenças entre abertos e concluídos. | Relatório reproduzível, com contagens e definição do instante em que cada campo estaria disponível. |
| 3. Preparação | Criar conjunto de treino com `Won`/`Lost`; excluir informação posterior; fazer junções e imputações somente com dados de treino. | Lista de variáveis permitidas, testes de vazamento e pipeline que funciona também nas oportunidades abertas. |
| 4. Modelagem | Comparar referência simples, regressão logística regularizada e uma alternativa mais flexível **somente se necessária**. | Mesmo conjunto de avaliação e a mesma informação disponível para todos os candidatos. |
| 5. Avaliação | Testar em período posterior, medir ordenação, calibração, cobertura e erros por grupo; inspecionar casos individuais. | Ganho útil e estável frente à referência; limites declarados. Se não houver ganho, manter a referência simples. |
| 6. Entrega | Integrar o método escolhido à ferramenta, explicar cada score e documentar operação. | Um vendedor consegue usar a carteira e outra pessoa consegue reproduzir os resultados. |

## Contrato de previsão

Antes de treinar, cada linha deve ter quatro definições: **unidade** (uma oportunidade), **instante da previsão**, **variáveis disponíveis naquele instante** e **desfecho observado depois**. O arquivo oferece o desfecho final, mas não fotografias históricas das etapas. Logo, a avaliação retrospectiva é um substituto imperfeito para prever negócios hoje em `Prospecting` ou `Engaging`.

O alvo binário entre negócios concluídos estima, no máximo, a associação com `Won` **condicionada a constar entre os negócios já concluídos**. Os 2.089 negócios ainda abertos têm desfecho desconhecido; não devem ser rotulados como perda. O G2 estreitou a avaliação a negócios resolvidos em 30 dias e reprovou o modelo para uso operacional; a interface não apresentará sua saída como probabilidade. Ver [resultado do G2](07-g2-modelagem.md).

## Prevenção de vazamento e sobreajuste

1. Excluir `deal_stage` final, `close_date`, `close_value` e qualquer derivação deles do conjunto de entradas.
2. Definir treino, validação e teste antes de aprender parâmetros de imputação, codificação ou normalização. Encapsular as transformações em um `Pipeline`, ajustado só no treino. [Fonte: práticas oficiais do scikit-learn](https://scikit-learn.org/stable/common_pitfalls.html).
3. Preferir um corte temporal que represente o conhecimento disponível em cada data: um rótulo só entra no treino depois do fechamento. Verificar a distribuição das datas antes de fixar os cortes. Uma divisão aleatória pode ser usada apenas como diagnóstico adicional, não como prova principal de uso futuro. [Fonte: validação temporal do scikit-learn](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-of-time-series-data).
4. Não selecionar variáveis, ajustar hiperparâmetros, calibrar probabilidades ou escolher limiar olhando o teste final. Registrar semente, versão dos dados, divisão e parâmetros.
5. Limitar complexidade e comparar com uma referência clara. A regressão logística regularizada é um ponto de partida por ser simples de manter e explicar; modelos mais complexos precisam justificar seu ganho.

## Métricas alinhadas à decisão

| Pergunta | Medida planejada | Cuidado |
|---|---|---|
| A lista curta reúne mais negócios ganháveis? | Ganhos observados e *lift* nos primeiros `k` negócios por vendedor, contra a referência; testar vários valores plausíveis de `k`. | O dataset não informa quantos contatos cabem na agenda; `k` é cenário, não fato. |
| O modelo separa ganhos de perdas? | ROC-AUC e precisão média (*average precision*) como medidas auxiliares. | Métricas globais podem melhorar sem melhorar a lista usada pelo vendedor. [Fonte: métricas do scikit-learn](https://scikit-learn.org/stable/modules/model_evaluation.html). |
| O número pode ser lido como probabilidade? | Curva de calibração e Brier score; calibrar em dados separados, se houver base suficiente. | Calibração no histórico concluído não corrige por si o viés dos negócios ainda abertos. [Fonte: calibração do scikit-learn](https://scikit-learn.org/stable/modules/calibration.html). |
| A ferramenta atende a carteira real? | Cobertura e distribuição de score por etapa, vendedor, região, produto e presença de conta. | A maioria dos negócios abertos não tem conta identificada; medir desempenho sem essa informação. |

Comparações devem trazer tamanho das amostras e, quando possível, intervalos de incerteza. Diferenças pequenas ou concentradas em um único segmento não bastam para declarar o modelo superior.

## Critério de escolha do modelo

Escolher o método mais simples que melhore a decisão em dados não usados para ajuste e funcione nos registros abertos. Se o modelo não superar a referência com estabilidade, a entrega usará uma regra transparente e explicará o resultado negativo do experimento. Não inventar percentual de aumento de receita: esse efeito requer acompanhamento prospectivo ou experimento de operação.

## Ferramentas de trabalho

- **Jupyter Notebook:** auditoria e experimentos legíveis; a skill oficial `jupyter-notebook` foi instalada no ambiente Codex em 15/10/2026 para apoiar notebooks reproduzíveis.
- **Python e scikit-learn:** usados no experimento G2; `scikit-learn==1.9.1` está fixado em `solution/requirements-model.txt`.
- **Aplicação local:** Streamlit é a proposta para G3, conforme o plano de execução. O notebook é evidência de análise e não substitui a ferramenta funcional exigida pelo challenge.
