# Diário de processo — Challenge 003: Lead Scorer

## I01 — Briefing absorvido por releitura em loop — 2026-09-21 14:28 BRT

- **Objetivo:** compreender integralmente o desafio antes de pesquisar soluções, analisar dados ou construir a ferramenta.
- **IA/ferramenta:** Codex para leitura sistemática; Git e GitHub CLI para confirmar a fonte e a versão do arquivo.
- **Ação ou prompt:** Luis definiu um gate de absorção: reavaliar o briefing por lentes diferentes até completar pelo menos duas passadas consecutivas sem novos achados.
- **Resultado:** cinco passadas concluídas; as passadas 2 a 5 não produziram novas descobertas. O README local corresponde ao commit-fonte `d4c8fc7e20cc99370df5cc438aa553bb4a9789b2` e tem SHA-256 `0f88457c166c0b945ef645dfb25ae35021d38a6dab92e4af613ddcc8253dd466`.
- **Julgamento humano:** a leitura em loop e o critério de parada são um diferencial criativo de Luis. A IA executou e documentou o protocolo, sem apresentar a técnica como sugestão própria.
- **Verificação:** releitura integral normal e reversa, conferência estrutural das 100 linhas e teste de 11 invariantes textuais; a fonte local não apresentou diferença contra o commit do challenge.
- **Evidência:** este ledger, o hash do arquivo e o histórico Git do README avaliado.
- **Limitação:** os dados ainda não foram inspecionados e nenhuma hipótese de scoring foi validada.

### Ledger das passadas

| Passada | Lente | Novos achados |
|---|---|---|
| 1 | leitura literal e documentos vinculados | problema comercial, quatro tabelas, solução funcional, documentação, process log, critérios, dicas, template e regras do PR |
| 2 | requisitos normativos | nenhum |
| 3 | conferência linha a linha | nenhum |
| 4 | conferência integral em ordem reversa | nenhum |
| 5 | identidade da fonte e matriz de invariantes | nenhum |

**Gate atingido:** pelo menos duas passadas consecutivas sem novos achados. Pesquisa e construção continuam bloqueadas até a Regra zero ser cumprida.

### Compreensão consolidada

O problema não é prever fechamento em abstrato. É substituir a priorização “no feeling” por uma fila diária que ajude 35 vendedores a decidir onde agir dentro de aproximadamente 8.800 oportunidades. O software precisa funcionar com os dados reais, ir além de ordenar por valor e explicar por que cada deal recebeu prioridade alta ou baixa.

O `sales_pipeline.csv` é a tabela central e se conecta a contas, produtos e equipe comercial. Antes de definir qualquer score, as chaves, cardinalidades, ausências e distribuição temporal precisam ser medidas. O briefing comum adiciona um limite decisivo: deals ativos não podem usar `close_date`, `close_value` nem estágio final como features, pois isso vazaria o resultado futuro.

Complexidade de modelo não é o objetivo. Regras ou heurísticas bem validadas e explicáveis podem superar um modelo opaco se ajudarem o vendedor a tomar uma ação na segunda-feira de manhã. Filtros por vendedor, manager e região são um bônus de alto valor, não substitutos dos requisitos mínimos.

A entrega precisa incluir setup reproduzível, lógica e limitações, além de evidências do processo. A pesquisa externa e a inspeção dos dados decidirão a tecnologia, os critérios do score e se o diferencial proposto — fila por vendedor com motivos, risco de esfriar e próxima ação — é sustentado pelos dados.

### Erro registrado nesta etapa

No primeiro verificador local, a variável de shell `path` sobrescreveu o `PATH` especial do `zsh`, e o comando `git` deixou de ser localizado. A variável foi renomeada para `challenge_file`; o verificador passou sem alterar arquivos.

## I02 — SDD adotado antes da construção — 2026-09-21 14:36 BRT

- **Objetivo:** tornar a especificação verificável o contrato de entrada para pesquisa, arquitetura e implementação do Lead Scorer.
- **IA/ferramenta:** plugin SDD `3.6.0` do `NeoLabHQ/context-engineering-kit`, baseado em GitHub Spec Kit, OpenSpec e arc42 adaptado.
- **Ação ou prompt:** Luis decidiu seguir Spec-Driven Development e indicou a instalação `npx skills add NeoLabHQ/context-engineering-kit --skill sdd --agent claude-code`.
- **Resultado:** o plugin já estava instalado, habilitado e atualizado no Claude Code. O estágio `add-task` criou somente um rascunho da intenção em `solution/003-lead-scorer/.specs/tasks/draft/`; isso ainda não é uma SPEC. Nenhum planejamento ou código foi iniciado.
- **Julgamento humano:** a escolha de SDD é de Luis. A metodologia será combinada com a Regra zero, Ponytail `full` e os gates de evidência do briefing; não substitui pesquisa, validação humana ou limites contra leakage.
- **Verificação:** `claude plugin details sdd@context-engineering-kit` confirmou versão `3.6.0`, cinco skills, oito agentes e status habilitado; `claude plugin update` confirmou a versão mais recente.
- **Evidência:** `solution/003-lead-scorer/.specs/tasks/draft/implement-explainable-lead-scorer.feature.md` e este registro.
- **Limitação:** a SPEC ainda não existe. `/plan-task` e `/implement-task` não foram executados; antes deles, o projeto será discutido e arquitetado com Luis.

### Fluxo acordado

1. `add-task`: preservar a intenção original em `draft`.
2. `plan-task`: pesquisar, analisar negócio e código, definir arquitetura, critérios de aceitação, testes e subtarefas.
3. Revisar a especificação contra o briefing, a Regra zero e o risco de leakage.
4. `implement-task`: construir por fases, com revisão e evidência em cada gate.
5. Mover a tarefa para `done` somente após definição de pronto e validações reproduzíveis.

### Erro e correção desta etapa

O comando publicado pela página do recurso falhou com `No matching skills found for: sdd`: o CLI encontrou 68 skills individuais, mas `sdd` é um plugin composto, não uma skill isolada. A instalação oficial do próprio repositório foi conferida; `sdd@context-engineering-kit` já estava instalado e habilitado, então apenas o atualizamos e validamos em vez de duplicá-lo.

## I03 — Documentar é parte central da entrega — 2026-09-21 14:39 BRT

- **Objetivo:** preservar decisões, correções, evidências e contribuições humanas enquanto o trabalho acontece.
- **Decisão de Luis:** o diário é tão importante quanto — ou até mais importante que — o resultado final. Ganha quem documenta.
- **Formato:** fragmentos curtos, objetivos e diretos são suficientes, desde que registrem os destaques apontados por Luis e os marcos relevantes do processo.
- **Regra editorial:** corrigir ortografia, gramática e clareza antes de registrar, sem alterar a intenção original.
- **Disciplina:** registrar continuamente; não depender da memória nem reconstruir retroativamente prompts, horários, erros ou decisões.
- **Julgamento humano:** esta prioridade e a obsessão pelo registro foram definidas por Luis, não pela IA.

Luis resumiu o princípio com uma frase atribuída a Silvio Santos:

> “Sabe por que o ovo da galinha vende mais que o da pata? Porque a galinha canta quando bota!”

**Princípio permanente:** fazer um bom trabalho não basta; o processo precisa deixar evidência clara, fiel e útil. O diário é parte do produto.

## I04 — Deliberação socrática por ondas adaptativas — 2026-09-21 14:42 BRT

- **Objetivo:** construir entendimento e arquitetura sólidos antes de escrever a SPEC.
- **Correção de estado:** existe apenas um rascunho `add-task`; ainda não discutimos suficientemente o projeto e não há SPEC pronta para revisão.
- **Decisão de Luis:** conduzir a descoberta em pelo menos cinco ondas de perguntas socráticas. As ondas posteriores devem depender das respostas anteriores, não de um questionário fixo preparado de antemão.
- **Método:** fazer uma pergunta por vez, testar premissas, pedir exemplos concretos, expor tensões e registrar decisões, alternativas rejeitadas, dúvidas e evidências ao final de cada onda.
- **Gate:** não executar `/plan-task`, desenhar arquitetura definitiva ou implementar enquanto as ondas não convergirem e Luis não validar a síntese do desenho.
- **Julgamento humano:** objetivos, prioridades e escolhas finais pertencem a Luis; a IA organiza a investigação, desafia pressupostos e transforma decisões aprovadas em especificação verificável.

### Mapa provisório das ondas

1. **Resultado e usuário:** qual decisão precisa melhorar, para quem e em qual momento do trabalho.
2. **Fluxo comercial:** como a priorização funciona hoje, onde falha e qual mudança seria realmente adotada.
3. **Dados e verdade temporal:** quais sinais podem ser usados, quando ficam disponíveis e como impedir leakage.
4. **Score e explicação:** o que significa prioridade, como justificar o ranking e qual próxima ação deve aparecer.
5. **Experiência e operação:** interface, filtros, frequência, exceções, fallback e limites de manutenção.
6. **Arquitetura e prova:** alternativas técnicas, trade-offs, testes, critérios de aceitação e definição de pronto.

O mapa é intencionalmente provisório. Cada resposta pode reordenar, dividir, ampliar ou eliminar perguntas e ondas. Ao final da descoberta, serão comparadas alternativas de solução; o desenho escolhido será apresentado em partes curtas para validação antes de alimentar o `/plan-task`.

## I05 — Registro contínuo da sessão socrática — 2026-09-21 14:48 BRT

- **Decisão de Luis:** registrar no diário todas as perguntas e respostas desta sessão de descoberta.
- **Forma de registro:** corrigir o português, preservar o sentido e anotar a decisão resultante sem transformar resposta parcial em requisito definitivo.
- **Estado:** Onda 1 em andamento; uma decisão aprovada e seus detalhes ainda em investigação.

### Onda 1 — Resultado e usuário

#### Pergunta 1

Na segunda-feira de manhã, qual decisão principal o vendedor deve conseguir tomar em até 60 segundos ao abrir a ferramenta?

#### Resposta de Luis

**D:** uma fila única que combine prioridade, risco, valor e próxima ação.

#### Decisão registrada

A experiência principal será uma fila unificada de trabalho, não quatro relatórios separados. A resposta ainda não define pesos, regras de desempate, público secundário ou forma de cálculo; esses pontos permanecem abertos para as próximas perguntas.

#### Pergunta 2

Quem precisa usar a primeira versão?

#### Resposta de Luis

**B:** vendedor e manager, com visão individual e da equipe.

#### Decisão registrada

A primeira versão terá dois públicos. O vendedor precisa operar a própria fila; o manager precisa enxergar o desempenho e as prioridades da equipe. Permissões de alteração, intervenção e redistribuição ainda não foram definidas.

#### Pergunta 3

O que o manager poderá fazer na primeira versão?

#### Resposta de Luis

**D:** visualizar, orientar, repriorizar e redistribuir deals.

#### Decisão registrada

O manager será um usuário operacional, não apenas observador. A solução deverá permitir visão da equipe, orientação ao vendedor, alteração de prioridade e redistribuição de oportunidades. Regras de permissão, histórico de alterações, conflitos e reversão permanecem abertas e precisarão ser tratadas em ondas posteriores.

#### Pergunta 4

Qual será a métrica principal de sucesso?

#### Resposta de Luis

**D:** aumento da receita esperada por vendedor.

Luis descartou “percentual de deals prioritários trabalhados em até 24 horas” como métrica norteadora porque isso deixaria uma análise importante e ambígua para a IA decidir. Considera a receita esperada por vendedor uma referência mais confiável.

#### Decisão registrada

A receita esperada por vendedor será a métrica norteadora; velocidade de ação, redução de deals frios e taxa de fechamento poderão funcionar como métricas auxiliares. A escolha reduz o risco de otimizar mera atividade, mas ainda exige uma fórmula independente, auditável e baseada apenas em informações disponíveis no momento do score. Sem isso, “receita esperada” poderia se tornar uma estimativa circular produzida pelo próprio modelo.

#### Pergunta 5

O que “receita esperada” deve significar na primeira versão?

#### Resposta final de Luis

**A:** probabilidade de fechamento × preço do produto.

#### Correção registrada

Uma mensagem intermediária respondeu apenas “C”, mas Luis a substituiu explicitamente pela opção A. A resposta final acima prevalece; a opção C não foi tratada como decisão aprovada.

#### Decisão registrada

A receita esperada de cada deal será calculada como `probabilidade de fechamento × preço do produto`. O preço vem do catálogo; a probabilidade ainda precisa ser definida, calibrada e validada somente com informação disponível no momento do score. O cálculo deverá mostrar os dois componentes ao usuário.

#### Pergunta 6

Como devemos provar que a fila melhora a receita por vendedor?

#### Resposta de Luis

**D:** duas etapas — backtest agora e piloto operacional depois.

#### Decisão registrada

A entrega atual deverá comparar retrospectivamente o ranking com resultados reais sem leakage. Como o dataset não prova adoção nem impacto causal em produção, a validação definitiva ficará para um piloto posterior com vendedores, ações e receita observadas.

### Síntese da Onda 1 — aprovada

- **Experiência principal:** fila única com prioridade, risco, valor e próxima ação.
- **Usuários:** vendedor e manager; o manager visualiza, orienta, reprioriza e redistribui.
- **Métrica norteadora:** receita esperada por vendedor.
- **Fórmula-base:** `probabilidade de fechamento × preço do produto`, com componentes visíveis.
- **Prova:** backtest sem leakage na entrega; piloto operacional como validação posterior.

Continuam abertos: definição da probabilidade, fluxo comercial real, auditoria das ações do manager e desenho da interface.

#### Aprovação de Luis

Onda 1 aprovada sem alterações em 21 de setembro de 2026. O gate de resultado e usuários foi concluído.

### Onda 2 — Fluxo comercial

#### Pergunta 1

Qual falha do fluxo atual deve ser eliminada primeiro?

#### Resposta de Luis

**A, seguida de B:** primeiro eliminar a priorização subjetiva, feita “no feeling”; depois reduzir o esforço causado pelo volume excessivo de oportunidades.

#### Decisão registrada

A solução deve primeiro instituir um critério comum, explicável e auditável. A redução de carga cognitiva vem em seguida: o sistema usa esse critério para transformar o pipeline extenso em uma fila curta e acionável. Filtrar volume sem padronizar a decisão apenas automatizaria o “feeling”.

#### Pergunta 2

Em que momento do fluxo a ferramenta deve intervir primeiro?

#### Resposta de Luis

**B:** continuamente, reordenando a fila quando os dados mudarem.

Luis escolheu a opção depois de comparar fila diária, atualização contínua, publicação pelo manager e análise sob demanda.

#### Decisão registrada

O comportamento-alvo é uma fila continuamente recalculada a partir de novas informações do CRM. Como o dataset do challenge é estático, a entrega atual demonstrará o mesmo mecanismo ao recalcular após atualização ou recarga dos dados; não alegará possuir uma integração em tempo real que não foi construída nem validada.

#### Pergunta 3

Como evitar que a reordenação contínua torne a fila instável ou difícil de confiar?

#### Resposta de Luis

**B:** reordenar somente quando a mudança ultrapassar um limite relevante.

#### Decisão registrada

A atualização dos dados pode ser contínua, mas uma alteração pequena não deve mudar a ordem exibida. A fila terá um mecanismo de estabilidade: somente variações materiais atravessam o limite de reordenação. O valor e a unidade desse limite ainda não foram definidos e não serão inventados antes da análise dos dados.

#### Pergunta 4

Como o limite de mudança relevante deve ser definido?

#### Recomendação da IA

Combinar **B + D**: medir a mudança pela variação percentual da receita esperada e calibrar o percentual com dados reais, mantendo-o configurável. No protótipo estático, recalcular toda a fila quando os dados forem atualizados; no produto integrado, aplicar o limite calibrado.

#### Decisão de Luis

Recomendação aprovada sem alterações.

#### Decisão registrada

O protótipo fará recálculo completo após nova carga de dados. O produto real usará variação percentual da receita esperada, com limite configurável e calibrado durante o piloto. Nenhum percentual será inventado com o dataset estático, que não contém snapshots sucessivos suficientes para validar instabilidade da fila.

#### Pergunta 5

Como uma repriorização manual feita pelo manager deve conviver com o recálculo automático?

#### Resposta de Luis

**A:** a repriorização manual desaparece no próximo recálculo.

#### Decisão registrada

A intervenção do manager será temporária e não modificará score, pesos ou fórmula. O próximo recálculo restabelece integralmente a ordem derivada dos dados. Essa escolha mantém uma única fonte de verdade para o ranking, mas exige comunicar claramente ao manager que a mudança não é persistente.

#### Pergunta 6

Mesmo sendo temporária, a intervenção do manager deve deixar qual evidência?

#### Resposta de Luis

**B:** registrar apenas quem alterou e quando.

#### Decisão registrada

A auditoria mínima da repriorização guardará identidade do manager e horário. Justificativa, comparação antes/depois e resultado posterior do deal não serão obrigatórios na primeira versão.

### Síntese da Onda 2 — aprovada

- **Problema primário:** substituir priorização subjetiva; depois reduzir o volume analisado.
- **Atualização:** recalcular continuamente quando os dados mudarem, mas reordenar apenas após mudança material.
- **Protótipo:** recalcular toda a fila após nova carga; sem alegar integração em tempo real.
- **Produto real:** usar variação percentual configurável, calibrada no piloto.
- **Intervenção do manager:** repriorização temporária até o próximo recálculo, auditando apenas quem e quando.

Permanecem para ondas posteriores: persistência de redistribuições, definição da probabilidade, eventos disponíveis no tempo, interface e limites operacionais.

#### Aprovação de Luis

Onda 2 aprovada sem alterações em 21 de setembro de 2026. O gate de fluxo comercial foi concluído.

### Onda 3 — Dados e verdade temporal

#### Pergunta 1

Quais oportunidades devem receber score e aparecer na fila operacional?

#### Resposta de Luis

**A:** somente deals ativos — `Prospecting` e `Engaging`. Deals `Won` e `Lost` servem apenas para aprendizado e validação.

#### Decisão registrada

A fila operacional excluirá oportunidades encerradas. O histórico de `Won` e `Lost` poderá ensinar e testar a probabilidade de fechamento, mas seus campos de resultado não poderão vazar para as features usadas nos deals ativos.

#### Pergunta 2

Como devemos separar os deals históricos para estimar e validar a probabilidade de fechamento?

#### Resposta de Luis

**B:** divisão temporal — deals antigos treinam; deals mais recentes validam.

#### Decisão registrada

A validação deverá simular o futuro: nenhum deal com fechamento posterior poderá informar o treinamento usado para avaliar um período anterior. O ponto de corte será escolhido somente após medir a distribuição das datas; não será definido arbitrariamente nesta conversa.

#### Evidência inspecionada antes da próxima pergunta

O arquivo real possui 8.800 oportunidades: 500 `Prospecting`, 1.589 `Engaging`, 4.238 `Won` e 2.473 `Lost`. Todos os `Prospecting` não têm `engage_date`; todos os `Engaging` têm `engage_date`, mas ainda não têm `close_date`. Os deals encerrados têm ambas as datas. O ZIP consultado tem SHA-256 `74d535826330b616758ebb6bb393abf701a5126364a72fbe71003cb6a7a87a9c`.

#### Pergunta 3

Como devemos estimar a probabilidade dos `Prospecting`, já que o histórico encerrado contém apenas deals que chegaram ao engajamento?

#### Resposta de Luis

**B:** usar uma heurística baseada em produto, vendedor e conta, com o objetivo de eliminar viés.

#### Decisão registrada

`Prospecting` não usará diretamente o modelo probabilístico dos deals que já chegaram a `Engaging`. Terá uma heurística própria baseada apenas em atributos disponíveis nesse estágio. Essa separação reduz o viés de seleção, mas não autoriza afirmar que o eliminou: sem resultados históricos de oportunidades que não chegaram ao engajamento, a heurística não pode ser tratada como probabilidade calibrada.

#### Pergunta 4

Como a ferramenta deve apresentar o resultado dessa heurística de `Prospecting` sem prometer uma probabilidade que os dados não sustentam?

#### Resposta de Luis

**D:** mostrar faixa de prioridade e receita potencial, separadas da receita esperada dos `Engaging`.

#### Decisão registrada

Deals em `Prospecting` terão classificação de prioridade e preço potencial do produto. Deals em `Engaging` poderão exibir probabilidade calibrada e receita esperada. A interface deverá distinguir visualmente potencial de expectativa para evitar comparação enganosa entre métricas de naturezas diferentes.

#### Pergunta 5

Quais informações devem ser proibidas como features do modelo de `Engaging` para impedir leakage?

#### Resposta inicial de Luis

**D:** permitir campos finais durante o treinamento e removê-los apenas no uso.

#### Contestação da IA

A opção D produz leakage e diferença entre treino e uso. O modelo aprenderia atalhos a partir de `close_value`, `close_date` ou estágio final — informações que não existem quando um deal ativo recebe score. A validação pareceria melhor do que o desempenho possível em produção, contrariando o risco central explícito do challenge.

#### Recomendação corretiva — aprovada por Luis

Adotar **C**: proibir `close_value`, `close_date`, estágio final e derivados como preditores. `Won/Lost` pode ser usado somente como rótulo; `close_date`, somente para corte temporal e avaliação; `close_value`, somente para medir resultado financeiro histórico.

#### Decisão final

Luis substituiu a resposta inicial pela opção **C**. O contrato contra leakage passa a ser obrigatório no código, nos testes e na documentação do modelo.

#### Evidência de qualidade dos dados

Entre os deals ativos, 337 de 500 `Prospecting` e 1.088 de 1.589 `Engaging` não têm conta: 1.425 de 2.089, ou 68,2%. Em contraste, todos os 6.711 deals encerrados têm conta. Usar atributos da conta sem fallback criaria forte diferença entre treino e uso. Também existe `GTXPro` no pipeline, enquanto o catálogo registra `GTX Pro`; essa chave precisa de normalização explícita e testada.

#### Pergunta 6

Como devemos tratar os deals ativos sem conta associada?

#### Resposta de Luis

**C:** usar modelo completo quando houver conta e modelo fallback sem atributos de conta quando não houver.

#### Decisão registrada

O roteamento será determinado pela disponibilidade da conta. O fallback será treinado deliberadamente sem atributos de conta, não com valores médios inventados. Os dois caminhos precisarão de validação temporal própria e a interface deverá informar qual deles produziu o score.

### Síntese da Onda 3 — aprovada

- **Universo operacional:** somente `Prospecting` e `Engaging`; encerrados servem para aprendizado e validação temporal.
- **Prospecting:** heurística própria; exibe prioridade e receita potencial, não probabilidade calibrada.
- **Engaging:** probabilidade e receita esperada, com divisão temporal entre treino e validação.
- **Antileakage:** campos finais e derivados proibidos como preditores; `Won/Lost` é somente rótulo.
- **Dados incompletos:** modelo completo com conta e fallback sem conta; normalização explícita de `GTXPro` para `GTX Pro`.

Permanecem abertos: features exatas, algoritmo, calibração da probabilidade, desempenho mínimo aceitável e tratamento de categorias novas.

#### Aprovação de Luis

**Resposta:** “Aprovo.”

**Gate concluído:** a Onda 3 está aprovada integralmente e passa a orientar a arquitetura e a futura SPEC.

### Onda 4 — Score e explicação

#### Pergunta 1

Qual componente deve comandar a prioridade dos deals em `Engaging`?

- **A.** Apenas receita esperada (`probabilidade × preço`).
- **B.** Apenas probabilidade de fechamento.
- **C.** Apenas urgência ou risco de esfriamento.
- **D.** Receita esperada como base, com urgência ou risco como modificador explícito; a próxima ação permanece separada.

**Recomendação da IA:** **D**. Preserva a métrica norteadora já aprovada sem deixar oportunidades valiosas e urgentes perderem prioridade. Os pesos não serão inventados agora: deverão ser simples, visíveis e validados com o histórico disponível.

#### Resposta de Luis

**Preferência:** **B > A >>> C** — probabilidade de fechamento acima da receita esperada, ambas muito acima de urgência ou risco de esfriamento. A opção D não foi incluída.

#### Interpretação provisória

A probabilidade deve comandar a prioridade. Ainda é necessário definir se a receita esperada será apenas informativa ou se funcionará como segundo critério, pois a decisão anterior adotou receita esperada por vendedor como métrica norteadora.

#### Pergunta 2

Na fila ordenada por probabilidade, qual deve ser o papel da receita esperada?

- **A.** Apenas exibição; nunca altera a ordem.
- **B.** Segundo critério: desempata probabilidades equivalentes ou muito próximas.
- **C.** Controle alternável: o usuário escolhe ordenar por probabilidade ou receita esperada.

**Recomendação da IA:** **B**. Respeita `B > A`, mantém uma única fila objetiva e ainda conecta a ordenação à métrica financeira aprovada.

#### Resposta de Luis

**B:** a receita esperada será o segundo critério para oportunidades com probabilidades equivalentes ou próximas.

#### Decisão registrada

A fila de `Engaging` será ordenada primeiro pela probabilidade de fechamento. A receita esperada será usada como desempate controlado, sem substituir o critério principal. O significado mensurável de “probabilidades próximas” ainda deverá ser definido e validado, sem tolerância arbitrária.

#### Pergunta 3

Como cada probabilidade de fechamento deve ser explicada ao vendedor?

- **A.** Mostrar os principais fatores favoráveis e desfavoráveis, com o valor observado e seu efeito em linguagem simples.
- **B.** Mostrar somente fatores favoráveis para tornar a orientação mais positiva.
- **C.** Gerar uma justificativa narrativa livre por IA.
- **D.** Exibir somente os coeficientes e detalhes técnicos completos do modelo.

**Recomendação da IA:** **A**. É fiel ao cálculo, acionável e auditável; evita esconder sinais negativos ou inventar causalidade em uma narrativa livre.

#### Resposta de Luis

**A:** mostrar os principais fatores favoráveis e desfavoráveis, com o valor observado e seu efeito em linguagem simples.

#### Decisão registrada

A explicação será derivada do cálculo real do score, não gerada livremente. Ela deverá mostrar evidências dos dois sentidos e evitar linguagem causal quando os dados sustentarem apenas associação.

#### Pergunta 4

Qual estratégia deve decidir o modelo probabilístico de `Engaging`?

- **A.** Regressão logística como escolha fixa: máxima transparência e menor complexidade.
- **B.** Árvore de decisão rasa: regras visuais, mas divisões potencialmente instáveis.
- **C.** Gradient boosting com explicações SHAP: maior capacidade não linear, porém mais complexidade.
- **D.** Comparar regressão logística e gradient boosting na validação temporal; usar o modelo complexo somente se entregar ganho relevante, probabilidade bem calibrada e explicações fiéis.

**Recomendação da IA:** **D**, com a regressão logística como padrão em caso de desempenho equivalente. Isso mede se a complexidade se paga antes de adotá-la.

#### Resposta de Luis

**D:** comparar regressão logística e gradient boosting na validação temporal; adotar o modelo complexo somente com ganho comprovado.

#### Decisão registrada

A regressão logística será o baseline obrigatório. O gradient boosting será apenas um concorrente. Complexidade, SHAP e dependências adicionais só entram se o concorrente superar o baseline nos critérios aprovados, mantiver calibração adequada e produzir explicações fiéis. Em desempenho equivalente, vence o modelo simples.

#### Pergunta 5

Qual critério deve selecionar o vencedor entre os modelos?

- **A.** Melhor separação entre `Won` e `Lost`, independentemente da calibração.
- **B.** Menor erro das probabilidades, independentemente da qualidade da ordenação.
- **C.** Maior resultado financeiro no topo da fila histórica, mesmo com probabilidades mal calibradas.
- **D.** Gate em duas etapas: primeiro exigir probabilidades calibradas; depois comparar a qualidade da ordenação e o resultado financeiro no topo da fila. Sem ganho relevante, vence o modelo simples.

**Recomendação da IA:** **D**. A fila precisa ordenar bem, mas o número exibido como probabilidade também precisa ser confiável.

#### Resposta de Luis

**D:** aplicar um gate de calibração e, entre os modelos aprovados, comparar ordenação e resultado financeiro; sem ganho relevante, vence o modelo simples.

#### Decisão registrada

Nenhum modelo poderá vencer apenas por discriminar bem se suas probabilidades forem pouco confiáveis. Após o gate de calibração, a seleção considerará a capacidade de priorizar `Won` e concentrar resultado financeiro no topo da fila. A magnitude mínima de ganho relevante será definida a partir da variabilidade observada na validação, não por um número arbitrário.

#### Pergunta 6

Quando duas probabilidades devem ser consideradas “próximas” para permitir o desempate por receita esperada?

- **A.** Quando forem iguais após arredondamento para percentual inteiro.
- **B.** Quando estiverem a até 5 pontos percentuais, como regra fixa.
- **C.** Quando pertencerem à mesma faixa de probabilidade cuja confiabilidade foi confirmada na validação temporal.
- **D.** Nunca; receita esperada só desempata probabilidades exatamente iguais.

**Recomendação da IA:** **C**. Evita precisão falsa e deriva o desempate da resolução que os dados realmente sustentam.

#### Resposta de Luis

**C:** probabilidades serão consideradas próximas quando pertencerem à mesma faixa cuja confiabilidade foi confirmada na validação temporal.

#### Decisão registrada

A interface não tratará diferenças menores do que a resolução sustentada pelos dados como precisão real. Dentro da mesma faixa validada, a receita esperada poderá desempatar; entre faixas distintas, prevalecerá a probabilidade. As faixas deverão ser derivadas e reportadas pela validação.

#### Pergunta 7

Como transformar produto, vendedor e conta em uma prioridade explicável para `Prospecting`, sem chamar o resultado de probabilidade?

- **A.** Usar taxas históricas brutas de sucesso para cada combinação.
- **B.** Usar evidências históricas suavizadas: combinações com poucos casos recuam progressivamente para grupos mais gerais, e a interface informa a força da evidência.
- **C.** Definir pesos manuais fixos para produto, vendedor e conta.
- **D.** Reutilizar o modelo de `Engaging`, mas ocultar a probabilidade.

**Recomendação da IA:** **B**. Evita que grupos pequenos pareçam conclusivos, mantém o cálculo auditável e lida com categorias raras ou novas sem inventar certeza.

#### Resposta de Luis

**B:** usar evidências históricas suavizadas, com recuo progressivo para grupos mais gerais e indicação da força da evidência.

#### Decisão registrada

A prioridade de `Prospecting` não usará taxas brutas de grupos pequenos nem pesos arbitrários. O cálculo deverá reduzir o efeito de amostras escassas, recorrer a evidências mais gerais quando necessário e declarar a sustentação disponível. O resultado continuará sendo faixa de prioridade, não probabilidade calibrada.

### Síntese da Onda 4 — aprovada

- **Ordem de `Engaging`:** probabilidade primeiro; receita esperada desempata somente dentro da mesma faixa validada.
- **Explicação:** fatores favoráveis e desfavoráveis derivados do cálculo real, com evidência observada, efeito simples e sem alegação causal indevida.
- **Modelos:** regressão logística como baseline e gradient boosting como concorrente; complexidade só entra com ganho relevante e explicação fiel.
- **Seleção:** calibração é gate; depois são avaliadas ordenação e concentração de resultado financeiro; empate favorece simplicidade.
- **`Prospecting`:** prioridade por evidências históricas suavizadas, com recuo para grupos gerais e força da evidência visível; nunca apresentada como probabilidade.

Permanecem para as ondas seguintes: interação e estados da interface, tratamento operacional de dados fora do domínio, arquitetura executável e critérios finais de prova.

#### Aprovação de Luis

**Resposta:** “Aprovo.”

**Gate concluído:** a Onda 4 está aprovada integralmente e passa a orientar a arquitetura e a futura SPEC.

### Onda 5 — Experiência e operação

#### Pergunta 1

Como a experiência deve permanecer unificada sem misturar a probabilidade calibrada de `Engaging` com a faixa heurística de `Prospecting`?

- **A.** Uma única lista intercalada, ordenando os dois tipos por um score comum.
- **B.** Uma única tela com duas filas ou abas: `Engaging` e `Prospecting`, cada uma com sua própria ordenação e linguagem.
- **C.** Uma única lista agrupada primeiro por estágio e depois pelo score de cada estágio.
- **D.** Exibir apenas `Engaging` na fila principal e deixar `Prospecting` em uma tela secundária.

**Recomendação da IA:** **B**. Mantém um ponto operacional único sem fabricar equivalência entre probabilidade e heurística.

#### Resposta de Luis

**B:** uma única tela com duas filas ou abas, uma para `Engaging` e outra para `Prospecting`.

#### Decisão registrada

A ferramenta terá uma entrada operacional única, mas preservará dois contextos de decisão. Cada aba terá ordenação, rótulos e explicações compatíveis com a evidência disponível naquele estágio. Não existirá score comum para intercalar as duas filas.

#### Pergunta 2

Qual escopo deve abrir por padrão para cada perfil?

- **A.** Vendedor e gestor sempre veem toda a equipe.
- **B.** Vendedor abre apenas sua carteira; gestor abre a equipe e pode filtrar por vendedor.
- **C.** Ambos abrem apenas a própria carteira.
- **D.** A tela sempre restaura o último filtro usado, independentemente do perfil.

**Recomendação da IA:** **B**. Reduz ruído para o vendedor e entrega visão de gestão sem criar duas experiências separadas.

#### Resposta de Luis

**B:** vendedor abre apenas sua carteira; gestor abre a equipe e pode filtrar por vendedor.

#### Decisão registrada

O escopo inicial será orientado ao papel. A visão do vendedor reduz a carga à carteira sob sua responsabilidade. A visão do gestor oferece panorama da equipe e recorte por vendedor, preservando a mesma estrutura de filas e métricas.

#### Pergunta 3

Como equilibrar leitura rápida e explicação detalhada em cada fila?

- **A.** Exibir todos os fatores e dados diretamente em cada linha.
- **B.** Usar linha compacta com prioridade, valor e principal motivo; ao selecionar, abrir painel lateral com explicação completa e próxima ação.
- **C.** Mostrar somente cartões grandes, um deal por bloco.
- **D.** Exibir uma tabela de dados brutos e deixar a interpretação para o usuário.

**Recomendação da IA:** **B**. Permite percorrer a fila rapidamente e mantém a justificativa acessível sem poluir a comparação.

#### Resposta de Luis

**B:** linha compacta com prioridade, valor e principal motivo; painel lateral com explicação completa e próxima ação.

#### Decisão registrada

A fila otimizará varredura visual. A linha exibirá apenas os elementos necessários à comparação; o painel lateral preservará contexto, fatores favoráveis e desfavoráveis, origem do score, força da evidência e próxima ação. A abertura do detalhe não mudará de página.

#### Pergunta 4

Como a ferramenta deve produzir a próxima ação recomendada?

- **A.** Texto livre gerado por IA para cada deal.
- **B.** Playbook determinístico: regras explícitas combinam estágio e principal fator acionável, mostrando por que a ação foi sugerida.
- **C.** Campo preenchido manualmente pelo gestor.
- **D.** Não recomendar ação; mostrar apenas o score.

**Recomendação da IA:** **B**. É auditável, funciona sem API paga e evita recomendações inventadas; o playbook mínimo pode ser validado por testes diretos.

#### Resposta de Luis

**B:** usar um playbook determinístico baseado no estágio e no principal fator acionável.

#### Decisão registrada

A recomendação será produzida por regras versionadas e testáveis, sem chamada a modelo generativo. Cada ação deverá apontar o sinal que a ativou. Na ausência de sinal acionável suficiente, a interface declarará isso em vez de inventar uma recomendação.

#### Pergunta 5

Como o gestor deve fazer a repriorização manual temporária já aprovada?

- **A.** Arrastar qualquer deal para uma posição arbitrária na fila.
- **B.** Usar uma ação “Priorizar temporariamente”, que fixa o deal no topo, identifica a intervenção e expira na próxima recalculação.
- **C.** Digitar manualmente um número de posição.
- **D.** Alterar diretamente a probabilidade calculada.

**Recomendação da IA:** **B**. Entrega a intervenção necessária com uma regra simples, auditável e sem confundir decisão humana com previsão do modelo.

#### Resposta de Luis

**B:** usar a ação “Priorizar temporariamente”, fixando o deal no topo até a próxima recalculação.

#### Decisão registrada

A intervenção manual não mudará probabilidade, faixa ou receita esperada. O deal será destacado e fixado no topo da respectiva fila, com autor e horário visíveis. Ao recarregar ou recalcular o conjunto de dados, a intervenção expira e a ordenação calculada volta a valer.

#### Pergunta 6

Como tratar um deal ativo cujos dados não permitem score confiável, por exemplo uma categoria realmente desconhecida e sem fallback validado?

- **A.** Aplicar silenciosamente o valor médio e manter um score numérico.
- **B.** Manter o deal na fila com estado “Dados insuficientes”, sem score enganoso, e indicar quais campos precisam de correção.
- **C.** Remover o deal da interface.
- **D.** Colocá-lo automaticamente no fim, sem explicar o motivo.

**Recomendação da IA:** **B**. Nenhuma oportunidade desaparece, e a interface transforma incerteza em uma ação concreta de qualidade de dados.

#### Resposta de Luis

**B:** manter o deal na fila com estado “Dados insuficientes”, sem score, indicando os campos que precisam de correção.

#### Decisão registrada

Deals sem suporte de dados permanecerão visíveis, mas não receberão número ou faixa que sugira confiança inexistente. A interface explicará o bloqueio e os dados a corrigir. O fallback sem conta continua válido quando aplicável; “Dados insuficientes” cobre somente casos fora dos caminhos validados.

### Síntese da Onda 5 — aprovada

- **Estrutura:** uma tela com filas separadas de `Engaging` e `Prospecting`, sem score comum entre estágios.
- **Papéis:** vendedor abre sua carteira; gestor abre a equipe e pode filtrar por vendedor.
- **Leitura:** linhas compactas para comparação e painel lateral com explicação, origem, evidência e próxima ação.
- **Operação:** próxima ação vem de playbook determinístico; gestor pode fixar temporariamente um deal no topo sem alterar o score.
- **Incerteza:** dados fora dos caminhos validados permanecem visíveis como “Dados insuficientes”, com correção indicada e sem score enganoso.

Permanecem para a Onda 6: arquitetura mínima, fronteira do protótipo, persistência, execução, testes e prova final.

#### Aprovação de Luis

**Resposta:** “Aprovo.”

**Gate concluído:** a Onda 5 está aprovada integralmente e passa a orientar a arquitetura e a futura SPEC.

### Onda 6 — Arquitetura e prova

#### Evidência antes da arquitetura

O repositório não prescreve stack nem possui aplicação-base. O challenge exige software funcional, dados reais, scoring explicável e setup reproduzível dentro de um orçamento sugerido de 4–6 horas. Portanto, a arquitetura deve minimizar integração acidental e concentrar esforço na qualidade do produto e da prova.

#### Pergunta 1

Qual arquitetura deve sustentar o protótipo funcional?

- **A.** Aplicação Python em Streamlit, com preparação de dados, scoring e interface no mesmo projeto.
- **B.** Frontend React e API Python separados.
- **C.** HTML/JavaScript estático consumindo scores pré-calculados.
- **D.** CLI Python que gera relatório priorizado.

**Recomendação da IA:** **A**. Entrega interface interativa, filtros, modelo e explicações com o menor número de partes, sem sacrificar nenhum requisito obrigatório.

#### Resposta de Luis

**A:** aplicação Python em Streamlit, com preparação de dados, scoring e interface no mesmo projeto.

#### Decisão registrada

O protótipo será uma aplicação Streamlit autocontida dentro da pasta da submissão. A separação interna será apenas a necessária para manter ingestão, scoring, interface e testes compreensíveis; não haverá frontend e API independentes.

#### Evidência das regras de submissão

O guia exige código-fonte, setup reproduzível e todos os arquivos da entrega dentro de `submissions/luis-roquette/`. Não há proibição de versionar o dataset CC0 dentro dessa pasta.

#### Pergunta 2

Como garantir que o avaliador rode a solução com os dados reais sem depender de credenciais externas?

- **A.** Versionar uma cópia dos quatro CSVs na solução, acompanhada de fonte, licença e checksums.
- **B.** Baixar os dados pela API do Kaggle durante o setup, exigindo credenciais do avaliador.
- **C.** Baixar automaticamente de uma URL externa não controlada na primeira execução.
- **D.** Pedir que o avaliador obtenha e copie os arquivos manualmente.

**Recomendação da IA:** **A**. O conjunto é pequeno, CC0 e fica reproduzível mesmo se Kaggle ou credenciais estiverem indisponíveis.

#### Resposta inicial e correção de Luis

Luis respondeu primeiro **“A com fallback em B”** e, em seguida, corrigiu para **“A com fallback em C”**. A segunda resposta substitui a primeira.

#### Decisão final

Os quatro CSVs reais serão versionados como fonte primária, com origem, licença e checksums. Um comando explícito de recuperação poderá baixar uma cópia de uma URL pública; ele não rodará silenciosamente na abertura do app e só substituirá arquivos após validar os checksums esperados. Falha de rede ou conteúdo divergente deverá preservar os dados existentes e encerrar com erro claro.

#### Pergunta 3

Quando o treinamento e a validação dos modelos devem acontecer no protótipo?

- **A.** Na primeira abertura do app, de forma determinística, com resultado armazenado em cache durante a execução.
- **B.** Antes da entrega; o app carrega um artefato pronto e um comando separado permite reproduzir o treino.
- **C.** Nunca no projeto; somente scores finais pré-calculados são versionados.
- **D.** A cada filtro ou interação da interface.

**Recomendação da IA:** **A**. Com cerca de 6,7 mil deals encerrados, o treino local é pequeno; executá-lo uma vez e manter em cache prova o pipeline completo sem artefato binário frágil.

#### Resposta de Luis

**A:** treinar e validar na primeira abertura, de forma determinística, mantendo o resultado em cache durante a execução.

#### Decisão registrada

O app executará o pipeline real uma vez por versão dos dados e da configuração, com seed fixa e cache por fingerprint. Filtros e navegação reutilizarão o resultado. Uma mudança nos dados ou na configuração invalidará o cache e provocará nova avaliação antes de publicar scores.

#### Pergunta 4

Onde a intervenção temporária do gestor deve persistir no protótipo?

- **A.** Apenas na sessão do navegador; um refresh apaga a intervenção.
- **B.** Em SQLite local, com autor, horário e fingerprint dos dados; uma nova versão dos dados invalida a intervenção.
- **C.** Alterando diretamente os CSVs originais.
- **D.** Em banco externo com autenticação completa.

#### Questionamento de Luis

“Como o README do projeto/desafio manda? Você é quem precisa averiguar e dizer.”

#### Verificação e correção da IA

O README não exige persistência, banco, autenticação nem auditoria durável. Ele exige solução funcional, dados reais, scoring explicável, setup, lógica e limitações; também orienta começar simples dentro de 4–6 horas. SQLite seria uma expansão criada pela IA, não uma exigência do desafio.

**Recomendação corrigida da IA:** **A**. Manter a intervenção em `session_state`, exibindo gestor e horário durante a sessão, satisfaz o comportamento temporário já aprovado. A ausência de persistência multiusuário será declarada como limitação e caminho de escala.

#### Resposta de Luis

**A:** persistência apenas na sessão do navegador.

#### Decisão registrada

A repriorização temporária usará `st.session_state`, com gestor selecionado e horário visíveis durante a sessão. Ela não será apresentada como auditoria persistente nem autenticação real. Refresh, nova sessão ou recalculação poderão removê-la; esse limite será documentado.

#### Pergunta 5

Qual conjunto de provas deve acompanhar a entrega funcional?

- **A.** Testes automatizados dos contratos críticos, smoke test de inicialização e evidência visual do fluxo principal executado com os dados reais.
- **B.** Apenas inspeção manual da interface.
- **C.** Apenas métricas do modelo em um relatório.
- **D.** Uma suíte extensa de testes ponta a ponta para todos os controles.

**Recomendação da IA:** **A**. Prova scoring, antileakage, fallbacks e execução sem transformar o challenge em um projeto de infraestrutura de testes.

#### Resposta de Luis

**A:** testes automatizados dos contratos críticos, smoke test e evidência visual do fluxo principal com os dados reais.

#### Decisão registrada

A entrega deverá provar, no mínimo, ingestão e joins, bloqueio de leakage, separação temporal, roteamento completo/fallback, ordenação, explicações e playbook. Também deverá iniciar o Streamlit em smoke test e registrar uma evidência visual do fluxo vendedor/gestor. Métricas isoladas não serão aceitas como prova de produto.

#### Pergunta 6

Qual contrato de ambiente deve ser oferecido ao avaliador?

- **A.** Python 3.11, ambiente virtual e `requirements.txt` com versões fixadas, além de comandos curtos para instalar, testar e executar.
- **B.** Docker como única forma de execução.
- **C.** `uv` obrigatório com lockfile.
- **D.** Conda obrigatório com arquivo de ambiente.

**Recomendação da IA:** **A**. Usa ferramentas amplamente disponíveis e reduz pré-requisitos; Docker ou outro gerenciador não resolve requisito adicional do brief.

#### Pergunta de Luis

“O que manda o desafio?”

#### Resposta verificada

O challenge declara que a tecnologia não importa, desde que a solução rode, use dados reais, aplique scoring e explique o resultado. Na documentação, exige setup com dependências e comandos. Não impõe Docker, `uv`, Conda nem uma versão de Python.

#### Decisão técnica

Adotar **A**: Python 3.11, `venv`, `requirements.txt` com versões fixadas e comandos curtos de instalação, teste e execução. É a opção com menos pré-requisitos que atende integralmente ao brief.

#### Pergunta 7

Qual deve ser o alcance de disponibilização da aplicação?

- **A.** Execução local reproduzível como única entrega.
- **B.** Execução local obrigatória e, após todos os gates, demo pública em Streamlit Community Cloud como conveniência adicional.
- **C.** Apenas demo pública, sem garantir execução local.
- **D.** Deploy obrigatório em infraestrutura própria com Docker.

**Recomendação da IA:** **B**. A prova local continua independente de terceiros, enquanto a demo pública reduz o atrito para o avaliador; publicação só ocorrerá após validação e autorização explícita.

#### Pergunta de esclarecimento de Luis

“O que é Streamlit Cloud?”

#### Explicação registrada

Streamlit Community Cloud é o serviço de hospedagem da Streamlit: conecta-se a um repositório GitHub, instala as dependências e executa o arquivo principal do app, gerando uma URL que o avaliador pode abrir sem instalar nada. Ele facilita a demonstração, mas não substitui o setup local: depende de um serviço externo, pode ter inicialização fria e limites de recursos. Como o projeto não usa segredos nem APIs pagas, é compatível com esse tipo de publicação.

#### Resposta de Luis

**B:** execução local obrigatória e demo pública adicional, por apresentar o melhor custo-benefício.

#### Decisão registrada

A entrega será plenamente executável sem a nuvem. Depois de código, testes, smoke test e inspeção visual aprovados, poderá ser publicada no Streamlit Community Cloud para fornecer acesso imediato por URL. O deploy não será usado para esconder falha no setup local.

#### Pergunta 8

O que a aplicação deve fazer se nenhum modelo de `Engaging` passar pelo gate de calibração?

- **A.** Publicar a probabilidade do modelo menos ruim mesmo assim.
- **B.** Remover a probabilidade e usar apenas uma faixa de prioridade relativa, acompanhada de aviso e métricas da falha.
- **C.** Impedir a abertura de toda a aplicação.
- **D.** Usar as métricas do conjunto de treino até o modelo parecer aceitável.

**Recomendação da IA:** **B**. Mantém a ferramenta útil sem apresentar como probabilidade um número que a validação rejeitou.

#### Resposta de Luis

**B:** remover a probabilidade e exibir apenas prioridade relativa, com aviso e métricas da falha.

#### Decisão registrada

Probabilidade só será publicada se sustentada pela validação temporal. Caso todos os candidatos falhem no gate, `Engaging` continuará operacional com faixas relativas claramente rotuladas, sem receita esperada probabilística, e a falha será documentada.

#### Diretriz de condução registrada

Luis determinou: “Você deve trazer questões relevantes para o entendimento do produto e de suas nuances. Tem autonomia, dentro do que o desafio exige, para decidir e avançar. Evite trazer decisões irrelevantes.”

Daqui em diante, perguntas ao usuário ficam restritas a escolhas que alterem produto, risco ou aderência ao challenge. Decisões técnicas proporcionais serão tomadas autonomamente e registradas com sua justificativa.

### Síntese da Onda 6 — aprovada

- **Arquitetura:** aplicação Python 3.11 + Streamlit, autocontida e sem API separada.
- **Dados e modelo:** CSVs reais versionados, recuperação externa validada por checksum e treino temporal determinístico com cache.
- **Estado e falhas:** intervenção manual apenas na sessão; nenhuma probabilidade é exibida se a calibração falhar.
- **Prova:** testes dos contratos críticos, smoke test e evidência visual executada com os dados reais.
- **Entrega:** setup local obrigatório e demo pública adicional no Streamlit Community Cloud após todos os gates.

Com esta síntese, as seis ondas adaptativas mínimas foram concluídas. O próximo estágio, após aprovação, é consolidar o design em seções curtas e validá-lo antes de transformar o draft na SPEC.

#### Aprovação de Luis

**Resposta:** “Aprovo a Onda 6.”

**Gate concluído:** as seis ondas adaptativas estão aprovadas. A descoberta socrática termina e começa a consolidação incremental do design.

#### Verificação do fluxo SDD

O plugin `sdd@context-engineering-kit` 3.6.0 permanece instalado e habilitado no Claude Code. Seu fluxo oficial é `draft → /plan-task → todo → /implement-task`; o componente `brainstorm` exige design em seções de 200–300 palavras com validação incremental. No Codex, os componentes equivalentes estão disponíveis como skills separadas. O draft existente só será preenchido após aprovação do design consolidado.

## Design consolidado

### Seção 1 — Produto e experiência operacional — aprovada

O produto será uma aplicação Streamlit para a rotina de priorização comercial. Ao abrir, o usuário escolhe o perfil demonstrado. O vendedor entra diretamente em sua carteira; o gestor entra na visão da equipe e pode filtrar por vendedor. A experiência ocupa uma única tela, mas separa `Engaging` e `Prospecting` em abas porque os dois estágios não compartilham a mesma natureza de score.

Em `Engaging`, a fila é ordenada primeiro por faixa validada de probabilidade de fechamento. Dentro da mesma faixa, receita esperada — probabilidade multiplicada pelo preço do produto — desempata os deals. Em `Prospecting`, a fila usa prioridade relativa derivada de evidências históricas suavizadas e mostra receita potencial, sem rotular a heurística como probabilidade. Assim, o produto mantém utilidade sem fabricar comparabilidade estatística.

Cada linha será compacta: posição, oportunidade, conta quando disponível, vendedor, produto, prioridade, valor e principal motivo. A seleção abre um painel lateral com fatores favoráveis e desfavoráveis, origem do score, força da evidência e próxima ação produzida por playbook determinístico. Dados fora dos caminhos validados permanecem visíveis como “Dados insuficientes”, com o campo a corrigir.

O gestor poderá “Priorizar temporariamente” um deal. A ação fixa o item no topo, exibe gestor e horário, não altera o score e expira com a sessão ou recalculação. O protótipo não promete autenticação, gravação no CRM nem auditoria persistente; esses limites serão declarados explicitamente.

#### Aprovação de Luis

**Resposta:** “Aprovo a seção 1.”

### Seção 2 — Arquitetura e fluxo de dados — aprovada

A solução terá três unidades de código: `app.py` cuida somente da apresentação e do estado da sessão; `data.py` carrega, valida, normaliza e relaciona os quatro CSVs; `scoring.py` concentra preparação de features, treino, validação, priorização, explicações e playbook. Essa fronteira permite testar toda a lógica sem iniciar o Streamlit, sem criar camadas, interfaces ou serviços que o protótipo não necessita.

Na primeira execução, `data.py` confirma arquivos e colunas obrigatórias, calcula o fingerprint do conjunto e normaliza chaves conhecidas — inclusive `GTXPro` para `GTX Pro` — antes dos joins com produtos, contas e equipe. Linhas não serão descartadas silenciosamente: problemas de integridade produzirão erro global quando impedirem o pipeline ou estado “Dados insuficientes” quando afetarem apenas um deal.

`scoring.py` separa oportunidades encerradas das ativas. Somente `Won` e `Lost` alimentam treino e validação, ordenados por `close_date`: período antigo treina; período recente simula o futuro. `close_date`, `close_value`, estágio final e qualquer derivado ficam fora da matriz de features. O pipeline gera dois candidatos para `Engaging` — regressão logística e gradient boosting — e dois caminhos por candidato: completo, quando há conta, e fallback deliberadamente sem atributos de conta. Cada caminho recebe validação própria.

O vencedor e seus diagnósticos são armazenados em cache pelo fingerprint dos dados e da configuração. Depois, os deals ativos percorrem exatamente o mesmo pré-processamento aprendido no treino. O resultado entregue ao `app.py` já contém faixa, probabilidade quando aprovada, valores, motivos, força da evidência, próxima ação e motivo de eventual bloqueio. Assim, a interface apenas filtra, apresenta e aplica a prioridade temporária da sessão.

#### Aprovação de Luis

**Resposta:** “Aprovo a seção 2.”

### Seção 3 — Score, calibração e explicação — aprovada

Para `Engaging`, o histórico será dividido cronologicamente em treino, calibração e teste final. O treino ajusta os candidatos; a fatia intermediária calibra probabilidades e define faixas; o período mais recente permanece intocado até a comparação final. Um modelo só poderá publicar probabilidade se superar o baseline de taxa histórica em Brier score e log loss no teste e se suas faixas mantiverem relação coerente entre previsão e frequência observada. Entre candidatos aprovados, vencem ordenação e concentração de resultado financeiro no topo; sem ganho consistente, permanece a regressão logística.

As features serão limitadas ao que existe no momento da decisão: produto, série, preço e atributos cadastrais da conta no caminho completo. Datas finais, valor fechado e estágio final são proibidos. `sales_agent` não entra diretamente no modelo de `Engaging`: dentro da carteira ele não ajuda a ordenar e, na visão da equipe, poderia confundir habilidade histórica do vendedor com qualidade do deal. Vendedor, manager e região serão usados para filtros e diagnóstico de desempenho por segmento, não para alterar a probabilidade.

A explicação da regressão logística virá das contribuições dos próprios coeficientes; se o gradient boosting vencer, usará contribuição local compatível com árvores. O painel traduzirá os fatores de maior impacto favorável e desfavorável, mostrando valor observado e direção, nunca causalidade. Receita esperada será calculada somente quando a probabilidade passar no gate.

Para `Prospecting`, produto, vendedor e conta alimentarão taxas históricas suavizadas. Combinações escassas recuam para grupos mais gerais e, por fim, para a base global. O app mostrará faixa de prioridade, receita potencial, tamanho da amostra efetiva e nível de evidência. O playbook mapeará estágio e principal fator acionável para uma recomendação versionada; se nenhum fator sustentado existir, declarará “Sem ação recomendada com os dados atuais”.

#### Aprovação de Luis

**Resposta:** “Aprovo a seção 3.”

### Seção 4 — Falhas, testes e evidências — aprovada

O sistema distinguirá falhas globais de problemas por oportunidade. Arquivo ausente, schema incompatível, chave duplicada crítica ou conjunto histórico incapaz de produzir as divisões temporais interrompem a aplicação com mensagem que identifica arquivo, causa e correção. Conta ausente segue o fallback validado; produto sem correspondência, preço inválido ou categoria sem caminho seguro mantém o deal visível como “Dados insuficientes”. Nenhuma exceção será convertida silenciosamente em zero, média ou score padrão.

Se um candidato falhar durante treino, o outro ainda poderá ser avaliado. Se nenhum passar no gate de calibração, `Engaging` muda explicitamente para prioridade relativa, remove probabilidade e receita esperada e mostra o diagnóstico. O app só publica resultados depois que as quatro rotas — modelos completo e fallback para os dois candidatos — terminarem ou declararem falha controlada.

Os testes automatizados cobrirão os contratos que poderiam invalidar a decisão: schema e joins; normalização `GTXPro`; proibição de leakage; ordem cronológica das divisões; ausência deliberada de conta no fallback; roteamento de deals; estabilidade da ordenação; expiração da prioridade manual; cálculo de receita; explicações compatíveis com o score; playbook; e supressão da probabilidade quando o gate falhar. Fixtures sintéticas pequenas testarão bordas; ao menos um teste de integração percorrerá os quatro CSVs reais.

O preflight canônico executará testes, verificação de imports, treino completo e smoke test do Streamlit no Codespace gerenciado. Depois, o fluxo vendedor e gestor será inspecionado no navegador: troca de abas, filtros, painel lateral, estado de dados insuficientes e prioridade temporária. Screenshots e métricas finais serão registradas como evidência. Qualquer falha determinística bloqueia push, deploy e alegação de conclusão.

#### Aprovação de Luis

**Resposta:** “Aprovo a seção 4.”

### Seção 5 — Entrega, documentação e limites — aprovada

Toda a entrega permanecerá em `submissions/luis-roquette/`. A solução conterá código, testes, `requirements.txt` fixado, os quatro CSVs em `data/raw/`, manifesto com origem, licença e checksums, além de um comando explícito de recuperação que valida o conteúdo antes de substituir qualquer arquivo. O README da solução fornecerá comandos copiáveis para criar o ambiente Python 3.11, instalar dependências, executar o preflight e iniciar o Streamlit. O README principal da submissão seguirá o template oficial e conduzirá o avaliador ao app, às evidências e ao process log.

A documentação explicará o problema de negócio, a diferença entre as filas, features permitidas e proibidas, divisão temporal, critérios de calibração, seleção do modelo, heurística de `Prospecting`, explicações e playbook. Um quadro de resultados registrará contagens reais, modelos avaliados, métricas por rota, modelo escolhido e fallback acionado. Screenshots mostrarão os fluxos de vendedor e gestor. O histórico de commits e este diário preservarão perguntas, respostas, correções e decisões humanas relevantes.

A execução local será a fonte de verdade. Somente após o preflight verde e a inspeção visual, a mesma revisão versionada poderá ser publicada no Streamlit Community Cloud; a URL será adicionada à documentação após verificação ao vivo. Nenhum segredo ou API paga será necessário.

As limitações serão explícitas: o dataset é um recorte estático; não contém desfechos de leads que nunca chegaram a `Engaging`; associações não provam causalidade; prioridade manual não persiste; não há autenticação, escrita no CRM, monitoramento de drift nem retreino agendado. A evolução recomendada será um piloto com vendedores, captura de intervenções e resultados, auditoria de desempenho por segmento e recalibração periódica antes de qualquer uso operacional em escala.

#### Aprovação de Luis

**Resposta:** “Aprovado.”

**Gate concluído:** as cinco seções do design consolidado estão aprovadas. O draft SDD pode receber os requisitos e seguir para `/plan-task`; implementação permanece bloqueada até a SPEC planejada ser revisada.

## I07 — SPEC planejada pelo SDD — 2026-09-21

- **Método:** `/plan-task` completo, com pesquisa, análise de codebase, análise de negócio, síntese arquitetural, decomposição e judge independente após cada fase.
- **Configuração:** qualidade-alvo `3,5/5`, até três iterações, todas as fases ativas, judges habilitados e tier equivalente a Opus por integridade de dados e modelagem não trivial.
- **Resultados dos gates:** pesquisa `4,10/5`; codebase `3,75/5`; negócio `3,52/5`; arquitetura `4,00/5`; decomposição `3,85/5`. Todos `PASS`.
- **Plano produzido:** oito passos em três fases verificáveis, largura paralela máxima dois, 37 subtarefas, 50 critérios e cinco rubricas integralmente mapeados.
- **Estado SDD:** task promovida de `draft` para `todo`; nenhum código de produto foi implementado nesta etapa.
- **Correção operacional:** o script de pastas do plugin tentou criar scaffolding na raiz Git. Apenas os arquivos recém-criados pelo próprio fluxo foram removidos, e os artefatos válidos permaneceram dentro de `submissions/luis-roquette/`.

### Melhorias não bloqueantes registradas pelos judges

- Explicitar horizonte de previsão e viés de censura do histórico composto apenas por deals resolvidos.
- Manter campos e nulabilidade dos contratos concretos durante a implementação.
- Separar obrigações agrupadas quando isso melhorar a rastreabilidade dos testes.
- Garantir teste visual da supressão de probabilidades e smoke test em ambiente virtual limpo.
- Concentrar em `04-canonical-verification` os testes reais que dependem do scoring criado em `03a`; `03b` deve usar fixtures do contrato.

## I08 — Auditoria final de aderência ao desafio e à stack — 2026-09-21

**Decisão de Luis:** antes da implementação, reler o repositório do desafio, conferir a cobertura integral do avaliador, validar toda a stack e eliminar gargalos conhecidos.

### Fontes relidas

- `challenges/build-003-lead-scorer/README.md`: software funcional, dados reais, priorização além de valor, explicação compreensível, setup, lógica, limitações, process log e bônus de filtros.
- `submission-guide.md`: solução e process log obrigatórios; evidência de decomposição, iteração, correção de erros e contribuição humana; comunicação concisa.
- `templates/submission-template.md`: README compartilhado com resumo, solução, resultados, recomendações, limitações, workflow e evidências.
- `CONTRIBUTING.md`: PR obrigatório, título padronizado e nenhuma alteração fora de `submissions/luis-roquette/`.

### Gargalos encontrados e correções incorporadas à SPEC

1. **Recuperação do dataset:** a API pública sem versão respondeu `404`; o endpoint com `datasetVersionNumber=1` respondeu corretamente. A recuperação foi fixada na versão 1, mantendo checksum obrigatório e preservação dos arquivos existentes.
2. **Python no Codespace:** a imagem atual oferece Python 3.14.2 e não oferece Python 3.11. A SPEC agora exige bootstrap descartável com `uv`, instalação do CPython 3.11 e criação do ambiente com `uv venv --seed --python 3.11`.
3. **Compatibilidade de dependências:** a instalação conjunta de Streamlit, pandas, NumPy, SciPy, scikit-learn e Playwright em Python 3.11, além dos imports críticos, foi comprovada. A SPEC acrescentou `protobuf<6`, requisito de compatibilidade do Streamlit Community Cloud, e preservou `pip check` como gate. A combinação final com esse pin e Chromium ainda precisa do preflight estável da implementação.
4. **Paralelismo da interface:** `03b` passa a testar somente fixtures congeladas do contrato; a integração real com o scoring de `03a` pertence ao passo `04`, removendo dependência circular escondida.
5. **Deploy aninhado:** o plano agora explicita Python 3.11, raiz do repositório como diretório de trabalho e `app.py` aninhado como entrypoint no Streamlit Community Cloud.
6. **Bônus de filtros:** a primeira releitura pós-correção mostrou que região estava prevista apenas para diagnóstico. A SPEC passou a exigir e testar filtros exatos por manager, região e vendedor, sem alterar scores.
7. **Título e destino do PR:** a checagem de entrega mostrou que a referência genérica à política de PR era insuficiente. O plano passou a exigir um único PR para `upstream/main` com o título exato `[Submission] Luis Roquette — Challenge 003`.

### Matriz de cobertura do avaliador

| Exigência | Cobertura planejada | Gate final |
|---|---|---|
| Software funcional | Streamlit executável, smoke test e jornadas Playwright | `04` local/Codespace + `05` ao vivo |
| Dados reais | Quatro CSVs CC0 versionados, manifestados e testados em integração | `01`, `02a`, `04` |
| Priorização além de valor | Engaging validado temporalmente; Prospecting com evidência suavizada | `02b`, `03a`, `04` |
| Explicação do score | Fatores favoráveis/desfavoráveis, origem, força da evidência e ação | `03a`, `03b`, `04` |
| Uso por não técnico | Carteira do vendedor, visão do gestor, filtros e estados acionáveis | `03b`, `04`, `05` |
| Setup, lógica e limitações | README copiável, ledger medido e limites explícitos | `04`, `06` |
| Process log | Perguntas, respostas, decisões, erros e correções preservados | este diário + `06` |
| Forma de submissão | README do template, escopo exclusivo e PR padronizado | `05`, `06` |

### Controle de escopo

A SPEC interna é deliberadamente completa para impedir lacunas, mas o material entregue ao avaliador permanecerá curto e operacional. O caminho crítico prioriza o que é obrigatório; filtros de gestor/região e deploy público permanecem diferenciais aprovados, sem criar API, autenticação, banco, escrita no CRM ou dependência paga.

**Estado após a auditoria:** cobertura de requisitos completa no plano; implementação, preflight, deploy renderizado e PR continuam sendo gates futuros e não foram declarados concluídos.

### Loop final de absorção

- **Passagem limpa 1/2:** requisitos funcionais, documentação obrigatória, bônus de filtros e limite de escopo foram remapeados após as correções; nenhum novo achado.
- **Passagem limpa 2/2:** oito passos, 50 critérios, 47 testes, stack, título/destino do PR e isolamento de arquivos foram verificados novamente; nenhum novo achado.
- **Goal de absorção:** atingido — duas passagens consecutivas sem novas descobertas.

### Gargalo operacional observado

Três tentativas de completar a prova remota da stack pelo `codespace-manager` foram recusadas porque o Codespace limpo do mesmo repositório alternou entre `Shutdown`, `Available` e `ShuttingDown`. A hipótese duvidosa é o ciclo de vida externo desse ambiente antigo. A validação não foi contornada: o preflight de implementação permanece obrigado a comprovar Python 3.11, instalação com `protobuf<6`, `pip check`, Chromium e abertura headless em um Codespace estável antes de push, deploy ou conclusão.

## I09 — Encerramento da construção socrática e método obrigatório de implementação — 2026-09-21

### Registro consolidado das ondas socráticas

As perguntas, alternativas, respostas de Luis, recomendações da IA e aprovações já estão preservadas integralmente neste diário, na ordem em que ocorreram. A construção foi conduzida por seis ondas adaptativas: cada onda posterior usou as respostas anteriores para aprofundar decisões relevantes e evitou transferir ambiguidades importantes para a IA.

1. **Onda 1 — objetivo e métrica:** definiu usuário, decisão operacional e receita esperada como métrica norteadora, calculada por probabilidade de fechamento × preço do produto.
2. **Onda 2 — experiência e priorização:** separou `Engaging` de `Prospecting`, definiu filas compreensíveis, detalhes acionáveis e intervenção temporária do gestor sem alterar o score.
3. **Onda 3 — verdade dos dados:** fixou divisão temporal, exclusão de leakage, uso de `Won/Lost` apenas como rótulo e tratamento explícito de dados insuficientes.
4. **Onda 4 — modelagem e explicação:** escolheu comparação controlada de candidatos, calibração obrigatória, fallback sem conta, explicações fiéis ao score e eliminação de viés de vendedor no modelo de `Engaging`.
5. **Onda 5 — produto e governança:** definiu filtros, contexto vendedor/gestor, estado de sessão, limitações, validação visual e evidências reproduzíveis.
6. **Onda 6 — entrega:** consolidou Python 3.11 + Streamlit, dados reais versionados com recuperação segura, execução local como fonte de verdade e Streamlit Community Cloud como demonstração adicional.

Após as ondas, cinco seções de design foram apresentadas e aprovadas individualmente: produto/experiência; arquitetura/dados; score/calibração/explicação; falhas/testes/evidências; entrega/documentação/limites. O planejamento SDD converteu essas decisões em oito etapas, três fases, 50 critérios e 47 contratos de teste. A auditoria final corrigiu os gargalos restantes e atingiu duas releituras consecutivas sem novos achados.

### Decisão de implementação em feedback looping

**Decisão de Luis:** seguir para a implementação respeitando obrigatoriamente a metodologia SDD, em fases cronológicas, uma após a outra.

Cada etapa seguirá a cascata:

`Planejamento → Revisão → Execução → Teste`

- O trabalho de cada etapa produz relatórios quase em tempo real para a própria IA.
- Os insights do relatório determinam autonomamente se a etapa precisa de reforço ou se pode avançar.
- Se o teste falhar, a mesma etapa retorna ao início do loop; a causa é corrigida e todos os gates aplicáveis são repetidos.
- Nenhuma etapa avança sem validação. Uma fase só termina depois da revisão SDD e dos testes verdes correspondentes.
- O `/goal` mantém o objetivo global; cascatas de `/loop` controlam a convergência de cada etapa sem inventar novos checkpoints humanos.

**Critério de saída:** somente avançar quando a etapa estiver implementada, revisada e validada; caso contrário, permanecer no feedback loop até corrigir ou identificar um impedimento externo concreto.

## I10 — Da intenção arquitetural à construção da fundação — 2026-09-21

Esta etapa registra a jornada construtiva proposta por Luis: documentar não apenas o resultado, mas como o arquiteto define a intenção, como o engenheiro a transforma em evidência executável e como cada correção melhora a solução. Essa autoria metodológica é parte central do trabalho. As decisões, descobertas, falhas e correções têm a mesma importância documental que o artefato final.

### Feedback looping aplicado ao passo 01

O ciclo obrigatório permaneceu:

`Planejamento → Revisão → Execução → Teste`

- **Planejamento — intenção do arquiteto:** criar um snapshot imutável e verificado dos dados reais, apoiado por uma fundação reproduzível em Python 3.11.
- **Revisão — contrato antes da construção:** conferir arquivos, contagens, origem, checksums, recuperação e o gate limpo de Codespace antes de aceitar a etapa.
- **Execução — construção do engenheiro:** incorporar os quatro CSVs reais, com 85 contas, 7 produtos, 35 equipes e 8.800 oportunidades; gerar manifesto e checksums; implementar os testes de integridade e reprodução.
- **Teste — evidência para o próximo ciclo:** executar o gate canônico em Codespace limpo, corrigir qualquer falha e repetir o ciclo completo antes de avançar.

### Iterações e correções registradas

1. A primeira rodada chegou a **12 de 13 testes aprovados**. A falha estava no carregamento de datas opcionais: o pandas representava a ausência como `NaN`, e o contrato esperava um valor opcional normalizado.
2. A causa foi corrigida na fronteira de dados com `pd.isna`, seguida de um teste de regressão específico. O conjunto passou a conter **14 testes**, todos aprovados: **14/14 PASS**.
3. A infraestrutura também entrou no loop. O transporte de um payload longo em Base64 falhou no PTY; a correção foi dividir o conteúdo em blocos de 1.000 caracteres e validar o resultado por SHA antes da execução.
4. Durante a passagem da arquitetura para a engenharia, descobriu-se que o ZIP oficial contém `metadata.csv`, além dos quatro CSVs exigidos. A recuperação passou a usar quatro URLs públicas, diretas e versionadas. O allowlist estrito do ZIP foi preservado nas fixtures para continuar rejeitando conteúdo inesperado.

### Estado factual do gate

- Os quatro downloads diretos foram comparados localmente e são byte a byte idênticos ao snapshot versionado.
- A revalidação remota do manifesto alterado **ainda não passou**: a competição pelo Codespace compartilhado e seu ciclo de vida encerraram a execução com `exit 73`.
- Portanto, o passo 01 ainda não pode ser declarado validado, apesar do resultado local e dos 14 testes aprovados. O loop permanece na própria etapa até o gate remoto terminar verde.
- Em paralelo, o passo `02b` está implementando a evidência temporal. Ele ainda não concluiu seu gate e não é tratado como etapa aprovada.

### Princípio preservado

O diário registra o desenho e a construção: intenção, hipótese, evidência, erro, causa, correção e novo teste. A metodologia criada por Luis transforma documentação em instrumento ativo de engenharia — os registros alimentam o próximo loop e impedem que uma decisão arquitetural se perca entre planejamento e implementação.

## I11 — Redundância Necessária e lapidação — 2026-09-22

### Redundância Necessária — método padrão de Luis

Padrão autoral aplicado depois do primeiro resultado integral da implementação. O `/goal` conduz revisões completas em cascatas de `/loop` até que pelo menos duas passagens consecutivas não encontrem erros, falhas, lacunas, melhorias relevantes nem otimizações.

- Cada achado zera o contador de passagens limpas.
- O achado é corrigido e retestado pelo ciclo `Planejamento → Revisão → Execução → Teste`.
- Todo o escopo relevante é então revisado novamente; ausência de achados exige evidência, nunca presunção.
- O objetivo é comprovar assimilação integral e implementação exaustiva, sem lacunas entre intenção e entrega.

**Estado atual:** o método global ainda não começou, pois a implementação está apenas na Fase 1 de 3. A Fase 1 obteve duas passagens técnicas limpas, mas seu relatório de revisão SDD permanece formalmente inválido após três tentativas: falta o campo literal `combined_score`, embora existam evidência numérica equivalente e **42/42 testes aprovados**.

### Revisão atual da Fase 1

A primeira revisão formal encontrou e levou à correção de quatro pontos: lacuna na inicialização da recuperação, mocks internos, funções grandes demais e teste top-K sem poder discriminatório. Os gates limpos de **42/42 testes** foram executados duas vezes. Entretanto, três emissões do relatório falharam na nomenclatura exata do schema; por isso, a Fase 1 ainda não está marcada como revisada.

### Lapidação e melhoria contínua — método padrão de Luis

Este método começa somente quando a implementação estiver completa e a Redundância Necessária alcançar duas passagens globais limpas. Um `/goal` com cascatas de `/loop` fará uma busca exaustiva por gargalos, erros, bugs, melhorias, otimizações, refinamentos técnicos e oportunidades em layout, design, UI/UX, código e segurança.

- Os achados serão listados e implementados pelo ciclo `Planejamento → Revisão → Execução → Teste`.
- Cada correção ou otimização reinicia a contagem e exige nova revisão do escopo relevante.
- A saída exige pelo menos duas passagens consecutivas sem correção ou otimização relevante.
- O objetivo é elevar um sistema já funcional ao próximo nível, sem confundir lapidação com implementação ainda incompleta.

**Estado atual:** 0 rodadas globais; método ainda não iniciado.

## Exceção formal aceita na Fase 1 — 2026-09-22

Luis autorizou explicitamente a aceitação do segundo relatório de revisão da Fase 1, semanticamente completo. As evidências registradas foram: conformidade com a SPEC `4,00`, avaliação interna `2,00`, resultado combinado `3,00`, duas passagens limpas consecutivas e **42/42 testes aprovados em ambas**.

A única exceção foi de serialização: o relatório emitiu `scores.combined` em vez da chave literal `combined_score`. Nenhum teste, achado ou gate técnico foi dispensado. Com essa autorização, a Fase 1 foi marcada como `[REVIEWED]` e a Fase 2 foi liberada.

## I12 — Jornada construtiva da Fase 2 — 2026-09-22

### Construção por etapas

- `4eccd2f`: interface do passo `03b` implementada; gate focal **8/8**.
- `9acf3ed`: scoring do passo `03a` implementado; gate focal **32/32** e validação relativa **2.089/2.089**.
- `e052e4e`: implementação do passo `04` validada no Codespace; o HEAD documental observado depois foi `c16a6d6`.
- Evidências do passo `04`: focal **2/2**, preflight **74/74**, `REAL_RENDERED_JOURNEY` e Python **3.11.15**.

### Feedback looping: RED → GREEN

- Quatro rotas foram rejeitadas honestamente pelos critérios definidos; nessas rotas, `probability` e `expected_revenue` permaneceram em zero.
- O cold start real foi medido em **72,851 s**; o timeout foi ajustado para **120 s**, com base nessa evidência.
- Widgets virtualizados e formulário foram substituídos por botões por linha, em páginas, para tornar a jornada renderizada determinística e testável.
- O estado dos filtros passou a ter resumo determinístico. Cada achado retornou ao ciclo `Planejamento → Revisão → Execução → Teste` até o gate verde.
- A contenção do semáforo compartilhado foi respeitada durante as execuções em Codespace; nenhuma validação concorrente foi tratada como prova da etapa.

### Estado e bloqueio da Fase 2

Dois checkboxes do subtask `04` permanecem desmarcados. A SPEC exige repetição pesada local no Mac, mas o `AGENTS.md` proíbe gates pesados no Mac sem autorização explícita de Luis. O conflito não foi contornado: a Fase 2 **não está concluída nem revisada**.

O `TC47` não foi reivindicado. Nenhum push foi realizado.

### Exceção autorizada para a repetição local — 2026-09-22

Luis autorizou explicitamente o bypass **apenas** da repetição pesada local no Mac, resolvendo o conflito entre a SPEC e a proibição do `AGENTS.md`. O preflight canônico do Codespace permanece obrigatório e verde, com **74/74 testes** e `REAL_RENDERED_JOURNEY`. A autorização não dispensa teste, CI, segurança nem gate remoto. A Fase 2 ainda não está marcada como revisada.

### Esclarecimento do owner sobre o preflight pós-fix — 2026-09-22

Após questionar a demora, Luis esclareceu que o bypass solicitado também abrangia o preflight integral ainda pendente depois do retrabalho da revisão. A decisão evita nova espera no semáforo compartilhado: o full pós-fix não será repetido.

A evidência válida do SHA `9228ffd` é o gate focal **6/6**. O último full **74/74** e `REAL_RENDERED_JOURNEY` pertencem ao SHA anterior; portanto, não se declara preflight full pós-fix verde. A Fase 2 permanece sem marcação de revisada até nova avaliação do revisor.

### Ciclos de revisão e retrabalho da Fase 2 — 2026-09-22

- **Revisão inicial:** nota `3,30`, com cinco achados.
- **Retrabalho 1:** gate RED com seis ocorrências — duas falhas e quatro erros — seguido de GREEN focal **6/6** no SHA `9228ffd`.
- **Reavaliação:** nota `3,90`, com duas issues residuais.
- **Retrabalho 2:** commits `2dbc3e5` para testes, `af046c4` para implementação e `3e94015` para documentação.

Por bypass explícito do owner e ausência de Codespace limpo, os quatro testes novos do segundo retrabalho foram escritos e revisados, mas **não executados**. Apenas `py_compile`, `bash -n` e `git diff --check` ficaram verdes. Não se declara GREEN nem full pós-fix, e o `TC47` não foi reivindicado. A Fase 2 aguarda a reavaliação estática final.

### Reavaliação estática final da Fase 2 — 2026-09-22

O mesmo revisor concluiu a reavaliação estática com conformidade à SPEC `4,45`, avaliação interna `4,35`, resultado combinado `4,40`, `issues: []` e `rework_required: false`. Os dois issues residuais foram considerados fechados por inspeção.

A limitação permanece explícita: as quatro regressões finais não foram executadas por bypass autorizado. Portanto, a Fase 2 pode ser marcada como `[REVIEWED]`, sem alegação de full pós-fix verde nem reivindicação do `TC47`.

## I13 — Passo 05: entrega pública até o bloqueio OAuth — 2026-09-22

- A branch foi enviada e o PR upstream [#140](https://github.com/luisroquette/ai-master-challenge/pull/140) está aberto, `mergeable` e sem checks registrados.
- O commit de evidências foi `f4cf4b1`. A correção de `source_identity` entrou em `14d0296`, seguida da documentação em `429c5e9`.
- Causa da falha: `Path(...).parent` subia um diretório além do necessário e fazia os hashes aparecerem como ausentes. A regressão focal direta passou com digest iniciado em `7e25ba0` e terminado em `d311`.
- Os gates leves ficaram verdes. `unittest` e preflight não foram executados, conforme o bypass autorizado e porque o Mac não dispõe de Streamlit.

Não havia app existente no Streamlit Community Cloud. O login foi iniciado e ficou bloqueado na tela de OAuth do GitHub, em `Authorize Streamlit Community Cloud`; o botão não foi clicado. Assim, o passo `05`, o `TC47`, o deploy, a URL pública e os screenshots continuam incompletos e não foram reivindicados.

## Embargo externo determinado pelo owner — 2026-09-22

Luis determinou que nada seja enviado aos avaliadores antes de validar o output final e conceder autorização mais que expressa.

- O PR upstream `#140`, aberto antes dessa ordem, foi fechado.
- A branch remota `origin/submission/luis-roquette-003-lead-scorer` foi apagada.
- A branch local e seus commits foram preservados.
- O formulário de criação da conta Streamlit não foi submetido; a aba foi fechada.
- Nenhum app, deploy, URL pública, `TC47` ou screenshot foi produzido.

**Regra operacional:** nenhuma nova publicação, push remoto, PR, merge, deploy ou comunicação aos avaliadores ocorrerá sem autorização expressa posterior de Luis.

## I14 — Preview local autorizado e correção de runtime — 2026-09-22

Luis autorizou explicitamente a instalação isolada das dependências e a abertura do sistema apenas no ambiente local, sem remover o embargo externo.

- O preview usa Python `3.11.15`, `uv 0.10.10` e 44 dependências fixadas em `/tmp/lead-scorer-preview.iSbpqF/venv`; `pip check` ficou verde.
- A primeira renderização real revelou `TypeError` em `app.py:35`: `json.dumps` não serializava o `MappingProxyType` retornado pela identidade imutável da fonte.
- A causa raiz foi corrigida em `bundle_cache_key` pela conversão explícita para `dict`, com regressão focal para `MappingProxyType`; commit local `c4b5781`, teste focal **1/1**, `py_compile` e `git diff --check` verdes.
- O aplicativo original, sem wrapper, foi reiniciado em `http://127.0.0.1:50398`, limitado a `127.0.0.1`. A interface renderizada mostrou os perfis, vendedor Anna Snelling, abas Engaging/Prospecting, tabela de prioridades, evidências e paginação de **25 de 57** oportunidades Engaging.
- A aba local foi preservada para validação de Luis. Nada foi enviado ao GitHub, Streamlit Cloud ou avaliadores; o passo `05`, o deploy público e o `TC47` permanecem incompletos.

## I15 — Rodada profunda de frontend, UI e UX — 2026-09-22

Luis determinou uma rodada profunda de melhoria do frontend, com foco principal em **UI e UX**, antes da validação final. A execução usará obrigatoriamente a skill `frontend-design`.

- A rodada partirá do sistema funcional já validado localmente e preservará integralmente regras de negócio, explicabilidade, rastreabilidade e acessibilidade.
- Antes de alterar código, será definida uma direção visual clara e coerente com o produto de priorização comercial, evitando estética genérica ou decorativa sem função.
- A lapidação cobrirá hierarquia da informação, tipografia, cores, densidade, espaçamento, estados, navegação, responsividade, microinterações e clareza das decisões apresentadas.
- Cada mudança seguirá `Planejamento → Revisão → Execução → Teste`; uma melhoria só permanecerá se produzir ganho observável sem degradar uso, desempenho ou compreensão.
- O resultado será novamente validado no preview local e documentado com decisões, antes/depois, evidências, correções e limitações. O embargo externo continua integralmente vigente.

## I16 — Execução da rodada profunda de frontend, UI e UX — 2026-09-22

### Direção e implementação

A skill `frontend-design` orientou uma direção de **mesa de decisão comercial editorial**: sóbria, densa e memorável, sem alterar regras de negócio. A interface recebeu hierarquia tipográfica, fundo atmosférico leve, paleta de papel/teal, cartões de contexto, filtros agrupados, indicadores executivos, tabelas formatadas, estados e botões coerentes, painel inicial instrutivo e detalhes com fatores em listas legíveis.

Foram preservados os contratos essenciais: tela única, abas Engaging/Prospecting independentes, dataframe nativo selecionável, painel adjacente, rótulos acessíveis, filtros de vendedor/gestor, rastreabilidade visível, ausência honesta de probabilidade em rotas rejeitadas e prioridade temporária exclusiva do gestor.

### Feedback looping e correções

- A primeira revisão visual encontrou a cor primária vermelha herdada do Streamlit, ambiguidade no indicador “Faixa alta” e fatores exibidos como listas Python.
- A correção aplicou o teal aos CTAs, renomeou o indicador para “Sinais altos” com aviso de escalas independentes e renderizou fatores em listas semânticas; índices e probabilidades passaram a ter formatação de leitura.
- O primeiro comando Playwright não executou testes: faltava o Chromium `v1243` no cache local. O navegador compatível foi instalado e o mesmo gate focal foi repetido sem skips.

### Evidências e redundância necessária

- `py_compile` e `git diff --check`: verdes.
- Streamlit AppTest: **4/4** em duas execuções.
- Contratos de portfólio e sessão: **14/14**.
- Jornadas Playwright: primeira tentativa com **0 testes** por dependência ambiental ausente; após a correção, **3/3** verdes.
- Passada limpa 1: inspeção renderizada de vendedor, gestor, Engaging, Prospecting, detalhe e estado vazio, sem novo achado relevante.
- Passada limpa 2: revisão de contratos, acessibilidade, estados e journeys automatizados, sem novo achado relevante.

O objetivo específico da rodada de UI/UX foi atingido com duas passadas consecutivas sem melhoria relevante. O preflight integral não foi executado nesta rodada e não é reivindicado. Nenhum push, PR, deploy, URL pública ou comunicação aos avaliadores ocorreu; o embargo externo permanece vigente.

### Correção posterior da verificação renderizada

Após o primeiro commit visual, a verificação local da identidade encontrou uma corrida em `tests/test_app.py`: o título já estava visível, mas a leitura do corpo ocorria antes da linha com revisão, fingerprint e fonte. A contagem anterior de passadas limpas foi invalidada e reiniciada.

- A causa raiz foi corrigida no verificador: ele agora aguarda a linha genérica completa de identidade antes de comparar os valores esperados, preservando a mensagem diagnóstica para divergências reais.
- Uma página que injeta a identidade depois do título foi adicionada como regressão; gate específico **1/1** verde.
- Passada limpa pós-correção 1: verificador renderizado local verde contra o commit `a77f47d`, sem reivindicar `TC47` público.
- Passada limpa pós-correção 2: **21/21** testes focais — 14 contratos, 4 AppTests e 3 journeys Playwright — mais `py_compile` e `git diff --check`, sem novo achado.

Com duas novas passadas consecutivas sem erro, gap ou melhoria relevante, a rodada profunda de UI/UX volta a atingir seu objetivo. O preflight integral e o `TC47` público continuam não executados.

## I17 — Feedback humano: da análise para o foco automático — 2026-09-22

Luis identificou uma lacuna de produto depois de usar a primeira versão lapidada: a interface estava mais clara, porém ainda exigia exploração e intervenção humana demais para cumprir a necessidade central do desafio.

> “Nossos vendedores gastam tempo demais em negócios que não vão fechar e deixam boas oportunidades esfriarem. Preciso de algo funcional — não de um modelo em um Jupyter Notebook que ninguém vai usar. Quero uma ferramenta que o vendedor abra, veja o pipeline e saiba onde focar. Pode ser simples, mas precisa funcionar.”

Essa observação alterou a prioridade da rodada: não bastava visualizar melhor o ranking; a ferramenta precisava transformar o ranking em orientação operacional imediata.

### Decisão e implementação

- Foi criado o **Foco automático**, reativo ao vendedor, gestor, região e equipe selecionados.
- A primeira tela agora apresenta um líder de Engaging e um de Prospecting, sempre escolhidos pelo ranking canônico de cada estágio, sem criar um score sintético comum.
- Cada cartão mostra oportunidade, produto, tipo de sinal, faixa, força da evidência e próxima ação recomendada; o vendedor obtém direção antes de abrir qualquer tabela.
- Quando um estágio não possui oportunidades no recorte, o cartão informa o estado vazio sem inventar recomendação.
- A fila completa, explicações, paginação e controles continuam disponíveis abaixo para aprofundamento e intervenção do gestor.

### Validação em feedback looping

- Teste novo prova que o radar escolhe um candidato suportado por estágio e nunca promove a linha insuficiente quando existe alternativa válida.
- Passada limpa 1: inspeção renderizada confirmou atualização automática entre vendedor e gestor, incluindo estágio vazio, sem novo achado relevante.
- Passada limpa 2: **22/22** testes focais verdes — 15 contratos, 4 AppTests e 3 journeys Playwright — além de `py_compile` e `git diff --check`.

**Contribuição humana decisiva:** Luis reposicionou a solução de “dashboard que explica” para “ferramenta que recomenda onde agir”. O embargo externo permanece integralmente vigente.

## I18 — Critério 10/10 para a pergunta central — 2026-09-22

Luis elevou a pergunta central a critério obrigatório de saída: **“Quero uma ferramenta que o vendedor abra, veja o pipeline e saiba onde focar.”** A implementação só será considerada aceitável quando responder a essa pergunta com nota **10/10**.

### Diagnóstico do estado atual

- Nota inicial: **7/10**. O Foco automático indica um líder por estágio, mas ainda obriga o vendedor a explorar as tabelas para construir a sequência seguinte de trabalho.
- Lacuna principal: dois cartões isolados não constituem uma fila curta, ordenada e imediatamente executável.
- Limite de honestidade: os dados não sustentam urgência temporal nem identificam negócios “esfriando”; a interface não inventará esse sinal.

### Critério objetivo de 10/10

- Ao abrir, o vendedor verá uma agenda operacional curta, sem precisar filtrar, ordenar ou abrir detalhes.
- `Engaging` e `Prospecting` continuarão separados, com suas ordenações canônicas e sem score sintético comum.
- Cada item mostrará posição, oportunidade, produto, sinal confiável, força da evidência e próxima ação.
- A interface distinguirá claramente **o que fazer agora** da fila completa usada para investigação.
- Estados sem oportunidade acionável serão explícitos e não produzirão recomendação artificial.

### Decisão de implementação

O Foco automático evoluirá para **Minha fila agora**, com até três oportunidades acionáveis por estágio. A primeira será marcada como início recomendado e as seguintes formarão a sequência imediata. Essa é a menor mudança capaz de cumprir a necessidade central sem criar autenticação, CRM, persistência ou comparabilidade estatística que o protótipo não possui.

### Execução e validação

- A abertura agora responde imediatamente **“Comece aqui”**, nomeando oportunidade, estágio e próxima ação.
- As duas frentes exibem até três itens na ordem canônica, com posição, produto, sinal, faixa, evidência e ação; linhas com dados insuficientes não são promovidas como trabalho recomendado.
- A fila completa permanece abaixo para investigação, sem competir com a orientação operacional inicial.
- Uma asserção residual ainda chamava a função de líder removida; o teste foi corrigido para validar a fila vazia diretamente.
- Validação focal final: **8/8** testes verdes — 1 contrato da nova fila, 4 jornadas AppTest e 3 jornadas Playwright — além de `py_compile` e `git diff --check` verdes.
- Inspeção no preview real confirmou o fluxo de Anna Snelling com 112 oportunidades: a tela indicou `CFKXEPFN` como início, seguida por três prioridades `Engaging` e três `Prospecting`, todas com ação explícita.
- Passada limpa 1: testes focais e gates estáticos sem novo achado. Passada limpa 2: inspeção renderizada e verificador local da identidade sem novo achado.
- O verificador local exibiu `TC-47 LIVE OK` por usar a mesma rotina, mas isso **não** constitui o `TC-47` público: não houve deploy, URL pública ou envio aos avaliadores.

### Avaliação da pergunta central

**Nota: 10/10 dentro do escopo e dos dados do challenge.** O vendedor abre, vê o tamanho e a composição do pipeline, recebe uma primeira ação inequívoca e enxerga a sequência curta de trabalho sem precisar filtrar, ordenar ou interpretar a tabela completa. A nota não afirma capacidade inexistente de detectar esfriamento temporal, autenticar usuários, persistir execução ou escrever no CRM; esses limites permanecem explícitos.

## I19 — Feedback humano: foco precisa de justificativa explícita — 2026-09-22

Luis identificou uma lacuna adicional na comunicação operacional:

> “Ainda senti falta de abordagens ou diretrizes claras, como: ‘Foque neste lead porque...’ e ‘Atenção neste lead! Sinais: ...’.”

O feedback invalida a nota 10/10 anterior. A fila dizia **o que fazer**, mas ainda não comunicava de modo suficientemente direto **por que aquele lead merecia foco** nem quais sinais sustentavam a recomendação. A nova nota provisória é **8/10**.

### Decisão

- O destaque principal usará a ordem explícita **“Foque neste lead”**.
- Cada recomendação separará **por quê**, **sinais observados** e **ação recomendada**.
- Os sinais virão dos fatores já reconstruídos pelo score; não serão gerados por texto livre nem tratados como causalidade.
- A linguagem continuará distinguindo prioridade relativa de probabilidade validada.
- O 10/10 só poderá ser restabelecido depois que a justificativa estiver visível na abertura, coberta por regressão e confirmada no preview real.

### Execução e evidência

- O destaque principal passou a declarar **“Foque neste lead”**, seguido de estágio, oportunidade, natureza do sinal, faixa e força da evidência.
- Abaixo dele, **“Atenção aos sinais”** apresenta os dois fatores de maior contribuição absoluta e informa se a associação observada é favorável ou desfavorável.
- Cada item das duas filas agora separa **“Por quê”**, **“Sinais”** e **“Ação”**; isso elimina a necessidade de o vendedor traduzir índice e faixa em uma decisão prática.
- Os rótulos humanizam `product`, `series`, `year_established` e as combinações históricas, sem alterar cálculo, ranking ou próxima ação.
- Passada limpa 1: **8/8** testes focais, `py_compile` e `git diff --check` verdes. Passada limpa 2: inspeção renderizada confirmou a nova mensagem e os sinais reais de `CFKXEPFN`, sem novo achado.

### Reavaliação

**Nota restabelecida: 10/10 dentro do escopo do challenge.** A primeira dobra agora responde, em sequência: **qual lead**, **por que ele**, **quais sinais sustentam a atenção** e **qual ação executar**. O sistema continua sem inventar causalidade ou urgência temporal.

## I20 — Encerramento da lapidação e abertura do check de segurança — 2026-09-22

Luis aprovou o output lapidado e encerrou essa rodada. A contribuição humana consolidada foi exigir que a interface não apenas ordenasse leads, mas declarasse **qual lead merece foco, por quê, quais sinais sustentam a decisão e qual ação deve ser executada**.

A última etapa antes da documentação geral será segurança. Por determinação de Luis, a análise deve considerar somente o que é pertinente ao projeto e classificar cada controle como **FEITO**, **NÃO FEITO** ou **NÃO APLICÁVEL**. Primeiro será emitido o parecer completo; os itens “NÃO FEITO” serão tratados depois, um a um, sem antecipar remediações.

### Resultado do diagnóstico inicial

- **3 FEITO:** ausência de chaves expostas, ausência de segredos detectados no histórico e proteção contra adulteração dos dados/scores do protótipo.
- **2 NÃO FEITO:** trilha persistente de auditoria para a repriorização e backup externo da revisão local.
- **14 NÃO APLICÁVEL:** login, cadastro, e-mail, API, Cloudflare, Sentry, custos, banco, RLS, criptografia de dados sensíveis, autenticação, restrição de registros, cookies autenticados e senhas não existem no escopo atual.

### Evidências e limites

- O app declara explicitamente que o seletor vendedor/gestor é demonstrativo e não autentica usuários.
- Os quatro CSVs são públicos, CC0, versionados e recuperáveis por manifesto; downloads exigem HTTPS e passam por SHA-256, validação de ZIP, limites de tamanho, lock e rollback.
- A prioridade temporária valida papel, estágio, carteira, fingerprint e geração, mas sua atribuição de gestor/horário existe apenas na sessão e não forma log durável.
- A branch remota continua removida por embargo; portanto, a revisão atual não possui backup externo, embora os dados-fonte sejam reproduzíveis.
- A varredura focal do estado atual e do histórico encontrou zero padrões de credenciais de alta confiança. `gitleaks` e `trufflehog` não estão instalados; essa limitação foi registrada sem instalar ferramentas adicionais.

O relatório completo foi criado em `docs/security-checklist.md`. Nenhuma remediação, publicação, deploy ou comunicação externa ocorreu.

## I21 — Segunda passada de certificação do checklist de segurança — 2026-09-22

Luis solicitou uma nova passada antes do tratamento dos gaps. Os 19 controles foram reavaliados contra código, dependências, manifesto, arquivos rastreados, histórico Git e estado da branch.

- Resultado inalterado: **3 FEITO, 2 NÃO FEITO e 14 NÃO APLICÁVEL**.
- Nova varredura: zero chaves AWS, OpenAI ou GitHub, zero chaves privadas, zero atribuições de segredo de alta confiança e nenhum `.env`, `.pem` ou `.key` rastreado.
- Validação focal: **12/12** testes verdes — dez de recuperação segura e dois da prioridade temporária.
- A branch remota segue ausente, confirmando que o trabalho local ainda não possui backup externo verificado.
- Nenhuma remediação foi executada. O parecer certifica a classificação dentro do protótipo atual; não reivindica pentest, SCA integral nem segurança de uma futura arquitetura com dados privados.

## I22 — Segurança, item 1: auditoria persistente — 2026-09-22

Luis autorizou atacar os itens “NÃO FEITO” um a um, validando cada aplicação antes de avançar. O primeiro item tratado foi a trilha de auditoria da prioridade temporária do gestor.

### Implementação

- Cada prioridade confirmada grava primeiro um evento append-only em `data/audit/manager-priorities.jsonl`.
- Diretório e arquivo usam permissões `0700` e `0600`; o append ocorre sob lock exclusivo e termina com `fsync`.
- Eventos são encadeados por SHA-256 e toda a cadeia é revalidada antes do próximo append.
- A operação falha fechado: log ausente de integridade, symlink, adulteração ou erro de I/O impede a alteração da prioridade.
- Como não existe login, o evento registra `actor_verified=false`; o nome do gestor permanece demonstrativo e não é promovido a identidade autenticada.

### Feedback looping e validação

- A regressão nova prova persistência de dois eventos, encadeamento, permissão `0600`, detecção de adulteração e ausência de mutação quando o append falha.
- Validação final: **20/20** testes focais verdes — dez de recuperação, três contratos diretos de pin/auditoria, quatro AppTest e três Playwright — além de `py_compile` e `git diff --check`.
- O checklist passou de **3 FEITO / 2 NÃO FEITO / 14 NÃO APLICÁVEL** para **4 FEITO / 1 NÃO FEITO / 14 NÃO APLICÁVEL**.

O único item “NÃO FEITO” restante é backup externo. Sua execução permanece bloqueada pelo embargo que proíbe push, deploy ou envio sem autorização mais que expressa de Luis.

## I23 — Segurança, item 2: backup local validado e limite externo — 2026-09-22

O segundo item foi atacado até o limite autorizado, sem violar o embargo externo.

- Foi criado um bundle Git completo em `/Users/luisroquette/Projects/ai-master-challenge-backups/003-lead-scorer-2026-09-22.bundle`.
- `git bundle verify` confirmou história completa e a referência correta da branch.
- Um clone real do bundle restaurou o mesmo `HEAD`, worktree limpo e os quatro CSVs com SHA-256 idênticos ao manifesto.
- O procedimento de recuperação foi registrado no checklist de segurança.
- O bundle local protege contra corrupção ou perda do checkout, mas permanece no mesmo Mac e não cobre falha física do equipamento.

O item continua **NÃO FEITO** quanto à cópia externa. Push da branch, upload do bundle ou qualquer outra transmissão permanece proibido até Luis autorizar especificamente o destino e a ação, sem confundir backup com envio aos avaliadores.

## I24 — Encerramento consciente do ciclo de segurança — 2026-09-22

Luis decidiu não autorizar ainda o envio da branch ou do bundle para backup externo, pois a entrega final continuará em lapidação e o embargo deve ser preservado.

O ciclo de auditoria de segurança foi encerrado com **4 FEITO, 1 NÃO FEITO e 14 NÃO APLICÁVEL**. O único item pendente — backup externo — permanece assim por decisão explícita do owner. A implementação local pertinente foi concluída, validada e documentada; nenhum push, deploy, PR ou contato com avaliadores ocorreu.

**Regra de reabertura:** revisar novamente o checklist imediatamente antes de publicação, adoção de dados privados, autenticação, banco ou integração com CRM.

## I25 — Auditoria final das regras de entrega — 2026-09-22

Antes de executar a embalagem final, as regras do Challenge 003, o guia de submissão, o README raiz, o `CONTRIBUTING.md` e o template oficial foram confrontados novamente com o plano.

### Achados incorporados

- A aplicação funcional continua sendo a entrega principal; tour, DOCX e mapa visual são evidências complementares.
- O arquivo obrigatório `submissions/luis-roquette/README.md` deve funcionar como porta de entrada e seguir o template oficial.
- O README precisa indexar solução, setup, resultados, limitações, ferramentas de IA, erros corrigidos, contribuição humana, iterações e evidências.
- A submissão final aceita somente um PR para `upstream/main`, com título `[Submission] Luis Roquette — Challenge 003`, e não pode alterar arquivos fora de `submissions/luis-roquette/`.
- Screenshots, gravação e export do chat são formatos opcionais; a narrativa escrita e o histórico Git já constituem evidências aceitas.
- A branch `submission/seu-nome` é o padrão documentado, mas já existe no fork para outro trabalho; o nome final será resolvido sem sobrescrever histórico e sem publicação antecipada.

### Correção de estado externo

O PR anterior `#140` está **fechado**, não foi mergeado, e a branch remota do Challenge 003 permanece removida. A leitura foi apenas verificatória. Nenhum novo push, deploy, PR ou contato com avaliadores ocorreu.

## I26 — Início da execução do plano de entrega — 2026-09-22

Luis autorizou a execução local do plano. O escopo inclui README raiz, resumo metodológico em Markdown e DOCX, curadoria de prompts, roteiro do tour, mapa visual e gates finais. Deploy, push, PR e qualquer transmissão externa continuam fora do escopo até autorização expressa posterior.

O nome de trabalho adotado para a metodologia é **Método de Construção Cognitiva em Loops (MCCL)**. A documentação será concisa, baseada em uma fonte Markdown e orientada a três movimentos para o avaliador: usar o sistema, compreender o método e verificar a evolução.

## I27 — Execução local da embalagem final — 2026-09-22

### Artefatos produzidos

- `submissions/luis-roquette/README.md`: porta de entrada baseada no template oficial, com solução, setup, resultados, recomendações, limitações, processo e evidências.
- `docs/metodologia-construcao-cognitiva-em-loops.md`: fonte textual única do método MCCL.
- `docs/metodologia-construcao-cognitiva-em-loops.docx`: versão executiva de três páginas.
- `docs/do-prompt-ao-produto.png`: mapa visual 1920 × 1080 da evolução do briefing à entrega.
- `docs/prompts-chave.md`: doze intervenções humanas e a mudança produzida por cada uma.
- `docs/roteiro-tour-guiado.md`: roteiro de sete cenas, com percursos de vendedor e gestor e fallback em vídeo ou GIF.
- `docs/filosofia-visual.md`: direção estética usada para o mapa.

### Feedback looping da documentação

1. O primeiro mapa visual apresentava a sequência inferior em direção cronológica invertida. A composição foi corrigida e reinspecionada em resolução original.
2. O primeiro render do DOCX mostrou linha decorativa sob o título, duas páginas com vazio excessivo e numeração continuada em 7–9. O gerador foi corrigido e o segundo render condensou o conteúdo em três páginas sem defeitos visíveis.
3. A auditoria de acessibilidade detectou uma imagem sem texto alternativo. O atributo foi incorporado ao OOXML; a nova auditoria terminou com **0 achados altos, médios ou baixos**.
4. As três páginas finais foram renderizadas novamente e inspecionadas integralmente após a correção de acessibilidade.

### Gate local e limite externo

A raiz do repositório ignora `submissions/` por padrão; por isso, os novos arquivos precisam de inclusão explícita com `git add -f`, sem alterar o `.gitignore` e sem tocar arquivos fora da pasta autorizada. O tour publicado, a URL pública, o TC-47 remoto, o push e o PR continuam pendentes por dependerem de autorização externa expressa.

## I28 — Correção da arquitetura de entrega visual — 2026-09-22

Luis rejeitou uma embalagem centrada em sete arquivos de texto e uma imagem estática. O diagnóstico foi direto: os READMEs estavam confusos, faltava uma narrativa audiovisual da construção, não existiam mapa mental e infográfico adequados e o sistema precisava de um wizard demonstrativo no padrão Arcade.

### Decisão de entrega

- Uma única porta de entrada visual passa a preceder a documentação.
- O README raiz vira um índice curto; detalhes técnicos e metodológicos ficam recolhidos como evidência.
- NotebookLM será usado para produzir vídeo explicativo, mapa mental e infográfico a partir de uma fonte curada e sem segredos.
- Arcade será usado para capturar o produto real como tour interativo, com hotspots e orientação passo a passo.
- Os artefatos longos continuam preservados, mas deixam de competir pela atenção inicial do avaliador.

A transmissão permanece limitada às ferramentas autorizadas por Luis para criação desses artefatos. Nenhum conteúdo será enviado aos avaliadores, publicado, submetido em PR ou implantado sem autorização expressa posterior.

## I29 — Produção visual no NotebookLM e portal guiado — 2026-09-22

Uma fonte única, curta e sem segredos foi preparada para impedir que os materiais visuais herdassem a dispersão dos documentos longos. O NotebookLM recebeu somente essa fonte e foi orientado a não inventar métricas, publicação, autenticação ou integração com CRM.

### Feedback looping visual

1. O primeiro mapa mental foi exportado com os ramos recolhidos. Todos os nós foram expandidos e a versão útil substituiu a inicial.
2. O primeiro infográfico usou a legenda ambígua “Falhas de Probabilidade 0”, apesar de quatro rotas terem sido rejeitadas. Uma segunda geração foi instruída com os contratos exatos: **4 de 4 rotas rejeitadas** e **0 probabilidades indevidas publicadas**.
3. O segundo infográfico corrigiu a afirmação e foi adotado como artefato final.
4. A experiência guiada local passou de nove para onze telas e incorporou as duas peças reais do NotebookLM.
5. A validação no navegador confirmou onze telas, cinco imagens carregadas em resolução nativa e zero erros ou avisos de console.

O vídeo explicativo foi solicitado em português, no formato abrangente, com foco no produto, nas decisões de integridade, na evolução MCCL, na contribuição humana e nos limites. O NotebookLM entregou uma versão de **5min48s**, baixada e incorporada diretamente à experiência guiada. O portal final passou a ter doze telas, incluindo reprodução nativa do vídeo.

## I30 — Wizard no estilo Arcade e limite da plataforma — 2026-09-22

O requisito foi atendido como uma experiência guiada local no estilo Arcade: doze telas, navegação sequencial, hotspots, capturas reais do produto, vídeo incorporado e chamadas claras para produto e evidências. Essa escolha mantém a experiência revisável antes de qualquer publicação.

O Arcade real foi aberto, mas exigiu autenticação ou criação de conta. Nenhuma conta, extensão, gravação pública ou compartilhamento foi criado automaticamente. A migração do wizard validado para a plataforma permanece uma etapa opcional posterior, sujeita à autorização específica de login/publicação e sem bloquear a entrega local.

## I31 — Correção da orientação de navegação — 2026-09-22

Na revisão humana, Luis identificou que não estava claro que a experiência avançava pelo botão inferior. A causa foi a hierarquia visual: a navegação parecia controle secundário e podia sair da área de atenção.

A primeira tela recebeu um CTA central animado **“Começar experiência →”**, a instrução explícita **“12 etapas · avance pelos botões abaixo”** e uma barra inferior fixa. O botão principal passou a usar alto contraste e rótulos contextuais: **Começar**, **Próxima etapa** e **Fim**. A correção aplicou a orientação da skill Frontend Design sem adicionar biblioteca ou novo componente externo.

## I32 — Auditoria pré-entrega e conformidade com o template — 2026-09-22

Luis autorizou iniciar a entrega oficial “como manda o figurino”. Antes de qualquer transmissão, as regras do Challenge 003, o guia, o `CONTRIBUTING.md`, o template e o PR anterior foram confrontados novamente com o pacote final.

- A entrega continua restrita a `submissions/luis-roquette/`; nenhum arquivo externo à pasta foi alterado.
- O PR oficial anterior é o `#140`, fechado sem merge. A regra “um PR por pessoa” determina atualizar a mesma branch e reabrir esse PR, em vez de criar outro.
- O README raiz foi alinhado explicitamente às seções do template: identificação, resumo, solução, abordagem, resultados, recomendações, limitações, workflow, erros da IA, contribuição humana e evidências.
- O primeiro passo da experiência local passou a incluir comando e URL exatos, sem sugerir que um arquivo HTML no GitHub equivale a um deploy.
- Os diretórios `__pycache__` encontrados são locais e ignorados; não fazem parte do diff. O whitespace apontado nos CSVs pertence ao snapshot CC0 preservado por checksum e não será reescrito.

Nenhum push, reabertura de PR, deploy ou contato com avaliadores ocorreu nesta etapa. A primeira transmissão externa permanece condicionada à confirmação de Luis imediatamente antes da ação.

## I33 — Incorporação do walkthrough humano legendado — 2026-09-22

Luis entregou a gravação final legendada e acelerada em 1,25× para integrar o pacote antes da publicação. O arquivo original tinha 233 MB, acima do limite individual de 100 MB do GitHub, e não poderia compor o PR nesse estado.

- A versão de entrega foi transcodificada localmente para H.264/AAC, 1280 × 720, 30 fps e 86,8 MB, sem chamada de API externa.
- A duração final é 6min05s; a decodificação integral terminou sem erro e quadros distribuídos pelo vídeo confirmaram imagem e legendas visíveis.
- O walkthrough humano passou a ser o vídeo principal da experiência guiada.
- O vídeo de 5min48s produzido no NotebookLM foi preservado como material complementar, mantendo a evidência visual originalmente planejada.
- README, portal e links finais foram atualizados sem criar uma nova etapa ou ampliar a navegação de doze telas.

Nenhum push, reabertura de PR, deploy ou contato com avaliadores ocorreu durante a incorporação.

## I34 — Auditoria final, publicação da branch e bypass do preflight — 2026-09-22

Luis autorizou a análise final de conformidade e determinou seguir com a entrega caso o resultado fosse positivo. O pacote foi novamente confrontado com o briefing, o guia, o template e as regras do PR.

- Resultado estático: todos os obrigatórios presentes; zero arquivos fora de `submissions/luis-roquette/`; zero blobs acima de 100 MB; zero padrões de segredo; branch contendo integralmente `upstream/main`.
- O commit `d1c351fef9f7a4cea36a4095e6c4eb1468b40c5d` foi enviado à branch do fork. O GitHub aceitou todo o pacote e apenas recomendou reduzir o vídeo de 82,8 MiB abaixo de 50 MiB; não houve bloqueio.
- Um Codespace limpo recuperou a branch e confirmou a disponibilidade externa do commit, concluindo o item de backup externo do checklist de segurança.
- A primeira tentativa de preflight encerrou antes dos testes porque a automação comparou o SHA correto abreviado com um sufixo completo inferido incorretamente. A segunda tentativa ficou condicionada à inicialização de outro Codespace.
- Luis então determinou: **“bypass no preflight. vamos direto”**. A execução pendente foi interrompida; nenhum resultado integral final é reivindicado.

A válvula de escape foi usada de forma explícita e transparente. Permanecem válidos os gates leves e focais registrados, mas eles não são apresentados como substitutos de um novo preflight integral.

## I35 — Entrega oficial pelo PR único — 2026-09-22

Após o registro transparente do bypass, o PR oficial `#140` foi reaberto em vez de criar uma segunda submissão, preservando a regra “um PR por pessoa”.

- Título final: `[Submission] Luis Fernando Roquette — Challenge 003`.
- Base: `Gestao-Quatro-Ponto-Zero/ai-master-challenge:main`.
- Head: `luisroquette:submission/luis-roquette-003-lead-scorer`.
- Estado observado após a reabertura: `OPEN`, não-draft e `CLEAN`.
- A descrição do PR orienta o avaliador ao README, experiência guiada, aplicação e diário; também declara explicitamente que não houve novo preflight integral final.

Esse PR é o canal oficial de entrega previsto pelo regulamento. Nenhum deploy público foi reivindicado como requisito cumprido e nenhuma mensagem paralela foi enviada aos avaliadores.

## I36 — Revisão pública final da experiência do avaliador — 2026-09-22

Luis solicitou uma revisão geral adicional antes de considerar a entrega encerrada. A branch local, o fork e o PR foram comparados no mesmo SHA; o PR permaneceu público, `OPEN`, não-draft e `CLEAN`, com todos os 63 arquivos restritos à pasta autorizada.

A inspeção da página pública sem login encontrou um único refinamento de comunicação: os quatro caminhos da seção “Como avaliar” estavam formatados como código, não como links. A descrição do PR foi atualizada com links diretos para o README, a experiência guiada, o setup da aplicação e o diário. Nenhuma lógica, dado, métrica ou limitação foi alterada nessa lapidação.

## I37 — Grafo estrutural e semântico com Graphify — 2026-09-22

Luis decidiu criar e documentar um grafo da entrega para transformar o conjunto de código, testes, SPECs, diário e materiais visuais em uma superfície única de navegação e auditoria.

- Escopo: toda a submissão, com 51 fontes detectadas; 36 documentos ou transcrições, oito arquivos de código, cinco imagens e dois vídeos transcritos localmente.
- Construção: AST local combinado com sete lotes semânticos; nenhuma API paga foi acionada.
- Resultado final: 570 nós, 989 relações e 21 comunidades rotuladas, com visualização HTML autocontida.
- Rastreabilidade: os 10 God Nodes, as cinco Surprising Connections e as sete Suggested Questions foram verificados integralmente e registrados com fonte e limite de interpretação.
- Integridade final: zero endpoints ausentes ou pendentes, zero duplicatas exatas e zero colapsos; cinco auto-relações AST foram mantidas e declaradas.
- Limites: o diagnóstico pré-build registrou 95 arestas pendentes normalizadas ou descartadas e 17 pares multirrelação; o DOCX foi representado pelo Markdown equivalente porque o extra opcional de Office não estava instalado; relações `INFERRED` não são apresentadas como prova causal ou de runtime.

A versão instalada do Graphify era `0.9.64`, enquanto a skill local declarava `0.9.51`. A ferramenta global não foi alterada durante a entrega; o comportamento efetivamente executado foi validado pelos diagnósticos do pacote instalado.

## I38 — Arquivo local organizado da entrega — 2026-09-22

Luis solicitou que todos os entregáveis e uma réplica do sistema fossem preservados de forma organizada no computador. Foi criada a pasta `Documents/AI-Master-Challenge/Challenge-003-Lead-Scorer-Entrega-Final-2026-09-22/` com a entrega completa, instruções de abertura, origem, inventário e checksums SHA-256.

- Foram preservados 81 arquivos úteis, incluindo aplicação, dados, testes, experiência guiada, vídeos, documentação, diário e grafo.
- Dez arquivos temporários `__pycache__/*.pyc` foram omitidos por não fazerem parte do sistema ou da entrega.
- A comparação com a origem terminou sem diferenças de conteúdo, considerando apenas essa exclusão organizacional.
- Os 81 checksums foram recalculados e validados; nenhum arquivo `.env` ou credencial pessoal foi incluído.
