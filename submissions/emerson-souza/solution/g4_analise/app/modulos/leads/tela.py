"""Tela do modulo Leads: resumo, minha segunda-feira, visao do gestor, o que muda a chance, plano, validacao, relatorio."""

import json
import os
from dataclasses import asdict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import servicos
from nucleo import leitura, sessoes, visual
from nucleo.exportar import botao_salvar
from nucleo.visual import cores, selo, selo_evidencia
from nucleo.carregar import tabelas_da_sessao
from . import relatorio
from .analise import Premissas, analisar
from .textos import dec, explicacao_metodo, md, moeda, num, pct, resumo_executivo

AZUL, VERMELHO, LARANJA, CINZA, VERDE = "#2E86AB", "#D1495B", "#F2A541", "#9AA5B1", "#3BB273"
CORES_FAIXA = {"Quente": VERMELHO, "Morno": LARANJA, "Frio": AZUL, "Parado": CINZA}
COLS_LISTA = ["id_oportunidade", "vendedor", "produto", "conta", "score", "faixa", "motivos", "proxima_acao",
              "valor_esperado", "valor", "idade_dias", "gestor", "regiao", "setor"]


@st.cache_resource(show_spinner="Calculando o score dos deals (só na primeira vez)...", max_entries=12)
def _analisar(sessao_id, versoes, premissas_json):
    """Resultado guardado no disco (servicos.analisar_com_cache) e na memoria: trocar de aba nao recalcula nada."""
    return servicos.analisar_com_cache(sessoes.obter(sessao_id), json.loads(premissas_json))


def premissas_na_tela(chave):
    p = Premissas()
    with st.expander("Premissas da análise (mude e tudo é recalculado)", icon=":material/tune:"):
        c1, c2, c3 = st.columns(3)
        hoje = c1.date_input("Data de 'hoje' (vazio = última data da base)", value=None, key=f"{chave}_hoje", format="DD/MM/YYYY")
        ind = c1.toggle("Usar fatores sem comprovação (marcados como indício)", p.usar_indicios, key=f"{chave}_ind",
                        help="Desligado: só entram fatores com diferença estatística (p < 0,10) e o tempo aberto.")
        suav = c1.number_input("Suavização (deals virtuais na média)", 0, 1000, p.suavizacao, 10, key=f"{chave}_suav",
                               help="Quanto maior, menos um grupo pequeno puxa o score.")
        lim = c2.number_input("Parado depois de (dias) — 0 = maior ciclo já fechado", 0, 1000, 0, 5, key=f"{chave}_lim")
        pen = c2.slider("Pontos tirados de deal parado", 0, 50, int(p.penalidade_parado), 5, key=f"{chave}_pen")
        q = c3.slider("Quente = topo do pipeline (%)", 10, 50, int(p.quente_pct), 1, key=f"{chave}_q")
        f = c3.slider("Frio = base do pipeline (%)", 10, 50, int(p.frio_pct), 1, key=f"{chave}_f")
    return Premissas(data_hoje=str(hoje) if hoje else None, usar_indicios=ind, suavizacao=int(suav),
                     limite_parado_dias=int(lim) if lim else None, penalidade_parado=float(pen), quente_pct=float(q), frio_pct=float(f))


def render(sessao):
    p = premissas_na_tela(sessao["id"])
    versoes = tuple(os.path.getmtime(c) for c in sessao["arquivos"].values())
    try:
        r = _analisar(sessao["id"], versoes, json.dumps(asdict(p), sort_keys=True, default=list))
    except (KeyError, ValueError) as erro:
        st.error(f"Não deu para calcular o score: {erro}. Confira o De/Para na aba Dados.")
        return None
    abas = st.tabs(visual.abas(["Resumo executivo", "Minha segunda-feira", "Visão do gestor", "O que muda a chance",
                    "Plano de ação", "Validação e método", "Qualidade dos dados", "Relatório", "Como ler"]))
    with abas[0]:
        aba_resumo(r)
    with abas[1]:
        aba_segunda(r, sessao["id"])
    with abas[2]:
        aba_gestor(r)
    with abas[3]:
        aba_fatores(r)
    with abas[4]:
        aba_acoes(r)
    with abas[5]:
        aba_validacao(r)
    with abas[6]:
        for q in r["qualidade"]:
            st.write("• " + md(q))
    with abas[7]:
        aba_relatorio(r, sessao)
    with abas[8]:
        aba_como_ler()
    return r


# ------------------------------------------------------------------ abas

def aba_resumo(r):
    ab = r["abertos"]
    c = st.columns(4)
    c[0].metric("Deals abertos", num(len(ab)))
    c[1].metric("Parados", pct(100 * ab.parado.mean()), help="Abertos há mais tempo que qualquer deal já fechado")
    c[2].metric("Valor esperado", moeda(ab.valor_esperado.sum()), help="Soma de chance × preço")
    c[3].metric("Ganho histórico", pct(100 * r["cortes"]["base"]))
    st.subheader("O que está acontecendo")
    for linha in resumo_executivo(r):
        st.markdown("• " + md(linha))
    cont = ab.faixa.value_counts().reindex(["Quente", "Morno", "Frio", "Parado"]).fillna(0)
    fig = go.Figure(go.Bar(x=cont.index, y=cont.values, marker_color=[CORES_FAIXA[k] for k in cont.index],
                           text=[num(v) for v in cont.values], textposition="outside"))
    fig.update_layout(height=280, title="Deals abertos por faixa", margin=dict(t=40, b=10), yaxis_title="deals")
    st.plotly_chart(fig, width="stretch")


def _filtros(ab, chave):
    c = st.columns(4)
    for i, (col, rot) in enumerate((("vendedor", "Vendedor"), ("gestor", "Manager"), ("regiao", "Região"), ("produto", "Produto"))):
        if col in ab:
            esc = c[i].multiselect(rot, sorted(ab[col].dropna().astype(str).unique()), key=f"{chave}_f_{col}", placeholder="Todos")
            if esc:
                ab = ab[ab[col].astype(str).isin(esc)]
    return ab


def _tabela_deals(df, nome_arquivo, chave):
    cols = [c for c in COLS_LISTA if c in df]
    df = df[cols].copy()
    for c in ("conta", "setor"):
        if c in df:
            df[c] = df[c].fillna("—")
    st.dataframe(df, hide_index=True, width="stretch",
                 column_config={"id_oportunidade": "deal","score": st.column_config.ProgressColumn("score", min_value=0, max_value=100, format="%d"),
                                "valor": st.column_config.NumberColumn("preço", format="%.0f"),
                                "valor_esperado": st.column_config.NumberColumn("valor esperado", format="%.0f"),
                                "idade_dias": st.column_config.NumberColumn("dias aberto", format="%.0f"),
                                "motivos": st.column_config.TextColumn("por quê (3 principais motivos)", width="large"),
                                "proxima_acao": st.column_config.TextColumn("próxima ação", width="medium")})
    botao_salvar(st, "Salvar lista (CSV)", lambda: df.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"), nome_arquivo, key=f"dl_{chave}")


def aba_segunda(r, chave):
    st.subheader("Onde focar esta semana")
    st.caption("Escolha você mesmo (vendedor) ou o seu time (manager/região). As listas já vêm na ordem de ataque.")
    ab = _filtros(r["abertos"], chave)
    vivos = ab[ab.lista == "Foco"]
    par = ab[ab.parado].sort_values("valor", ascending=False)
    prosp = ab[ab.lista == "Prospecção"]
    c = st.columns(3)
    c[0].metric("1 · Foco (vivos)", num(len(vivos)))
    c[0].caption(md(moeda(vivos.valor_esperado.sum()) + " de valor esperado"))
    c[1].metric("2 · Requalificar (parados)", num(len(par)))
    c[1].caption(md(moeda(par.valor.sum()) + " em preço de tabela"))
    c[2].metric("3 · Prospecção", num(len(prosp)))
    c[2].caption(md(moeda(prosp.valor_esperado.sum()) + " de valor esperado"))
    t1, t2, t3 = st.tabs(["1 · Foco da semana", "2 · Requalificar", "3 · Prospecção"])
    with t1:
        st.caption("Deals vivos, do maior para o menor valor esperado (chance × preço).")
        _tabela_deals(vivos, "foco_da_semana.csv", f"{chave}_v")
    with t2:
        st.caption("Abertos há mais tempo que qualquer deal já fechado: confirmar se existem. Ordem: maior preço primeiro.")
        _tabela_deals(par, "requalificar.csv", f"{chave}_p")
    with t3:
        st.caption("Sem data de início: fazer o primeiro contato. Ordem: maior valor esperado primeiro.")
        _tabela_deals(prosp, "prospeccao.csv", f"{chave}_r")

    st.subheader("Por que este deal tem este score?")
    if len(ab):
        opcoes = ab.head(300)
        idc = "id_oportunidade" if "id_oportunidade" in ab else None
        esc = st.selectbox("Deal", opcoes.index, key=f"{chave}_deal",
                           format_func=lambda i: f"{opcoes.loc[i, idc] if idc else i} · {opcoes.loc[i, 'vendedor']} · "
                                                 f"{opcoes.loc[i, 'produto']} · score {opcoes.loc[i, 'score']:.0f}")
        d = ab.loc[esc]
        c = st.columns(4)
        c[0].metric("Score (chance %)", f"{d.score:.0f}")
        c[1].metric("Faixa", d.faixa)
        c[2].metric("Preço", moeda(d.valor) if pd.notna(d.valor) else "—")
        c[3].metric("Valor esperado", moeda(d.valor_esperado) if pd.notna(d.valor_esperado) else "—")
        st.markdown("**Motivos:** " + md(d.motivos))
        st.markdown("**Cálculo completo:** `" + d.conta_do_score + "`")
        st.markdown("**Próxima ação:** " + d.proxima_acao)


def aba_gestor(r):
    v = r["vendedores"].copy()
    st.subheader("Pipeline por vendedor")
    c1, c2 = st.columns(2)
    if "gestor" in v:
        g = c1.multiselect("Manager", sorted(v.gestor.dropna().unique()), key="gest_m", placeholder="Todos")
        if g:
            v = v[v.gestor.isin(g)]
    if "regiao" in v:
        rg = c2.multiselect("Região", sorted(v.regiao.dropna().unique()), key="gest_r", placeholder="Todas")
        if rg:
            v = v[v.regiao.isin(rg)]
    fig = px.bar(v.sort_values("parados_%"), x="parados_%", y="vendedor", orientation="h", color="parados_%",
                 color_continuous_scale=["#DCEAF2", VERMELHO], hover_data=["abertos", "parados", "gestor"] if "gestor" in v else None,
                 height=max(300, 22 * len(v)))
    fig.update_layout(xaxis_title="% do pipeline parado", yaxis_title="", coloraxis_showscale=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    st.caption("Quanto maior a barra, mais deals esquecidos na carteira do vendedor: é onde a conversa de gestão rende mais.")
    st.dataframe(v.round(1), hide_index=True, width="stretch",
                 column_config={"valor_esperado": st.column_config.NumberColumn("valor esperado", format="%.0f")})
    fig = px.scatter(v, x="taxa_historica_%", y="valor_esperado", size="abertos", hover_name="vendedor",
                     color="regiao" if "regiao" in v else None, height=360)
    fig.update_layout(xaxis_title="% de ganho histórico", yaxis_title="valor esperado em aberto", margin=dict(t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    f = r["fatores"].get("vendedor")
    if f:
        st.caption(f"Diferença de ganho entre vendedores: p = {dec(f['p_valor'], 3)} ({f['evidencia']}). "
                   "Se não é comprovada, não use a taxa de ganho para cobrar pessoas.")
    c = r["concentracao"]
    if c:
        st.subheader("Concentração do valor esperado")
        st.write(f"As 10 contas com mais valor esperado somam **{pct(c['top10_%'])}** do total (dos deals com conta cadastrada).")
        st.dataframe(c["top10"].round(0), hide_index=True, width="stretch")


def aba_fatores(r):
    st.subheader("O que o histórico diz sobre a chance de ganhar")
    fat = r["fatores"]
    if fat:
        esc = st.radio("Fator", list(fat), format_func=lambda k: fat[k]["rotulo"], horizontal=True)
        f = fat[esc]
        t = f["tabela"]
        base = 100 * r["cortes"]["base"]
        fig = go.Figure(go.Bar(x=t.grupo.astype(str), y=t["taxa_%"], marker_color=cores(len(t)),
                               error_y=dict(type="data", symmetric=False, array=t["ic_max_%"] - t["taxa_%"], arrayminus=t["taxa_%"] - t["ic_min_%"])))
        fig.add_hline(y=base, line_dash="dot", annotation_text=f"média {base:.0f}%")
        fig.update_layout(height=380, yaxis_title="% de ganho", margin=dict(t=10, b=10), yaxis_range=[0, 100])
        st.plotly_chart(fig, width="stretch")
        st.caption(f"p = {dec(f['p_valor'], 3)} → **{f['evidencia']}**. A barrinha é o intervalo de 95%: se cruza a linha da média, "
                   f"o grupo pode ser igual à média. {'Entra no score.' if f['usado'] else 'Não entra no score (premissa).'}")
        st.dataframe(t.round(1), hide_index=True, width="stretch")
    c = r["curva"]
    if c:
        st.subheader("Tempo aberto: a chance dos deals que chegaram a cada idade")
        t = c["tabela"]
        fig = go.Figure(go.Scatter(x=t.idade_dias, y=t["taxa_%"], mode="lines", line_color=AZUL, customdata=t.deals,
                                   hovertemplate="%{x} dias: %{y:.0f}% (n=%{customdata})<extra></extra>"))
        fig.add_hline(y=100 * r["cortes"]["base"], line_dash="dot", annotation_text="média")
        fig.add_vline(x=r["cortes"]["limite_parado"], line_color=VERMELHO, annotation_text="a partir daqui: parado")
        fig.update_layout(height=340, xaxis_title="dias aberto", yaxis_title="% de ganho", margin=dict(t=10, b=10))
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Perdidos fecham rápido (mediana {dec(c['mediana_perdido'], 0)} dias) e ganhos demoram mais "
                   f"(mediana {dec(c['mediana_ganho'], 0)} dias). Nenhum deal fechado passou de {c['max_ciclo']} dias.")


def aba_acoes(r):
    ac = r["acoes"]
    st.subheader("Plano de ação — ordenado pela força da evidência")
    for a in ac.itertuples():
        cor = selo_evidencia(a.evidencia)
        with st.container(border=True):
            st.markdown(f"**{a.prioridade}. {a.acao}** {cor}")
            st.write(md(a.o_que_fazer))
            c = st.columns(2)
            c[0].metric("Deals", num(a.deals))
            c[1].metric("Valor envolvido", moeda(a.valor))
            st.caption(md("Por quê: " + a.por_que))
    st.caption("Selo verde = fato nos dados · azul = cálculo (chance × preço) · cinza = sem evidência.")


def aba_validacao(r):
    v = r["validacao"]
    st.subheader("O score acerta? Teste numa foto do passado")
    if v:
        c = st.columns(3)
        c[0].metric("AUC do score", dec(v["auc"]), help="0,50 = acaso; 1,00 = perfeito")
        c[1].metric("AUC só pelo preço", dec(v["auc_so_valor"]))
        c[2].metric("Deals testados", num(v["n_teste"]))
        st.write(f"Em {v['data_foto']:%d/%m/%Y} o sistema aprendeu só com os {num(v['n_treino'])} deals que já tinham fechado e "
                 f"pontuou os {num(v['n_teste'])} que estavam abertos. Depois conferimos quem ganhou.")
        fig = px.bar(v["por_faixa"], x="faixa", y="taxa_real", color="faixa", color_discrete_map=CORES_FAIXA,
                     text=v["por_faixa"].taxa_real.map(lambda x: f"{x:.0f}%"))
        fig.add_hline(y=v["taxa_teste"], line_dash="dot", annotation_text="média do teste")
        fig.update_layout(height=300, showlegend=False, yaxis_title="% que ganhou de verdade", margin=dict(t=10, b=10))
        st.plotly_chart(fig, width="stretch")
        st.caption("Se as barras ficam parecidas, o score não separa ganho de perda nesta base. A lista continua útil porque "
                   "ordena por valor e separa o que está vivo do que está parado, que são fatos.")
    else:
        st.info("Histórico insuficiente para o teste (precisa de datas de início e fechamento).")
    st.subheader("Como os números foram calculados")
    for x in explicacao_metodo(r):
        st.markdown("• " + md(x))


def aba_relatorio(r, sessao):
    st.write("Relatório para a Head de RevOps: resumo, plano, listas de foco e requalificação, time, método e limitações.")
    md_txt = relatorio.markdown(r, sessao["nome"])
    c1, c2 = st.columns(2)
    botao_salvar(c1, "Salvar PDF", lambda: relatorio.pdf(r, sessao["nome"]), "priorizacao_pipeline.pdf", key=f"pdf_{sessao['id']}")
    botao_salvar(c2, "Salvar Markdown", md_txt, "priorizacao_pipeline.md", key=f"md_{sessao['id']}")
    with st.expander("Pré-visualizar"):
        st.markdown(md_txt)


def aba_como_ler():
    st.markdown("""
**Score** — a chance estimada de ganhar o deal, de 0 a 100. Começa na média do histórico e cada fator soma ou tira pontos.
Os **3 motivos** mostram os fatores que mais pesaram, com o número de pontos (ex.: "+7: aberto há 95 dias…").

**Faixas** — Quente, Morno e Frio dividem os deals vivos pelo score. **Parado** = aberto há mais tempo do que qualquer deal
que já fechou: provavelmente esquecido.

**Valor esperado** — chance × preço. É a ordem das listas: um deal grande com chance média vem antes de um pequeno com
chance alta, e vice-versa quando a diferença de chance é grande.

**Minha segunda-feira** — filtre por você (vendedor) ou pelo time. Ataque na ordem: 1 · Foco, 2 · Requalificar,
3 · Prospecção. Selecione um deal para ver a conta completa do score.

**Visão do gestor** — quem tem mais pipeline parado, valor esperado por vendedor e concentração em poucas contas.

**O que muda a chance** — a taxa de ganho de cada grupo, com intervalo de confiança e o teste. "Indício" e "não comprovada"
= diferença que pode ser acaso.

**Validação** — o teste honesto: o score aprende com o passado e é conferido em deals que ele não viu.

**Premissas** (no topo) — data de hoje, uso dos indícios, limite de parado e tamanho das faixas: tudo recalcula na hora.
""")
