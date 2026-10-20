# Registro de refinamento — dashboard BI e UX

- Data/hora: 20/10/2026 (data da sessão; horário não registrado pelo ambiente)
- Objetivo: transformar a tela operacional em um dashboard mais interativo e amigável, sem alterar a política ou recalcular scores.
- Alterações: abas de visão geral/fila/detalhe; KPIs de volume, score médio, estágio, contas ausentes e cobertura; gráficos descritivos por estágio e manager; busca por oportunidade, conta, produto ou vendedor; filtros por vendedor, manager, região, estágio, produto e faixa de score; botão para limpar filtros; tabela com rótulos amigáveis e limite visual de 100 linhas; painel de interpretação do score.
- Arquivos: `app.py`, `src/filters.py` e `tests/test_filters.py`.
- Verificação: `.\\.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp-ui` terminou com `15 passed in 0.84s`.
- Limitação: a verificação automatizada da inicialização local foi iniciada, mas o comando headless permaneceu em execução até o timeout; a página online anterior estava funcional. É necessário confirmar o redeploy e revisar visualmente a nova versão publicada.
- Regra preservada: filtros só reduzem a visualização; score, posição global e explicações vêm do motor de scoring.

