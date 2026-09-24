# Narrativa do processo — como a IA foi usada

Cronologia por sessão. Cada item aponta para evidência (decision log, chat export, arquivos). Números vêm de saídas de comando registradas no chat export.

## Sessão 1 — 22/09/2026 (noite) · Entender antes de construir

**Pedido:** ler toda a documentação do repositório, escolher o Challenge 003 e montar um time de agentes do Claude Code com guardrails.

**Como decompus o problema antes de promptar:**
1. Ler os 9 arquivos de documentação (README raiz, índice, 4 briefs, CONTRIBUTING, guia de submissão, template, `.gitignore`) — e não só o brief do 003. Isso revelou duas armadilhas de processo: o PR só pode tocar `submissions/<nome>/` e a raiz ignora `submissions/` no `.gitignore` (exige `git add -f`).
2. Verificar sintaxe antes de escrever configuração: um subagente `claude-code-guide` confirmou na documentação oficial os campos de frontmatter de agentes e skills, o contrato JSON dos hooks e a precedência de permissões. Sem isso os arquivos teriam sido escritos "de memória".
3. Olhar os dados antes de desenhar agentes: baixei a cópia CC0 do Kaggle (endpoint público, sem credencial) e rodei um perfil com pandas.

**O que os dados mostraram e que mudou o desenho** (chat export, bloco "Profile the pipeline"): 68% dos 2.089 deals abertos sem `account`; `close_value` = 0 em todo Lost e nulo em todo aberto (leakage); snapshot em 2017-12-31; Lost com mediana de 14 dias vs. Won 57; `GTXPro` ≠ `GTX Pro`; setor `technolgy`. Cada achado virou guardrail codificado, não só texto: hook `guard_leakage.py` bloqueia `close_value`/`close_date` em features e `now()/today()` em código de solução.

**Entregas:** `CLAUDE.md`, 8 agentes, 6 skills, 6 hooks (testados com payloads simulados), `settings.json`, dados raw com `SHA256SUMS`, decision log.

## Sessão 2 — 23/09/2026 (madrugada) · Correções e Spark

**Pedido do Bernardo:** renomear agentes, criar `security-engineer`, adotar Spark para um modelo de ML "que sempre execute a classificação".

**Onde eu (IA) levantei uma objeção e como foi resolvida:** 8.800 linhas não justificam Spark por volume. Registrei a objeção e propus a justificativa honesta — Spark como pipeline operacional (bronze/silver/gold por `as_of`, modelo versionado, jobs idempotentes), com a camada de apresentação sem JVM. O Bernardo confirmou Spark como decisão de arquitetura (ADR 0001).

**Descoberta de ambiente:** o JDK padrão da máquina é o 23 (não suportado pelo Spark 3.5); existe um Corretto 21 instalado. Virou verificação no hook de sessão e regra na skill `spark-ml-practices`.

**Erro da IA corrigido:** `git mv -k` em arquivo não rastreado não faz nada e retorna 0; o rename do agente falhou silenciosamente e foi refeito com `mv` ([erros-da-ia.md](./02-erros-da-ia.md#e2)).

## Sessão 3 — 23/09/2026 (manhã) · Produto, entrega e design

**Pedido:** código em Python + React, Docker, Swagger, documentação navegável em HTML, design system do G4, diagramas em Mermaid, novos papéis de produto e liderança técnica, avaliar o Jev.

**Decisões com evidência:**
- Streamlit → FastAPI + React (ADR 0002); Docker Compose (ADR 0003); MkDocs Material (ADR 0004).
- Jev avaliado a partir do anúncio oficial e rejeitado para o scoring (ADR 0005): problema tabular supervisionado com desfechos próprios, explicabilidade exata e execução offline pesam mais.
- Tokens do design system extraídos do CSS público de g4business.com por `curl` (`#001F35`, `#B9915B`, `#F5F4F3`, Manrope, Libre Baskerville), com contraste AA calculado — não "inspirado".
- Artefatos de saída commitados para a UI abrir sem JDK (ADR 0006).

**Erro da IA corrigido:** a visão geral da arquitetura estava em ASCII e ilegível; reescrita em Mermaid. Outro: a rubrica interna inflava achados do dataset como diferenciais ([erros-da-ia.md](./02-erros-da-ia.md#e4)).

## Sessão 4 — 23/09/2026 · Process log e início do código

Exportação da transcrição desta sessão com o script [`tools/export_claude_session.py`](./tools/export_claude_session.py) (raciocínio interno não exportado). Início da construção: scaffold do monorepo pelo `tech-lead`, seguido de dados, scoring, API, web e docs.

## Sessão 5 — 23/09/2026 (11h em diante) · Construção

Onda de construção orquestrada pela sessão principal, um agente por especialidade, na ordem do fluxo do `CLAUDE.md`. Cada item cita a entrada do [decision log](./decisions.md) ou o artefato que o comprova.

| Ordem | Agente | O que entregou | Números-chave (fonte) |
|---|---|---|---|
| 1 | `tech-lead` | Scaffold do monorepo (`solution/{shared,pipeline,api,web,docs-site}`), contrato `ScoredDeal` em pacote compartilhado (ADR 0007), Compose com perfil `pipeline`, Makefile | 7 ADRs em `docs/adr/` |
| 2 | `data-engineer` | Bronze → silver → gold particionado por `as_of`, checks que falham o job, `_manifest.json` por partição, `docs/data-quality-report.md` | 8.800 deals; 2.089 abertos; 1.425 (68,2%) sem conta; conta é artefato temporal (100% dos fechados vs 32% dos abertos); 1.291 de 1.589 Engaging > 138 d (decision log 13:40 e 13:45) |
| 3 | `data-scientist` | 11 hipóteses registradas antes da análise, EDA, backtest em dois cortes com baselines e ICs, protótipo das regras, `docs/scoring-logic.md`, `docs/specs/scoring-spec.md` | 7 hipóteses refutadas; nenhum sinal bate o aleatório (AUC-ROC 0,44–0,53); `p_win` = taxa-base por produto; pesos 25/35/40 (decision log 14:30) |
| 4 | `product-designer` | `docs/design/{ux-spec,design-tokens,accessibility,review-checklist}.md`; tabela de contraste calculada | Scaffold com contraste 2,89–4,39:1 corrigido para AA (decision log 12:30) |
| 5 | `revops-engineer` | `docs/revops-review.md`: validação dos 14 reason codes, duas filas, sprint de limpeza, piloto com controle, lista "o que a ferramenta não faz" | Mediana por vendedor 12 vivos / 44 parados; 6 de 27 sem deal vivo; 561 deals / R$ 1,25 mi em 139–180 d; win rate 63% → 53% se os 1.291 virarem Lost (§7); `QUARTER_END_WINDOW` vetado (decision log 15:20) |
| 6 | `security-engineer` | `docs/security-review.md`: modelo de ameaças, auditorias, correções em nginx/Compose/`.dockerignore`/staging, hooks fail-closed | 0 críticos/altos; `pip-audit` 0 CVEs em 4 projetos; `detect-secrets` 0; contexto do docs de dezenas de MB para 378 kB (decision log 15:50) |
| 7 | `machine-learning-engineer` | Regras em Spark SQL, LR em modo sombra, jobs `train`/`score`, model card, PSI, validação linha a linha contra `ScoredDeal`, `docs/ml-pipeline.md` | LR não promovida (AUC-PR 0,628/0,582 vs 0,661/0,600); A 67 / B 516 / C 771 / D 735; Spearman 0,46; R$ 3.185.048 nominais parados; `train` 58,1 s, `score` 10,3 s (`metrics.json`, `_manifest.json`; decision log 16:40) |
| 8 | `backend-engineer` | API FastAPI em `/api/v1`: 11 rotas, filtros, `queue=work\|confirm`, `as_of`, feedback append-only, envelope de erro, headers `X-As-Of`/`X-Model-Version`, `openapi.json` exportado | `solution/api/README.md`; testes em `solution/api/tests` |
| 9 | `application-engineer` | Web React: fila Trabalhar / Confirmar ou encerrar, drawer, `/time`, `/qualidade`, estado na URL, modo mock (MSW), captura de telas com Playwright | 7 screenshots em `screenshots/` (modo demonstração) |
| 10 | `quality-engineer` · `code-reviewer` · `security-engineer` | Clean-room, `docs/code-review.md`, ajustes de setup | `docs/code-review.md` |
| 11 | `tech-writer` | README da submissão no template do G4, `docs/limitations.md`, `solution/README.md`, site MkDocs com todos os documentos, esta sessão no process log | `mkdocs build --strict` verde |

**Onde a IA errou nesta onda** (detalhe em [erros-da-ia.md](./02-erros-da-ia.md)): hipótese da conta preenchida ao longo do ciclo (refutada pelo `data-engineer`); premissas de idade e "mais novo primeiro" (refutadas pelo backtest); rótulo "Prob. de fechar" e direções +/− em reason codes sem poder preditivo (pegos pelo `revops-engineer`); hooks fail-open e `COPY . .` com `node_modules` (pegos pelo `security-engineer`); `regParam` que zerava a LR e unidades misturadas nos pesos (pegos pelo `machine-learning-engineer`).

**Decisões humanas pendentes de confirmação do Bernardo** (marcadas no decision log): padrões visuais V1–V4; vocabulário "Trabalhar" / "Confirmar ou encerrar"; troca de "Prob. de fechar" por "Fecham {p}% dos {product}"; bump de `vite`/`vitest`/`react-router-dom`; bind das portas.

## Ferramentas e para quê

| Ferramenta | Uso |
|---|---|
| Claude Code (Fable 5.1) — sessão principal | orquestração, decisões, escrita de configuração e código |
| Subagentes do Claude Code (15 papéis versionados em `.claude/agents/`; 9 skills em `.claude/skills/`) | especialização e revisão cruzada; `claude-code-guide` para verificar documentação oficial |
| Hooks do Claude Code (6 scripts) | guardrails executáveis: escopo de arquivos, comandos destrutivos, leakage, relógio real, split aleatório, quality gate |
| uv, PySpark, FastAPI, React/Vite, Docker, MkDocs, Playwright | stack da solução e captura de telas |
| curl + pandas | verificação de dados e de tokens de design na fonte |
