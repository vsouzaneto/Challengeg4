# Auditoria de qualidade dos dados

_Gerado por `01_auditoria_dados.py`. Revisado por agente juiz independente (`process-log/revisoes/fase1_auditoria_parecer.md`)._

## Dataset 1: Customer Support Tickets

### 1. O que o enunciado promete × o que os dados entregam

| Enunciado do case | Dados reais |
|---|---|
| ~30.000 tickets | **8.469** |
| 3 tipos de ticket | **5** tipos |
| Texto completo da reclamação | **100%** com campo não preenchido (`{product_purchased}`); só **16** frases de abertura, a mais comum em 69% |
| Texto da resolução aplicada | Frases sem sentido no estilo da biblioteca Faker (ex.: *"Offer investment fish."*) |
| Tempo até 1ª resposta / até resolução | **Carimbos de data e hora**, todos numa janela de **27 horas** (31/05/2023 a 02/06/2023), para compras feitas entre 2020 e 2021 |
| Dados de cliente | E-mails todos em domínios `@example` |

### 2. Evidências de que os dados são sintéticos

- Em **49%** dos tickets fechados (1.365 de 2.769) a resolução acontece **antes** da primeira resposta.
- Os carimbos de tempo acompanham a ordem do `Ticket ID` (Spearman ρ = 0,14, p < 0,001): cada linha recebe "agora + sorteio de até 24 h" enquanto o gerador avança, um rastro típico de geração automática.
- CSAT de 1 a 5 com frequências 553 / 549 / 580 / 543 / 544: estatisticamente uniforme (p = 0,80).
- Os 3 status também são equiprováveis (Pending Customer Response: 2.881, Open: 2.819, Closed: 2.769; p = 0,33). **Os 67% "não fechados" vêm de um sorteio de 1/3 por status, e não de um backlog real.**
- A única regra de processo consistente é a máquina de estados (Open sem resposta; Pending com resposta e sem resolução; Closed completo): sem nenhuma exceção.

### 3. As variáveis não se relacionam entre si

Dos **21** pares de variáveis categóricas, **0** têm associação estatisticamente significativa (p < 0,05). Maior Cramér's V (corrigido para viés): **0,021**. Numa operação real, prioridade e canal, ou tipo e assunto, estariam claramente associados.

| Par | V corrigido | p-valor |
|---|---|---|
| Ticket Type × Ticket Subject | 0,000 | 0,98 |
| Ticket Type × Ticket Priority | 0,000 | 0,56 |
| Ticket Type × Ticket Channel | 0,000 | 0,46 |
| Ticket Type × Product Purchased | 0,000 | 0,92 |
| Ticket Type × Customer Gender | 0,000 | 0,66 |
| Ticket Type × Ticket Status | 0,008 | 0,34 |
| Ticket Subject × Ticket Priority | 0,000 | 0,65 |
| Ticket Subject × Ticket Channel | 0,000 | 0,72 |
| Ticket Subject × Product Purchased | 0,011 | 0,33 |
| Ticket Subject × Customer Gender | 0,000 | 0,77 |
| Ticket Subject × Ticket Status | 0,021 | 0,16 |
| Ticket Priority × Ticket Channel | 0,016 | 0,08 |
| Ticket Priority × Product Purchased | 0,019 | 0,26 |
| Ticket Priority × Customer Gender | 0,000 | 0,60 |
| Ticket Priority × Ticket Status | 0,011 | 0,23 |
| Ticket Channel × Product Purchased | 0,000 | 0,63 |
| Ticket Channel × Customer Gender | 0,000 | 0,57 |
| Ticket Channel × Ticket Status | 0,000 | 0,77 |
| Product Purchased × Customer Gender | 0,000 | 0,92 |
| Product Purchased × Ticket Status | 0,000 | 0,66 |
| Customer Gender × Ticket Status | 0,007 | 0,30 |

**Teste com classificador:** se o texto da descrição fosse real, ele deveria prever o assunto e o tipo do ticket.

| Alvo | Acurácia (validação cruzada, 5 dobras) | Chute da classe mais frequente |
|---|---|---|
| Ticket Subject | 6,4% | 6,8% |
| Ticket Type | 19,5% | 20,7% |
| Ticket Priority | 24,9% | 25,9% |

### 4. Nada explica a satisfação

10 testes. Com correção de Bonferroni, o limiar de significância passa a ser p < 0,0050.

| Variável | Teste | p-valor | Significativo após correção? |
|---|---|---|---|
| Ticket Type | Kruskal-Wallis | 0,699 | não |
| Ticket Subject | Kruskal-Wallis | 0,807 | não |
| Ticket Priority | Kruskal-Wallis | 0,629 | não |
| Ticket Channel | Kruskal-Wallis | 0,278 | não |
| Product Purchased | Kruskal-Wallis | 0,667 | não |
| Customer Gender | Kruskal-Wallis | 0,625 | não |
| duracao_h | Spearman ρ = 0,022 | 0,254 | não |
| Customer Age | Spearman ρ = -0,004 | 0,832 | não |
| hora_1a_resposta | Spearman ρ = -0,040 | 0,035 | não |
| data_compra | Spearman ρ = -0,039 | 0,041 | não |

- Os 2 p-valores abaixo de 0,05 são compatíveis com o acaso em 10 testes; nenhum sobrevive à correção e os efeitos são desprezíveis (|ρ| < 0,05).
- **Poder estatístico:** com ~692 notas por grupo (desvio-padrão 1,41), os testes detectariam uma diferença de **0,21 ponto** de CSAT entre dois grupos (80% de poder, α = 5%). Não detectar nada não é falta de amostra.

### 4b. Onde o fluxo trava? A pergunta respondida ao pé da letra

Duração (resolução − 1ª resposta) dos 2.769 tickets fechados, nas 80 combinações de canal × prioridade × tipo.

| As 3 "piores" combinações | Média | IC95% | Tickets |
|---|---|---|---|
| Email · Medium · Product inquiry | 3,4 h | -0,6 a 7,5 h | 21 |
| Chat · Low · Billing inquiry | 3,3 h | 1,1 a 5,4 h | 35 |
| Chat · High · Refund request | 3,0 h | -0,3 a 6,2 h | 41 |

| As 3 "melhores" combinações | Média | IC95% | Tickets |
|---|---|---|---|
| Email · Critical · Product inquiry | -4,1 h | -7,0 a -1,3 h | 40 |
| Social media · Medium · Cancellation request | -3,4 h | -6,7 a -0,1 h | 25 |
| Chat · Medium · Technical issue | -3,2 h | -6,3 a -0,2 h | 30 |

- A "pior" combinação parece **7,6 h mais lenta** que a "melhor". Mas, embaralhando as durações ao acaso entre os tickets, a diferença entre a pior e a melhor combinação fica em média em **8,1 h**: o gap observado não supera o acaso (teste de permutação p = 0,68; Kruskal-Wallis entre as 80 combinações p = 0,37).
- Por que alguns intervalos das extremas não se sobrepõem e ainda assim é ruído: com 80 combinações, as mais extremas *sempre* parecem diferentes (comparações múltiplas). O teste certo compara o gap observado com o que o acaso produz, e ele não passa disso. Note também que as "melhores" têm duração média **negativa**, o que é impossível numa operação real.
- **Resposta:** com estes dados, nenhuma combinação trava o fluxo de forma distinguível do ruído. Apontar "X é o gargalo" seria escolher um número sorteado.

### 5. Conclusão e o que ainda é aproveitável

**O Dataset 1 é sintético, com variáveis geradas de forma independente.** Diferenças entre grupos (tempo por prioridade, CSAT por canal etc.) estão dentro do ruído e **não devem ser usadas para diagnóstico**: produziriam números com aparência real que levariam a decisões erradas.

Ainda aproveitável, com essa ressalva explícita:
- A **estrutura** da operação: a máquina de estados Open → Pending → Closed, canais, prioridades, tipos e assuntos.
  Ela serve de molde para o fluxo proposto e para o plano de instrumentação.
- As 16 frases-modelo como casos de teste de fumaça do protótipo (nunca para treino ou avaliação).
- O mix de volume só como ilustração: ele é quase uniforme por construção.

## Dataset 2: IT Service Ticket Classification

- **47.837** registros; nulos: 0; textos duplicados: 0.
- Texto real de e-mails corporativos de TI, **parcialmente pré-processado**: minúsculas, sem pontuação e sem números, dados pessoais removidos e stopwords removidas do corpo (o assunto do e-mail ainda as mantém).
- Tamanho: mediana de 26 palavras (75% até 46; máximo 981).
- **8 classes desbalanceadas**: Hardware 28,5% × Administrative rights 3,7%. Por isso a métrica principal é o **F1-macro**, e não só a acurácia.
- **Ruído de rótulo:** numa amostra de 32 textos lida pelo agente juiz, cerca de 15 a 25% dos rótulos eram duvidosos ou ambíguos (ex.: pedido de acesso a fila rotulado como `Storage`). Isso coloca um teto natural na acurácia de qualquer modelo.
- **Não tem** tempo, canal nem satisfação: serve para provar a automação de triagem, não para diagnóstico operacional.