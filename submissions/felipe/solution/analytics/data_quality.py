"""Métricas de qualidade / reconciliação cadastro vs eventos (forense dados)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from analytics.paths import OUT, REPORTS


def compute_data_quality(tables: dict, acc: pd.DataFrame) -> dict:
    raw_acc = tables["accounts"]
    churn = tables["churn_events"]
    sub = tables["subscriptions"]
    usage = tables["feature_usage"]

    net_ids = set(raw_acc.loc[raw_acc["churn_flag"] == 1, "account_id"])
    with_events = set(churn["account_id"].unique())
    flag_no_event = net_ids - with_events

    mrr_flag_no_event = float(
        acc.loc[acc["account_id"].isin(flag_no_event), "mrr_amount"].sum()
    )

    sub_start = sub.groupby("account_id")["start_date"].min()
    u = usage.merge(sub[["subscription_id", "account_id", "start_date"]], on="subscription_id")
    u["usage_date"] = pd.to_datetime(u["usage_date"])
    u["start_date"] = pd.to_datetime(u["start_date"])
    before_sub = u[u["usage_date"] < u["start_date"]]
    usage_rows_before_sub = int(len(before_sub))
    usage_rows_total = int(len(u))

    dup_sub = usage.groupby("subscription_id").size()
    dup_sub_count = int((dup_sub > 1).sum())

    summary = {
        "contas_total": int(len(raw_acc)),
        "churn_liquido_flag": int(len(net_ids)),
        "contas_flag_sem_evento_churn": int(len(flag_no_event)),
        "mrr_contratual_flag_sem_evento_usd": round(mrr_flag_no_event, 2),
        "linhas_uso_total": usage_rows_total,
        "linhas_uso_antes_inicio_assinatura": usage_rows_before_sub,
        "pct_uso_antes_assinatura": round(
            100 * usage_rows_before_sub / max(usage_rows_total, 1), 1
        ),
        "subscription_ids_com_uso_duplicado": dup_sub_count,
        "eventos_churn_total": int(len(churn)),
        "contas_com_evento": int(len(with_events)),
    }
    return summary


def export_data_quality(tables: dict, acc: pd.DataFrame) -> dict:
    summary = compute_data_quality(tables, acc)
    rows = [{"metrica": k, "valor": v} for k, v in summary.items()]
    pd.DataFrame(rows).to_csv(OUT / "data_quality_summary.csv", index=False)
    (OUT / "data_quality_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    body = f"""# Qualidade de dados — CEO (1 página)

**Por que importa:** o board pode decidir com **cadastro** (`churn_flag`) ou com **eventos** — eles **não batem** sempre.

| Sinal | Valor | Leitura |
|-------|-------|---------|
| Contas com flag churn líquido | **{summary['churn_liquido_flag']}** | Definição cadastro |
| Dessas, **sem nenhum evento** de churn | **{summary['contas_flag_sem_evento_churn']}** | Reconciliar com Financeiro/Dados |
| MRR contratual nessas contas (exposição) | **US$ {summary['mrr_contratual_flag_sem_evento_usd']:,.0f}** | Priorizar auditoria, não “receita recuperada” |
| Uso **antes** do início da assinatura | **{summary['linhas_uso_antes_inicio_assinatura']:,}** / {summary['linhas_uso_total']:,} linhas ({summary['pct_uso_antes_assinatura']}%) | Não usar série bruta para “engajamento subiu” |
| Assinaturas com múltiplas linhas de uso | **{summary['subscription_ids_com_uso_duplicado']}** | Validar grain de telemetria |

**Ação:** alinhar KPI (líquido + eventos + MRR) **e** corrigir cadastro — complementa o diagnóstico **revolving** (`executive_summary.md`).

Detalhe técnico: `outputs/data_quality_summary.csv`
"""
    (REPORTS / "data_quality_ceo.md").write_text(body, encoding="utf-8")
    return summary
