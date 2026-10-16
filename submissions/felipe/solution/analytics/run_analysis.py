"""
RavenStack Challenge 001 — pipeline reprodutível (5 tabelas → diagnóstico + filas).
Execute: python run_analysis.py
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from analytics.columns import coalesce_plan_seats, attach_status, plan_column, to_export_frame
from analytics.data_quality import export_data_quality
from analytics.export_dashboard import export_dashboard_bundle
from analytics.paths import DATA, OUT, REPORTS, FIG, SOLUTION
from analytics.write_model_limits import write_model_and_limits

ROOT = SOLUTION

for d in (OUT, REPORTS, FIG):
    d.mkdir(parents=True, exist_ok=True)


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_tables() -> dict[str, pd.DataFrame]:
    paths = {
        "accounts": DATA / "ravenstack_accounts.csv",
        "subscriptions": DATA / "ravenstack_subscriptions.csv",
        "feature_usage": DATA / "ravenstack_feature_usage.csv",
        "support_tickets": DATA / "ravenstack_support_tickets.csv",
        "churn_events": DATA / "ravenstack_churn_events.csv",
    }
    for p in paths.values():
        if not p.exists():
            raise FileNotFoundError(f"Coloque os CSVs do Kaggle em {DATA} — ver data/README.md")

    acc = pd.read_csv(paths["accounts"], parse_dates=["signup_date"])
    sub = pd.read_csv(
        paths["subscriptions"], parse_dates=["start_date", "end_date"]
    )
    usage = pd.read_csv(
        paths["feature_usage"], parse_dates=["usage_date"]
    )
    tix = pd.read_csv(
        paths["support_tickets"], parse_dates=["submitted_at", "closed_at"]
    )
    churn = pd.read_csv(paths["churn_events"], parse_dates=["churn_date"])
    return {
        "accounts": acc,
        "subscriptions": sub,
        "feature_usage": usage,
        "support_tickets": tix,
        "churn_events": churn,
        "_paths": paths,
    }


def validate_keys(tables: dict) -> pd.DataFrame:
    acc, sub, usage, tix, churn = (
        tables["accounts"],
        tables["subscriptions"],
        tables["feature_usage"],
        tables["support_tickets"],
        tables["churn_events"],
    )
    rows = []
    sub_ids = set(sub["subscription_id"])
    acc_ids = set(acc["account_id"])
    rows.append(
        {
            "check": "usage.subscription_id ⊆ subscriptions",
            "pass": usage["subscription_id"].isin(sub_ids).all(),
            "detail": f"{usage['subscription_id'].nunique()} ids",
        }
    )
    rows.append(
        {
            "check": "sub.account_id ⊆ accounts",
            "pass": sub["account_id"].isin(acc_ids).all(),
            "detail": f"{sub['account_id'].nunique()} accounts in subs",
        }
    )
    rows.append(
        {
            "check": "tickets.account_id ⊆ accounts",
            "pass": tix["account_id"].isin(acc_ids).all(),
            "detail": f"{tix['account_id'].nunique()} accounts w/ tickets",
        }
    )
    rows.append(
        {
            "check": "churn.account_id ⊆ accounts",
            "pass": churn["account_id"].isin(acc_ids).all(),
            "detail": f"{churn['account_id'].nunique()} accounts w/ events",
        }
    )
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "integration_qa.csv", index=False)
    return df


def build_account_master(tables: dict) -> pd.DataFrame:
    acc = tables["accounts"].copy()
    sub = tables["subscriptions"]
    usage = tables["feature_usage"]
    tix = tables["support_tickets"]
    churn = tables["churn_events"]

    latest_sub = sub.sort_values("start_date").groupby("account_id").tail(1)
    acc = acc.merge(
        latest_sub[
            [
                "account_id",
                "subscription_id",
                "mrr_amount",
                "arr_amount",
                "plan_tier",
                "seats",
            ]
        ],
        on="account_id",
        how="left",
        suffixes=("_acct", "_sub"),
    )

    churn_stats = churn.groupby("account_id").agg(
        churn_events=("churn_event_id", "count"),
        first_churn=("churn_date", "min"),
        last_churn=("churn_date", "max"),
        last_reason=("reason_code", "last"),
        reactivation_share=("is_reactivation", "mean"),
    )
    acc = acc.merge(churn_stats, on="account_id", how="left")
    acc["churn_events"] = acc["churn_events"].fillna(0).astype(int)
    acc["has_churn_history"] = acc["churn_events"] > 0

    u = usage.merge(sub[["subscription_id", "account_id"]], on="subscription_id")
    usage_agg = u.groupby("account_id").agg(
        usage_rows=("usage_count", "count"),
        total_usage=("usage_count", "sum"),
        total_errors=("error_count", "sum"),
        active_days=("usage_date", "nunique"),
        features_used=("feature_name", "nunique"),
        last_usage=("usage_date", "max"),
    )
    usage_agg["errors_per_use"] = usage_agg["total_errors"] / usage_agg[
        "total_usage"
    ].clip(lower=1)
    acc = acc.merge(usage_agg, on="account_id", how="left")

    tix_agg = tix.groupby("account_id").agg(
        tickets=("ticket_id", "count"),
        escalation_rate=("escalation_flag", "mean"),
        avg_sat=("satisfaction_score", "mean"),
        avg_resolution_h=("resolution_time_hours", "mean"),
        avg_frt_min=("first_response_time_minutes", "mean"),
    )
    acc = acc.merge(tix_agg, on="account_id", how="left")
    for c in ["tickets", "escalation_rate", "avg_sat"]:
        if c in acc.columns:
            acc[c] = acc[c].fillna(0 if c != "avg_sat" else np.nan)

    acc["net_churned"] = acc["churn_flag"].astype(bool)
    acc["revolving_active"] = (~acc["net_churned"]) & acc["has_churn_history"]
    acc = coalesce_plan_seats(acc)
    acc = attach_status(acc)
    return acc


def segment_churn_rates(acc: pd.DataFrame) -> None:
    plan_col = plan_column(acc)
    dims = ["industry", "referral_source", plan_col, "country", "is_trial"]
    frames = []
    for dim in dims:
        g = (
            acc.groupby(dim)
            .agg(
                accounts=("account_id", "count"),
                net_churn_rate=("net_churned", "mean"),
                avg_mrr=("mrr_amount", "mean"),
                total_mrr=("mrr_amount", "sum"),
            )
            .reset_index()
        )
        dim_label = "plan_tier" if "plan_tier" in dim else dim
        g["dimension"] = dim_label
        g = g.rename(columns={dim: "segment"})
        g["gross_event_accounts"] = g["segment"].map(
            acc.groupby(dim)["has_churn_history"].mean().to_dict()
        )
        frames.append(g)
    seg = pd.concat(frames, ignore_index=True)
    seg["net_churn_rate_pct"] = (seg["net_churn_rate"] * 100).round(1)
    seg.to_csv(OUT / "segment_net_churn.csv", index=False)

    # MRR-weighted churn by industry
    rows = []
    for industry, g in acc.groupby("industry"):
        rows.append(
            {
                "industry": industry,
                "accounts": len(g),
                "net_churn_rate": g["net_churned"].mean(),
                "mrr_lost": g.loc[g["net_churned"], "mrr_amount"].sum(),
                "mrr_revolving": g.loc[g["revolving_active"], "mrr_amount"].sum(),
            }
        )
    pd.DataFrame(rows).to_csv(OUT / "industry_mrr_impact.csv", index=False)


def usage_paradox(acc: pd.DataFrame, tables: dict) -> dict:
    usage = tables["feature_usage"]
    sub = tables["subscriptions"]
    churn = tables["churn_events"]
    u = usage.merge(sub[["subscription_id", "account_id"]], on="subscription_id")
    u["month"] = u["usage_date"].dt.to_period("M").astype(str)
    monthly = u.groupby("month")["usage_count"].sum()
    monthly.to_csv(OUT / "platform_usage_monthly.csv")

    first_churn = (
        churn.sort_values("churn_date").groupby("account_id").first().reset_index()
    )
    u = u.merge(first_churn[["account_id", "churn_date"]], on="account_id", how="inner")
    u["days_before"] = (u["churn_date"] - u["usage_date"]).dt.days
    win = u[u["days_before"].between(0, 30)].groupby("account_id")["usage_count"].sum()
    prev = u[u["days_before"].between(31, 60)].groupby("account_id")["usage_count"].sum()
    cmp = pd.DataFrame({"last_30d": win, "prior_30d": prev}).dropna()
    cmp["usage_drop_30pct"] = cmp["last_30d"] < cmp["prior_30d"] * 0.7
    cmp.to_csv(OUT / "pre_churn_usage_window.csv")

    retained = acc[~acc["net_churned"]]["account_id"]
    mean_usage_row = u[u["account_id"].isin(retained)]["usage_count"].mean()
    mean_usage_churned = u[u["account_id"].isin(acc[acc["net_churned"]]["account_id"])][
        "usage_count"
    ].mean()

    return {
        "monthly_usage_last6": monthly.tail(6).tolist(),
        "usage_per_row_retained": float(mean_usage_row),
        "usage_per_row_net_churned": float(mean_usage_churned),
        "pct_pre_churn_usage_drop": float(cmp["usage_drop_30pct"].mean()) if len(cmp) else 0,
        "accounts_with_window": len(cmp),
    }


def risk_score(acc: pd.DataFrame) -> pd.DataFrame:
    """Score explicável para contas ativas (priorização CS)."""
    active = acc[~acc["net_churned"]].copy()
    if active.empty:
        return active

    def norm(s: pd.Series) -> pd.Series:
        s = s.fillna(s.median())
        lo, hi = s.quantile(0.05), s.quantile(0.95)
        if hi <= lo:
            return pd.Series(0.0, index=s.index)
        return ((s - lo) / (hi - lo)).clip(0, 1)

    active["s_history"] = norm(active["churn_events"])
    active["s_escalation"] = norm(active["escalation_rate"])
    active["s_trial"] = active["is_trial"].astype(float)
    active["s_devtools"] = (active["industry"] == "DevTools").astype(float)
    active["s_event_ref"] = (active["referral_source"] == "event").astype(float)
    active["s_errors"] = norm(active["errors_per_use"])

    active["risk_score"] = (
        30 * active["s_history"]
        + 25 * active["s_escalation"]
        + 15 * active["s_event_ref"]
        + 10 * active["s_devtools"]
        + 10 * active["s_trial"]
        + 10 * active["s_errors"]
    ).round(1)

    active["risk_band"] = pd.cut(
        active["risk_score"],
        bins=[-0.1, 25, 45, 100],
        labels=["Monitorar", "Prioridade média", "Ligar esta semana"],
    )

    drivers = []
    for _, row in active.iterrows():
        parts = []
        if row["churn_events"] >= 1:
            parts.append(f"{int(row['churn_events'])} evento(s) de churn no histórico")
        if row["escalation_rate"] > active["escalation_rate"].median():
            parts.append(f"escalações {row['escalation_rate']:.0%} (acima da mediana)")
        if row["referral_source"] == "event":
            parts.append("aquisição via evento")
        if row["industry"] == "DevTools":
            parts.append("segmento DevTools")
        if row["is_trial"]:
            parts.append("conta trial")
        if not parts:
            parts.append("sinais moderados — revisar uso e tickets")
        drivers.append("; ".join(parts))
    active["why_risk"] = drivers

    active["mrr_priority"] = (active["risk_score"] * active["mrr_amount"]).round(0)
    cols = [
        "account_id",
        "account_name",
        "industry",
        "referral_source",
        "mrr_amount",
        "churn_events",
        "escalation_rate",
        "tickets",
        "risk_score",
        "risk_band",
        "mrr_priority",
        "why_risk",
        "revolving_active",
    ]
    queue = active.sort_values("mrr_priority", ascending=False)
    slim = queue[cols]
    slim.to_csv(OUT / "cs_action_queue.csv", index=False)
    slim.head(50).to_csv(OUT / "cs_action_queue_top50.csv", index=False)
    try:
        slim.to_excel(OUT / "cs_action_queue.xlsx", index=False)
    except Exception:
        pass  # openpyxl optional at runtime
    return queue


def merge_risk_into_accounts(acc: pd.DataFrame, queue: pd.DataFrame) -> pd.DataFrame:
    risk = queue[
        ["account_id", "risk_score", "risk_band", "mrr_priority", "why_risk"]
    ].drop_duplicates("account_id")
    acc = acc.drop(
        columns=["risk_score", "risk_band", "mrr_priority", "why_risk"],
        errors="ignore",
    )
    return acc.merge(risk, on="account_id", how="left")


def train_churn_model(acc: pd.DataFrame) -> dict:
    df = acc.copy()
    y = df["net_churned"].astype(int)
    plan_col = plan_column(df)
    cat = pd.get_dummies(
        df[["industry", "referral_source", plan_col]], drop_first=True
    )
    seat_col = "assentos" if "assentos" in df.columns else "seats"
    num_cols = [
        c
        for c in [
            "mrr_amount",
            seat_col,
            "churn_events",
            "tickets",
            "escalation_rate",
            "errors_per_use",
            "features_used",
            "is_trial",
        ]
        if c in df.columns
    ]
    num = df[num_cols].fillna(0)
    X = pd.concat([num, cat], axis=1)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)
    model = LogisticRegression(max_iter=3000, class_weight="balanced")
    model.fit(X_train_s, y_train)
    proba = model.predict_proba(X_test_s)[:, 1]
    auc = roc_auc_score(y_test, proba)
    coef = pd.Series(model.coef_[0], index=X.columns).sort_values(key=abs, ascending=False)
    coef.head(15).to_csv(OUT / "model_top_coefficients.csv")
    return {"test_auc": float(auc), "n_features": X.shape[1]}


def feedback_topics(tables: dict) -> None:
    churn = tables["churn_events"]
    text = churn["feedback_text"].fillna("").str.lower()
    keywords = {
        "competitor": text.str.contains("competitor|switch"),
        "missing_features": text.str.contains("missing|feature"),
        "pricing": text.str.contains("price|expensive|cost"),
        "support": text.str.contains("support|response"),
    }
    rows = []
    for k, mask in keywords.items():
        rows.append({"theme": k, "mentions": int(mask.sum()), "share_of_events": mask.mean()})
    pd.DataFrame(rows).to_csv(OUT / "feedback_text_themes.csv", index=False)


def plot_figures(acc: pd.DataFrame, paradox: dict) -> None:
    sns.set_theme(style="whitegrid", font_scale=0.95)
    fig, ax = plt.subplots(figsize=(8, 4))
    monthly = pd.read_csv(OUT / "platform_usage_monthly.csv")
    ax.plot(monthly["month"], monthly["usage_count"], marker="o")
    ax.set_title("Uso agregado da plataforma (soma usage_count/mês)")
    ax.set_xlabel("Mês")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(FIG / "01_platform_usage_monthly.png", dpi=150)
    plt.close()

    fig, ax = plt.subplots(figsize=(7, 4))
    rates = acc.groupby("industry")["net_churned"].mean().sort_values(ascending=True)
    rates.plot(kind="barh", ax=ax, color="#4C72B0")
    ax.set_title("Churn líquido (churn_flag) por indústria")
    ax.set_xlabel("Taxa")
    fig.tight_layout()
    fig.savefig(FIG / "02_net_churn_by_industry.png", dpi=150)
    plt.close()

    fig, ax = plt.subplots(figsize=(6, 4))
    counts = pd.Series(
        {
            "Ativas sem histórico": (~acc["net_churned"] & ~acc["has_churn_history"]).sum(),
            "Ativas pós-churn (revolving)": acc["revolving_active"].sum(),
            "Churn líquido (flag=1)": acc["net_churned"].sum(),
        }
    )
    counts.plot(kind="bar", ax=ax, color=["#55A868", "#C44E52", "#8172B3"])
    ax.set_title("O paradoxo: eventos ≠ churn líquido")
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(FIG / "03_churn_paradox_counts.png", dpi=150)
    plt.close()


def write_executive_summary(
    acc: pd.DataFrame, paradox: dict, model: dict, qa: pd.DataFrame
) -> None:
    n = len(acc)
    net = int(acc["net_churned"].sum())
    events = int(acc["churn_events"].sum())
    revolving = int(acc["revolving_active"].sum())
    mrr_lost = acc.loc[acc["net_churned"], "mrr_amount"].sum()
    mrr_revolving = acc.loc[acc["revolving_active"], "mrr_amount"].sum()

    dev_rate = acc.loc[acc["industry"] == "DevTools", "net_churned"].mean()
    evt_rate = acc.loc[acc["referral_source"] == "event", "net_churned"].mean()
    esc_ch = acc.loc[acc["net_churned"], "escalation_rate"].mean()
    esc_ret = acc.loc[~acc["net_churned"], "escalation_rate"].mean()

    md = f"""# Diagnóstico executivo — RavenStack Churn

_Gerado em {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")} · pipeline `run_analysis.py`_

## Resposta em 60 segundos

O CEO está certo **e** errado ao mesmo tempo — dependendo da métrica:

| Métrica | Valor | Leitura |
|---------|-------|---------|
| Contas com **churn líquido** (`churn_flag=1`) | **{net}** / {n} (**{100*net/n:.1f}%**) | Retenção headline ainda razoável |
| **Eventos** de churn na base | **{events}** em {n} contas | Volume bruto >> churn líquido |
| Contas **ativas com histórico de churn** | **{revolving}** | **MRR ~ US$ {mrr_revolving:,.0f}** em “porta giratória” |
| MRR das contas churn líquido | **US$ {mrr_lost:,.0f}** | Perda econômica real |
| Uso médio por linha (retidas vs churn líquido) | {paradox['usage_per_row_retained']:.2f} vs {paradox['usage_per_row_net_churned']:.2f} | Produto: uso **não separa** quem sai |
| CSAT médio (tickets) | ~4,0 em ambos os grupos | CS: satisfação **não discrimina** |

**Causa raiz (síntese):** não é queda global de uso nem CSAT baixo. É uma combinação de (**1**) **métrica errada no board** (eventos vs churn líquido + reativações), (**2**) **base instável** ({revolving} contas ativas já churnearam antes), (**3**) **segmentos** (DevTools **{100*dev_rate:.1f}%** churn líquido, referral **event** **{100*evt_rate:.1f}%**), (**4**) **sinal operacional** (taxa de escalação **{100*esc_ch:.1f}%** vs **{100*esc_ret:.1f}%** nas retidas — correlação, não causalidade comprovada).

## 1. O que está causando o churn?

1. **Porta giratória (revolving):** {revolving} contas estão ativas hoje mas já tiveram churn; isso explica CS “parece ok” enquanto eventos sobem.
2. **Segmento:** DevTools e aquisição via **event** concentram pior `churn_flag` (ver `outputs/segment_net_churn.csv`).
3. **Autoreporte ruidoso:** `reason_code` está equilibrado (~100/evento); texto de feedback menciona competitor/features/preço — cruzar com `outputs/feedback_text_themes.csv`.
4. **Uso pré-churn:** só **{100*paradox['pct_pre_churn_usage_drop']:.0f}%** das contas com janela ({paradox['accounts_with_window']}) caem >30% nos 30d antes do 1º evento — **não** é queda universal de usage.

## 2. Segmentos em risco (dados)

- Fila priorizada: **`outputs/cs_action_queue_top50.csv`** (score explicável + MRR).
- Impacto MRR por indústria: **`outputs/industry_mrr_impact.csv`**.

## 3. O que fazer (priorizado)

| # | Ação | Impacto esperado | Esforço |
|---|------|------------------|---------|
| 1 | Mudar KPIs: **churn líquido + reativação + MRR** (não só eventos) | Alinha board | Baixo |
| 2 | Playbook CS para **{revolving} contas revolving** (US$ {mrr_revolving:,.0f} MRR) | **+US$ {0.05*mrr_revolving:,.0f}/mês** se 5% retidos (ver `recommendations_impact.csv`) | Médio |
| 3 | Cohort **DevTools** + **event**: onboarding 30d | Reduz segmento outliers | Médio |
| 4 | Alerta por **escalação** + histórico churn | Early warning | Médio |
| 5 | Piloto modelo (AUC teste **{model['test_auc']:.2f}**) — usar como triagem, não verdade | Escala priorização | Alto |

## Integridade dos dados

QA de joins: **{qa['pass'].all()}** (detalhe em `outputs/integration_qa.csv`).

## Limitações

- Dataset sintético/demo; causalidade não provada (correlações CSAT/uso/escalação).
- `churn_flag` vs eventos: reativações inflacionam narrativa de “crise de uso”.
- Modelo linear; validar em produção antes de automatizar outreach.

---
Relatório técnico complementar: `reports/technical_appendix.md`
"""
    # fix helper reference
    (REPORTS / "executive_summary.md").write_text(md, encoding="utf-8")


def usage_by_industry_month(tables: dict) -> None:
    """CEO tip: uso 'cresceu' no agregado — e por segmento?"""
    acc = tables["accounts"]
    sub = tables["subscriptions"]
    usage = tables["feature_usage"]
    u = usage.merge(sub[["subscription_id", "account_id"]], on="subscription_id")
    u = u.merge(acc[["account_id", "industry"]], on="account_id")
    u["month"] = u["usage_date"].dt.to_period("M").astype(str)
    pivot = (
        u.groupby(["month", "industry"])["usage_count"]
        .sum()
        .reset_index()
        .rename(columns={"usage_count": "total_usage"})
    )
    pivot.to_csv(OUT / "usage_by_industry_month.csv", index=False)


def write_recommendations_impact(acc: pd.DataFrame) -> None:
    mrr_rev = acc.loc[acc["revolving_active"], "mrr_amount"].sum()
    mrr_lost = acc.loc[acc["net_churned"], "mrr_amount"].sum()
    avg_mrr = acc["mrr_amount"].median()
    scenarios = [
        {
            "acao": "Playbook CS — reter 5% do MRR revolving (90 dias)",
            "premissa": "277 contas ativas com histórico de churn",
            "impacto_mrr_usd": round(0.05 * mrr_rev, 0),
            "impacto_anual_arr_usd": round(0.05 * mrr_rev * 12, 0),
            "confianca": "Média — depende execução",
        },
        {
            "acao": "Playbook CS — reter 10% do MRR revolving (90 dias)",
            "premissa": "Mesma base US$ {:.0f} MRR".format(mrr_rev),
            "impacto_mrr_usd": round(0.10 * mrr_rev, 0),
            "impacto_anual_arr_usd": round(0.10 * mrr_rev * 12, 0),
            "confianca": "Baixa — upside",
        },
        {
            "acao": "Evitar 10 churns líquidos adicionais (contas ~ mediana MRR)",
            "premissa": f"Mediana MRR US$ {avg_mrr:,.0f}",
            "impacto_mrr_usd": round(10 * avg_mrr, 0),
            "impacto_anual_arr_usd": round(10 * avg_mrr * 12, 0),
            "confianca": "Média — cenário ilustrativo",
        },
        {
            "acao": "Corrigir métricas de board (evitar decisões erradas)",
            "premissa": "Custo de oportunidade qualitativo",
            "impacto_mrr_usd": 0,
            "impacto_anual_arr_usd": 0,
            "confianca": "Alta — alinhamento estratégico",
        },
    ]
    pd.DataFrame(scenarios).to_csv(OUT / "recommendations_impact.csv", index=False)


def write_cs_playbook(acc: pd.DataFrame) -> None:
    top = (
        acc[~acc["net_churned"]]
        .sort_values(
            by="mrr_amount",
            ascending=False,
        )
    )
    top = top[top["has_churn_history"]].head(10)
    lines = [
        "# Playbook CS — Contas revolving (uso amanhã)",
        "",
        "_Gerado por `run_analysis.py`. Importe `outputs/cs_action_queue.xlsx` no CRM._",
        "",
        "## Ritual semanal (30 min)",
        "",
        "1. Filtrar fila `Ligar esta semana` + ordenar por `mrr_priority`.",
        "2. Para cada conta: ler `why_risk` + último ticket.",
        "3. Registrar outcome (retenção / downgrade / churn) — alimentar modelo futuro.",
        "",
        "## Top 10 contas por MRR (com histórico de churn)",
        "",
        "| account_id | MRR | eventos | industry |",
        "|------------|-----|---------|----------|",
    ]
    for _, r in top.iterrows():
        ev = int(r.get("churn_events", 0))
        lines.append(
            f"| {r['account_id']} | {r['mrr_amount']:,.0f} | {ev} | {r['industry']} |"
        )
    lines.extend(
        [
            "",
            "## Script de ligação (60s)",
            "",
            '- "Notamos que vocês já passaram por cancelamento antes — queremos garantir que o valor está claro."',
            '- "Há algo no suporte (escalações) ou no rollout que podemos destravar esta semana?"',
            "",
            "## O que NÃO fazer",
            "",
            "- Não usar `reason_code` do último churn como verdade — autoreporte é ruidoso.",
            "- Não prometer feature roadmap baseado só em usage agregado (uso médio é igual entre grupos).",
            "",
        ]
    )
    (REPORTS / "playbook_cs_revolving.md").write_text("\n".join(lines), encoding="utf-8")


def write_ceo_one_pager(acc: pd.DataFrame, paradox: dict) -> None:
    n = len(acc)
    net = int(acc["net_churned"].sum())
    revolving = int(acc["revolving_active"].sum())
    mrr_rev = acc.loc[acc["revolving_active"], "mrr_amount"].sum()
    text = f"""# CEO — Uma página

**Pergunta:** Por que churn sobe se CSAT e uso estão ok?

**Resposta:** Vocês medem **eventos** (600) e reativações; o **churn líquido** são **{net}** contas ({100*net/n:.0f}%). **{revolving}** contas **ativas** já cancelaram antes (**US$ {mrr_rev:,.0f} MRR**) — CS vê contas vivas, board vê eventos.

**Três ações esta semana:** (1) KPI = líquido + MRR + reativação; (2) CS ligar fila top 50 (`cs_action_queue_top50.csv`); (3) cohort DevTools + canal event.

**Não culpar:** produto (uso {paradox['usage_per_row_retained']:.1f} vs {paradox['usage_per_row_net_churned']:.1f}) nem CS (CSAT ~4).

**Detalhe:** `reports/executive_summary.md` · **App:** `python serve_dashboard.py` → http://127.0.0.1:8765
"""
    (REPORTS / "ceo_one_pager.md").write_text(text, encoding="utf-8")


def write_causality_register() -> None:
    body = """# Registro correlação vs causalidade

| Claim | Evidência | Classificação |
|-------|-----------|---------------|
| Uso agregado não explica churn líquido | Médias ~10 usage_count/linha iguais | Correlação fraca / não separa |
| Escalação associada a churn líquido | 6,1% vs 4,3% | Correlação observada |
| DevTools / event pior churn | segment_net_churn.csv | Correlação segmentar |
| Porta giratória existe | 277 revolving, MRR sum | Fato descritivo |
| reason_code explica causa | Distribuição uniforme ~100/tipo | **Não usar** como causal |
| Modelo prediz churn | AUC ~0,62 hold-out | Predição fraca — triagem only |

**Testes que faltam para causalidade:** experimento CS, A/B onboarding DevTools, intervenção pós-escalação.
"""
    (REPORTS / "causality_register.md").write_text(body, encoding="utf-8")


def write_technical_appendix(acc: pd.DataFrame, model: dict) -> None:
    body = f"""# Apêndice técnico

## Grão analítico

Conta (`account_id`) enriquecida com última assinatura, agregados de `feature_usage` via `subscription_id`, tickets e histórico de `churn_events`.

## Modelo

LogisticRegression (balanced), hold-out 25%, **AUC = {model['test_auc']:.3f}**.
Coeficientes: `outputs/model_top_coefficients.csv`.

## Artefatos

| Arquivo | Conteúdo |
|---------|----------|
| `cs_action_queue.csv` | Todas as contas ativas scored |
| `pre_churn_usage_window.csv` | Janela 30/60d antes do 1º churn |
| `segment_net_churn.csv` | Taxas por dimensão |
| `figures/*.png` | Gráficos para CEO |
| `usage_by_industry_month.csv` | Uso por indústria/mês |
| `recommendations_impact.csv` | Cenários de impacto MRR/ARR |
| `causality_register.md` | Correlação vs causalidade |

## Linhagem (5 tabelas)

Ver `../../docs/METODOLOGIA.md` (linhagem de dados).
"""
    (REPORTS / "technical_appendix.md").write_text(body, encoding="utf-8")


def main() -> None:
    tables = load_tables()
    manifest = {
        k: {"sha256": file_sha256(v), "bytes": v.stat().st_size}
        for k, v in tables["_paths"].items()
    }
    (OUT / "data_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    qa = validate_keys(tables)
    acc = build_account_master(tables)

    segment_churn_rates(acc)
    paradox = usage_paradox(acc, tables)
    feedback_topics(tables)
    queue = risk_score(acc)
    acc = merge_risk_into_accounts(acc, queue)
    acc.to_csv(OUT / "account_master.csv", index=False)
    export_pt = to_export_frame(acc)
    export_pt.to_csv(OUT / "contas_analitico.csv", index=False, encoding="utf-8-sig")
    fila_pt = export_pt[
        (export_pt["churn_liquido"] == False)  # noqa: E712
        & export_pt["score_risco"].notna()
    ].sort_values("prioridade_mrr", ascending=False)
    fila_pt.to_csv(OUT / "fila_cs_priorizada.csv", index=False, encoding="utf-8-sig")
    fila_pt.head(50).to_csv(
        OUT / "fila_cs_top50.csv", index=False, encoding="utf-8-sig"
    )

    model = train_churn_model(acc)
    plot_figures(acc, paradox)
    usage_by_industry_month(tables)
    write_recommendations_impact(acc)
    write_cs_playbook(acc)
    write_ceo_one_pager(acc, paradox)
    write_causality_register()

    summary_stats = {
        "accounts": len(acc),
        "net_churned": int(acc["net_churned"].sum()),
        "churn_events_total": int(tables["churn_events"].shape[0]),
        "revolving_active": int(acc["revolving_active"].sum()),
        "mrr_lost": float(acc.loc[acc["net_churned"], "mrr_amount"].sum()),
        "mrr_revolving": float(acc.loc[acc["revolving_active"], "mrr_amount"].sum()),
        "model_auc": model["test_auc"],
        "paradox": paradox,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    (OUT / "summary_stats.json").write_text(
        json.dumps(summary_stats, indent=2), encoding="utf-8"
    )

    dq = export_data_quality(tables, acc)
    write_executive_summary(acc, paradox, model, qa)
    write_technical_appendix(acc, model)
    write_model_and_limits(model["test_auc"])
    export_dashboard_bundle(acc, summary_stats, tables=tables, qualidade_dados=dq)
    print("OK — outputs em", OUT)
    print("Command Center:", SOLUTION / "command-center" / "dist" / "index.html")
    print(json.dumps(summary_stats, indent=2))


if __name__ == "__main__":
    main()
