"""
Modulo Leads (desafio 003) - motor do score, sem tela.

Regras: PLANEJAMENTO.md secao 4.3. Padrao de entrega: secao 4.5.
Score = chance de ganhar (0-100), explicada em pontos: base historica + cada fator (vendedor, produto,
setor, porte, tempo aberto). Prioridade = valor esperado (chance x preco). Nada que so se sabe depois
de fechar entra no score (sem vazamento).
"""

import re
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score

from nucleo.carregar import para_data, para_numero

FATORES = {"vendedor": "Vendedor", "produto": "Produto", "setor": "Setor da conta", "porte": "Porte da conta"}
FATORES_DE_CONTA = ("setor", "porte")
GANHO = {"won", "ganho", "ganha", "ganhou", "closed won", "fechado ganho"}
PERDIDO = {"lost", "perdido", "perdida", "perdeu", "closed lost", "fechado perdido"}
CORRECOES_TEXTO = {"technolgy": "technology"}   # erros de digitacao achados nos dados
PORTES = ["Pequena", "Média", "Grande", "Muito grande"]


@dataclass
class Premissas:
    data_hoje: str | None = None           # None = ultima data da base
    usar_indicios: bool = True             # fatores sem comprovacao estatistica entram (marcados como indicio)
    suavizacao: int = 100                  # "deals virtuais" na media: grupo pequeno nao pesa demais
    limite_parado_dias: int | None = None  # None = maior ciclo ja fechado na base
    penalidade_parado: float = 20.0        # pontos tirados de deal parado alem do limite (hipotese)
    quente_pct: float = 33.0               # topo do pipeline que vira "Quente"
    frio_pct: float = 33.0                 # base do pipeline que vira "Frio"


# ---------------------------------------------------------------- utilidades

def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    margem = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centro - margem), min(1.0, centro + margem))


def _chave(texto):
    return re.sub(r"[^a-z0-9]", "", str(texto).lower())


def evidencia(p):
    if p != p:
        return "sem teste"
    return "comprovado" if p < 0.05 else "indício" if p < 0.10 else "sem comprovação"


# ---------------------------------------------------------------- preparo

def preparar(tabs, p: Premissas):
    op = tabs["oportunidades"].copy()
    info = {"correcoes": []}
    for c in ("vendedor", "produto", "estagio", "conta"):
        if c in op:
            op[c] = op[c].where(op[c].isna(), op[c].astype(str).str.strip())

    # produto escrito diferente da tabela de produtos (ex.: "GTXPro" x "GTX Pro")
    if "produtos" in tabs:
        pr = tabs["produtos"].copy()
        canon = {_chave(x): x for x in pr["produto"].astype(str)}
        novo = op["produto"].map(lambda x: canon.get(_chave(x), x))
        for antes, depois in pd.DataFrame({"a": op["produto"], "d": novo})[op["produto"] != novo].drop_duplicates().values:
            n = int((op["produto"] == antes).sum())
            info["correcoes"].append(f"Produto '{antes}' → '{depois}' ({n} deals): mesmo produto escrito diferente da tabela de produtos.")
        op["produto"] = novo
        cols = [c for c in ("produto", "serie", "preco") if c in pr]
        op = op.merge(pr[cols].drop_duplicates("produto"), on="produto", how="left")
    if "vendedores" in tabs:
        v = tabs["vendedores"]
        op = op.merge(v[[c for c in ("vendedor", "gestor", "regiao") if c in v]].drop_duplicates("vendedor"), on="vendedor", how="left")
    if "contas" in tabs and "conta" in op:
        ct = tabs["contas"].copy()
        if "setor" in ct:
            for errado, certo in CORRECOES_TEXTO.items():
                n = int((ct["setor"] == errado).sum())
                if n:
                    info["correcoes"].append(f"Setor '{errado}' → '{certo}' ({n} contas): erro de digitação.")
            ct["setor"] = ct["setor"].replace(CORRECOES_TEXTO)
        if "funcionarios" in ct:
            ct["porte"] = pd.qcut(para_numero(ct["funcionarios"]), 4, labels=PORTES, duplicates="drop").astype(str)
        cols = [c for c in ("conta", "setor", "porte", "local", "receita", "funcionarios") if c in ct]
        op = op.merge(ct[cols].drop_duplicates("conta"), on="conta", how="left")

    info["tem_datas"] = "data_inicio" in op
    est = op["estagio"].astype(str).str.lower()
    op["situacao"] = np.where(est.isin(GANHO), "ganho", np.where(est.isin(PERDIDO), "perdido", "aberto"))
    op["ganhou"] = op["situacao"] == "ganho"
    op["inicio"] = para_data(op["data_inicio"]) if "data_inicio" in op else pd.NaT
    op["fechamento"] = para_data(op["data_fechamento"]) if "data_fechamento" in op else pd.NaT
    datas = pd.concat([op["inicio"], op["fechamento"]]).dropna()
    hoje = pd.Timestamp(p.data_hoje) if p.data_hoje else (datas.max() if len(datas) else pd.Timestamp.today().normalize())
    info["hoje"] = hoje
    op["ciclo_dias"] = (op["fechamento"] - op["inicio"]).dt.days
    op["idade_dias"] = np.where(op["situacao"] == "aberto", (hoje - op["inicio"]).dt.days, np.nan)

    # valor do deal aberto: preco de tabela; sem tabela, mediana do valor fechado (ganhos) do mesmo produto
    if "valor" in op and para_numero(op["valor"]).notna().any():
        op["valor"] = para_numero(op["valor"])
        info["regra_valor"] = "valor informado em cada deal"
    elif "preco" in op:
        op["valor"] = para_numero(op["preco"])
        info["regra_valor"] = "preço de tabela do produto"
    elif "valor_fechado" in op:
        med = op[op.ganhou].assign(v=para_numero(op["valor_fechado"])).groupby("produto")["v"].median()
        op["valor"] = op["produto"].map(med)
        info["regra_valor"] = "mediana do valor dos deals ganhos do mesmo produto"
    else:
        op["valor"] = np.nan
        info["regra_valor"] = "sem valor na base"
    if "valor_fechado" in op and "preco" in op:
        g = op[op.ganhou]
        razao = para_numero(g["valor_fechado"]) / g["valor"]
        info["valor_fechado_sobre_preco"] = float(razao.median())
    return op, info


# ---------------------------------------------------------------- historico

def fatores(hist, p: Premissas):
    base = hist.ganhou.mean()
    m = p.suavizacao
    saida = {}
    for f, rotulo in FATORES.items():
        if f not in hist or hist[f].nunique() < 2:
            continue
        h = hist[hist[f].notna() & (hist[f].astype(str) != "nan")]
        g = h.groupby(f).agg(deals=("ganhou", "size"), ganhos=("ganhou", "sum"))
        g["taxa_%"] = 100 * g.ganhos / g.deals
        ic = [wilson(k, n) for k, n in zip(g.ganhos, g.deals)]
        g["ic_min_%"] = [100 * a for a, _ in ic]
        g["ic_max_%"] = [100 * b for _, b in ic]
        g["pontos"] = 100 * ((g.ganhos + m * base) / (g.deals + m) - base)
        tabela = pd.crosstab(h[f], h.ganhou)
        pv = float(stats.chi2_contingency(tabela)[1]) if tabela.shape[0] > 1 and tabela.shape[1] > 1 else np.nan
        ev = evidencia(pv)
        saida[f] = {"rotulo": rotulo, "tabela": g.sort_values("taxa_%", ascending=False).reset_index().rename(columns={f: "grupo"}),
                    "p_valor": pv, "evidencia": ev, "usado": ev in ("comprovado", "indício") or p.usar_indicios,
                    "amplitude": float(g["taxa_%"].max() - g["taxa_%"].min())}
    return saida


def curva_tempo(hist, min_n=30):
    """Taxa de ganho dos deals que CHEGARAM a cada idade (sobreviveram ate ali). Nao usa o futuro do deal."""
    h = hist.dropna(subset=["ciclo_dias"])
    if len(h) < min_n:
        return None
    dur = h.ciclo_dias.values
    ganhou = h.ganhou.values
    linhas = []
    for a in range(0, int(dur.max()) + 1):
        sel = dur >= a
        n = int(sel.sum())
        if n < min_n:
            break
        linhas.append({"idade_dias": a, "deals": n, "taxa_%": 100 * ganhou[sel].mean()})
    t = pd.DataFrame(linhas)
    ganhos, perdidos = h[h.ganhou].ciclo_dias, h[~h.ganhou].ciclo_dias
    return {"tabela": t, "max_ciclo": int(dur.max()), "mediana_ganho": float(ganhos.median()),
            "mediana_perdido": float(perdidos.median()),
            "p_valor": float(stats.mannwhitneyu(ganhos, perdidos)[1]) if len(ganhos) and len(perdidos) else np.nan}


# ---------------------------------------------------------------- score

def _frase_fator(f, grupo, taxa, base, ev):
    nomes = {"vendedor": f"vendedor {grupo}", "produto": f"produto {grupo}", "setor": f"conta do setor {grupo}",
             "porte": f"conta de porte {str(grupo).lower()}"}
    extra = "" if ev == "comprovado" else " (indício)" if ev == "indício" else " (diferença não comprovada)"
    return f"{nomes[f]} ganha {taxa:.0f}% dos deals (média {100 * base:.0f}%){extra}"


def pontuar(op, hist, fat, curva, p: Premissas, tem_datas=True):
    base = hist.ganhou.mean()
    ab = op[op.situacao == "aberto"].copy()
    limite = p.limite_parado_dias or (curva["max_ciclo"] if curva else None)
    tempo = curva["tabela"].set_index("idade_dias")["taxa_%"] if curva else pd.Series(dtype=float)
    idade_max_curva = int(tempo.index.max()) if len(tempo) else -1

    chances, motivos, detalhe, parado = [], [], [], []
    for _, d in ab.iterrows():
        pts = []
        for f, info in fat.items():
            if not info["usado"] or pd.isna(d.get(f)) or str(d.get(f)) == "nan":
                continue
            linha = info["tabela"].set_index("grupo")
            if d[f] not in linha.index:
                continue
            x = linha.loc[d[f]]
            pts.append((float(x.pontos), info["rotulo"], _frase_fator(f, d[f], x["taxa_%"], base, info["evidencia"])))
        esta_parado = False
        if pd.notna(d.idade_dias):
            a = int(d.idade_dias)
            if limite is not None and a > limite:
                esta_parado = True
                pts.append((-p.penalidade_parado, "Tempo aberto",
                            f"aberto há {a} dias, mais que o maior ciclo já fechado ({limite} dias): provável deal esquecido"))
            elif len(tempo):
                t = float(tempo.loc[min(a, idade_max_curva)])
                pts.append((t - 100 * base, "Tempo aberto", f"aberto há {a} dias: deals que chegam a essa idade ganham {t:.0f}%"))
        elif tem_datas:
            pts.append((0.0, "Tempo aberto", "sem data de início (ainda em prospecção): tempo não entra"))
        chance = float(np.clip(100 * base + sum(x[0] for x in pts), 1, 99))
        chances.append(chance)
        parado.append(esta_parado)
        top = sorted([x for x in pts if abs(x[0]) >= 0.5], key=lambda x: -abs(x[0]))[:3]
        motivos.append(" · ".join(f"{x[0]:+.0f}: {x[2]}" for x in top) or "nenhum fator muda a chance: fica na média")
        detalhe.append(f"base {100 * base:.0f}" + "".join(f" {x[0]:+.1f} ({x[1].lower()})" for x in pts) + f" = {chance:.0f}")
    ab["score"] = np.round(chances, 0)
    ab["parado"] = parado
    ab["motivos"] = motivos
    ab["conta_do_score"] = detalhe
    ab["valor_esperado"] = ab.score / 100 * ab.valor
    vivos = ab[~ab.parado]
    q_alto = np.percentile(vivos.score, 100 - p.quente_pct) if len(vivos) else 101
    q_baixo = np.percentile(vivos.score, p.frio_pct) if len(vivos) else -1
    ab["faixa"] = np.where(ab.parado, "Parado", np.where(ab.score >= q_alto, "Quente", np.where(ab.score <= q_baixo, "Frio", "Morno")))
    # em qual lista da segunda-feira o deal entra
    ab["lista"] = np.where(ab.parado, "Requalificar", np.where(ab.idade_dias.isna() & tem_datas, "Prospecção", "Foco"))
    ab["proxima_acao"] = [proxima_acao(d) for _, d in ab.iterrows()]
    ab = ab.sort_values(["valor_esperado", "score"], ascending=False)
    return ab, {"base": base, "limite_parado": limite, "corte_quente": q_alto, "corte_frio": q_baixo}


def proxima_acao(d):
    if d.faixa == "Parado":
        return "Confirmar com o cliente se o deal ainda existe; se não, fechar como perdido (limpa o pipeline)."
    if d.lista == "Prospecção":
        return "Fazer o primeiro contato e qualificar (necessidade, orçamento, decisor)."
    if d.faixa == "Quente":
        return "Prioridade da semana: marcar a conversa de fechamento."
    if d.faixa == "Morno":
        return "Avançar um passo concreto (demo, proposta ou reunião com o decisor)."
    return "Baixa prioridade: manter contato leve, sem tirar tempo dos quentes."


# ---------------------------------------------------------------- validacao (backtest honesto)

def validar(op, p: Premissas, frac=0.7):
    """Tira uma 'foto' do passado: aprende so com o que fechou ate a data D e pontua os deals que estavam
    abertos em D (resultado conhecido depois). Mede se o score separa quem ganhou de quem perdeu."""
    fech = op[op.situacao != "aberto"].dropna(subset=["fechamento"])
    if len(fech) < 100 or fech.inicio.isna().all():
        return None
    D = fech.fechamento.quantile(frac)
    treino = fech[fech.fechamento <= D]
    teste = fech[(fech.inicio <= D) & (fech.fechamento > D)].copy()
    if len(teste) < 50 or teste.ganhou.nunique() < 2:
        return None
    fat = fatores(treino, p)
    curva = curva_tempo(treino)
    teste["situacao"] = "aberto"
    teste["idade_dias"] = (D - teste.inicio).dt.days
    resultado = teste.ganhou.values
    sc, _ = pontuar(teste, treino, fat, curva, p)
    sc = sc.loc[teste.index]
    auc = float(roc_auc_score(resultado, sc.score))
    por_faixa = sc.assign(ganhou=resultado).groupby("faixa").agg(deals=("ganhou", "size"), taxa_real=("ganhou", "mean")).reset_index()
    por_faixa["taxa_real"] = 100 * por_faixa.taxa_real
    auc_valor = float(roc_auc_score(resultado, sc.valor.fillna(0))) if sc.valor.notna().any() else np.nan
    return {"data_foto": D, "n_treino": len(treino), "n_teste": len(teste), "auc": auc, "auc_so_valor": auc_valor,
            "por_faixa": por_faixa, "taxa_teste": 100 * float(resultado.mean())}


# ---------------------------------------------------------------- visoes para decidir

def por_vendedor(ab, hist):
    g = ab.groupby("vendedor").agg(abertos=("score", "size"), parados=("parado", "sum"),
                                   quentes=("faixa", lambda s: int((s == "Quente").sum())),
                                   valor_esperado=("valor_esperado", "sum"), score_medio=("score", "mean"))
    g["parados_%"] = 100 * g.parados / g.abertos
    g["taxa_historica_%"] = 100 * hist.groupby("vendedor").ganhou.mean().reindex(g.index)
    for c in ("gestor", "regiao"):
        if c in ab:
            g[c] = ab.groupby("vendedor")[c].first()
    return g.sort_values("valor_esperado", ascending=False).reset_index()


def concentracao(ab):
    if "conta" not in ab or ab.conta.isna().all():
        return None
    g = ab.dropna(subset=["conta"]).groupby("conta").valor_esperado.sum().sort_values(ascending=False)
    total = ab.valor_esperado.sum()
    return {"top10": g.head(10).reset_index(), "top10_%": 100 * float(g.head(10).sum() / total) if total else np.nan}


def acoes(ab, fat, curva, info):
    L = []
    par = ab[ab.parado]
    if len(par):
        L.append({"acao": "Limpar o pipeline: requalificar os deals parados",
                  "o_que_fazer": "Cada vendedor confirma com o cliente se o deal existe; o que não existe vira 'perdido'. "
                                 "Isso devolve tempo e deixa o forecast verdadeiro.",
                  "deals": len(par), "valor": float(par.valor.sum()),
                  "evidencia": "forte", "por_que": f"{len(par):,} deals ({100 * len(par) / len(ab):.0f}% dos abertos)".replace(",", ".") + f" estão abertos há mais "
                  f"tempo que qualquer deal já fechado na base ({curva['max_ciclo'] if curva else '?'} dias)."})
    vivos = ab[ab.lista == "Foco"]
    if len(vivos):
        top = vivos.head(max(1, int(0.2 * len(vivos))))
        L.append({"acao": "Foco da semana: os 20% de deals vivos com maior valor esperado",
                  "o_que_fazer": "Começar a segunda-feira por esta lista (chance × preço), não pelo maior valor nem pelo mais recente.",
                  "deals": len(top), "valor": float(top.valor_esperado.sum()), "evidencia": "cálculo",
                  "por_que": f"Eles concentram {100 * top.valor_esperado.sum() / max(vivos.valor_esperado.sum(), 1):.0f}% do valor esperado dos deals vivos."})
    prosp = ab[ab.lista == "Prospecção"]
    if len(prosp):
        sem = int(prosp.conta.isna().sum()) if "conta" in prosp else len(prosp)
        L.append({"acao": "Qualificar a prospecção",
                  "o_que_fazer": "Fazer o 1º contato e registrar a conta no CRM (sem conta o score não usa setor e porte).",
                  "deals": len(prosp), "valor": float(prosp.valor_esperado.sum()), "evidencia": "cálculo",
                  "por_que": f"{len(prosp)} deals ainda sem data de início; {sem} deles sem conta cadastrada."})
    if "vendedor" in fat:
        f = fat["vendedor"]
        pior = ab.groupby("vendedor").parado.mean().sort_values(ascending=False)
        L.append({"acao": "Gestão do time: cobrar higiene de pipeline, não taxa de ganho",
                  "o_que_fazer": f"A diferença de taxa de ganho entre vendedores ({f['tabela']['taxa_%'].min():.0f}% a "
                                 f"{f['tabela']['taxa_%'].max():.0f}%) {'é comprovada' if f['evidencia'] == 'comprovado' else 'não é comprovada (pode ser acaso)'}. "
                                 f"Já a parte do pipeline parado varia de {100 * pior.min():.0f}% a {100 * pior.max():.0f}% por vendedor.",
                  "deals": int(ab.parado.sum()), "valor": float(ab[ab.parado].valor.sum()),
                  "evidencia": "forte" if f["evidencia"] != "comprovado" else "comprovado",
                  "por_que": f"Teste de taxa de ganho por vendedor: p = {str(round(f['p_valor'], 2)).replace('.', ',')}. Maior % parado: {pior.index[0]}."})
    ordem = {"forte": 0, "comprovado": 0, "cálculo": 1, "indício": 2, "sem comprovação": 3}
    out = pd.DataFrame(L)
    if len(out):
        out = out.sort_values("evidencia", key=lambda s: s.map(ordem), kind="stable").reset_index(drop=True)
        out.insert(0, "prioridade", range(1, len(out) + 1))
    return out


def qualidade(op, info, fat):
    ab = op[op.situacao == "aberto"]
    def n(v):
        return f"{v:,}".replace(",", ".")
    itens = [f"Base com {n(len(op))} deals: {n(int(op.ganhou.sum()))} ganhos, {n(int((op.situacao == 'perdido').sum()))} "
             f"perdidos e {n(len(ab))} abertos."]
    itens += info["correcoes"]
    if info["tem_datas"]:
        itens.append(f"'Hoje' = {info['hoje']:%d/%m/%Y} (última data da base; editável nas premissas).")
    else:
        itens.append("A base não tem datas de negociação: o tempo aberto e o teste no passado não se aplicam.")
    if "conta" in op:
        n = int(ab.conta.isna().sum())
        if n:
            itens.append(f"{n} deals abertos sem conta cadastrada: o score deles não usa setor nem porte.")
    n = int(ab.inicio.isna().sum())
    if n and info["tem_datas"]:
        itens.append(f"{n} deals abertos sem data de início (estágio de prospecção): o tempo aberto não entra no score deles.")
    itens.append(f"Valor dos deals abertos: {info['regra_valor']}."
                 + (f" Nos ganhos, o valor fechado fica em {100 * info['valor_fechado_sobre_preco']:.0f}% do preço (mediana), "
                    "então o preço é uma boa aproximação." if "valor_fechado_sobre_preco" in info else ""))
    fracos = [f"{x['rotulo'].lower()} (p = {str(round(x['p_valor'], 2)).replace('.', ',')})" for x in fat.values() if x["evidencia"] == "sem comprovação"]
    if fracos:
        itens.append("Fatores com diferença pequena e não comprovada estatisticamente: " + ", ".join(fracos)
                     + ". Entram com peso reduzido (suavização) e marcados como tal; dá para desligar nas premissas.")
    if info["tem_datas"]:
        itens.append("A duração total do ciclo NÃO entra como fator (só se conhece depois de fechar = vazamento). "
                     "O que entra é a idade atual do deal comparada com os deals que chegaram à mesma idade.")
    return itens


# ---------------------------------------------------------------- orquestracao

def analisar(tabs, p: Premissas | None = None):
    p = p or Premissas()
    op, info = preparar(tabs, p)
    hist = op[op.situacao != "aberto"]
    if len(hist) < 30 or hist.ganhou.nunique() < 2:
        raise ValueError("É preciso ter deals ganhos e perdidos no histórico para aprender o score.")
    fat = fatores(hist, p)
    curva = curva_tempo(hist)
    ab, corte = pontuar(op, hist, fat, curva, p, tem_datas=info["tem_datas"])
    return {"premissas": p, "info": info, "deals": op, "historico": hist, "fatores": fat, "curva": curva,
            "abertos": ab, "cortes": corte, "validacao": validar(op, p), "vendedores": por_vendedor(ab, hist),
            "concentracao": concentracao(ab), "acoes": acoes(ab, fat, curva, info), "qualidade": qualidade(op, info, fat)}
