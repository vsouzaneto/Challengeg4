# Step 03 — Construir painel relativo ao churn sem vazamento

**Task File:** `.specs/tasks/todo/implement-ceo-answer-architecture.feature.md` (raiz da solução; acompanhar o mesmo basename quando movida de status).
**Phase:** 1 — Base analítica verificável.
**Model:** opus.
**Agent:** general:opus.
**Depends on:** 01.
**Parallel with:** 02.
**Note:** Caminhos relativos a `submissions/luis-roquette/solution/001-churn/`. Opus pela integridade temporal e seleção retrospectiva. Ownership: `src/ravenstack_churn/panel.py` e `tests/test_panel.py`; não editar diagnosis/config/conftest nem artefatos em paralelo. Mesmas fórmulas de features, sem novo motor analítico.
**Goal:** Disponibilizar casos e controles contemporâneos nas janelas pré-evento e explicitar cobertura/reutilização.

**Interfaces:**

- Consome `select_first_terminal_events(...)`, `build_account_panel(...)` e parâmetros do Step 01.
- Produz `build_event_aligned_panel(tables: dict[str, pd.DataFrame], terminal_events: pd.DataFrame, chronology: Literal["observed", "strict"]) -> pd.DataFrame`.
- A chave de linha é `account_id/anchor_date/cohort/relative_window_start/relative_window_end/chronology`; labels e âncoras são idênticos entre cronologias.
- Step 04 agrega esse painel em `event_cohort_metrics`; nenhum consumidor usa suas linhas para scoring ou fila.

Adicionar `build_event_aligned_panel` em `panel.py`, reutilizando `build_account_panel`, `_add_usage_window`, `_add_support_window` e `_add_trends`. Seleção terminal e configuração vêm do Step 01. Produzir recortes separados de junho–novembro/2024 e do horizonte do snapshot diagnóstico. A extração local de montagem de linha é permitida para evitar produto cartesiano inútil; nenhuma cópia de fórmula ou módulo novo.

#### Expected Output

Painel de pares conta/âncora/janela/cronologia, com origem e exclusões identificáveis, casos antes do primeiro churn válido e controles observáveis no mesmo calendário. Painel mensal/contratos preexistentes continuam executáveis, com label desconhecido quando o horizonte ultrapassa `observation_end`.

#### Success Criteria

- Cutoffs `t−1/t−31/t−61` geram janelas `[-30,-1]/[-60,-31]/[-90,-61]`; feature de 90 dias é adicional e não vira repetição independente.
- Casos são cadastrados, sem churn anterior e ativos no cutoff; controles permanecem sem terminal até `t+29`, com observação completa, podendo churnar depois.
- Strict/observed usam mesmas âncoras/labels; informação posterior não entra; cobertura ausente permanece nula e reutilização é contável.
- Coortes retrospectivas não alimentam scoring ou fila; fronteiras de end para uso e estoque permanecem documentadas. Cobertura: CK-5, CK-7, CK-8, CK-11, HR-1–HR-3.

#### Subtasks

1. Ler construção de linhas/features em `panel.py` e a seleção do Step 01; listar pares necessários e regras distintas de uso `<= end` e estoque `< end`.
2. Implementar casos, controles, âncoras e exclusões para o período executivo e o recorte diagnóstico, sem relaxar horizonte quando faltar observação.
3. Reusar fórmulas para os pares elegíveis e ambas as cronologias, conservando conjunto de contas por âncora nas três janelas e ausências reais; extrair helper local somente se necessário.
4. Expor identificadores suficientes para contas distintas, participações por âncora, cobertura e controles reutilizados; manter o painel relativo fora de avaliação preditiva/scoring.
5. Escrever e executar `.venv/bin/python -m pytest -q tests/test_panel.py` no ambiente permitido: evento no dia do churn excluído, controle que churna depois do horizonte, label incompleto fora do cutoff de scoring, signup tardio, end de assinatura, dados pós-cutoff, conta reutilizada e strict/observed com mesmas âncoras.

#### Blockers & Risks

| Blocker / Risk | Impact | Likelihood | Mitigation / Resolution |
|---|---|---|---|
| Sobreviventes até fim do dataset enviesam controles | Alto | Alta | Elegibilidade só até t+29; testar controle que churna depois. |
| Informação do cancelamento entra em feature | Alto | Alta | Cutoff t−1 e testes metamórficos com registros posteriores; nenhum scoring a partir da coorte. |
| Produto cartesiano torna reprodução inviável | Médio | Média | Construir apenas pares necessários, reusar fórmula local e medir custo no ambiente autorizado. |
| Horizonte diagnóstico sem observação completa | Alto | Média | Retornar indisponibilidade e exclusões; não usar outra época como substituto temporal. |
