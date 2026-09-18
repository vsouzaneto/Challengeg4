"""G8: o veredito de equivalência resiste às críticas de método?

Responde a três objeções da crítica adversarial (process-log/critique/):
1. O erro-padrão de `compare()` supõe posts independentes, mas cada creator tem vários posts.
   → correlação intraclasse (ICC) da taxa de engajamento por creator e o efeito de desenho.
2. O TOST usa IC 90% individual, sem correção para múltiplos testes.
   → maior limite |diferença| + z·SE com Bonferroni para todas as comparações com veredito.
3. A régua de ±1 p.p. foi escolhida pelo Douglas.
   → menor régua com a qual todas as comparações continuariam equivalentes.

Uso: uv run python src/analysis/robustness.py   (depois de run_inference.py)
Saída: outputs/tables/inf-robustness.csv
"""

import sys
from pathlib import Path

import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src import app_data  # noqa: E402

TABLES = ROOT / "outputs" / "tables"
SCOPE = ["Instagram", "TikTok", "YouTube"]
FAMILIES = {
    "fatores": "inf-factors.csv",
    "patrocinio_condicoes": "inf-sponsorship-conditions.csv",
    "patrocinio_celulas": "inf-sponsorship-cells.csv",
    "hashtags": "inf-hashtags.csv",
    "audiencia": "inf-audience-cells.csv",
}


def icc_by_creator(df: pd.DataFrame) -> tuple[float, float, int, float]:
    """ICC(1) por ANOVA de um fator; efeito de desenho = 1 + (k̄ − 1)·ICC."""
    g = df.groupby("creator_id", observed=True).er
    k, n = g.size(), len(df)
    a = len(k)
    msb = (k * (g.mean() - df.er.mean()) ** 2).sum() / (a - 1)
    msw = ((df.er - g.transform("mean")) ** 2).sum() / (n - a)
    k0 = (n - (k ** 2).sum() / n) / (a - 1)
    icc = (msb - msw) / (msb + (k0 - 1) * msw)
    return icc, 1 + (k.mean() - 1) * icc, a, k.mean()


def main() -> None:
    posts = app_data.load_posts()
    icc, deff, n_creators, posts_per_creator = icc_by_creator(posts[posts.platform.isin(SCOPE)])

    tables = pd.concat([pd.read_csv(TABLES / f).assign(familia=fam) for fam, f in FAMILIES.items()])
    # + 2 comparações fora destas tabelas, ambas com veredito: seguidores (regressão) e patrocínio ajustado
    # (este já usa erro-padrão agrupado por creator). Total: as 332 comparações da taxa de engajamento.
    m = len(tables) + 2
    z90, z_bonf = stats.norm.ppf(0.95), stats.norm.ppf(1 - 0.05 / m)
    tables["limite_tost_90"] = tables.diferenca_pp.abs() + z90 * tables.se
    tables["limite_bonferroni"] = tables.diferenca_pp.abs() + z_bonf * tables.se

    rows = [
        {"checagem": "creators no escopo", "valor": n_creators},
        {"checagem": "posts por creator (média)", "valor": round(posts_per_creator, 2)},
        {"checagem": "ICC da taxa de engajamento por creator", "valor": round(icc, 5)},
        {"checagem": "efeito de desenho (1 = agrupamento não muda o erro-padrão)", "valor": round(deff, 4)},
        {"checagem": "comparações da taxa de engajamento com veredito", "valor": m},
        {"checagem": "z do TOST com Bonferroni", "valor": round(z_bonf, 3)},
    ]
    for fam, t in tables.groupby("familia", sort=False):
        rows.append({"checagem": f"{fam}: maior limite TOST 90% (p.p.)", "valor": round(t.limite_tost_90.max(), 3)})
        rows.append({"checagem": f"{fam}: maior limite com Bonferroni (p.p.)", "valor": round(t.limite_bonferroni.max(), 3)})
    rows += [
        {"checagem": "todas: maior limite TOST 90% = menor régua que mantém tudo equivalente (p.p.)",
         "valor": round(tables.limite_tost_90.max(), 3)},
        {"checagem": "todas: maior limite com Bonferroni (p.p.)", "valor": round(tables.limite_bonferroni.max(), 3)},
        {"checagem": "todas continuam equivalentes a ±1 p.p. com Bonferroni",
         "valor": bool(tables.limite_bonferroni.max() < 1.0)},
    ]
    out = pd.DataFrame(rows)
    out.to_csv(TABLES / "inf-robustness.csv", index=False)
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
