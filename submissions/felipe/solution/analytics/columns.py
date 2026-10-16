"""Normalização de colunas — uma fonte de verdade para CSVs e dashboard."""
from __future__ import annotations

import numpy as np
import pandas as pd

# Mapeamento técnico → rótulo de negócio (export PT)
# Canais (Kaggle) → rótulo UI com inicial maiúscula
CANAL_LABEL = {
    "ads": "Ads",
    "event": "Event",
    "organic": "Organic",
    "partner": "Partner",
    "other": "Other",
}


def label_canal(value: object) -> object:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return value
    key = str(value).strip().lower()
    return CANAL_LABEL.get(key, str(value).strip().capitalize())


EXPORT_RENAME = {
    "account_id": "conta_id",
    "account_name": "nome_conta",
    "industry": "industria",
    "country": "pais",
    "referral_source": "canal_aquisicao",
    "plano_atual": "plano_atual",
    "assentos": "assentos",
    "is_trial": "em_trial",
    "mrr_amount": "mrr_usd",
    "arr_amount": "arr_usd",
    "churn_events": "eventos_churn",
    "escalation_rate": "taxa_escalacao",
    "tickets": "tickets_suporte",
    "avg_sat": "csat_medio",
    "total_usage": "uso_total",
    "errors_per_use": "erros_por_uso",
    "risk_score": "score_risco",
    "risk_band": "faixa_risco",
    "mrr_priority": "prioridade_mrr",
    "why_risk": "motivo_risco",
    "status_conta": "status_conta",
    "signup_date": "data_cadastro",
    "last_churn": "data_ultimo_churn",
    "last_usage": "data_ultimo_uso",
    "net_churned": "churn_liquido",
    "revolving_active": "conta_revolving",
}


def coalesce_plan_seats(acc: pd.DataFrame) -> pd.DataFrame:
    df = acc.copy()
    plan_sub = df["plan_tier_sub"] if "plan_tier_sub" in df.columns else None
    plan_acct = df["plan_tier_acct"] if "plan_tier_acct" in df.columns else None
    if plan_sub is not None and plan_acct is not None:
        df["plano_atual"] = plan_sub.fillna(plan_acct)
    elif plan_sub is not None:
        df["plano_atual"] = plan_sub
    elif plan_acct is not None:
        df["plano_atual"] = plan_acct
    elif "plan_tier" in df.columns:
        df["plano_atual"] = df["plan_tier"]

    seats_sub = df["seats_sub"] if "seats_sub" in df.columns else None
    seats_acct = df["seats_acct"] if "seats_acct" in df.columns else None
    if seats_sub is not None and seats_acct is not None:
        df["assentos"] = seats_sub.fillna(seats_acct).astype("Int64")
    elif seats_sub is not None:
        df["assentos"] = seats_sub
    elif seats_acct is not None:
        df["assentos"] = seats_acct
    elif "seats" in df.columns:
        df["assentos"] = df["seats"]

    drop = [c for c in df.columns if c.endswith("_acct") or c.endswith("_sub")]
    drop += [c for c in ("plan_tier", "seats") if c in df.columns]
    return df.drop(columns=drop, errors="ignore")


def attach_status(acc: pd.DataFrame) -> pd.DataFrame:
    df = acc.copy()
    df["status_conta"] = np.select(
        [df["net_churned"], df["revolving_active"] & ~df["net_churned"]],
        ["Churn líquido", "Ativa (revolving)"],
        default="Ativa estável",
    )
    return df


def to_export_frame(acc: pd.DataFrame) -> pd.DataFrame:
    """DataFrame limpo para CRM / dashboard (sem colunas duplicadas de merge)."""
    df = coalesce_plan_seats(acc)
    df = attach_status(df)
    cols = [
        "account_id",
        "account_name",
        "industry",
        "country",
        "referral_source",
        "plano_atual",
        "assentos",
        "is_trial",
        "mrr_amount",
        "arr_amount",
        "status_conta",
        "net_churned",
        "revolving_active",
        "signup_date",
        "last_churn",
        "last_usage",
        "churn_events",
        "tickets",
        "escalation_rate",
        "avg_sat",
        "total_usage",
        "errors_per_use",
        "features_used",
        "risk_score",
        "risk_band",
        "mrr_priority",
        "why_risk",
    ]
    present = [c for c in cols if c in df.columns]
    out = df[present].copy()
    if "is_trial" in out.columns:
        out["is_trial"] = out["is_trial"].map({True: "Sim", False: "Não", "True": "Sim", "False": "Não"})
    if "escalation_rate" in out.columns:
        out["taxa_escalacao_pct"] = (out["escalation_rate"].fillna(0) * 100).round(1)
        out = out.drop(columns=["escalation_rate"])
    out = out.rename(columns=EXPORT_RENAME)
    if "canal_aquisicao" in out.columns:
        out["canal_aquisicao"] = out["canal_aquisicao"].map(label_canal)
    if "churn_liquido" in out.columns:
        out["churn_liquido"] = out["churn_liquido"].astype(bool)
    for col in ("data_cadastro", "data_ultimo_churn", "data_ultimo_uso"):
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], errors="coerce").dt.strftime("%Y-%m-%d")
    return out


def plan_column(acc: pd.DataFrame) -> str:
    if "plano_atual" in acc.columns:
        return "plano_atual"
    if "plan_tier_sub" in acc.columns:
        return "plan_tier_sub"
    return "plan_tier_acct"
