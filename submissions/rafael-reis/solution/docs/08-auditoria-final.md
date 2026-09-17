# Auditoria final de implementação

**Data:** 2026-09-16. Esta auditoria compara código, artefatos, testes e as seis specs. Um `[x]` abaixo possui evidência executável ou visual; itens incompletos permanecem abertos.

## Evidências executadas

- [x] `.venv/bin/python tests/test_data_pipeline.py` — fontes, privacidade, SQLite, modelo, splits, embeddings, FAISS, geometria e vizinhos.
- [x] `.venv/bin/python tests/test_backend.py` — validação, idempotência concorrente, CORS permitido, replay, Graph, feedback, isolamento e proveniência de sessão.
- [x] `SUPPORT_BASE_URL=http://127.0.0.1:8000 .venv/bin/python tests/test_integration.py` — API real, replay, alerta→Graph, Copilot e hashes da baseline versionada dos 13 originais.
- [x] `pnpm --dir frontend test` e `pnpm --dir frontend run build` — ROI, tipos e build Vite.
- [x] Navegador: Ticket Lab executou inferência online e abriu o mesmo ticket no Graph, com oito conexões e tabela alternativa.
- [x] Navegador: build com `VITE_API_BASE_URL=http://127.0.0.1:8001` carregou Diagnosis por API externa CORS-autorizada.
- [x] Navegador: após reinício do backend, Diagnosis DS1 e Command Center DS2 carregaram métricas reais, indisponibilidade temporal e limiar de revisão de 75%.
- [x] Navegador: O Início carregou o roteiro para leigos, a narrativa técnica em primeira pessoa e o comando local; Graph overview exibiu relações agregadas e o indicador textual do pulso neon sobre arestas reais.
- [x] Navegador: Graph exibiu 28 halos neon; selecionar um grupo deixou 27 nós/arestas inativos e o segundo clique restaurou a rede e o painel inicial, sem erros de console.
- [x] Navegador/API: Diagnosis filtrou presença e nota CSAT sem alterar a origem histórica; os denominadores e a lista de evidências acompanharam o recorte.
- [x] Navegador: Ticket Lab persistiu a identidade na URL e restaurou o texto, a identidade e o resultado completo após recarga.

## Estado por lente

| Lente | Núcleo verificável | Pendência relevante |
|---|---|---|
| Operational Diagnosis | filtros dimensionais e de presença/nota CSAT, seis cruzamentos, tabela e indisponibilidade temporal | multisseleção e ficha de fórmula/unidade por KPI |
| AI Automation Strategy | limites humanos, benchmark, fluxo e ROI parametrizado | carteira ainda não calcula elegibilidade/IDs por oportunidade |
| AI Ticket Lab | validação, classificação, embeddings, vizinhos, política, idempotência, persistência por URL e Lab→Graph | validação de versão/contexto, tempos separados por etapa e avaliação PT-BR/DS1 |
| AI Copilot | recuperação DS1, fallback extrativo, isolamento DS2 e feedback | histórico de feedback/sugestão recuperável na UI após reload |
| Support Intelligence Graph | espaços versionados, Sigma/Graphology, tabela, deep links, relações agregadas, alerta→membros, seleção tipo Obsidian, arraste individual e camadas neon | filtros funcionais, avaliação humana dos agrupamentos e teste formal de fallback WebGL/reduced motion |
| Support Command Center | sessões, eventos, replay, alerta, métricas, links contextuais e proveniência de eventos | trilha visual completa, reconexão em duas abas e fila IA enquanto há processamento |

## Limites que não serão mascarados

- [ ] VAL-01: relevância de vizinhos, duplicatas, clusters e resoluções ainda não receberam avaliação humana anotada.
- [ ] VAL-02: não há benchmark rotulado de entradas PT-BR, do DS1 ou de near-duplicates.
- [ ] OPS-05: uma API pública exige autenticação, rate limiting, monitoramento e revisão de privacidade além do CORS implementado.
- [ ] QA-01: teclado, 320 px, zoom de 200%, reduced motion, recuperação pós-restart e duas abas ainda precisam de ensaio dedicado.

Essas pendências não alteram os resultados medidos nem são substituídas por dados simulados. Elas permanecem marcadas nas specs e no plano para o próximo sprint.
