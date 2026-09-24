---
name: pr-check
description: Checklist final antes de abrir ou atualizar o Pull Request da submissão do G4 — escopo de arquivos, armadilha do .gitignore, testes, lint, checksums dos dados, README no template, process log presente, título do PR. Use quando o Bernardo pedir `/pr-check` ou antes de qualquer `git push` da branch de submissão.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash(git *), Bash(uv *), Bash(uvx *), Bash(make *), Bash(docker compose *), Bash(docker run *), Bash(curl *), Bash(shasum *), Bash(ls *), Bash(wc *), Bash(/usr/libexec/java_home *)
---

Execute o checklist abaixo **rodando cada comando** e reporte uma tabela `item · PASS/FAIL · evidência`. Não marque PASS sem saída de comando. Não corrija nada silenciosamente: liste as correções necessárias no final e aplique só as triviais (formatação, `git add -f`).

Estado atual:
```!
cd "${CLAUDE_PROJECT_DIR}/../.." && git branch --show-current && git status --short --ignored -- submissions/bernardo-couto | head -40 && echo "--- arquivos alterados fora da pasta de submissão (deve ser vazio):" && git diff --name-only origin/main...HEAD 2>/dev/null | grep -v '^submissions/bernardo-couto/' || true
```

## Itens

1. **Branch** é `submission/bernardo-couto`.
2. **Escopo**: `git diff --name-only origin/main...HEAD | grep -v '^submissions/bernardo-couto/'` retorna vazio.
3. **Staging seguro**: `bash tools/git-stage.sh` (nunca `git add -f` direto) e a saída mostra `generated: 0 · outside submission folder: 0`. Conferir `git diff --cached --stat | tail -1` (centenas de arquivos, não dezenas de milhares).
4. **Dados raw íntegros**: `cd solution/data/raw && shasum -a 256 -c SHA256SUMS`.
5. **Testes**: `cd solution && make test` verde (pipeline pytest, api pytest, web vitest).
6. **Lint**: `make lint` (ruff + mypy no Python; eslint + tsc no TS) limpo.
7. **Entrega sobe do zero**: `cd solution && docker compose build && docker compose up -d`; `curl -f localhost:8000/health`; `curl -sf localhost:8000/openapi.json | uvx openapi-spec-validator -`; `curl -sf localhost:5173 | grep -qi lead`; `curl -sf localhost:8001 | grep -qi documenta`; `docker compose down`. Imagens `api` e `web` não contêm pyspark (`docker run --rm <img> python -c "import pyspark"` deve falhar).
7b. **Docs**: `cd solution/docs-site && uv run mkdocs build --strict` sem avisos; diagramas em Mermaid (nenhum bloco ASCII de arquitetura em `docs/`).
8. **README da submissão** existe, segue as seções do `../../templates/submission-template.md` (Sobre mim, Executive Summary, Solução, Process Log, Evidências) e não tem `TODO` pendente.
9. **Process log**: `process-log/decisions.md` tem ≥1 entrada do tipo `erro-ia`; `process-log/README.md` indexa evidências; `process-log/screenshots/` não está vazio.
10. **Docs**: `solution/README.md` (setup), `docs/scoring-logic.md`, `docs/ml-pipeline.md`, `docs/data-quality-report.md`, `docs/limitations.md` existem.
11. **Segredos**: `grep -rEl "(api[_-]?key|secret|token|password|KAGGLE_KEY)" --include=*.py --include=*.toml --include=*.md --include=*.json . | grep -v node_modules` retorna vazio ou só falsos positivos justificados.
12. **Sem relógio nem split aleatório**: `grep -rnE "\.now\(\)|today\(\)|current_date|current_timestamp|randomSplit|CrossValidator|TrainValidationSplit" solution/src solution/app` vazio (ou só linhas com `# leakage-ok`).
13. **JDK**: `/usr/libexec/java_home -v 21` ou `-v 17` existe; README explica `JAVA_HOME`; `uv run python -c "from lead_scorer.spark import get_spark; get_spark('prcheck', for_tests=True).stop()"` funciona.
14. **Jobs reexecutáveis**: `uv run python -m lead_scorer.jobs.score --as-of 2017-12-31` roda duas vezes sem duplicar linhas; `manifest.json` presente.
15. **Modelo versionado**: `solution/models/latest` aponta para uma pasta com `model_card.md`, `metrics.json`, `feature_list.json`.
16. **Dependências**: `uv lock --check` ok; `uvx pip-audit -r <(cd solution && uv export --no-hashes --no-emit-project)` sem vulnerabilidades altas (ou justificadas em `docs/security-review.md`).
17. **Segurança**: `docs/security-review.md` existe e seus achados críticos estão fechados.
18. **Título do PR** planejado: `[Submission] Bernardo Couto — Challenge 003`. Corpo termina com a atribuição do Claude Code.

Argumentos: `$ARGUMENTS`
