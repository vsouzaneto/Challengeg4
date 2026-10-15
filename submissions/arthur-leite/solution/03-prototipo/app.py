"""
Triage Copilot: resposta ao Diretor de Operações + protótipo de triagem de suporte com IA.

    streamlit run app.py

Abas (na ordem do storytelling):
  1. Resposta ao Diretor   painel: diagnóstico → o que automatizar (e o que não) → prova → quanto vale → decisões
  2. Triagem ao vivo       cole um ticket e veja a decisão, a explicação e o rascunho (abre já com um exemplo)
  3. Fila real             9.568 tickets reais nunca vistos no treino, com desempenho medido
  4. Calculadora de ROI    premissas ajustáveis → horas e R$
  5. Metodologia e limites testes estatísticos, benchmark completo, fluxo, regras e limitações

Todo número exibido é recalculado dos dados com o método dos scripts oficiais (src/painel.py indica a origem
de cada um) ou vem de src/roi.py e src/politica.py, as mesmas fontes do relatório executivo.
"""
import html

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src import llm, roi
from src import painel as P
from src.politica import REGRAS, ROTULOS, avaliar
from src.triagem import (COBERTURA_MINIMA, DADOS, SIMILARIDADE_MINIMA, MotorTriagem, decidir, dividir)

st.set_page_config(page_title="Triage Copilot · Resposta ao Diretor", page_icon="🎫", layout="wide")
st.markdown(P.CSS, unsafe_allow_html=True)

if not (DADOS.exists() and P.DS1.exists()):  # 1ª execução num servidor novo (ex.: Streamlit Cloud)
    with st.spinner("Baixando os datasets públicos do Kaggle (1ª execução)..."):
        import baixar_dados  # noqa: F401  (o download roda na importação)

num, pct = P.num, P.pct
COR_FAIXA, NOME_FAIXA, NOME_CURTO = P.COR_FAIXA, P.NOME_FAIXA, P.NOME_CURTO
GRAFICO = {"displayModeBar": False}


# ------------------------------------------------------------------ dados e modelo (com cache)
@st.cache_resource(show_spinner="Carregando o motor de triagem (na 1ª vez, treina em ~1 min)...")
def motor(versao: int = 2) -> MotorTriagem:
    """versao: força recarregar se o servidor guardou em cache uma versão antiga da classe do motor."""
    return MotorTriagem.carregar()


@st.cache_data(show_spinner=False)
def base_ds2() -> pd.DataFrame:
    return pd.read_csv(DADOS)


@st.cache_data(show_spinner=False)
def teste() -> pd.DataFrame:
    _, _, te = dividir(base_ds2())
    return te


@st.cache_data(show_spinner="Classificando os 9.568 tickets de teste...")
def avaliacao_teste(versao: int = 2) -> pd.DataFrame:
    """versao: muda a chave do cache quando as colunas mudam (v2 traz motivo_humano, usado no painel)."""
    te = teste()
    r = motor().classificar_lote(te["Document"])
    r["real"] = te["Topic_group"]
    r["acertou"] = r["categoria"] == r["real"]
    r["acertou_top2"] = (r["top2_a"] == r["real"]) | (r["top2_b"] == r["real"])
    return r


@st.cache_data(show_spinner="Recalculando o diagnóstico do Dataset 1 (1.000 sorteios)...")
def diagnostico() -> dict:
    return P.diagnostico_ds1()


@st.cache_data(show_spinner="Testando o motor com tickets de outro domínio...")
def fora_dominio() -> dict:
    return P.fora_do_dominio(motor())


@st.cache_data(show_spinner=False)
def politica_ds2() -> dict:
    return P.politica_ds2(base_ds2()["Document"])


EXEMPLOS = {
    "Hardware rotineiro": "Hi, my laptop screen is flickering and the external monitor is not detected since this morning. Can you help?",
    "Pedido de compra (ambíguo)": "Please approve the purchase order for 3 new docking stations for the finance team.",
    "Fora do domínio (em português)": "Quero saber o status do meu pedido de reembolso do curso",
    "Possível phishing": "URGENT: I received a suspicious email asking for my password and I clicked the link. What should I do?",
    "Desligamento de funcionário": "John is a leaver from Friday, please remove his access to all systems and collect his laptop.",
}
ALEATORIO = "Ticket real aleatório do conjunto de teste"


def classe_decisao(r, dec) -> tuple[str, str]:
    """Classe CSS e rótulo da saída final de um ticket (o escalonamento da política vence)."""
    if "Escalado" in dec.modo:
        return "escalado", "Escalado para Segurança"
    return r.faixa, NOME_CURTO[r.faixa]


def secao(n: str, titulo: str, sub: str = "") -> None:
    st.markdown(f'<div class="secao"><div class="n">{n}</div><div class="t">{titulo}</div></div>'
                + (f'<div class="secao-sub">{sub}</div>' if sub else ""), unsafe_allow_html=True)


def titulo_grafico(t: str, legenda: str = "") -> None:
    st.markdown(f'<div class="graf-tit">{t}</div>' + (f'<div class="graf-leg">{legenda}</div>' if legenda else ""),
                unsafe_allow_html=True)


m = motor()
av = avaliacao_teste()
fx = P.faixas(av)
diag = diagnostico()
fd = fora_dominio()
pol = politica_ds2()
auto_, sug_, hum_, prec_, prec_sug_ = roi.faixas_de(av)
cenarios = {nome: roi.calcular(c, auto_, sug_, hum_, prec_, prec_sug_) for nome, c in roi.CENARIOS.items()}
base = cenarios["Base"]

aba_painel, aba_ao_vivo, aba_fila, aba_roi, aba_metodo = st.tabs(
    ["Resposta ao Diretor", "Triagem ao vivo", f"Fila real ({num(fx['n'])} tickets)", "Calculadora de ROI", "Metodologia e limites"])

# ================================================================== 1. RESPOSTA AO DIRETOR
with aba_painel:
    st.markdown(f"""
<div class="hero">
  <div class="kicker">Triage Copilot · Redesign do Suporte com IA · Arthur Leite</div>
  <h1>Resposta ao Diretor de Operações</h1>
  <p class="lead">Os dados atuais <b>não mostram</b> onde o suporte perde tempo. A <b>triagem</b> pode ser automatizada com travas
  de segurança, testada em {num(fx['n'])} tickets reais, começando em modo sombra.</p>
  <div class="pedido"><b>Decisão pedida:</b> aprovar a instrumentação da operação e um piloto de 4 semanas (seção 5).</div>
</div>
<div class="cards">
  <div class="card c1"><div class="q">1 · Onde perdemos tempo?</div>
    <div class="big">{pct(diag['frac_negativos'], 0)}</div>
    <div class="sub">dos tickets fechados foram "resolvidos" antes da 1ª resposta</div>
    <div class="ans">Não dá para afirmar com estes dados: o 1º gargalo é de <b>medição</b>.</div></div>
  <div class="card c2"><div class="q">2 · O que automatizar?</div>
    <div class="big">{pct(fx['auto']['frac'])}</div>
    <div class="sub">dos tickets roteados sozinhos, com {pct(fx['auto']['acerto'])} de acerto</div>
    <div class="ans">A <b>triagem</b>, em 3 faixas de confiança. Ações sensíveis e respostas ficam com humanos.</div></div>
  <div class="card c3"><div class="q">3 · Funciona?</div>
    <div class="big">{num(fx['n'])}</div>
    <div class="sub">tickets reais que o modelo nunca viu, testados inteiros (sem escolha a dedo)</div>
    <div class="ans"><b>Sim, em tickets reais de TI.</b> Na sua operação, depois de retreinar no seu histórico e passar pelo modo sombra. Teste nas abas acima.</div></div>
  <div class="card c4"><div class="q">Quanto vale?</div>
    <div class="big">{num(base['horas_recuperaveis'])} h</div>
    <div class="sub">de agente liberadas por ano no cenário base, ≈ {num(base['horas_recuperaveis'] / 12)} h/mês (faixa: {num(cenarios['Conservador']['horas_recuperaveis'])} a {num(cenarios['Otimista']['horas_recuperaveis'])} h/ano)</div>
    <div class="ans">≈ {num(base['fte'], 1)} pessoa ≈ R$ {num(base['reais_ano'])}/ano de tempo liberado, <b>a confirmar no piloto</b>.</div></div>
</div>
""", unsafe_allow_html=True)

    # ---------------------------------------------------------- 1. diagnóstico
    secao("1", "Onde estamos perdendo tempo? O primeiro gargalo é de medição",
          f"Antes de apontar gargalos, testei se a base de operação ({num(diag['n_tickets'])} tickets do Dataset 1) "
          "consegue mostrá-los. Não consegue, e os três gráficos mostram por quê.")
    g1, g2, g3 = st.columns(3, gap="medium")
    with g1:
        titulo_grafico(f"Em {pct(diag['frac_negativos'], 0)} dos tickets, a resolução vem antes da 1ª resposta",
                       f"{num(diag['n_negativos'])} de {num(diag['n_fechados'])} tickets fechados. Os \"tempos\" são carimbos "
                       f"sorteados numa janela de {num(diag['janela_h'])} horas, não durações reais.")
        st.plotly_chart(P.fig_duracoes(diag["duracoes_h"]), width="stretch", config=GRAFICO)
    with g2:
        cs = diag["csat"]
        titulo_grafico("A satisfação é igual em todas as notas: é sorteada",
                       f"Notas de 1 a 5 com frequências quase idênticas ({num(cs.min())} a {num(cs.max())}). Canal, prioridade, "
                       f"tipo, produto, tempo e perfil: nenhum muda a nota, e diferenças de {num(diag['csat_diferenca_detectavel'], 1)} "
                       "ponto seriam detectadas.")
        st.plotly_chart(P.fig_csat(cs), width="stretch", config=GRAFICO)
    with g3:
        pior, melhor = diag["pior"], diag["melhor"]
        titulo_grafico("A \"pior\" combinação não se distingue do acaso",
                       f"Entre as {diag['n_combinacoes']} combinações de canal × prioridade × tipo, a pior parece "
                       f"{num(diag['gap_observado_h'], 1)} h mais lenta que a melhor. Embaralhando os tempos ao acaso, "
                       f"a diferença média é de {num(diag['gap_acaso_medio_h'], 1)} h. E a \"melhor\" dura {num(melhor[1], 1)} h.")
        st.plotly_chart(P.fig_permutacao(diag["gap_acaso_h"], diag["gap_observado_h"], diag["p_permutacao"]),
                        width="stretch", config=GRAFICO)
    st.markdown(f"""
<div class="veredito"><b>Por que isso importa:</b> qualquer "gargalo por canal" ou "driver de satisfação" tirado desta base teria
cara de verdade e levaria a decisões erradas. Nem as variáveis se relacionam entre si ({num(diag['n_pares_associados'])} de
{num(diag['n_pares'])} pares associados). Por isso, o primeiro passo é <b>medir a operação direito</b>:</div>
<div class="fluxo">
  <div class="passo"><b>Carimbos separados</b>criação, 1ª resposta e resolução, para medir durações reais</div>
  <div class="passo"><b>Log de cada mudança de fila</b>mede o reroteamento e o tempo perdido na fila errada</div>
  <div class="passo"><b>Categoria na abertura × na resolução</b>mede o erro de triagem atual</div>
  <div class="passo"><b>Tempo ativo do agente</b>separado do tempo de espera; satisfação com taxa de resposta</div>
</div>
""", unsafe_allow_html=True)

    # ---------------------------------------------------------- 2. o que automatizar / o que não
    secao("2", "O que automatizar com IA: a triagem, em 3 faixas de confiança",
          f"Validado em {num(len(base_ds2()))} tickets reais de TI (Dataset 2): o modelo aprendeu com o histórico e foi medido em "
          f"{num(fx['n'])} tickets que nunca viu. Ele só decide sozinho quando a precisão medida na validação é de pelo menos 95%.")
    st.plotly_chart(P.fig_faixas(fx), width="stretch", config=GRAFICO)
    st.markdown(f"""
<div class="nota"><span class="pill auto">Automático</span> a IA roteia sozinha &nbsp;·&nbsp;
<span class="pill sugere">Sugestão</span> a IA mostra 2 opções e o agente escolhe com 1 clique &nbsp;·&nbsp;
<span class="pill humano">Humano</span> o agente classifica do zero (inclui {pct(fx['humano_trava'])} barrados pelas travas de domínio)</div>
<div class="nota">Na sua operação, as 8 categorias de TI da prova viram as suas filas: Billing, Refund, Technical issue, Product inquiry e Cancellation. O motor é o mesmo, retreinado no seu histórico.</div>
<div class="kpis">
  <div class="kpi"><div class="v" style="color:var(--verde)">{pct(fx['auto']['acerto'])}</div>
    <div class="l">de acerto na faixa automática. Todas as 8 categorias ficam em 95% ou mais (Hardware no limite)</div></div>
  <div class="kpi"><div class="v" style="color:#B7791F">{pct(fx['sugere']['top2'])}</div>
    <div class="l">das vezes, a categoria certa está entre as 2 sugeridas ao agente</div></div>
  <div class="kpi"><div class="v">{pct(fd['auto_sem_travas'])} → {pct(fd['auto_com_travas'])}</div>
    <div class="l">dos tickets de outro domínio (clientes, Dataset 1) iriam para o automático: sem × com as travas</div></div>
</div>
""", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        titulo_grafico("Na faixa automática, todas as categorias ficaram em 95% ou mais no teste",
                       "Acerto da faixa automática por categoria (estimativa pontual). Hardware, a mais confundida, está no limite: intervalo de 94,0% a 96,2%.")
        st.plotly_chart(P.fig_acerto_categoria(fx["por_categoria"]), width="stretch", config=GRAFICO)
    with c2:
        titulo_grafico("Por que não um LLM para classificar? O modelo do histórico acerta mais",
                       "Mesma amostra de 400 tickets do teste. Com o histórico no prompt, o LLM empata com o simples voto dos "
                       "5 tickets mais parecidos: quem acerta é o histórico, não o LLM. Ele fica onde é bom: redigir rascunhos.")
        st.plotly_chart(P.fig_benchmark(), width="stretch", config=GRAFICO)

    st.markdown('<div class="graf-tit" style="margin-top:1rem;font-size:1.15rem">O que NÃO automatizar: '
                'rotear ≠ executar ≠ responder</div>', unsafe_allow_html=True)
    cartoes = "".join(
        f'<div class="regra"><div class="h">{ROTULOS[k]}<span>{pct(pol["por_regra"][k][1])} dos tickets</span></div>'
        f'<div class="a">{html.escape(v["acao"])}</div></div>' for k, v in REGRAS.items())
    st.markdown(f"""
<div class="graf-leg"><b>{pct(pol['frac_alguma_regra'])}</b> dos {num(pol['n'])} tickets acionam ao menos uma regra: a IA pode
rotear, mas a ação fica com um humano, seja qual for a confiança do modelo. As regras são explícitas, e não pela categoria,
porque os temas sensíveis atravessam as categorias.</div>
<div class="regras">{cartoes}</div>
<div class="nota">Também não automatizamos: <b>fechar tickets</b>, <b>enviar respostas sem revisão</b> e <b>decidir sobre tickets
fora do domínio</b> (outro idioma ou assunto novo vão para a faixa humana).</div>
""", unsafe_allow_html=True)

    # ---------------------------------------------------------- 3. prova
    secao("3", "Mostre que funciona: o protótipo rodando",
          "Cada ticket passa por 4 etapas. Abaixo, 4 tickets processados agora pelo motor real, cada um com uma saída diferente.")
    st.markdown("""
<div class="fluxo">
  <div class="passo"><b>1 · Política</b>segurança → fila de Segurança + escalonamento; urgência → plantão; saúde → sem LLM</div>
  <div class="passo"><b>2 · Travas de domínio</b>não reconhece o ticket (idioma, assunto novo) → triagem humana</div>
  <div class="passo"><b>3 · Classificador</b>confiança alta → automático; média → 2 sugestões; baixa → humano</div>
  <div class="passo"><b>4 · Na fila (copiloto)</b>palavras-chave + 3 casos parecidos + rascunho; ação sensível → sempre humano</div>
</div>""", unsafe_allow_html=True)
    blocos = []
    for nome in ["Hardware rotineiro", "Pedido de compra (ambíguo)", "Fora do domínio (em português)", "Possível phishing"]:
        texto = EXEMPLOS[nome]
        r = m.classificar(texto)
        dec = decidir(r, avaliar(texto))
        classe, rot = classe_decisao(r, dec)
        blocos.append(f'<div class="ex"><div class="kicker">{nome}</div><div class="txt">"{html.escape(texto)}"</div>'
                      f'<div class="res"><span class="pill {classe}">{rot}</span> → {html.escape(dec.fila)}</div>'
                      + (f'<div class="nota">2 opções ao agente: {html.escape(r.top2[0][0])} ({pct(r.top2[0][1], 0)}) · '
                         f'{html.escape(r.top2[1][0])} ({pct(r.top2[1][1], 0)})</div>' if r.faixa == "sugere" else "")
                      + f'<div class="nota">Ação: {html.escape(dec.executar)}</div></div>')
    st.markdown(f'<div class="exemplos">{"".join(blocos)}</div>'
                '<div class="nota" style="margin-top:.5rem">Teste com qualquer texto na aba <b>Triagem ao vivo</b> e veja o '
                f'desempenho nos {num(fx["n"])} tickets na aba <b>Fila real</b>.</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------- 4. quanto vale
    secao("4", f"Quanto vale: ≈ {num(base['horas_recuperaveis'])} horas de agente por ano no cenário base",
          "Tempo de triagem liberado, com o desempenho medido da IA e premissas de mercado para o tempo de hoje.")
    tiles = []
    for nome, r in cenarios.items():
        c = roi.CENARIOS[nome]
        tiles.append(f'<div class="cen{" base" if nome == "Base" else ""}"><div class="nome">{nome}</div>'
                     f'<div class="h">{num(r["horas_recuperaveis"])} h/ano</div>'
                     f'<div class="d">{num(c.triagem_min, 1)} min de triagem por ticket hoje<br>'
                     f'≈ {num(r["fte"], 1)} pessoa · R$ {num(r["reais_ano"])}/ano</div></div>')
    custo_hora = roi.Premissas().custo_hora
    st.markdown(f"""
<div class="cenarios">{''.join(tiles)}</div>
<div class="veredito">Em base mensal: de <b>{num(cenarios['Conservador']['horas_recuperaveis'] / 12)} a
{num(cenarios['Otimista']['horas_recuperaveis'] / 12)} h/mês</b> (base ≈ {num(base['horas_recuperaveis'] / 12)} h/mês ≈
R$ {num(base['reais_ano'] / 12)}/mês). O maior desperdício recuperável que dá para medir hoje é o <b>tempo de triagem manual</b>:
a IA libera cerca de {pct(base['horas_recuperaveis'] / base['horas_atual'], 0)} dele. O maior de todos, a espera do cliente na
fila errada, só será medido com a instrumentação.</div>
<div class="nota">É <b>tempo de agente liberado</b>, não economia de caixa, e ainda não desconta implantação e manutenção.
Volume: {num(roi.Premissas().volume_ano)} tickets/ano (enunciado). Custo/hora: R$ {num(custo_hora, 2)} (salário + encargos,
salario.com.br, out/2026). O resultado depende quase só dos minutos de triagem por ticket hoje, a premissa mais fraca:
por isso ela é a 1ª métrica do piloto. Ficam de fora, de propósito: o tempo de espera do cliente na fila errada
(provavelmente o maior ganho), a redução de reroteamento (não demonstrada) e os rascunhos. Ajuste as premissas na aba
<b>Calculadora de ROI</b>.</div>
""", unsafe_allow_html=True)

    # ---------------------------------------------------------- 5. decisões
    secao("5", "O que preciso de você", "Três decisões. A decisão de escalar sai dos números do piloto, não destas premissas.")
    st.markdown("""
<div class="decisoes">
  <div class="dec"><div class="n">Decisão 1</div><div class="t">Aprovar a instrumentação (semana 0)</div>
    <div class="d">Carimbos separados de criação, 1ª resposta e resolução, mais o log de mudança de fila. Sem isso, nenhum
    diagnóstico de gargalo é confiável.</div></div>
  <div class="dec"><div class="n">Decisão 2</div><div class="t">Aprovar 4 semanas de piloto</div>
    <div class="d">Modo sombra primeiro (a IA classifica sem rotear), depois o automático em 3 categorias estáveis.</div></div>
  <div class="dec"><div class="n">Decisão 3</div><div class="t">Indicar os donos das regras</div>
    <div class="d">Segurança, RH e Financeiro validam e mantêm a política do que não se automatiza.</div></div>
</div>
<div class="fluxo">
  <div class="passo"><b>Semana 0 · Instrumentar</b>carimbos, log de mudança de fila, retreino no histórico próprio.
    <br><i>Avança se:</i> dados chegando completos</div>
  <div class="passo"><b>Semanas 1–2 · Modo sombra</b>a IA classifica, mas não roteia.
    <br><i>Avança se:</i> concordância ≥ 95% na faixa automática</div>
  <div class="passo"><b>Semanas 3–4 · Automático parcial</b>só Compras, Acessos e Armazenamento.
    <br><i>Avança se:</i> as reatribuições não aumentam</div>
  <div class="passo"><b>Semana 5+ · Escala</b>todas as categorias, sugestões e rascunho.
    <br><i>Avança se:</i> ganho medido ≥ cenário conservador</div>
</div>
<div class="nota" style="margin-top:1.2rem">Fontes: 01-diagnostico/outputs/auditoria.md · modelo_desperdicio.md ·
03-prototipo/benchmark/outputs/benchmark.md · motor_final.md. Os números deste painel são recalculados dos dados ao abrir o app,
com o mesmo método dos scripts; detalhes e testes estatísticos na aba <b>Metodologia e limites</b>.</div>
""", unsafe_allow_html=True)

# ================================================================== 2. TRIAGEM AO VIVO
with aba_ao_vivo:
    st.markdown("### Triagem ao vivo")
    st.caption("Escolha um exemplo ou cole qualquer ticket (em inglês, como os dados de treino). O motor decide a fila, "
               "o nível de automação e quem executa a ação, e explica por quê.")
    escolha = st.selectbox("Exemplo", list(EXEMPLOS) + [ALEATORIO], index=0)
    if escolha == ALEATORIO:
        if "semente_aleatoria" not in st.session_state:
            st.session_state.semente_aleatoria = 0
        if st.button("Sortear outro ticket"):
            st.session_state.semente_aleatoria = int(np.random.default_rng().integers(1_000_000))
        amostra = teste().sample(1, random_state=st.session_state.semente_aleatoria).iloc[0]
        padrao = amostra["Document"]
        st.info(f"Ticket real do conjunto de teste. Categoria verdadeira: **{amostra['Topic_group']}** "
                "(texto já pré-processado na origem: sem pontuação nem stopwords).")
    else:
        padrao = EXEMPLOS[escolha]
    texto = st.text_area("Texto do ticket", value=padrao, height=110)

    if not texto.strip():
        st.info("Cole o texto de um ticket acima, ou escolha um exemplo, para ver a decisão.")
    else:
        r = m.classificar(texto)
        pol_t = avaliar(texto)
        dec = decidir(r, pol_t)
        classe, rot = classe_decisao(r, dec)
        st.markdown(f"""
<div class="decisao-ticket {classe}">
  <div class="rot">{rot} · {html.escape(dec.modo)}</div>
  <div class="fila">Fila: {html.escape(dec.fila)}</div>
  <div class="det">Confiança do modelo: <b>{pct(r.confianca, 1)}</b> &nbsp;·&nbsp; Quem executa a ação: <b>{html.escape(dec.executar)}</b></div>
</div>""", unsafe_allow_html=True)
        if dec.escalar:
            st.error("Escalar agora: a política detectou urgência ou incidente de segurança.")

        st.markdown("#### Por quê")
        for linha in dec.explicacao:
            st.markdown(f"- {linha}")

        e1, e2 = st.columns(2, gap="large")
        with e1:
            st.markdown("**Palavras que mais pesaram**")
            if r.palavras_chave:
                st.dataframe(pd.DataFrame([(t, num(w, 3)) for t, w in r.palavras_chave], columns=["termo", "peso"]),
                             hide_index=True, width="stretch")
            else:
                st.caption("Nenhuma palavra conhecida pelo modelo.")
            st.markdown(f"**2 categorias mais prováveis:** {r.top2[0][0]} ({pct(r.top2[0][1], 0)}) · "
                        f"{r.top2[1][0]} ({pct(r.top2[1][1], 0)})")
            st.caption(f"Travas de domínio: o modelo reconhece {pct(r.cobertura_vocab, 0)} das palavras (mín. "
                       f"{pct(COBERTURA_MINIMA, 0)}); similaridade com o histórico {num(r.similaridade, 2)} "
                       f"(mín. {num(SIMILARIDADE_MINIMA, 2)}).")
        with e2:
            st.markdown("**Tickets parecidos já resolvidos**")
            for s in r.similares:
                st.markdown(f"- `{s['categoria']}` ({num(s['similaridade'], 2)}) {s['texto'][:160]}...")

        st.markdown("#### Rascunho de resposta para o agente")
        if not dec.pode_rascunho:
            st.warning("Rascunho por LLM **bloqueado**: dado sensível ou ticket fora do domínio. Resposta 100% humana.")
        elif not llm.disponivel():
            st.caption("LLM desligado (sem GEMINI_API_KEY configurada). Todo o resto funciona sem ele.")
        elif st.button("Gerar rascunho com Gemini"):
            with st.spinner("Redigindo..."):
                txt = llm.rascunhar_resposta(texto, dec.fila, r.similares, [ROTULOS[a] for a in pol_t.alertas])
            st.text_area("Rascunho (o agente revisa antes de enviar)", txt or "API indisponível no momento.", height=180)

# ================================================================== 3. FILA REAL
with aba_fila:
    st.markdown("### Fila real: tickets que o modelo nunca viu")
    st.markdown(f"**{num(len(av))} tickets reais** do Dataset 2, separados antes do treino. Nada aqui é escolhido a dedo: "
                "é o conjunto de teste inteiro (que gera os números oficiais) ou uma amostra aleatória dele.")
    a1, a2 = st.columns([3, 1])
    n = a1.slider("Tamanho da fila", 200, len(av), len(av), step=100)
    semente = a2.number_input("Semente da amostra", 0, 9999, 0)
    f = av.sample(n, random_state=int(semente))

    resumo = (f.groupby("faixa").agg(tickets=("acertou", "size"), precisao=("acertou", "mean"), top2=("acertou_top2", "mean"))
              .reindex(["auto", "sugere", "humano"]))
    resumo["% da fila"] = resumo["tickets"] / len(f)
    k = st.columns(3)
    for col, faixa in zip(k, ["auto", "sugere", "humano"]):
        lin = resumo.loc[faixa]
        extra = f"acerto da 1ª opção: {pct(lin.precisao)}" if faixa != "sugere" else f"certa entre as 2: {pct(lin.top2)}"
        col.metric(NOME_FAIXA[faixa], f"{pct(lin['% da fila'])} da fila")
        col.caption(extra)

    g1, g2 = st.columns(2, gap="large")
    with g1:
        por_cat = f.assign(faixa=f["faixa"].map(NOME_CURTO)).groupby(["categoria", "faixa"]).size().reset_index(name="tickets")
        fig = px.bar(por_cat, x="tickets", y="categoria", color="faixa", orientation="h",
                     color_discrete_map={NOME_CURTO[k]: v for k, v in COR_FAIXA.items()},
                     category_orders={"faixa": list(NOME_CURTO.values())},
                     title="Faixa de automação por categoria prevista")
        fig.update_layout(legend_title_text="", separators=",.", yaxis_title="", legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig, width="stretch", config=GRAFICO)
    with g2:
        cm = pd.crosstab(f["real"], f["categoria"], normalize="index")
        fig = px.imshow(cm, text_auto=".0%", color_continuous_scale="Greens", aspect="auto",
                        title="Matriz de confusão (linhas = categoria real)")
        fig.update_layout(coloraxis_showscale=False, xaxis_title="prevista", yaxis_title="real")
        st.plotly_chart(fig, width="stretch", config=GRAFICO)

    pol_lote = teste().loc[f.index, "Document"].map(avaliar)
    alert = pd.Series([a for p in pol_lote for a in p.alertas]).map(ROTULOS).value_counts()
    st.markdown(f"**Política:** {pct(pol_lote.map(lambda p: p.exige_humano_para_executar).mean())} dos tickets desta fila têm "
                "uma ação que exige humano, mesmo quando o roteamento é automático.")
    st.dataframe(alert.rename("tickets").rename_axis("regra").to_frame(), width="stretch")
    with st.expander("Ver os erros da faixa automática"):
        erros = f[(f["faixa"] == "auto") & ~f["acertou"]].join(teste()["Document"])
        st.dataframe(erros[["Document", "real", "categoria", "confianca"]], width="stretch")

# ================================================================== 4. CALCULADORA DE ROI
with aba_roi:
    st.markdown("### Calculadora de ROI")
    st.caption("Mesmo cálculo do painel e do relatório (src/roi.py). Troque as premissas pelos números reais da operação.")
    roi.renderizar(st, av)

# ================================================================== 5. METODOLOGIA E LIMITES
TABELA_BENCH = "\n".join(f"| {r[0]} | {r[1]} | {pct(r[2])} | {r[3]} |" for r in P.BENCHMARK_LLM)
with aba_metodo:
    st.markdown(f"""
### Diagnóstico: os testes estatísticos
Fonte: `solution/01-diagnostico/outputs/auditoria.md` (gerado por `01_auditoria_dados.py` e revisado por um agente juiz
independente). Os números abaixo são recalculados ao abrir o app, com o mesmo método e a mesma semente.

| O que testei | Resultado |
|---|---|
| **Onde o fluxo trava?** ({diag['n_combinacoes']} combinações canal × prioridade × tipo, tickets fechados) | A "pior" ({diag['pior'][0]}, {num(diag['pior'][1], 1)} h) parece {num(diag['gap_observado_h'], 1)} h mais lenta que a "melhor" ({diag['melhor'][0]}, {num(diag['melhor'][1], 1)} h). Teste de permutação ({num(len(diag['gap_acaso_h']))} sorteios, semente 0): o acaso produz em média {num(diag['gap_acaso_medio_h'], 1)} h, p = {num(diag['p_permutacao'], 2)}. **Nenhuma combinação se distingue do ruído** |
| Os "tempos" são tempos? | Carimbos de data e hora numa janela de {num(diag['janela_h'])} h; em **{pct(diag['frac_negativos'], 0)}** dos fechados ({num(diag['n_negativos'])} de {num(diag['n_fechados'])}), a resolução vem **antes** da 1ª resposta |
| A satisfação varia com algo? | CSAT uniforme de 1 a 5 (qui-quadrado p = 0,80); 10 testes com correção de Bonferroni, nenhum significativo; poder para detectar {num(diag['csat_diferenca_detectavel'], 2)} ponto |
| As variáveis conversam entre si? | **{diag['n_pares_associados']} de {diag['n_pares']}** pares associados (qui-quadrado, p < 0,05); maior Cramér's V corrigido = 0,021 |
| O texto é real? | 100% com campo não preenchido (`{{product_purchased}}`); 16 frases-modelo; resoluções sem sentido |

**Decisão:** não apresento "gargalos por canal" nem "drivers de satisfação". A prova da automação é feita no Dataset 2
(dados reais), e o ganho é estimado por premissas explícitas (aba Calculadora de ROI).

### Motor de triagem: desempenho no teste
Fonte: `benchmark/outputs/motor_final.md`. {num(fx['n'])} tickets nunca vistos; limiares escolhidos na validação.

| Faixa | % dos tickets | Acerto da 1ª opção | Certa entre as 2 primeiras |
|---|---|---|---|
| Automático | {pct(fx['auto']['frac'])} | {pct(fx['auto']['acerto'])} (IC95% bootstrap 95,9% a 96,8%) | {pct(fx['auto']['top2'])} |
| Sugestão | {pct(fx['sugere']['frac'])} | {pct(fx['sugere']['acerto'])} | {pct(fx['sugere']['top2'])} |
| Humano | {pct(fx['humano']['frac'])} | {pct(fx['humano']['acerto'])} | {pct(fx['humano']['top2'])} |

A faixa humana soma {pct(fx['humano_confianca'])} por confiança baixa e {pct(fx['humano_trava'])} pela trava de domínio
(similaridade com o histórico < {num(SIMILARIDADE_MINIMA, 2)} ou menos de {pct(COBERTURA_MINIMA, 0)} das palavras conhecidas).
Fora do domínio ({num(fd['n'])} tickets de cliente do Dataset 1): {pct(fd['auto_sem_travas'])} iriam para o automático sem as
travas; com elas, {pct(fd['auto_com_travas'])}.

### Modelo simples × LLM
Fonte: `benchmark/outputs/benchmark.md` (as chamadas ao LLM não são refeitas no app).

| Abordagem | Como | Acerto | Tickets |
|---|---|---|---|
{TABELA_BENCH}

No teste completo, o modelo simples
(TF-IDF + regressão logística) tem acurácia e F1-macro de 0,860. Na amostra de 400 tickets, a diferença pareada entre ele e o
melhor LLM (RAG) é significativa (McNemar: 53 × 21 tickets, p = 0,0003); contra o Gemini 3.8 flash, 70 × 7 (p < 10⁻¹³).
O teste favorece o modelo local (texto já pré-processado, categorias dadas só pelo nome, plano gratuito do Gemini): um LLM mais
forte, com definições das categorias, provavelmente reduziria a distância.

### Fluxo proposto
```
ticket entra
   │
   ├─► 1. Política (regras explícitas): segurança? saúde? desligamento? aprovação? privilégio? urgência?
   │        └─ segurança → fila de Segurança + escalonamento (sobrepõe tudo)
   │
   ├─► 2. Travas de domínio: o modelo conhece este tipo de ticket?   não → HUMANO classifica
   │
   ├─► 3. Classificador (TF-IDF + regressão logística, treinado no histórico)
   │        ├─ confiança ≥ limiar da categoria → AUTOMÁTICO (precisão medida ≥ 95%)
   │        ├─ confiança média               → SUGESTÃO: humano escolhe entre 2
   │        └─ confiança baixa               → HUMANO classifica
   │
   └─► 4. Na fila: agente recebe palavras-chave + tickets parecidos + rascunho (LLM, opcional)
            └─ ação sensível (aprovar, conceder, revogar) → sempre humano
```

### O que NÃO automatizamos
""")
    st.dataframe(pd.DataFrame([{"Regra": ROTULOS[k], "Frequência no Dataset 2": v["freq_ds2"], "O que acontece": v["acao"],
                                "Por quê": v["porque"]} for k, v in REGRAS.items()]), hide_index=True, width="stretch")
    st.markdown("""
### Limitações
- Treinado em tickets internos de TI, **em inglês**. Para outra operação, retreina-se com o histórico dela (minutos, sem GPU).
- Os rótulos do Dataset 2 têm ruído estimado de 15–25% (amostra de 32 textos: ordem de grandeza): parte dos "erros" medidos é rótulo errado.
- Travas de domínio: o limiar foi escolhido observando os mesmos tickets de outro domínio usados para avaliá-lo; o resultado tende a ser otimista.
- As regras da política são por palavra-chave: alta sensibilidade de propósito, mas com falsos positivos (custam segundos de um humano) e variações que escapam (ex.: "last day" não aciona desligamento).
- O ROI usa premissas de mercado, porque os tempos do Dataset 1 são sintéticos. Os números reais vêm do piloto.
- O motor é retreinado quando o app sobe. Em outro sistema operacional ou com outras versões das bibliotecas, os números podem variar em até 0,1 ponto (ex.: 65,6% × 65,5% no automático). Os valores oficiais estão em `motor_final.md`.
""")
