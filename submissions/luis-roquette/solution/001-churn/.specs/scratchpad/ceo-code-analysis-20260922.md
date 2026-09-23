# Registro de exploração — fase 2b

2026-09-22. Repositório `ai-master-challenge`, branch `submission/luis-roquette`, HEAD `517bdcff8cdff3503e83d6ba6c978b30b1ef8754`. Escopo: leitura integral dos módulos, app, testes, configuração e artefatos; nenhuma mudança de implementação.

## Evidências coletadas

- Lidos integralmente: `src/ravenstack_churn/{config,contracts,quality,panel,diagnosis,modeling,publish,cli}.py`, `app.py`, os oito arquivos em `tests/`, Makefile, pyproject, requirements, README, tema, briefing, draft da nova tarefa, SPEC anterior e trecho atual do diário. A skill `plan-task` foi consultada para o papel delimitado da fase 2b.
- Fluxo confirmado: cinco CSVs com SHA fixado → contratos/qualidade → painéis observed/strict → claims/candidatos/modelo → AnalysisResult → nove payloads + manifesto → app somente leitura.
- Não existe série mensal de churn, decomposição de motivos, painel relativo ao evento, scorecard graduado ou contrato de resposta executiva. Relatório e app calculam a síntese separadamente.
- O painel de 30 dias não deve ser tratado como mês calendário; snapshot de segmentos cobre um único corte. Corroboração de motivos não está limitada ao horizonte avaliado. `confidence=inconclusive` mistura insuficiência com contraevidência.
- A escolha da Arquitetura A e coortes relativas ao churn está registrada no diário atual. Números exploratórios do diário não foram recalculados nesta análise e não se tornam contrato numérico por repetição.

## Limites desta exploração

Somente leitura e criação deste registro e da análise. Não executei testes, reprodução, publicação, APIs pagas ou mudanças no draft. Os testes foram inspecionados; resultados anteriores do diário não são validação desta fase.
