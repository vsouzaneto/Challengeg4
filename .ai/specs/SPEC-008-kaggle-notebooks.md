---
status: passing
canonical: false
area: benchmarking
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-008 Notebooks Kaggle × briefs dos 4 challenges

Qual `.ipynb` da aba **Code** de cada dataset se encaixa melhor no deliverable. Os briefs em `challenges/*/README.md` continuam canônicos. Esta spec **não** substitui SPEC-001–004.

Fonte da lista: HTML da aba Code de cada dataset, lido em 2026-09-21. Células internas do Kaggle Viewer quase não extraem texto — o julgamento usa **título + input dataset + metadados do kernel** (runtime, outputs, hotness). Onde o slug foi aberto e confirmado, a URL está abaixo. Slug não resolvido = só o título da aba Code.

Nenhum notebook da aba Code cobre sozinho 100% do brief. O “melhor” é o **melhor ponto de partida**, não uma submissão pronta.

---

## 001 — Diagnóstico de Churn

**Aba:** [rivalytics/saas-subscription-and-churn-analytics-dataset/code](https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset/code)

**Brief:** causa raiz cruzando as 5 tabelas; segmentos em risco com contas nomeadas; ações priorizadas com impacto estimado.

### Universo na aba Code

| Notebook | Autor | Hotness | Slug confirmado |
|----------|-------|---------|-----------------|
| Churn_analysis | Rorisang Matunda | 3 | [rorisangmatunda/churn-analysis](https://www.kaggle.com/code/rorisangmatunda/churn-analysis) — input = este dataset; 20s; 1 output |
| SaaS Retention & Revenue Risk Analytics | Bogdana Matrofailo | 1 | [bogdanamatrofailo/saas-retention-revenue-risk-analytics](https://www.kaggle.com/code/bogdanamatrofailo/saas-retention-revenue-risk-analytics) |
| SaaS Activation & 유지 분석 | ggunue | 0 | [ggunue/saas-activation](https://www.kaggle.com/code/ggunue/saas-activation) — input = este dataset; 24s |
| SaaS Data Quality Audit: Why I Rejected 25,000 Row | vangsrivij | 1 | [vangsrivij/saas-data-quality-audit-why-i-rejected-25-000-row](https://www.kaggle.com/code/vangsrivij/saas-data-quality-audit-why-i-rejected-25-000-row) — input = este dataset; 29s |

### Encaixe vs brief

| Notebook | Causa raiz (cruzar 5 tabelas) | Segmentos + contas | Ações + impacto $ | Nota |
|----------|-------------------------------|--------------------|-------------------|------|
| Churn_analysis | possível EDA; título genérico; runtime curto | incerto | incerto | Mais views (562). Bom “olá dados”, fraco como relatório de CEO. |
| **Retention & Revenue Risk** | título aponta retenção + risco | risco de receita | impacto em $ implícito no título | Melhor alinhamento com Q2/Q3 do brief. |
| Activation & 유지 | testa “uso cresceu?” (ativação × permanência) | parcial | fraco | Complemento útil à contradição do CEO; não é o diagnóstico completo. |
| Data Quality Audit | não | não | não | Higiene. Útil **antes** do relatório; rejeitar 25k linhas **não** responde o CEO. |

### Escolha

**SaaS Retention & Revenue Risk Analytics** (Bogdana Matrofailo).

Por quê: o brief pede causa **e** risco **e** impacto estimado. Só este título declara retenção + risco de receita no mesmo artefato. `Churn_analysis` é o mais popular, mas parece EDA curta. `saas-activation` entra como **segundo notebook** se a pergunta “o uso cresceu de verdade?” ainda estiver aberta. O audit de qualidade não compete com o deliverable.

**Ainda falta (mesmo no vencedor):** confirmar joins das 5 tabelas nas células; lista de `account_id` em risco; playbook com dono + $ em risco. SPEC-001 Q1–Q5 continuam o gate.

---

## 002 — Redesign de Suporte

**Aba:** [suraj520/customer-support-ticket-dataset/code](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset/code)

**Brief:** (1) diagnóstico operacional no Dataset 1 — gargalo, CSAT, desperdício em horas; (2) o que automatizar / não automatizar / fluxo; (3) protótipo. Dataset 2 (IT tickets, 8 categorias) **não** aparece como input em nenhum kernel da primeira página.

### Universo (primeira página, Hotness)

| Notebook | Autor | Hotness | Papel aparente |
|----------|-------|---------|----------------|
| **SupportIQ – Customer Support Intelligence Platform** | Hanumathureddygari | 0 | Plataforma; 14 outputs; 54s; [hanumathureddygari/supportiq-customer-support-intelligence-platform](https://www.kaggle.com/code/hanumathureddygari/supportiq-customer-support-intelligence-platform) — input = Dataset 1 |
| Complaint priority system | Rohit Kumar | 12 | Prioridade (classificador) |
| Ticket Sense: Dedup + LLM Cluster Naming | Lucas Henrique Mateo | 0 | Duplicatas + clusters (item do brief) |
| Ticket Classification | raween adel | 0 | Classificador |
| CustomerSupportTickets-EDA | Geeta Basker | 6 | EDA; [geetabasker/customersupporttickets-eda](https://www.kaggle.com/code/geetabasker/customersupporttickets-eda) — 19s, 0 outputs |
| EDA-data understanding and visualization | Esraa Emad | 1 | EDA |
| AgentNet Self-Correcting Enterprise Support Agent | RajaGanapathy | 3 | Agente / protótipo |
| ticket classfication / LSTM_ticket3 / Ticket | vários | 1–4 | Classificador texto |
| Ticket Priority Classifier | Harry Keys | 5 | Prioridade |
| Auto Tagging Support Tickets Using LLM | Awais Azam | 4 | Tagging |
| Customer Support Ticket Bot | Rigved Shirvalkar | 2 | Bot |
| Gen AI Capstone - Customer Support RAG Bot | Sujata Kaushal | 2 | Respostas sugeridas (RAG) |
| Analyzing Customer Satisfaction Rate | El-Hussien Ahmed El-Sokkary | 9 | CSAT (Q “o que impacta satisfação?”). Slug não resolvido nesta leitura |
| Customer Support Ticket Analysis For BIAS | Pankaj Mishra | 2 | Viés, não ops |

### Encaixe vs brief

| Obrigatório | Melhor kernel isolado | Cabe no vencedor? |
|-------------|----------------------|-------------------|
| Gargalos canal × prioridade × tipo | EDA (Geeta / Esraa) | Incerto — SupportIQ tem ToC e 14 outputs; células não lidas |
| Drivers de CSAT | Analyzing Customer Satisfaction Rate | Incerto |
| Horas / custo desperdiçado | nenhum título declara | Provável gap |
| O que automatizar / não | SupportIQ (plataforma) | Parcial |
| Fluxo ticket → IA → humano | SupportIQ / AgentNet / RAG Bot | Parcial |
| Protótipo | SupportIQ (14 artifacts) ou RAG / Dedup / Priority | Sim, se os outputs rodarem |
| Dataset 2 (48k textos, 8 tópicos) | **nenhum na lista** | Gap |

### Escolha

**SupportIQ – Customer Support Intelligence Platform** (Hanumathureddygari).

Por quê: único kernel cujo título cobre inteligência operacional **e** artefato executável. Runtime 54s + 14 arquivos de output = mais substância que EDA de 19s. Classificadores (priority, LSTM, tagging) cobrem só o diferencial de protótipo. `Analyzing Customer Satisfaction Rate` (hotness 9) e `CustomerSupportTickets-EDA` (hotness 6) são os melhores **complementos** da parte 1.

**Ainda falta:** Dataset 2 no treino/teste do classificador; quantificar horas e custo; escrever o que **não** automatizar com exemplos do CSV; fluxo explícito humano-no-loop. Classificador “100% automático” é red flag no brief.

---

## 003 — Lead Scorer

**Aba:** [agungpambudi/crm-sales-predictive-analytics/code](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics/code)

**Brief:** ferramenta que o vendedor usa (não notebook órfão); scoring além de ordenar por valor; explicação do score; setup + limitações.

### Universo na aba Code

| Notebook | Autor | Hotness | Slug confirmado |
|----------|-------|---------|-----------------|
| **0.2 Do CRM Fields Actually Predict Deal Outcomes?** | Vladimir Belsch | 0 | [vladimirbelsch/0-2-do-crm-fields-actually-predict-deal-outcomes](https://www.kaggle.com/code/vladimirbelsch/0-2-do-crm-fields-actually-predict-deal-outcomes) — input = este dataset; 28s; 0 outputs |
| BitNet: Faster Inference Framework for 1-Bit LLM | Agung Pambudi | 33 | Fora de escopo — LLM 1-bit; dataset só como input colateral |

### Encaixe vs brief

| Requisito | Este notebook | BitNet |
|-----------|---------------|--------|
| Usa `accounts` / `pipeline` / `teams` / `products` | Sim (input = dataset CRM) | Não (tema errado) |
| Lógica de scoring (não só close_value) | Sim — pergunta se campos predizem Won/Lost | Não |
| Explicabilidade (por que score alto/baixo) | Provável (teste de campos) | Não |
| App / CLI / dashboard / API usável | **Não** — notebook 28s, 0 outputs | Não |
| Filtro vendedor / manager / região | Não declarado | Não |

### Escolha

**0.2 Do CRM Fields Actually Predict Deal Outcomes?** (Vladimir Belsch).

Por quê: é o **único** `.ipynb` da aba que trata win/loss a partir dos campos do CRM. BitNet não compete. A Head de RevOps pediu ferramenta, não Jupyter — este kernel é a **base da lógica**, não a entrega. Empacotar em Streamlit/API/CLI com “por que este deal” é o trabalho do challenge.

**Ainda falta:** UI para o vendedor; score explicável por oportunidade aberta (Prospecting/Engaging, não só Won/Lost histórico); filtro por agent/manager/regional_office.

---

## 004 — Estratégia Social Media

**Aba:** [omenkj/social-media-sponsorship-and-engagement-dataset/code](https://www.kaggle.com/datasets/omenkj/social-media-sponsorship-and-engagement-dataset/code)

**Brief:** o que gera engagement (além de “vídeo > imagem”); patrocínio vs orgânico com controle; audiência; o que não funciona; estratégia + política de sponsor + quick wins.

### Universo na aba Code

| Notebook | Autor | Hotness | Slug |
|----------|-------|---------|------|
| social-media-engagement-analyser | Swayam Agrahari | 1 | Listado na aba; slug `/code/<user>/…` **não** resolvido nesta leitura (404 em `swayamagrahari` e `swayam`) |

Um kernel só. Não há segundo candidato na aba.

### Encaixe vs brief

| Obrigatório | Esperado neste título | Risco |
|-------------|----------------------|-------|
| Engagement por plataforma / tipo / categoria / faixa de creator | Sim (analyser) | Pode parar na média por plataforma (tabela 1 do brief) |
| Orgânico vs `is_sponsored` com controle | Incerto — título não cita sponsor | Gap mais provável |
| Perfil de audiência | Incerto | Gap |
| O que NÃO funciona | Incerto | Gap |
| Estratégia + threshold de sponsor + quick wins | Notebook de análise ≠ memo executivo | Gap |
| Diferencial (modelo / dashboard / hashtags / cluster) | Incerto | — |

### Escolha

**social-media-engagement-analyser** (Swayam Agrahari) — único `.ipynb` da aba.

Abrir pela [aba Code](https://www.kaggle.com/datasets/omenkj/social-media-sponsorship-and-engagement-dataset/code). Sem alternativa no Kaggle deste dataset.

**Ainda falta:** comparação patrocinado vs orgânico **controlando** creator size + plataforma + categoria; o que parar de fazer; política com threshold; algo recorrente (dashboard ou modelo). Sem isso a banca lê “baseline de IA”.

---

## Resumo

| Challenge | Melhor `.ipynb` na aba Code | URL | Não escolhido (e por quê) |
|-----------|----------------------------|-----|---------------------------|
| 001 churn | SaaS Retention & Revenue Risk Analytics | [bogdanamatrofailo/saas-retention-revenue-risk-analytics](https://www.kaggle.com/code/bogdanamatrofailo/saas-retention-revenue-risk-analytics) | `Churn_analysis` = EDA popular; `saas-activation` = complemento “uso cresceu”; audit = higiene |
| 002 support | SupportIQ – Customer Support Intelligence Platform | [hanumathureddygari/supportiq-…](https://www.kaggle.com/code/hanumathureddygari/supportiq-customer-support-intelligence-platform) | Classificadores = só proto; EDA/CSAT = só parte 1; nenhum usa Dataset 2 |
| 003 lead | 0.2 Do CRM Fields Actually Predict Deal Outcomes? | [vladimirbelsch/0-2-do-crm-fields-…](https://www.kaggle.com/code/vladimirbelsch/0-2-do-crm-fields-actually-predict-deal-outcomes) | BitNet = LLM, não CRM |
| 004 social | social-media-engagement-analyser | [aba Code do dataset](https://www.kaggle.com/datasets/omenkj/social-media-sponsorship-and-engagement-dataset/code) | Não há segundo kernel |

Cópia local adaptada (001): [notebook-data-001-churn/04_ANALISE_retention/saas-retention-revenue-risk-analytics.ipynb](../../notebook-data-001-churn/04_ANALISE_retention/saas-retention-revenue-risk-analytics.ipynb) — path Kaggle removido; carga via Delta do Lab 01 ou `dados/*.csv`.

Cópia local adaptada (002): [notebook-process-002-support/04_ANALISE_supportiq/supportiq-customer-support-intelligence-platform.ipynb](../../notebook-process-002-support/04_ANALISE_supportiq/supportiq-customer-support-intelligence-platform.ipynb) — path Kaggle / kagglehub removidos; carga via Delta do Lab 01 ou `dados/customer_support_tickets.csv`.

Cópia local adaptada (003): [notebook-build-003-lead-scorer/04_ANALISE_crm/0-2-do-crm-fields-actually-predict-deal-outcomes.ipynb](../../notebook-build-003-lead-scorer/04_ANALISE_crm/0-2-do-crm-fields-actually-predict-deal-outcomes.ipynb) — path Kaggle removido; carga via Delta do Lab 01 ou `dados/*.csv`.

Cópia local adaptada (004): [notebook-marketing-004-social/04_ANALISE_social/social-media-engagement-analyser.ipynb](../../notebook-marketing-004-social/04_ANALISE_social/social-media-engagement-analyser.ipynb) — path Kaggle removido; carga via Delta do Lab 01 ou `dados/social_media_dataset.csv`.

Copiar o notebook vencedor **não** passa o gate de process log nem o de “superar o baseline”. Serve para não recomeçar o EDA do zero.

## Verificação

- [x] Cada aba Code oficial foi lida (2026-09-21).
- [x] Winner de 001, 002 e 003 tem URL de kernel que abre.
- [x] 004: um kernel na aba; slug direto 404 nesta leitura.
- [ ] Células/outputs dos winners não foram reexecutados localmente.

## Evidência

2026-09-21: fetch das URLs `/code` dos quatro datasets + páginas de kernel confirmadas acima. Briefs: `challenges/data-001-churn`, `process-002-support`, `build-003-lead-scorer`, `marketing-004-social`.

## Sucesso / falha

- Sucesso: candidato parte do kernel da tabela e completa os gaps (contas, horas, UI, sponsor controlado).
- Falha: entregar o notebook Kaggle sem cruzar tabelas / sem ferramenta / sem política de patrocínio.
