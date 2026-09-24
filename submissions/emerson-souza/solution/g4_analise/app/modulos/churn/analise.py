"""
Modulo Churn (desafio 001) - motor de analise, sem tela.

Regras: PLANEJAMENTO.md secao 4.1. Padrao de entrega: secao 4.5.
Tudo o que aparece na tela e no relatorio sai daqui, calculado sobre os dados da sessao.
"""

from dataclasses import dataclass, field, asdict

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from nucleo.carregar import para_booleano, para_data, para_numero

SINAIS = {
    "queda_uso": "Queda de uso",
    "erros_beta": "Erros em funcionalidade beta",
    "escalado": "Chamado escalado",
    "resposta_lenta": "1ª resposta lenta",
    "satisfacao_baixa": "Satisfação baixa",
    "downgrade": "Downgrade de plano",
    "segmento": "Segmento de risco",
}

NIVEL_EVIDENCIA = {"forte": 0, "fraca (indício)": 1, "regra de negócio (ver teste dos sinais)": 2,
                   "motivo declarado pelos clientes": 2, "sem evidência": 4, "sem evidência estatística": 4}

DIMENSOES = {"segmento": "Segmento / indústria", "canal_aquisicao": "Canal de aquisição",
             "pais": "País", "plano": "Plano", "em_teste": "Em período de teste", "faixa_assentos": "Faixa de assentos",
             "produto": "Produto", "faixa_idade": "Faixa de idade", "genero": "Gênero"}


@dataclass
class Premissas:
    janela_dias: int = 90            # uso recente x anterior (dias antes da data de referencia)
    queda_pct: float = 30.0          # queda de uso que dispara o alerta
    limite_resposta_min: float | None = None   # None = percentil 75 da propria base
    satisfacao_baixa: float = 3.0    # nota <= este valor conta como baixa
    taxa_recuperacao_pct: float = 20.0         # % do MRR em risco que as acoes conseguem salvar (premissa)
    pesos_pelos_dados: bool = True   # regra 4.1: so pontua sinal que mostrou diferenca nos dados (p < 0,10)
    pesos: dict = field(default_factory=lambda: {
        "queda_uso": 20, "erros_beta": 15, "escalado": 15, "resposta_lenta": 10,
        "satisfacao_baixa": 10, "downgrade": 10, "segmento": 20})

    def chave(self):
        d = asdict(self)
        d["pesos"] = tuple(sorted(d["pesos"].items()))
        return tuple(sorted(d.items()))


# ---------------------------------------------------------------- utilidades estatisticas

def wilson(k, n, z=1.96):
    """Intervalo de confianca de 95% para uma proporcao (funciona bem com n pequeno)."""
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    margem = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centro - margem), min(1.0, centro + margem))


def p_valor_tabela(x, y):
    tabela = pd.crosstab(x, y)
    if tabela.shape[0] < 2 or tabela.shape[1] < 2:
        return np.nan
    if tabela.shape == (2, 2) and (tabela.values < 5).any():
        return stats.fisher_exact(tabela.values)[1]
    return stats.chi2_contingency(tabela)[1]


# ---------------------------------------------------------------- preparacao

def preparar(tabs, p: Premissas):
    """Tabela mestra: 1 linha por cliente com valor, sinais e perfil. Sinais medidos ANTES da data de referencia."""
    cli = tabs["clientes"].copy()
    cli["id_cliente"] = cli["id_cliente"].astype(str)
    cli["cancelou"] = para_booleano(cli["cancelou"])
    if "em_teste" in cli:
        cli["em_teste"] = para_booleano(cli["em_teste"]).map({True: "Sim", False: "Não"})
    if "assentos" in cli:
        assentos = para_numero(cli["assentos"])
        cli["faixa_assentos"] = pd.cut(assentos, [0, 5, 10, 25, 50, np.inf],
                                       labels=["1-5", "6-10", "11-25", "26-50", "51+"]).astype(str)
    if "idade" in cli:
        cli["faixa_idade"] = pd.cut(para_numero(cli["idade"]), [0, 25, 35, 50, 65, 200],
                                    labels=["até 25", "26-35", "36-50", "51-65", "66+"]).astype(str)

    con = tabs.get("contratos")
    sem_receita = con is None
    if con is not None:
        con = con.copy()
        con["id_cliente"] = con["id_cliente"].astype(str)
        con["receita_mensal"] = para_numero(con["receita_mensal"])
        for c in ("inicio", "fim"):
            if c in con:
                con[c] = para_data(con[c])

    canc = tabs.get("cancelamentos")
    if canc is not None:
        canc = canc.copy()
        canc["id_cliente"] = canc["id_cliente"].astype(str)
        canc["data"] = para_data(canc["data"]) if "data" in canc else pd.NaT

    datas = ([con[c].max() for c in ("inicio", "fim") if c in con] if con is not None else []) \
        + ([canc["data"].max()] if canc is not None else [])
    uso = tabs.get("uso") if con is not None else None   # uso liga ao cliente pelo contrato
    cham = tabs.get("chamados")
    if uso is not None:
        uso = uso.copy()
        uso["data"] = para_data(uso["data"])
        datas.append(uso["data"].max())
    if cham is not None and "abertura" in cham:
        cham = cham.copy()
        cham["abertura"] = para_data(cham["abertura"])
        datas.append(cham["abertura"].max())
    validas = [d for d in datas if pd.notna(d)]
    fim_base = max(validas) if validas else pd.Timestamp.today().normalize()

    m = cli.drop_duplicates("id_cliente").set_index("id_cliente")
    if con is not None:
        # valor: receita da ULTIMA assinatura de cada cliente (sem somar assinaturas repetidas)
        ordem = "inicio" if "inicio" in con else None
        ultima = (con.sort_values(ordem) if ordem else con).groupby("id_cliente").tail(1).set_index("id_cliente")
        m["mrr"] = ultima["receita_mensal"].reindex(m.index)
    else:
        m["mrr"] = 1.0   # sem receita: cada cliente vale 1 (os "valores" viram contagem de clientes)

    # motivo e data: ULTIMO evento de cancelamento
    if canc is not None:
        ult_ev = canc.sort_values("data").groupby("id_cliente").tail(1).set_index("id_cliente")
        m["motivo"] = ult_ev["motivo"].reindex(m.index) if "motivo" in ult_ev else np.nan
        m["data_cancelamento"] = ult_ev["data"].reindex(m.index)
    else:
        m["motivo"] = np.nan
        m["data_cancelamento"] = pd.NaT
    m.loc[~m["cancelou"], ["motivo", "data_cancelamento"]] = np.nan

    # data de referencia: cancelada -> data do cancelamento; ativa (ou sem data) -> fim da base
    m["ref"] = m["data_cancelamento"].where(m["cancelou"]).fillna(fim_base)
    ref = m["ref"]
    j = pd.Timedelta(days=p.janela_dias)

    disponiveis = {"downgrade": con is not None and "downgrade" in con,
                   "segmento": any(d in m for d in ("segmento", "canal_aquisicao"))}
    # -------- uso
    if uso is not None:
        uso["quantidade"] = para_numero(uso["quantidade"]).fillna(0)
        uso["id_contrato"] = uso["id_contrato"].astype(str)
        ligacao = con[["id_contrato", "id_cliente"]].astype(str).drop_duplicates("id_contrato")
        uso = uso.merge(ligacao, on="id_contrato", how="inner")
        uso["dias"] = (uso["id_cliente"].map(ref) - uso["data"]).dt.days
        recente = uso[(uso.dias >= 0) & (uso.dias < p.janela_dias)].groupby("id_cliente")["quantidade"].sum()
        anterior = uso[(uso.dias >= p.janela_dias) & (uso.dias < 2 * p.janela_dias)].groupby("id_cliente")["quantidade"].sum()
        m["uso_recente"] = recente.reindex(m.index).fillna(0)
        m["uso_anterior"] = anterior.reindex(m.index).fillna(0)
        m["variacao_uso_pct"] = np.where(m.uso_anterior > 0, 100 * (m.uso_recente - m.uso_anterior) / m.uso_anterior, np.nan)
        m["queda_uso"] = m["variacao_uso_pct"] <= -p.queda_pct
        disponiveis["queda_uso"] = True
        if "erros" in uso and "e_beta" in uso:
            uso["erros"] = para_numero(uso["erros"]).fillna(0)
            uso["e_beta"] = para_booleano(uso["e_beta"])
            obs = uso[(uso.dias >= 0) & (uso.dias < 2 * p.janela_dias) & uso.e_beta]
            m["erros_beta_qtd"] = obs.groupby("id_cliente")["erros"].sum().reindex(m.index).fillna(0)
            m["erros_beta"] = m["erros_beta_qtd"] > 0
            disponiveis["erros_beta"] = True
    # -------- chamados
    limite = p.limite_resposta_min
    if cham is not None:
        cham["id_cliente"] = cham["id_cliente"].astype(str)
        if "abertura" in cham:
            cham["dias"] = (cham["id_cliente"].map(ref) - cham["abertura"]).dt.days
            obs = cham[(cham.dias >= 0) & (cham.dias < 2 * p.janela_dias)]
        else:
            obs = cham
        g = obs.groupby("id_cliente")
        m["chamados_periodo"] = g.size().reindex(m.index).fillna(0)
        if "escalado" in cham:
            m["escalado"] = g["escalado"].apply(lambda s: para_booleano(s).any()).reindex(m.index).fillna(False).astype(bool)
            disponiveis["escalado"] = True
        if "primeira_resposta_min" in cham:
            frt = para_numero(cham["primeira_resposta_min"])
            if limite is None:
                limite = float(frt.quantile(0.75))
            media = obs.assign(f=para_numero(obs["primeira_resposta_min"])).groupby("id_cliente")["f"].mean()
            m["resposta_media_min"] = media.reindex(m.index)
            m["resposta_lenta"] = m["resposta_media_min"] > limite
            disponiveis["resposta_lenta"] = True
        if "satisfacao" in cham:
            sat = obs.assign(s=para_numero(obs["satisfacao"])).groupby("id_cliente")["s"].min()
            m["satisfacao_min"] = sat.reindex(m.index)
            m["satisfacao_baixa"] = m["satisfacao_min"] <= p.satisfacao_baixa
            disponiveis["satisfacao_baixa"] = True
    # -------- downgrade
    if disponiveis["downgrade"]:
        c2 = con.assign(d=para_booleano(con["downgrade"]))
        if "inicio" in c2:
            c2["dias"] = (c2["id_cliente"].map(ref) - c2["inicio"]).dt.days
            c2 = c2[(c2.dias >= 0) & (c2.dias < 2 * p.janela_dias)]
        m["downgrade"] = c2.groupby("id_cliente")["d"].any().reindex(m.index).fillna(False).astype(bool)

    for s in SINAIS:
        if s != "segmento" and s in m:
            m[s] = m[s].fillna(False).astype(bool)
    return m, {"fim_base": fim_base, "limite_resposta_min": limite, "disponiveis": disponiveis, "sem_receita": sem_receita}


# ---------------------------------------------------------------- analises

def numeros_base(m):
    total = len(m)
    canceladas = int(m.cancelou.sum())
    return {
        "clientes": total,
        "canceladas": canceladas,
        "ativas": total - canceladas,
        "taxa_churn": canceladas / total if total else np.nan,
        "ic_taxa": wilson(canceladas, total),
        "mrr_perdido": float(m.loc[m.cancelou, "mrr"].sum()),
        "mrr_ativo": float(m.loc[~m.cancelou, "mrr"].sum()),
        "mrr_mediano_canceladas": float(m.loc[m.cancelou, "mrr"].median()),
        "mrr_mediano_ativas": float(m.loc[~m.cancelou, "mrr"].median()),
    }


def motivos(m):
    c = m[m.cancelou]
    tabela = c["motivo"].fillna("sem registro").value_counts().rename_axis("motivo").reset_index(name="contas")
    tabela["%"] = 100 * tabela["contas"] / len(c)
    mrr = c.assign(motivo=c["motivo"].fillna("sem registro")).groupby("motivo")["mrr"].sum()
    tabela["mrr_perdido"] = tabela["motivo"].map(mrr)
    return tabela


def testar_sinais(m, disponiveis):
    linhas = []
    for s, rotulo in SINAIS.items():
        if s == "segmento" or not disponiveis.get(s) or s not in m:
            continue
        x = m[s]
        n_com = int(x.sum())
        t_com = m.loc[x, "cancelou"].mean() if n_com else np.nan
        t_sem = m.loc[~x, "cancelou"].mean()
        p = p_valor_tabela(x, m.cancelou) if 0 < n_com < len(m) else np.nan
        linhas.append({
            "sinal": rotulo, "chave": s, "contas_com_sinal": n_com,
            "churn_com_sinal_%": 100 * t_com if n_com else np.nan, "churn_sem_sinal_%": 100 * t_sem,
            "diferenca_pp": 100 * (t_com - t_sem) if n_com else np.nan, "p_valor": p,
            "evidencia": ("forte" if p < 0.05 else "fraca (indício)" if p < 0.10 else "sem evidência")
            if pd.notna(p) else "não se aplica (ninguém tem o sinal)",
        })
    return pd.DataFrame(linhas)


def segmentos(m):
    media = m.cancelou.mean()
    saida = {}
    for dim, rotulo in DIMENSOES.items():
        if dim not in m or m[dim].nunique() < 2:
            continue
        g = m.groupby(dim).agg(contas=("cancelou", "size"), canceladas=("cancelou", "sum"))
        g["taxa_%"] = 100 * g.canceladas / g.contas
        ic = [wilson(k, n) for k, n in zip(g.canceladas, g.contas)]
        g["ic_min_%"] = [100 * a for a, _ in ic]
        g["ic_max_%"] = [100 * b for _, b in ic]
        g["mrr_ativo"] = m[~m.cancelou].groupby(dim)["mrr"].sum().reindex(g.index).fillna(0)
        g = g.sort_values("taxa_%", ascending=False).reset_index().rename(columns={dim: "grupo"})
        p = p_valor_tabela(m[dim], m.cancelou)
        saida[dim] = {"rotulo": rotulo, "tabela": g, "p_valor": p, "media_%": 100 * media}
    return saida


def paradoxo(tabs, m):
    """Testa as duas frases do enunciado: 'o uso cresceu' e 'a satisfacao esta ok'."""
    out = {}
    uso = tabs.get("uso")
    if uso is not None:
        u = uso.copy()
        u["data"] = para_data(u["data"])
        u["quantidade"] = para_numero(u["quantidade"]).fillna(0)
        t = u.groupby(u["data"].dt.to_period("Q")).agg(uso=("quantidade", "sum"), contratos=("id_contrato", "nunique"))
        t["uso_por_contrato"] = t.uso / t.contratos
        t.index = t.index.astype(str)
        out["uso_trimestral"] = t.rename_axis("trimestre").reset_index()
        if len(t) >= 2:
            out["variacao_uso_%"] = 100 * (t.uso.iloc[-1] - t.uso.iloc[0]) / t.uso.iloc[0]
    cham = tabs.get("chamados")
    if cham is not None and "satisfacao" in cham:
        c = cham.assign(s=para_numero(cham["satisfacao"]), id_cliente=cham["id_cliente"].astype(str))
        c["cancelou"] = c.id_cliente.map(m.cancelou)
        g = c.groupby("cancelou")["s"]
        out["satisfacao"] = {
            "media_geral": float(c.s.mean()),
            "media_canceladas": float(g.mean().get(True, np.nan)),
            "media_ativas": float(g.mean().get(False, np.nan)),
            "sem_resposta_%": 100 * float(c.s.isna().mean()),
            "p_valor": float(stats.mannwhitneyu(c.s[c.cancelou == True].dropna(), c.s[c.cancelou == False].dropna()).pvalue)
            if c.s[c.cancelou == True].notna().any() and c.s[c.cancelou == False].notna().any() else np.nan,
        }
    return out


def calcular_score(m, p: Premissas, segs):
    """Score 0-100 = soma dos pesos dos sinais presentes. Mostra a contribuicao de cada sinal."""
    s = m.copy()
    s["score_risco"] = 0.0
    contribs = []
    for sinal, peso in p.pesos.items():
        if sinal == "segmento":
            fator = pd.Series(0.0, index=s.index)
            qual = pd.Series("", index=s.index)   # QUAL perfil deu os pontos (ex.: canal 'event' 30% x 22%)
            for dim in ("segmento", "canal_aquisicao"):
                if dim in segs:
                    tab = segs[dim]["tabela"].set_index("grupo")
                    excesso = (tab["taxa_%"] - segs[dim]["media_%"]) / 10.0     # 10 p.p. acima da media = fator 1
                    f_dim = s[dim].map(excesso).fillna(0).clip(0, 1)
                    texto = s[dim].map(lambda g, t=tab, d=dim: f"{segs[d]['rotulo'].split(' /')[0].lower()} '{g}' cancela "
                                       f"{t.loc[g, 'taxa_%']:.0f}% (média {segs[d]['media_%']:.0f}%)" if g in t.index else "")
                    maior = f_dim > fator
                    qual = qual.where(~maior, texto)
                    fator = np.maximum(fator, f_dim)
            s["_perfil_de_risco"] = qual
            pontos = peso * fator
        elif sinal in s:
            pontos = peso * s[sinal].astype(float)
        else:
            continue
        s["pts_" + sinal] = pontos
        s["score_risco"] += pontos
        contribs.append(sinal)
    s["score_risco"] = s["score_risco"].clip(0, 100).round(0)
    s["faixa_risco"] = pd.cut(s.score_risco, [-1, 29, 49, 100], labels=["Baixo", "Médio", "Alto"]).astype(str)

    def porque(linha):
        itens = sorted(((linha["pts_" + c], f"Perfil de risco: {linha['_perfil_de_risco']}" if c == "segmento" and linha.get("_perfil_de_risco")
                         else SINAIS[c]) for c in contribs if linha["pts_" + c] > 0), reverse=True)
        return "; ".join(f"{r} (+{v:.0f})" for v, r in itens) or "nenhum sinal"
    s["motivos_do_score"] = s.apply(porque, axis=1)
    return s.drop(columns=["_perfil_de_risco"], errors="ignore")


def validar_score(s):
    y = s.cancelou.astype(int)
    if y.nunique() < 2:
        return np.nan
    return float(roc_auc_score(y, s.score_risco))


def modelo_preditivo(s, disponiveis):
    """Regressao logistica e floresta aleatoria com validacao cruzada de 5 partes (nunca avalia no treino)."""
    X = pd.DataFrame(index=s.index)
    for c in SINAIS:
        if c != "segmento" and c in s:
            X[c] = s[c].astype(int)
    for c in ("mrr", "variacao_uso_pct", "chamados_periodo", "resposta_media_min", "satisfacao_min"):
        if c in s:
            X[c] = s[c]
    for dim in ("segmento", "canal_aquisicao", "plano", "pais"):
        if dim in s:
            X = X.join(pd.get_dummies(s[dim], prefix=dim, dtype=int))
    X = X.fillna(X.median(numeric_only=True)).fillna(0)
    y = s.cancelou.astype(int)
    if y.sum() < 10 or (len(y) - y.sum()) < 10:
        return None
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, class_weight="balanced"))
    rf = RandomForestClassifier(n_estimators=300, min_samples_leaf=5, class_weight="balanced", random_state=42)
    auc_lr = cross_val_score(lr, X, y, cv=cv, scoring="roc_auc")
    auc_rf = cross_val_score(rf, X, y, cv=cv, scoring="roc_auc")
    lr.fit(X, y)
    coef = pd.Series(lr[-1].coef_[0], index=X.columns).sort_values(key=abs, ascending=False).head(10)
    return {"auc_lr": (auc_lr.mean(), auc_lr.std()), "auc_rf": (auc_rf.mean(), auc_rf.std()),
            "variaveis": len(X.columns), "coeficientes": coef.rename("peso_padronizado").rename_axis("variavel").reset_index()}


def priorizar(s):
    ativos = s[~s.cancelou].copy()
    mrr_alto = ativos.mrr >= ativos.mrr.median()
    ativos["mrr_em_risco"] = ativos.mrr * ativos.score_risco / 100
    ativos["prioridade"] = np.select(
        [(ativos.score_risco >= 50) & mrr_alto, (ativos.score_risco >= 50) | ((ativos.score_risco >= 30) & mrr_alto)],
        ["1 · Salvar agora", "2 · Acompanhar"], "3 · Monitorar")
    return ativos.sort_values(["prioridade", "mrr_em_risco"], ascending=[True, False])


def precisa_de_suporte(ativos):
    """Ponte para o modulo de Suporte (PLANEJAMENTO 4.1): conta em risco E com sinal de suporte."""
    sinal_suporte = pd.Series(False, index=ativos.index)
    for c in ("escalado", "resposta_lenta", "satisfacao_baixa"):
        if c in ativos:
            sinal_suporte |= ativos[c]
    return ativos[(ativos.score_risco >= 30) & sinal_suporte]


def acoes(ativos, sinais, segs, mot, p: Premissas, suporte):
    rec = p.taxa_recuperacao_pct / 100
    lista = []

    def add(titulo, o_que, alvo, evidencia, porque):
        if len(alvo) == 0:
            return
        mrr = float(alvo.mrr.sum())
        lista.append({"acao": titulo, "o_que_fazer": o_que, "contas": len(alvo), "mrr_em_jogo": mrr,
                      "impacto_estimado_mrr": mrr * rec, "evidencia": evidencia, "por_que": porque,
                      "ids": list(alvo.index)})

    extras = tuple(d for d in ("produto", "faixa_idade", "genero", "pais", "plano") if d in segs and segs[d]["p_valor"] < 0.10)
    for dim in ("segmento", "canal_aquisicao") + extras:
        if dim not in segs:
            continue
        seg = segs[dim]
        topo = seg["tabela"].iloc[0]
        if topo["taxa_%"] > seg["media_%"] + 5:
            alvo = ativos[ativos[dim] == topo["grupo"]]
            ev = "forte" if seg["p_valor"] < 0.05 else "fraca (indício)" if seg["p_valor"] < 0.10 else "sem evidência estatística"
            add(f"Plano de retenção para {seg['rotulo'].lower()} '{topo['grupo']}'",
                f"Contato proativo do CS, revisão de onboarding e expectativa de venda para as contas ativas de '{topo['grupo']}'.",
                alvo, ev,
                f"'{topo['grupo']}' cancela {topo['taxa_%']:.0f}% contra {seg['media_%']:.0f}% da média "
                f"(IC 95%: {topo['ic_min_%']:.0f}–{topo['ic_max_%']:.0f}%, p = {str(round(seg['p_valor'], 2)).replace('.', ',')}).")
    add("Régua de atendimento para contas em risco com problema de suporte",
        "Fila prioritária, meta de 1ª resposta menor e dono no CS. Enviar estas contas para a ferramenta de Suporte.",
        suporte, "regra de negócio (ver teste dos sinais)",
        "Contas com score ≥ 30 e chamado escalado, resposta lenta ou satisfação baixa no período.")
    ev = {r.chave: r.evidencia for r in sinais.itertuples()} if len(sinais) else {}
    if "queda_uso" in ativos:
        add("Alerta de desengajamento (queda de uso)",
            f"Ligar para as contas cujo uso caiu mais de {p.queda_pct:.0f}% na janela de {p.janela_dias} dias.",
            ativos[ativos.queda_uso], ev.get("queda_uso", "-"),
            "Queda de uso é o sinal clássico de cancelamento silencioso; aqui o teste mostra a força real dele.")
    if "erros_beta" in ativos:
        add("Estabilizar funcionalidades beta",
            "Tirar da base principal as funcionalidades beta com erro e avisar as contas afetadas.",
            ativos[ativos.erros_beta], ev.get("erros_beta", "-"),
            "Contas que tiveram erro em beta no período.")
    if len(mot):
        preco = mot[mot.motivo.isin(["budget", "pricing"])]["%"].sum()
        if preco > 0:
            add("Revisar oferta e preço para contas de alto risco",
                "Oferecer plano ajustado / desconto de retenção antes da renovação para as contas 'Salvar agora'.",
                ativos[ativos.prioridade == "1 · Salvar agora"], "motivo declarado pelos clientes",
                f"Orçamento + preço somam {preco:.0f}% dos motivos declarados de cancelamento.")
    tabela = pd.DataFrame(lista)
    if len(tabela):
        # Prioridade: primeiro a FORCA DA EVIDENCIA, depois o impacto em dinheiro.
        # Acao sem evidencia nos dados nao vira prioridade so porque mexe com muito MRR.
        tabela["nivel"] = tabela["evidencia"].map(NIVEL_EVIDENCIA).fillna(3)
        tabela = tabela.sort_values(["nivel", "impacto_estimado_mrr"], ascending=[True, False]).reset_index(drop=True)
        tabela = tabela.drop(columns="nivel")
        tabela.insert(0, "prioridade", range(1, len(tabela) + 1))
    return tabela


def qualidade(m, tabs, ctx):
    itens = []
    if ctx.get("sem_receita"):
        itens.append("A base não tem contratos/receita: cada cliente vale 1, e os valores em dinheiro viram contagem de clientes.")
    canc = tabs.get("cancelamentos")
    if canc is not None:
        canc = canc.assign(id_cliente=lambda d: d["id_cliente"].astype(str))
        ev = set(canc.id_cliente)
        marcadas = set(m.index[m.cancelou])
        if marcadas - ev:
            itens.append(f"{len(marcadas - ev)} contas marcadas como canceladas não têm evento de cancelamento (motivo = 'sem registro').")
        if ev - marcadas:
            itens.append(f"{len(ev - marcadas)} contas têm evento de cancelamento mas não estão marcadas como canceladas "
                         "(provável reativação). Para a taxa de churn vale a marcação da conta.")
        if "reativacao" in canc:
            itens.append(f"{int(para_booleano(canc['reativacao']).sum())} eventos são reativações.")
    else:
        itens.append("Sem eventos de cancelamento: não há motivo nem data de cancelamento.")
    if m.mrr.isna().any():
        itens.append(f"{int(m.mrr.isna().sum())} clientes sem contrato: ficam sem valor (MRR).")
    for s, rotulo in SINAIS.items():
        if not ctx["disponiveis"].get(s):
            itens.append(f"Sinal '{rotulo}' desligado: faltam os dados para calculá-lo.")
    if "satisfacao_min" in m and m.satisfacao_min.notna().any():
        itens.append(f"Menor nota de satisfação registrada na base: {m.satisfacao_min.min():.0f}. "
                     "Com escala 1–5, a régua de 'satisfação baixa' é uma premissa editável.")
    itens.append(f"Data de referência das contas ativas: {ctx['fim_base']:%d/%m/%Y} (último dado da base). "
                 "Canceladas: data do cancelamento. Sinais medidos só ANTES dessa data (evita vazamento).")
    return itens


def pesos_aprendidos(p, sinais, segs):
    """Peso proporcional ao aumento de churn, so para sinais com p < 0,10. O resto fica com peso zero."""
    brutos = {}
    for r in sinais.itertuples():
        brutos[r.chave] = max(r.diferenca_pp, 0) if pd.notna(r.p_valor) and r.p_valor < 0.10 else 0
    exc = [segs[d]["tabela"]["taxa_%"].max() - segs[d]["media_%"] for d in ("segmento", "canal_aquisicao")
           if d in segs and segs[d]["p_valor"] < 0.10]
    brutos["segmento"] = max(exc) if exc else 0
    total = sum(brutos.values())
    novos = {k: (100 * v / total if total else 0) for k, v in brutos.items()}
    return Premissas(**{**asdict(p), "pesos": novos})


# ---------------------------------------------------------------- orquestracao

def analisar(tabs, p: Premissas | None = None):
    p = p or Premissas()
    m, ctx = preparar(tabs, p)
    segs = segmentos(m)
    sinais = testar_sinais(m, ctx["disponiveis"])
    if p.pesos_pelos_dados:
        p = pesos_aprendidos(p, sinais, segs)
    s = calcular_score(m, p, segs)
    mot = motivos(s)
    ativos = priorizar(s)
    suporte = precisa_de_suporte(ativos)
    return {
        "premissas": p, "contexto": ctx, "mestra": s, "base": {**numeros_base(s), "sem_receita": ctx["sem_receita"]}, "motivos": mot,
        "sinais": sinais, "segmentos": segs, "paradoxo": paradoxo(tabs, s),
        "auc_score": validar_score(s), "modelo": modelo_preditivo(s, ctx["disponiveis"]),
        "ativos": ativos, "precisa_suporte": suporte, "acoes": acoes(ativos, sinais, segs, mot, p, suporte),
        "qualidade": qualidade(s, tabs, ctx),
    }
