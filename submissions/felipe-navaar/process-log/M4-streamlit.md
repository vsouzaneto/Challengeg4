# Registro de etapa — M4: interface e filtros

- Data/hora: 20/10/2026 (data da sessão; horário não registrado pelo ambiente)
- Módulo e objetivo: M4 — disponibilizar fila interativa offline com filtros combináveis, explicação do score e estados de erro/vazio.
- Ferramenta/modelo efetivamente utilizado: Codex via ferramentas locais; edição por patch.
- Prompt enviado (texto ou caminho da evidência): instruções do usuário e `prompts/04-M4-streamlit.md`.
- Resultado produzido / arquivos alterados: `app.py`, `src/filters.py`, `tests/test_filters.py` e este registro.
- Escopo implementado: filtros por vendedor, manager e região; fila somente com abertos; conta ausente legível; tabela com posição global, score e preço de referência; detalhes com fatores, avisos, política e data de referência. O filtro não recalcula nem renumera o score.
- Comandos de verificação realmente executados: `.\\.venv\\Scripts\\python.exe -m pytest -q`; `.\\.venv\\Scripts\\python.exe -m streamlit run app.py --server.headless true --server.port 8501 --browser.gatherUsageStats false`.
- Saídas observadas: pytest terminou com `14 passed in 1.31s`. O Streamlit exibiu `You can now view your Streamlit app in your browser`, Local URL `http://localhost:8501` e `Uvicorn server started on :::8501`. A execução foi encerrada pelo timeout do comando após confirmar a inicialização.
- Verificação visual: não realizada; não há navegador visual disponível nesta sessão.
- Limitações: aplicação ainda é uma demonstração offline local; não há CRM, API externa, autenticação ou publicação.
- Próximo módulo: M5 — testes e validação integrada.
