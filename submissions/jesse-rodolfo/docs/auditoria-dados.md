# Auditoria dos dados (Bloco 1)

Tudo abaixo saiu de `solution/analise/01_auditoria.py`, rodado nesta sessão com pandas 3.0.6 / scipy.
Reproduzir: `.venv/bin/python -I solution/analise/01_auditoria.py`

## Dataset 1: Customer Support Ticket Dataset (`customer_support_tickets.csv`)

- **Registros:** 8.469 linhas, 17 colunas. Não bate com os "30 mil por ano" do brief (28% disso), e não há data de abertura do ticket para anualizar.
- **Duplicados:** 0 linhas e 0 Ticket ID repetidos. 139 e-mails aparecem mais de uma vez, sempre com nomes diferentes (139 de 139): e-mail gerado aleatoriamente, não identifica cliente. Não dá para medir cliente recorrente.
- **Nulos:** só em 4 colunas, e seguem o status à risca:

| Status | n | First Response Time | Time to Resolution | CSAT | Resolution |
|---|---|---|---|---|---|
| Closed | 2.769 | 100% | 100% | 100% | 100% |
| Pending Customer Response | 2.881 | 100% | 0% | 0% | 0% |
| Open | 2.819 | 0% | 0% | 0% | 0% |

- **Campos de tempo: são carimbos de hora, não durações.** First Response Time e Time to Resolution são datetimes, todos entre 2023-05-31 21:53 e 2023-06-02 00:55 (janela de 27 horas). A compra é de 2020-01-01 a 2021-12-30. Não existe coluna de abertura do ticket, então tempo de primeira resposta e tempo de resolução **não são calculáveis**.
- **Tentativa de derivar duração:** Time to Resolution menos First Response Time, nos 2.769 Closed: mediana 0,17 h, mínimo -23,2 h, máximo +23,5 h. **1.365 de 2.769 (49%) resolvem antes da primeira resposta.** O campo é ruído uniforme em torno de zero, não serve como duração.
- **Satisfação (CSAT):** só existe nos 2.769 Closed. Distribuição plana de 1 a 5 (553 / 549 / 580 / 543 / 544). Média 2,96 a 3,08 em qualquer corte. Nenhuma variável explica a nota:

| Variável | chi2 p | Kruskal p |
|---|---|---|
| Prioridade | 0,400 | 0,629 |
| Canal | 0,467 | 0,278 |
| Tipo | 0,257 | 0,699 |
| Assunto | 0,876 | 0,807 |
| Produto | 0,253 | 0,667 |
| Gênero | 0,148 | 0,625 |

  Correlação de Spearman CSAT x "duração" derivada: 0,022. CSAT x idade: -0,004. O maior gap entre produtos (Fitbit Versa 2,54 vs Dyson 3,22, n entre 47 e 83) cabe no ruído (Kruskal p=0,667).
- **"Other" em Customer Gender:** é valor real da coluna (2.686 tickets, ao lado de Male 2.896 e Female 2.887), diferente do "outros" que a página do Kaggle mostra ao resumir colunas.
- **Categorias equilibradas demais:** 5 tipos entre 1.634 e 1.752; 4 prioridades entre 2.063 e 2.192; 4 canais entre 2.073 e 2.143; 3 status entre 2.769 e 2.881; 42 produtos entre 178 e 240. Prioridade não depende do tipo (chi2 p=0,561) nem do canal (p=0,078). Em operação real, "Critical" não teria a mesma frequência que "Low" e pedido de reembolso não teria a mesma chance de ser crítico que dúvida de produto.
- **Tipo x Assunto são independentes (chi2 p=0,981).** "Refund request" aparece como assunto em 100 tickets de Billing inquiry (dúvida ou disputa de fatura), 126 de Cancellation, 122 de Product inquiry. O rótulo do tipo não descreve o assunto.
- **Texto (Ticket Description): gerado.**
  - 8.469 de 8.469 contêm o placeholder literal `{product_purchased}` sem substituir.
  - Só 16 primeiras frases distintas em 8.469 tickets. 5.868 (69%) começam com "I'm having an issue with the {product_purchased}. Please assist."
  - O resto do texto mistura frases sem relação ("I would like my price to rise so that I can return it", "Please give credit to: @joeyclay").
  - A frase-modelo também não acompanha o assunto: "I'm unable to access my account" aparece com assunto Delivery problem (17) e Display issue (14). A palavra-chave do assunto aparece no texto em 23,2% dos tickets.
- **Resolution: texto aleatório** estilo gerador de lorem ("Offer investment fish.", "Should strong investment lead.").

## Dataset 2: IT Service Ticket Classification (`all_tickets_processed_improved_v3.csv`)

- **Registros:** 47.837 linhas, 2 colunas (Document, Topic_group), 0 nulos, 0 textos duplicados.
- **Distribuição das 8 categorias (desbalanceada, como operação real):**

| Categoria | n | % |
|---|---|---|
| Hardware | 13.617 | 28,5 |
| HR Support | 10.915 | 22,8 |
| Access | 7.125 | 14,9 |
| Miscellaneous | 7.060 | 14,8 |
| Storage | 2.777 | 5,8 |
| Purchase | 2.464 | 5,2 |
| Internal Project | 2.119 | 4,4 |
| Administrative rights | 1.760 | 3,7 |

- **Texto:** mediana 26 palavras (média 43,6, máx 981). Já pré-processado: minúsculas, sem pontuação, sem stopwords, nomes removidos. Tem cara de e-mail real de service desk interno (assinaturas, "sent monday july", "importance high", PO de compra). Diferente do D1, não há placeholder nem frase-modelo.
- **Ruído de rótulo visível:** exemplo amostrado "oracle issue with project tasks editing" rotulado Hardware. Hardware parece absorver chamados de sistema. Isso limita o teto de acurácia de qualquer classificador e precisa entrar na avaliação.
- **Correspondência com o D1: nenhuma direta.** D2 é service desk interno de TI/RH (HR Support, Purchase, Internal Project, Administrative rights). D1 é suporte ao consumidor de eletrônicos (Refund, Cancellation, Billing inquiry, ou dúvida ou disputa de fatura). Sobreposição parcial só de assunto: Account access ~ Access, Hardware issue ~ Hardware, Data loss ~ Storage. Sem rótulo comum, o classificador treinado no D2 **não pode ser medido no texto do D1**; e o texto do D1 não carrega sinal do próprio rótulo.

## Conclusão da auditoria

**O que dá para concluir com segurança:**
- D1 é sintético. Evidências: placeholder não substituído em 100%, 16 frases-modelo, Resolution aleatório, CSAT plano e independente de tudo, distribuições uniformes, 49% de resoluções antes da primeira resposta, e-mails reaproveitados com outro nome.
- D1 serve para descrever **estrutura do fluxo** (3 status, 4 canais, 5 tipos, onde os campos param de ser preenchidos) e volume relativo de backlog: 67% dos tickets (5.700 de 8.469) não estão fechados, 34% esperando o cliente.
- D2 é texto realista e rotulado, com desbalanceamento real. É a base certa para treinar e medir o classificador.

**O que não dá:**
- Calcular tempo de primeira resposta, tempo de resolução ou tempo parado por ticket. Os campos não permitem.
- Afirmar o que move satisfação. Nos dados, nada move. Qualquer "insight" de CSAT por canal ou produto tirado deste dataset é ruído.
- Medir retrabalho, reabertura, repasse entre times ou troca de canal: não há coluna para isso.
- Validar classificador em texto do D1.
- Projetar para 30 mil tickets/ano a partir de contagem do D1 sem premissa externa.

**O que muda na abordagem (proposta, decisão do Jessé):**
1. O diagnóstico vira "o que esses dados deixam e não deixam ver", e o achado principal é que a operação, se mede assim, não tem instrumentação para saber onde perde tempo. Isso é diagnóstico, não desculpa.
2. Horas de desperdício saem de premissas explícitas em faixa (tempo de triagem por ticket, % reclassificado), aplicadas aos 30 mil do brief, e não de médias do D1.
3. Classificador treinado e medido no D2 com split aleatório estratificado e seed fixa. D1 entra só como teste de sanidade de roteamento por regra (tipo, prioridade, canal) e como exemplo de por que texto ruim derruba automação.
4. Lista mínima de campos que a operação precisa começar a registrar (abertura, primeira resposta, reabertura, transferências) antes de qualquer automação ser avaliada em produção.

## Testes usados no diagnóstico (Bloco 2)

Saída de `solution/analise/02_diagnostico.py`. O diagnóstico cita só a conclusão; os testes ficam aqui.

**Status x prioridade, canal e tipo (qui-quadrado):**

| Corte | % fechado, menor e maior | p |
|---|---|---|
| Prioridade | Low 31,2% a Critical 34,1% | 0,227 |
| Canal | Social media 32,2% a Email 33,6% | 0,771 |
| Tipo | Cancellation 30,4% a Refund 34,0% | 0,339 |
| 80 combinações canal x prioridade x tipo (85 a 136 tickets cada) | 19,4% a 43,4% | 0,081 |

Amplitude de 24,0 pontos entre as 80 combinações. Embaralhando o status 500 vezes (seed 42), o acaso sozinho dá de 17,9 a 27,1 pontos (percentis 5 e 95).

**CSAT x variáveis (só os 2.769 fechados):**

| Variável | Pior média | Melhor média | Qui-quadrado p | Kruskal p |
|---|---|---|---|---|
| Prioridade | Critical 2,96 | Low 3,05 | 0,400 | 0,629 |
| Canal | Phone 2,95 | Chat 3,08 | 0,467 | 0,278 |
| Tipo | Refund 2,93 | Cancellation 3,03 | 0,257 | 0,699 |
| Assunto | Delivery problem 2,80 | Installation support 3,18 | 0,876 | 0,807 |
| Produto | Fitbit Versa 2,54 | Dyson 3,22 | 0,253 | 0,667 |
| Gênero | Female 2,97 | Male 3,03 | 0,148 | 0,625 |

Spearman CSAT x idade -0,004; CSAT x (Time to Resolution menos First Response Time) 0,022. Floresta aleatória com todas as variáveis, validação cruzada em 5 partes (seed 42): 20,0% de acerto (desvio 0,7 ponto), contra 20,9% chutando sempre a nota mais comum.

## Contagens usadas na proposta (Bloco 3)

Saída de `solution/analise/03_proposta.py`.

**Portões de autoridade no dataset 1 (8.469 tickets):**

| Item | Tickets | % |
|---|---|---|
| Ticket Type Refund request (reembolso) | 1.752 | 20,7 |
| Ticket Type Billing inquiry (dúvida ou disputa de fatura) | 1.634 | 19,3 |
| Assunto Payment issue (dúvida ou disputa de fatura) | 526 | 6,2 |
| Ticket Type Cancellation request (cancelamento) | 1.695 | 20,0 |
| Assunto Refund request / Cancellation request | 576 / 487 | 6,8 / 5,8 |
| Financeiro por tipo OU assunto | 5.707 | 67,4 |
| Priority Critical | 2.129 | 25,1 |
| Financeiro OU Critical (portões de autoridade) | 6.379 | 75,3 |
| Nota 1 ou 2 entre os fechados | 1.102 de 2.769 | 39,8 |
| Assunto Data loss / Account access (não são portão) | 491 / 509 | 5,8 / 6,0 |

**Piloto:** Email tem 2.143 tickets (25,3%) e 722 pendentes. Pendentes fora de portão financeiro ou Critical, elegíveis a encerramento automático: 24,2% de todos os pendentes.

**Resolution:** 2.769 textos nos fechados, 2.769 únicos. Nenhum se repete, nem dentro do mesmo assunto.

**Resíduo de fecho ou ausência no dataset 2 (47.837 textos, busca por palavra inteira):**

| Termo | Textos | % |
|---|---|---|
| thanks / thank | 31.944 | 66,8 |
| regards | 19.571 | 40,9 |
| best | 7.544 | 15,8 |
| annual leave | 1.034 | 2,2 |
| out of office | 0 | 0,0 |
| Qualquer um | 40.602 | 84,9 |
| Qualquer um, sem "best" (ambíguo: aparece em "best tool") | 40.390 | 84,4 |

"out of office" não aparece em nenhuma forma ("out of office" ou "out office"). "thank" pode ser cortesia no meio do pedido e não só assinatura, então 84,9% é teto do resíduo, não contagem exata de assinaturas.
