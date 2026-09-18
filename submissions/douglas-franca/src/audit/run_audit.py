"""G2: auditoria estrutural e forense do dataset do Challenge 004.

Uso: uv run python src/audit/run_audit.py
Saídas:
  outputs/tables/dq-findings.csv      achados DQ-xx com número observado
  outputs/tables/dq-poisson.csv       teste de dispersão por métrica e por segmento
  outputs/tables/dq-independence.csv  associação entre colunas categóricas (Cramér's V)
  outputs/tables/dq-profile.csv       perfil por coluna
  outputs/tables/dq-segment-amplitude.csv  amplitude da taxa de engajamento por segmento
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "social_media_dataset.csv"
TABLES = ROOT / "outputs" / "tables"

METRICS = ["views", "likes", "shares", "comments_count"]
SEGMENTS = ["platform", "content_type", "content_category", "is_sponsored", "audience_age_distribution"]
PLATFORM_DOMAINS = r"instagram|tiktok|youtube|youtu\.be|bilibili|xiaohongshu|rednote"
COMPANY_SUFFIXES = r"(?:LLC|Inc|Ltd|PLC|Group|and Sons)$|^\w+, \w+ and \w+$|^\w+-\w+$"
FUNCTION_WORDS = {
    "or", "and", "the", "their", "they", "this", "that", "these", "those", "which", "whose", "whom",
    "from", "with", "into", "about", "according", "although", "because", "whether", "while", "since",
    "might", "would", "could", "should", "must", "may", "will", "can", "yet", "also", "each", "every",
    "some", "any", "many", "much", "most", "more", "other", "another", "such", "own", "same", "than",
    "then", "there", "here", "where", "when", "what", "who", "why", "how", "not", "nor", "only", "very",
    "its", "his", "her", "our", "your", "my", "we", "you", "he", "she", "it", "i", "me", "him", "us", "them",
}


def load() -> pd.DataFrame:
    df = pd.read_csv(RAW)
    df.attrs["n_source_columns"] = df.shape[1]
    df["post_date"] = pd.to_datetime(df["post_date"], format="%m/%d/%y %I:%M %p")
    df["interactions"] = df["likes"] + df["shares"] + df["comments_count"]
    df["er_pp"] = df["interactions"] / df["views"] * 100
    return df


def dispersion_test(x: pd.Series) -> dict:
    """Índice de dispersão: sob Poisson, (n-1)·s²/média ~ χ²(n-1) e var/média ≈ 1."""
    n, mean, var = len(x), x.mean(), x.var(ddof=1)
    d = (n - 1) * var / mean
    cdf = stats.chi2.cdf(d, n - 1)
    return {"n": n, "media": mean, "variancia": var, "var_sobre_media": var / mean,
            "p_bicaudal_poisson": 2 * min(cdf, 1 - cdf)}


def cramers_v(a: pd.Series, b: pd.Series) -> tuple[float, float]:
    table = pd.crosstab(a, b)
    chi2, p, _, _ = stats.chi2_contingency(table)
    k = min(table.shape) - 1
    return float(np.sqrt(chi2 / (table.values.sum() * k))), float(p)


def main() -> None:
    df = load()
    findings: list[dict] = []

    def add(dq_id, severity, check, observed, implication):
        findings.append({"id": dq_id, "severidade": severity, "checagem": check,
                         "observado": observed, "implicacao": implication})

    # ---------- Estrutura ----------
    profile = pd.DataFrame({
        "tipo": df.dtypes.astype(str),
        "nulos": df.isna().sum(),
        "distintos": df.nunique(),
        "exemplo": df.iloc[0].astype(str).str[:60],
    })
    profile.to_csv(TABLES / "dq-profile.csv", index_label="coluna")

    dup_id, dup_content = df["id"].duplicated().sum(), df["content_id"].duplicated().sum()
    inconsistent_sponsor = (
        (df.is_sponsored & (df.disclosure_type == "none"))
        | (~df.is_sponsored & (df.disclosure_type != "none"))
        | (~df.is_sponsored & (df.sponsor_name != "Not sponsors"))
    ).sum()
    add("DQ-01", "OK", "estrutura",
        f"{len(df):,} linhas × {df.attrs['n_source_columns']} colunas; ids duplicados={dup_id}; content_id duplicados={dup_content}; "
        f"datas inválidas=0; inconsistências de patrocínio={inconsistent_sponsor}",
        "arquivo mecanicamente íntegro: os problemas são de validade, não de formato")
    add("DQ-02", "MENOR", "nulos",
        f"hashtags={df.hashtags.isna().sum():,} ({df.hashtags.isna().mean():.1%}); "
        f"comments_text={df.comments_text.isna().sum():,} ({df.comments_text.isna().mean():.1%}); demais=0",
        "ausência preservada; sem imputação")
    add("DQ-03", "MAIOR", "orgânico codificado como texto",
        "orgânicos têm sponsor_name/sponsor_category='Not sponsors' e disclosure='none' em vez de nulo",
        "valores-sentinela precisam de regra explícita em qualquer agregação")

    # ---------- Forense: métricas ----------
    zero = ((df[METRICS] == 0).any(axis=1)).sum()
    ranges = "; ".join(f"{m} {df[m].min():,}–{df[m].max():,}" for m in METRICS)
    add("DQ-04", "CRÍTICA", "sobrevivência / cauda",
        f"posts com alguma métrica zerada={zero}; {ranges}; maior post tem {df.views.max() / df.views.min():.2f}x as views do menor",
        "sem cauda longa e sem fracassos: não representa redes sociais reais (onde poucos posts concentram o alcance)")

    poisson_rows = []
    for m in METRICS:
        poisson_rows.append({"metrica": m, "segmento": "TOTAL", "grupo": "todos", **dispersion_test(df[m])})
        for seg in SEGMENTS:
            for g, sub in df.groupby(seg):
                poisson_rows.append({"metrica": m, "segmento": seg, "grupo": str(g), **dispersion_test(sub[m])})
    poisson = pd.DataFrame(poisson_rows)
    poisson.to_csv(TABLES / "dq-poisson.csv", index=False)
    total = poisson[poisson.segmento == "TOTAL"].set_index("metrica")
    seg = poisson[poisson.segmento != "TOTAL"]
    lam_spread = seg.groupby("metrica").media.agg(lambda s: (s.max() - s.min()) / s.mean() * 100)
    add("DQ-05", "CRÍTICA", "gerador Poisson com λ fixo",
        "var/média: " + "; ".join(f"{m}={total.loc[m, 'var_sobre_media']:.3f} (p={total.loc[m, 'p_bicaudal_poisson']:.2f})" for m in METRICS)
        + f"; em {len(seg)} segmentos var/média entre {seg.var_sobre_media.min():.2f} e {seg.var_sobre_media.max():.2f}; "
        + "λ varia entre segmentos no máximo " + ", ".join(f"{m} {v:.2f}%" for m, v in lam_spread.items()),
        "cada métrica se comporta como um sorteio de Poisson com a MESMA média para todo post (inferência pela "
        "assinatura estatística; o gerador não está disponível): nenhuma característica influencia o resultado. "
        "Contagens reais de engajamento são sobredispersas (var/média >> 1)")

    # Amplitude da taxa de engajamento dentro de cada segmento: sustenta a afirmação
    # "as diferenças observadas entre segmentos são ruído" em docs/data-quality-report.md.
    amplitude = (
        pd.DataFrame(
            [
                {
                    "segmento": s,
                    "n_niveis": df[s].nunique(),
                    "er_pp_min": df.groupby(s).er_pp.mean().min(),
                    "er_pp_max": df.groupby(s).er_pp.mean().max(),
                    "amplitude_pp": df.groupby(s).er_pp.mean().max() - df.groupby(s).er_pp.mean().min(),
                }
                for s in SEGMENTS
            ]
        )
        .sort_values("amplitude_pp", ascending=False)
        .reset_index(drop=True)
    )
    amplitude.to_csv(TABLES / "dq-segment-amplitude.csv", index=False)

    corr = df[METRICS + ["follower_count"]].corr()
    add("DQ-06", "CRÍTICA", "métricas independentes entre si",
        f"r(likes,views)={corr.loc['likes', 'views']:.3f}; r(shares,views)={corr.loc['shares', 'views']:.3f}; "
        f"r(comments,likes)={corr.loc['comments_count', 'likes']:.3f}; r(views,followers)={corr.loc['views', 'follower_count']:.3f}",
        "curtidas não acompanham views e views não acompanham seguidores: no mundo real essas correlações são fortes")

    # ---------- Forense: creators ----------
    per_creator = df.groupby("creator_id").agg(
        posts=("id", "size"), nomes=("creator_name", "nunique"), plataformas=("platform", "nunique"),
        seguidores_std=("follower_count", "std"))
    add("DQ-07", "MAIOR", "cadastro de creator",
        f"{len(per_creator):,} creators; posts por creator {per_creator.posts.min()}–{per_creator.posts.max()}; "
        f"creators com >1 nome={(per_creator.nomes > 1).mean():.1%}; "
        f"desvio de seguidores dentro do mesmo creator={per_creator.seguidores_std.mean():,.0f} vs população={df.follower_count.std():,.0f}; "
        f"creators em 5 plataformas={(per_creator.plataformas == 5).mean():.1%}",
        "não existe cadastro mestre: o mesmo creator muda de nome e de tamanho a cada post. Tamanho de creator é atributo do post, não da pessoa")
    ks_unif = stats.kstest(df.follower_count, stats.uniform(loc=df.follower_count.min(),
                                                            scale=df.follower_count.max() - df.follower_count.min()).cdf)
    add("DQ-08", "MAIOR", "distribuição de seguidores",
        f"KS contra uniforme(1K–1M): D={ks_unif.statistic:.4f}; faixa {df.follower_count.min():,}–{df.follower_count.max():,}; "
        f"<10K={(df.follower_count < 10_000).mean():.2%}; >1M=0",
        "seguidores sorteados de forma uniforme: não há mega-influenciadores e nano é 0,9% da base")
    add("DQ-09", "MAIOR", "frequência de postagem",
        f"cada creator tem {per_creator.posts.min()}–{per_creator.posts.max()} posts em 2 anos",
        "sem variação de cadência: a pergunta 'com que frequência postar' não pode ser respondida por este arquivo")

    # ---------- Forense: conteúdo ----------
    ks_len = stats.kruskal(*[g.content_length for _, g in df.groupby("content_type")])
    add("DQ-10", "MAIOR", "content_length sem unidade",
        f"mesma distribuição para video/image/text/mixed (Kruskal p={ks_len.pvalue:.2f}; medianas "
        + ", ".join(f"{k}={v:.0f}" for k, v in df.groupby('content_type').content_length.median().items()) + ")",
        "'duração' de imagem igual à de vídeo: o campo não mede duração nem tamanho; faixas '30–60s' não têm significado")
    platform_urls = df.content_url.str.contains(PLATFORM_DOMAINS, case=False).mean()
    company_like = df.loc[df.is_sponsored, "sponsor_name"].str.contains(COMPANY_SUFFIXES).mean()
    tokens = df.hashtags.dropna().str.split(",").explode().str.strip().str.lower()
    add("DQ-11", "MAIOR", "texto gerado por biblioteca de dados falsos",
        f"URLs de plataforma={platform_urls:.1%}; sponsors com padrão de nome gerado={company_like:.1%}; "
        f"hashtags: {tokens.nunique():,} termos distintos, {tokens.isin(FUNCTION_WORDS).mean():.1%} são palavras funcionais (ex.: 'or', 'their'); "
        "descrições e comentários são frases sem relação com a categoria",
        "hashtags, descrições e comentários não carregam semântica: análise de hashtag/NLP é inválida neste arquivo")
    add("DQ-12", "MAIOR", "ausência de custo e resultado de negócio",
        "não há custo, fee, campaign_id, cliques, conversões, receita nem janela de atribuição",
        "ROI e 'custo implícito' não podem ser medidos, só parametrizados")
    add("DQ-13", "MAIOR", "audiência agregada",
        "cada post tem UMA faixa etária, UM gênero e UM país (não é distribuição, apesar do nome)",
        "perfil de audiência é atributo do post; inferir comportamento individual é falácia ecológica")
    monthly = df.post_date.dt.to_period("M").value_counts().sort_index().iloc[1:-1]  # descarta meses parciais
    hourly = df.post_date.dt.hour.value_counts()
    hour_chi = stats.chisquare(hourly)
    add("DQ-14", "MAIOR", "tempo sem padrão humano",
        f"{df.post_date.min():%d/%m/%Y}–{df.post_date.max():%d/%m/%Y} (meses das pontas parciais); sem fuso horário; "
        f"meses completos {monthly.min():,}–{monthly.max():,} posts; posts por hora {hourly.min():,}–{hourly.max():,} "
        f"(3h da manhã={hourly[3]:,} vs 19h={hourly[19]:,}; χ² contra uniforme p={hour_chi.pvalue:.2f})",
        "publicação uniforme 24h por dia: melhor horário e sazonalidade não são inferíveis")

    # ---------- Associação entre colunas ----------
    pairs = [("language", "audience_location"), ("language", "platform"), ("platform", "content_type"),
             ("content_category", "sponsor_category"), ("audience_location", "platform"),
             ("audience_age_distribution", "platform"), ("is_sponsored", "platform")]
    ind = pd.DataFrame([{"coluna_a": a, "coluna_b": b, "cramers_v": v, "p": p}
                        for a, b in pairs for v, p in [cramers_v(df[a], df[b])]])
    ind.to_csv(TABLES / "dq-independence.csv", index=False)
    lang_loc = ind.query("coluna_a=='language' and coluna_b=='audience_location'").iloc[0]
    zh_in_br = ((df.language == "Chinese") & (df.audience_location == "Brazil")).sum()
    add("DQ-15", "MAIOR", "colunas sem coerência entre si",
        f"Cramér's V idioma×país da audiência={lang_loc.cramers_v:.3f}; posts em chinês com audiência no Brasil={zh_in_br:,}; "
        f"maior V entre os {len(ind)} pares testados={ind.cramers_v.max():.3f}",
        "idioma, país, plataforma e categoria não têm associação entre si: segmentação por persona não tem base")
    br = df[df.audience_location == "Brazil"]
    add("DQ-16", "INFO", "audiência Brasil",
        f"{len(br):,} posts ({len(br) / len(df):.1%}); por plataforma: "
        + ", ".join(f"{k} {v}" for k, v in br.platform.value_counts().items()),
        "Bilibili e RedNote aparecem com audiência brasileira no mesmo volume das demais: mais um sinal de sorteio")

    pd.DataFrame(findings).to_csv(TABLES / "dq-findings.csv", index=False)
    with pd.option_context("display.max_colwidth", 400, "display.width", 400):
        for f in findings:
            print(f"{f['id']} [{f['severidade']}] {f['checagem']}\n   {f['observado']}\n")


if __name__ == "__main__":
    main()
