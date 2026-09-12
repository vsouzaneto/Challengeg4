# ADR 0001 — Política de verdade analítica

## Contexto

O dataset RavenStack apresenta definições concorrentes de churn e relações temporais incompatíveis. `accounts.churn_flag`, `churn_events` e o encerramento de assinaturas não reconciliam entre si. As contas também possuem assinaturas abertas simultâneas sem uma dimensão de produto que explique a sobreposição.

Uma única taxa de churn ou soma de MRR esconderia essas divergências e produziria precisão aparente.

## Decisão

1. Tratar `accounts.churn_flag` apenas como snapshot declarado.
2. Tratar `churn_events` como ledger histórico separado.
3. Tratar `subscriptions` como fonte de receita no grão da assinatura.
4. Publicar receita por conta apenas como cenário ou intervalo rotulado como proxy.
5. Preservar registros inválidos em quarentena; não corrigir datas, status ou valores com imputações inventadas.
6. Exibir, para cada métrica, universo, cobertura e estado de confiabilidade.
7. Usar linguagem de associação, não de causalidade.
8. Entregar inicialmente um índice de triagem explicável; só publicar probabilidade de churn se houver label temporal confiável e validação fora da amostra.
9. Tratar impacto financeiro como simulação até existirem custo da intervenção e efeito incremental medido.

## Alternativas rejeitadas

- **Usar apenas `accounts.churn_flag`:** ignora centenas de eventos históricos conflitantes.
- **Usar apenas `churn_events`:** confunde evento histórico com estado atual e não identifica a assinatura encerrada.
- **Somar todas as assinaturas abertas:** pode multiplicar artificialmente o MRR por conta.
- **Descartar toda conta com qualquer inconsistência:** destrói a amostra e oculta a qualidade real da fonte.
- **Imputar datas ou status prováveis:** cria fatos que a fonte não contém.
- **Treinar imediatamente um classificador:** produziria performance aparente sobre um target incoerente.

## Consequências

- Algumas métricas esperadas, como logo churn mensal, GRR e NRR, podem permanecer indisponíveis como fatos.
- O relatório terá uma análise de qualidade e uma análise demonstrativa da parcela elegível.
- Cenários de receita terão premissas visíveis e análise de sensibilidade.
- O diferencial da submissão será a rastreabilidade do julgamento, não a quantidade de gráficos ou a falsa precisão.

## Status

Aceita pelo autor da submissão em 2026-09-12.

