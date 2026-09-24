"""
Pontes do Churn para outras ferramentas (PLANEJAMENTO.md, secao 6).

Cada ponte recebe a sessao de origem e o resultado da analise e devolve o que a sub-sessao precisa:
{"nome", "modulo", "tabelas": {tabela: DataFrame}, "descricao"}. As colunas ja saem com os nomes do
contrato do modulo de destino, entao o De/Para da sub-sessao e identidade.
"""

import pandas as pd

from nucleo import leitura
from nucleo.carregar import para_booleano, para_numero, tabelas_da_sessao


def para_suporte(sessao, r):
    """Selo verde, Tipo A: tickets da RavenStack das contas 'precisa de suporte' -> ferramenta de Suporte.

    Regra: conta ativa com score de risco >= 30 E com chamado escalado, resposta lenta ou satisfacao baixa
    (PLANEJAMENTO 4.1). Vao todos os chamados dessas contas (historico completo), para ver onde o
    atendimento delas trava. Sem classificador: esses tickets nao tem texto.
    """
    tabs = tabelas_da_sessao(sessao, leitura.ler)
    if "chamados" not in tabs:
        raise ValueError("A sessão de Churn não tem a tabela de chamados de suporte.")
    contas = r["precisa_suporte"]
    ch = tabs["chamados"]
    ch = ch[ch["id_cliente"].astype(str).isin(contas.index.astype(str))]
    saida = pd.DataFrame({"id_chamado": ch["id_chamado"], "id_cliente": ch["id_cliente"]})
    if "prioridade" in ch:
        saida["prioridade"] = ch["prioridade"]
    if "primeira_resposta_min" in ch:
        saida["tempo_resposta_h"] = (para_numero(ch["primeira_resposta_min"]) / 60).round(2)
    if "resolucao_h" in ch:
        saida["tempo_resolucao_h"] = para_numero(ch["resolucao_h"])
    if "satisfacao" in ch:
        saida["satisfacao"] = para_numero(ch["satisfacao"])
    if "escalado" in ch:
        saida["escalado"] = para_booleano(ch["escalado"])
    # plano da conta faz o papel de "produto" no Suporte (permite comparar Basic x Pro x Enterprise)
    if "plano" in contas:
        saida["produto"] = saida["id_cliente"].astype(str).map(contas["plano"].astype(str).rename(index=str))
    mrr = float(contas["mrr"].sum()) if "mrr" in contas else 0.0
    descricao = (f"Churn '{sessao.get('nome', '')}': {len(contas)} contas em risco com problema de suporte "
                 f"(MRR US$ {mrr:,.0f}/mês) → {len(saida)} chamados delas".replace(",", "."))
    return {"nome": "Contas em risco → Suporte", "modulo": "suporte", "tabelas": {"chamados": saida.reset_index(drop=True)},
            "descricao": descricao}


def para_leads(sessao, r):
    """Selo laranja, Tipo A adaptado: carteira de expansao. Cada conta ativa vira uma 'oportunidade' com valor = MRR.

    O historico sao as proprias contas: ficou = 'ganho', cancelou = 'perdido'. Assim o motor de Leads calcula a
    chance de a conta ficar por plano, setor e porte e ordena por valor esperado (chance x MRR): no topo ficam as
    contas grandes e seguras, as melhores para expansao. Limites: a base nao tem vendedor nem datas de negociacao,
    e o historico inclui as proprias contas ativas.
    """
    m = r["mestra"]
    ids = m.index.astype(str)
    plano = m["plano"].astype(str) if "plano" in m else "Sem plano"
    hist = pd.DataFrame({"id_oportunidade": "H-" + ids, "vendedor": "Sem dono na base", "produto": plano,
                         "conta": ids, "estagio": m["cancelou"].map({True: "Lost", False: "Won"}).values})
    ativos = m[~m["cancelou"]]
    abertos = pd.DataFrame({"id_oportunidade": ativos.index.astype(str), "vendedor": "Sem dono na base",
                            "produto": ativos["plano"].astype(str) if "plano" in ativos else "Sem plano",
                            "conta": ativos.index.astype(str), "estagio": "Ativa",
                            "valor": ativos["mrr"] if "mrr" in ativos else None})
    contas = pd.DataFrame({"conta": ids})
    if "segmento" in m:
        contas["setor"] = m["segmento"].values
    if "assentos" in m:
        contas["funcionarios"] = m["assentos"].values
    descricao = (f"Churn '{sessao.get('nome', '')}': {len(ativos)} contas ativas viram oportunidades de expansão "
                 f"(valor = MRR; 'ganho' = conta ficou, 'perdido' = cancelou; sem vendedor e sem datas na base)")
    return {"nome": "Carteira de expansão (Churn → Leads)", "modulo": "leads",
            "tabelas": {"oportunidades": pd.concat([hist, abertos], ignore_index=True), "contas": contas},
            "descricao": descricao}


def para_midia(sessao, r, base):
    """Selo azul, Tipo B: paises onde o churn esta acima da media -> posts com audiencia desses paises (Midia)."""
    from nucleo.perfis import filtrar, ler_tabela, pais, coluna_bruta
    seg = r["segmentos"].get("pais")
    if not seg:
        raise ValueError("a sessão de Churn não tem o país dos clientes")
    t = seg["tabela"]
    acima = t[t["taxa_%"] > seg["media_%"]]
    posts = ler_tabela(base, "posts")
    existentes = set(posts[coluna_bruta(base, "posts", "audiencia_local")].map(pais))
    alvo = [(pais(g), x) for g, x in zip(acima.grupo, acima["taxa_%"]) if pais(g) in existentes]
    if not alvo:
        raise ValueError("nenhum país com churn acima da média existe na audiência da base de Mídia")
    df = filtrar(posts, base, "posts", {"audiencia_local": ([a for a, _ in alvo], pais)})
    perfil = ", ".join(f"{a} ({x:.0f}%)" for a, x in alvo)
    descricao = (f"Perfil do Churn '{sessao.get('nome', '')}': países com churn acima da média de {seg['media_%']:.0f}% → {perfil} "
                 f"(teste entre países: p = {_d(seg['p_valor'])}). Posts com audiência nesses países: {_n(len(df))}.")
    return {"nome": "Audiência dos países que mais cancelam (Churn → Mídia)", "modulo": "midia", "base": base,
            "brutas": {"posts": df}, "descricao": descricao}


def _n(v):
    return f"{v:,}".replace(",", ".")


def _d(v):
    return f"{v:.2f}".replace(".", ",")
