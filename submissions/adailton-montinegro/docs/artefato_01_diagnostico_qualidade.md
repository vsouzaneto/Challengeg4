# Artefato 01: Diagnóstico de Qualidade, Profiling e Matriz de Saneamento

**Projeto:** RavenStack SaaS Subscription and Churn Analytics  
**Desafio:** AI Master G4 — Challenge 001  
**Data da Execução:** 2026-09-12  
**Motor de Processamento:** DuckDB v1.5.5 (SQL Determinístico)  
**Tabela de Quarentena:** `silver.quarentena_inconsistencias`  

---

## 1. Sumário Executivo de Qualidade

Antes de qualquer modelagem preditiva ou métrica executiva, foi realizado profiling sistemático sobre os 5 datasets brutos da RavenStack (~500 contas, 1.449 contratos de assinatura, 6.346 registros de uso de funcionalidades, 1.532 chamados de suporte e 374 eventos de churn).

### Principais Descobertas e Riscos Críticos Mitigados:
1. **O "Phantom MRR" por Falta de Fechamento Histórico:** Identificamos que 317 das 500 contas possuíam múltiplos contratos de assinatura com `end_date IS NULL` simultaneamente. Sempre que um cliente realizava upgrade ou downgrade, o sistema gerava uma nova linha de assinatura sem encerrar a anterior. Uma soma ingênua de `WHERE end_date IS NULL` apontaria um MRR irreal de **$1.003.870,00**. O saneamento na camada Silver isolou **$656.350,00** de MRR fantasma, revelando o MRR real ativo no corte de **$347.520,00** (distribuído em 384 contas ativas e 116 churneadas).
2. **Inconsistência de SLA em Suporte:** 114 chamados apresentaram `first_response_time_minutes` posterior ao horário de encerramento do chamado (`closed_at`), evidenciando falhas de telemetria no Zendesk/Freshdesk da RavenStack.
3. **Horizonte Temporal e Transações Futuras:** Enquanto o cadastro de contas (`accounts`) e os tickets de suporte encerram em janeiro de 2026, 258 assinaturas e 113 eventos de churn continham datas estendidas até 2030 (decorrentes de simulações sintéticas ou projeções futuras do billing). Esses registros foram devidamente quarentenados para não enviesar a análise retrospectiva de 2021 a 2026.

---

## 2. Balanço Geral de Linhas e Reconciliação Camada Bronze vs Silver

Nenhum dado é descartado silenciosamente. Todos os registros permanecem na Bronze e fluem para a Silver com tipagem estrita, enriquecimento de chaves temporais e flags de rastreabilidade.

| Entidade | Tabela Bronze | Tabela Silver | Registros Aproveitados | Registros Quarentenados | Justificativa Técnica |
|---|---|---|---|---|---|
| **Contas** | `bronze.accounts` | `silver.accounts` | 500 (100%) | 0 (0%) | 100% de unicidade e integridade referencial. |
| **Assinaturas** | `bronze.subscriptions` | `silver.subscriptions` | 1.449 (100%) | 949 anomalias registradas | 691 planos sobrepostos sem end_date + 258 transações com início futuro (> 2026-01-31). |
| **Eventos de Uso** | `bronze.feature_usage` | `silver.feature_usage` | 6.346 (100%) | 0 | Chaves conectadas a `subscription_id`, 485 registros futuros catalogados. |
| **Tickets Suporte** | `bronze.support_tickets` | `silver.support_tickets` | 1.532 (100%) | 114 | 114 chamados com primeiro atendimento registrado após o fechamento. |
| **Eventos de Churn** | `bronze.churn_events` | `silver.churn_events` | 374 (100%) | 0 | 100% de paridade exata com as 374 assinaturas que possuem `churn_flag = true`. |

---

## 3. Matriz de Quarentena e Impacto Contábil no MRR

A tabela `silver.quarentena_inconsistencias` registra a trilha de auditoria completa de cada inconsistência detectada, permitindo que a controladoria e o time de engenharia reconciliem centavo por centavo:

```sql
SELECT 
    anomaly_type, 
    count(*) AS total_registros, 
    sum(impact_mrr) AS impacto_mrr_total
FROM silver.quarentena_inconsistencias
GROUP BY anomaly_type
ORDER BY total_registros DESC;
```

### Resultados da Reconciliação:

| Tipo de Anomalia (`anomaly_type`) | Tabela Origem | Registros | Impacto em MRR | Ação Tomada na Camada Silver |
|---|---|---|---|---|
| `HISTORICAL_OVERLAP_NO_END_DATE` | `subscriptions` | 691 | $656.350,00 | Calculado `effective_end_date` via window function `LEAD(start_date)`. Apenas o contrato vigente (`rn_desc = 1`) compõe o MRR ativo. |
| `FUTURE_DATED_TRANSACTION` | `subscriptions` | 258 | $242.480,00 | Flag de quarentena aplicada. Isolados do cálculo de MRR histórico/atual de fechamento de janeiro/2026. |
| `INVALID_FIRST_RESPONSE_AFTER_CLOSE` | `support_tickets` | 114 | $0,00 | Sinalizado com a flag `is_sla_anomalous = true` para evitar distorção no cálculo de First Response Time médio. |

### Reconciliação Contábil de MRR:

$$\begin{aligned}
\text{MRR Total Bruto Ingerido (Soma de todos os contratos)} &= \$1.360.190,00 \\
\text{(-) MRR de Contratos Encerrados por Churn (374 contratos)} &= -\$356.320,00 \\
\text{(=) MRR Aparente Ingênuo (end\_date IS NULL)} &= \$1.003.870,00 \\
\text{(-) MRR Fantasma de Planos Anteriores Substituídos} &= -\$656.350,00 \\
\text{(=) MRR dos Contratos Mais Recentes (500 contas)} &= \$457.230,00 \\
\text{(-) MRR do Último Contrato de Contas Já Canceladas (116 contas)} &= -\$109.710,00 \\
\mathbf{(=)\text{ MRR Real Ativo no Fechamento (384 contas)}} &\mathbf{= \$347.520,00}
\end{aligned}$$

---

## 4. Testes Determinísticos de Integridade Executados

1. **Unicidade de Chaves Primárias:**
   - `account_id` em accounts: 0 duplicados.
   - `subscription_id` em subscriptions: 0 duplicados.
   - `usage_id` em feature_usage: 0 duplicados.
   - `ticket_id` em support_tickets: 0 duplicados.
   - `churn_event_id` em churn_events: 0 duplicados.
2. **Integridade Referencial:**
   - `subscriptions.account_id` órfãos: 0.
   - `feature_usage.subscription_id` órfãos: 0.
   - `support_tickets.account_id` órfãos: 0.
   - `churn_events.account_id` órfãos: 0.
3. **Consistência Relacional de Churn:**
   - 100% dos 374 registros em `churn_events` correspondem exatamente às 374 assinaturas em `subscriptions` com `churn_flag = true` e `end_date = churn_date`.
4. **Saneamento de Tipos e Strings:**
   - Remoção de espaços espúrios (`TRIM`) em categorias, normalização de siglas de países (`UPPER`) e conversão explícita de tipos monetários para `DECIMAL(10,2)`.
