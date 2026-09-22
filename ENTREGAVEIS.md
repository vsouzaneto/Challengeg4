# Entregáveis — onde está no lab

Os briefs abaixo são o contrato. A implementação no Databricks (Lab 03) é o artefato que o executivo / vendedor abre depois do Lab 01:

| Challenge | Notebook | Dashboard AI/BI | Kernel de partida (SPEC-008) |
| --- | --- | --- | --- |
| 001 churn | [notebook-data-001-churn/03_LAB_Dashboard/lab03_dashboard.ipynb](notebook-data-001-churn/03_LAB_Dashboard/lab03_dashboard.ipynb) | [lab-001-churn-ceo](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611c23d1c1d8abb2e1d9847d535/published?o=7474644277755368) | Retention & Revenue Risk → Lab 04 |
| 002 support | [notebook-process-002-support/03_LAB_Dashboard/lab03_dashboard.ipynb](notebook-process-002-support/03_LAB_Dashboard/lab03_dashboard.ipynb) | [lab-002-support-ops](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611c9d4161bac29737cf1c07d47/published?o=7474644277755368) | SupportIQ → Lab 04 |
| 003 lead | [notebook-build-003-lead-scorer/03_LAB_Dashboard/lab03_dashboard.ipynb](notebook-build-003-lead-scorer/03_LAB_Dashboard/lab03_dashboard.ipynb) | [lab-003-crm-seller](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611cd0118a78e40dc8a5f8a3609/published?o=7474644277755368) | CRM fields × outcomes → Lab 04 (lógica; a ferramenta é o Lab 03) |
| 004 social | [notebook-marketing-004-social/03_LAB_Dashboard/lab03_dashboard.ipynb](notebook-marketing-004-social/03_LAB_Dashboard/lab03_dashboard.ipynb) | [lab-004-social-media](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611d0801412b387d62b0dc4d8d6/published?o=7474644277755368) | Engagement analyser → Lab 04 |

Jobs: 01 → 02 → **03 dashboard** → 04. Spec: [SPEC-014-lab-03-entregaveis.md](.ai/specs/SPEC-014-lab-03-entregaveis.md).

---

# CONTEXTO ai-master-challenge\challenges\data-001-churn

Verifique qual projeto .ipynb disponível https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset/code se encaixa melhor na necessidade:

Deliverable principal

Um relatório de diagnóstico respondendo:

O que está causando o churn? Não a resposta óbvia — a causa raiz. Cruze os dados entre tabelas.

Quais segmentos estão mais em risco? Com dados, não feeling. Identifique contas específicas.

O que a empresa deveria fazer? Ações concretas, priorizadas, com impacto estimado.

----

# CONTEXTO ai-master-challenge\challenges\process-002-support

Verifique qual projeto .ipynb disponível https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset/code se encaixa melhor na necessidade:

1. Diagnóstico operacional (obrigatório)

Com base no Dataset 1, identifique com dados:

Onde o fluxo trava? Gargalos por canal, prioridade, tipo de ticket. Quais combinações geram os piores tempos de resolução?

O que impacta satisfação? Quais variáveis mais influenciam o Customer Satisfaction Rating? É o tempo de resposta? O canal? O tipo de problema?

Quanto estamos desperdiçando? Quantifique em horas e, se possível, estime custo. Onde está o maior desperdício recuperável?

2. Proposta de automação com IA (obrigatório)

Com base em ambos os datasets, proponha:

O que automatizar — Classificação automática, roteamento inteligente, respostas sugeridas, triagem de prioridade, detecção de duplicatas — o que fizer sentido com base nos dados.

O que NÃO automatizar — Nem tudo deve ser delegado para IA. Quais tipos de ticket exigem julgamento humano? Justifique com exemplos dos dados.

Como funcionaria na prática — Descreva o fluxo proposto: ticket entra → o que acontece em cada etapa → onde IA atua → onde humano intervém.

3. Protótipo funcional (diferencial)

Construa algo que demonstre que sua proposta funciona. Exemplos:

Um classificador de tickets que recebe texto e retorna categoria + confiança

Um sistema de respostas sugeridas baseado em tickets similares

Um roteador automático que categoriza e prioriza tickets novos

Um dashboard que mostra os gargalos em tempo real

Qualquer coisa funcional que demonstre a automação proposta

----

# CONTEXTO ai-master-challenge\challenges\build-003-lead-scorer

Verifique qual projeto .ipynb disponível https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics/code se encaixa melhor na necessidade:

1. Solução funcional (obrigatório)

Construa algo que um vendedor possa usar. Não importa a tecnologia — importa que funcione.

Exemplos de soluções válidas:

Aplicação web (Streamlit, React, HTML+JS, qualquer coisa)

Dashboard interativo (Plotly Dash, Retool, Metabase)

CLI tool ou script que gera relatório priorizados

API que recebe dados de um deal e retorna score + explicação

Planilha inteligente com fórmulas de scoring

Bot que envia prioridades por Slack/email

Requisitos mínimos:

Precisa rodar (não é mockup, wireframe ou PowerPoint)

Precisa usar os dados reais do dataset

Precisa ter lógica de scoring/priorização (não é só ordenar por valor)

O vendedor precisa entender por que um deal tem score alto ou baixo

2. Documentação mínima (obrigatório)

Setup: Como rodar a solução (dependências, comandos, URL)

Lógica: Que critérios de scoring você usou e por quê

Limitações: O que a solução não faz e o que precisaria pra escalar

3. Process log (obrigatório)

Evidências de como você usou IA para construir. Leia o Guia de Submissão.

Este challenge é especialmente interessante para quem usa "vibe coding" — Cursor, Claude Code, Replit Agent, v0, etc. Mostre o processo.

----

# CONTEXTO ai-master-challenge\challenges\marketing-004-social

Verifique qual projeto .ipynb disponível https://www.kaggle.com/datasets/omenkj/social-media-sponsorship-and-engagement-dataset/code se encaixa melhor na necessidade:

1. Análise de performance (obrigatório)

Responda com dados — não com achismo:

O que gera engajamento? Por plataforma, tipo de conteúdo, categoria, tamanho de creator. Vá além do óbvio ("vídeos performam melhor que imagens" não é insight).

Patrocínio funciona? Compare orgânico vs. patrocinado em engagement rate, alcance, custo implícito. Em que condições patrocinar vale a pena? Com que tipo de influenciador?

Qual o perfil de audiência que mais engaja? Existe diferença por plataforma? Por tipo de conteúdo? Por categoria?

O que NÃO funciona? Tão importante quanto saber o que funciona.

2. Estratégia recomendada (obrigatório)

Com base na análise, recomende:

Onde concentrar esforço? Qual plataforma, tipo de conteúdo, frequência de postagem, faixa de creator.

Política de patrocínio. Patrocinar ou não? Em que condições? Com que perfil de influenciador? Qual o threshold de seguidores/engagement que justifica investimento?

O que parar de fazer. Identifique investimentos com baixo retorno baseado nos dados.

Quick wins. O que pode ser implementado esta semana com base nos findings.

3. Algo a mais (diferencial)

Nos surpreenda. Caminhos possíveis:

Modelo preditivo de engagement (input: características do post → output: engagement estimado)

Dashboard interativo para o time de social media acompanhar performance

Gerador de recomendações de conteúdo baseado em padrões dos top performers

Análise de hashtags — quais combinações correlacionam com alto engagement?

Segmentação de audiência com clustering

Qualquer coisa que transforme dados em decisão recorrente

----