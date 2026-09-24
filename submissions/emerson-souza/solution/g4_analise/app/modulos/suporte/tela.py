"""Tela do modulo Suporte: onde trava, satisfacao, desperdicio, automacao, prototipo, relatorio."""

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
from nucleo.visual import cores, selo
from nucleo.carregar import tabelas_da_sessao
from . import relatorio
from .analise import Premissas, analisar, decidir, similares, treinar_classificador
from .textos import dec, explicacao_metodo, md, num, pct, reais, resumo_executivo

AZUL, VERMELHO, LARANJA, CINZA, VERDE = "#2E86AB", "#D1495B", "#F2A541", "#9AA5B1", "#3BB273"


@st.cache_resource(show_spinner="Treinando o classificador de tickets (só na primeira vez, ~30 s)...")
def _classificador(caminho, mapa, versao):
    tabs = tabelas_da_sessao({"modulo": "suporte", "arquivos": {"treino": caminho}, "mapeamento": {"treino": mapa}}, leitura.ler)
    return treinar_classificador(tabs["treino"])


@st.cache_resource(show_spinner="Analisando os chamados (só na primeira vez)...", max_entries=12)
def _analisar(sessao_id, versoes, premissas_json):
    """Resultado guardado no disco (servicos.analisar_com_cache) e na memoria: trocar de aba nao recalcula nada."""
    return servicos.analisar_com_cache(sessoes.obter(sessao_id), json.loads(premissas_json))


def premissas_na_tela(chave):
    p = Premissas()
    with st.expander("Premissas da análise (mude e tudo é recalculado)", icon=":material/tune:"):
        c1, c2, c3 = st.columns(3)
        custo = c1.number_input("Custo da hora do agente (R$)", 10.0, 500.0, p.custo_hora, 5.0, key=f"{chave}_custo")
        mes = c1.number_input("Tickets por mês (0 = volume da base ÷ 12)", 0, 1_000_000, 0, 100, key=f"{chave}_mes")
        tri = c1.number_input("Minutos de triagem por ticket", 1.0, 60.0, p.minutos_triagem, 1.0, key=f"{chave}_tri")
        c2.caption("Meta de tempo (SLA) por prioridade, em horas")
        sla = {}
        for k, v in (("critical", 4), ("high", 8), ("medium", 24), ("low", 48)):
            sla[k] = c2.number_input(k.capitalize(), 1, 500, v, key=f"{chave}_sla_{k}")
        sla["urgent"] = sla["critical"]
        auto = c3.slider("Confiança para automático", 0.50, 0.99, p.confianca_auto, 0.01, key=f"{chave}_auto")
        hum = c3.slider("Abaixo disso vai direto para humano", 0.10, 0.90, p.confianca_humano, 0.05, key=f"{chave}_hum")
    return Premissas(custo_hora=custo, sla_h=sla, confianca_auto=auto, confianca_humano=min(hum, auto),
                     minutos_triagem=tri, tickets_por_mes=float(mes) if mes else None)


def render(sessao):
    p = premissas_na_tela(sessao["id"])
    versoes = tuple(os.path.getmtime(c) for c in sessao["arquivos"].values())
    try:
        r = _analisar(sessao["id"], versoes, json.dumps(asdict(p), sort_keys=True, default=list))
    except KeyError as erro:
        st.error(f"Falta um campo obrigatório nos dados para esta análise: {erro}. Confira o De/Para na aba Dados.")
        return None
    if sessao.get("origem_id"):
        st.caption("Sub-sessão cooperativa: análise feita só nos chamados das contas enviadas pela sessão de origem.")
    abas = st.tabs(visual.abas(["Resumo executivo", "Onde trava", "Satisfação", "Desperdício", "Automação",
                    "Testar ticket", "Qualidade dos dados", "Relatório", "Como ler"]))
    with abas[0]:
        aba_resumo(r)
    with abas[1]:
        aba_gargalos(r)
    with abas[2]:
        aba_satisfacao(r)
    with abas[3]:
        aba_desperdicio(r)
    with abas[4]:
        aba_automacao(r)
    with abas[5]:
        aba_prototipo(r)
    with abas[6]:
        for q in r["qualidade"]:
            st.write("• " + q)
    with abas[7]:
        md_txt = relatorio.markdown(r, sessao["nome"])
        c1, c2 = st.columns(2)
        botao_salvar(c1, "Salvar PDF", lambda: relatorio.pdf(r, sessao["nome"]), "diagnostico_suporte.pdf", key=f"pdf_{sessao['id']}")
        botao_salvar(c2, "Salvar Markdown", md_txt, "diagnostico_suporte.md", key=f"md_{sessao['id']}")
        with st.expander("Pré-visualizar"):
            st.markdown(md_txt)
    with abas[8]:
        aba_como_ler()
    return r


def aba_resumo(r):
    v, d, a = r["volume"], r["desperdicio"], r["automacao"]
    c = st.columns(4)
    c[0].metric("Chamados", num(v["total"]))
    if "em_aberto_%" in v:
        c[1].metric("Sem resolução", pct(v["em_aberto_%"]), help="Abertos + aguardando o cliente")
    elif "escalado_%" in v:
        c[1].metric("Escalados", pct(v["escalado_%"]))
    if d:
        c[2].metric("Horas acima da meta (medidas)", num(d["horas_medidas"]), help=f"{num(d['chamados_medidos'])} chamados com tempo válido")
    if r["classificador"]:
        c[3].metric("Acerto do classificador", pct(100 * r["classificador"]["acuracia"], 1))
    elif "resposta_mediana_h" in v:
        c[3].metric("1ª resposta (mediana)", f"{dec(v['resposta_mediana_h'], 1)} h")
    st.subheader("O que está acontecendo")
    for linha in resumo_executivo(r):
        st.markdown("• " + md(linha))


def aba_gargalos(r):
    g = r["gargalos"]
    if not g["por_dimensao"]:
        st.info("Sem canal, prioridade ou tipo nos dados.")
        return
    st.subheader("Tempo de atendimento por grupo")
    dim = st.radio("Ver por", list(g["por_dimensao"]), format_func=lambda k: g["por_dimensao"][k]["rotulo"], horizontal=True)
    d = g["por_dimensao"][dim]
    t = d["tabela"]
    fig = go.Figure(go.Bar(x=t[dim].astype(str), y=t.mediana_h, marker_color=cores(len(t)),
                           error_y=dict(type="data", symmetric=False, array=t.ic_max_h - t.mediana_h, arrayminus=t.mediana_h - t.ic_min_h),
                           text=[f"{dec(v, 1)} h" for v in t.mediana_h], textposition="inside"))
    fig.update_layout(height=340, yaxis_title="horas (mediana)", margin=dict(t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Tempo: p = {dec(d['p_tempo'], 3)} ({'diferença comprovada' if d['p_tempo'] < 0.05 else 'sem diferença estatística'}). "
               "A barrinha é o intervalo de 95% da mediana: barras que se sobrepõem = grupos iguais na prática.")
    if "em_aberto_%" in t:
        fig = px.bar(t, x=dim, y="em_aberto_%", color_discrete_sequence=[LARANJA], text=t["em_aberto_%"].map(lambda v: f"{v:.0f}%"))
        fig.update_layout(height=280, yaxis_title="% sem resolução", margin=dict(t=10, b=10), yaxis_range=[0, 100])
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Acúmulo: p = {dec(d['p_backlog'], 3)}. Se todas as barras são parecidas, o acúmulo é geral (capacidade), não de um grupo.")
    st.dataframe(t.round(1), hide_index=True, width="stretch")
    if len(g["combinacoes"]):
        st.subheader("Combinações com os piores tempos (mínimo de 30 chamados medidos)")
        st.dataframe(g["combinacoes"].head(10).round(1), hide_index=True, width="stretch")
        st.caption("'vs_geral_h' = horas acima da mediana geral. Diferenças de 1–2 h com amostras de ~80 chamados são pequenas; "
                   "use como pista, não como conclusão.")
    if len(g["backlog"]):
        st.subheader("Onde está o maior acúmulo (canal × prioridade × tipo)")
        st.dataframe(g["backlog"].head(10).round(1), hide_index=True, width="stretch")


def aba_satisfacao(r):
    s = r["satisfacao"]
    if not s:
        st.info("Sem dados de satisfação suficientes.")
        return
    c1, c2 = st.columns([1, 2])
    fig = px.bar(s["distribuicao"], x="nota", y="chamados", color=s["distribuicao"]["nota"].astype(str), color_discrete_sequence=["#D1495B", "#E4572E", "#F2A541", "#17A398", "#3BB273"])
    fig.update_layout(height=280, margin=dict(t=10, b=10))
    c1.plotly_chart(fig, width="stretch")
    c1.caption(f"Média {dec(s['media'])} em {num(s['avaliados'])} avaliações.")
    t = s["tabela"]
    fig = px.bar(t, x="p_valor", y="variável", orientation="h", color="veredito",
                 color_discrete_map={"diferença comprovada": VERDE, "indício": LARANJA, "sem diferença": CINZA})
    fig.add_vline(x=0.05, line_dash="dot", annotation_text="p = 0,05")
    fig.update_layout(height=300, margin=dict(t=10, b=10), xaxis_title="p-valor (quanto menor, mais forte a evidência)")
    c2.plotly_chart(fig, width="stretch")
    st.dataframe(t.round(3), hide_index=True, width="stretch")
    st.caption("Para uma variável 'impactar' a satisfação, a barra precisa ficar à esquerda da linha de 0,05.")


def aba_desperdicio(r):
    d = r["desperdicio"]
    if not d:
        st.info("Sem tempo ou prioridade nos dados para medir desperdício.")
        return
    c = st.columns(4)
    c[0].metric("Passaram da meta", pct(d["estouraram_%"]))
    c[1].metric("Horas acima da meta (medidas)", num(d["horas_medidas"]))
    c[2].metric("Custo (medido)", reais(d["custo_medido"]))
    c[3].metric("Custo projetado (base toda)", reais(d["custo_projetado"]),
                help="Supondo que os chamados sem tempo válido se comportam como os medidos. É projeção, não medição.")
    t = d["por_prioridade"]
    fig = px.bar(t, x="prioridade", y="horas_acima_meta", text=t["custo_R$"].map(reais), color_discrete_sequence=[VERMELHO])
    fig.update_layout(height=320, yaxis_title="horas acima da meta", margin=dict(t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    st.dataframe(t.round(0), hide_index=True, width="stretch")
    st.markdown(md(f"**Maior desperdício recuperável:** '{t.iloc[0]['prioridade']}', porque a meta é curta e o tempo real é o mesmo "
                   "das outras prioridades. Fazer a prioridade valer na fila (os críticos na frente) recupera essas horas sem contratar ninguém."))
    st.caption(f"Além disso, {num(d['backlog'])} chamados estão sem resolução: trabalho represado que não entra nessa conta.")


def aba_automacao(r):
    a, c = r["automacao"], r["classificador"]
    if not c:
        st.info("Envie o Dataset 2 (textos classificados) para treinar o classificador e montar a proposta de automação.")
        return
    st.subheader("Como funcionaria na prática")
    p = r["premissas"]
    st.graphviz_chart(f"""
digraph {{ rankdir=LR; node [shape=box, style="filled", color="#9AA5B1", fillcolor="#ECF1F3", fontname="Helvetica"];
 entra [label="Ticket entra\\n(email, chat, telefone, social)"];
 regra [label="Regras fixas\\ncancelamento? reembolso?\\nprioridade crítica?", fillcolor="#E4E9EC"];
 ia [label="IA classifica\\n(categoria + confiança)"];
 auto [label="Automático\\nconfiança ≥ {str(round(p.confianca_auto, 2)).replace(".", ",")}\\nroteia para a fila certa", fillcolor="#DCEBE4"];
 sug [label="IA sugere\\n{str(round(p.confianca_humano, 2)).replace(".", ",")}–{str(round(p.confianca_auto, 2)).replace(".", ",")}\\nagente confirma com 1 clique", fillcolor="#F3EAD7"];
 hum [label="Humano decide\\nconfiança < {str(round(p.confianca_humano, 2)).replace(".", ",")}\\nou regra fixa ou permissão de acesso", fillcolor="#F1DFDC"];
 entra -> regra; regra -> hum [label="sim"]; regra -> ia [label="não"]; ia -> auto; ia -> sug; ia -> hum; }}""")
    st.subheader("Quanto dá para automatizar com segurança (testado em tickets nunca vistos)")
    f = a["faixas"]
    col = st.columns(3)
    for i, x in f.iterrows():
        col[i].metric(x.faixa, pct(x["tickets_%"]), f"acerto {pct(x['acerto_%'], 1)}", delta_color="off")
    st.subheader("O que NÃO automatizar e por quê")
    st.markdown(md(
        f"- **Cancelamento e reembolso:** envolvem dinheiro e risco de perder o cliente; {num(a['bloqueados_por_regra'].get('Tipo cancelamento/reembolso', 0))} chamados na base.\n"
        f"- **Prioridade crítica:** o custo de errar é alto; {num(a['bloqueados_por_regra'].get('Prioridade crítica', 0))} chamados.\n"
        "- **Permissão de acesso (Administrative rights):** é a categoria em que o modelo mais erra e mexe com segurança.\n"
        f"- **Confiança abaixo de {pct(100 * p.confianca_humano)}:** nessa faixa o modelo acerta só {pct(f.iloc[2]['acerto_%'])}."))
    for titulo, ex in r["exemplos"].items():
        with st.expander(f"Exemplos reais: {titulo}"):
            st.dataframe(ex, hide_index=True, width="stretch")
    st.subheader("Retorno estimado")
    c = st.columns(4)
    c[0].metric("Tickets/mês (premissa)", num(a["tickets_mes"]))
    c[1].metric("Saem automáticos", pct(a["automatizado_%"]))
    c[2].metric("Horas economizadas/mês", num(a["horas_mes"]))
    c[3].metric("Economia/mês", reais(a["reais_mes"]))
    st.caption(f"{num(a['bloqueados_total'])} dos {num(a['bloqueados_total'] + a['elegiveis'])} chamados da base caem nas regras "
               "de 'sempre humano'. A economia vem só da triagem; mude as premissas no topo para simular outro volume.")
    st.subheader("Qualidade do classificador")
    st.dataframe(c_round(r["classificador"]["comparacao"]), hide_index=True, width="stretch")
    st.dataframe(r["classificador"]["por_classe"].round(3), hide_index=True, width="stretch")
    conf = r["classificador"]["confusao"]
    fig = px.imshow(conf, text_auto=True, color_continuous_scale="Blues", aspect="auto")
    fig.update_layout(height=420, xaxis_title="previsto", yaxis_title="real", margin=dict(t=10, b=10))
    st.plotly_chart(fig, width="stretch")


def c_round(df):
    return df.round(3)


def aba_prototipo(r):
    c = r["classificador"]
    if not c:
        st.info("O protótipo precisa do Dataset 2 para treinar o classificador.")
        return
    st.subheader("Teste um ticket novo")
    st.caption("Escreva como o cliente escreveria (o modelo foi treinado em tickets de TI em inglês).")
    texto = st.text_area("Texto do ticket", "Hi, I can't log in to the VPN since this morning, my password was reset. Please help.", height=100)
    c1, c2 = st.columns(2)
    tipo = c1.selectbox("Tipo (se já souber)", ["—", "Technical issue", "Billing inquiry", "Product inquiry", "Cancellation request", "Refund request"])
    prio = c2.selectbox("Prioridade", ["—", "Low", "Medium", "High", "Critical"])
    if texto.strip():
        d = decidir(texto, c, r["premissas"], tipo=None if tipo == "—" else tipo, prioridade=None if prio == "—" else prio)
        cor = {"Automático": "green", "IA sugere, humano confirma": "orange", "Direto para humano": "red"}[d["decisao"]]
        k = st.columns(3)
        k[0].metric("Categoria", d["categoria"])
        k[1].metric("Confiança", pct(100 * d["confianca"]))
        k[2].metric("Decisão", d["decisao"])
        st.markdown(selo(d["decisao"], cor))
        if d["motivos"]:
            st.warning("Vai para humano porque: " + "; ".join(d["motivos"]))
        st.write("**Outras categorias possíveis:** " + " · ".join(f"{n} ({pct(100 * v)})" for n, v in d["alternativas"][1:]))
        st.write("**Tickets parecidos já vistos** (ajudam o agente a responder):")
        st.dataframe(similares(texto, c), hide_index=True, width="stretch")


def aba_como_ler():
    st.markdown("""
**Resumo executivo**: a situação em texto, com os números.

**Onde trava**: tempo de atendimento (mediana) e acúmulo por canal, prioridade e tipo. Barras parecidas = não há gargalo
naquele recorte. O p-valor diz se a diferença é real (menor que 0,05).

**Satisfação**: o que muda a nota do cliente. Só conta como "impacta" com p < 0,05.

**Desperdício**: horas que passaram da meta de cada prioridade, convertidas em reais pelo custo/hora (premissa editável).

**Automação**: o fluxo proposto, quanto sai automático com segurança (testado em tickets que o modelo nunca viu), o que
fica sempre com humano, com exemplos reais, e o retorno em horas e reais.

**Testar ticket**: o protótipo. Escreva um ticket e veja a categoria, a confiança, a decisão (automático, sugere ou humano)
e tickets parecidos.
""")
