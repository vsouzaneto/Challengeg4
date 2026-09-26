"""
signal_check.py — "Isso é sinal ou é ruído?"

Ferramenta recorrente para o time de social media. Roda sobre qualquer export
com o mesmo esquema do dataset (platform, content_type, content_category,
follower_count, is_sponsored, views, likes, shares, comments_count, post_date).

Para cada dimensão (plataforma, formato, categoria, faixa de creator, patrocínio)
ela responde três perguntas antes de alguém tomar decisão:
  1. O efeito é estatisticamente distinguível de zero? (IC 95%, correção de Bonferroni)
  2. Ele se repete em outro período? (metade antiga vs. metade recente dos dados)
  3. Ele é grande o bastante para importar? (lift mínimo relevante, padrão 5%)
Só vira recomendação o que passa nos três.

Uso:
  python signal_check.py social_media_dataset.csv [--min-lift 5]
"""
import argparse
import sys

import numpy as np
import pandas as pd
from scipy import stats

DIMS = ["platform", "content_type", "content_category", "creator_tier", "is_sponsored"]
TIERS = [0, 10e3, 50e3, 100e3, 500e3, np.inf]
TIER_LABELS = ["<10K", "10-50K", "50-100K", "100-500K", "500K+"]


def load(path):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["post_date"], format="%m/%d/%y %I:%M %p", errors="coerce")
    df["engagement"] = df["likes"] + df["shares"] + df["comments_count"]
    df["er"] = df["engagement"] / df["views"].clip(lower=1)
    df["creator_tier"] = pd.cut(df["follower_count"], TIERS, labels=TIER_LABELS)
    return df


def health(df):
    """Checagens de sanidade: dados de redes sociais reais NÃO se parecem com isto."""
    out = []
    cv = df["views"].std() / df["views"].mean()
    out.append(("Dispersão de views (CV)", f"{cv:.3f}", "OK" if cv > 0.5 else "ALERTA: views quase constantes (real costuma ter CV > 1)"))
    rho = stats.spearmanr(df["views"], df["follower_count"]).statistic
    out.append(("Correlação views × seguidores", f"{rho:.3f}", "OK" if rho > 0.2 else "ALERTA: alcance não depende de audiência"))
    rho2 = stats.spearmanr(df["views"], df["likes"]).statistic
    out.append(("Correlação views × likes", f"{rho2:.3f}", "OK" if rho2 > 0.3 else "ALERTA: likes não dependem de views"))
    zero = (df["engagement"] == 0).mean()
    out.append(("Posts com engajamento zero", f"{zero:.1%}", "OK" if zero > 0 else "ALERTA: nenhum post fracassou (improvável)"))
    fol_var = df.groupby("creator_id")["follower_count"].nunique().median()
    out.append(("Seguidores distintos por creator (mediana)", f"{fol_var:.0f}", "OK" if fol_var <= 2 else "ALERTA: seguidores mudam a cada post do mesmo creator"))
    return pd.DataFrame(out, columns=["check", "valor", "status"])


def lifts(df, dim):
    base = df["er"].mean()
    g = df.groupby(dim, observed=True)["er"].agg(["mean", "std", "count"])
    g["lift_%"] = (g["mean"] / base - 1) * 100
    g["ic95_%"] = 1.96 * g["std"] / np.sqrt(g["count"]) / base * 100
    return g


def check(df, min_lift):
    df = df.dropna(subset=["date"]).sort_values("date")
    half = df["date"].iloc[len(df) // 2]
    old, new = df[df["date"] < half], df[df["date"] >= half]
    n_tests = sum(df[d].nunique() for d in DIMS)
    z_bonf = stats.norm.ppf(1 - 0.025 / n_tests)
    rows = []
    for dim in DIMS:
        full, a, b = lifts(df, dim), lifts(old, dim), lifts(new, dim)
        for lvl, r in full.iterrows():
            z = abs(r["lift_%"]) / (r["ic95_%"] / 1.96) if r["ic95_%"] > 0 else 0
            signif = z > z_bonf
            same_sign = np.sign(a.loc[lvl, "lift_%"]) == np.sign(b.loc[lvl, "lift_%"]) if lvl in a.index and lvl in b.index else False
            big = abs(r["lift_%"]) >= min_lift
            verdict = "SINAL" if (signif and same_sign and big) else ("pequeno demais" if signif and same_sign else "RUÍDO")
            rows.append((dim, lvl, int(r["count"]), round(r["lift_%"], 2), round(r["ic95_%"], 2),
                         round(a.loc[lvl, "lift_%"], 2) if lvl in a.index else None,
                         round(b.loc[lvl, "lift_%"], 2) if lvl in b.index else None, verdict))
    return pd.DataFrame(rows, columns=["dimensao", "nivel", "posts", "lift_ER_%", "±IC95_%", "lift_1a_metade", "lift_2a_metade", "veredito"])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--min-lift", type=float, default=5.0, help="lift mínimo (%%) para ser relevante ao negócio")
    args = p.parse_args()
    df = load(args.csv)
    pd.set_option("display.width", 200)
    print("\n== SAÚDE DOS DADOS ==")
    h = health(df)
    print(h.to_string(index=False))
    print("\n== SEGMENTOS: SINAL OU RUÍDO? (métrica: engajamento / views) ==")
    r = check(df, args.min_lift)
    print(r.to_string(index=False))
    n_sig = (r["veredito"] == "SINAL").sum()
    alerts = h["status"].str.startswith("ALERTA").sum()
    print(f"\nResumo: {n_sig} de {len(r)} segmentos com sinal acionável; {alerts} alertas de saúde dos dados.")
    if alerts:
        print("Não tome decisões de alocação com base neste arquivo antes de resolver os alertas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
