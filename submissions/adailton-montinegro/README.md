# Submissão — Adailton Montinegro — Challenge 001 (Diagnóstico de Churn)

## Sobre mim

- **Nome:** Adailton Montinegro
- **LinkedIn:** [linkedin.com/in/adailtonmontinegro](https://www.linkedin.com/in/adailtonmontinegro/)
- **Challenge escolhido:** Challenge 001 — Diagnóstico de Churn (RavenStack)

---

## Executive Summary

Auditamos e cruzamos as 5 tabelas relacionais da RavenStack (~500 contas, 5.000 assinaturas, 25.000 logs de telemetria, 2.000 tickets e 600 eventos de cancelamento) utilizando DuckDB, análise de sobrevivência (Kaplan-Meier) e aprendizado de máquina explicável. 

Desmontamos o paradoxo apresentado pelo CEO: o uso aparente da plataforma bateu recorde no 4º trimestre de 2024 (32.227 eventos) devido a uma ilusão de agregação gerada pela entrada rápida de contas com onboarding intenso que cancelam em poucas semanas (67.5% da coorte 2024-Q4 cancelou), enquanto o CSAT de 4.0/5.0 mascara um viés severo de não-resposta (41.2% dos tickets sem nota). 

O sinal predecessor letal de cancelamento é operacional: **a taxa de escalação em tickets de suporte salta de 4.5% para 14.6% nas duas semanas imediatamente anteriores ao churn**. O cancelamento sangrou **$255.442/mês em MRR (~$3.06M ARR)**, com 72.6% da perda concentrada em planos Enterprise e Pro. Entregamos um Cockpit Prescritivo em Streamlit e HTML interativo que rankeia contas em risco e aciona playbooks determinísticos, projetando preservação de mais de $393k em ARR anual no primeiro ano.

---

## Solução

### Abordagem

Para superar o baseline genérico de ferramentas de IA (que se limitam a afirmar que "clientes que usam menos cancelam mais"), adotamos uma abordagem de **Engenharia de Dados e Investigação Causal em 5 fases**:

1. **Auditoria de Integridade e Profiling Estrito (DuckDB):** Validação de integridade referencial em todas as chaves primárias e estrangeiras (0 órfãos), conciliação matemática de faturamento (`ARR == MRR * 12` em 100% dos registros) e mapeamento de missing values.
2. **Decomposição Temporal e Coortes de Sobrevivência:** Análise de coortes por trimestre de aquisição e estimação da função de sobrevivência de Kaplan-Meier para mapear a tenure real até o ponto de inflexão de abandono.
3. **Desconstrução de Vieses Operacionais:** Isolamento do Paradoxo de Simpson no volume de uso e auditoria de viés de sobrevivente no CSAT de suporte técnico.
4. **Modelagem Preditiva com Explicabilidade (Random Forest + Feature Importance):** Engenharia de 28 features multidimensionais para cálculo de probabilidade calibrada de churn e ranking de importância de atrito.
5. **Cockpit Prescritivo Operacional (Streamlit + HTML Standalone):** Tradução dos achados analíticos em ferramenta de ação diária para Customer Success e CEO.

---

### Resultados / Findings

#### 1. A Anatomia do Churn: O Ponto de Inflexão em 2024-Q4
A perda de clientes não ocorreu de forma linear. Entre 2023-Q1 e 2023-Q3, a empresa operou com churn residual (6 a 19 eventos/trimestre). No entanto, a partir de 2024-Q1 o churn acelerou vertiginosamente, culminando em **251 cancelamentos em 2024-Q4 (41.8% de todo o churn dos 2 anos)**.

| Trimestre | Eventos de Churn | Contas Únicas | Reembolsos Solicitados ($) | Uso Total de Features | Taxa de Erro (%) |
|-----------|------------------|---------------|----------------------------|-----------------------|------------------|
| 2023-Q1   | 6                | 6             | $0.00                      | 31,400                | 5.72%            |
| 2023-Q2   | 11               | 11            | $38.15                     | 31,128                | 6.00%            |
| 2023-Q3   | 19               | 17            | $70.81                     | 31,155                | 5.45%            |
| 2023-Q4   | 37               | 36            | $658.57                    | 30,878                | 5.60%            |
| 2024-Q1   | 54               | 50            | $681.52                    | 31,593                | 5.70%            |
| 2024-Q2   | 92               | 77            | $990.30                    | 30,789                | 5.71%            |
| 2024-Q3   | 130              | 107           | $2,502.58                  | 31,355                | 5.66%            |
| 2024-Q4   | **251**          | **180**       | **$3,710.32**              | **32,227** (Recorde)  | 5.22%            |

#### 2. Desmontando a Afirmação de Produto: "O uso cresceu"
- O volume total de eventos de fato atingiu a máxima histórica em 2024-Q4 (32.227).
- Porém, contas que cancelaram no plano Basic apresentaram uso médio **superior** às retidas (586.2 vs 512.3 interações). 
- **Causa Raiz:** O crescimento de uso decorre de um fluxo inflado de novas contas em onboarding rápido. Os usuários tentam adotar a plataforma com intensidade inicial, mas encontram gargalos de estabilidade ou valor percebido e abandonam. A tenure mediana até o churn é de apenas **103 dias (Basic), 124 dias (Pro) e 135 dias (Enterprise)**.

#### 3. Desmontando a Afirmação de CS: "A satisfação está OK"
- O CSAT aparente da base é de ~4.0 em todos os planos.
- **Causa Raiz:** **41.2% dos chamados não possuem nota de satisfação (825 de 2.000 tickets)**. Clientes severamente insatisfeitos simplesmente não respondem a pesquisas de satisfação.
- O sinal real não é a nota, mas o **colapso operacional do suporte**:
  * Em períodos de estabilidade (>60 dias antes do churn), a taxa de escalação de chamados é de 5.0%.
  * **Nos 14 dias imediatamente anteriores ao cancelamento, a taxa de escalação salta para 14.6% (quase o triplo)**.
  * O First Response Time em tickets urgentes atinge média de 89 minutos, inaceitável para clientes corporativos.

#### 4. Vulnerabilidade Setorial e Canais Tóxicos
- **DevTools:** Taxa de churn de **31.0%** (113 contas, 35 cancelamentos). Desenvolvedores e times técnicos possuem tolerância zero a falhas em features beta e tempos lentos de resposta.
- **Canal de Aquisição:** Contas vindas de **Eventos (30.2% churn)** e **Ads (23.5% churn)** apresentam qualidade significativamente inferior às originadas por **Parceiros (14.6% churn)** e **Orgânico (17.5% churn)**.

#### 5. O Impacto Financeiro Real (MRR)
Perda acumulada de **$255.442,00/mês em MRR**:
- **Enterprise:** $93.651,00/mês perdidos (34 contas).
- **Pro:** $91.882,00/mês perdidos (39 contas).
- **Basic:** $69.909,00/mês perdidos (37 contas).
- As Top 10 contas Enterprise canceladas sozinhas somam mais de **$60.000/mês** em perda de receita (ex: Company_4 com $21.691/mês e Company_240 com $10.945/mês).

---

### Recomendações

Priorizamos as ações na matriz Impacto x Esforço:

1. **Protocolo "Red Alert" no Suporte (Impacto Imediato / Esforço Baixo):**
   - Automatizar gatilho no Zendesk/Jira: Qualquer ticket escalado ou com First Response Time > 60 min em contas Enterprise/Pro aciona notificação imediata no Slack do Head de CS e Executive Sponsor.
   - Meta: Eliminar o pico de 14.6% de escalação desassistida na janela de 14 dias pré-churn.

2. **Blindagem de Estabilidade em DevTools e Beta Features (Impacto Alto / Esforço Médio):**
   - Desativar a inclusão compulsória de clientes Enterprise em flags de beta que apresentem erro acima de 5%.
   - Revisar as features com maior volume absoluto de falhas (Feature_4 e Feature_9 acumulam mais de 750 erros em contas ativas).

3. **Revisão dos Canais de Aquisição em RevOps (Impacto Médio / Esforço Baixo):**
   - Redirecionar verba de eventos patrocinados (30.2% de churn) para o programa de co-marketing e Parcerias (14.6% de churn).
   - Ajustar a qualificação de ICP para evitar entrada de clientes sem fit técnico.

4. **Cockpit Prescritivo Ativo de CS (Entregue nesta Submissão):**
   - Utilizar o arquivo `ravenstack_account_risk_scores.csv` para intervenção prioritária nas contas ativas classificadas como `Crítico (Alto Risco)`.

---

### Limitações

- **Granularidade Diária de Telemetria:** Os dados fornecem somatórios diários por feature, mas não logs de clickstream em nível de sessão de usuário, o que permitiria mapear a sequência exata de eventos antes de um erro.
- **Natureza Sintética do Dataset:** Por ser um dataset simulado, variáveis como planos e frequências de cobrança possuem distribuições parcialmente uniformes geradas por scripts, exigindo que a inteligência de diagnóstico focasse em anomalias temporais, coortes e cruzamento entre tickets e churn.

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| **Antigravity (Orquestrador Chefe / Japax)** | Análise das diretrizes, síntese de specs, formulação de hipóteses, redação técnica e condução da sessão. |
| **Taiga MCP (`taigaApi`)** | Governança e rastreabilidade determinística em tempo real (Épico 02, US 1007 e Tasks #9 a #13). |
| **DuckDB + Pandas** | Profiling in-memory dos 5 CSVs, auditoria de integridade referencial, detecção de Simpson's Paradox e conciliação de MRR/ARR. |
| **Lifelines (Kaplan-Meier)** | Modelagem de sobrevivência não-paramétrica para cálculo da probabilidade acumulada de retenção temporal. |
| **Scikit-Learn (Random Forest & Pipeline)** | Treinamento de modelo preditivo com pipeline blindada contra vazamento de dados e extração de feature importance. |
| **Streamlit + Altair + Chart.js** | Construção do cockpit interativo executivo e prescritivo com simulador financeiro de ROI. |

---

### Workflow

1. **Kickoff e Fase-Gate:** Leitura dos 4 desafios, definição do foco inegociável no Challenge 001 (Analytics) e criação da infraestrutura de governança no Taiga sob o Épico 02.
2. **Ingestão e Profiling Determinístico (Task #9):** Download dos 5 CSVs oficiais e execução do script DuckDB (`01_data_profiling.py`), constatando integridade referencial de 100% e confirmando que ARR = MRR * 12.
3. **Investigação Causal e Quebra do Baseline (Task #10):** Formulação e teste das 4 hipóteses causais. Identificação do pico de 41.8% de cancelamentos em 2024-Q4 e da subida de escalações para 14.6% nas duas semanas pré-churn.
4. **Engenharia de Features e Modelagem Preditiva (Task #11):** Geração de dataset tabular com 28 variáveis agregadas por conta, validação cruzada 5-fold e geração do arquivo de scores prescritivos.
5. **Desenvolvimento do Cockpit Executivo (Task #12):** Criação da aplicação Streamlit em 4 abas e geração do artefato HTML standalone com Chart.js para visualização imediata sem dependências.
6. **Consolidação Formal e Handoff (Task #13):** Estruturação do relatório final de submissão e documentação do Process Log.

---

### Onde a IA errou e como corrigi

1. **Erro de Correlação Superficial Inicial (Alucinação de Baseline):**
   - *O que a IA tentou fazer:* Em sua primeira inferência sobre os dados de uso, o modelo de linguagem sugeriu a hipótese clássica de que "clientes com menor uso cancelam mais".
   - *Como corrigi:* Forcei uma consulta analítica no DuckDB estratificada por plano. Descobrimos exatamente o oposto: clientes cancelados no plano Basic tinham uso médio superior (586 vs 512). Essa intervenção humana guiou a descoberta do Paradoxo de Simpson e da curta tenure das novas coortes.

2. **Viés no CSAT Não Percebido pela IA:**
   - *O que a IA tentou fazer:* A IA avaliou a média simples de CSAT (4.0/5.0) e concluiu que o suporte estava bem avaliado.
   - *Como corrigi:* Ordenei uma contagem de nulos na coluna `satisfaction_score`. Constatamos que 41.2% dos tickets não tinham nota (viés do sobrevivente). Instruí a IA a analisar os tickets filtrando por janela temporal pré-churn, o que revelou o salto de escalações para 14.6% a 14 dias do churn.

3. **Falha de Sintaxe no DuckDB:**
   - *O que a IA fez:* O script gerado usou `%q` dentro de `strftime(churn_date, '%Y-Q%q')`, causando erro de compilação no motor DuckDB.
   - *Como corrigi:* Corrigi a expressão para `cast(year(...) as varchar) || '-Q' || cast(quarter(...) as varchar)`.

4. **Erro de Valores Ausentes no Pipeline Scikit-Learn:**
   - *O que a IA fez:* Ao instanciar `StandardScaler` diretamente sobre features de suporte, o modelo quebrou devido a contas sem nenhum ticket registrado (NaNs resultantes do LEFT JOIN).
   - *Como corrigi:* Reestruturei a pipeline adicionando `SimpleImputer(strategy='median')` antes do escalonamento, garantindo robustez matemática sem data leakage.

---

### O que eu adicionei que a IA sozinha não faria

1. **Visão de Negócio Executiva (C-Level):** Tradução de métricas brutas em impacto financeiro real ($255k/mês em MRR perdido; perda concentrada de $60k/mês nas top 10 contas Enterprise).
2. **Decomposição do Paradoxo:** Identificação de que o crescimento de uso da plataforma era uma miragem provocada pelo onboarding agressivo de coortes recentes de baixa retenção.
3. **Simulador de ROI de Retenção:** Construção de um modelo de payback que prova ao CFO e CEO que reter apenas 35% das contas Enterprise cobre com folga os investimentos em CS e engenharia de confiabilidade.
4. **Governança Multi-Agente Rastreável:** Criação de um rastro auditável no Taiga onde cada tarefa técnica possui evidências, scripts e comentários estruturados.

---

## Evidências

- [x] **Repositório Git:** Branch `submission/adailton-montinegro` no clone local `/Users/montinegro/G4 AI Master/repo`.
- [x] **Aplicação Streamlit:** Código-fonte em [`repo/submissions/adailton-montinegro/app/app.py`](app/app.py).
- [x] **Dashboard HTML Standalone:** Artefato em [`repo/submissions/adailton-montinegro/artifacts/executive_dashboard.html`](artifacts/executive_dashboard.html).
- [x] **Base de Risco Prescritivo (500 contas):** [`repo/submissions/adailton-montinegro/artifacts/ravenstack_account_risk_scores.csv`](artifacts/ravenstack_account_risk_scores.csv).
- [x] **Métricas de Modelagem e Feature Importance:** [`repo/submissions/adailton-montinegro/artifacts/model_metrics.json`](artifacts/model_metrics.json).
- [x] **Scripts de Análise Causal e Profiling:** Localizados em `/Users/montinegro/G4 AI Master/scripts/`.
- [x] **Governança no Taiga:** Projeto `g4-ai-master` (ID 3), Épico 02 (ID 36), User Story 02 (ID 1007), Tasks #9 a #13 com histórico e logs completos.

---

_Submissão concluída e auditada em: 12 de Setembro de 2026_
