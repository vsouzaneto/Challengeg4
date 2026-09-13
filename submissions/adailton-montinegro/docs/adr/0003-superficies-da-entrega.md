# ADR 0003 — Superfícies da entrega

## Contexto

O desafio aceita formatos livres, mas precisa ser compreendido rapidamente por um CEO e também demonstrar uma solução funcional. Uma aplicação isolada pode falhar no ambiente do avaliador; um relatório isolado não oferece exploração, filtros ou uma fila operacional de risco.

Manter análises independentes em cada formato criaria risco de números divergentes.

## Decisão

1. Entregar uma aplicação Streamlit como superfície interativa.
2. Entregar um relatório executivo em PDF como artefato canônico e avaliável sem execução de código.
3. Manter um gerador versionado e executável para o PDF, acompanhado por uma narrativa editorial em Markdown.
4. Gerar os números e gráficos de ambas as superfícies a partir das mesmas tabelas gold e do mesmo catálogo de métricas.
5. Registrar no PDF a versão dos dados, a data de corte, o universo, a cobertura e o estado de confiabilidade das métricas.
6. Usar o Streamlit para filtros, drill-down, tabela de contas e cenários que não cabem no PDF.
7. Usar o PDF para síntese executiva, evidências principais, recomendações priorizadas e limitações.

## Alternativas rejeitadas

- **Somente Streamlit:** aumenta o risco de a análise não ser avaliada por falha de ambiente ou dependência de rede.
- **Somente PDF:** não entrega a ferramenta explorável e operacional solicitada.
- **Análises separadas por formato:** duplica lógica e permite resultados incompatíveis.
- **Notebook como entrega principal:** comunica pior para o público executivo e não substitui a experiência interativa.

## Consequências

- Métricas e gráficos reutilizáveis precisam ser separados da camada de apresentação.
- O pipeline deve exportar datasets ou consultas estáveis para geração do relatório.
- A validação final deve reconciliar cards e gráficos equivalentes entre Streamlit e PDF.
- O README da submissão deverá oferecer uma leitura rápida e instruções de execução do app.

## Status

Aceita pelo autor da submissão em 2026-09-12.
