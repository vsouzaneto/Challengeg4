"""Detalhe por conta para drawer de investigação no Command Center."""
from __future__ import annotations

import pandas as pd


def build_investigation_index(tables: dict, acc: pd.DataFrame) -> dict[str, dict]:
    churn = tables["churn_events"].sort_values("churn_date")
    sub = tables["subscriptions"]
    usage = tables["feature_usage"]
    tix = tables["support_tickets"]

    u = usage.merge(sub[["subscription_id", "account_id"]], on="subscription_id")
    u["month"] = pd.to_datetime(u["usage_date"]).dt.to_period("M").astype(str)
    usage_m = (
        u.groupby(["account_id", "month"])["usage_count"]
        .sum()
        .reset_index()
        .sort_values(["account_id", "month"])
    )

    out: dict[str, dict] = {}
    for _, row in acc.iterrows():
        aid = row["account_id"]
        ev = churn[churn["account_id"] == aid].tail(8)
        eventos = [
            {
                "data": pd.Timestamp(x).strftime("%Y-%m-%d"),
                "motivo": str(r),
                "reativacao": bool(re),
            }
            for x, r, re in zip(ev["churn_date"], ev["reason_code"], ev["is_reactivation"])
        ]
        um = usage_m[usage_m["account_id"] == aid].tail(6)
        uso_mensal = [
            {"mes": m, "total": int(t)} for m, t in zip(um["month"], um["usage_count"])
        ]
        tk = tix[tix["account_id"] == aid]
        suporte = {
            "tickets": int(len(tk)),
            "csat_medio": round(float(tk["satisfaction_score"].mean()), 2)
            if len(tk) and tk["satisfaction_score"].notna().any()
            else None,
            "taxa_escalacao_pct": round(100 * tk["escalation_flag"].mean(), 1) if len(tk) else 0,
        }
        alertas: list[str] = []
        if bool(row.get("net_churned")) and not eventos:
            alertas.append("Flag churn líquido sem evento registrado")
        if bool(row.get("revolving_active")):
            alertas.append("Conta ativa com histórico de churn (revolving)")

        out[aid] = {
            "eventos_churn": eventos,
            "uso_mensal": uso_mensal,
            "suporte": suporte,
            "alertas": alertas,
        }
    return out
