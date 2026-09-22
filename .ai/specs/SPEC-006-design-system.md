---
status: passing
canonical: true
area: design-system
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-006 Design system G4 Scale

## Comportamento visível

UIs construídas neste git (submissão, proto, dashboard) usam a identidade do PDF G4 Scale: navy/aço/gelo, wordmark losango + `G4SCALE`, CTA pill, grafismo de régua. Não usam glam, rebrand G4 2026 nem chrome Behance.

## Contrato

1. Fonte canônica de cor e logo = PDF em `.ai/design-system/` + hex em `G4-SCALE-TOKENS.md` / `tokens.css`.
2. Seis cores de marca apenas. Estados de form = tokens `feedback-*` derivados, não paleta do framework.
3. Tipografia oficial **não nomeada**. Fallback `--g4s-font-sans` (Inter / Geist / Helvetica Neue).
4. Componentes: receitas em `GUIDANCE.md` (grau **derivado**). Hex solto em Angular/React/Vue = fora.
5. Páginas 6–7 do PDF estão fora do contrato.
6. Copiar `tokens.css` para `submissions/<nome>/solution/` — não versionar tema no brief.

## Verificação

- [ ] `tokens.css` contém exatamente `#32445A` `#466381` `#9CA5AC` `#E3EAF2` `#EFF2FB` `#FFFFFF`.
- [ ] SPEC-REVERSE lista as 7 páginas e marca 6–7 como chrome.
- [ ] GUIDANCE mapeia Angular, React e Vue para `--g4s-*`.
- [ ] Nenhum token `#fe357b` / dourado editorial / `#0057FF`.

Reamostrar o PDF se o arquivo for trocado:

```text
python -c "import pymupdf; … Matrix(2,2) …"
```

## Evidência

2026-09-21: PDF 11 741 533 bytes, 7 págs., texto 0. Hex da pág. 2 amostrados no raster 2×. Case Behance fev/2022 (Glauber Pinheiro).

## Notas

Não é Storybook. Não é o manual institucional 2026. Losango “de olho” em CSS puro só se parecer com as faixas do PDF; senão wordmark texto.

## Sucesso / falha

- Sucesso: app 003 com header canvas, CTA navy pill, score thin navy, tabela mist, charts aço→gelo.
- Falha: MUI default, Vuetify purple, dashboard Plotly rainbow, CTA rosa.

## Migração e compatibilidade

Prefixo `--g4s-` é estável. Trocar PDF = bump desta spec + reamostra + tokens.
