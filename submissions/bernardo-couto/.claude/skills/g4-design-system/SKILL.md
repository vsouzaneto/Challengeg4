---
name: g4-design-system
description: Tokens do design system do G4 extraídos do CSS público de g4business.com (cores, tipografia, raios) e regras de aplicação no frontend React/Tailwind do Lead Scorer, incluindo contraste e o que não usar (logo). Use ao desenhar, implementar ou revisar qualquer tela, componente ou documento visual.
user-invocable: false
---

# Design system G4 — tokens verificados (2026-09-23)

Fonte: variáveis globais do Elementor em `https://g4business.com/wp-content/uploads/elementor/css/post-7.css` e fontes carregadas pela home. Extraído por `curl`, não inferido.

## Cores

| Token | Hex | Papel no site | Uso no Lead Scorer |
|---|---|---|---|
| `primary` | `#001F35` | cor primária (navy) | fundo de header/sidebar, botões primários, títulos |
| `secondary` | `#B9915B` | dourado | acento de ação, bordas de destaque, ícones, tier A |
| `text` | `#031A26` | texto | texto principal sobre fundos claros |
| `surface` | `#F5F4F3` | fundo off-white | fundo de página |
| `navy-700` | `#184560` | navy intermediário | hover de primário, gráficos |
| `risk` | `#842E20` | burgundy | risco/zumbi, reason codes negativos |
| `risk-deep` | `#441B1B` | vinho escuro | estados críticos |
| `white` | `#FFFFFF` | — | cards |
| `highlight` | `#FFCB00` | amarelo | usar com parcimônia (alertas de atenção) |

Semântica adicional (não vem do site; definida aqui para tiers e direção de reason codes, sempre acompanhada de ícone/texto):
`tier-A` = `#B9915B` · `tier-B` = `#184560` · `tier-C` = `#6B7A8C` · `tier-D` = `#9AA3AE` · positivo = `#1F6F5F` · negativo = `#842E20` · neutro = `#6B7A8C`.

## Contraste (WCAG AA, texto normal ≥ 4,5:1)

- `#031A26` sobre `#F5F4F3`: ≈ 15:1 ✓ · `#FFFFFF` sobre `#001F35`: ≈ 16:1 ✓ · `#B9915B` sobre `#FFFFFF`: ≈ 2,9:1 ✗ (só ícones, bordas, texto ≥ 24 px bold, ou botão dourado com texto `#001F35` ≈ 5,5:1 ✓) · `#842E20` sobre `#F5F4F3`: ≈ 8,5:1 ✓ · `#184560` sobre `#F5F4F3`: ≈ 9:1 ✓.

## Tipografia

- Títulos do site: **PPMuseum** 600 (fonte proprietária, não redistribuível) → fallback **Libre Baskerville** 700 (Google Fonts) para títulos de destaque (h1/h2).
- Corpo e UI: **Manrope** 400/500/600/700 (Google Fonts), com fallback `-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`.
- Escala sugerida: 12 / 14 / 16 / 20 / 24 / 32 px; line-height 1,5 no corpo.

## Forma e espaçamento

- Raio padrão **10 px** (cards, inputs, botões); **20 px** em containers de destaque.
- Bordas 1–2 px com `#001F3526` (navy a 15%).
- Grid de 8 px; cards brancos sobre `#F5F4F3` com sombra suave.

## Tom

Direto, executivo, pt-BR, sem jargão de data science na UI. Frases curtas na voz do vendedor.

## Regras

1. Não embutir o logo do G4 nem arquivos de marca; usar wordmark textual "Lead Scorer · Vendas".
2. Direção de reason code sempre por ícone + texto, além da cor.
3. Dourado nunca como cor de texto pequeno sobre claro.
4. Tema único claro no MVP (dark mode fora de escopo).

## Tailwind (trecho para `tailwind.config.ts`)

```ts
colors: {
  g4: { primary: '#001F35', secondary: '#B9915B', text: '#031A26', surface: '#F5F4F3',
        navy700: '#184560', risk: '#842E20', riskDeep: '#441B1B', highlight: '#FFCB00' },
  tier: { A: '#B9915B', B: '#184560', C: '#6B7A8C', D: '#9AA3AE' },
  signal: { pos: '#1F6F5F', neg: '#842E20', neutral: '#6B7A8C' },
},
fontFamily: { sans: ['Manrope', 'system-ui', 'sans-serif'], serif: ['"Libre Baskerville"', 'Georgia', 'serif'] },
borderRadius: { DEFAULT: '10px', lg: '20px' },
```
