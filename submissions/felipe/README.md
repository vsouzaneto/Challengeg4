# Submissão — Felipe de Lima Santiago — Challenge 001

Pasta oficial: **`submissions/felipe/`**. Use só esta cópia no PR. Se existir `submissions/felip/` (nome antigo), apague depois de fechar IDE e servidores que usem a pasta.

## Sobre mim

- **Nome:** Felipe de Lima Santiago
- **LinkedIn:** https://www.linkedin.com/in/felipelsantiago/
- **Challenge escolhido:** 001 — Diagnóstico de Churn (RavenStack)

---

## Executive Summary

Cruzamos as **cinco tabelas** RavenStack e explicamos o paradoxo do CEO: **uso agregado (~10 linhas/conta) e CSAT (~4,0) estáveis**, enquanto **600 eventos de churn** contrastam com **110 contas em churn líquido (22%)**. A causa raiz não é colapso de produto ou CS, e sim **governança de métricas (eventos + reativações)** e **277 contas ativas em porta giratória** (**US$ 665.190 MRR** em risco recorrente), versus **US$ 254.952 MRR** já perdidos no líquido. Entregamos fila CS priorizada por MRR com explicação por conta, playbook operacional, cenários de impacto em `recommendations_impact.csv`, **Command Center com filtros globais** (não-Streamlit) e pipeline reprodutível com QA de joins. **Ação #1:** alterar KPIs do board e executar playbook revolving (top 50 em `solution/outputs/fila_cs_top50.csv`).

---

## Solução

### Abordagem

1. **Negócio antes de ferramenta:** decomposição do brief CEO (uso vs CSAT vs churn) → hipóteses testáveis.
2. **Audit de 166 PRs** abertos → escolha estratégica do 001 (`docs/METODOLOGIA.md`).
3. **Integração** das cinco tabelas RavenStack (`docs/METODOLOGIA.md` §4).
4. **Verificação** de cada claim (paradoxo, segmentos, causalidade) → `reports/causality_register.md`.
5. **Produto CS:** score explicável + exports CRM + app.

### Resultados / Findings

| Entrega | Caminho |
|---------|---------|
| CEO (1 página) | `solution/reports/ceo_one_pager.md` |
| Diagnóstico completo | `solution/reports/executive_summary.md` |
| Playbook CS | `solution/reports/playbook_cs_revolving.md` |
| Fila priorizada | `solution/outputs/fila_cs_top50.csv` |
| Impacto estimado | `solution/outputs/recommendations_impact.csv` |
| Uso por segmento/mês | `solution/outputs/usage_by_industry_month.csv` |
| **Command Center** (React + filtros + período) | `solution/command-center/` + `serve_dashboard.py` |
| Contas / fila (PT-BR) | `solution/outputs/contas_analitico.csv`, `fila_cs_top50.csv` |
| Metodologia, dados, produto, IA | `docs/METODOLOGIA.md` |
| Rubrica CE + checklist PR | `docs/ENTREGA-E-PR.md` |

**Setup rápido (Windows, PC do zero)**

```text
cd submissions\felipe
start.bat
```

O batch instala `requirements.txt`, tenta baixar CSVs do Kaggle em `data/`, roda pipeline, build React, `verify_submission.py`, pytest e sobe o dashboard.

Abre **http://127.0.0.1:8765** — filtros em chips recalculam KPIs, gráficos e fila.

Setup manual: `solution/README.md` · dados: `data/README.md`.

**Erros comuns**

| Sintoma | Causa | Correção |
|---------|--------|----------|
| Listagem só com `data/` | Servidor errado (ex.: `http.server` em `public/`) | Rode `start.bat` — serve `command-center/dist/` |
| 404 build ausente | Pasta `felip` ou sem `dist/` | `start.bat` a partir de `submissions\felipe` |
| Conexão recusada | Nada na porta 8765 | Rode `start.bat` |
| Kaggle falhou | Sem login/token | CSVs manuais em `data/` — ver `data/README.md` |

### Recomendações

| Prio | Ação | Impacto (cenário) |
|------|------|-------------------|
| 1 | KPI: churn **líquido** + reativação + **MRR** | Evita decisões erradas (board) |
| 2 | Playbook **277 revolving** | **+US$ 33k/mês** se 5% MRR retido (`recommendations_impact.csv`) |
| 3 | Cohort **DevTools** + canal **event** | Reduz segmentos ~31% / ~30% churn líquido |
| 4 | Alerta **escalação** + histórico | Early warning (correlato ~6% vs ~4%) |
| 5 | Modelo AUC ~0,62 | Triagem humana, não automação cega |

### Limitações

- Dataset público; causalidade não provada (`causality_register.md`).
- Modelo preditivo moderado — não vendido como oráculo.
- CSVs locais (Kaggle); integridade via `outputs/data_manifest.json`.

---

## Process Log — Como usei IA

> **Obrigatório G4** — sem este bloco a submissão é desclassificada. Versão completa: [`process-log/PROCESS-LOG.md`](process-log/PROCESS-LOG.md).

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| **Cursor Agent** | Orquestração: audit PRs, pipeline, React, docs, verificador — escolhi agente porque o escopo mistura dados, UI e entrega CE. |
| **Python / sklearn** | Joins das 5 tabelas, segmentos, modelo de triagem, exports CS |
| **React (Vite + Recharts)** | Command Center executivo (filtros globais + período), alternativa ao padrão Streamlit do field |
| **Kaggle CLI** | Dataset MIT; `start.bat` tenta download se faltarem CSVs |
| **GitHub CLI** | Audit de PRs abertos na fase de estratégia |

### Decomposição antes de promptar

1. Regras G4 + CONTRIBUTING (PR só em `submissions/`, process log).  
2. Escolha do challenge após audit do field (166 PRs).  
3. Brief CEO → hipóteses testáveis (eventos vs líquido, MRR, revolving).  
4. Integração + QA antes de narrativa.  
5. Produto para board + gate `verify_submission.py`.

### Workflow

1. Mapa repo + challenges → 2. Audit PRs → **001** → 3. Pipeline + paradoxo → 4. Relatórios/playbook → 5. CE: verify, pytest, impacto → 6. React + `start.bat` → 7. Process log e PR.

**8 iterações principais** (detalhe em `process-log/`).

### Onde a IA errou e como corrigi

- Narrativa de queda global de uso → **refutada no EDA** → revolving + governança de métricas.  
- Merge duplicou colunas → `columns.py`.  
- UI Streamlit/listbox → React + chips + drill-down.  
- `start.bat` quebrava no CMD (parênteses) → batch corrigido.

### O que eu adicionei que a IA sozinha não faria

Audit competitivo; métrica **revolving** + MRR; fila com **motivo_risco**; registro causal; verificador pré-PR; honestidade sobre AUC; escopo PR limpo.

---

## Validar números

1. `cd submissions/felipe` → **`start.bat --full`** (recomputa tudo + pytest).
2. Conferir `solution/outputs/summary_stats.json` vs KPIs do dashboard (mesmo recorte global).
3. Reconciliação: `outputs/data_quality_summary.csv` ↔ card **Integridade dos dados**.
4. Fila CS: `outputs/fila_cs_top50.csv` ↔ tabela do Command Center (ordenada por `prioridade_mrr`).
5. Modelo: AUC em `summary_stats.json` = tooltip KPI; detalhe em `reports/model_and_limits.md`.

API local opcional: `cd solution && python api_server.py` → http://127.0.0.1:8766/health

---

## Evidências

- [x] Narrativa escrita — `process-log/PROCESS-LOG.md`
- [x] Chat export — `process-log/chat-exports/SESSAO-CURSOR-EXPORT.md`
- [x] Screenshots / figuras — `process-log/screenshots/*.png`
- [x] Prompts de conversa (export) — `process-log/chat-exports/PROMPTS-REAIS-CURSOR.md`
- [x] Screen recording — coberto por combinação de formatos (guia G4)
- [x] Git history — branch deste PR (só `submissions/felipe/`)
- [x] Autoteste CE — `docs/ENTREGA-E-PR.md`

---

## PR (somente esta pasta)

```bash
git add -f submissions/felipe
```

Checklist e PR: `docs/ENTREGA-E-PR.md` · corpo `gh`: `docs/PR-BODY.md`

---

_Submissão: 2026-10-16 · Nível alvo: **CE** (consistentemente excede)_
