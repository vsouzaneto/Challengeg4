"""Answers the four business questions of Challenge 004 with tested evidence (one function per question)."""
from dataclasses import dataclass, field
from itertools import combinations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests

from .data import AUDIENCE, PLATFORMS

ALPHA = 0.05
MIN_SEGMENT = 100
ENGAGEMENT = "eng_rate_views"  # (likes + shares + comments) / views
REACH = "views"
DIMENSIONS = ["platform", "content_type", "content_category", "follower_tier"]
STRATA = DIMENSIONS  # sponsored vs. organic is compared only inside identical strata
# Assumption (no price column in the data): a sponsored post costs ~US$10 per 1,000 followers.
COST_PER_FOLLOWER = 0.01


@dataclass
class Answer:
    question: str
    verdict: str
    evidence: pd.DataFrame
    details: dict[str, pd.DataFrame] = field(default_factory=dict)

    def to_markdown(self, max_rows: int = 12) -> str:
        parts = [f"## {self.question}", f"**Resposta:** {self.verdict}", self.evidence.head(max_rows).to_markdown(floatfmt=".4g")]
        parts += [f"### {name}\n{table.head(max_rows).to_markdown(floatfmt='.4g')}" for name, table in self.details.items()]
        return "\n\n".join(parts)


# ---------- statistical building blocks ----------

def _fdr(pvalues: pd.Series) -> np.ndarray:
    return multipletests(pvalues, method="fdr_bh")[1] if len(pvalues) else np.array([])


def segment_scan(df: pd.DataFrame, dims: list[str], metric: str, min_n: int = MIN_SEGMENT) -> pd.DataFrame:
    """Every value and every combination of `dims` vs. the rest (Welch t-test, BH-corrected).

    `índice` = segment mean / overall mean × 100.
    """
    overall, rows = df[metric].mean(), []
    for size in range(1, len(dims) + 1):
        for combo in combinations(dims, size):
            keys = combo[0] if len(combo) == 1 else list(combo)
            for key, idx in df.groupby(keys, observed=True).groups.items():
                if len(idx) < min_n:
                    continue
                inside = df.loc[idx, metric]
                outside = df[metric].drop(idx)
                key = key if isinstance(key, tuple) else (key,)
                rows.append({"segmento": " · ".join(map(str, key)), "dimensões": " × ".join(combo), "n": len(idx),
                             "índice": inside.mean() / overall * 100,
                             "p_value": stats.ttest_ind(inside, outside, equal_var=False).pvalue})
    table = pd.DataFrame(rows)
    table["q_value"] = _fdr(table["p_value"])
    table["significativo"] = table["q_value"] < ALPHA
    return table.sort_values("índice", ascending=False, ignore_index=True)


def stratified_difference(df: pd.DataFrame, treated: pd.Series, metric: str, strata: list[str]) -> dict:
    """Treated − control difference averaged over identical strata (inverse-variance weights), in % of control."""
    diffs, variances, control_means = [], [], []
    for _, g in df.assign(_t=treated.values).groupby(strata, observed=True):
        t, c = g.loc[g["_t"], metric], g.loc[~g["_t"], metric]
        if len(t) < 2 or len(c) < 2:
            continue
        diffs.append(t.mean() - c.mean())
        variances.append(t.var() / len(t) + c.var() / len(c))
        control_means.append(c.mean())
    w = 1 / np.array(variances)
    estimate = np.sum(w * diffs) / w.sum()
    se = np.sqrt(1 / w.sum())
    base = np.average(control_means, weights=w)
    return {"diferença": estimate, "IC95 inf": estimate - 1.96 * se, "IC95 sup": estimate + 1.96 * se,
            "diferença (%)": estimate / base * 100, "p_value": 2 * stats.norm.sf(abs(estimate / se)), "estratos": len(diffs)}


def regression_effect(df: pd.DataFrame, metric: str, term: str, controls: list[str]) -> dict:
    """OLS coefficient of `term` controlling for categorical `controls` (robust HC3 errors)."""
    formula = f"{metric} ~ C({term}) + " + " + ".join(f"C({c})" for c in controls)
    fit = smf.ols(formula, data=df.astype({term: str})).fit(cov_type="HC3")
    name = next(p for p in fit.params.index if p.startswith(f"C({term})"))
    low, high = fit.conf_int().loc[name]
    return {"coeficiente": fit.params[name], "IC95 inf": low, "IC95 sup": high, "p_value": fit.pvalues[name], "R²": fit.rsquared}


def _group_effects(df: pd.DataFrame, by: str, metric: str) -> dict:
    groups = [g.values for _, g in df.groupby(by, observed=True)[metric]]
    h, p = stats.kruskal(*groups)
    means = df.groupby(by, observed=True)[metric].mean()
    return {"dimensão": by, "melhor": means.idxmax(), "pior": means.idxmin(),
            "diferença melhor−pior (%)": (means.max() / means.min() - 1) * 100, "epsilon²": h / (len(df) - 1), "p_value": p}


def _verdict_from(table: pd.DataFrame, positive: str, negative: str) -> str:
    return positive if table["significativo"].any() else negative


# ---------- Q1 ----------

def what_drives_engagement(df: pd.DataFrame, metric: str = ENGAGEMENT) -> Answer:
    """Q1: which platform / content type / category / creator size (and combinations) lift engagement?"""
    effects = pd.DataFrame([_group_effects(df, d, metric) for d in DIMENSIONS])
    effects["q_value"] = _fdr(effects["p_value"])
    effects["significativo"] = effects["q_value"] < ALPHA
    segments = segment_scan(df, DIMENSIONS, metric)
    winners = segments[segments["significativo"]]
    n_tests, n_raw = len(segments), int((segments["p_value"] < ALPHA).sum())
    if len(winners):
        best = winners.iloc[0]
        verdict = f"{best['segmento']} gera {best['índice'] - 100:+.1f}% de engajamento vs. a média (q={best['q_value']:.3g})."
    else:
        verdict = (f"Nenhum fator nem combinação gera engajamento diferente. {n_tests} segmentos testados, {n_raw} com p<0,05 cru "
                   f"(~{n_tests * ALPHA:.0f} esperados por acaso) e 0 após correção. Maior diferença entre grupos: "
                   f"{effects['diferença melhor−pior (%)'].max():.2f}%.")
    return Answer("1. O que gera engajamento?", verdict, effects,
                  {"Segmentos com maior índice (aparente)": segments.head(10), "Segmentos significativos": winners})


# ---------- Q2 ----------

def does_sponsorship_work(df: pd.DataFrame, cost_per_follower: float = COST_PER_FOLLOWER) -> Answer:
    """Q2: sponsored vs. organic on engagement, reach and implied cost — overall and by condition."""
    sponsored = df["is_sponsored"].astype(bool)
    overall = pd.DataFrame({
        f"{m} — estratificado": stratified_difference(df, sponsored, m, STRATA) for m in [ENGAGEMENT, REACH, "likes", "comments_count"]
    }).T
    controls = [c for c in STRATA]
    overall.loc[f"{ENGAGEMENT} — regressão", ["diferença", "IC95 inf", "IC95 sup", "p_value"]] = list(
        regression_effect(df, ENGAGEMENT, "is_sponsored", controls).values())[:4]
    overall["q_value"] = _fdr(overall["p_value"])

    conditions = []
    for dim in ["platform", "follower_tier", "content_type", "content_category"]:
        for value, g in df.groupby(dim, observed=True):
            others = [s for s in STRATA if s != dim]
            res = stratified_difference(g, g["is_sponsored"].astype(bool), ENGAGEMENT, others)
            conditions.append({"condição": f"{dim} = {value}", "uplift engajamento (%)": res["diferença (%)"], "p_value": res["p_value"]})
    conditions = pd.DataFrame(conditions)
    conditions["q_value"] = _fdr(conditions["p_value"])
    conditions["significativo"] = conditions["q_value"] < ALPHA

    by_sponsor = df[sponsored].groupby("sponsor_category")[ENGAGEMENT].mean() / df.loc[~sponsored, ENGAGEMENT].mean() * 100 - 100
    by_disclosure = df[sponsored].groupby("disclosure_type")[ENGAGEMENT].mean() / df.loc[~sponsored, ENGAGEMENT].mean() * 100 - 100

    cost = df[sponsored].assign(custo_estimado=lambda d: d["follower_count"] * cost_per_follower,
                                cpm_implicito=lambda d: d["custo_estimado"] / d[REACH] * 1000)
    cost_table = cost.groupby("follower_tier", observed=True).agg(
        posts=("custo_estimado", "size"), custo_mediano=("custo_estimado", "median"), views_medianas=(REACH, "median"),
        cpm_implicito_mediano=("cpm_implicito", "median"), engajamento_medio=(ENGAGEMENT, "mean"))

    eng = overall.loc[f"{ENGAGEMENT} — estratificado"]
    reach = overall.loc[f"{REACH} — estratificado"]
    works = eng["p_value"] < ALPHA and eng["diferença"] > 0
    cheapest, priciest = cost_table["cpm_implicito_mediano"].idxmin(), cost_table["cpm_implicito_mediano"].idxmax()
    verdict = (
        f"{'Sim' if works else 'Não'}: no mesmo estrato (plataforma × formato × categoria × porte), patrocinado vs. orgânico = "
        f"{eng['diferença (%)']:+.3f}% de engajamento e {reach['diferença (%)']:+.3f}% de alcance (p={eng['p_value']:.2f} / {reach['p_value']:.2f}). "
        f"{int(conditions['significativo'].sum())} de {len(conditions)} condições têm efeito. Como as views não crescem com os seguidores, "
        f"o custo por mil views (CPM implícito) cresce com o porte: {cheapest} US$ {cost_table.loc[cheapest, 'cpm_implicito_mediano']:.2f} vs. "
        f"{priciest} US$ {cost_table.loc[priciest, 'cpm_implicito_mediano']:.0f} (premissa: US$ {cost_per_follower * 1000:.0f} por mil seguidores). "
        f"Se patrocinar, use creators pequenos e negocie por resultado."
    )
    return Answer("2. Patrocínio funciona?", verdict, overall,
                  {"Em que condições? (uplift do patrocínio por condição)": conditions.sort_values("uplift engajamento (%)", ascending=False),
                   "Custo implícito por porte de creator (patrocinados)": cost_table,
                   "Engajamento vs. orgânico por categoria de patrocinador (%)": by_sponsor.to_frame("diferença (%)"),
                   "Engajamento vs. orgânico por tipo de disclosure (%)": by_disclosure.to_frame("diferença (%)")})


# ---------- Q3 ----------

def audience_that_engages(df: pd.DataFrame, metric: str = ENGAGEMENT) -> Answer:
    """Q3: which audience segment engages most — overall and within each platform / content type / category?"""
    overall = pd.DataFrame([_group_effects(df, a, metric) for a in AUDIENCE])
    overall["q_value"] = _fdr(overall["p_value"])

    rows = []
    for context in ["platform", "content_type", "content_category"]:
        for value, g in df.groupby(context, observed=True):
            for aud in AUDIENCE:
                eff = _group_effects(g, aud, metric)
                rows.append({"contexto": f"{context} = {value}", "audiência": aud, "segmento que mais engaja": eff["melhor"],
                             "diferença melhor−pior (%)": eff["diferença melhor−pior (%)"], "p_value": eff["p_value"]})
    within = pd.DataFrame(rows)
    within["q_value"] = _fdr(within["p_value"])
    within["significativo"] = within["q_value"] < ALPHA

    persona = segment_scan(df, AUDIENCE, metric)
    verdict = _verdict_from(
        within,
        "Há segmentos de audiência que engajam mais em contextos específicos — ver tabela de significativos.",
        f"Nenhum perfil de audiência engaja mais: {len(within)} testes (por plataforma, formato e categoria) e 0 significativos. "
        f"A melhor 'persona' (gênero × idade × país) tem índice {persona.iloc[0]['índice']:.1f} com q={persona.iloc[0]['q_value']:.2f}. "
        "Escolha a audiência por objetivo de negócio (quem compra), não por engajamento.")
    return Answer("3. Qual audiência mais engaja?", verdict, overall,
                  {"Por contexto (plataforma, formato, categoria)": within.sort_values("p_value"),
                   "Personas (gênero × idade × país)": persona.head(10)})


# ---------- Q4 ----------

def _belief(name: str, df: pd.DataFrame, x: pd.Series, y: str) -> dict:
    """Test one market belief. Numeric x → Spearman; boolean x → Welch t (effect in % of the False group)."""
    if x.dtype == bool:
        a, b = df.loc[x, y], df.loc[~x, y]
        effect, p = (a.mean() / b.mean() - 1) * 100, stats.ttest_ind(a, b, equal_var=False).pvalue
        unit = "% de diferença"
    else:
        effect, p = stats.spearmanr(x, df[y])
        unit = "ρ de Spearman"
    return {"crença de mercado": name, "métrica": y, "efeito": effect, "unidade": unit, "p_value": 1.0 if np.isnan(p) else p}


def what_does_not_work(df: pd.DataFrame) -> Answer:
    """Q4: common practices/beliefs that the data does NOT support, plus the weakest segments."""
    beliefs = pd.DataFrame([
        _belief("Mais seguidores → mais alcance", df, df["follower_count"], REACH),
        _belief("Mais seguidores → mais engajamento", df, df["follower_count"], ENGAGEMENT),
        _belief("Mais hashtags → mais alcance", df, df["n_hashtags"], REACH),
        _belief("Vídeo engaja mais que imagem/texto", df, df["content_type"] == "video", ENGAGEMENT),
        _belief("Conteúdo curto (<60) engaja mais", df, df["content_length"] < 60, ENGAGEMENT),
        _belief("Postar à noite (18–24h) dá mais alcance", df, df["hour"] >= 18, REACH),
        _belief("Fim de semana dá mais alcance", df, df["weekday"].isin(["Saturday", "Sunday"]), REACH),
        _belief("Patrocínio aumenta alcance", df, df["is_sponsored"].astype(bool), REACH),
        _belief("Disclosure explícito derruba engajamento", df[df.is_sponsored.astype(bool)],
                df.loc[df.is_sponsored.astype(bool), "disclosure_type"] == "explicit", ENGAGEMENT),
        _belief("Legenda longa engaja mais", df, df["caption_words"], ENGAGEMENT),
        _belief("Mais views → mais likes", df, df["views"], "likes"),
    ])
    beliefs["q_value"] = _fdr(beliefs["p_value"])
    beliefs["se sustenta?"] = np.where(beliefs["q_value"] < ALPHA, "sim", "não")

    platforms_weak = []
    for p in PLATFORMS:
        sub = df[df.platform == p]
        scan = segment_scan(sub, ["content_type", "content_category", "follower_tier"], ENGAGEMENT)
        worst = scan.iloc[-1]
        platforms_weak.append({"plataforma": p, "pior segmento (aparente)": worst["segmento"], "índice": worst["índice"],
                               "q_value": worst["q_value"], "significativo": worst["significativo"]})
    weak = pd.DataFrame(platforms_weak)

    failed = beliefs[beliefs["se sustenta?"] == "não"]["crença de mercado"].tolist()
    weak_sig = weak[weak["significativo"]]
    weak_text = ("Segmentos significativamente piores: " + "; ".join(weak_sig["plataforma"] + " → " + weak_sig["pior segmento (aparente)"])
                 if len(weak_sig) else "Nenhum segmento é significativamente pior em nenhuma plataforma")
    verdict = (f"{len(failed)} de {len(beliefs)} crenças comuns não se sustentam nesta base: " + "; ".join(failed) + f". {weak_text}. "
               "Investir para mudar um atributo que não altera o resultado (ex.: pagar mais por seguidores, otimizar horário) não traz retorno nesta base.")
    return Answer("4. O que NÃO funciona?", verdict, beliefs, {"Pior segmento por plataforma": weak})


def answer_all(df: pd.DataFrame) -> list[Answer]:
    return [what_drives_engagement(df), does_sponsorship_work(df), audience_that_engages(df), what_does_not_work(df)]
