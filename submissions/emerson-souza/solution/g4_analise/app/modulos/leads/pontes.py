"""Pontes do Leads (PLANEJAMENTO.md, secao 6). Tipo B: perfil de onde mais ganhamos -> onde concentrar conteudo."""

from nucleo.perfis import coluna_bruta, filtrar, ler_tabela, pais


def para_midia(sessao, r, base, top=3):
    """Selo azul, Tipo B: paises onde mais ganhamos (valor ganho) -> posts com audiencia desses paises (Midia)."""
    d = r["deals"]
    if "local" not in d:
        raise ValueError("a sessão de Leads não tem o país das contas")
    g = d[d.ganhou].assign(p=d["local"].map(pais)).groupby("p").valor.sum().sort_values(ascending=False)
    posts = ler_tabela(base, "posts")
    existentes = set(posts[coluna_bruta(base, "posts", "audiencia_local")].map(pais))
    alvo = [x for x in g.index if x in existentes][:top]
    if not alvo:
        raise ValueError("nenhum país onde ganhamos existe na audiência da base de Mídia")
    df = filtrar(posts, base, "posts", {"audiencia_local": (alvo, pais)})
    total = g.sum()
    perfil = ", ".join(f"{x} ({100 * g[x] / total:.0f}% do valor ganho)" for x in alvo)
    setor = ""
    if "setor" in d:
        s = d[d.ganhou].groupby("setor").valor.sum().sort_values(ascending=False)
        if len(s):
            setor = f" Setor com mais valor ganho: {s.index[0]}."
    descricao = (f"Perfil do Leads '{sessao.get('nome', '')}': países onde mais ganhamos → {perfil}.{setor} "
                 f"Posts com audiência nesses países: {_n(len(df))}.")
    return {"nome": "Audiência dos países onde mais vendemos (Leads → Mídia)", "modulo": "midia", "base": base,
            "brutas": {"posts": df}, "descricao": descricao}


def _n(v):
    return f"{v:,}".replace(",", ".")


def _d(v):
    return f"{v:.2f}".replace(".", ",")
