"""Strategy decisions for Challenge 004: where to focus, sponsorship policy, what to stop, quick wins.

Decision rule used throughout: options that are NOT significantly worse than the best are "equivalent";
among equivalents, the cheapest wins. Cost inputs are explicit, configurable assumptions (the data has no prices).
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

from . import audits, cleaning, discovery, exploration, questions
from .data import PLATFORMS
from .questions import ALPHA, ENGAGEMENT, REACH, Answer

# --- Assumptions (replace with the company's real numbers) ---
COST_PER_FOLLOWER = questions.COST_PER_FOLLOWER       # US$ per follower per sponsored post (US$ 10 / 1K followers)
PRODUCTION_COST = {"text": 50, "image": 100, "mixed": 150, "video": 300}  # US$ per in-house post
TARGET_CPM = 10.0    # max US$ per 1,000 views worth paying (paid-social benchmark)
TARGET_CPE = 0.05    # max US$ per interaction (like/share/comment) worth paying
FOLLOWER_GRID = [5_000, 10_000, 25_000, 50_000, 100_000, 250_000, 500_000, 1_000_000]
COST_GRID = [0.005, 0.01, 0.02, 0.05]   # US$ per follower tried in the threshold sensitivity
CPM_GRID = [5.0, 10.0, 20.0]            # target CPMs tried in the threshold sensitivity

# --- A/B test sizing ---
POWER = 0.8
RELEVANT_UPLIFT = 0.05     # smallest uplift worth detecting in a sponsorship test (5%)
MIN_TEST_POSTS = 30        # practical floor per group, even when the math asks for fewer
MAX_AB_POSTS = 2_000       # above this per group, a dedicated A/B is impractical: monitor instead

ROBUST = "robusta (vale com dados reais)"
ASSUMED = "depende de premissa (recalcular com preços reais)"


@dataclass
class Recommendation(Answer):
    actions: list[str] = field(default_factory=list)

    def to_markdown(self, max_rows: int = 12) -> str:
        steps = "\n".join(f"{i}. {a}" for i, a in enumerate(self.actions, 1))
        return super().to_markdown(max_rows).replace("**Resposta:**", "**Decisão:**", 1) + (f"\n\n**Ações:**\n{steps}" if steps else "")


# ---------- building blocks ----------

def equivalence_table(df: pd.DataFrame, by: str, metric: str) -> pd.DataFrame:
    """Each option vs. the best one (Welch t, BH): equivalent = not significantly worse than the best."""
    means = df.groupby(by, observed=True)[metric].agg(["mean", "size"]).sort_values("mean", ascending=False)
    best = means.index[0]
    best_values = df.loc[df[by] == best, metric]
    rows = []
    for option in means.index:
        values = df.loc[df[by] == option, metric]
        p = 1.0 if option == best else stats.ttest_ind(best_values, values, equal_var=False).pvalue
        rows.append({by: option, "n": len(values), "média": values.mean(), "vs. melhor (%)": (values.mean() / best_values.mean() - 1) * 100, "p_value": p})
    table = pd.DataFrame(rows)
    table["q_value"] = multipletests(table["p_value"], method="fdr_bh")[1]
    table["equivalente ao melhor"] = table["q_value"] >= ALPHA
    return table.set_index(by)


def cheapest_equivalent(table: pd.DataFrame, cost: pd.Series) -> str:
    """Among options equivalent to the best, the one with the lowest cost per unit of result."""
    candidates = table[table["equivalente ao melhor"]].join(cost.rename("custo"))
    candidates["custo por resultado"] = candidates["custo"] / candidates["média"]
    return candidates["custo por resultado"].idxmin()


def frequency_effect(df: pd.DataFrame, metric: str = REACH) -> pd.DataFrame:
    """Per platform: do days with more posts get worse per-post results? (Spearman of daily volume vs. daily mean)."""
    daily = (df.assign(day=df["post_date"].dt.date)
               .groupby(["platform", "day"]).agg(posts=(metric, "size"), resultado=(metric, "mean")).reset_index())
    rows = []
    for platform, g in daily.groupby("platform"):
        rho, p = stats.spearmanr(g["posts"], g["resultado"])
        low, high = g["posts"].quantile([0.25, 0.75])
        rows.append({"plataforma": platform, "posts/dia (mediana)": g["posts"].median(), "ρ volume × resultado": rho, "p_value": p,
                     "resultado em dias de baixo volume": g.loc[g.posts <= low, "resultado"].mean(),
                     "resultado em dias de alto volume": g.loc[g.posts >= high, "resultado"].mean()})
    table = pd.DataFrame(rows).set_index("plataforma")
    table["q_value"] = multipletests(table["p_value"], method="fdr_bh")[1]
    table["saturação"] = (table["q_value"] < ALPHA) & (table["ρ volume × resultado"] < 0)
    return table


def implied_costs(df: pd.DataFrame, cost_per_follower: float = COST_PER_FOLLOWER) -> pd.DataFrame:
    """Sponsored posts with implied cost, CPM (per 1K views) and CPE (per interaction)."""
    sp = df[df["is_sponsored"].astype(bool)].copy()
    sp["custo"] = sp["follower_count"] * cost_per_follower
    sp["cpm"] = sp["custo"] / sp[REACH] * 1000
    sp["cpe"] = sp["custo"] / sp["interactions"]
    return sp


def break_even(df: pd.DataFrame, cost_per_follower: float = COST_PER_FOLLOWER, target_cpm: float = TARGET_CPM,
               target_cpe: float = TARGET_CPE) -> dict:
    """Follower threshold where a sponsored post stops paying off, and the engagement each creator size needs."""
    views, interactions = df[REACH].median(), df["interactions"].median()
    max_followers_cpm = target_cpm * views / 1000 / cost_per_follower
    max_followers_cpe = target_cpe * interactions / cost_per_follower
    grid = pd.DataFrame({"seguidores": FOLLOWER_GRID})
    grid["custo do post (US$)"] = grid["seguidores"] * cost_per_follower
    grid["CPM esperado (US$)"] = grid["custo do post (US$)"] / views * 1000
    grid["CPE esperado (US$)"] = grid["custo do post (US$)"] / interactions
    grid["views necessárias p/ CPM-alvo"] = grid["custo do post (US$)"] / target_cpm * 1000
    grid["engajamento necessário p/ CPE-alvo"] = grid["custo do post (US$)"] / (target_cpe * views)
    grid["vale a pena?"] = (grid["CPM esperado (US$)"] <= target_cpm) & (grid["CPE esperado (US$)"] <= target_cpe)
    return {"views medianas": views, "interações medianas": interactions, "teto de seguidores (CPM)": max_followers_cpm,
            "teto de seguidores (CPE)": max_followers_cpe, "threshold": min(max_followers_cpm, max_followers_cpe), "grade": grid.set_index("seguidores")}


def threshold_sensitivity(df: pd.DataFrame, costs: list[float] = COST_GRID, cpms: list[float] = CPM_GRID) -> pd.DataFrame:
    """Follower ceiling (CPM rule) for each price × target CPM: shows how much the ceiling owes to the assumptions."""
    views = df[REACH].median()
    grid = pd.DataFrame({f"CPM-alvo US$ {cpm:.0f}": [cpm * views / 1000 / c for c in costs] for cpm in cpms},
                        index=pd.Index([f"US$ {c * 1000:.0f} por mil seguidores" for c in costs], name="preço do creator"))
    return grid.round(-2)


def tier_cost_ratio(df: pd.DataFrame) -> float:
    """How many times more the largest tier pays per 1K views than the smallest. Independent of the price level
    whenever the fee is proportional to followers (it cancels out), so it holds for any per-follower rate."""
    cpm = implied_costs(df).groupby("follower_tier", observed=True)["cpm"].median().dropna()
    return float(cpm.iloc[-1] / cpm.iloc[0])


def ab_sample_size(p_control: float, p_test: float, power: float = POWER) -> int | None:
    """Posts per group to tell two rates apart (two-sided α, given power); None when there is no gap to size."""
    if not np.isfinite([p_control, p_test]).all() or p_control == p_test:
        return None
    n = NormalIndPower().solve_power(proportion_effectsize(p_test, p_control), alpha=ALPHA, power=power)
    return int(np.ceil(n))


def mean_sample_size(df: pd.DataFrame, metric: str, uplift: float = RELEVANT_UPLIFT, power: float = POWER) -> int:
    """Posts per group to detect a relative uplift in a metric's mean, floored at a practical minimum."""
    effect = uplift * df[metric].mean() / df[metric].std()
    return max(MIN_TEST_POSTS, int(np.ceil(NormalIndPower().solve_power(effect, alpha=ALPHA, power=power))))


# ---------- 1. Where to focus ----------

def where_to_focus(df: pd.DataFrame, production_cost: dict = PRODUCTION_COST, cost_per_follower: float = COST_PER_FOLLOWER) -> Recommendation:
    platform = equivalence_table(df, "platform", REACH).join(equivalence_table(df, "platform", ENGAGEMENT)[["vs. melhor (%)", "equivalente ao melhor"]], rsuffix=" (engajamento)")
    content = equivalence_table(df, "content_type", ENGAGEMENT)
    content["custo de produção (US$)"] = pd.Series(production_cost)
    tier = equivalence_table(df, "follower_tier", ENGAGEMENT)
    tier["custo mediano patrocinado (US$)"] = implied_costs(df, cost_per_follower).groupby("follower_tier", observed=True)["custo"].median()
    frequency = frequency_effect(df)

    platform_tie = platform["equivalente ao melhor"].all() and platform["equivalente ao melhor (engajamento)"].all()
    format_tie = content["equivalente ao melhor"].all()
    tier_tie = tier["equivalente ao melhor"].all()
    best_platform = platform.index[0]
    best_format = cheapest_equivalent(content, pd.Series(production_cost))
    best_tier = cheapest_equivalent(tier, tier["custo mediano patrocinado (US$)"])
    saturated = frequency.index[frequency["saturação"]].tolist()

    decision = (
        (f"Plataforma: nenhuma vence (diferenças ≤ {platform['vs. melhor (%)'].abs().max():.2f}%), então concentre em 1–2 por custo operacional e presença do público-alvo. "
         if platform_tie else f"Plataforma: {best_platform} (significativamente melhor). ")
        + (f"Formato: nenhum engaja mais (diferenças ≤ {content['vs. melhor (%)'].abs().max():.2f}%), então vale o mais barato de produzir; "
           f"pela premissa de custo, {best_format}, mas a escolha depende do custo real e do formato que cada plataforma comporta. "
           if format_tie else f"Formato: {best_format} (rende mais e compensa o custo de produção). ")
        + ("Creators: o porte não muda o engajamento nem as views, então não há motivo para pagar mais por creators grandes. "
           if tier_tie else f"Creators: {best_tier} (equivalente em engajamento e mais barato). ")
        + (f"Frequência: há saturação em {', '.join(saturated)}." if saturated else
           f"Frequência: dias com mais posts (mediana de {frequency['posts/dia (mediana)'].median():.0f} por plataforma, somando todos os creators) "
           "não têm pior desempenho por post; o limite é a capacidade de produção, e a cadência da marca deve ser medida com os dados dela.")
    )
    actions = [
        ("Não pagar a mais por formato esperando engajamento: levantar o custo real de produção por formato e usar o mais barato que "
         f"a plataforma comporta (pela premissa atual, {best_format})." if format_tie
         else f"Fixar o mix de produção em {best_format} como padrão."),
        "Não pagar prêmio por porte de creator: escolher pelo preço por resultado e pelo público-alvo." if tier_tie
        else f"Priorizar creators {best_tier} nas próximas contratações.",
        "Concentrar o time em 1–2 plataformas (critério: onde está o cliente-alvo e o menor custo operacional)." if platform_tie
        else f"Realocar esforço para {best_platform}.",
        "Aumentar a frequência até o limite da capacidade e reavaliar a saturação mensalmente (`frequency_effect`).",
    ]
    return Recommendation("1. Onde concentrar esforço?", decision, platform,
                          {"Formato (engajamento × custo)": content, "Faixa de creator": tier, "Frequência (saturação por plataforma)": frequency},
                          actions)


def disclosure_rule(df: pd.DataFrame) -> str:
    """Disclosure action backed by the audit: share at high risk, share with a visible label, and the engagement cost."""
    sponsored = df[df["is_sponsored"].astype(bool)]
    high = 100 * (audits.disclosure_risk(sponsored) == "alto").mean()
    visible = 100 * audits.has_ad_marker(sponsored).mean()
    costly = audits.disclosure_audit(df).details["Disclosure × engajamento"]["significativo"].any()
    return (f"Exigir rótulo de publicidade verificável no próprio texto (#publi/#ad): hoje {high:.0f}% dos patrocinados usam disclosure "
            f"implícito (risco regulatório alto) e só {visible:.1f}% mostram o rótulo no texto"
            + (". O tipo de disclosure muda o engajamento: testar antes." if costly else "; o tipo de disclosure não muda o engajamento."))


# ---------- 2. Sponsorship policy ----------

def sponsorship_policy(df: pd.DataFrame, cost_per_follower: float = COST_PER_FOLLOWER, target_cpm: float = TARGET_CPM,
                       target_cpe: float = TARGET_CPE) -> Recommendation:
    answer = questions.does_sponsorship_work(df, cost_per_follower)
    eng = answer.evidence.loc[f"{ENGAGEMENT} — estratificado"]
    conditions = answer.details["Em que condições? (uplift do patrocínio por condição)"]
    good_conditions = conditions[conditions["significativo"] & (conditions["uplift engajamento (%)"] > 0)]
    be = break_even(df, cost_per_follower, target_cpm, target_cpe)
    costs = implied_costs(df, cost_per_follower)
    profile = costs.groupby("follower_tier", observed=True).agg(
        posts=("custo", "size"), cpm_mediano=("cpm", "median"), cpe_mediano=("cpe", "median"), engajamento=(ENGAGEMENT, "mean"))
    profile["dentro do threshold"] = profile["cpm_mediano"] <= target_cpm

    lift = eng["p_value"] < ALPHA and eng["diferença"] > 0
    ratio = tier_cost_ratio(df)
    sensitivity = threshold_sensitivity(df)
    group_size = mean_sample_size(df, ENGAGEMENT)
    decision = (
        ("Patrocinar para ganhar desempenho: sim, " if lift else "Patrocinar para ganhar desempenho: não. O patrocínio não muda engajamento nem alcance. ")
        + ("nas condições com efeito: " + ", ".join(good_conditions["condição"]) + ". " if len(good_conditions) else "Nenhuma condição tem efeito. ")
        + f"Regra que vale com qualquer preço: como as views não crescem com os seguidores, um cachê proporcional aos seguidores deixa o "
          f"creator {profile.index[-1]} ~{ratio:,.0f}x mais caro por mil views que o {profile.index[0]}. Por isso, pagar por resultado, não por post. "
        + f"Com as premissas atuais (US$ {cost_per_follower * 1000:.0f} por mil seguidores, até US$ {target_cpm:.0f} por mil views e "
          f"US$ {target_cpe:.2f} por interação), o post de preço fixo se paga até ~{be['threshold']:,.0f} seguidores; "
          f"com outros preços o teto vai de {sensitivity.min().min():,.0f} a {sensitivity.max().max():,.0f} (tabela de sensibilidade). "
        + "O desempenho histórico do creator não serve de critério, porque não diferencia creators."
    )
    actions = [
        f"Contratar por resultado: até US$ {target_cpm:.0f} por mil views ou US$ {target_cpe:.2f} por interação, em vez de preço fixo por post (vale com qualquer cachê).",
        f"Enquanto o preço for fixo por post: teto de ~{be['threshold']:,.0f} seguidores (sai das premissas; recalcular com o cachê real).",
        disclosure_rule(df),
        f"Todo novo patrocínio entra com grupo de comparação (posts orgânicos parecidos, ≥ {group_size} por grupo) para medir o ganho real.",
    ]
    return Recommendation("2. Política de patrocínio", decision, answer.evidence,
                          {"Ponto de equilíbrio por tamanho de creator": be["grade"], "Teto de seguidores por premissa (sensibilidade)": sensitivity,
                           "Perfil de influenciador (patrocinados)": profile, "Condições testadas": conditions}, actions)


# ---------- 3. Stop doing ----------

def stop_doing(df: pd.DataFrame, production_cost: dict = PRODUCTION_COST, cost_per_follower: float = COST_PER_FOLLOWER,
               target_cpm: float = TARGET_CPM, target_cpe: float = TARGET_CPE) -> Recommendation:
    be = break_even(df, cost_per_follower, target_cpm, target_cpe)
    costs = implied_costs(df, cost_per_follower)
    above = costs[costs["follower_count"] > be["threshold"]]
    fair_price = np.minimum(above[REACH] / 1000 * target_cpm, above["interactions"] * target_cpe)
    sponsorship_waste = (above["custo"] - fair_price).sum()

    content = equivalence_table(df, "content_type", ENGAGEMENT)
    cheapest = cheapest_equivalent(content, pd.Series(production_cost))
    equivalent_formats = content.index[content["equivalente ao melhor"]]
    extra = df[df["content_type"].isin(equivalent_formats)]["content_type"].map(production_cost) - production_cost[cheapest]
    production_waste = extra.clip(lower=0).sum()

    beliefs = questions.what_does_not_work(df).evidence
    rows = [
        {"investimento": f"Patrocínio acima de {be['threshold']:,.0f} seguidores", "posts": len(above),
         "% dos patrocinados": len(above) / len(costs) * 100, "gasto implícito (US$)": above["custo"].sum(),
         "excedente sobre preço justo (US$)": sponsorship_waste, "evidência": "views e engajamento não crescem com seguidores"},
        {"investimento": f"Formatos mais caros que {cheapest} sem ganho", "posts": int((extra > 0).sum()),
         "% dos patrocinados": np.nan, "gasto implícito (US$)": df["content_type"].map(production_cost).sum(),  # total production spend
         "excedente sobre preço justo (US$)": production_waste, "evidência": "engajamento equivalente entre formatos"},
    ]
    for belief in beliefs[beliefs["se sustenta?"] == "não"]["crença de mercado"]:
        rows.append({"investimento": f"Otimizar com base em: {belief}", "posts": np.nan, "% dos patrocinados": np.nan,
                     "gasto implícito (US$)": np.nan, "excedente sobre preço justo (US$)": np.nan, "evidência": "efeito nulo (q ≥ 0,05)"})
    table = pd.DataFrame(rows).set_index("investimento")
    decision = (f"Parar de pagar preço fixo por seguidores: as views não acompanham o porte. Pelas premissas de preço, {len(above) / len(costs):.0%} dos posts "
                f"patrocinados ficam acima do teto e {sponsorship_waste / costs['custo'].sum():.0%} do gasto implícito com patrocínio é excedente sobre o preço justo "
                f"(~US$ {sponsorship_waste / 1e6:,.0f} mi neste histórico; valor ilustrativo, não contábil). "
                "Parar de pagar a mais por formatos caros esperando engajamento: nenhum formato engaja mais. "
                f"Parar de usar como regra geral {int((beliefs['se sustenta?'] == 'não').sum())} práticas testadas sem efeito (horário, hashtags, legenda, duração...).")
    actions = ["Congelar renovações por preço fixo acima do teto até renegociar por resultado.",
               "Formatos caros só com motivo de marca ou teste A/B aprovado, não por expectativa de engajamento.",
               "Tirar \"melhor horário\", \"número ideal de hashtags\" e \"legenda longa\" do checklist como regra geral; "
               "horário só por plataforma e depois de teste (ver fila de testes)."]
    return Recommendation("3. O que parar de fazer", decision, table, {"Crenças testadas": beliefs}, actions)


# ---------- 4. Quick wins ----------

def quick_wins(df: pd.DataFrame, **assumptions) -> Recommendation:
    """Actions for this week: robust ones first (valid on the company's real data too), then the ones that rest on cost assumptions."""
    focus, stop = where_to_focus(df), stop_doing(df, **assumptions)
    be = break_even(df, **assumptions)
    cheapest = cheapest_equivalent(focus.details["Formato (engajamento × custo)"], pd.Series(PRODUCTION_COST))
    waste_share = stop.evidence.iloc[0]["excedente sobre preço justo (US$)"] / stop.evidence.iloc[0]["gasto implícito (US$)"]
    wins = pd.DataFrame([
        {"ação": "Novos contratos e renovações por resultado (views ou interações), não por post", "base": ROBUST, "esforço": "médio",
         "impacto": f"o custo por view deixa de crescer com o porte (hoje o maior porte paga ~{tier_cost_ratio(df):,.0f}x mais por mil views)",
         "dono": "Parcerias / Compras"},
        {"ação": "Rótulo de publicidade verificável no texto (#publi/#ad) como padrão", "base": ROBUST, "esforço": "baixo",
         "impacto": disclosure_rule(df).split(": ", 1)[1], "dono": "Social media"},
        {"ação": "Todo patrocínio novo com grupo de comparação orgânico", "base": ROBUST, "esforço": "baixo",
         "impacto": f"mede o ganho real; ≥ {mean_sample_size(df, ENGAGEMENT)} posts por grupo para ver +{RELEVANT_UPLIFT:.0%} de engajamento",
         "dono": "AI Master / Analytics"},
        {"ação": "Não pagar a mais por creator \"campeão\" e tirar horário/hashtags ideais do checklist", "base": ROBUST, "esforço": "baixo",
         "impacto": "desempenho passado e essas regras não mudam o resultado; horas do time liberadas", "dono": "Social media"},
        {"ação": f"Teto de ~{be['threshold']:,.0f} seguidores para contratos de preço fixo", "base": ASSUMED, "esforço": "baixo (regra de compra)",
         "impacto": f"pelas premissas, {waste_share:.0%} do gasto implícito com patrocínio é excedente", "dono": "Head de Marketing"},
        {"ação": f"Formato padrão pelo custo real de produção (pela premissa, {cheapest})", "base": ASSUMED, "esforço": "baixo",
         "impacto": "mesmo engajamento com menor custo por post", "dono": "Conteúdo"},
    ])
    robust = int((wins["base"] == ROBUST).sum())
    decision = (f"{len(wins)} ações para esta semana, sem contratação nem ferramenta nova. As {robust} primeiras valem também com os dados reais "
                f"da empresa; as {len(wins) - robust} últimas dependem das premissas de preço e devem ser recalculadas com os preços reais.")
    return Recommendation("4. Quick wins (esta semana)", decision, wins,
                          {"Base: onde concentrar": pd.DataFrame({"decisão": [focus.verdict]})}, wins["ação"].tolist())


def test_queue(df: pd.DataFrame, by_platform: pd.DataFrame | None = None) -> Recommendation:
    """The few hypotheses worth testing, ordered by evidence, with the posts each test needs.
    Sized to confirm half of the observed gap (observed gaps from a scan are inflated by selection)."""
    if by_platform is None:
        by_platform = pd.concat([discovery.scan_by_platform(df, m, platforms=PLATFORMS) for m in ["views", "likes", "comments_count"]],
                                ignore_index=True)
    q_global = multipletests(by_platform["p_value"], method="fdr_bh")[1]
    best = by_platform.assign(q_global=q_global).sort_values("p_value").iloc[0]
    metric_names = {"views": "views", "likes": "likes", "comments_count": "comentários"}
    rows = []
    rest_rate = best["taxa top 5% (%)"] / best["lift"] / 100
    target = (rest_rate + best["taxa top 5% (%)"] / 100) / 2
    rows.append({"tipo": "bolsão", "hipótese": f"{best['plataforma']} · {best['bolsão']} aumenta a chance de top 5% em {metric_names.get(best['alvo'], best['alvo'])}",
                 "evidência": f"{best['taxa top 5% (%)']:.1f}% vs. {rest_rate:.1%} ({best['lift']:.1f}x), nos 2 anos; q global = {best['q_global']:.3f} entre {len(by_platform):,} testes",
                 "posts por grupo": ab_sample_size(rest_rate, target)})

    daypart = discovery.daypart_top_rate(df, "comments_count")
    top_hour = daypart.sort_values("q (hora)").iloc[0]
    if top_hour["q (hora)"] < ALPHA:
        platform = daypart.index[daypart["q (hora)"] == top_hour["q (hora)"]][0]
        g = df[df["platform"] == platform]
        top = g["comments_count"] >= g["comments_count"].quantile(discovery.TOP1_Q)
        early = g["daypart"].isin(["madrugada", "manhã"])
        p_early, p_late = top[early].mean(), top[~early].mean()
        rows.append({"tipo": "horário", "hipótese": f"{platform}: posts até 12h entram mais no top 1% de comentários",
                     "evidência": f"{p_early:.2%} vs. {p_late:.2%}; hora típica do top {top_hour['hora mediana top']:.0f}h vs. {top_hour['hora mediana demais']:.0f}h (q = {top_hour['q (hora)']:.2f})",
                     "posts por grupo": ab_sample_size(p_late, (p_early + p_late) / 2)})

    rows.append({"tipo": "patrocínio", "hipótese": f"Patrocínio aumenta o engajamento em pelo menos {RELEVANT_UPLIFT:.0%}",
                 "evidência": "nenhum efeito neste histórico; aqui as métricas variam só ~1% entre posts, por isso bastam poucos posts "
                             "(mínimo prático); com os dados da empresa a conta é refeita",
                 "posts por grupo": mean_sample_size(df, ENGAGEMENT)})
    table = pd.DataFrame(rows).dropna(subset=["posts por grupo"]).astype({"posts por grupo": int})
    table["como tratar"] = np.where(table["posts por grupo"] <= MAX_AB_POSTS, "teste A/B",
                                    "acompanhar no histórico (A/B exigiria posts demais)")
    table.index = pd.RangeIndex(1, len(table) + 1, name="#")
    decision = (f"Só {len(table)} hipóteses merecem teste; o resto das variações encontradas está no nível do acaso. "
                "Nenhuma vira regra antes do teste: os números de posts mostram o custo de confirmar cada uma.")
    actions = [f"{r['hipótese']}: {r['como tratar']}; {r['posts por grupo']:,} posts por grupo." for _, r in table.iterrows()]
    brief = test_brief(df, best, rest_rate, target, int(table.iloc[0]["posts por grupo"]))
    return Recommendation("5. Fila de testes", decision, table, {"Brief do teste 1": brief}, actions)


WINDOW_SUFFIX = " (janela)"


def pocket_mask(df: pd.DataFrame, pocket: pd.Series) -> pd.Series:
    """Posts of a categorical pocket found by discovery.scan_by_platform (e.g. TikTok · beauty · Spanish)."""
    mask = df["platform"] == pocket["plataforma"]
    for column, value in zip(pocket["dimensão"].split(" × "), pocket["bolsão"].split(" · ")):
        if column.endswith(WINDOW_SUFFIX):  # numeric window, e.g. "hour (janela)" = "6–9"
            low, high = (float(v.replace(",", "")) for v in value.split("–"))
            mask &= df[column.removesuffix(WINDOW_SUFFIX)].between(low, high)
        else:
            mask &= df[column].astype(str) == value
    return mask


def _dominant(values: pd.Series) -> tuple[str, float]:
    shares = values.value_counts(normalize=True)
    return shares.index[0], shares.iloc[0]


def test_brief(df: pd.DataFrame, pocket: pd.Series, control_rate: float, target_rate: float, posts_per_group: int) -> pd.DataFrame:
    """Everything a team needs to run the pocket test: groups, format, creator tier, audience, time, length and success rule."""
    segment = df[pocket_mask(df, pocket)]
    platform, metric = pocket["plataforma"], pocket["alvo"]
    dims = dict(zip(pocket["dimensão"].split(" × "), pocket["bolsão"].split(" · ")))
    language = dims.get("language")
    on_platform = df[df["platform"] == platform]
    control = on_platform.loc[on_platform["language"] != language, "language"].mode()[0] if language else None
    fmt = segment["content_type"].mode()[0]
    cpm = implied_costs(df).groupby("follower_tier", observed=True)["cpm"].median()
    hour = discovery.daypart_top_rate(on_platform, metric, q=discovery.TOP_Q).loc[platform, "q (hora)"]
    length_matters = bool(audits.length_by_format(df).evidence["significativo"].any())
    unit = audits.LENGTH_UNIT.get(fmt, "")
    rows = {
        "Grupos": f"{pocket['bolsão']} no {platform} (teste) × o mesmo conteúdo em {control} (controle)" if control else pocket["bolsão"],
        "Formato": f"{fmt} ({_dominant(segment['content_type'])[1]:.0%} do segmento); o mesmo nos dois grupos",
        "Faixa de creator": f"{cpm.idxmin()} (menor custo por mil views); a mesma nos dois grupos",
        "Público-alvo": "{} ({:.0%} do segmento) e {} anos ({:.0%}): os mais frequentes".format(*_dominant(segment["audience_location"]),
                                                                                         *_dominant(segment["audience_age_distribution"])),
        "Horário": (f"sem evidência de horário para {metric} no {platform} (q = {hour:.2f}): distribuir os horários igualmente entre os grupos"
                    if hour >= ALPHA else f"horário com efeito no {platform} (q = {hour:.2f}): fixar o mesmo horário nos dois grupos"),
        "Duração": (f"~{segment.loc[segment['content_type'] == fmt, 'content_length'].median():.0f} {unit} (mediana do segmento); "
                    + ("a duração mudou o resultado: manter igual nos grupos" if length_matters else "a duração não mudou o resultado em nenhum formato")),
        "Critério de sucesso": (f"taxa de top 5% em {metric} ≥ {target_rate:.1%} no grupo {language or 'teste'} (resto do {platform}: {control_rate:.1%}), "
                                f"p < {ALPHA}, com {posts_per_group:,} posts por grupo (poder de {POWER:.0%})"),
    }
    return pd.DataFrame({"campo": rows.keys(), "valor": rows.values()}).set_index("campo")


# Claims a generic LLM analysis would make from these beliefs (questions.what_does_not_work).
AI_CLAIMS = {
    "Mais seguidores → mais alcance": "Creators maiores entregam mais alcance: priorize macro e mega.",
    "Vídeo engaja mais que imagem/texto": "Vídeo é o formato que mais engaja: migre o mix para vídeo.",
    "Postar à noite (18–24h) dá mais alcance": "Publique à noite (18–24h), quando o alcance é maior.",
}


def claims_vs_data(df: pd.DataFrame, queue: Recommendation | None = None) -> pd.DataFrame:
    """'What an AI would say × what the data shows': the biggest raw segment, common beliefs and the one pocket that survived."""
    segments = questions.what_drives_engagement(df).details["Segmentos com maior índice (aparente)"]
    top = segments.iloc[0]
    rows = [{"o que a IA diria": f"{top['segmento']} é o segmento que mais engaja: concentre o investimento nele.",
             "o que os dados mostram": f"índice {top['índice']:.1f} (média = 100), n = {top['n']}, p = {top['p_value']:.2f}, q = {top['q_value']:.2f}",
             "veredito": "maior diferença bruta entre centenas de segmentos; some após a correção" if not top["significativo"] else "se sustenta"}]
    beliefs = questions.what_does_not_work(df).evidence.set_index("crença de mercado")
    for belief, claim in AI_CLAIMS.items():
        b = beliefs.loc[belief]
        effect = f"ρ = {b['efeito']:.3f}" if b["unidade"].startswith("ρ") else f"{b['efeito']:+.2f}%"
        rows.append({"o que a IA diria": claim, "o que os dados mostram": f"{effect} ({b['métrica']}), q = {b['q_value']:.2f}",
                     "veredito": "não se sustenta" if b["se sustenta?"] == "não" else "se sustenta"})
    queue = queue or test_queue(df)
    pocket = queue.evidence.iloc[0]
    rows.append({"o que a IA diria": f"{pocket['hipótese']}.", "o que os dados mostram": pocket["evidência"],
                 "veredito": f"único que passou no filtro: vai para {pocket['como tratar']} com {pocket['posts por grupo']:,} posts por grupo"})
    return pd.DataFrame(rows)


def recommend_all(df: pd.DataFrame) -> list[Recommendation]:
    return [where_to_focus(df), sponsorship_policy(df), stop_doing(df), quick_wins(df)]


def deliverable_evidence(df: pd.DataFrame, queue: Recommendation | None = None) -> Answer:
    """The proofs the executive summary relies on: rate per follower vs. per view, survivorship, stability over time, AI claims vs. data."""
    tiers = exploration.engagement_rate_by_tier(df)
    per_follower, per_view = tiers["interações por seguidor (mediana)"], tiers["interações por view (mediana)"]
    zeros = cleaning.survivorship_check(df)
    quarters, seasonality = exploration.engagement_by_quarter(df)
    verdict = (f"Medida por seguidor, o {tiers.index[0]} parece ~{per_follower.iloc[0] / per_follower.iloc[-1]:.0f}x melhor que o "
               f"{tiers.index[-1]} ({per_follower.iloc[0]:.3f} × {per_follower.iloc[-1]:.4f}). É efeito da conta: por view, todas as faixas "
               f"ficam em ~{per_view.median():.3f}, com ~{tiers['views (mediana)'].median():,.0f} views medianas. "
               f"{int(zeros['posts com zero'].sum())} posts com zero em views, likes, compartilhamentos "
               f"ou comentários (mínimo de {zeros.loc['likes', 'mínimo']:,} likes; views de {zeros.loc['views', 'mínimo']:,} a "
               f"{zeros.loc['views', 'máximo']:,}): a base não tem posts que fracassaram. Engajamento médio entre "
               f"{quarters['engajamento'].min():.4f} e {quarters['engajamento'].max():.4f} nos {len(quarters)} trimestres "
               f"({quarters.index[0]} a {quarters.index[-1]}; p = {seasonality['p_value']:.2f}): estável, sem sazonalidade.")
    return Answer("6. Provas do resumo executivo", verdict, claims_vs_data(df, queue),
                  {"Engajamento por seguidor × por view, por faixa de creator": tiers, "Posts sem resultado (survivorship)": zeros,
                   "Engajamento por trimestre": quarters})
