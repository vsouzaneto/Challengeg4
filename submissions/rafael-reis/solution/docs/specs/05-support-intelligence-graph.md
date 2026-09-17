# Spec 05 — Support Intelligence Graph

**Status:** núcleo semântico, Graph, deep links, relações agregadas, alerta→ocorrências, seleção tipo Obsidian, arraste individual e camadas visuais neon implementados; validação humana e fallback visual dedicado permanecem pendentes.
**Rota:** `/#/graph`.
**Pergunta:** como os tickets se relacionam semanticamente, e o que essas relações revelam sobre classificação, incidentes e qualidade dos dados?

O Graph representa embeddings, relações de vizinhança e agrupamentos mensurados. Não representa os neurônios do classificador e não deve ser chamado de “rede neural do modelo”. Compartilha tickets, sessões, versões, filtros e eventos com as demais abas.

Referências normativas: [arquitetura compartilhada](../01-arquitetura-compartilhada.md), [dados e métricas](../03-dados-e-metricas.md), [design e experiência](../04-design-e-experiencia.md).

## 1. Pessoas e decisões apoiadas

- **Analista/gestor:** investigar famílias de problemas, volume, CSAT disponível e oportunidades propostas de automação.
- **Responsável por IA:** localizar baixa confiança, ambiguidade, possível erro de rótulo e limites da taxonomia.
- **Operação durante a demo:** seguir crescimento simulado de grupos, possíveis duplicatas e alertas, com evidências acessíveis.

O sistema deve permitir responder às dez perguntas semânticas do briefing: famílias naturais; aderência da taxonomia; possíveis subcategorias; possíveis rótulos inadequados; duplicatas; ambiguidade; dificuldades do classificador; baixa confiança; volume; potencial de automação. Cada conclusão exige amostra, método e links para tickets. Para DS1, a análise de CSAT informa sua cobertura. TTR e combinações com TTR permanecem indisponíveis enquanto não houver durações válidas.

## 2. Pipeline e escolha técnica

`texto permitido → SentenceTransformers → embedding normalizado → FAISS IndexFlatIP → vizinhos/kNN → agrupamento validado → projeção UMAP → artefatos → visualização`.

- **SentenceTransformers:** um modelo explicitamente versionado; não incluir resolução, CSAT ou rótulo alvo no texto usado para avaliar a classificação. A composição do texto de cada corpus pertence ao manifesto.
- **FAISS IndexFlatIP:** busca exata inicial com vetores normalizados; permite conferir os scores e evita introduzir tuning de busca aproximada antes de medições de necessidade.
- **HDBSCAN:** escolha inicial para grupos e ruído, com parâmetros validados no espaço original ou em redução intermediária cuja qualidade seja medida. A projeção UMAP bidimensional é visualização; não deve determinar clusters sem validação específica.
- **UMAP:** coordenadas persistidas por versão e seed. A proximidade na tela é uma aproximação; a evidência de uma edge é seu score original.
- **Sigma.js + Graphology:** escolha de frontend para renderização e manipulação do grafo, integrada ao shell HTML/CSS/TypeScript com Vite. Não adicionar outro motor gráfico para o mesmo fluxo.
- **Leiden/Louvain:** alternativas P2 somente se avaliação demonstrar que a estrutura de comunidades no kNN atende melhor ao corpus. Não executar todos os métodos apenas para multiplicar controles.

Separar espaços DS1 e DS2. Um modelo de embedding compartilhado não cria uma chave de junção entre datasets. Fixar `dataset_id`, hash da entrada, `space_id`, modelo, pré-processamento, parâmetros, seeds, limites e versões no manifesto de artefatos.

A auditoria DS1 encontrou placeholders em todos os textos de descrição. Conferir se vizinhos/grupos refletem o problema descrito ou repetição de template; registrar o tratamento aplicado e exemplos de limitações. O conteúdo é proveniente do arquivo público, sem garantia adicional de representar uma operação de produção validada.

## 3. Semântica visual

| Elemento | Significado obrigatório |
|---|---|
| Nó de ticket | Um ticket histórico ou uma ocorrência da sessão; a legenda distingue os tipos. |
| Nó agregado | Um cluster/subcluster identificado; o rótulo e a contagem mostram que não é um ticket individual. |
| Posição | Projeção do embedding; posição aproximada não é prova de categoria, causalidade ou duplicidade. |
| Aresta entre tickets | Relação kNN que passou pela regra documentada; origem/destino, score e limiar são consultáveis. |
| Peso da aresta | Similaridade calculada no espaço original; espessura possui escala declarada. |
| Aresta agregada | Relação entre grupos baseada em vizinhanças observadas; apresentar a agregação, nunca tratá-la como comparação direta de dois tickets. |
| Cor | Campo escolhido no modo atual; ausente/indisponível tem estilo próprio e legenda textual. |
| Tamanho | Em agregados, volume por escala declarada; em tickets, tamanho uniforme por padrão. Destaque de seleção não altera o significado da métrica. |
| Cluster | Grupo produzido pelo método/versão; não equivale à categoria oficial. Ruído permanece sem grupo. |
| Destaque de alerta | Condição registrada com tipo e evidências; texto/ícone sempre acompanham a cor ou o brilho. |

Categorias oficiais, previsão e nome editorial de cluster são campos diferentes. Nome sugerido para um grupo exige exemplos representativos; não transformar automaticamente o nome em novo rótulo supervisionado.

## 4. Hierarquia, navegação e limites

1. **Visão geral:** clusters principais e painel de resumo do corpus selecionado.
2. **Grupo:** subclusters apenas quando há estrutura medida e estável; caso contrário, abrir diretamente a lista de tickets daquele cluster. Não fabricar níveis “Access → Authentication → Password Reset”.
3. **Tickets:** amostra/recorte limitado, vizinhos e detalhes com tabela paginada da população completa.

Zoom pode aumentar o detalhe quando há dados carregados; breadcrumb e comandos explícitos oferecem a mesma navegação sem gestos. Filtros são aplicados ao recorte consultado e não recalculam embeddings ou clusters silenciosamente. Mostrar contagem total, elegível e exibida.

**Budgets iniciais propostos, a medir na máquina alvo:** até 100 agregados por vista, até 100 subgrupos por vista, até 200 tickets e 1.500 arestas na vista detalhada. Se o recorte exceder o orçamento, manter agregação, paginar a lista e explicar a seleção dos nós exibidos. Nunca enviar/renderizar os 56.306 registros de origem simultaneamente. Não denominar uma amostra limitada como população completa.

Cada drill-down conserva `dataset_id`, `source`, `space_id`, `session_id`, `ticket_id`, `cluster_id`, `alert_id`, `model_version` e filtros compatíveis. Um filtro inválido no destino é removido com aviso; contexto inexistente mostra erro recuperável, sem foco em um cluster aleatório.

## 5. Modos e prioridades

| Modo | Prioridade | Fonte, limitações e evidência |
|---|---|---|
| Estrutura semântica | P0 | Grupos, ruído, vizinhanças reais e medidas de similaridade. |
| Categoria | P0 | DS2 `Topic_group` observado versus previsto; DS1 `Ticket Type` possui outra taxonomia. |
| Confiança do modelo | P0 | Inferências reais da sessão ou avaliação identificada; não comparar confiança de treino com resultado fora da amostra. |
| Possíveis duplicatas | P0 | Candidatos acima de limiar validado; distinguir conteúdo exatamente igual e similaridade semântica. |
| Revisão humana | P0 | Decisões e motivos da política compartilhada. |
| Volume | P0 | Contagens históricas e ocorrências simuladas separadas; denominador e janela visíveis. |
| Prioridade | P1 | Observada DS1 ou sugerida por política DS2; nunca misturar as duas origens na mesma legenda. |
| CSAT | P1 | Somente DS1 e registros com nota; mostrar quantidade e cobertura, não imputar ausência como zero. |
| Possível rotulagem inadequada | P1 | Discordância entre rótulo, vizinhos e previsão fora da amostra; é candidato à revisão, não erro confirmado. |
| Oportunidade de automação | P1 | Regra explícita e versionada, com evidência/cobertura e hipótese de esforço quando usada. |
| Possível incidente emergente | P0 | Janela/relógio de simulação, grupo, contagem, similaridade e regras do alerta. |
| Tempo de resolução | P2 condicional | Bloqueado nos arquivos atuais: timestamps sem início não permitem TTR. Habilitar apenas com fonte validada de duração. |

Modos indisponíveis devem explicar o motivo; não gerar valores fictícios para completar o seletor. DS2 não possui CSAT, tempo ou prioridade observada.

## 6. Contratos e estado

Consultas propostas: `GET /api/spaces/{space_id}/graph` para níveis/recortes e consulta de detalhes de ticket/cluster segundo a arquitetura compartilhada. O backend entrega somente o recorte solicitado e limites efetivos.

O envelope inclui `space_id`, versões, origem, filtros aplicados, nível, contagens totais/exibidas, motivo de truncamento, `nodes`, `edges` e legenda. Nós incluem ID, tipo, coordenadas, cluster, atributos disponíveis e origem. Edges incluem IDs de extremidades, peso, método e se são agregadas. Métricas ausentes carregam motivo.

- ID histórico DS1: `ds1:<Ticket ID>`; DS2: `ds2:<sha256 do texto normalizado>`. A contagem de linhas originais e a de textos únicos são distintas; duplicação física do DS2 não deve criar IDs colidentes.
- Ocorrência de sessão: `session:<uuid>:<uuid>`, com `source_ticket_id` quando reproduz um histórico. Ocorrências diferentes podem apontar ao mesmo conteúdo sem esconder o fato.
- `cluster_id` pertence a uma versão de `space_id`. Após reconstrução dos artefatos, rejeitar deep link incompatível ou oferecer a nova visão geral; não reutilizar um número de cluster como se fosse identidade permanente.
- O snapshot de sessão informa `last_seq`. Depois dele, consumir `GET /api/sessions/{session_id}/events?after_seq=...`; aplicar eventos por sequência e ID, sem duplicações. Polling compartilhado começa com candidato de 1 segundo e backoff em falhas.
- Seleção, câmera e filtros pertencem ao estado da view; evidências e métricas pertencem ao backend/artefatos. O browser não recompõe a base inteira a cada evento.

## 7. Entrada de tickets e explainability

Para tickets do Ticket Lab: carregar resultado persistido, verificar `space_id`, inserir o nó da ocorrência, revelar os vizinhos/arestas reais, focar o ticket e abrir painel com categoria, confiança, prioridade/rota de política, duplicidade candidata, cluster e scores.

Para replay: utilizar embeddings, vizinhos, associação e coordenadas persistidos quando `inference_mode=precomputed`. O efeito de chegada é novo na sessão; o cálculo semântico não é apresentado como executado ao vivo. Incluir ligação da ocorrência ao registro histórico, mas não tratar sua própria referência histórica como duplicata detectada. A busca pode consultar base imutável e overlay autorizado da sessão, excluindo o próprio ticket.

Para texto manual: gerar embedding online e obter vizinhos reais. Projetar pelo transform persistido do redutor, quando suportado e validado. Fallback explícito pode posicionar o nó junto aos vizinhos por uma regra determinística; nesse caso rotular “posição aproximada a partir dos vizinhos”. Não refazer o UMAP completo a cada chegada. Ausência de vizinhos confiáveis leva a área de itens não associados.

A animação apenas revela esses resultados. Não interpolar uma narrativa de aprendizado do modelo, inventar conexões ou prometer explicação causal da classificação. `prefers-reduced-motion` apresenta o estado final sem deslocamento; o painel textual informa a chegada e suas evidências.

## 8. Estados, acessibilidade e desempenho

Prever carregamento, corpus vazio, filtro sem resultados, artefato ausente, link inválido, grupo sem subclusters, ruído, servidor indisponível e replay desconectado. Conservar a última visão válida com horário de atualização quando o polling falhar; a consulta histórica continua utilizável.

Canvas não substitui conteúdo acessível. Entregar lista/tabela equivalente de grupos, tickets e arestas relevantes, controle de busca, seleção por teclado, breadcrumbs, botões de zoom/foco, painel com títulos e legenda que não depende apenas de cores. Não anunciar cada frame nem tomar foco durante o replay. Eventos podem ser resumidos em região de status e consultados em lista.

Carregar o motor de grafo quando a aba for aberta. Usar dados agregados offline, limitar arestas e atualizar apenas nós/contadores alterados. Medir tempo para primeira interação, tamanho transferido, estabilidade do navegador e consumo de memória nos orçamentos propostos antes de aumentá-los.

## 9. Checkpoints de implementação

Os checkpoints de fluxo integrado abaixo são P0, incluindo reação ao replay, ticket manual e alerta navegável. Somente os modos adicionais identificados como P1/P2 na tabela ficam para aprofundamento posterior.

- [x] Produzir manifesto, embeddings, índice, vizinhos, clusters, ruído e projeção por corpus/versão.
- [ ] Validar a qualidade dos vizinhos e agrupamentos com amostras e métricas apropriadas, documentando limitações.
- [x] Expor recortes hierárquicos, métricas disponíveis e limites no backend.
- [x] Implementar Sigma.js/Graphology, seleção, modos de cor, legenda, detalhe e tabela acessível.
- [x] Adicionar pulso visual reduzível nas arestas reais e relações agregadas entre grupos por cosseno de centroides; scores e método permanecem consultáveis na tabela.
- [x] Adicionar nós neon pequenos com movimento individual sutil, seleção tipo Obsidian, restauração pelo segundo clique/fundo e arraste individual preservado durante o polling.
- [x] Adicionar entrada/saída animada do workspace Graph com fallback sem animação quando o navegador não oferece View Transitions ou quando o usuário reduz movimento.
- [ ] Entregar todos os modos P0 com origem e evidência; bloquear modos sem dados.
- [x] Restaurar contexto por URL e abrir o ticket recém-analisado com scores reais.
- [x] Consumir eventos de sessão de forma incremental, idempotente e recuperável.
- [x] Abrir alertas do Command Center com cluster e ocorrências correspondentes destacadas.
- [ ] Implementar modos P1 após a base; medir limites antes de ampliar o recorte.
- [ ] Validar movimento reduzido, navegação por teclado e fallback sem atualizações ao vivo.

Arquivos previstos: `scripts/build_semantic.py`, `artifacts/<versao>/`, `backend/app.py`, `backend/pipeline.py`, `backend/sessions.py` e `frontend/src/views/graph.ts`. Fases relacionadas: F11–F16, F19, F22–F25, F29–F31 e F34–F35.

## 10. Testes e aceite

1. Selecionar uma edge: o score coincide com a busca vetorial e os IDs existem no corpus/espaço correto.
2. Alternar categoria e confiança: legenda muda corretamente, rótulo observado não vira previsão e ausência não vira zero.
3. Abrir cluster sem subclusters e ticket classificado como ruído: ambos mantêm navegação e explicação coerentes.
4. Seguir Ticket Lab → Graph e alerta → Graph: mesmos IDs, sessão e versões, com as ocorrências corretas destacadas e restauradas por recarga.
5. Reentregar um evento e desconectar/reconectar: nenhum nó ou contador duplicado; o snapshot reconcilia lacunas.
6. Verificar os limites por nível e uma base com mais registros que o orçamento: o navegador recebe recorte limitado e a população continua consultável em tabela.
7. Usar DS1: CSAT tem cobertura visível e TTR fica indisponível; usar DS2: não surgem métricas operacionais inexistentes.
8. Ligar movimento reduzido e usar somente teclado/tabela: a mesma evidência e navegação continuam acessíveis.
9. Produzir vizinhança ambígua ou sem similaridade suficiente: o sistema não inventa cluster, confiança ou arestas.

## 11. Riscos

Projeções podem distorcer distâncias; destacar scores originais. Grupos dependem de parâmetros; documentar estabilidade e ruído antes de atribuir significado. Nomes de clusters podem sugerir certeza excessiva; apresentar exemplos e método. Exibir muitos nós/arestas prejudica compreensão e desempenho; respeitar divulgação progressiva. Sem séries temporais reais, crescimento e incidentes são evidências da simulação, nunca confirmação de incidente histórico ou de produção.
