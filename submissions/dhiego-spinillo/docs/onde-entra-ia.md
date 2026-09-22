# Onde entra IA — e onde não entra

Esta solução usa IA como apoio de leitura, não como autoridade operacional. A escolha é deliberada: texto varia e exige interpretação; identidade, elegibilidade, risco e execução precisam de fonte verificável, política explícita e trilha de auditoria.

## Mapa de decisões

| Momento | Mecanismo | Por que esta escolha | Limite / quem decide |
|---|---|---|---|
| Sugerir categoria em `/classificador` | Modelo local TF-IDF + regressão logística, treinado nos rótulos do D2 | No teste reservado, 86% de concordância, contra 45,25% do Jev com definições sem treino específico. Modelo incluído permite uso local, rápido e sem custo por chamada. | O rótulo é sugestão. No teste, o limiar de 0,61 deixou 44 divergências em 658 sugestões acima do limiar. Atendente confirma/corrige; categoria nunca libera uma ação. |
| Interpretar intenção, tentativa, risco, temperatura e menção de prazo em `/fluxos` | LLM opcional, contrato JSON estrito e citações literais validadas no texto | Há muitas formas de pedir recuperação, relatar tentativa, demonstrar atrito ou indicar uma data. O modelo transforma texto aberto em sinais conferíveis pelo atendente. | Não infere identidade, estado, causa, prioridade, SLA ou resolução. Uma menção pode pertencer a email encaminhado; falha de IA retorna a regras lexicais e impede autonomia quando a política exige extração válida. Os sete cenários são desenvolvimento, não benchmark independente. |
| Detectar bloqueios adicionais | Regras lexicais determinísticas | Um bloqueio identificável não deve desaparecer porque o LLM omitiu ou interpretou de outro modo. | Busca literal é limitada e explicitamente exibida na interface. Ausência de sinal não prova ausência de risco. |
| Consultar identidade, outros tickets/notas e estado | Adaptadores locais fictícios na demonstração; em produção seriam integrações somente leitura | Esses fatos precisam vir do sistema de origem, não de interpretação do modelo. | Contas, notas e sistemas desta demo são fictícios. Não há integração de produção. |
| Escolher caminho, emitir token e concluir procedimento | Política e máquina de estados determinísticas | Recuperação, restrição cadastral, fonte indisponível, uso único, expiração e falha exigem comportamento repetível e auditável. | A demo não altera senha, conta ou canal real. Cliente escolhe iniciar; exceções chegam ao humano. |
| Preparar resposta | Texto por regra, editável e aprovado por humano | A resposta deve refletir fato de fonte consultada e não afirmar diagnóstico que não existe. | Não há envio externo. Não usamos geração livre: o recap experimental teve fidelidade aprovada em 6 de 15 saídas pelo revisor automatizado. |
| Investigar possível incidente | Humano, com evidências preservadas | “Dados de outra pessoa” pode ser incidente, preenchimento, cache ou interpretação. É necessário investigar, não completar lacunas com IA. | A solução mantém caso aberto e encaminha à equipe responsável; não presume causa ou resolução. |

## Sinais que entram como apoio, não como decisão

| Sinal apresentado | Mecanismo e evidência | Limite |
|---|---|---|
| Temperatura / possível atrito | IA opcional ou regra lexical apresenta somente expressão literal de frustração, insatisfação ou irritação. Ausência de expressão resulta em `unknown`, jamais em “cliente tranquilo”. | Não gera nota de sentimento, prioridade ou ação. O atendente confirma o contexto e o pedido ainda pendente. |
| Prazo / possível urgência | IA opcional ou regra lexical mostra palavras e datas explícitas como `urgent`, `today` ou `deadline`. | Não prova urgência operacional: pode ser trecho histórico, e urgência depende de impacto, prazo aplicável e contexto. Não muda a fila automaticamente. |
| Estado de SLA | A interface torna explícito que o relógio não está disponível na demonstração. | Não há cálculo de atraso, cumprimento ou horas perdidas sem abertura, política de prazo, primeira resposta e eventos de trabalho. |

## O que não foi colocado em IA ou automação decisória

| Decisão fora do escopo | Motivo |
|---|---|
| Nota de sentimento, prioridade automática ou risco de churn | O D2 não possui rótulo de referência para sentimento e não há histórico/identidade confiável para recorrência ou churn. Sinal textual de atrito não é diagnóstico de satisfação nem motivo suficiente para reordenar a fila. |
| SLA, atraso e horas desperdiçadas | O D1 não tem abertura e 49,3% dos pares temporais disponíveis estão invertidos. Corrigir o sinal não recupera uma duração válida. |
| Resposta automática ao cliente | Risco de omitir pedido, afirmar algo não confirmado ou responder fora de contexto. O escopo do protótipo é preparar e registrar uma resposta revisável. |
| Alteração cadastral, concessão de acesso ou reset de conta real | Risco de segurança e necessidade de autenticação/integração real. O fluxo demonstra apenas o contrato e a trilha do procedimento em provedor fictício. |
| LLM sobre todos os 47.837 textos | Sem referência humana para intenção/tentativa/risco, a rodada não produziria avaliação válida. Também acrescentaria custo variável. A classificação integral usa o modelo local congelado; seu resultado não é convertido em elegibilidade ou saving. |

## Como explicar em uma frase

**“Usei IA onde ela interpreta linguagem; usei regras e sistemas onde é preciso provar um fato ou controlar uma ação; deixei o humano decidir onde há risco, ambiguidade ou impacto no cliente.”**

## Próxima validação necessária

Antes de ampliar a extração por IA, separar uma amostra nova antes das respostas e obter revisão humana para intenção, tentativas, risco e cobertura dos pedidos. Antes de automatizar qualquer ação real, integrar fontes confiáveis, autenticar o usuário e medir erro, recontato e trabalho ativo por procedimento. Nenhuma dessas provas é substituída por score de categoria, citação literal ou cenário de demonstração.
