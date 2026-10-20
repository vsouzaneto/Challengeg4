"""Audits that do not depend on finding engagement effects: disclosure compliance, sponsor fit, market coherence,
content length in its real unit (per format) and statistical power per subgroup.

Rules (which disclosure is risky, which sponsor fits which niche, which language/platform reaches which country)
are explicit, editable constants: they encode market knowledge, not something learned from this dataset.
"""
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from .focus import mde_correlation, mde_two_groups
from .questions import ALPHA, DIMENSIONS, ENGAGEMENT, REACH, STRATA, Answer, stratified_difference

# ---------- rules (edit with legal / market input) ----------

# Every market below requires ads to be identifiable as ads; "implicit" disclosure fails that test everywhere.
AD_RULES = {
    "USA": "FTC Endorsement Guides", "UK": "CAP Code (ASA) / CMA", "Germany": "UWG §5a",
    "India": "ASCI Influencer Guidelines", "China": "Lei de Publicidade (art. 14)", "Japan": "Lei de prêmios (stealth marketing, 2023)",
    "Brazil": "CONAR (Guia de publicidade por influenciadores)", "Russia": "Lei Federal de Publicidade (marcação)",
}
# Disclosure only inside the video is missed by viewers who scroll the feed without sound or read only the text.
RISK_LEVELS = {"implicit": "alto", "explicit_video": "médio", "explicit_text": "baixo"}
AD_MARKERS = {"ad", "ads", "advertising", "sponsored", "sponsor", "partner", "paidpartnership", "paid", "publi", "werbung"}

SPONSOR_FIT = {
    "beauty": {"cosmetics", "fashion"},
    "lifestyle": {"food", "travel", "fashion"},
    "tech": {"electronics", "gaming"},
}

MARKET_LANGUAGES = {
    "USA": {"English", "Spanish"}, "UK": {"English"}, "China": {"Chinese"}, "India": {"Hindi", "English"},
    "Japan": {"Japanese"}, "Brazil": {"Portuguese"}, "Germany": {"German"}, "Russia": {"Russian"},
}
# Platforms blocked or banned in the market (2024 status).
UNAVAILABLE_PLATFORMS = {"China": {"Instagram", "YouTube", "TikTok"}, "India": {"TikTok"}, "Russia": {"Instagram"}}

# Each format has its own unit; image/mixed have no natural "length".
LENGTH_UNIT = {"video": "segundos", "text": "palavras"}
LENGTH_BINS_BY_FORMAT = {
    "video": {"curto (<60 s)": 60, "médio (60–180 s)": 180, "longo (180–360 s)": 360, "muito longo (360+ s)": np.inf},
    "text": {"curto (<100 palavras)": 100, "médio (100–300)": 300, "longo (300+)": np.inf},
}

RELEVANT_EFFECT = 0.05  # smallest effect (5% of the mean) the business would act on
POWER_DIMENSIONS = DIMENSIONS + ["language", "audience_gender_distribution", "audience_age_distribution", "audience_location"]


def _fdr(pvalues) -> np.ndarray:
    return multipletests(pvalues, method="fdr_bh")[1] if len(pvalues) else np.array([])


def _share(mask: pd.Series) -> float:
    return round(100 * mask.mean(), 1)


# ---------- 1. disclosure compliance ----------

def has_ad_marker(df: pd.DataFrame) -> pd.Series:
    """True when hashtags or caption contain an ad label (#ad, #sponsored, ...): disclosure a reader can see."""
    tags = df["hashtags"].fillna("").str.lower().str.split(",").map(lambda t: {x.strip().lstrip("#") for x in t})
    words = df["content_description"].fillna("").str.lower().str.findall(r"#?\w+").map(lambda w: {x.lstrip("#") for x in w})
    return pd.Series([bool(AD_MARKERS & (t | w)) for t, w in zip(tags, words)], index=df.index)


def disclosure_risk(df: pd.DataFrame) -> pd.Series:
    """Risk level per sponsored post (NaN for organic)."""
    explicit_text = (df["disclosure_type"] == "explicit") & df["disclosure_location"].isin(["caption", "hashtags"])
    explicit_video = (df["disclosure_type"] == "explicit") & (df["disclosure_location"] == "video")
    risk = np.select([df["disclosure_type"] == "implicit", explicit_video, explicit_text],
                     [RISK_LEVELS["implicit"], RISK_LEVELS["explicit_video"], RISK_LEVELS["explicit_text"]], default=None)
    return pd.Series(risk, index=df.index).where(df["is_sponsored"].astype(bool))


def disclosure_audit(df: pd.DataFrame) -> Answer:
    """How many sponsored posts carry regulatory risk, where, and whether the label is visible in the text."""
    sp = df[df["is_sponsored"].astype(bool)].assign(risco=lambda d: disclosure_risk(d), marcador=lambda d: has_ad_marker(d))
    by_market = (sp.groupby("audience_location")
                 .agg(posts=("risco", "size"), alto=("risco", lambda r: _share(r == "alto")),
                      médio=("risco", lambda r: _share(r == "médio")), baixo=("risco", lambda r: _share(r == "baixo")),
                      verificável=("marcador", _share))
                 .rename(columns={"alto": "% risco alto", "médio": "% risco médio", "baixo": "% risco baixo",
                                  "verificável": "% com rótulo no texto"}))
    by_market.insert(0, "norma", by_market.index.map(AD_RULES))
    by_platform = pd.crosstab(sp["platform"], sp["risco"], normalize="index").mul(100).round(1)
    label_check = (sp.groupby("disclosure_location")["marcador"].mean().mul(100).round(2).to_frame("% com rótulo no texto"))
    label_check.loc["orgânicos (referência)"] = round(100 * has_ad_marker(df[~df["is_sponsored"].astype(bool)]).mean(), 2)

    rows = []
    for col in ["disclosure_type", "disclosure_location"]:
        groups = [g[ENGAGEMENT].to_numpy() for _, g in sp.groupby(col) if len(g) > 1]
        p = stats.kruskal(*groups).pvalue if len(groups) > 1 else np.nan
        means = sp.groupby(col)[ENGAGEMENT].mean()
        rows.append({"comparação": col, "melhor": means.idxmax(), "pior": means.idxmin(),
                     "diferença melhor−pior (%)": 100 * (means.max() / means.min() - 1), "p_value": p})
    cost = pd.DataFrame(rows)
    cost["q_value"] = _fdr(cost["p_value"])
    cost["significativo"] = cost["q_value"] < ALPHA

    high, verifiable = _share(sp["risco"] == "alto"), _share(sp["marcador"])
    medium = _share(sp["risco"] == "médio")
    any_cost = cost["significativo"].any()
    verdict = (f"{high}% dos posts patrocinados usam disclosure implícito (risco alto em todos os {len(AD_RULES)} mercados) "
               f"e {medium}% divulgam só dentro do vídeo (risco médio). "
               f"Só {verifiable}% têm um rótulo de publicidade visível no texto, então o rótulo da base não pode ser auditado. "
               + ("O tipo ou local do disclosure muda o engajamento: ver tabela." if any_cost else
                  "Tipo e local do disclosure não mudam o engajamento, então exigir disclosure explícito no texto não tem custo de desempenho."))
    return Answer("Auditoria de disclosure (compliance)", verdict, by_market.sort_values("% risco alto", ascending=False),
                  {"Risco por plataforma (%)": by_platform, "Rótulo visível no texto × local declarado": label_check,
                   "Disclosure × engajamento": cost})


# ---------- 2. sponsor × niche fit ----------

def sponsor_fits(df: pd.DataFrame) -> pd.Series:
    """True when the sponsor's industry matches the creator's content niche (organic → NaN)."""
    fit = [s in SPONSOR_FIT.get(c, set()) for c, s in zip(df["content_category"], df["sponsor_category"])]
    return pd.Series(fit, index=df.index).where(df["is_sponsored"].astype(bool))


def sponsor_fit(df: pd.DataFrame) -> Answer:
    """Share of sponsorships inside the creator's niche and whether in-niche ones perform better (same strata)."""
    sp = df[df["is_sponsored"].astype(bool)].copy()
    sp["no nicho"] = sponsor_fits(sp).astype(bool)
    mix = pd.crosstab(sp["content_category"], sp["sponsor_category"], normalize="index").mul(100).round(1)
    by_sponsor = sp.groupby("sponsor_category")["no nicho"].mean().mul(100).round(1).to_frame("% no nicho")
    rows = []
    for metric in [ENGAGEMENT, REACH]:
        r = stratified_difference(sp, sp["no nicho"], metric, STRATA)
        rows.append({"métrica": metric, **r})
    effect = pd.DataFrame(rows).set_index("métrica")
    effect["q_value"] = _fdr(effect["p_value"])
    effect["significativo"] = effect["q_value"] < ALPHA

    in_niche = _share(sp["no nicho"])
    works = effect["significativo"].any() and (effect.loc[effect["significativo"], "diferença"] > 0).all()
    verdict = (f"Só {in_niche}% dos patrocínios estão no nicho do creator (ex.: cosmetics em beauty). "
               + ("Os patrocínios no nicho rendem mais no mesmo estrato: priorizar fit na seleção de creators." if works else
                  "No mesmo estrato, patrocínio no nicho não rende mais nem menos neste dataset: fit é critério de marca, não de desempenho, até haver dados reais."))
    return Answer("Fit patrocinador × nicho", verdict, effect, {"Mix nicho × patrocinador (%)": mix, "% no nicho por patrocinador": by_sponsor})


# ---------- 3. market coherence ----------

def market_coherence_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Per post: does the content language match the audience market, and is the platform available there?"""
    lang_ok = [lang in MARKET_LANGUAGES.get(m, set()) for lang, m in zip(df["language"], df["audience_location"])]
    plat_ok = [p not in UNAVAILABLE_PLATFORMS.get(m, set()) for p, m in zip(df["platform"], df["audience_location"])]
    out = pd.DataFrame({"idioma do mercado": lang_ok, "plataforma disponível": plat_ok}, index=df.index)
    out["coerente"] = out.all(axis=1)
    return out


def market_coherence(df: pd.DataFrame) -> Answer:
    """Share of posts aimed at a market in a language it does not speak or on a platform it cannot open."""
    flags = market_coherence_flags(df)
    d = df.join(flags)
    by_market = (d.groupby("audience_location")
                 .agg(posts=("coerente", "size"), idioma=("idioma do mercado", _share),
                      plataforma=("plataforma disponível", _share), coerente=("coerente", _share))
                 .rename(columns={"idioma": "% no idioma do mercado", "plataforma": "% em plataforma disponível",
                                  "coerente": "% coerente"}))
    by_market["idiomas do mercado no dataset"] = [", ".join(sorted(MARKET_LANGUAGES[m] & set(df["language"]))) or "nenhum"
                                                  for m in by_market.index]
    blocked = (d.loc[~d["plataforma disponível"]].groupby(["audience_location", "platform"]).size()
               .rename("posts").reset_index().sort_values("posts", ascending=False))
    rows = []
    for metric in [ENGAGEMENT, REACH]:
        a, b = d.loc[d["coerente"], metric], d.loc[~d["coerente"], metric]
        rows.append({"métrica": metric, "coerentes": a.mean(), "incoerentes": b.mean(),
                     "diferença (%)": 100 * (a.mean() / b.mean() - 1), "p_value": stats.ttest_ind(a, b, equal_var=False).pvalue})
    effect = pd.DataFrame(rows).set_index("métrica")
    effect["q_value"] = _fdr(effect["p_value"])
    effect["significativo"] = effect["q_value"] < ALPHA

    no_lang = [m for m in by_market.index if by_market.loc[m, "idiomas do mercado no dataset"] == "nenhum"]
    verdict = (f"Só {_share(flags['coerente'])}% dos posts falam o idioma do mercado da audiência e estão numa plataforma disponível lá. "
               f"{_share(~flags['plataforma disponível'])}% miram um mercado onde a plataforma é bloqueada (ex.: Instagram/YouTube na China). "
               f"{len(no_lang)} de {len(by_market)} mercados ({', '.join(no_lang)}) não têm nenhum post no próprio idioma. "
               + ("Posts coerentes rendem diferente: ver tabela." if effect["significativo"].any() else
                  "Coerência não muda o resultado aqui, o que confirma que audiência e conteúdo foram sorteados de forma independente. Use como checagem de qualidade dos dados reais."))
    return Answer("Coerência idioma × mercado × plataforma", verdict, by_market, {"Plataformas bloqueadas no mercado": blocked,
                                                                               "Coerentes × incoerentes": effect})


# ---------- 4. content length in its own unit ----------

def length_by_format(df: pd.DataFrame, metrics: tuple[str, ...] = (REACH, ENGAGEMENT)) -> Answer:
    """Length vs. results only where length means something (video = seconds, text = words), with MDE."""
    dist = df.groupby("content_type")["content_length"].describe()[["count", "min", "50%", "max"]]
    dist["unidade"] = dist.index.map(lambda f: LENGTH_UNIT.get(f, "indefinida"))
    corr_rows, bin_tables = [], {}
    for fmt, edges in LENGTH_BINS_BY_FORMAT.items():
        sub = df[df["content_type"] == fmt]
        bins = pd.cut(sub["content_length"], [-np.inf, *edges.values()], labels=list(edges), right=False)
        for m in metrics:
            rho, p = stats.spearmanr(sub["content_length"], sub[m])
            corr_rows.append({"formato": fmt, "unidade": LENGTH_UNIT[fmt], "métrica": m, "n": len(sub), "ρ": rho,
                              "MDE de ρ": mde_correlation(len(sub)), "p_value": p})
        table = sub.groupby(bins, observed=True)[list(metrics)].mean()
        bin_tables[f"{fmt} por faixa ({LENGTH_UNIT[fmt]})"] = (table / sub[list(metrics)].mean() * 100).round(2).add_suffix(" (índice)")
    corr = pd.DataFrame(corr_rows)
    corr["q_value"] = _fdr(corr["p_value"])
    corr["significativo"] = corr["q_value"] < ALPHA

    undefined = df["content_type"].isin(set(df["content_type"]) - set(LENGTH_UNIT))
    found = corr[corr["significativo"]]
    verdict = (f"{_share(undefined)}% dos posts (imagem e misto) têm 'duração' sem unidade definida, e eles ficam fora da análise. "
               "Separando vídeo (segundos) e texto (palavras), "
               + (f"o tamanho importa em: {', '.join(found['formato'] + '·' + found['métrica'])}." if len(found) else
                  f"o tamanho não muda views nem engajamento (|ρ| ≤ {corr['ρ'].abs().max():.3f}; detectaríamos |ρ| ≥ {corr['MDE de ρ'].max():.3f}). "
                  "A crença 'conteúdo curto engaja mais' foi testada antes misturando segundos e palavras e deve usar esta versão."))
    return Answer("Duração por formato (unidade correta)", verdict, corr, {"Distribuição por formato": dist, **bin_tables})


# ---------- 5. power per subgroup ----------

def subgroup_power(df: pd.DataFrame, metrics: tuple[str, ...] = (ENGAGEMENT, REACH),
                   dims: list[str] = POWER_DIMENSIONS, relevant: float = RELEVANT_EFFECT) -> Answer:
    """For each value of each dimension vs. the rest: observed difference and the smallest one we could detect (% of mean)."""
    rows = []
    for dim in dims:
        for value, mask in ((v, df[dim] == v) for v in df[dim].dropna().unique()):
            n1, n2 = int(mask.sum()), int((~mask).sum())
            if n1 < 2 or n2 < 2:
                continue
            for m in metrics:
                mean = df[m].mean()
                rows.append({"dimensão": dim, "valor": str(value), "métrica": m, "n": n1,
                             "diferença observada (%)": 100 * (df.loc[mask, m].mean() - df.loc[~mask, m].mean()) / mean,
                             "MDE (%)": 100 * mde_two_groups(df[m].std(), n1, n2) / mean})
    table = pd.DataFrame(rows)
    table["conclusivo"] = table["MDE (%)"] < 100 * relevant
    table = table.sort_values("MDE (%)", ascending=False).reset_index(drop=True)
    weakest = table.iloc[0]
    inconclusive = table[~table["conclusivo"]]
    verdict = (f"Para todo subgrupo, mostramos o menor efeito que daria para ver (MDE, 80% de poder). "
               f"O mais fraco é {weakest['dimensão']} = {weakest['valor']} (n = {weakest['n']:,}), com MDE de {weakest['MDE (%)']:.2f}% em {weakest['métrica']}. "
               + (f"{len(inconclusive)} comparações não conseguem ver um efeito de {100 * relevant:.0f}%, então 'equivalente' nelas significa 'sem dados suficientes'."
                  if len(inconclusive) else
                  f"Todas detectariam um efeito de {100 * relevant:.0f}%, então 'equivalente' aqui quer dizer 'sem diferença relevante', não 'sem dados'."))
    return Answer("Poder estatístico por subgrupo", verdict, table)


def audit_all(df: pd.DataFrame) -> list[Answer]:
    return [disclosure_audit(df), sponsor_fit(df), market_coherence(df), length_by_format(df), subgroup_power(df)]
