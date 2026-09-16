# ADR 0002 — Flags, priorização e acompanhamento do cliente

**Data:** 15/09/2026
**Status:** decisão de escopo aceita — implementações futuras; desenho detalhado proposto.
**Origem:** nesta conversa, Dhiego relacionou sua experiência com churn e health score a sentimento, níveis N1/N2/N3, árvore de categorias, segmento do cliente, reincidência e acompanhamento próximo de clientes atritados. Este registro não afirma resultados históricos dessa experiência.

## Contexto

Encaminhar para uma fila não resolve, sozinho, a ordem de atendimento nem a continuidade do cuidado. A proposta deve distinguir assunto, responsável, prioridade, estado do relacionamento e permissão de ação, conforme o ADR 0001.

## Decisão de escopo

Após discutir as possibilidades, Dhiego definiu nesta conversa que estas extensões devem compor **Implementações futuras — propostas**, com levantamento de dados necessários para evoluir controles e análises. Não construir flags de sentimento, histórico N1/N2/N3, segmentação, reincidência, priorização contextual ou acompanhamento próximo no protótipo atual; tampouco construir seus cenários simulados. Isso substitui a sugestão anterior de demonstrar algumas dessas flags amanhã.

A entrega atual permanece centrada em classificação, política de encaminhamento, revisão/correção humana e avaliação. O documento `../implementacoes-futuras.md` relaciona cada evolução à decisão que apoia, às fontes necessárias e ao critério de validação.

## Desenho proposto para evolução futura

Representar sinais como flags com origem e evidência. Aplicar política explícita para sugerir prioridade e encaminhamento. Manter revisão humana quando faltarem dados ou houver inferência não validada. Nenhuma flag isolada estima probabilidade de churn.

| Dimensão | Como obter | Como usar e quais limites declarar |
|---|---|---|
| Categoria e subcategoria | Taxonomia definida; modelo sugere posição | D2 tem oito grupos, sem rótulos hierárquicos. Árvore adicional seria proposta, sem desempenho comprovado. |
| Sentimento expresso | Modelo propõe rótulo e trecho de evidência, sujeito a revisão | Separar tom da mensagem de urgência, impacto e risco de churn. Ausência de linguagem negativa não comprova cliente tranquilo. |
| Nível atual e trajetória N1/N2/N3 | Eventos reais de atribuição e escalonamento | Não inferir a passagem por níveis apenas pelo texto. Desconhecido permanece desconhecido. |
| Impacto e urgência | Campos estruturados e confirmação; extração textual como sugestão | Alegação do cliente e impacto confirmado precisam de estados distintos. |
| Segmento e compromisso de atendimento | Cadastro/CRM e contrato | Clusterização é agrupamento, não ranking automático de importância. Política comercial precisa definir o tratamento. |
| Reincidência e reabertura | Identidade confiável, histórico, janela temporal e regra do que conta como repetição | Similaridade textual isolada não prova reincidência do mesmo cliente. |
| Atrito acumulado / acompanhamento próximo | Histórico confirmado ou indicação humana com motivo | Criar estado operacional com responsável, próxima revisão e critério de saída; sem alegar predição de churn. |
| Tempo de espera e prazo de atendimento | Abertura, eventos e calendário aplicável | Não calcular esses indicadores com os timestamps inválidos do D1. |

## Política de prioridade a discutir

Começar com ordenação por critérios explícitos, sem inventar pesos de um score único:

1. Tratar impacto crítico confirmado e obrigações de atendimento conforme política declarada.
2. Considerar prazo aplicável, escalonamento sem resolução, reincidência confirmada e acompanhamento ativo.
3. Considerar segmento/contrato onde a política permitir; ser cliente menor não elimina impacto crítico.
4. Usar ordem de chegada entre casos equivalentes e uma regra de aumento de prioridade por espera para evitar adiamento indefinido.

Sentimento negativo é sinal para cuidado e revisão, não um atalho universal para o topo da fila. Entrada em acompanhamento próximo exige motivo e responsável; não interrompe o atendimento normal. Em caso de dados insuficientes, solicitar revisão e exibir a lacuna, sem converter ausência em zero.

## Representação mínima de uma flag

`tipo`, `valor`, `origem` (dado, regra, modelo ou humano), `evidencia`, `observado_em`, `estado_validacao` e, quando aplicável, `validade_ate`. Guardar versão da regra/modelo. Score de modelo, quando existente, não deve ser apresentado como certeza.

## Dados disponíveis e recorte do case

Inspeção dos cabeçalhos dos CSVs em 15/09/2026:

- D1 traz tipo, assunto, prioridade declarada, status, canal, texto e campos de cliente. Não traz trilha N1/N2/N3, contrato, segmento de negócio ou série de eventos de atendimento. A existência de nome/email não comprova um histórico longitudinal utilizável. Satisfação pós-atendimento não substitui sentimento disponível na entrada.
- D2 traz somente `Document` e `Topic_group`; não contém histórico de cliente, níveis, prioridade ou rótulos de sentimento. O texto disponível é processado e exige cautela para inferir tom.
- Não há base para afirmar redução de churn ou precisão de uma ordenação operacional completa usando esses arquivos.

**Condição para implementação futura:** obter e validar os dados pertinentes, definir a política com operação e escolher uma hipótese de valor. Cenários simulados podem apoiar essa discussão numa evolução posterior, mas não substituem validação operacional e não entram no escopo atual.

## Evidência e autoria

Dhiego introduziu as dimensões operacionais e a necessidade de ir além de FIFO. Codex estruturou a proposta de dados, política, limites e cenários. Dhiego decidiu manter essas dimensões como propostas futuras e levantar os dados necessários. Implementação e verificação permanecem futuras; não apresentar nenhuma como concluída. Registrar a decisão de limitar o escopo no process log.
