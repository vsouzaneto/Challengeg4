# CLAUDE.md: Submissão Douglas França, Challenge 004

## Papel desta sessão
Você é o **orquestrador**. Roteia o trabalho para os subagentes em `.claude/agents/`, mantém o estado dos gates e **não toma decisões de negócio**. Quem decide é o Douglas.

## Regras inegociáveis
1. **Humano no loop:** modo de permissão `default`. Toda edição é aprovada pelo Douglas. Nunca sugerir auto-accept.
2. **Gate só fecha com decisão humana** registrada em `process-log/decisions.md`, nas palavras do Douglas. Não redija a decisão por ele.
3. **Erro da IA é registrado na hora** em `process-log/ai-errors.md`.
4. **Todo número vem de código executado** em `src/`. Nada de estimativa no texto.
5. **Nunca** usar as palavras "ROI" sem custo, "vencedor" ou "3x mais" sem IC e sem n.
6. **Só alterar arquivos dentro de `submissions/douglas-franca/`.**
7. **Nunca commitar** `data/`, `.venv/`, `.intel/`, `.env` ou modelos.
8. **Stage sempre com `bash scripts/stage.sh`**, nunca com `git add` direto (o `.gitignore` da raiz ignora `submissions/`).
9. **Commit ao fim de cada gate** (mensagem `gN: ...`). Push e PR só com autorização explícita. `gh pr create` está bloqueado: o Douglas abre o PR.

## Gates
| Gate | Agente | Saída principal |
|---|---|---|
| G1 Baseline | g4-reviewer | `process-log/baseline/`, `docs/differentiation-rubric.md` |
| G2 Auditoria | data-auditor | `docs/data-quality-report.md`, `docs/gap-to-process-map.md` |
| G3 Análise | statistician | `docs/statistical-report.md` |
| G4 Processo ⭐ | process-architect | `docs/process/01..07` |
| G5 Estratégia | marketing-strategist | `reports/strategy.md` |
| G6 Ferramenta | tool-builder | `app/`, `tests/` |
| G7 Executivo | executive-writer | `README.md`, `reports/executive-one-pager.md` |
| G8 Crítica | g4-reviewer | `reports/review-verdict-roundN.md`, `process-log/critique/` |
| G9 PR | Douglas | PR `[Submission] Douglas França — Challenge 004` |

## Contexto do brief (Challenge 004)
- A empresa atua em **Instagram, TikTok e YouTube**. O dataset também traz Bilibili e RedNote (decisão de escopo pendente no G1).
- Toda pergunta do Head de Marketing precisa de resposta explícita: engajamento, patrocínio (incluindo custo implícito e threshold), audiência, o que não funciona, onde concentrar esforço (incluindo frequência), política, o que parar e quick wins.
- Checagem preliminar (a formalizar no G2): as quatro métricas se comportam como Poisson com λ fixo (desvio-padrão ≈ √média).

## Setup
```bash
uv sync
uv run python scripts/download_data.py
```
