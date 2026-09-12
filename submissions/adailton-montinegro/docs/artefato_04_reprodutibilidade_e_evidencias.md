# Artefato 04: Guia de Reprodutibilidade Integral, Testes e Trilha de Evidências

**Projeto:** RavenStack SaaS Subscription and Churn Analytics  
**Desafio:** AI Master G4 — Challenge 001  
**Autor:** Adailton Montinegro  
**Data:** 12 de Setembro de 2026  

---

## 1. Instruções Passo a Passo para Reprodutibilidade Local

O projeto foi concebido para ser 100% autônomo, autocontido e reproduzível com zero dependências externas não documentadas.

### 1.1 Pré-requisitos
* Sistema Operacional: macOS, Linux ou Windows (WSL)
* Python: Versão 3.10 ou superior
* Gerenciador de Pacotes: `uv` (recomendado) ou `pip` tradicional
* Git

### 1.2 Clonagem e Execução Rápida (One-Shot)

```bash
# 1. Clonar o repositório
git clone https://github.com/adailtonmontinegro/ai-master-challenge.git
cd ai-master-challenge

# 2. Acessar a branch de submissão
git checkout submission/adailton-montinegro

# 3. Executar o script mestre (cria venv, roda DuckDB e abre Streamlit na porta 8501)
./submissions/adailton-montinegro/solution/run.sh
```

### 1.3 Execução Manual Passo a Passo

Caso prefira executar cada componente de forma granular:

```bash
# Criação do ambiente virtual
uv venv .venv --python 3.12
source .venv/bin/activate

# Instalação das dependências pinadas
uv pip install -r submissions/adailton-montinegro/solution/requirements.txt

# Execução do pipeline DuckDB (Bronze -> Silver -> Gold)
python3 submissions/adailton-montinegro/solution/src/pipeline.py

# Inicialização da aplicação Streamlit
streamlit run submissions/adailton-montinegro/solution/src/app.py
```

---

## 2. Arquitetura das Camadas e Dicionário de Dados

Toda a persistência física reside no banco local `submissions/adailton-montinegro/solution/data/ravenstack.duckdb`.

### 2.1 Camada Bronze (`bronze`)
Espelho fiel dos 5 CSVs brutos sem filtros ou exclusões:
* `bronze.accounts` (500 linhas)
* `bronze.subscriptions` (1.449 linhas)
* `bronze.feature_usage` (6.346 linhas)
* `bronze.support_tickets` (1.532 linhas)
* `bronze.churn_events` (374 linhas)

### 2.2 Camada Silver (`silver`)
Dados higienizados, tipados e com tabela de auditoria:
* `silver.quarentena_inconsistencias`: Registra desvios com impacto em MRR (691 sobreposições de contratos sem end_date, 258 transações futuras e 114 chamados anômalos de SLA).
* `silver.accounts`: Normalização de texto (`TRIM`), países em caixa alta.
* `silver.subscriptions`: Imputação de `effective_end_date` via window function `LEAD(start_date)` e sinalizadores `is_latest_contract` e `is_currently_active`.
* `silver.feature_usage`: Eventos limpos associados a contratos.
* `silver.support_tickets`: Indicador `is_sla_anomalous`.
* `silver.churn_events`: Vinculação com o contrato correspondente.

### 2.3 Camada Gold (`gold`)
Modelagem dimensional e tabelas analíticas agregadas consumidas pelo Streamlit:
* `gold.dim_accounts`: Dimensão enriquecida com safra de entrada, tempo de vida em meses e causa principal de saída.
* `gold.dim_plans`: Catálogo de benefícios e preços base por tier.
* `gold.fato_assinaturas`, `gold.fato_eventos_uso`, `gold.fato_atendimento`, `gold.fato_churn`: Fatos transacionais auditados.
* `gold.agg_mrr_bridge`: Decomposição mensal de MRR (Beginning, New, Expansion, Reactivation, Contraction, Churned, Ending, Quick Ratio).
* `gold.agg_cohort_logo_retention` e `gold.agg_cohort_revenue_retention`: Matrizes de safras M1 a M12.
* `gold.agg_account_health_score`: Modelo de pontuação (0-100), segmentação de risco (Verde, Amarelo, Vermelho) e cálculo de ARR em risco.

---

## 3. Checklist de Testes e Validação Determinística

| Teste de Integridade | Comando / Query de Teste | Resultado Obtido | Status |
|---|---|---|---|
| **Unicidade de Chaves Primárias** | `SELECT count(col) - count(DISTINCT col)` em todas as tabelas | 0 duplicatas em todas as 5 entidades | **Aprovado** |
| **Integridade Referencial** | `LEFT JOIN` entre chaves estrangeiras com verificação de nulos | 0 órfãos em subscriptions, usage, tickets e churn | **Aprovado** |
| **Paridade Exata de Churn** | `churn_events` vs `subscriptions WHERE churn_flag = true` | 374 eventos mapeados com 100% de paridade | **Aprovado** |
| **Identidade Contábil do MRR Bridge** | `ending_mrr(M) == beginning_mrr(M+1)` | Resíduo de $0,00 em todos os 60 meses do histórico | **Aprovado** |
| **Isolamento de Phantom MRR** | Contratos sobrepostos sem end_date | $656.350,00 isolados em quarentena sem perda silenciosa | **Aprovado** |
| **Compilação e Execução do Streamlit** | `python3 -m py_compile src/app.py` | Compilação com código de retorno 0 | **Aprovado** |
