#!/usr/bin/env python3
"""Gera dashboard/index.html a partir de template.html + o CSV do dataset.
Uso: python build_dashboard.py caminho/para/social_media_dataset.csv
Pré-calcula as estatísticas (portão de sinal + médias por segmento) e embute no HTML,
para que o arquivo abra sozinho sem precisar do CSV de 23 MB."""
import json, sys, os
import numpy as np, pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(sys.argv[1])
df["eng"] = (df.likes + df.shares + df.comments_count) / df.views
df["is_sponsored"] = df.is_sponsored.map({True: "patrocinado", False: "orgânico"})
df["creator_tier"] = pd.cut(df.follower_count, [0, 1e4, 5e4, 25e4, 1e12], labels=["<10K", "10K-50K", "50K-250K", ">250K"]).astype(str)
dims = ["platform", "content_type", "content_category", "creator_tier", "is_sponsored"]

def gstats(keys, metric):
    g = df.groupby(keys, observed=True)[metric].agg(["count", "mean", "sem"]).reset_index()
    g["k"] = g[keys].astype(str).agg(" · ".join, axis=1)
    return [{"k": r.k, "n": int(r["count"]), "mean": round(float(r["mean"]), 7), "se": round(float(r["sem"]), 8)} for _, r in g.sort_values("mean", ascending=False).iterrows()]

perf = {}
for m in ["eng", "views", "shares", "comments_count"]:
    perf[m] = {}
    for d in dims:
        perf[m][d] = gstats([d], m)
        if d != "is_sponsored":
            perf[m][d + "|is_sponsored"] = gstats([d, "is_sponsored"], m)

# portão de sinal (mesma lógica do JS, calculada em Python sobre os 52K)
tests = [{"d": d, "p": round(float(stats.kruskal(*[g.eng.values for _, g in df.groupby(d, observed=True)]).pvalue), 4)} for d in dims]
a = df.sample(frac=.5, random_state=1); b = df.drop(a.index)
k = dims[:-1] + ["is_sponsored"]
ca = a.groupby(k, observed=True).eng.mean(); cb = b.groupby(k, observed=True).eng.mean(); idx = ca.index.intersection(cb.index)
gate = {
    "n": int(len(df)), "tests": tests, "sig": int(sum(t["p"] < .05 for t in tests)),
    "splitHalf": round(float(np.corrcoef(ca.loc[idx], cb.loc[idx])[0, 1]), 4),
    "cvViews": round(float(df.views.std() / df.views.mean() * 100), 3),
    "creatorFollowerVariants": round(float(df.groupby("creator_id").follower_count.nunique().mean()), 2),
    "zeroPct": float(((df.likes + df.shares + df.comments_count) == 0).mean() * 100),
    "sponsored": gstats(["is_sponsored"], "eng"),
}
embed = json.dumps({"gate": gate, "perf": perf}, ensure_ascii=False, separators=(",", ":"))
html = open(f"{HERE}/template.html", encoding="utf-8").read().replace("__EMBED__", embed)
open(f"{HERE}/index.html", "w", encoding="utf-8").write(html)
print("ok", len(html) // 1024, "KB")
