# Resposta executiva canônica

Resposta curta: A taxa mensal ponderada de churn ficou em 12.4% no período recente, variação de +7.0 pp versus a referência. O MRR perdido observado no período recente foi US$ 1.622.337; é impacto associado aos churns, não receita automaticamente recuperável. O uso cresceu no agregado (0.336→0.493), mas caiu entre as contas que churnariam em 30 dias (0.349→0.304). Nenhum mecanismo passou todos os gates. Decisão: validar dados, uso e satisfação antes de intervir.

## 1. O que mudou

**Alta confiança**

A taxa mensal ponderada de churn ficou em 12.4% no período recente, variação de +7.0 pp versus a referência. O MRR perdido observado no período recente foi US$ 1.622.337; é impacto associado aos churns, não receita automaticamente recuperável. O uso cresceu no agregado (0.336→0.493), mas caiu entre as contas que churnariam em 30 dias (0.349→0.304).

- **C-churn-change:** A taxa mensal ponderada de churn ficou em 12.4% no período recente, variação de +7.0 pp versus a referência.
- **C-churn-impact:** O MRR perdido observado no período recente foi US$ 1.622.337; é impacto associado aos churns, não receita automaticamente recuperável.
- **C-usage-overall:** Uso diário por conta no agregado: 0.336→0.493.
- **C-usage-churn-next-30d:** Uso diário por conta entre futuros churners de 30 dias: 0.349→0.304.

## 2. Onde está concentrado

**Alta confiança**

Não há concentração material demonstrada: o maior recorte elegível tem RR 1.08×, abaixo do limiar descritivo de 1,25×.

- **C-top-segment:** country / US teve risco relativo descritivo de 1.08x.

## 3. Causa ainda não demonstrada

**Baixa confiança**

Nenhuma hipótese passou todos os gates; não há causa identificada.


## 4. O que ainda não sabemos

**Baixa confiança**

A satisfação geral dos respondentes subiu de 3.96→4.02 (cobertura 63.3%); entre futuros churners, caiu de 4.50→3.67 (cobertura 65.9%). São apenas tickets respondidos; não representam toda a base. A auditoria sinalizou 34.240 ocorrências de regras de qualidade; uma mesma linha pode aparecer em mais de uma regra.

- **C-satisfaction-overall:** Satisfação geral entre tickets respondidos: 3.96→4.02.
- **C-satisfaction-churn-next-30d:** Satisfação entre respondentes que churnariam em 30 dias: 4.50→3.67.
- **C-data-quality-anomalies:** A auditoria sinalizou 34.240 ocorrências de regras de qualidade; uma mesma linha pode aparecer em mais de uma regra.

## 5. Próximas ações

**Baixa confiança**

Validar dados, uso e satisfação antes de intervir em clientes.

- **A-data-integrity:** Sanear eventos fora do ciclo de vida e medir novamente o churn.
- **A-usage-prospective:** Acompanhar uso e churn prospectivamente por 30 dias.
- **A-satisfaction-sample:** Medir satisfação numa amostra representativa, fora dos tickets.

---

# Diagnóstico executivo de churn

## Decisão executiva

Evidência insuficiente para priorizar uma causa

**Leitura em uma frase:** uso aumentou no agregado e caiu na coorte que churnará em 30 dias; satisfação exige atenção; nenhuma hipótese passou todos os gates.

## O que não bate

| métrica | coorte | início | fim | tendência | leitura | cobertura |
| --- | --- | --- | --- | --- | --- | --- |
| Uso da plataforma (C-usage-growth) | Todas as contas | 0.336 | 0.493 | 0.039 | Aumentou | 0.884 |
| Satisfação dos clientes (C-satisfaction-ok) | Todas as contas | 3.959 | 4.021 | n/d | Exige atenção | 0.633 |
| Uso da plataforma (C-usage-growth) | Churn em até 30 dias | 0.349 | 0.304 | 0.002 | Caiu | 0.729 |
| Satisfação dos clientes (C-satisfaction-ok) | Churn em até 30 dias | 4.500 | 3.667 | n/d | Exige atenção | 0.659 |

## Qualidade que limita a decisão

| regra | linhas |
| --- | --- |
| Usos anteriores à assinatura | 19142 |
| Usos anteriores ao cadastro | 13198 |
| Tickets anteriores ao cadastro | 1077 |
| Flags de conta divergentes do evento | 301 |
| Usos posteriores ao fim da assinatura | 290 |
| Flags de assinatura divergentes por conta | 211 |
| Grupos de IDs de uso duplicados | 21 |

## Hipóteses avaliadas

| hipótese | por que não passou |
| --- | --- |
| Renovação automática desligada | Associação insuficiente |
| Queda de uso | Instável entre cronologias |
| Erros de produto | Instável entre cronologias |
| Downgrade comercial | Amostra ou cobertura insuficiente |
| Baixa satisfação | Modelo estatístico inválido |
| Escalações de suporte | Amostra ou cobertura insuficiente |

## Segmentos descritivos

Entre os segmentos elegíveis, País / US tem o maior risco relativo (1.08x); valores maiores abaixo permanecem inconclusivos por amostra ou número de churns.

| dimensão | segmento | contas | taxa de churn | taxa geral | risco relativo | MRR perdido | elegibilidade |
| --- | --- | --- | --- | --- | --- | --- | --- |
| País | US | 106 | 0.160 | 0.149 | 1.075 | 223111.000 | Elegível |
| Trial | Não | 146 | 0.151 | 0.149 | 1.010 | 374777.000 | Elegível |
| Faixa de MRR | Alto | 170 | 0.141 | 0.149 | 0.946 | 459183.000 | Elegível |
| Cobrança | Misto | 171 | 0.140 | 0.149 | 0.941 | 449951.000 | Elegível |
| Plano | Misto | 168 | 0.137 | 0.149 | 0.918 | 435486.000 | Elegível |
| Plano | Basic | 4 | 0.500 | 0.149 | 3.352 | 6685.000 | Inconclusivo |
| Cobrança | Anual | 5 | 0.400 | 0.149 | 2.681 | 15917.000 | Inconclusivo |
| Faixa de MRR | Médio | 10 | 0.300 | 0.149 | 2.011 | 7863.000 | Inconclusivo |
| País | AU | 15 | 0.267 | 0.149 | 1.788 | 131919.000 | Inconclusivo |
| Plano | Enterprise | 8 | 0.250 | 0.149 | 1.676 | 24875.000 | Inconclusivo |
| Origem | Eventos | 38 | 0.211 | 0.149 | 1.411 | 142010.000 | Inconclusivo |
| Cobrança | Mensal | 5 | 0.200 | 0.149 | 1.341 | 1178.000 | Inconclusivo |
| Indústria | Cybersecurity | 37 | 0.189 | 0.149 | 1.268 | 103707.000 | Inconclusivo |
| Origem | Parceiros | 27 | 0.185 | 0.149 | 1.241 | 39525.000 | Inconclusivo |
| Indústria | DevTools | 36 | 0.167 | 0.149 | 1.117 | 86210.000 | Inconclusivo |

## Contas para validação

Nenhuma conta está autorizada para intervenção: não há finding aceito. As contas abaixo servem somente para validação dos sinais e dos dados.
| conta | ordem de validação | quantidade de sinais | MRR exposto máximo | sinais | uso permitido |
| --- | --- | --- | --- | --- | --- |
| A-49b828 | 1 | 4 | 31108.000 | Queda de uso, Escalações de suporte, Baixa satisfação, Renovação automática desligada | Somente validação |
| A-e60f9d | 2 | 3 | 50095.000 | Queda de uso, Downgrade comercial, Renovação automática desligada | Somente validação |
| A-92a3af | 3 | 3 | 34538.000 | Queda de uso, Downgrade comercial, Renovação automática desligada | Somente validação |
| A-d4ac0e | 4 | 3 | 27215.000 | Queda de uso, Baixa satisfação, Renovação automática desligada | Somente validação |
| A-4e631b | 5 | 3 | 24398.000 | Erros de produto, Downgrade comercial, Renovação automática desligada | Somente validação |
| A-bcf87c | 6 | 3 | 13611.000 | Queda de uso, Downgrade comercial, Renovação automática desligada | Somente validação |
| A-bc4d48 | 7 | 3 | 12390.000 | Queda de uso, Escalações de suporte, Renovação automática desligada | Somente validação |
| A-e98302 | 8 | 3 | 9725.000 | Queda de uso, Erros de produto, Renovação automática desligada | Somente validação |
| A-1b707d | 9 | 3 | 9180.000 | Queda de uso, Erros de produto, Renovação automática desligada | Somente validação |
| A-019782 | 10 | 3 | 5169.000 | Erros de produto, Baixa satisfação, Renovação automática desligada | Somente validação |

## Plano de ação

- **1 semana:** colocar eventos fora do ciclo de vida em quarentena analítica, auditar uma amostra das 97 contas com renovação automática desligada e corrigir os vínculos de data.
- **30–90 dias:** instrumentar o ciclo de vida com chaves e relógios confiáveis, acompanhar uma coorte prospectiva e repetir os gates antes de automatizar contato.
- **Medição:** cobertura temporal válida, estabilidade observed/strict e MRR realmente perdido na coorte prospectiva.

## Metodologia e limitações

Painel conta-data de corte, leitura strict para decisão e observed apenas para sensibilidade. As associações não demonstram causalidade; MRR exposto é oportunidade máxima, não receita recuperável.

O modelo preditivo só é publicado quando supera todos os gates fora do tempo. Nesta execução: publish_model=False.
