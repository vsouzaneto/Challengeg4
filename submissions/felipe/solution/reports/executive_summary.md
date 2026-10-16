# Diagnóstico executivo — RavenStack Churn

_Gerado em 2026-10-16 19:46 UTC · pipeline `run_analysis.py`_

## Resposta em 60 segundos

O CEO está certo **e** errado ao mesmo tempo — dependendo da métrica:

| Métrica | Valor | Leitura |
|---------|-------|---------|
| Contas com **churn líquido** (`churn_flag=1`) | **110** / 500 (**22.0%**) | Retenção headline ainda razoável |
| **Eventos** de churn na base | **600** em 500 contas | Volume bruto >> churn líquido |
| Contas **ativas com histórico de churn** | **277** | **MRR ~ US$ 665,190** em “porta giratória” |
| MRR das contas churn líquido | **US$ 254,952** | Perda econômica real |
| Uso médio por linha (retidas vs churn líquido) | 10.01 vs 10.03 | Produto: uso **não separa** quem sai |
| CSAT médio (tickets) | ~4,0 em ambos os grupos | CS: satisfação **não discrimina** |

**Causa raiz (síntese):** não é queda global de uso nem CSAT baixo. É uma combinação de (**1**) **métrica errada no board** (eventos vs churn líquido + reativações), (**2**) **base instável** (277 contas ativas já churnearam antes), (**3**) **segmentos** (DevTools **31.0%** churn líquido, referral **event** **30.2%**), (**4**) **sinal operacional** (taxa de escalação **6.1%** vs **4.3%** nas retidas — correlação, não causalidade comprovada).

## 1. O que está causando o churn?

1. **Porta giratória (revolving):** 277 contas estão ativas hoje mas já tiveram churn; isso explica CS “parece ok” enquanto eventos sobem.
2. **Segmento:** DevTools e aquisição via **event** concentram pior `churn_flag` (ver `outputs/segment_net_churn.csv`).
3. **Autoreporte ruidoso:** `reason_code` está equilibrado (~100/evento); texto de feedback menciona competitor/features/preço — cruzar com `outputs/feedback_text_themes.csv`.
4. **Uso pré-churn:** só **31%** das contas com janela (264) caem >30% nos 30d antes do 1º evento — **não** é queda universal de usage.

## 2. Segmentos em risco (dados)

- Fila priorizada: **`outputs/cs_action_queue_top50.csv`** (score explicável + MRR).
- Impacto MRR por indústria: **`outputs/industry_mrr_impact.csv`**.

## 3. O que fazer (priorizado)

| # | Ação | Impacto esperado | Esforço |
|---|------|------------------|---------|
| 1 | Mudar KPIs: **churn líquido + reativação + MRR** (não só eventos) | Alinha board | Baixo |
| 2 | Playbook CS para **277 contas revolving** (US$ 665,190 MRR) | **+US$ 33,260/mês** se 5% retidos (ver `recommendations_impact.csv`) | Médio |
| 3 | Cohort **DevTools** + **event**: onboarding 30d | Reduz segmento outliers | Médio |
| 4 | Alerta por **escalação** + histórico churn | Early warning | Médio |
| 5 | Piloto modelo (AUC teste **0.62**) — usar como triagem, não verdade | Escala priorização | Alto |

## Integridade dos dados

QA de joins: **True** (detalhe em `outputs/integration_qa.csv`).

## Limitações

- Dataset sintético/demo; causalidade não provada (correlações CSAT/uso/escalação).
- `churn_flag` vs eventos: reativações inflacionam narrativa de “crise de uso”.
- Modelo linear; validar em produção antes de automatizar outreach.

---
Relatório técnico complementar: `reports/technical_appendix.md`
