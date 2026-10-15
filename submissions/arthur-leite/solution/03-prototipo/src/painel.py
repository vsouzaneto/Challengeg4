"""
Painel "Resposta ao Diretor": cálculos e gráficos da 1ª tela do app.

Regra deste módulo: nenhum número é digitado à mão se puder ser recalculado dos dados com o MESMO
método dos scripts oficiais. Cada função indica o script/arquivo de origem que ela reproduz:

  diagnostico_ds1()  ->  01-diagnostico/01_auditoria_dados.py  (seção 4b + seção 2 de outputs/auditoria.md)
  fora_do_dominio()  ->  benchmark/avaliar_motor.py            (seção 3 de outputs/motor_final.md)
  politica_ds2()     ->  src/politica.py (docstring: 23,4%)  e  proposta.md (tabela do "não automatizar")
  BENCHMARK_LLM      ->  benchmark/outputs/benchmark.md (as chamadas ao LLM não são refeitas no app:
                         custam cota da API; os números são os do arquivo, com a mesma casa decimal)

Compatível com pandas 2.2 e 3 (colunas de texto via .to_numpy(dtype=object)).
"""
from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import chi2_contingency, norm

from .politica import REGRAS, ROTULOS, avaliar
from .triagem import RAIZ, MotorTriagem, preparar

DS1 = RAIZ / "data/ds1_customer_support/customer_support_tickets.csv"
CSAT = "Customer Satisfaction Rating"

# ---------------------------------------------------------------- paleta e formatação
VERDE, AMBAR, VERMELHO = "#2E7D32", "#F9A825", "#C62828"
NEUTRO, NEUTRO_CLARO, DESTAQUE = "#64748B", "#CBD5E1", "#1E3A5F"
COR_FAIXA = {"auto": VERDE, "sugere": AMBAR, "humano": VERMELHO}
NOME_FAIXA = {"auto": "Automático", "sugere": "Sugestão (humano confirma)", "humano": "Humano"}
NOME_CURTO = {"auto": "Automático", "sugere": "Sugestão", "humano": "Humano"}


def num(x: float, casas: int = 0) -> str:
    """Número no padrão brasileiro: 8.469 · 0,68 · 1.218 (mesma função `n` do 01_auditoria_dados.py)."""
    s = f"{x:,.{casas}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


def pct(x: float, casas: int = 1) -> str:
    """Fração -> percentual brasileiro: 0.655 -> 65,5%."""
    return num(100 * x, casas) + "%"


# ---------------------------------------------------------------- benchmark (arquivo, não recalculado)
# benchmark/outputs/benchmark.md, seção 2 (acurácia; amostra de 400 tickets do teste, exceto onde indicado)
BENCHMARK_LLM = [
    # (rótulo curto, descrição, acurácia, n, é o modelo escolhido?)
    ("Modelo treinado no histórico", "TF-IDF + regressão logística", 0.850, 400, True),
    ("LLM + 5 tickets parecidos", "Gemini flash-lite com os 5 tickets mais parecidos do histórico no prompt (RAG)", 0.769, 399, False),
    ("5 tickets parecidos, sem LLM", "voto dos 5 tickets mais parecidos do histórico (kNN-5)", 0.760, 400, False),
    ("LLM mais forte + exemplos", "Gemini 3.8 flash com 3 exemplos por categoria (n = 200, limite de cota)", 0.535, 200, False),
    ("LLM + exemplos", "Gemini flash-lite com 3 exemplos por categoria", 0.480, 400, False),
    ("LLM só com nomes", "Gemini flash-lite só com o nome das categorias", 0.440, 400, False),
]


# ---------------------------------------------------------------- diagnóstico (Dataset 1)
def diagnostico_ds1(caminho: Path = DS1, n_perm: int = 1000, semente: int = 0) -> dict:
    """Reproduz 01_auditoria_dados.py: durações, CSAT e o teste de permutação das 80 combinações.

    Mesma semente (default_rng(0)) e mesmas 1.000 permutações do script. A média por grupo é feita
    com np.bincount em vez de groupby (mesmo resultado, ~20x mais rápido), aplicada à MESMA sequência
    de permutações sobre o MESMO vetor de durações na mesma ordem.
    """
    d = pd.read_csv(caminho)
    frt = pd.to_datetime(d["First Response Time"])
    ttr = pd.to_datetime(d["Time to Resolution"])
    dur = (ttr - frt).dt.total_seconds() / 3600
    validos = dur.notna()
    neg = int((dur < 0).sum())

    janela_h = (max(frt.max(), ttr.max()) - min(frt.min(), ttr.min())).total_seconds() / 3600
    notas_brutas = d[CSAT].dropna()
    notas = notas_brutas.astype(int).value_counts().sort_index()
    # poder estatístico: menor diferença de CSAT detectável entre 2 grupos (80% de poder, alfa 5%)
    grupo = len(notas_brutas) / 4
    mde = (norm.ppf(0.975) + norm.ppf(0.8)) * notas_brutas.std() * np.sqrt(2 / grupo)
    # pares de variáveis categóricas com associação significativa (qui-quadrado, p < 0,05)
    categoricas = ["Ticket Type", "Ticket Subject", "Ticket Priority", "Ticket Channel",
                   "Product Purchased", "Customer Gender", "Ticket Status"]
    pares = [chi2_contingency(pd.crosstab(d[a], d[b]))[1] for a, b in itertools.combinations(categoricas, 2)]

    chaves = ["Ticket Channel", "Ticket Priority", "Ticket Type"]
    f = d[d["Ticket Status"] == "Closed"].assign(duracao_h=dur)
    g = f.groupby(chaves)["duracao_h"].agg(["mean", "count"])
    ordem = g.sort_values("mean", ascending=False)
    amplitude = float(ordem["mean"].iloc[0] - ordem["mean"].iloc[-1])

    codigos = f.groupby(chaves).ngroup().to_numpy(dtype=np.int64)
    contagem = np.bincount(codigos)
    valores = f["duracao_h"].to_numpy(dtype=float)
    rng = np.random.default_rng(semente)
    acaso = np.empty(n_perm)
    for i in range(n_perm):
        medias = np.bincount(codigos, weights=rng.permutation(valores)) / contagem
        acaso[i] = medias.max() - medias.min()

    def rotulo(idx) -> str:
        return " · ".join(idx)

    return {
        "n_tickets": len(d),
        "n_fechados": int(validos.sum()),
        "n_negativos": neg,
        "frac_negativos": neg / int(validos.sum()),
        "janela_h": janela_h,
        "csat_diferenca_detectavel": float(mde),
        "n_pares": len(pares),
        "n_pares_associados": int(sum(p < 0.05 for p in pares)),
        "duracoes_h": dur[validos].to_numpy(dtype=float),
        "csat": notas,                                   # nota -> quantidade
        "n_combinacoes": len(g),
        "gap_observado_h": amplitude,
        "gap_acaso_h": acaso,
        "gap_acaso_medio_h": float(acaso.mean()),
        "p_permutacao": float((acaso >= amplitude).mean()),
        "pior": (rotulo(ordem.index[0]), float(ordem["mean"].iloc[0])),
        "melhor": (rotulo(ordem.index[-1]), float(ordem["mean"].iloc[-1])),
    }


def fora_do_dominio(motor: MotorTriagem, caminho: Path = DS1) -> dict:
    """Reproduz a seção 3 do avaliar_motor.py: tickets de cliente (outro domínio) no motor de TI."""
    d1 = pd.read_csv(caminho)
    x1 = d1["Ticket Description"].str.replace(r"\{[^}]*\}", " ", regex=True).map(preparar)
    r1 = motor.classificar_lote(x1)
    lim = np.array([motor.limiares[c] for c in r1["categoria"].to_numpy(dtype=object)])
    return {"n": len(r1), "auto_com_travas": float((r1["faixa"] == "auto").mean()),
            "auto_sem_travas": float((r1["confianca"].to_numpy(dtype=float) >= lim).mean())}


def politica_ds2(textos: pd.Series) -> dict:
    """Frequência de cada regra do 'não automatizar' nos 47.837 tickets do Dataset 2 (src/politica.py)."""
    pol = textos.map(avaliar)
    regras = pd.Series([a for p in pol for a in p.alertas]).value_counts()
    return {"n": len(textos),
            "frac_alguma_regra": float(pol.map(lambda p: p.exige_humano_para_executar).mean()),
            "por_regra": {k: (int(regras.get(k, 0)), regras.get(k, 0) / len(textos)) for k in REGRAS}}


def faixas(av: pd.DataFrame) -> dict:
    """Resumo das 3 faixas no conjunto de teste (mesmo cálculo do avaliar_motor.py, seções 1 e 2)."""
    tot = len(av)
    out = {"n": tot}
    for f in ["auto", "sugere", "humano"]:
        g = av[av["faixa"] == f]
        out[f] = {"frac": len(g) / tot, "acerto": float(g["acertou"].mean()), "top2": float(g["acertou_top2"].mean())}
    hum = av[av["faixa"] == "humano"]
    out["humano_trava"] = float((hum["motivo_humano"] == "trava de domínio").sum() / tot)
    out["humano_confianca"] = float((hum["motivo_humano"] == "confiança baixa").sum() / tot)
    auto = av[av["faixa"] == "auto"]
    out["por_categoria"] = (auto.groupby("categoria")["acertou"].agg(["mean", "size"])
                            .rename(columns={"mean": "acerto", "size": "tickets"}).sort_values("acerto"))
    return out


# ---------------------------------------------------------------- gráficos
def _layout(fig: go.Figure, altura: int = 300, **kw) -> go.Figure:
    kw.setdefault("margin", dict(l=8, r=8, t=8, b=8))
    fig.update_layout(height=altura, showlegend=False,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(size=13), separators=",.", hoverlabel=dict(font_size=13), **kw)
    return fig


def fig_duracoes(dur: np.ndarray) -> go.Figure:
    """Histograma das 'durações' (resolução − 1ª resposta): metade é negativa."""
    bordas = np.arange(np.floor(dur.min()), np.ceil(dur.max()) + 1, 1.0)
    cont, _ = np.histogram(dur, bins=bordas)
    centros = bordas[:-1] + 0.5
    cores = [VERMELHO if c < 0 else NEUTRO for c in centros]
    fig = go.Figure(go.Bar(x=centros, y=cont, marker_color=cores, marker_line_width=0,
                           hovertemplate="%{x:.0f} h: %{y} tickets<extra></extra>"))
    fig.add_vline(x=0, line_width=2, line_color="rgba(127,127,127,.9)")
    zero = (0 - bordas[0]) / (bordas[-1] - bordas[0])   # posição do zero em coordenadas do papel
    fig.add_annotation(x=zero, y=1, xref="paper", yref="paper", text="<b>◄ impossível</b>",
                       showarrow=False, xanchor="right", yanchor="bottom", xshift=-4, font=dict(color=VERMELHO, size=11))
    fig.add_annotation(x=zero, y=1, xref="paper", yref="paper", text="positiva ►", showarrow=False,
                       xanchor="left", yanchor="bottom", xshift=4, font=dict(color=NEUTRO, size=11))
    fig.update_xaxes(title_text="horas entre 1ª resposta e resolução", ticksuffix=" h", zeroline=False,
                     range=[bordas[0], bordas[-1]])
    fig.update_yaxes(title_text="tickets", showgrid=True, gridcolor="rgba(127,127,127,.15)")
    return _layout(fig, bargap=0.08, margin=dict(l=8, r=8, t=26, b=8))


def fig_csat(csat: pd.Series) -> go.Figure:
    """Notas de 1 a 5 com a mesma frequência: satisfação sorteada."""
    fig = go.Figure(go.Bar(x=[str(i) for i in csat.index], y=csat.to_numpy(), marker_color=NEUTRO,
                           text=[num(v) for v in csat.to_numpy()], textposition="outside",
                           hovertemplate="nota %{x}: %{y} clientes<extra></extra>"))
    media = csat.mean()
    fig.add_hline(y=media, line_dash="dot", line_color="rgba(127,127,127,.8)")
    fig.update_xaxes(title_text="nota de satisfação (1 a 5)", type="category")
    fig.update_yaxes(title_text="clientes", range=[0, csat.max() * 1.25], showgrid=True, gridcolor="rgba(127,127,127,.15)")
    return _layout(fig, bargap=0.35)


def fig_permutacao(acaso: np.ndarray, observado: float, p: float) -> go.Figure:
    """Distribuição do 'gap pior − melhor' produzido pelo acaso × o gap observado."""
    fig = go.Figure(go.Histogram(x=acaso, nbinsx=30, marker_color=NEUTRO_CLARO, marker_line_width=0,
                                 hovertemplate="gap de %{x} h: %{y} sorteios<extra></extra>"))
    fig.add_vline(x=observado, line_width=3, line_color=DESTAQUE)
    fig.add_annotation(x=observado, y=1, yref="paper", text=f"<b>dados reais: {num(observado, 1)} h</b>",
                       showarrow=False, xanchor="center", yanchor="bottom", font=dict(color=DESTAQUE, size=12))
    fig.add_annotation(x=1, y=0.6, xref="paper", yref="paper", xanchor="right", yanchor="middle", showarrow=False,
                       text=f"o acaso empata<br>ou supera os dados<br>reais em <b>{num(100 * p)}%</b><br>dos sorteios",
                       font=dict(size=12, color=NEUTRO), align="right")
    fig.update_xaxes(title_text="diferença 'pior − melhor' combinação (h)", ticksuffix=" h")
    fig.update_yaxes(title_text="sorteios ao acaso", showgrid=True, gridcolor="rgba(127,127,127,.15)")
    return _layout(fig, bargap=0.05, margin=dict(l=8, r=8, t=26, b=8))


def fig_faixas(fx: dict) -> go.Figure:
    """Barra única 100%: quanto da fila cai em cada faixa."""
    fig = go.Figure()
    for f in ["auto", "sugere", "humano"]:
        v = fx[f]["frac"]
        fig.add_trace(go.Bar(y=[""], x=[100 * v], orientation="h", marker_color=COR_FAIXA[f], marker_line_width=0,
                             text=f"<b>{pct(v)}</b>", textposition="inside", insidetextanchor="middle", textangle=0,
                             textfont=dict(color="#1F2937" if f == "sugere" else "white", size=14),
                             hovertemplate=f"{NOME_FAIXA[f]}: {pct(v)} dos tickets<extra></extra>"))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(visible=False, range=[0, 100])
    fig.update_yaxes(visible=False)
    return _layout(fig, altura=70, margin=dict(l=0, r=0, t=0, b=0))


def fig_acerto_categoria(por_cat: pd.DataFrame) -> go.Figure:
    """Acerto da faixa automática por categoria, com a régua de 95%."""
    traducao = {"Access": "Acessos", "Administrative rights": "Direitos de administrador", "HR Support": "Suporte de RH",
                "Hardware": "Hardware", "Internal Project": "Projeto interno", "Miscellaneous": "Diversos",
                "Purchase": "Compras", "Storage": "Armazenamento"}
    y = [traducao.get(c, c) for c in por_cat.index]
    x = 100 * por_cat["acerto"].to_numpy(dtype=float)
    fig = go.Figure(go.Bar(y=y, x=x, orientation="h", marker_color=VERDE, marker_line_width=0,
                           text=[pct(v / 100) for v in x], textposition="outside", cliponaxis=False,
                           customdata=por_cat["tickets"].to_numpy(),
                           hovertemplate="%{y}: %{x:.1f}% de acerto em %{customdata} tickets<extra></extra>"))
    fig.add_vline(x=95, line_dash="dash", line_color=VERMELHO, line_width=1.5)
    fig.add_annotation(x=95, y=1.0, yref="paper", text="mínimo exigido: 95%", showarrow=False, xanchor="right",
                       yanchor="bottom", xshift=-4, font=dict(size=11, color=VERMELHO))
    fig.update_xaxes(range=[90, 101.6], tickvals=[90, 95, 100], ticktext=["90%", "95%", "100%"], showgrid=True, gridcolor="rgba(127,127,127,.15)")
    return _layout(fig, altura=300, margin=dict(l=8, r=8, t=22, b=8))


def fig_benchmark() -> go.Figure:
    """Modelo simples × LLM: acerto na mesma amostra de tickets."""
    dados = list(reversed(BENCHMARK_LLM))
    rot = [r[0] for r in dados]
    x = [100 * r[2] for r in dados]
    cores = [DESTAQUE if r[4] else NEUTRO_CLARO for r in dados]
    fig = go.Figure(go.Bar(y=rot, x=x, orientation="h", marker_color=cores, marker_line_width=0,
                           text=[pct(r[2]) for r in dados], textposition="outside", cliponaxis=False,
                           customdata=[[r[1], r[3]] for r in dados],
                           hovertemplate="%{customdata[0]}<br>%{x:.1f}% de acerto em %{customdata[1]} tickets<extra></extra>"))
    fig.update_xaxes(range=[0, 108], tickvals=[0, 25, 50, 75, 100], ticktext=["0%", "25%", "50%", "75%", "100%"], showgrid=True,
                     gridcolor="rgba(127,127,127,.15)")
    fig.update_yaxes(automargin=True)
    return _layout(fig, altura=300)


# ---------------------------------------------------------------- CSS do app
CSS = """
<style>
:root{
  --verde:#2E7D32; --ambar:#F9A825; --vermelho:#C62828; --destaque:#1E3A5F; --neutro:#64748B;
  --borda:rgba(127,127,127,.22); --fundo-card:rgba(127,127,127,.06); --texto-suave:rgba(127,127,127,1);
}
.block-container{max-width:1180px; padding-top:2.2rem; padding-bottom:3rem;}
h1,h2,h3{letter-spacing:-.01em;}
.kicker{font-size:.78rem; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:var(--texto-suave); margin-bottom:.2rem;}
.hero h1{font-size:2.05rem; line-height:1.15; margin:.1rem 0 .5rem 0; padding:0;}
.hero .lead{font-size:1.12rem; line-height:1.5; max-width:880px; margin:0 0 .6rem 0;}
.hero .pedido{display:inline-block; font-size:.92rem; border:1px solid var(--borda); border-left:4px solid var(--destaque);
  border-radius:8px; padding:.45rem .8rem; background:var(--fundo-card);}
.cards{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin:1.1rem 0 .4rem 0;}
.card{border:1px solid var(--borda); background:var(--fundo-card); border-radius:12px; padding:14px 16px 16px; border-top:4px solid var(--neutro);}
.card .q{font-size:.76rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--texto-suave);}
.card .big{font-size:2.1rem; font-weight:700; line-height:1.1; margin:.35rem 0 .1rem 0;}
.card .sub{font-size:.85rem; color:var(--texto-suave); line-height:1.35; min-height:2.3em;}
.card .ans{font-size:.98rem; line-height:1.4; margin-top:.55rem; font-weight:500;}
.card.c1{border-top-color:var(--vermelho);} .card.c1 .big{color:var(--vermelho);}
.card.c2{border-top-color:var(--verde);} .card.c2 .big{color:var(--verde);}
.card.c3{border-top-color:var(--destaque);}
.card.c4{border-top-color:var(--ambar);}
.secao{display:flex; align-items:center; gap:.7rem; margin:2.4rem 0 .2rem 0; padding-top:1.2rem; border-top:1px solid var(--borda);}
.secao .n{flex:0 0 auto; width:2rem; height:2rem; border-radius:50%; background:var(--destaque); color:#fff; font-weight:700;
  display:flex; align-items:center; justify-content:center; font-size:1rem;}
.secao .t{font-size:1.45rem; font-weight:700; line-height:1.2;}
.secao-sub{font-size:1.02rem; margin:.2rem 0 1rem 2.7rem; color:var(--texto-suave); max-width:900px;}
.graf-tit{font-weight:650; font-size:1rem; margin:.2rem 0 .1rem 0; line-height:1.3;}
.graf-leg{font-size:.86rem; color:var(--texto-suave); line-height:1.4; margin-bottom:.3rem;}
.kpis{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:.6rem 0 .4rem 0;}
.kpi{border:1px solid var(--borda); border-radius:10px; padding:10px 14px; background:var(--fundo-card);}
.kpi .v{font-size:1.6rem; font-weight:700; line-height:1.15;}
.kpi .l{font-size:.84rem; color:var(--texto-suave); line-height:1.35;}
.regras{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:.4rem 0;}
.regra{border:1px solid var(--borda); border-left:4px solid var(--vermelho); border-radius:10px; padding:10px 14px; background:var(--fundo-card);}
.regra .h{display:flex; justify-content:space-between; align-items:baseline; gap:.5rem; font-weight:700;}
.regra .h span{font-weight:600; font-size:.85rem; color:var(--texto-suave); white-space:nowrap;}
.regra .a{font-size:.88rem; line-height:1.4; margin-top:.25rem;}
.fluxo{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:.5rem 0 .8rem 0;}
.passo{border:1px solid var(--borda); border-radius:10px; padding:10px 12px; background:var(--fundo-card); font-size:.88rem; line-height:1.4;}
.passo b{display:block; font-size:.95rem; margin-bottom:.15rem;}
.exemplos{display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:.4rem 0;}
.ex{border:1px solid var(--borda); border-radius:10px; padding:10px 12px; background:var(--fundo-card); font-size:.86rem; line-height:1.4;}
.ex .txt{font-style:italic; min-height:3.6em;}
.ex .res{margin-top:.45rem; font-weight:600;}
.pill{display:inline-block; padding:.08rem .55rem; border-radius:999px; font-size:.78rem; font-weight:700; color:#fff; white-space:nowrap;}
.pill.auto{background:var(--verde);} .pill.sugere{background:var(--ambar); color:#1F2937;} .pill.humano{background:var(--vermelho);}
.pill.escalado{background:#7F1D1D;} .pill.neutro{background:var(--neutro);}
.cenarios{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:.4rem 0;}
.cen{border:1px solid var(--borda); border-radius:12px; padding:12px 16px; background:var(--fundo-card);}
.cen.base{border:2px solid var(--destaque);}
.cen .nome{font-size:.78rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--texto-suave);}
.cen .h{font-size:1.9rem; font-weight:700; line-height:1.15; margin:.2rem 0;}
.cen .d{font-size:.86rem; line-height:1.45; color:var(--texto-suave);}
.decisoes{display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:.4rem 0 .8rem 0;}
.dec{border:1px solid var(--borda); border-radius:12px; padding:12px 16px; background:var(--fundo-card); border-top:4px solid var(--destaque);}
.dec .n{font-size:.78rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase; color:var(--texto-suave);}
.dec .t{font-weight:700; font-size:1.02rem; margin:.2rem 0 .25rem 0; line-height:1.3;}
.dec .d{font-size:.88rem; line-height:1.45;}
.nota{font-size:.86rem; color:var(--texto-suave); line-height:1.45;}
.veredito{border:1px solid var(--borda); border-left:4px solid var(--destaque); border-radius:10px; padding:.7rem 1rem;
  background:var(--fundo-card); line-height:1.5; margin:.6rem 0;}
.decisao-ticket{border-radius:12px; padding:14px 18px; margin:.6rem 0; color:#fff;}
.decisao-ticket .rot{font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; opacity:.9; font-weight:700;}
.decisao-ticket .fila{font-size:1.5rem; font-weight:700; line-height:1.2; margin:.15rem 0;}
.decisao-ticket .det{font-size:.92rem; opacity:.95;}
.decisao-ticket.auto{background:var(--verde);} .decisao-ticket.sugere{background:var(--ambar); color:#1F2937;}
.decisao-ticket.humano{background:var(--vermelho);} .decisao-ticket.escalado{background:#7F1D1D;}
@media (max-width: 900px){
  .cards,.fluxo,.exemplos{grid-template-columns:repeat(2,minmax(0,1fr));}
  .regras,.decisoes,.cenarios{grid-template-columns:repeat(2,minmax(0,1fr));}
}
@media (max-width: 600px){
  .cards,.fluxo,.exemplos,.regras,.decisoes,.cenarios,.kpis{grid-template-columns:1fr;}
  .hero h1{font-size:1.6rem;} .secao .t{font-size:1.2rem;} .secao-sub{margin-left:0;}
  .card .big{font-size:1.8rem;}
}
</style>
"""
