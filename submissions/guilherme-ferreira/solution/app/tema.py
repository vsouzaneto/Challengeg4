"""Visual do G4 aplicado por CSS. O config.toml não serve: no Streamlit Cloud, com o app numa
subpasta, ele teria de ficar na raiz do repositório."""
import base64
from pathlib import Path

import streamlit as st

AZUL = "#001F35"
DOURADO = "#B9915B"
DOURADO_ESCURO = "#8A6A3F"
OFF_WHITE = "#F5F4F3"
RODAPE = "Protótipo de candidato ao AI Master Challenge, sem vínculo oficial com o G4"
LOGO = Path(__file__).resolve().parent / "assets" / "logo_g4.svg"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital@1&family=Manrope:wght@200;400;600;800&display=swap');
.stApp {{ background: {OFF_WHITE}; color: {AZUL}; font-family: 'Manrope', sans-serif; }}
.stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp li, .stApp label {{ font-family: 'Manrope', sans-serif; color: {AZUL}; }}
.stApp h2, .stApp h3 {{ font-weight: 400; }}
header[data-testid="stHeader"] {{ background: {AZUL}; }}
header[data-testid="stHeader"] a, header[data-testid="stHeader"] span, header[data-testid="stHeader"] p {{ color: {OFF_WHITE}; }}
.radar-cabecalho {{ background: {AZUL}; border-radius: 10px; padding: 18px 24px; display: flex; flex-wrap: wrap;
  align-items: center; gap: 12px 20px; margin-bottom: 12px; }}
.radar-cabecalho img {{ height: 32px; }}
.radar-cabecalho h1 {{ color: {OFF_WHITE} !important; font-weight: 200; font-size: 1.9rem; margin: 0; padding: 0; }}
.radar-cabecalho em {{ font-family: 'Libre Baskerville', serif; font-style: italic; color: {DOURADO}; }}
div[data-testid="stMetric"] {{ background: #FFFFFF; border-top: 2px solid {DOURADO_ESCURO}; border-radius: 10px; padding: 12px 16px; }}
div[data-testid="stMetricValue"] {{ color: {AZUL}; font-weight: 600; font-size: 1.9rem; }}
div[data-testid="stMetricValue"] > div {{ white-space: normal !important; overflow: visible !important; text-overflow: clip !important; }}
.stApp [class*="st-key-cartao"] {{ background: #FFFFFF; border: 1px solid #E1E0D9 !important;
  border-top: 2px solid {DOURADO_ESCURO} !important; border-radius: 10px; padding: 16px; }}
.stButton > button {{ border-radius: 10px; border: 1px solid {AZUL}; color: {AZUL}; font-weight: 600; }}
.stButton > button[kind="primary"] {{ background: {DOURADO}; border-color: {DOURADO}; color: {AZUL}; font-weight: 800; }}
.stApp .radar-rodape {{ color: {DOURADO_ESCURO}; font-size: 0.8rem; text-align: center; margin: 40px 0 8px; }}
/* Controles com fundo branco e texto azul, qualquer que seja o tema (claro ou escuro) do sistema */
.stApp [data-testid="stSelectbox"] [role="group"],
.stApp [data-testid="stNumberInputContainer"], .stApp [data-testid="stNumberInputField"],
.stApp [data-testid="stNumberInputStepDown"], .stApp [data-testid="stNumberInputStepUp"] {{
  background-color: #FFFFFF !important; color: {AZUL} !important; }}
.stApp [data-testid="stSelectbox"] input, .stApp [data-testid="stSelectbox"] span, .stApp [data-testid="stSelectbox"] svg {{ color: {AZUL} !important; }}
.stApp [data-testid="stSelectbox"] [role="group"]:focus-within,
.stApp [data-testid="stNumberInputContainer"]:focus-within {{ border-color: {AZUL} !important; }}
/* Filtros do mapa: botão do popover com cara de caixa de seleção */
.stApp .radar-rotulo {{ font-size: 0.875rem; margin: 0 0 0.25rem; }}
.stApp [data-testid="stPopoverButton"] {{ background-color: #FFFFFF !important; border: 1px solid #C3C2B7 !important;
  border-radius: 10px; }}
.stApp [data-testid="stPopoverButton"]:hover, .stApp [data-testid="stPopoverButton"][aria-expanded="true"] {{
  border-color: {AZUL} !important; }}
.stApp [data-testid="stPopoverButton"] > div {{ width: 100%; display: flex; justify-content: space-between; }}
.stApp [data-testid="stPopoverButton"] > div > div:first-child {{ flex: 1; justify-content: flex-start !important; text-align: left; }}
.stApp [data-testid="stPopoverButton"] * {{ color: {AZUL} !important; }}
/* O painel do popover fica fora do .stApp */
[data-testid="stPopoverBody"] {{ background-color: #FFFFFF !important; border: 1px solid #C3C2B7 !important; }}
[data-testid="stPopoverBody"] p {{ color: {AZUL} !important; font-family: 'Manrope', sans-serif; }}
[data-testid="stPopoverBody"] [data-testid="stCheckbox"] label > span + div {{ background-color: #FFFFFF !important;
  border: 1px solid {AZUL} !important; }}
[data-testid="stPopoverBody"] [data-testid="stCheckbox"][data-selected="true"] label > span + div {{
  background-color: {AZUL} !important; }}
[role="listbox"] {{ background-color: #FFFFFF !important; }}
[role="listbox"] [role="option"], [role="listbox"] [role="option"] * {{ color: {AZUL} !important; }}
/* Azul no lugar do vermelho padrão do Streamlit */
.stApp [data-testid="stSlider"] div[style*="translate(-50%, -50%)"] {{ background-color: {AZUL} !important; }}
.stApp [data-testid="stSlider"] .efbyxod5 {{ background-image: none !important; background-color: #E1E0D9 !important; }}
.stApp [data-testid="stSliderThumbValue"], .stApp [data-testid="stSliderThumbValue"] * {{ color: {AZUL} !important; }}
.stApp [data-testid="stSliderTickBar"], .stApp [data-testid="stSliderTickBar"] * {{ color: #52514E !important; }}
.stApp [data-testid="stRadioOption"] > div > div:first-child {{ border: 1px solid {AZUL} !important; }}
.stApp [data-testid="stRadioOption"]:not([data-selected="true"]) > div > div:first-child {{ background-color: #FFFFFF !important; }}
.stApp [data-testid="stTooltipIcon"] svg {{ stroke: #52514E !important; color: #52514E !important; }}
.stApp [data-testid="stRadioOption"][data-selected="true"] > div > div:first-child {{ background-color: {AZUL} !important; }}
.stApp [data-testid="stRadioOption"] > div > div:first-child > div {{ background-color: #FFFFFF !important; }}
/* Textos auxiliares */
.stApp [data-testid="stMetricLabel"], .stApp [data-testid="stMetricLabel"] * {{ color: {AZUL} !important; }}
.stApp [data-testid="stCaptionContainer"], .stApp [data-testid="stCaptionContainer"] * {{ color: #52514E !important; }}
.stApp [data-testid="stCaptionContainer"] {{ opacity: 1 !important; }}
/* Tabelas */
.stApp [data-testid="stTable"] {{ overflow-x: auto !important; }}
.stApp [data-testid="stTable"] table {{ background: #FFFFFF; color: {AZUL}; border-collapse: collapse; width: 100%; }}
.stApp [data-testid="stTable"] th {{ background: {AZUL}; font-weight: 600; }}
.stApp [data-testid="stTable"] th, .stApp [data-testid="stTable"] th * {{ color: {OFF_WHITE} !important; }}
.stApp [data-testid="stTable"] td, .stApp [data-testid="stTable"] th {{ border: 1px solid #E1E0D9; padding: 6px 10px; }}
.stApp [data-testid="stTable"] td {{ color: {AZUL}; }}
</style>
"""
LEGENDA_CLASSES = (
    "**Sinal:** diferença acima de 10%, confiável e com pelo menos 30 posts. "
    "**Abaixo do limiar:** a diferença parece real, mas é menor que 10% e não justifica mudar nada. "
    "**Ruído:** pode ser acaso. **Poucos posts:** menos de 30 posts para comparar."
)


def aplicar():
    st.markdown(CSS, unsafe_allow_html=True)


def cabecalho(titulo, destaque):
    logo = ""
    if LOGO.exists():
        logo = f'<img src="data:image/svg+xml;base64,{base64.b64encode(LOGO.read_bytes()).decode()}" alt="G4">'
    st.markdown(f'<div class="radar-cabecalho">{logo}<h1>{titulo} <em>{destaque}</em></h1></div>', unsafe_allow_html=True)


def rodape():
    st.markdown(f'<p class="radar-rodape">{RODAPE}</p>', unsafe_allow_html=True)
