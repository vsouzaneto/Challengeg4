"""
Modulo Suporte (desafio 002) - motor de analise, sem tela.

Regras: PLANEJAMENTO.md secao 4.2. Padrao de entrega: secao 4.5.
Dataset 1 (chamados): onde trava, satisfacao, desperdicio.
Dataset 2 (textos classificados): prova que a classificacao automatica funciona e quanto dela e segura.
"""

import hashlib
import os
from dataclasses import asdict, dataclass, field

import joblib
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import make_pipeline

from nucleo import sessoes
from nucleo.carregar import para_booleano, para_data, para_numero

DIMENSOES = {"canal": "Canal", "prioridade": "Prioridade", "tipo": "Tipo do chamado", "produto": "Produto",
             "faixa_idade": "Faixa de idade", "genero": "Gênero", "status": "Status"}
PRIORIDADES_ORDEM = ["Critical", "High", "Medium", "Low", "urgent", "high", "medium", "low"]


@dataclass
class Premissas:
    custo_hora: float = 45.0                    # R$ por hora de agente
    sla_h: dict = field(default_factory=lambda: {"critical": 4, "urgent": 4, "high": 8, "medium": 24, "low": 48})
    confianca_auto: float = 0.85                # >= automatico
    confianca_humano: float = 0.60              # < vai direto para humano; no meio, IA sugere e humano confirma
    minutos_triagem: float = 5.0                # tempo que um agente gasta classificando/roteando 1 ticket
    tickets_por_mes: float | None = None        # None = volume da base / 12
    nunca_automatizar_tipos: tuple = ("Cancellation request", "Refund request")
    nunca_automatizar_prioridades: tuple = ("Critical", "urgent")
    nunca_automatizar_categorias: tuple = ("Administrative rights",)


# ---------------------------------------------------------------- utilidades

def mediana_ic(valores, n_boot=500, semente=42):
    v = np.asarray(valores, dtype=float)
    v = v[~np.isnan(v)]
    if len(v) < 5:
        return (np.nan, np.nan)
    rng = np.random.default_rng(semente)
    meds = np.median(rng.choice(v, size=(n_boot, len(v)), replace=True), axis=1)
    return (float(np.percentile(meds, 2.5)), float(np.percentile(meds, 97.5)))


def kruskal(df, grupo, valor):
    amostras = [g[valor].dropna().values for _, g in df.groupby(grupo) if g[valor].notna().sum() >= 5]
    if len(amostras) < 2:
        return np.nan, np.nan
    h, p = stats.kruskal(*amostras)
    n = sum(len(a) for a in amostras)
    eta2 = max(0.0, (h - len(amostras) + 1) / (n - len(amostras)))   # tamanho do efeito (0 = nenhum)
    return float(p), float(eta2)


def veredito(p):
    if pd.isna(p):
        return "sem dados"
    return "diferença comprovada" if p < 0.05 else "indício" if p < 0.10 else "sem diferença"


# ---------------------------------------------------------------- preparacao (dataset 1)

def preparar(ch):
    c = ch.copy()
    info = {}
    if "tempo_resolucao_h" in c:
        c["duracao_h"] = para_numero(c["tempo_resolucao_h"])
        info["regra_duracao"] = "duração informada diretamente na base (horas)"
    elif "primeira_resposta" in c and "resolucao" in c:
        pr, rs = para_data(c["primeira_resposta"]), para_data(c["resolucao"])
        bruto = (rs - pr).dt.total_seconds() / 3600
        c["duracao_h"] = bruto.where(bruto > 0)
        info["regra_duracao"] = ("duração = data/hora da resolução − data/hora da 1ª resposta, só quando positiva "
                                 "(a base não tem a hora de abertura do chamado)")
        info["duracao_negativa"] = int((bruto <= 0).sum())
        info["duracao_com_datas"] = int(bruto.notna().sum())
    else:
        c["duracao_h"] = np.nan
        info["regra_duracao"] = "sem dados de tempo"
    if "tempo_resposta_h" in c:
        c["resposta_h"] = para_numero(c["tempo_resposta_h"])
    if "satisfacao" in c:
        c["satisfacao"] = para_numero(c["satisfacao"])
    if "idade" in c:
        c["faixa_idade"] = pd.cut(para_numero(c["idade"]), [0, 25, 35, 50, 65, 200],
                                  labels=["até 25", "26-35", "36-50", "51-65", "66+"]).astype(str)
    if "escalado" in c:
        c["escalado"] = para_booleano(c["escalado"])
    if "status" in c:
        st = c["status"].astype(str).str.lower()
        c["em_aberto"] = ~st.str.contains("closed|fechad|resolv")
    elif "resolucao" in c:
        c["em_aberto"] = c["resolucao"].isna()
    info["n_duracao_valida"] = int(c["duracao_h"].notna().sum())
    return c, info


# ---------------------------------------------------------------- diagnostico

def volume(c):
    out = {"total": len(c)}
    if "em_aberto" in c:
        out["em_aberto"] = int(c.em_aberto.sum())
        out["em_aberto_%"] = 100 * c.em_aberto.mean()
    if "resposta_h" in c and c.resposta_h.notna().any():
        out["resposta_mediana_h"] = float(c.resposta_h.median())
    if "escalado" in c:
        out["escalado_%"] = 100 * float(c.escalado.mean())
    if "status" in c:
        out["por_status"] = c["status"].value_counts().rename_axis("status").reset_index(name="chamados")
    return out


def gargalos(c, min_n=30):
    dims = [d for d in ("canal", "prioridade", "tipo") if d in c]
    saida = {"por_dimensao": {}, "combinacoes": pd.DataFrame(), "backlog": pd.DataFrame()}
    for d in dims:
        g = c.groupby(d)["duracao_h"]
        t = pd.DataFrame({"chamados": c.groupby(d).size(), "com_duracao": g.count(), "mediana_h": g.median(),
                          "p90_h": g.quantile(0.9)})
        ic = {k: mediana_ic(v) for k, v in g}
        t["ic_min_h"] = [ic[k][0] for k in t.index]
        t["ic_max_h"] = [ic[k][1] for k in t.index]
        if "em_aberto" in c:
            t["em_aberto_%"] = 100 * c.groupby(d)["em_aberto"].mean()
        p, eta = kruskal(c, d, "duracao_h")
        pb = _p_backlog(c, d)
        saida["por_dimensao"][d] = {"rotulo": DIMENSOES[d], "tabela": t.sort_values("mediana_h", ascending=False).reset_index(),
                                     "p_tempo": p, "efeito_tempo": eta, "p_backlog": pb}
    # combinacoes 2 a 2 para tempo (com minimo de amostra), 3 a 3 para backlog (usa todos os chamados)
    linhas = []
    for i, a in enumerate(dims):
        for b in dims[i + 1:]:
            for (va, vb), g in c.groupby([a, b]):
                n = g.duracao_h.notna().sum()
                if n >= min_n:
                    linhas.append({"combinação": f"{DIMENSOES[a]}={va} · {DIMENSOES[b]}={vb}", "com_duracao": int(n),
                                   "mediana_h": g.duracao_h.median(), "p90_h": g.duracao_h.quantile(0.9)})
    if linhas:
        comb = pd.DataFrame(linhas).sort_values("mediana_h", ascending=False)
        geral = c.duracao_h.median()
        comb["vs_geral_h"] = comb.mediana_h - geral
        saida["combinacoes"] = comb.reset_index(drop=True)
    if "em_aberto" in c and len(dims) >= 2:
        bl = c.groupby(dims).agg(chamados=("em_aberto", "size"), em_aberto=("em_aberto", "sum")).reset_index()
        bl["em_aberto_%"] = 100 * bl.em_aberto / bl.chamados
        saida["backlog"] = bl.sort_values("em_aberto", ascending=False).reset_index(drop=True)
    return saida


def _p_backlog(c, d):
    if "em_aberto" not in c:
        return np.nan
    t = pd.crosstab(c[d], c.em_aberto)
    return float(stats.chi2_contingency(t)[1]) if t.shape[0] > 1 and t.shape[1] > 1 else np.nan


def satisfacao(c):
    if "satisfacao" not in c or c.satisfacao.notna().sum() < 20:
        return None
    linhas = []
    for d, rot in DIMENSOES.items():
        if d in c and d != "status" and c[d].nunique() > 1:
            p, eta = kruskal(c, d, "satisfacao")
            medias = c.groupby(d)["satisfacao"].mean()
            linhas.append({"variável": rot, "p_valor": p, "efeito (0-1)": eta, "menor média": f"{medias.idxmin()} ({medias.min():.2f})".replace(".", ","),
                           "maior média": f"{medias.idxmax()} ({medias.max():.2f})".replace(".", ","), "veredito": veredito(p)})
    if c.duracao_h.notna().sum() > 20:
        ok = c[["duracao_h", "satisfacao"]].dropna()
        rho, p = stats.spearmanr(ok.duracao_h, ok.satisfacao)
        linhas.append({"variável": "Tempo de atendimento", "p_valor": float(p), "efeito (0-1)": float(rho ** 2),
                       "menor média": f"correlação {rho:+.2f}", "maior média": "", "veredito": veredito(p)})
    tab = pd.DataFrame(linhas).sort_values("p_valor")
    return {"tabela": tab, "media": float(c.satisfacao.mean()), "avaliados": int(c.satisfacao.notna().sum()),
            "distribuicao": c.satisfacao.value_counts().sort_index().rename_axis("nota").reset_index(name="chamados")}


def desperdicio(c, p: Premissas):
    if "prioridade" not in c or c.duracao_h.notna().sum() == 0:
        return None
    sla = c["prioridade"].astype(str).str.lower().map(p.sla_h)
    excesso = (c.duracao_h - sla).clip(lower=0)
    c2 = c.assign(sla_h=sla, excesso_h=excesso, estourou=c.duracao_h > sla)
    medidos = c2[c2.duracao_h.notna() & c2.sla_h.notna()]
    total_h = float(medidos.excesso_h.sum())
    por = medidos.groupby("prioridade").agg(chamados=("excesso_h", "size"), estouraram=("estourou", "sum"),
                                            horas_acima_meta=("excesso_h", "sum")).reset_index()
    por["custo_R$"] = por.horas_acima_meta * p.custo_hora
    por["meta_h"] = por.prioridade.astype(str).str.lower().map(p.sla_h)
    # projecao para toda a base: proporcao medida x volume total
    fator = len(c2) / max(len(medidos), 1)
    backlog = int(c2.get("em_aberto", pd.Series(False, index=c2.index)).sum())
    return {"horas_medidas": total_h, "custo_medido": total_h * p.custo_hora, "chamados_medidos": len(medidos),
            "horas_projetadas": total_h * fator, "custo_projetado": total_h * fator * p.custo_hora,
            "estouraram_%": 100 * float(medidos.estourou.mean()) if len(medidos) else np.nan,
            "por_prioridade": por.sort_values("horas_acima_meta", ascending=False), "backlog": backlog,
            "mediana_h": float(medidos.duracao_h.median()) if len(medidos) else np.nan}


# ---------------------------------------------------------------- classificador (dataset 2)

def _pasta_modelos():
    pasta = os.path.join(os.environ.get("G4_SESSOES", sessoes.BASE), "_modelos")
    os.makedirs(pasta, exist_ok=True)
    return pasta


def treinar_classificador(treino, semente=42, usar_cache=True):
    """TF-IDF + regressao logistica, avaliado em 20% dos textos que o modelo nunca viu."""
    d = treino[["texto", "categoria"]].dropna().astype(str)
    chave = hashlib.md5(pd.util.hash_pandas_object(d, index=False).values.tobytes()).hexdigest()[:16]
    arquivo = os.path.join(_pasta_modelos(), f"classificador_{chave}.joblib")
    if usar_cache and os.path.exists(arquivo):
        return joblib.load(arquivo)
    x_tr, x_te, y_tr, y_te = train_test_split(d.texto, d.categoria, test_size=0.2, stratify=d.categoria, random_state=semente)
    modelo = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=3, sublinear_tf=True, max_features=150000),
                           LogisticRegression(C=5, max_iter=1000, class_weight="balanced"))
    modelo.fit(x_tr, y_tr)
    proba = modelo.predict_proba(x_te)
    pred = modelo.classes_[proba.argmax(1)]
    conf = proba.max(1)
    prec, rec, f1, sup = precision_recall_fscore_support(y_te, pred, labels=modelo.classes_, zero_division=0)
    por_classe = pd.DataFrame({"categoria": modelo.classes_, "precisão": prec, "recall": rec, "f1": f1, "tickets_teste": sup})
    base = make_pipeline(TfidfVectorizer(min_df=3, sublinear_tf=True), ComplementNB(alpha=0.3)).fit(x_tr, y_tr)
    pred_nb = base.predict(x_te)
    teste = pd.DataFrame({"texto": x_te.values, "real": y_te.values, "previsto": pred, "confianca": conf})
    resultado = {
        "modelo": modelo, "n_treino": len(x_tr), "n_teste": len(x_te), "classes": list(modelo.classes_),
        "acuracia": accuracy_score(y_te, pred), "f1_macro": f1_score(y_te, pred, average="macro"),
        "por_classe": por_classe.sort_values("f1"),
        "confusao": pd.DataFrame(confusion_matrix(y_te, pred, labels=modelo.classes_), index=modelo.classes_, columns=modelo.classes_),
        "comparacao": pd.DataFrame([
            {"abordagem": "TF-IDF (palavras e pares de palavras) + regressão logística", "acurácia": accuracy_score(y_te, pred),
             "f1_macro": f1_score(y_te, pred, average="macro"), "observação": "escolhida: melhor acerto e dá a confiança de cada previsão"},
            {"abordagem": "TF-IDF + Naive Bayes (linha de base simples)", "acurácia": accuracy_score(y_te, pred_nb),
             "f1_macro": f1_score(y_te, pred_nb, average="macro"), "observação": "mais rápida, acerta menos"},
            {"abordagem": "Chute na categoria mais comum", "acurácia": float((y_te == y_tr.mode()[0]).mean()), "f1_macro": np.nan,
             "observação": "o mínimo que qualquer modelo precisa superar"},
        ]),
        "teste": teste,
    }
    joblib.dump(resultado, arquivo)
    return resultado


def faixas_de_confianca(clf, p: Premissas):
    t = clf["teste"]
    faixas = [("Automático", t.confianca >= p.confianca_auto),
              ("IA sugere, humano confirma", (t.confianca >= p.confianca_humano) & (t.confianca < p.confianca_auto)),
              ("Direto para humano", t.confianca < p.confianca_humano)]
    linhas = []
    for nome, m in faixas:
        sub = t[m]
        linhas.append({"faixa": nome, "tickets_%": 100 * m.mean(), "acerto_%": 100 * (sub.real == sub.previsto).mean() if len(sub) else np.nan,
                       "tickets_teste": int(m.sum())})
    return pd.DataFrame(linhas)


def decidir(texto, clf, p: Premissas, tipo=None, prioridade=None, top=3):
    """Protótipo: o que acontece com um ticket novo."""
    m = clf["modelo"]
    proba = m.predict_proba([texto])[0]
    ordem = np.argsort(proba)[::-1][:top]
    categoria, conf = m.classes_[ordem[0]], float(proba[ordem[0]])
    motivos_humano = []
    if tipo in p.nunca_automatizar_tipos:
        motivos_humano.append(f"tipo '{tipo}' envolve dinheiro ou perda de cliente")
    if prioridade in p.nunca_automatizar_prioridades:
        motivos_humano.append(f"prioridade '{prioridade}'")
    if categoria in p.nunca_automatizar_categorias:
        motivos_humano.append(f"categoria '{categoria}' (acesso/permissão = risco de segurança)")
    if motivos_humano or conf < p.confianca_humano:
        decisao = "Direto para humano"
        if conf < p.confianca_humano:
            motivos_humano.append(f"confiança baixa ({conf:.0%})")
    elif conf >= p.confianca_auto:
        decisao = "Automático"
    else:
        decisao = "IA sugere, humano confirma"
    return {"categoria": categoria, "confianca": conf, "decisao": decisao, "motivos": motivos_humano,
            "alternativas": [(m.classes_[i], float(proba[i])) for i in ordem]}


def similares(texto, clf, n=3):
    """Tickets reais parecidos (do conjunto de teste), para o agente ver casos anteriores."""
    vet = clf["modelo"][0]
    t = clf["teste"]
    base = vet.transform(t.texto)
    q = vet.transform([texto])
    sim = (base @ q.T).toarray().ravel()
    idx = np.argsort(sim)[::-1][:n]
    return t.iloc[idx].assign(similaridade=sim[idx])[["texto", "real", "similaridade"]]


def sinal_do_texto_ds1(c):
    """O texto do dataset 1 carrega o tipo do chamado? (se nao, a classificacao tem que vir do dataset 2)"""
    if "texto" not in c or "tipo" not in c or c["tipo"].nunique() < 2:
        return None
    txt = c["texto"].astype(str).str.replace("{product_purchased}", "", regex=False)
    x = TfidfVectorizer(min_df=2).fit_transform(txt)
    acc = cross_val_score(LogisticRegression(max_iter=1000), x, c["tipo"].astype(str), cv=3).mean()
    return {"acuracia": float(acc), "acaso": 1 / c["tipo"].nunique(), "placeholder_%": 100 * c["texto"].astype(str).str.contains("{product_purchased}", regex=False).mean()}


# ---------------------------------------------------------------- automacao, exemplos e ROI

def automacao(c, clf, p: Premissas):
    if clf is None:
        return None
    faixas = faixas_de_confianca(clf, p)
    bloqueio = pd.Series(False, index=c.index)
    motivos = {}
    if "tipo" in c:
        m = c["tipo"].isin(p.nunca_automatizar_tipos)
        motivos["Tipo cancelamento/reembolso"] = int(m.sum())
        bloqueio |= m
    if "prioridade" in c:
        m = c["prioridade"].isin(p.nunca_automatizar_prioridades)
        motivos["Prioridade crítica"] = int(m.sum())
        bloqueio |= m
    elegiveis = int((~bloqueio).sum())
    cobertura_auto = float((clf["teste"].confianca >= p.confianca_auto).mean())
    cobertura_sug = float(((clf["teste"].confianca >= p.confianca_humano) & (clf["teste"].confianca < p.confianca_auto)).mean())
    mes = p.tickets_por_mes or len(c) / 12
    fracao_eleg = elegiveis / len(c) if len(c) else 0
    auto_mes = mes * fracao_eleg * cobertura_auto
    sug_mes = mes * fracao_eleg * cobertura_sug
    horas = (auto_mes * p.minutos_triagem + sug_mes * p.minutos_triagem * 0.5) / 60     # sugestao economiza metade
    return {"faixas": faixas, "bloqueados_por_regra": motivos, "bloqueados_total": int(bloqueio.sum()),
            "elegiveis": elegiveis, "fracao_elegivel": fracao_eleg, "tickets_mes": mes,
            "auto_mes": auto_mes, "sugestao_mes": sug_mes, "humano_mes": mes - auto_mes - sug_mes,
            "horas_mes": horas, "reais_mes": horas * p.custo_hora, "automatizado_%": 100 * auto_mes / mes if mes else 0}


def exemplos_nao_automatizar(c, clf, p: Premissas, n=3):
    """Exemplos REAIS dos dados para justificar o que fica com humano."""
    ex = {}
    if "tipo" in c and "texto" in c:
        for tipo in p.nunca_automatizar_tipos:
            sub = c[c["tipo"] == tipo]
            if len(sub):
                col = [x for x in ("id_chamado", "tipo", "prioridade", "canal", "texto") if x in sub]
                ex[f"Tipo '{tipo}' (DS1)"] = sub[col].head(n)
    if clf is not None:
        t = clf["teste"]
        for cat in p.nunca_automatizar_categorias:
            sub = t[t.real == cat]
            if len(sub):
                ex[f"Categoria '{cat}' (DS2): erros do modelo"] = sub[sub.real != sub.previsto].head(n)[["texto", "real", "previsto", "confianca"]]
        ex["Baixa confiança (DS2): o modelo não tem certeza"] = t[t.confianca < p.confianca_humano].head(n)[["texto", "real", "previsto", "confianca"]]
    return ex


def qualidade(c, info, sinal_ds1):
    itens = []
    itens.append(f"Base com {len(c):,} chamados.".replace(",", "."))
    if "duracao_negativa" in info:
        itens.append(f"Tempo: {info['regra_duracao']}. Dos {info['duracao_com_datas']} chamados com as duas datas, "
                     f"{info['duracao_negativa']} têm a resolução ANTES da 1ª resposta e ficaram de fora. Sobram "
                     f"{info['n_duracao_valida']} com duração válida.")
    else:
        itens.append(f"Tempo: {info['regra_duracao']}.")
    if "satisfacao" in c:
        itens.append(f"Satisfação existe em {int(c.satisfacao.notna().sum())} chamados ({100 * c.satisfacao.notna().mean():.0f}%); "
                     "os demais estão sem nota e ficam de fora dessa parte.")
    if sinal_ds1:
        itens.append(f"O texto do Dataset 1 não indica o tipo do chamado: um classificador treinado nele acerta "
                     f"{100 * sinal_ds1['acuracia']:.0f}%, igual ao acaso ({100 * sinal_ds1['acaso']:.0f}%). "
                     f"{sinal_ds1['placeholder_%']:.0f}% das descrições têm o marcador '{{product_purchased}}' não preenchido. "
                     "Por isso o classificador é treinado no Dataset 2.")
    if "resolucao_texto" in c:
        itens.append("Os textos de resolução do Dataset 1 são frases aleatórias (sem relação com o problema): não servem "
                     "para 'respostas sugeridas'.")
    return itens


# ---------------------------------------------------------------- orquestracao

def analisar(tabs, p: Premissas | None = None, clf=None):
    p = p or Premissas()
    c, info = preparar(tabs["chamados"])
    if clf is None and "treino" in tabs:
        clf = treinar_classificador(tabs["treino"])
    s1 = sinal_do_texto_ds1(c)
    return {"premissas": p, "info": info, "chamados": c, "volume": volume(c), "gargalos": gargalos(c),
            "satisfacao": satisfacao(c), "desperdicio": desperdicio(c, p), "classificador": clf,
            "automacao": automacao(c, clf, p), "exemplos": exemplos_nao_automatizar(c, clf, p),
            "sinal_ds1": s1, "qualidade": qualidade(c, info, s1)}
