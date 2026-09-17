# Support Intelligence — documentação de produto

Status: núcleo demonstrável implementado e validado localmente; checkpoints P0 de qualidade, validação humana e controles para exposição pública permanecem abertos onde ainda não há evidência. Escopo: um sistema de Inteligência de Suporte, observado por seis lentes. Todos os arquivos desta entrega permanecem em `submissions/rafael-reis/solution/`.

## Ordem de leitura

1. [Arquitetura e contratos compartilhados](01-arquitetura-compartilhada.md).
2. [Plano de implementação — sprints e fases F00–F40](02-plano-de-implementacao.md).
3. [Dados, limitações e métricas](03-dados-e-metricas.md).
4. [Design G4 e experiência integrada](04-design-e-experiencia.md).
5. [Validação, demo e process log](05-validacao-demo-processo.md).
6. [Resultados técnicos medidos](06-resultados-tecnicos.md).
7. [Operação e deploy](07-operacao-e-deploy.md).
8. [Auditoria final de implementação](08-auditoria-final.md).

Índice do [process log](../../process-log/README.md), exigido pelo guia de submissão.

## Porta de entrada

[O Início](../frontend/src/views/start.ts) é uma rota de onboarding, não uma sétima lente. Ela explica os dois corpora, o significado dos estados e o roteiro recomendado para percorrer as seis lentes sem misturar histórico, simulação e hipótese.

| Lente | Pergunta | Spec |
|---|---|---|
| O Início | Como percorrer o sistema e explicar seus limites? | [00](specs/00-o-inicio.md) |
| Operational Diagnosis | Onde estamos perdendo tempo e o que os dados permitem concluir? | [01](specs/01-operational-diagnosis.md) |
| AI Automation Strategy | O que automatizar e quando exigir um humano? | [02](specs/02-ai-automation-strategy.md) |
| AI Ticket Lab | O modelo entende um novo ticket? | [03](specs/03-ai-ticket-lab.md) |
| AI Copilot | Que evidência histórica ajuda o agente? | [04](specs/04-ai-copilot.md) |
| Support Intelligence Graph | Como tickets, grupos e decisões se relacionam? | [05](specs/05-support-intelligence-graph.md) |
| Support Command Center | O que acontece na sessão e no sistema de IA? | [06](specs/06-support-command-center.md) |

## Decisões que orientam todas as entregas

- Um catálogo de tickets, um serviço de inferência, um contrato de métricas e uma sessão compartilhada. Cada rota consulta esses mesmos recursos.
- Arquivos disponíveis: DS1 com **8.469** registros e DS2 com **47.837**; o total de 56.306 não representa uma base ligada por IDs.
- DS1 não possui data de abertura; campos de resposta/resolução são timestamps inconsistentes. TTR/FRT ficam indisponíveis até existir evidência suficiente. Não usar data da compra como abertura.
- DS2 oferece texto e categoria; não oferece resolução, prioridade, canal ou CSAT. Não transferir esses atributos do DS1 por semelhança.
- Classificação, busca e conexões vêm de artefatos reais. Roteamento e prioridade sem rótulo de treino são políticas explícitas, versionadas e auditáveis.
- Replay usa conteúdo dos arquivos com horário simulado. ROI é cenário parametrizado. Ausência de evidência aparece como indisponibilidade, nunca como zero.
- O Design System G4 orienta um único shell. O grafo tem significado e alternativa tabular; animações são opcionais.
- CSVs e assets originais permanecem imutáveis. Reset inicia outra sessão, preservando a anterior.

## Prioridades

**P0 — núcleo demonstrável:** diagnóstico honesto, estratégia fundamentada, classificador real, recuperação real, grafo semântico hierárquico, sessão/replay, observabilidade e navegação contextual. Deve funcionar sem serviço externo de LLM.

**P1 — aprofundamento:** análise estatística mais extensa, avaliação humana de duplicatas/recuperação, subclusters onde sustentados, políticas calibradas para automação e cenários de incidentes avaliados.

**P2 — evolução:** integração de produção, múltiplos operadores, LLM externo opcional, drift com metodologia, retreino governado. Não necessários para apresentar o núcleo.

Checklists de implementação usam `[ ]` enquanto pendentes; `[x]` exige artefato e evidência de verificação. A auditoria final registra o motivo das lacunas abertas.
