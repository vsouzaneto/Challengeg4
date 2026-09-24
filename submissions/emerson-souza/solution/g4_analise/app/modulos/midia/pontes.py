"""Pontes da Midia (PLANEJAMENTO.md, secao 6). Tipo B: audiencia que mais engaja -> deals dessas regioes (Leads)."""

from nucleo.perfis import coluna_bruta, filtrar, ler_tabela, pais


def para_leads(sessao, r, base, top=3):
    """Selo azul, Tipo B: paises da audiencia que mais engaja -> so os deals de contas desses paises (Leads)."""
    drv = r["drivers"].get("audiencia_local")
    if not drv:
        raise ValueError("a sessão de Mídia não tem o local da audiência")
    if "contas" not in base["arquivos"]:
        raise ValueError("a base de Leads escolhida não tem a tabela de contas (com o país)")
    contas = ler_tabela(base, "contas")
    col_local = coluna_bruta(base, "contas", "local")
    ranking = [pais(x) for x in drv["tabela"].grupo]   # ja vem do maior para o menor engajamento
    existentes = set(contas[col_local].map(pais))
    alvo = [x for x in ranking if x in existentes][:top]
    if not alvo:
        raise ValueError("nenhum país da audiência existe nas contas da base de Leads")
    nomes = set(contas.loc[contas[col_local].map(pais).isin(alvo), coluna_bruta(base, "contas", "conta")].astype(str))
    op = ler_tabela(base, "oportunidades")
    df = filtrar(op, base, "oportunidades", {"conta": (nomes, str)})
    if df.empty:
        raise ValueError("nenhum deal de contas desses países")
    descricao = (f"Perfil da Mídia '{sessao.get('nome', '')}': países cuja audiência mais engaja → {', '.join(alvo)} "
                 f"(diferença entre países: p = {_d(drv['p_valor'])}; {drv['veredito']}). Deals de contas nesses países: {_n(len(df))}.")
    return {"nome": "Deals nos países da audiência que engaja (Mídia → Leads)", "modulo": "leads", "base": base,
            "brutas": {"oportunidades": df}, "descricao": descricao}


def _n(v):
    return f"{v:,}".replace(",", ".")


def _d(v):
    return f"{v:.2f}".replace(".", ",")
