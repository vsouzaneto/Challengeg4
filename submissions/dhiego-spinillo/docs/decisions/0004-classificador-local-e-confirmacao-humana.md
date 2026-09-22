# ADR 0004 — Classificação local; confirmação humana

**Status:** vigente no protótipo. **Data:** 21/09/2026.

## Contexto

Dhiego solicitou comparar Jev com classificador simples e avançar para concluir o case hoje. A escolha precisava apoiar-se no D2, preservando a fronteira entre inferência, regra e ação humana. [Comparação](../../solution/comparacao.md).

## Decisão

Usar TF-IDF + regressão logística treinada no D2 para sugerir uma categoria. O mesmo teste de 800 tickets produziu 86,00% de acurácia local contra 45,25% Jev zero-shot. A diferença permanece na sensibilidade sem os textos próximos internos ao teste. Não afirmar superioridade geral sobre Jev: o acesso a rótulos de treino difere.

Todos os encaminhamentos exigem humano. A seleção por score não manteve a meta de erro ≤5% no teste (44/658 erros). O mapa de filas é demonstrativo; não representa estrutura fornecida pela empresa. A confirmação de domínio vem do operador, não de um detector validado. Nenhuma categoria autoriza reembolso, cancelamento ou concessão de acesso.

## Alternativas consideradas

- **Jev como classificador principal:** não escolhido sob a configuração avaliada. Rapidez e baixo custo de API não compensaram o erro contra os rótulos do D2.
- **Classificador local com encaminhamento automático acima do limiar:** rejeitado porque o objetivo de erro não se manteve no teste; não ajustar limiar retrospectivamente para parecer aprovado.
- **LLM para todo o fluxo:** rejeitado; interpretação não substitui política, registro, cálculo ou autorização.
- **Classificação com confirmação e motivo:** escolhida, com registros exportáveis para revisão posterior. Não há retreino automático a partir das correções.

Recap tem tarefa e avaliação próprias e permanece assistivo/experimental. Acurácia de categoria não é métrica de qualidade de resumo.
