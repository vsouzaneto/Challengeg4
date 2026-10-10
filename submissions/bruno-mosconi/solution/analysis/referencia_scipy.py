"""Valores de referência do scipy para as funções estatísticas escritas à mão em TypeScript (D23).

Lê as entradas que `npm run auditoria` grava em saidas/estatistica-entradas.json e grava
../src/core/scipy-reference.json, que o teste src/core/stats.scipy.test.ts compara com tolerância.

Rodar: .venv/bin/python -I referencia_scipy.py
"""

import json
from pathlib import Path

import numpy as np
import scipy
from scipy import stats

AQUI = Path(__file__).resolve().parent
ENTRADAS = AQUI / "saidas" / "estatistica-entradas.json"
SAIDA = AQUI.parent / "src" / "core" / "scipy-reference.json"
SEMENTE = 20171231
SORTEIOS = 10_000

e = json.loads(ENTRADAS.read_text())
rng = np.random.default_rng(SEMENTE)

chi2_grid = [{"x": x, "df": df, "sf": float(stats.chi2.sf(x, df))} for x, df in e["chi2Grid"]]

tabelas = {}
for nome, tabela in e["tables"].items():
    t = np.array(tabela, dtype=float)
    t = t[t.sum(axis=1) > 0]
    t = t[:, t.sum(axis=0) > 0]
    r = stats.chi2_contingency(t, correction=False)
    tabelas[nome] = {"table": tabela, "statistic": float(r.statistic), "df": int(r.dof), "p": float(r.pvalue)}

wilson = []
for k, n in e["wilson"]:
    ci = stats.binomtest(k, n).proportion_ci(confidence_level=0.95, method="wilson")
    wilson.append({"k": k, "n": n, "low": float(ci.low), "high": float(ci.high)})

spearman = {
    nome: {"x": x, "y": y, "rho": float(stats.spearmanr(x, y).statistic)}
    for nome, (x, y) in e["spearman"].items()
}

# Embaralhamento: as observações trocam de grupo, como no TS (desfecho embaralhado, grupo fixo).
grupo = np.array(e["permutation"]["group"])
y = np.array(e["permutation"]["y"], dtype=float)
amostras = [y[grupo == g] for g in range(grupo.max() + 1)]


def amplitude(*xs):
    taxas = [x.mean() for x in xs if len(x)]
    return max(taxas) - min(taxas)


perm = stats.permutation_test(
    amostras, amplitude, permutation_type="independent", alternative="greater",
    n_resamples=SORTEIOS, vectorized=False, rng=rng,
)
permutacao = {
    "observed": float(perm.statistic),
    "shareAtLeast": float(perm.pvalue),
    "ours": e["permutation"]["ours"],
}

pareados = {}
for nome, caso in e["paired"].items():
    us = caso["units"]
    a = np.array([u["a"] for u in us], dtype=float)
    b = np.array([u["b"] for u in us], dtype=float)
    den = np.array([u["den"] for u in us], dtype=float)
    total = den.sum()
    idx = np.arange(len(us))

    def diferenca(i):
        i = i.astype(int)
        return (a[i].sum() - b[i].sum()) / den[i].sum()

    boot = stats.bootstrap(
        (idx,), diferenca, vectorized=False, n_resamples=SORTEIOS,
        confidence_level=0.95, method="percentile", rng=rng,
    )
    sinais = stats.permutation_test(
        (a, b), lambda x, y: (x.sum() - y.sum()) / total, permutation_type="samples",
        alternative="two-sided", n_resamples=SORTEIOS, vectorized=False, rng=rng,
    )
    pareados[nome] = {
        "units": us,
        "difference": float((a.sum() - b.sum()) / total),
        "ci95": [float(boot.confidence_interval.low), float(boot.confidence_interval.high)],
        "pSignFlip": float(sinais.pvalue),
        "ours": caso["ours"],
    }

SAIDA.write_text(json.dumps({
    "scipy": scipy.__version__,
    "seed": SEMENTE,
    "resamples": SORTEIOS,
    "chi2Sf": chi2_grid,
    "chiSquare": tabelas,
    "wilson": wilson,
    "spearman": spearman,
    "permutation": permutacao,
    "paired": pareados,
}, indent=1))
print(f"gravado {SAIDA}")
