"""Tela do modulo Churn: resumo, causa raiz, segmentos e contas, plano de acao, metodo, qualidade, relatorio."""

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
from .analise import SINAIS, Premissas, analisar
from .textos import correlacao_causalidade, dec, explicacao_metodo, md, moeda, valor, pct, resumo_executivo

AZUL, VERMELHO, CINZA = "#2E86AB", "#D1495B", "#9AA5B1"


@st.cache_resource(show_spinner="Analisando os dados de churn (só na primeira vez)...", max_entries=12)
def _analisar(sessao_id, versoes, premissas_json):
    """Resultado guardado no disco (servicos.analisar_com_cache) e na memoria: trocar de aba nao recalcula nada."""
    return servicos.analisar_com_cache(sessoes.obter(sessao_id), json.loads(premissas_json))


def premissas_na_tela(chave):
    padrao = Premissas()
    with st.expander("Premissas da análise (mude e tudo é recalculado)", icon=":material/tune:"):
        c1, c2, c3 = st.columns(3)
        janela = c1.slider("Janela de uso (dias)", 30, 180, padrao.janela_dias, 15, key=f"{chave}_jan",
                           help="Uso recente = últimos N dias; anterior = os N dias antes disso.")
        queda = c1.slider("Queda de uso que acende o alerta (%)", 10, 80, int(padrao.queda_pct), 5, key=f"{chave}_queda")
        sat = c2.slider("Satisfação 'baixa' é nota até", 1, 5, int(padrao.satisfacao_baixa), key=f"{chave}_sat")
        lim = c2.number_input("Resposta lenta acima de (min) — 0 = automático (percentil 75)", 0, 10000, 0, 10,
                              key=f"{chave}_lim")
        rec = c3.slider("Taxa de recuperação das ações (%)", 5, 60, int(padrao.taxa_recuperacao_pct), 5, key=f"{chave}_rec",
                        help="Premissa de quanto do MRR em risco as ações conseguem salvar. Usada no impacto estimado.")
        pelos_dados = c3.toggle("Pesos do score pelos dados", padrao.pesos_pelos_dados, key=f"{chave}_modo",
                                help="Ligado: só pontua o sinal que mostrou diferença nos dados (p < 0,10). "
                                     "Desligado: use os pesos de regra de negócio abaixo.")
        pesos = dict(padrao.pesos)
        if not pelos_dados:
            st.caption("Pesos de regra de negócio (somam o score de 0 a 100):")
            cols = st.columns(len(pesos))
            for col, (k, v) in zip(cols, padrao.pesos.items()):
                pesos[k] = col.number_input(SINAIS[k], 0, 100, v, 5, key=f"{chave}_p_{k}")
    return Premissas(janela_dias=janela, queda_pct=float(queda), satisfacao_baixa=float(sat),
                     limite_resposta_min=float(lim) if lim else None, taxa_recuperacao_pct=float(rec),
                     pesos_pelos_dados=pelos_dados, pesos=pesos)


def render(sessao):
    p = premissas_na_tela(sessao["id"])
    versoes = tuple(os.path.getmtime(c) for c in sessao["arquivos"].values())
    d = asdict(p)
    try:
        r = _analisar(sessao["id"], versoes, json.dumps(asdict(p), sort_keys=True, default=list))
    except KeyError as erro:
        st.error(f"Falta um campo obrigatório nos dados para esta análise: {erro}. Confira o De/Para na aba Dados.")
        return None
    abas = st.tabs(visual.abas(["Resumo executivo", "Causa raiz", "Segmentos e contas", "Plano de ação",
                    "Modelo e método", "Qualidade dos dados", "Relatório", "Como ler"]))
    with abas[0]:
        aba_resumo(r)
    with abas[1]:
        aba_causa(r)
    with abas[2]:
        aba_segmentos(r)
    with abas[3]:
        aba_acoes(r)
    with abas[4]:
        aba_modelo(r)
    with abas[5]:
        for q in r["qualidade"]:
            st.write("• " + q)
    with abas[6]:
        aba_relatorio(r, sessao)
    with abas[7]:
        aba_como_ler()
    return r


# ------------------------------------------------------------------ abas

def aba_resumo(r):
    b = r["base"]
    c = st.columns(4)
    c[0].metric("Taxa de churn", pct(100 * b["taxa_churn"], 1), help="Contas canceladas / total")
    c[1].metric("Contas canceladas", f"{b['canceladas']:,} de {b['clientes']:,}".replace(",", "."))
    rot = ("Clientes perdidos", "Clientes ativos") if b.get("sem_receita") else ("MRR perdido / mês", "MRR ativo / mês")
    c[2].metric(rot[0], valor(r, b["mrr_perdido"]))
    c[3].metric(rot[1], valor(r, b["mrr_ativo"]))
    st.subheader("O que está acontecendo")
    for linha in resumo_executivo(r):
        st.markdown("• " + md(linha))
    st.info(md(correlacao_causalidade()))


def aba_causa(r):
    st.subheader("1. O paradoxo do CEO: 'o uso cresceu' e 'a satisfação está ok'")
    par = r["paradoxo"]
    c1, c2 = st.columns(2)
    if "uso_trimestral" in par:
        t = par["uso_trimestral"]
        fig = go.Figure([go.Bar(x=t.trimestre, y=t.uso, name="uso total", marker_color=cores(len(t)))])
        fig.update_layout(title="Uso total por trimestre", height=320, margin=dict(t=40, b=20))
        c1.plotly_chart(fig, width="stretch")
        c1.caption(f"Variação do 1º ao último trimestre: {pct(par['variacao_uso_%'], 1)}. O uso está estável; "
                   "não é o uso agregado que explica o churn.")
    if "satisfacao" in par:
        sa = par["satisfacao"]
        fig = go.Figure([go.Bar(x=["Cancelaram", "Ficaram"], y=[sa["media_canceladas"], sa["media_ativas"]],
                                marker_color=[VERMELHO, AZUL], text=[f"{dec(sa['media_canceladas'])}", f"{dec(sa['media_ativas'])}"])])
        fig.update_layout(title="Satisfação média (1 a 5)", yaxis_range=[0, 5], height=320, margin=dict(t=40, b=20))
        c2.plotly_chart(fig, width="stretch")
        c2.caption(f"Quem cancelou não estava menos satisfeito (p = {dec(sa['p_valor'])}). "
                   f"{pct(sa['sem_resposta_%'])} dos chamados não têm avaliação: a 'satisfação ok' mede só quem respondeu.")

    st.subheader("2. Motivos declarados no cancelamento")
    mot = r["motivos"]
    fig = px.bar(mot, x="%", y="motivo", orientation="h", text=mot["%"].map(lambda v: f"{v:.0f}%"),
                 hover_data={"contas": True, "mrr_perdido": ":,.0f"}, color="motivo", color_discrete_sequence=cores(len(mot)))
    fig.update_layout(height=300, yaxis={"categoryorder": "total ascending"}, margin=dict(t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    st.caption("Motivo = último evento de cancelamento de cada conta cancelada. 'sem registro' = conta cancelada sem evento.")

    st.subheader("3. Sinais de comportamento: separam quem sai de quem fica?")
    s = r["sinais"]
    if len(s):
        longo = s.melt(id_vars=["sinal", "p_valor", "evidencia"], value_vars=["churn_com_sinal_%", "churn_sem_sinal_%"],
                       var_name="grupo", value_name="churn_%")
        longo["grupo"] = longo.grupo.map({"churn_com_sinal_%": "com o sinal", "churn_sem_sinal_%": "sem o sinal"})
        fig = px.bar(longo, x="sinal", y="churn_%", color="grupo", barmode="group",
                     color_discrete_map={"com o sinal": VERMELHO, "sem o sinal": CINZA})
        fig.add_hline(y=100 * r["base"]["taxa_churn"], line_dash="dot", annotation_text="média")
        fig.update_layout(height=340, margin=dict(t=10, b=10), yaxis_title="% de churn")
        st.plotly_chart(fig, width="stretch")
        st.dataframe(s.drop(columns="chave").round({"churn_com_sinal_%": 1, "churn_sem_sinal_%": 1, "diferenca_pp": 1, "p_valor": 3}),
                     hide_index=True, width="stretch")
        st.caption("Se a barra vermelha não fica acima da cinza com p < 0,05, o sinal não explica o churn nesta base.")
    else:
        st.info("Sem dados de uso/chamados: sinais de comportamento não puderam ser testados.")


def aba_segmentos(r):
    st.subheader("Churn por perfil de cliente")
    segs = r["segmentos"]
    escolha = st.selectbox("Ver por", list(segs), format_func=lambda k: segs[k]["rotulo"])
    seg = segs[escolha]
    tab = seg["tabela"]
    fig = go.Figure(go.Bar(
        x=tab.grupo, y=tab["taxa_%"], marker_color=[VERMELHO if v > seg["media_%"] + 5 else AZUL for v in tab["taxa_%"]],
        error_y=dict(type="data", symmetric=False, array=tab["ic_max_%"] - tab["taxa_%"], arrayminus=tab["taxa_%"] - tab["ic_min_%"]),
        text=[f"{v:.0f}% (n={n})" for v, n in zip(tab["taxa_%"], tab.contas)], textposition="inside", insidetextanchor="start"))
    fig.add_hline(y=seg["media_%"], line_dash="dot", annotation_text=f"média {seg['media_%']:.0f}%")
    fig.update_layout(height=380, yaxis_title="% de churn", margin=dict(t=20, b=10))
    st.plotly_chart(fig, width="stretch")
    veredito = ("diferença comprovada" if seg["p_valor"] < 0.05 else "indício de diferença" if seg["p_valor"] < 0.10
                else "sem diferença estatística")
    st.caption(f"Teste entre os grupos: p = {dec(seg['p_valor'], 3)} → **{veredito}**. "
               "As barras de erro mostram o intervalo de 95%: se cruzam a linha da média, o grupo pode ser igual à média.")
    st.dataframe(tab.round(1), hide_index=True, width="stretch")

    st.subheader("Contas ativas priorizadas (risco × valor)")
    a = r["ativos"].copy()
    c1, c2 = st.columns([1, 3])
    filtro = c1.multiselect("Prioridade", sorted(a.prioridade.unique()), default=sorted(a.prioridade.unique())[:2])
    if escolha in a:
        grupos = c2.multiselect(seg["rotulo"], sorted(a[escolha].dropna().unique()))
        if grupos:
            a = a[a[escolha].isin(grupos)]
    a = a[a.prioridade.isin(filtro)] if filtro else a
    fig = px.scatter(r["ativos"], x="score_risco", y="mrr", color="prioridade", hover_name=r["ativos"].index,
                     hover_data={"motivos_do_score": True}, height=360,
                     color_discrete_map={"1 · Salvar agora": VERMELHO, "2 · Acompanhar": "#F2A541", "3 · Monitorar": CINZA})
    fig.update_layout(xaxis_title="Score de risco (0–100)", yaxis_title="MRR (US$/mês)", margin=dict(t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    colunas = [c for c in ["nome_cliente", "prioridade", "score_risco", "mrr", "mrr_em_risco", "motivos_do_score",
                           "segmento", "canal_aquisicao", "plano", "pais"] if c in a]
    st.dataframe(a[colunas].round(0), width="stretch")
    botao_salvar(st, "Salvar lista (CSV)", lambda: a[colunas].to_csv(sep=";", decimal=",").encode("utf-8-sig"), "contas_priorizadas.csv", key="dl_contas")


def aba_acoes(r):
    ac = r["acoes"]
    st.subheader("Plano de ação — ordenado pela força da evidência, depois pelo impacto")
    if not len(ac):
        st.info("Nenhuma ação gerada com os dados atuais.")
        return
    st.metric("Impacto estimado das ações com evidência (≠ 'sem evidência')",
              valor(r, ac[~ac.evidencia.str.startswith("sem")].impacto_estimado_mrr.sum(), True),
              help="Soma do MRR das contas-alvo × taxa de recuperação. Contas podem aparecer em mais de uma ação.")
    for a in ac.itertuples():
        cor = selo_evidencia(a.evidencia)
        with st.container(border=True):
            st.markdown(f"**{a.prioridade}. {a.acao}** {cor}")
            st.write(a.o_que_fazer)
            c = st.columns(3)
            c[0].metric("Contas-alvo", a.contas)
            c[1].metric("Em jogo", valor(r, a.mrr_em_jogo))
            c[2].metric("Impacto estimado", valor(r, a.impacto_estimado_mrr, True))
            st.caption(md("Por quê: " + a.por_que))
            with st.expander("Ver contas"):
                st.write(", ".join(map(str, a.ids)))
    st.caption("Selo cinza = sem evidência nos dados: fica no fim da lista e deve ser testado antes de virar investimento.")
    st.subheader("Contas que precisam de suporte melhor")
    st.write(f"**{len(r['precisa_suporte'])} contas** em risco (score ≥ 30) com chamado escalado, resposta lenta ou "
             "satisfação baixa. Para analisar o atendimento delas, use a aba **Usar em outra ferramenta → Suporte** (no topo da sessão).")


def aba_modelo(r):
    st.subheader("O score explica quem cancelou?")
    s = r["mestra"]
    fig = px.box(s.assign(situacao=s.cancelou.map({True: "Cancelou", False: "Ativa"})), x="situacao", y="score_risco",
                 color="situacao", color_discrete_map={"Cancelou": VERMELHO, "Ativa": AZUL}, points=False, height=320)
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    st.caption(f"AUC do score = {dec(r['auc_score'])} (0,50 = acaso; 1,00 = perfeito). Medido na mesma base usada para "
               "definir os pesos, então é otimista.")
    st.write("**Pesos usados no score:** " + ", ".join(f"{SINAIS[k]} {v:.0f}" for k, v in r["premissas"].pesos.items() if v))
    m = r["modelo"]
    if m:
        st.subheader("Modelo preditivo (machine learning) — número honesto")
        c = st.columns(2)
        c[0].metric("Regressão logística (AUC)", f"{dec(m['auc_lr'][0])} ± {dec(m['auc_lr'][1])}")
        c[1].metric("Floresta aleatória (AUC)", f"{dec(m['auc_rf'][0])} ± {dec(m['auc_rf'][1])}")
        st.caption(f"Validação cruzada em 5 partes com {m['variaveis']} variáveis: o modelo nunca é avaliado nos dados em que "
                   "aprendeu. Resultado perto de 0,5 = os dados não permitem prever churn com confiança.")
        st.dataframe(m["coeficientes"].round(3), hide_index=True, width="stretch")
    st.subheader("Como os números foram calculados")
    for x in explicacao_metodo(r):
        st.markdown("• " + md(x))


def aba_relatorio(r, sessao):
    st.write("Relatório para o CEO com resumo, plano de ação, gráficos, método e limitações.")
    md_txt = relatorio.markdown(r, sessao["nome"])
    c1, c2 = st.columns(2)
    botao_salvar(c1, "Salvar PDF", lambda: relatorio.pdf(r, sessao["nome"]), "diagnostico_churn.pdf", key=f"pdf_{sessao['id']}")
    botao_salvar(c2, "Salvar Markdown", md_txt, "diagnostico_churn.md", key=f"md_{sessao['id']}")
    with st.expander("Pré-visualizar"):
        st.markdown(md_txt)


def aba_como_ler():
    st.markdown("""
**Resumo executivo** — a história em texto, com os números principais. Comece por aqui.

**Causa raiz** — testa as frases do CEO ('uso cresceu', 'satisfação ok'), mostra os motivos declarados e testa cada sinal
de comportamento: barra vermelha = churn de quem tem o sinal; cinza = de quem não tem. Só é causa provável se a vermelha
ficar bem acima **e** o p for menor que 0,05.

**Segmentos e contas** — churn por perfil com intervalo de confiança (a barrinha preta). Embaixo, as contas ativas
priorizadas por risco × valor, com o motivo de cada score. Dá para filtrar e baixar.

**Plano de ação** — o que fazer, para quais contas, quanto dinheiro está em jogo e o impacto estimado. A ordem segue a
força da evidência: selo verde = forte, laranja = indício ou regra de negócio, cinza = sem evidência.

**Modelo e método** — se o score e o machine learning conseguem separar quem cancela (AUC) e como cada número foi calculado.

**Premissas** (no topo) — mude a janela, os limites e a taxa de recuperação: tudo é recalculado na hora.
""")
