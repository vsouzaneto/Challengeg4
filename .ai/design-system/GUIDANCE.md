# Guidance — componentes G4 Scale (Angular, React, Vue)

Contrato visual para qualquer stack. Tokens: [tokens.css](tokens.css). Canônico vs derivado: [SPEC-DRIVEN.md](SPEC-DRIVEN.md).

Não existe pacote `g4-scale-ui` neste git. O componente nasce no app do candidato mapeando `--g4s-*`.

---

## 1. Princípios (valores da pág. 2)

| Valor | Em UI |
|-------|--------|
| Minimalista | Um acento (navy/aço). Sem sombra ornamental. Sem ícone decorativo. |
| Moderna | Display thin + foto full-bleed **ou** dashboard gelado. Sem skeuomorphism. |
| Humana | Foto de pessoas reais, luz fria; copy direto. Sem stock “high-five”. |
| Madura | Densidade executiva: números grandes, labels overline. Sem emoji de marca. |
| Inovadora | Grafismo de régua e números de pilar (`01`), não ilustração 3D. |
| Confiável | Contraste navy/branco; CTA único por bloco; estado vazio honesto. |

---

## 2. Anatomia da página (mockups 1 e 5)

```
[ wordmark ◆ G4SCALE ]     link  link  link     ( CTA pill )
────────────────────────────────────────────────────────────
  HERO foto full-bleed
  display thin BRANCO          kicker slate
  social line-icons
────────────────────────────────────────────────────────────
  page = mist / canvas
  cards = branco, radius 24, foto + title + CTA
────────────────────────────────────────────────────────────
  footer canvas · wordmark · links slate
```

Largura de conteúdo ~1120–1200 px. Gutter 24–48. Header 64–72 px, fundo canvas, borda inferior ausente ou 1 px ice.

---

## 3. Receitas de componente

Estados: `default` · `hover` · `focus-visible` · `active` · `disabled`.  
Focus: `outline: 2px solid var(--g4s-focus-ring); outline-offset: 2px`.

### Button

| Variante | Fundo | Texto | Borda | Raio |
|----------|-------|-------|-------|------|
| **Primary** | navy | canvas | none | pill |
| **Secondary** | steel | canvas | none | pill |
| **Ghost** | transparent | navy | 1 px steel | pill |
| **Quiet** | transparent | steel | none | pill |
| Disabled | ice | slate | none | pill |

Hover primary: aço (`#466381`). Active: navy. Altura 40–44 px, padding `12px 24px`, weight 500, sem sombra. Ícone só linear, 16 px, à esquerda.

Proibido: contained quadrado Material; elevation 4; ripple rosa.

### Link

Cor steel; hover navy; underline só no hover. Nav do header: sem underline, weight 400, muted; item ativo = navy + tracking.

### Input / Select / Textarea

- Fundo canvas, borda `1px` slate 40%, radius **control** (8 px — não pill).
- Label: caption / overline navy.
- Placeholder: slate.
- Focus: borda steel + ring.
- Erro: borda + texto `feedback-danger` (derivado).
- Altura 40–44 px. Sem floating label estilo MUI se isso puxar tema default.

### Card

Fundo canvas, radius 24, sem borda ou borda ice. Sobre navy: + `--g4s-shadow-card`. Padding 24–32. Título title-size navy. Corpo 16 slate/steel. CTA no rodapé, alinhado à esquerda (mockup *QUERO PARTICIPAR*).

Card de pilar: número gelo 96–128 px atrás da foto (`01`).

### Header / Nav

Esquerda: wordmark. Centro/direita: links. Extrema direita: primary pill. Mobile: wordmark + ícone linear (não hamburger colorido).

### Score / KPI (003)

Número display 48–72, weight 200, navy. Label overline slate. Delta: ok/warn/danger **só** no texto auxiliar, não no número. Barra de score: track ice, fill navy. Explicação do score em caption — obrigatório no 003.

### Table

Header overline slate, fundo mist. Row canvas; hover ice. Números tabulares, alinhados à direita. Sem zebra verde/azul de framework.

### Badge / Tag

Pill, fundo ice, texto navy, weight 500, 11–12 px. Status Won/Lost (003): texto + badge ice/navy — não verde/vermelho saturado.

### Tabs

Underline steel no ativo; sem pill preenchida no grupo (isso compete com CTA).

### Modal / Drawer

Overlay navy @ 40%. Superfície canvas, radius 24, sem header colorido.

### Toast

Canvas + borda esquerda 4 px navy (info) ou feedback-* (estado). Sem snackbar verde Material.

### Chart

Grid ice; eixo slate; série 1 navy; série 2 steel; série 3 slate. Tooltip canvas, radius 8. Sem gradient candy.

### Empty / Error

Texto steel, um CTA ghost. Sem ilustração 3D.

---

## 4. Logo e grafismo

**Wordmark**

```html
<span class="g4s-mark" aria-hidden="true"></span>
<span class="g4s-word">G4SCALE</span>
```

- Losango: 4 faixas concêntricas, cor = aço em fundo claro, canvas em fundo navy/foto.
- Não esticar. Não recortar o losango. Não substituir por “G4” solto em outra fonte.
- Altura mínima ~24 px (header). Favicon = só o losango.

**Grafismo de régua**

Ticks 1–2 px, altura 24–64, gap 16–24, cor canvas @ 30% sobre navy **ou** slate @ 40% sobre gelo. Uso: hero de merch, fundo de KPI, divisor — não como bullet de lista.

---

## 5. Fotografia

- Pessoas em contexto de trabalho; paleta fria (ciano-cinza).
- Overlay de texto: foto já escura **ou** navy @ 20–30% — display sempre canvas.
- Sem filtro laranja, sem duotone rosa.

---

## 6. Acessibilidade

| Par | Contraste |
|-----|-----------|
| navy em canvas / mist / ice | texto corpo OK |
| canvas em navy / steel | texto + CTA OK |
| slate em canvas | **só** caption / placeholder — não corpo longo |
| slate em ice | evitar texto essencial |

Focus visível obrigatório. Não depender da foto para contraste do display (checar overlay).

---

## 7. Mapear no framework

Importar `tokens.css` **uma vez** no entry. Depois só `var(--g4s-*)`.

### Angular

```ts
// styles.scss — entry
@use 'tokens'; // ou @import 'tokens.css';

// NÃO: @include mat.theme com paleta $azure / $pink
```

```scss
// button.component.scss
:host button.g4s-primary {
  background: var(--g4s-bg-strong);
  color: var(--g4s-fg-on-strong);
  border: 0;
  border-radius: var(--g4s-radius-pill);
  min-height: 40px;
  padding: 12px 24px;
  font: 500 14px/1 var(--g4s-font-sans);
}
:host button.g4s-primary:hover {
  background: var(--g4s-bg-strong-alt);
}
```

Material / CDK: `mat.define-theme` com primary = navy, tertiary = steel, error = `--g4s-feedback-danger`. Desligar ripple colorido. `MatPaginator` e `MatTable` herdam fundo mist.

Standalone: preferir botão nativo + classes a `mat-flat-button` sem tema.

### React

```tsx
import './tokens.css';

export function Button({ variant = 'primary', ...props }: ButtonProps) {
  return <button className={`g4s-btn g4s-btn--${variant}`} {...props} />;
}
```

```css
.g4s-btn--primary {
  background: var(--g4s-bg-strong);
  color: var(--g4s-fg-on-strong);
  border-radius: var(--g4s-radius-pill);
}
```

MUI: `createTheme({ palette: { primary: { main: '#32445A' }, secondary: { main: '#466381' }, background: { default: '#EFF2FB', paper: '#FFFFFF' } }, shape: { borderRadius: 8 }, typography: { fontFamily: 'Inter, …' } })`. `MuiButton.styleOverrides.root.borderRadius = 999`.

Chakra / Mantine / Ant: o mesmo remap. Tailwind: estender `theme.colors.g4s` — **não** usar `blue-600` / `slate-900` quente como se fosse marca.

### Vue

```ts
// main.ts
import './tokens.css';
```

```vue
<button class="g4s-btn g4s-btn--primary"><slot /></button>
```

Vuetify: `createVuetify({ theme: { themes: { light: { colors: { primary: '#32445A', secondary: '#466381', surface: '#FFFFFF', background: '#EFF2FB' } } } } })`. Naive / Element Plus: `n-config-provider` / `ElConfigProvider` com as mesmas hex.

---

## 8. Por challenge

| Serviço | Superfície | Obrigatório visual |
|---------|------------|--------------------|
| 001 Churn | relatório / dashboard | KPI navy, tabelas mist, charts aço→gelo; CEO lê em 1 tela |
| 002 Support | proto classificador / inbox | lista de tickets em card; prioridade = badge ice, não semáforo arco-íris |
| 003 Lead Scorer | **app que roda** | header + lista de deals + score explicável; CTA “focar neste deal” = primary pill |
| 004 Social | análise / dashboard | cards de plataforma; sponsored = badge, não dourado |

RavenStack (001): pode ter wordmark próprio no relatório; o **chrome da ferramenta** continua G4 Scale se a entrega for “produto G4”.

---

## 9. Do / Don't

| Do | Don't |
|----|-------|
| Navy / aço / gelo | Rosa glam, dourado 2026, azul Behance |
| Pill só em CTA e badge | Input pill, table pill |
| Display thin no hero | Display bold condensado “startup” |
| Ticks de régua | Pattern geométrico novo |
| Losango de faixas | Esfera armilar, monograma inventado |
| Inter/Geist como fallback | Montserrat + Open Sans (glam) |
| Um CTA por card | Três contained side-by-side |
| Chart em escala de aço | Rainbow Plotly default |

---

## 10. Checklist de implementação

1. Copiar `tokens.css` para o app.  
2. Importar no entry (scss / `main.ts` / `index.tsx`).  
3. Remapear o tema do kit **antes** do primeiro componente.  
4. Button / Card / Table / Score com as receitas acima.  
5. Wordmark só se houver asset; senão texto `G4SCALE` em tracking 0.04em + weight 500 — não desenhar losango “de olho” em CSS se ficar um quadrado cheio.  
6. Passar o checklist de [SPEC-DRIVEN.md](SPEC-DRIVEN.md).
