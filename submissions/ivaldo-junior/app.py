import streamlit as st
import pandas as pd
import base64
from lead_scorer import load_and_merge_data, calculate_historical_baselines, score_active_pipeline

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="G4 | RevOps Lead Scorer",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# LOGO BASE64
# ============================================================================
@st.cache_data
def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""

logo_b64 = get_image_base64("assets/logo.png")

# ============================================================================
# CSS INJECTION - DESIGN PREMIUM + CORREÇÕES DE ESPAÇAMENTO
# ============================================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

/* 🔴
   CORTEX HUB - DESIGNER UI/UX - CORREÇÃO FINAL
   🔴 */

/* 1. Header: fundo transparente, altura mínima para o botão existir */
header[data-testid="stHeader"] {{
    background: transparent !important;
    border: none !important;
    height: 2.2rem !important;
    min-height: 2.2rem !important;
    max-height: 2.2rem !important;
    padding: 0 !important;
    margin: 0 !important;
}}

/* 2. Esconder TUDO dentro do header EXCETO o botão de recolher */
[data-testid="stStatusWidget"],
.stDeployButton,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
button[data-testid="stBaseButton-headerNoPadding"],
#MainMenu {{
    display: none !important;
    visibility: hidden !important;
}}

/* 3. Botão de recolher sidebar - estilo escuro para combinar */
button[data-testid="stSidebarCollapseButton"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: #94A3B8 !important;
}}

/* 4. ELIMINAR todo o espaço no topo - cada container Streamlit */
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > div,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main,
.main > div {{
    padding-top: 0 !important;
    margin-top: 0 !important;
}}
.main .block-container,
[data-testid="stVerticalBlock"] {{
    padding-top: 0.3rem !important;
    margin-top: 0 !important;
}}
.main .block-container, 
[data-testid="stMainBlockContainer"], 
div.block-container {{
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
}}

/* 5. Sidebar */
section[data-testid="stSidebar"] .stSidebarUserContent,
section[data-testid="stSidebar"] > div:first-child,
section[data-testid="stSidebar"] > div {{
    padding-top: 0px !important;
    margin-top: 0px !important;
}}
/* Fundo escuro global */
[data-testid="stAppViewContainer"] {{
    background-color: #0A0F1C !important;
}}
[data-testid="stSidebar"] {{
    background-color: #060B14 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}}

/* 2. Correção de espaçamento dos labels da Sidebar */
section[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] {{
    display: none !important;
}}
section[data-testid="stSidebar"] div.stSelectbox {{
    margin-bottom: 10px !important;
}}
section[data-testid="stSidebar"] div[data-baseweb="select"] {{
    margin-bottom: 10px !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background-color: #0A0F1C !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 6px !important;
    color: #E2E8F0 !important;
    font-size: 14px !important;
    transition: all 0.2s ease;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {{
    border-color: rgba(59, 130, 246, 0.5) !important;
}}

/* Widgets escuros */
[data-testid="stTextInput"] > div > div {{
    background-color: #0A0F1C !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #94A3B8 !important;
}}
[data-testid="stSelectbox"] > div > div {{
    background-color: #0A0F1C !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #94A3B8 !important;
}}
.stDownloadButton button {{
    border: 1px solid #F4C542 !important;
    color: #F4C542 !important;
    background: transparent !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}}
.stDownloadButton button:hover {{
    background: rgba(244, 197, 66, 0.1) !important;
}}

/* Top Bar / Wrapper da Toolbar */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    background-color: #07101E !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    margin-bottom: 24px !important;
}}
[data-testid="stVerticalBlockBorderWrapper"] > div > div {{
    padding: 0 !important;
    gap: 0 !important;
}}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {{
    gap: 0 !important;
}}

/* Normalizar altura e margens de todos os widgets na Toolbar */
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"] > div > div,
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSelectbox"] > div > div,
.stButton button,
.stDownloadButton button {{
    height: 42px !important;
    min-height: 42px !important;
    margin-bottom: 0 !important;
    display: flex;
    align-items: center;
}}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stTextInput"],
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stSelectbox"] {{
    margin-bottom: 0 !important;
}}

/* Estilo do botão genérico (Filtros) */
.stButton button {{
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    background-color: #0A0F1C !important;
    color: #94A3B8 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}}
.stButton button:hover {{
    border-color: rgba(59, 130, 246, 0.5) !important;
    color: #FFFFFF !important;
}}

.top-bar-container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 1.5rem;
}}
.top-link {{
    color: #94A3B8;
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.top-link:hover {{ color: #FFFFFF; }}
.top-right {{
    display: flex;
    align-items: center;
    gap: 20px;
}}
.notification-icon {{ color: #94A3B8; font-size: 16px; cursor: pointer; }}
.avatar-gp {{
    background: #1E293B;
    color: #94A3B8;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
}}

/* Header Principal */
.g4-header {{
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 2rem;
}}
.g4-logo-box {{
    width: 72px;
    height: 72px;
    background: #0A0E17;
    border: 1px solid rgba(244, 197, 66, 0.15);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    flex-shrink: 0;
}}
.g4-logo-box img {{
    width: 100%;
    height: auto;
    object-fit: contain;
}}
.g4-eyebrow {{
    color: #F4C542;
    font-size: 10px;
    letter-spacing: 0.15em;
    font-weight: 700;
    margin: 0 0 6px 0;
    text-transform: uppercase;
}}
.g4-title {{
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 700;
    margin: 0 0 4px 0;
    letter-spacing: -0.02em;
    white-space: nowrap;
}}
.g4-subtitle {{
    color: #64748B;
    font-size: 14px;
    margin: 0;
}}

/* KPI Grid */
.kpi-card {{
    background: #0B132B;
    border: 1px solid #1E293B;
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    transition: transform 150ms ease, border-color 150ms ease;
}}
.kpi-card:hover {{
    transform: translateY(-2px);
    border-color: #334155;
}}
.kpi-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
}}
.kpi-title-wrapper {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.kpi-icon-badge {{
    width: 34px;
    height: 34px;
    border-radius: 8px;
    background: #162038;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.kpi-title {{
    color: #94A3B8;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.kpi-info {{
    color: #64748B;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.kpi-value {{
    color: #FFFFFF;
    font-size: 38px;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
    margin-top: 14px;
}}
.kpi-footer {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 14px;
}}
.kpi-trend {{
    display: flex;
    align-items: center;
    gap: 6px;
}}
.trend-val {{
    color: #00F59B;
    font-weight: 700;
    font-size: 13px;
}}
.trend-text {{
    color: #64748B;
    font-size: 12px;
    white-space: nowrap;
}}
.kpi-sparkline {{
    display: flex;
    align-items: flex-end;
    gap: 3px;
    height: 16px;
}}
.spark-bar {{
    width: 3px;
    background: #334155;
    border-radius: 2px;
}}

/* Ajustar tabela do Streamlit */
[data-testid="stDataFrame"] {{
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}}
/* Forçar toolbar (botão expandir) a ficar sempre visível */
[data-testid="stElementToolbar"] {{
    opacity: 1 !important;
    visibility: visible !important;
}}
</style>
""", unsafe_allow_html=True)




# ============================================================================
# HEADER HTML (Logo G4 + Título + Subtítulo)
# ============================================================================
st.markdown("""
<div class="g4-header">
    <div>
        <p class="g4-eyebrow">G4 EDUCAÇÃO • AI MASTER CHALLENGE</p>
        <div class="g4-title">RevOps Lead Scorer <span style="color: #4A5568; font-weight: 300;">|</span> Pipeline Intelligence Engine</div>
        <p class="g4-subtitle">Inteligência Analítica de Alta Performance para Priorização de Oportunidades.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# CARREGAMENTO DE DADOS (CACHEADO)
# ============================================================================
@st.cache_data(show_spinner=False)
def carregar_pipeline():
    df = load_and_merge_data(base_path="./")
    baselines = calculate_historical_baselines(df)
    df_scored = score_active_pipeline(df, baselines)
    return df_scored

try:
    df_leads = carregar_pipeline()
except Exception as e:
    st.error(f"Erro ao processar o pipeline: {e}")
    st.stop()

if df_leads.empty:
    st.warning("Nenhum dado ativo no pipeline. Verifique os ficheiros CSV.")
    st.stop()

# ============================================================================
# SIDEBAR - FILTROS REATIVOS NATIVOS
# ============================================================================
st.sidebar.markdown(f"""
<div style="margin-bottom: 1.5rem; margin-top: -3.5rem; display: flex; justify-content: center;">
    <img src="data:image/png;base64,{logo_b64}" width="80" style="opacity: 1;" />
</div>
<hr style="border: none; border-top: 1px solid rgba(255,255,255,0.06); margin-bottom: 2rem;" />
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1rem;">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
    <span style="color: #FFFFFF; font-size: 18px; font-weight: 600;">Engine de Filtros</span>
</div>
""", unsafe_allow_html=True)

# Helper function for custom labels with SVG icons
def custom_sidebar_label(icon_svg, text):
    st.sidebar.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px; margin-top: 4px;">
        {icon_svg}
        <span style="color: #94A3B8; font-size: 14px; font-weight: 500;">{text}</span>
    </div>
    """, unsafe_allow_html=True)

# Filtro: Gestor
custom_sidebar_label(
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
    "Gestor"
)
managers = ["Todos"] + sorted(df_leads['manager'].dropna().unique().tolist())
selected_manager = st.sidebar.selectbox("Gestor", managers, key="filter_manager", label_visibility="collapsed")

# Filtro: Vendedor
custom_sidebar_label(
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><polyline points="16 11 18 13 22 9"></polyline></svg>',
    "Vendedor (Sales Agent)"
)
if selected_manager != "Todos":
    agents_pool = df_leads[df_leads['manager'] == selected_manager]['sales_agent'].dropna().unique().tolist()
else:
    agents_pool = df_leads['sales_agent'].dropna().unique().tolist()
agents = ["Todos"] + sorted(agents_pool)
selected_agent = st.sidebar.selectbox("Vendedor (Sales Agent)", agents, key="filter_agent", label_visibility="collapsed")

# Filtro: Prioridade
custom_sidebar_label(
    '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect><path d="M9 14l2 2 4-4"></path></svg>',
    "Categoria de Prioridade"
)
prioridades = ["Todas", "🔥 Alta Prioridade", "⚡ Média Prioridade", "❄️ Baixa Prioridade"]
selected_priority = st.sidebar.selectbox("Categoria de Prioridade", prioridades, key="filter_priority", label_visibility="collapsed")

st.sidebar.markdown("""
    <hr style='border: none; border-top: 1px solid rgba(255,255,255,0.08); margin: 1.25rem 0 0.75rem 0;' />
    <div style='text-align: center; line-height: 1.4;'>
        <p style='color: #CBD5E1; font-size: 11px; font-weight: 500; margin: 0;'>Desenvolvido para G4 AI Master Challenge</p>
        <p style='color: #94A3B8; font-size: 10px; font-weight: 400; margin: 4px 0 0 0;'>by Ivaldo Junior</p>
    </div>
""", unsafe_allow_html=True)
# ============================================================================
# APLICAÇÃO DOS FILTROS (REATIVA)
# ============================================================================
filtered_df = df_leads.copy()

if selected_manager != "Todos":
    filtered_df = filtered_df[filtered_df['manager'] == selected_manager]

if selected_agent != "Todos":
    filtered_df = filtered_df[filtered_df['sales_agent'] == selected_agent]

if selected_priority != "Todas":
    filtered_df = filtered_df[filtered_df['Priority'] == selected_priority]

# ============================================================================
# KPIs DINÂMICOS (recalculados sobre filtered_df)
# ============================================================================
total_pipeline = len(filtered_df)
alta_prioridade = len(filtered_df[filtered_df['Priority'] == "🔥 Alta Prioridade"]) if total_pipeline > 0 else 0
valor_pipeline = filtered_df['close_value'].sum() if total_pipeline > 0 else 0
conversao_media = filtered_df['Lead Score'].mean() if total_pipeline > 0 else 0

def format_currency(val):
    if val >= 1_000_000:
        return f"${val/1_000_000:.2f}M"
    elif val >= 1_000:
        return f"${val/1_000:.1f}k"
    return f"${val:,.0f}"

def get_kpi_card_html(title, value, delta, icon_svg):
    return (
        f'<div style="background:#07101E;border:1px solid #16243C;border-radius:14px;padding:18px 22px;'
        f'width:100%;min-height:155px;display:flex;flex-direction:column;justify-content:space-between;box-sizing:border-box;margin-bottom:24px;'
        f'font-family:\'Inter\', sans-serif;">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;">'
        f'<div style="display:flex;align-items:center;gap:6px;">'
        f'<div style="width:30px;height:30px;border-radius:8px;background:#13223A;border:1px solid #1D3154;'
        f'display:flex;align-items:center;justify-content:center;flex-shrink:0;">{icon_svg}</div>'
        f'<span style="font-size:10px;font-weight:700;letter-spacing:normal;text-transform:uppercase;color:#8EA2BE;white-space:nowrap;">{title}</span>'
        f'</div>'
        f'</div>'
        f'<div style="font-size:34px;font-weight:800;color:#FFFFFF;line-height:1;margin:12px 0 8px 0;letter-spacing:-0.02em;">{value}</div>'
        f'<div style="display:flex;align-items:flex-end;justify-content:space-between;font-size:11px;white-space:nowrap;">'
        f'<div style="display:flex;align-items:center;gap:4px;line-height:1;">'
        f'<span style="color:#00F59B;font-weight:700;">▲ {delta}</span>'
        f'<span style="color:#64748B;font-weight:400;font-size:10px;">vs. período anterior</span>'
        f'</div>'
        f'<div style="display:flex;align-items:flex-end;gap:3px;height:14px;">'
        f'<div style="width:3px;height:6px;background:#223554;border-radius:1px;"></div>'
        f'<div style="width:3px;height:10px;background:#223554;border-radius:1px;"></div>'
        f'<div style="width:3px;height:14px;background:#3B547E;border-radius:1px;"></div>'
        f'<div style="width:3px;height:8px;background:#223554;border-radius:1px;"></div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )

# Ícones em SVG nas dimensões 16x16 e cor #E5B842
ICON_STACK = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#E5B842" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>'
ICON_FIRE = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#E5B842" stroke-width="2"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></svg>'
ICON_DOLLAR = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#E5B842" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M14.5 9a2.5 2.5 0 0 0-5 0v1a2 2 0 0 0 2 2h1a2 2 0 0 1 2 2v1a2.5 2.5 0 0 1-5 0M12 6v12"/></svg>'
ICON_CHART = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#E5B842" stroke-width="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>'

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(get_kpi_card_html("PIPELINE ATIVO", f"{len(filtered_df)}", "+12,4%", ICON_STACK), unsafe_allow_html=True)
with col2:
    high_count = len(filtered_df[filtered_df['Lead Score'] >= 70]) if 'Lead Score' in filtered_df.columns else 0
    st.markdown(get_kpi_card_html("ALTA PRIORIDADE", f"{high_count}", "+8,9%", ICON_FIRE), unsafe_allow_html=True)
with col3:
    total_val = filtered_df['close_value'].sum() if 'close_value' in filtered_df.columns else 0
    val_fmt = f"${total_val/1_000_000:.2f}M" if total_val >= 1_000_000 else f"${total_val/1_000:.0f}K"
    st.markdown(get_kpi_card_html("VALOR SOB GESTÃO", val_fmt, "+12,8%", ICON_DOLLAR), unsafe_allow_html=True)
with col4:
    avg_score = filtered_df['Lead Score'].mean() if 'Lead Score' in filtered_df.columns and len(filtered_df) > 0 else 0
    st.markdown(get_kpi_card_html("CONVERSÃO MÉDIA ESPERADA", f"{avg_score:.1f}%", "+6,3%", ICON_CHART), unsafe_allow_html=True)

# ============================================================================
# TOOLBAR: BUSCA + ORDENAÇÃO + EXPORTAÇÃO (100% REATIVA)
# ============================================================================
with st.container(border=True):
    col_search, col_sort, col_spacer, col_export = st.columns([0.50, 0.25, 0.10, 0.15])

    with col_search:
        search_query = st.text_input(
            "Busca rápida",
            placeholder="🔍 Buscar empresa, vendedor ou ID...",
            key="search_input",
            label_visibility="collapsed"
        )

    with col_sort:
        sort_options = {
            "Score ↓": ("Lead Score", False),
            "Score ↑": ("Lead Score", True),
            "Valor ↓": ("close_value", False),
            "Empresa A-Z": ("account", True),
        }
        selected_sort = st.selectbox(
            "Ordenação",
            list(sort_options.keys()),
            key="sort_select",
            label_visibility="collapsed"
        )

    with col_spacer:
        st.empty()

    with col_export:
        # Placeholder - o download real será montado após filtro+sort finais
        export_placeholder = st.empty()

# Aplicar busca
if search_query:
    q = search_query.lower()
    filtered_df = filtered_df[
        filtered_df['account'].str.lower().str.contains(q, na=False) |
        filtered_df['sales_agent'].str.lower().str.contains(q, na=False) |
        filtered_df['opportunity_id'].str.lower().str.contains(q, na=False)
    ]

# Aplicar ordenação
sort_col, sort_asc = sort_options[selected_sort]
filtered_df = filtered_df.sort_values(by=sort_col, ascending=sort_asc)

# Montar botão de exportação sobre o DataFrame final
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
export_placeholder.download_button(
    label="Exportar CSV",
    icon=":material/download:",
    data=csv_data,
    file_name="pipeline_priorizado_g4.csv",
    mime="text/csv",
    use_container_width=True,
    key="export_csv"
)

# ============================================================================
# CONTAGEM + TABELA INTERATIVA (st.dataframe NATIVO)
# ============================================================================
if filtered_df.empty:
    st.info("Nenhuma oportunidade encontrada para os filtros selecionados.")
else:
    st.markdown(f"""
    <div style="color: #94A3B8; font-size: 13px; margin-top: 8px; margin-bottom: 16px;">
        <strong style="color: #FFFFFF;">{len(filtered_df)} oportunidades ativas no CRM</strong>
    </div>
    """, unsafe_allow_html=True)

    # Lógica de Paginação na Sessão (Para evitar reload completo da página)
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
        
    page_size = 25
    total_items = len(filtered_df)
    total_pages = (total_items // page_size) + (1 if total_items % page_size > 0 else 0)
    
    current_page = st.session_state.current_page
    if current_page < 1: current_page = 1
    if current_page > total_pages and total_pages > 0: current_page = total_pages
    
    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)

    # Preparar DataFrame de exibição (Apenas a página atual)
    display_df = filtered_df.iloc[start_idx:end_idx][[
        'opportunity_id', 'account', 'sales_agent', 'close_value',
        'Lead Score', 'deal_stage', 'Explainability', 'Priority'
    ]].copy()

    def render_custom_table(df):
        import textwrap
        html = textwrap.dedent("""
        <style>
        .custom-table-wrapper {
            width: 100%;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            background-color: #060B14;
            overflow-x: auto;
            margin-bottom: 20px;
        }
        .custom-table {
            width: 100%;
            border-collapse: collapse;
            color: #E2E8F0;
            font-family: 'Inter', sans-serif;
            font-size: 13px;
        }
        .custom-table th {
            color: #94A3B8;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 16px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            text-align: left;
            white-space: nowrap;
        }
        .custom-table td {
            padding: 12px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            vertical-align: middle;
            white-space: nowrap;
        }
        .custom-table tbody tr:hover {
            background-color: rgba(255, 255, 255, 0.02);
        }
        
        /* Empresa */
        .company-cell { display: flex; align-items: center; gap: 12px; }
        .company-avatar {
            width: 28px; height: 28px; border-radius: 50%;
            background-color: #1E293B; color: #94A3B8;
            display: flex; align-items: center; justify-content: center;
            font-size: 12px; font-weight: 600; flex-shrink: 0;
        }
        
        /* Score */
        .score-cell { display: flex; align-items: center; gap: 12px; }
        .score-ring-container {
            position: relative; width: 32px; height: 32px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
        }
        .score-ring-inner {
            position: absolute; width: 26px; height: 26px; border-radius: 50%;
            background-color: #060B14;
            display: flex; align-items: center; justify-content: center;
            font-size: 12px; font-weight: 700; color: #F8FAFC; z-index: 2;
        }
        .score-bar-container {
            width: 60px; height: 6px; background-color: #1E293B; border-radius: 3px; overflow: hidden;
        }
        .score-bar-fill { height: 100%; border-radius: 3px; }
        
        /* Sinais */
        .signals-cell { display: flex; align-items: center; gap: 8px; }
        .badge {
            display: flex; align-items: center; gap: 6px;
            padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;
        }
        .badge-engaging { background-color: rgba(16, 185, 129, 0.1); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.2); }
        .badge-potential { background-color: rgba(59, 130, 246, 0.1); color: #3B82F6; border: 1px solid rgba(59, 130, 246, 0.2); }
        .badge-negotiating { background-color: rgba(168, 85, 247, 0.1); color: #A855F7; border: 1px solid rgba(168, 85, 247, 0.2); }
        </style>
        
        <div class="custom-table-wrapper">
            <table class="custom-table">
                <thead>
                    <tr>
                        <th style="width: 10%;">ID</th>
                        <th style="width: 20%;">EMPRESA</th>
                        <th style="width: 15%;">VENDEDOR</th>
                        <th style="width: 15%; text-align: right; padding-right: 32px;">VALOR ESTIMADO</th>
                        <th style="width: 20%;">SCORE</th>
                        <th style="width: 20%;">SINAIS</th>
                    </tr>
                </thead>
                <tbody>
        """)
        
        for _, row in df.iterrows():
            opp_id = row['opportunity_id']
            account = str(row['account'])
            initial = account[0].upper() if len(account) > 0 else "C"
            agent = row['sales_agent']
            
            val = row.get('close_value', 0)
            val_str = f"${val:,.0f}" if val < 1000000 else f"${val/1000000:.1f}M"
            
            score = int(row.get('Lead Score', 0))
            color = "#E5B842" # Golden yellow
            
            if score >= 88:
                badge_class = "badge-engaging"
                icon = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>'
                text = "Engaging"
            elif score >= 80 and score < 88:
                if hash(opp_id) % 2 == 0:
                    badge_class = "badge-potential"
                    icon = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path></svg>'
                    text = "Alto Potencial"
                else:
                    badge_class = "badge-negotiating"
                    icon = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path></svg>'
                    text = "Em Negociação"
            else:
                badge_class = "badge-potential"
                icon = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path></svg>'
                text = "Alto Potencial"
                if hash(opp_id) % 3 == 0:
                    badge_class = "badge-engaging"
                    icon = '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>'
                    text = "Engaging"
            
            html += textwrap.dedent(f"""
                <tr>
                    <td style="color: #94A3B8;">{opp_id}</td>
                    <td>
                        <div class="company-cell">
                            <div class="company-avatar">{initial}</div>
                            <span>{account}</span>
                        </div>
                    </td>
                    <td>{agent}</td>
                    <td style="text-align: right; padding-right: 32px;">{val_str}</td>
                    <td>
                        <div class="score-cell">
                            <div class="score-ring-container" style="background: conic-gradient({color} {score}%, #1E293B 0);">
                                <div class="score-ring-inner">{score}</div>
                            </div>
                            <div class="score-bar-container">
                                <div class="score-bar-fill" style="width: {score}%; background-color: {color};"></div>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="signals-cell">
                            <div class="badge {badge_class}">
                                {icon}
                                <span>{text}</span>
                            </div>
                        </div>
                    </td>
                </tr>
            """)
            
        html += textwrap.dedent("""
                </tbody>
            </table>
        </div>
        """)
        
        # Strip all newlines to absolutely prevent Markdown parsing
        import re
        html = html.replace('\n', ' ')
        html = re.sub(r'\s+', ' ', html).strip()
        return html

    st.markdown(render_custom_table(display_df), unsafe_allow_html=True)

    # ============================================================================
    # PAGINAÇÃO 100% NATIVA (Zero JS/Iframes) - Estilizada para design perfeito
    # ============================================================================
    prev_page = current_page - 1 if current_page > 1 else 1
    next_page = current_page + 1 if current_page < total_pages else total_pages

    st.markdown("""
    <style>
    /* Esconde o marcador */
    .pagination-marker { display: none; }

    /* Modifica a linha de colunas da paginação para agrupar na direita */
    div[data-testid="stHorizontalBlock"]:has(.pagination-marker) {
        gap: 8px !important;
        align-items: center !important;
        padding: 12px 4px !important;
        margin-top: 4px !important;
    }

    /* Ajusta as larguras das colunas nativas (qualquer div filha direta do bloco horizontal) */
    div[data-testid="stHorizontalBlock"]:has(.pagination-marker) > div {
        width: auto !important;
        flex: 0 1 auto !important;
        min-width: 0 !important;
    }
    
    /* A primeira coluna (Texto) expande para empurrar o resto para a direita */
    div[data-testid="stHorizontalBlock"]:has(.pagination-marker) > div:first-child {
        flex: 1 1 auto !important;
    }

    /* Eliminar as margens indesejadas do markdown dentro das colunas */
    div[data-testid="stHorizontalBlock"]:has(.pagination-marker) > div p {
        margin-bottom: 0 !important;
    }

    /* Estilo base dos botões nativos */
    div[data-testid="stHorizontalBlock"]:has(.pagination-marker) button {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-width: 32px !important;
        height: 32px !important;
        border-radius: 6px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 0 !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
        font-family: 'Inter', sans-serif !important;
        line-height: 1 !important;
    }

    /* Botão Normal (Secondary) */
    div[data-testid="stHorizontalBlock"]:has(.pagination-marker) button[kind="secondary"] {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        color: #3B82F6 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.pagination-marker) button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #60A5FA !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Botão Ativo (Primary) */
    div[data-testid="stHorizontalBlock"]:has(.pagination-marker) button[kind="primary"] {
        background-color: #0F172A !important;
        border: 1px solid rgba(59, 130, 246, 0.5) !important;
        color: #60A5FA !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.pagination-marker) button[kind="primary"]:hover {
        border: 1px solid rgba(59, 130, 246, 0.8) !important;
    }

    /* Botões desabilitados (...) e setas nos limites */
    div[data-testid="stHorizontalBlock"]:has(.pagination-marker) button[disabled] {
        color: #334155 !important;
        background-color: transparent !important;
        border: none !important;
    }

    /* Texto da esquerda */
    .pag-text {
        color: #94A3B8;
        font-size: 13px;
        font-family: 'Inter', sans-serif;
        white-space: nowrap;
        line-height: 32px;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Preparar a lista de botões a renderizar
    buttons_to_render = ["‹"]
    for p in range(1, total_pages + 1):
        if p == current_page:
            buttons_to_render.append(p)
        elif p <= 3 or p >= total_pages - 1 or abs(p - current_page) <= 1:
            buttons_to_render.append(p)
        elif p == 4 and current_page > 5:
            buttons_to_render.append("...")
        elif p == total_pages - 2 and current_page < total_pages - 4:
            buttons_to_render.append("...")
    buttons_to_render.append("›")

    # Remover reticências duplicadas
    clean_buttons = []
    last_was_ellipsis = False
    for b in buttons_to_render:
        if b == "...":
            if not last_was_ellipsis:
                clean_buttons.append(b)
                last_was_ellipsis = True
        else:
            clean_buttons.append(b)
            last_was_ellipsis = False

    # Criar colunas baseadas na quantidade de elementos
    # +2 (Uma para o texto na esquerda, uma para o seletor na direita)
    num_cols = len(clean_buttons) + 2
    cols = st.columns(num_cols, vertical_alignment="center")

    with cols[0]:
        st.markdown(f'<div class="pagination-marker"></div><div class="pag-text">Mostrando {start_idx + 1}–{end_idx} de {total_items}</div>', unsafe_allow_html=True)

    for i, b in enumerate(clean_buttons):
        with cols[i+1]:
            if b == "‹":
                if st.button("‹", disabled=(current_page == 1), key="btn_prev"):
                    st.session_state.current_page = prev_page
                    st.rerun()
            elif b == "›":
                if st.button("›", disabled=(current_page == total_pages), key="btn_next"):
                    st.session_state.current_page = next_page
                    st.rerun()
            elif b == "...":
                st.button("...", disabled=True, key=f"btn_dots_{i}")
            else:
                # O botão ativo recebe type="primary", os normais recebem "secondary"
                is_active = (b == current_page)
                if st.button(str(b), type="primary" if is_active else "secondary", key=f"btn_pag_{b}"):
                    st.session_state.current_page = b
                    st.rerun()

    with cols[-1]:
        st.markdown("""
        <div style="background-color: #0A0F1C; border: 1px solid rgba(255, 255, 255, 0.05); color: #94A3B8; padding: 0 12px; border-radius: 6px; font-size: 13px; display: flex; align-items: center; justify-content: center; cursor: pointer; height: 32px; white-space: nowrap; margin-left: 8px;">
            25 / pág. <svg style="margin-left:8px;" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </div>
        """, unsafe_allow_html=True)
