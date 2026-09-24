# Design tokens — Lead Scorer · Vendas

Tokens do G4 (skill `g4-design-system`, extraídos do CSS público de g4business.com) mapeados para **papéis semânticos**, com contraste WCAG 2.x verificado por script. Tema único claro. Sem logo: wordmark textual.

---

## 1. Cores → papéis semânticos

| Papel | Token Tailwind | Hex | Onde |
|---|---|---|---|
| Fundo de página | `g4-surface` | `#F5F4F3` | `body` |
| Superfície de card / linha | `white` | `#FFFFFF` | cards, `DealRow`, drawer |
| Texto principal | `g4-text` | `#031A26` | corpo, números |
| Texto secundário | `g4-muted` **(novo)** | `#5B6673` | legendas, "esperados", metadados. Substitui `signal-neutral` como cor de texto (4,39:1, falha). |
| Primário / header / sidebar | `g4-primary` | `#001F35` | header, botão primário, scrim do drawer (40 %) |
| Hover do primário, links, próxima ação | `g4-navy700` | `#184560` | `next_action`, links, anel de foco |
| Acento de ação | `g4-secondary` | `#B9915B` | fundo de botão de ação (texto navy), borda de destaque, tier A, ícones ≥ 20 px. **Nunca texto sobre claro.** |
| Risco | `g4-risk` | `#842E20` | zumbi, `Descartar`, erro da API, direção `−` |
| Risco crítico | `g4-riskDeep` | `#441B1B` | > 138 dias (ícone/borda) |
| Atenção | `g4-highlight` | `#FFCB00` | faixa "conta não informada" a 20 % (`#FFCB00`/20 sobre branco ≈ `#FFF5CC`), texto `g4-text` |
| Tier A | `tier-A` | `#B9915B` | badge sólido, texto `g4-primary` |
| Tier B | `tier-B` | `#184560` | badge sólido, texto branco |
| Tier C | `tier-C` (borda/ícone) · `tier-Cbg` + `tier-Ctext` **(novos)** | `#6B7A8C` · `#E8EBEF` + `#3F4C5C` | badge tintado (branco sobre `#6B7A8C` falha) |
| Tier D | `tier-D` (borda/ícone) · `tier-Dbg` + `tier-Dtext` **(novos)** | `#9AA3AE` · `#F0F2F4` + `#55606C` | badge tintado |
| Sinal + | `signal-pos` · `signal-posBg` **(novo)** | `#1F6F5F` · `#E3F1EC` | ícone ▲, chip de razão positiva |
| Sinal − | `signal-neg` · `signal-negBg` **(novo)** | `#842E20` · `#F6E7E4` | ícone ▼, chip de razão negativa |
| Sinal i | `g4-muted` · `signal-infoBg` **(novo)** | `#5B6673` · `#E8EBEF` | ícone ℹ, chip informativo |
| Linha selecionada | `g4-rowSelected` **(novo)** | `#EEF2F6` | linha com drawer aberto |
| Linha hover | `g4-rowHover` **(novo)** | `#F9F8F7` | hover/focus-within |
| Skeleton | `tier-Cbg` | `#E8EBEF` | placeholders de carregamento |
| Borda | `border-g4line` | `#001F3526` | 1 px em cards/inputs |
| Anel de foco | `g4-navy700` | `#184560` | `outline: 2px solid; outline-offset: 2px` (dourado falha 3:1 sobre branco) |
| Texto desabilitado | `g4-disabled` **(novo)** | `#8A939E` | só em controles desabilitados (isentos pela WCAG 1.4.3); nunca em conteúdo |

---

## 2. Tabela de contraste verificada

Método: WCAG 2.x — luminância relativa `L = 0.2126·R + 0.7152·G + 0.0722·B` com linearização sRGB (`c/12.92` se `c ≤ 0.03928`, senão `((c+0.055)/1.055)^2.4`), razão `(L_claro + 0.05) / (L_escuro + 0.05)`. Limiares AA: **4,5:1** texto normal; **3:1** texto grande (≥ 24 px ou ≥ 18,66 px bold) e componentes de UI (1.4.11). Script executado em 2026-09-23:

```python
def lum(hex_):
    h = hex_.lstrip('#'); r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
def ratio(fg, bg):
    a, b = lum(fg), lum(bg); return (max(a, b) + 0.05) / (min(a, b) + 0.05)
```

### 2.1 Pares aprovados para texto (≥ 4,5:1)

| Primeiro plano | Fundo | Razão | Uso |
|---|---|---|---|
| `#031A26` texto | `#F5F4F3` surface | **16,21:1** | corpo sobre página |
| `#031A26` texto | `#FFFFFF` | **17,80:1** | corpo em cards |
| `#031A26` texto | `#EEF2F6` rowSelected | **15,82:1** | linha selecionada |
| `#031A26` texto | `#F9F8F7` rowHover | **16,78:1** | linha hover |
| `#031A26` texto | `#FFCB00` highlight | **11,69:1** | faixa de atenção (a 100 %; a 20 % o contraste só sobe) |
| `#FFFFFF` | `#001F35` primary | **16,83:1** | header, botão primário |
| `#FFFFFF` | `#184560` navy700 | **10,20:1** | tier B, hover primário |
| `#FFFFFF` | `#842E20` risk | **8,78:1** | botão Descartar, faixa de erro |
| `#FFFFFF` | `#441B1B` riskDeep | **14,81:1** | crítico |
| `#FFFFFF` | `#1F6F5F` pos | **6,00:1** | (opcional) chip sólido positivo |
| `#001F35` primary | `#B9915B` secondary | **5,82:1** | **botão dourado / badge tier A** |
| `#B9915B` secondary | `#001F35` primary | **5,82:1** | texto/ícone dourado sobre header navy (permitido) |
| `#001F35` primary | `#FFCB00` highlight | **11,06:1** | alerta |
| `#184560` navy700 | `#F5F4F3` | **9,28:1** | próxima ação, links sobre página |
| `#184560` navy700 | `#FFFFFF` | **10,20:1** | próxima ação em card |
| `#842E20` risk | `#F5F4F3` | **7,99:1** | texto de risco |
| `#842E20` risk | `#FFFFFF` | **8,78:1** | razão negativa |
| `#842E20` risk | `#F6E7E4` negBg | **7,30:1** | chip negativo |
| `#1F6F5F` pos | `#FFFFFF` | **6,00:1** | razão positiva |
| `#1F6F5F` pos | `#F5F4F3` | **5,47:1** | razão positiva sobre página |
| `#1F6F5F` pos | `#E3F1EC` posBg | **5,16:1** | chip positivo |
| `#5B6673` muted | `#FFFFFF` | **5,84:1** | texto secundário em card |
| `#5B6673` muted | `#F5F4F3` | **5,32:1** | texto secundário sobre página, rodapé |
| `#5B6673` muted | `#E8EBEF` infoBg | **4,89:1** | chip informativo |
| `#3F4C5C` tierCtext | `#E8EBEF` tierCbg | **7,32:1** | badge tier C |
| `#55606C` tierDtext | `#F0F2F4` tierDbg | **5,71:1** | badge tier D |
| `#001F35` primary | `#F4ECE0` tintGold | **14,37:1** | chip "tier A" em versão tinta (se preferir ao sólido) |
| `#001F35` primary | `#E6EBF0` tintNavy | **14,03:1** | chip de filtro ativo |

### 2.2 Pares reprovados — proibidos como texto

| Primeiro plano | Fundo | Razão | Consequência |
|---|---|---|---|
| `#B9915B` dourado | `#FFFFFF` | **2,89:1** | falha AA até para texto grande (3:1). Dourado só como fundo com texto navy, borda ou ícone ≥ 20 px. |
| `#B9915B` dourado | `#F5F4F3` | **2,63:1** | idem |
| `#FFFFFF` | `#B9915B` | **2,89:1** | **badge tier A não pode ter texto branco** → texto `#001F35` |
| `#FFFFFF` | `#6B7A8C` tier C | **4,39:1** | **falha para texto normal**; passa só ≥ 24 px. Badge tier C → tinta `#E8EBEF` + `#3F4C5C`. |
| `#FFFFFF` | `#9AA3AE` tier D | **2,55:1** | falha total → tinta `#F0F2F4` + `#55606C` |
| `#6B7A8C` neutral | `#FFFFFF` | **4,39:1** | **rodapé atual de `App.tsx` (`text-signal-neutral`, 14 px) falha** → usar `g4-muted` |
| `#6B7A8C` neutral | `#F5F4F3` | **3,99:1** | idem; `signal-neutral` fica só para ícone ℹ (≥ 3:1 como componente gráfico: passa) |
| `#8A939E` disabled | `#FFFFFF` / `#F5F4F3` | 3,11 / 2,83 | só em controles `disabled` (isentos) |

### 2.3 Componentes não textuais (≥ 3:1, WCAG 1.4.11)

| Elemento | Cores | Razão | Status |
|---|---|---|---|
| Anel de foco | `#184560` sobre `#FFFFFF` / `#F5F4F3` | 10,20 / 9,28 | ✓ |
| Anel de foco dourado (descartado) | `#B9915B` sobre `#FFFFFF` | 2,89 | ✗ |
| Ícone ▲ `#1F6F5F` sobre branco | | 6,00 | ✓ |
| Ícone ▼ `#842E20` sobre branco | | 8,78 | ✓ |
| Ícone ℹ `#6B7A8C` sobre branco | | 4,39 | ✓ (≥ 3) |
| Borda de card `#001F3526` | decorativa | — | isenta (não transmite informação) |

Desvios já identificados no scaffold `solution/web/src/App.tsx`: (1) `text-white` em todos os badges de tier; (2) `text-signal-neutral` a 14 px no rodapé. Ambos corrigidos pelo bloco Tailwind abaixo + classes por tier.

---

## 3. Tipografia

| Papel | Fonte | Peso | Tamanho / line-height | Classe |
|---|---|---|---|---|
| Wordmark, h1 de tela | Libre Baskerville | 700 | 24 px / 1,25 (h1) · 20 px (wordmark) | `font-serif text-2xl font-bold` |
| h2 de seção | Manrope | 600 | 20 px / 1,3 | `text-xl font-semibold` |
| Score na linha | Manrope | 700 | 20 px / 1 | `text-xl font-bold tabular-nums` |
| Título da linha (Conta · Produto) | Manrope | 600 | 16 px / 1,5 | `text-base font-semibold` |
| Corpo, razão | Manrope | 400 | 14 px / 1,5 | `text-sm` |
| Próxima ação | Manrope | 600 | 14 px / 1,5 | `text-sm font-semibold text-g4-navy700` |
| Metadados, legenda, rodapé | Manrope | 500 | 12 px / 1,5 | `text-xs font-medium text-g4-muted` |
| Números em tiles | Manrope | 700 | 32 px / 1,1 | `text-3xl font-bold tabular-nums` |

Escala: 12 / 14 / 16 / 20 / 24 / 32. Números sempre `tabular-nums` (alinhamento em tabelas). Mínimo 12 px; nada abaixo.

## 4. Espaçamento, raio, elevação

- Grid 8 px: `p-4` (16) interno de linha/card; `gap-2` (8) entre badge/score/título; `p-6` (24) no drawer; `space-y-3` (12) entre linhas da fila.
- Raio **10 px** (`rounded`) em cards, linhas, inputs, botões, badges; **20 px** (`rounded-lg`) só no cartão de estado (vazio/artefatos).
- Borda 1 px `border-g4line`; sombra `shadow-sm` em cards; drawer `shadow-xl`.
- Larguras: sidebar 264 px; conteúdo máx. 1120 px; drawer 480 px (100 % abaixo de 640 px).
- Alvos de toque/clique ≥ 40×40 px (botões de ação 40 px de altura).

## 5. Especificação de componentes

| Componente | Anatomia | Estados | Classes base |
|---|---|---|---|
| **Button primary** | texto 14 px 600, altura 40, `px-4` | hover `bg-g4-navy700`; focus anel navy; disabled `bg-tier-Cbg text-g4-disabled` | `bg-g4-primary text-white rounded font-semibold` |
| **Button action (dourado)** | idem, texto navy | hover `brightness-95`; focus anel navy | `bg-g4-secondary text-g4-primary` |
| **Button danger** (Descartar) | idem, texto branco | pede confirmação inline | `bg-g4-risk text-white` |
| **Button secondary** | borda 1 px, texto navy700 | hover `bg-g4-rowHover` | `border border-g4line text-g4-navy700 bg-white` |
| **Tier badge** | 28×28 (linha) / 24 px pill (tabela), letra 14 px 700 | — | A `bg-tier-A text-g4-primary` · B `bg-tier-B text-white` · C `bg-tier-Cbg text-tier-Ctext` · D `bg-tier-Dbg text-tier-Dtext` |
| **Confidence badge** | ícone ●/◐/○ + texto 12 px 500 | — | `text-g4-muted`; ícone `text-g4-navy700` |
| **Reason chip / linha** | ícone 16 px + peso `tabular-nums` + texto 14 px | — | `+` `text-signal-pos` · `−` `text-signal-neg` · `i` `text-g4-muted` |
| **Filter chip** | texto 12 px 600 + botão × (24×24) | focus anel | `bg-g4-tintNavy text-g4-primary rounded-full px-3 py-1` |
| **Card / DealRow** | `article`, borda, `p-4` | hover `bg-g4-rowHover`; selected `bg-g4-rowSelected border-g4-navy700`; focus-within anel | `bg-white border border-g4line rounded shadow-sm` |
| **Table row** (manager) | `tr` altura 44, zebra `bg-g4-surface` em pares | hover `bg-g4-rowHover`; linha inteira é link | `text-sm tabular-nums` |
| **Drawer** | `aside role=dialog`, 480 px, scrim `bg-g4-primary/40` | abrindo/fechando 150 ms `ease-out`; `prefers-reduced-motion` → sem transição | `bg-white shadow-xl p-6 overflow-y-auto` |
| **Tile** | rótulo 12 px muted acima, número 32 px, sub-rótulo | clicável → `a` com anel | `bg-white border border-g4line rounded p-4` |
| **Warning strip** (conta) | ícone ⚠ 16 px + texto 12 px + CTA link | — | `bg-g4-highlight/20 text-g4-text rounded px-3 py-2` |
| **Toast** | texto 14 px + botão | 6 s, `role=status`; erro `role=alert` | `bg-g4-primary text-white` / `bg-g4-risk text-white` |
| **Skeleton** | blocos `rounded` | `animate-pulse` (desligado com reduced-motion) | `bg-tier-Cbg` |

---

## 6. `tailwind.config.ts` — bloco `theme.extend` completo (para o application-engineer aplicar)

```ts
import type { Config } from 'tailwindcss';

// G4 tokens verified from g4business.com (see .claude/skills/g4-design-system/SKILL.md).
// Semantic additions (muted, tints, row states) documented in docs/design/design-tokens.md
// with WCAG ratios; do not add a color here without adding its contrast row there.
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        g4: {
          primary: '#001F35',
          secondary: '#B9915B',
          text: '#031A26',
          muted: '#5B6673', // 5.84:1 on white — replaces signal.neutral for text
          disabled: '#8A939E', // disabled controls only (WCAG-exempt)
          surface: '#F5F4F3',
          navy700: '#184560',
          risk: '#842E20',
          riskDeep: '#441B1B',
          highlight: '#FFCB00',
          tintNavy: '#E6EBF0', // active filter chip bg
          tintGold: '#F4ECE0', // optional tier A tint
          rowHover: '#F9F8F7',
          rowSelected: '#EEF2F6',
        },
        tier: {
          A: '#B9915B', // text must be g4.primary (5.82:1)
          B: '#184560', // text white (10.20:1)
          C: '#6B7A8C', // icon/border only; badge uses Cbg/Ctext
          D: '#9AA3AE', // icon/border only; badge uses Dbg/Dtext
          Cbg: '#E8EBEF',
          Ctext: '#3F4C5C', // 7.32:1 on Cbg
          Dbg: '#F0F2F4',
          Dtext: '#55606C', // 5.71:1 on Dbg
        },
        signal: {
          pos: '#1F6F5F', // 6.00:1 on white
          neg: '#842E20', // 8.78:1 on white
          neutral: '#6B7A8C', // icons only (4.39:1 fails for small text)
          posBg: '#E3F1EC',
          negBg: '#F6E7E4',
          infoBg: '#E8EBEF',
        },
      },
      fontFamily: {
        sans: ['Manrope', 'system-ui', 'sans-serif'],
        serif: ['"Libre Baskerville"', 'Georgia', 'serif'],
      },
      fontSize: {
        xs: ['12px', '1.5'],
        sm: ['14px', '1.5'],
        base: ['16px', '1.5'],
        xl: ['20px', '1.3'],
        '2xl': ['24px', '1.25'],
        '3xl': ['32px', '1.1'],
      },
      borderRadius: { DEFAULT: '10px', lg: '20px' },
      borderColor: { g4line: '#001F3526' },
      outlineColor: { focus: '#184560' },
      width: { sidebar: '264px', drawer: '480px' },
      maxWidth: { content: '1120px' },
      boxShadow: { card: '0 1px 2px rgba(0,31,53,0.06), 0 1px 3px rgba(0,31,53,0.10)' },
    },
  },
  plugins: [],
} satisfies Config;
```

Diff efetivo em relação ao arquivo atual: adiciona `g4.muted/disabled/tintNavy/tintGold/rowHover/rowSelected`, `tier.Cbg/Ctext/Dbg/Dtext`, `signal.posBg/negBg/infoBg`, `fontSize`, `outlineColor`, `width`, `maxWidth`, `boxShadow`. Nada removido — `signal.neutral` permanece para ícones.

Adição sugerida em `src/index.css` (`@layer base`):

```css
:focus-visible { outline: 2px solid #184560; outline-offset: 2px; border-radius: 10px; }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
```

## 7. `src/i18n/pt-BR.ts`

O objeto `t` completo está em `ux-spec.md` §8 (fonte única para não divergir). Substitui o arquivo atual por inteiro; as chaves já existentes (`brand`, `tagline`, `status`, `tiers`) mantêm os mesmos valores; `placeholder` é removida quando a tela real entrar.
