# Export narrativo — sessões Cursor (Challenge 001)

_Formato aceito G4: **chat export / narrativa escrita** (prompts humanos + resposta/correção resumida)._

---

## Iteração 1 — Regras e escopo

**Prompt:** Estudar AI Master Challenge, challenges e o que é CE.

**IA:** Mapeou 4 challenges, PR exclusivo, process log obrigatório.

**Humano:** Não codar antes de escolher challenge e ler submission-guide.

---

## Iteração 2 — Audit competitivo

**Prompt:** Analisar PRs abertos, gaps do field, qual challenge.

**IA:** Script + `pr-deficiencies-report.md`; sugeriu 001.

**Correção:** `gh api --repo` inválido → ajuste no helper.

**Humano:** 003 saturado; 001 permite 5 tabelas + narrativa CEO + fila MRR.

---

## Iteração 3 — Pipeline e paradoxo

**Prompt:** Integrar 5 CSVs RavenStack e responder tensão CEO (CSAT/uso vs churn).

**IA:** `run_analysis.py`, primeiros relatórios, sugestão de queda de uso.

**Correção (dados):** Médias de uso ~iguais → tese **600 eventos vs 110 líquido**, **277 revolving**.

**Correção (merge):** `plan_tier`/`seats` duplicados → `columns.py`.

---

## Iteração 4 — Nível CE

**Prompt:** Hardening G4: verificador, pytest, playbook, impacto MRR, causalidade.

**IA:** `verify_submission.py`, rubrica, exports XLSX/CSV, `causality_register.md`.

**Humano:** Manter AUC ~0,62 explícito; não oversell do modelo.

---

## Iteração 5 — Produto (React)

**Prompt:** Command Center executivo, não template Streamlit.

**IA:** Vite + Recharts, bundle JSON, filtros.

**Humano:** Chips globais, drill-down, navy+dourado G4; remover logo quando pedido.

---

## Iteração 6 — Filtros e operação

**Prompt:** Filtro de datas, start.bat Windows, docs enxutos.

**IA:** `periodo_*` no bundle, `start.bat`, consolidação `docs/METODOLOGIA.md`.

**Correção:** `start.bat` — parênteses em echo quebravam CMD → batch reescrito.

---

## Iteração 7 — Entrega

**Prompt:** Process log completo (guia G4), CONTRIBUTING, PR.

**IA:** PROCESS-LOG expandido, evidências, commit/PR.

**Humano:** Checklist: só `submissions/felipe/`, fork + branch `submission/felipe-santiago`.

---

## Ferramentas (resumo)

Cursor Agent · Python/pandas/sklearn · React/Vite/Recharts · Kaggle CLI · gh

## Julgamento humano recorrente

Validar números antes de aceitar narrativa da IA; recusar UI genérica; PR limpo; localhost only para dashboard.
