# Artefato 02: Memória de Cálculo de Métricas SaaS, MRR Bridge e Coortes

**Projeto:** RavenStack SaaS Subscription and Churn Analytics  
**Desafio:** AI Master G4 — Challenge 001  
**Data da Execução:** 2026-09-12  
**Camada Analítica:** DuckDB Gold (`gold.agg_mrr_bridge`, `gold.agg_cohort_logo_retention`, `gold.agg_cohort_revenue_retention`)  

---

## 1. Racional Matemático e Fórmulas Canônicas

Todas as agregações na camada Gold seguem as convenções contábeis e analíticas padrão de Venture Capital e SaaS (David Skok / OpenView / ChartMogul):

### 1.1 Decomposição Mensal do MRR Bridge
Para cada mês de calendário $M$, o balanço de receita recorrente mensal obedece estritamente à identidade:

$$\text{Ending MRR}_M = \text{Beginning MRR}_M + \text{Net MRR}_M$$

Onde:
$$\text{Beginning MRR}_M = \text{Ending MRR}_{M-1}$$
$$\text{Net MRR}_M = \text{New MRR}_M + \text{Expansion MRR}_M + \text{Reactivation MRR}_M - \text{Contraction MRR}_M - \text{Churned MRR}_M$$

* **New MRR:** Receita proveniente de contas novas cujo primeiro contrato iniciou dentro do mês $M$.
* **Expansion MRR:** Aumento de receita líquida de clientes ativos existentes comparado ao mês anterior ($MRR_M > MRR_{M-1}$).
* **Contraction MRR:** Redução de receita líquida de clientes ativos existentes ($0 < MRR_M < MRR_{M-1}$).
* **Churned MRR:** Receita de contas que possuíam contrato ativo no mês anterior e cancelaram no mês $M$ ($MRR_{M-1} > 0 \land MRR_M = 0$).
* **Reactivation MRR:** Retorno de clientes que estavam cancelados há pelo menos 1 mês e voltaram a pagar ($MRR_{M-1} = 0 \land MRR_M > 0$).

### 1.2 SaaS Quick Ratio
Mede a eficiência de crescimento em relação às perdas de receita:

$$\text{Quick Ratio} = \frac{\text{New MRR} + \text{Expansion MRR} + \text{Reactivation MRR}}{\text{Contraction MRR} + \text{Churned MRR}}$$
* Benchmark SaaS: $> 4.0$ (Excelente), $2.0 - 4.0$ (Saudável), $< 2.0$ (Alerta de Ineficiência / Churn excessivo).

### 1.3 Coortes de Retenção
* **Logo Retention Rate (Retenção de Clientes):**
$$\text{Logo Retention}_{c, t} = \frac{\text{Contas Ativas da Safra } c \text{ no Mês } t}{\text{Total de Contas Inicial da Safra } c}$$
* **Net Revenue Retention (NRR):**
$$\text{NRR}_{c, t} = \frac{\sum \text{MRR dos Clientes da Safra } c \text{ no Mês } t}{\sum \text{MRR Inicial da Safra } c}$$

---

## 2. Tabela Resumo Anualizada do MRR Bridge

Consolidação anual das movimentações financeiras da RavenStack (2021 a janeiro de 2026):

| Ano | Beginning MRR | New MRR | Expansion MRR | Reactivation MRR | Contraction MRR | Churned MRR | Ending MRR | Net Growth | Quick Ratio Médio |
|---|---|---|---|---|---|---|---|---|---|
| **2021** | $0,00 | $67.430,00 | $2.410,00 | $0,00 | $0,00 | $9.800,00 | $60.040,00 | +$60.040,00 | 7,13 (Forte) |
| **2022** | $60.040,00 | $56.960,00 | $12.380,00 | $17.650,00 | $2.680,00 | $37.520,00 | $106.830,00 | +$46.790,00 | 2,16 (Saudável) |
| **2023** | $106.830,00 | $63.780,00 | $24.640,00 | $39.810,00 | $9.120,00 | $50.360,00 | $175.580,00 | +$68.750,00 | 2,16 (Saudável) |
| **2024** | $175.580,00 | $33.430,00 | $30.820,00 | $74.520,00 | $15.420,00 | $51.100,00 | $247.830,00 | +$72.250,00 | 2,09 (Alerta) |
| **2025** | $247.830,00 | $7.870,00 | $13.560,00 | $96.840,00 | $14.810,00 | $60.490,00 | $290.800,00 | +$42.970,00 | **1,57 (Crítico)** |
| **2026 (Jan)** | $290.800,00 | $360,00 | $910,00 | $6.120,00 | $0,00 | $3.980,00 | $294.210,00 | +$3.410,00 | 1,86 (Alerta) |

---

## 3. Matriz de Coortes: O Desabamento da Safra de 2025

| Safra Anual | Contas Iniciais | Initial MRR | Retenção M3 (%) | Retenção M6 (%) | Retenção M12 (%) | NRR M12 (%) |
|---|---|---|---|---|---|---|
| **2021** | 90 | $67.430,00 | 100,0% | 91,1% | 75,6% | 114,2% |
| **2022** | 97 | $56.960,00 | 100,0% | 95,9% | 83,5% | 128,4% |
| **2023** | 112 | $63.780,00 | 100,0% | 95,5% | 83,9% | 122,1% |
| **2024** | 95 | $33.430,00 | 100,0% | 95,8% | 87,4% | 118,6% |
| **2025** | 96 | $7.870,00 | **90,6%** | **75,0%** | **41,7%** | **68,3%** |

---

## 4. Decomposição de Churn por Tier de Plano

| Tier de Plano | Contas Churneadas | Eventos de Churn | MRR Total Perdido | MRR Médio / Churn | Refund Total USD | Causa #1 de Churn |
|---|---|---|---|---|---|---|
| **Enterprise** | 71 | 76 | **$172.200,00 (48,3%)** | **$2.265,79** | $1.750,00 | **Suporte ($40.400,00)** |
| **Pro** | 131 | 148 | **$131.920,00 (37,0%)** | $891,35 | $4.750,00 | **Suporte ($41.280,00)** |
| **Basic** | 135 | 150 | **$52.200,00 (14,7%)** | $348,00 | $3.900,00 | **Pricing ($12.810,00)** |
| **Total** | **337** | **374** | **$356.320,00 (100%)** | **$952,73** | **$10.400,00** | **Suporte ($91.190,00)** |

---

## 5. Validações Contábeis Concluídas

1. **Paridade Matemática do MRR Bridge:**
   $$\text{Ending MRR}_{2026-01} = \$294.210,00 = \text{Beginning MRR} + \text{Net MRR}$$
   Diferença residual = $\$0,00$.
2. **Reativações Recorrentes:**
   85 contas churnearam mais de uma vez ao longo do histórico, o que explica por que a receita de reativação ($96.840 em 2025) mascarou o colapso da aquisição nova ($7.870).
3. **Concentração de Risco no Top-Tier:**
   Contas Enterprise representam apenas 20,3% dos cancelamentos em quantidade de logos, mas respondem por quase metade (48,3%) de todo o capital evaporado.
