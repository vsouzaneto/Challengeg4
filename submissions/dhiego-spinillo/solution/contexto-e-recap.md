# Compreensão e recap: exemplos nos próprios datasets

**15/09/2026 · análise exploratória; funcionalidade não implementada.**

Dhiego esclareceu que guias fiscais e confirmação cadastral eram exemplos de experiência anterior, não conteúdo das bases. Pediu exemplos dos próprios arquivos e propôs recap de conversas e, eventualmente, uma ou duas sugestões de resposta com revisão do atendente. Envio automático continua fora do escopo.

[Extrator reproduzível](inspecionar_contexto.py) · [Exemplos e perfis de comprimento](reports/contexto-e-recap.json).

## 1. O que existe de histórico

**D1:** descrições entre 21 e 63 palavras (mediana 49). Não há lista de interações com autor/horário. Os placeholders e trechos pouco plausíveis continuam limitando o uso.

**D2:** texto mediano de 26 palavras, máximo de 981; 4.133 registros têm pelo menos 100 palavras, 1.104 têm pelo menos 200 e 99 têm pelo menos 500. Comprimento não equivale a número de mensagens. Entretanto, inspeção de registros selecionados identificou encadeamentos com `re`, saudações e referências a respostas, confirmações e datas dentro de um único `Document`.

**Refinamento da análise anterior:** não há histórico estruturado de eventos/mensagens, mas há indícios de conversas concatenadas em alguns documentos. Portanto, podemos investigar recap desses trechos. Não podemos reconstruir automaticamente autores, cronologia exata ou estado final como se estivessem garantidos pelo arquivo.

As posições de D2 abaixo começam em 1, sem o cabeçalho, e se referem ao hash registrado. Não são IDs de ticket fornecidos pelo dataset.

## 2. Exemplo: evitar pedir o que já foi informado

**D1, ticket 7.** O texto relata erro `Invalid Credentials`, afirma uso das credenciais corretas e pede recuperar acesso à conta. O campo Subject é `Refund request`, enquanto Type é `Product inquiry`; a leitura deve considerar a inconsistência dos metadados. Há ainda um trecho genérico sobre encontrar uma opção, que não deve ser inventado como intenção específica.

- **Fato textual:** erro informado e tentativa de acesso sem sucesso; correção das credenciais é uma afirmação do cliente, não uma verificação do sistema.
- **Informação ausente no trecho:** conta/serviço e passos de recuperação já tentados. O campo de produto separado poderia ajudar, mas o placeholder enfraquece a ligação semântica da descrição.
- **Pergunta candidata para revisão:** confirmar o serviço/conta afetado e perguntar se já tentou recuperar o acesso, sem solicitar senha.
- **Erro a evitar:** perguntar novamente qual mensagem de erro apareceu ou responder sobre reembolso apenas porque esse é o Subject.

Essa leitura foi feita por Codex durante a análise; não é saída de um protótipo nem rótulo humano validado.

## 3. Exemplo: preservar tentativas anteriores

**D2, registro 9.766, Hardware, 32 palavras.** O usuário relata falta de memória, erros e desligamentos; o documento também menciona que arquivou e apagou itens, sem resolver adequadamente.

- **Pedido aparente:** ajuda para voltar a utilizar o notebook normalmente.
- **Já informado/tentado:** erros/desligamentos e tentativa de liberar espaço arquivando/apagando itens.
- **Ambiguidade:** o texto não permite distinguir com segurança falta de armazenamento de falta de memória RAM.
- **Pergunta candidata para revisão:** qual mensagem exata aparece e em qual situação o equipamento desliga?
- **Erro a evitar:** recomendar novamente apagar arquivos como se nenhuma tentativa tivesse ocorrido, ou diagnosticar automaticamente falta de RAM.

Há contexto útil para preparação do atendimento, mas não uma conversa longa completa neste exemplo.

## 4. Exemplo: distinguir aprovação, execução e confirmação

**D2, registro 2.982, Miscellaneous, 108 palavras.** O documento sobre extensão de conta/contrato contém trechos de pedido, aprovação de extensão até dezembro, referência a informação atualizada e pedido de confirmação.

**Recap candidato, redigido por Codex para discutir o formato:**

- **Assunto:** extensão de validade de conta/contrato.
- **Evidência disponível:** há referência a extensão aprovada até dezembro (`extension until december has approved`) e solicitação de atualização.
- **Ponto de atenção:** também há referência a atualização/confirmação; o texto concatenado não permite afirmar com segurança qual é a mensagem mais recente nem se o processo está concluído.
- **Próximo passo sugerido:** conferir a validade vigente e o registro mais recente antes de responder ou encerrar.

O recap deve manter a ambiguidade. Aprovação não é sinônimo de alteração executada, e alteração executada não é sinônimo de confirmação pelo cliente.

## 5. Exemplo mais longo: instruções, prazo e bloqueio misturados

**D2, registro 8.614, Hardware, 303 palavras.** Há instruções de atualização de atributos em planilha/sistema, referências a prazos, relato de erro ao modificar categorias e uma referência a mudanças anexadas. Os anexos não estão disponíveis.

Uma ajuda ao atendente poderia separar objetivo da solicitação, impedimento relatado, ações mencionadas e referências que precisam ser verificadas. Não deve afirmar o conteúdo do anexo nem concluir que o erro foi resolvido a partir de uma frase de agradecimento. O registro demonstra por que um texto longo pode demandar síntese, mas não valida a correção de qualquer resumo.

## 6. Hipótese de função assistida

Um recap útil ao atendente poderia apresentar:

1. O que o cliente quer.
2. Fatos e informações já fornecidos, com trechos de origem.
3. O que já foi tentado, respondido ou realizado — distinguindo afirmação de confirmação.
4. Pendências e ambiguidades, sem preencher o desconhecido.
5. Próximo passo sugerido, sujeito à revisão.

Separar **recap** (síntese do material disponível) de **sugestão de resposta** (rascunho a revisar). Sem enviar mensagem, alterar prioridade ou encerrar ticket automaticamente. Se a cronologia não for recuperável, apresentar resumo temático e declarar que a ordem não foi confirmada.

## 7. Dados e avaliação necessários

Para um recap de conversa completa: mensagens integrais, autor/papel, horário, anexos acessíveis quando necessários, ações executadas e estado atual. Nos exemplos do D2, usar apenas o texto disponível e explicitar lacunas.

Se essa função for escolhida para o protótipo, revisar uma amostra definida com critérios próprios: fidelidade aos trechos, distinção entre solicitado/aprovado/executado/confirmado, preservação de tentativas, cobertura de pedidos, lacunas explícitas e utilidade do próximo passo. Considerar textos curtos/longos e casos em que não é possível recapitular com segurança.

Os exemplos deste documento foram selecionados intencionalmente para exploração. Não são avaliação representativa nem devem virar, sozinhos, prova de desempenho. A acurácia de classificação não mede qualidade de recap. Inclusão dessa função, extensão do conjunto de revisão e stack continuam em discussão.
