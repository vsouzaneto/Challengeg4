# Fase 3 — arquitetura da resposta ao CEO

2026-09-22. Planejamento somente. Task: `../tasks/draft/implement-ceo-answer-architecture.feature.md`. Base: análise de impacto, skill local `../../.claude/skills/answer-first-churn/SKILL.md` e leitura de `config.py`, `contracts.py`, `panel.py`, `diagnosis.py`, `cli.py`, `publish.py`, abertura de `app.py`, Makefile e testes existentes de painel/diagnóstico/publicação.

## Constatações verificadas

- `first_terminal_churn` agrega a menor data antes de considerar signup; `_reason_corroborates` faz outra seleção independente. A seleção comum precisa filtrar eventos inválidos antes da deduplicação, preservando um evento válido posterior.
- Os labels de 30 dias do painel não representam meses calendário. O histórico executivo exige denominadores próprios, sem reinterpretar esses labels.
- `AnalysisResult` e `publish_artifacts` já concentram a publicação. O relatório e o app escolhem conclusões separadamente; uma resposta JSON construída uma vez elimina essa duplicação.
- O manifesto atual protege arquivos individualmente, sem transação do conjunto nem snapshot de leitura. A arquitetura explicita publicação offline, um escritor e nenhum leitor durante a substituição.
- Os gates atuais exigem estabilidade de coeficiente de até 25%, cobertura de 70%, 30 contas expostas, 10 churns e corroboração de motivos de pelo menos 1,25×. São limites a preservar; ausência de suporte não é contraevidência de efeito nulo.

## Decisões para a SPEC

Arquitetura A; quatro tabelas analíticas novas e `ceo_answer.json`; nenhum módulo ou dependência nova. Histórico primário de contas cadastradas em risco no começo do mês; universo financeiro publicado com cobertura. Coortes relativas retrospectivas com controles nas mesmas datas e reamostragem por conta. Strict é a leitura principal; observed é sensibilidade explícita. A fila continua limitada a findings aceitos, agora também condicionados aos critérios temporais documentados, sem promoção por MRR.

Os contratos na task incluem tipos/nulos, referências, unidades, comparadores e incerteza. A SPEC preserva Description e Acceptance Criteria. Nenhum teste, reprodução, app, push ou deploy foi executado nesta fase; a revisão humana da SPEC continua anterior à implementação.

Correções do judge: QA passa a usar a mesma seleção válida para divergências de flags e publica `label_policy=first_valid_non_reactivation_event`, com regressão invalid-only→valid em `tests/test_quality.py`; anomalias brutas continuam contadas. Satisfação usa respostas como pesos dentro de cada âncora e quantidade de casos elegíveis como pesos entre âncoras comuns às coortes, com fixture manual 1,4/4 e pesos 1:3 → 3,35. Escopo esperado atualizado para 15 arquivos de código/testes/documentação; somente a SPEC e este scratchpad foram editados.
