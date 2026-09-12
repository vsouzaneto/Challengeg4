# Process Log: Trilha de Interações com IA e Julgamento Humano

**Candidato:** Adailton Montinegro  
**Desafio:** 001 — Diagnóstico de Churn RavenStack  
**Data:** 12 de Setembro de 2026  

---

## 1. Ferramentas de IA Utilizadas

| Ferramenta | Papel / Função | Justificativa de Escolha |
|---|---|---|
| **Google Antigravity (Gemini 3.8 Flash High)** | Orquestrador de Arquitetura, Engenheiro Chefe e Validador Contábil | Raciocínio multi-etapa longo, visão holística de projeto, orquestração de subagentes e execução autônoma via `/goal`. |
| **Grok CLI (xAI Grok 1.0.30)** | Engenheiro de Dados e Implementador de Pipelines | Sintaxe direta, geração de transformações SQL analíticas e verificação de padrões de engenharia. |
| **DuckDB CLI / Engine** | Motor SQL Local Determinístico | Performance analítica colunar SIMD em memória e persistência leve em arquivo único. |

---

## 2. Metodologia de Decomposição do Problema

Em vez de enviar o dataset para uma IA pedindo um "diagnóstico genérico", o problema foi atacado com arquitetura Spec-Driven Development (SDD) e orquestração distribuída (`mont-teamwork`):

1. **Fase 0 (Profiling e Integridade de Dados):**
   - Questionamento do dataset: Não assumir que os números do CSV são verdade absoluta.
   - Detecção do Phantom MRR: Identificamos que contratos antigos nunca eram encerrados ao haver upgrade/downgrade, inflando a receita aparente em 3x ($1M vs $347k reais).
2. **Fase 1 (Modelagem Dimensional e MRR Bridge):**
   - Construção do modelo dimensional canônico (Bronze -> Silver -> Gold).
   - Fechamento da identidade contábil do MRR Bridge mês a mês.
   - Cálculo de coortes de retenção de clientes e receita (NRR).
3. **Fase 2 (Análise Comportamental e Causa Raiz):**
   - Teste de hipóteses para responder ao paradoxo do CEO.
   - Descoberta da "Síndrome do Power User Traído": Usuários que cancelaram usavam 53% mais e tinham 53% mais erros técnicos.
   - Modelo de Health Score determinístico (0-100).
4. **Fase 3 (Dashboard Interativo Streamlit):**
   - Construção de interface em 4 visões conectando à camada Gold do DuckDB.
5. **Fase 4 (Documentação e Entrega Executiva):**
   - Produção dos 4 artefatos Markdown canônicos e estruturação da submissão para PR.

---

## 3. Onde a IA Errou e Como Foi Corrigida

### Erro 1: Soma Ingênua de MRR em Assinaturas
* **O que a IA propôs inicialmente:** Ao calcular o MRR atual da RavenStack, a IA sugeriu simplesmente executar `SELECT sum(mrr_amount) FROM subscriptions WHERE end_date IS NULL`.
* **Como identifiquei o erro:** Ao auditar o resultado ($1.003.870,00), notei que a receita média por conta ativa passaria de $2.000,00, incompatível com a distribuição de planos da empresa.
* **A correção humana:** Executei uma query de sobreposição e descobri que 317 contas tinham múltiplos contratos ativos ao mesmo tempo. Implantei a regra determinística na camada Silver usando `LEAD(start_date)` para imputar `effective_end_date` e `ROW_NUMBER() ... = 1` para considerar apenas o contrato vigente, isolando $656.350,00 de Phantom MRR na tabela de quarentena.

### Erro 2: Utilização de Função Inexistente no DuckDB (`INITCAP`)
* **O que a IA gerou:** O script SQL da Silver utilizou `INITCAP(industry)` para padronizar textos.
* **O erro:** O DuckDB não possui a função nativa `initcap`, causando falha de compilação no pipeline.
* **A correção:** Corrigi para `TRIM(industry)` e funções nativas compatíveis, testando com `py_compile` antes da persistência.

### Erro 3: Inversão Temporal em Tickets de Suporte
* **O que a IA aceitaria:** Aceitar cegamente a média de First Response Time dos tickets.
* **A anomalia detectada:** Criei um teste de consistência temporal e encontrei 114 tickets onde a primeira resposta ocorria após o encerramento do chamado.
* **A correção:** Isolei os registros na quarentena e adicionei a flag `is_sla_anomalous` para evitar contaminação da métrica média de SLA.

---

## 4. O Que o Julgamento Humano Adicionou (Além do Que a IA Faria Sozinha)

1. **Desmistificação do Paradoxo do CEO:**
   Uma IA tradicional listaria apenas os "motivos declarados" de cancelamento (`reason_code`). O julgamento analítico cruzou o comportamento pré-churn e descobriu que as contas canceladas eram os **maiores clientes e maiores usuários da ferramenta**, apontando a frustração técnica como alavanca causadora.
2. **Priorização por Impacto de Receita (Não por Volume de Logos):**
   A IA tende a tratar todas as linhas igualmente. Demonstramos à diretoria que perder 76 contas Enterprise destruiu quase metade de toda a receita da história da empresa, enquanto o time de suporte focava tempo igual em chamados de Basic ($30/mês).
3. **Quarentena Rastreável vs Exclusão Silenciosa:**
   Garantimos que nenhum dado inconsistente fosse descartado via `WHERE` silencioso, criando a tabela contábil de reconciliação para auditoria da controladoria.
