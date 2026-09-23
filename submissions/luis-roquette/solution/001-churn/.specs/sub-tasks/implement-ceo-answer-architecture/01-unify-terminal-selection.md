# Step 01 — Unificar seleção terminal, qualidade e receita

**Task File:** `.specs/tasks/todo/implement-ceo-answer-architecture.feature.md` (relativo à raiz da solução; acompanhar o mesmo basename quando movida para `in-progress/` ou `done/`).
**Phase:** 1 — Base analítica verificável.
**Model:** opus.
**Agent:** general:opus.
**Depends on:** None.
**Parallel with:** None.
**Note:** Todos os caminhos deste arquivo são relativos a `submissions/luis-roquette/solution/001-churn/`. Opus por contrato compartilhado entre painel, QA e diagnóstico e integridade dos labels/MRR. Implementar somente após revisão humana da SPEC; não acionar API paga. Não congelar valores antigos produzidos por uma política incorreta.
**Goal:** Fazer todos os consumidores usarem o mesmo primeiro churn válido e distinguir receita desconhecida de zero.

**Interfaces:**

- Produz `select_first_terminal_events(accounts: pd.DataFrame, churn_events: pd.DataFrame, observation_end: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]`: eventos escolhidos e exclusões por evento/razão.
- Mantém `first_terminal_churn(churn_events: pd.DataFrame, accounts: pd.DataFrame, observation_end: pd.Timestamp) -> pd.Series`: Series indexada por `account_id`, derivada da seleção compartilhada.
- Mantém `mrr_lost_at_churn(subscriptions: pd.DataFrame, terminal_churn: pd.Series) -> pd.Series`: dtype nullable, com zero somente quando o histórico conhecido comprovar ausência de MRR ativo.
- É consumida por `build_quality_report`, `build_account_panel`, Steps 02/03 e `cli.reproduce`.

Ler a Architecture Overview e rastrear todos os callers de `first_terminal_churn` e `mrr_lost_at_churn` antes de editar. Em `src/ravenstack_churn/panel.py`, selecionar eventos válidos antes da deduplicação, retornar evento escolhido/exclusões e preservar a Series pública de datas. Adaptar `src/ravenstack_churn/quality.py`, os callers existentes em `diagnosis.py`/`cli.py` e os testes afetados sem criar uma segunda política. Em `config.py`, centralizar calendário, observação até 2024-12-31, seed 42, 2.000 réplicas e critérios já definidos na arquitetura.

#### Expected Output

Seleção compartilhada com desempate `account_id/churn_date/churn_event_id`, QA e manifesto com `first_valid_non_reactivation_event`, calendário explícito e MRR nullable no caminho existente. Testes em `tests/test_panel.py` e `tests/test_quality.py`, com ajuste estritamente necessário dos callers/fixtures já existentes. A execução legada continua possível; o Step 04 regenera os canônicos ao fechar a fase.

#### Success Criteria

- Evento anterior ao signup seguido de válido escolhe o válido, conserva risco até ele e usa seu motivo; flag de reativação ausente não vira terminal.
- QA, painel e metadados do manifesto concordam; contagens de anomalias brutas não desaparecem.
- Assinaturas distintas ativas no dia anterior são somadas uma vez; histórico desconhecido não vira zero; reativação não abre episódio novo.
- Regressões direcionadas passam no ambiente permitido; nenhum caller usa assinatura antiga nem números de referência impostos. Cobertura: CK-2, CK-3, CK-8, CK-11, HR-2, HR-3.

#### Subtasks

1. Inspecionar código/callers, estado Git, contratos de origem e parâmetros de `config.py`; preservar trabalho paralelo e registrar hashes dos cinco CSVs.
2. Implementar seleção valid-before-first em `panel.py`, exclusões por razão e adaptação de `first_terminal_churn`, sem duplicar fórmulas nem usar evento inválido como label.
3. Migrar `quality.py` e todos os callers existentes; propagar a mesma `label_policy` ao manifesto no caminho existente de `publish.py`; manter contagens brutas e imports sem ciclo.
4. Corrigir `mrr_lost_at_churn` e consumidores para valores desconhecidos/zero conhecido, limites de assinatura e deduplicação; centralizar somente os parâmetros aprovados.
5. Escrever regressões em `tests/test_panel.py`/`tests/test_quality.py`: inválido→válido, invalid-only com flag de churn, empate, reativação/flag nula, data desconhecida/fora do limite, MRR desconhecido/zero; executar `.venv/bin/python -m pytest -q tests/test_panel.py tests/test_quality.py` no ambiente autorizado e registrar resultado.

#### Blockers & Risks

| Blocker / Risk | Impact | Likelihood | Mitigation / Resolution |
|---|---|---|---|
| Caller mantém assinatura/política antiga | Alto | Alta | Buscar todos os usos antes e depois; migrar em um único step e testar igualdade QA/painel/manifesto. |
| Regeneração muda resultados antigos legítimos | Alto | Alta | Registrar deltas e causas; não ajustar valores à referência; Step 04 fecha os canônicos. |
| MRR desconhecido provoca fillna(0) downstream | Alto | Média | Traçar consumidores e testar conhecido versus desconhecido; conservar estado parcial. |
| Ambiente sem runtime autorizado | Alto | Média | Preparar diff e testes; executar apenas no ambiente permitido com commit/diff comprovado; não substituir gate. |
