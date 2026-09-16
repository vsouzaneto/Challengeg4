# ADR 0001 — Fronteira entre regras de negócio e inferência por IA

**Data:** 15/09/2026
**Status:** princípio definido por Dhiego; implementação pendente.
**Origem:** nesta conversa, Dhiego destacou a tentação de aplicar IA em tudo e pediu que a solução explicite o que deve ser determinístico. Relacionou o princípio à sua experiência com o painel dos gestores e a um artigo que publicou no LinkedIn. O artigo não foi consultado neste registro.

## Contexto

O protótipo precisa mostrar uma intervenção útil e verificável na triagem. Classificar texto, calcular impacto, determinar responsabilidade e autorizar uma ação são tarefas distintas. Acrescentar um LLM não estabelece, por si só, benefício operacional.

## Decisão

Usar regras e cálculos explícitos para fatos estruturados, métricas, política de encaminhamento, permissões e registros. Avaliar modelos para interpretar texto onde regras simples não forem suficientes. Reservar ao humano decisões sem política definida, exceções e correções.

| Responsabilidade | Mecanismo proposto | Limite |
|---|---|---|
| Contagens, denominadores, métricas de avaliação e cenários de capacidade | Código determinístico, com fórmulas e fontes | Cálculo correto não corrige dado inválido nem torna hipótese uma observação. |
| Inferir categoria do texto | Comparação entre regras simples e classificador aprendido | Resultado é uma previsão; exige avaliação fora do treino. |
| Mapear categoria elegível para fila responsável | Configuração explícita e versionada | Filas demonstrativas identificadas; ausência de mapeamento leva à revisão. |
| Decidir se pode encaminhar automaticamente | Política em código: escopo validado, dados necessários, limiar validado, fila configurada e ação permitida | Score alto não comprova domínio, autorização nem ausência de risco. |
| Justificar encaminhamento ou retenção | Código do motivo e mensagem derivados da regra executada | LLM não inventa justificativa retrospectiva. |
| Resumir pedido ou sugerir esclarecimento | LLM opcional, avaliado separadamente e sujeito a revisão | Não inventar campos ausentes; não usar sugestão como autoridade para executar. |
| Corrigir destino ou decidir exceção | Humano com registro de motivo | Correção não implica retreino ou mudança automática da política. |
| Executar reembolso, cancelar ou conceder privilégios | Fora do escopo de execução do case | Reconhecer e encaminhar um pedido não autoriza sua execução. |

O domínio suportado deve ser declarado; se houver detector de domínio, sua eficácia precisa ser avaliada. A própria elegibilidade não pode depender apenas de uma declaração de confiança do modelo.

## Alternativas consideradas

- **LLM decidindo todo o fluxo:** não adotado; mistura inferência textual com regras, métricas e autoridade.
- **Somente regras para todo texto:** hipótese de comparação, sem assumir que terá cobertura suficiente.
- **Classificação avaliada + política explícita + humano nas exceções:** direção adotada; detalhes e limites dependem da avaliação.

## Consequências e critérios de verificação

- Mostrar na interface a previsão do modelo, a regra aplicada e a decisão humana como informações distintas.
- Registrar versões do modelo e da política, motivo e eventual correção.
- Verificar casos de fila ausente, score abaixo do limiar, ação fora do escopo e dado obrigatório ausente.
- Avaliar categoria e encaminhamento final separadamente: uma regra estável ainda pode operar sobre uma previsão errada.
- LLM permanece uma extensão proposta. Só incluir com tarefa, benefício esperado e avaliação definidos; falha da API não deve impedir consulta, regras ou revisão manual.
- Autoria: Dhiego definiu o princípio de produto nesta conversa; Codex organizou esta proposta de divisão de responsabilidades. Nenhuma implementação é afirmada como concluída.

## Esclarecimento — análise pronta e recap dinâmico

Na análise visual v1, os números vêm de relatórios reproduzíveis e os recaps são exemplos preparados por Codex, identificados como leitura exploratória. Se recap entrar no protótipo, a inferência deverá receber o texto selecionado e produzir uma saída vinculada à entrada. Exemplos fixos não demonstram essa capacidade.

A IA pode apoiar compreensão antes da redação: pedido, tentativas já relatadas, dúvidas e próximo passo sugerido. Sugestões de resposta são uma função separada, dependente de contexto suficiente e revisão humana; não haverá envio automático. Fidelidade ao texto, cobertura dos pedidos e preservação de incertezas precisam de avaliação própria. A escolha de implementar essas funções permanece aberta.
