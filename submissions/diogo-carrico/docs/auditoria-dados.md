# Auditoria dos dados

> Gerado por `solution/scripts/write_audit_report.py` a partir de `solution/outputs/audit/*.json`.
> Não editar à mão: rode `uv run python scripts/run_audit.py` e depois este script.

## Veredito

**Dataset 1 (tickets de suporte) é sintético.** Oito sinais, vindos de cinco partes diferentes da base (descrições, resoluções, e-mails, horários e distribuições), apontam na mesma direção. A base não sustenta diagnóstico de tempo nem de satisfação: serve para demonstrar o método e o fluxo, não para medir uma operação.

**Dataset 2 (tickets de TI) traz texto de e-mails de suporte, já pré-processado** (“hi”, “regards” e “thank” estão entre as palavras mais comuns), com 8 classes desbalanceadas. É a base para treinar e avaliar o classificador.

## O que o brief diz e o que os dados mostram

| O brief diz | Os dados mostram |
| --- | --- |
| ~30.000 tickets | 8.469 registros. O arquivo tem 29.808 linhas físicas porque 6.150 descrições contêm quebras de linha |
| 3 tipos de ticket (Technical, Billing, Product inquiry) | 5 tipos. Refund request e Cancellation request somam 40,7% do volume |
| First Response Time = tempo até a primeira resposta | É um carimbo de data e hora, não uma duração. Sem a data de abertura do ticket, o tempo de resposta não pode ser calculado |
| Time to Resolution = tempo total até a resolução | Também é um carimbo. Em 49,3% dos 2.769 tickets fechados, a resolução acontece antes da primeira resposta |
| Nota de satisfação do cliente | Existe só nos 2.769 tickets fechados (32,7% da base) |

## Sinais de dados sintéticos no Dataset 1

| # | Sinal | Evidência |
| --- | --- | --- |
| 1 | Placeholder de template não preenchido | `{product_purchased}` em 100% das descrições, mais 155 variações (`{order_id}`, `{product_price}`...). Nenhuma descrição cita o produto comprado (0%) |
| 2 | Texto repetido | “I'm having an issue with the {product_purchased}.” aparece 5.998 vezes e “Please assist.” 6.181 vezes em 8.469 descrições |
| 3 | Resoluções sem sentido | 2.769 resoluções, todas diferentes, com 5,5 palavras em média. Exemplos sorteados: “Almost Republican let strategy.”; “Help red business point window ever represent.”; “Eat increase hand situation size.” |
| 4 | E-mails de exemplo | 100% em example.com, .org ou .net, domínios reservados para documentação (RFC 2606) |
| 5 | Janela de tempo impossível | Todas as respostas e resoluções cabem em 27,0 horas (2023-05-31 21:53:30 a 2023-06-02 00:55:33), enquanto as compras vão de 2020-01-01 a 2021-12-30 |
| 6 | Timestamps contraditórios | 49,3% dos tickets fechados são resolvidos antes da primeira resposta |
| 7 | Distribuições de sorteio | Tipo (p = 0,11), prioridade (p = 0,20), canal (p = 0,72), status (p = 0,33), 42 produtos (p = 0,48), CSAT (p = 0,80) e idade de 18 a 70 anos (p = 0,55) são indistinguíveis de partes iguais (qui-quadrado). Gênero (p < 0,01) e assunto (p = 0,02) se afastam um pouco, com no máximo 1,2× de diferença entre categorias; “Other” em 31,7% dos clientes é improvável numa base real |
| 8 | Nada se relaciona com nada | Assunto × tipo: V de Cramér 0,03 (p = 0,98). Um modelo TF-IDF + regressão logística prevê o tipo pela descrição com 18,9% de acurácia, contra 20,0% de chance; assunto 5,8% contra 6,2%; prioridade 25,4% contra 25,0% |

## Satisfação e tempo de resolução

Correlação de Spearman entre horas de resolução e CSAT: ρ = 0,022 (p de permutação 0,25; faixa nula de 95%: −0,037 a 0,037; n = 2.769). Só com durações não negativas: ρ = 0,003 (p = 0,92; n = 1.404).

Uma correlação perto de zero, sozinha, não provaria nada; aqui ela é coerente com os outros oito sinais.

## Estrutura por status

| Status | Tickets | Primeira resposta | Resolução e CSAT |
| --- | --- | --- | --- |
| Open | 2.819 (33,3%) | Nenhuma | Nenhuma |
| Pending Customer Response | 2.881 (34,0%) | Todas | Nenhuma |
| Closed | 2.769 (32,7%) | Todas | Todas |

## Dataset 2

- 47.837 tickets em 8 classes: Hardware 28,5%, HR Support 22,8%, Access 14,9%, Miscellaneous 14,8%, Storage 5,8%, Purchase 5,1%, Internal Project 4,4%, Administrative rights 3,7%. A maior classe é 7,7× a menor, então a acurácia sozinha engana: reportamos também macro-F1.
- Texto pré-processado: 100% em minúsculas, nenhum dígito (0%), pontuação em 0,03% dos documentos. Stopwords ainda são 21,6% dos tokens, então não foram removidas por completo. Uma comparação com modelos de linguagem precisa levar isso em conta, porque eles foram treinados com texto natural.
- 12.327 palavras distintas; mediana de 26 tokens por documento (p95 136, máximo 981); 133 documentos com menos de 5 tokens.
- Nenhum texto duplicado exatamente (0), portanto nenhum conflito de rótulo entre duplicatas exatas. A estimativa de ruído de rótulo (X1) vai depender de quase-duplicatas e de revisão manual.

## O que isso muda no plano

- **Diagnóstico (D1):** gargalos e drivers de satisfação não podem ser medidos nesta base. O tempo de resposta não existe, o CSAT é uniforme e nenhuma variável se associa a outra. Entregamos o teste nulo e a lista do que medir numa operação real.
- **Ligação entre os datasets:** aplicar o modelo do Dataset 2 às descrições do Dataset 1 mede o desvio de domínio, não o desempenho.
- **Rascunhos de resposta (X2):** ancorados numa base de conhecimento própria, nunca nas resoluções do Dataset 1.
