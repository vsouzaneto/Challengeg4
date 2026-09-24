"""
Modulo Midia (desafio 004) - motor de analise, sem tela.

Regras: PLANEJAMENTO.md secao 4.4. Padrao de entrega: secao 4.5.
Engajamento = (curtidas + compartilhamentos + comentarios) / views. Toda comparacao de patrocinio e feita
DENTRO do mesmo estrato (plataforma + categoria + faixa de seguidores). "Funciona" so com teste estatistico
E efeito minimo relevante. Teste de sanidade: numa copia, injeta um efeito conhecido e confere se a
ferramenta o encontra.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score

from nucleo.carregar import para_booleano, para_data, para_numero

FAIXAS_SEG = [0, 10_000, 50_000, 100_000, 500_000, np.inf]
ROTULOS_SEG = ["<10K", "10K–50K", "50K–100K", "100K–500K", "500K+"]
DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
DIMENSOES = {
    "plataforma": "Plataforma", "tipo": "Tipo de conteúdo", "categoria": "Categoria", "faixa_seguidores": "Tamanho do criador",
    "faixa_tamanho": "Tamanho/duração do conteúdo", "qtd_hashtags": "Quantidade de hashtags", "dia_semana": "Dia da semana",
    "turno": "Horário", "idioma": "Idioma", "patrocinado_txt": "Patrocínio", "divulgacao": "Tipo de divulgação",
    "categoria_patrocinador": "Categoria do patrocinador", "audiencia_idade": "Audiência: idade",
    "audiencia_genero": "Audiência: gênero", "audiencia_local": "Audiência: local",
}
AUDIENCIA = ("audiencia_idade", "audiencia_genero", "audiencia_local")


@dataclass
class Premissas:
    efeito_minimo_pct: float = 5.0          # diferenca relativa minima para dizer que "funciona"
    custo_mil_seguidores: float = 10.0      # US$ pagos por post patrocinado a cada 1.000 seguidores (hipotese)
    min_posts_grupo: int = 300              # tamanho minimo de grupo nas combinacoes
    efeito_sanidade_pct: float = 10.0       # efeito injetado no teste de sanidade


# ---------------------------------------------------------------- preparo

def preparar(tabs):
    c = tabs["posts"].copy()
    info = {}
    for col in ("views", "curtidas", "compartilhamentos", "comentarios", "seguidores", "tamanho"):
        if col in c:
            c[col] = para_numero(c[col])
    partes = [x for x in ("curtidas", "compartilhamentos", "comentarios") if x in c]
    if not partes:
        raise ValueError("ligue no De/Para pelo menos um destes campos: curtidas, compartilhamentos ou comentários "
                         "(sem eles não existe engajamento para analisar)")
    info["partes_engajamento"] = partes
    c["interacoes"] = c[partes].sum(axis=1) if partes else np.nan
    c["eng_%"] = 100 * c["interacoes"] / c["views"].where(c["views"] > 0)
    c["data"] = para_data(c["data"])
    c["semana"] = c["data"].dt.to_period("W").dt.start_time
    c["dia_semana"] = c["data"].dt.dayofweek.map(dict(enumerate(DIAS)))
    c["turno"] = pd.cut(c["data"].dt.hour, [-1, 5, 11, 17, 23], labels=["madrugada", "manhã", "tarde", "noite"]).astype(str)
    if "seguidores" in c:
        c["faixa_seguidores"] = pd.cut(c["seguidores"], FAIXAS_SEG, labels=ROTULOS_SEG, right=False).astype(str)
    if "tamanho" in c:
        c["faixa_tamanho"] = pd.qcut(c["tamanho"], 4, labels=["curto", "médio", "longo", "muito longo"], duplicates="drop").astype(str)
    if "hashtags" in c:
        tags = c["hashtags"].fillna("").astype(str).str.lower().str.split(",")
        c["lista_hashtags"] = tags.map(lambda x: sorted({t.strip() for t in x if t.strip()}))
        c["qtd_hashtags"] = c["lista_hashtags"].map(len).clip(upper=5).map(lambda n: "5+" if n >= 5 else str(n))
    if "patrocinado" in c:
        c["patrocinado"] = para_booleano(c["patrocinado"])
        c["patrocinado_txt"] = np.where(c["patrocinado"], "patrocinado", "orgânico")
    for col in ("divulgacao", "categoria_patrocinador"):
        if col in c and "patrocinado" in c:
            c[col] = c[col].where(c["patrocinado"], "orgânico")
    info["n"] = len(c)
    info["periodo"] = (c["data"].min(), c["data"].max())
    info["zero_interacao"] = int((c["interacoes"] == 0).sum())
    info["cv_views_%"] = 100 * float(c["views"].std() / c["views"].mean())
    return c, info


# ---------------------------------------------------------------- utilidades

def _d(v, casas=2):
    return f"{v:.{casas}f}".replace(".", ",")


def veredito(p, efeito, p_min):
    if p != p:
        return "sem teste"
    if p < 0.05 and efeito >= p_min.efeito_minimo_pct:
        return "funciona (diferença real e relevante)"
    if p < 0.05:
        return "diferença real, mas pequena demais para importar"
    return "sem diferença (é ruído)"


def _grupo(c, dim, alvo="eng_%"):
    g = c.groupby(dim, observed=True)[alvo].agg(posts="size", media="mean", dp="std").reset_index()
    g["ic_min"] = g.media - 1.96 * g.dp / np.sqrt(g.posts)
    g["ic_max"] = g.media + 1.96 * g.dp / np.sqrt(g.posts)
    return g.drop(columns="dp").rename(columns={dim: "grupo"})


# ---------------------------------------------------------------- diagnostico

def numeros(c, info):
    out = {"posts": len(c), "eng_medio_%": float(c["eng_%"].mean()), "views_mediana": float(c["views"].median())}
    if "id_criador" in c:
        out["criadores"] = int(c["id_criador"].nunique())
    if "patrocinado" in c:
        out["patrocinados_%"] = 100 * float(c["patrocinado"].mean())
    return out


def drivers(c, p: Premissas):
    saida = {}
    media = c["eng_%"].mean()
    for dim, rot in DIMENSOES.items():
        if dim not in c or c[dim].nunique() < 2:
            continue
        t = _grupo(c, dim)
        t["vs_media_%"] = 100 * (t.media / media - 1)
        pv = float(stats.kruskal(*[x["eng_%"].dropna() for _, x in c.groupby(dim, observed=True)])[1])
        efeito = float(100 * (t.media.max() - t.media.min()) / media)
        extra = {}
        for m, nome in (("views", "views"), ("compartilhamentos", "compartilhamentos")):
            if m in c:
                extra[nome] = c.groupby(dim, observed=True)[m].mean()
        for nome, s in extra.items():
            t[f"{nome}_media"] = t.grupo.map(s)
        saida[dim] = {"rotulo": rot, "tabela": t.sort_values("media", ascending=False), "p_valor": pv, "efeito_%": efeito,
                      "veredito": veredito(pv, efeito, p)}
    return saida


def combinacoes(c, p: Premissas):
    dims = [d for d in ("plataforma", "tipo", "categoria", "faixa_seguidores") if d in c]
    if len(dims) < 2:
        return None
    media = c["eng_%"].mean()
    g = c.groupby(dims, observed=True)["eng_%"]
    linhas = []
    for chave, x in g:
        if len(x) < p.min_posts_grupo:
            continue
        resto = c["eng_%"].drop(x.index)
        pv = float(stats.ttest_ind(x, resto, equal_var=False)[1])
        linhas.append({**dict(zip(dims, chave if isinstance(chave, tuple) else (chave,))), "posts": len(x),
                       "eng_%": float(x.mean()), "vs_media_%": 100 * (x.mean() / media - 1), "p_valor": pv})
    t = pd.DataFrame(linhas)
    if not len(t):
        return None
    limite = 0.05 / len(t)   # correcao de Bonferroni: muitas combinacoes = muitos "achados" por acaso
    t["passa_no_teste"] = t.p_valor < limite
    t = t.sort_values("vs_media_%", ascending=False)
    return {"tabela": t, "testadas": len(t), "limite_p": limite, "aprovadas": int(t.passa_no_teste.sum()),
            "p_brutos_abaixo_005": int((t.p_valor < 0.05).sum()), "dims": dims}


def _estrato(c):
    cols = [x for x in ("plataforma", "categoria", "faixa_seguidores") if x in c]
    return c[cols].astype(str).agg(" · ".join, axis=1) if cols else pd.Series("todos", index=c.index)


def comparar_patrocinio(c, alvo="eng_%"):
    """Diferenca patrocinado - organico DENTRO de cada estrato (tira o efeito de plataforma, categoria e tamanho)."""
    d = c[[alvo, "patrocinado"]].copy()
    d["estrato"] = _estrato(c)
    d["centrado"] = d[alvo] - d.groupby("estrato")[alvo].transform("mean")
    a, b = d.loc[d.patrocinado, "centrado"], d.loc[~d.patrocinado, "centrado"]
    if len(a) < 20 or len(b) < 20:
        return None
    dif = float(a.mean() - b.mean())
    pv = float(stats.ttest_ind(a, b, equal_var=False)[1])
    return {"diferenca": dif, "diferenca_%": 100 * dif / float(c[alvo].mean()), "p_valor": pv,
            "n_patrocinado": len(a), "n_organico": len(b), "estratos": int(d.estrato.nunique())}


def patrocinio(c, p: Premissas):
    if "patrocinado" not in c or c.patrocinado.nunique() < 2:
        return None
    out = {"engajamento": comparar_patrocinio(c, "eng_%"), "alcance": comparar_patrocinio(c, "views")}
    if "compartilhamentos" in c:
        out["compartilhamentos"] = comparar_patrocinio(c, "compartilhamentos")
    ruim = out["engajamento"]
    out["veredito"] = veredito(ruim["p_valor"], abs(ruim["diferenca_%"]), p) if ruim else "sem teste"
    # em que condicoes? por faixa de criador e por tipo de divulgacao
    por = []
    if "faixa_seguidores" in c:
        for f in ROTULOS_SEG:
            sub = c[c.faixa_seguidores == f]
            r = comparar_patrocinio(sub) if len(sub) else None
            if r:
                por.append({"faixa": f, "posts": len(sub), "diferenca_%": r["diferenca_%"], "p_valor": r["p_valor"]})
    out["por_faixa"] = pd.DataFrame(por)
    # custo implicito (premissa): paga-se por seguidor, mas o resultado nao muda com o tamanho
    if "seguidores" in c:
        s = c[c.patrocinado].copy()
        s["custo"] = s.seguidores / 1000 * p.custo_mil_seguidores
        s["custo_por_mil_views"] = 1000 * s.custo / s.views
        s["custo_por_interacao"] = s.custo / s.interacoes.replace(0, np.nan)
        cust = s.groupby("faixa_seguidores", observed=True).agg(
            posts=("custo", "size"), custo_medio=("custo", "mean"), views_medias=("views", "mean"),
            eng_medio=("eng_%", "mean"), custo_por_mil_views=("custo_por_mil_views", "median"),
            custo_por_interacao=("custo_por_interacao", "median")).reindex(ROTULOS_SEG).dropna(how="all").reset_index()
        out["custo"] = cust
        barata = cust.sort_values("custo_medio").iloc[0]
        out["faixa_mais_barata"] = barata.faixa_seguidores
        out["gasto_total"] = float(s.custo.sum())
        # se todo patrocinio fosse pago no preco medio da faixa 10K-50K (resultado igual), quanto sairia
        ref = cust.set_index("faixa_seguidores").custo_medio.get("10K–50K", barata.custo_medio)
        out["custo_referencia"] = float(ref)
        out["economia_%"] = 100 * (1 - ref * len(s) / s.custo.sum()) if s.custo.sum() else np.nan
        out["seguidores_mediana_patrocinados"] = float(s.seguidores.median())
    return out


def audiencia(c):
    """Qual audiencia engaja mais, por plataforma (com teste)."""
    if "plataforma" not in c:
        return None
    linhas = []
    for dim in AUDIENCIA:
        if dim not in c:
            continue
        for plat, sub in c.groupby("plataforma"):
            g = sub.groupby(dim)["eng_%"]
            if g.ngroups < 2:
                continue
            pv = float(stats.kruskal(*[x for _, x in g])[1])
            m = g.mean()
            linhas.append({"plataforma": plat, "audiência": DIMENSOES[dim].replace("Audiência: ", ""), "melhor": m.idxmax(),
                           "melhor_eng_%": float(m.max()), "pior": m.idxmin(), "pior_eng_%": float(m.min()), "p_valor": pv})
    return pd.DataFrame(linhas) if linhas else None


def frequencia(c):
    if "id_criador" not in c:
        return None
    g = c.groupby("id_criador").agg(posts=("eng_%", "size"), eng=("eng_%", "mean"), inicio=("data", "min"), fim=("data", "max"))
    meses = ((g.fim - g.inicio).dt.days / 30.4).clip(lower=1)
    g["posts_por_mes"] = g.posts / meses
    rho, pv = stats.spearmanr(g.posts_por_mes, g.eng)
    return {"posts_por_criador": g.posts.describe().to_dict(), "posts_por_mes_mediana": float(g.posts_por_mes.median()),
            "rho": float(rho), "p_valor": float(pv), "variacao_posts": int(g.posts.nunique())}


def hashtags(c, p: Premissas, top=15):
    if "lista_hashtags" not in c:
        return None
    ex = c[["eng_%", "lista_hashtags"]].explode("lista_hashtags").dropna()
    cont = ex.lista_hashtags.value_counts()
    media = c["eng_%"].mean()
    linhas = []
    for tag in cont.head(top).index:
        com = ex.loc[ex.lista_hashtags == tag, "eng_%"]
        sem = c.loc[~c.index.isin(com.index), "eng_%"]
        linhas.append({"hashtag": tag, "posts": len(com), "eng_%": float(com.mean()), "vs_media_%": 100 * (com.mean() / media - 1),
                       "p_valor": float(stats.ttest_ind(com, sem, equal_var=False)[1])})
    # pares de hashtags usados juntos
    pares = c.lista_hashtags.map(lambda x: [f"{a} + {b}" for i, a in enumerate(x) for b in x[i + 1:]])
    exp = pd.DataFrame({"par": pares, "eng_%": c["eng_%"]}).explode("par").dropna()
    cp = exp.par.value_counts()
    pares_top = exp[exp.par.isin(cp[cp >= 30].index)].groupby("par")["eng_%"].agg(posts="size", media="mean").sort_values("media", ascending=False)
    return {"tabela": pd.DataFrame(linhas), "distintas": int(cont.size), "sem_hashtag_%": 100 * float((c.lista_hashtags.map(len) == 0).mean()),
            "pares_melhores": pares_top.head(10).reset_index(), "pares_testados": int(len(pares_top))}


def modelo_preditivo(c, semente=42):
    """Diferencial: da para prever o engajamento de um post antes de publicar? (validacao cruzada, numero honesto)"""
    cols = [d for d in ("plataforma", "tipo", "categoria", "faixa_seguidores", "faixa_tamanho", "qtd_hashtags", "turno",
                        "dia_semana", "patrocinado_txt", "idioma", "audiencia_idade", "audiencia_genero", "audiencia_local") if d in c]
    if not cols:
        return None
    base = c.dropna(subset=["eng_%"])
    if len(base) < 100:
        return None
    if len(base) > 20_000:
        base = base.sample(20_000, random_state=semente)
    X = pd.get_dummies(base[cols].astype(str), drop_first=True)
    y = base["eng_%"].values
    r2_lr = cross_val_score(LinearRegression(), X, y, cv=5, scoring="r2")
    r2_rf = cross_val_score(RandomForestRegressor(n_estimators=60, max_depth=8, random_state=semente, n_jobs=-1), X, y, cv=5, scoring="r2")
    return {"r2_lr": (float(r2_lr.mean()), float(r2_lr.std())), "r2_rf": (float(r2_rf.mean()), float(r2_rf.std())),
            "variaveis": len(cols), "amostra": len(base)}


def clusters_audiencia(c, k=4, semente=42):
    """Diferencial: agrupa CRIADORES pelo perfil da audiencia (idade, genero, local) e compara o engajamento dos grupos."""
    dims = [d for d in AUDIENCIA if d in c]
    if "id_criador" not in c or not dims:
        return None
    perfil = pd.concat([pd.crosstab(c["id_criador"], c[d], normalize="index").add_prefix(f"{d}=") for d in dims], axis=1)
    if len(perfil) < 4 * k:
        return None
    rot = KMeans(n_clusters=k, n_init=10, random_state=semente).fit_predict(perfil.values)
    grupo = pd.Series(rot, index=perfil.index, name="cluster")
    eng = c.groupby("id_criador")["eng_%"].mean()
    t = pd.DataFrame({"cluster": grupo, "eng": eng.reindex(grupo.index)})
    pv = float(stats.kruskal(*[x.eng.dropna() for _, x in t.groupby("cluster")])[1])
    linhas = []
    for g, x in t.groupby("cluster"):
        centro = perfil.loc[x.index].mean()
        tracos = []
        for d in dims:
            parte = centro[[i for i in centro.index if i.startswith(f"{d}=")]]
            tracos.append(f"{parte.idxmax().split('=', 1)[1]} ({100 * parte.max():.0f}%)")
        linhas.append({"grupo": f"Grupo {g + 1}", "criadores": len(x), "perfil_típico": " · ".join(tracos),
                       "eng_%": float(x.eng.mean())})
    return {"tabela": pd.DataFrame(linhas).sort_values("eng_%", ascending=False), "p_valor": pv, "k": k}


def recomendar_post(c, p: Premissas, **escolhas):
    """Diferencial: 'gerador de recomendacao'. Para o post que o time quer publicar, mostra o engajamento esperado
    (posts parecidos do historico, com intervalo) e compara com as alternativas de formato e plataforma."""
    filtro = pd.Series(True, index=c.index)
    usados = {}
    for campo, valor in escolhas.items():
        if valor is not None and campo in c:
            filtro &= c[campo].astype(str) == str(valor)
            usados[campo] = valor
    parecidos = c.loc[filtro, "eng_%"]
    if len(parecidos) < 20:
        return {"n": len(parecidos), "usados": usados}
    media, dp = parecidos.mean(), parecidos.std()
    out = {"n": len(parecidos), "usados": usados, "eng_%": float(media),
           "ic": (float(media - 1.96 * dp / np.sqrt(len(parecidos))), float(media + 1.96 * dp / np.sqrt(len(parecidos)))),
           "faixa_normal": (float(parecidos.quantile(0.1)), float(parecidos.quantile(0.9))),
           "views": float(c.loc[filtro, "views"].mean())}
    alternativas = []
    for campo in ("tipo", "plataforma"):
        if campo not in c:
            continue
        base = filtro.copy() if campo not in usados else pd.Series(True, index=c.index)
        if campo in usados:
            for k, v in usados.items():
                if k != campo:
                    base &= c[k].astype(str) == str(v)
        g = c.loc[base].groupby(campo)["eng_%"].agg(["mean", "size"])
        g = g[g["size"] >= 20]
        if len(g) > 1:
            pv = float(stats.kruskal(*[x["eng_%"] for _, x in c.loc[base].groupby(campo) if len(x) >= 20])[1])
            alternativas.append({"campo": campo, "melhor": g["mean"].idxmax(), "ganho_%": float(100 * (g["mean"].max() / media - 1)),
                                 "p_valor": pv})
    out["alternativas"] = alternativas
    return out


def teste_de_sanidade(c, p: Premissas):
    """Numa COPIA dos dados, injeta um efeito conhecido e confere se a ferramenta o encontra.
    Prova que 'sem diferenca' e conclusao, nao defeito."""
    out = {}
    fator = 1 + p.efeito_sanidade_pct / 100
    if "patrocinado" in c and c.patrocinado.nunique() == 2:
        copia = c.copy()
        copia.loc[copia.patrocinado, "eng_%"] *= fator
        r = comparar_patrocinio(copia)
        out["patrocinio"] = {"injetado_%": p.efeito_sanidade_pct, "encontrado_%": r["diferenca_%"], "p_valor": r["p_valor"],
                             "achou": r["p_valor"] < 0.05 and abs(r["diferenca_%"] - p.efeito_sanidade_pct) < p.efeito_sanidade_pct / 2}
    if "tipo" in c and c.tipo.nunique() > 1:
        alvo = c.tipo.value_counts().index[-1]
        copia = c.copy()
        copia.loc[copia.tipo == alvo, "eng_%"] *= fator
        d = drivers(copia[["eng_%", "tipo"]], p)["tipo"]
        topo = d["tabela"].iloc[0]
        out["tipo"] = {"grupo": alvo, "injetado_%": p.efeito_sanidade_pct, "encontrado_%": float(topo["vs_media_%"]), "p_valor": d["p_valor"], "achou": topo.grupo == alvo and d["p_valor"] < 0.05}
    return out


def painel(c):
    """Serie semanal para acompanhar no dia a dia (ultima semana incompleta fica de fora)."""
    if c["data"].isna().all():
        return None
    s = c.groupby(["semana", "plataforma"] if "plataforma" in c else ["semana"])["eng_%"].agg(posts="size", eng="mean").reset_index()
    ultima = c["semana"].max()
    s = s[s.semana < ultima]
    return s


def estrategia(r, p: Premissas):
    """Recomendacoes priorizadas: o que, para quem, quando e com que evidencia."""
    L = []
    pat, drv = r["patrocinio"], r["drivers"]
    tamanho = drv.get("faixa_seguidores")
    if pat and "custo" in pat:
        L.append({"acao": "Pagar patrocínio pelo resultado, não pelo tamanho do criador",
                  "o_que": f"Contratar pela faixa mais barata que entrega o mesmo resultado e pagar por view/interação entregue. "
                           f"Teto de preço: o custo médio de um criador de 10K–50K ({pat['custo_referencia']:,.0f} US$ por post, pela premissa).".replace(",", "."),
                  "para_quem": "Time de parcerias / influência", "quando": "Nos próximos contratos (esta semana: renegociar os maiores)",
                  "evidencia": "decisão por custo (resultado igual comprovado)",
                  "por_que": f"Engajamento e views são iguais em todas as faixas de seguidores (p = {_d(tamanho['p_valor'])}); "
                             f"hoje a mediana dos patrocinados é {pat['seguidores_mediana_patrocinados'] / 1000:,.0f} mil seguidores. "
                             f"Pela premissa de custo, a economia seria de ~{pat['economia_%']:.0f}%.".replace(",", ".")})
    if pat and pat["engajamento"]:
        e = pat["engajamento"]
        L.append({"acao": "Patrocinar só com teste controlado (A/B)",
                  "o_que": "Para cada campanha patrocinada, manter um grupo de criadores parecidos sem patrocínio e comparar. "
                           "Sem isso não dá para dizer que o patrocínio gera engajamento.",
                  "para_quem": "Head de Marketing + parcerias", "quando": "Próxima campanha",
                  "evidencia": "fato nos dados (sem diferença)" if e["p_valor"] >= 0.05 else "comprovado",
                  "por_que": f"Comparando dentro do mesmo estrato ({e['estratos']} combinações de plataforma, categoria e tamanho), "
                             f"patrocinado × orgânico: {_d(e['diferenca_%'])}% de engajamento (p = {_d(e['p_valor'])})."})
    iguais = [v["rotulo"].lower() for k, v in drv.items() if k in ("plataforma", "tipo", "categoria") and v["veredito"].startswith("sem")]
    if iguais:
        L.append({"acao": "Escolher plataforma e formato pelo custo de produção, não por 'qual engaja mais'",
                  "o_que": "Manter o mix atual e priorizar o que é mais barato e rápido de produzir para o time; nenhuma "
                           "plataforma, formato ou categoria entrega mais engajamento.",
                  "para_quem": "Time de conteúdo", "quando": "Planejamento do próximo mês",
                  "evidencia": "decisão por custo (resultado igual comprovado)",
                  "por_que": "Sem diferença estatística em: " + ", ".join(iguais) + "."})
    L.append({"acao": "Parar de premiar 'engagement rate' isolado e rankings de plataforma",
              "o_que": "Relatórios passam a mostrar intervalo de confiança e comparação justa (mesmo estrato). Diferença dentro do "
                       "ruído não vira decisão.",
              "para_quem": "Analytics / Head de Marketing", "quando": "Já no próximo relatório",
              "evidencia": "fato nos dados",
              "por_que": (f"Das {r['combinacoes']['testadas']} combinações testadas, {r['combinacoes']['p_brutos_abaixo_005']} parecem "
                          f"'vencedoras' pelo teste comum, mas {r['combinacoes']['aprovadas']} passam quando se corrige para o número de testes."
                          if r["combinacoes"] else "Diferenças entre grupos ficam dentro do ruído.")})
    f = r["frequencia"]
    if f:
        L.append({"acao": "Testar frequência de postagem de propósito",
                  "o_que": "Escolher 2 grupos de criadores e variar a frequência por 4 semanas, medindo no painel.",
                  "para_quem": "Time de conteúdo", "quando": "Próximas 4 semanas",
                  "evidencia": "sem evidência (o dado não varia)",
                  "por_que": f"Cada criador tem {f['posts_por_criador']['min']:.0f} a {f['posts_por_criador']['max']:.0f} posts em ~2 anos: "
                             "não há variação de frequência para medir o efeito."})
    ordem = {"fato nos dados": 0, "fato nos dados (sem diferença)": 0, "comprovado": 0,
             "decisão por custo (resultado igual comprovado)": 1, "sem evidência (o dado não varia)": 2}
    out = pd.DataFrame(L)
    out["_o"] = out.evidencia.map(ordem).fillna(3)
    out = out.sort_values("_o", kind="stable").drop(columns="_o").reset_index(drop=True)
    out.insert(0, "prioridade", range(1, len(out) + 1))
    return out


def quick_wins(r):
    q = []
    pat = r["patrocinio"]
    if pat and "custo" in pat:
        grandes = pat["custo"][pat["custo"].faixa_seguidores.isin(["100K–500K", "500K+"])]
        q.append(f"Listar os contratos ativos com criadores de 100K+ seguidores ({int(grandes.posts.sum()):,} posts patrocinados na base)".replace(",", ".") + f" "
                 "e renegociar para preço por resultado.")
    q.append("Montar o primeiro teste A/B de patrocínio: 20 criadores patrocinados × 20 parecidos sem patrocínio.")
    q.append("Usar a aba 'Painel' toda segunda-feira: engajamento semanal por plataforma, com o intervalo do normal.")
    return q


def qualidade(c, info, freq):
    itens = [f"Base com {info['n']:,} posts".replace(",", ".") + (f" de {c['id_criador'].nunique():,} criadores".replace(",", ".") if "id_criador" in c else "")
             + (f", de {info['periodo'][0]:%d/%m/%Y} a {info['periodo'][1]:%d/%m/%Y}." if pd.notna(info["periodo"][0]) else ".")]
    itens.append(f"Engajamento = ({' + '.join(info['partes_engajamento'])}) ÷ views; não existe coluna pronta.")
    itens.append(f"Viés de sobrevivência: {info['zero_interacao']} posts com zero interação. "
                 + ("A base parece conter só posts que 'deram certo' (ou foi gerada artificialmente): não dá para medir o que fracassou."
                    if info["zero_interacao"] == 0 else ""))
    itens.append(f"As views variam só {_d(info['cv_views_%'], 1)}% em torno da média (coeficiente de variação), independente do tamanho "
                 "do criador. Em dados reais de redes sociais a variação é enorme: esta base é sintética ou muito filtrada, e as "
                 "conclusões valem para ela.")
    if "id_criador" in c and "seguidores" in c:
        n_var = int((c.groupby("id_criador").seguidores.nunique() > 1).sum())
        plats = float(c.groupby("id_criador").plataforma.nunique().mean()) if "plataforma" in c else np.nan
        itens.append(f"{n_var} criadores aparecem com número de seguidores diferente em cada post e, em média, em {_d(plats, 1)} "
                     "plataformas. Por isso o tamanho do criador é lido post a post.")
    if freq:
        itens.append("Frequência de postagem: praticamente igual para todos os criadores; o efeito da frequência não pode ser medido.")
    itens.append("Não existe custo no dataset: o custo do patrocínio é uma premissa editável (US$ por 1.000 seguidores).")
    return itens


# ---------------------------------------------------------------- orquestracao

def analisar(tabs, p: Premissas | None = None):
    p = p or Premissas()
    c, info = preparar(tabs)
    drv = drivers(c, p)
    freq = frequencia(c)
    r = {"premissas": p, "info": info, "posts": c, "numeros": numeros(c, info), "drivers": drv,
         "combinacoes": combinacoes(c, p), "patrocinio": patrocinio(c, p), "audiencia": audiencia(c), "frequencia": freq,
         "hashtags": hashtags(c, p), "modelo": modelo_preditivo(c), "clusters": clusters_audiencia(c), "sanidade": teste_de_sanidade(c, p), "painel": painel(c),
         "qualidade": qualidade(c, info, freq)}
    r["estrategia"] = estrategia(r, p)
    r["quick_wins"] = quick_wins(r)
    return r
