# Process Log — Challenge 001 (obrigatório G4)

**Candidato:** Felipe de Lima Santiago  
**Formatos usados nesta pasta:** narrativa escrita + chat export + figuras (screenshots) + git history (este PR).

Metodologia e números do case: [`../docs/METODOLOGIA.md`](../docs/METODOLOGIA.md).

---

## 1. Ferramentas de IA e por quê

| Ferramenta | Por quê (não só “o que”) |
|------------|---------------------------|
| **Cursor Agent** | Repositório grande, muitos arquivos e iterações — precisava de agente que edita código, roda pipeline, build React e docs no mesmo fluxo. |
| **Python + pandas/sklearn** | Join das 5 tabelas, QA reprodutível, modelo de triagem e exports CS — IA gerou rascunho; números validados por script fixo. |
| **React (Vite + Recharts)** | Field converge em Streamlit; pedi produto executivo com filtros globais — IA implementou UI, eu defini critérios de aceite (chips, drill-down, G4 visual). |
| **Kaggle CLI** | Dataset MIT oficial; `start.bat` tenta download automático para quem clona do zero. |
| **GitHub CLI (`gh`)** | Audit de 166 PRs abertos para escolha estratégica do challenge — script assistido por IA, corrigido manualmente. |

**Formatos combinados (guia G4):** narrativa + chat export + figuras + git — cobre o espírito de “screenshots de conversa” via [`chat-exports/PROMPTS-REAIS-CURSOR.md`](./chat-exports/PROMPTS-REAIS-CURSOR.md). Screen recording não anexado (opcional quando há combinação).

---

## 2. Decomposição do problema (antes de promptar)

Ordem consciente — **sem** “gera um dashboard de churn” como primeiro prompt:

1. **Regras G4:** PR só em `submissions/`, process log obrigatório, superar baseline, CONTRIBUTING + submission-guide.
2. **Escolha de challenge:** auditar field (166 PRs) → 001 vs saturação do 003.
3. **Brief CEO em hipóteses falsificáveis:** eventos ≠ líquido; uso agregado vs subset pré-churn; CSAT vs escalação; MRR vs contagem.
4. **Integração de dados:** grafo de joins + QA antes de narrativa.
5. **Produto:** o que o board precisa ver em 5 min (one-pager + Command Center).
6. **Gate de entrega:** `verify_submission.py`, pytest, `start.bat`, docs consolidados.

Só depois disso: prompts de implementação (pipeline, relatórios, React, hardening CE).

---

## 3. Workflow (onde a IA entrou)

| Etapa | Humano | IA |
|-------|--------|-----|
| Leitura repo + challenges | Priorizou CE vs “só passar” | Mapa de pastas e regras |
| Audit PRs | Decidiu Challenge **001** | Script + relatório de deficiências |
| EDA / joins | Validou paradoxo nos CSVs | `run_analysis.py`, exports |
| Narrativa CEO | Tom e tese revolving | Rascunhos `reports/*.md` |
| UI | Rejeitou Streamlit/listbox | Command Center React |
| Entrega | PR scope, honestidade AUC | `start.bat`, docs, verificador |

---

## 4. Onde a IA errou e como corrigi

| Erro da IA | Como percebi | Correção |
|------------|--------------|----------|
| Narrativa de **queda global de uso** | Conferi médias no EDA (~10 linhas/conta, retidas vs churn) | Pivot: eventos + **revolving** + governança de métricas |
| Merge duplicou `plan_tier` / `seats` | Colunas `_sub`/`_acct` no export | `analytics/columns.py` coalesce explícito |
| `gh api --repo` inválido no audit | Script falhou | Ajuste de chamada `gh` |
| UI Streamlit / `<select multiple>` | Não atende barra executiva | React + chips + clique nos gráficos |
| Servidor em `public/` (listagem só `data/`) | 404 / directory listing | `serve_dashboard.py` + `start.bat` |
| `start.bat` quebrava no Windows | Parênteses em `echo` / mensagens npm | Reescrita do batch + caminho `ROOT=%~dp0` |
| Cursor hover cinza “quadrado” no gráfico | Feedback visual | Tooltip cursor suavizado (blur + dourado) |

Detalhe iterativo: [`chat-exports/SESSAO-CURSOR-EXPORT.md`](./chat-exports/SESSAO-CURSOR-EXPORT.md).

---

## 5. O que eu adicionei que a IA sozinha não faria

- **Audit quantitativo** de PRs antes de escolher o case (posicionamento, não conveniência).
- Métrica **revolving** + **MRR em risco** (277 contas, ~US$ 665k) — não só “churn subiu”.
- Fila CS com **`motivo_risco`** por conta e playbook operacional.
- **`causality_register.md`** + AUC ~0,62 visível (triagem, não oráculo).
- **`verify_submission.py`** como gate CE antes do PR.
- Decisão de **não** publicar tunnel/ngrok; dashboard só **localhost**.
- Consolidação de docs (`METODOLOGIA.md`, `ENTREGA-E-PR.md`) e entrega “clone e rode” (`start.bat` + artefatos).

---

## 6. Iterações (quantidade)

**8 ciclos principais** (cada um com vários sub-prompts):

1. Mapa repo + regras G4  
2. Audit 166 PRs → decisão 001  
3. Pipeline v1 + paradoxo revolving  
4. Relatórios CEO + exports CS  
5. Hardening CE (verify, pytest, playbook, impacto, causalidade)  
6. Command Center React + filtros + identidade G4  
7. Filtro de período, docs consolidados, `start.bat`  
8. Polish UI + preparação PR (process log completo, evidências)  
9. **Fases P0–P6** — qualidade de dados, drawer conta, SPEC-001, pytest expandido, `start.bat --full`, API read-only, posicionamento PR

**Loom / demo gravada (P5):** _[inserir link quando gravado]_ — alternativa: screenshots `screenshots/ui-*.png` + `start.bat`.

---

## 7. Evidências (checklist guia de submissão)

| Formato | Onde |
|---------|------|
| [x] **Narrativa escrita** | Este arquivo + README § Process Log |
| [x] **Chat export** | [`chat-exports/SESSAO-CURSOR-EXPORT.md`](./chat-exports/SESSAO-CURSOR-EXPORT.md) |
| [x] **Screenshots / figuras** | [`screenshots/*.png`](./screenshots/) + prompts em [`PROMPTS-REAIS-CURSOR.md`](./chat-exports/PROMPTS-REAIS-CURSOR.md) |
| [x] **Screen recording** | Substituído por combinação export + figuras + git (ver [`screenshots/README.md`](./screenshots/README.md)) |
| [x] **Git history** | Branch `submission/felipe-santiago` — commits só em `submissions/felipe/` |

---

## 8. Autoverificação

```bash
cd submissions/felipe/solution
python verify_submission.py
python -m pytest analytics/tests/ -q
```

Esperado: `VERIFICAÇÃO CE: APROVADA` e testes verdes.
