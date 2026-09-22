# SPEC-REVERSE — Identidade Visual G4 Scale (PDF)

| Campo | Valor |
|-------|-------|
| **Arquivo** | `.ai/design-system/Identidade-Visual-G4-Scale-2026-09-21-14_30_59.pdf` |
| **Bytes** | 11 741 533 |
| **Páginas** | 7 |
| **Texto extraível** | nenhum (`pypdf` e `pymupdf.get_text` = vazio) |
| **Origem visual** | Case Behance *Identidade Visual — G4 Scale* · Glauber Pinheiro · **fev/2022** |
| **URL pública do case** | https://www.behance.net/gallery/146452985/Identidade-Visual-G4-Scale |
| **Leitura** | 2026-09-21 · raster 2× (`1224×1584` px/página) |

## O que este PDF é

Peça de **identidade de marca** (logo, paleta, valores, aplicações, mockups web/social). Não é biblioteca de componentes, não é Figma Dev Mode, não é o rebrand institucional G4 de 2026.

O próprio case declara (texto da pág. 2, lido no raster): o logo dos eixos **seguiu o manual da marca G4 Educação** — não houve processo complexo de símbolo novo. O grafismo (régua) é o acréscimo de Scale.

## Mapa das páginas

| Pág. | Conteúdo de marca | Chrome alheio |
|------|-------------------|---------------|
| 1 | Hero site (foto + display *CRESCER*), nav, CTA, bloco institucional, moodboard de produto | Barra Behance / Adobe no topo |
| 2 | **Valores** (6 círculos) + **paleta com hex** + wordmark branco no aço | — |
| 3 | Lockups do logo em 4 fundos + foto + papelaria | — |
| 4 | Cartão / gancho; **grafismo** (ticks de régua); tote / camiseta; footer site | — |
| 5 | Hero recortado; card *G4 CONNECT*; 3 cards sociais | — |
| 6 | Perfil do autor, comentários, tags | **Behance** — fora do DS |
| 7 | Footer Behance / Pro | **Behance** — fora do DS |

Páginas 6–7 **não** entram em token, componente nem paleta.

## Valores de marca (pág. 2, canônico)

Seis atributos, círculos outline brancos sobre navy `#32445A`:

1. Minimalista  
2. Moderna  
3. Humana  
4. Madura  
5. Inovadora  
6. Confiável  

Texto da paleta (pág. 2): tons de cinza em **gradação** remetem a **escala e transformação**; as nuances modernizam a comunicação G4 Scale.

## Paleta amostrada (canônica)

Pontos estáveis no raster da pág. 2 (não inventados):

| Papel no PDF | Hex | Amostra |
|--------------|-----|---------|
| Navy — board de valores | `#32445A` | centro do bloco superior |
| Aço — swatch esquerdo + rodapé do logo | `#466381` | swatch às vezes `#466383` (1 bit de compressão) — **canônico `#466381`** |
| Cinza médio — swatch direito | `#9CA5AC` | |
| Gelo — swatch inferior esquerdo | `#E3EAF2` | |
| Névoa — swatch inferior centro | `#EFF2FB` | |
| Branco | `#FFFFFF` | |

CTA sólido no mockup da pág. 5 amostrado `#395676` (anti-alias sobre foto). Em código, CTA = navy `#32445A` ou aço `#466381`, texto `#FFFFFF`.

Hero céu (pág. 1) `#E9ECF1` — **derivado da foto**, não é swatch do PDF.

## Logo (págs. 2–4)

```
◆  G4SCALE
```

- Símbolo: losango / diamante de **faixas concêntricas** (eixo / escala).
- Wordmark: *G4SCALE* (às vezes *G4 SCALE* no texto corrido). Caixa alta, grotesk geométrica, tracking justo.
- Sobre fundo claro / gelo / cinza: wordmark **navy/aço**.
- Sobre foto escura ou aço `#466381`: wordmark **branco**.
- Área de respiro ≈ altura do losango em todos os lados (lido nos mockups; o PDF não dá mm).

## Grafismo (pág. 4)

Série de **ticks verticais** iguais, como régua / escala. Aplicado em desktop, tote e camiseta, baixa opacidade, sem cor extra. É o único padrão gráfico além do logo.

## UI observada nos mockups (págs. 1 e 5) — derivado

Não há spec de componente. O que se vê:

| Padrão | Evidência |
|--------|-----------|
| Header branco, wordmark à esquerda, nav texto, CTA pill à direita | pág. 1, 5 |
| Display ultra-thin, tracking aberto, branco sobre foto | *CRESCER* |
| Corpo pequeno, cinza médio, alinhado à direita no hero | “SEM LIMITES” / “INSCREVA-SE AGORA” |
| Card branco, raio grande (~24 px visual), foto + título + CTA navy pill | *G4 CONNECT* |
| Número de pilar enorme, gelo (`01`) | pág. 5 |
| Cards sociais quadrados, raio grande, wordmark canto | pág. 5 |
| Footer branco, wordmark + links | págs. 1 e 4 |
| Ícones sociais lineares, finos, à esquerda do hero | pág. 1 |

## Tipografia

**Nenhuma família é nomeada** no PDF. Visual:

- Display: grotesk geométrica, peso 200–300, tracking alto.
- UI / corpo: a mesma família em 400–500, tracking normal.
- Wordmark: a mesma família, peso médio, tracking compacto.

Fallback de implementação → [G4-SCALE-TOKENS.md](G4-SCALE-TOKENS.md) (marcado derivado).

## Ausências (não completar de memória)

- Typeface licenciada, tamanhos em px, line-height.
- Escala de espaçamento, grid, breakpoints.
- Raios, sombras, motion, dark mode.
- Estados (hover / focus / disabled / error / success).
- Ícones nomeados (só estilo linear fino).
- Acessível contrast ratio escrito.
- Token de acento quente (não existe rosa nem dourado neste PDF).

## O que este PDF não é

- Design system coded (Storybook, ng-zorro, MUI, Vuetify).
- Identidade G4 2026 (esfera armilar, dourado editorial, FutureBrand).
- Identidade glam / Bfluence.
- Manual completo G4 Educação (só é citado como restrição do logo).
