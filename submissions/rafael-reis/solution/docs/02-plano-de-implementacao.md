# Plano de implementação — sprints e checkpoints

Este plano cobre as 40 fases solicitadas e o incremento de onboarding F40. Numeração preserva o briefing; dependências determinam a ordem real. F25 é desenhada em S0 e implementada em S4, antes dos consumidores de sessão. Estimativas de prazo só após benchmark do ambiente; o escopo de seis lentes excede o protótipo básico de 4–6 horas citado no challenge.

## Como acompanhar

- `[ ]` pendente; `[x]` somente após implementar e verificar com evidência registrada no process log.
- Cada fase tem um checkpoint de implementação e outro de aceite. Documentação pronta não marca feature como pronta.
- Bloqueio por falta de dados não autoriza fabricação: implementar o estado indisponível e registrar o dado necessário.
- P0 segue as seis specs. P1/P2 podem ficar explicitamente pendentes; não retirar requisitos P0 para simular conclusão.
- Nenhum commit/push sem build validado; push e exclusões dependem de autorização explícita.

**Atualização de implementação (2026-09-16):** fases marcadas com `[x]` possuem artefato e check executado; uma fase com implementação marcada e aceite aberto permanece parcial. A matriz detalhada está em [08-auditoria-final.md](08-auditoria-final.md).

## Sprints

| Sprint | Objetivo | Fases | Gate de saída |
|---|---|---|---|
| S0 | Fundação e contratos | F00–F02 + desenho antecipado de F25 | Inventário, contratos, lacunas temporais e design revisados. |
| S1 | Diagnóstico histórico | F03–F06 | Primeira entrega obrigatória com cortes reais e limitações visíveis. |
| S2 | Estratégia e classificador | F07–F10 | Segunda entrega obrigatória e modelo comparado a baseline. |
| S3 | Núcleo semântico | F11–F16 | Índices e espaços separados, clusters e projeção reais. |
| S4 | API e Ticket Lab | F17–F19 + implementação F25 | Inferência nova e sessão persistida, contratos conectados. |
| S5 | Copilot e Graph | F20–F24 | Recuperação rastreável, feedback e Lab→Graph. |
| S6 | Command Center e Replay | F26–F29 | Contadores e grafo sincronizados por eventos reais da simulação. |
| S7 | Incidentes e observabilidade | F30–F33 | Alertas navegáveis, auditoria e métricas de modelo. |
| S8 | Verificação e desempenho | F34–F36 | Checks, limitações e execução documentados. |
| S9 | Execução e demonstração | F37–F40 | Demo local ensaiada, guia O Início e pendências explícitas. |

## Fases detalhadas

### F00 — Inspeção do repositório e ambiente

- **Objetivo:** Identificar fontes, restrições, assets e runtime.
- **Entradas:** Briefing, README, CSVs, PDF G4.
- **Saídas:** Inventário e ambiente compatível documentados.
- **Arquivos previstos:** docs/; configuração do ambiente isolado.
- **Dependências:** Nenhuma.
- **Abordagem:** Ler originais sem modificá-los; conferir Python/Node e dependências antes de instalar.
- **Testes:** Comparar inventário com arquivos locais e testar imports.
- **Critérios de aceite:** Entradas e limitações localizadas; ambiente reproduzível.
- **Riscos:** Versões ML incompatíveis com Python do sistema.
- [x] **F00.I — Implementação:** inventário registrado; ambiente Python 3.12 isolado e dependências congeladas em `requirements.lock.txt`.
- [x] **F00.A — Checkpoint:** imports FastAPI/scikit-learn/FAISS/Sentence-Transformers/HDBSCAN/UMAP passaram; MPS disponível; checksums dos 13 originais registrados.

### F01 — Validação dos datasets

- **Objetivo:** Fixar identidade e schema verificável.
- **Entradas:** CSVs e contrato de dados.
- **Saídas:** Manifesto com hashes, contagens, nulos e IDs.
- **Arquivos previstos:** scripts/prepare_data.py; artifacts/<v>/manifest.json.
- **Dependências:** F00.
- **Abordagem:** CSV por nome de coluna; NFC/whitespace para IDs; validar unicidade.
- **Testes:** Repetir preparação e comparar hashes/IDs; CSVs intactos.
- **Critérios de aceite:** 8.469 DS1 e 47.837 DS2 contabilizados ou divergência explicitamente relatada.
- **Riscos:** Confundir estimativas do briefing com arquivos reais.
- [x] **F01.I — Implementação:** manifesto, catálogo SQLite sanitizado e IDs foram produzidos.
- [x] **F01.A — Checkpoint:** hashes, contagens e IDs foram verificados no check de dados.

### F02 — Qualidade dos dados

- **Objetivo:** Explicitar dados ausentes, duplicados e inválidos.
- **Entradas:** Manifesto e registros.
- **Saídas:** Relatório de qualidade e capacidades por dataset.
- **Arquivos previstos:** scripts/prepare_data.py; artifacts/<v>/quality.json.
- **Dependências:** F01.
- **Abordagem:** Medir placeholders, cronologia inconsistente, cobertura de CSAT/resolução e grupos repetidos.
- **Testes:** Casos nulos, resolução anterior à resposta e rótulos conflitantes.
- **Critérios de aceite:** TTR/FRT sem origem temporal válida ficam null com motivo.
- **Riscos:** Transformar timestamp em duração ou preencher lacunas com zero.
- [x] **F02.I — Implementação:** relatório de qualidade e bloqueios temporais foram produzidos.
- [x] **F02.A — Checkpoint:** pares temporais inválidos e indisponibilidade foram verificados.

### F03 — EDA operacional

- **Objetivo:** Mapear volume e distribuição por dimensões reais.
- **Entradas:** DS1 validado.
- **Saídas:** Agregações e evidências filtráveis.
- **Arquivos previstos:** scripts/prepare_data.py; artifacts/<v>/diagnosis.json.
- **Dependências:** F02.
- **Abordagem:** Canal×prioridade, canal×tipo, prioridade×tipo, triplo, produto×tipo, status×canal; mostrar n.
- **Testes:** Totais conciliam com filtros e linhas elegíveis.
- **Critérios de aceite:** Todo corte oferece denominador e tickets de suporte.
- **Riscos:** Interpretar grupo pequeno ou não observado como gargalo comprovado.
- [x] **F03.I — Implementação:** agregações/cortes DS1 e API de diagnóstico foram implementados.
- [x] **F03.A — Checkpoint:** recorte Phone × High foi conciliado independentemente com o CSV.

### F04 — Estatística e CSAT

- **Objetivo:** Examinar associações sem alegar causalidade.
- **Entradas:** CSAT e dimensões observadas.
- **Saídas:** Distribuição, cobertura e relatório de associações.
- **Arquivos previstos:** scripts/prepare_data.py; artifacts/<v>/statistics.json.
- **Dependências:** F03.
- **Abordagem:** Média/mediana/p75/p90/p95/desvio quando pertinentes; intervalos/amostras pequenas; testes exploratórios com correção de multiplicidade se usados.
- **Testes:** Validar quantis em amostra conhecida; zero respondentes gera null.
- **Critérios de aceite:** Cobertura de respondentes sempre visível; nenhuma relação temporal inventada.
- **Riscos:** Viés de seleção: apenas Closed tem CSAT; texto templateado.
- [x] **F04.I — Implementação:** CSAT, cobertura, distribuição, estatísticas e filtros por presença/nota foram implementados.
- [x] **F04.A — Checkpoint:** amostra vazia retorna nulo e a cobertura de CSAT foi verificada.

### F05 — Metodologia de ROI

- **Objetivo:** Tornar esforço e custo cenários auditáveis.
- **Entradas:** Volume elegível, parâmetros humanos e qualidade da automação.
- **Saídas:** Calculadora com fórmulas e premissas.
- **Arquivos previstos:** frontend/src/views/strategy.ts; docs/03-dados-e-metricas.md.
- **Dependências:** F03; taxas reais após F10.
- **Abordagem:** Separar etapas para não contar economia duas vezes; descontar revisão/retrabalho/custos e parametrizar horizonte.
- **Testes:** Zero elegibilidade, custo ausente, benefício negativo e parâmetros inválidos.
- **Critérios de aceite:** ROI não aparece como realizado; dinheiro só com custo informado.
- **Riscos:** Usar TTR decorrido como trabalho do agente.
- [x] **F05.I — Implementação:** calculadora de ROI por premissas editáveis foi implementada.
- [x] **F05.A — Checkpoint:** custo zero, ganho negativo e validação aritmética passaram no teste do frontend.

### F06 — Operational Diagnosis UI

- **Objetivo:** Entregar primeiro diagnóstico HTML completo.
- **Entradas:** F03/F04, tokens e shell.
- **Saídas:** Rota diagnosis com gráficos/tabelas/evidências.
- **Arquivos previstos:** frontend/index.html; frontend/src/main.ts; frontend/src/styles.css; frontend/src/views/diagnosis.ts.
- **Dependências:** F03, F04; contratos de F25 definidos.
- **Abordagem:** Shell comum, filtros e drill-down; qualidade antes de conclusões.
- **Testes:** Navegação por teclado, filtros cruzados, estados sem dados e links.
- **Critérios de aceite:** Spec 01 passa com dados reais e TTR/FRT indisponíveis explicados.
- **Riscos:** Dashboard estético sem decisões sustentadas.
- [x] **F06.I — Implementação:** rota Diagnosis, filtros, cruzamentos, evidências e estados de indisponibilidade foram implementados.
- [ ] **F06.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F07 — AI Automation Strategy UI

- **Objetivo:** Entregar estratégia acionável e human-in-the-loop.
- **Entradas:** Diagnóstico, capacidades e ROI.
- **Saídas:** Rota automation com oportunidades e políticas.
- **Arquivos previstos:** frontend/src/views/strategy.ts.
- **Dependências:** F05, F06.
- **Abordagem:** Separar observado/hipótese, definir não automatizar e mostrar arquitetura/evidências.
- **Testes:** Origem de cada oportunidade, parâmetros ROI e links preservam contexto.
- **Critérios de aceite:** Spec 02 passa; nenhuma promessa de automatizar 100%.
- **Riscos:** Extrapolar DS2 para DS1 ou assumir custos.
- [x] **F07.I — Implementação:** rota Strategy, limites humanos, benchmark e ROI foram implementados.
- [ ] **F07.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F08 — Benchmark ML

- **Objetivo:** Comparar alternativas sem contaminar teste.
- **Entradas:** DS2 e grupos de texto.
- **Saídas:** Splits persistidos, baseline e comparação.
- **Arquivos previstos:** scripts/train.py; artifacts/<v>/benchmark.json.
- **Dependências:** F02.
- **Abordagem:** Baseline majoritário e TF-IDF com modelos lineares; splits estratificados por grupos; seed fixa.
- **Testes:** Grupos disjuntos, classes representadas, treino sem acesso ao teste.
- **Critérios de aceite:** Accuracy/Macro F1 e F1 por categoria calculados em holdout identificado.
- **Riscos:** Duplicatas próximas vazando entre partições.
- [x] **F08.I — Implementação:** split por grupos, baseline e avaliação holdout foram produzidos.
- [x] **F08.A — Checkpoint:** IDs/textos normalizados entre partições foram verificados como disjuntos.

### F09 — Classificador final

- **Objetivo:** Persistir o melhor compromisso medido.
- **Entradas:** Benchmark e split de treino/validação.
- **Saídas:** Pipeline serializado e manifesto.
- **Arquivos previstos:** scripts/train.py; artifacts/<v>/classifier.joblib.
- **Dependências:** F08.
- **Abordagem:** Selecionar por Macro F1/calibração/custo; congelar versão antes da avaliação final.
- **Testes:** Roundtrip salvar/carregar mantém previsões.
- **Critérios de aceite:** Inferência de texto novo funciona usando artefato real.
- **Riscos:** Reajustar modelo ao teste final.
- [x] **F09.I — Implementação:** classificador calibrado e versão persistida foram produzidos.
- [x] **F09.A — Checkpoint:** recarga do joblib e inferência real passaram no check de dados.

### F10 — Análise de confiança

- **Objetivo:** Governar abstenção e automação.
- **Entradas:** Previsões de validação, rótulos e modelo.
- **Saídas:** Relatório de calibração, cobertura×risco e policy_version.
- **Arquivos previstos:** scripts/train.py; artifacts/<v>/model_metrics.json; artifacts/<v>/policy.json.
- **Dependências:** F09.
- **Abordagem:** Calibrar em amostra separada; escolher limiar pela evidência; sensível/OOD exige humano.
- **Testes:** Baixa confiança e idioma não validado nunca entram como seguros.
- **Critérios de aceite:** UI diferencia score, confidence e limiar experimental.
- **Riscos:** Tratar predict_proba não validado como garantia.
- [x] **F10.I — Implementação:** calibração, limiar experimental e razões de revisão foram implementados.
- [x] **F10.A — Checkpoint:** entrada manual abaixo do limiar exigiu revisão no backend.

### F11 — Sentence embeddings

- **Objetivo:** Representar semanticamente conteúdo dos dois datasets.
- **Entradas:** Textos sanitizados por dataset.
- **Saídas:** Vetores normalizados, mapa de IDs e encoder fixado.
- **Arquivos previstos:** scripts/build_semantic.py; artifacts/<v>/<dataset>/embeddings.npy.
- **Dependências:** F02.
- **Abordagem:** Encoder multilíngue candidato; processamento em lotes, cache persistido e manifesto.
- **Testes:** Dimensão, norma, valores finitos, IDs e sample similarity.
- **Critérios de aceite:** Ticket manual passa pelo mesmo preprocessamento/encoder.
- **Riscos:** Download indisponível, memória, truncamento e domínio.
- [x] **F11.I — Implementação:** embeddings normalizados dos dois corpora e encoder fixado foram produzidos.
- [x] **F11.A — Checkpoint:** dimensão, norma, finitude e entrada online foram verificadas.

### F12 — Índice FAISS

- **Objetivo:** Buscar vizinhos reais com scores auditáveis.
- **Entradas:** Embeddings e IDs.
- **Saídas:** Índice exato por espaço semântico.
- **Arquivos previstos:** scripts/build_semantic.py; artifacts/<v>/<dataset>/index.faiss.
- **Dependências:** F11.
- **Abordagem:** IndexFlatIP sobre vetores normalizados; top-k sem self match.
- **Testes:** Comparar scores com produto escalar em amostra.
- **Critérios de aceite:** Índice e corpus têm checksum/dimensão compatíveis.
- **Riscos:** Misturar espaços ou apresentar distância como similaridade.
- [x] **F12.I — Implementação:** índices FAISS exatos e mapas de IDs foram produzidos.
- [x] **F12.A — Checkpoint:** self-match, cardinalidade e score unitário foram verificados.

### F13 — Análise de vizinhança

- **Objetivo:** Validar a utilidade das conexões.
- **Entradas:** Top-k e amostras de tickets.
- **Saídas:** Amostra de pares, métricas de vizinhança e kNN esparso.
- **Arquivos previstos:** scripts/build_semantic.py; artifacts/<v>/<dataset>/neighbors.json.
- **Dependências:** F12.
- **Abordagem:** Revisar pares fortes/fracos e concordância de categorias; nunca matriz quadrática completa.
- **Testes:** Excluir própria referência e limitar k.
- **Critérios de aceite:** Edges correspondem a resultados do índice e são reproduzíveis.
- **Riscos:** Semelhança textual não comprova mesmo incidente.
- [x] **F13.I — Implementação:** vizinhos top-k rastreáveis foram persistidos por corpus.
- [x] **F13.A — Checkpoint:** vizinhos excluem a própria referência e os edges vêm do índice.

### F14 — UMAP

- **Objetivo:** Projetar os vetores para navegação visual.
- **Entradas:** Embeddings por espaço.
- **Saídas:** Coordenadas e transformador persistidos.
- **Arquivos previstos:** scripts/build_semantic.py; artifacts/<v>/<dataset>/projection.joblib.
- **Dependências:** F11.
- **Abordagem:** Ajustar offline com seed; transformar novos pontos sem refazer todo mapa.
- **Testes:** Coordenadas finitas e coerentes após reload; comparação de vizinhos.
- **Critérios de aceite:** Posição explicitamente descrita como aproximação 2D.
- **Riscos:** Usuário interpretar distância de tela como score.
- [x] **F14.I — Implementação:** UMAP e transformação de ponto manual foram persistidos.
- [x] **F14.A — Checkpoint:** coordenadas finitas e posição online foram verificadas.

### F15 — Clustering / comunidades

- **Objetivo:** Identificar famílias naturais e ruído.
- **Entradas:** Embeddings e análise de vizinhança.
- **Saídas:** Clusters versionados, ruído e rótulos descritivos.
- **Arquivos previstos:** scripts/build_semantic.py; artifacts/<v>/<dataset>/clusters.json.
- **Dependências:** F13.
- **Abordagem:** HDBSCAN original/redução validada; avaliar estabilidade; subclusters apenas se sustentados.
- **Testes:** Conservar membros e ruído; verificar coesão e distribuição.
- **Critérios de aceite:** Categoria oficial e cluster são entidades distintas.
- **Riscos:** Forçar categorias conhecidas como clusters descobertos.
- [x] **F15.I — Implementação:** HDBSCAN, ruído e rótulos exploratórios foram produzidos.
- [x] **F15.A — Checkpoint:** membros, ruído e separação de categoria/cluster foram verificados tecnicamente.

### F16 — Artefatos do grafo

- **Objetivo:** Preparar dados limitados por nível.
- **Entradas:** Clusters, projeção, vizinhos e métricas.
- **Saídas:** Overview, detalhes e manifesto de espaço.
- **Arquivos previstos:** scripts/build_semantic.py; artifacts/<v>/<dataset>/graph.json.
- **Dependências:** F14, F15.
- **Abordagem:** Agregar cluster→subcluster quando existir→tickets; limites e paginação.
- **Testes:** Referências válidas; pesos reais; contagens conciliadas.
- **Critérios de aceite:** Nenhuma resposta exige renderizar os 56.306 registros de uma vez.
- **Riscos:** Payload grande ou métricas de DS1 aplicadas em DS2.
- [x] **F16.I — Implementação:** manifesto semântico, overview e recortes de tickets foram implementados.
- [x] **F16.A — Checkpoint:** pesos, contagens e limites do Graph foram verificados.

### F17 — Camada FastAPI

- **Objetivo:** Expor núcleo de inferência e dados.
- **Entradas:** Modelos, catálogo e contratos.
- **Saídas:** API validada com OpenAPI e health.
- **Arquivos previstos:** backend/app.py; backend/pipeline.py.
- **Dependências:** F09, F12, F16; contrato F25.
- **Abordagem:** Carregar artefatos uma vez; validar requests; falhar explicitamente se incompatíveis.
- **Testes:** Input vazio/excessivo, espaço errado, timeout e artefato ausente.
- **Critérios de aceite:** Uma mesma chamada alimenta Lab, Graph e sessão.
- **Riscos:** Mock silencioso como fallback.
- [x] **F17.I — Implementação:** FastAPI, validação, saúde/readiness e contratos compartilhados foram implementados.
- [x] **F17.A — Checkpoint:** entradas inválidas, espaço incompatível e artefatos foram exercitados no backend.

### F18 — AI Ticket Lab

- **Objetivo:** Permitir entrada livre e resultados reais.
- **Entradas:** API e contexto compartilhado.
- **Saídas:** Rota ticket-lab funcional.
- **Arquivos previstos:** frontend/src/views/lab.ts.
- **Dependências:** F17, F10.
- **Abordagem:** Mostrar classificação, vizinhos, políticas, versão/latência e botão para Graph.
- **Testes:** Textos não vistos, entrada inválida, erro, retry e teclado.
- **Critérios de aceite:** Spec 03 passa e payload corresponde ao backend.
- **Riscos:** Resultados decorativos ou hardcoded.
- [x] **F18.I — Implementação:** Ticket Lab executa classificação, busca, política e links contextuais.
- [x] **F18.A — Checkpoint:** inferência manual real e Lab→Graph foram exercitados no navegador e na integração.

### F19 — Detecção de duplicatas

- **Objetivo:** Sinalizar candidatos com evidências.
- **Entradas:** Vizinhos e amostra anotada.
- **Saídas:** Score, regra versionada e revisão de pares.
- **Arquivos previstos:** backend/pipeline.py; artifacts/<v>/policy.json.
- **Dependências:** F13, F17.
- **Abordagem:** Threshold experimental até validação; separar match exato de semântico.
- **Testes:** Self/reference exclusion; negativos difíceis e casos próximos do limiar.
- **Critérios de aceite:** Nenhum ticket é fundido/excluído automaticamente.
- **Riscos:** Score de cosseno interpretado como probabilidade.
- [x] **F19.I — Implementação:** candidatos por similaridade, limiar e política explícita foram implementados.
- [ ] **F19.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F20 — Recuperação de resoluções

- **Objetivo:** Encontrar evidências históricas válidas.
- **Entradas:** DS1, resoluções presentes e índice DS1.
- **Saídas:** Contexto Top-K com IDs e limitações.
- **Arquivos previstos:** backend/pipeline.py.
- **Dependências:** F12, F17.
- **Abordagem:** Filtrar resolução vazia; alertar conteúdo genérico; DS2 não herda resolução DS1.
- **Testes:** Sem evidência retorna insuficiente; fontes batem com catálogo.
- **Critérios de aceite:** Cada resolução exibida é rastreável à linha sanitizada.
- **Riscos:** Confundir texto templateado com procedimento verificado.
- [x] **F20.I — Implementação:** recuperação DS1 por vizinhos e fontes sanitizadas foi implementada.
- [x] **F20.A — Checkpoint:** DS1 recupera fontes e DS2 retorna evidência insuficiente sem join artificial.

### F21 — AI Copilot

- **Objetivo:** Ajudar o agente com fonte e feedback.
- **Entradas:** Contexto recuperado e sessão.
- **Saídas:** Rota copilot, sugestão extractiva e feedback.
- **Arquivos previstos:** frontend/src/views/copilot.ts; backend/sessions.py.
- **Dependências:** F20, F25.
- **Abordagem:** Gerador determinístico rastreável; LLM opcional; ACCEPT/EDIT/REJECT versionados.
- **Testes:** Falha LLM, edit vazio, rejeição e idempotência do feedback.
- **Critérios de aceite:** Spec 04 passa sem serviço externo; nenhuma mensagem é enviada.
- **Riscos:** Alucinação, prompt injection e feedback perdido.
- [x] **F21.I — Implementação:** Copilot extrativo, feedback e eventos foram implementados.
- [x] **F21.A — Checkpoint:** edit/reject, idempotência e ausência DS2 foram verificados.

### F22 — Support Intelligence Graph

- **Objetivo:** Transformar semântica em investigação.
- **Entradas:** Artefatos e API.
- **Saídas:** Rota graph com Sigma e alternativa tabular.
- **Arquivos previstos:** frontend/src/views/graph.ts.
- **Dependências:** F16, F17, F06.
- **Abordagem:** Overview hierárquico, modos por capacidade, legenda e tabela.
- **Testes:** WebGL indisponível, vazios, foco por teclado e limites.
- **Critérios de aceite:** Spec 05 passa sem confundir grafo com rede neural.
- **Riscos:** Visual decorativo sem utilidade ou contexto.
- [x] **F22.I — Implementação:** Graph Sigma/Graphology, legenda, detalhe e tabela alternativa foram implementados.
- [ ] **F22.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F23 — Drill-down do grafo

- **Objetivo:** Abrir evidências precisas do cluster/ticket.
- **Entradas:** IDs/filters e dados de vizinhança.
- **Saídas:** Deep links e painel contextual.
- **Arquivos previstos:** frontend/src/views/graph.ts; backend/app.py.
- **Dependências:** F22.
- **Abordagem:** IDs versionados, seleção URL e tickets paginados.
- **Testes:** Link direto/reload/back e contexto incompatível.
- **Critérios de aceite:** Selecionar cluster explica seus membros e métricas.
- **Riscos:** Selecionar grupo homônimo de outro espaço.
- [x] **F23.I — Implementação:** deep links por ticket/cluster/alerta e painel contextual foram implementados.
- [x] **F23.A — Checkpoint:** ticket manual e alerta abrem o recorte compatível no Graph.

### F24 — Entrada de novo ticket no grafo

- **Objetivo:** Explicar vizinhança do ticket manual.
- **Entradas:** Embedding, posição e vizinhos online.
- **Saídas:** Overlay de sessão com câmera e edges reais.
- **Arquivos previstos:** backend/pipeline.py; frontend/src/views/graph.ts.
- **Dependências:** F18, F23, F25.
- **Abordagem:** Transformação UMAP e conexões reais; animação só apresenta resultado.
- **Testes:** Reduced motion, retorno ao foco e inferência sem vizinhos.
- **Critérios de aceite:** Ticket Lab→Graph mantém ticket/space/session.
- **Riscos:** Animação aleatória ou perda do ticket após navegação.
- [x] **F24.I — Implementação:** overlay do ticket manual usa UMAP transform e edges reais.
- [x] **F24.A — Checkpoint:** o fluxo Lab→Graph preservou ticket, sessão, espaço e oito conexões.

### F25 — Eventos e sessões

- **Objetivo:** Estabelecer estado único e persistente.
- **Entradas:** Contratos deste planejamento.
- **Saídas:** SQLite, snapshots, eventos, IDs e máquina de estados.
- **Arquivos previstos:** backend/sessions.py; backend/app.py.
- **Dependências:** F01; desenho antecipado em S0.
- **Abordagem:** Um worker local, sequência monotônica, idempotência e reset por nova sessão.
- **Testes:** Eventos repetidos/desordenados, restart, duas abas, isolamento e reset sem apagar logs.
- **Critérios de aceite:** Snapshot+cursor e histórico preservam consistência.
- **Riscos:** Contagem duplicada, concorrência e exclusão acidental.
- [x] **F25.I — Implementação:** SQLite de sessões, eventos, idempotência e reset não destrutivo foram implementados.
- [x] **F25.A — Checkpoint:** eventos ordenados, cursor, isolamento e reset preservando histórico foram verificados.

### F26 — Support Command Center

- **Objetivo:** Consolidar operação, IA e evidências.
- **Entradas:** Métricas históricas, modelo e sessão.
- **Saídas:** Rota command-center e controles.
- **Arquivos previstos:** frontend/src/views/command.ts.
- **Dependências:** F25, F17, F10.
- **Abordagem:** Separar fontes e denominadores; cada card tem evidência ou motivo de indisponibilidade.
- **Testes:** Sem sessão, modelo ausente, filtros e links de cards.
- **Critérios de aceite:** Spec 06 passa; fila IA não é backlog de suporte.
- **Riscos:** Mostrar indicadores fictícios para preencher layout.
- [x] **F26.I — Implementação:** Command Center com controles, métricas e evidências foi implementado.
- [ ] **F26.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F27 — Live Replay Engine

- **Objetivo:** Reproduzir conteúdo real com agenda simulada.
- **Entradas:** IDs reais, artefatos e sessão.
- **Saídas:** Replay play/pause/reset/speed e trilha.
- **Arquivos previstos:** backend/sessions.py.
- **Dependências:** F25, F17.
- **Abordagem:** Pré-cálculo reutilizado explicitamente; manual continua online; seed e agenda persistidos.
- **Testes:** Play idempotente, pause, completar, reset, retry e multiplicador.
- **Critérios de aceite:** Conteúdo real; arrival_time rotulado simulation.
- **Riscos:** Reprocessar corpus inteiro ou simular produção.
- [x] **F27.I — Implementação:** replay real com play/pause/speed/reset e agenda simulada foi implementado.
- [x] **F27.A — Checkpoint:** sequência, conclusão e reset sem exclusão passaram na integração.

### F28 — Dashboard incremental

- **Objetivo:** Atualizar KPIs conforme eventos.
- **Entradas:** Snapshot e eventos paginados.
- **Saídas:** Contadores/distribuições atuais com cursor.
- **Arquivos previstos:** frontend/src/main.ts; frontend/src/views/command.ts.
- **Dependências:** F26, F27.
- **Abordagem:** Polling 1 s candidato, deduplicação, backoff e ressincronização.
- **Testes:** Reconexão, evento repetido, cursor expirado e duas abas.
- **Critérios de aceite:** Somatório incremental igual a snapshot recomputado no teste.
- **Riscos:** Browser virar fonte de verdade da operação.
- [x] **F28.I — Implementação:** polling incremental, cursor, snapshot e backoff foram implementados.
- [ ] **F28.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F29 — Grafo incremental

- **Objetivo:** Reagir ao replay sem reconstruir tudo.
- **Entradas:** Eventos e overlay da sessão.
- **Saídas:** Nós/edges/contagens e foco consistente.
- **Arquivos previstos:** frontend/src/views/graph.ts.
- **Dependências:** F24, F27, F28.
- **Abordagem:** Atualização do subgrafo visível; contagens agregadas nos demais níveis.
- **Testes:** Replay em outra aba, troca de nível e limite de nós.
- **Critérios de aceite:** Novos nós correspondem às ocorrências reais da sessão.
- **Riscos:** Travamento por desenho/consulta de toda a base.
- [x] **F29.I — Implementação:** Graph consulta overlays de sessão e reconcilia contagens por snapshot/eventos.
- [ ] **F29.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F30 — Demonstração de incidentes

- **Objetivo:** Demonstrar burst semântico com regra transparente.
- **Entradas:** Clusters, agenda e eventos.
- **Saídas:** Cenário simulado e alertas com evidência.
- **Arquivos previstos:** backend/sessions.py; frontend/src/views/command.ts.
- **Dependências:** F15, F27, F29.
- **Abordagem:** Janela simulation_time, fontes únicas, coesão e thresholds configurados; cooldown.
- **Testes:** Burst versus sequência dispersa, mesmo conteúdo repetido e expiração da janela.
- **Critérios de aceite:** Alerta abre membros exatos; threshold identificado como experimental.
- **Riscos:** Alegar validade estatística/temporal inexistente.
- [x] **F30.I — Implementação:** cenário concentrado, janela, fontes únicas e alertas versionados foram implementados.
- [x] **F30.A — Checkpoint:** alerta→membros exatos no Graph passou na integração.

### F31 — Drill-down entre rotas

- **Objetivo:** Garantir uma história contínua.
- **Entradas:** URLs, IDs e métricas.
- **Saídas:** Fluxos Lab→Graph→Copilot e Command→Graph/Strategy.
- **Arquivos previstos:** frontend/src/main.ts; frontend/src/views/.
- **Dependências:** F07, F21, F23, F26, F30.
- **Abordagem:** Centralizar leitura/escrita de contexto e filtros compatíveis.
- **Testes:** Percorrer todos links com reload/back e sessão existente.
- **Critérios de aceite:** Mesma evidência/ID em qualquer lente.
- **Riscos:** Seis estados isolados mascarados por navegação.
- [x] **F31.I — Implementação:** links contextuais entre lentes compartilham dataset, sessão, espaço e ticket.
- [ ] **F31.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F32 — Auditabilidade

- **Objetivo:** Reconstruir decisões e intervenções.
- **Entradas:** Eventos, previsões e feedback.
- **Saídas:** Trilha consultável sanitizada.
- **Arquivos previstos:** backend/sessions.py; frontend/src/views/command.ts.
- **Dependências:** F25, F21, F31.
- **Abordagem:** Guardar versões e razões; exportar só dados autorizados/sanitizados.
- **Testes:** Trace prediction→neighbors→policy→human decision.
- **Critérios de aceite:** Nenhum overwrite de decisão histórica; source explícito.
- **Riscos:** PII/segredos no log ou registro incompleto.
- [x] **F32.I — Implementação:** eventos persistidos registram inferência, vizinhos, política, alertas e feedback.
- [x] **F32.A — Checkpoint:** eventos de replay, sugestão e feedback foram verificados com proveniência, versões e isolamento de sessão.

### F33 — Model Intelligence

- **Objetivo:** Explicar limites do classificador.
- **Entradas:** Teste congelado e inferências da sessão.
- **Saídas:** Painel de modelo, confusões e overrides.
- **Arquivos previstos:** frontend/src/views/command.ts; artifacts/<v>/model_metrics.json.
- **Dependências:** F10, F26, F32.
- **Abordagem:** Separar avaliação offline de confidence online; drift futuro exige método.
- **Testes:** Classes sem amostra, denominadores, override só com humano registrado.
- **Critérios de aceite:** Métricas reais rastreáveis a versão/split.
- **Riscos:** Chamar mudança de distribuição de drift.
- [x] **F33.I — Implementação:** métricas do modelo, versão e limites de confiança foram expostos no Command Center.
- [ ] **F33.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F34 — Testes

- **Objetivo:** Verificar invariantes e experiência integrada.
- **Entradas:** Sistema P0 implementado.
- **Saídas:** Checks unitários mínimos e smoke end-to-end.
- **Arquivos previstos:** tests/; docs/05-validacao-demo-processo.md.
- **Dependências:** F31, F32, F33.
- **Abordagem:** Cobrir perda/dupla contagem, vazamento, fonte, artefato, a11y e fallback.
- **Testes:** Executar checks e registrar resultados reais.
- **Critérios de aceite:** 15 critérios do briefing passam ou bloqueio explícito com causa.
- **Riscos:** Teste de render isolado não verificar sistema.
- [x] **F34.I — Implementação:** checks de dados, backend, integração e frontend foram implementados e executados.
- [ ] **F34.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F35 — Performance

- **Objetivo:** Medir e corrigir gargalos reais.
- **Entradas:** Build e dados completos.
- **Saídas:** Relatório de latência/payload/memória.
- **Arquivos previstos:** docs/05-validacao-demo-processo.md; arquivos onde medição indicar.
- **Dependências:** F34.
- **Abordagem:** Medir cold/warm, p50/p95, CPU/memória e navegação; budgets são metas a validar.
- **Testes:** Replay 50/100/500 e graph por níveis, sem expandir corpus inteiro.
- **Critérios de aceite:** Sem operações pesadas repetidas por evento; limites respeitados.
- **Riscos:** Otimização prematura esconder falhas de correção.
- [ ] **F35.I — Implementação:** produzir as saídas e registrar evidência.
- [ ] **F35.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F36 — Documentação final

- **Objetivo:** Tornar execução e limitações reproduzíveis.
- **Entradas:** Código, artefatos e verificações.
- **Saídas:** Guia de execução, model/data cards e process log atualizado.
- **Arquivos previstos:** docs/; SOLUCAO.md; manifests e arquivos de dependências.
- **Dependências:** F34, F35.
- **Abordagem:** Instruções exatas e resultados medidos; atualizar checkboxes apenas com evidência.
- **Testes:** Outra execução segue o guia sem conhecimento tácito.
- **Critérios de aceite:** Documentação descreve o que existe, não só o desejado.
- **Riscos:** Prometer fases não concluídas.
- [x] **F36.I — Implementação:** guia local, operação/deploy, resultados e auditoria foram atualizados.
- [ ] **F36.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F37 — Implantação

- **Objetivo:** Preparar execução consistente local e ambiente alvo.
- **Entradas:** Build validado e artefatos sanitizados.
- **Saídas:** Serviço local demonstrável; deploy público condicionado ao destino.
- **Arquivos previstos:** backend/app.py; frontend/dist/; SOLUCAO.md.
- **Dependências:** F34, F35, F36.
- **Abordagem:** Mesmo processo serve API/static; saúde/readiness; destino público exige credenciais/acesso/dados adequados.
- **Testes:** Build, rotas diretas, API, restart e ausência de CSV cru.
- **Critérios de aceite:** Demo local acessível e reproduzível; não declarar publicação sem URL verificada.
- **Riscos:** Ambiente efêmero perder SQLite; exposição de dados.
- [x] **F37.I — Implementação:** execução local, readiness e configuração de frontend/API separados foram preparados.
- [x] **F37.A — Checkpoint:** serviço local, API externa CORS-autorizada e build foram exercitados; não há URL pública declarada.

### F38 — Preparação da apresentação

- **Objetivo:** Ensaiar a história executiva.
- **Entradas:** Produto e cenário reproduzível.
- **Saídas:** Roteiro de 12 passos, evidências e fallback.
- **Arquivos previstos:** docs/05-validacao-demo-processo.md; evidências autorizadas.
- **Dependências:** F37.
- **Abordagem:** DIAGNOSE→DESIGN→AUTOMATE→OBSERVE→EXPLAIN→IMPROVE.
- **Testes:** Ensaio com reset não destrutivo, LLM desligado e polling interrompido.
- **Critérios de aceite:** Apresentação prova conexões e limitações sem números fictícios.
- **Riscos:** Depender de cenário cherry-picked sem declarar seleção.
- [x] **F38.I — Implementação:** roteiro executivo e contingências foram documentados.
- [ ] **F38.A — Checkpoint:** executar os testes e confirmar os critérios de aceite.

### F39 — QA final

- **Objetivo:** Encerrar com aceite verificável.
- **Entradas:** Todas entregas P0 e evidências.
- **Saídas:** Checklist final e pendências transparentes.
- **Arquivos previstos:** docs/02-plano-de-implementacao.md; docs/05-validacao-demo-processo.md.
- **Dependências:** F38.
- **Abordagem:** Revisar links, corpus íntegro, build, logs, a11y e origem de cada KPI.
- **Testes:** Percorrer 15 critérios e seis specs; hashes antes/depois.
- **Critérios de aceite:** Somente checks verificados marcados; nenhum push sem autorização.
- **Riscos:** Confundir preparação com conclusão ou esconder bloqueios de dados.
- [x] **F39.I — Implementação:** auditoria final, checklist e evidências executadas foram registrados.
- [x] **F39.A — Checkpoint:** as seis specs foram relidas; hashes, testes, build e smoke test local confirmados; pendências mantidas abertas.

### F40 — O Início narrativo e rede visual viva

- **Objetivo:** dar a uma pessoa não técnica um caminho de entrada e tornar a rede semântica legível sem alterar seu significado.
- **Entradas:** seis specs, catálogo compartilhado, coordenadas e arestas reais do Graph.
- **Saídas:** rota `/#/inicio` com narrativa em primeira pessoa, comando de execução local, roteiro de oito passos, navegação contextual e camada neon reduzível nas arestas.
- **Arquivos previstos:** `frontend/src/main.ts`, `frontend/src/ui.ts`, `frontend/src/views/start.ts`, `frontend/src/views/graph.ts`, `frontend/src/styles.css`, `backend/pipeline.py`.
- **Dependências:** F22, F23, F31, F34.
- **Abordagem:** reutilizar Sigma/Graphology; relações de overview usam cosseno de centroides e continuam marcadas como agregadas; animação é CSS/SVG sobre a geometria retornada, com nós pequenos e pulsantes, seleção que isola vizinhos, arraste individual, transição de entrada/saída, tabela e aviso textual.
- **Testes:** type-check, testes existentes, build Vite e smoke browser em O Início/Graph.
- **Critérios de aceite:** pessoa consegue entender a linha de raciocínio e iniciar a demo sem contexto técnico; não existe o antigo card de checklist; Graph overview tem conexões reais consultáveis, seleção tipo Obsidian, arraste individual e transição de workspace; movimento reduzido desliga o pulso; nenhuma promessa de rede neural interna.
- **Riscos:** brilho ser interpretado como evidência; mitigação por legenda, score/método na tabela e aviso persistente.
- [x] **F40.I — Implementação:** O Início narrativo, comando local, remoção do checklist, navegação inicial, relações agregadas, nós neon, seleção, arraste e transição do workspace foram implementados.
- [x] **F40.A — Checkpoint:** `pnpm run check`, `pnpm test` e `pnpm run build` passaram; a interação Graph foi revisada por agente; smoke browser e QA dedicado de 320px/zoom/reduced-motion continuam no gate G6.

## Gates transversais de implementação

- [x] G1 — CSVs mantêm checksums originais e todo dado derivado tem proveniência.
- [ ] G2 — Métricas/IDs/filtros são compartilhados; deep links sobrevivem a reload.
- [x] G3 — Nenhum join fictício DS1↔DS2; tempos indisponíveis e hipóteses claramente rotulados.
- [x] G4 — Modelo, embeddings, vizinhos e edges são reais; scores não são intercambiáveis.
- [x] G5 — Replay/LLM indisponíveis não impedem usar as outras capacidades disponíveis.
- [ ] G6 — Interface G4 com teclado, contraste e prefers-reduced-motion; grafo tem tabela equivalente.
- [x] G7 — Build/checks passam; roteiro de demo e process log descrevem evidências reais.

## Referências

[Arquitetura](01-arquitetura-compartilhada.md) · [Dados](03-dados-e-metricas.md) · [Design](04-design-e-experiencia.md) · [Validação e demo](05-validacao-demo-processo.md) · [Índice das seis specs](00-indice.md)
