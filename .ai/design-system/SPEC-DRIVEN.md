# SPEC-DRIVEN — Design system G4 Scale

Como evoluir UI neste git sem inventar cor, símbolo ou família.

---

## Fonte de verdade

| Assunto | Onde | Grau |
|---------|------|------|
| Swatches + valores + logo + grafismo | PDF + [SPEC-REVERSE.md](SPEC-REVERSE.md) | **canônico** |
| Hex e papéis | [G4-SCALE-TOKENS.md](G4-SCALE-TOKENS.md) + [tokens.css](tokens.css) | canônico (amostra 2026-09-21) |
| Receitas de componente | [GUIDANCE.md](GUIDANCE.md) | **derivado** dos mockups |
| Spec de plataforma | [../specs/SPEC-006-design-system.md](../specs/SPEC-006-design-system.md) | contrato deste git |

Uma spec `in_progress` por vez. Mudança de hex canônico = reamostrar o PDF na mesma entrega.

---

## Regras

1. **Seis cores de marca.** `#32445A` `#466381` `#9CA5AC` `#E3EAF2` `#EFF2FB` `#FFFFFF`. Qualquer outra é derivada e deve ser nomeada assim.
2. **Sem segundo acento.** Proibido rosa glam, dourado 2026, azul Behance `#0057FF`, roxo Material, verde “success” de framework.
3. **Estados de form** (erro / sucesso / aviso) não estão no PDF. Usar os tokens `--g4s-feedback-*` de [tokens.css](tokens.css) (desaturados, derivados) — não importar paleta do framework.
4. **Logo:** losango de faixas + `G4SCALE`. Não redesenhar o símbolo. Não trocar por esfera armilar.
5. **Grafismo:** só ticks de régua. Sem padrão geométrico novo, sem emoji de marca.
6. **Tipo:** PDF não nomeia fonte. Usar `--g4s-font-sans` (fallback aberto). Não puxar Montserrat/Open Sans do glam.
7. **Framework ≠ marca.** Angular Material, MUI, PrimeNG, Vuetify, Naive, Element Plus só entram se o **tema** mapear `--g4s-*`. Tema default do kit = fora.
8. **Págs. 6–7 do PDF** não são token.
9. **RavenStack** (001) é cenário. O DS G4 Scale veste a **ferramenta**, não o logo fictício da conta SaaS — a menos que o candidato crie marca própria e declare no process log.
10. **Hex no JS/TS/Vue só via token.** `var(--g4s-color-navy)` / `theme.navy`.

---

## Onde colocar código

| Tipo | Destino |
|------|---------|
| App do candidato | `submissions/<nome>/solution/` — copiar `tokens.css`, não editar o PDF |
| Evolução do contrato DS | `.ai/design-system/` + [SPEC-006](../specs/SPEC-006-design-system.md) |
| Novo swatch | só se o PDF (ou manual G4 oficial) mostrar — reamostrar |

---

## Qualidade

Antes de considerar um componente “G4 Scale”:

- [ ] Fundo é canvas / névoa / gelo / navy / aço — não cinza quente 50 do Tailwind default.
- [ ] CTA primário é pill navy/aço + texto branco.
- [ ] Display grande é thin + tracking aberto **ou** o layout não usa display (tabelas/dash).
- [ ] Contraste texto navy sobre gelo/branco passa leitura (navy `#32445A` em `#FFFFFF` / `#E3EAF2` é o par canônico).
- [ ] Zero token glam / dourado / Behance.

Área crítica: wordmark, CTA, cores de gráfico (eixo deve ser aço→gelo, não rainbow).
