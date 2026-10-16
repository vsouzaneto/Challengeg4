# Conformidade CE e abertura de PR

Meta: **consistentemente excede (CE)** nos critérios obrigatórios do Challenge 001, com gate automático antes do PR.

Metodologia e arquitetura: [`METODOLOGIA.md`](./METODOLOGIA.md).

---

## Rubrica autoteste (G4)

| Critério | Nível | Evidência |
|----------|-------|-----------|
| 5 tabelas integradas | CE | `integration_qa.csv`, `METODOLOGIA.md` §4 |
| Insights verificáveis | CE | `executive_summary.md`, `summary_stats.json`, figuras |
| Recomendações + impacto MRR | CE | `recommendations_impact.csv`, playbook, fila top 50 |
| Causalidade honesta | CE | `causality_register.md`, AUC ~0,62 documentado |
| CEO 5 min | CE | `ceo_one_pager.md` + Command Center |
| Process log | CE | `process-log/` |
| Superar baseline IA | CE | Tese revolving + audit 166 PRs |
| Dashboard + CS operável | CE | React + playbook + XLSX/CSV fila |
| Reprodutibilidade | CE | `run_analysis.py`, pytest, `verify_submission.py` |
| PR só `submissions/felipe/` | CE | Escopo do commit |

**Autoteste local:** `verify_submission.py` OK · pytest verde · PR #198 · escopo só `submissions/felipe/`.

**Autoavaliação rubrica (candidato):** **10/10** nos critérios obrigatórios Challenge 001 + process log combinado; nota oficial = avaliação G4.

---

## Regras G4 → evidência (resumo)

| Regra | Evidência |
|-------|-----------|
| IA + como usou | `process-log/`, README § Process Log |
| Template README | `README.md` |
| Setup | `requirements.txt`, `start.bat` |
| 3 perguntas do brief | `executive_summary.md` + `METODOLOGIA.md` §3 |

Autoteste rápido (Windows): `submissions\felipe\start.bat` · gate: `python verify_submission.py` em `solution/`

---

## Checklist antes do PR

- [ ] CSVs em `data/` (Kaggle ou manual)
- [ ] `start.bat` ou pipeline manual OK
- [ ] `verify_submission.py` → **APROVADA**
- [ ] `pytest analytics/tests/` verde
- [ ] LinkedIn no README
- [ ] Commit **apenas** `submissions/felipe/`
- [ ] Apagar cópia `submissions/felip/` no disco, se existir
- [ ] Fork + branch + push

**Título:** `[Submission] Felipe de Lima Santiago — Challenge 001`

```bash
git checkout -b submission/felipe-santiago
git add -f submissions/felipe
git commit -m "Submission Challenge 001 — RavenStack churn diagnosis"
git push -u origin submission/felipe-santiago
gh pr create --repo Gestao-Quatro-Ponto-Zero/ai-master-challenge \
  --title "[Submission] Felipe de Lima Santiago — Challenge 001" \
  --body-file submissions/felipe/docs/PR-BODY.md
```

Corpo sugerido do PR: [`PR-BODY.md`](./PR-BODY.md).
