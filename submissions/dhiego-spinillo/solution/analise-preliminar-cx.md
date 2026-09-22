# Análise preliminar — urgência, atrito e qualidade do atendimento

**15/09/2026 · fase de análise, sem escolha final de solução.**

Esta exploração responde às provocações de Dhiego: urgência não é sinônimo de criticidade; uma mesma pessoa pode acumular experiências ruins; respostas superficiais ou incompletas geram novas interações. Fonte: leitura integral dos CSVs, contagens reproduzíveis e inspeção textual delimitada. [Resultados](reports/exploracao-cx.json) · [Script](explorar_cx.py) · [Como reproduzir](REPRODUZIR.md).

## Leitura executiva

Há sinais textuais que mereceriam investigação numa operação: pedido urgente com prioridade baixa, declaração de múltiplos contatos e grande volume em espera pelo cliente. Mas a base apresenta texto padronizado, identidade inconsistente e resoluções pouco plausíveis. Os sinais ajudam a formular perguntas; não comprovam que a empresa do cenário cometeu essas falhas.

A interpretação preliminar é que o diagnóstico precisa distinguir três problemas: **reconhecer a necessidade e o prazo, preservar o histórico/contexto e acompanhar a resolução efetiva**. Só classificar assunto não cobre os três. A escolha do recorte permanece em discussão.

## 1. Urgência pode estar escondida sob uma prioridade baixa

**Observado:** 165 descrições contêm literalmente `urgently`. Destas, 39 estão em Low e 39 em Medium: **78/165, ou 47,3%**. As outras são High (47) e Critical (40). No ticket 68, a prioridade é Low e o trecho diz: “I need them urgently”, referindo-se à recuperação de arquivos apagados.

**Leitura operacional:** o exemplo de uma obrigação com vencimento hoje, trazido por Dhiego, mostra por que tamanho/impacto e prazo para agir precisam ser distintos. Um pedido simples pode perder todo o valor se respondido depois do prazo.

**Limite:** não sabemos o critério usado para `Ticket Priority`, o prazo real, o momento do pedido ou a resposta dada. O padrão sobre recuperar arquivos se repete nas descrições. A contagem não mede quantos clientes reais urgentes foram mal atendidos e não justifica elevar prioridade por palavra-chave.

**Inspeção de ruído:** `today` aparece em 18 descrições; um dos primeiros exemplos se refere a anúncio de produto, outro ao dia de compra. `deadline` aparece em quatro, com trechos como doação e prazo de compra. Essas ocorrências não equivalem automaticamente a prazo de atendimento. A análise inspecionou os cinco primeiros exemplos de `urgently` e `today` e todos os quatro de `deadline`; não rotulou manualmente todo o lote.

**Dados para aprofundar:** prazo solicitado, prazo confirmado, impacto da demora, horário de entrada, fuso/calendário e compromisso do canal. O exemplo contábil é uma analogia operacional, não um caso observado nesta base de suporte de produtos.

## 2. Canais: existe diferença descritiva de notas, não diagnóstico de SLA

Convenção apenas exploratória: notas 1–2 são chamadas de baixas; isso não é definição oficial de CSAT do desafio.

| Canal | Tickets | Aguardando cliente | Notas disponíveis | Notas 1–2 / notas disponíveis | Média das notas |
|---|---:|---:|---:|---:|---:|
| Chat | 2.073 | 714 (34,4%) | 674 | 245/674 (36,4%) | 3,083 |
| Email | 2.143 | 722 (33,7%) | 720 | 303/720 (42,1%) | 2,964 |
| Phone | 2.132 | 705 (33,1%) | 691 | 285/691 (41,2%) | 2,952 |
| Social media | 2.121 | 740 (34,9%) | 684 | 269/684 (39,3%) | 2,969 |

**Leitura operacional:** email tem maior proporção de notas baixas entre os avaliados; chat, menor. Isso sugere uma pergunta para amostragem de casos, não a conclusão de que o email é o gargalo. A diferença entre maior e menor média é aproximadamente 0,13 ponto; a associação descritiva entre canal e satisfação explica cerca de 0,14% da variação observada, conforme a auditoria inicial.

**Limites:** não há duração confiável nem política de SLA por canal. Só 2.769 de 8.469 tickets têm nota e todos estão fechados. A base não traz coluna específica de WhatsApp; não presumir que `Social media` representa esse canal. Uma distribuição quase equilibrada entre canais, prioridades e estados, somada aos problemas textuais, reforça a cautela sobre realismo, sem provar sozinha um mecanismo de geração.

**Pergunta a investigar numa operação real:** o prazo prometido e esperado difere por canal, mas os fluxos respeitam essa diferença? Precisaríamos medir atraso contra o compromisso aplicável ao ticket, não comparar apenas médias brutas entre canais.

## 3. Repetição de contato: existe declaração de atrito, mas falta identidade confiável

**Observado no texto:** 460 descrições dizem que o cliente já contatou o suporte várias vezes e o problema permanece sem solução. Destas, 245 estão em Low/Medium. Há 152 tickets avaliados nesse grupo: 70 têm nota 1–2 (**46,1%**), contra 1.032/2.617 (**39,4%**) entre os avaliados sem essa frase.

**Leitura:** a direção da diferença é coerente com a hipótese trazida por Dhiego — contatos repetidos podem acompanhar uma experiência pior. É uma associação exploratória em texto repetitivo, com grupo pequeno e seleção de tickets fechados; não prova causalidade, recorrência real ou churn. Não elevar essa comparação a achado operacional validado.

**Verificação da identidade:** há 8.320 emails distintos em 8.469 linhas. Os 139 emails repetidos abrangem 288 registros. Em todos os 139 grupos há nomes diferentes; em 134, idades diferentes; em 95, gêneros diferentes. Não exportamos os dados pessoais para os resultados.

**Consequência:** não podemos construir uma jornada individual apenas agrupando por email. Pode haver dado inconsistente ou endereço compartilhado; falta identidade de conta/pessoa reconciliada. Também falta abertura confiável para ordenar a sequência. Frase de contato repetido é relato presente no texto, não confirmação por histórico.

**Dados para aprofundar:** identificador estável de cliente/conta, histórico ligado, reaberturas, causa, transferências, responsável e eventos com horário. Uma relação com churn exigiria desfecho e horizonte de observação que não existem aqui.

## 4. Aguardando cliente: possível área de retrabalho, não culpa comprovada

**Observado:** 2.881 tickets (**34,0%** da base) estão em `Pending Customer Response`. Esse estado representa de 33,1% a 34,9% dos tickets de cada canal.

**Hipóteses concorrentes:** o atendente pode estar aguardando uma informação indispensável; pode ter pedido novamente informação já enviada; pode ter enviado uma resposta que não resolveu o pedido; o cliente pode ter abandonado a interação. O arquivo não distingue essas situações.

**Limite:** uma fotografia do status não mede duração, número de idas e voltas nem responsabilidade pela espera. Não chamar esses 2.881 casos de tempo desperdiçado ou falha do cliente/atendente.

**Dados para aprofundar:** motivo da pendência, item solicitado, mensagens anteriores, início/fim da espera e quantidade de ciclos. Verificar se uma informação pedida já estava disponível exige acesso à conversa.

## 5. Respostas incompletas: a pergunta é importante, mas a coluna Resolution não sustenta a avaliação

**Observado:** as 2.769 resoluções preenchidas têm **3 a 8 palavras**, com mediana de **5**. Em amostra aleatória reprodutível de 20 registros (seed 42), a leitura de Codex encontrou frases sem sentido claro de atendimento, como a resolução do ticket 8027: “Fight strategy green at.” A amostra está no JSON para inspeção.

**Interpretação:** comprimento curto sozinho não prova resposta ruim. A combinação de frases pouco plausíveis, placeholders em todas as descrições e ausência de diálogo impõe uma limitação de qualidade do arquivo. Não é evidência de que atendentes reais tenham respondido assim.

Para verificar o caso “perguntou três coisas, recebeu duas respostas”, precisaríamos extrair os itens pedidos e ligar cada um a uma resposta, esclarecimento ou ação pendente. Isso exige mensagens e sequência, não apenas uma nota final chamada Resolution. Sentimento também precisa distinguir a fala do cliente de trechos de agente: a busca por `frustrat` encontra oito descrições, incluindo uma frase de desculpas que não comprova sentimento do cliente.

**Consequência para a proposta:** não usar essas resoluções como respostas aprovadas num mecanismo de busca/geração. Preservar cobertura de perguntas e qualidade de resposta como hipótese de evolução dependente de conversas reais e avaliação humana.

## 6. O que o Dataset 2 pode provar

Os 47.837 registros têm apenas `Document` e `Topic_group`, com oito categorias. Há base para testar classificação; não para validar prazo, prioridade, percurso de atendimento, sentimento ou risco de churn. Os exemplos inspecionados têm texto processado, com perda de contexto e forma original.

**Aprofundamento posterior:** foram encontrados indícios de cadeias de email concatenadas dentro de alguns documentos. Isso permite investigar uma síntese limitada ao texto disponível, sem tratar cronologia e autoria como conhecidas. Ver [exemplos para recap](contexto-e-recap.md).

O maior grupo, Hardware, contém 13.617 registros (28,47%); prever sempre essa classe é uma referência mínima. Access e Administrative rights são grupos distintos, úteis para discutir que identificar um pedido de acesso não autoriza sua execução. Nenhum classificador foi treinado nesta fase.

## O que podemos dizer ao diretor neste momento

“O arquivo contém indícios que justificam investigar reconhecimento de urgência, repetição de contato e o que leva um caso a aguardar o cliente. Ainda não consigo atribuir horas perdidas ou apontar um canal como causa: faltam eventos confiáveis e a representação das conversas tem problemas. Podemos testar uma intervenção delimitada, explicando quais resultados ela consegue demonstrar e quais perguntas exigem instrumentação.”

## Próxima discussão

Antes de escolher tecnologia, discutir com Dhiego: como distinguir **pedido com prazo curto**, **alto impacto** e **cliente atritado** na entrada? São dimensões diferentes e podem exigir respostas diferentes. As extensões avançadas continuam propostas futuras; estes achados não ampliam automaticamente o escopo.
