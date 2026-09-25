"""Detector de gargalos com controle de falso positivo — e a validação dele.

Uma análise ingênua ordena segmentos pela média e chama o pior de "gargalo". Em 80 combinações, o pior sempre parece
alarmante, mesmo em ruído puro. Este detector testa cada segmento contra o resto (teste t de Welch, unilateral) e
corrige para comparações múltiplas (Benjamini-Hochberg): só sinaliza o que sobrevive.

Nota de método: a primeira versão usava p-valores de permutação com 500 sorteios. O menor p possível (1/501) é maior
que o limiar de BH para 149 testes (0,05/149), então um gargalo isolado NUNCA seria detectado — a curva de poder
mostrava 0% até para +12 h. O teste t dá caudas exatas e é adequado aqui (segmentos com n >= 15, variável limitada).

Validação:
  1. Dados reais do Dataset 1 -> quantos gargalos sinaliza (esperado: 0, os tempos são sorteados).
  2. Gargalos injetados de tamanho conhecido -> com que frequência detecta (curva de poder).

Uso: python 02_diagnostico_gargalos.py
Saída: app/data/diagnostico.json
"""
from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

from common import SEED, TICKETS_CSV, save_json

DIMS = ["Ticket Channel", "Ticket Priority", "Ticket Type"]
ALPHA = 0.05


def segment_codes(df, dims):
    """Uma coluna de códigos inteiros por definição de segmento (cada dimensão sozinha, pares e a combinação tripla)."""
    defs = {}
    for k in range(1, len(dims) + 1):
        for combo in combinations(dims, k):
            codes, labels = pd.MultiIndex.from_frame(df[list(combo)]).factorize()
            defs[combo] = (codes, labels)
    return defs


def diagnose(values, defs, higher_is_worse=True, min_n=15):
    """Testa cada segmento contra o restante (Welch, unilateral na direção 'pior'); corrige com BH."""
    values = np.asarray(values, float)
    sign = 1 if higher_is_worse else -1
    n_all, total, total_sq = len(values), values.sum(), (values ** 2).sum()
    rows = []
    for combo, (codes, labels) in defs.items():
        k = len(labels)
        n = np.bincount(codes, minlength=k).astype(float)
        s = np.bincount(codes, weights=values, minlength=k)
        sq = np.bincount(codes, weights=values ** 2, minlength=k)
        n_r, s_r, sq_r = n_all - n, total - s, total_sq - sq
        mean, mean_r = s / n, s_r / n_r
        var, var_r = (sq - n * mean ** 2) / (n - 1), (sq_r - n_r * mean_r ** 2) / (n_r - 1)
        se2 = var / n + var_r / n_r
        t = sign * (mean - mean_r) / np.sqrt(se2)
        dof = se2 ** 2 / ((var / n) ** 2 / (n - 1) + (var_r / n_r) ** 2 / (n_r - 1))
        p = stats.t.sf(t, dof)
        for i, label in enumerate(labels):
            if n[i] < min_n:
                continue
            rows.append({"segmento": " × ".join(map(str, label if isinstance(label, tuple) else (label,))),
                         "dimensoes": len(combo), "n": int(n[i]), "media": mean[i],
                         "diferenca": mean[i] - mean_r[i], "p": p[i]})
    out = pd.DataFrame(rows)
    out["q"] = multipletests(out["p"], method="fdr_bh")[1]
    out["gargalo"] = out["q"] < ALPHA
    return out.sort_values("p")


df = pd.read_csv(TICKETS_CSV)
df = df[df["Ticket Status"] == "Closed"].copy()
df["ttr_h"] = (pd.to_datetime(df["Time to Resolution"]) - pd.to_datetime(df["First Response Time"])).dt.total_seconds() / 3600
defs = segment_codes(df, DIMS)
rng = np.random.default_rng(SEED)

# 1. Dados reais
real_ttr = diagnose(df["ttr_h"], defs)
real_csat = diagnose(df["Customer Satisfaction Rating"], defs, higher_is_worse=False)
naive_worst = real_ttr.sort_values("diferenca", ascending=False).iloc[0]
print(f"Segmentos testados: {len(real_ttr)} | gargalos de tempo sinalizados: {real_ttr['gargalo'].sum()} | "
      f"de satisfação: {real_csat['gargalo'].sum()}")
print(f"Pior segmento pela média (o que a análise ingênua reportaria): {naive_worst['segmento']} "
      f"(+{naive_worst['diferenca']:.1f} h, p = {naive_worst['p']:.3f}, q = {naive_worst['q']:.2f})")

# 2. Curva de poder: injeta +X horas num segmento real de cada tamanho e mede a taxa de detecção
targets = {
    "canal inteiro (~690 tickets)": {"Ticket Channel": "Social media"},
    "canal × prioridade (~170)": {"Ticket Channel": "Social media", "Ticket Priority": "Critical"},
    "canal × prioridade × tipo (~35)": {"Ticket Channel": "Social media", "Ticket Priority": "Critical",
                                        "Ticket Type": "Refund request"},
}
effects = [1, 2, 3, 4, 6, 8, 12]
reps = 100
power = []
for name, target in targets.items():
    mask = np.logical_and.reduce([df[c] == v for c, v in target.items()])
    seg_label = " × ".join(target.values())
    for effect in effects:
        hits = 0
        for _ in range(reps):
            # base = tempos embaralhados (ruído puro) + efeito conhecido no segmento-alvo
            injected = rng.permutation(df["ttr_h"].values) + np.where(mask, effect, 0.0)
            res = diagnose(injected, defs)
            hits += bool(res.loc[res["segmento"] == seg_label, "gargalo"].iloc[0])
        power.append({"alvo": name, "n": int(mask.sum()), "efeito_h": effect, "deteccao": hits / reps})
        print(f"  {name:34s} +{effect:>2} h -> detectado em {hits}/{reps}")

# Falsos alarmes em ruído puro: quantos segmentos o detector sinaliza quando não há efeito nenhum
false_alarms = [diagnose(rng.permutation(df["ttr_h"].values), defs)["gargalo"].sum() for _ in range(reps)]
print(f"Ruído puro ({reps} rodadas): {np.mean(np.array(false_alarms) > 0):.0%} das rodadas com algum alarme; "
      f"média de {np.mean(false_alarms):.2f} segmento(s) sinalizado(s) por rodada")

save_json("diagnostico.json", {
    "segmentos_testados": len(real_ttr),
    "real": {
        "gargalos_tempo": int(real_ttr["gargalo"].sum()), "gargalos_csat": int(real_csat["gargalo"].sum()),
        "top_tempo": real_ttr.head(8).to_dict("records"), "top_csat": real_csat.head(5).to_dict("records"),
        "ingenuo": naive_worst.to_dict(),
    },
    "poder": power,
    "falsos_alarmes_medio": float(np.mean(false_alarms)),
    "rodadas_com_alarme": float(np.mean(np.array(false_alarms) > 0)),
    "desvio_padrao_h": float(df["ttr_h"].std()),
})
