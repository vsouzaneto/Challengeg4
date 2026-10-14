# Proposta de automação

Números de `solution/analise/03_proposta.py`. Contagens completas no anexo de `docs/auditoria-dados.md`.

## Regra mestra

A IA só responde o que existe no banco de respostas validadas. O que não existe vai para um humano validar uma vez; a resposta validada entra no banco e, da próxima vez, sai automática. A IA nunca inventa. "Confiança baixa" significa "não bate com nada do banco".

Mesmo com resposta no banco, alguns tickets ficam com humano por autoridade, não por falta de resposta: reembolso tem resposta conhecida, mas quem aprova é gente.

Este é o desenho do produto de atendente de IA do Jessé, não resultado medido em escala. As três camadas saem da regra:

| Camada | Quando |
|---|---|
| Humano decide | Portão de autoridade, com ou sem resposta no banco |
| Autoatendimento com portão | Resposta existe no banco e o ticket não cai em portão |
| Confirmação humana | Não bate com o banco, ou o classificador diverge da escolha do cliente; a validação alimenta o banco |

## Fluxo

0. **Entrada estruturada:** o cliente escolhe o tipo num menu e preenche 2 ou 3 campos obrigatórios; o texto livre é complemento.
1. **Classificador confere:** roda no texto livre, sem assinatura; se divergir da escolha do cliente, vai para humano.
2. **Banco de respostas decide:** se existe resposta validada e não há portão, ela sai.
3. **Humano valida o que falta:** o que não bate com o banco é validado uma vez e entra no banco.
4. **Resposta ou roteamento:** portão de autoridade vai para a fila de quem tem alçada, com a sugestão da IA.
5. **Lembrete de cliente parado:** o pendente recebe lembrete e é encerrado por prazo, fora dos portões.
6. **Aprendizado:** resolução repetida com nota 4 ou 5 no mesmo assunto vira resposta sugerida; nota 1 ou 2 vai para revisão.

Roda no helpdesk atual via API ou com um orquestrador; nada aqui depende de ferramenta específica.

## Portões de autoridade

| Portão | Exemplo no dataset 1 | Tickets |
|---|---|---|
| Reembolso | Ticket Type "Refund request" | 1.752 |
| Dúvida ou disputa de fatura | Ticket Type "Billing inquiry" e assunto "Payment issue" | 1.634 e 526 |
| Cancelamento | Ticket Type "Cancellation request" | 1.695 |
| Crítico | Ticket Priority "Critical" | 2.129 |
| Cliente já insatisfeito | Nota 1 ou 2 entre os 2.769 fechados | 1.102 |

**Crítico por regra operacional, não por escolha do cliente:** serviço fora, pagamento bloqueado, perda de dados confirmada. No dataset, Critical é 25,1% e não depende do tipo, sinal de que hoje é etiqueta.

**Acesso à conta e perda de dados não são portão.** São os tipos mais fáceis de padronizar: entrada estruturada (login; o que foi perdido e quando) e banco de respostas. Perda de dados confirmada vira crítico pela regra acima.

Somando os quatro primeiros portões, 75,3% dos tickets do dataset 1 cairiam em portão. Isso é efeito do sorteio uniforme do dataset, em que tipo, assunto e prioridade não dependem uns dos outros; o piloto mede a proporção real.

## Passo zero: padronizar a entrada antes de automatizar

Exemplos de campos obrigatórios: reembolso pede número do pedido, data e motivo escolhido numa lista; acesso pede login; perda de dados pede o que foi perdido e quando. No chat, menu de três opções e um campo.

Com o tipo escolhido pelo cliente, a triagem cai quase a zero nos tickets bem preenchidos e o classificador passa a conferir em vez de adivinhar. É também a forma mais barata de instrumentar a entrada, por isso entra na recomendação 1 do diagnóstico. Quando for implantado, o abandono do formulário vira contador.

Evidência de que o texto livre sozinho é entrada ruim: até 84,9% dos 47.837 textos do dataset 2 carregam resíduo de fecho ou ausência (teto: "thank" também aparece como cortesia no meio do pedido). Os termos: "thanks" ou "thank" em 66,8%, "regards" em 40,9%, "best" em 15,8%, "annual leave" em 2,2%. Foi uma assinatura com "annual leave" que puxou a triagem humana para RH num ticket de antivírus.

## Fase 1: piloto "Lembrete de cliente parado"

- **Canal:** só Email (25,3% dos tickets).
  - Chat não entra: pendente de chat é cliente que saiu do site. Isso se trata com régua de inatividade em minutos e resumo por e-mail, outra automação, em onda posterior.
- **Régua:** lembrete em 2 e 5 dias úteis. Encerramento em 7, com mensagem dizendo que responder reabre. Portões de autoridade nunca fecham sozinhos.
- **Contadores:** lembretes enviados, encerrados automaticamente, reabertos depois do encerramento.
- **Duração:** 8 semanas. **Parada:** reabertura acima de 20% suspende o encerramento; o lembrete continua.
- **Limitação declarada:** na escala de 30 mil/ano, Email tem cerca de 50 pendentes e 4 encerramentos por semana, ou cerca de 34 em 8 semanas. O contador de reabertura mostra direção, não taxa.

## Fase 2: triagem e roteamento

- **Entra em produção quando:** os campos da recomendação 1 estiverem instrumentados, a entrada estruturada estiver no ar e o limiar de confiança estiver calibrado com tickets reais da operação.
- **O protótipo do Bloco 4:** prova viabilidade técnica no dataset 2. Não é o piloto.
- **Parada:** pausa se menos de 60% dos tickets passarem do limiar de confiança, ou se humanos corrigirem a classificação em mais de 15% dos casos.

## Aprendizado e o quinto campo

A regra de aprendizado é a regra mestra aplicada no tempo, mas não dá para testar neste dataset. Os 2.769 textos de Resolution dos fechados são todos únicos, nenhum se repete no mesmo assunto, e a nota não tem relação com nada. Por isso a resolução ligada à nota vira o quinto campo a instrumentar.

## ROI da fase 1

Premissas do diagnóstico mais quatro novas:
- três são da IA, declaradas e não medidas: o lembrete substitui 50/70/90% das cobranças manuais; 50/35/20% dos pendentes elegíveis fecham por prazo; 20/10/5% dos encerrados reabrem;
- implantação de 40/30/20 h, do Jessé, pela experiência montando lembrete e encerramento automático.

Só fecham por prazo os 24,2% de pendentes fora dos portões.

| Resultado | Conservador | Base | Otimista |
|---|---|---|---|
| Líquido h/ano, todos os canais (recuperado menos retrabalho) | 97 | 1.161 | 4.855 |
| Líquido R$/ano, todos os canais | R$ 2,9 mil | R$ 58 mil | R$ 340 mil |
| Líquido R$/ano, só Email (piloto) | R$ 0,7 mil | R$ 14,7 mil | R$ 86 mil |
| Implantação | R$ 1,2 mil | R$ 1,5 mil | R$ 1,4 mil |
| Retorno da implantação, só o piloto | 19,6 meses | 1,2 mês | 0,2 mês |

O piloto se justifica como instrumentação, não só pelas horas. É a primeira medição real dos campos que o diagnóstico não conseguiu medir, e o retorno maior está na fase 2, que depende deles.
