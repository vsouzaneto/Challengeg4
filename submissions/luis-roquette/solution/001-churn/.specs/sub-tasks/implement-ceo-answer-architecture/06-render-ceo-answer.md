# Step 06 — Exibir a mesma resposta no dashboard

**Task File:** `.specs/tasks/todo/implement-ceo-answer-architecture.feature.md` (raiz da solução; acompanhar o mesmo basename quando movida de status).
**Phase:** 2 — Resposta executiva consistente.
**Model:** sonnet.
**Agent:** general:sonnet.
**Depends on:** 05.
**Parallel with:** 07.
**Note:** Caminhos relativos a `submissions/luis-roquette/solution/001-churn/`. Sonnet: renderização em `app.py` e testes locais, usando contrato fechado; não altera cálculos/contratos. Ownership: `app.py` e `tests/test_app.py`. Se contrato faltar, reportar ao dono do Step 05; não inventar default permissivo ou editar publish em paralelo.
**Goal:** Abrir o dashboard com a resposta canônica em cinco blocos e manter leitura de evidências, filtros e downloads.

**Interfaces:**

- Consome `artifacts/ceo_answer.json` somente após `validate_artifact_set(artifact_dir)` e as quatro tabelas novas pelo manifesto da mesma execução.
- Produz apenas apresentação em `app.py`; não exporta função analítica nem altera o contrato do Step 05.
- Testes usam `streamlit.testing.v1.AppTest` e fixtures completas de `tests/conftest.py`; ausência ou invalidade bloqueia renderização decisória.

Validar artefatos antes de ler `ceo_answer.json`. Renderizar headline, claims, limites e ações sem recomputar decisões; manter três abas, componentes, tema e navegação. Eliminar narrativa duplicada, tratar flat/insufficient/zero/nulo/watchlist vazia e mostrar dados strict/observed correspondentes ao filtro, sem rebatizar a resposta principal strict.

#### Expected Output

Primeira área útil mostra resposta e cinco blocos; metodologia/modelo ficam depois. Novas tabelas podem ser inspecionadas na aba Evidências com unidade/período/fontes, mantendo controles atuais. Falha de artefato mostra arquivo/causa/reprodução necessária e interrompe a leitura.

#### Success Criteria

- AppTest confirma ordem, texto, valores, IDs e ações do mesmo JSON/relatório, inclusive sem mecanismo sustentado.
- Nenhuma função analítica é chamada durante renderização; watchlist vazia não cria slider inválido; mudança de filtro troca conteúdo real.
- Ausência/tamper/schema inválido bloqueia app sem fallback antigo; zero/nulo não produz divisão inválida.
- Leitura renderizada permite localizar mudança, recorte, limite e próxima ação sem metodologia. Cobertura: CK-1, CK-5, CK-6, CK-8–CK-12, HR-1–HR-3.

#### Subtasks

1. Ler `app.py`, `tests/test_app.py` e conjunto validado do Step 05; reutilizar `section_heading`, `format_display_frame`, `render_table` e controles existentes.
2. Substituir a abertura por renderização do headline/cinco blocos/ações de `ceo_answer.json`, movendo metodologia/modelo para depois e removendo decisões duplicadas.
3. Ligar novas evidências/filtros ao conteúdo de chronology correto; tratar rótulos flat/insufficient, razões zero/nulas e watchlist vazia; preservar downloads e abas.
4. Escrever e executar `.venv/bin/python -m pytest -q tests/test_app.py` no ambiente permitido: cinco blocos nos estados accepted/inconclusive/no-data, igualdade com JSON, filtros, corrupção sem fallback e monkeypatch que falha se análise for chamada.
5. Abrir `make app` com artefatos do Step 05 já validados, inspecionar conteúdo renderizado desktop/mobile e registrar a resposta mostrada, não só HTTP 200; entregar evidência à revisão única da fase.

#### Blockers & Risks

| Blocker / Risk | Impact | Likelihood | Mitigation / Resolution |
|---|---|---|---|
| Narrativa duplicada contradiz JSON | Alto | Alta | Renderizar claims prontos; teste compara valores/texto/IDs e bloqueia chamadas analíticas. |
| Filtro altera rótulo sem alterar valores | Alto | Média | Testar datasets strict/observed divergentes e preservar identificação da resposta strict. |
| Fixture incompleta incentiva fallback silencioso | Médio | Média | Usar fixture válida do Step 05; defeito de contrato volta a seu dono, nunca inferir número faltante. |
| AppTest passa mas leitura inicial oculta resposta | Médio | Média | Inspecionar primeira tela renderizada e registrar evidência de desktop/mobile. |
