# ADR 0004 — Gate de parada e análise demonstrativa

## Contexto

A auditoria encontrou violações sistêmicas de temporalidade, conflito entre definições de churn e impossibilidade de reconciliar eventos de cancelamento com assinaturas e receita. Em um ambiente real, continuar a análise como se a camada de fatos fosse confiável ampliaria o risco de decisões erradas.

O desafio, porém, solicita um diagnóstico completo e permite uma análise educacional sobre dados sintéticos. É necessário separar a recomendação profissional da continuação demonstrativa.

## Decisão

1. A página de qualidade terminará com um gate executivo explícito recomendando interromper a análise naquele ponto.
2. A recomendação principal será concentrar esforços em identificar e corrigir a origem dos erros de instrumentação, implantar contratos de dados e reconstruir o histórico confiável antes de diagnosticar churn ou automatizar ações de retenção.
3. Se uma leitura de curto prazo for indispensável, a empresa deverá criar evidência fora da telemetria contaminada por meio de:
   - pesquisa de satisfação com clientes;
   - coleta estruturada de sugestões e pedidos de melhoria;
   - entrevistas com clientes ativos, churnados e reativados;
   - avaliação interna com Customer Success e Suporte;
   - revisão manual de uma amostra de contas de maior impacto.
4. O restante da aplicação será apresentado somente após esse callout e terá o rótulo permanente **análise demonstrativa da parcela recuperável**.
5. Métricas demonstrativas devem informar universo, cobertura, regra de elegibilidade e estado de confiança.
6. Nenhum achado demonstrativo poderá ser convertido em causalidade, receita reconciliada, probabilidade de churn ou ROI comprovado.

## Consequências

- O relatório responde ao desafio sem transformar a continuação analítica em recomendação profissional.
- O CEO recebe primeiro a decisão correta para uma empresa real e, em seguida, uma exploração transparente do que ainda pode ser aprendido.
- A fila de Customer Success operará em modo de triagem e validação humana, não como automação autônoma.
- O plano de ação priorizará correção na fonte, observabilidade e coleta direta de voz do cliente.

## Status

Aceita pelo autor da submissão em 2026-09-12.

