# Tokens G4 Scale

Fonte: raster 2× do PDF, 2026-09-21. Prefixo CSS: `--g4s-`.

## Cor — canônico (PDF pág. 2)

| Token | Hex | RGB | Papel |
|-------|-----|-----|-------|
| `--g4s-color-navy` | `#32445A` | 50 68 90 | Ink, header invertido, CTA, board de valores |
| `--g4s-color-steel` | `#466381` | 70 99 129 | Marca em fundo claro, faixa, logo invertível |
| `--g4s-color-slate` | `#9CA5AC` | 156 165 172 | Texto secundário, ícone, tick, borda suave |
| `--g4s-color-ice` | `#E3EAF2` | 227 234 242 | Superfície 01, número de pilar, hover row |
| `--g4s-color-mist` | `#EFF2FB` | 239 242 251 | Canvas frio, página, zebra |
| `--g4s-color-canvas` | `#FFFFFF` | 255 255 255 | Card, header, input |

Papéis semânticos (alias, mesma tinta):

| Alias | Aponta para |
|-------|-------------|
| `--g4s-fg-high` | navy |
| `--g4s-fg-medium` | steel |
| `--g4s-fg-muted` | slate |
| `--g4s-fg-on-strong` | canvas |
| `--g4s-bg-canvas` | canvas |
| `--g4s-bg-page` | mist |
| `--g4s-bg-subtle` | ice |
| `--g4s-bg-strong` | navy |
| `--g4s-bg-strong-alt` | steel |
| `--g4s-border-default` | slate @ 40% |
| `--g4s-border-strong` | steel |

## Cor — derivado (não está no swatch)

Usar só quando o componente exige estado. Não promover a “marca”.

| Token | Hex | Por quê |
|-------|-----|---------|
| `--g4s-hero-sky` | `#E9ECF1` | Céu do hero pág. 1 (foto) |
| `--g4s-cta-sampled` | `#395676` | Botão pág. 5 com anti-alias — **não usar**; preferir navy |
| `--g4s-feedback-ok` | `#3D5A4C` | Verde desaturado puxando navy |
| `--g4s-feedback-warn` | `#8A7348` | Âmbar frio (não dourado de marca) |
| `--g4s-feedback-danger` | `#7A3E44` | Vermelho desaturado |
| `--g4s-focus-ring` | `#466381` | Mesmo que steel, 2px offset canvas |

## Tipo

| Token | Valor | Grau |
|-------|-------|------|
| `--g4s-font-sans` | `"Inter", "Geist", "Helvetica Neue", Arial, sans-serif` | **derivado** — PDF não nomeia |
| `--g4s-font-display-weight` | `200` | derivado (CRESCER) |
| `--g4s-font-ui-weight` | `400` | derivado |
| `--g4s-font-ui-medium` | `500` | derivado |
| `--g4s-tracking-display` | `0.18em` | derivado |
| `--g4s-tracking-wordmark` | `0.04em` | derivado |

Escala sugerida (derivada, 8 px):

| Papel | Size / line | Peso | Tracking |
|-------|-------------|------|----------|
| Display | 72–96 / 0.95 | 200 | 0.18em |
| Title | 28–36 / 1.15 | 300–400 | 0.04em |
| Section | 20–24 / 1.25 | 400 | 0 |
| Body | 16 / 1.5 | 400 | 0 |
| Caption | 13 / 1.4 | 400 | 0.02em |
| Overline | 11 / 1.3 | 500 | 0.16em · uppercase |

## Forma

| Token | Valor | Grau | Evidência |
|-------|-------|------|-----------|
| `--g4s-radius-pill` | `999px` | derivado | CTA, chips de valor |
| `--g4s-radius-card` | `24px` | derivado | cards pág. 5 |
| `--g4s-radius-control` | `8px` | derivado | input (não aparece pill no form) |
| `--g4s-radius-none` | `0` | canônico no grafismo | ticks da régua são retos |

## Elevação

Mockups quase planos. Sombra só para card sobre navy.

| Token | Valor |
|-------|-------|
| `--g4s-shadow-card` | `0 8px 32px rgba(50, 68, 90, 0.12)` |
| `--g4s-shadow-none` | `none` |

## Espaço (derivado, grid 8)

`4 8 12 16 24 32 48 64 96`. Hero e cards usam 24–48. Nav 16–24.

## Motion

Ausente no PDF. Default: `150ms ease`. Sem bounce, sem gradient animado.

## Charts

Série única: navy. Comparativos: navy / steel / slate / ice. **Proibido** paleta Category10 / Set2 sem remapear.
