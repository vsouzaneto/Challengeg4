"""Etapa 1 do método: testar hipóteses sobre o que separa deals ganhos de perdidos.

Cada hipótese é uma função registrada em HYPOTHESES que devolve um dicionário com
o número que a confirma ou refuta. O resultado vai para docs/exploration_results.md
e docs/exploration_results.json; os fatores do scoring só podem nascer de hipóteses
que sobreviveram aqui.

Uso:
    python 02_explore.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from leadscorer.data import enrich, load_tables, reference_date

HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "raw"
DOCS = HERE.parent / "docs"

HYPOTHESES: list = []


def hypothesis(hid: str, statement: str, origin: str):
    def deco(fn):
        HYPOTHESES.append((hid, statement, origin, fn))
        return fn
    return deco


def chi2_pvalue(table: pd.DataFrame) -> float:
    if table.shape[0] < 2 or table.shape[1] < 2:
        return float("nan")
    return float(stats.chi2_contingency(table.values)[1])


def wr_table(closed: pd.DataFrame, dim: str, min_n: int = 20) -> pd.DataFrame:
    g = closed.groupby(dim)["won"].agg(n="size", win_rate="mean")
    return g[g["n"] >= min_n].sort_values("win_rate")


def spread(g: pd.DataFrame) -> float:
    return float(g["win_rate"].max() - g["win_rate"].min()) if len(g) else float("nan")


# ----------------------------------------------------------------------------- vendedor

@hypothesis("H1", "Vendedores diferem de verdade na taxa de conversão (não é ruído)", "IA")
def h_agent(ctx):
    closed = ctx["closed"]
    g = wr_table(closed, "sales_agent", 20)
    p = chi2_pvalue(pd.crosstab(closed["sales_agent"], closed["won"]))
    top = g.tail(5)["win_rate"].mean(); bottom = g.head(5)["win_rate"].mean()
    return {"metric": "spread de win rate entre vendedores (n>=20) e p-valor do qui-quadrado",
            "value": {"spread_pp": round(100 * spread(g), 1), "top5_mean": round(100 * top, 1), "bottom5_mean": round(100 * bottom, 1),
                      "p_value": p, "agents_with_closed": int(len(g)), "min_n": int(g["n"].min())},
            "verdict": "confirmada" if p < 0.01 and spread(g) > 0.08 else "refutada"}


@hypothesis("H2", "O encaixe vendedor × produto separa mais do que o vendedor sozinho", "IA")
def h_agent_product(ctx):
    closed = ctx["closed"]
    g = closed.groupby(["sales_agent", "product"])["won"].agg(n="size", win_rate="mean")
    g = g[g["n"] >= 20]
    q1, q3 = g["win_rate"].quantile([0.25, 0.75])
    ga = wr_table(closed, "sales_agent", 20)
    qa1, qa3 = ga["win_rate"].quantile([0.25, 0.75])
    open_cov = ctx["open"].merge(g.reset_index()[["sales_agent", "product"]].assign(cov=1), on=["sales_agent", "product"], how="left")["cov"].notna().mean()
    return {"metric": "gap entre quartis de win rate: vendedor×produto vs vendedor; cobertura dos deals abertos",
            "value": {"combo_iqr_gap_pp": round(100 * (q3 - q1), 1), "agent_iqr_gap_pp": round(100 * (qa3 - qa1), 1),
                      "combos_n>=20": int(len(g)), "open_deals_covered_pct": round(100 * float(open_cov), 1),
                      "combo_min_wr": round(100 * g["win_rate"].min(), 1), "combo_max_wr": round(100 * g["win_rate"].max(), 1)},
            "verdict": "confirmada" if (q3 - q1) > (qa3 - qa1) * 1.2 else "refutada"}


@hypothesis("H3", "Vendedor com muitos deals abertos (sobrecarga) converte pior", "IA")
def h_workload(ctx):
    open_by_agent = ctx["open"].groupby("sales_agent").size().rename("open_deals")
    g = wr_table(ctx["closed"], "sales_agent", 20).join(open_by_agent, how="inner")
    rho, p = stats.spearmanr(g["open_deals"], g["win_rate"])
    return {"metric": "correlação de Spearman entre deals abertos por vendedor e win rate histórica",
            "value": {"spearman_rho": round(float(rho), 3), "p_value": float(p), "open_deals_min": int(g["open_deals"].min()), "open_deals_max": int(g["open_deals"].max())},
            "verdict": "confirmada" if p < 0.05 and rho < -0.3 else "refutada"}


# ----------------------------------------------------------------------------- produto e valor

@hypothesis("H4", "Produtos diferem na taxa de conversão", "IA")
def h_product(ctx):
    closed = ctx["closed"]
    g = wr_table(closed, "product", 20)
    p = chi2_pvalue(pd.crosstab(closed["product"], closed["won"]))
    return {"metric": "spread de win rate entre produtos e p-valor", "value": {"spread_pp": round(100 * spread(g), 1), "p_value": p, "table": {k: round(100 * v, 1) for k, v in g["win_rate"].items()}},
            "verdict": "confirmada" if p < 0.01 and spread(g) > 0.08 else "refutada"}


@hypothesis("H5", "Deal mais caro (preço de lista) tem menor chance de fechar", "IA")
def h_price(ctx):
    closed = ctx["closed"]
    g = closed.groupby("sales_price")["won"].agg(n="size", win_rate="mean").sort_index()
    rho, p = stats.spearmanr(closed["sales_price"], closed["won"])
    return {"metric": "win rate por preço de lista e correlação de Spearman", "value": {"table": {f"{int(k):,}": round(100 * v, 1) for k, v in g["win_rate"].items()}, "spearman_rho": round(float(rho), 3), "p_value": float(p)},
            "verdict": "confirmada" if p < 0.01 and rho < -0.05 else "refutada"}


@hypothesis("H6", "Produtos diferem no tempo de ciclo (dias de engage a close)", "IA")
def h_cycle_by_product(ctx):
    closed = ctx["closed"]
    g = closed.groupby("product")["cycle_days"].agg(n="size", median="median", p75=lambda s: s.quantile(0.75))
    kw = stats.kruskal(*[grp["cycle_days"].values for _, grp in closed.groupby("product")])
    return {"metric": "mediana do ciclo por produto e teste de Kruskal-Wallis", "value": {"table": {k: {"median": float(r["median"]), "p75": float(r["p75"]), "n": int(r["n"])} for k, r in g.iterrows()}, "p_value": float(kw.pvalue), "spread_median_days": float(g["median"].max() - g["median"].min())},
            "verdict": "confirmada" if kw.pvalue < 0.01 and (g["median"].max() - g["median"].min()) >= 7 else "refutada"}


@hypothesis("H7", "Desconto: o valor fechado (close_value) fica abaixo do preço de lista, e o desconto varia por vendedor", "IA")
def h_discount(ctx):
    won = ctx["closed"][ctx["closed"]["won"]].copy()
    won["ratio"] = won["close_value"] / won["sales_price"]
    by_agent = won.groupby("sales_agent")["ratio"].median()
    return {"metric": "razão close_value/sales_price nos Won; mediana global e spread entre vendedores", "value": {"median_ratio": round(float(won["ratio"].median()), 3), "p10": round(float(won["ratio"].quantile(0.1)), 3), "p90": round(float(won["ratio"].quantile(0.9)), 3), "agent_spread": round(float(by_agent.max() - by_agent.min()), 3)},
            "verdict": "confirmada" if won["ratio"].median() < 0.98 or (by_agent.max() - by_agent.min()) > 0.05 else "refutada"}


# ----------------------------------------------------------------------------- tempo

@hypothesis("H8", "Deal parado há muito tempo não fecha: quanto maior o ciclo, menor a taxa de ganho", "IA")
def h_cycle_buckets(ctx):
    closed = ctx["closed"]
    bins = [-1, 14, 30, 45, 60, 90, 120, 138, 10_000]
    labels = ["0-14", "15-30", "31-45", "46-60", "61-90", "91-120", "121-138", ">138"]
    b = pd.cut(closed["cycle_days"], bins=bins, labels=labels)
    g = closed.groupby(b, observed=True)["won"].agg(n="size", win_rate="mean")
    return {"metric": "win rate por faixa de ciclo (dias) entre deals fechados", "value": {k: {"n": int(r["n"]), "win_rate": round(100 * r["win_rate"], 1)} for k, r in g.iterrows()},
            "verdict": "confirmada" if g["win_rate"].iloc[-1] < g["win_rate"].iloc[0] else "refutada"}


@hypothesis("H9", "Existe um teto de ciclo acima do qual ninguém ganha (linha dos 138 dias)", "IA")
def h_ceiling(ctx):
    closed = ctx["closed"]
    won_max = int(closed.loc[closed["won"], "cycle_days"].max()); lost_max = int(closed.loc[~closed["won"], "cycle_days"].max())
    over = closed[closed["cycle_days"] > won_max]
    return {"metric": "ciclo máximo entre Won vs Lost e quantos Lost passaram do teto", "value": {"won_max_cycle_days": won_max, "lost_max_cycle_days": lost_max, "lost_beyond_won_max": int(len(over))},
            "verdict": "confirmada" if lost_max > won_max + 7 else "refutada"}


@hypothesis("H10", "Sobreviver às primeiras semanas aumenta a chance: P(ganhar | ciclo >= a) sobe antes de cair", "IA")
def h_survival(ctx):
    closed = ctx["closed"]
    out = {}
    for a in (0, 7, 14, 30, 45, 60, 90, 120, 138, 150):
        s = closed[closed["cycle_days"] >= a]
        out[str(a)] = {"n": int(len(s)), "win_rate": round(100 * float(s["won"].mean()), 1) if len(s) else None}
    wr = [v["win_rate"] for v in out.values() if v["win_rate"] is not None]
    return {"metric": "P(ganhar | ciclo >= a dias) para vários a", "value": out, "verdict": "confirmada" if max(wr[:4]) > wr[0] + 2 else "refutada"}


@hypothesis("H11", "Os deals em Engaging hoje estão, em sua maioria, além de qualquer ciclo histórico de vitória", "IA")
def h_open_age(ctx):
    open_eng = ctx["open"][ctx["open"]["deal_stage"] == "Engaging"]
    age = (ctx["ref"] - open_eng["engage_date"]).dt.days
    won_max = int(ctx["closed"].loc[ctx["closed"]["won"], "cycle_days"].max())
    return {"metric": "idade dos Engaging na data de referência vs ciclo máximo de um Won", "value": {"n_engaging": int(len(age)), "age_p50": float(age.median()), "beyond_won_max": int((age > won_max).sum()), "beyond_won_max_pct": round(100 * float((age > won_max).mean()), 1), "won_max_cycle_days": won_max, "engage_date_max": str(open_eng["engage_date"].max().date())},
            "verdict": "confirmada" if (age > won_max).mean() > 0.5 else "refutada"}


@hypothesis("H12", "Sazonalidade: o mês de engajamento muda a taxa de ganho", "IA")
def h_season(ctx):
    closed = ctx["closed"]
    m = closed["engage_date"].dt.to_period("M").astype(str)
    g = closed.groupby(m)["won"].agg(n="size", win_rate="mean")
    p = chi2_pvalue(pd.crosstab(m, closed["won"]))
    return {"metric": "win rate por mês de engage_date e p-valor", "value": {"spread_pp": round(100 * spread(g), 1), "p_value": p, "months": int(len(g))}, "verdict": "confirmada" if p < 0.01 and spread(g) > 0.08 else "refutada"}


# ----------------------------------------------------------------------------- conta

@hypothesis("H13", "Quem já comprou compra de novo: conta com vitórias anteriores converte melhor", "IA")
def h_repeat(ctx):
    closed = ctx["closed"].sort_values("engage_date").copy()
    prior = []
    for _, row in closed.iterrows():
        hist = ctx["closed"][(ctx["closed"]["account"] == row["account"]) & (ctx["closed"]["close_date"] < row["engage_date"])]
        prior.append((int(hist["won"].sum()), int(len(hist))))
    closed["prior_won"] = [p[0] for p in prior]; closed["prior_n"] = [p[1] for p in prior]
    closed["prior_wr"] = np.where(closed["prior_n"] > 0, closed["prior_won"] / closed["prior_n"].replace(0, np.nan), np.nan)
    b = pd.cut(closed["prior_won"], bins=[-1, 0, 2, 5, 10, 1000], labels=["0", "1-2", "3-5", "6-10", ">10"])
    g = closed.groupby(b, observed=True)["won"].agg(n="size", win_rate="mean")
    has = closed[closed["prior_n"] >= 5]
    rho, p = stats.spearmanr(has["prior_wr"], has["won"]) if len(has) > 30 else (np.nan, np.nan)
    ctx["closed_prior"] = closed
    return {"metric": "win rate por nº de vitórias anteriores da conta (antes do engage) e correlação com a taxa histórica da conta",
            "value": {"by_prior_won": {k: {"n": int(r["n"]), "win_rate": round(100 * r["win_rate"], 1)} for k, r in g.iterrows()}, "spearman_prior_wr_vs_won": round(float(rho), 3), "p_value": float(p)},
            "verdict": "confirmada" if (g["win_rate"].iloc[-1] - g["win_rate"].iloc[0]) > 0.05 or (p < 0.01 and rho > 0.05) else "refutada"}


@hypothesis("H14", "Conta grande (receita/funcionários) fecha menos, mas paga mais", "IA")
def h_size(ctx):
    closed = ctx["closed"].dropna(subset=["revenue"])
    t = pd.qcut(closed["revenue"], 3, labels=["pequena", "média", "grande"])
    g = closed.groupby(t, observed=True).agg(n=("won", "size"), win_rate=("won", "mean"), won_value_median=("close_value", lambda s: s[closed.loc[s.index, "won"]].median()))
    p = chi2_pvalue(pd.crosstab(t, closed["won"]))
    return {"metric": "win rate e valor mediano dos Won por tercil de receita da conta", "value": {k: {"n": int(r["n"]), "win_rate": round(100 * r["win_rate"], 1), "won_value_median": float(r["won_value_median"])} for k, r in g.iterrows()} | {"p_value": p},
            "verdict": "confirmada" if p < 0.01 else "refutada"}


@hypothesis("H15", "Setor da conta muda a taxa de ganho", "IA")
def h_sector(ctx):
    closed = ctx["closed"].dropna(subset=["sector"])
    g = wr_table(closed, "sector", 20)
    p = chi2_pvalue(pd.crosstab(closed["sector"], closed["won"]))
    return {"metric": "spread de win rate por setor e p-valor", "value": {"spread_pp": round(100 * spread(g), 1), "p_value": p}, "verdict": "confirmada" if p < 0.01 and spread(g) > 0.08 else "refutada"}


@hypothesis("H16", "Subsidiária de outra conta se comporta diferente de conta independente", "IA")
def h_subsidiary(ctx):
    closed = ctx["closed"].dropna(subset=["sector"]).copy()
    closed["is_sub"] = closed["subsidiary_of"].notna()
    g = closed.groupby("is_sub")["won"].agg(n="size", win_rate="mean")
    p = chi2_pvalue(pd.crosstab(closed["is_sub"], closed["won"]))
    return {"metric": "win rate subsidiária vs independente", "value": {str(k): {"n": int(r["n"]), "win_rate": round(100 * r["win_rate"], 1)} for k, r in g.iterrows()} | {"p_value": p}, "verdict": "confirmada" if p < 0.01 else "refutada"}


# ----------------------------------------------------------------------------- estrutura do pipeline aberto

@hypothesis("H17", "Deals abertos sem conta são um problema de processo, não uma característica de estágio", "IA")
def h_orphans(ctx):
    op = ctx["open"]
    g = op.groupby("deal_stage")["has_account"].agg(n="size", with_account=lambda s: int(s.sum()))
    by_agent = op.groupby("sales_agent")["has_account"].mean()
    return {"metric": "share de deals abertos sem conta por estágio e dispersão entre vendedores", "value": {k: {"n": int(r["n"]), "without_account_pct": round(100 * (1 - r["with_account"] / r["n"]), 1)} for k, r in g.iterrows()} | {"agent_with_account_min_pct": round(100 * float(by_agent.min()), 1), "agent_with_account_max_pct": round(100 * float(by_agent.max()), 1), "closed_without_account": int(ctx["closed"]["account"].isna().sum())},
            "verdict": "confirmada" if abs(g["with_account"].div(g["n"]).diff().iloc[-1]) < 0.15 else "refutada"}


@hypothesis("H18", "Há vendedores sem nenhum deal fechado no histórico (impossível calibrar por vendedor)", "IA")
def h_new_agents(ctx):
    all_agents = set(ctx["teams"]["sales_agent"]); with_closed = set(ctx["closed"]["sales_agent"])
    missing = sorted(all_agents - with_closed)
    open_of_missing = ctx["open"][ctx["open"]["sales_agent"].isin(missing)]
    return {"metric": "vendedores cadastrados sem deal fechado e seus deals abertos", "value": {"agents": missing, "open_deals": int(len(open_of_missing))}, "verdict": "confirmada" if missing else "refutada"}


@hypothesis("H19", "É possível reconstruir o pipeline aberto em datas passadas (base do backtest por snapshot)", "IA")
def h_snapshot(ctx):
    closed = ctx["closed"]; out = {}
    for t in ("2017-03-31", "2017-06-30", "2017-09-30"):
        ts = pd.Timestamp(t)
        snap = closed[(closed["engage_date"] <= ts) & (closed["close_date"] > ts)]
        out[t] = {"open_then_and_closed_later": int(len(snap)), "won_later_pct": round(100 * float(snap["won"].mean()), 1) if len(snap) else None,
                  "median_age_days_at_t": float((ts - snap["engage_date"]).dt.days.median()) if len(snap) else None}
    return {"metric": "deals que estavam abertos em t e fecharam depois, por data t", "value": out, "verdict": "confirmada" if all(v["open_then_and_closed_later"] > 300 for v in out.values()) else "refutada"}


# ----------------------------------------------------------------------------- robustez (o que a primeira rodada não checou)

def _null_iqr_gap(closed: pd.DataFrame, keys: list[str], min_n: int, n_sim: int = 500, seed: int = 7) -> tuple[float, float, float]:
    """Gap entre quartis observado vs. o esperado se cada grupo fosse binomial com a taxa global.

    Devolve (observado, média nula, p-valor = fração de simulações com gap >= observado).
    """
    rng = np.random.default_rng(seed)
    g = closed.groupby(keys)["won"].agg(n="size", wins="sum")
    g = g[g["n"] >= min_n]
    p0 = float(closed["won"].mean())
    obs = float(np.subtract(*np.percentile(g["wins"] / g["n"], [75, 25])))
    sims = []
    for _ in range(n_sim):
        w = rng.binomial(g["n"].values, p0)
        sims.append(float(np.subtract(*np.percentile(w / g["n"].values, [75, 25]))))
    sims = np.array(sims)
    return obs, float(sims.mean()), float((sims >= obs).mean())


@hypothesis("H2b", "O gap vendedor × produto é maior do que o acaso produziria com esses tamanhos de amostra (Monte Carlo sob nulo binomial)", "IA")
def h_agent_product_null(ctx):
    obs, null_mean, p = _null_iqr_gap(ctx["closed"], ["sales_agent", "product"], 20)
    obs_a, null_a, p_a = _null_iqr_gap(ctx["closed"], ["sales_agent"], 20)
    return {"metric": "gap entre quartis observado vs. nulo binomial (500 simulações), para combo e para vendedor",
            "value": {"combo": {"observed_pp": round(100 * obs, 1), "null_mean_pp": round(100 * null_mean, 1), "p_value": p},
                      "agent": {"observed_pp": round(100 * obs_a, 1), "null_mean_pp": round(100 * null_a, 1), "p_value": p_a}},
            "verdict": "confirmada" if p < 0.05 else "refutada"}


@hypothesis("H12b", "A sazonalidade sobrevive quando se remove a censura (só meses em que todo deal teve 138 dias para fechar)", "IA")
def h_season_uncensored(ctx):
    closed = ctx["closed"]
    cutoff = ctx["ref"] - pd.Timedelta(days=138)
    full = closed[closed["engage_date"] <= cutoff]
    m_all = closed["engage_date"].dt.to_period("M").astype(str)
    m_full = full["engage_date"].dt.to_period("M").astype(str)
    g_all = closed.groupby(m_all)["won"].agg(n="size", win_rate="mean")
    g_full = full.groupby(m_full)["won"].agg(n="size", win_rate="mean")
    p = chi2_pvalue(pd.crosstab(m_full, full["won"]))
    return {"metric": "win rate por mês com e sem os meses censurados (engage após ref - 138 d)",
            "value": {"cutoff": str(cutoff.date()), "all_months": {k: {"n": int(r["n"]), "wr": round(100 * r["win_rate"], 1)} for k, r in g_all.iterrows()},
                      "uncensored_spread_pp": round(100 * spread(g_full), 1), "uncensored_p_value": p, "uncensored_months": int(len(g_full))},
            "verdict": "confirmada" if p < 0.01 and spread(g_full) > 0.08 else "refutada"}


@hypothesis("H8b", "Ciclo curto = derrota rápida: a relação ciclo × ganho não é 'parado não fecha', é 'quem morre, morre cedo'", "IA")
def h_die_early(ctx):
    closed = ctx["closed"]
    won_cycle = closed.loc[closed["won"], "cycle_days"]; lost_cycle = closed.loc[~closed["won"], "cycle_days"]
    return {"metric": "distribuição do ciclo de Won vs Lost",
            "value": {"won": {"p25": float(won_cycle.quantile(0.25)), "p50": float(won_cycle.median()), "p75": float(won_cycle.quantile(0.75))},
                      "lost": {"p25": float(lost_cycle.quantile(0.25)), "p50": float(lost_cycle.median()), "p75": float(lost_cycle.quantile(0.75))},
                      "lost_within_14d_pct": round(100 * float((lost_cycle <= 14).mean()), 1), "won_within_14d_pct": round(100 * float((won_cycle <= 14).mean()), 1),
                      "mannwhitney_p": float(stats.mannwhitneyu(won_cycle, lost_cycle).pvalue)},
            "verdict": "confirmada" if lost_cycle.median() < won_cycle.median() else "refutada"}


@hypothesis("H13b", "O efeito negativo de 'muitas vitórias anteriores' desaparece quando se controla o período (é confusão com o tempo)", "IA")
def h_repeat_controlled(ctx):
    closed = ctx.get("closed_prior")
    if closed is None:
        return {"metric": "depende de H13", "value": {}, "verdict": "não testada"}
    cutoff = ctx["ref"] - pd.Timedelta(days=138)
    full = closed[closed["engage_date"] <= cutoff].copy()
    full["q"] = full["engage_date"].dt.to_period("Q").astype(str)
    full["prior_bucket"] = pd.cut(full["prior_won"], bins=[-1, 0, 5, 1000], labels=["0", "1-5", ">5"])
    g = full.groupby(["q", "prior_bucket"], observed=True)["won"].agg(n="size", win_rate="mean")
    within = {}
    for q, sub in g.groupby(level=0):
        sub = sub.droplevel(0)
        if {"0", ">5"} <= set(sub.index):
            within[q] = {"wr_0": round(100 * float(sub.loc["0", "win_rate"]), 1), "n_0": int(sub.loc["0", "n"]), "wr_gt5": round(100 * float(sub.loc[">5", "win_rate"]), 1), "n_gt5": int(sub.loc[">5", "n"])}
    diffs = [v["wr_0"] - v["wr_gt5"] for v in within.values() if v["n_0"] >= 30 and v["n_gt5"] >= 30]
    return {"metric": "win rate de contas sem vitórias anteriores vs. com >5, dentro de cada trimestre (sem meses censurados)",
            "value": {"by_quarter": within, "mean_diff_pp": round(float(np.mean(diffs)), 1) if diffs else None},
            "verdict": "confirmada" if diffs and abs(np.mean(diffs)) < 3 else "refutada"}


@hypothesis("H20", "O valor esperado (preço × probabilidade) concentra o pipeline: poucos deals carregam a maior parte do valor", "IA")
def h_value_concentration(ctx):
    op = ctx["open"].dropna(subset=["sales_price"]).sort_values("sales_price", ascending=False)
    total = float(op["sales_price"].sum())
    cum = op["sales_price"].cumsum() / total
    n10 = int((cum <= 0.5).sum()) + 1
    top20pct = float(op["sales_price"].head(int(0.2 * len(op))).sum() / total)
    return {"metric": "concentração do valor de lista no pipeline aberto", "value": {"open_deals": int(len(op)), "total_list_value": round(total), "deals_for_50pct_value": n10, "top20pct_deals_share_of_value": round(100 * top20pct, 1)},
            "verdict": "confirmada" if top20pct > 0.5 else "refutada"}


@hypothesis("H21", "A base é truncada à esquerda: só há fechamentos a partir de 2017-03-01, então derrotas rápidas de deals engajados antes disso estão ausentes e inflam a win rate dos primeiros meses", "IA")
def h_left_truncation(ctx):
    closed = ctx["closed"]
    close_min = closed["close_date"].min(); engage_min = closed["engage_date"].min()
    early = closed[closed["engage_date"] < close_min]
    lost_fast_share_clean = float((closed[closed["engage_date"] >= close_min].query("~won")["cycle_days"] <= 14).mean())
    return {"metric": "janela de close_date vs engage_date; deals engajados antes do primeiro fechamento possível; ciclo mínimo desses deals",
            "value": {"close_date_min": str(close_min.date()), "engage_date_min": str(engage_min.date()), "engaged_before_window": int(len(early)),
                      "min_cycle_of_those": int(early["cycle_days"].min()) if len(early) else None, "their_win_rate": round(100 * float(early["won"].mean()), 1) if len(early) else None,
                      "lost_within_14d_share_in_clean_window": round(100 * lost_fast_share_clean, 1)},
            "verdict": "confirmada" if len(early) and early["won"].mean() > closed["won"].mean() + 0.05 else "refutada"}


@hypothesis("H12c", "Na janela limpa (engajados entre 2017-03-01 e ref - 138 d, sem truncamento nem censura) ainda há variação mensal relevante", "IA")
def h_season_clean(ctx):
    closed = ctx["closed"]
    lo = closed["close_date"].min(); hi = ctx["ref"] - pd.Timedelta(days=138)
    clean = closed[(closed["engage_date"] >= lo) & (closed["engage_date"] <= hi)]
    m = clean["engage_date"].dt.to_period("M").astype(str)
    g = clean.groupby(m)["won"].agg(n="size", win_rate="mean")
    p = chi2_pvalue(pd.crosstab(m, clean["won"]))
    ctx["clean_window"] = (lo, hi, int(len(clean)))
    return {"metric": "win rate por mês de engajamento na janela limpa", "value": {"window": [str(lo.date()), str(hi.date())], "n": int(len(clean)), "months": {k: {"n": int(r["n"]), "wr": round(100 * r["win_rate"], 1)} for k, r in g.iterrows()}, "spread_pp": round(100 * spread(g), 1), "p_value": p},
            "verdict": "confirmada" if p < 0.01 and spread(g) > 0.08 else "refutada"}


@hypothesis("H10b", "Na janela limpa, P(ganhar | ciclo >= a) continua subindo com a idade do deal", "IA")
def h_survival_clean(ctx):
    closed = ctx["closed"]
    lo = closed["close_date"].min(); hi = ctx["ref"] - pd.Timedelta(days=138)
    clean = closed[(closed["engage_date"] >= lo) & (closed["engage_date"] <= hi)]
    out = {}
    for a in (0, 7, 14, 21, 30, 45, 60, 90, 120):
        s = clean[clean["cycle_days"] >= a]
        out[str(a)] = {"n": int(len(s)), "win_rate": round(100 * float(s["won"].mean()), 1) if len(s) else None}
    return {"metric": "P(ganhar | ciclo >= a) na janela limpa", "value": out, "verdict": "confirmada" if out["14"]["win_rate"] > out["0"]["win_rate"] + 2 else "refutada"}


def run() -> tuple[str, dict]:
    tables = load_tables(RAW)
    e = enrich(tables)
    ref = reference_date(tables.pipeline)
    closed = e[e["is_closed"]].copy()
    closed["won"] = closed["deal_stage"].eq("Won")
    closed["cycle_days"] = (closed["close_date"] - closed["engage_date"]).dt.days
    ctx = {"tables": tables, "teams": tables.teams, "e": e, "ref": ref, "closed": closed, "open": e[e["is_open"]].copy()}
    results = []
    lines = ["# Resultados da exploração de hipóteses", "", f"Dados: {len(e):,} oportunidades; {len(closed):,} fechadas; data de referência {ref.date()}.", "",
             "| # | Hipótese | Origem | Métrica | Resultado | Veredito |", "|---|---|---|---|---|---|"]
    for hid, statement, origin, fn in HYPOTHESES:
        r = fn(ctx)
        r.update({"id": hid, "statement": statement, "origin": origin})
        results.append(r)
        val = json.dumps(r["value"], ensure_ascii=False, default=str)
        lines.append(f"| {hid} | {statement} | {origin} | {r['metric']} | `{val}` | **{r['verdict']}** |")
        print(f"{hid:4s} {r['verdict']:10s} {statement}")
    md = "\n".join(lines) + "\n"
    return md, {"reference_date": str(ref.date()), "results": results}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    md, data = run()
    DOCS.mkdir(exist_ok=True)
    (DOCS / "exploration_results.md").write_text(md, encoding="utf-8")
    (DOCS / "exploration_results.json").write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print("->", DOCS / "exploration_results.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
