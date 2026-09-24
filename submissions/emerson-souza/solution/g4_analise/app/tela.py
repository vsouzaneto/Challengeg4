"""Telas do G4 Analise (Streamlit). Aberto pela janela propria em app/principal.py."""

import os
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nucleo import cruzamentos, depara, leitura, perfis, sessoes  # noqa: E402
from servicos import PONTES, criar_sessao_desafio, criar_sub_sessao  # noqa: E402
from nucleo.exportar import botao_salvar, csv_principal, excel_completo, pasta_de_saida  # noqa: E402
from nucleo.contratos import MODULOS  # noqa: E402
from nucleo import visual  # noqa: E402
from modulos.churn import tela as tela_churn  # noqa: E402
from modulos.suporte import tela as tela_suporte  # noqa: E402
from modulos.leads import tela as tela_leads  # noqa: E402
from modulos.midia import tela as tela_midia  # noqa: E402

TELAS_PRONTAS = {"churn": tela_churn, "suporte": tela_suporte, "leads": tela_leads, "midia": tela_midia}


FONTES = {"desafio": "do desafio", "arquivos": "enviados", "cruzamento": "vindos de outra análise"}

ETAPA_DO_MODULO = {"churn": 3, "suporte": 4, "leads": 6, "midia": 7}

st.set_page_config(page_title="G4 Analise", layout="wide")
visual.aplicar_estilo(st)
visual.tema_plotly()


# ---------- utilidades ----------

def ir(pagina, sessao_id=None):
    st.session_state["pagina"] = pagina
    st.session_state["sessao_id"] = sessao_id


@st.cache_data(show_spinner="Lendo os dados...")
def carregar(caminho, _versao):
    return leitura.ler(caminho)


def ler_da_sessao(caminho):
    return carregar(caminho, os.path.getmtime(caminho))


def rotulo_modulo(chave):
    m = MODULOS[chave]
    return f"{m.nome} (desafio {m.desafio})"


# ---------- barra lateral ----------

def barra_lateral():
    visual.marca(st.sidebar)
    st.sidebar.caption("Churn · Suporte · Leads · Mídia")
    st.sidebar.button("Nova sessão", width="stretch", type="primary", icon=":material/add:", on_click=ir, args=("nova",))
    st.sidebar.button("Início", width="stretch", type="tertiary", icon=":material/home:", on_click=ir, args=("inicio",))
    st.sidebar.divider()
    st.sidebar.caption("SESSÕES")
    todas = sessoes.listar()
    if not todas:
        st.sidebar.caption("Nenhuma sessão ainda.")
    raizes = [s for s in todas if not s["origem_id"]]
    atual = st.session_state.get("sessao_id") if st.session_state.get("pagina") == "sessao" else None

    def item(s, nivel):
        icone = ":material/subdirectory_arrow_right:" if nivel else visual.ICONES_MODULO[s["modulo"]]
        recuo = "\u2003" * max(nivel - 1, 0)
        st.sidebar.button(f"{recuo}{s['nome']}", key=f"s_{s['id']}", width="stretch", icon=icone,
                          type="secondary" if s["id"] == atual else "tertiary", on_click=ir, args=("sessao", s["id"]))
        for f in sessoes.filhas(s["id"]):
            item(f, nivel + 1)

    for s in raizes:
        item(s, 0)


# ---------- inicio ----------

def pagina_inicio():
    visual.cabecalho(st, "Análises de negócio em um só lugar", "G4 Analise")
    st.write("Crie uma **sessão**, escolha a ferramenta e carregue os dados. Cada ferramenta resolve seu desafio sozinha, "
             "e o resultado de uma pode alimentar outra (ex.: contas em risco de churn → análise de suporte).")
    colunas = st.columns(4)
    for col, m in zip(colunas, MODULOS.values()):
        with col.container(border=True):
            st.markdown(f"{visual.ICONES_MODULO[m.chave]} **{m.nome}**")
            st.caption(f"Desafio {m.desafio}")
            st.write(m.descricao)
    st.button("Nova sessão", on_click=ir, args=("nova",), type="primary", icon=":material/add:")


# ---------- nova sessao ----------

def pagina_nova():
    visual.cabecalho(st, "Nova sessão", "G4 Analise")
    nome = st.text_input("Nome da sessão", placeholder="Ex.: Churn RavenStack - setembro")
    chave = st.radio("Tipo de análise", list(MODULOS), format_func=rotulo_modulo, horizontal=True)
    modulo = MODULOS[chave]
    st.caption(modulo.descricao)
    fonte = st.radio("Dados", ["desafio", "arquivos"], horizontal=True,
                     format_func=lambda f: "Usar os dados do desafio" if f == "desafio" else "Enviar meus arquivos")

    if fonte == "desafio":
        nova_com_dados_do_desafio(nome, modulo)
    else:
        nova_com_arquivos(nome, modulo)


def nova_com_dados_do_desafio(nome, modulo):
    pasta = leitura.pasta_dados_desafio()
    if not pasta:
        st.error("Não encontrei a pasta de dados do desafio. Coloque os arquivos em `dados/` (veja o README).")
        return
    arquivos, faltam = {}, []
    for t in modulo.tabelas:
        caminho = os.path.join(pasta, t.arquivo_desafio)
        if os.path.exists(caminho):
            arquivos[t.nome] = caminho
        elif t.obrigatoria:
            faltam.append(t.arquivo_desafio)
    st.write("**Arquivos que serão usados:**")
    for t in modulo.tabelas:
        marca = (visual.selo("encontrado", "green") if t.nome in arquivos else
                 visual.selo("falta", "red") if t.obrigatoria else visual.selo("opcional, não encontrado", "gray"))
        st.markdown(f"{marca} {t.rotulo} — `{t.arquivo_desafio}`")
    if faltam:
        st.error("Faltam arquivos obrigatórios: " + ", ".join(faltam))
        return
    if st.button("Criar sessão", type="primary", disabled=not nome.strip()):
        novo = criar_sessao_desafio(nome.strip(), modulo.chave)
        ir("sessao", novo)
        st.rerun()
    if not nome.strip():
        st.caption("Dê um nome à sessão para criar.")


def nova_com_arquivos(nome, modulo):
    st.write("Envie um arquivo por tabela (CSV, Excel ou JSON) e ligue as colunas aos campos do sistema.")
    enviados, mapas, problemas = {}, {}, []
    for t in modulo.tabelas:
        with st.container(border=True):
            st.subheader(t.rotulo + ("" if t.obrigatoria else "  (opcional)"))
            arquivo = st.file_uploader("Arquivo", type=list(leitura.FORMATOS), key=f"up_{modulo.chave}_{t.nome}")
            if arquivo is None:
                if t.obrigatoria:
                    problemas.append(f"Falta o arquivo de {t.rotulo}.")
                continue
            try:
                df = leitura.ler(arquivo)
            except Exception as erro:
                st.error(f"Não consegui ler o arquivo: {erro}")
                problemas.append(f"Arquivo de {t.rotulo} ilegível.")
                continue
            st.caption(f"{len(df):,} linhas · {df.shape[1]} colunas".replace(",", "."))
            with st.expander("Ver perfil das colunas"):
                st.dataframe(leitura.perfil(df), hide_index=True, width="stretch")
            sugestao = depara.sugerir(t, df.columns)
            opcoes = [""] + list(df.columns)
            mapa = {}
            cols = st.columns(3)
            for i, c in enumerate(t.campos):
                with cols[i % 3]:
                    padrao = sugestao.get(c.nome) or ""
                    mapa[c.nome] = st.selectbox(
                        c.rotulo + (" *" if c.obrigatorio else ""), opcoes,
                        index=opcoes.index(padrao), key=f"map_{modulo.chave}_{t.nome}_{c.nome}") or None
            falta = depara.faltando(t, mapa)
            if falta:
                problemas.append(f"{t.rotulo}: ligue os campos obrigatórios ({', '.join(falta)}).")
            enviados[t.nome], mapas[t.nome] = arquivo, mapa

    st.caption("* campo obrigatório")
    for p in problemas:
        st.warning(p)
    if st.button("Criar sessão", type="primary", disabled=bool(problemas) or not nome.strip()):
        novo = sessoes.criar(nome.strip(), modulo.chave, "arquivos", mapas, {})
        caminhos = {t: sessoes.salvar_arquivo(novo, t, a) for t, a in enviados.items()}
        sessoes.atualizar_arquivos(novo, caminhos)
        ir("sessao", novo)
        st.rerun()


# ---------- sessao ----------

def pagina_sessao(sessao_id):
    s = sessoes.obter(sessao_id)
    if not s:
        st.warning("Sessão não encontrada.")
        return
    modulo = MODULOS[s["modulo"]]
    visual.cabecalho(st, s["nome"], f"{modulo.nome} · desafio {modulo.desafio}")
    st.caption(f"Dados: "
               f"{FONTES.get(s['fonte'], s['fonte'])} · criada em {s['criada_em'].replace('T', ' ')}")
    if s["origem_id"]:
        cor, texto = cruzamentos.SELOS.get(s["selo"], ("gray", ""))
        st.markdown(f"{visual.selo(texto, cor)} Veio de: {s['origem_descricao'].replace('$', chr(92) + '$')}")
        if sessoes.obter(s["origem_id"]) and st.button("Voltar para a sessão de origem", icon=":material/arrow_back:",
                                                       type="tertiary"):
            ir("sessao", s["origem_id"])
            st.rerun()

    aba_analise, aba_dados, aba_cruz, aba_exp = st.tabs([":material/analytics: Análise", ":material/table_chart: Dados",
                                                          ":material/hub: Usar em outra ferramenta",
                                                          ":material/ios_share: Exportar"])
    with aba_dados:
        mostrar_dados(s, modulo)
    resultado = None
    with aba_analise:
        if modulo.chave in TELAS_PRONTAS:
            resultado = TELAS_PRONTAS[modulo.chave].render(s)
        else:
            st.info(f"O módulo **{modulo.nome}** (desafio {modulo.desafio}) é construído na etapa "
                    f"{ETAPA_DO_MODULO[modulo.chave]} do plano. Os dados desta sessão já estão prontos para ele.")
    with aba_cruz:
        mostrar_cruzamentos(s, modulo, resultado)
    with aba_exp:
        mostrar_exportar(s, modulo, resultado)

    st.divider()
    with st.expander("Apagar sessão"):
        confirma = st.checkbox("Confirmo que quero apagar esta sessão (e as sub-sessões dela).")
        if st.button("Apagar", disabled=not confirma):
            sessoes.apagar(sessao_id)
            ir("inicio")
            st.rerun()


def mostrar_dados(s, modulo):
    for t in modulo.tabelas:
        caminho = s["arquivos"].get(t.nome)
        with st.container(border=True):
            st.subheader(t.rotulo)
            if not caminho:
                st.caption("Não informado" + (" (obrigatório!)" if t.obrigatoria else " (opcional)"))
                continue
            if not os.path.exists(caminho):
                st.error(f"Arquivo não encontrado: {caminho}")
                continue
            df = ler_da_sessao(caminho)
            mapa = s["mapeamento"].get(t.nome, {})
            ausentes = [col for col in mapa.values() if col and col not in df.columns]
            st.caption(f"{len(df):,} linhas · {df.shape[1]} colunas · `{os.path.basename(caminho)}`".replace(",", "."))
            if ausentes:
                st.error("Colunas do De/Para que não existem no arquivo: " + ", ".join(ausentes))
            ligacao = pd.DataFrame([{
                "campo do sistema": c.rotulo + (" *" if c.obrigatorio else ""),
                "coluna do arquivo": mapa.get(c.nome) or "—",
            } for c in t.campos])
            c1, c2 = st.columns([2, 3])
            with c1:
                st.write("**De/Para**")
                st.dataframe(ligacao, hide_index=True, width="stretch")
            with c2:
                st.write("**Perfil das colunas**")
                st.dataframe(leitura.perfil(df), hide_index=True, width="stretch")


def mostrar_exportar(s, modulo, resultado):
    if resultado is None:
        st.info("Rode a análise desta sessão primeiro.")
        return
    st.write(f"Os arquivos são gravados em **{pasta_de_saida()}** (com data e hora no nome, nada é sobrescrito).")
    c1, c2 = st.columns(2)
    with c1.container(border=True):
        st.markdown("**Dados analisados (CSV)**")
        st.caption("Uma linha por item analisado (conta, chamado, deal ou post) com TODAS as colunas calculadas: score, "
                   "faixa, motivos, sinais etc. Separador ';' e vírgula decimal: abre direto no Excel.")
        botao_salvar(st, "Salvar CSV", lambda: csv_principal(modulo.chave, resultado), f"{modulo.chave}_dados_analisados.csv",
                     key=f"exp_csv_{s['id']}")
    with c2.container(border=True):
        st.markdown("**Tudo junto (Excel)**")
        st.caption("Um arquivo com uma aba por tabela: os dados analisados + cada tabela da análise (segmentos, testes, "
                   "ações, validação...). Um CSV só não comporta tabelas com colunas diferentes; o Excel sim.")
        botao_salvar(st, "Salvar Excel", lambda: excel_completo(modulo.chave, resultado), f"{modulo.chave}_analise_completa.xlsx",
                     key=f"exp_xlsx_{s['id']}")


def mostrar_cruzamentos(s, modulo, resultado):
    st.write("O resultado desta análise pode ser usado por estas ferramentas. Cada envio cria uma **sub-sessão** "
             "(aparece embaixo desta na barra lateral) com um selo que diz o quanto a ligação é forte.")
    with st.expander("O que significam os selos"):
        for cor, texto in cruzamentos.SELOS.values():
            st.markdown(visual.selo(texto, cor))
        st.caption("Tipo A = a outra ferramenta roda nos mesmos dados. Tipo B = o resultado vira um perfil que filtra "
                   "outra base (hipótese para testar, não prova).")
    ja_criadas = sessoes.filhas(s["id"])
    for destino, selo, tipo, descricao in cruzamentos.destinos(modulo.chave):
        cor, texto = cruzamentos.SELOS[selo]
        chave = f"c_{s['id']}_{destino}"
        with st.container(border=True):
            st.markdown(f"{visual.ICONES_MODULO[destino]} **{MODULOS[destino].nome}** {visual.selo(texto, cor)}"
                        + (f" · Tipo {tipo}" if tipo not in ("-", "lista") else ""))
            st.caption(descricao)
            if selo == "bloqueado":
                st.button("Indisponível", key=chave, disabled=True)
                continue
            if (modulo.chave, destino) not in PONTES:
                st.button("Em construção (próximas etapas do plano)", key=chave, disabled=True)
                continue
            if resultado is None:
                st.button("Rode a análise desta sessão primeiro", key=chave, disabled=True)
                continue
            if tipo == "lista":
                try:
                    saida = PONTES[(modulo.chave, destino)](s, resultado)
                except (KeyError, ValueError) as erro:
                    st.error(f"Não deu para montar a lista: {erro}")
                    continue
                st.write(saida["resumo"])
                botao_salvar(st, "Salvar lista (CSV)", lambda: saida["df"].to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"), saida["arquivo"], key=chave)
                continue
            base = None
            if tipo == "B":
                opcoes = perfis.bases_de_destino(destino)
                if not opcoes:
                    st.info(f"Crie antes uma sessão de {MODULOS[destino].nome} (ou use os dados do desafio) para servir de base.")
                    continue
                i = st.selectbox(f"Base de {MODULOS[destino].nome} que o perfil vai filtrar", range(len(opcoes)),
                                 format_func=lambda k: opcoes[k][0], key=f"base_{chave}")
                base = opcoes[i][1]
            if st.button(f"Enviar para {MODULOS[destino].nome}", key=chave, type="primary", icon=":material/send:"):
                try:
                    novo = criar_sub_sessao(s, destino, resultado, base)
                except (KeyError, ValueError) as erro:
                    st.error(f"Não deu para montar o envio: {erro}")
                else:
                    ir("sessao", novo)
                    st.rerun()
            for f in [f for f in ja_criadas if f["modulo"] == destino]:
                if st.button(f"Abrir: {f['nome']} (criada em {f['criada_em'].replace('T', ' ')})", key=f"abre_{f['id']}"):
                    ir("sessao", f["id"])
                    st.rerun()
            st.caption("Os envios usam as premissas que estão na tela da análise neste momento.")


# ---------- roteamento ----------

st.session_state.setdefault("pagina", "inicio")
barra_lateral()
if st.session_state["pagina"] == "nova":
    pagina_nova()
elif st.session_state["pagina"] == "sessao" and st.session_state.get("sessao_id"):
    pagina_sessao(st.session_state["sessao_id"])
else:
    pagina_inicio()
