# Process log — Lead Scorer

Este registro descreve, em ordem de desenvolvimento, como usamos IA para investigar o problema, testar hipóteses e construir o MVP. Ele foi redigido retrospectivamente a partir da conversa e das execuções realizadas. A descrição do uso de ChatGPT foi fornecida pelo autor da submissão; as ações do Codex estão registradas nesta conversa. Este documento não substitui exportações de conversas, screenshots ou uma execução reproduzível do backtest.

## 1. Definição do problema

O desafio apresenta uma operação com 35 vendedores e aproximadamente 8.800 oportunidades. A priorização era feita no feeling: cada vendedor escolhia onde investir tempo com base na própria experiência.

Nosso objetivo foi ajudar o vendedor a responder: “Em quais oportunidades devo concentrar meu tempo?”. Antes de programar, lemos o desafio, as regras de contribuição e o template de submissão. Limitamos o trabalho à pasta da submissão.

## 2. Primeira hipótese

Inicialmente, consideramos um score de probabilidade de fechamento baseado no histórico do CRM. A hipótese era que características dos produtos, vendedores e contas poderiam separar oportunidades com maior e menor chance de vitória.

Tratamos essa ideia como hipótese a investigar, não como capacidade já demonstrada. A implementação ficou para depois da inspeção e dos testes históricos.

## 3. Inspeção dos dados

Após localizar o ZIP baixado pelo autor, inspecionamos seu conteúdo e extraímos somente os quatro CSVs solicitados: contas, produtos, vendedores e pipeline. A análise encontrou:

- 8.800 oportunidades: 2.089 abertas e 6.711 encerradas.
- 1.425 abertas sem conta associada, equivalentes a 68,21% das abertas.
- Divergência entre `GTXPro` no pipeline e `GTX Pro` no catálogo, afetando 1.480 oportunidades. A normalização foi feita em memória, sem reescrever os CSVs.
- Ausência de histórico de mudanças de estágio; temos o estado registrado, não a trajetória completa de cada negociação.
- `close_value`, `close_date` e estágio final como riscos de data leakage: informações posteriores à decisão não podem alimentar uma previsão de fechamento.

Todas as perdas tinham `close_value` igual a zero e todas as vitórias tinham valor positivo. Usar esse campo como entrada revelaria diretamente o resultado. Também verificamos ausências, datas, duplicatas e correspondências entre tabelas antes de construir o motor.

## 4. Correção importante da hipótese

A exploração com IA avaliou uma camada de propensão histórica. O primeiro experimento combinou produto, vendedor e setor; o segundo simplificou para produto e vendedor, disponíveis nas oportunidades abertas.

Ordenamos as encerradas por `engage_date` e separamos aproximadamente 70% para histórico e 30% para teste. O corte foi 16/08/2017: 4.690 negócios anteriores e 2.021 posteriores. Excluímos 983 negócios do histórico porque ainda não tinham encerrado antes do corte, restando 3.707 resultados disponíveis para cálculo. `close_date` serviu somente para verificar disponibilidade temporal. `close_value` foi usado apenas como resultado econômico na avaliação dos rankings.

Comparamos preço, propensão histórica e propensão multiplicada pelo preço. O teste mostrou que:

- Preço sozinho era uma referência econômica forte.
- Historical Fit sozinho não apresentou poder preditivo consistente nos cortes avaliados.
- Balanced Priority teve pequenos ganhos em alguns cortes, mas não em todos.
- Esses ganhos não foram estatisticamente convincentes no experimento realizado.

Na versão final, com produto e vendedor, os 20% superiores capturaram 48,91% do valor realizado no teste, contra 48,58% usando somente preço. A taxa Won foi 65,53%, contra 64,78%. Em 500 reamostragens pareadas, os intervalos aproximados de 95% das diferenças incluíram zero: de −0,91 a +1,90 ponto percentual para captura de valor e de −1,23 a +3,17 pontos para taxa Won.

Esses intervalos são exploratórios e não tratam completamente a dependência entre negócios das mesmas contas ou vendedores. Não provam equivalência entre estratégias nem superioridade da proposta.

Decidimos NÃO apresentar Historical Fit como probabilidade de fechamento. Não aceitamos automaticamente a primeira hipótese explorada com a IA: usamos os dados para reduzir a promessa do produto. Os backtests foram executados em memória e relatados na conversa; nesta etapa, não salvamos um script específico de reprodução desses experimentos.

## 5. Decisão de produto

A solução final é uma ferramenta de priorização econômica com incerteza explícita:

- Priority Score é um ranking relativo, não uma probabilidade.
- Valor econômico é o sinal principal; `sales_price` permanece disponível como referência independente.
- Historical Fit é a média simples das taxas históricas ajustadas de produto e vendedor.
- O shrinkage usa peso 50 para aproximar grupos pequenos da taxa geral: `(vitórias + 50 × taxa geral) / (exemplos + 50)`.
- Balanced Priority é `sales_price × Historical Fit`. O Priority Score transforma esse valor em posição percentual entre todas as abertas, com posição média nos empates.
- Confiança Alta exige pelo menos 200 exemplos em ambos os grupos; Média exige pelo menos 50 em ambos; Baixa corresponde aos demais casos. Esses rótulos representam volume de evidência, não garantia de acerto.
- Watchlist reúne preço no percentil 80 ou superior da carteira aberta e confiança Baixa.
- Oportunidades de baixa confiança nunca são descartadas automaticamente.

Na simulação de referência de 31/12/2017, o motor preservou as 2.089 abertas: 1.407 com confiança Alta, 667 Média e 15 Baixa. As 15 da Watchlist continuaram no ranking. A referência é uma convenção de simulação, não uma data comprovada de extração.

## 6. Risco de feedback loop

Na revisão do produto, explicitamos o risco de um score baixo fazer vendedores ignorarem oportunidades. A redução de atenção poderia diminuir suas chances de sucesso; novos dados passariam a refletir essa decisão e poderiam reforçar artificialmente o ranking em atualizações futuras.

Por isso, score serve para priorizar, não excluir. Todas as oportunidades continuam acessíveis e casos de pouca evidência recebem revisão humana. Essas escolhas reduzem o risco de exclusão automática, mas não demonstram que o ciclo de retroalimentação foi eliminado. Não realizamos um experimento em operação comercial para medi-lo.

## 7. Desenvolvimento e validação

Usamos Python para processamento e Streamlit para interface, com responsabilidades separadas:

- `solution/data.py`: carregamento, validação e normalização em memória.
- `solution/scoring.py`: histórico, scores, suporte, confiança e Watchlist.
- `solution/app.py`: apresentação, filtros e explicações determinísticas, sem LLM.

Primeiro implementamos o motor, executamos o código e criamos oito testes automatizados. Depois acrescentamos testes da interface. Na conclusão da V3, os 14 testes da suíte passaram; também executamos testes de interação com o AppTest do Streamlit.

As verificações cobriram preservação das 2.089 abertas, ausência de alteração dos CSVs por comparação de hashes, exclusão de resultados futuros do histórico, independência dos scores em relação a campos proibidos, shrinkage, empates, casos sem histórico e filtros que não recalculam os scores globais.

Comparamos também a saída completa antes e depois das mudanças de apresentação e os hashes de `data.py` e `scoring.py`: scores, Watchlist e motor permaneceram iguais.

A primeira tentativa de instalar Streamlit falhou por restrições de rede. Paramos e relatamos o erro, sem modificar código para contorná-lo. Em uma etapa posterior, Streamlit 1.65 já estava disponível no ambiente; então executamos a interface. Não atribuímos ao Codex a instalação que ocorreu fora desse registro.

## 8. Iterações da interface

**V1 — Dashboard técnico.** Entregamos filtros, indicadores, tabela completa, explicação de cada oportunidade e comparação com preço. Era funcional, mas exibia muitos detalhes antes de orientar a ação.

**V2 — Prioridades de hoje.** Reduzimos a primeira tela a cinco oportunidades, três indicadores e linguagem em português. Recolhemos a carteira completa e os detalhes históricos.

**V3 — Agir e revisar.** A seção “Foque nestas oportunidades hoje” passou a selecionar as cinco maiores prioridades entre confiança Alta e Média. Logo abaixo, “Revise estas oportunidades antes de agir” apresenta a Watchlist. Nenhum score foi recalculado e nenhuma oportunidade foi removida.

A separação foi necessária porque alta prioridade econômica com baixa evidência não deve parecer uma recomendação automática. Nos cards, classificações textuais de prioridade substituíram números semelhantes a probabilidades; o valor numérico permaneceu nos detalhes.

Após aprovação da interface, fizemos apenas dois ajustes finais de texto: “Prioridades exibidas” no indicador das cinco recomendações e uma orientação para o vendedor selecionar seu nome na barra lateral.

## 9. Como a IA foi usada

Segundo o relato do autor, ChatGPT foi usado para decompor o problema, questionar hipóteses, definir experimentos, revisar decisões e elaborar prompts de implementação.

Codex foi usado para inspecionar arquivos, analisar os CSVs, escrever código, executar testes, construir a interface e validar alterações. O trabalho foi dividido em etapas autorizadas: leitura, localização dos dados, análise, experimentos, motor, interface e documentação.

As explicações dentro do produto são determinísticas, baseadas nos dados. A solução não chama um LLM para justificar scores ou recomendar negócios.

## 10. Onde a IA precisou ser corrigida

O exemplo principal foi a expectativa inicial de que propensão histórica pudesse oferecer uma estimativa forte de fechamento. O backtest temporal não sustentou essa interpretação.

A correção foi reduzir a promessa: em vez de apresentar uma previsão confiável de compra, entregamos prioridade relativa com referência econômica, suporte histórico e limites visíveis. Não foi uma comprovação de que qualquer modelo preditivo seria impossível, mas de que os experimentos realizados não justificavam aquela promessa.

Também corrigimos a apresentação: o topo do ranking econômico reunia oportunidades com pouca evidência. O usuário exigiu separá-las das recomendações de ação, sem esconder esses negócios nem alterar os scores.

## 11. Julgamento humano

O autor orientou decisões que não deveriam ser delegadas automaticamente à IA:

- Não transformar score em sentença de aceitação ou descarte.
- Considerar valor econômico, não apenas taxa de fechamento.
- Preservar oportunidades com pouca evidência.
- Considerar o risco de feedback loops antes de automatizar decisões.
- Exigir comparação temporal com uma referência simples.
- Preferir transparência a uma solução mais sofisticada e obscura.
- Separar prioridade econômica de recomendação de ação e revisão humana.

O papel humano foi definir limites de interpretação, exigir validação e decidir como comunicar a incerteza ao vendedor.

## 12. Limitações

- Dataset antigo, com datas observadas de 2016–2017; não demonstramos validade em uma operação atual.
- Ausência de atividades comerciais, como última interação, próxima ação, orçamento e decisor.
- Ausência de histórico de mudanças de estágio e de versões históricas dos cadastros e preços.
- Muitas oportunidades abertas sem conta associada.
- Teste restrito a encerradas, com risco de seleção por duração do ciclo e encerramento observado.
- Um corte temporal e comparações exploratórias; resultados não constituem validação externa.
- Ausência de prova causal de que usar o ranking aumenta vendas ou produtividade.
- Balanced Priority não demonstrou superioridade estatística confiável sobre preço sozinho.
- Confiança mede quantidade de exemplos, não calibração, qualidade dos dados ou certeza individual.
- Valor capturado no teste não equivale a receita incremental, margem ou retorno por hora de trabalho.

O resultado é um MVP de apoio à decisão. Seu mérito está na explicação verificável e nos limites explícitos, não em uma promessa de previsão que os dados não sustentaram.
