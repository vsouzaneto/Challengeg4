# 01 — Ambiente e prova mínima persistida

**Task File:** ../../tasks/done/implement-support-decision-copilot.feature.md
**Phase:** 1
**Model:** sonnet
**Agent:** sdd:developer
**Depends on:** None
**Parallel with:** None
**Note:** Execução exige a aprovação humana da SPEC já registrada; este arquivo não a concede. Caminhos abaixo relativos a `submissions/luis-roquette/solution/002-support/`. Tier typical: prova delimitada com contratos estabelecidos.
**Goal:** Tornar o pacote instalável e comprovar o fluxo mínimo Streamlit/SQLite/download antes de fixar dependências.

Ler a pesquisa `../../research/002-support.md`, o template oficial e a skill `.claude/skills/offline-support-decision-copilot/SKILL.md`. Confirmar os três candidatos existentes e usar a menor prova do selecionado. A prova é sintética, identificada como tal, sem dados pessoais nem alegação de desempenho real. Não implementar o domínio nesta etapa.

#### Expected Output

`pyproject.toml`, `requirements.lock`, `Makefile`, `.streamlit/config.toml`, `src/support_copilot/__init__.py`, `app.py` e prova em `tests/test_workflow.py`; `.gitignore` local cobre raw/artifacts/.venv/caches/runtime/scratchpad. Pesquisa registra versões realmente reproduzidas. README técnico inicial informa preparo e comandos já existentes.

#### Success Criteria

Instalação limpa encontra `support_copilot`; `make doctor`, `make lint`, `make test` e `make demo` têm comportamento real e exit status preservado. Navegação, formulário editado, transação, nova conexão e download são comprovados; arquivo baixado coincide com o persistido. Gate ainda inexistente falha explicitamente, sem placeholder que retorna sucesso. Nenhuma chamada de API paga.

#### Subtasks

1. Conferir aprovação, pesquisa, regras locais e ausência/presença de workflows; registrar início em `../../process-log/002-support.md`.
2. Criar package discovery e ambiente Python 3.12; instalar/reproduzir via `codespace-manager` com SHA/diff exato; fixar versões só após compatibilidade comprovada.
3. Implementar `app.py` de prova com controles nativos, SQLite temporário e CSV, e configurar Streamlit para não depender de serviços externos no uso normal.
4. Escrever os próprios testes em `tests/test_workflow.py` para import, navegação/formulário e leitura por nova conexão; capturar download real, sem confiar só em HTTP 200.
5. Consolidar Makefile/ignore/README inicial e registrar comandos, versões, erros e resultados; não iniciar treino, abrir teste real ou publicar evidência sintética como entrega.

#### Blockers & Risks

| Tipo | Situação | Impact | Likelihood | Resolução ou mitigação |
|---|---|---|---|---|
| Blocker | Aprovação humana da SPEC ausente | High | Medium | Parar execução e solicitar somente a aprovação; nenhum scaffolding antes dela. |
| Risk | API de navegação/AppTest incompatível com lock | Medium | Medium | Provar interação inteira antes de expandir; corrigir seleção/lock e repetir prova. |
| Risk | Instalação sem package discovery ou falha mascarada por cleanup | Medium | Medium | Testar import limpo e preservar exit status independente do encerramento do servidor. |
