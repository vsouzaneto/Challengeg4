# Registro de incremento visual — dashboard BI

- Data: 20/10/2026.
- Objetivo: tornar o dashboard mais executivo e explorável, mantendo os dados reais e a política `heuristic-v1` intactos.
- Alterações: tema visual com cabeçalho e cards; gráficos interativos Plotly para estágio, região, managers e produtos; guia visual de prioridade na fila; download do recorte filtrado em CSV; ficha do deal com medidor, decomposição do score e avisos; aba de cobertura dos campos de dados.
- Dependência adicionada: `plotly==7.1.0` instalado no ambiente local e incluído em `requirements.txt`.
- Verificação: `.\\.venv\\Scripts\\python.exe -m compileall -q app.py src` e `.\\.venv\\Scripts\\python.exe -m pytest -q -p no:cacheprovider --basetemp .pytest-tmp-visual` terminaram com `15 passed in 1.11s`.
- Verificação adicional: `.\\.venv\\Scripts\\python.exe -c "import app; print('app importado com sucesso')"` retornou `app importado com sucesso`. O Streamlit exibiu somente avisos esperados de execução fora do runtime web.
- Limitação de ambiente: a tentativa de executar um servidor Streamlit temporário na porta 8504 foi bloqueada pela política antes da inicialização; não houve saída de erro do aplicativo.
- Regra preservada: filtros e gráficos apenas apresentam subconjuntos da fila já pontuada; não recalculam score, ranking ou explicações.
