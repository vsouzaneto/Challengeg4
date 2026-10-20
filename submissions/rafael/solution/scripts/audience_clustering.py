"""Segmentação de audiência com clustering — versão em arquivo da aba "Agrupamento de audiência" do site.

Roda o mesmo agrupamento do site (social_insights.audience_segments) para a base inteira e para cada plataforma,
e grava a tabela de grupos e a lista de perfis.

Uso: python solution/scripts/audience_clustering.py data/raw/social_media_dataset.csv docs
"""
import sys
from pathlib import Path

import pandas as pd

from social_insights import audience_segments, data

RELIABILITY = {"consistente": "consistentes", "fraco": "fracos (só passam em um teste)", "nao_sustenta": "não se sustentam"}


def describe(r: dict) -> list[dict]:
    rows = []
    for g in r["grupos"]:
        more = [f"{c['campo']}={c['valor']} ({c['lift']:+.0%})" for c in g["consumo"][:3] if c["lift"] > 0.02]
        t = g["traco"]
        rows.append({"grupo": "ABCDEF"[g["grupo"]], "perfis": g["perfis"], "posts": f"{g['share_posts']:.0%}",
                     "traço do público": f"{t['campo'].removeprefix('audience_')}={t['valor']} ({t['lift']:+.0%})" if t else "—",
                     "consome mais": ", ".join(more) or "—"})
    return rows


def main(csv: str, outdir: str) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    df = data.add_features(pd.read_csv(csv))
    sections, profiles = [], []
    for name, filtros in [("Todas as plataformas", {})] + [(p, {"platform": p}) for p in data.PLATFORMS]:
        r = audience_segments.segment(df, filtros)
        if "erro" in r:
            sections.append(f"## {name}\n\n{r['erro']}\n")
            continue
        profiles.append(pd.DataFrame(r["mapa"]).drop(columns=["x", "y"]).assign(recorte=name))
        sections.append(f"""## {name}

{r['perfis']} perfis, {r['k']} grupos — **{RELIABILITY[r['confiabilidade']]}**
(separação {r['silhouette']:.2f} vs. acaso até {r['acaso_p95']:.2f}; estabilidade {r['estabilidade']:.2f}).

{pd.DataFrame(describe(r)).to_markdown(index=False)}
""")
    pd.concat(profiles).to_csv(out / "audience_segments.csv", index=False)
    (out / "segmentacao-audiencia.md").write_text(
        "# Segmentação de audiência com clustering\n\nGerado por `solution/scripts/audience_clustering.py` "
        "(mesmo cálculo da aba *Agrupamento de audiência* do site).\n\n" + "\n".join(sections))
    print("\n".join(s.splitlines()[0] + " · " + s.splitlines()[2] for s in sections if "grupos" in s))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
