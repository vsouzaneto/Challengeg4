# Execução local para a entrega

**22/09/2026 — Docker em `http://127.0.0.1:8766`, sem VPS.** Capturas reais do navegador, conferidas visualmente; viewport 1920 × 903, imagens da página completa. A rodada foi executada por Codex para verificar e documentar o software, não representa validação humana do candidato nem atendimento real.

Nesta rodada, **Interpretar com IA foi desmarcado** e recap permaneceu desligado. Nenhuma chamada paga foi feita: o classificador local e as regras permitem reproduzir a demonstração sem credenciais. As [evidências anteriores com IA real e telas mobile](../fluxos-v1/README.md) e os [resultados arquivados da extração](../../../solution/reports/fluxos-desenvolvimento.json) continuam preservados. Não apresentar a rodada sem API como nova avaliação do LLM.

## O que observar

| Captura | Ação executada e resultado |
|---|---|
| [1. Autosserviço concluído](01-autosservico-concluido.png) | D2 1.083. Consultar contexto → solicitar recuperação → concluir no provedor fictício. Trilha registra token consumido e conclusão. |
| [2. Resposta editada e aprovada](02-resposta-editada-aprovada.png) | No mesmo caso, informar que não resolveu → transferir com histórico → editar rascunho → aprovar. Texto salvo permanece visível; sem envio externo. |
| [3. Investigação em aberto](03-investigacao-em-aberto.png) | D2 45.725. Identificar relato de dados de outra pessoa → assumir investigação. Caso continua não resolvido; nenhum reset ou causa presumida. |
| [4. Valor por processo](04-valor-por-processo.png) | Hipóteses padrão: 5,6 h no autosserviço e 66,67 h na preparação. Resultados financeiros dependem das premissas, não medem saving. |
| [5. Reset isolado negativo](05-reset-isolado-negativo.png) | Reduzir elegíveis à preparação a zero e recalcular. Saldo mensal −R$ 381; ROI −88,1%; sem recuperação do investimento. |
| [6. Classificação e comparação](06-classificador-e-comparacao.png) | Mesmo texto curto no classificador, domínio confirmado e recap desligado. Sugere Access com revisão humana. Comparação arquivada mostra Local 86% × Jev 45,25%. |
| [7. Resumo executivo](07-resumo-executivo.png) | Síntese visual do diagnóstico, intervenção, evidência e decisão de investimento. Os 204 testes citados são do aplicativo/cálculos; o lote integral acrescentou 12, totalizando 216. |
| [8. Matriz de decisões](08-matriz-ia-regras-humano.png) | Explicita por que IA interpreta texto, modelo local sugere categoria, regras liberam procedimento e humano responde/investiga. O bloco expansível registra o que ficou fora da IA por risco, dados ausentes, escopo ou custo. |

Os arquivos `.txt` ao lado das capturas 2, 3, 5 e 6 registram o conteúdo visível da página para facilitar conferência. A análise visual inicial está nas [evidências do diagnóstico](../visual-v1/README.md).

## Como repetir

1. Na pasta da submissão, executar `docker compose up --build` e abrir `http://127.0.0.1:8766`.
2. Se houver chave configurada, desmarcar **Interpretar com IA** para repetir esta rodada sem API. Seguir a sequência da tabela; estados ficam no volume SQLite local.
3. Abrir `/valor` e comparar o cenário padrão com preparação igual a zero. Acessar `/classificador` para a classificação e `/resumo` para a síntese.

Verificação adicional: **216 testes passaram localmente e no contêiner**, sem chamadas pagas. A [classificação dos 47.837 registros](../../../solution/reports/full-population/report.md) possui relatório e CSV próprios; estas capturas de poucos exemplos não substituem aquela avaliação.

Nenhum deploy, push ou PR foi realizado nesta etapa. Sistemas, contas e notas das demonstrações são fictícios; os textos vêm do dataset público.
