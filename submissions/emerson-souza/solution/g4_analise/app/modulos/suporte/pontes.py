"""
Pontes do Suporte para outras ferramentas (PLANEJAMENTO.md, secao 6).

Suporte -> Churn (amarelo, Tipo A): quem pediu cancelamento vira "cancelou" e a ferramenta de Churn mostra o que
diferencia esses clientes (produto, idade, genero, satisfacao). Sem receita na base: valores = contagem.
Suporte -> Leads (amarelo, lista): tickets "Product inquiry" viram lista de oportunidades para o CRM. Nao vira
sessao de Leads porque a base de suporte nao tem vendas ganhas/perdidas para o score aprender.
"""

import pandas as pd

from nucleo.carregar import para_numero

PEDIDO_CANCELAMENTO = ("cancellation request", "pedido de cancelamento", "cancelamento")
PERGUNTA_PRODUTO = ("product inquiry", "pergunta sobre produto", "dúvida sobre produto")


def _ultimo_por_cliente(c, col):
    return c.groupby("id_cliente")[col].agg(lambda s: s.dropna().iloc[-1] if s.notna().any() else None)


def para_churn(sessao, r):
    c = r["chamados"]
    if "id_cliente" not in c or "tipo" not in c:
        raise ValueError("a sessão precisa do cliente (e-mail/ID) e do tipo do chamado no De/Para")
    c = c.dropna(subset=["id_cliente"]).copy()
    c["id_cliente"] = c["id_cliente"].astype(str)
    pediu = c["tipo"].astype(str).str.lower().isin(PEDIDO_CANCELAMENTO)
    cli = pd.DataFrame({"id_cliente": sorted(c["id_cliente"].unique())}).set_index("id_cliente")
    cli["cancelou"] = c.assign(p=pediu).groupby("id_cliente")["p"].any()
    for col in ("produto", "idade", "genero"):
        if col in c:
            cli[col] = _ultimo_por_cliente(c, col)
    clientes = cli.reset_index()
    tabs = {"clientes": clientes}
    ch = pd.DataFrame({"id_chamado": c["id_chamado"], "id_cliente": c["id_cliente"]})
    for col in ("prioridade", "satisfacao", "escalado"):
        if col in c:
            ch[col] = c[col]
    if "resposta_h" in c:
        ch["primeira_resposta_min"] = (para_numero(c["resposta_h"]) * 60).round(1)
    tabs["chamados"] = ch.reset_index(drop=True)
    if "assunto" in c:
        tabs["cancelamentos"] = c.loc[pediu, ["id_cliente", "assunto"]].rename(columns={"assunto": "motivo"}).reset_index(drop=True)
    n = int(clientes.cancelou.sum())
    descricao = (f"Suporte '{sessao.get('nome', '')}': {len(clientes):,} clientes; {n:,} pediram cancelamento "
                 "('cancelou' = abriu pedido de cancelamento; motivo = assunto do chamado; sem receita na base)").replace(",", ".")
    return {"nome": "Quem pede cancelamento (Suporte → Churn)", "modulo": "churn", "tabelas": tabs, "descricao": descricao}


def para_leads(sessao, r):
    """Lista (nao sessao): tickets de pergunta sobre produto = oportunidades de venda para o CRM."""
    c = r["chamados"]
    if "tipo" not in c:
        raise ValueError("a sessão precisa do tipo do chamado no De/Para")
    sel = c[c["tipo"].astype(str).str.lower().isin(PERGUNTA_PRODUTO)]
    cols = [x for x in ("id_chamado", "id_cliente", "produto", "assunto", "prioridade", "canal", "status", "idade", "genero") if x in sel]
    lista = sel[cols].copy()
    if "prioridade" in lista:
        ordem = {"critical": 0, "urgent": 0, "high": 1, "medium": 2, "low": 3}
        lista = lista.assign(_o=lista["prioridade"].astype(str).str.lower().map(ordem).fillna(9)).sort_values("_o").drop(columns="_o")
    return {"tipo": "lista", "df": lista.reset_index(drop=True), "arquivo": "oportunidades_de_venda_suporte.csv",
            "resumo": f"{len(lista):,}".replace(",", ".") + " tickets de pergunta sobre produto, da maior para a menor prioridade."}


IDADE_PARA_MIDIA = {"até 25": ["13-18", "19-25"], "26-35": ["26-35"], "36-50": ["36-50"], "51-65": ["50+"], "66+": ["50+"]}
GENERO_PARA_MIDIA = {"male": ["male"], "masculino": ["male"], "female": ["female"], "feminino": ["female"],
                     "other": ["non-binary", "unknown"], "outro": ["non-binary", "unknown"]}


def para_midia(sessao, r, base):
    """Selo azul, Tipo B: faixa de idade e genero com a PIOR satisfacao -> posts com essa audiencia (Midia)."""
    from nucleo.perfis import filtrar, ler_tabela
    c = r["chamados"]
    if "satisfacao" not in c or c.satisfacao.notna().sum() < 20:
        raise ValueError("a sessão de Suporte não tem satisfação suficiente para montar o perfil")
    filtros, partes = {}, []
    if "faixa_idade" in c:
        m = c.groupby("faixa_idade").satisfacao.mean().dropna()
        pior = m.idxmin()
        if pior in IDADE_PARA_MIDIA:
            filtros["audiencia_idade"] = (IDADE_PARA_MIDIA[pior], None)
            partes.append(f"idade {pior} (satisfação {m.min():.2f})".replace(".", ","))
    if "genero" in c:
        m = c.groupby("genero").satisfacao.mean().dropna()
        pior = str(m.idxmin())
        if pior.lower() in GENERO_PARA_MIDIA:
            filtros["audiencia_genero"] = (GENERO_PARA_MIDIA[pior.lower()], None)
            partes.append(f"gênero {pior} (satisfação {m.min():.2f})".replace(".", ","))
    if not filtros:
        raise ValueError("a sessão de Suporte não tem idade nem gênero dos clientes")
    df = filtrar(ler_tabela(base, "posts"), base, "posts", filtros)
    if df.empty:
        raise ValueError("nenhum post da base de Mídia tem essa audiência")
    sat = r["satisfacao"]
    teste = ("; nenhuma variável tem diferença comprovada de satisfação" if sat is not None and (sat["tabela"].p_valor >= 0.05).all() else "")
    descricao = (f"Perfil do Suporte '{sessao.get('nome', '')}': quem dá a pior nota → " + " e ".join(partes) + teste
                 + f". Posts com essa audiência: {len(df):,}.".replace(",", "."))
    return {"nome": "Audiência de quem mais reclama (Suporte → Mídia)", "modulo": "midia", "base": base,
            "brutas": {"posts": df}, "descricao": descricao}
