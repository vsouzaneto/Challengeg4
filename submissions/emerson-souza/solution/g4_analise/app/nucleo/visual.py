"""
Identidade visual do G4 Analise: sobria, sem emojis, com barra lateral grafite e cor petroleo.

Cores e fontes do tema ficam em .streamlit/config.toml; aqui ficam a paleta dos graficos, os selos de evidencia
(badges de texto) e o pouco de CSS que o tema nao cobre.
"""

import re

# paleta (graficos, PDF e selos) -- a mesma do config.toml
PETROLEO = "#4F46E5"      # cor principal (indigo) -- nome mantido por compatibilidade
AZUL_ACO = "#5B6B8C"
AMBAR = "#F2A541"
TIJOLO = "#D1495B"
MUSGO = "#3BB273"
GRAFITE = "#1E2433"
CINZA = "#9AA5B1"
CLARO = "#DCEAF2"
# paleta colorida para diferenciar categorias (graficos, cartoes, icones)
PALETA = ["#2E86AB", "#E4572E", "#3BB273", "#F2A541", "#6C5CE7", "#17A398", "#D1495B", "#8D6A9F"]
SEQUENCIA = PALETA


def cores(n):
    """n cores diferentes da paleta (repete se passar de 8)."""
    return [PALETA[i % len(PALETA)] for i in range(n)]

ICONES_MODULO = {"churn": ":material/person_remove:", "suporte": ":material/support_agent:",
                 "leads": ":material/trending_up:", "midia": ":material/campaign:"}
COR_MODULO = {"churn": "red", "suporte": "green", "leads": "blue", "midia": "violet"}   # cor de cada ferramenta


def icone_colorido(chave):
    return f":{COR_MODULO[chave]}[{ICONES_MODULO[chave]}]"


# icones sobrios (Material) das abas das ferramentas
ICONES_ABA = {
    "Resumo executivo": "summarize", "Causa raiz": "troubleshoot", "Segmentos e contas": "groups",
    "Plano de ação": "checklist", "Modelo e método": "model_training", "Qualidade dos dados": "fact_check",
    "Relatório": "description", "Como ler": "help", "Onde trava": "hourglass_bottom",
    "Satisfação": "sentiment_satisfied", "Desperdício": "money_off", "Automação": "smart_toy",
    "Testar ticket": "science", "Minha segunda-feira": "event", "Visão do gestor": "supervisor_account",
    "O que muda a chance": "insights", "Validação e método": "verified", "O que gera engajamento": "trending_up",
    "Patrocínio": "paid", "Audiência": "groups", "Estratégia": "flag", "Painel semanal": "monitoring",
    "Recomendar post": "lightbulb", "Sanidade e método": "rule",
}


def abas(nomes):
    """Rotulos das abas com icone sobrio na frente."""
    return [f":material/{ICONES_ABA[n]}: {n}" if n in ICONES_ABA else n for n in nomes]

_EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✅❌➕↩️]\\s*")


def sem_emoji(texto):
    return _EMOJI.sub("", str(texto)).strip()


def selo(texto, cor):
    """Badge de texto (cor: green, orange, blue, red, gray, violet)."""
    return f":{cor}-badge[{texto}]"


def selo_evidencia(evidencia):
    e = str(evidencia).lower()
    if e.startswith(("forte", "comprovado", "fato", "testado")):
        return selo(evidencia, "green")
    if e.startswith(("cálculo", "decisão")):
        return selo(evidencia, "blue")
    if e.startswith(("fraca", "indício", "regra", "motivo")):
        return selo(evidencia, "orange")
    return selo(evidencia, "gray")


CSS = f"""
<style>
/* cabecalho proprio */
.g4-sobre {{ font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: {AZUL_ACO}; margin: 0 0 .15rem 0; }}
.g4-titulo {{ font-size: 1.85rem; font-weight: 600; color: {GRAFITE}; margin: 0; line-height: 1.2; }}
.g4-linha {{ height: 3px; width: 56px; background: {PETROLEO}; margin: .55rem 0 .35rem 0; }}
.g4-marca {{ font-size: .8rem; letter-spacing: .22em; text-transform: uppercase; font-weight: 700; color: #E3E6F0; }}
.g4-marca span {{ color: #A5B4FC; }}
/* barra lateral: lista de sessoes alinhada a esquerda, como um menu */
section[data-testid="stSidebar"] .stButton button {{ justify-content: flex-start !important; text-align: left; padding-left: .6rem; }}
section[data-testid="stSidebar"] .stButton button > div {{ justify-content: flex-start !important; width: 100%; }}
section[data-testid="stSidebar"] .stButton button p {{ text-align: left !important; }}
/* indicadores como cartoes com filete petroleo */
div[data-testid="stMetric"] {{ border: 1px solid #D6DDE2; border-left: 4px solid {PALETA[0]}; padding: .55rem .8rem;
    background: #FFFFFF; border-radius: 2px; }}
div[data-testid="stColumn"]:nth-child(2) div[data-testid="stMetric"] {{ border-left-color: {PALETA[1]}; }}
div[data-testid="stColumn"]:nth-child(3) div[data-testid="stMetric"] {{ border-left-color: {PALETA[2]}; }}
div[data-testid="stColumn"]:nth-child(4) div[data-testid="stMetric"] {{ border-left-color: {PALETA[3]}; }}
div[data-testid="stMetricLabel"] p {{ text-transform: uppercase; letter-spacing: .06em; font-size: .72rem; color: #5A6B78; }}
/* abas em caixa alta discreta */
button[data-baseweb="tab"] p {{ font-size: .86rem; letter-spacing: .02em; }}
</style>
"""


def aplicar_estilo(st):
    st.markdown(CSS, unsafe_allow_html=True)


def cabecalho(st, titulo, sobre=""):
    from html import escape
    st.markdown(
        f'<div class="g4-sobre">{escape(sobre)}</div>'
        f'<div class="g4-titulo" style="font-size:1.85rem;font-weight:600;color:{GRAFITE};line-height:1.2">{escape(titulo)}</div>'
        f'<div class="g4-linha"></div>', unsafe_allow_html=True)


def marca(st_sidebar):
    st_sidebar.markdown('<div class="g4-marca">G4 <span>Analise</span></div>', unsafe_allow_html=True)


def tema_plotly():
    """Tema padrao dos graficos Plotly: mesma fonte e paleta, grade discreta."""
    import plotly.graph_objects as go
    import plotly.io as pio
    t = go.layout.Template(pio.templates["plotly_white"])
    t.layout.colorway = SEQUENCIA
    t.layout.font = dict(family='"Segoe UI", "Helvetica Neue", Arial, sans-serif', color="#33424F", size=12)
    t.layout.xaxis.gridcolor = t.layout.yaxis.gridcolor = "#E6EBEE"
    t.layout.separators = ",."   # virgula decimal e ponto de milhar (pt-BR)
    t.layout.paper_bgcolor = "#FFFFFF"
    t.layout.plot_bgcolor = "#FFFFFF"
    pio.templates["g4"] = t
    pio.templates.default = "g4"
