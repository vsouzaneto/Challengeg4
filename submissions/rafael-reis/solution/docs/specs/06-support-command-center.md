# Spec 06 — Support Command Center

**Status:** núcleo de sessão, replay, métricas, alertas e navegação implementado; ensaio de reconexão, duas abas e trilha visual completa permanecem pendentes.  
**Rota:** `/#/command-center`.  
**Pergunta:** o que está acontecendo agora na demonstração da operação e da IA, com quais evidências e limitações?

O Command Center consolida a mesma sessão, tickets, decisões e artefatos utilizados nas demais abas. Operational Diagnosis aprofunda o histórico; esta aba observa o processamento, a saúde da automação, o modelo e os sinais semânticos. Não substitui nem recalcula uma segunda versão do diagnóstico.

Referências normativas: [arquitetura compartilhada](../01-arquitetura-compartilhada.md), [dados e métricas](../03-dados-e-metricas.md), [design e experiência](../04-design-e-experiencia.md).

## 1. Pessoas, hierarquia e estado compartilhado

- **Gestor de suporte:** enxergar volume, revisão humana, oportunidades e limites da evidência.
- **Responsável por IA:** inspecionar confiança, latência, versão, overrides e erros de processamento.
- **Apresentador/avaliador:** executar replay com conteúdo histórico real, acompanhar eventos e abrir sua evidência.

Hierarquia visual: estado/alertas críticos → controles da sessão → indicadores essenciais → automação e modelo → inteligência semântica → tendências e decisões recentes. Usar o sistema visual G4 definido na documentação compartilhada, evitando exibir todos os indicadores com o mesmo peso.

Seletores de origem e corpus são explícitos. `historical`, `simulation`, `user_created` e `model_evaluation` não entram em um mesmo denominador sem uma combinação deliberada, rotulada e decomposta. Um ticket manual adicionado à sessão de replay mantém a origem manual.

## 2. Saúde operacional: o que pode ser mostrado

| Indicador solicitado | Definição implementável e limite atual |
|---|---|
| Tickets recebidos | Histórico: total do recorte, sem taxa temporal de chegada. Replay: ocorrências `TICKET_ARRIVED` na janela de simulação. Manual: novas entradas explicitamente incluídas. |
| Tickets abertos/resolvidos | DS1: distribuição observada de `Ticket Status`, um retrato do arquivo; “Closed” não prova quando houve resolução. DS2 e replay de chegadas não fornecem ciclo operacional. |
| Backlog | DS1: se exibido, “não encerrados no retrato histórico”, com regra de status declarada. Não confundir com fila de processamento IA nem apresentar como backlog atual de produção. |
| First Response Time | Indisponível como duração nos arquivos atuais: coluna contém timestamp e não há início do atendimento. |
| TTR mediano/p90 | Indisponíveis: `Time to Resolution` contém timestamp, sem `created_at` que permita calcular a duração total. Não subtrair hora do dia nem assumir data de compra como abertura. |
| CSAT | DS1, apenas notas presentes; mostrar N elegível e cobertura. Há 2.769 registros com CSAT/resolução na auditoria inicial, de 8.469 linhas. Replay não cria novo CSAT. |
| Volume/distribuição de categoria | DS2: categoria observada histórica ou prevista pelo modelo, claramente diferenciadas. DS1: `Ticket Type`, outra taxonomia. |
| Canal/prioridade | Observados no DS1. DS2 não possui esses atributos; prioridade por política aparece como sugestão, canal fica indisponível. |

O replay demonstra chegadas e processamento IA. Ele não resolve tickets, não gera TTR e não reduz um backlog de atendimento por terminar a classificação. Exibir separadamente **na fila de IA**, **em processamento**, **processados com sucesso**, **parciais** e **falhas**.

A auditoria DS1 identificou ainda 1.365 dos 2.769 registros com resolução datada antes da primeira resposta, além de placeholders nas descrições. Não derivar uma duração alternativa pela subtração desses campos nem denominar o arquivo como evidência operacional de produção validada. No replay, “real” significa conteúdo efetivamente presente no dataset, não comprovação de um atendimento real.

Os 47.837 registros originais DS2 não possuem tempo, ID nativo, resolução ou CSAT. Contagens de linhas e textos únicos devem seguir o manifesto da preparação; não pressupor que todo registro corresponde a conteúdo único.

## 3. Saúde de automação e métricas do modelo

Todo card informa origem, janela, numerador/denominador quando for taxa, versão e atualização. Ausência de amostra é “sem dados”, nunca 0%.

Uma decisão de triagem é elegível quando o resultado está `processing_status=complete`, foi produzido pela política (`decision_origin=policy_suggested`) e contém `suggested_route`. Resultados parciais ficam fora desse denominador e aparecem como ocorrências processadas, mas não como decisões automáticas.

| Indicador | Regra |
|---|---|
| Triagem sem revisão | Decisões de política sem revisão ÷ decisões de triagem elegíveis. A UI chama isso de “Triagem sem revisão”; indicar “na demonstração” e não afirmar envio a fila externa. |
| Revisão humana | Decisões que exigem revisão ÷ decisões de triagem elegíveis. Pode sobrepor baixa confiança; não somar taxas como categorias exclusivas. |
| Baixa confiança | Predições abaixo do limiar daquela versão ÷ predições válidas do mesmo modelo/domínio. |
| Respostas sugeridas | Tickets com sugestão realmente gerada/recuperada ÷ tickets elegíveis para o Copilot; faltas e indisponibilidade têm motivos. |
| Aceitas/editadas/rejeitadas | Contagens e taxas pela última decisão efetiva por sugestão/versão entre as que receberam feedback; exibir também sem feedback. Histórico preserva revisões, sem somá-las como sugestões diferentes. Feedback não é resolução do ticket. |
| Duplicatas candidatas | Ocorrências com candidato conforme política ÷ ocorrências avaliadas para duplicidade; não declarar duplicatas confirmadas. |
| Oportunidade de automação | Regra explícita da aba Strategy, com elegibilidade e exclusões; oportunidade não equivale a economia realizada. |
| Esforço/ROI estimados | Cenário parametrizado por usuário, com unidade, custo/hora, minutos por tarefa, adoção, revisão e custo da solução; sem valor padrão de salário apresentado como fato. |
| Versão/amostras de treino | Manifesto do classificador carregado, com exclusões e hash/split. |
| Macro F1, accuracy, F1 por categoria | Somente artefato de avaliação fora da amostra, com suporte e split. Não recalcular com previsões sem rótulo verdadeiro. |
| Confiança média/distribuição | Escore e estado de calibração identificados; separar inferências online de replay pré-calculado e de avaliação. |
| Human override | Tickets em que uma decisão humana registrada divergiu da previsão ÷ tickets com revisão humana válida e comparável. Editar texto no Copilot não é override de classe. |
| Latência | Tempo medido por etapa/total. Execução online e leitura de artefato pré-calculado ficam em séries diferentes. |
| Distribuição de predições | Contagem de categorias previstas em uma população identificada; não é distribuição de rótulos verdadeiros. |
| Confusion hotspots | Pares de erro da matriz de confusão do teste; sessão sem rótulos não gera essa métrica. |

Variação simples de distribuição pode ser exibida como mudança observada. **Drift** fica em P2 e exige referência, método, janela, tamanho de amostra e política de alerta validados. Não denominar movimento no gráfico como drift.

## 4. Live Replay: fluxo e controles

Banner persistente: **LIVE REPLAY — Simulação com dados históricos**. No detalhe: **conteúdo histórico real; ordem e horários de chegada simulados**. O cenário de concentração usa adicionalmente **CENÁRIO DE INCIDENTE SIMULADO**.

1. Escolher corpus, tamanho do lote e cenário. Começar com candidato de 50 tickets; habilitar 100/500 após medição. A lista de IDs, seed, versão e agenda ficam registradas.
2. Criar sessão com identificador próprio, artefatos fixados e estado `STOPPED`.
3. Acionar **Play**: backend avança a agenda; os controles não dependem de uma aba permanecer aberta.
4. Ajustar **Speed** entre 1×, 2×, 5× e 10×. Velocidade altera o relógio de chegada simulado, não fabrica latência real nem supera sem limite a capacidade do processamento.
5. **Pause** suspende novas chegadas e congela o relógio de simulação. Processamentos já iniciados podem terminar; explicar esse comportamento.
6. **Play** em sessão pausada retoma do próximo item. Repetir a requisição não cria outro produtor.
7. **Completed** ocorre somente quando todas as chegadas previstas foram emitidas e não resta processamento pendente; falhas/parciais aparecem no balanço final.
8. **Reset** cria uma nova sessão com os mesmos parâmetros; conserva a anterior e seus eventos. Não exclui logs nem altera CSVs. Ao trocar a sessão ativa, interromper novas chegadas da anterior conforme transição registrada.

| Estado | Ações válidas |
|---|---|
| `STOPPED` | Play, ajustar parâmetros/speed, criar novo cenário. |
| `PLAYING` | Pause, ajustar speed, Reset para nova sessão. |
| `PAUSED` | Play, ajustar speed, Reset para nova sessão. |
| `COMPLETED` | Consultar evidência, Reset para nova sessão; não reexecutar silenciosamente os mesmos IDs. |

Exibir sessão, cenário, estado, total previsto, chegadas, processados, fila IA, relógio de simulação, conexão e versão. A reconexão do browser restaura a sessão pelo backend. Após reinício do processo servidor, uma sessão antes ativa deve exigir retomada controlada a partir do checkpoint; não reiniciar do começo sem indicação.

## 5. Processamento, eventos e persistência

Reutilizar `backend/pipeline.py`. O histórico pode usar embeddings, classificação, vizinhos, projeção e associação de cluster persistidos quando a versão confere. Para entrada manual, executar inferência e embedding reais. Mostrar `inference_mode=precomputed|online` na evidência e em agregações relevantes.

Etapas previstas: `TICKET_ARRIVED → CLASSIFICATION_STARTED → CLASSIFICATION_COMPLETED → EMBEDDING_CREATED → NEIGHBORS_FOUND → DUPLICATE_ANALYSIS → PRIORITY_ANALYSIS → ROUTING_DECISION → HUMAN_OR_AUTO_DECISION → GRAPH_NODE_CREATED → DASHBOARD_UPDATED`. Recuperação e geração de sugestão são opcionais.

Esses nomes representam fatos/estágios auditáveis, não autorização para inventar processamento. Uma etapa carregada de artefato informa `inference_mode=precomputed`, origem do artefato e tempo de leitura; uma capacidade DS1 não suportada fica `skipped` com motivo, não produz classificação DS2 fictícia. Falhas geram estado explícito e não emitem sucesso posterior inexistente.

O evento segue o contrato compartilhado: `event_id`, `session_id`, `seq` monotônico, `ticket_id`, `source_ticket_id` se histórico, `event_type`, `occurred_at` de execução, `simulation_time` quando houver, `source`, `content_origin`, `dataset_id`, `space_id`, `model_version`, `policy_version`, `inference_mode` e payload específico. `occurred_at` não substitui tempo histórico ausente; `simulation_time` não mede latência de modelo.

Persistir sessões, ocorrências, eventos e feedback em SQLite local. Eventos são imutáveis. Identidades idempotentes e a transação de evento/progresso impedem que retry some duas vezes; snapshots podem ser reconciliados com o log. Modelo e índice ficam carregados no backend, não no navegador.

### Transporte escolhido

Usar snapshot + **polling incremental**, suficiente como primeira solução para a demonstração local. Candidato inicial: uma consulta por segundo enquanto a sessão estiver ativa, com backoff em falhas e consultas menos frequentes em repouso. Um consumidor compartilhado no shell atualiza Graph e Command Center.

- `GET /api/sessions/{session_id}/snapshot` retorna estado consolidado e `last_seq` de uma visão consistente.
- `GET /api/sessions/{session_id}/events?after_seq=...` retorna eventos ordenados posteriores ao cursor, respeitando limite/paginação e próximo cursor.
- Cursor só avança após aplicar eventos válidos; duplicatas são ignoradas por identidade/seq. Lacuna ou incompatibilidade pede snapshot e reconciliação.
- `POST /api/sessions` cria a sessão; `POST /api/sessions/{session_id}/control` executa os comandos e retorna o estado autoritativo. Reset retorna a identidade de uma nova sessão.

Não introduzir WebSocket/SSE em P0. Reavaliar SSE somente se medições demonstrarem que latência ou custo do polling impedem os critérios de aceite. Manter o contrato de eventos independente do transporte.

## 6. Alertas semânticos e drill-down

| Alerta | Evidência mínima e restrição |
|---|---|
| Crescimento de grupo | Cluster versionado, contagem/janela atual e referência explícita; origem/relógio visíveis. |
| Rajada de possíveis duplicatas | IDs das ocorrências e origem histórica, regra, quantidade, janela e scores. Repetições do mesmo conteúdo devem ser identificadas. |
| Possível rotulagem inadequada | Rótulo observado, previsão elegível e vizinhos; hipótese de revisão, não erro confirmado. |
| Baixo CSAT | DS1, N com nota, cobertura, regra e comparação; não gerar para DS2. |
| Baixa confiança | Modelo, limiar, quantidade elegível e exemplos. |
| Oportunidade de automação | Regra da Strategy, elegibilidade, exclusões e suposições de esforço. |
| Possível incidente emergente | Concentração semântica por janela simulada em **passos ordinais**, contagem, similaridade e grupo; nenhum claim de incidente real. |
| TTR elevado | Indisponível nos dados atuais; futuro somente com duração válida. |

Os thresholds são candidatos de demonstração até avaliação. Registrar política, tamanho mínimo, janela, cooldown e limites antes do cenário; não ajustar invisivelmente o critério para garantir o alerta. Cenários de concentração selecionam tickets reais semanticamente próximos, com seed e IDs auditáveis. Contar também `source_ticket_id` únicos: repetir a mesma fonte não pode inflar a evidência de incidência. Cenário misto de comparação ajuda verificar excesso de alertas, sem transformar essa comparação em prova estatística de produção.

O mesmo incidente em uma janela não deve gerar um card novo a cada atualização: manter `alert_id`, agregar novas evidências e preservar seu histórico. Se houver baseline insuficiente, mostrar “concentração no cenário” em vez de afirmar crescimento anormal.

Todo KPI acionável abre evidência: baixa confiança → lista filtrada; overrides → decisões humana/modelo; alerta → `/#/graph` com `space_id`, `cluster_id`, `alert_id`, sessão e ocorrências; oportunidade → `/#/automation` com regra/filtros; métrica histórica → `/#/diagnosis`. Card indisponível abre sua explicação. Não usar clique decorativo nem perder origem ao navegar.

## 7. Interface, falhas e acessibilidade

Estados necessários: sem sessão; carregando snapshot; parado; rodando; pausado; completo; sem amostra; erro parcial; desconectado; versão incompatível; serviço de LLM indisponível. Preservar números com indicação de desatualização enquanto a reconexão ocorre. Não trocar a ausência por zero.

Reprodução é opcional para o restante do produto: Diagnosis, Strategy, Ticket Lab, Copilot com recuperação histórica, Graph histórico e métricas de avaliação continuam disponíveis. Sem LLM, manter recuperação e sugestão extrativa rastreável quando as fontes forem suficientes; caso contrário, declarar evidência insuficiente. Feedback só incide sobre sugestão existente.

Botões nativos rotulados, foco visível, status textual, tabelas para séries/decisões e unidades em todos os indicadores. Respeitar movimento reduzido; atualizações automáticas não deslocam foco. Resumir mudanças em região de status sem anunciar cada evento. Permitir pausar a exibição de atualizações para leitura sem confundir com pausa do replay.

## 8. Prioridades e checkpoints

**P0-a — cockpit mínimo consistente**

- [x] Implementar snapshot/eventos, persistência, identidades e cursores compartilhados.
- [x] Exibir disponibilidade real de métricas, origens, versões e evidências.
- [x] Exibir estado/controle de sessão e replay histórico com Play/Pause/Reset/Speed.
- [x] Atualizar contadores/distribuições de forma incremental e idempotente.
- [ ] Separar fila IA, status histórico e backlog; separar latência online e leitura pré-calculada.
- [x] Abrir tickets e Graph com os mesmos IDs; manter consultas úteis com replay indisponível.

**P0-b — segunda etapa do núcleo integrado obrigatório**

- [x] Integrar chegada/atualização do Graph e entrada manual opcional do Ticket Lab.
- [x] Registrar feedback do Copilot, triagem e revisão humana com denominadores elegíveis explícitos.
- [x] Implementar cenário de concentração semântica com alertas e evidência reproduzível.
- [x] Abrir alerta no cluster e destacar exatamente as ocorrências envolvidas.
- [x] Implementar cenários de esforço/ROI com parâmetros visíveis e sem alegação de economia realizada.
- [ ] Verificar reconexão, reinício controlado e ausência de duplicações.

**P1 — aprofundamento após a demonstração integrada**

- [ ] Ampliar a inspeção de tendências e distribuições para diferentes janelas, mantendo as mesmas regras de origem/denominador.
- [ ] Expor análise detalhada dos parâmetros de cenário e resultados de revisão para comparação manual entre sessões.

**P2 — condicionado a dados/necessidade medidos**

- [ ] Introduzir drift apenas com metodologia e amostra de referência.
- [ ] Considerar SSE se polling falhar nos requisitos medidos.
- [ ] Acrescentar ciclo operacional/TTR apenas após dados de abertura/resolução válidos.

Arquivos previstos: `backend/sessions.py`, `backend/pipeline.py`, `backend/app.py`, `artifacts/<versao>/` e `frontend/src/views/command.ts`. Fases relacionadas: F25–F33, F34–F35 e F38–F39. P0-a/P0-b são etapas do mesmo núcleo obrigatório; o aceite não se encerra antes de sua integração.

## 9. Testes e aceite

1. Iniciar replay com IDs realmente existentes nos datasets; conferir banner de simulação, sequência reproduzível e origem de cada conteúdo.
2. Play repetido não duplica produtor; Pause congela novas chegadas; Speed altera agenda; Completed aguarda escoar fila; Reset cria outro ID sem apagar o log anterior.
3. Reentregar eventos, abrir duas abas, desconectar e reconectar: contadores e nós continuam consistentes com o snapshot e sem duplicidade.
4. Concluir classificação de um ticket: aumenta processados IA, não aumenta tickets resolvidos nem fabrica TTR/CSAT.
5. Criar ticket manual na sessão: inferência online e embedding reais, origem manual preservada e mesma ocorrência disponível no Graph.
6. Rodar cenário de concentração com regra declarada: alerta mostra janela, IDs e evidência; clicar abre o cluster/ocorrências correspondentes. Um resultado sem alerta também é reportado honestamente.
7. Comparar cada taxa com seus eventos elegíveis e denominador; amostra vazia retorna indisponível e não 0%/100%.
8. Conferir métricas de modelo com o artefato de avaliação e hashes; versão de tela não pode diferir da versão executada.
9. Desativar LLM e interromper polling: as capacidades independentes continuam utilizáveis; avisos não ocultam evidências históricas já carregadas.
10. Executar por teclado/movimento reduzido, inspecionar tabelas e conferir hashes dos CSVs antes/depois da sessão.

## 10. Riscos e limites assumidos

Simulação pode parecer produção; manter origem persistente em cards, alertas e exportações. Um replay pré-calculado pode parecer inferência online; separar tempos/modos. Contadores inconsistentes em retries podem destruir a credibilidade da demo; persistir e reconciliar por evento. O processo único local é o limite inicial: não prometer concorrência de produção, alta disponibilidade ou recuperação distribuída. Configurar tamanho/velocidade conforme medições e admitir fila crescente em vez de descartar tickets silenciosamente. A ausência de duração operacional é uma limitação dos dados, não um motivo para gerar números demonstrativos.
