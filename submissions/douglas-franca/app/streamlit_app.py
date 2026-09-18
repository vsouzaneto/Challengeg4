"""Decision Gate: a ferramenta que roda o processo TO-BE (docs/process/03-to-be.md).

Rodar localmente: uv run streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.audit.health import health_check, verdict as health_verdict  # noqa: E402
from src.decision.rules import (  # noqa: E402
    REQUIRED_CONTRACT_FIELDS,
    SESOI_PP,
    CycleResult,
    ci_from_arms,
    contract_gaps,
    cycle_decision,
    sales_to_break_even,
    sample_size_per_arm,
)
from src.decision.stats import VERDICT_HELP, level_vs_rest  # noqa: E402
from src import app_data  # noqa: E402

ASSETS = Path(__file__).resolve().parent / "assets"
MAIN_PLATFORMS = ["Instagram", "TikTok", "YouTube"]
DIMENSIONS = {
    "Formato": "content_type",
    "Categoria": "content_category",
    "Faixa de seguidores": "tier",
    "Patrocinado": "is_sponsored",
    "Tipo de divulgação": "disclosure_type",
    "Idade da audiência": "audience_age",
    "Gênero da audiência": "audience_gender",
    "País da audiência": "audience_location",
    "Plataforma": "platform",
}
TIER_ORDER = ["<10K", "10–50K", "50–100K", "100–500K", "500K–1M"]
BLUE, INK2, BAND = "#2a78d6", "#52514e", "rgba(120,120,110,0.14)"
VERDICT_ICON = {"EQUIVALENTE": "⚪", "DIFERENTE, MAS IRRELEVANTE": "🟡", "DIFERENTE": "🟢", "INCONCLUSIVO": "❔"}

st.set_page_config(page_title="Decision Gate · Social Media", page_icon="🚦", layout="wide")


@st.cache_data(show_spinner="Carregando os 52.214 posts do challenge (na primeira abertura, o download leva alguns segundos)...")
def load_posts() -> pd.DataFrame:
    return app_data.load_posts()


@st.cache_data
def challenge_health() -> tuple[bool, str, list]:
    checks = health_check(load_posts())
    ok, message = health_verdict(checks)
    return ok, message, checks


def render_checks(checks: list) -> None:
    table = pd.DataFrame([{"": "✅" if c.passed else "❌", "Regra": f"{c.code} · {c.name}",
                           "Resultado": c.detail, "Por que importa": c.why} for c in checks])
    st.dataframe(table, hide_index=True, width="stretch", height=38 * (len(table) + 1),
                 column_config={"": st.column_config.TextColumn(width=40),
                                "Regra": st.column_config.TextColumn(width="medium"),
                                "Resultado": st.column_config.TextColumn(width="medium"),
                                "Por que importa": st.column_config.TextColumn(width="large")})


# ---------------------------------------------------------------- cabeçalho
st.title("🚦 Decision Gate · Social Media")
st.caption("Ferramenta do novo processo de decisão (Challenge 004 · Douglas França). "
           f"Régua de decisão: taxa de engajamento, diferença mínima relevante de ±{SESOI_PP:g} p.p.")

ok, message, _ = challenge_health()
if not ok:
    st.error(f"**Arquivo do challenge: {message}.** Os números do painel servem para demonstrar o método, "
             "não para decidir. Veja a aba 1.", icon="🛑")

with st.sidebar:
    st.subheader("Status")
    posts = load_posts()
    st.write(f"🟢 App no ar · {len(posts):,} posts carregados".replace(",", "."))
    st.write("Health check: `/healthz` (online) · `/_stcore/health` (local)")
    st.divider()
    st.markdown("**Como usar, na ordem do ciclo**\n\n"
                "1. Checar se os dados servem\n2. Acompanhar com margem de erro\n"
                "3. Aprovar (ou bloquear) um patrocínio\n4. Fechar o ciclo de 30 dias")
    st.divider()
    st.caption("Decisões de gasto e de escala são sempre humanas: a ferramenta calcula e sugere.")

def render_panel() -> None:
    """Aba 2. Função para poder encerrar cedo sem interromper as abas 3 e 4."""
    st.subheader("Painel: diferença de cada grupo contra o resto, com margem de erro")
    st.write(f"A faixa cinza é a zona **irrelevante para decisão** (±{SESOI_PP:g} p.p.). "
             "Só um intervalo que sai inteiro da faixa justifica mexer em verba. Não há ranking de médias.")
    checked = st.session_state.get("checked")
    bases = ["Arquivo do challenge"] + ([f"Arquivo checado na aba 1 ({checked['label']})"] if checked else [])
    base = st.radio("Base", bases, horizontal=True,
                    help="Envie ou escolha um arquivo na aba 1 para analisá-lo aqui. A análise usa as mesmas regras.")
    panel, panel_platforms = posts, MAIN_PLATFORMS
    if base != "Arquivo do challenge":
        try:
            panel = app_data.to_panel_frame(checked["df"])
        except ValueError as err:
            st.error(f"Este arquivo não pode ir para o painel: {err}.")
            return
        panel_platforms = sorted(panel.platform.astype(str).unique())
        if not checked["passed"]:
            st.warning(f"Este arquivo foi **reprovado no Gate 0** ({checked['msg']}). "
                       "O painel mostra os números, mas eles não sustentam decisão de verba.", icon="⚠️")
    dims = {k: v for k, v in DIMENSIONS.items() if v in panel.columns}
    c1, c2 = st.columns([2, 1])
    with c1:
        platforms = st.multiselect("Plataformas", sorted(panel.platform.astype(str).unique()),
                                   default=[p for p in panel_platforms if p in set(panel.platform.astype(str))],
                                   help="Bilibili e RedNote ficam fora do escopo da empresa; disponíveis como referência.")
    with c2:
        dim_label = st.selectbox("Comparar por", list(dims))
    dim = dims[dim_label]
    scope = panel[panel.platform.astype(str).isin(platforms)]
    if dim == "platform" and len(platforms) < 2:
        st.warning("Escolha ao menos duas plataformas para comparar.")
    elif scope.empty:
        st.warning("Escolha ao menos uma plataforma.")
    else:
        levels = [t for t in TIER_ORDER if t in set(scope[dim].astype(str))] if dim == "tier" else None
        data = scope.assign(**{dim: scope[dim].astype(str)})
        table = level_vs_rest(data, dim, levels=levels, min_n=30)
        if table.empty:
            st.info("Nenhum grupo tem ao menos 30 posts de cada lado para comparar. Escolha outra dimensão.")
            return
        k1, k2, k3 = st.columns(3)
        k1.metric("Posts no filtro", f"{len(scope):,}".replace(",", "."))
        k2.metric("Taxa de engajamento média", f"{scope.er.mean():.2f}%")
        k3.metric("Comparações que mudam a decisão",
                  f"{int((table.veredito == 'DIFERENTE').sum())} de {len(table)}")

        fig = go.Figure()
        fig.add_vrect(x0=-SESOI_PP, x1=SESOI_PP, fillcolor=BAND, line_width=0)
        fig.add_annotation(x=0, y=1, xref="x", yref="paper", yanchor="bottom", showarrow=False,
                           text=f"faixa irrelevante para decisão (±{SESOI_PP:g} p.p.)", font={"color": INK2})
        fig.add_vline(x=0, line_color=INK2, line_width=1)
        fig.add_trace(go.Scatter(
            x=table.diferenca_pp, y=table.nivel, mode="markers",
            marker={"size": 10, "color": BLUE, "line": {"color": "white", "width": 2}},
            error_x={"type": "data", "symmetric": False, "array": table.ic95_sup - table.diferenca_pp,
                     "arrayminus": table.diferenca_pp - table.ic95_inf, "color": BLUE, "thickness": 2, "width": 0},
            customdata=table[["n_grupo", "media_grupo", "ic95_inf", "ic95_sup", "veredito"]],
            hovertemplate=("<b>%{y}</b><br>n = %{customdata[0]:,}<br>média = %{customdata[1]:.3f}%<br>"
                           "diferença = %{x:+.3f} p.p.<br>IC 95%: %{customdata[2]:+.3f} a %{customdata[3]:+.3f}"
                           "<br>%{customdata[4]}<extra></extra>"),
            showlegend=False))
        fig.update_layout(height=120 + 42 * len(table), margin={"l": 10, "r": 10, "t": 40, "b": 40},
                          xaxis={"title": "diferença na taxa de engajamento vs. resto (p.p.)",
                                 "range": [-1.4, 1.4], "zeroline": False},
                          yaxis={"autorange": "reversed"}, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch")

        shown = table.assign(
            veredito=table.veredito.map(lambda v: f"{VERDICT_ICON[v]} {v}: {VERDICT_HELP[v]}"),
            ic95=[f"{lo:+.3f} a {hi:+.3f}" for lo, hi in zip(table.ic95_inf, table.ic95_sup)],
        )[["nivel", "n_grupo", "media_grupo", "diferenca_pp", "ic95", "p_ajustado_bh", "veredito"]]
        st.dataframe(shown.rename(columns={"nivel": dim_label, "n_grupo": "n", "media_grupo": "média (%)",
                                           "diferenca_pp": "diferença (p.p.)", "ic95": "IC 95% (p.p.)",
                                           "p_ajustado_bh": "p ajustado"}),
                     hide_index=True, width="stretch",
                     column_config={"média (%)": st.column_config.NumberColumn(format="%.3f"),
                                    "diferença (p.p.)": st.column_config.NumberColumn(format="%+.4f"),
                                    "p ajustado": st.column_config.NumberColumn(format="%.2f")})
        st.caption("p ajustado: correção de Benjamini-Hochberg para múltiplos testes. "
                   "Sem ela, ruído vira 'insight' (ex.: 'patrocínio de moda é pior').")


tab1, tab2, tab3, tab4 = st.tabs(["1 · Os dados servem?", "2 · Painel com margem de erro",
                                  "3 · Aprovar patrocínio", "4 · Fechar ciclo de 30 dias"])

# ---------------------------------------------------------------- 1. Gate 0
with tab1:
    st.subheader("Gate 0: este arquivo pode sustentar uma decisão?")
    st.write("Antes de qualquer análise, a pergunta: **de onde vieram estes dados, e eles se comportam como uma "
             "operação real?** As regras vêm da auditoria do arquivo do challenge e do contrato de dados.")
    source = st.radio("Arquivo", ["Arquivo do challenge (52.214 posts)",
                                  "Exemplo sintético bem instrumentado (fictício)", "Enviar meu CSV"],
                      horizontal=True)
    df_check = None
    if source.startswith("Arquivo do challenge"):
        df_check = load_posts()
    elif source.startswith("Exemplo"):
        df_check = pd.read_csv(ASSETS / "exemplo_sintetico_contrato_de_dados.csv")
        st.info("Dado **fictício**, gerado para mostrar como um arquivo instrumentado passa no gate "
                "(`scripts/build_app_assets.py`).")
    else:
        uploaded = st.file_uploader("CSV com colunas de métricas (views, likes, shares, comments) e, se possível, "
                                    "as colunas do contrato de dados", type="csv")
        if uploaded is not None:
            df_check = pd.read_csv(uploaded)
    if df_check is not None:
        checks = health_check(df_check)
        passed, msg = health_verdict(checks)
        (st.success if passed else st.error)(msg)
        render_checks(checks)
        if not source.startswith("Arquivo do challenge"):
            st.session_state["checked"] = {"label": source, "df": df_check, "passed": passed, "msg": msg}
            st.caption("Este arquivo fica disponível no painel da aba 2.")

# ---------------------------------------------------------------- 2. Painel
with tab2:
    render_panel()

# ---------------------------------------------------------------- 3. Gate 1
with tab3:
    st.subheader("Gate 1: este contrato de patrocínio pode virar piloto?")
    st.write("O gestor de parcerias preenche; a ferramenta aponta o que falta e calcula quanto o contrato precisa "
             "vender. **A aprovação final é do Head de Marketing, com o custo validado pelo Financeiro.**")
    with st.form("contrato"):
        a, b, c = st.columns(3)
        with a:
            campaign_id = st.text_input("campaign_id (CRM)")
            crm_deal_id = st.text_input("ID do negócio no pipeline de parceria")
            creator_id = st.text_input("creator_id (cadastro mestre)")
            objetivo = st.selectbox("Objetivo", ["venda", "alcance", "engajamento"], index=None,
                                    placeholder="Selecione")
            hypothesis_id = st.text_input("ID da hipótese pré-registrada")
        with b:
            fee = st.number_input("Fee do creator (R$)", min_value=0.0, value=3000.0, step=100.0)
            producao = st.number_input("Custo de produção e mídia (R$)", min_value=0.0, value=0.0, step=100.0)
            margem = st.number_input("Margem de contribuição por venda (R$)", min_value=0.0, value=50.0, step=5.0)
            vendas_esperadas = st.number_input("Vendas incrementais esperadas", min_value=0.0, value=40.0, step=5.0)
            cupom = st.text_input("Cupom exclusivo")
            utm = st.text_input("UTM exclusiva")
        with c:
            grupo_comparacao = st.text_input("Grupo de comparação (como foi montado)")
            desvio = st.number_input("Desvio esperado da taxa de engajamento por post (p.p.)",
                                     min_value=0.5, value=5.0, step=0.5,
                                     help="O AI Master estima com o histórico que passou no Gate 0.")
            aprovado_por = st.text_input("Aprovado por (Head + Financeiro)")
            aprovado_em = st.text_input("Data da aprovação")
        submitted = st.form_submit_button("Checar contrato")
    if submitted:
        needed = sales_to_break_even(fee, margem, producao) if margem > 0 else float("inf")
        contract = {
            "campaign_id": campaign_id, "crm_deal_id": crm_deal_id, "creator_id": creator_id,
            "custo_total": fee + producao if fee + producao > 0 else None, "objetivo": objetivo,
            "hypothesis_id": hypothesis_id, "metrica_primaria": objetivo or None,
            "regua": SESOI_PP, "break_even": needed if margem > 0 else None,
            "grupo_comparacao": grupo_comparacao, "cupom": cupom, "utm": utm,
            "aprovado_por": aprovado_por, "aprovado_em": aprovado_em,
        }
        gaps = contract_gaps(contract)
        m1, m2, m3 = st.columns(3)
        m1.metric("Vendas extras para empatar", "—" if margem <= 0 else f"{needed:,.0f}".replace(",", "."))
        m2.metric("Folga sobre o break-even", "—" if margem <= 0 else f"{vendas_esperadas - needed:+,.0f} vendas".replace(",", "."))
        m3.metric("Posts por braço no teste", f"{sample_size_per_arm(desvio):,}".replace(",", "."))
        if gaps:
            st.error(f"🛑 **BLOQUEADO:** faltam {len(gaps)} de {len(REQUIRED_CONTRACT_FIELDS)} campos obrigatórios: "
                     + ", ".join(f"`{g}`" for g in gaps))
        elif margem > 0 and vendas_esperadas < needed:
            st.warning("⚠️ **Completo, mas a expectativa de vendas não cobre o custo.** "
                       "Renegocie o fee ou revise a hipótese antes de aprovar.")
        else:
            st.success("✅ **Pronto para piloto.** Registre a decisão humana no CRM e inclua o contrato no ciclo de 30 dias.")
        st.caption("Break-even = (fee + produção) ÷ margem por venda. Engajamento não entra na conta: "
                   "no melhor cenário do arquivo do challenge, um post patrocinado gera 0,77 interação extra.")

# ---------------------------------------------------------------- 4. Fechamento
with tab4:
    st.subheader("Fechamento do ciclo de 30 dias")
    st.write("Envie o resultado por post (colunas `test_arm` = tratamento/comparacao e `engagement_rate_pp`). "
             "No dia 15 a leitura é só acompanhamento; **a decisão sai aqui, no dia 30**.")
    use_example = st.toggle("Usar resultado de exemplo (fictício)", value=True)
    result_df = None
    if use_example:
        result_df = pd.read_csv(ASSETS / "exemplo_sintetico_resultado_teste.csv")
    else:
        up = st.file_uploader("CSV do teste", type="csv", key="teste")
        if up is not None:
            result_df = pd.read_csv(up)
    e1, e2, e3 = st.columns(3)
    execution_ok = e1.checkbox("Execução conforme o pré-registro", value=True)
    completeness = e2.slider("Completude dos dados do teste", 0.0, 1.0, 0.98, 0.01)
    has_cost = e3.checkbox("Teste com custo (patrocínio)", value=False)
    ret = None
    if has_cost:
        r1, r2, r3 = st.columns(3)
        vendas = r1.number_input("Vendas incrementais atribuídas", min_value=0.0, value=40.0)
        margem_r = r2.number_input("Margem por venda (R$)", min_value=0.0, value=50.0, key="margem_r")
        custo_r = r3.number_input("Custo total do teste (R$)", min_value=0.0, value=3000.0)
        ret = vendas * margem_r - custo_r
    if result_df is not None:
        required = {"test_arm", "engagement_rate_pp"}
        if not required <= set(result_df.columns):
            st.error(f"O CSV precisa das colunas {sorted(required)}.")
        else:
            arms = result_df.groupby("test_arm").engagement_rate_pp.agg(["mean", "std", "size"])
            if not {"tratamento", "comparacao"} <= set(arms.index):
                st.error("A coluna test_arm precisa ter os valores 'tratamento' e 'comparacao'.")
            else:
                t, cmp_ = arms.loc["tratamento"], arms.loc["comparacao"]
                diff, low, high = ci_from_arms(t["mean"], t["std"], int(t["size"]),
                                               cmp_["mean"], cmp_["std"], int(cmp_["size"]))
                decision, reason = cycle_decision(CycleResult(diff, low, high, execution_ok, completeness, ret))
                s1, s2, s3 = st.columns(3)
                s1.metric("Efeito (p.p.)", f"{diff:+.2f}")
                s2.metric("IC 95%", f"{low:+.2f} a {high:+.2f}")
                s3.metric("Retorno sobre o break-even", "sem custo" if ret is None else f"R$ {ret:,.0f}".replace(",", "."))
                icon = {"Escalar": "🟢", "Replicar": "🔵", "Iterar": "🟠", "Parar": "🔴"}[decision]
                st.markdown(f"### {icon} Sugestão: **{decision}**")
                st.write(f"Motivo: {reason}.")
                st.caption("A sugestão segue a regra pré-registrada (`src/decision/rules.py`). "
                           "Quem decide é o Head de Marketing, e a decisão fica registrada com justificativa.")
                st.dataframe(arms.rename(columns={"mean": "média (p.p.)", "std": "desvio", "size": "posts"}),
                             width="stretch")
