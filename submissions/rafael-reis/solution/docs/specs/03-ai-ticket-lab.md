# Spec 03 — AI Ticket Lab

**Status:** núcleo implementado e exercitado com inferência online, idempotência e navegação para o Graph.  
**Rota:** `/#/ticket-lab`.  
**Pergunta:** a IA consegue interpretar um ticket novo e mostrar evidências da decisão?

Esta aba é a entrada manual do mesmo pipeline utilizado pelo replay, Graph e Command Center. Os resultados pertencem a tickets identificados, persistidos e consultáveis; não existem respostas demonstrativas fixas.

Referências normativas: [arquitetura compartilhada](../01-arquitetura-compartilhada.md), [dados e métricas](../03-dados-e-metricas.md), [design e experiência](../04-design-e-experiencia.md).

## 1. Pessoas, resultado e limites

- **Analista de suporte:** informar uma solicitação, entender categoria sugerida, rota, prioridade e necessidade de revisão.
- **Gestor:** verificar evidências de automação em texto não escolhido previamente pela equipe.
- **Avaliador técnico:** reproduzir a inferência com versão, latência e vizinhos verificáveis.

O classificador supervisionado inicial utiliza `Document → Topic_group` do Dataset 2. Sua saída tem oito categorias conforme o artefato treinado. O DS2 não possui rótulos de prioridade, rota, resolução ou CSAT; prioridade e rota são sugestões de uma política explícita e versionada. A classificação DS2 não deve ser apresentada como classificação validada de tickets do DS1.

O DS1 pode ser escolhido para busca semântica e posterior recuperação de resoluções. Nessa opção, a classificação de oito categorias fica indisponível até existir avaliação específica desse uso. Campos sem suporte têm valor nulo e motivo, nunca valores de preenchimento.

## 2. Fluxo principal

1. Abrir com `dataset_id`, `space_id` e contexto compatível da navegação; mostrar o corpus que será consultado e o domínio suportado pelo modelo.
2. Digitar texto livre; exemplo clicável apenas preenche a entrada e continua sujeito ao pipeline real.
3. Opcionalmente ativar **Adicionar à sessão ativa**, exibindo o identificador e a origem daquela sessão. Sem sessão ativa, oferecer criação explícita de uma sessão de demonstração.
4. Enviar uma vez. Validar texto e limite de tamanho no cliente e no servidor; não aceitar entrada vazia após normalização. Um limite inicial de 10.000 caracteres é uma proposta de proteção, ajustável ao tokenizer e documentado no manifesto.
5. Criar a análise com identidade persistente, classificar quando suportado, gerar embedding, consultar FAISS, avaliar duplicidade, associação semântica, prioridade e rota, e aplicar a política de revisão humana.
6. Exibir resultados disponíveis e erros por etapa. Falha de busca não deve apagar uma classificação já calculada; a decisão final indica processamento parcial e revisão necessária.
7. Abrir **Ver na rede semântica**, **Abrir no Copilot** ou evidência de um vizinho mantendo o mesmo ticket e suas versões.
8. Se incluído na sessão ativa, o mesmo resultado alimenta eventos e contadores. Navegar entre abas não realiza uma segunda inferência nem conta o ticket novamente.

Toda análise manual é persistida em uma sessão sandbox e continua recuperável por ID, mesmo sem **Adicionar à sessão ativa**. A opção controla sua publicação nos eventos/métricas da sessão de demonstração, sem criar uma segunda análise nem reclassificar o mesmo resultado. A associação à sessão é registrada no backend; não é um contador exclusivo do navegador.

## 3. Contrato funcional

O endpoint proposto é `POST /api/tickets/analyze`, definido em conjunto com o contrato compartilhado. A requisição inclui `request_id` idempotente, `text`, `dataset_id`, `space_id`, `session_id` quando aplicável e `add_to_live_session`.

| Campo de saída | Semântica e regra |
|---|---|
| `ticket_id`, `session_id` | Identidade de ocorrência `session:<uuid>:<uuid>` e sessão de persistência; reutilizadas em todas as abas. |
| `source`, `source_ticket_id` | `user_created`; sem vínculo histórico artificial. Um texto manual igual a um histórico continua uma ocorrência nova. |
| `dataset_id`, `space_id` | Corpus de busca e versão do espaço semântico; o ticket não altera os CSVs. |
| `predicted_category` | Categoria do classificador realmente executado, ou nulo quando o domínio não é suportado. |
| `confidence` | Escore do classificador, método e estado de calibração; não equivale a similaridade. |
| `suggested_priority`, `suggested_route` | Resultado de política versionada, com razões e origem `policy_suggested`; não são previsões supervisionadas DS2. |
| `potential_duplicate` | Candidato, ID, similaridade, limiar e versão da regra; um escore de similaridade não é probabilidade calibrada de duplicação. |
| `nearest_cluster` | `cluster_id` pertencente ao `space_id`, método e escore de associação; pode ser nulo/ruído. |
| `similar_tickets` | IDs históricos, texto de evidência permitido, posição no ranking, similaridade e metadados disponíveis no corpus. |
| `suggested_action` | Ação derivada de classificação, evidências e política, com motivos. Não é resolução inventada. |
| `human_review_required` | Booleano e lista de motivos: baixa confiança, ausência de evidência, domínio incerto, falha parcial ou regra de risco. |
| `model_version`, `policy_version` | Versões efetivamente usadas; uma nova requisição deve fixar artefatos consistentes para todas as etapas. |
| `inference_mode`, `latency_ms` | `online`; tempo medido no servidor, total e etapas disponíveis, separado do tempo de rede/interface. |
| `processing_status`, `errors` | Completo, parcial ou falha, com etapas e mensagens seguras para apresentação. |

Os nomes acima detalham as necessidades desta aba; a estrutura final de envelopes segue a arquitetura compartilhada. Incluir score bruto e rótulo legível quando um campo não representar probabilidade.

### Regras de inferência e evidência

- Normalizar sem destruir informação relevante; a mesma versão de pré-processamento deve servir treino e inferência. Mascarar dados pessoais na apresentação e nos logs apropriados.
- Os textos DS1 contêm placeholders segundo a auditoria. Preservar a origem e sinalizar esse limite nos vizinhos; não apresentar o corpus público como operação de produção validada. A política de tratamento de placeholders deve ser compartilhada entre artefatos e inferência.
- Usar SentenceTransformers e consultar `IndexFlatIP` com embeddings normalizados. A ordenação dos vizinhos utiliza a similaridade real retornada; não a distância visual UMAP.
- Recuperar vizinhos dentro do espaço escolhido. Espaços DS1 e DS2 permanecem separados, sem join de clientes ou tickets.
- Excluir o próprio registro histórico quando a tela for usada para inspeção de um ticket existente. Na busca de sessão, excluir também o próprio ID do overlay autorizado. Para texto manual, um vizinho histórico igual é evidência válida de possível duplicação.
- Exibir quantidade efetiva de vizinhos; corpus pequeno ou restrições podem retornar menos que K. Não completar a lista com exemplos.
- Fixar limiares após avaliação em conjunto de validação; documentar cobertura e erros. Não escolher um número alto apenas para produzir o rótulo “automático”.
- Baixa confiança, textos fora do domínio, idioma não avaliado e evidência insuficiente devem permitir abstenção. O valor de confiança sozinho não prova conhecimento do domínio.
- Repetir a mesma requisição após timeout recupera a análise anterior pelo `request_id`; nova submissão intencional recebe nova identidade.
- Nunca executar ações em sistemas de atendimento externos. “Roteado” significa decisão registrada na demonstração, identificada como tal.

## 4. Interface, estados e acessibilidade

Layout: entrada de texto e seleção do corpus; resumo da decisão; evidências semânticas; explicação de revisão humana; ações para Graph e Copilot. O resultado preserva o texto submetido enquanto uma nova edição permanece rascunho.

| Estado | Comportamento esperado |
|---|---|
| Inicial | Entrada rotulada, instrução de domínio/idioma, limite de tamanho e artefatos disponíveis. |
| Processando | Estado textual das etapas reais, botão de envio protegido contra duplicidade; sem percentuais fictícios. |
| Resultado completo | Categoria, confiança, prioridade/rota com sua origem, vizinhos, versão e latência. |
| Revisão humana | Motivo próximo da decisão; não depender de cor de alerta. |
| Resultado parcial | Mostrar o que foi calculado, identificar a etapa indisponível e oferecer nova tentativa sem duplicar ocorrência. |
| Nenhum vizinho confiável | Mensagem explícita, sem conectar aleatoriamente o ticket a um cluster. |
| Artefato ausente/incompatível | Bloquear apenas a capacidade afetada e indicar o artefato necessário. |
| Erro de validação/servidor | Preservar o texto; focar o erro ou associá-lo ao campo; não expor traceback ou conteúdo sensível. |

Usar rótulos persistentes, botões operáveis por teclado, foco visível, resumo de status em região `aria-live="polite"` e tabela acessível para vizinhos. Um retorno assíncrono não deve roubar o foco de quem continua editando. Respeitar `prefers-reduced-motion`.

## 5. Integrações e navegação

- **Graph:** `/#/graph` com `ticket_id`, `session_id`, `dataset_id`, `space_id`, `source=user_created` e `model_version`. Carregar o ticket persistido, seus vizinhos e cluster antes de posicionar a câmera. Recarregar a URL deve restaurar o foco.
- **Command Center:** inclusão opcional produz eventos com IDs e origem compartilhados. Um ticket manual em sessão de replay mantém `source=user_created`; não vira conteúdo histórico nem entra no denominador de chegadas simuladas sem indicação.
- **Copilot:** repassar o ticket. No DS2, informar ausência de resoluções e manter o contexto sem inventar vínculo com DS1. Busca explicitamente cruzada entre corpora é P2, depende de contrato e avaliação próprios e permanece fora da implementação inicial.
- **Automation Strategy:** abrir a regra e suas evidências para explicar rota, prioridade e revisão.

Implementação prevista em `frontend/src/views/lab.ts`, `backend/app.py`, `backend/pipeline.py`, `backend/sessions.py` e artefatos versionados produzidos por `scripts/train.py` e `scripts/build_semantic.py`. Reutilizar o pipeline; evitar classificador, busca ou limiares próprios da tela.

## 6. Prioridades e checkpoints

**P0 — capacidade funcional obrigatória**

- [x] Validar a entrada, carregar artefatos consistentes e executar classificação real DS2.
- [x] Gerar embedding online, recuperar vizinhos reais e retornar scores verificáveis.
- [x] Aplicar prioridade, rota, duplicidade e revisão por políticas declaradas; mostrar razões.
- [x] Persistir análise/versões e permitir nova tentativa idempotente.
- [x] Abrir Graph com o mesmo ticket e evidências; abrir Copilot preservando contexto.
- [ ] Exibir todos os estados de erro/abstenção e alternativa textual às visualizações.

**P0-b — integração do núcleo da demonstração**

- [x] Adicionar opcionalmente à sessão ativa e verificar atualização única dos contadores.
- [x] Recuperar análise por URL após recarga; o resultado persistido restaura texto, ticket, versão, decisão e vizinhos.
- [ ] Validar `model_version` e rejeitar explicitamente contexto antigo ou incompatível antes de exibir o resultado.

**P1 — aprofundamento da observabilidade**

- [ ] Mostrar tempos por etapa e origem de cada decisão sem confundir score e probabilidade.

**P2 — somente após o fluxo principal**

- [ ] Comparar modelos versionados se houver avaliação comparável disponível.
- [ ] Expandir idiomas ou domínio DS1 após validação específica e abstenção adequada.

Dependências do plano: F08–F13, F15–F19; integração nas F22–F25 e F31–F34. A atribuição final de sprint está no planejamento geral.

## 7. Testes e aceite

1. Enviar pelo menos um texto livre fora dos exemplos de interface; verificar no backend execução do artefato real e embedding novo. Nenhum resultado é uma resposta fixa ao texto.
2. Recomputar os vizinhos de uma entrada de teste diretamente no índice e conferir IDs, ordenação e scores retornados pela API.
3. Repetir a requisição com o mesmo `request_id`: uma análise e uma ocorrência; enviar intencionalmente outra requisição: nova ocorrência.
4. Abrir o link do Graph em outra aba e recarregar: mesmo `ticket_id`, versões e vizinhos. Uma associação insuficiente deve aparecer sem cluster, sem inventar posição/evidência.
5. Usar entrada vazia, tamanho excessivo, idioma não avaliado, falha do índice e versão inválida: erro/abstenção claros, texto preservado e nenhuma decisão automática indevida.
6. Comparar um ticket DS1 e um DS2: atributos exclusivos do outro corpus permanecem indisponíveis; prioridade DS2 é rotulada como política.
7. Adicionar à sessão ativa, navegar e reconectar: contadores incrementam uma vez, origem manual permanece visível e os CSVs mantêm seus hashes.
8. Executar por teclado e com movimento reduzido: resultado, vizinhos, erros e ações continuam utilizáveis.

Não exigir acurácia, confiança ou latência inventadas. Registrar resultados reais da validação e ajustar o escopo de automação ao desempenho observado.

## 8. Riscos e decisões pendentes

| Risco | Tratamento |
|---|---|
| Texto livre fora do domínio/idioma de treino | Exibir limites, medir exemplos de desafio e encaminhar à revisão; não prometer detecção perfeita de OOD. |
| Similaridade alta interpretada como duplicata certa | Exibir candidato e score; política conservadora; confirmação humana para qualquer ação posterior. |
| Rotas/prioridades aparentarem treinamento inexistente | Mostrar `policy_version`, origem da regra e motivos ao lado da sugestão. |
| Tokenização truncar a parte importante | Exibir aviso de truncamento e registrar comprimento efetivo; calibrar o limite antes do aceite. |
| Falha/recarregamento duplicar decisões | Idempotência e persistência no backend, não apenas botão desabilitado. |
| Inferência lenta na máquina da apresentação | Aquecer/carregar o modelo uma vez, medir latência e manter progresso textual; não substituir inferência manual por resultado pré-calculado. |
