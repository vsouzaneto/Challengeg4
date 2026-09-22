# ADR 0007 — Autonomia por procedimento e cenários econômicos

Data: 21/09/2026. Status: direção proposta; calculadora implementada, autosserviço e integrações pendentes.

## Contexto

Dhiego questionou o valor de uma ferramenta em que tudo depende de clicar e validar. Propôs três velocidades: resolver sozinho, entregar praticamente pronto e reservar decisões humanas. Também solicitou ROI com premissas salariais e econômicas, e sugeriu capturas como evidência em vez de depender de publicação na VPS.

## Decisão

Projetar autonomia por procedimento. Classificação identifica assunto; não autoriza ação. Manter revisão no classificador avaliado, cujo limiar não atingiu a meta de erro, sem estender essa limitação a todo autosserviço determinístico. Priorizar recuperação de senha como candidato delimitado; distinguir falhas técnicas de pedido simples. IA interpreta/extrai/recupera; regras e sistemas responsáveis autorizam e executam. Rotas ainda não implementadas ficam identificadas como proposta.

O caminho intermediário deve consultar contexto por integrações, preparando o trabalho e reduzindo conferências manuais. Incidentes/ambiguidade exigem investigação humana com evidências, sem diagnóstico inventado. Sentimento será sinal auxiliar após referência humana e avaliação, não regra isolada de prioridade.

Estimar capacidade e economia separadamente, com premissas editáveis, custos completos, possibilidade de resultado negativo e mecanismo explícito de despesa evitada. Não usar acurácia ou menções no D2 como taxa automatizável. Capturar evidências reais do app e manter reprodução local; nenhuma publicação externa foi realizada nesta decisão.

## Consequências

O case passa a mostrar onde investir e como decidir se vale o custo, além da prova técnica existente. Fluxos autônomos exigem implementação/validação próprias. Uma simulação futura deve dizer o que é simulado e não será prova de integração real nem de saving. [Mapa dos caminhos](../tres-velocidades.md) · [Economics](../economics.md).
