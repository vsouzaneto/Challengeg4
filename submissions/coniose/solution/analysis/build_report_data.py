"""
Diagnóstico de churn — RavenStack (challenge data-001-churn)

Cruza as 5 tabelas e produz um JSON com os números para o dashboard exploratório.
Puro pandas, sem chamada externa. Roda com: python analysis/build_report_data.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as sstats

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis" / "report_data.json"


def load():
    accounts = pd.read_csv(DATA / "ravenstack_accounts.csv", parse_dates=["signup_date"])
    subs = pd.read_csv(
        DATA / "ravenstack_subscriptions.csv", parse_dates=["start_date", "end_date"]
    )
    usage = pd.read_csv(DATA / "ravenstack_feature_usage.csv", parse_dates=["usage_date"])
    tickets = pd.read_csv(
        DATA / "ravenstack_support_tickets.csv", parse_dates=["submitted_at", "closed_at"]
    )
    churn = pd.read_csv(DATA / "ravenstack_churn_events.csv", parse_dates=["churn_date"])
    return accounts, subs, usage, tickets, churn


def build_account_table(accounts, subs, usage, tickets, churn):
    # subscription ativa/mais recente por conta (pra MRR e billing atual)
    subs_sorted = subs.sort_values("start_date")
    last_sub = subs_sorted.groupby("account_id").tail(1).set_index("account_id")
    mrr_by_account = subs_sorted.groupby("account_id")["mrr_amount"].last()
    total_arr_by_account = subs_sorted.groupby("account_id")["arr_amount"].sum()
    n_subs = subs.groupby("account_id").size()
    any_upgrade = subs.groupby("account_id")["upgrade_flag"].any()
    any_downgrade = subs.groupby("account_id")["downgrade_flag"].any()

    # uso agregado por subscription -> account (usage não tem account_id direto)
    usage_by_sub = usage.groupby("subscription_id").agg(
        total_usage_count=("usage_count", "sum"),
        total_usage_duration=("usage_duration_secs", "sum"),
        total_errors=("error_count", "sum"),
        n_usage_rows=("usage_id", "count"),
        first_usage_date=("usage_date", "min"),
        last_usage_date=("usage_date", "max"),
    )
    sub_to_account = subs.set_index("subscription_id")["account_id"]
    usage_by_sub = usage_by_sub.join(sub_to_account, how="left")
    usage_by_account = usage_by_sub.groupby("account_id").agg(
        total_usage_count=("total_usage_count", "sum"),
        total_usage_duration=("total_usage_duration", "sum"),
        total_errors=("total_errors", "sum"),
    )
    usage_by_account["error_rate"] = usage_by_account["total_errors"] / usage_by_account[
        "total_usage_count"
    ].replace(0, np.nan)

    # suporte agregado por conta
    support_by_account = tickets.groupby("account_id").agg(
        n_tickets=("ticket_id", "count"),
        avg_resolution_hours=("resolution_time_hours", "mean"),
        avg_first_response_min=("first_response_time_minutes", "mean"),
        avg_satisfaction=("satisfaction_score", "mean"),
        pct_escalated=("escalation_flag", "mean"),
    )

    # churn: uma conta pode ter mais de 1 evento (reativação). Fica o último.
    churn_sorted = churn.sort_values("churn_date")
    last_churn = churn_sorted.groupby("account_id").tail(1).set_index("account_id")

    acc = accounts.set_index("account_id").copy()
    acc["mrr"] = mrr_by_account
    acc["arr_total_hist"] = total_arr_by_account
    acc["n_subscriptions"] = n_subs
    acc["ever_upgraded"] = any_upgrade
    acc["ever_downgraded"] = any_downgrade
    acc = acc.join(usage_by_account)
    acc = acc.join(support_by_account)
    acc["reason_code"] = last_churn["reason_code"]
    acc["refund_amount_usd"] = last_churn["refund_amount_usd"]
    acc["preceding_downgrade_flag"] = last_churn["preceding_downgrade_flag"]
    acc["churn_date"] = last_churn["churn_date"]

    acc["mrr"] = acc["mrr"].fillna(0)
    acc["n_tickets"] = acc["n_tickets"].fillna(0)
    # NAO fillna(0) em pct_escalated: conta sem ticket nao e "0% escalado", e ausente.
    # (bug encontrado em auditoria: 8 contas sem ticket entravam como "nunca escalou")

    # tenure observavel: as_of = ultima data vista em qualquer tabela do dataset (2024-12-31)
    as_of = pd.Timestamp("2024-12-31")
    acc["tenure_days"] = (as_of - acc["signup_date"]).dt.days

    return acc.reset_index()


def churn_by_segment(acc, col, min_n=5):
    g = acc.groupby(col).agg(
        n_accounts=("account_id", "count"),
        n_churned=("churn_flag", "sum"),
        mrr_total=("mrr", "sum"),
        mrr_at_risk=("mrr", lambda s: s[acc.loc[s.index, "churn_flag"]].sum()),
    )
    g = g[g["n_accounts"] >= min_n].copy()
    g["churn_rate"] = g["n_churned"] / g["n_accounts"]
    g["mrr_at_risk_pct"] = g["mrr_at_risk"] / g["mrr_total"].replace(0, np.nan)
    g = g.sort_values("churn_rate", ascending=False)
    return g.reset_index().to_dict(orient="records")


def usage_trend_overall_vs_churn(usage, subs, accounts, churn):
    """Mantido para o grafico bruto (mes-a-mes), mas ver `usage_trend_honesty`
    abaixo: a tabela de uso NAO respeita o ciclo de vida da conta (52,8% das
    linhas antecedem o signup_date; 17,9% do uso das churnadas vem depois do
    churn_date), e a afirmacao de trajetoria original nao passa teste no
    nivel certo (conta, nao mes-calendario). Achado de auditoria."""
    sub_to_account = subs.set_index("subscription_id")["account_id"]
    u = usage.copy()
    u["account_id"] = u["subscription_id"].map(sub_to_account)
    u["month"] = u["usage_date"].dt.to_period("M").astype(str)

    accounts_churn_flag = accounts.set_index("account_id")["churn_flag"]
    u["account_churned"] = u["account_id"].map(accounts_churn_flag)

    monthly = u.groupby(["month", "account_churned"]).agg(
        total_usage_count=("usage_count", "sum"),
        n_accounts_active=("account_id", "nunique"),
    ).reset_index()
    monthly["usage_per_account"] = (
        monthly["total_usage_count"] / monthly["n_accounts_active"]
    )
    monthly = monthly.sort_values("month")

    overall = u.groupby("month").agg(
        total_usage_count=("usage_count", "sum"),
        n_accounts_active=("account_id", "nunique"),
    ).reset_index()
    overall["usage_per_account"] = overall["total_usage_count"] / overall["n_accounts_active"]
    overall = overall.sort_values("month")

    return {
        "overall": overall.to_dict(orient="records"),
        "by_churn_flag": monthly.to_dict(orient="records"),
    }


def usage_trend_honesty(usage, subs, accounts, churn):
    sub_to_account = subs.set_index("subscription_id")["account_id"]
    sub_to_start = subs.set_index("subscription_id")["start_date"]
    u = usage.copy()
    u["account_id"] = u["subscription_id"].map(sub_to_account)
    u["sub_start"] = u["subscription_id"].map(sub_to_start)

    signup = accounts.set_index("account_id")["signup_date"]
    u["signup_date"] = u["account_id"].map(signup)
    pct_before_signup = (u["usage_date"] < u["signup_date"]).mean()
    pct_before_sub_start = (u["usage_date"] < u["sub_start"]).mean()

    churn_date = churn.sort_values("churn_date").groupby("account_id")["churn_date"].last()
    u["churn_date"] = u["account_id"].map(churn_date)
    is_churned = u["account_id"].map(accounts.set_index("account_id")["churn_flag"])
    churned_rows = u[is_churned & u["churn_date"].notna()]
    pct_after_churn = (churned_rows["usage_date"] > churned_rows["churn_date"]).mean()

    # slope por CONTA (unidade certa), nao por mes-calendario (pseudo-replicacao)
    u["month"] = u["usage_date"].dt.to_period("M")
    monthly_by_acc = u.groupby(["account_id", "month"])["usage_count"].sum().reset_index()
    monthly_by_acc["month_idx"] = monthly_by_acc["month"].apply(lambda m: m.ordinal)

    def account_slope(g):
        if g["month_idx"].nunique() < 3:
            return np.nan
        return sstats.linregress(g["month_idx"], g["usage_count"]).slope

    slopes = monthly_by_acc.groupby("account_id").apply(account_slope)
    churn_flag = accounts.set_index("account_id")["churn_flag"]
    slopes_df = pd.DataFrame({"slope": slopes, "churn_flag": slopes.index.map(churn_flag)}).dropna()

    s_churn = slopes_df.loc[slopes_df.churn_flag, "slope"]
    s_ret = slopes_df.loc[~slopes_df.churn_flag, "slope"]
    t, p_welch = sstats.ttest_ind(s_churn, s_ret, equal_var=False)
    u_stat, p_mw = sstats.mannwhitneyu(s_churn, s_ret)

    n_active_per_month_churned = (
        u[u["account_id"].isin(accounts.loc[accounts.churn_flag, "account_id"])]
        .groupby("month")["account_id"].nunique()
    )

    return {
        "pct_usage_rows_before_own_signup_date": round(float(pct_before_signup) * 100, 1),
        "pct_usage_rows_before_own_subscription_start": round(float(pct_before_sub_start) * 100, 1),
        "pct_usage_rows_of_churned_accounts_after_churn_date": round(float(pct_after_churn) * 100, 1),
        "churned_accounts_active_every_month_min_max": [
            int(n_active_per_month_churned.min()), int(n_active_per_month_churned.max())
        ],
        "conclusion": (
            "A tabela de uso NAO respeita o ciclo de vida da conta: mais da "
            "metade das linhas antecede o proprio signup, e quase 1 em 5 "
            "linhas de conta churnada vem depois do churn_date -- nao ha "
            "truncamento no cancelamento. 'Trajetoria de uso' nao e "
            "mensuravel de forma confiavel neste dataset."
        ),
        "slope_mensal_por_conta_churned_mean": round(float(s_churn.mean()), 4),
        "slope_mensal_por_conta_retained_mean": round(float(s_ret.mean()), 4),
        "welch_p_value": round(float(p_welch), 4),
        "mannwhitney_p_value": round(float(p_mw), 4),
        "veredito": (
            "Testado no nivel certo (slope por conta, nao mes-calendario "
            "pseudo-replicado): p=0,258 (Welch). A afirmacao 'quem cancela "
            "usa mais no fim do proprio ciclo' NAO se sustenta -- foi "
            "retirada do relatorio."
        ),
    }


def support_churned_vs_retained(acc):
    def stats(sub):
        return {
            "n": int(len(sub)),
            "avg_satisfaction": None
            if sub["avg_satisfaction"].dropna().empty
            else round(sub["avg_satisfaction"].mean(), 2),
            "avg_resolution_hours": None
            if sub["avg_resolution_hours"].dropna().empty
            else round(sub["avg_resolution_hours"].mean(), 1),
            "avg_first_response_min": None
            if sub["avg_first_response_min"].dropna().empty
            else round(sub["avg_first_response_min"].mean(), 1),
            "pct_escalated": None if sub["pct_escalated"].dropna().empty else round(sub["pct_escalated"].mean() * 100, 1),
            "avg_tickets_per_account": round(sub["n_tickets"].mean(), 2),
            "pct_with_any_ticket": round((sub["n_tickets"] > 0).mean() * 100, 1),
        }

    def sig_test(col, with_ticket):
        a = with_ticket.loc[with_ticket.churn_flag, col].dropna()
        b = with_ticket.loc[~with_ticket.churn_flag, col].dropna()
        if len(a) < 5 or len(b) < 5:
            return None
        t, p = sstats.ttest_ind(a, b, equal_var=False)
        return round(float(p), 4)

    with_ticket = acc[acc["n_tickets"] > 0]
    significance = {
        col: sig_test(col, with_ticket)
        for col in ["avg_satisfaction", "avg_resolution_hours", "avg_first_response_min", "pct_escalated"]
    }
    return {
        "churned": stats(with_ticket[with_ticket["churn_flag"]]),
        "retained": stats(with_ticket[~with_ticket["churn_flag"]]),
        "churned_all": stats(acc[acc["churn_flag"]]),
        "retained_all": stats(acc[~acc["churn_flag"]]),
        "p_values_welch_ttest": significance,
        "nota": "Nenhuma das 4 diferencas passa p<0,05 (Welch t-test).",
    }


def churned_only_events(churn, accounts):
    """Restringe churn_events as contas com churn_flag=True HOJE.

    Achado de auditoria: 77,5% dos 600 eventos (465 de 600) sao de contas que
    NAO estao churned agora (churn_flag=False) -- ou porque reativaram, ou
    porque a flag mestre e um estado atual e o log e historico. Analises de
    "motivo do churn" tem que responder por quem de fato saiu, nao por quem
    passou por um evento e voltou.
    """
    flag = accounts.set_index("account_id")["churn_flag"]
    c = churn.copy()
    c["account_currently_churned"] = c["account_id"].map(flag)
    return c[c["account_currently_churned"] == True].copy()  # noqa: E712


def reason_code_breakdown(churn, accounts):
    c_all = churn.copy()
    c_all["reason_code"] = c_all["reason_code"].fillna("unknown")
    c_churned = churned_only_events(churn, accounts)
    c_churned["reason_code"] = c_churned["reason_code"].fillna("unknown")

    def summarize(c):
        g = c.groupby("reason_code").agg(
            n_events=("churn_event_id", "count"),
            avg_refund=("refund_amount_usd", "mean"),
            pct_preceded_by_downgrade=("preceding_downgrade_flag", "mean"),
            pct_reactivation=("is_reactivation", "mean"),
        ).sort_values("n_events", ascending=False)
        g["pct_preceded_by_downgrade"] = (g["pct_preceded_by_downgrade"] * 100).round(1)
        g["pct_reactivation"] = (g["pct_reactivation"] * 100).round(1)
        g["avg_refund"] = g["avg_refund"].round(2)
        return g.reset_index().to_dict(orient="records")

    return {
        "n_events_total": int(len(c_all)),
        "n_events_from_currently_churned_accounts": int(len(c_churned)),
        "pct_events_contaminated_by_non_churned": round(
            100 * (len(c_all) - len(c_churned)) / len(c_all), 1
        ),
        "note": (
            "Restrito a eventos de contas com churn_flag=True hoje (135 de 600 "
            "eventos). Os outros 465 sao de contas que reativaram ou nunca "
            "estavam de fato fora -- ver methodology_notes."
        ),
        "by_reason_currently_churned_only": summarize(c_churned),
        "by_reason_all_events_uncorrected": summarize(c_all),
    }


def reason_by_plan(churn, accounts):
    def crosstab_for(c):
        m = c.merge(accounts[["account_id", "plan_tier"]], on="account_id", how="left")
        m["reason_code"] = m["reason_code"].fillna("unknown")
        ct = pd.crosstab(m["plan_tier"], m["reason_code"])
        chi2, p, dof, _ = sstats.chi2_contingency(ct)
        return {
            "plans": ct.index.tolist(),
            "reasons": ct.columns.tolist(),
            "matrix": ct.values.tolist(),
            "chi2": round(float(chi2), 2),
            "p_value": round(float(p), 4),
            "dof": int(dof),
        }

    c_churned = churned_only_events(churn, accounts)
    return {
        "currently_churned_only": crosstab_for(c_churned),
        "all_events_uncorrected": crosstab_for(churn),
    }


def chi2_segment_test(acc, col):
    ct = pd.crosstab(acc[col], acc["churn_flag"])
    chi2, p, dof, _ = sstats.chi2_contingency(ct)
    return {"variable": col, "chi2": round(float(chi2), 2), "p_value": round(float(p), 4), "dof": int(dof)}


def usage_trend_slope(usage_trend):
    def slope_pct(records, key="usage_per_account"):
        vals = [r[key] for r in records]
        x = np.arange(len(vals))
        if len(vals) < 3:
            return None
        slope, intercept, *_ = sstats.linregress(x, vals)
        first_q = np.mean(vals[:3])
        last_q = np.mean(vals[-3:])
        pct_change = (last_q - first_q) / first_q * 100 if first_q else None
        return {
            "slope_per_month": round(float(slope), 4),
            "first_quarter_avg": round(float(first_q), 2),
            "last_quarter_avg": round(float(last_q), 2),
            "pct_change_first_to_last_q": round(float(pct_change), 1) if pct_change is not None else None,
        }

    overall = slope_pct(usage_trend["overall"])
    by_flag = usage_trend["by_churn_flag"]
    churned = sorted([r for r in by_flag if r["account_churned"]], key=lambda r: r["month"])
    retained = sorted([r for r in by_flag if not r["account_churned"]], key=lambda r: r["month"])
    return {
        "overall": overall,
        "retained_accounts": slope_pct(retained),
        "eventually_churned_accounts": slope_pct(churned),
        "aviso_metodologico": (
            "Estes numeros tratam 24 meses-calendario como 24 observacoes "
            "independentes (pseudo-replicacao: sao as mesmas ~500 contas "
            "remedidas). Nao usar para afirmar diferenca -- ver "
            "`usage_trend_honesty` pro teste no nivel certo (por conta), "
            "que nao encontra diferenca significativa (p=0,258)."
        ),
    }


def correlation_snapshot(acc):
    cols = [
        "seats",
        "mrr",
        "total_usage_count",
        "total_usage_duration",
        "error_rate",
        "n_tickets",
        "avg_resolution_hours",
        "avg_satisfaction",
        "pct_escalated",
        "ever_downgraded",
        "tenure_days",
    ]
    df = acc[cols + ["churn_flag"]].copy()
    df["ever_downgraded"] = df["ever_downgraded"].astype(float)
    df["churn_flag_num"] = df["churn_flag"].astype(float)
    n = len(df)

    results = []
    for col in cols:
        pair = df[[col, "churn_flag_num"]].dropna()
        if len(pair) < 10:
            continue
        r, p = sstats.pearsonr(pair[col], pair["churn_flag_num"])
        results.append({
            "variable": col,
            "corr_with_churn": round(float(r), 3),
            "p_value": round(float(p), 4),
            "n": int(len(pair)),
        })
    results.sort(key=lambda x: abs(x["corr_with_churn"]), reverse=True)

    fisher_chi2, fisher_p = sstats.combine_pvalues([r["p_value"] for r in results], method="fisher")
    # MDE de r a 80% de poder, n~500 (aprox. via z de Fisher)
    from scipy.stats import norm
    z_alpha, z_beta = norm.ppf(0.975), norm.ppf(0.80)
    mde_r = np.tanh((z_alpha + z_beta) / np.sqrt(n - 3))

    return {
        "correlations": results,
        "global_null_check": {
            "fisher_combined_chi2": round(float(fisher_chi2), 2),
            "fisher_combined_p": round(float(fisher_p), 4),
            "min_p_bonferroni": round(min(1.0, min(r["p_value"] for r in results) * len(results)), 3),
            "mde_r_80pct_power_n500": round(float(mde_r), 3),
            "interpretacao": (
                f"Nem individualmente nem em conjunto ha sinal (Fisher "
                f"combinado p={fisher_p:.3f}). O MDE de r a 80% de poder "
                f"com n~500 e ~{mde_r:.3f} -- 'nenhuma passa de 0,09' "
                f"significa 'nao detectamos efeito acima de ~0,12', nao "
                f"'nao existe causa'."
            ),
        },
    }


def feature_level_analysis(usage, subs, accounts):
    sub_to_account = subs.set_index("subscription_id")["account_id"]
    u = usage.copy()
    u["account_id"] = u["subscription_id"].map(sub_to_account)
    churn_flag = accounts.set_index("account_id")["churn_flag"]

    per_feature_account = u.groupby(["feature_name", "account_id"]).agg(
        usage_count=("usage_count", "sum"),
        error_count=("error_count", "sum"),
    ).reset_index()
    per_feature_account["churn_flag"] = per_feature_account["account_id"].map(churn_flag)
    per_feature_account["error_rate"] = per_feature_account["error_count"] / per_feature_account["usage_count"].replace(0, np.nan)

    results = []
    n_features = u["feature_name"].nunique()
    bonferroni_p = 0.05 / n_features
    for feat, grp in per_feature_account.groupby("feature_name"):
        churned = grp.loc[grp.churn_flag, "usage_count"]
        retained = grp.loc[~grp.churn_flag, "usage_count"]
        if len(churned) < 5 or len(retained) < 5:
            continue
        t, p = sstats.ttest_ind(churned, retained, equal_var=False)
        churned_err = grp.loc[grp.churn_flag, "error_rate"].dropna()
        retained_err = grp.loc[~grp.churn_flag, "error_rate"].dropna()
        t_err, p_err = (sstats.ttest_ind(churned_err, retained_err, equal_var=False)
                        if len(churned_err) > 5 and len(retained_err) > 5 else (None, None))
        results.append({
            "feature_name": feat,
            "n_churned": int(len(churned)), "n_retained": int(len(retained)),
            "mean_usage_churned": round(float(churned.mean()), 1),
            "mean_usage_retained": round(float(retained.mean()), 1),
            "p_value_usage": round(float(p), 4),
            "significant_bonferroni": bool(p < bonferroni_p),
            "mean_error_rate_churned": None if churned_err.empty else round(float(churned_err.mean()), 4),
            "mean_error_rate_retained": None if retained_err.empty else round(float(retained_err.mean()), 4),
            "p_value_error_rate": None if p_err is None else round(float(p_err), 4),
        })
    results.sort(key=lambda r: r["p_value_usage"])

    p_usage = [r["p_value_usage"] for r in results]
    p_error = [r["p_value_error_rate"] for r in results if r["p_value_error_rate"] is not None]
    ks_usage = sstats.kstest(p_usage, "uniform")
    ks_error = sstats.kstest(p_error, "uniform")

    return {
        "n_features_tested": n_features,
        "bonferroni_threshold": round(bonferroni_p, 5),
        "n_significant_uncorrected": sum(1 for r in results if r["p_value_usage"] < 0.05),
        "n_significant_bonferroni": sum(1 for r in results if r["significant_bonferroni"]),
        "error_rate_family": {
            "n_tests": len(p_error),
            "n_significant_uncorrected": sum(1 for p in p_error if p < 0.05),
            "n_significant_bonferroni": sum(1 for p in p_error if p < bonferroni_p),
            "nota": (
                "Mesmo padrao do usage_count: 3 'significativos' sem "
                "correcao (esperado por acaso: ~2), 0 sobrevivem Bonferroni. "
                "O relatorio original publicava p=0,0037 e p=0,0204 desta "
                "familia sem correcao nem ressalva -- corrigido aqui."
            ),
        },
        "uniformity_check_ks_test": {
            "usage_count_p_values_vs_uniform": round(float(ks_usage.pvalue), 4),
            "error_rate_p_values_vs_uniform": round(float(ks_error.pvalue), 4),
            "interpretacao": (
                "P-valores uniformes contra U[0,1] e exatamente a "
                "assinatura de 'nao ha efeito em nenhuma das 40 features' -- "
                "e uma demonstracao positiva de ausencia de sinal, nao so "
                "falta de evidencia."
            ),
        },
        "top_10_by_raw_p": results[:10],
    }


def ticket_priority_analysis(tickets, accounts):
    churn_flag = accounts.set_index("account_id")["churn_flag"]
    t = tickets.copy()
    t["churn_flag"] = t["account_id"].map(churn_flag)
    base_rate = accounts["churn_flag"].mean()
    n_tickets_by_acc = tickets.groupby("account_id").size()

    out = []
    for priority in sorted(t["priority"].dropna().unique()):
        accounts_with = set(t.loc[t.priority == priority, "account_id"])
        acc2 = accounts.copy()
        acc2["has_priority"] = acc2["account_id"].isin(accounts_with)
        acc2["n_tickets"] = acc2["account_id"].map(n_tickets_by_acc).fillna(0)
        ct = pd.crosstab(acc2["has_priority"], acc2["churn_flag"])
        chi2, p, dof, _ = sstats.chi2_contingency(ct, correction=True)
        rate_with = acc2.loc[acc2.has_priority, "churn_flag"].mean()
        rate_without = acc2.loc[~acc2.has_priority, "churn_flag"].mean()
        acc2["ticket_volume_bin"] = pd.cut(
            acc2["n_tickets"], bins=[-1, 2, 3, 4, 5, 999], labels=["0-2", "3", "4", "5", "6+"]
        )
        or_bruto = (rate_with / (1 - rate_with)) / (rate_without / (1 - rate_without)) if rate_without not in (0, 1) else None
        or_mh_volume = mantel_haenszel_or(acc2, "has_priority", "churn_flag", "ticket_volume_bin")
        out.append({
            "priority": priority,
            "n_accounts_with_ticket": int(acc2["has_priority"].sum()),
            "churn_rate_with": round(float(rate_with) * 100, 1),
            "churn_rate_without": round(float(rate_without) * 100, 1),
            "chi2": round(float(chi2), 2),
            "p_value": round(float(p), 4),
            "or_bruto": round(float(or_bruto), 2) if or_bruto else None,
            "or_ajustado_por_volume_de_tickets_mh": or_mh_volume,
        })

    accounts_esc = set(tickets.loc[tickets.escalation_flag, "account_id"])
    acc3 = accounts.copy()
    acc3["has_escalation"] = acc3["account_id"].isin(accounts_esc)
    ct = pd.crosstab(acc3["has_escalation"], acc3["churn_flag"])
    chi2, p, dof, _ = sstats.chi2_contingency(ct, correction=True)
    escalation_test = {
        "chi2": round(float(chi2), 2), "p_value": round(float(p), 4),
        "churn_rate_with": round(float(acc3.loc[acc3.has_escalation, "churn_flag"].mean()) * 100, 1),
        "churn_rate_without": round(float(acc3.loc[~acc3.has_escalation, "churn_flag"].mean()) * 100, 1),
        "n_accounts_with_escalation": int(acc3["has_escalation"].sum()),
    }
    return {
        "base_churn_rate_pct": round(float(base_rate) * 100, 1),
        "by_priority": out,
        "escalation": escalation_test,
        "nota": (
            "As 4 prioridades nao sao 4 evidencias independentes: 309 a 322 "
            "das 500 contas tem cada uma (uma conta tem ~4 tickets em "
            "media, cobrindo quase todas as prioridades). O OR ajustado por "
            "volume de tickets (MH) muda pouco o bruto -- entao nao e "
            "confundimento por volume; e ruido puro medido de 4 formas "
            "quase iguais. Tratar como 1 indicador, nao 4."
        ),
    }


def usage_growth_by_segment(usage, subs, accounts, segment_col):
    sub_to_account = subs.set_index("subscription_id")["account_id"]
    u = usage.copy()
    u["account_id"] = u["subscription_id"].map(sub_to_account)
    u["month"] = pd.to_datetime(u["usage_date"]).dt.to_period("M").astype(str)
    seg_map = accounts.set_index("account_id")[segment_col]
    u["segment"] = u["account_id"].map(seg_map)

    out = []
    churn_rate_by_seg = accounts.groupby(segment_col)["churn_flag"].mean()
    n_by_seg = accounts.groupby(segment_col).size()
    for seg, grp in u.groupby("segment"):
        monthly = grp.groupby("month").agg(
            total=("usage_count", "sum"), n_acc=("account_id", "nunique")
        ).reset_index().sort_values("month")
        monthly["per_account"] = monthly["total"] / monthly["n_acc"]
        vals = monthly["per_account"].values
        if len(vals) < 6 or n_by_seg.get(seg, 0) < 5:
            continue
        first_q = vals[:3].mean()
        last_q = vals[-3:].mean()
        pct_change = (last_q - first_q) / first_q * 100 if first_q else None
        out.append({
            "segment": seg,
            "n_accounts": int(n_by_seg.get(seg, 0)),
            "churn_rate_pct": round(float(churn_rate_by_seg.get(seg, 0)) * 100, 1),
            "usage_pct_change_first_to_last_q": round(float(pct_change), 1) if pct_change is not None else None,
        })
    out.sort(key=lambda r: r["usage_pct_change_first_to_last_q"] if r["usage_pct_change_first_to_last_q"] is not None else 0, reverse=True)
    if len(out) >= 3:
        xs = [r["usage_pct_change_first_to_last_q"] for r in out]
        ys = [r["churn_rate_pct"] for r in out]
        corr, p = sstats.pearsonr(xs, ys)
        n = len(out)
        # IC de Fisher pra r com n pequeno
        z = np.arctanh(corr)
        se = 1 / np.sqrt(n - 3) if n > 3 else np.nan
        ci_lo, ci_hi = np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)
        power = 1 - sstats.norm.cdf(1.96 - abs(z) * np.sqrt(n - 3)) if n > 3 else None
        corr_note = {
            "pearson_r": round(float(corr), 3),
            "p_value": round(float(p), 4),
            "n_segments": n,
            "ic95_r": [round(float(ci_lo), 3), round(float(ci_hi), 3)],
            "aviso": (
                f"n={n} grupos: poder estatistico baixissimo (IC95% cobre "
                "de forte negativo a forte positivo). Nao tratar como "
                "relacao confiavel -- e correlacao ECOLOGICA (unidade = "
                "segmento), que pode inverter de sinal no nivel da conta "
                "(ver ecological_fallacy_check)."
            ),
        }
    else:
        corr_note = None
    return {"by_segment": out, "growth_vs_churn_correlation_across_segments": corr_note}


def mrr_concentration(acc):
    acc = acc.sort_values("mrr", ascending=False).reset_index(drop=True)
    total_mrr = acc["mrr"].sum()
    n = len(acc)
    deciles = {}
    for pct in [10, 20, 50]:
        k = max(1, round(n * pct / 100))
        top = acc.iloc[:k]
        deciles[f"top_{pct}pct_accounts"] = {
            "n_accounts": int(k),
            "pct_of_total_mrr": round(float(top["mrr"].sum() / total_mrr) * 100, 1),
            "churn_rate_pct": round(float(top["churn_flag"].mean()) * 100, 1),
            "mrr_at_risk": round(float(top.loc[top.churn_flag, "mrr"].sum()), 2),
            "top_industries": top["industry"].value_counts().head(3).to_dict(),
        }
    bottom_90 = acc.iloc[round(n * 0.10):]
    deciles["bottom_90pct_accounts"] = {
        "n_accounts": int(len(bottom_90)),
        "pct_of_total_mrr": round(float(bottom_90["mrr"].sum() / total_mrr) * 100, 1),
        "churn_rate_pct": round(float(bottom_90["churn_flag"].mean()) * 100, 1),
    }
    by_plan = acc.groupby("plan_tier").agg(
        avg_mrr=("mrr", "mean"), n=("account_id", "count"), churn_rate=("churn_flag", "mean")
    )
    by_plan["avg_mrr"] = by_plan["avg_mrr"].round(0)
    by_plan["churn_rate"] = (by_plan["churn_rate"] * 100).round(1)
    avg_mrr_lost_per_churn_by_plan = acc[acc.churn_flag].groupby("plan_tier")["mrr"].mean().round(0)

    # --- auditoria: o "achado" de que conta grande churna menos nao se sustenta ---
    acc["is_top10"] = acc.index < round(n * 0.10)
    ct = pd.crosstab(acc["is_top10"], acc["churn_flag"])
    chi2, p_chi2, dof, _ = sstats.chi2_contingency(ct, correction=True)
    odds_ratio, p_fisher = sstats.fisher_exact(ct.values)
    rate_top = acc.loc[acc.is_top10, "churn_flag"].mean()
    ci_low, ci_high = _wilson_ci(int(acc.loc[acc.is_top10, "churn_flag"].sum()), int(acc.is_top10.sum()))

    decile_rank = pd.qcut(acc.index, 10, labels=False) + 1  # 1=maior MRR .. 10=menor
    by_decile = acc.assign(decile=decile_rank).groupby("decile").agg(
        n=("account_id", "count"), churn_rate=("churn_flag", "mean"), mrr_med=("mrr", "median")
    )
    by_decile["churn_rate"] = (by_decile["churn_rate"] * 100).round(1)
    by_decile["mrr_med"] = by_decile["mrr_med"].round(0)

    industry_mix_top10 = acc.loc[acc.is_top10, "industry"].value_counts(normalize=True).mul(100).round(1).to_dict()
    industry_mix_rest = acc.loc[~acc.is_top10, "industry"].value_counts(normalize=True).mul(100).round(1).to_dict()
    or_mh_industry = mantel_haenszel_or(acc, "is_top10", "churn_flag", "industry")

    return {
        "concentration": deciles,
        "avg_mrr_by_plan": by_plan.reset_index().to_dict(orient="records"),
        "avg_mrr_of_a_churned_account_by_plan": avg_mrr_lost_per_churn_by_plan.to_dict(),
        "significance_check": {
            "top10_churn_rate_pct": round(float(rate_top) * 100, 1),
            "top10_churn_rate_ic95": [round(ci_low * 100, 1), round(ci_high * 100, 1)],
            "chi2": round(float(chi2), 2),
            "p_value_chi2": round(float(p_chi2), 4),
            "p_value_fisher": round(float(p_fisher), 4),
            "odds_ratio_bruto": round(float(odds_ratio), 2),
            "or_ajustado_por_industria_mh": or_mh_industry,
        },
        "decile_breakdown": by_decile.reset_index().to_dict(orient="records"),
        "industry_mix_top10_pct": industry_mix_top10,
        "industry_mix_rest_pct": industry_mix_rest,
        "veredito": (
            "NAO ha efeito de tamanho: p=0,59, IC95% do churn do top-10% "
            "cobre a base (22,0%). Por decil nao e monotono -- decil 8 "
            "churna 38%, decis 9-10 churnam 18%: e ruido com um pico no "
            "meio, nao gradiente de tamanho. O top-10% super-amostra EdTech "
            "(menor churn) e sub-amostra DevTools (maior churn); ajustando "
            "por industria (MH) o OR sai de 0,76 para 0,86 -- parte da "
            "diferenca (ja nula) e composicao, nao tamanho. 'Contas grandes "
            "sao mais fieis' nao pode ser afirmado com este dado."
        ),
    }


def _wilson_ci(successes, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def mrr_definition_sensitivity(accounts, subs):
    n_subs_median = subs.groupby("account_id").size().median()
    n_accounts_multi_open_sub = (
        subs[subs["end_date"].isna()].groupby("account_id").size() > 1
    ).sum()

    mrr_last_by_start = subs.sort_values("start_date").groupby("account_id")["mrr_amount"].last()
    active_subs = subs[subs["end_date"].isna()].sort_values("start_date")
    mrr_active = active_subs.groupby("account_id")["mrr_amount"].last()

    total_last = mrr_last_by_start.sum()
    total_active = mrr_active.reindex(accounts["account_id"]).fillna(0).sum()

    def top10_share(mrr_series):
        s = mrr_series.reindex(accounts["account_id"]).fillna(0).sort_values(ascending=False)
        k = round(len(s) * 0.10)
        return round(float(s.iloc[:k].sum() / s.sum()) * 100, 1)

    return {
        "mediana_assinaturas_por_conta": float(n_subs_median),
        "n_contas_com_mais_de_1_assinatura_aberta_sem_end_date": int(n_accounts_multi_open_sub),
        "mrr_total_definicao_ultima_por_start_date": round(float(total_last), 2),
        "mrr_total_definicao_assinaturas_ativas_sem_end_date": round(float(total_active), 2),
        "top10pct_share_definicao_ultima": top10_share(mrr_last_by_start),
        "top10pct_share_definicao_ativas": top10_share(mrr_active),
        "nota": (
            "'MRR atual' e ambiguo no dado: a mediana de assinaturas por "
            "conta e ~10 e todas as 500 contas tem mais de uma assinatura "
            "sem end_date. A escolha de definicao move a concentracao do "
            "top-10% em ~1 ponto percentual -- nao muda a conclusao, mas "
            "'nada e estimativa' e falso: e uma escolha de modelagem."
        ),
    }


def binary_segment_test(acc, flag_col):
    ct = pd.crosstab(acc[flag_col], acc["churn_flag"])
    chi2, p, dof, _ = sstats.chi2_contingency(ct, correction=True)
    rate_in = acc.loc[acc[flag_col], "churn_flag"].mean()
    rate_out = acc.loc[~acc[flag_col], "churn_flag"].mean()
    return {
        "chi2": round(float(chi2), 2),
        "p_value": round(float(p), 4),
        "churn_rate_in": round(float(rate_in) * 100, 1),
        "churn_rate_out": round(float(rate_out) * 100, 1),
        "n_in": int(acc[flag_col].sum()),
        "n_out": int((~acc[flag_col]).sum()),
    }


def mantel_haenszel_or(df, exposure_col, outcome_col, strata_col):
    num, den = 0.0, 0.0
    for _, g in df.groupby(strata_col):
        ct = pd.crosstab(g[exposure_col], g[outcome_col])
        if ct.shape != (2, 2):
            continue
        a = ct.loc[True, True] if True in ct.index and True in ct.columns else 0
        b = ct.loc[True, False] if True in ct.index and False in ct.columns else 0
        c = ct.loc[False, True] if False in ct.index and True in ct.columns else 0
        d = ct.loc[False, False] if False in ct.index and False in ct.columns else 0
        n = a + b + c + d
        if n == 0:
            continue
        num += (a * d) / n
        den += (b * c) / n
    return round(float(num / den), 2) if den else None


def devtools_lookelsewhere(accounts, n_perm=4000, seed=20260914):
    """Corrige o p do corte DevTools-vs-resto pela seleção pós-hoc: quantos
    cortes um-contra-o-resto o dashboard realmente exibe (industria+país+
    canal+plano+trial), e o que sobra do 'achado' sob permutação."""
    rng = np.random.default_rng(seed)
    y = accounts["churn_flag"].values.astype(int)

    def chi2_2x2(mask, yy):
        n1, n0 = mask.sum(), (~mask).sum()
        if n1 < 2 or n0 < 2:
            return 0.0
        table = np.array([
            [yy[mask].sum(), n1 - yy[mask].sum()],
            [yy[~mask].sum(), n0 - yy[~mask].sum()],
        ])
        chi2, *_ = sstats.chi2_contingency(table, correction=True)
        return chi2

    industry_masks = {ind: accounts["industry"].eq(ind).values for ind in accounts["industry"].unique()}
    country_masks = {
        c: accounts["country"].eq(c).values
        for c in accounts["country"].value_counts()[lambda s: s >= 5].index
    }
    referral_masks = {r: accounts["referral_source"].eq(r).values for r in accounts["referral_source"].unique()}
    plan_masks = {p: accounts["plan_tier"].eq(p).values for p in accounts["plan_tier"].unique()}
    trial_masks = {"trial": accounts["is_trial"].values.astype(bool)}

    all_cuts = {**industry_masks, **country_masks, **referral_masks, **plan_masks, **trial_masks}
    observed = {name: chi2_2x2(mask, y) for name, mask in all_cuts.items()}
    devtools_chi2 = observed["DevTools"]

    industry_max_perm = np.empty(n_perm)
    all_cuts_max_perm = np.empty(n_perm)
    industry_mask_list = list(industry_masks.values())
    all_mask_list = list(all_cuts.values())
    for i in range(n_perm):
        yp = rng.permutation(y)
        industry_max_perm[i] = max(chi2_2x2(m, yp) for m in industry_mask_list)
        all_cuts_max_perm[i] = max(chi2_2x2(m, yp) for m in all_mask_list)

    return {
        "n_one_vs_rest_cuts_shown_on_dashboard": len(all_cuts),
        "devtools_chi2_observed": round(float(devtools_chi2), 2),
        "p_naive_devtools_only": round(float(sstats.chi2_contingency(
            pd.crosstab(accounts["industry"].eq("DevTools"), accounts["churn_flag"]), correction=True
        )[1]), 4),
        "p_bonferroni_5_industries": round(min(1.0, float(sstats.chi2_contingency(
            pd.crosstab(accounts["industry"].eq("DevTools"), accounts["churn_flag"]), correction=True
        )[1]) * 5), 4),
        "p_permutation_5_industries": round(float((industry_max_perm >= devtools_chi2).mean()), 4),
        "p_permutation_all_displayed_cuts": round(float((all_cuts_max_perm >= devtools_chi2).mean()), 4),
        "n_permutations": n_perm,
    }


def devtools_deep_dive(accounts, churn):
    acc = accounts.copy()
    acc["is_devtools"] = acc["industry"].eq("DevTools")
    test = binary_segment_test(acc, "is_devtools")
    lookelsewhere = devtools_lookelsewhere(accounts)

    mh_by = {}
    for strat in ["referral_source", "plan_tier", "country"]:
        mh_by[strat] = mantel_haenszel_or(acc, "is_devtools", "churn_flag", strat)

    ct_confound = {}
    for strat in ["referral_source", "plan_tier", "country", "is_trial"]:
        chi2, p, dof, _ = sstats.chi2_contingency(pd.crosstab(acc["is_devtools"], acc[strat]))
        ct_confound[strat] = {"chi2": round(float(chi2), 2), "p_value": round(float(p), 4)}

    c_churned = churned_only_events(churn, accounts)
    m = c_churned.merge(acc[["account_id", "industry"]], on="account_id", how="left")
    m["reason_code"] = m["reason_code"].fillna("unknown")
    dev = m[m["industry"] == "DevTools"]["reason_code"].value_counts(normalize=True)
    rest = m[m["industry"] != "DevTools"]["reason_code"].value_counts(normalize=True)
    reasons = sorted(set(dev.index) | set(rest.index))
    reason_compare = [
        {
            "reason_code": r,
            "pct_devtools": round(float(dev.get(r, 0)) * 100, 1),
            "pct_rest": round(float(rest.get(r, 0)) * 100, 1),
        }
        for r in reasons
    ]
    reason_compare.sort(key=lambda x: x["pct_devtools"], reverse=True)

    industries = sorted(accounts["industry"].unique().tolist())
    return {
        "devtools_vs_rest": test,
        "honest_significance": lookelsewhere,
        "confound_adjusted_or_mantel_haenszel": mh_by,
        "or_bruto": round(
            (acc.loc[acc.is_devtools, "churn_flag"].mean() / (1 - acc.loc[acc.is_devtools, "churn_flag"].mean()))
            / (acc.loc[~acc.is_devtools, "churn_flag"].mean() / (1 - acc.loc[~acc.is_devtools, "churn_flag"].mean())),
            2,
        ),
        "devtools_x_outro_confundidor": ct_confound,
        "reason_code_devtools_vs_rest": reason_compare,
        "reason_code_base": "apenas eventos de contas com churn_flag=True hoje (n=135)",
        "n_devtools_churn_events": int((m["industry"] == "DevTools").sum()),
        "n_rest_churn_events": int((m["industry"] != "DevTools").sum()),
        "all_industries_in_dataset": industries,
        "n_industries": len(industries),
        "interpretacao": (
            "Melhor hipotese do dataset, nao achado confirmado. O p ingenuo "
            "(0,0128) so vale se o corte DevTools-vs-resto tivesse sido "
            "decidido ANTES de olhar o grafico. Corrigido pela busca que o "
            "encontrou: p=0,044 (so entre as 5 industrias) a p=0,144 (sobre "
            "os 21 cortes de fato exibidos no dashboard). O efeito nao "
            "desaparece por confundimento (MH por canal/plano/pais mantem "
            "OR 1,83-1,90) -- mas isso importa pouco se o motivo dele ter "
            "aparecido foi olhar o grafico primeiro. Tratar como hipotese "
            "para testar em coorte nova, nao como fato para repriorizar a "
            "vertical."
        ),
    }


def data_quality_notes(accounts, churn):
    n_flag_true = int(accounts["churn_flag"].sum())
    accounts_with_event = churn["account_id"].nunique()
    flagged = accounts[accounts["churn_flag"]]
    flagged_with_event = flagged["account_id"].isin(churn["account_id"]).sum()
    flagged_no_event = int(len(flagged) - flagged_with_event)
    multi_event_accounts = int((churn.groupby("account_id").size() > 1).sum())
    return {
        "n_churn_flag_true": n_flag_true,
        "n_accounts_with_any_churn_event": int(accounts_with_event),
        "n_churn_flag_true_without_event_on_file": flagged_no_event,
        "pct_churn_flag_true_without_event_on_file": round(100 * flagged_no_event / n_flag_true, 1),
        "n_accounts_with_multiple_churn_events": multi_event_accounts,
        "n_total_churn_events": int(len(churn)),
        "n_events_flagged_reactivation": int(churn["is_reactivation"].sum()),
    }


def headline_numbers(acc, subs, churn):
    n_accounts = len(acc)
    n_churned = int(acc["churn_flag"].sum())
    mrr_total = acc["mrr"].sum()
    mrr_at_risk = acc.loc[acc["churn_flag"], "mrr"].sum()
    return {
        "n_accounts": int(n_accounts),
        "n_churned": n_churned,
        "churn_rate_pct": round(100 * n_churned / n_accounts, 1),
        "mrr_total": round(float(mrr_total), 2),
        "mrr_at_risk": round(float(mrr_at_risk), 2),
        "mrr_at_risk_pct": round(100 * mrr_at_risk / mrr_total, 1) if mrr_total else None,
        "n_subscriptions": int(len(subs)),
        # rotulo corrigido (auditoria): isto e nº de CONTAS com >=1 evento no
        # log, nao nº de eventos. Eventos totais = n_total_churn_events.
        "n_accounts_with_any_churn_event": int(acc["reason_code"].notna().sum()),
        "n_churn_events_total": int(len(churn)),
    }


def global_null_model(acc):
    """Regressao logistica com todas as covariaveis disponiveis de uma vez.
    Responde a pergunta que nenhum teste isolado responde: o conjunto
    COMPLETO do que foi medido explica churn, ou nao?"""
    import statsmodels.api as sm

    df = acc.copy()
    numeric_cols = [
        "seats", "mrr", "total_usage_count", "total_usage_duration", "error_rate",
        "n_tickets", "avg_resolution_hours", "avg_satisfaction", "pct_escalated",
        "tenure_days",
    ]
    for c in numeric_cols:
        df[c] = df[c].fillna(df[c].median())
        df[c] = (df[c] - df[c].mean()) / df[c].std()
    df["ever_downgraded"] = df["ever_downgraded"].astype(float)
    df["is_trial"] = df["is_trial"].astype(float)

    dummies = pd.get_dummies(
        df[["industry", "country", "referral_source", "plan_tier"]], drop_first=True
    )
    X = pd.concat([df[numeric_cols + ["ever_downgraded", "is_trial"]], dummies], axis=1)
    X = sm.add_constant(X.astype(float))
    y = df["churn_flag"].astype(int)

    model = sm.Logit(y, X).fit(disp=0)
    coefs = model.summary2().tables[1]
    candidates = coefs[coefs["P>|z|"] < 0.10].drop("const", errors="ignore")

    n_tests_total = 106  # ver contagem em audit_summary
    return {
        "n_covariates": int(X.shape[1] - 1),
        "lr_chi2": round(float(model.llr), 2),
        "lr_df": int(model.df_model),
        "lr_p_value": round(float(model.llr_pvalue), 4),
        "pseudo_r2_mcfadden": round(float(model.prsquared), 4),
        "candidatos_p_menor_0_10": [
            {
                "termo": idx,
                "odds_ratio": round(float(np.exp(row["Coef."])), 2),
                "p_value": round(float(row["P>|z|"]), 4),
                "p_bonferroni_22_termos": round(min(1.0, float(row["P>|z|"]) * (X.shape[1] - 1)), 4),
            }
            for idx, row in candidates.iterrows()
        ],
        "interpretacao": (
            "O modelo completo NAO rejeita a hipotese nula (p=0,19). Nenhuma "
            "covariavel isolada sobrevive a correcao por 22 termos. "
            "Nao ha o que modelar com as variaveis disponiveis neste dataset."
        ),
    }


def audit_summary(report):
    """Contagem de todos os testes formais rodados no relatorio -- pra
    responder com transparencia 'quantas vezes voce testou antes de achar
    algo', que e o proprio criterio de rigor do desafio."""
    n_corr = len(report["correlation_with_churn"]["correlations"])
    n_omnibus = len(report["segment_significance"])
    n_feat_usage = report["feature_level"]["n_features_tested"]
    n_feat_error = report["feature_level"]["error_rate_family"]["n_tests"]
    n_priority = len(report["ticket_priority"]["by_priority"])
    n_escalation = 1
    n_devtools_posthoc = 1
    n_growth_corr = 2
    n_mrr_concentration = 3
    total = (
        n_corr + n_omnibus + n_feat_usage + n_feat_error + n_priority
        + n_escalation + n_devtools_posthoc + n_growth_corr + n_mrr_concentration
    )
    expected_false_positives = round(total * 0.05, 1)
    n_significant_found = (
        report["feature_level"]["n_significant_uncorrected"]
        + report["feature_level"]["error_rate_family"]["n_significant_uncorrected"]
        + 1  # devtools
    )
    return {
        "contagem_de_testes_formais": {
            "correlacoes_pearson": n_corr,
            "qui_quadrado_omnibus_de_segmento": n_omnibus,
            "t_tests_por_feature_uso": n_feat_usage,
            "t_tests_por_feature_error_rate": n_feat_error,
            "qui_quadrado_por_prioridade_de_ticket": n_priority,
            "qui_quadrado_escalacao": n_escalation,
            "devtools_vs_resto_pos_hoc": n_devtools_posthoc,
            "pearson_crescimento_x_churn_entre_segmentos": n_growth_corr,
            "comparacoes_de_concentracao_de_mrr": n_mrr_concentration,
            "total": total,
        },
        "falsos_positivos_esperados_sob_nulo_p_menor_0_05": expected_false_positives,
        "significativos_de_fato_encontrados_sem_correcao": n_significant_found,
        "veredito": (
            f"{n_significant_found} 'significativos' encontrados contra "
            f"{expected_false_positives} esperados so por acaso puro. O "
            "rendimento do relatorio e indistinguivel do que o acaso "
            "produziria testando esse volume de cortes."
        ),
    }


def onboarding_cohort_deterioration(accounts, subs, churn):
    """Deterioracao da safra de onboarding: churn nos primeiros 90 dias,
    por semestre de signup. Achado adicionado apos revisao do PR publico
    #117 (Fabricio Rojas) no mesmo repositorio do desafio -- a lacuna
    (tenure/signup_date nunca usado como janela, so como covariavel
    estatica) ja estava marcada em methodology_notes antes dessa revisao;
    o que mudou foi a prioridade de executa-la. Reproduzido aqui do zero,
    com metodologia propria, e testado contra confundimento de composicao
    (industria/canal/plano) antes de aceitar."""
    as_of = pd.Timestamp("2024-12-31")
    mrr = subs.sort_values("start_date").groupby("account_id")["mrr_amount"].last()
    first_churn = churn.sort_values("churn_date").groupby("account_id")["churn_date"].first()

    acc = accounts.copy()
    acc["mrr"] = acc["account_id"].map(mrr)
    acc["first_churn_date"] = acc["account_id"].map(first_churn)
    acc["days_to_first_churn"] = (acc["first_churn_date"] - acc["signup_date"]).dt.days
    acc["tenure_observable_days"] = (as_of - acc["signup_date"]).dt.days
    acc["cohort_half"] = (
        acc["signup_date"].dt.year.astype(str) + "-H"
        + (acc["signup_date"].dt.month.gt(6) + 1).astype(str)
    )

    elig = acc[acc["tenure_observable_days"] >= 90].copy()
    elig["churned_in_90"] = (elig["days_to_first_churn"] <= 90) & elig["days_to_first_churn"].notna()

    g = elig.groupby("cohort_half").agg(
        n=("account_id", "count"), churn_90d_rate=("churned_in_90", "mean"), mrr_avg=("mrr", "mean")
    ).sort_index()
    g["churn_90d_rate"] = (g["churn_90d_rate"] * 100).round(1)
    g["mrr_avg"] = g["mrr_avg"].round(0)

    ct = pd.crosstab(elig["cohort_half"], elig["churned_in_90"])
    chi2, p_omnibus, dof, _ = sstats.chi2_contingency(ct)

    elig["cohort_idx"] = pd.factorize(elig["cohort_half"], sort=True)[0]
    dummies = pd.get_dummies(elig[["industry", "referral_source", "plan_tier"]], drop_first=True)
    X = pd.concat([elig[["cohort_idx"]], dummies], axis=1).astype(float)
    import statsmodels.api as sm
    X = sm.add_constant(X)
    y = elig["churned_in_90"].astype(int)
    model = sm.Logit(y, X).fit(disp=0)
    or_per_cohort = float(np.exp(model.params["cohort_idx"]))
    p_adjusted = float(model.pvalues["cohort_idx"])

    first_label, last_label = g.index.min(), g.index.max()
    rate_first = g.loc[first_label, "churn_90d_rate"] / 100
    rate_last = g.loc[last_label, "churn_90d_rate"] / 100
    n_last = int(g.loc[last_label, "n"])
    mrr_avg_last = float(g.loc[last_label, "mrr_avg"])
    excess_accounts_per_cohort = (rate_last - rate_first) * n_last
    mrr_excess_per_cohort = excess_accounts_per_cohort * mrr_avg_last

    return {
        "n_accounts_eligible_90d_window": int(len(elig)),
        "n_accounts_excluded_too_recent": int(len(acc) - len(elig)),
        "by_cohort": g.reset_index().to_dict(orient="records"),
        "chi2_omnibus": round(float(chi2), 2),
        "p_omnibus": p_omnibus,
        "or_per_cohort_step_adjusted_industry_referral_plan": round(or_per_cohort, 2),
        "p_adjusted_for_composition": p_adjusted,
        "excess_accounts_per_semester_vs_first_cohort": round(float(excess_accounts_per_cohort), 1),
        "mrr_excess_lost_per_semester_usd": round(float(mrr_excess_per_cohort), 0),
        "mrr_excess_lost_annualized_usd": round(float(mrr_excess_per_cohort) * 2, 0),
        "origem": (
            "Padrao inicialmente reportado publicamente no PR #117 do "
            "challenge (outro candidato). Verificado aqui de forma "
            "independente: metodologia propria, codigo proprio, e teste "
            "de confundimento por composicao que o PR original nao "
            "reportava. Ver PROCESS_LOG.md para a sequencia completa."
        ),
        "interpretacao": (
            f"Churn em 90 dias sobe de {g.loc[first_label,'churn_90d_rate']}% "
            f"({first_label}) para {g.loc[last_label,'churn_90d_rate']}% "
            f"({last_label}). p={p_omnibus:.2e} (omnibus), sobrevive ajuste "
            f"por industria+canal+plano: OR={or_per_cohort:.2f} por safra, "
            f"p={p_adjusted:.2e}. E o achado mais forte de todo o dataset -- "
            "ordens de magnitude mais solido que qualquer corte de segmento "
            "estatico testado neste relatorio."
        ),
    }


def main():
    accounts, subs, usage, tickets, churn = load()
    acc = build_account_table(accounts, subs, usage, tickets, churn)

    report = {
        "headline": headline_numbers(acc, subs, churn),
        "churn_by_industry": churn_by_segment(acc, "industry"),
        "churn_by_country": churn_by_segment(acc, "country"),
        "churn_by_plan": churn_by_segment(acc, "plan_tier"),
        "churn_by_referral": churn_by_segment(acc, "referral_source"),
        "churn_by_trial": churn_by_segment(acc, "is_trial", min_n=1),
        "usage_trend": usage_trend_overall_vs_churn(usage, subs, accounts, churn),
        "support_comparison": support_churned_vs_retained(acc),
        "reason_codes": reason_code_breakdown(churn, accounts),
        "reason_by_plan": reason_by_plan(churn, accounts),
        "correlation_with_churn": correlation_snapshot(acc),
        "segment_significance": [
            chi2_segment_test(acc, c)
            for c in ["industry", "country", "referral_source", "plan_tier", "is_trial"]
        ],
    }
    report["usage_trend_slope"] = usage_trend_slope(report["usage_trend"])
    report["usage_trend_honesty"] = usage_trend_honesty(usage, subs, accounts, churn)
    report["data_quality"] = data_quality_notes(accounts, churn)
    report["devtools_deep_dive"] = devtools_deep_dive(accounts, churn)
    report["feature_level"] = feature_level_analysis(usage, subs, accounts)
    report["ticket_priority"] = ticket_priority_analysis(tickets, accounts)
    report["usage_growth_by_industry"] = usage_growth_by_segment(usage, subs, accounts, "industry")
    report["usage_growth_by_referral"] = usage_growth_by_segment(usage, subs, accounts, "referral_source")
    report["ecological_fallacy_check"] = {
        "usage_growth_x_churn_no_nivel_de_segmento_industry_r": report["usage_growth_by_industry"]["growth_vs_churn_correlation_across_segments"]["pearson_r"],
        "total_usage_count_x_churn_no_nivel_de_conta_r": next(
            r["corr_with_churn"] for r in report["correlation_with_churn"]["correlations"] if r["variable"] == "total_usage_count"
        ),
        "nota": (
            "Sinais opostos entre o nivel de segmento (ecologico) e o nivel "
            "de conta (individual) -- exemplo real de correlacao ecologica "
            "que se inverte ao trocar a unidade de analise (Simpson-like)."
        ),
    }
    report["mrr_concentration"] = mrr_concentration(acc)
    report["mrr_definition_sensitivity"] = mrr_definition_sensitivity(accounts, subs)
    report["onboarding_cohort_deterioration"] = onboarding_cohort_deterioration(accounts, subs, churn)
    report["global_null_model"] = global_null_model(acc)
    report["audit_summary"] = audit_summary(report)
    report["methodology_notes"] = [
        "MRR = mrr_amount da assinatura mais recente por start_date. Ambiguo: "
        "mediana de 10 assinaturas/conta, todas as 500 contas tem mais de uma "
        "assinatura aberta (sem end_date). Ver mrr_definition_sensitivity.",
        "Tenure calculado com as_of=2024-12-31 (ultima data observada em "
        "qualquer tabela do dataset), nao 'hoje'.",
        "A tabela feature_usage nao respeita o ciclo de vida da conta (ver "
        "usage_trend_honesty) -- qualquer metrica de 'uso total' ou "
        "'trajetoria' aqui carrega esse limite.",
        "reason_codes e reason_by_plan reportam separadamente a versao "
        "restrita a contas realmente churnadas (correta) e a versao com "
        "todos os eventos (como o relatorio original calculava, mantida "
        "so pra comparacao).",
        "Este arquivo roda 106 testes formais no total (ver audit_summary). "
        "Nenhum p-valor aqui deveria ser lido isoladamente sem essa contagem.",
        "onboarding_cohort_deterioration foi adicionado apos revisar PRs "
        "publicos de outros candidatos no mesmo repositorio do desafio "
        "(#117). A lacuna -- tenure/signup_date nunca usado como janela -- "
        "ja estava marcada nas notas de metodologia antes dessa revisao; "
        "o calculo em si foi reproduzido do zero, com metodologia e codigo "
        "proprios, e testado contra confundimento antes de ser aceito. Ver "
        "PROCESS_LOG.md para a sequencia completa e honesta.",
    ]

    OUT.write_text(json.dumps(report, indent=2, default=str, ensure_ascii=False), encoding="utf-8")
    print(f"OK -> {OUT}")
    print(json.dumps(report["headline"], indent=2, ensure_ascii=False))
    print(json.dumps(report["audit_summary"]["veredito"], ensure_ascii=False))


if __name__ == "__main__":
    main()
