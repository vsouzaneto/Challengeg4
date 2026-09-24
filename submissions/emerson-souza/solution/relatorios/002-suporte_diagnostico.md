# Diagnóstico de Suporte — Suporte
_Gerado pelo G4 Analise em 24/09/2026 18:12_

## Resumo executivo
- **8.469 chamados, 67% ainda sem resolução** (5.700 abertos ou aguardando o cliente). Esse acúmulo é o gargalo que os dados mostram com mais clareza, e ele é igual em todos os canais, prioridades e tipos, ou seja, é um problema de capacidade, não de um canal específico.
- **A prioridade não muda o tempo de atendimento:** chamados 'Critical' levam 6,0 h (mediana), o mesmo que os demais (5,9–7,1 h; p = 0,07). Na prática a fila não respeita a urgência.
- **Canal, prioridade, tipo do chamado não explica(m) diferenças de tempo** com segurança estatística: canal (p = 0,77), prioridade (p = 0,07), tipo do chamado (p = 0,14).
- **Nada nos dados impacta a satisfação** (média 2,99 de 5, em 2.769 avaliações): canal, gênero, prioridade, produto, tipo do chamado, faixa de idade, tempo de atendimento têm p > 0,05. A satisfação aqui não serve como termômetro; precisa ser medida de outro jeito.
- **Desperdício:** 28% dos chamados medidos passaram da meta de tempo, somando 2.334 h acima da meta (R\$ 105.035) nos 1.402 chamados com tempo válido. O maior desperdício recuperável está em 'Critical' (1.447 h).
- **A classificação automática funciona:** treinada em 38.269 tickets de TI e testada em 9.568 que o modelo nunca viu, acerta 86,5% das 8 categorias.
- **Onde a IA entra e onde para:** com confiança ≥ 85% o ticket vai direto (58% dos tickets, 97,9% de acerto); na faixa intermediária a IA sugere e o humano confirma; abaixo de 60% e em cancelamento, reembolso, prioridade crítica e permissão de acesso, **sempre humano**.
- **Retorno estimado:** 26% do volume sai automático, economizando cerca de 18 h/mês de triagem (R\$ 811/mês), com as premissas da tela. É um ganho modesto e honesto: o maior ganho está em atacar o acúmulo e fazer a prioridade valer.

## Tempo e acúmulo por canal (tempo: p = 0,77)

| Grupo | Chamados | Mediana (h) | P90 (h) | Em aberto |
|---|---|---|---|---|
| Chat | 2.073 | 6,5 | 16,1 | 67% |
| Email | 2.143 | 6,5 | 15,8 | 66% |
| Social media | 2.121 | 6,4 | 16,9 | 68% |
| Phone | 2.132 | 6,0 | 15,1 | 68% |

## Tempo e acúmulo por prioridade (tempo: p = 0,07)

| Grupo | Chamados | Mediana (h) | P90 (h) | Em aberto |
|---|---|---|---|---|
| High | 2.085 | 7,1 | 17,1 | 66% |
| Low | 2.063 | 7,1 | 16,8 | 69% |
| Critical | 2.129 | 6,0 | 15,2 | 66% |
| Medium | 2.192 | 5,9 | 15,3 | 68% |

## Tempo e acúmulo por tipo do chamado (tempo: p = 0,14)

| Grupo | Chamados | Mediana (h) | P90 (h) | Em aberto |
|---|---|---|---|---|
| Product inquiry | 1.641 | 7,0 | 15,9 | 68% |
| Refund request | 1.752 | 6,7 | 17,2 | 66% |
| Technical issue | 1.747 | 6,4 | 15,4 | 67% |
| Cancellation request | 1.695 | 6,4 | 15,9 | 70% |
| Billing inquiry | 1.634 | 5,3 | 15,4 | 67% |

## O que impacta a satisfação

| Variável | p | Veredito |
|---|---|---|
| Canal | 0,278 | sem diferença |
| Gênero | 0,625 | sem diferença |
| Prioridade | 0,629 | sem diferença |
| Produto | 0,667 | sem diferença |
| Tipo do chamado | 0,699 | sem diferença |
| Faixa de idade | 0,747 | sem diferença |
| Tempo de atendimento | 0,976 | sem diferença |

## Desperdício (horas acima da meta)

| Prioridade | Meta (h) | Estouraram | Horas acima | Custo |
|---|---|---|---|---|
| Critical | 4 | 236 de 374 | 1.447 | R\$ 65.135 |
| High | 8 | 158 de 355 | 887 | R\$ 39.899 |
| Low | 48 | 0 de 332 | 0 | R\$ 0 |
| Medium | 24 | 0 de 341 | 0 | R\$ 0 |

## Classificador (Dataset 2)

| Abordagem | Acurácia | F1 |
|---|---|---|
| TF-IDF (palavras e pares de palavras) + regressão logística | 86,5% | 0,87 |
| TF-IDF + Naive Bayes (linha de base simples) | 77,8% | 0,76 |
| Chute na categoria mais comum | 28,5% |  |

## Automação proposta

| Faixa | % dos tickets | Acerto |
|---|---|---|
| Automático | 58% | 97,9% |
| IA sugere, humano confirma | 23% | 82,6% |
| Direto para humano | 19% | 57,2% |

**Nunca automatizar:** Tipo cancelamento/reembolso: 3447 chamados; Prioridade crítica: 2129 chamados; categoria Administrative rights; confiança baixa.
**Retorno estimado:** 18 h/mês (R\$ 811/mês).

## Como os números foram calculados
- **Tempo de atendimento:** duração = data/hora da resolução − data/hora da 1ª resposta, só quando positiva (a base não tem a hora de abertura do chamado).
- **Onde trava:** mediana e percentil 90 do tempo por canal, prioridade e tipo (intervalo de 95% da mediana por reamostragem); combinações só com pelo menos 30 chamados; teste de Kruskal-Wallis entre os grupos.
- **Acúmulo:** % de chamados abertos ou aguardando o cliente por grupo (teste qui-quadrado).
- **Satisfação:** Kruskal-Wallis por variável e correlação de Spearman com o tempo. p < 0,05 = impacto comprovado.
- **Desperdício:** horas acima da meta de cada prioridade × custo/hora (R\$ 45); metas: critical 4 h, urgent 4 h, high 8 h, medium 24 h, low 48 h.
- **Classificador:** TF-IDF + regressão logística treinada em 80% do Dataset 2 e avaliada nos 20% restantes (nunca vistos).
- **Automação:** confiança ≥ 85% = automático; entre 60% e 85% = IA sugere; abaixo = humano. Bloqueados sempre: tipos Cancellation request, Refund request; prioridades Critical, urgent; categorias Administrative rights.
- **Retorno:** tickets/mês × parte elegível × cobertura da faixa × 5 min de triagem (a faixa 'sugere' economiza metade).

## Qualidade dos dados
- Base com 8.469 chamados.
- Tempo: duração = data/hora da resolução − data/hora da 1ª resposta, só quando positiva (a base não tem a hora de abertura do chamado). Dos 2769 chamados com as duas datas, 1367 têm a resolução ANTES da 1ª resposta e ficaram de fora. Sobram 1402 com duração válida.
- Satisfação existe em 2769 chamados (33%); os demais estão sem nota e ficam de fora dessa parte.
- O texto do Dataset 1 não indica o tipo do chamado: um classificador treinado nele acerta 19%, igual ao acaso (20%). 100% das descrições têm o marcador '{product_purchased}' não preenchido. Por isso o classificador é treinado no Dataset 2.
- Os textos de resolução do Dataset 1 são frases aleatórias (sem relação com o problema): não servem para 'respostas sugeridas'.