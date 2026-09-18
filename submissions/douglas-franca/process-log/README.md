# Process Log: índice de evidências

Evidências de como a IA foi usada, organizadas por gate. Tudo em texto (Markdown) ou PNG.

| Pasta/arquivo | Conteúdo |
|---|---|
| `decisions.md` | Decisões humanas por gate (fonte da seção "O que eu adicionei") |
| `ai-errors.md` | Onde a IA errou, como foi detectado e como foi corrigido |
| `baseline/` | Respostas literais de IAs ao brief colado sem contexto (G1) |
| `critique/` | Críticas adversariais multi-modelo + síntese (G8) |
| `chat-exports/` | Transcripts das sessões em Markdown |
| `screenshots/` | Prints nomeados `gN-descricao.png` |

## Sessão 0: leitura do repositório
Antes de construir, li o brief, o guia de submissão e as submissões públicas do repositório. O objetivo era entender o critério de qualidade e o que já tinha sido entregue no Challenge 004, para não repetir o que já existe. Nenhum conteúdo de outras submissões foi copiado.
Transcript da sessão inteira (G0 a G8): `chat-exports/sessao-claude-code-g0-a-g8.md`.

## Linha do tempo por gate
Os gates de análise, processo, estratégia, ferramenta e crítica (G1–G6, G8) fecham com decisões minhas registradas em `decisions.md` (17 linhas); G0 (setup) e G7 (evidências) são etapas operacionais. Os erros da IA de cada gate estão em `ai-errors.md`, com a coluna "Gate".

| Gate | Data | Commits | Minha decisão que fechou o gate | Evidências |
|---|---|---|---|---|
| G0 Setup | 2026-09-16 | `14e3e7f` | — (etapa operacional) | estrutura, 8 agentes (`.claude/agents/`), permissões que bloqueiam `gh pr create` para a IA |
| G1 Baseline | 2026-09-16 | `f94b3ec`, `04dfa71` | Tese do diferencial em minhas palavras; Bilibili e RedNote só como referência | `baseline/` (5 IAs), `screenshots/g1-*` (46 prints), `outputs/tables/g1-baseline-claims-check.csv`, `docs/differentiation-rubric.md` |
| G2 Auditoria | 2026-09-16 | `aa3e2e1` | O achado principal é o mecanismo (dados sorteados); as perguntas do Head são respondidas dentro dessa moldura | `docs/data-quality-report.md`, `outputs/tables/dq-*.csv`, `docs/gap-to-process-map.md` |
| G3 Análise | 2026-09-16 | `d57bd4d` | Régua de ±1 p.p. na taxa de engajamento, definida **antes** dos testes | `docs/statistical-report.md`, `outputs/tables/inf-*.csv`, `outputs/figures/g3-*.png` |
| G4 Processo | 2026-09-16 | `a6a6f7a` | Como a operação funciona hoje (minha vivência); os dois fluxos do brief com o mesmo peso; divisão IA × humano | `docs/process/01` a `07`, `outputs/figures/g4-*.png` |
| G5 Estratégia | 2026-09-16 | `c0bb778` | Estratégia aprovada; preços de mercado para o custo implícito (pesquisa minha, com fontes) | `reports/strategy.md`, `outputs/tables/str-*.csv`, `tests/test_rules.py` |
| G6 Ferramenta | 2026-09-16/17 | `07e8a90`, `c71f65f` | Escopo em 4 telas, sem IA generativa; publicar online | `app/`, `tests/`, `outputs/figures/app/`, app no ar |
| G7 Evidências | 2026-09-17 | `1e7c507` … `df2f903` | — (etapa operacional) | `README.md`, `reports/executive-one-pager.md`, `screenshots/` |
| G8 Crítica | 2026-09-18 | `8cd775c`, `c976a8e`, … | README abre pelo processo; suspensão de patrocínio vira regra de entrada; processo atual vira premissa a validar | `reports/review-verdict-round1.md`, `critique/critique-synthesis.md` |
