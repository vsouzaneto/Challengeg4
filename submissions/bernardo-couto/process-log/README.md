# Process log — índice de evidências

Como a IA foi usada para construir o Lead Scorer, com evidências verificáveis dentro do repositório.

| Evidência | Onde | O que mostra |
|---|---|---|
| Narrativa cronológica | [`01-narrativa.md`](./01-narrativa.md) | Cinco sessões: pedido, decomposição, onde a IA entrou, o que o humano decidiu; a sessão 5 lista cada agente da onda de construção com o que entregou |
| Erros da IA e correções | [`02-erros-da-ia.md`](./02-erros-da-ia.md) | Erros pegos por verificação ou pelo Bernardo (E1–E7, E9–E11) e uma objeção técnica decidida pelo humano (E8), com correção e evidência |
| Decision log | [`decisions.md`](./decisions.md) | Decisões datadas com alternativas descartadas e impacto; entradas `erro-ia` e `insight` em destaque |
| Chat exports | [`chat-exports/`](./chat-exports/) | Três transcrições (prompts, respostas, ferramentas e resultados; raciocínio interno não exportado): sessões 1–4 (setup, correções, produto, process log), sessão 5 (construção) e sessão 6 (fechamento e PR). Blocos que casam com `tools/filter-patterns.txt` não são exportados |
| Exportador | [`tools/export_claude_session.py`](./tools/export_claude_session.py) | Gera os chat exports a partir do JSONL da sessão, com filtro de padrões sensíveis (`tools/filter-patterns.txt`) e recorte por `--since/--until` para separar sessões gravadas no mesmo arquivo |
| Screenshots do app | [`screenshots/`](./screenshots/) | 6 telas capturadas por `npm run screenshots:real` (Playwright) **contra a API real** (`as_of=2017-12-31`, modelo `2017-12-31-rules-v1`): `web-fila`, `web-fila-drawer`, `web-fila-confirmar`, `web-time`, `web-qualidade`, `web-estado-vazio`. `web-estado-artefatos` (503, artefatos ausentes) só existe em modo demonstração (`npm run screenshots`) |
| Hipóteses antes da análise | `../solution/pipeline/analysis/00_hypotheses.md` (resumo no site de docs, página "Hipóteses e vereditos") | 11 hipóteses com critério de refutação escritas antes de rodar qualquer script; 7 refutadas; texto original intacto |
| Configuração do Claude Code | [`../.claude/`](../.claude/) e [`../CLAUDE.md`](../CLAUDE.md) | 15 agentes, 9 skills, 6 hooks — o "sistema" de trabalho, versionado |
| Arquitetura do time de agentes | [`../docs/agents-architecture.md`](../docs/agents-architecture.md) | Quem faz o quê, fluxo (Mermaid) e por que cada guardrail existe |
| ADRs | [`../docs/adr/`](../docs/adr/) | 7 decisões estruturais com alternativas e consequências |
| Artefatos gerados por código | `../solution/models/2017-12-31-rules-v1/`, `../solution/data/gold/scores/as_of=2017-12-31/_manifest.json` | Model card, métricas de backtest, manifesto com git sha, checksums e contagens — a origem de todo número citado no README |
| Documentação navegável | `../solution/docs-site/` → http://localhost:8001 | Todos os documentos acima em HTML, com Mermaid e Swagger |
| Git history | `git log --oneline -- submissions/bernardo-couto` | Evolução em commits pequenos na branch `submission/bernardo-couto` (staging via `../tools/git-stage.sh`) |

Ferramentas: Claude Code (Fable 5.1) com subagents, skills e hooks; uv; PySpark; FastAPI; React; Docker; MkDocs; Playwright.
