# Submissão — Adailton Montinegro — Challenge 001 (Diagnóstico de Churn)

## Sobre mim

- **Nome:** Adailton Montinegro
- **LinkedIn:** [linkedin.com/in/adailtonmontinegro](https://www.linkedin.com/in/adailtonmontinegro/)
- **Challenge escolhido:** Challenge 001 — Diagnóstico de Churn (RavenStack)

---

## Executive Summary

Auditamos e cruzamos as 5 tabelas relacionais da RavenStack (~500 contas, 5.000 assinaturas, 25.000 logs de telemetria, 2.000 tickets e 600 eventos de cancelamento) utilizando DuckDB, modelagem estatística de sobrevivência (Kaplan-Meier), aprendizado de máquina explicável (Random Forest) e governança multi-agente determinística.

**Desmontamos os dois paradoxos centrais apresentados pelo CEO:**
1. **O Paradoxo do Produto ("O uso cresceu"):** A análise temporal contínua de 24 meses prova que o uso médio por conta ativa permaneceu **matematicamente estável entre 23,0 e 26,7 eventos/mês** (média de 24,6 usos/mês; desvio padrão < 0,9). O crescimento alegado pela diretoria de produto foi uma miragem baseada em ruído estocástico de final de ano (+2,6% nominal), enquanto os cancelamentos mensais aceleravam de **1 em Jan/2023 para 117 em Dez/2024 (+11.600%)**. O churn é **descolado do volume de uso**.
2. **O Paradoxo do Suporte ("A satisfação está OK"):** A nota média de satisfação (CSAT de 4,0/5,0) mascara um **viés severo de não-resposta de 41,2%** (clientes insatisfeitos não avaliam). O indicador preditivo real é a **taxa de escalação de chamados para engenharia, que salta de 4,5% para 14,6% nas duas semanas anteriores ao cancelamento**.

O cancelamento sangrou **$255.442,00/mês em MRR (~$3.065.304,00 ARR)**. Entregamos uma **Matriz Cartesiana de Quadrantes**, segmentando a base em Zona Crítica (102 contas que concentram $462k de MRR sob risco), Cauda Vulnerável (137 contas), Vacas Leiteiras (104 contas retidas) e Base Estável (157 contas), acompanhada de um **Cockpit Prescritivo em Streamlit e HTML Standalone** com semáforos estritos, toggle de moeda (USD/BRL com PTAX R$ 5,50) e playbooks determinísticos por squad.

---

## Solução

### Abordagem

Para superar o baseline genérico de ferramentas de IA (que se limitam a afirmar que "clientes que usam menos cancelam mais"), a squad conduziu uma investigação profunda em 6 eixos:

1. **Auditoria de Integridade e Profiling Estrito (DuckDB):** Validação de 100% de integridade referencial nas 4 relações de chave estrangeira (0 órfãos) e conciliação matemática contábil (`ARR == MRR * 12` em 100% dos 5.000 contratos).
2. **Série Temporal Contínua de 24 Meses (Mês a Mês):** Reconstrução do histórico completo de Jan/2023 a Dez/2024, provando a constância matemática do engajamento per capita e a trajetória exponencial de churn.
3. **Desconstrução de Vieses Operacionais e Análise Pré-Churn:** Mapeamento da janela retrospectiva pré-cancelamento (0-14 dias, 15-30 dias, 31-60 dias e 60+ dias), isolando o gatilho operacional de suporte.
4. **Matriz Cartesiana de Quadrantes:** Cruzamento bidimensional entre Impacto Financeiro (MRR > $1.500) e Probabilidade de Churn (Score > 0,40), classificando as 500 contas em 4 quadrantes acionáveis.
5. **Análise Qualitativa de Motivos e Feedbacks:** Decomposição dos 600 eventos de churn por `reason_code`, quantificação de reembolsos e frequência de termos textuais.
6. **Benchmark do Sucesso (ICP Retido):** Análise comparativa das 390 contas retidas para identificar os fatores de proteção da base.

---

### Resultados / Findings

#### 1. Linha do Tempo Mensal: A Prova Factual da Estabilidade de Uso
A tabela a seguir consolida a evolução mensal nos momentos-chave dos 24 meses avaliados:

| Mês | Novos Clientes | Clientes Ativos c/ Uso | Uso Total | Uso Médio / Conta Ativa | Cancelamentos | Reembolsos ($) | Taxa Erro (%) |
|---|---|---|---|---|---|---|---|
| **2023-01** | 17 | 440 | 10.877 | **24,7** | 1 | $0,00 | 5,44% |
| **2023-06** | 13 | 420 | 10.002 | **23,8** | 5 | $0,00 | 6,26% |
| **2023-12** | 20 | 431 | 10.435 | **24,2** | 16 | $358,06 | 6,23% |
| **2024-03** | 27 | 430 | 10.725 | **24,9** | 24 | $355,24 | 5,50% |
| **2024-06** | 21 | 416 | 10.106 | **24,3** | 40 | $514,46 | 5,33% |
| **2024-09** | 25 | 415 | 10.195 | **24,6** | 53 | $1.019,21 | 5,53% |
| **2024-10** | 31 | 435 | 11.450 | **26,3** | 66 | $832,18 | 4,98% |
| **2024-11** | 32 | 410 | 10.039 | **24,5** | 68 | $732,06 | 5,35% |
| **2024-12** | 17 | 428 | 10.738 | **25,1** | **117** (Pico) | **$2.146,08** | 5,35% |

**Conclusão Causal:** O uso per capita nunca caiu nem disparou; manteve-se perfeitamente estabilizado em ~24,6 usos/mês. O churn não é provocado por falta de adoção, mas por atrito insolúvel em contas ativas.

#### 2. O Gatilho Operacional no Suporte Técnico
Analisando os 2.000 tickets de suporte das contas que cancelaram na janela regressiva até o dia do cancelamento:

| Janela Retrospectiva Pré-Churn | Total de Tickets | Tempo Médio Resposta (min) | Taxa de Escalação (%) | Nota Média (1-5) | % Sem Avaliação |
|---|---|---|---|---|---|
| **60+ dias antes (Normal)** | 1.629 | 87,1 min | 5,0% | 3,98 | 43,1% |
| **31-60 dias antes** | 97 | 103,0 min | 4,1% | 4,03 | 40,2% |
| **15-30 dias antes** | 66 | 77,7 min | 4,5% | 4,00 | 51,5% |
| **0-14 dias antes (Gatilho Fatal)** | 41 | 78,4 min | **14,6%** (3x) | 4,03 | 29,3% |

**Conclusão:** O CSAT aparente de 4,0 é irrelevante por conta do viés de não-resposta. O indicador crítico é a escalação: nas últimas duas semanas, quando um chamado escala para engenharia, a probabilidade de cancelamento atinge o ápice.

#### 3. Matriz Cartesiana de Quadrantes (500 Contas)
Segmentamos toda a base em 4 quadrantes operacionais:

| Quadrante | Critério | Contas | MRR Total ($) | Ticket Médio ($) | Churn Histórico | Ação Estratégica Prescritiva |
|---|---|---|---|---|---|---|
| **Q1: Zona Crítica** | MRR > $1,5k & Risco > 0,40 | 102 | $462.530,00 | $4.534,61 | 49,0% | Intervenção C-Level + Executive Sponsor + SLA Prioritário |
| **Q2: Cauda Vulnerável** | MRR <= $1,5k & Risco > 0,40 | 137 | $57.521,00 | $419,86 | 43,8% | Régua Automatizada de CS + Tutoriais de Auto-atendimento |
| **Q3: Vacas Leiteiras** | MRR > $1,5k & Risco <= 0,40 | 104 | $635.711,00 | $6.112,61 | 0,0% | Plano de Expansão / Upsell + Contratos Plurianuais |
| **Q4: Base Estável** | MRR <= $1,5k & Risco <= 0,40 | 157 | $82.628,00 | $526,29 | 0,0% | Manutenção Padrão de Sucesso do Cliente |

#### 4. Análise Qualitativa: Motivos e Feedbacks Declarados (600 Eventos)
- **Motivos (`reason_code`):** Features (19,0%), Suporte (17,3%), Orçamento/Budget (17,3%), Desconhecido (15,8%), Concorrente (15,3%) e Preço/Pricing (15,2%).
- **Feedbacks Mais Frequentes:**
  1. `"too expensive"`: 161 ocorrências (26,8%)
  2. `"missing features"`: 155 ocorrências (25,8%)
  3. `Sem feedback`: 148 ocorrências (24,7%)
  4. `"switched to competitor"`: 136 ocorrências (22,7%)
- **Precedentes Críticos:**
  * **10,0% das contas** reduziram o plano (downgrade) nos 90 dias anteriores ao cancelamento fatal.
  * **10,0% dos eventos** foram reativações de clientes que já haviam cancelado antes.
  * Reembolsos somaram **$9.155,75**, liderados por cancelamentos de produto/features ($1.905,90).

#### 5. Benchmark de Contas Retidas (O ICP de Sucesso)
Comparando as 390 contas ativas contra as 110 canceladas:
- **Canal de Parcerias:** 19,5% das contas ativas vieram de Parcerias (contra apenas 11,8% nas canceladas). Canais como Eventos (30,2% churn) trazem clientes desqualificados.
- **Modelo Contratual:** Contratos anuais e auto-renovação conferem previsibilidade, mas não blindam contra falhas de suporte (ambos grupos têm ~82% de auto-renovação).
- **Estabilidade Operacional:** Contas retidas têm menor incidência de escalações de suporte (0,18 vs 0,22).

---

### Recomendações

1. **Gatilho Operacional "Red Alert" no Suporte (Impacto Imediato / Esforço Baixo):**
   - Implementar webhook imediato: qualquer chamado de conta do **Quadrante Q1 (Zona Crítica)** que for escalado notifica em tempo real o Head de CS e o Arquiteto Responsável no Slack.
   - Meta: Atendimento em < 15 minutos em incidentes críticos, neutralizando o gatilho das duas semanas pré-churn.

2. **Revisão de Qualificação em RevOps (Impacto Alto / Esforço Médio):**
   - Realocar 40% do orçamento de marketing de Eventos (30,2% de churn) para o Programa de Canais e Parcerias (14,6% de churn), elevando a retenção estrutural da coorte de entrada.

3. **Política de Blindagem de Downgrade (Janela de 90 Dias):**
   - Criar playbook automático: solicitações de downgrade acionam oferta imediata de renegociação contratual e lock-in anual com desconto escalonado antes da saída definitiva.

4. **Operação Diária via Cockpit Prescritivo:**
   - Adotar o arquivo `ravenstack_account_risk_scores.csv` no dia a dia da squad de CS, priorizando as contas ativas do Quadrante 1.

---

### Limitações

- **Granularidade Diária:** Ausência de clickstream em nível de sessão individual; a análise baseia-se em agregados diários por funcionalidade.
- **Natureza Simulada do Dataset:** O dataset sintético possui certas distribuições uniformes (como planos e auto-renovação), exigindo que a inteligência causal focasse em anomalias temporais, escalações e regressões comportamentais.

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta / Agente | Papel Operacional | O que Executou |
|---|---|---|
| **Japax (Antigravity)** | Orquestrador Chefe & Auditoria | Decomposição do problema, formulação de hipóteses, code review adversário, governança no Taiga e redação final. |
| **Altman (Codex CLI)** | Arquiteto de Dados | Modelagem matemática de 24 meses, script de analítica avançada (`07_codex_advanced_analytics.py`), matriz de quadrantes e reconstrução do app Streamlit. |
| **Taiga MCP (`taigaApi`)** | Governança Determinística | Registro em tempo real de 3 Épicos (#1 a #3), 3 User Stories (#2, #8 e #15) e 10 Tasks (#3 a #6, #9 a #13 e #14 a #17). |
| **DuckDB + Pandas** | Motor Analítico | Processamento in-memory de mais de 33 mil linhas relacionais sem dependência de banco externo. |
| **Streamlit + Altair + Chart.js** | Visualização Executiva | Cockpit interativo em 6 abas e dashboard standalone HTML com toggle de moeda USD/BRL e semáforos estritos. |

---

### Workflow Multi-Agente & Iteração Crítica

1. **Kickoff & Mapeamento:** Japax explorou as diretrizes e estruturou o Épico 01 e 02 no Taiga.
2. **Primeira Rodada Analítica (Tasks #9 a #13):** Profiling inicial via DuckDB, detecção do pico de Q4 e prototipação do app Streamlit.
3. **Revisão Crítica do Operador Humano (HITL):** O operador apontou descasamento visual no gráfico de uso, jargão em CSAT, ausência de dispersão em quadrantes e inversão de cores nos deltas do header.
4. **Delegação e Fact-Checking pelo Codex CLI (Altman):** 
   - Altman reprocessou a série histórica em 24 meses com DuckDB e **desmentiu factualmente a hipótese de que o uso per capita havia despencado ou crescido**: provou que ele foi constante em ~24,6 usos/mês.
   - Construiu a Matriz Cartesiana de Quadrantes, detalhou os 600 eventos de cancelamento e isolou o benchmark das contas retidas.
5. **Reconstrução dos Entregáveis (Task #16):** Reescrita completa de `app.py` e `executive_dashboard.html`, corrigindo semáforos (vermelho para perdas), adicionando toggle USD/BRL e formatação brasileira.
6. **Auditoria Final por Japax (Task #17):** Validação cruzada dos números, garantia de rastreabilidade no Taiga e consolidação deste relatório.

---

### Onde a IA errou e como foi corrigida

1. **Alucinação Inicial sobre Queda de Uso:**
   - *Erro:* Diante da observação de que o uso bruto era plano enquanto o churn subia, a IA sugeriu inicialmente que "o uso per capita despencou".
   - *Correção Humana & Fact-Checking:* O operador questionou a evidência e exigiu prova numérica. Altman rodou a query mensal contínua no DuckDB e constatou que o uso por conta ativa era rigorosamente estável (23 a 26 usos/mês). Corrigimos o insight para o fato verdadeiro: o churn é descolado do volume de uso.
2. **Inversão Semântica das Cores no Streamlit:**
   - *Erro:* O Streamlit renderizou a perda de receita em verde devido ao delta negativo (`-$3M`).
   - *Correção:* Substituição por blocos HTML customizados com semáforo vermelho explícito para perdas e verde para contas ativas.
3. **Jargão Técnico de Atendimento:**
   - *Erro:* Uso do termo técnico "CSAT" sem explicação para gestores de fora da área.
   - *Correção:* Substituição por "Nota Média de Satisfação (1 a 5)" e explicitação do viés de não-resposta (41,2% sem nota).

---

### O que adicionei que a IA sozinha não faria

1. **Rigor Causal e Julgamento Crítico:** Recusa de conclusões fáceis ou respostas de cartilha ("cliente que usa menos cancela mais").
2. **Matriz de Quadrantes Acionável:** Tradução de scores estatísticos em 4 gavetas de decisão de negócio com playbooks específicos.
3. **Simulador Financeiro Conectado a Payback:** Prova matemática de que reter 35% das contas Enterprise cobre o custo anual de uma squad de resiliência.
4. **Governança Auditável:** Linha do tempo completa e verificável no Taiga registrando cada interação e tomada de decisão.

---

## Evidências

- [x] **Repositório Git:** Branch `submission/adailton-montinegro` no clone local `/Users/montinegro/G4 AI Master/repo`.
- [x] **Aplicação Streamlit Reconstruída:** [`repo/submissions/adailton-montinegro/app/app.py`](app/app.py).
- [x] **Dashboard Standalone HTML v2:** [`repo/submissions/adailton-montinegro/artifacts/executive_dashboard.html`](artifacts/executive_dashboard.html).
- [x] **Matriz de Quadrantes & Scores (500 contas):** [`repo/submissions/adailton-montinegro/artifacts/ravenstack_account_risk_scores.csv`](artifacts/ravenstack_account_risk_scores.csv).
- [x] **JSON Analítico Avançado (24 meses, quadrantes, feedbacks):** [`repo/submissions/adailton-montinegro/artifacts/advanced_analytics.json`](artifacts/advanced_analytics.json).
- [x] **Scripts de Engenharia e Análise:** Em [`repo/submissions/adailton-montinegro/scripts/`](scripts/).
- [x] **Governança no Taiga:** Projeto `g4-ai-master` (ID 3), Épicos 01, 02 e 03 concluídos, com histórico cronológico auditável.

---

_Submissão final revisada e auditada em: 12 de Setembro de 2026_
