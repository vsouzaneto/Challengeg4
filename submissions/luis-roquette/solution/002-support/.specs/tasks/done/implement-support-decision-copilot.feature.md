---
title: Implement Support Decision Copilot
---

## Initial User Prompt

Antes de seguir, registre o fechamento de toda essa parte de exploração e criação da SPEC no nosso diário e, depois, aprove e crie a SPEC.

### Requirements

#### Outcome

Construir o Challenge 002 como um **Support Decision Copilot** local e autocontido que conecta diagnóstico operacional, triagem segura, resposta assistida, decisão humana e evidência gerencial em um fluxo demonstrável.

#### Primary experience

- Abrir na fila diária priorizada do agente de suporte.
- Ordenar tickets por prioridade composta e explicável, usando somente sinais validados.
- Exibir contexto sanitizado, categoria, prioridade, confiança calibrada, regras acionadas e decisão do gate.
- Permitir aprovar, editar e aprovar, rejeitar ou escalonar.
- Persistir localmente decisão, motivo e diferença entre sugestão e resposta final.

#### Automation boundary

- Automatizar roteamento apenas quando confiança calibrada e regras explícitas de risco permitirem.
- Fazer regras de risco prevalecerem sobre confiança alta.
- Encaminhar caso sensível, crítico, ambíguo, inválido ou incerto para revisão humana.
- Nunca enviar respostas externas no MVP.
- Nunca aprender online com uma decisão individual.

#### Response assistance

- Recuperar resoluções históricas sanitizadas e semelhantes do conjunto permitido.
- Mostrar fontes, identificadores e scores usados.
- Produzir rascunho editável somente quando a evidência superar o limite validado.
- Abster-se e escalonar quando não houver precedente seguro.
- Não usar geração livre como fallback.

#### Dataset boundaries

- Usar o Dataset 1 para diagnóstico operacional, workspace de Customer Support e recuperação de respostas.
- Usar o Dataset 2 no Laboratório IT, com sua taxonomia de oito categorias e modelo próprio.
- Reutilizar componentes de classificação, calibração, abstinência e auditoria sem unir linhas, rótulos ou taxonomias dos datasets.
- Remover PII antes de treino, persistência, interface, screenshot ou exportação.

#### Analytics and evidence

- Quantificar gargalos, fatores associados à satisfação e desperdício recuperável com denominadores rastreáveis.
- Separar histórico observado, desempenho medido do protótipo e cenários projetados.
- Fornecer calculadora de cenários conservador, base e otimista com premissas editáveis.
- Tratar associação como associação e custo como cenário, nunca como causalidade ou fato não observado.
- Exibir scorecard gerencial compacto e Laboratório IT separado.

#### Validation

- Comparar baselines simples antes de modelos mais complexos.
- Selecionar modelos por validação cruzada no conjunto de desenvolvimento.
- Manter teste estratificado congelado até modelo, calibração, regras e thresholds estarem definidos.
- Reportar macro-F1, métricas por classe, matriz de confusão, calibração e risco versus cobertura.
- Quando houver amostra elegível suficiente, avaliar recuperação em tickets não vistos com rubrica humana de relevância, correção, segurança e esforço de edição. Essa avaliação é uma validação futura opcional, não exigida pelo briefing; enquanto ausente ou insuficiente, drafts permanecem bloqueados sem impedir a conclusão do diagnóstico, do roteamento seguro e do protótipo.
- Testar o fluxo ponta a ponta, persistência, exportação, abstinência e precedência das regras de risco.

#### Delivery constraints

- Executar localmente com um comando e sem API paga, credenciais ou serviço externo.
- Escolher framework, dependências, modelos e persistência somente após a Regra Zero de pesquisa e reprodução.
- Manter toda entrega pública em `submissions/luis-roquette/`.
- Incluir README executivo, setup, pesquisa, testes, métricas, limitações, process log e screenshot real.
- Excluir helpdesk real, envio de mensagens, autenticação, multiempresa, deploy obrigatório, aprendizado online e infraestrutura especulativa.
- Reduzir ou remover qualquer função invalidada pelos dados; nunca simular evidência ausente.

#### Process gates

- Pesquisar GitHub, Reddit e documentação oficial antes de implementar.
- Inspecionar pelo menos três candidatos quando existirem e reproduzir a menor prova útil do escolhido.
- Aplicar Ponytail `full`: primeiro reutilizar, depois escrever o mínimo necessário.
- Executar `plan-task` e obter revisão humana da SPEC antes de iniciar `implement-task`.
- Registrar contemporaneamente decisões, perguntas, respostas, erros, correções e verificações no diário.

# Description

Entregar o Support Decision Copilot, uma demonstração local para agentes de suporte e gestores de Operações responderem às três perguntas do Challenge 002: onde o atendimento perde tempo, o que pode ser automatizado com segurança e como esse fluxo funciona na prática. O agente começa na fila diária, inspeciona a recomendação explicável, consulta precedentes seguros e registra sua decisão. O gestor encontra diagnóstico rastreável, resultados medidos e cenários editáveis separados.

**Scope Included:** diagnóstico operacional, satisfação e oportunidade de redução de trabalho no Dataset 1; fila priorizada com revisão humana; classificação independente Customer Support/IT; resposta assistida por precedentes sanitizados; decisões locais persistidas/exportáveis; scorecard; Laboratório IT com texto livre; reprodução, testes, documentação e evidências reais. Se os dados invalidarem uma função, entregar sua desativação explicada e a evidência da limitação.

**Scope Excluded:** helpdesk, envio/fechamento real de tickets, geração livre, APIs pagas, serviços remotos durante uso normal, autenticação, multiempresa, deploy obrigatório, aprendizado online, união de linhas/taxonomias e causalidade ou custo não observados. Downloads públicos iniciais sem credenciais são permitidos. As aproximadamente 30 mil solicitações anuais do briefing são contexto operacional, não a quantidade de linhas do Dataset 1.

**User Scenarios:**

1. **Fila diária:** o agente abre a fila reservada para demonstração, filtra tickets e entende posição, categoria, confiança e motivos do gate; artefato inválido indisponibiliza a função afetada com causa/correção.
2. **Assistência segura:** o agente vê fontes/scores, revisa o rascunho e aprova ou edita e aprova; a decisão confirmada permanece disponível após reiniciar.
3. **Exceção humana:** casos sensíveis, críticos, inválidos, ambíguos, incertos ou sem precedente seguro recebem revisão/abstinência; rejeição/escalonamento exigem motivo; falha de gravação não confirma sucesso nem perde registros anteriores.
4. **Decisão gerencial:** o gestor compara gargalos e associações com satisfação, inspeciona denominadores/limitações e altera premissas dos cenários conservador, base e otimista sem transformar projeções em fatos.
5. **Laboratório IT:** texto novo produz classificação, confiança e gate na taxonomia própria de oito classes; entrada ou artefato inválido recebe fallback, sem reutilizar modelo Customer Support.

- **Pesquisa técnica:** `../../../../../research/002-support.md`
- **Skill de pesquisa:** [offline-support-decision-copilot](../../../.claude/skills/offline-support-decision-copilot/SKILL.md). Consultar antes de finalizar dependências, calibração, recuperação, persistência e exportação; a prova executável continua obrigatória.
- **Plano de implementação:** `../../../docs/superpowers/plans/2026-09-21-support-decision-copilot.md`

## Acceptance Criteria

**Checklist:**

| ID | Question | Category | Importance |
|---|---|---|---|
| CK-1 | Em ambiente documentado e preparado, `make demo` disponibiliza a aplicação local com os dois datasets reais, sem credenciais ou API paga, e o uso normal funciona sem chamadas externas? | hard_rule | essential |
| CK-2 | Dados brutos e PII ficam fora do Git, e nomes, emails e telefones em campos livres, edições e motivos são sanitizados antes de treino, persistência, interface, screenshot ou exportação? | hard_rule | essential |
| CK-3 | O relatório de qualidade identifica fontes/hashes, schemas, contagens, duplicidades, ausências e exclusões; isola valores inválidos/negativos sem convertê-los em zero; e preserva datasets, rótulos, modelos e métricas separados? | hard_rule | essential |
| CK-4 | Gargalos por canal, prioridade, tipo e combinações mostram contagem, mediana e IQR de `post_response_hours` apenas para tickets fechados com timestamps válidos e ordenados, reconciliam denominadores e declaram primeira resposta e resolução total não observáveis? | hard_rule | essential |
| CK-5 | A análise de satisfação publica amostra, ausências, efeitos univariados e comparação multivariada com baseline, identifica apenas associações e retorna `no_reliable_signal` quando Ridge não melhora MAE médio em pelo menos 2%? | principle | essential |
| CK-6 | A oportunidade observada usa excesso não negativo sobre a mediana de pares do mesmo tipo/prioridade, para grupos com pelo menos 30 linhas válidas, enquanto cenários conservador/base/otimista expõem volume elegível, fração endereçável, minutos poupados e custo/hora editáveis, sem apresentar proxy ou projeção como economia realizada? | principle | essential |
| CK-7 | Cada domínio mantém splits estratificados 60/20/20 reproduzíveis com IDs disjuntos, usa CV apenas no treino, registra e trata duplicatas que contaminariam avaliação, e congela teste até modelo, calibração, regras e thresholds serem fixados? | hard_rule | essential |
| CK-8 | Classificadores são comparados a dummy e baselines textuais por macro-F1, usam features permitidas, desativam automação quando o ganho de CV é menor que 0,02 e reportam métricas globais/por classe, confusão, log loss, calibração e risco versus cobertura no teste congelado? | hard_rule | essential |
| CK-9 | Roteamento automático exige modelo suportado, entrada válida, probabilidades válidas e confiança calibrada no threshold validado; todo bloqueio de risco prevalece sobre confiança, e ausência de threshold elegível desativa automação inclusive quando a confiança é 1,0? | hard_rule | essential |
| CK-10 | A política versionada justifica categorias humanas com contagens e exemplos sanitizados, distingue regras IT sem evidência operacional, e a fila explica a ordem por prioridade existente, quantidade de riscos e incerteza usando apenas sinais validados? | principle | important |
| CK-11 | Recuperação consulta somente resoluções não vazias de tickets fechados sanitizados do treino Customer Support, mostra até três IDs/scores e só oferece rascunho histórico editável acima do limite validado, abstendo-se explicitamente em qualquer ausência de evidência segura? | hard_rule | essential |
| CK-12 | Se houver pelo menos 30 consultas elegíveis em cada split e a validação opcional for executada, duas amostras independentes, seeded e estratificadas recebem avaliações humanas registradas sem retuning pelo teste; caso contrário, a insuficiência fica documentada e drafts permanecem bloqueados, sem bloquear os entregáveis canônicos do challenge? | principle | optional |
| CK-13 | Aprovar, editar e aprovar, rejeitar e escalonar registram decisão local; rejeição/escalonamento exigem motivo; nenhuma ação envia mensagem, fecha ticket real, aprende online ou modifica modelos/thresholds? | hard_rule | essential |
| CK-14 | Cada gravação é atômica, sobrevive ao reinício e registra ID, data, ticket/domínio, versões de dados/modelo/regras, threshold, recomendação, gate/motivos, ação humana, textos sanitizados e diferença de edição; falha mantém registros anteriores e exportação preserva esses campos? | hard_rule | essential |
| CK-15 | A aplicação abre na fila, oferece filtros essenciais e detalhe sanitizado, confirma o ID efetivamente gravado, distingue carregamento/indisponibilidade/artefato desatualizado e mantém rótulos, navegação por teclado e significado independente de cor? | principle | important |
| CK-16 | Scorecard separa `Histórico observado`, `Desempenho medido` e `Cenários projetados`; Laboratório IT aceita texto livre e exibe sua taxonomia de oito classes, confiança, gate e métricas; oportunidades conectam evidências dos domínios sem juntar registros? | principle | essential |
| CK-17 | Artefato ausente, corrompido, incompatível ou com hash divergente bloqueia apenas a função afetada, impede automação insegura e informa caminho, causa e `make reproduce` como correção, mantendo disponível a evidência válida restante? | hard_rule | essential |
| CK-18 | Reprodução registra hashes, contagens, splits, sementes, versões, regras e thresholds, regenera resultados equivalentes com as mesmas entradas/configuração e oferece instrução explícita para obter os CSVs quando o download público falha? | hard_rule | essential |
| CK-19 | README executivo na raiz da submissão segue o template oficial, responde às três perguntas do diretor e aponta setup técnico, métricas reais, limitações, screenshot real, export persistido e diário contemporâneo, sem perfil pessoal inventado ou alegação de gate não executado? | hard_rule | essential |
| CK-20 | Pesquisa/prova mínima, aprovação humana da SPEC e ciclo Planejamento → Revisão → Execução → Teste são evidenciados; resultados de gates são atribuídos ao SHA/diff real e qualquer preflight pulado por instrução do owner fica registrado como não executado/não verde, sem falsa aprovação; toda entrega pública permanece em `submissions/luis-roquette/`? | hard_rule | essential |

**Regular Checks:**

**Inventário histórico pré-implementação:** no momento da redação, o repositório ainda não continha aplicação, Makefile, testes ou workflow de CI. No estado final, aplicação, Makefile e testes existem; workflow de CI próprio não foi adicionado. Os gates canônicos abaixo preservam os critérios aprovados. Executar a partir de `submissions/luis-roquette/solution/002-support/`, exceto checks Git na raiz. Instalação, suíte completa e reprodução pesada usam `codespace-manager`; resultado de outro SHA não vale.

- [ ] RC-1 — Executar `make doctor` e conferir Python 3.12, dependências bloqueadas, fontes públicas e mensagens de correção; demonstrar `make demo` e uso após download sem credenciais. Cobre CK-1/18/20.
- [ ] RC-2 — Executar `make test && make lint && make reproduce` no ambiente gerenciado com o SHA/diff exato, salvo instrução explícita do owner para pular o preflight terminal. Nesse caso, registrar `não executado/não verde`, preservar os últimos resultados reais com seu SHA e nunca convertê-los em aprovação do estado final. Cobre CK-2–14/17/18/20.
- [ ] RC-3 — Executar `.venv/bin/pytest tests/test_workflow.py -q` e demonstração visual real: fila, escalonamento humano, reinício, download CSV, scorecard e texto livre IT; conferir screenshot sanitizado e audit ID persistido. Aprovação/edição real só é exigível se existir draft seguro habilitado; seus controles permanecem cobertos por testes. Cobre CK-13–19.
- [ ] RC-4 — Conferir manifests/splits, denominadores e relatórios de métricas, congelamento dos thresholds e motivos de funções desativadas. Se a avaliação humana opcional não tiver população suficiente, registrar contagens reais e manter drafts bloqueados; os dois formulários de 30 casos não bloqueiam a entrega canônica. Cobre CK-3–12/18/19.
- [ ] RC-5 — Executar `git diff --check`, `git status --short` e `git diff --name-only upstream/main --`; revisar entrega contra PII, segredos e licença; conferir README pelo template e diário em cada checkpoint. Nenhum arquivo público fora de `submissions/luis-roquette/`. Cobre CK-2/19/20.

**Rubric:**

| Criterion | Weight |
|---|---|
| Operational Evidence Honesty | 0.25 |
| Safe Decision and Response Boundaries | 0.25 |
| Independent and Reproducible Validation | 0.20 |
| Agent Workflow and Durable Evidence | 0.20 |
| Project Guidelines Alignment | 0.10 |

**Rubric Score Definitions:**

### Operational Evidence Honesty

Avalia se o diretor rastreia cada conclusão ao universo elegível e distingue intervalo observado, associação, proxy e cenário. Cobre CK-3/4/5/6/16. Classificar pela evidência apresentada, não pela aparência do painel.

Anchors:

- `score_2`:
  ```text
  Tempo total de resolução: mediana 2 h; n=40; ausentes=12.
  Fonte: timestamp de resolução menos timestamp de primeira resposta.
  ```
- `score_4`:
  ```text
  Intervalo pós-primeira-resposta: mediana 2 h; n=40; ausentes=12.
  Fonte: timestamp de resolução menos timestamp de primeira resposta.
  ```
- `contrast`: muda somente o nome da medida para corresponder ao intervalo observado.

### Safe Decision and Response Boundaries

Avalia a proteção da decisão humana diante de risco, PII e evidência insuficiente, mesmo com probabilidades favoráveis. Cobre CK-2/8/9/10/11/13/17 e o comportamento fail-closed opcional de CK-12.

Anchors:

- `score_2`:
  ```text
  Prioridade=Critical; confiança=0.99; regra=critical_priority; decisão=auto_route.
  ```
- `score_4`:
  ```text
  Prioridade=Critical; confiança=0.99; regra=critical_priority; decisão=human_review.
  ```
- `contrast`: muda somente a decisão, fazendo a regra de risco prevalecer.

### Independent and Reproducible Validation

Avalia reprodução sem contaminação entre desenvolvimento/teste ou domínios, mantendo resultados negativos visíveis. Cobre CK-1/7/8/12/18.

Anchors:

- `score_2`:
  ```text
  threshold=0.80; origem_do_ajuste=frozen_test; versão=model-01; teste=test-01.
  ```
- `score_4`:
  ```text
  threshold=0.80; origem_do_ajuste=calibration; versão=model-01; teste=test-01.
  ```
- `contrast`: muda somente a origem dos dados usados para selecionar o threshold.

### Agent Workflow and Durable Evidence

Avalia se o agente compreende a sugestão, decide e recupera evidência íntegra após sair da aplicação. Cobre CK-10/13/14/15/16/17/19.

Anchors:

- `score_2`:
  ```text
  Ação=editar e aprovar; UI=Salvo, audit_id=17.
  Após reinício: consultar audit_id=17 → ausente.
  ```
- `score_4`:
  ```text
  Ação=editar e aprovar; UI=Salvo, audit_id=17.
  Após reinício: consultar audit_id=17 → presente.
  ```
- `contrast`: muda somente a existência do evento confirmado após reiniciar.

### Project Guidelines Alignment

Avalia aderência demonstrada ao desafio, SDD, Regra Zero, Ponytail, limites de custo/escopo, documentação contemporânea e validação do estado entregue. Cobre CK-1/2/19/20. Cobertura de plano não substitui execução.

Anchors:

- `score_2`:
  ```text
  SHA pretendido=abc123; suíte completa=não executada por instrução do owner; relatório=preflight aprovado.
  ```
- `score_4`:
  ```text
  SHA pretendido=abc123; suíte completa=não executada por instrução do owner; relatório=preflight não executado/não verde.
  ```
- `contrast`: muda somente a integridade documental; comando não executado nunca sustenta alegação verde.

**Test Strategy:**

**Criticality:** alta para privacidade, integridade da auditoria e roteamento indevido; demonstração local com controles que falham de modo seguro. Testes não autorizam APIs pagas, comunicação externa ou implementação antes da aprovação da SPEC.

| Type | Size | Framework | Dependencies | Gate |
|---|---|---|---|---|
| unit | fixtures pequenas determinísticas | pytest | dados, análise, gate, recuperação e armazenamento | testes focados por alteração; `make test` final |
| integration | fixtures pequenas; reprodução completa remota | pytest + pipeline documentado | lock, datasets, manifests, modelos e SQLite | `make test && make reproduce` no SHA pretendido |
| ui | fluxo e navegação multipágina | Streamlit AppTest + inspeção visual real | aplicação, artefatos sanitizados e banco temporário | `tests/test_workflow.py` e demonstração persistida |
| evaluation | splits completos; amostras humanas somente se houver população elegível | scikit-learn + rubricas humanas opcionais | dados separados, configuração congelada e avaliador humano quando aplicável | insuficiência documentada mantém drafts bloqueados; não bloqueia o challenge |
| inspection | arquivos públicos, comandos e processo | Git + revisão documental/visual | guia, template, SPEC, diário e evidências | diff limpo/restrito e revisão final |

**Test Cases to Cover:**

#### CK-1: Execução local

- [integration] Executar `make demo` em ambiente limpo com pré-requisitos documentados; após downloads públicos, bloquear rede e verificar inferência, decisões e exportação locais.
- [inspection] Conferir ausência de API paga, modelo remoto e fallback com credenciais pessoais.

#### CK-2: Privacidade em todo o fluxo

- [unit] Inserir nome, email e telefone em descrição, resolução, edição e motivo; confirmar sanitização antes de cada saída, sem depender apenas de esconder colunas.
- [inspection] Inspecionar arquivos rastreados, screenshot e export real; dados pessoais/demográficos não entram nas features ou exports.

#### CK-3: Qualidade e separação

- [unit] Cobrir schema ausente, IDs duplicados, texto vazio, datas ilegíveis, intervalo negativo, nota fora da faixa e domínio incorreto; reconciliar entrada, exclusão e elegibilidade.
- [integration] Conferir fontes/hashes e contagens efetivas, sem fixar contagens históricas como invariantes; impedir uso de modelo/taxonomia IT no workspace Customer Support.

#### CK-4: Diagnóstico temporal

- [unit] Com intervalos válidos/negativos/ausentes e tickets não fechados, recalcular mediana, IQR e denominadores de grupos e combinações.
- [inspection] Conferir nome `post_response_hours` e declaração de que duração até primeira resposta/resolução total não é observável.

#### CK-5: Satisfação

- [unit] Cobrir avaliações ausentes e amostra sem sinal; melhora de MAE abaixo de 2% gera `no_reliable_signal` e não publica importância multivariada como achado.
- [evaluation] Registrar CV Ridge versus DummyRegressor, amostra/ausências e efeitos univariados; conclusão expressa associação, sem features demográficas.

#### CK-6: Oportunidade e cenários

- [unit] Testar grupos de 29/30 linhas, mediana do mesmo tipo/prioridade entre canais e excesso truncado em zero; excluir linhas inválidas das somas.
- [unit] Recusar volume/custo/minutos negativos, NaN/infinito e fração fora de 0–1; conferir horas anuais = volume × fração × minutos / 60 e custo = horas × custo/hora.
- [ui] Alterar cada premissa nos três cenários; projeções mudam, históricos permanecem idênticos e separados.

#### CK-7: Independência

- [unit] Repetir splits com seed 42 e IDs disjuntos; detectar duplicatas textuais e registrar tratamento que impeça contaminação entre treino/referência e consulta avaliada.
- [integration] Espionar IDs usados por treino, seleção, calibração e threshold; nenhum ID de teste participa antes do congelamento e a avaliação não muda configuração.

#### CK-8: Classificação útil ou desativada

- [evaluation] Comparar dummy e TF-IDF + MultinomialNB/LogisticRegression/LinearSVC em cinco folds estratificados de treino; empate até 0,01 favorece simplicidade. Customer usa descrição→tipo; IT documento→tópico; subject ablation exige auditoria de proxy.
- [unit] Testar ganho 0,019/0,020, modelo não suportado e distribuição inválida; domínio sem sinal permanece visível com automação desativada.
- [evaluation] Conferir macro-F1, métricas de todas as classes, confusão, log loss, ECE e risco/cobertura com versões/denominadores no teste congelado.

#### CK-9: Gate

- [unit] Cobrir confiança abaixo/igual/acima do limite, NaN/infinito, probabilidades fora da faixa, classe desconhecida, texto vazio/ambíguo/OOD e exceção do modelo; nenhum inválido autoriza automação.
- [unit] Para confiança 0,99, cada bloqueio sensível e prioridade Critical vence; sem threshold elegível, até confiança 1,0 fica bloqueada.
- [evaluation] Escolher menor limite da grade 0,50–0,95 por 0,05 com erro seletivo de calibração até 10% e seleção não vazia; registrar cobertura, sem tratar zero casos como evidência de erro zero.

#### CK-10: Política e prioridade

- [unit] Validar ordem estável por prioridade ordinal, riscos e incerteza; fatores mostrados correspondem ao cálculo e nenhum SLA/idade inexistente é inferido.
- [inspection] Conferir justificativa, contagens e IDs sanitizados de Billing inquiry/Refund request/Cancellation request e HR Support/Access/Administrative rights; regras IT declaram risco semântico quando não há desfecho operacional observado.

#### CK-11: Recuperação

- [unit] Testar índice ausente, fonte vazia/inadequada, empate, similaridade baixa e consulta sem termos conhecidos; não criar resposta livre nem indexar resoluções de calibração/teste.
- [unit] Conferir máximo de três fontes/scores e cópia sanitizada da resolução histórica aceita; sem limite validado manter `draft=null` com motivo.

#### CK-12: Revisão humana opcional futura

- [evaluation] Se existirem 30 consultas elegíveis, preparar calibração estratificada com seed; humano registra relevância/correção/segurança/esforço de edição de 1–5, notas e autoria, sem consultar teste.
- [evaluation] Se a validação opcional for executada, testar limites 0,20–0,90 por 0,10; exigir médias de correção/segurança pelo menos 4 e nenhum safety abaixo de 3. Pacote vazio, insuficiente, incompleto ou reprovado mantém drafts bloqueados; uma avaliação futura de teste não reajusta a configuração congelada.

#### CK-13: Decisão humana

- [ui] Exercitar quatro ações, rejeição/escalonamento sem motivo, edição com PII e aprovação sem draft após abstinência; impedir confirmação de resposta inexistente e mostrar alternativas humanas.
- [integration] Confirmar ausência de envio/fechamento externo, treino ou mudança de threshold/modelo após cada ação.

#### CK-14: Persistência/exportação

- [unit] Injetar falha transacional; registro anterior permanece e não há evento parcial; conferir sanitização, campos obrigatórios e versões/threshold exatos da decisão.
- [integration] Gravar, reiniciar e exportar o mesmo audit ID; conferir textos/edit_ratio, nulo em rejeição/escalonamento/abstinência; texto iniciado por fórmula não executa ao abrir CSV em planilha.

#### CK-15: Experiência

- [ui] Conferir fila inicial, filtros, detalhe, motivos, fontes, edição e confirmação; navegar por teclado e distinguir estados sem depender de cor.
- [ui] Exercitar carregamento, vazio, indisponível, desatualizado e falha ao salvar; não mostrar `Salvo` sem audit ID persistido.

#### CK-16: Scorecard e IT

- [ui] Conferir três blocos de evidência e premissas; texto livre IT retorna classe/confiança/gate e métricas próprias sem mudar o domínio da fila.
- [inspection] Conferir oportunidades ligadas à evidência operacional Customer Support e de classificação IT, sem join fictício de tickets.

#### CK-17: Artefatos inválidos

- [integration] Remover/corromper artefato, mudar hash e incompatibilizar versão; conferir caminho/causa/`make reproduce`, bloqueio da função e continuidade das evidências válidas restantes.

#### CK-18: Reprodução

- [integration] Executar pipeline duas vezes com mesmas entradas/lock/configuração; comparar resultados/hashes excluindo só metadados temporais documentados; não retunar no teste.
- [inspection] Simular download indisponível; mensagem/README indicam nomes/local dos CSVs e retomada, sem inventar dados substitutos.

#### CK-19: Entrega

- [inspection] Conferir README raiz pelo template, links, três respostas executivas, limitações temporais/de sinal, perfil informado ou `Não informado`, setup, screenshot e export da demonstração real.
- [inspection] Conferir diário contemporâneo e distinção entre proposta, execução local, gate remoto e estado persistido; falha conhecida não aparece como sucesso.

#### CK-20: Processo

- [inspection] Conferir candidatos/prova mínima, aprovação humana, loops e SHA dos gates; quando o owner mandar pular o preflight terminal, registrar a decisão e o estado não executado/não verde, sem reaproveitar resultado de outro SHA.
- [inspection] Conferir diff público restrito à submissão e prontidão para `[Submission] Luis Roquette — Challenge 002`; publicação depende do escopo autorizado, não se presume pela preparação.

**Definition of Done:**

- [X] CK-1–11 e CK-13–20 possuem evidência; checks/testes passam no estado pretendido e limitações legítimas aparecem como funções desativadas, sem simular sucesso. CK-12 registra honestamente a validação futura opcional ou a insuficiência que mantém drafts bloqueados.
- [X] Ambos os domínios são demonstrados com dados reais independentes; diagnóstico e métricas têm fontes/denominadores/versões; oportunidades/projeções expõem premissas. Rubricas humanas são opcionais e só habilitam assistência futura.
- [X] Um escalonamento humano real persiste após reinício e exporta dados sanitizados; `decisions-demo.csv` e seu hash são a evidência exclusiva do audit ID/persistência, enquanto a screenshot comprova somente o Scorecard. Aprovação/edição real só é exigida quando houver draft seguro; seus controles permanecem validados por testes.
- [X] READMEs, pesquisa, diário e evidências cumprem desafio/template; dados brutos, PII, segredos, modelos gerados e banco runtime não integram a entrega pública.
- [X] SPEC foi aprovada antes da implementação; revisões/testes fecharam os loops; publicação/deploy não são presumidos pela prontidão local e nenhum gate obrigatório permanece ocultamente pendente. A rubrica humana opcional pode permanecer não executada com drafts bloqueados e limitação explícita.

## Architecture Overview

### Estratégia e referências

Um processo Python local serve quatro páginas Streamlit e lê artefatos produzidos por um pipeline offline. Funções pequenas de dados, análise, modelos, gate, recuperação e SQLite mantêm a UI sem treino ou ajuste de políticas. Dataset 1 e Dataset 2 compartilham implementação, nunca registros, taxonomia, vetorizador ajustado, modelo ou métricas. A fronteira externa termina no download público inicial e instalação; inferência, decisão e exportação não usam rede.

Esta seção integra a [pesquisa reutilizável](../../../.claude/skills/offline-support-decision-copilot/SKILL.md) e a [análise de impacto](../../analysis/analysis-implement-support-decision-copilot.md). Seus contratos resolvem as lacunas do [plano anterior](../../../docs/superpowers/plans/2026-09-21-support-decision-copilot.md); a decomposição deverá usar estes contratos quando houver divergência. Nenhum módulo, gate, resultado ou versão compatível está implementado/comprovado nesta fase.

Python 3.12, pandas, scikit-learn, joblib, Streamlit, pytest e Ruff são a seleção proposta; SQLite, CSV, JSON, hashing e comparação textual usam stdlib. Fixar versões exatas somente após a prova de navegação → formulário editado → commit SQLite → leitura em nova conexão → download real. Essa prova decide a compatibilidade das páginas e do AppTest; falha exige corrigir a escolha antes de expandir a UI. Sem frontend separado, serviço de busca, ORM, LLM, embeddings ou abstração de providers.

```text
CSVs locais → validação + sanitização + qualidade → splits independentes
  ├─ Customer → diagnóstico observado → scorecard + cenários
  ├─ Customer → modelo + política → fila de teste congelado
  ├─ Customer treino fechado → índice → validação humana opcional → assistência ou abstinência
  └─ IT → modelo + política → laboratório separado
artefatos + manifesto validado → UI → decisão humana → SQLite → CSV persistido
```

### Componentes e propriedade dos contratos

Todos os caminhos abaixo são relativos à solution, salvo indicação. Tipos estruturados são dataclasses imutáveis para valores de domínio e TypedDicts/JSON para relatórios/manifesto; ficam no módulo responsável, sem arquivo genérico de modelos. `Domain = Literal["customer", "it"]`; números JSON são finitos, ausências são `null`, não NaN/Infinity. IDs e versões são strings não vazias. Erros de validação usam `ValueError` com código/campo, sem ecoar texto bruto; erros de I/O preservam sua causa sanitizada.

| Componente | Responsabilidade e saída |
|---|---|
| `data.py` | Schemas, máscaras, qualidade, IDs, deduplicação, `DatasetSplit`, manifesto; entrega apenas frames sanitizados aos demais módulos. |
| `analytics.py` | Denominadores, intervalos, gargalos, satisfação, oportunidades e cenários; sem inferir tempos/custos ausentes. |
| `modeling.py` | CV, seleção, calibração, predição escalar/lote e avaliação por domínio; não recebe decisões humanas para treino. |
| `decision.py` | `TicketSignals`, política versionada, gate e ordem explicável; sem I/O ou efeito externo. |
| `retrieval.py` | Índice do treino Customer fechado, fontes, pacote de revisão, lock e abstinência. |
| `store.py` | Valida snapshot, sanitiza textos finais, grava transação, relê, lista e exporta eventos. |
| `ui.py` + `app.py` | Validam disponibilidade por recurso, exibem quatro páginas, recolhem decisão e mostram ID confirmado. |
| `scripts/reproduce.py` | Orquestra dados → treino/calibração → locks → teste → artefatos; não inventa avaliações humanas. |

### Dados, privacidade e diagnóstico

`load_customer_tickets(path: Path) -> pd.DataFrame` e `load_it_tickets(path: Path) -> pd.DataFrame` validam colunas/tipos e retornam frames sanitizados com `ticket_id: str`, `domain: Domain`, `text: str`, `target: str` e `text_group_id: str`. Customer conserva somente campos operacionais necessários e `resolution: str | None`; IT usa `Document → Topic_group`, com as oito classes verificadas na fonte. IDs Customer derivam do ID original validado; IT deriva de SHA-256 do hash da fonte, ordinal da linha e documento. Não persistir documento bruto no ID/manifesto. A fonte/hash identifica a versão; não prometer IDs idênticos após reordenação de outro arquivo.

`sanitize_text(value: str | None, names: Sequence[str] = ()) -> str` mascara emails, telefones e nomes conhecidos antes de qualquer saída; `sanitize_customer_frame(frame: pd.DataFrame) -> pd.DataFrame` remove colunas identificadoras/demográficas. Aplicar o mesmo núcleo no IT, nas edições e nos motivos. Detecção de nome arbitrário não está comprovada por regex: texto suspeito sem tratamento seguro fica em quarentena, fora de treino/UI/export; a interface solicita nova entrada sanitizada sem repetir o original. A revisão manual de amostras e de todos os exemplos públicos é obrigatória; falha bloqueia a publicação da evidência, sem alegar anonimização universal. Não registrar entrada livre crua em logs/exceções; widgets podem conter apenas o texto que o próprio usuário está digitando até submissão, nunca reexibir input recusado como resultado.

`make_split(frame: pd.DataFrame, target: str, random_state: int = 42) -> DatasetSplit`; `DatasetSplit` contém `domain`, frames `train/calibration/test` e `split_version: str`. Antes do split, agrupar texto sanitizado canônico (casefold, espaços/pontuação normalizados e identificadores/números variáveis substituídos). Conservar um representante determinístico por grupo/rótulo, contar exclusões e pôr grupos com rótulos conflitantes em quarentena; reportar limitação de near-duplicates sem correspondência canônica. Auditar padrões/template residuais antes de congelar; se houver contaminação, rever agrupamento antes de medir. Aplicar 60/20/20 estratificado aos representantes elegíveis, com arredondamento documentado. IDs e grupos precisam ser disjuntos. Se suporte de classe não permitir split/CV, marcar o domínio sem evidência suficiente; nunca duplicar casos ou retirar linhas do teste para completar treino.

`add_operational_fields(frame) -> pd.DataFrame` acrescenta `post_response_hours: float | None` e `interval_status: Literal["valid", "not_closed", "missing", "invalid_timestamp", "negative"]`; motivos são mutuamente exclusivos nessa ordem de precedência. `grouped_bottlenecks(frame) -> pd.DataFrame` retorna dimensões de agrupamento, `n_total`, `n_eligible`, `n_excluded`, `median_hours`, `q1_hours`, `q3_hours`, `iqr_hours` e exclusões por motivo. Todos os agregados vazios são nulos. `recoverable_excess_hours(frame) -> pd.DataFrame` retorna tipo/prioridade, `eligible_n`, `peer_median_hours`, `observed_excess_hours`, `status`; menos de 30 válidos retorna `insufficient_support` e valores nulos.

`satisfaction_associations(frame) -> SatisfactionReport` retorna `status: supported | no_reliable_signal | insufficient_support`, amostra/ausências/exclusões, efeitos univariados, especificação de CV, MAE dummy/Ridge, melhoria relativa e importância de permutação opcional. Folds e pré-processamento são separados; importância vem de folds retidos, somente com melhoria de pelo menos 2%. `operational_summary(frame) -> OperationalSummary` agrega contagens reconciliáveis, medidas anteriores e versões. `ScenarioAssumptions` contém `annual_eligible_volume: int`, `addressable_share: float`, `minutes_saved: float`, `hourly_cost: float`, `name: conservative | base | optimistic`; `scenario_projection(summary, assumptions) -> ScenarioResult` devolve as premissas, `annual_hours`, `annual_cost` e `evidence_kind="projected"`. Recusa não finitos/negativos e fração fora de [0,1]; não altera histórico nem assume que excesso observado será convertido em economia.

### Modelos, sinais e gate

`candidate_pipelines() -> dict[str, sklearn.pipeline.Pipeline]`; `select_candidate(train: pd.DataFrame, text: str, target: str) -> SelectionResult` retorna candidato, scores dos cinco folds, média/desvio, baseline, ganho e motivo. Dummy, TF-IDF+NB, TF-IDF+LogisticRegression e TF-IDF+LinearSVC usam os mesmos folds de treino e vetor ajustado dentro de cada fold. Empate até 0,01 favorece a ordem de simplicidade registrada. Customer usa descrição; ablação de subject é diagnóstica e exige auditoria antes de qualquer inclusão.

`train_domain_model(domain: Domain, split: DatasetSplit) -> ModelTrainingResult` devolve `status: supported | classification_unsupported | insufficient_support`, `model: DomainModel | None`, `selection: SelectionResult`, `policy: RoutingPolicy` e `reason_codes: tuple[str, ...]`. Ganho menor que 0,02 não habilita classificador operacional. O conjunto de calibração de 20% é subdividido uma única vez, estratificado e seeded, em `calibration_fit` e `policy_selection` iguais com arredondamento registrado; o primeiro ajusta sigmoid sobre o pipeline congelado treinado nos 60%, o segundo escolhe threshold. Classe ausente em qualquer parte desativa automação por insuficiência, sem usar teste. A estimativa na seleção de threshold é identificada como desenvolvimento, não desempenho final independente.

`DomainModel.predict_one(text: str) -> Prediction` é o contrato escalar; `predict_batch(texts: Sequence[str]) -> list[Prediction]` preserva comprimento/ordem e retorna `[]` para entrada vazia. Não há `predict` que altere o tipo de retorno conforme o argumento. `Prediction` contém `domain`, `status: ok | unsupported | unavailable | invalid_input`, `label: str | None`, `confidence: float | None`, `probabilities: dict[str, float] | None`, `model_version: str | None`, `zero_vector: bool | None`, `reason_codes: tuple[str, ...]`. O próprio `DomainModel` aplica ao texto sanitizado o vetorizador TF-IDF já ajustado de seu pipeline e calcula `zero_vector = (vector.nnz == 0)` por linha, tanto na chamada escalar quanto no lote; não reajusta nem usa outro vocabulário para essa medição. Vetor zero retorna `invalid_input`, `zero_vector=true` e motivo `ood_zero_vector`; falha/ausência de vetorizador retorna `zero_vector=null` e motivo `ood_check_unavailable`, nunca `false` presumido. Somente `ok` permite label/distribuição/confiança; confiança é o máximo da distribuição, labels pertencem à taxonomia, valores finitos em [0,1] e soma dentro de 1e-6 de 1. Falha do modelo retorna estado explícito, nunca probabilidades fictícias. Métricas dos candidatos rejeitados continuam disponíveis como evidência de avaliação, sem virar predição operacional.

`RoutingPolicy` contém `domain`, `rules_version`, `model_version: str | None`, `automation_enabled: bool`, `threshold: float | None`, `disabled_reason: str | None`, `sensitive_labels: tuple[str, ...]`, regras de texto/sinais e evidência de seleção. Escolher menor threshold da grade 0,50–0,95/0,05 com conjunto aceito não vazio e erro seletivo ≤10% na parte `policy_selection`, depois de aplicar os mesmos bloqueios de risco. Sem candidato válido: `automation_enabled=false, threshold=null`; confiança 1,0 não contorna desativação. Não reajustar calibrador após selecionar o threshold.

`TicketSignals` contém `domain`, `ticket_id`, `input_valid: bool`, `privacy_passed: bool`, `artifact_valid: bool`, `priority: Literal["Low", "Medium", "High", "Critical"] | None`, `zero_vector: bool | None`, `ambiguous: bool`, `sensitive_matches: tuple[str, ...]`, `validation_reasons: tuple[str, ...]`. `derive_signals(text, *, domain, ticket_id, priority, prediction, policy, artifact_valid, privacy_passed) -> TicketSignals` é a única derivação, reutilizada no pipeline/UI. Copia `prediction.zero_vector` sem inferir a partir da confiança ou do texto: `true` acrescenta `ood_zero_vector`; `null` acrescenta `ood_check_unavailable`; ambos tornam `input_valid=false` e obrigam revisão humana. Entrada vazia/sem tokens, domínio/classe incompatíveis e distribuição inválida também bloqueiam. OOD observável começa com vetor TF-IDF zero; ambiguidade usa diferença top-1/top-2 <0,10, constante conservadora declarada na política antes do teste, não uma garantia de detecção de todo OOD. Prioridade desconhecida em Customer é inválida; IT usa `None` e declara prioridade não observada. Matches usam categoria conhecida/predita e lista explícita de expressões sensíveis versionadas; indisponibilidade de um detector obrigatório bloqueia. Mostrar limites desses detectores na evidência. Os testes escalar/lote e do gate devem provar propagação de vetor zero/medição indisponível, inclusive contra uma distribuição adversarial com confiança 0,99.

`decide_route(prediction: Prediction, signals: TicketSignals, policy: RoutingPolicy) -> RouteDecision`; `RouteDecision` contém `action: auto_route | human_review`, `reason_codes: tuple[str, ...]`, `threshold: float | None`, `rules_version`, `model_version: str | None`. A ordem é invalidez/privacidade/artefato → risco/sensibilidade/Critical → modelo/automação desativada → confiança. Nunca aceitar sinais fornecidos pelo cliente como decisão já validada. Regras Customer incluem Billing inquiry/Refund request/Cancellation request; IT inclui HR Support/Access/Administrative rights, explicitamente justificadas como risco semântico quando não há desfechos operacionais. Guardar contagens e IDs sanitizados de exemplos, sem alterar política pelos resultados finais.

`priority_score(priority, confidence: float | None, risk_count: int) -> tuple[int, int, float]` retorna ordinal Critical=4/High=3/Medium=2/Low=1/ausente=0, quantidade de bloqueios de risco distintos e incerteza `1-confidence` (1 quando indisponível). Ordenar tupla decrescente e desempatar por `ticket_id` crescente. Exibir os três componentes; não inventar SLA, idade ou prioridade IT. `evaluate_frozen_test(model_result: ModelTrainingResult, test: pd.DataFrame, policy: RoutingPolicy) -> ModelMetrics` recebe configuração já bloqueada e produz macro-F1, classes/support, confusão, log loss, ECE em 10 bins fixos e risco/cobertura com denominadores. Métrica não calculável é nula com motivo; conjunto aceito vazio tem risco nulo, não zero.

### Recuperação e revisão humana

`fit_retriever(train_closed: pd.DataFrame) -> TicketRetriever` indexa somente descrição/resolução sanitizada e não vazia, domínio Customer, status fechado e grupo de treino permitido. `TicketRetriever.suggest(text: str, policy: RetrievalPolicy, *, signals: TicketSignals) -> RetrievalResult` retorna `status: draft | abstain | unavailable`, `sources: tuple[SourceMatch, ...]`, `draft: str | None`, `reason_codes`, `index_version`, `policy_version`, `threshold: float | None`. `SourceMatch` contém `ticket_id`, `similarity: float`, `resolution: str`, `text_group_id`; máximo três, similaridade finita em [0,1], desempate por ID. O parâmetro `signals` é obrigatório e vem de `derive_signals` para o mesmo texto sanitizado/ticket, tanto no pipeline quanto na UI; nenhum caller pode reconstruir um draft copiando diretamente uma fonte. Dentro de `suggest`, antes de materializar qualquer draft, exigir domínio Customer, `input_valid=true`, `privacy_passed=true`, `artifact_valid=true`, `zero_vector=false`, `ambiguous=false`, prioridade conhecida diferente de Critical e `sensitive_matches` vazio, além da política de recuperação habilitada e score elegível. Qualquer falha retorna `draft=null` e motivo correspondente, independentemente de confiança/similaridade; PII/invalidez impede a própria consulta e retorna fontes vazias. Para Critical/sensível com entrada sanitizada válida, fontes seguras podem permanecer visíveis apenas como consulta, com draft bloqueado. Draft autorizado copia apenas a resolução da primeira fonte segura; score é similaridade, não confiança calibrada. `tests/test_retrieval.py` e `tests/test_workflow.py` devem exercer pipeline e UI com Critical, sensibilidade e privacidade reprovada mesmo com score 1,0, comprovando ausência de draft e de aprovação habilitada.

`RetrievalPolicy` contém `drafts_enabled`, threshold opcional, `policy_version`, `packet_id`, `calibration_rubric_sha256: str | None`, `status: pending_review | enabled | disabled | insufficient_evidence`. `evaluate_retriever(retriever, unseen: pd.DataFrame, rubric_path: Path) -> RetrievalMetrics` valida IDs, scores humanos, autoria e versão antes de reportar resultados; nunca modifica política. `RetrievalMetrics` registra população/amostra, completude, médias por dimensão, contagens inseguras, cobertura e motivo de abstinência.

O CLI `python -m support_copilot.retrieval prepare-review --artifacts artifacts --split calibration|test` gera pacote a partir dos splits existentes, sem novo split/treino. Cada pacote associa `packet_id`, hashes de fonte/split/índice/configuração, IDs de consulta/fonte, similaridade e estado de elegibilidade. Seleção: seed 42, estratos por tipo, sem reposição, sobre consultas sanitizadas com texto e resolução de referência seguros; elegibilidade não depende de score alto. O pacote de revisão mostra contexto e resolução de referência retida para o humano, mas esta resolução nunca entra no índice. Sem fonte, usar `source_id` vazio e registrar abstinência, sem fabricar avaliação favorável.

O CSV humano mantém `query_id,source_id,relevance,correctness,safety,edit_effort,reviewer_notes` e acrescenta `packet_id,reviewer_id,reviewed_at`; notas são sanitizadas, autor pode ser pseudônimo estável. Todas as quatro escalas são 1–5, com âncoras documentadas (relevância/correção/segurança: 1 inadequado, 5 adequado; edição: 1 nenhuma, 5 reescrita completa). Ausência de candidato recebe marcação explícita no pacote e não é aceita no denominador de draft. `lock-review --artifacts artifacts --rubric evidence/retrieval-calibration-rubric.csv` valida pacote inteiro, aplica a grade 0,20–0,90/0,10 e grava `artifacts/review/retrieval-policy-lock.json`. Entre subconjuntos aceitos não vazios, escolher menor threshold com médias de correção/segurança ≥4 e nenhum safety <3; campos não preenchidos não viram zeros ou acertos. Lock guarda hashes e decisão inclusive quando desabilitada.

Somente após modelo, calibração, regras, thresholds de roteamento e decisão de recuperação bloqueados, liberar pacote opcional de 30 consultas de teste independente. Rubrica de teste descreve qualidade futura e nunca ajusta threshold; reprovação pode apenas desativar assistência e registrar que uma futura versão exigirá nova avaliação independente. Menos de 30 consultas distintas elegíveis em qualquer split gera `insufficient_evidence`, com contagem real, sem reposição, duplicação ou relaxamento do gate. Nesse caso manter assistência bloqueada e explicar a limitação; CK-12 não é gate da entrega canônica. Rubrica ausente/incompleta impede somente declarar recuperação validada. Para uma demonstração sem revisão, registrar explicitamente decisão congelada `disabled/pending_review` antes de abrir teste; não habilitar depois usando conhecimento adquirido no teste da mesma versão.

### Auditoria atômica e export persistido

Banco local: `data/runtime/decisions.sqlite3`, ignorado pelo Git e separado dos artefatos regeneráveis. Uma tabela `decisions` e `PRAGMA user_version=1`; versão desconhecida impede escrita com correção explícita, sem apagar ou recriar banco existente. SQLite usa parâmetros, transação explícita, fechamento de conexão e `submission_id UNIQUE`. Um UUID por envio permanece estável durante reruns/tentativas; repetição idêntica retorna o mesmo registro, payload divergente para UUID existente falha.

`DecisionEvent` possui `submission_id: str`, `ticket_id`, `domain`, `data_version: str | None`, `model_version: str | None`, `rules_version: str | None`, `retrieval_version: str | None`, `threshold: float | None`, `retrieval_threshold: float | None`, `prediction_status`, `suggested_label: str | None`, `confidence: float | None`, `gate_action`, `reason_codes: tuple[str, ...]`, `source_ids: tuple[str, ...]`, `human_action: approve | edit_approve | reject | escalate`, `human_reason: str | None`, `suggestion_text: str | None`, `final_text: str | None`. `StoredDecision` acrescenta `id: int`, `created_at: str` UTC ISO-8601 e `edit_ratio: float | None`. Campos indisponíveis ficam SQL NULL com motivo explícito; não inventar versão/label/confiança para manter NOT NULL. Dados/configuração conhecidos permanecem obrigatórios mesmo se modelo estiver indisponível.

`initialize_store(path: Path) -> None` cria/valida schema; `record_decision(connection: sqlite3.Connection, event: DecisionEvent) -> StoredDecision` valida snapshot calculado pelos módulos, sanitiza novamente, grava e retorna registro confirmado; `list_decisions(connection) -> list[StoredDecision]` ordena por ID. Aprovar exige draft seguro não vazio e final igual à sugestão; editar e aprovar exige draft existente e resposta final não vazia após sanitização. Rejeitar/escalonar exigem motivo e final nulo; abstinência não pode confirmar resposta inexistente. `edit_ratio = 1 - SequenceMatcher(None, suggestion, final).ratio()` sobre valores sanitizados; nulo para rejeição/escalonamento/ausência de draft. Falha reverte só a transação atual e mantém o formulário para nova tentativa. UI mostra sucesso apenas após reler o ID por nova conexão.

`export_decisions_csv(connection, destination: Path) -> ExportResult`, com `ExportResult(path: Path, content: bytes, row_count: int, sha256: str)`. Exportar snapshot consistente dos registros commitados em ordem de ID; incluir todos os campos de `StoredDecision`, listas como JSON compacto e nulos como célula vazia. Strings vazias opcionais são normalizadas para nulo na gravação, evitando ambiguidade. UTF-8, cabeçalho fixo, newline LF e quoting via `csv`; neutralizar células textuais cujo primeiro caractere significativo seja `=,+,-,@` ou tab/CR/LF com prefixo de apóstrofo, inclusive variantes com whitespace/control chars. Armazenamento conserva texto sanitizado original; README documenta a transformação no CSV e o teste em planilha.

Destino normal: `data/runtime/exports/decisions-<uuid>.csv`, escrito primeiro em arquivo temporário irmão e finalizado por rename atômico, sem sobrescrever export anterior. `st.download_button` usa exatamente `ExportResult.content` do arquivo persistido; falha ao gravar não anuncia export salvo. A evidência pública será `evidence/decisions-demo.csv`, cópia revisada de export real contendo ao menos o ID de um escalonamento humano; aprovação/edição é incluída somente se houver draft seguro habilitado. Pode restringir linhas por IDs, mantendo todos os campos e valores exportados. Registrar hash, IDs e relação com screenshot em `evidence/metrics.json`/README; nunca publicar o banco completo. Se assistência validada não permitir aprovação real, não fabricar evento: o escalonamento persistido demonstra a intervenção humana exigida pelo briefing e a limitação fica explícita.

### Manifesto, reprodução e disponibilidade

`write_manifest(manifest: Manifest, destination: Path) -> None` substitui a assinatura incompleta `write_manifest(paths, destination)`. Valida estrutura e serializa JSON canônico ordenado por chave via escrita atômica. `Manifest` contém os seguintes campos obrigatórios:

| Campo | Contrato |
|---|---|
| `schema_version`, `generated_at`, `code_revision`, `configuration_sha256`, `lock_sha256` | Versão inteira 1, timestamp UTC, revisão+fingerprint do diff quando necessário e hashes da configuração/lock reais; generated_at é volátil. |
| `runtime` | Python e dict de versões exatas das dependências; nenhuma credencial/caminho pessoal. |
| `sources: dict[Domain, SourceManifest]` | Nome do arquivo, SHA-256 dos bytes, schema/colunas permitidas, total de linhas, exclusões/qualidade, `data_version`, `sanitizer_version`. |
| `splits: dict[Domain, SplitManifest]` | Seed, estratégia/deduplicação, `split_version`, IDs/grupos train/calibration/test e subdivisões calibration_fit/policy_selection, contagens por classe e exclusões justificadas. |
| `models: dict[Domain, ModelManifest]` | Estado/suporte, candidato, features/taxonomia, CV, calibração, model_version opcional, política de automação, threshold opcional, hash da configuração congelada. |
| `retrieval: RetrievalManifest` | Índice/split de referência, versões, packet IDs, hashes de rubricas, lock, threshold opcional, status e números de consultas elegíveis/revisadas. |
| `artifacts: dict[str, ArtifactEntry]` | Chave lógica estável → caminho relativo dentro de artifacts, tipo/schema, SHA-256, hash lógico, domínio opcional, dependências e `status: ready | unavailable`/motivo. Entradas indisponíveis têm caminho/hash nulos. |

`artifacts/manifest.json` não lista seu próprio hash recursivamente. `data_version` depende de fonte/schema/sanitizador/agrupamento; `model_version` inclui split/features/seleção/calibração/lock; `rules_version` inclui regras e thresholds. `load_artifacts(root: Path) -> ArtifactBundle` em `ui.py` retorna por chave `FeatureState(status: ready | missing | corrupt | incompatible | stale, value: object | None, path: str, reason: str | None, correction="make reproduce")`. Falha na raiz/manifesto bloqueia dependentes; falha no modelo IT não bloqueia análises Customer ou eventos já salvos. As dependências declaradas determinam a propagação, sem tolerar uso de valor cacheado antigo.

Resolver caminhos sob raiz local confiável, rejeitar traversal/symlinks para fora, conferir schema/versões/hashes antes de desserializar joblib. Manifesto e binários locais não são uploads aceitos: hashes provam consistência, não autenticidade contra alteração maliciosa de ambos. Não adicionar download de modelo. Chaves de cache incluem manifesto/versões, não só nome de arquivo; regeneração invalida o recurso afetado.

O comando canônico permanece `python scripts/reproduce.py --customer data/raw/customer_support_tickets.csv --it data/raw/all_tickets_processed_improved_v3.csv --output artifacts`. Primeiro produz desenvolvimento/pacote de calibração; rubricas humanas bloqueiam apenas assistência/evidência correspondente. Depois de locks válidos ou decisão explícita de desativação, emite teste/queue/métricas. Reexecução com rubrica/hash incompatível falha com motivo, sem retunar de forma silenciosa. Saídas temporárias e manifesto publicado por último impedem leitores de usar conjuntos parcialmente atualizados; hashes divergentes durante atualização desabilitam o recurso até conclusão.

Artefatos previstos: `manifest.json`, `risk-policy.json`; seis relatórios sob `analytics/` já listados na análise; `models/customer.joblib`, `models/it.joblib`, `models/metrics.json`; `retrieval/customer.joblib`, `retrieval/metrics.json`; `review/retrieval-calibration-template.csv`, `review/retrieval-test-template.csv`, `review/retrieval-policy-lock.json`; `queue/customer-test.csv`. Binário sem modelo suportado não é criado; manifesto registra indisponibilidade. Templates de teste não aparecem antes dos locks. Métricas JSON carregam domínios separados e status quando indisponíveis.

Reprodução idêntica compara entradas, splits, políticas, predições, tabelas e métricas canônicas; timestamp é excluído só da comparação documentada. Hash binário verifica integridade da instância, enquanto `logical_sha256` cobre conteúdo lógico estável de modelos/relatórios quando serialização tiver metadados voláteis. Seed e ordenação são fixadas; diferenças numéricas admitidas precisam ser explicitadas no teste (tolerância absoluta 1e-9 para saídas float no mesmo lock), nunca absorvidas como novo baseline sem revisão.

`make demo` verifica ambiente preparado, reaproveita lock/dados/artefatos compatíveis e abre app; não força download/reinstalação/treino a cada uso offline. `make setup/data/reproduce` são etapas explícitas quando necessárias; ausência de fontes mostra URLs públicas, nomes esperados e destino para download manual, sem credenciais/fallback sintético. `make doctor` não reprova uso preparado por falta de internet. Geração pesada e suíte completa obedecem ao ambiente gerenciado e SHA/diff exato definidos nos critérios; nenhuma etapa de planejamento autoriza execução agora.

### Experiência e mudanças esperadas

`app.py` registra fila como página inicial, scorecard, Laboratório IT e evidências; `render_queue()`, `render_scorecard()`, `render_it_lab()` e `render_evidence()` retornam `None` e consomem um bundle validado, sem ajustar modelos. Estado do editor inclui domínio/ticket/versão da sugestão; trocar ticket não reaproveita rascunho anterior. Estado de envio conserva UUID até confirmar/abandonar a tentativa. Campos têm labels visíveis, ordem de foco natural, botões com nomes claros, erro associado ao formulário e status legível sem depender de cor. Usar controles nativos com teclado e contraste verificáveis; não substituir campos por HTML que remova semântica. AppTest verifica fluxo; navegador real verifica navegação por teclado, foco, renderização e download.

Scorecard separa as três naturezas de evidência exigidas; laboratório aceita texto sanitizado com modelo IT e prioridade não observada, sem contaminar a fila. Evidências mostram versões, indisponibilidades, limitações e decisões exportáveis. Falha de artefato informa caminho/causa/correção e conserva funções válidas; falha de banco conserva consultas/evidência e bloqueia confirmação de nova decisão até correção.

| Ação | Arquivos previstos |
|---|---|
| Criar ambiente e entrada | `pyproject.toml`, `requirements.lock`, `Makefile`, `.streamlit/config.toml`, `app.py`, `scripts/reproduce.py`, `src/support_copilot/__init__.py`. Package discovery deve existir já na prova de instalação. |
| Criar implementação | `src/support_copilot/data.py`, `analytics.py`, `modeling.py`, `decision.py`, `retrieval.py`, `store.py`, `ui.py`. |
| Criar verificações | `tests/test_data.py`, `test_analytics.py`, `test_modeling.py`, `test_decision.py`, `test_retrieval.py`, `test_store.py`, `test_workflow.py`; cobrem regressões reais dos contratos e fluxo persistido, sem novo framework. |
| Criar entrega revisada | `README.md` da solution, `../../README.md` da submissão; `evidence/metrics.json`, `operational-summary.json`, `screenshot.png`, `retrieval-calibration-rubric.csv`, `retrieval-test-rubric.csv`, `decisions-demo.csv`. Arquivos de evidência só recebem resultados reais após execução/revisão. |
| Modificar documentação/ignore | `.gitignore` para raw/artifacts/.venv/caches/data/runtime; `../../research/002-support.md` para a prova e lock; `../../process-log/002-support.md` para decisões/erros/verificação contemporâneos. |

Comparado ao inventário de impacto: um arquivo público adicional (`evidence/decisions-demo.csv`), total previsto de 29 criações, três modificações e nenhuma remoção; lock de revisão e exports runtime são gerados/ignorados. Nenhuma alteração em desafio, raiz do repositório, templates, workflows ou serviços. Scratchpads seguem ignorados. Todo staging futuro deve usar caminhos públicos explícitos, pois o ignore raiz oculta `submissions/`; a arquitetura não autoriza publicação, push ou implementação antes da revisão humana da SPEC.

## Implementation Process

Executar somente após aprovação humana registrada desta SPEC. Lançar **um agente por step**, passando o caminho atual do task file **e** o caminho do respectivo Sub-Task File; usar exatamente o **Model** e **Agent** daquele step, implementar apenas esse step e seus testes. Executar em paralelo os steps independentes indicados, respeitando dependências, propriedade de arquivos e o limite de dois agentes de implementação simultâneos. Tiers descrevem capacidade; na instalação atual mapear para modelos disponíveis sem acionar APIs pagas ou trocar provider automaticamente.

Ao concluir todos os steps de uma fase, executar `sdd:code-reviewer` **uma vez por fase**, no `Reviewer model` indicado, sobre o diff e as evidências completas do marco. A revisão é barreira entre fases; `Depends on` registra dependências de artefatos, não repete a barreira. Corrigir achados antes de prosseguir e registrar decisões/erros/testes no diário. O orquestrador serializa inserções no diário quando há agentes paralelos. Aprovação da SPEC não substitui as avaliações humanas de recuperação nem concede publicação.

### Parallelization Overview

```text
PHASE 1 — diagnóstico executável
  01 Ambiente/prova -> 02 Dados/splits/manifesto -> 03 Diagnóstico
  [review: opus]
===================== phase barrier =====================
PHASE 2 — fluxo completo com revisão pendente
  02 -> 04 Modelos/gate -> 06 Recuperação -----------+
  02 -> 05 Auditoria -------------------------------+-> 07 Integração
  03 ----------------------------------------------+
  04 ----------------------------------------------+
  02 --------------------> 06
  [review: opus; selar snapshot imutável S07 do workflow]
===================== phase barrier =====================
PHASE 3 — métricas, evidência real e avaliação opcional
  07/S07 -> 08 Métricas/freeze/revisão opcional --+
  07 -----> 09 Docs/workflow mutável ---+-> 10 Demo/suíte consolidada
  [review: opus]
```

Todos os caminhos da tabela são relativos à solution `submissions/luis-roquette/solution/002-support/`. Os diretórios de subtarefas não mudam quando o task file for promovido; atualizar `Task File` nos subtasks para sua localização atual.

Snapshot S07 é saída obrigatória de 07, selada após a revisão da fase 2: `data/runtime/validation/phase2-<workflow_sha256>/test_workflow.py`, cópia byte a byte do workflow daquele marco. Hash, caminho e fingerprint do código/configuração/lock ficam registrados no diário. A tabela conserva a dependência 08 → 07 porque 07 entrega esse snapshot; o paralelo 08/09 usa arquivos de teste diferentes.

| Step | Phase | Model | Agent | Depends on | Parallel with | Sub-Task File |
|---|---|---|---|---|---|---|
| 01 [DONE] | 1 | sonnet | sdd:developer | None | None | `.specs/sub-tasks/implement-support-decision-copilot/01-environment-proof.md` |
| 02 [DONE] | 1 | opus | sdd:data-engineer | 01 | None | `.specs/sub-tasks/implement-support-decision-copilot/02-sanitized-data-contracts.md` |
| 03 [DONE] | 1 | sonnet | sdd:data-engineer | 02 | None | `.specs/sub-tasks/implement-support-decision-copilot/03-operational-diagnostic.md` |
| 04 [DONE] | 2 | opus | sdd:ml-engineer | 02 | 05 | `.specs/sub-tasks/implement-support-decision-copilot/04-models-and-risk-gate.md` |
| 05 [DONE] | 2 | opus | sdd:developer | 02 | 04, 06 | `.specs/sub-tasks/implement-support-decision-copilot/05-transactional-audit.md` |
| 06 [DONE] | 2 | opus | sdd:ml-engineer | 02, 04 | 05 | `.specs/sub-tasks/implement-support-decision-copilot/06-safe-retrieval-and-review.md` |
| 07 [DONE] | 2 | opus | sdd:developer | 03, 04, 05, 06 | None | `.specs/sub-tasks/implement-support-decision-copilot/07-integrated-local-workflow.md` |
| 08 [DONE] | 3 | opus | sdd:ml-engineer | 07 | 09 | `.specs/sub-tasks/implement-support-decision-copilot/08-human-evaluation-and-freeze.md` |
| 09 [DONE] | 3 | sonnet | sdd:tech-writer | 07 | 08 | `.specs/sub-tasks/implement-support-decision-copilot/09-delivery-documentation.md` |
| 10 [DONE] | 3 | sonnet | sdd:test-engineer | 08, 09 | None | `.specs/sub-tasks/implement-support-decision-copilot/10-real-demo-and-final-gates.md` |

Caminho de execução mais longo, incluindo barreiras: 01 → 02 → 03 → revisão da fase 1 → 04 → 06 → 07 → revisão da fase 2/S07 → 08 → 10 → revisão da fase 3. Avaliação humana no step 08 ocorre somente se houver população elegível e não bloqueia o prazo canônico; na insuficiência, a assistência permanece desativada. Largura máxima: dois steps, sem escrita concorrente nos mesmos arquivos. Na fase 2, 05 documenta armazenamento no README e 06 documenta o protocolo exclusivamente no docstring/ajuda CLI de `retrieval.py`. Na fase 3, 08 escreve evidence/testes modeling/retrieval e executa somente o teste de reprodução em S07 com hash conferido antes/depois; 09 escreve READMEs/workflow mutável e executa só seu teste documental. Nenhum deles coleta a suíte inteira durante o paralelo. Step 10 executa workflow e suíte final consolidados após ambos; S07 não substitui evidência do estado final.

### Phase Overview

#### Phase 1 [REVIEWED]

**Steps:** 01, 02, 03.

**Reviewer model:** opus — teto disponível e mesmo tier do contrato compartilhado de dados.

**Acceptance Criteria that should be fulfiled:** aplicação diagnóstica local executável com fontes reais sanitizadas, qualidade rastreável, análises válidas e cenários editáveis; teste final lacrado e capacidades futuras claramente indisponíveis. Reviewer executa prova do ambiente e testes de dados/análise, inspeciona relatório/denominadores e painel. Não exige ainda fila final, rubricas humanas ou métricas finais.

**Checklist items:**

- CK-2 — sanitização/quarentena e exclusão de dados privados no fluxo disponível; regressões de UI/export continuam nas próximas fases.
- CK-3 — fonte, schema, qualidade, exclusões e separação dos domínios.
- CK-4 — diagnóstico temporal observado e denominadores reconciliáveis.
- CK-5 — associação com satisfação sustentada por baseline ou ausência de sinal declarada.
- CK-6 — excesso elegível e projeções editáveis explicitamente distintas.

**Rubrics:**

- Operational Evidence Honesty.
- Independent and Reproducible Validation — fontes/splits de desenvolvimento, sem alegação de avaliação final.
- Project Guidelines Alignment — Regra Zero, aprovação inicial e ambiente comprovado.

#### Phase 2 [REVIEWED]

**Steps:** 04, 05, 06, 07.

**Reviewer model:** opus — teto disponível, cobrindo integridade e integração dos contratos.

**Acceptance Criteria that should be fulfiled:** aplicação completa executável em modo seguro de revisão pendente, com os quatro fluxos demonstráveis por fixtures sanitizadas, persistência real em banco temporário e artefatos inválidos isolados. Desenvolvimento real gera pacote de calibração; teste real permanece lacrado. Reviewer usa testes de módulos/AppTest e reinício/export; fixtures não contam como evidência final da submissão.

**Checklist items:**

- CK-7 e CK-9 — isolamento/freeze comprovados e gate com risco prevalente, incluindo indisponibilidade/OOD.
- CK-10 e CK-11 — prioridade explicável, política versionada e recuperação restrita com abstinência.
- CK-13 e CK-14 — quatro ações válidas, integridade SQLite e export persistido.
- CK-15 — fila inicial, estados/labels e workflow disponíveis; prova visual real final ocorre na fase 3.
- CK-17 — artefatos inválidos bloqueiam apenas funções afetadas com causa/correção.

**Rubrics:**

- Safe Decision and Response Boundaries.
- Independent and Reproducible Validation — calibração/locks e impossibilidade de antecipar teste.
- Agent Workflow and Durable Evidence — execução com fixtures identificadas e registros persistidos.
- Project Guidelines Alignment — gates do diff e diário contemporâneo.

#### Phase 3 [REVIEWED]

**Steps:** 08, 09, 10.

**Reviewer model:** opus — teto disponível para independência da avaliação e evidências finais.

**Acceptance Criteria that should be fulfiled:** diagnóstico concreto do Dataset 1, aplicação demonstrada nos dois domínios reais, configuração congelada, reprodução equivalente e entrega documentada com screenshot/export de escalonamento correlacionados. Reviewer confere automação e não automação, fluxo funcional, process log, números/denominadores e ROI transparente no SHA/diff pretendido. Rubricas humanas são validação futura opcional; ausência de amostra mantém drafts bloqueados, sem bloquear a conclusão canônica.

**Checklist items:**

- CK-1 e CK-18 — execução local/offline preparada e reprodução real rastreável.
- CK-8 — medições finais por domínio. CK-12 — insuficiência ou avaliação opcional documentada, sempre fail-closed.
- CK-16 — scorecard e Laboratório IT reais, conectados somente por evidências agregadas.
- CK-19 e CK-20 — template/READMEs/diário/evidências reais, aprovação da SPEC e integridade documental dos gates, incluindo preflight pulado como não executado/não verde.
- CK-2–7, CK-9–11, CK-13–15 e CK-17 — regressão final do comportamento já entregue, incluindo tela/export sem PII e escalonamento persistido; aprovação/edição real somente se houver draft seguro.

**Rubrics:**

- Operational Evidence Honesty.
- Safe Decision and Response Boundaries.
- Independent and Reproducible Validation.
- Agent Workflow and Durable Evidence.
- Project Guidelines Alignment.
