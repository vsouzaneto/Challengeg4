# Diagnóstico de Churn — Churn
_Gerado pelo G4 Analise em 24/09/2026 18:12_

## Resumo executivo
- **110 de 500 clientes cancelaram (22,0%)**, com intervalo de confiança de 95% entre 19% e 26%. A receita mensal perdida é de **US\$ 254.952** (MRR da última assinatura de cada conta cancelada). Ainda estão ativos US\$ 963.603 por mês.
- **O que o CEO ouviu está certo, mas não explica o churn:** o uso total variou 2,6% do primeiro ao último trimestre, ou seja, praticamente estável; a satisfação média é 4,0 de 5, e quem cancelou deu nota 4,0 contra 4,0 de quem ficou (sem diferença, p = 0,49); 41% dos chamados ficaram sem avaliação. Nem o uso agregado nem a satisfação separam quem sai de quem fica.
- **Nenhum dos 6 sinais de comportamento testados** (queda de uso, erros em funcionalidade beta, chamado escalado, 1ª resposta lenta, satisfação baixa, downgrade de plano) **separa, com segurança estatística, as contas que cancelaram das que ficaram.** Qualquer recomendação baseada nele(s) é hipótese, não fato.
- **Onde o risco é maior (perfil, não comportamento):** segmento / indústria **DevTools** cancela 31% contra 22% da média (p = 0,07); canal de aquisição **event** cancela 30% contra 22% da média (p = 0,08). É o sinal mais forte da base, mas ainda é indício (p entre 0,05 e 0,10), não prova.
- **Motivos declarados:** o mais citado é 'budget' (15%); orçamento + preço somam 30%. 32% das canceladas não têm motivo registrado.
- **Previsão:** um modelo de machine learning, avaliado com validação cruzada, acerta pouco acima do acaso (AUC 0,56; 0,50 = moeda jogada). Os dados não permitem prever com confiança quem vai cancelar; por isso a priorização usa regra explicável + valor da conta.
- **Primeira ação recomendada:** Plano de retenção para canal de aquisição 'event' — 67 contas, US\$ 132.705/mês em jogo, impacto estimado de US\$ 26.541/mês (premissa: recuperar 20%).

## Plano de ação (priorizado)

| # | Ação | Contas | MRR em jogo | Impacto estimado | Evidência |
|---|---|---|---|---|---|
| 1 | Plano de retenção para canal de aquisição 'event' | 67 | US\$ 132.705 | US\$ 26.541 | fraca (indício) |
| 2 | Plano de retenção para segmento / indústria 'DevTools' | 78 | US\$ 125.158 | US\$ 25.032 | fraca (indício) |
| 3 | Revisar oferta e preço para contas de alto risco | 59 | US\$ 215.904 | US\$ 43.181 | motivo declarado pelos clientes |
| 4 | Régua de atendimento para contas em risco com problema de suporte | 33 | US\$ 51.109 | US\$ 10.222 | regra de negócio (ver teste dos sinais) |
| 5 | Alerta de desengajamento (queda de uso) | 114 | US\$ 274.961 | US\$ 54.992 | sem evidência |
| 6 | Estabilizar funcionalidades beta | 105 | US\$ 235.224 | US\$ 47.045 | sem evidência |

## Motivos declarados

| Motivo | Contas | % | MRR perdido |
|---|---|---|---|
| sem registro | 35 | 31,8% | US\$ 87.952 |
| budget | 17 | 15,5% | US\$ 50.035 |
| pricing | 16 | 14,5% | US\$ 31.025 |
| features | 15 | 13,6% | US\$ 34.851 |
| support | 14 | 12,7% | US\$ 28.553 |
| competitor | 7 | 6,4% | US\$ 14.131 |
| unknown | 6 | 5,5% | US\$ 8.405 |

## Sinais testados

| Sinal | Contas com sinal | Churn com | Churn sem | p | Evidência |
|---|---|---|---|---|---|
| Queda de uso | 140 | 18,6% | 23,3% | 0,30 | sem evidência |
| Erros em funcionalidade beta | 142 | 26,1% | 20,4% | 0,21 | sem evidência |
| Chamado escalado | 25 | 32,0% | 21,5% | 0,32 | sem evidência |
| 1ª resposta lenta | 67 | 25,4% | 21,5% | 0,58 | sem evidência |
| Satisfação baixa | 84 | 16,7% | 23,1% | 0,25 | sem evidência |
| Downgrade de plano | 115 | 16,5% | 23,6% | 0,14 | sem evidência |

## Segmentos

**Segmento / indústria** (p = 0,07; média 22,0%)

| Grupo | Contas | Taxa | IC 95% |
|---|---|---|---|
| DevTools | 113 | 31,0% | 23%–40% |
| FinTech | 112 | 22,3% | 16%–31% |
| HealthTech | 96 | 21,9% | 15%–31% |
| EdTech | 79 | 16,5% | 10%–26% |
| Cybersecurity | 100 | 16,0% | 10%–24% |

**Canal de aquisição** (p = 0,08; média 22,0%)

| Grupo | Contas | Taxa | IC 95% |
|---|---|---|---|
| event | 96 | 30,2% | 22%–40% |
| other | 103 | 24,3% | 17%–33% |
| ads | 98 | 23,5% | 16%–33% |
| organic | 114 | 17,5% | 12%–26% |
| partner | 89 | 14,6% | 9%–23% |

**País** (p = 0,66; média 22,0%)

| Grupo | Contas | Taxa | IC 95% |
|---|---|---|---|
| DE | 25 | 32,0% | 17%–52% |
| US | 291 | 23,4% | 19%–29% |
| FR | 22 | 22,7% | 10%–43% |
| IN | 49 | 20,4% | 11%–34% |
| UK | 58 | 19,0% | 11%–31% |
| CA | 23 | 17,4% | 7%–37% |
| AU | 32 | 12,5% | 5%–28% |

**Plano** (p = 1,00; média 22,0%)

| Grupo | Contas | Taxa | IC 95% |
|---|---|---|---|
| Enterprise | 154 | 22,1% | 16%–29% |
| Basic | 168 | 22,0% | 16%–29% |
| Pro | 178 | 21,9% | 16%–29% |

**Em período de teste** (p = 0,39; média 22,0%)

| Grupo | Contas | Taxa | IC 95% |
|---|---|---|---|
| Sim | 97 | 25,8% | 18%–35% |
| Não | 403 | 21,1% | 17%–25% |

**Faixa de assentos** (p = 0,62; média 22,0%)

| Grupo | Contas | Taxa | IC 95% |
|---|---|---|---|
| 6-10 | 72 | 29,2% | 20%–41% |
| 26-50 | 106 | 21,7% | 15%–30% |
| 51+ | 37 | 21,6% | 11%–37% |
| 1-5 | 126 | 20,6% | 14%–29% |
| 11-25 | 159 | 20,1% | 15%–27% |

## Contas ativas prioritárias (top 20)

| Conta | Prioridade | Risco | MRR | Por quê |
|---|---|---|---|---|
| A-afa505 | 1 · Salvar agora | 90 | US\$ 13.930 | Perfil de risco: segmento 'DevTools' cancela 31% (média 22%) (+90) |
| A-d792a6 | 1 · Salvar agora | 90 | US\$ 12.935 | Perfil de risco: segmento 'DevTools' cancela 31% (média 22%) (+90) |
| A-82861f | 1 · Salvar agora | 90 | US\$ 8.159 | Perfil de risco: segmento 'DevTools' cancela 31% (média 22%) (+90) |
| A-e7a1e2 | 1 · Salvar agora | 82 | US\$ 8.756 | Perfil de risco: canal de aquisição 'event' cancela 30% (média 22%) (+82) |
| A-726cfa | 1 · Salvar agora | 90 | US\$ 7.562 | Perfil de risco: segmento 'DevTools' cancela 31% (média 22%) (+90) |
| A-8b0451 | 1 · Salvar agora | 82 | US\$ 8.159 | Perfil de risco: canal de aquisição 'event' cancela 30% (média 22%) (+82) |
| A-068fc6 | 1 · Salvar agora | 82 | US\$ 6.965 | Perfil de risco: canal de aquisição 'event' cancela 30% (média 22%) (+82) |
| A-2d4502 | 1 · Salvar agora | 82 | US\$ 6.766 | Perfil de risco: canal de aquisição 'event' cancela 30% (média 22%) (+82) |
| A-aa9511 | 1 · Salvar agora | 90 | US\$ 5.970 | Perfil de risco: segmento 'DevTools' cancela 31% (média 22%) (+90) |
| A-3b5cd1 | 1 · Salvar agora | 82 | US\$ 6.368 | Perfil de risco: canal de aquisição 'event' cancela 30% (média 22%) (+82) |
| A-ad64c6 | 1 · Salvar agora | 90 | US\$ 5.572 | Perfil de risco: segmento 'DevTools' cancela 31% (média 22%) (+90) |
| A-3f9cc0 | 1 · Salvar agora | 82 | US\$ 5.970 | Perfil de risco: canal de aquisição 'event' cancela 30% (média 22%) (+82) |
| A-96e141 | 1 · Salvar agora | 90 | US\$ 4.975 | Perfil de risco: segmento 'DevTools' cancela 31% (média 22%) (+90) |
| A-297a2d | 1 · Salvar agora | 82 | US\$ 5.373 | Perfil de risco: canal de aquisição 'event' cancela 30% (média 22%) (+82) |
| A-034368 | 1 · Salvar agora | 82 | US\$ 4.577 | Perfil de risco: canal de aquisição 'event' cancela 30% (média 22%) (+82) |
| A-3b37d9 | 1 · Salvar agora | 82 | US\$ 4.577 | Perfil de risco: canal de aquisição 'event' cancela 30% (média 22%) (+82) |
| A-c16b88 | 1 · Salvar agora | 82 | US\$ 4.577 | Perfil de risco: canal de aquisição 'event' cancela 30% (média 22%) (+82) |
| A-832ec2 | 1 · Salvar agora | 82 | US\$ 4.378 | Perfil de risco: canal de aquisição 'event' cancela 30% (média 22%) (+82) |
| A-19b2c8 | 1 · Salvar agora | 90 | US\$ 3.980 | Perfil de risco: segmento 'DevTools' cancela 31% (média 22%) (+90) |
| A-ac9111 | 1 · Salvar agora | 82 | US\$ 4.179 | Perfil de risco: canal de aquisição 'event' cancela 30% (média 22%) (+82) |

## Como os números foram calculados
- **Cliente cancelado** = marcação oficial da conta. O motivo e a data vêm do último evento de cancelamento.
- **MRR perdido** = receita da última assinatura de cada conta cancelada (somar todas as assinaturas encerradas misturaria upgrade/downgrade com cancelamento e inflaria o número).
- **Sinais** medidos só no período ANTES da data de referência (cancelada: data do cancelamento; ativa: 31/12/2024), para não usar informação do futuro. Queda de uso: últimos 90 dias contra os 90 anteriores, queda ≥ 30%. Demais sinais: últimos 180 dias. Resposta lenta: média acima de 131 min (percentil 75 da base).
- **Teste de cada sinal:** taxa de churn de quem tem o sinal × quem não tem, com teste qui-quadrado (ou Fisher). p < 0,05 = evidência forte; 0,05–0,10 = indício; acima = sem evidência.
- **Score de risco (0–100):** com 'pesos pelos dados', só pontua o que mostrou diferença (p < 0,10); cada conta mostra quais sinais somaram pontos.
- **Prioridade:** risco × valor. 'Salvar agora' = risco ≥ 50 e MRR acima da mediana; 'Acompanhar' = risco ≥ 50 ou (risco ≥ 30 e MRR alto); o resto, 'Monitorar'.
- **Impacto estimado** = MRR das contas-alvo × taxa de recuperação (20%, premissa editável).
- **Ações ordenadas pela força da evidência primeiro**, depois pelo impacto: ação sem evidência não vira prioridade só porque mexe com muito dinheiro.

## Correlação × causalidade
Tudo aqui é **correlação**: mostra onde o churn é maior, não prova o porquê. Exemplo: um segmento cancelar mais pode ser pelo produto, pelo preço para esse público ou pela forma de venda. Para provar causa, o próximo passo é testar: aplicar a ação num grupo de clientes e comparar com um grupo parecido que não recebeu.

## Qualidade dos dados
- 35 contas marcadas como canceladas não têm evento de cancelamento (motivo = 'sem registro').
- 277 contas têm evento de cancelamento mas não estão marcadas como canceladas (provável reativação). Para a taxa de churn vale a marcação da conta.
- 61 eventos são reativações.
- Menor nota de satisfação registrada na base: 3. Com escala 1–5, a régua de 'satisfação baixa' é uma premissa editável.
- Data de referência das contas ativas: 31/12/2024 (último dado da base). Canceladas: data do cancelamento. Sinais medidos só ANTES dessa data (evita vazamento).