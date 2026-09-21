# Design system do G4 (o que é público) e como aplicar no Lead Scorer

O G4 não publica manual de marca nem arquivo de tokens. Tudo abaixo foi lido de código: o kit global do Elementor do site (post-7.css e CSS das páginas), o docs.json e o landing.html da documentação do G4 OS, o HTML de g4oscloud.com e o src/index.css do repositório interno nexus-whisper-schema. Cada token tem a fonte. O que é recomendação nossa, e não prática observada do G4, está marcado como "recomendação". Extração feita em 21/09/2026.

## Cores

| Papel | Hex | Nome interno | Onde o G4 usa | Fonte |
|---|---|---|---|---|
| Navy (primária) | #001F35 | --navy-blue, --e-global-color-primary | Seções escuras, texto sobre o CTA dourado, "ink" do G4 OS | [1][5] |
| Navy de texto | #031A26 | --maua-blue, --e-global-color-text | Texto corrido, h1 a h3 nos PDFs internos; no nexus é o "Navy" (HSL 200 86% 8%), foreground e sidebar | [1][7][8] |
| Dourado (secundária/acento) | #B9915B | --royal-gold, --e-global-color-secondary, --line-color | Cor mais frequente do CSS (24 ocorrências). Linhas, eyebrows, ícones, primary do G4 OS docs, --gold do site g4oscloud | [1][2][4][5][6] |
| Dourado escuro | #977342 | (sem token) | Borda e início do gradiente do CTA | [3] |
| Dourado claro | #C9A96E | (sem token) | Fim do gradiente do CTA | [3] |
| Dourado claro (dark mode) | #D1BEA4 | colors.dark | Modo escuro da documentação do G4 OS | [4] |
| Cream (fundo) | #F5F4F3 | --royal-silver, --e-global-color-accent, --fade-color | Fundo de página predominante; background do nexus (HSL 30 8% 96%); usado na maior parte via var() | [1][3][7] |
| Branco | #FFFFFF | | Seções e cards; --bg do g4oscloud | [3][6] |
| Cinza quente | #EDECEA | | Fundo alternativo no landing do G4 OS | [5] |
| Fundo docs | #fafbfc | --g4-bg | Fundo do site em algumas páginas | [2] |
| Borda | rgba(0,31,53,0.09) e #001F3526 | --border-color | Bordas finas no landing do G4 OS e no site (navy a 9% e 15%) | [2][5] |
| Azul médio | #184560 | --e-global-color-1b6017f | Apoio, raro (1 ocorrência) | [1] |
| Terracota | #af4332 | --primary-color | Botão/hover em algumas páginas do site | [2] |
| Tijolo | #842E20 | --primary-hover | Destaque e alerta; G4 Skills (3 ocorrências) | [1][2][3] |
| Vinho | #441B1B, #4A1018 | | Raros (1 ocorrência cada) | [1][3] |
| Cinzas utilitários | #64748B, #E5E7EB, #F8FAFC, #D1D5DB, #9CA3AF | | Meta/rodapé, bordas de tabela e cabeçalho de tabela nos PDFs internos (paleta cinza do Tailwind) | [3][8] |
| Amarelo legado | #FFCB00 | | Resquício da marca antiga. Não usar | [2] |
| Transição de página | #FFBC7D | | Só no efeito de transição do Elementor. Não usar | [1] |

Contraste sobre os fundos de trabalho (razões WCAG calculadas por nós, aproximadas):

| Combinação | Razão | Uso permitido |
|---|---|---|
| #031A26 sobre #F5F4F3 | 16:1 | Texto corrido |
| #001F35 sobre #F5F4F3 | 15:1 | Texto e títulos |
| #001F35 sobre #FFFFFF | 17:1 | Texto e títulos |
| #F5F4F3 sobre #001F35 | 15:1 | Texto sobre navy |
| #B9915B sobre #001F35 | 5,8:1 | Texto e rótulos sobre navy |
| #842E20 sobre #F5F4F3 | 8:1 | Texto de alerta |
| #184560 sobre #F5F4F3 | 9:1 | Texto secundário |
| #977342 sobre #F5F4F3 | 3,9:1 | Só texto grande (18 px+ ou 14 px bold) |
| #B9915B sobre #F5F4F3 | 2,6:1 | Reprova para texto. Só linhas, ícones, fundos de badge e eyebrow decorativo |
| #B9915B sobre #FFFFFF | 2,9:1 | Idem |

## Tipografia

| Papel | Fonte | Pesos usados | Onde | Fonte da info |
|---|---|---|---|---|
| Títulos e display | PP Museum (Pangram Pangram, humanist sans, comercial; self-hosted como PPMuseum-Light/Regular/Ultrabold + itálicos) | 200, 400, 600 e itálicos; muitas vezes itálico | Estilos globais de título do site; line-height 1.2em | [1][9] |
| Corpo, UI, botões | Manrope (Google Fonts, 100 a 900 + itálicos) | 200, 400, 600, 800; botões 800 / 16 px | Tipografia global primária, secundária, de texto e accent do kit; line-height 1.4em | [1] |
| Serif de apoio | Libre Baskerville (Google Fonts) | 400 a 700, alguns itálicos | 7 estilos globais e cerca de 23 regras nas páginas | [1] |
| Serif do G4 OS | Source Serif 4 (landing da documentação, 300/400, itálico para ênfase) e Playfair Display (site g4oscloud) | Leves | Títulos com um trecho em itálico ("O <em>Sistema Operacional com IA</em>") | [5][6] |
| Sans do G4 OS | Manrope e Inter | | UI | [5][6] |
| Mono | JetBrains Mono | 9 a 12 px, letter-spacing | Rótulos pequenos no landing e no site do G4 OS | [5][6] |
| Apps internos | DM Sans e Plus Jakarta Sans | | nexus-whisper-schema (app Lovable). Não é peça de marca | [7] |

Escala tipográfica do kit (tokens): 14, 16, 20, 31, 39, 49 e 61 px. Tamanhos mais usados nas páginas: 16 px (56x), 14 px (47x), depois 36, 32, 18, 12, 56 e 48 px. Line-height 1.2em em títulos (25x) e 1.4em em texto (7x). [1][3]

Substituição da PP Museum (recomendação, porque a fonte é comercial e sem licença pública): Manrope 800 para os títulos de interface, que é a família que o próprio site usa em botões e UI, e uma única linha em serif (Source Serif 4 400, ou Libre Baskerville 400 que o site já carrega) com um trecho em itálico para o nome do produto ou a frase de abertura, como o G4 OS faz. Não usar serif em tudo; o site não faz isso.

## Raio, espaçamento e layout

Raios de borda: tokens --Raio-borda-8px, 12px, 16px, 20px, 24px. Na prática das páginas: 10 px (17x), 15 px (12x), 16 px (10x), 8 px (3x); pílulas de 999px/50% só 4 vezes. O G4 OS usa 10 px; o nexus usa 0.75rem (12 px). [1][3][5][7] Recomendação: 8 px em botões, 12 px em cards, nada de pílula.

Espaçamento: não existe escala formal. O kit define 20 px entre widgets; botões têm padding 16 x 48 px no desktop e 16 x 24 px no mobile. [1][3] Recomendação: base de 8 px (8, 16, 24, 32, 48).

Layout: container máximo 1140 px (1024 px em telas até 1024 px; 767 px no mobile). [1] Fundo de página predominante cream #F5F4F3 com seções em navy #001F35 e branco. [3]

## Componentes observados

Botão primário do site: fundo gradiente linear 90deg #977342 → #C9A96E, borda 1 px #977342, texto navy (--e-global-color-primary) em Manrope 800 16 px, raio 8 px, padding 16 x 48 px. Hover e focus com fundo transparente no estilo global. [1][3]

Eyebrow de marca (PDF interno): #B9915B, 11 px, uppercase, letter-spacing 0.08em, peso 600. Cabeçalho de documento com linha inferior de 2 px em #B9915B. Títulos em #031A26. Meta e rodapé em #64748B. Tabelas com bordas #E5E7EB e cabeçalho #F8FAFC. [8]

Título com ênfase em itálico: "O <em>Sistema Operacional com IA</em>", serif leve, no site e no landing do G4 OS. [5][6]

Estética descrita pelo próprio G4: "traços de gravura clássica, composição precisa e um dourado editorial que remete a legado e autoridade", "Não há excesso. Há intenção."; no G4 OS, minimalismo com screenshots claros e muito espaço em branco. [5][10]

Badges e gráficos: os workflows do G4 OS usam badges verde, azul, amarelo e vermelho por quadrante ou segmento, sem hex definido. O nexus define paleta de gráficos gold, navy médio (HSL 200 86% 25%, cerca de #095277), teal, laranja e roxo, também sem hex nas fontes lidas. [7][11]

Logos: favicon "g4-icone_logotipo_azul_rgb_flat" (PNG 32/192/180 px), logo branca "logo-g4-completa-branca.svg" (101 x 40), logo escura "g4educacao-logo-escura.svg" (81 x 32). O favicon do G4 OS docs é um quadrado 524 x 524 com rx=115 (raio de cerca de 22%). [12][13] Não usar o logotipo do G4 na submissão: é marca registrada de terceiro e a entrega é sua, não deles.

## .streamlit/config.toml

As cinco chaves do bloco base funcionam em qualquer Streamlit recente. As chaves do bloco estendido (fontes, raio, borda, sidebar) exigem Streamlit 1.45 ou mais novo e não foram testadas nesta varredura; se a sua versão reclamar, apague o bloco estendido e mantenha o CSS da seção seguinte.

```toml
[theme]
base = "light"
primaryColor = "#B9915B"
backgroundColor = "#F5F4F3"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#031A26"
font = "sans serif"

# Bloco estendido (Streamlit >= 1.45; remover se der erro)
baseRadius = "10px"
borderColor = "#DAD7D2"
showWidgetBorder = true
linkColor = "#184560"
headingFont = "Manrope, sans-serif"
codeFont = "JetBrains Mono, monospace"

[[theme.fontFaces]]
family = "Manrope"
url = "https://fonts.gstatic.com/s/manrope/v15/xn7gYHE41ni1AdIRggexSg.woff2"
weight = "200 800"

[theme.sidebar]
backgroundColor = "#001F35"
secondaryBackgroundColor = "#0A2C47"
textColor = "#F5F4F3"
primaryColor = "#B9915B"
```

Observações: #DAD7D2 e #0A2C47 são derivações nossas (cream escurecido e navy clareado) para borda e fundo secundário da sidebar; não aparecem no site. A URL do woff2 do Manrope é a que o Google Fonts serve hoje e pode mudar; se quebrar, apague o bloco fontFaces e deixe o @import do CSS carregar a fonte.

## CSS para injetar no Streamlit

Chamar uma vez no topo do app com `st.markdown(CSS, unsafe_allow_html=True)`. Os seletores `data-testid` mudam entre versões do Streamlit; se algo não pegar, inspecione no navegador e ajuste.

```css
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@200;400;600;700;800&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;1,8..60,300;1,8..60,400&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --g4-navy: #001F35;
  --g4-ink: #031A26;
  --g4-gold: #B9915B;
  --g4-gold-dark: #977342;
  --g4-gold-light: #C9A96E;
  --g4-cream: #F5F4F3;
  --g4-white: #FFFFFF;
  --g4-warm-gray: #EDECEA;
  --g4-blue: #184560;
  --g4-brick: #842E20;
  --g4-muted: #64748B;
  --g4-border: rgba(0, 31, 53, 0.09);
  --g4-sans: 'Manrope', 'Segoe UI', Arial, sans-serif;
  --g4-serif: 'Source Serif 4', 'Libre Baskerville', Georgia, serif;
  --g4-mono: 'JetBrains Mono', Consolas, monospace;
  --g4-radius-sm: 8px;
  --g4-radius: 10px;
  --g4-radius-lg: 16px;
}

html, body, [data-testid="stAppViewContainer"], .stMarkdown, .stText, p, li, td, th, label {
  font-family: var(--g4-sans);
  color: var(--g4-ink);
  line-height: 1.4;
}

[data-testid="stAppViewContainer"] { background: var(--g4-cream); }
[data-testid="stHeader"] { background: transparent; }

h1, h2, h3 {
  font-family: var(--g4-sans);
  font-weight: 800;
  color: var(--g4-navy);
  line-height: 1.2;
  letter-spacing: -0.01em;
}
h1 { font-size: 39px; }
h2 { font-size: 31px; }
h3 { font-size: 20px; }

/* Uma linha de abertura em serif, como o G4 OS faz. Uso: <p class="g4-display">Pipeline de <em>segunda de manhã</em></p> */
.g4-display {
  font-family: var(--g4-serif);
  font-weight: 300;
  font-size: 49px;
  line-height: 1.2;
  color: var(--g4-navy);
  margin: 0 0 8px 0;
}
.g4-display em { font-style: italic; font-weight: 400; }

/* Eyebrow dourado (padrão dos PDFs internos) */
.g4-eyebrow {
  font-family: var(--g4-sans);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--g4-gold);
  margin-bottom: 4px;
}

/* Linha de 2px dourada abaixo do cabeçalho */
.g4-rule { border: 0; border-bottom: 2px solid var(--g4-gold); margin: 8px 0 24px 0; }

/* Rótulos pequenos em mono (padrão do landing do G4 OS) */
.g4-label {
  font-family: var(--g4-mono);
  font-size: 11px;
  letter-spacing: 0.06em;
  color: var(--g4-muted);
  text-transform: uppercase;
}

/* Sidebar navy (caso o bloco [theme.sidebar] não exista na sua versão) */
[data-testid="stSidebar"] { background: var(--g4-navy); }
[data-testid="stSidebar"] * { color: var(--g4-cream); }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--g4-gold); }

/* Botão primário: gradiente dourado do site, texto navy */
.stButton > button, [data-testid="stFormSubmitButton"] > button {
  font-family: var(--g4-sans);
  font-weight: 800;
  font-size: 16px;
  color: var(--g4-navy);
  background: linear-gradient(90deg, var(--g4-gold-dark) 0%, var(--g4-gold-light) 100%);
  border: 1px solid var(--g4-gold-dark);
  border-radius: var(--g4-radius-sm);
  padding: 12px 24px;
}
.stButton > button:hover { background: transparent; color: var(--g4-navy); border-color: var(--g4-gold-dark); }

/* Métricas (KPIs em cards, primeiro bloco da tela como nos workflows do G4 OS) */
[data-testid="stMetric"] {
  background: var(--g4-white);
  border: 1px solid var(--g4-border);
  border-radius: var(--g4-radius);
  padding: 16px 20px;
}
[data-testid="stMetricLabel"] { font-family: var(--g4-sans); font-size: 12px; color: var(--g4-muted); text-transform: uppercase; letter-spacing: 0.06em; }
[data-testid="stMetricValue"] { font-family: var(--g4-sans); font-weight: 800; font-size: 32px; color: var(--g4-navy); }

/* Tabelas */
[data-testid="stDataFrame"], [data-testid="stTable"] { border: 1px solid var(--g4-border); border-radius: var(--g4-radius); overflow: hidden; }

/* Cards genéricos */
.g4-card {
  background: var(--g4-white);
  border: 1px solid var(--g4-border);
  border-radius: var(--g4-radius);
  padding: 20px;
  margin-bottom: 16px;
}

/* Badges de faixa de score (paleta na seção seguinte) */
.g4-badge {
  display: inline-block;
  font-family: var(--g4-sans);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  padding: 3px 10px;
  border-radius: var(--g4-radius-sm);
}
.g4-badge--focar   { background: var(--g4-navy);  color: var(--g4-gold); }
.g4-badge--manter  { background: var(--g4-gold);  color: var(--g4-navy); }
.g4-badge--risco   { background: var(--g4-brick); color: var(--g4-cream); }
.g4-badge--soltar  { background: var(--g4-warm-gray); color: var(--g4-muted); }

/* Esconder o menu e o rodapé padrão do Streamlit */
#MainMenu, footer { visibility: hidden; }
```

## Regras de uso

Fundo. Cream #F5F4F3 na página, branco nos cards, navy #001F35 na sidebar ou em no máximo um bloco de destaque por tela. Nunca dois fundos escuros lado a lado. O site alterna cream, branco e navy; não usa cinza frio.

Texto. #031A26 para corpo, #001F35 para títulos, #64748B para meta e legendas. Dourado nunca vira texto corrido sobre fundo claro (contraste 2,6:1). Sobre navy, dourado funciona (5,8:1) e é o padrão dos títulos da sidebar e dos rótulos de KPI.

Dourado. Um acento, não uma cor de área. Usar em: linha de 2 px sob o cabeçalho, eyebrow uppercase, botão primário (gradiente com texto navy), ícone ativo, um número de destaque por tela. Se mais de 10% da tela estiver dourada, está errado. Na documentação do G4 OS o dourado é a única cor de marca sobre branco.

Alerta. Tijolo #842E20 para "em risco" e mensagens de erro. Não usar vermelho puro (#FF0000) nem verde saturado; o site não tem verde. Se precisar de "positivo", usar navy ou dourado, não verde.

Tipografia. Manrope em tudo. Títulos 800, corpo 400, rótulos 600 uppercase com letter-spacing. Uma única linha em serif leve por tela (nome do produto ou frase de abertura), com um trecho em itálico. Line-height 1.2 em títulos e 1.4 em texto. Tamanhos da escala do kit: 12, 14, 16, 20, 31, 39, 49.

Forma. Raio 8 px em botões e badges, 10 a 12 px em cards, 16 px só em contêineres grandes. Sem pílulas. Bordas de 1 px em navy a 9% (rgba(0,31,53,0.09)), não cinza puro. Sem sombras pesadas; o site usa bordas finas, não elevação.

Ordem na tela (padrão dos workflows do G4 OS). KPIs em cards no topo, depois o visual, depois a tabela com badge, depois recomendações nomeadas, depois 3 a 5 bullets de gap. Cada score com o "porque" ao lado, nunca só o número.

O que denuncia "cara de IA" no visual: gradiente roxo ou azul-ciano, emoji em título, cards com ícone colorido genérico, verde/amarelo/vermelho de semáforo, pílulas, sombras difusas, fonte Inter em tudo, fundo cinza frio #F3F4F6, tabela zebrada azul. Nenhum desses aparece no site do G4.

## Paleta sugerida para faixas de score (recomendação)

O G4 usa badges verde, azul, amarelo e vermelho nos workflows, mas sem hex e sem relação com a marca. Para manter a paleta do site, sugerimos quatro faixas com nomes do vocabulário deles:

| Faixa | Rótulo sugerido | Fundo | Texto | Razão |
|---|---|---|---|---|
| Score alto, valor alto | Focar agora | #001F35 | #B9915B | O par navy + dourado é o de maior destaque no site |
| Score alto, valor menor | Manter aquecido | #B9915B | #001F35 | Dourado como segundo nível |
| Esfriando, valor alto | Não pode perder | #842E20 | #F5F4F3 | Tijolo é a única cor de alerta do site; nome vem do RFV de Nardon |
| Score baixo | Soltar | #EDECEA | #64748B | Neutro, sem cor |

Para gráficos com séries: dourado #B9915B, navy #001F35, azul médio #184560, tijolo #842E20, cinza #9CA3AF, nesta ordem. Evitar mais de cinco séries.

## Fontes

1. https://g4business.com/wp-content/uploads/elementor/css/post-7.css (kit global .elementor-kit-7, bloco :root com --navy-blue, --royal-gold, --royal-silver, --maua-blue, --manrope, --PPMuseum, --Raio-borda-*, --Tamanho-font-*, @font-face PPMuseum, tipografias globais, botão global, container e widget spacing)
2. https://g4business.com/ (HTML e CSS inline: --line-color, --primary-color, --primary-hover, --fade-color, --g4-bg, --border-color, links de Google Fonts)
3. https://g4business.com/wp-content/uploads/elementor/css/post-32690.css, post-25730.css e post-291.css (CTA .elementor-element-27dc6fe, contagem de hex, raios, tamanhos e line-heights)
4. https://github.com/Gestao-Quatro-Ponto-Zero/g4os-docs/blob/main/docs.json
5. https://github.com/Gestao-Quatro-Ponto-Zero/g4os-docs/blob/main/landing.html
6. https://g4oscloud.com/ (HTML: Inter, Manrope, Playfair Display, JetBrains Mono, --gold, --bg)
7. https://github.com/Gestao-Quatro-Ponto-Zero/nexus-whisper-schema/blob/7e9da41bd2e863eb1627490d18e0cffc914aa5b1/src/index.css e tailwind.config.ts
8. https://github.com/Gestao-Quatro-Ponto-Zero/nexus-whisper-schema/blob/7e9da41bd2e863eb1627490d18e0cffc914aa5b1/src/utils/exportTurmaAnalysisPdf.ts
9. https://pangrampangram.com/products/museum e https://g4business.com/wp-content/uploads/2026/01/PPMuseum-Light.ttf (e Regular, Ultrabold, itálicos)
10. https://g4educacao.com/sobre (seção "Nossa identidade")
11. https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills/blob/main/workflows/ecossistema-vendas/WORKFLOW.md
12. https://g4business.com/wp-content/uploads/2026/07/cropped-g4-icone_logotipo_azul_rgb_flat-1-192x192.png ; .../2026/01/logo-g4-completa-branca.svg ; .../2026/01/g4educacao-logo-escura.svg
13. https://github.com/Gestao-Quatro-Ponto-Zero/g4os-docs/blob/main/favicon.svg

Não encontrado: brand book, tokens.json, Figma, escala de espaçamento, hex das badges e da paleta de gráficos, licença da PP Museum. Brandfetch e Behance retornaram 403.
