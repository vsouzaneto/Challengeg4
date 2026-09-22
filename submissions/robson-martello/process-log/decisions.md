# Registro de decisões

| # | Hipótese / decisão | Evidência | Resultado | Decisão |
| ---: | --- | --- | --- | --- |
| 01 | Os dados permitem medir a resolução? | 16,6% dos intervalos temporais são válidos. | Insuficiente | Não otimizar a resolução. |
| 02 | Tipo, prioridade e canal explicam satisfação? | Os tamanhos de efeito observados foram próximos de zero. | Não | Não modelar satisfação. |
| 03 | Podemos estimar horas desperdiçadas? | Faltam acordo de nível de serviço, tempo de trabalho do agente e data de criação do ticket. | Não | Não estimar. |
| 04 | Um modelo consegue classificar tickets? | Regressão logística com TF-IDF alcançou 86,6% de acurácia. | Sim | Candidato a automação controlada. |
| 05 | A confiança permite automação seletiva? | Os 60% de casos com maior confiança atingiram 97,8% de acurácia. | Sim | Automatizar apenas essa faixa e revisar os demais casos. |
| 06 | Um modelo de linguagem melhora os casos difíceis? | Ficou abaixo da regressão logística. | Não | Remover da hipótese. |
| 07 | Jev melhora a decisão de prontidão? | 77,8% de acerto versus 100% das regras determinísticas. | Não | Remover da hipótese. |
| 08 | Devemos construir uma aplicação? | Nenhuma aplicação de IA superou uma referência mais simples. | Não | Não construir. |
