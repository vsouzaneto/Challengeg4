# Step 02 — Calcular histórico, segmentos e motivos

**Task File:** `.specs/tasks/todo/implement-ceo-answer-architecture.feature.md` (raiz da solução; acompanhar o mesmo basename quando movida de status).
**Phase:** 1 — Base analítica verificável.
**Model:** opus.
**Agent:** general:opus.
**Depends on:** 01.
**Parallel with:** 03.
**Note:** Caminhos relativos a `submissions/luis-roquette/solution/001-churn/`. Opus por integridade de denominadores, receita e reamostragem por conta. Ownership: `src/ravenstack_churn/diagnosis.py` e `tests/test_diagnosis.py`; não editar panel/config/conftest nem artefatos em paralelo. Fixtures específicas ficam neste arquivo de teste até integração.
**Goal:** Produzir fatos históricos auditáveis sobre mudança de churn, exposição econômica, segmentos e motivos.

**Interfaces:**

- Consome `select_first_terminal_events(...)` do Step 01 e os parâmetros versionados de `config.py`.
- Produz `build_monthly_churn(tables: dict[str, pd.DataFrame], terminal_events: pd.DataFrame) -> pd.DataFrame` com o schema de `monthly_churn.csv`.
- Produz `build_reason_distribution(tables: dict[str, pd.DataFrame], terminal_events: pd.DataFrame) -> pd.DataFrame` com o schema de `reason_distribution.csv`.
- Step 04 consome ambos os DataFrames; Step 05 apenas os serializa, sem recalcular métricas.

Adicionar `build_monthly_churn` e `build_reason_distribution` em `diagnosis.py`, consumindo seleção terminal/configuração do Step 01. Cumprir os contratos completos da Architecture Overview para `monthly_churn.csv` e `reason_distribution.csv`, inclusive chaves com `comparison_kind`, comparadores, fontes e nulos; neste step as funções são testáveis diretamente, sem publicar novos payloads. Reusar dimensões de `_segment_metrics`, helpers existentes e dependências instaladas.

#### Expected Output

DataFrames determinísticos com schemas/cabeçalhos mesmo vazios, chaves naturais, taxa mensal e agregada por exposição conta-mês, volume/MRR e comparadores disjuntos. Distribuição de motivos separa períodos e população/horizonte diagnóstico; não usa eventos inválidos nem toda a história como corroboração contemporânea.

#### Success Criteria

- População `registered_at_start`, churns elegíveis, entrantes e exclusões reconciliam; meses usam calendário, não soma de labels de 30 dias.
- Wilson mensal e bootstrap por conta nos contrastes seguem parâmetros/limites definidos; IC/razão inválidos ficam indisponíveis com causa.
- Segmentos usam complemento; elegibilidade 30 contas/10 churns e IC do RR acima de 1 precedem destaque de excesso de risco.
- MRR distingue soma conhecida/parcial de estoque exposto, USD e deduplicação; não soma estoques mensais nem dimensões sobrepostas. Cobertura: CK-2–CK-4, CK-6, CK-8, CK-11, HR-1, HR-3.

#### Subtasks

1. Ler `diagnosis.py`, contratos de `monthly_churn`/`reason_distribution`, seleção do Step 01 e `_segment_metrics`; definir interfaces locais concretas sem módulo novo.
2. Implementar série abril/2023–novembro/2024 e comparação julho–dezembro/2023 versus junho–novembro/2024, contabilizando entrantes, exclusões e mês incompleto conforme a arquitetura.
3. Calcular segmentos versus complemento, intervalos, receita conhecida/desconhecida e estoque; usar bootstrap com conta inteira e sorteio comum nos períodos, 95% de réplicas válidas e guardas para amostra/denominador.
4. Produzir distribuição de motivos do primeiro terminal válido, unknown explícito e janelas/populações separadas, com referências únicas e limites financeiros.
5. Escrever e executar `.venv/bin/python -m pytest -q tests/test_diagnosis.py` no ambiente permitido: taxas ponderadas distintas de médias simples, fevereiro/dia 31, entradas/reativação, zero denominador, amostra pequena, bootstrap determinístico, segmento grande sem excesso, receita parcial e motivo fora da janela. Conferir referências exploratórias como comparação, nunca golden value.

#### Blockers & Risks

| Blocker / Risk | Impact | Likelihood | Mitigation / Resolution |
|---|---|---|---|
| Tratar conta-mês repetida como independente | Alto | Alta | Reamostrar conta com todos os meses e o mesmo sorteio nos contrastes; fixture distingue erros de ponderação. |
| Receita inflada por assinatura/dimensão/estoque repetido | Alto | Média | Chave de assinatura/conta explícita; testes de sobreposição e estoque agregado null. |
| Eventos fora do horizonte corroboram mecanismo | Alto | Alta | Filtrar período/população antes de agrupar motivos e preservar denominadores/exclusões. |
| Conflito com trabalho paralelo | Médio | Média | Step 03 possui panel/test_panel; nenhuma edição compartilhada; Step 04 integra ambos. |
