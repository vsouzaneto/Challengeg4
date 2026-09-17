# Validação, demonstração e process log

## Critério de conclusão

Um comportamento só está concluído quando existe, foi exercitado e sua evidência foi registrada. Falta de dado real exige mensagem de indisponibilidade; não exige fabricar resultado. As fases do [plano](02-plano-de-implementacao.md) e os checklists de cada spec são o backlog oficial.

## Matriz de aceite do sistema vivo

| ID | Verificação | Evidência esperada | Fases |
|---|---|---|---|
| LIVE-01 | Iniciar sessão de replay | ID, estado PLAYING e configuração retornados pelo servidor | F25/F27 |
| LIVE-02 | Reproduzir registros dos CSVs | source_ticket_id resolve para catálogo e checksum original | F01/F27 |
| LIVE-03 | Identificar simulação | Label persistente de Live Data Replay e horário simulado | F26/F27 |
| LIVE-04 | Atualizar Command Center | Snapshot e contadores mudam, sem dupla contagem | F28 |
| LIVE-05 | Atualizar Graph | Ocorrências/nós/contagens correspondem aos mesmos eventos | F29 |
| LIVE-06 | Classificar texto manual | Previsão real, versão, latência e política | F18 |
| LIVE-07 | Gerar embedding manual | Mesmo encoder/dimensão/normalização do espaço ativo | F11/F18 |
| LIVE-08 | Buscar vizinhos reais | IDs e scores conferem com índice, sem self match | F12/F18 |
| LIVE-09 | Inserir ticket no Graph | Deep link seleciona o ID criado e suas conexões reais | F24 |
| LIVE-10 | Alerta→cluster e membros | IDs destacados são os da janela salva no alerta | F30/F31 |
| LIVE-11 | Separar fontes | Histórico, simulação, manual e avaliação não somados silenciosamente | F26/F33 |
| LIVE-12 | Entender sem movimento | Tabela, textos, foco por teclado e reduced motion | F22/F34 |
| LIVE-13 | Preservar originais | Checksums CSV/PDF/logos antes e depois iguais | F01/F39 |
| LIVE-14 | Não apresentar números fictícios | KPI liga a evidência ou mostra null+motivo/premissas | F03/F05/F33 |
| LIVE-15 | Operar sem LLM externo | Recuperação/extrativo/feedback permanecem funcionais | F21/F34 |

## Verificações necessárias

- [x] DATA — contagens, IDs, normalização, nulos, hashes, SQLite canônico e indisponibilidade temporal.
- [x] ML — partições sem vazamento de grupos, baseline, avaliação congelada, manifesto e reload idêntico.
- [x] SEMANTIC — produto escalar confere com scores; versões de encoder/índice/projeção compatíveis; DS1/DS2 isolados.
- [ ] SESSION — idempotência, eventos ordenados, restart, duas abas, reset preservando histórico e erros persistidos.
- [ ] COPILOT — nenhuma resolução inventada, fontes citadas, rejeição/edição persistidas, ausência de evidência explícita.
- [ ] NAVIGATION — O Início e as seis lentes, foco, filtros, back/reload e links incompatíveis.
- [ ] ACCESSIBILITY — teclado, nomes acessíveis, contraste, tabela equivalente e reduced motion.
- [ ] FALLBACK — interromper polling e LLM opcional sem indisponibilizar páginas independentes.
- [x] BUILD — build e checagem de tipos do frontend; imports/compilação e checks do backend.
- [ ] LIVE-01–15 — exercício integrado usando dados locais e texto novo não selecionado previamente.

Usar checks pequenos focados nas invariantes; não criar suites que apenas repetem a implementação. Fixtures de teste podem ser sintéticas se identificadas e nunca exibidas como evidências reais de produto. Entrada maliciosa, vazio, duplicação e fronteiras numéricas merecem teste.

## Performance: metas a medir, não resultados

Primeiro medir cold start, inferência warm p50/p95, consulta de vizinhos, payload/latência por nível, memória do processo e fluidez da UI no computador de apresentação. Incluir versões, hardware e tamanho de amostra no registro.

Orçamento inicial candidato: polling 1 s; Graph até 200 agregados no overview, 500 tickets/2.500 edges no detalhe, tabelas paginadas; aumentar somente após medição. Inferência manual warm alvo p95 até 3 s no ambiente local; cold start separado. Se não atingir, exibir progresso e registrar resultado sem mudar labels. Replay deve respeitar capacidade de processamento/backpressure e não acumular trabalho sem limite. Contagens agregadas não são limitadas ao recorte visível do grafo.

Ensaiar lotes 50/100/500 com seed registrada. Reutilizar embeddings/artefatos históricos; não construir matriz completa de similaridade nem recalcular UMAP a cada evento. Cache não pode mascarar uma inferência manual como execução nova: modo e latência distinguem reaproveitamento.

## Roteiro executivo de 12 passos

1. **Diagnosis:** apresentar volume, qualidade e CSAT com cobertura. Explicar que a ausência de abertura impede concluir onde o TTR é maior; mostrar o dado necessário para responder.
2. **Strategy:** abrir oportunidade apoiada por evidência e delimitar decisão humana. Ajustar premissas do ROI sem tratá-lo como benefício realizado.
3. **Command Center:** criar sessão, exibir `Historical Dataset Simulation` e iniciar Live Replay.
4. Observar tickets reais do corpus entrando, classificação/política e contadores atualizando.
5. Abrir o **Graph** com o mesmo session_id, mantendo o espaço semântico do replay.
6. Executar cenário de concentração de conteúdo real, claramente marcado `SIMULATED INCIDENT SCENARIO`; mostrar regra e janela.
7. Clicar no alerta no Command Center e verificar cluster/membros exatos no Graph.
8. Abrir **Ticket Lab**, escrever texto livre e mostrar que a entrada não é exemplo fixo de UI.
9. Ler classificação, confidence, rota sugerida por política, vizinhos, modelo e latência.
10. Acionar **View in Semantic Network** e inspecionar nó e edges reais, com tabela equivalente.
11. Abrir **Copilot** em contexto DS1 explícito, recuperar resoluções com suas limitações e registrar ACCEPT/EDIT/REJECT. Se o ticket veio do domínio DS2, informar a ausência de resoluções nesse corpus e trocar de contexto declaradamente; não fabricar ponte entre bases.
12. Encerrar no **Command Center**, separando avaliação do modelo, decisões da sessão e impacto estimado. Mostrar o que foi observado, o que é simulação e o que depende de novos dados.

Narrativa: DIAGNOSE → DESIGN → AUTOMATE → OBSERVE → EXPLAIN → IMPROVE. A lacuna temporal é parte do diagnóstico, não um erro escondido na apresentação.

Plano de contingência: se polling falhar, usar snapshots/consultas e continuar as rotas; se LLM falhar, usar recuperação/extrativo; se inferência/índice falhar, mostrar o erro e continuar diagnóstico/estratégia/model metrics disponíveis. Não reproduzir vídeo ou valores de exemplo como se fossem resultado online.

## Process log desta etapa

O guia do challenge exige evidências de uso de IA. Este registro descreve somente ações realizadas, sem inventar experimentos ou decisões humanas.

| Etapa | Ação e evidência | Julgamento / resultado |
|---|---|---|
| Solicitação | Usuário forneceu arquitetura das seis lentes e pediu plano e specs antes da implementação | Manter tudo no diretório do challenge e preservar o briefing original |
| Inspeção | Leitura do README, guia de submissão, CSVs e PDF G4 | Ainda não havia aplicação; assets/dados já estavam presentes e não versionados |
| Decomposição | Codex dividiu leitura de dados, design e specs entre agentes, mantendo arquitetura/planejamento centralizados | Reduzir conflito de arquivos e harmonizar contratos antes de programar |
| Verificação de dados | Auditoria agregada com Python; resultados em [dados](03-dados-e-metricas.md) | Corrigir pressupostos do briefing: 8.469 DS1, 47.837 DS2, tempos não calculáveis, resoluções somente DS1 |
| Verificação visual | PDF G4 lido e inspecionado; contraste conferido | Usar tokens reais; não herdar alegação de contraste sem cálculo |
| Escolhas técnicas | Consulta à documentação oficial registrada em [arquitetura](01-arquitetura-compartilhada.md) | Aplicação local única, polling antes de streaming, grafo e ML reais |
| Ambiente de implementação | Ambiente isolado Python 3.12 criado no challenge; dependências congeladas em `requirements.lock.txt`; imports FastAPI/scikit-learn/FAISS/Sentence-Transformers/HDBSCAN/UMAP passaram | Originais preservados; aceleração MPS disponível; nenhuma publicação ou push |
| Direção do usuário | Usuário confirmou “Iniciar a implementação após documentar” | Implementação autorizada após concluir e revisar este conjunto |
| Implementação | Backend FastAPI, SQLite de catálogo/sessões, ML, semântica, seis lentes, O Início e frontend Vite construídos dentro do challenge | Dados históricos, simulação e entrada manual mantêm origem separada; nenhum CSV foi alterado |
| Portabilidade | Catálogo/previsões migrados para SQLite; encoder deixou de depender de caminho absoluto macOS; frontend aceita API externa por variável de build | Artefatos continuam imutáveis e a publicação usa backend com volume persistente |
| Validação final | Checks de dados, backend, integração, ROI, build e navegador executados em 2026-09-16 | Resultados e lacunas registrados em [resultados técnicos](06-resultados-tecnicos.md) e [auditoria final](08-auditoria-final.md) |
| Onboarding e rede visual | Rota O Início carregada no navegador com narrativa Hermes → Codex → planejamento, comando local e seis lentes; Graph overview passou a exibir relações agregadas calculadas por centroides, nós neon pequenos, pulso nas arestas reais, seleção tipo Obsidian, arraste individual e transição do workspace | A camada visual não altera scores, IDs ou interpretação; validação dedicada em 320px/zoom/reduced-motion continua no gate de acessibilidade |
| Persistência do Ticket Lab | Texto novo foi analisado, a URL recebeu `ticket_id`/sessão/versões e o recarregamento restaurou texto, categoria, confiança e vizinhos; a ação sugerida e metadados de arestas/alertas passaram a acompanhar o contrato | Validação de `model_version` antigo/incompatível e tempos por etapa continuam pendentes |

Ao implementar, acrescentar execução, resultados de build/checks, métricas de avaliação, problemas encontrados, correções e limitações. Dados fictícios e números de layout do briefing não servem como evidência.

## Entrega e operação

A solução permanece neste diretório por instrução explícita do usuário, embora o guia geral do challenge sugira `submissions/`. Preparar documentação de execução local primeiro. Publicação externa e submissão por PR não são presumidas nesta etapa; o push desta entrega foi autorizado explicitamente pelo usuário após os checks. Preservar os CSVs e logs, inclusive no reset.
