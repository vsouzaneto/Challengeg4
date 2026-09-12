# Submissão — Adailton Montinegro — Challenge 001 (Diagnóstico de Churn)

## Sobre mim

- **Nome:** Adailton Montinegro
- **LinkedIn:** [https://www.linkedin.com/in/adailtonmontenegro/](https://www.linkedin.com/in/adailtonmontenegro/)
- **Challenge escolhido:** 001 — Diagnóstico de Churn (RavenStack)

---

## Executive Summary

A RavenStack enfrentou um colapso na retenção da safra de 2025 para 41,7% (contra >83% nos anos anteriores) e degradação do SaaS Quick Ratio para 1,57. Solucionamos o paradoxo do CEO revelando que o aumento de uso e a satisfação aparentemente neutra mascaravam a **"Síndrome do Power User Traído"**: as contas canceladas usavam a plataforma 53% mais, adotavam 60% mais features beta e enfrentavam 53% mais erros técnicos, esbarrando em tempos lentos de suporte. O plano Enterprise respondeu por **48,3% de todo o MRR perdido ($172.200,00)**, tendo falhas de suporte como causa #1 ($40.400,00). Desenvolvemos um modelo heurístico de Health Score no DuckDB e um dashboard interativo em Streamlit que identificou **33 contas ativas em risco crítico imediato ($279.840,00 em ARR)**, acompanhado de um plano de intervenção em 3 horizontes (30/60/90 dias) capaz de preservar mais de $220.000,00 anuais.

---

## Solução

### Abordagem

O projeto adotou metodologia Spec-Driven Development (SDD) e orquestração de trabalho em time (`mont-teamwork`) com as seguintes premissas arquiteturais:
1. **Engenharia de Dados Determinística com DuckDB:** Persistência local estruturada em camadas Bronze (ingestão dos 5 CSVs brutos), Silver (saneamento, tipagem e tabela contábil de quarentena) e Gold (modelo dimensional, fatos, MRR Bridge mensal, coortes de retenção e health score).
2. **Mitigação do Phantom MRR (Fase 0):** Descoberta e isolamento de 691 contratos históricos sem `end_date` gerados em upgrades/downgrades que inflavam a receita aparente em $656.350,00, apurando o MRR real ativo no corte de Jan/2026 em $347.520,00 (384 contas).
3. **Análise de Causa Raiz Cruzada (Fase 1 e 2):** Cruzamento comportamental entre uso diário de features, taxas de erro em testes beta, métricas operacionais de tickets (tempo de resolução e first response) e eventos de cancelamento por tier de cliente.
4. **Aplicação Visual em Streamlit (Fase 3):** Dashboard interativo conectando em modo `read-only` à camada Gold em 4 visões (Executiva, Retenção, Produto/Suporte e Simulador de Risco).

### Resultados / Findings

* **A Hemorragia no Enterprise:** Contas Enterprise representam apenas 20,3% das perdas em volume de logos (76 eventos), mas respondem por **48,3% do capital evaporado ($172.200,00 de MRR)**, com ticket médio perdido de **$2.265,79/mês** (vs $348,00 no Basic).
* **O Mito da Satisfação OK:** O CSAT médio de 3,2 é neutro e cego. O volume de chamados de suporte **explodiu +84% em 2025** (701 tickets) e o volume de erros técnicos aumentou **+90%** (815 erros). Clientes que cancelaram abriram mais chamados e aguardaram média de 121 minutos para primeira resposta e 24,2 horas para resolução.
* **A Desconexão de Features Beta:** Features como `feature_36`, `feature_39` e `feature_25` apresentaram taxas de erro acima de 8,5% a 9,7%, concentrando frustrações nos clientes corporativos que utilizavam a ferramenta para fluxos operacionais críticos.
* **Radar de Risco:** O modelo de Health Score identificou **33 contas ativas no quadrante Vermelho (Crítico)**, totalizando **$23.320,00 de MRR ($279.840,00 em ARR)** sob risco de churn iminente, lideradas por contas como `Dean-Jimenez` (MRR $1.800) e `Novak and Sons` (MRR $1.600).

### Recomendações

1. **Horizonte 1 (0-30 dias) — Estancar a Sangria Enterprise:**
   - Montar força-tarefa executiva (CS + Engenharia) para contatar nas próximas 72h as 33 contas em risco crítico, oferecendo créditos de serviço e suporte VIP.
   - Criar fila dedicada no suporte com SLA de primeiro atendimento em até 15 minutos para Enterprise/Pro (custo financeiro zero via roteamento no Zendesk).
2. **Horizonte 2 (30-60 dias) — Estabilização de Produto:**
   - Pausar rollout geral das features beta com taxa de erro > 8% até correção de bugs e criação de ambiente de sandbox isolado.
   - Corrigir a telemetria de chamados (114 tickets detectados com first response posterior ao fechamento).
3. **Horizonte 3 (60-90 dias) — Governança Preditiva e Ajuste de Preço:**
   - Automatizar o Health Score do DuckDB no CRM de CS para disparo de alertas preventivos.
   - Reempacotar limites de assentos do plano Basic para mitigar atrito de preço (causa #1 no Basic).

### Limitações

* O dataset histórico não possui logs de transcrição de chamados de voz, limitando a análise qualitativa de atendimento às notas de CSAT e textos de feedback de churn.
* Parte dos registros sintéticos do dataset estendia-se até 2030; essas projeções foram devidamente isoladas na tabela de quarentena para manter a análise focada na operação real de 2021 a janeiro de 2026.

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| **Google Antigravity (Gemini 3.8 Flash High)** | Orquestração do projeto via SDD, arquitetura de dados DuckDB, análise matemática de MRR Bridge, resolução de anomalias e redação técnica. |
| **Grok CLI (xAI Grok 1.0.30)** | Execução distribuída de rotinas de suporte de dados e geração de transformações SQL analíticas. |
| **DuckDB CLI / Engine** | Motor analítico local em memória de alta performance com processamento determinístico das 3 camadas lógicas. |

### Workflow

1. **Setup e Governança:** Fork do repositório upstream, criação da branch `submission/adailton-montinegro` e abertura de User Story #1009 e 5 Tasks no Taiga para governança.
2. **Profiling e Saneamento (Fase 0):** Ingestão determinística dos 5 CSVs, testes de unicidade, integridade referencial e criação da tabela `silver.quarentena_inconsistencias` isolando o Phantom MRR ($656k).
3. **Modelagem Gold e Métricas SaaS (Fase 1):** Construção do modelo dimensional, cálculo estrito do MRR Bridge mensal (fechamento contábil exato mês a mês) e matrizes de coortes (Logo Retention e NRR).
4. **Análise Comportamental (Fase 2):** Cruzamento de uso pré-churn vs contas retidas, solução do paradoxo do CEO e modelagem do Health Score heurístico (0-100).
5. **Aplicação Interativa (Fase 3):** Desenvolvimento do dashboard Streamlit multi-página lendo a camada Gold em modo read-only e criação do script `run.sh`.
6. **Consolidação Executiva (Fase 4):** Redação dos artefatos canônicos (`artefato_01` a `artefato_04`), validações de integridade e submissão via Pull Request.

### Onde a IA errou e como corrigi

* **Soma Ingênua de Assinaturas:** A IA tentou inicialmente calcular a receita somando todos os contratos onde `end_date IS NULL`. Intervi demonstrando que planos históricos substituídos por upgrades não possuíam `end_date`, gerando Phantom MRR de $656.350,00. Corrigi utilizando window function `LEAD(start_date)` para delimitar a vigência real de cada assinatura.
* **Funções Não Nativas:** A IA utilizou a função `INITCAP` que não é nativa do DuckDB, causando erro de compilação corrigido imediatamente com `TRIM`.
* **Inversão Temporal de SLA:** A IA não havia checado a cronologia dos tickets de suporte. Criei validação determinística que identificou 114 tickets com first response posterior ao encerramento, enviando-os para a tabela de quarentena.

### O que eu adicionei que a IA sozinha não faria

* **Identificação da Síndrome do Power User Traído:** Em vez de aceitar as explicações superficiais do time ("o uso cresceu" ou motivos textuais genéricos), cruzei a intensidade de uso por conta e provei que a empresa estava perdendo justamente seus clientes mais valiosos e mais engajados devido ao acúmulo de falhas técnicas.
* **Ponderação Financeira sobre Volume de Logos:** Reorientei o foco da análise para demonstrar que o churn de Enterprise é o verdadeiro ofensor da viabilidade do negócio (48% da receita perdida), impedindo que a empresa gaste energia excessiva em contas Basic de $30/mês.
* **Garantia de Reprodutibilidade e Integridade Contábil:** Exigência de que cada centavo fosse rastreado e reconciliado sem exclusões arbitrárias.

---

## Evidências

* [Artefato 01: Diagnóstico de Qualidade e Matriz de Saneamento](docs/artefato_01_diagnostico_qualidade.md)
* [Artefato 02: Memória de Cálculo de Métricas SaaS, MRR Bridge e Coortes](docs/artefato_02_memoria_calculo_metricas.md)
* [Artefato 03: Relatório Diagnóstico Executivo de Churn](docs/artefato_03_relatorio_executivo.md)
* [Artefato 04: Guia de Reprodutibilidade Integral e Evidências](docs/artefato_04_reprodutibilidade_e_evidencias.md)
* [Plano de Execução e Orquestração de Equipe (mont-teamwork)](docs/teamwork_plan.md)
* [Registro de Prompts e Process Log](process-log/prompt_history.md)
* [Código Fonte do Pipeline DuckDB e Aplicação Streamlit](solution/)
* [Git History: Commits detalhados com desenvolvimento guiado por IA](https://github.com/adailtonmontinegro/ai-master-challenge/commits/submission/adailton-montinegro)

---

_Submissão enviada em: 12 de Setembro de 2026_
