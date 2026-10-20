# Registro de etapa — M5: testes e validação integrada

- Data/hora: 20/10/2026 (data da sessão; horário não registrado pelo ambiente)
- Módulo e objetivo: M5 — validar integração de ingestão, análise, scoring, filtros e execução do Streamlit.
- Ferramenta/modelo efetivamente utilizado: Codex via ferramentas locais e navegador conectado.
- Prompt enviado (texto ou caminho da evidência): instruções do usuário e `prompts/05-M5-validacao.md`.
- Comandos de verificação realmente executados:
  - `.\\.venv\\Scripts\\python.exe -m pytest -q`;
  - `.\\.venv\\Scripts\\python.exe -m pytest -q --basetemp .pytest-tmp-m5`;
  - `.\\.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp-m5-clean`;
  - validação integrada real com ingestão, scoring e filtros;
  - requisição HTTP para a URL publicada do Streamlit;
  - execução headless local do Streamlit na porta 8502.
- Falha encontrada e correção: a primeira suíte teve 11 passes e 3 erros por `PermissionError` no diretório temporário padrão `AppData\\Local\\Temp\\pytest-of-fnava`. A suíte foi repetida com basetemp dentro do projeto e terminou com `14 passed in 0.82s`; sem cacheprovider não houve warning.
- Saídas integradas observadas: 2.089 deals abertos; scores entre 40 e 70; scores finitos; 79 linhas após filtro combinado; score invariável sob filtro; política usa somente `deal_stage` como campo ponderado; 1.588 linhas possuem avisos de dados ausentes; nenhum deal descartado.
- Comparações de ranking: a ordem do score não é igual à ordem pura por preço (`2.069` posições diferentes em 2.089). A política mantém Engaging acima de Prospecting e usa preço somente como desempate dentro do mesmo score; isso não comprova ganho de conversão.
- Streamlit: URL publicada respondeu HTTP 200 e a revisão visual confirmou título, resumo, 2.089 deals, filtros, tabela priorizada, conta ausente, detalhe, fatores e avisos.
- Critérios de aceite: AC01–AC09 marcados após verificações reais em `docs/ACEITE.md`; AC10 permanece pendente para M6.
- Limitações: não foi feita validação comercial com vendedores; a UI/UX ainda pode ser refinada; o app continua baseado em CSVs históricos offline.
- Próximo módulo: M6 — documentação final e submissão; requer revisão dos artefatos finais antes de qualquer PR.

