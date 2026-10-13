"""OS-09 - validacao da ferramenta.

Blocos:
  A  Recalculo independente da definicao nova (lift contra o resto do recorte)
     para os segmentos simples da base completa. Referencia do item 0.5.1.
  B  Base com efeito conhecido: primeiras 6.000 linhas, likes x 1,3 nos videos.
     Gera o CSV e a referencia de lift/ep por content_type (item 0.5.2).
  C  CSV do template preenchido com as primeiras 2.000 linhas + clicks,
     conversions e cost ficticios (seed 42). Fixture da validacao 2.
  D  Conferencia a mao do simulador: 30 organicos + 10 patrocinados por mes,
     R$ 2.000 por patrocinado, base completa (validacao 3).

As comparacoes com o engine.js ficam no solution/tool/validar_os09.mjs.
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
DATA_PATH = Path(os.environ.get("DATA_PATH", REPO_ROOT / "datasets" / "social_media_dataset.csv"))
SAIDA = REPO_ROOT / "solution" / "outputs" / "os09"
FIXTURES = SAIDA / "fixtures"

METRICAS = ["taxa", "interacoes", "views"]
FAIXA_LIMITES = [50_000, 100_000, 500_000, 1_000_000, np.inf]
FAIXA_LABELS = ["até 50K", "50–100K", "100–500K", "500K–1M", "acima de 1M"]

# fixture do bloco B: so as colunas que o engine le, para o CSV nao ter texto livre
COLS_ENGINE = ["post_date", "platform", "content_type", "content_category",
               "follower_count", "is_sponsored", "views", "likes", "shares",
               "comments_count", "audience_age_distribution",
               "audience_gender_distribution", "audience_location"]

COLS_TEMPLATE = ["post_date", "platform", "content_type", "content_category",
                 "follower_count", "is_sponsored", "views", "likes", "shares",
                 "comments_count", "audience_age_distribution",
                 "audience_gender_distribution", "audience_location", "hashtags",
                 "clicks", "conversions", "cost"]


def faixa_de(s):
    """Mesma regra do engine: primeiro limite >= seguidores."""
    out = np.full(len(s), len(FAIXA_LIMITES) - 1)
    for i in range(len(FAIXA_LIMITES) - 1, -1, -1):
        out[s <= FAIXA_LIMITES[i]] = i
    return [FAIXA_LABELS[i] for i in out]


def preparar(df):
    """Metricas por post e a faixa de seguidores."""
    d = df.copy()
    d["interacoes"] = d["likes"] + d["shares"] + d["comments_count"]
    d["taxa"] = d["interacoes"] / d["views"]
    d["faixa"] = faixa_de(d["follower_count"].to_numpy())
    return d


def indices(d, met):
    """Indice por post: valor / media da metrica na plataforma (normal) e
    valor / media geral do recorte (geral, usado para avaliar a plataforma)."""
    media_plat = d.groupby("platform")[met].transform("mean")
    return d[met] / media_plat, d[met] / d[met].mean()


def lift_ep(idx, dentro):
    """d = media em S - media fora de S; lift = 1 + d; ep = sqrt(dpS²/nS + dpR²/nR)."""
    s = idx[dentro].to_numpy()
    r = idx[~dentro].to_numpy()
    d = s.mean() - r.mean()
    ep = np.sqrt(s.std(ddof=1) ** 2 / len(s) + r.std(ddof=1) ** 2 / len(r))
    return len(s), 1 + d, ep


# as 7 variaveis de segmento simples do engine (desempenho + publico)
VARS = [("plataforma", "platform"), ("formato", "content_type"),
        ("categoria", "content_category"), ("faixa", "faixa"),
        ("idade", "audience_age_distribution"),
        ("genero", "audience_gender_distribution"),
        ("pais", "audience_location")]


def bloco_segmentos(d, vars_=VARS):
    """lift e ep de cada valor de cada variavel, nas 3 metricas."""
    linhas = []
    for met in METRICAS:
        idx_normal, idx_geral = indices(d, met)
        for var_id, col in vars_:
            idx = idx_geral if var_id == "plataforma" else idx_normal
            for valor in sorted(d[col].astype(str).str.strip().unique()):
                dentro = d[col].astype(str).str.strip() == valor
                n, lift, ep = lift_ep(idx, dentro)
                linhas.append({"metrica": met, "variavel": var_id, "segmento": valor,
                               "n": n, "lift": lift, "ep": ep})
    return pd.DataFrame(linhas)


def main():
    SAIDA.mkdir(parents=True, exist_ok=True)
    FIXTURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)
    print(f"Base: {len(df)} linhas ({DATA_PATH})")

    # ------------------------------------------------------------------ bloco A
    d = preparar(df)
    ref_a = bloco_segmentos(d)
    ref_a.to_csv(SAIDA / "a_referencia_lift_ep.csv", index=False)
    print(f"A: {len(ref_a)} linhas segmento x metrica -> a_referencia_lift_ep.csv")

    # ------------------------------------------------------------------ bloco B
    b = df.head(6000).copy()
    video = b["content_type"] == "video"
    b.loc[video, "likes"] = (b.loc[video, "likes"] * 1.3).astype(int)
    print(f"B: 6.000 linhas, {int(video.sum())} videos com likes x 1,3")
    b[COLS_ENGINE].to_csv(FIXTURES / "base_efeito_conhecido.csv", index=False)

    db = preparar(b)
    ref_b = bloco_segmentos(db, [("formato", "content_type")])
    ref_b.to_csv(SAIDA / "b_referencia_efeito_conhecido.csv", index=False)
    print(ref_b[ref_b.metrica == "taxa"][["segmento", "n", "lift", "ep"]].to_string(index=False))

    # ------------------------------------------------------------------ bloco C
    rng = np.random.default_rng(42)
    c = df.head(2000).copy()
    n = len(c)
    pat = c["is_sponsored"].astype(str).str.strip().str.upper() == "TRUE"
    # cliques ~ 1% das views; conversoes ~ 3% dos cliques; custo so no patrocinado
    c["clicks"] = rng.binomial(c["views"].to_numpy().astype(int), 0.01)
    c["conversions"] = rng.binomial(c["clicks"].to_numpy().astype(int), 0.03)
    custo = np.where(pat, rng.integers(500, 5001, size=n), 0)
    c["cost"] = custo
    c["post_date"] = pd.to_datetime(c["post_date"], format="%m/%d/%y %I:%M %p").dt.strftime("%Y-%m-%d %H:%M")
    c[COLS_TEMPLATE].to_csv(FIXTURES / "template_preenchido.csv", index=False)
    print(f"C: 2.000 linhas -> fixtures/template_preenchido.csv "
          f"(clicks {c.clicks.sum()}, conversions {c.conversions.sum()}, "
          f"patrocinados {int(pat.sum())}, custo medio pat. {custo[pat].mean():.2f})")

    # ------------------------------------------------------------------ bloco D
    # medias por post do recorte (base completa) e IC 95% da media
    linhas = []
    for met in ["views", "interacoes"]:
        v = d[met].to_numpy()
        media = v.mean()
        ep = v.std(ddof=1) / np.sqrt(len(v))
        linhas.append({"item": f"media por post - {met}", "valor": media,
                       "ic_lo": media - 1.96 * ep, "ic_hi": media + 1.96 * ep})
    # efeito do patrocinio: media ponderada das diferencas de indice por estrato
    for met in ["views", "interacoes"]:
        idx_normal, _ = indices(d, met)
        dd = d.assign(idx=idx_normal)
        chaves = ["platform", "content_category", "content_type", "faixa"]
        soma_d, soma_var, total = 0.0, 0.0, 0
        estratos = []
        for _, g in dd.groupby(chaves, observed=True):
            p = g[g["is_sponsored"].astype(str).str.strip().str.upper() == "TRUE"]["idx"].to_numpy()
            o = g[g["is_sponsored"].astype(str).str.strip().str.upper() != "TRUE"]["idx"].to_numpy()
            if len(p) >= 30 and len(o) >= 30:
                estratos.append((p, o))
                total += len(p) + len(o)
        for p, o in estratos:
            w = (len(p) + len(o)) / total
            soma_d += w * (p.mean() - o.mean())
            soma_var += w * w * (p.std(ddof=1) ** 2 / len(p) + o.std(ddof=1) ** 2 / len(o))
        efeito, ep_ef = 1 + soma_d, np.sqrt(soma_var)
        media_org = d[d["is_sponsored"].astype(str).str.strip().str.upper() != "TRUE"][met].mean()
        linhas.append({"item": f"efeito patrocinio - {met}", "valor": efeito,
                       "ic_lo": efeito - 1.96 * ep_ef, "ic_hi": efeito + 1.96 * ep_ef})
        linhas.append({"item": f"media organica por post - {met}", "valor": media_org,
                       "ic_lo": np.nan, "ic_hi": np.nan})
        # ganho do patrocinio em 10 posts patrocinados por mes
        ganho = (efeito - 1) * media_org * 10
        linhas.append({"item": f"ganho do patrocinio (10 posts) - {met}", "valor": ganho,
                       "ic_lo": (efeito - 1 - 1.96 * ep_ef) * media_org * 10,
                       "ic_hi": (efeito - 1 + 1.96 * ep_ef) * media_org * 10})
    # cenario: 30 organicos + 10 patrocinados, R$ 2.000 por patrocinado
    for met in ["views", "interacoes"]:
        v = d[met].to_numpy()
        media, ep = v.mean(), v.std(ddof=1) / np.sqrt(len(v))
        linhas.append({"item": f"total no mes (40 posts) - {met}", "valor": 40 * media,
                       "ic_lo": 40 * (media - 1.96 * ep), "ic_hi": 40 * (media + 1.96 * ep)})
    linhas.append({"item": "investimento no mes", "valor": 10 * 2000, "ic_lo": np.nan, "ic_hi": np.nan})
    ref_d = pd.DataFrame(linhas)
    ref_d.to_csv(SAIDA / "d_referencia_simulador.csv", index=False)
    print("D: cenario do simulador -> d_referencia_simulador.csv")
    print(ref_d.to_string(index=False))


if __name__ == "__main__":
    main()
