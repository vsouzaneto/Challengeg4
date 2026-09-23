# Diário de processo — Challenge 004: Estratégia Social Media

## I01 — Briefing absorvido por releitura em loop — 2026-09-21 14:27 BRT

- **Objetivo:** compreender integralmente o desafio antes de pesquisar soluções, analisar dados ou construir qualquer ferramenta.
- **IA/ferramenta:** Codex para leitura sistemática; Git e GitHub CLI para confirmar a versão do arquivo.
- **Ação ou prompt:** Luis definiu um gate de absorção: reavaliar o briefing por lentes diferentes até completar pelo menos duas passadas consecutivas sem novos achados.
- **Resultado:** seis passadas concluídas; as passadas 5 e 6 não produziram novas descobertas. O arquivo local e o `main` remoto eram idênticos no blob Git `52b10db595fb2a3f50c8a7cc73573fa53f5db087`.
- **Julgamento humano:** a técnica de leitura em loop e o critério de parada foram decisões criativas de Luis. A IA executou e documentou o protocolo.
- **Verificação:** checklist reverso localizou 18 de 18 requisitos críticos; duas releituras consecutivas encerraram sem novos achados.
- **Evidência:** este ledger e o histórico Git do arquivo.
- **Limitação:** os dados ainda não foram inspecionados; nenhuma hipótese de performance foi validada.

### Ledger das passadas

| Passada | Lente | Novos achados |
|---|---|---|
| 1 | leitura literal | contexto, dados, quatro entregáveis, critérios de qualidade, dicas e público executivo |
| 2 | contradições e exigências implícitas | ausência de gasto impede ROI financeiro verdadeiro; Bilibili e RedNote aparecem nos dados, mas não no contexto inicial; frequência e thresholds exigem cautela causal |
| 3 | documentos obrigatórios vinculados | process log é eliminatório e deve mostrar decomposição, iterações, erros da IA, correções e contribuição humana |
| 4 | template e regras de submissão | resumo executivo curto, resultados com evidência, recomendações priorizadas, limitações, instruções de uso e alterações restritas à pasta da submissão |
| 5 | conferência integral por seção | nenhum |
| 6 | checklist reverso dos requisitos | nenhum |

**Gate atingido:** duas passadas consecutivas sem novos achados. Pesquisa e construção continuam bloqueadas até a Regra zero ser cumprida.

### Compreensão consolidada

O desafio pede uma análise controlada, não médias gerais. A comparação entre conteúdo orgânico e patrocinado precisa considerar pelo menos plataforma, categoria e tamanho do creator, além de contextualizar engagement rate com alcance. Sem dados de gasto, não existe base para declarar ROI financeiro.

A estratégia deve dizer onde concentrar esforço, o que produzir, para quem, quando, com qual faixa de creator e qual evidência sustenta a decisão. Também precisa apontar o que parar, ordenar prioridades e propor quick wins executáveis na mesma semana.

O diferencial deve transformar os achados em decisão recorrente sem aumentar o escopo antes da evidência. A escolha entre dashboard, recomendador ou outra ferramenta será feita somente após pesquisa de soluções existentes e inspeção dos dados.

## I02 — SDD adotado antes da construção — 2026-09-21 14:31 BRT

- **Objetivo:** transformar o desafio em especificação verificável antes de implementar análise ou ferramenta.
- **IA/ferramenta:** skills `add-task`, `plan-task` e `implement-task` do Context Engineering Kit, instaladas para Claude Code via `npx skills`.
- **Ação ou prompt:** Luis decidiu usar Spec-Driven Development e indicou a skill SDD do repositório `NeoLabHQ/context-engineering-kit`.
- **Resultado:** a versão atual não expõe uma skill única chamada `sdd`; o fluxo foi instalado pelos três componentes publicados. Nenhuma SPEC foi criada: ela dependerá da descoberta socrática e da arquitetura aprovadas por Luis.
- **Julgamento humano:** adotar SDD foi decisão de Luis. O planejamento deve passar por revisão humana antes de qualquer implementação; a SPEC não substitui a Regra zero de pesquisa e evidência.
- **Verificação:** o instalador confirmou as três skills para Claude Code e classificou todas como seguras.
- **Evidência:** este registro, `skills-lock.json` e os diretórios locais `.claude/skills/`.
- **Limitação:** `npx skills` instala skills, mas não os subagentes do plugin completo. Os artefatos de ferramenta ficam locais e não entrarão no Pull Request, que aceita apenas `submissions/luis-roquette/`.

**Fluxo adotado:** `descoberta socrática → arquitetura aprovada → add-task → plan-task → revisão humana da SPEC → implement-task`, sempre subordinado às regras de pesquisa, Ponytail, testes e integridade do desafio.

## I03 — Documentação como parte central da entrega — 2026-09-21 14:34 BRT

- **Decisão de Luis:** documentar todo o processo é tão importante quanto — ou mais importante que — o resultado final. Ganha quem documenta.
- **Forma:** registrar continuamente fragmentos curtos, objetivos e diretos, com destaque para os pontos que Luis sinalizar durante o trabalho.
- **Regra editorial:** corrigir erros de português antes de incorporar qualquer fala ou decisão ao diário, preservando o sentido original.
- **Princípio:** como dizia Silvio Santos: “Sabe por que o ovo de galinha vende mais que o de pata? Porque a galinha canta quando bota!”
- **Aplicação:** cada decisão, hipótese, correção, evidência, limitação e contribuição humana relevante será registrada no momento em que ocorrer, sem reconstrução retroativa.

## I04 — Descoberta socrática em ondas adaptativas — 2026-09-21 14:41 BRT

- **Decisão de Luis:** a SPEC não será presumida nem escrita antes de discutirmos exaustivamente o projeto e arquitetarmos a solução sobre bases sólidas.
- **Método:** conduzir pelo menos cinco ondas socráticas, com uma pergunta de múltipla escolha por vez. Cada onda posterior dependerá das respostas e descobertas das ondas anteriores.
- **Objetivo:** explicitar problema, decisão de negócio, usuários, restrições, hipóteses, alternativas, riscos, dados, arquitetura, critérios de sucesso e definição de pronto antes da especificação.
- **Adaptação:** não existe roteiro rígido. As respostas de Luis determinam a próxima pergunta, e ondas adicionais serão abertas se permanecer qualquer ambiguidade material.
- **Gate:** somente após encerrar as ondas, comparar abordagens, validar a arquitetura em blocos e obter concordância de Luis será criada a SPEC SDD.
- **Correção de processo:** o placeholder criado prematuramente foi removido sem entrar no Git. Nenhuma SPEC existe neste momento.
- **Formato definido por Luis:** todas as perguntas serão de múltipla escolha, com opções claras, mutuamente distintas e recomendação explícita quando houver base para recomendá-la.

## I05 — Ledger da descoberta socrática — 2026-09-21 14:49 BRT

Este ledger registra todas as perguntas, respostas, correções e decisões da descoberta nesta sessão.

### Tentativa anterior à Onda 1 — descartada

- **Pergunta:** se a entrega estivesse pronta amanhã, qual seria a única decisão de maior valor que o Head de Marketing deveria conseguir tomar com confiança?
- **Resposta de Luis:** a pergunta deveria ser de múltipla escolha.
- **Efeito:** pergunta descartada sem resposta de conteúdo; todas as ondas passaram a usar múltipla escolha.

### Onda 1 — decisão central

- **Pergunta:** qual decisão principal a solução deve permitir?
- **Opções:** A) realocar esforço e patrocínio; B) definir o calendário editorial; C) criar um sistema operacional recorrente para planejar, acompanhar e corrigir a estratégia.
- **Resposta de Luis:** **C — criar um sistema operacional recorrente**.
- **Implicação:** a solução não será apenas uma análise estática. Ela deverá sustentar um ciclo repetível de decisão, acompanhamento e correção; o escopo desse ciclo será definido nas próximas ondas.

### Onda 2 — operador principal

- **Pergunta:** quem deve operar o sistema recorrente no cotidiano?
- **Opções:** A) Gestor de Social Media, no planejamento e acompanhamento diário; B) Head de Marketing, na revisão semanal de estratégia e investimento; C) Analista de Marketing, no diagnóstico mensal e preparação das recomendações.
- **Resposta de Luis:** **A, B e C**, tendo o **Gestor de Social Media como operador principal**.
- **Implicação:** a arquitetura deverá atender três níveis de uso sem confundir responsabilidades: operação diária pelo Gestor de Social Media, decisão executiva pelo Head de Marketing e análise periódica pelo Analista de Marketing. O fluxo principal será desenhado para o gestor; os demais receberão visões derivadas.

### Onda 3 — cadência central

- **Pergunta:** qual cadência deve comandar o sistema?
- **Opções:** A) ciclo diário, com consolidações semanais e mensais automáticas; B) ciclo semanal, com dados diários usados apenas como entrada; C) ciclo mensal, orientado principalmente à revisão estratégica.
- **Resposta de Luis:** **A — ciclo diário, com consolidações semanais e mensais automáticas**.
- **Implicação:** o produto deverá gerar utilidade operacional todos os dias e agregar os mesmos dados em visões semanais e mensais, sem criar três fluxos independentes.

### Onda 4 — entrega diária principal

- **Pergunta:** qual deve ser a primeira entrega que o Gestor de Social Media vê diariamente?
- **Opções:** A) fila priorizada de ações; B) painel de monitoramento com desempenho recente, alertas e desvios; C) quadro de experimentos.
- **Resposta de Luis:** **B — painel de monitoramento**.
- **Implicação:** a experiência principal começa pela observação objetiva do desempenho e das mudanças relevantes. Recomendações e experimentos poderão derivar do painel, mas não substituirão a leitura dos dados como porta de entrada.

### Onda 5 — mecanismo de alerta

- **Pergunta:** o que deve fazer o painel chamar a atenção do gestor?
- **Opções:** A) desvio contextual em relação a plataforma, formato, categoria e faixa de creator; B) limites fixos; C) ranking absoluto do período.
- **Resposta de Luis:** **A com C** — desvio contextual como mecanismo recomendado, acompanhado por ranking absoluto.
- **Implicação:** o painel deverá priorizar anomalias contra grupos comparáveis e usar rankings como contexto secundário. Números absolutos não poderão, isoladamente, sustentar uma recomendação.
- **Estado das ondas:** o mínimo de cinco ondas foi atingido, mas a descoberta continuará porque ainda existem decisões de arquitetura, governança e validação em aberto.

### Onda 6 — resposta aos alertas

- **Pergunta:** após detectar um desvio, o sistema deve explicar e sugerir uma ação com decisão humana, alterar automaticamente o plano ou apenas mostrar os dados?
- **Opções:** A) explicar o sinal e sugerir uma ação, exigindo decisão humana; B) alterar automaticamente calendário, formato ou investimento; C) mostrar somente os dados, sem recomendar ação.
- **Resposta de Luis:** **A — explicar o sinal e sugerir uma ação, exigindo decisão humana**.
- **Implicação:** a IA terá papel assistivo e explicável. O sistema poderá recomendar, mas não executará mudanças de calendário ou investimento sem aprovação do gestor; evidência, incerteza e justificativa deverão acompanhar cada sugestão.

### Onda 7 — entrada de dados do MVP

- **Pergunta:** como o sistema deve receber novos dados?
- **Opções:** A) importação manual de CSV; B) integração direta com APIs das plataformas; C) modelo híbrido, com CSV funcional agora e arquitetura preparada para APIs futuras.
- **Resposta de Luis:** **C**, deixando claro que, para o MVP, foi escolhida uma solução simplificada e manual.
- **Implicação:** o MVP aceitará arquivos CSV com validação explícita. Integrações com APIs serão apenas uma possibilidade futura; não haverá conectores, autenticação ou sincronização automática no escopo inicial.
- **Simplificação deliberada:** a extensibilidade futura não autoriza abstrações ou infraestrutura especulativas. O código do MVP deverá permanecer mínimo e orientado ao formato de dados comprovado.

### Onda 8 — formato de uso do MVP

- **Pergunta:** onde os três perfis devem usar o sistema?
- **Opções:** A) dashboard web local; B) planilha enriquecida; C) notebook analítico.
- **Resposta de Luis:** **A — dashboard web local**.
- **Implicação:** o MVP deverá permitir importar o CSV e navegar visualmente por monitoramento, desvios contextuais, rankings e recomendações. A ferramenta deverá funcionar localmente e ser demonstrável sem infraestrutura remota obrigatória.

### Onda 9 — experiência dos três perfis

- **Pergunta:** como o dashboard deve atender Gestor, Head e Analista?
- **Opções:** A) cockpit principal para o Gestor, com resumos semanais e mensais exportáveis; B) três áreas separadas; C) interface única com seletor de perfil.
- **Resposta de Luis:** **A — cockpit principal para o Gestor, com resumos exportáveis para os demais**.
- **Implicação:** haverá uma única experiência operacional, centrada no Gestor de Social Media. Head e Analista consumirão sínteses derivadas da mesma fonte, evitando três produtos, permissões ou navegações independentes no MVP.

### Onda 10 — benchmark dos alertas

- **Pergunta:** como definir o desempenho esperado de cada post?
- **Opções:** A) mediana e distribuição de grupos comparáveis por plataforma, formato, categoria, faixa de creator e período; B) média global; C) modelo preditivo desde o MVP.
- **Resposta de Luis:** **A — grupo comparável**.
- **Implicação:** alertas serão baseados em referências robustas e contextuais. A granularidade final dependerá do tamanho real das amostras; quando um grupo for pequeno, o sistema deverá recuar para um nível comparável mais amplo e declarar essa limitação.

### Onda 11 — avaliação de patrocínios

- **Pergunta:** como o MVP deve avaliar posts patrocinados?
- **Opções:** A) comparação controlada de alcance e engajamento contra orgânicos comparáveis, sem alegar ROI financeiro sem custo; B) comparação direta de médias gerais; C) ROI calculado com custos hipotéticos.
- **Resposta de Luis:** **A — comparação controlada, sem alegação indevida de ROI financeiro**.
- **Implicação:** patrocínio será avaliado como diferença observacional de desempenho dentro de contextos comparáveis. O sistema deverá separar associação de causalidade, mostrar incerteza e declarar que retorno financeiro exige dados reais de investimento e receita.

### Onda 12 — sucesso principal do MVP

- **Pergunta:** qual prova define que o MVP funciona?
- **Opções:** A) importar um CSV e identificar desvio, evidência, contexto e próxima ação em até cinco minutos, com números rastreáveis; B) atingir uma métrica mínima de previsão; C) exibir todas as métricas e filtros do dataset.
- **Resposta de Luis:** **A — decisão rastreável em até cinco minutos**.
- **Implicação:** a definição de pronto será orientada à velocidade e à qualidade da decisão, não ao volume de funcionalidades. Cada alerta e recomendação deverá permitir chegar aos registros e cálculos que a sustentam.

### Onda 13 — ciclo de aprendizado

- **Pergunta:** o que deve acontecer com cada recomendação?
- **Opções:** A) registrar se foi aceita, rejeitada ou editada e comparar depois a decisão com o resultado observado; B) exibir temporariamente sem guardar a decisão; C) converter automaticamente em tarefa ou publicação.
- **Resposta de Luis:** **A — registrar a decisão humana e comparar com o resultado posterior**.
- **Implicação:** o sistema terá memória operacional auditável. A evolução não dependerá de a IA executar ações: dependerá de registrar a escolha humana, receber dados posteriores e confrontar recomendação, decisão e resultado sem inventar causalidade.

### Onda 14 — persistência local

- **Pergunta:** onde o MVP deve guardar decisões e resultados?
- **Opções:** A) SQLite local, sem serviço externo; B) arquivos CSV ou JSON; C) somente na sessão.
- **Resposta de Luis:** **A — SQLite local**.
- **Implicação:** decisões, revisões e resultados poderão ser consultados entre sessões com integridade transacional e trilha auditável, sem exigir conta, nuvem ou banco remoto.

### Onda 15 — retenção dos dados

- **Pergunta:** o que deve ser persistido no SQLite?
- **Opções:** A) decisões, resultados e metadados do arquivo, mantendo o CSV bruto fora do banco; B) toda a base importada; C) uma cópia completa de cada CSV enviado.
- **Resposta de Luis:** **A — persistir decisões, resultados e metadados; não copiar o CSV bruto**.
- **Implicação:** o banco manterá o estado operacional mínimo. Cada importação poderá ser identificada por metadados e hash, enquanto análises serão recalculadas a partir do arquivo fornecido pelo usuário, reduzindo duplicação e exposição de dados.

### Onda 16 — motor de recomendações

- **Pergunta:** como o MVP deve produzir recomendações?
- **Opções:** A) regras estatísticas determinísticas, com evidência, benchmark e justificativa reproduzível; B) API de IA generativa; C) modelo local de IA.
- **Resposta de Luis:** **A — regras estatísticas determinísticas**.
- **Implicação:** recomendações deverão resultar de cálculos e regras auditáveis. Nenhuma API paga, modelo generativo ou dependência de inferência será necessária para operar o MVP.

### Onda 17 — comunicação da incerteza

- **Pergunta:** como cada alerta deve demonstrar sua confiabilidade?
- **Opções:** A) mostrar benchmark, tamanho da amostra, diferença observada e nível de confiança; B) usar apenas um semáforo; C) apresentar somente uma explicação textual.
- **Resposta de Luis:** **A — evidência quantitativa e nível de confiança**.
- **Implicação:** todo alerta deverá expor os elementos mínimos para auditoria. Grupos insuficientes deverão ser sinalizados, e uma recomendação não poderá aparentar certeza maior que a sustentada pelos dados.

### Onda 18 — navegação do dashboard

- **Pergunta:** como organizar a experiência principal?
- **Opções:** A) visão geral com alertas prioritários e detalhamento sob demanda; B) páginas separadas por tema; C) página única extensa.
- **Resposta de Luis:** **A — visão geral com drill-down**.
- **Implicação:** o dashboard deverá começar pelo que exige atenção e permitir aprofundamento progressivo até os registros e cálculos. A arquitetura de informação evitará tanto fragmentação por excesso de páginas quanto uma tela única sobrecarregada.

### Onda 19 — prioridade dos alertas

- **Pergunta:** como ordenar os alertas na visão geral?
- **Opções:** A) impacto × confiança × atualidade; B) maior variação percentual; C) ordem cronológica.
- **Resposta de Luis:** **A — impacto × confiança × atualidade**.
- **Implicação:** uma anomalia extrema, mas pequena ou pouco sustentada, não dominará automaticamente o painel. A fórmula final deverá ser simples, documentada e testada, sem esconder seus componentes em um score opaco.

### Onda 20 — definição de impacto

- **Pergunta:** sem dados financeiros, como medir o impacto de um alerta?
- **Opções:** A) volume potencial afetado, combinando alcance, interações e exposição do creator, separado da confiança estatística; B) somente engagement rate; C) importância subjetiva atribuída pelo gestor.
- **Resposta de Luis:** **A — volume potencial afetado**.
- **Implicação:** o dashboard priorizará escala observável sem chamá-la de receita ou ROI. Taxa e volume serão apresentados juntos para evitar favorecer artificialmente creators grandes ou pequenos.

### Onda 21 — arquivo inválido

- **Pergunta:** como o MVP deve reagir a um CSV incompleto ou inconsistente?
- **Opções:** A) bloquear a análise e mostrar coluna, problema e correção esperada; B) importar apenas linhas válidas e descartar as demais; C) corrigir automaticamente sem confirmação.
- **Resposta de Luis:** **A — bloquear e apresentar diagnóstico acionável**.
- **Implicação:** a validação da entrada será um gate. O sistema não produzirá indicadores sobre uma base parcialmente descartada ou modificada sem conhecimento do usuário; o erro deverá indicar localização, causa e correção.

### Onda 22 — saída para Head e Analista

- **Pergunta:** o que o dashboard deve exportar?
- **Opções:** A) resumo executivo de uma página e CSV das evidências e decisões; B) relatório técnico completo em PDF; C) somente imagens dos gráficos.
- **Resposta de Luis:** **A — resumo executivo e CSV rastreável**.
- **Implicação:** o Head receberá síntese curta e priorizada; o Analista poderá auditar os dados estruturados. A exportação evitará um relatório longo que replique toda a interface.

### Onda 23 — uso dos dados de audiência

- **Pergunta:** como audiência deve influenciar a análise?
- **Opções:** A) usar idade, gênero e localização nos benchmarks e filtros quando houver amostra suficiente; B) criar clusters e personas automáticas; C) mostrar demografia sem influenciar alertas.
- **Resposta de Luis:** **A — segmentação contextual condicionada à suficiência da amostra**.
- **Implicação:** audiência fará parte do contexto analítico, mas não fragmentará grupos até perder validade. O sistema deverá recuar a uma segmentação mais ampla e informar o usuário quando a amostra não sustentar o corte solicitado.

### Onda 24 — diferencial do MVP

- **Pergunta:** qual deve ser o diferencial principal da entrega?
- **Opções:** A) cockpit decisório completo, com alertas contextuais, recomendações explicáveis, decisão humana e aprendizado posterior; B) modelo preditivo adicional; C) módulo avançado de hashtags adicional.
- **Resposta de Luis:** **A — cockpit decisório completo**.
- **Implicação:** o diferencial virá da integração disciplinada entre análise, decisão e aprendizado, não da acumulação de módulos. Modelo preditivo e análise avançada de hashtags ficam fora do MVP, salvo se a pesquisa ou os dados provarem que são necessários.
- **Estado da descoberta:** 24 ondas concluídas. Problema, usuários, cadência, entrada, persistência, análise, confiança, decisão, exportação e diferencial têm direção suficiente para comparar arquiteturas antes da SPEC.

## I06 — Arquitetura-base escolhida pelo briefing — 2026-09-21 16:33 BRT

- **Pergunta:** entre monólito web local, frontend com API separada, aplicativo desktop, planilha, plataforma preditiva e sistema generativo, qual arquitetura segue mais fielmente o Challenge 004?
- **Decisão:** **monólito web local** — interface, análise determinística, SQLite e exportações no mesmo projeto.
- **Evidência do briefing:** a entrega obrigatória combina análise de performance e estratégia; o diferencial aceita explicitamente um dashboard interativo ou qualquer ferramenta que transforme dados em decisão recorrente; o resultado deve ser acionável, priorizado e compreensível em cinco minutos.
- **Adequação:** uma aplicação local única entrega importação manual, análise controlada, alertas, drill-down, recomendações, registro de decisões e exportações sem exigir API, nuvem ou múltiplos serviços.
- **Rejeições:** separar frontend e API ou empacotar desktop adiciona infraestrutura sem requisito; planilha e relatório enfraquecem o ciclo diário; ML e agentes generativos aumentam risco, custo e opacidade sem resolver os critérios obrigatórios.
- **Verificação:** o README local e o `main` remoto eram idênticos no blob Git `52b10db595fb2a3f50c8a7cc73573fa53f5db087` no momento da decisão.
- **Limite:** o padrão arquitetural está decidido; framework e bibliotecas só serão escolhidos após a pesquisa obrigatória e reprodução de candidatos.

## I07 — Pesquisa obrigatória e escolha do framework — 2026-09-21 17:25 BRT

- **Decisão registrada:** pesquisar e reproduzir alternativas antes de escolher o framework e somente depois escrever a SPEC. A ordem evita transformar preferência técnica em requisito.
- **Dataset verificado:** o arquivo público possui 52.214 linhas, 27 colunas, cinco plataformas, 22.314 posts patrocinados e 29.900 orgânicos; não contém investimento, receita ou conversão.
- **Frameworks comparados:** Streamlit, Dash e Panel, com verificação de documentação oficial, licença, atividade, releases, testes e relatos de uso.
- **Soluções prontas comparadas:** três repositórios MIT de dashboards sociais/marketing. O mais próximo oferece bons padrões de validação, mas usa outro schema e uma pilha maior que o necessário.
- **Escolha:** Streamlit 1.64 + Pandas + SQLite da biblioteca padrão. É a menor pilha que cobre upload, validação, análise, drill-down, decisão persistida e exportação.
- **Reprodução:** o spike local passou health check, upload automatizado, renderização de KPI/gráfico/tabela, controle de download visível e persistência SQLite. A conclusão do download não foi testada no spike. Evidência salva em `process-log/evidence/004/framework-research/streamlit-proof.png`.
- **Limite deliberado:** nada de API separada, cloud, autenticação, DuckDB, ML ou LLM no MVP. Estado durável vai para SQLite; o CSV bruto permanece fora do banco.
- **Registro de correções durante a pesquisa:** uma variável `path` sobrescreveu o `PATH` especial do zsh; foi renomeada sem modificar arquivos. O primeiro seletor Playwright encontrou a área visual do upload, não o `input`; a verificação foi corrigida para `input[type="file"]` e passou.
- **Documento completo:** `submissions/luis-roquette/research/004-social.md`.

## I08 — SPEC elaborada pela metodologia SDD — 2026-09-21

- **Ordem aplicada:** pesquisa obrigatória → task inicial → análise de negócio → arquitetura → decomposição → julgamentos → SPEC canônica. A implementação não começou.
- **Artefato canônico:** `submissions/luis-roquette/solution/004-social/SPEC.md`; o pacote operacional SDD permanece local em `.specs/` e `.claude/`.
- **Qualidade validada:** pesquisa 4,18/5; análise do codebase 4,20/5; análise de negócio 4,47/5; arquitetura 4,38/5; decomposição 4,28/5.
- **Correção analítica decisiva:** a primeira arquitetura comparava a taxa de um post com a distribuição das medianas por creator. O julgamento detectou unidades observacionais diferentes; o contrato passou a comparar post com distribuição de posts e manteve medianas por creator apenas na análise de patrocínio.
- **Correções de dados:** o CSV não contém `engagement_rate`; a taxa será derivada e versionada. Campos de audiência são rótulos categóricos, não percentuais. O snapshot não contém zeros nas cinco métricas verificadas, limitação que deve ser mostrada.
- **Planejamento:** quatro passos em duas fases, estimativa otimista de 310 minutos de implementação ativa após o planejamento, mais 50 minutos de contingência. O tempo de pesquisa/planejamento não foi medido e não será ocultado.
- **Gate seguinte:** revisão humana da SPEC. Escrever e revisar a SPEC não autoriza implementação, push, PR, publicação ou uso de API paga.

## I09 — Auditoria final da SPEC em loop — 2026-09-21

- **Método:** duas passadas completas e independentes precisavam terminar consecutivamente sem novos achados.
- **Achados corrigidos antes da contagem final:** o spike apenas mostrou o controle de download, sem concluir um download; comparações posteriores agora exigem janelas equivalentes ou normalização diária; 27 colunas menos 16 obrigatórias resultam em 11 opcionais, não 10.
- **Resultado:** passadas finais A e B sem novos achados. Links, caminhos SDD, requisitos, métricas, causalidade, critérios, testes e sincronização entre task e SPEC foram reavaliados.
- **Identidade auditada:** SHA-256 da SPEC `a70a5e7f5dfbf6614cb59c0d72266df6bcbb5ac8bd662f101a212688ff631ea9`.
- **Limite:** o goal de absorção/revisão documental foi atingido; não é prova de runtime e não substitui a revisão humana anterior à implementação.

## I10 — Otimização do plano com `writing-plans` em loop — 2026-09-21

- **Decisão:** aplicar a skill `writing-plans` à SPEC e continuar em cascata até obter duas passadas consecutivas sem melhorias substanciais.
- **Artefato novo:** `submissions/luis-roquette/solution/004-social/IMPLEMENTATION-PLAN.md`, normativo para execução e vinculado pela SPEC.
- **Melhorias incorporadas:** seis tasks TDD; 44 ações rastreáveis; interfaces e arquivos exatos; testes separados por responsabilidade; mapa CK/HR; seis commits pequenos; tempo ativo total limitado a 360 minutos.
- **Erros prevenidos durante o loop:** exemplos não coletáveis pelo `unittest`; placeholders `...`; staging de novos arquivos dentro de `submissions/` ignorada; caminho incorreto da CLI; `sys.path` incorreto no discovery; conflito entre o plano novo e subtarefas SDD antigas; contrato inconsistente entre `load_csv`, `derive_metrics` e `analyze`.
- **Bordas transformadas em regressões:** arquivo acima de 50 MiB, CSV vazio/malformado, cabeçalho duplicado, timezone misturado, zeros, creator repetido, IQR constante, composição desigual de patrocínio, fórmula CSV, rollback e janelas temporais desiguais.
- **Passada limpa 1:** nenhuma melhoria substancial em cobertura, interfaces, comandos, dependências ou gates.
- **Passada limpa 2:** revisão inversa, do handoff à ingestão, sem melhoria substancial; todos os CK-01–11 e HR-01–04 possuem task e prova primária.
- **Goal atingido:** duas passadas consecutivas sem melhorias ou otimizações substanciais apontadas.
- **Limite:** o plano foi otimizado e revisado; implementação, push, PR e deploy continuam não autorizados até a revisão humana.

## I11 — Auditoria final contra o repositório e a stack — 2026-09-21

- **Fonte remota:** `main` do fork em `4aed364d572fabe0f1fff1f0c6f32960b30fe575`; o briefing do Challenge 004 permanece no blob `52b10db595fb2a3f50c8a7cc73573fa53f5db087`, idêntico ao já absorvido.
- **Arquivos relidos:** README raiz, briefing completo, `submission-guide.md`, `CONTRIBUTING.md` e `templates/submission-template.md`.
- **Gap crítico encontrado e corrigido:** o plano previa somente o README técnico. A entrega exige também `submissions/luis-roquette/README.md` baseado no template oficial; Task 6 agora cria e valida ambos.
- **Regras de PR incorporadas:** somente caminhos em `submissions/luis-roquette/`, branch-alvo `submission/luis-roquette`, um PR e título `[Submission] Luis Roquette — Challenge 004`. A publicação continua dependente de autorização explícita.
- **Cobertura do avaliador:** análise obrigatória, estratégia obrigatória, diferencial recorrente, comparação justa, priorização, clareza executiva, process log e formato de submissão estão mapeados a tasks e provas finais no plano.
- **Stack comprovada:** Python 3.14.2, Streamlit 1.64.0, Pandas 2.3.3, SQLite 3.50.4 e `AppTest` importaram juntos; `pip check` não encontrou dependências quebradas.
- **Prova de capacidade-base:** 52.214 linhas lidas em 0,17 s; derivação e agrupamento representativo em 0,01 s; probe total em 0,65 s, cerca de 218 MB de memória máxima e zero swap.
- **Erro operacional registrado:** o primeiro comando `gh api` deixou `?ref=main` sem aspas; o zsh tentou expandir o caractere curinga. A consulta foi repetida com o endpoint entre aspas e passou sem alterar arquivos.
- **Passada final 1:** após incluir o README obrigatório, nova comparação briefing → critérios → tasks → provas terminou sem lacunas adicionais.
- **Passada final 2:** auditoria inversa de stack, tempo, imports, dependências, staging, escopo Git e handoff terminou sem novo gargalo de plano; 360 minutos ativos, zero dependência paga e todos os CK/HR cobertos.
- **Limite de certeza:** o plano cobre integralmente os requisitos conhecidos e a stack não apresenta gargalo-base. Runtime final, achados reais, fluxo de cinco minutos, exports, persistência e setup limpo só podem ser certificados após a implementação e os gates das Tasks 1–6.

## I12 — Autorização de implementação e Feedback Looping — 2026-09-21

- **Decisão humana:** Luis autorizou o início da implementação após a pesquisa, as 24 ondas socráticas, a SPEC, o plano otimizado e a auditoria final. As perguntas, alternativas e respostas das 24 ondas permanecem registradas integralmente em I05; este marco não as resume nem substitui.
- **Metodologia obrigatória:** manter SDD como autoridade e executar em fases cronológicas, uma após a outra, pelo ciclo `Planejamento → Revisão → Execução → Teste`.
- **Feedback Looping:** cada resultado de execução e teste produz um report objetivo para a própria IA. Com base nele, a IA decide entre reforçar/corrigir o trabalho na mesma fase ou avançar para a fase seguinte.
- **Gate de avanço:** uma fase só termina quando seus critérios e testes aplicáveis estiverem validados. Se algum teste falhar, o ciclo reinicia na própria fase; nenhuma falha é transferida silenciosamente para a seguinte.
- **Cascata de loops:** cada passo do plano usa seu loop local; as revisões de fase consolidam os passos concluídos. O Definition of Done recebe um loop final independente de verificação, correção e nova verificação.
- **Reports:** registrar durante a execução, com baixa latência, o plano da fase, a revisão, os comandos realmente executados, resultados, falhas, correções, evidências e julgamento humano. Documentar é parte central da entrega, não um apêndice.
- **Mapeamento SDD:** S1 cobre Tasks 1–2 do plano; S2 cobre Task 3; S3 cobre Tasks 4–5; S4 cobre Task 6. A ordem é estritamente sequencial e preserva a prioridade da análise e da estratégia antes do cockpit.
- **Limites de autorização:** implementação local e commits da branch estão autorizados. APIs pagas, push, PR, merge, deploy, publicação, investimento ou execução externa continuam fora do escopo até autorização explícita.

## I13 — S1/Task 1: fronteira do CSV e métricas — 2026-09-21 19:16 BRT

- **Planejamento:** implementar primeiro a fronteira atômica do CSV e as fórmulas puras, sem Streamlit, SQLite, serviço ou dependência além dos pins já reproduzidos.
- **Revisão:** o contrato preservou subconjuntos válidos, zeros, hash/linhas de origem, faixas de creators e diagnósticos acionáveis; o CSV bruto permaneceu fora do repositório.
- **Execução:** foram criados `requirements.txt`, `analysis.py`, fixtures determinísticas e testes `unittest`. O primeiro run ficou vermelho pelo motivo esperado: `ModuleNotFoundError: analysis`.
- **Feedback loop:** o primeiro run verde parcial teve 13/14 testes aprovados; o único erro era um `creator_id` fornecido duas vezes no builder. A correção foi feita no helper. Warnings do Pandas revelaram dtypes `object`; a normalização passou a criar dtypes numéricos/booleanos reais e o gate foi repetido com warnings tratados como erro.
- **Teste sintético:** `PYTHONWARNINGS=error python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_analysis.py' -v` terminou com 14/14 testes aprovados em 0,515 s.
- **Teste real:** ambiente isolado em `/tmp`, Python 3.14.2, Streamlit 1.64.0 e Pandas 2.3.3; `pip check` sem dependências quebradas. O CSV público de 23.290.049 bytes reconciliou 52.214 linhas e as cinco plataformas.
- **Medição:** validação real em 1,242 s; análise inicial em 10,999 s; total 12,241 s. O caminho cabe no objetivo de decisão em cinco minutos; não foi adicionada otimização preventiva.
- **Limitação:** o teste real encontrou cobertura zero para comparação de patrocínio na janela-padrão recente, estado válido de insuficiência — não uma licença para relaxar os mínimos. Exports e CLI pertencem à S2/Task 3.

## I14 — S1/Task 2: evidência contextual e ações — 2026-09-21 19:21 BRT

- **Planejamento:** manter o núcleo comparável fixo, aplicar os cinco níveis de fallback apenas à audiência e separar alertas post a post, comparação editorial e patrocínio por creator/estrato.
- **Revisão:** a fórmula de força permaneceu separada de impacto; a prioridade usa P95 da plataforma, força e recência ancorada no dataset. Ações são templates determinísticos e nunca executam publicação ou investimento.
- **Execução:** foram implementados benchmarks com exclusão do creator-alvo, quartis por post, fallback explícito, concentração, patrocínio estratificado, comparação editorial de janelas iguais, deduplicação contextual e fila de até três prioridades.
- **Feedback loop 1:** 15/16 testes passaram. A fixture de recomendação agregada tinha 20 creators; excluir um ainda deixava benchmark individual suficiente e o teste não isolava o agregado. A fixture passou a usar cinco creators compartilhados, preservando a elegibilidade editorial e tornando o alerta individual insuficiente.
- **Feedback loop 2:** testes adicionais fixaram a penalidade de concentração (`0,95` balanceado versus `0,05` concentrado), sinais editoriais positivos/negativos/conflitantes, fallback sem remover controles essenciais e agregado sem outlier.
- **Feedback loop 3:** o ambiente isolado, com a resolução atual de NumPy, expôs avisos de unidade temporal genérica em `pd.Timedelta`. O motor passou a usar `datetime.timedelta` da biblioteca padrão; a fixture também deixou de fazer uma concatenação redundante.
- **Gate:** `PYTHONWARNINGS=error python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v` terminou com 17/17 testes aprovados em 1,508 s. `py_compile` e `git diff --check` passaram sem saída.
- **Gate isolado final:** 17/17 testes em 1,470 s, com warnings tratados como erro. O caminho completo do CSV canônico passou em 13,17 s, pico residente de 491.651.072 bytes e zero swap.
- **Julgamento:** a janela real recente não gerou comparação patrocinada elegível; o motor expõe insuficiência e cobertura, sem reduzir 30 posts/cinco creators para fabricar recomendação.
- **Limitação:** este marco prova CK-01–07 no motor e a capacidade real. Exportação, CLI, relatório e evidência oficial continuam corretamente reservados para S2/Task 3.

## I15 — S2/Task 3: análise publicada e exportação segura — 2026-09-21 19:44 BRT

- **Planejamento:** gerar relatório e evidência pelo mesmo resultado do motor, sem recalcular analytics no export; usar HTML estático escapado, CSV neutro a fórmulas e escrita atômica. O relatório deveria responder ao briefing antes de qualquer cockpit.
- **Revisão:** S1 ainda não expunha agregados auditáveis por plataforma, conteúdo, categoria, faixa de creator, audiência e mês. O contrato recebeu `dimensions` e um teste de regressão; thresholds e achados não foram alterados para produzir uma narrativa mais atraente.
- **Primeiro gate vermelho:** `test_exports.py` falhou por ausência esperada de `export_evidence` e `executive_summary`. Após a implementação, 20/21 testes passaram; a projeção priorizava `posts=1` sobre `metric_value=10`. O seletor compartilhado foi corrigido.
- **Feedback loop real:** a primeira exportação válida produziu 414.643 linhas e 184.043.808 bytes, inviável para GitHub. A causa era repetir uma linha completa por vínculo fonte×dimensão. Todos os IDs foram preservados, mas agrupados em uma linha `source_ref` por `evidence_id`, com hash em coluna própria; o artefato caiu para centenas de registros e cerca de 6,5 MB.
- **Execução real:** a CLI processou as 52.214 linhas completas, sem alertas post a post no modo de publicação, e gerou `evidence.csv`/HTML por troca atômica. Uma medição intermediária completou em 13,66 s, pico residente de 462.929.920 bytes e zero swap.
- **Recálculo independente:** Pandas direto, sem chamar o motor, confirmou Bilibili em 19,904630989319% de mediana ERv (10.598 posts); YouTube/mixed/beauty/500.000+ em +0,212889341081 p.p. (114 orgânicos/79 patrocinados; 113/78 creators); e o ranking positivo com força mínima 0,70 em YouTube/mixed/beauty/500.000+ seguido por TikTok/image/tech/100.000–499.999.
- **Estratégia humana:** não transformar diferenças globais mínimas em mudança de mix; testar somente células patrocinadas controladas, revisar a célula negativa prioritária e exigir investimento, custo e conversão antes de qualquer decisão de ROI. Frequência e threshold de creators permanecem hipóteses de teste, não leis do dataset.
- **Proveniência:** fonte SHA-256 `693a2df6e609d1c099f3430d9a5b894b224fe12b2420c0d93e6defe90d15f18e`; método `1.0.0`; comando: `python3 analysis.py /caminho/social_media_dataset.csv --evidence evidence.csv --summary summary.html`.
- **Limites:** o snapshot não contém zeros observados nem dados financeiros; associação patrocinada não é causalidade. A publicação local não autoriza push, PR ou deploy.

## I16 — Revisão P1/S1: endurecimento da fronteira temporal e numérica — 2026-09-21 20:02 BRT

- **Report recebido:** a primeira revisão de P1 atribuiu nota combinada 3,18 e encontrou uma falha alta de CK-01 em S1: `NaT`, offsets incompatíveis e inteiros acima de `int64` podiam atravessar ou derrubar `load_csv`.
- **Planejamento/revisão:** corrigir somente a fronteira de confiança de S1, sem alterar exports/relatório de S2. Política temporal explícita: o arquivo usa datas todas sem offset ou todas com o mesmo offset UTC declarado; nenhuma conversão silenciosa para UTC.
- **Gate vermelho:** duas regressões reproduziram três falhas: `NaT` e `+00:00/-03:00` eram aceitos; `views=2**63` lançava `OverflowError` em vez de retornar diagnóstico.
- **Execução:** `NaT` agora é data inválida; offsets distintos geram `incompatible_timezone_offset`; valores fora de `0..2**63-1` geram `integer_out_of_range`. As séries numéricas validadas alimentam a conversão, evitando um segundo parse divergente.
- **Teste positivo:** duas datas com o mesmo `+02:00` permanecem aceitas como dtype temporal compatível e atravessam `analyze` sem erro.
- **Gate verde:** suíte completa com warnings como erro: 27/27 testes aprovados em 2,332 s. `compileall` e `git diff --check` passaram; não existe lint configurado no repositório.
- **Regressão real:** CSV canônico aprovado com 52.214 linhas e cinco plataformas; validação em 1,270 s e análise em 11,545 s.
- **Resultado:** a importação continua atômica e nenhum dos três valores hostis pode alcançar o motor após um retorno de sucesso.

## I17 — Revisão P1/S1: recência do agregado patrocinado — 2026-09-21 20:07 BRT

- **Novo achado do Feedback Looping:** a evidência de patrocínio não carregava `representative_date`; a fila usava como fallback a mediana de todas as datas da plataforma, inclusive outros estratos.
- **Impacto:** a atualidade e a prioridade podiam ser reduzidas ou elevadas por posts alheios ao braço patrocinado avaliado, contrariando o contrato de recência do agregado.
- **Gate vermelho:** fixture com o estrato patrocinado em 31/01 e todo o restante da plataforma em 01/01 falhou por ausência de `representative_date`.
- **Correção:** cada estrato patrocinado elegível agora registra a mediana de `post_date` dos posts do braço patrocinado. A recomendação exige essa data diretamente; o fallback global por plataforma foi removido da fila agregada.
- **Gate verde:** a regressão confirmou data de evidência/recomendação em 31/01 e recência `1,0`. A suíte completa passou com 28/28 testes em 2,647 s, warnings tratados como erro; `compileall` e `git diff --check` passaram.
- **Regressão real:** CSV canônico aprovado com 52.214 linhas e cinco plataformas; validação em 1,251 s e análise em 11,828 s. A janela-padrão permaneceu sem estrato patrocinado suficiente, como já documentado, sem relaxar o mínimo.
- **Limite:** nenhuma alteração foi feita em `analysis.md`, `evidence.csv` ou no formato de exportação de S2.

## I18 — Revisão P1/S1: universo do P95 e linhas físicas — 2026-09-21 20:23 BRT

- **Gaps do Feedback Looping:** o P95 agregado usava somente comparações elegíveis, embora a SPEC exija todos os grupos não vazios do mesmo tipo/plataforma/janela; diagnósticos de `load_csv` ainda usavam `index+2`, incorreto após células multilinha.
- **Gate vermelho do P95:** um grupo patrocinado grande, sem braço orgânico e portanto inelegível, não alterou o denominador de 3.000 views do grupo elegível.
- **Correção do P95:** os pools de normalização agora são independentes da fila. Editorial usa todos os grupos orgânicos não vazios do núcleo/audiência; patrocínio usa todos os grupos patrocinados não vazios do núcleo. Elegibilidade continua decidindo recomendações, nunca o universo do denominador.
- **Gate vermelho de linhas:** um registro inválido após texto com quebra de linha reportou linha lógica 3, em vez da linha física 4.
- **Correção de linhas:** todos os diagnósticos por registro reutilizam o mapa físico criado pelo `csv.reader`, o mesmo contrato persistido em `source_line`; multiline conta cada linha física.
- **Gates verdes:** a fixture grande aumentou o denominador, reduziu a prioridade e permaneceu fora da fila; o CSV multiline reportou `views` e `post_date` na linha 4. Suíte completa com warnings como erro: 33/33 em 3,565 s; `compileall` e `git diff --check` passaram.
- **CSV real:** 52.214 linhas e cinco plataformas passaram; load em 1,268 s e dois escopos analisados em 26,422 s. A fila recente permaneceu idêntica. A fila histórica manteve os mesmos três IDs e a mesma ordem, mas os scores mudaram de `4,567965e-09 / 3,950288e-11 / 5,079782e-12` para `6,532899e-09 / 5,863452e-11 / 6,169594e-12`.
- **Handoff S2:** como a fila histórica mudou numericamente, `analysis.md`, `evidence.csv` e HTML precisam ser regenerados pelo responsável de S2. Nenhum desses artefatos foi alterado neste fix S1.

## I19 — Revisão P1/S2: contrato único de prioridades — 2026-09-21 20:09 BRT

- **Planejamento:** corrigir os três achados de S2: exportar a fila e seus componentes, gerar o relatório com a ordem do motor corrigido em `81b18fd` e preservar o vínculo compacto entre ID e linha da fonte.
- **Revisão:** `result[recommendations]` será a única fila ordenada; rankings por efeito/força não substituirão a fórmula. O relatório documentará a recência histórica, sem alterar scores para favorecer achados. Não há nova decisão humana sobre patrocínio.
- **Correção de proveniência:** I15 chamou a síntese da IA de “Estratégia humana”; essa atribuição não comprova aprovação humana das células escolhidas. Esta revisão mantém o registro histórico e substitui aquela seleção editorial pela fila determinística do motor.
- **Gate vermelho:** a regressão falhou pela ausência de `analysis_report`; foram acrescentados checks da fila completa, recomposição da prioridade e round-trip de ID opaco/linha física, inclusive campo CSV multilinha.
- **Execução:** a CLI ganhou `--report`; Markdown, HTML e CSV consomem a mesma fila. CSV inclui rank/componentes/valores/P95/ação/janelas; `source_ref` usa arrays JSON paralelos. O mapa passou de índice lógico para linha física inicial do registro.
- **Gate intermediário:** 30/30 testes passaram com warnings como erro em 2,648 s, antes da regeneração dos artefatos reais. O aceite publicado e a repetição real serão verificados a seguir.
- **Gate final:** `PYTHONWARNINGS=error python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v` passou com 31/31 testes em 2,916 s. `python3 -m compileall -q submissions/luis-roquette/solution/004-social` e `git diff --check` passaram.
- **Regeração real:** `PYTHONWARNINGS=error python3 submissions/luis-roquette/solution/004-social/analysis.py /tmp/social-dataset.tEuI48/social_media_dataset.csv --evidence submissions/luis-roquette/solution/004-social/evidence.csv --summary /tmp/ai-master-004-s2-fixed-summary.html --report submissions/luis-roquette/solution/004-social/analysis.md`. Duas execuções finais concluíram em 14,03 s e 14,81 s, até 544.964.608 bytes residentes, zero swap. CSV, Markdown e HTML foram idênticos byte a byte; HTML ficou em `/tmp`.
- **Prova independente:** leitura via `csv.reader.line_num` reconciliou 571.112 vínculos e todos os 52.214 IDs distintos com as linhas físicas da fonte. O export tem 400 registros: 1 summary, 198 evidence, 198 source_ref, 3 recommendation; 10.404.284 bytes. Recência, impacto e score foram recompostos dos campos exportados, e a ordem dos três IDs foi conferida no Markdown/HTML.
- **Fila corrigida:** Bilibili/mixed/tech/100.000–499.999 (`4,567965181674604e-09`); Instagram/text/tech/500.000+ (`3,950287568451419e-11`); YouTube/video/beauty/50.000–99.999 (`5,07978178671046e-12`). A troca resulta da recência por estrato corrigida em S1; não houve seleção por efeito positivo ou força mínima extra. O primeiro item tem força limitada e exige coleta/teste, não investimento.
- **Identidade dos artefatos:** `evidence.csv` SHA-256 `1a64240eb9c195a000d803edb104dda9b96abaa4577f9f94ebcfe10b3dee132f`; `analysis.md` SHA-256 `7c3bd408aa3a03113b4771e6706b8e756afad5434971c5c781e87ada8bc22500`; HTML SHA-256 `b4ee4c560ca2d9a613b2bf39346182741940df1364bad3866824fa9791ddbcc5`.
- **Tempo/limites:** correção retomada às 20:09 e gates concluídos às 20:15 BRT, cerca de 6 minutos; a leitura anterior à interrupção não foi cronometrada. O CSV cresceu para preservar as linhas físicas. Fluxo do cockpit e impressão A4 visual continuam para P2; este gate não declara a interface pronta. Sem API paga, push, PR ou deploy.
- **Staging:** `git add` foi recusado pela regra que ignora `submissions/`; repetido com `git add -f` somente nos seis arquivos autorizados, sem incluir ferramentas locais ou CSV bruto.

## I20 — P1/S2: regeração após correção do P95 — 2026-09-21 20:24 BRT

- **Planejamento/revisão:** atualizar apenas os artefatos publicados a partir do motor `f56260f`, que corrigiu os pools do P95. Preservar a fila única; repetir CLI, reconciliação e gates antes do commit.
- **Execução:** CLI canônica com `--evidence`, `--summary` e `--report`, mesma fonte `/tmp/social-dataset.tEuI48/social_media_dataset.csv`; Markdown/CSV atualizados, HTML em `/tmp/ai-master-004-s2-p95-summary.html`. Repetição independente gerou os três arquivos idênticos byte a byte. Tempos: 16,06 s e 16,36 s; pico residente até 524.566.528 bytes; zero swap.
- **Reconciliação:** preservados os IDs/ordem `sponsorship-16ea8aa86ed6ce32`, `sponsorship-79c48fa46f3b3f67`, `sponsorship-4bd4e28ee9e3b1fc`. Novos scores: `6.532898978367645e-09`, `5.863452075398538e-11`, `6.1695940289632845e-12`; impacto, recência e score recompostos dos campos exportados e conferidos no Markdown/HTML. Leitura independente de linhas físicas confirmou 571.112 vínculos e os 52.214 IDs distintos.
- **Gate:** `PYTHONWARNINGS=error python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v`: 33/33 em 4,048 s. `python3 -m compileall -q submissions/luis-roquette/solution/004-social` e `git diff --check` passaram. Nenhuma alteração adicional de código/teste necessária.
- **Artefatos:** CSV com 400 registros (1 summary, 198 evidence, 198 source_ref, 3 recommendation), 10.404.254 bytes, SHA-256 `c106c38aba57be25ab5c3a053b8f963f56c73bef9d04147051a25c69047e6fa8`; Markdown com 14.154 bytes, SHA-256 `f4286971c544e0de75ead8df3c71397f08f70f584537661f9cfa39ccf9d3df22`; HTML com 3.272 bytes, SHA-256 `4936cda65862bfcbc31cf2440fc83e6b10bfbb0195c6dc9997fa9644fbdbeb12`.
- **Resultado/limite:** regeneração e contratos reconciliados; nenhuma nova preocupação identificada neste escopo. Commit local apenas; sem push, deploy, API paga ou dados brutos na submissão.

## I21 — Revisão P1/S1: fuso do escopo e hipótese de frequência — 2026-09-21 20:42 BRT

- **Feedback Looping:** a segunda revisão marcou 3,84/5 e encontrou dois gaps altos de S1: escopo explícito sem fuso quebrava frames com offset; frequência existia apenas como tópico, sem hipótese mensurável.
- **Gate vermelho:** a fixture `+02:00` falhou ao comparar datas conscientes e ingênuas; as fixtures de uma e duas semanas falharam pela ausência de `frequency_hypothesis`.
- **Correção de fuso:** limites ingênuos do escopo agora são localizados no fuso uniforme aceito pelo dataset, preservando a data civil informada; limites conscientes são convertidos para esse fuso. A regressão com `+02:00` e escopo explícito passou.
- **Contrato de frequência:** cada recomendação proprietária recebe `status`, `value`, `unit`, método, amostra de creators/creator-weeks, semanas completas disponíveis/observadas, janela, ação e limitação causal. Não foi criado item duplicado na fila.
- **Regressões:** duas semanas ISO completas produziram mediana `3,0 posts/creator/semana`, 10 creator-weeks e ação de teste; uma semana produziu `status=collect`, valor nulo e `collect_two_complete_weeks`.
- **Gate verde:** suíte completa com warnings como erro: 35/35 em 4,583 s; `compileall` e `git diff --check` passaram.
- **CSV real:** fonte canônica com 52.214 linhas e cinco plataformas; carga em 1,350 s e duas análises em 28,518 s. A fila recente permaneceu idêntica e pediu coleta, sem semanas completas observadas. A fila histórica manteve IDs, ordem e scores; as três hipóteses patrocinadas tiveram mediana `1,0`, respectivamente 31/46/45 creator-weeks e 27/36/39 semanas observadas, na janela completa de 29/05/2023 a 25/05/2025.
- **Handoff S2:** `analysis.md`, `evidence.csv` e HTML precisam expor os novos campos de frequência e ser regenerados pelo responsável de S2. Nenhum artefato de apresentação/exportação foi alterado neste fix.
- **Limite:** frequência usa combinações creator-semana observadas; ausência de linha não foi convertida em zero, pois a fonte não comprova ausência de publicação fora da coleta. Sem API paga, push, PR ou deploy.

## I22 — Revisão P1/S2: fórmula CSV e frequência publicada — 2026-09-21 20:45 BRT

- **Planejamento:** corrigir os dois achados de S2 da revisão 3,84/5: neutralizar fórmulas após espaços/controles e projetar integralmente `frequency_hypothesis` do motor `04e69db` no CSV, Markdown e HTML.
- **Revisão:** reutilizar o renderizador compartilhado de recomendações; frequência permanece ligada à mesma evidência, sem novo item ou alteração de score. CSV preservará o texto original depois do apóstrofo e o objeto completo de frequência em JSON.
- **Gate vermelho:** duas regressões reproduziram a falta de `frequency_hypothesis` no export e os textos inseguros sem apóstrofo após espaços, LF e controles mistos.
- **Execução/gate parcial:** `_cell` procura o primeiro caractere significativo, ignorando whitespace e controles Unicode, antes de prefixar o texto original. A projeção JSON conserva todos os campos de frequência; o texto compartilhado expõe hipótese/ação, amostra, janela, mínimo e limites. Os oito testes de exportação passaram em 1,183 s, incluindo os estados test/collect e números negativos preservados como números.
- **Gate final:** `PYTHONWARNINGS=error python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v`: 37/37 em 5,118 s. `python3 -m compileall -q submissions/luis-roquette/solution/004-social` e `git diff --check` passaram.
- **Regeração/determinismo:** CLI canônica com `--evidence`, `--summary` e `--report`, fonte `/tmp/social-dataset.tEuI48/social_media_dataset.csv`. Duas execuções concluíram em 16,34 s e 16,76 s, pico residente até 545.964.032 bytes, zero swap. CSV, Markdown e HTML foram idênticos byte a byte; HTML em `/tmp/ai-master-004-s2-frequency-summary.html`.
- **Frequência real independente:** `csv.reader`, `datetime`, `Counter` e `statistics.median`, sem chamar o motor, confirmaram mediana 1,0 nas três recomendações patrocinadas. Bilibili/mixed/tech/100.000–499.999: 31 creator-semanas, 31 creators, 27 semanas observadas; Instagram/text/tech/500.000+: 46/46/36; YouTube/video/beauty/50.000–99.999: 45/45/39. Todas têm 104 semanas completas disponíveis na janela 29/05/2023–25/05/2025, `status=test`, `test_observed_cadence`; ausência de registro não vira zero.
- **Invariantes:** IDs, ordem e scores são idênticos ao export anterior de `04e69db`; frequência complementa as recomendações. Reconciliados novamente 571.112 vínculos e todos os 52.214 IDs com linhas físicas. CSV mantém 400 registros (1 summary, 198 evidence, 198 source_ref, 3 recommendation).
- **Artefatos:** `evidence.csv`: 10.406.247 bytes, SHA-256 `5e1243312190c87c31babe136e6fe753a68b166a0aa68cd5b20b203beca47660`; `analysis.md`: 16.094 bytes, SHA-256 `2b2fb7ded2ba0f55a37d28e7420601b43e281bf0c17d72102c3c512bb5e836aa`; HTML: 4.787 bytes, SHA-256 `772b159b7a531a41f908c4d0708166069bf47558a6d78d929620c878d9b9f36b`.
- **Resultado/limites:** dois achados S2 corrigidos; nenhuma nova preocupação identificada neste escopo. A hipótese é observacional e requer teste humano, não prova de frequência ótima. A impressão A4 e o fluxo do cockpit permanecem no gate P2. Sem API paga, push, PR ou deploy.

## I23 — P1/S2: fronteira final de controles no CSV — 2026-09-21 20:54 BRT

- **Planejamento/revisão:** a terceira revisão marcou 4,36/5, mas identificou controles iniciais sem marcador de fórmula escapando da neutralização. Corrigir `_cell` para tratar controles Unicode Cc/Cf antes do primeiro caractere significativo como perigosos por si só, preservando o texto original e a proteção de fórmulas já existente.
- **Gate vermelho:** a nova regressão reproduziu TAB/CR/LF/NUL/DEL/BOM/zero-width-space sem apóstrofo, com texto comum ou controle isolado, tanto diretamente quanto após espaços. A classificação incorreta de LF+texto como seguro foi removida.
- **Execução:** a varredura prefixa imediatamente o texto original ao encontrar um controle inicial ou marcador `=,+,-,@`; para no primeiro caractere comum. Controles internos após texto comum e números tipados permanecem intactos.
- **Gate verde:** `PYTHONWARNINGS=error python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v`: 38/38 em 4,649 s. `python3 -m compileall -q submissions/luis-roquette/solution/004-social` e `git diff --check` passaram. Regressões verificam os mesmos casos em evidências e decisões.
- **Artefatos:** varredura dos 13.200 campos/400 registros de `evidence.csv` encontrou zero controles iniciais; a nova condição não altera seus bytes. `analysis.md` e CSV foram comparados byte a byte com HEAD e preservam os hashes de I22. Não houve regeração desnecessária, alteração analítica ou de HTML; o teste da CLI manteve a prova de determinismo sintético.
- **Resultado:** achado alto corrigido, sem nova preocupação identificada neste escopo; trabalho de 20:54 a 20:55 BRT. Commit local apenas, sem push, PR ou API paga.

## I24 — A jornada de construção como eixo do diário — 2026-09-21 20:59 BRT

- **Orientação e autoria humana:** Luis reforçou que o papel mais importante dos relatórios, agendas e diários é narrar sua jornada de construção: como o arquiteto projeta, como o engenheiro constrói, como o feedback modifica a construção, por que cada decisão foi tomada e quais evidências a validaram. A IA registra essa orientação com o português revisado, preservando seu sentido e a autoria de Luis.
- **Do projeto à obra:** na Fase 1, as 24 ondas socráticas esclareceram o problema e os limites; a pesquisa sustentou a escolha da arquitetura; SPEC e plano converteram as decisões em contratos verificáveis. Após a autorização humana, S1 construiu o motor analítico e S2 transformou seus resultados em análise, estratégia e evidências auditáveis. Essa sequência explica por que a solução foi construída dessa forma.
- **Como o feedback mudou a construção:** as revisões encontraram entradas que podiam derrubar o motor, divergência entre relatório e fila, lacunas de rastreabilidade, normalização/recência inadequadas, frequência sem hipótese calculada e controles CSV inseguros. Os ciclos de planejamento, revisão, execução e teste devolveram cada problema ao ponto responsável; corrigir significou mudar a construção e provar a mudança, sem ajustar os achados para favorecer a narrativa.
- **Evidência de fechamento:** a revisão final de P1 registrou **4,78/5, zero achados e 38/38 testes aprovados**. Os registros I13–I23 mostram os erros, as decisões corretivas e suas provas; a reconciliação da fonte real, os exports determinísticos e as regressões sustentam o fechamento desta fase. Isso não declara o cockpit ou a entrega inteira concluídos.
- **Regra para as próximas fases:** essa narrativa é obrigatória, além dos comandos e resultados. Cada marco deve ligar intenção, decisão, construção, feedback, mudança e evidência, distinguindo a contribuição de Luis da execução da IA. Documentar a jornada faz parte da entrega, sem inventar retrospectivamente decisões ou experiências.

## I25 — S3/Task 4: memória durável das decisões — 2026-09-21 21:19 BRT

- **Desenho do arquiteto:** Luis definiu que o sistema deve apoiar uma rotina decisória, não apenas exibir números. A arquitetura converteu essa intenção em três registros mínimos e separados: proveniência da importação, decisão humana versionada e observação posterior. O CSV bruto continua transitório e fora do SQLite.
- **Construção do engenheiro:** `storage.py` criou schema versionado, chaves estrangeiras, transações parametrizadas, UUIDs idempotentes e leitura após reinício. Revisões viram novos eventos e herdam o baseline original imutável; aceitar uma recomendação permanece diferente de declarar sua execução.
- **Feedback e correção:** o primeiro gate ficou vermelho pela ausência esperada do módulo. Depois da implementação, 6/9 cenários passaram e três falharam porque o teste selecionava “o último” outcome por UUID, não pelo `event_id`. O seletor do teste foi corrigido para verificar exatamente o evento exercitado; nenhuma regra de negócio foi relaxada.
- **Evidência validada:** `PYTHONWARNINGS=error python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_storage.py' -v` aprovou 9/9 testes em 0,006 s. Foram comprovados schema/FK, idempotência, novo evento, reinício, baseline imutável, rollback, ausência de campos brutos e guards de fonte, janela, escopo, método, amostra, execução e cobertura.
- **Limite honesto:** janelas desiguais preservam medianas e volumes normalizados por dia, mas permanecem pendentes; o sistema não classifica melhora/piora por volume bruto. Este marco valida persistência e temporalidade, não a experiência completa do cockpit.

## I26 — S3/Task 5: do desenho ao cockpit operável — 2026-09-21 21:28 BRT

- **Desenho do arquiteto:** a jornada definida por Luis chegou à interface sem criar um segundo produto analítico. O panorama local compõe o mesmo motor e os mesmos exports: fonte/período, filtros, três prioridades, componentes, ranking, registros de origem, decisão, histórico, observação posterior e downloads. Componentes nativos e uma única página preservam o MVP manual escolhido nas ondas socráticas.
- **Construção do engenheiro:** `app.py` mantém o último resultado válido na sessão, grava somente após formulário explícito e leitura confirmada, usa SQLite fora do worktree e oferece períodos recente, semana ISO, mês, histórico e intervalo explícito com cobertura parcial visível. `test_app.py` exercita estados sem fonte, upload válido/inválido, filtro vazio, componentes, drill-down, decisão/reinício, baseline contextual, outcome posterior e downloads.
- **Feedback loop 1:** o primeiro gate ficou vermelho pela ausência esperada de `app.py`. Após a primeira composição, 5/5 AppTests passaram. A ampliação do contrato encontrou falta de período parcial, ranking e outcome na UI; os três estados foram implementados antes do gate acumulado.
- **Feedback loop 2:** warnings tratados como erro revelaram o uso de `pd.Timedelta` incompatível com a resolução temporal do NumPy atual. A aplicação passou a usar `datetime.timedelta`. O teste também fechou explicitamente sua conexão SQLite; o único aviso remanescente sob `PYTHONWARNINGS=error` vem da limpeza interna de `TemporaryDirectory` do `AppTest` ao encerrar o interpretador, com exit code zero, e não aparece no gate canônico.
- **Feedback loop 3 — correção de integridade:** a revisão posterior ao navegador revelou que o baseline inicial agregava todo o filtro visível, não o contexto exato da recomendação, e que o outcome recebia o escopo histórico. A correção passou a recalcular apenas o agregado contextual no motor puro, preservar seus IDs de origem e comparar os controles efetivamente selecionados no snapshot posterior. A regressão confirma 30 taxas, cinco creators e 30 referências no baseline da fixture.
- **Navegador real:** servidor local em `127.0.0.1`, Chrome e dataset canônico de 23,3 MB. A tela reconciliou hash `693a2df6e609…`, 52.214 linhas, cinco plataformas e, na janela recente, 468 posts, 4.724.954 visualizações e 940.289 interações. Tecla Tab percorreu controles sem bloqueio; uma decisão `accepted` foi confirmada e persistida; HTML e CSV iniciaram download; um CSV inválido mostrou erro sem apagar fonte/histórico; após reiniciar o servidor em outra porta, o histórico reapareceu sem o CSV e pediu o reenvio do hash para o drill-down.
- **Gate validado:** a suite acumulada aprovou **52/52 testes em 10,991 s**. `compileall` e `git diff --check` passaram sem saída. O banco e o dataset usados no navegador ficaram em `/tmp`, fora da submissão; nenhum serviço externo, API paga, push, PR ou deploy foi acionado.
- **Limites e autoria:** a interação automatizada comprova funcionamento técnico, não substitui a validação HR-01 por um gestor humano cronometrado. O cockpit não afirma que a decisão de 2026 foi executada nem usa dados de 2025 como efeito; sem snapshot posterior comparável, o estado correto continua “resultado pendente”.

## I27 — S4/Task 6: da obra validada ao handoff — 2026-09-21 21:36 BRT

- **A jornada construtiva como entrega:** Luis determinou que o diário registrasse não só comandos, mas o percurso de autoria: o arquiteto investiga e desenha; o engenheiro constrói; o feedback revela tensões; a correção altera a obra; a evidência decide se a etapa pode avançar. Essa orientação foi aplicada às 24 ondas, à pesquisa, à SPEC, ao plano e a cada ciclo I13–I26.
- **Planejamento e revisão:** S4 reuniu os contratos finais: dois READMEs, instalação limpa, CLI real, interface em navegador, export A4, screenshot persistente, matriz CK/HR, rubricas e escopo Git. Nenhuma nota poderia compensar requisito obrigatório ausente; HR-01 não seria atribuído a uma automação.
- **Feedback loop de ambiente:** o primeiro gate com `python3` global carregou 48 testes e falhou em `tests/test_app.py` porque Streamlit não estava instalado. A falha voltou ao setup: foi criado `/tmp/ai-master-004-s4.u57Rt2/.venv`, instalados os dois pins e confirmado `pip check` sem dependências quebradas. Não houve mudança de código para esconder uma lacuna do ambiente.
- **Gate limpo:** Python 3.14.2, Pandas 2.3.3, Streamlit 1.64.0 e SQLite 3.50.4. A suite aprovou **52/52** em 9,993 s; execução total 10,52 s, pico residente 207.568.896 bytes e zero swap. `compileall` e `git diff --check` passaram.
- **CSV canônico:** a CLI reproduziu as 52.214 linhas em 23,77 s, pico residente 519.471.104 bytes e zero swap. Os hashes foram `5e124331…` (CSV), `772b159b…` (HTML) e `2b2fb7d…` (Markdown); CSV e Markdown foram idênticos byte a byte aos publicados.
- **A4 e exports:** Chrome imprimiu o resumo em uma página A4 (594,96 × 841,92 pt); causalidade, ausência de ROI e necessidade de custos reais permanecem visíveis. Os testes reconciliam IDs, ordem, componentes, referências e neutralização de fórmulas/controles.
- **Navegador real:** upload do CSV de 23,3 MB mostrou hash `693a2df6e609…`, 52.214 linhas, cinco plataformas e, na janela recente, 468 posts, 4.724.954 views e 940.289 interações. A tela exibiu as três prioridades, impacto, força, atualidade, drill-down e downloads. A captura exata da aba validada foi persistida em `process-log/evidence/004/cockpit-proof.png` (1502×776; SHA-256 `a1945b57366d7fccef79675532240a04cbf5c6c489b50b879404da16e928f1d6`). A validação anterior de decisão, erro atômico e reinício permanece em I26.
- **Atualização após I28:** o refresh de S4 validou 58/58 testes em 9,243 s, CLI canônica em 16,69 s, resumo em uma página A4 e artefatos analíticos idênticos. A prova visual passou a mostrar o histórico corrigido após reinício, com revisão vinculada, outcome `pending / execution_before_decision` e outcome `observed / comparable_after_declared_execution`: PNG 1502×817, SHA-256 `130408568727ed1aac8e21e2283f7c9f39a8caac017e13a43f80a69de8bbcf9c`.
- **Atualização após I31:** o refresh de S4 aprovou 62/62 testes em 17,407 s (18,27 s totais), com warnings como erro, `pip check`, `compileall` e `git diff --check` verdes. A CLI canônica completou em 23,08 s, pico residente de 558.514.176 bytes e zero swap; CSV/Markdown reproduzidos foram idênticos aos publicados, e o HTML permaneceu em uma página A4. A prova visual agora registra o histórico reaberto sem CSV e distingue `observed / comparable_action_not_executed` de `observed / comparable_execution_unknown`, ambos não causais: PNG 1502×817, SHA-256 `362da9813327e6a701ee7ffb3bbb9f37a6c61afd52f833113e33acc3058c2ee1`.
- **Atualização da Redundância Passada 1:** I32–I37 corrigiram controle temporal por mês, overflow, parser, taxa indefinida, interoperabilidade do CSV, frequência mensal, proveniência histórica, documentos canônicos e cobertura visual. A contagem vigente é 74 testes; os hashes publicados são `9eebfa0d…` (CSV) e `a8ab9b96…` (Markdown). A nova prova `cockpit-priorities-proof.png` complementa, sem substituir, a captura focal de outcomes.
- **Atualização da Redundância Passada 2:** I38–I40 elevaram o método a `2.0.0`, fecharam parser/bordas/filtros, publicaram alvo e comparador, responderam audiência condicionada e preservaram snapshot/contrato de observação. O gate vigente é **102/102**; hashes atuais: CSV `017588dfa23f…`, Markdown `c65b42f631c…`, HTML `a90d85f64b20…`. As provas focais de I41 substituem as imagens antigas; HR-01 continua pendente.
- **Atualização da Redundância Passada 3:** I42–I43 elevaram o contrato ativo a `2.1.0`, fecharam datas e inteiros nas bordas, impediram ação forte sobre sinal negativo fraco e criaram a barreira final `export_field`. O gate vigente é **109/109**; hashes atuais: CSV `3a91736cd23c…`, Markdown `8fd5a1e524b7…`, HTML `a5cf43b65d56…`. A prova focal de fonte/qualidade foi renovada em I44; históricos 2.0.0 permanecem apenas como eventos legíveis e incompatíveis. HR-01 continua pendente.
- **Atualização da Redundância Passada 4:** a auditoria encontrou quatro lacunas e, portanto, foi **clean=false**: mediana temporal incorreta no editorial, overflow derivado no limite de 2262, perda da fila além do top 3 e ausência de metadados de período parcial no export. Os commits `d2d5c879`, `92a05dc` e `6499f7c` corrigiram os quatro pontos, elevaram o método a `2.2.0` e o gate a **116/116**. Hashes atuais: CSV `9fb2d4dbc769…`, Markdown `4038018d466e…`, HTML `99a493cbc7cd…`. Esta passada reinicia o contador: **0 de 2 passadas limpas**.
- **Atualização da Redundância Passada 5:** a auditoria encontrou duas lacunas e, portanto, foi **clean=false**: o CSV perdia recomendações além do top 3 e a cronologia de outcomes misturava calendário civil da fonte com UTC. `d2d2dbe` e `56546aa` fecharam fila/baseline integral e calendário `+14:00`/`-12:00`/naive, elevaram o método a `2.3.0` e o gate a **119/119**. O CSV agora contém seis recomendações e 6.703 registros. Esta passada reinicia o contador: **0 de 2 passadas limpas**; I46 preserva os hashes e a prova completa.
- **Redundância Passada 6:** `clean=true`, zero achados e contador **1 de 2 passadas limpas**. A auditoria independente confrontou contrato, código, três probes adversariais, correções recentes, CSV real e imagens sem editar a entrega; I47 preserva a evidência.
- **Atualização da Redundância Passada 7:** `clean=false`, dois achados médios e contador reiniciado em **0 de 2**. `138f803`/`bdeb546` introduziram `analysis_state` (`ready`/`empty_scope`), impediram KPIs/prioridades/downloads em recorte vazio e distinguiram delta ausente de zero medido. Método `2.4.0`, **122/122 testes**; I48 registra correções e gates.
- **Handoff honesto:** automação não é um Gestor de Social Media. HR-01 continua pendente até um operador humano executar upload → explicação → decisão em até cinco minutos. O pacote está tecnicamente reproduzível, mas a Definition of Done integral permanece aberta por esse único gate humano.

### Matriz de aceitação final

| ID | Estado | Evidência |
|---|---|---|
| CK-01 | pass | `test_analysis.py`; fonte real reconciliada em I27 |
| CK-02 | pass | fórmula/zeros/faixas em testes e `analysis.md` |
| CK-03 | pass | fallback, IQR, creators e abstinência em `test_analysis.py` |
| CK-04 | pass | estratos controlados também por mês-calendário, contraparte contemporânea e cobertura explícita; I32–I35 |
| CK-05 | pass | dimensões, audiência, tempo e estado `empty_scope` sem KPI falso; `test_app.py`, `test_exports.py`, I48 |
| CK-06 | pass | prioridade recomposta com mediana temporal real, ordem estável, seis ações exportadas e fila completa decidível; `test_analysis.py`, `test_queue_export.py`, I45–I48 |
| CK-07 | pass | esforço, público, frequência mensal por semanas completas, patrocínio, creators, interrupção e quick wins; I34–I35 |
| CK-08 | pass | decisão/revisão preservam texto, envelope integral, snapshot alvo/comparador, IDs por papel, idempotência, reinício e ação adicional; `test_storage.py`, `test_queue_export.py`, I38–I46 |
| CK-09 | pass | contrato observado reaplica segmento/estatística; calendário da fonte governa cronologia/futuro, replay é SIMULAÇÃO e método antigo é incompatível; I40–I46 |
| CK-10 | pass | HTML normal/adversarial em uma A4; estado vazio e delta ausente preservados; CSV integral reconstruído na ordem `export_field` → `analysis_field` → `history_field`; I39–I48 |
| CK-11 | pass | app local/teclado, fila completa, recorte vazio honesto, sem conta, API ou ação automática; I26–I48 |
| HR-01 | **pending** | exige Gestor de Social Media humano cronometrado |
| HR-02 | pass | `analysis.md` legível sem dashboard e ligado a `evidence.csv` |
| HR-03 | pass | I01–I48 preservam pesquisa, 24 ondas, decisões, falhas, correções e limites |
| HR-04 | pass | setup, provas focais, remoção do diário 001 e auditoria Git restrita à submissão; I37, I45–I48 |

### Rubricas finais

| Rubrica | Nota | Justificativa verificável |
|---|---:|---|
| R-01 — Comparabilidade | 4,8/5 | patrocínio controla cinco dimensões, usa medianas por creator e declara cobertura/abstinência |
| R-02 — Auditabilidade | 5,0/5 | hash, método, IDs, linhas físicas, fórmula, filtros e joins reproduzíveis |
| R-03 — Acionabilidade | 4,5/5 | fila única, dono, janela, métrica, revisão e frequência como hipótese; dados históricos limitam atualidade |
| R-04 — Clareza executiva | 4,7/5 | prioridades no primeiro bloco da UI e resumo A4 de uma página |
| R-05 — Qualidade do diário | 5,0/5 | jornada, decisões humanas, loops, erros, correções, comandos e evidências ligados |

- **Metadados de publicação ainda não executada:** branch-alvo `submission/luis-roquette`; um único PR; título `[Submission] Luis Roquette — Challenge 004`. Push, PR, merge e deploy permanecem fora do escopo autorizado.

## I28 — S3: a revisão confronta a obra com a jornada — 2026-09-21 22:07 BRT; retomada em 22/09 às 06:57 BRT

- **Arquiteto → revisão:** a jornada de Luis exige explicar a evidência antes de decidir e reencontrar o aprendizado depois de fechar a tela. A revisão P2 (3,62/5) encontrou quatro lacunas reais: benchmark omitido na UI, observação de 2025 aceita para decisão de 2026, revisão disponível só na API e outcomes ocultos após reiniciar. As afirmações amplas de I26/I27 não comprovavam esses quatro caminhos; este ciclo as corrige sem reconstruir o passado.
- **Plano → revisão do plano:** reutilizar exclusivamente os objetos do motor para mostrar taxa/volume, distribuição, delta, amostra, contexto/fallback, suficiência, força e referências; carregar a data UTC da decisão na guarda temporal; criar revisão nativa vinculada; mostrar o outcome durável. Não alterar fórmulas, rankings, schema, CSV analítico ou estratégia de S1/S2.
- **Engenheiro → feedback:** `app.py` passou a renderizar as três famílias de evidência, distinguir medianas por creator de quartis dos posts em patrocínio, vincular revisões e expor janelas/execução/medianas/volumes diários no histórico. `storage.py` passou a exigir execução não anterior à decisão e janela posterior tanto à decisão quanto à execução. O teste adversarial agora devolve `pending / execution_before_decision` em vez de `observed`.
- **Correção verificável:** a primeira asserção visual esperava C=0,075; o motor corretamente aplicava também a concentração de creators, produzindo C=0,06. Corrigida a expectativa, sem alterar o motor. A limpeza explícita do diretório temporário global do AppTest eliminou o `ResourceWarning` de encerramento antes relatado em I26; nenhum warning foi silenciado. Os testes incluem editorial, post com fallback, patrocínio, revisão sem CSV e reabertura de outcome pendente. O primeiro gate acumulado passou 57/57 em 16,562 s com `PYTHONWARNINGS=error`.
- **Navegador → novo feedback:** o seletor automatizado falhou antes do envio; o acesso nativo teve timeout. A inspeção revelou o nome acessível completo `upload Upload`, incluindo o ícone; corrigido o seletor, o envio ocorreu. Chrome mostrou taxa 8%, benchmark mediana/Q1/Q3 de 4%, delta 4 p.p., 30 posts/cinco creators nos dois períodos, contexto, suficiência, C=0,06 e referências. Ao trocar a fonte, os componentes de score conservavam valores do upload anterior porque a chave era o ranking: a chave passou a usar `evidence_id`, com regressão conferindo três zeros para a nova fonte insuficiente. Não houve mudança de ranking ou fórmula.
- **Persistência real:** a decisão `5967b3e3-afa2-47fb-95d7-592aab6332cb` e a revisão `3f414a84-5a9f-4932-9e3a-cb93b008715a` foram criadas pela UI. Execução declarada em 14/01/2025 para a decisão de 22/09/2026 produziu `pending / execution_before_decision`. Uma fixture explicitamente sintética de 23–29/09/2026, com execução declarada em 22/09, produziu `observed / comparable_after_declared_execution`. Após parar o processo de `8517` e iniciar outro em `8518` com o mesmo SQLite, Chrome reabriu sem CSV e mostrou original, revisão vinculada e ambos outcomes, suas datas, motivo, medianas 8/9%, delta 1 p.p., 428,5714 views/dia em cada janela e rótulo não causal. Capturas da sessão confirmaram a apresentação; S4 deve renovar o arquivo visual publicado.
- **Gate final e limites:** `PYTHONWARNINGS=error /tmp/ai-master-004-s4.u57Rt2/.venv/bin/python -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v` aprovou **58/58 em 11,098 s**, incluindo dez AppTests, dez testes de storage e três de aceitação. `compileall -q` e `git diff --check` passaram. SQLite e fixtures ficaram em `/tmp`; dados de teste futuros não comprovam resultado real. Outcomes gravados por versões anteriores não são reclassificados retroativamente. HR-01 continua pendente; não houve API paga, push, PR ou deploy.

## I29 — Redundância Necessária — 2026-09-22 07:05 BRT

- **Decisão e autoria humana:** Luis instituiu a etapa **Redundância Necessária**. Depois do primeiro resultado, a construção deve ser reavaliada exaustivamente em loops sucessivos para buscar erros, falhas, lacunas, melhorias e otimizações que ainda possam ser executadas.
- **Goal obrigatório:** somente considerar essa assimilação encerrada após **pelo menos duas passadas consecutivas sem erros, falhas, lacunas, melhorias ou otimizações executáveis**. Um gate verde isolado não encerra a busca.
- **Fluxo:** cada descoberta retorna ao ciclo Planejamento → Revisão → Execução → Teste; após a correção, a contagem de passadas limpas reinicia. Achado não é apenas relatado: quando pertence ao escopo, é implementado e novamente validado.
- **Jornada construtiva:** o arquiteto confronta o projeto com o que foi construído; o engenheiro reforça o ponto fraco; a evidência decide se uma passada foi realmente limpa. Esta é uma etapa posterior à primeira implementação e distinta da revisão P2 atual.

## I30 — Lapidação e melhoria/otimização — 2026-09-22 07:05 BRT

- **Decisão e autoria humana:** Luis instituiu uma segunda etapa, **Lapidação e melhoria/otimização**, executada depois da busca e correção de bugs. Seu objeto é o que já funciona, mas ainda pode ser elevado.
- **Escopo de inspeção:** gargalos, erros residuais, bugs, refinamentos técnicos, layout, design, UI/UX, código e segurança. A etapa não autoriza complexidade especulativa: melhoria precisa ser relevante, demonstrável e compatível com o briefing.
- **Goal obrigatório:** concluir somente após **pelo menos duas passadas consecutivas sem correções ou otimizações relevantes**. Toda descoberta aplicável entra em Feedback Looping, é implementada e retestada; uma alteração reinicia a contagem.
- **Jornada construtiva:** o arquiteto verifica proporção, coerência e experiência; o engenheiro lapida a solução sem quebrar seus contratos; testes e evidências demonstram a elevação. Esta etapa vem depois da Redundância Necessária e não deve ser confundida com a revisão P2 em andamento.

## I31 — S3: os estados humanos precisam conservar seu significado — 2026-09-22 07:18 BRT

- **Arquiteto → feedback:** a segunda revisão P2 aprovou as quatro correções anteriores, mas encontrou duas ambiguidades: texto alterado podia aparecer sob “aceita/rejeitada”, e “não executada” recebia o motivo de execução desconhecida. A nota 4,18/5 não encerrou a fase, pois a primeira lacuna era alta e afetava a autoria da decisão.
- **Planejamento → revisão → execução:** concentrar a regra em `record_decision`: somente `edited` conserva texto editado, obrigatório e sem espaços vazios; `accepted/rejected` gravam texto editado vazio. Os dois formulários também limpam esse campo no evento e explicam seu uso. Histórico e exports escolhem texto pelo estado, inclusive para linhas antigas, sem reescrever o banco. Uma ramificação distingue `comparable_action_not_executed` de `comparable_execution_unknown`; ambas continuam observações não causais. Motor, ranking, schema e artefatos analíticos permaneceram intactos.
- **Teste → evidência:** regressões cobrem decisão inicial e revisão nos três estados, texto indevido em aceita/rejeitada, texto vazio em editada, normalização, reabertura e observações futuras sintéticas `no/unknown`. O gate direcionado `PYTHONWARNINGS=error /tmp/ai-master-004-s4.u57Rt2/.venv/bin/python -m unittest tests.test_storage tests.test_app -v`, executado no diretório da solução, passou **24/24 em 7,368 s**. O gate completo da raiz, com o mesmo ambiente e `unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v`, passou **62/62 em 12,162 s**. `compileall -q` e `git diff --check` passaram.
- **Navegador → persistência:** Chrome em `127.0.0.1:8519` aceitou a ação com texto divergente preenchido e criou revisão rejeitada também com texto divergente; o histórico exibiu somente a ação original. SQLite confirmou `edited_text=''` nos dois eventos. Pela UI, a mesma fixture futura produziu `observed / comparable_action_not_executed` com “Não” e `observed / comparable_execution_unknown` com “Não informado”. Após recarregar sem CSV, os dois motivos e rótulos não causais continuaram visíveis.
- **Handoff e limite:** S4 deve atualizar contagem, matriz CK-08/09 e legenda visual, conforme P2-R03; a contagem vigente é 62. O SQLite isolado ficou em `/tmp/ai-master-004-s3-rereview.sqlite3`; nenhum dado bruto entrou na submissão. Registros antigos permanecem auditáveis, sem migração destrutiva; HR-01 continua pendente e esta correção ainda não equivale às duas passadas limpas das etapas I29/I30. Sem API paga, push, PR ou deploy.

## I32 — Redundância Necessária, passada 1: período, inteiros e CSV — 2026-09-22 08:29 BRT

- **Planejamento → revisão:** a primeira passada encontrou três lacunas de S1: patrocínio sem controle temporal contemporâneo, overflow silencioso em métricas aceitas no limite `int64` e rejeição oculta de texto livre acima de 128 KiB apesar do contrato de 50 MiB.
- **Gates vermelhos:** orgânico apenas em janeiro e patrocinado apenas em fevereiro geraram estrato elegível; `likes=2^63−1` mais um compartilhamento virou interação negativa; `comments_text` com 140.000 caracteres foi rejeitado pelo limite global do `csv.reader`.
- **Execução temporal:** comparação de patrocínio passou a usar `platform + content_type + content_category + follower_band + calendar_month`. Cada mês exige 30 taxas e cinco creators em ambos os braços; lacunas expõem posts, taxas definidas e creators orgânicos/patrocinados. Cobertura conta apenas posts de meses comparáveis.
- **Execução numérica:** interações, somas de grupos, views, exposição por creator e ERv ponderada usam inteiros Python antes da divisão. O limite individual aceito continua `0..2^63−1`, mas combinações e totais já não fazem wrap.
- **Execução do parser:** durante a leitura, o limite de campo é elevado deliberadamente para 50 MiB e sempre restaurado em `finally`; o teto total de 50 MiB continua bloqueado antes do parsing.
- **Teste:** as quatro regressões direcionadas passaram. O gate final da suíte completa com warnings como erro aprovou 65/65 em 14,676 s; `compileall` e `git diff --check` passaram.
- **CSV canônico recente:** 52.214 linhas; carga em 2,287 s e análise em 14,036 s. Não houve estrato patrocinado elegível, cobertura 0 e 141 meses/contextos descobertos. A fila recente preservou os três IDs e scores anteriores.
- **CSV canônico histórico:** com o escopo exato da CLI e alertas de post desativados, análise em 16,923 s; 12 estratos mensais elegíveis, 5.216 descobertos e cobertura de 1,55897%. A fila mudou para `sponsorship-2ff921f93a33ef4e` (abril/2025; 0,424558), `sponsorship-0a403f138f6a6af4` (março/2025; 0,0190582) e `sponsorship-bea2b2758f50181b` (dezembro/2024; 2,93375e-06).
- **CLI real isolada:** a regeneração integral em `/tmp` concluiu em 23,33 s, pico residente de 542.310.400 bytes e zero swap. Produziu 1 resumo, 73 evidências, 73 referências e três recomendações; hashes `f71a26e5…` (CSV), `0dd3c288…` (HTML) e `f6aeeefa…` (Markdown).
- **Feedback do próprio teste:** uma primeira medição histórica habilitou alertas post a post para todas as 52.214 linhas, caminho diferente da CLI e desproporcional; foi interrompida e repetida com `include_post_alerts=False`, conforme o contrato canônico documentado.
- **Handoff S2:** a fila histórica publicada, o Markdown, o CSV e o HTML ficaram semanticamente obsoletos e precisam ser regenerados pelo responsável de S2. Nenhum artefato de apresentação/exportação foi alterado neste ciclo S1.
- **Estado da redundância:** a passada 1 teve achados e reinicia a contagem de passadas limpas. Sem API paga, push, PR ou deploy.

## I33 — Redundância Necessária, passada 1: preservar ausência e tornar evidência legível — 2026-09-22

- **Arquiteto → feedback:** o resumo confundia ausência de denominador com zero de desempenho, e a evidência exigia um aumento oculto do limite do leitor CSV. Ambos impediam a leitura fiel da construção. O plano foi preservar a semântica da taxa e manter rastreabilidade compacta com leitura padrão, antes de publicar a nova comparação mensal de S1 (`798acee`).
- **Gate vermelho → execução:** regressões reproduziram HTML com `0.00%` para views=0 e falha do parser padrão em referências extensas. HTML agora diz “não definida” e explica views=0; o CSV mantém `metric_name=median_erv` com valor vazio. Referências usam blocos de até 500 entradas/32.768 caracteres, com ordem e índice explícitos; IDs excepcionalmente longos são fragmentados e recompostos sem perda.
- **Prova parcial:** 11 testes de exportação passaram em 2,820 s, incluindo zero definido versus taxa indefinida, reconstrução de 20.001 IDs (um com 140 mil caracteres), controles CSV e determinismo. Removidos os aumentos de `field_size_limit` dos testes de aceitação; um novo processo deve ler o artefato publicado sem alterar o padrão.
- **Por que a narrativa mudou:** o motor agora exige braços orgânico/patrocinado no mesmo mês-calendário. O relatório e a evidência devem mostrar os contextos mensais e sua cobertura, sem conservar a antiga fila histórica ou extrapolar meses sem contraparte. A regeneração e o recálculo independente validarão essa mudança antes do commit.
- **Gate completo:** `PYTHONWARNINGS=error /tmp/ai-master-004-s4.u57Rt2/.venv/bin/python -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v` passou **68/68 em 13,599 s**. `compileall -q` com o mesmo Python e `git diff --check` passaram. Os leitores de aceitação não alteram mais o limite global; um processo novo confirmou leitura padrão.
- **Regeração real/determinismo:** CLI canônica com `--evidence`, `--report` e `--summary`; HTML em `/tmp/ai-master-004-s2-monthly-summary.html`. Duas execuções: 18,77 s e 20,16 s, pico residente até 574.210.048 bytes, zero swap. CSV, Markdown e HTML idênticos byte a byte. CSV: 1.165 registros (1 summary, 73 evidence, 1.088 source_ref, 3 recommendation); maior campo 4.500 caracteres. Reconstrução independente confirmou 522.954 vínculos e os 52.214 IDs/linhas físicos.
- **Recálculo independente:** biblioteca padrão, sem importar o motor, reagrupou a fonte por mês/contexto e confirmou 12 estratos elegíveis, 5.216 sem contrapartes suficientes e 814 posts cobertos (1,5589688589%). Para os três prioritários, confirmou medianas por creator/delta, totais, P95 de todos os grupos patrocinados mensais, força, data mediana, recência, prioridade e cadência observada.
- **Nova fila:** YouTube/video/lifestyle/500.000+/2025-04: 38 orgânicos/31 patrocinados, delta +0,0270583791 p.p., prioridade 0,4245579676; RedNote/video/beauty/500.000+/2025-03: 39/30, delta −0,0628742262 p.p., prioridade 0,0190581570; YouTube/video/beauty/500.000+/2024-12: 35/31, delta +0,1112294853 p.p., prioridade 0,0000029337478495. Força limitada nos três contextos mantém a ação de teste/coleta; o sinal negativo não foi removido.
- **Identidade dos artefatos:** CSV 12.960.361 bytes, SHA-256 `52fbd08c27fa6b84ba6816212a7778163e6e88659bc10ae133e587a9706ea11c`; Markdown 16.658 bytes, SHA-256 `f85d9886fad5f60255434523c74af1bcb2b0727dd95a4053f4fc5f881ea7af77`; HTML 4.773 bytes, SHA-256 `0dd3c2880bc90eba3c4ab9e915a3224b608eadfce3d8110fdf309ecbc613ffe9`.
- **Feedback para a próxima passada:** a frequência conserva a janela global de 104 semanas, mesmo quando o contexto é mensal; março/2025 mostra seis semanas com registros, incluindo fronteiras parciais do mês. Encaminhado a S1 para avaliar alinhamento entre cobertura semanal e contexto mensal; S2 não alterou o cálculo para ocultar isso. R1-04/R1-06 estão corrigidos, mas a redundância não foi declarada limpa. Sem push, PR, deploy ou API paga.

## I34 — Redundância Necessária: frequência no mesmo contexto mensal — 2026-09-22 08:49 BRT

- **Feedback → planejamento:** após a correção mensal de patrocínio, S2 mostrou que a hipótese de frequência ainda usava a cobertura global de 104 semanas. A evidência de março contava seis semanas, inclusive as duas fronteiras que atravessavam fevereiro/abril.
- **Gate vermelho:** a mesma evidência de março passou de 20 para 25 creator-semanas apenas porque posts de abril tornaram completa a semana 31/03–06/04. O conteúdo de abril não entrou diretamente no grupo, mas alterou indevidamente sua cobertura temporal.
- **Revisão da regra:** recomendações com `period_month` usam a interseção entre escopo e mês civil; contam somente semanas ISO integralmente contidas nessa interseção. Contextos sem mês preservam a regra anterior de semanas completas no escopo.
- **Execução:** `frequency_hypothesis` agora expõe `coverage_rule` e `period_month`, além de janela, semanas, amostra, valor e ação já existentes. Menos de duas semanas completas observadas continua produzindo coleta, sem sugerir cadência.
- **Regressões:** março suficiente usa 03–30/03, quatro semanas, 20 creator-semanas e mediana 1,0; posts extras de abril não mudam o objeto. Uma fixture com somente uma semana completa observada produz `collect`. Os dois contratos não mensais anteriores continuam verdes.
- **Gate acumulado:** `PYTHONWARNINGS=error ... unittest discover ... -v` aprovou 70/70 em 13,564 s; `compileall` e `git diff --check` passaram.
- **CSV canônico:** 52.214 linhas; carga em 1,385 s e análise histórica em 18,141 s, pico residente de 559.202.304 bytes e zero swap. IDs, ordem, scores, valor 1,0 e status `test` da fila não mudaram.
- **Frequência corrigida:** abril/2025 passou de 104/5/31 para 3 semanas disponíveis/3 observadas/18 creator-semanas, janela 07–27/04; março passou de 104/6/30 para 4/4/27, janela 03–30/03; dezembro/2024 passou de 104/6/31 para 4/4/28, janela 02–29/12.
- **Handoff S2:** `evidence.csv`, `analysis.md` e HTML precisam ser regenerados para substituir as coberturas globais e incluir a regra/mês. Nenhum artefato de apresentação foi alterado por S1.
- **Estado da redundância:** o achado corrigido reinicia novamente a contagem de passadas limpas. Sem API paga, push, PR ou deploy.

## I35 — Redundância Necessária: publicar a frequência mensal corrigida — 2026-09-22 08:51 BRT

- **Arquiteto → revisão:** o feedback de I33 retornou a S1 e corrigiu a cobertura semanal em `c9bdace`. Agora S2 deve tornar essa regra verificável na leitura executiva, preservando IDs, ordem e scores. O objeto JSON já exporta todos os campos; a apresentação precisa nomear mês e regra.
- **Plano de prova:** exigir `period_month` e `coverage_rule` na reconciliação CSV/Markdown/HTML, regenerar os três artefatos, recalcular frequências diretamente da fonte e repetir interoperabilidade, rastreabilidade e gates completos. Proveniência de decisões/outcomes permanece para o ciclo R1-03.
- **Execução → feedback:** as regressões falharam pela ausência do mês na apresentação; o renderizador compartilhado passou a exibir mês e regra. O relatório explica a exclusão de semanas que atravessam meses. A projeção JSON existente preservou automaticamente os dois campos novos, sem nova transformação ou duplicação da hipótese.
- **Gate final:** `PYTHONWARNINGS=error /tmp/ai-master-004-s4.u57Rt2/.venv/bin/python -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v`: **70/70 em 14,019 s**. `compileall -q` no mesmo ambiente e `git diff --check` passaram.
- **Prova independente da frequência:** biblioteca padrão (`calendar`, `Counter`, `statistics.median`) selecionou apenas semanas segunda–domingo inteiramente dentro do mês. Abril/2025: 07–27/04, 3 semanas disponíveis/observadas, 18 creator-semanas e 18 creators; março/2025: 03–30/03, 4/4 semanas, 27/27; dezembro/2024: 02–29/12, 4/4 semanas, 28/28. Os três valores continuam 1,0 e `status=test`; IDs, ordem e scores foram comparados com o commit anterior e permaneceram idênticos.
- **Regeração e leitura:** duas execuções canônicas da CLI em 18,23 s e 19,33 s; pico residente até 568.475.648 bytes, zero swap. Os três artefatos são idênticos byte a byte. O `csv.reader` padrão permaneceu em 131.072 e leu 1.165 registros, maior campo de 4.500 caracteres. Reconstrução integral: 522.954 vínculos e todos os 52.214 IDs/linhas físicos.
- **Artefatos:** CSV 12.960.673 bytes, SHA-256 `9eebfa0d5fce550f257b06fe0bcdac1b818b5e2a18ccc5afe8a9dcc940f36de7`; Markdown 17.122 bytes, SHA-256 `a8ab9b96c1fedaa1851bca4f2e4bbf2cae5829afcc1e8398073d55c66adbf611`; HTML 4.983 bytes, SHA-256 `f0860999b1d23c8f24718214148c1b5487b1f3477872ee31d2aa803fff3426e4`, em `/tmp/ai-master-004-s2-cadence-month-summary.html`.
- **Estado:** regra mensal e evidência publicada reconciliadas; nenhuma preocupação nova neste escopo. R1-03 ainda deve tratar a proveniência de decisões/outcomes; este commit não altera esse fluxo nem declara a passada limpa. Sem push, PR, deploy ou API paga.

## I36 — Redundância Necessária: a história não pertence ao upload ativo — 2026-09-22 09:01 BRT

- **Arquiteto → feedback:** a exigência de Luis de demonstrar a construção encontrou um desvio concreto no download: o histórico persistido era reduzido pela UI e reidentificado com a fonte ativa. R1-03 pediu três fontes independentes e uma revisão vinculada para provar a correção.
- **Planejamento → revisão:** preservar o evento completo no app; exportar proveniência por registro; guardar o escopo de novas observações; manter colunas adicionais condicionais para não mudar o CSV estático sem decisões. Baselines podem conter milhares de referências: também precisam de fragmentação legível pelo parser padrão, sem reintroduzir R1-06.
- **Engenharia:** decisões exportam baseline, fonte/escopo/método, cronologia, revisão, estado e textos; outcomes exportam fonte observada, vínculo com a decisão, declaração de execução, janela, cobertura/comparação, delta e views/dia, explicitamente não causais. Campos históricos grandes usam `history_field` reconstruível; proteção contra fórmulas permanece na célula recomposta.
- **Prova parcial:** 39/39 testes de exportação/storage/AppTest passaram em 9,739 s com `PYTHONWARNINGS=error`. O banco foi fechado e reaberto; a decisão A, revisão de A e observação B foram exportadas enquanto C estava ativa. AppTest capturou os bytes efetivamente passados ao botão CSV e confirmou igualdade após uma nova sessão.
- **Limite assumido:** escopo de outcomes legados não existia no banco; não foi inventado. Exporta vazio quando ausente. Novos outcomes guardam seu próprio escopo no objeto observado, sem migração destrutiva ou modificação do histórico anterior.
- **Gate completo:** `PYTHONWARNINGS=error /tmp/ai-master-004-s4.u57Rt2/.venv/bin/python -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v` passou **74/74 em 16,687 s**; `compileall -q` e `git diff --check` passaram. Nenhum cálculo ou ranking foi alterado.
- **Navegador → evidência:** faltava Playwright no venv; sem instalar dependências, o Chrome via CUA abriu a aplicação isolada em `127.0.0.1:8520`. Fixture sintética em SQLite tinha decisão A, revisão de A e observação B; o upload de 60 linhas tornou ativa C (`7ce745583f37…`). O botão real baixou 27 registros/31.647 bytes, com origens, vínculo, motivo, execução e delta corretos. Após encerrar e reiniciar o processo, o histórico apareceu antes do upload; reenviar C e baixar novamente produziu bytes idênticos. SHA-256 `0bb07b810637f3279cc96b261fc819fe1b69a3bf76c7bd69e74d724ca5cb5af5`; arquivos de prova locais `Downloads/evidencias-decisoes (1).csv` e `(2).csv`, fora do Git.
- **Handoff S4:** README descreve o contrato histórico e sua reconstrução. `evidence.csv`/`analysis.md` publicados não contêm decisões e não precisam de regeneração: hashes de I35 permanecem iguais; comparação do exportador sem histórico com `714e79c` confirmou bytes idênticos. Atualizar a descrição do contrato na SPEC para incluir `history_field`; screenshots não mudam visualmente por R1-03, mas a prova textual deve citar o novo download e o limite dos outcomes legados. R1-03 corrigido; a próxima revisão independente decide se a passada está limpa. Sem push, PR, deploy ou API paga.

## I37 — Redundância Necessária, passada 1: reconciliar contrato, pacote e prova visual — 2026-09-22 09:13 BRT

- **Arquiteto → legado confrontado:** a revisão encontrou documentos canônicos ainda presos ao estado pré-implementação, um diário de pré-início pertencente ao Challenge 001 e uma captura final focada apenas em outcomes. O problema não estava na execução corrente, mas na coerência do pacote que o avaliador recebe.
- **Contrato sem apagar a história:** SPEC e plano receberam adendos datados com o estado implementado. O status original foi preservado como registro histórico; Tasks 1–5 e checks independentes da Task 6 foram marcados concluídos, enquanto o cenário humano de cinco minutos permaneceu aberto. Os READMEs passaram a refletir comparação mensal de patrocínio, frequência no mesmo mês/contexto, `history_field`, proveniência por evento, 74 testes e hashes correntes.
- **Proveniência do pacote:** `process-log/000-pre-inicio.md` descrevia exclusivamente o Challenge 001/churn. Foi removido desta submissão por `git rm`, operação recuperável, sem atribuir retroativamente aquele trabalho ao Challenge 004. Este diário continua sendo a fonte autoritativa da jornada social.
- **Evidência visual:** preservada a captura focal de histórico/outcomes. Uma segunda prova usou o CSV canônico de 23,3 MB no Chrome local: fonte `693a2df6e609…`, 52.214 linhas, período recente com 468 posts, 4.724.954 views e 940.289 interações, primeira prioridade e drill-down abertos, além dos botões reais de HTML/CSV. O artefato é um composto vertical mecânico de dois frames CUA exatos, sem recriar conteúdo: `cockpit-priorities-proof.png`, 2550×1836, SHA-256 `42ea2fb7e6ef13d6c64126467665dddf14bca47933e89da005cf2d588bc7d653`.
- **Limite legado R1-03:** outcomes criados antes da persistência de escopo não recebem contexto inventado; no export, seu escopo permanece vazio. Novos outcomes conservam a própria proveniência e escopo. Esta limitação explícita preserva auditabilidade sem migração destrutiva.
- **Gate limpo e reprodução:** venv novo em `/tmp`, Python 3.14.2, Pandas 2.3.3, Streamlit 1.64.0 e SQLite 3.50.4; `pip check` sem dependências quebradas. A suíte com warnings como erro passou **74/74 em 15,216 s** (15,80 s totais), pico residente de 212.942.848 bytes e zero swap; `compileall` e `git diff --check` passaram. A CLI canônica concluiu em 20,46 s, pico residente de 553.402.368 bytes e zero swap; uma segunda execução produziu os três arquivos idênticos byte a byte. CSV/Markdown coincidiram com os publicados, hashes `9eebfa0d…` e `a8ab9b96…`; HTML `f0860999…` imprimiu em uma página A4 (594,96 × 841,92 pt). O `csv.reader` padrão leu 1.166 linhas físicas sem elevar seu limite.
- **Gates externos:** HR-01 continua pendente até um Gestor de Social Media executar o roteiro em até cinco minutos. A branch local `submission/luis-roquette-004-social` não coincide com a branch obrigatória `submission/luis-roquette`; a integração é gate exclusivo de publicação e não autoriza rename, push ou PR neste ciclo.

## I38 — Redundância Necessária, passada 2: endurecer a fronteira e tornar o motor interativo auditável — 2026-09-22

- **Planejamento → revisão:** sete achados do motor foram reproduzidos antes da correção: dupla interpretação do CSV, bordas temporais, editorial fora dos filtros, guarda de volume por média, IDs sem escopo/versão, varreduras repetidas no histórico completo e perda dos motivos de insuficiência. O ciclo permaneceu em S1; apresentação, armazenamento, publicação e APIs ficaram fora.
- **Fronteira exata:** o `csv.reader` é agora a única interpretação do arquivo. NUL é rejeitado com linha física/coluna; contagens aceitam somente dígitos ASCII, sem sinal, decimal ou expoente, são convertidas por `int` antes do limite int64 e preservam valores acima de 2^53. Datas fora da resolução de nanossegundos falham atomicamente.
- **Tempo e filtros:** escopos usam fim semiaberto no próximo dia, incluindo o último nanossegundo. O helper puro `align_scope_timestamp` preserva a data civil no timezone da fonte e deve ser consumido pela UI em S3. Editorial atual/anterior, alvos e denominadores recebem o mesmo universo filtrado; regressões excluem plataforma e audiência sem recomendação residual nem `KeyError`.
- **Método 2.0.0:** a guarda patrocinada expõe e usa medianas de views/interações por post em ambos os braços. IDs incorporam escopo canônico, referência, estatística e método; seleções equivalentes permanecem estáveis. Eventos `1.0.0` são históricos e não são declarados comparáveis automaticamente ao `2.0.0`.
- **Auditabilidade:** cada recomendação carrega snapshot puro de evidência com alvo, comparador, contexto, estatística, fonte e escopo; alertas preservam post e benchmark, patrocínio preserva ambos os braços e a guarda de volume. Diagnósticos agregam níveis tentados, posts/creators, motivo e amostras. A coluna `engagement_rate` ignorada passa a gerar aviso ao operador.
- **Performance sem trocar o resultado:** pools e índices de benchmark são pré-computados. Quando o início do escopo coincide com o primeiro registro, a ausência de histórico anterior é provada uma vez e os diagnósticos equivalentes são agregados, sem fabricar alertas. Fixture de 5.000 posts terminou abaixo de 10 s e confirmou 25.000 níveis tentados.
- **CSV real:** 52.214 posts. Janela recente interativa: 2.131 alvos, 1.898 alertas e 9.211 níveis tentados em **6,143 s**. Histórico completo interativo: **18,602 s**, 261.070 níveis, zero alertas e três recomendações, contra o probe anterior interrompido após 45,027 s com apenas 4.275 benchmarks iniciados. CLI canônica concluiu em **18,88 s**, pico residente 538.656.768 bytes e zero swap.
- **Impacto canônico:** contextos, ordem, scores, deltas, ações e frequência permaneceram iguais: YouTube/lifestyle/2025-04 (0,4245579676), RedNote/beauty/2025-03 (0,0190581570) e YouTube/beauty/2024-12 (0,0000029337). Os IDs canônicos passaram a `sponsorship-c514404c97b43cfb`, `sponsorship-8ad62bd48c58837c` e `sponsorship-342a5cae1a28de2d`; S2 deve regenerar CSV/Markdown/HTML para publicar método, escopo e identidades novos. Nenhum artefato S2 foi alterado aqui.
- **Feedback do teste:** a primeira repetição encontrou uma asserção nova apontando para o nível errado do objeto; ela foi reconciliada pelo `evidence_id` entre recomendação, snapshot e alerta-fonte. Regressão isolada passou. O gate completo final com warnings como erro aprovou **83/83 em 7,037 s**; `compileall -q` e `git diff --check` passaram. Sem push, PR, deploy ou API paga.

## I39 — Redundância Necessária, passada 2: transformar o cálculo em evidência reconstruível — 2026-09-22

- **Arquitetura → feedback:** o motor já calculava referências e tipos de ação, mas o relatório perdia comparadores e convertia decisões distintas em texto genérico. A revisão também mostrou que marginais de audiência não respondiam à pergunta condicionada. A correção de S2 preserva prioridades e guardas; modifica a ponte entre resultado, leitor e histórico, sem editar app ou storage.
- **Plano → revisão → construção:** explicitar target/comparator em CSV, limitar o resumo ao escopo filtrado, selecionar eventos recentes da mesma fonte e distinguir revisões superadas. Textos operacionais passam a refletir cada ação determinística; o detalhe completo continua no CSV quando a síntese abrevia textos longos. A4 será medido com seis eventos e uma revisão, não presumido pela aparência.
- **Pergunta de audiência:** o resultado passa a comparar rótulos dentro de plataforma/formato/categoria/faixa/mês e condição de patrocínio. Cada braço exige 30 taxas e cinco creators; cobertura e insuficiência são resultados publicáveis. Outros atributos de audiência não são controlados e não se infere persona, causalidade ou vencedor geral. As comparações não entram na fila existente.
- **Primeiro feedback dos testes:** os 14 testes de exportação existentes passaram. Duas fixtures novas reutilizavam content_id; a fronteira as rejeitou corretamente. IDs das fixtures foram corrigidos, sem afrouxar a regra. A regeneração canônica e as provas independentes estão em execução; resultados serão registrados a seguir.
- **Construção validada:** nove regressões novas cobrem alerta alvo/benchmark, estatísticas/fallback, editorial atual/anterior, resumo filtrado, textos de ação renderizados e persistidos, audiência suficiente/insuficiente, diagnósticos e fragmentação. A fixture de audiência suficiente revelou um bool NumPy no contexto; convertido explicitamente para bool nativo antes de serializar, sem mudar o cálculo. Campos extensos usam `analysis_field` com nome qualificado `record_type.campo`, evitando colisão entre uma evidência e sua recomendação. IDs/linhas continuam em blocos separados por papel.
- **Resposta independente à audiência:** auditoria somente com stdlib, sem importar o motor, recompôs 8.749 contextos mensais por dimensão. Idade: 21.644 células, máximo de 19 taxas; gênero: 19.024, máximo 23; localização: 28.638, máximo 12. Nenhuma célula chega a 30 taxas; logo zero pares elegíveis, zero posts cobertos e cobertura 0%. A conclusão agora está no relatório obrigatório e no CSV: não há base para escolher um público sob esses controles, e isso não prova igualdade de desempenho.
- **Fila e reconstrução real:** `tests/verify_real_exports.py /tmp/social-dataset.tEuI48/social_media_dataset.csv evidence.csv` recalculou agrupamentos, P95, força, data representativa, recência e ordem. Confirmou as prioridades `sponsorship-c514404c97b43cfb` = 0,4245579676237061; `sponsorship-8ad62bd48c58837c` = 0,01905815702457926; `sponsorship-342a5cae1a28de2d` = 0,0000029337478494917338. Não houve recalibração nem troca de ordem. O parser padrão leu 6.700 registros: 76 evidências, 1.403 source_ref, 5.216 estratos patrocinados insuficientes, três recomendações, um resumo e uma linha de qualidade. Reconstituiu 679.596 vínculos, cobrindo os 52.214 IDs e suas linhas físicas; maior campo de 4.500 caracteres, limite 131.072 inalterado.
- **Gates e artefatos:** suíte completa com `PYTHONWARNINGS=error` passou **92/92 em 9,563 s**; logging conhecido do AppTest foi mantido, não suprimido. `compileall -q` e `git diff --check` passaram. CLI real final em **20,73 s**, pico RSS **471.760.896 bytes**, zero swap. CSV: 21.821.793 bytes, SHA-256 `017588dfa23f032684066c049f2f5aac4a380e5615de029b80e57a29311b3f1e`; Markdown: 19.557 bytes, `c65b42f631c3532433683b2cf2cbdcea1be74147cfc86cc38146b13f52859fe6`; HTML local: 6.681 bytes, `a90d85f64b20e0d2c556cba2bcfda09378e16f07c4507f25927ad0a5f29f7fb1`. Comando: `python analysis.py /tmp/social-dataset.tEuI48/social_media_dataset.csv --evidence evidence.csv --summary /tmp/ai-master-004-r2-summary.html --report analysis.md`. Repetição da CLI confere os três arquivos byte a byte.
- **Resumo impresso e handoff:** Chrome gerou o resumo normal e a fixture adversarial com seis eventos da mesma fonte, uma revisão, textos de 140 mil caracteres e um evento de outra fonte. Ambos têm **uma página A4**, 594,96 × 841,92 pt; a skill PDF orientou a renderização PNG e inspeção visual, sem corte/sobreposição. Chrome não encerrou automaticamente e os processos isolados foram terminados após timeout; a prova é o PDF produzido e validado por `pdfinfo`/`pdftoppm`, não um exit limpo do navegador. Artefatos locais `/tmp/ai-master-004-r2-adversarial.pdf` e `.png`, hashes `5d09360412b81a7c58a110c05a79a39e24f3f30de11adde8e3cb0750888b7666` e `db97cb783640250fcfe6bb0d7ef2f2577c8bd4f3c87070f179177b76cb63bac1`. S3 deve consumir `current_source_row_ids`/`previous_source_row_ids` no drill-down editorial e na proveniência durável, além de quality/audience; app/storage não foram editados aqui. Sem push, PR, deploy ou API paga.

## I40 — Redundância Necessária, passada 2: preservar a decisão que realmente foi tomada — 2026-09-22

- **Arquiteto → feedback:** a trilha exigida por Luis não terminava em guardar JSON: o baseline precisava representar a evidência vista, e a próxima observação precisava medir o mesmo grupo. R2-03/04/05 mostraram que a UI ainda agregava por conta própria, misturava braços e comparava segmento com panorama. O plano foi consumir snapshots do motor e reaplicar um contrato estatístico explícito, sem duplicar o motor no app.
- **Engenharia:** `decision_baseline` preserva snapshot exato e base de acompanhamento; `observe_evidence` reutiliza agregação segura e controles salvos. Patrocínio mantém alvo patrocinado/comparador orgânico e mediana por creator; editorial exclui patrocínio; post mantém alvo, benchmark e agregado contextual separado. Snapshot inclui força, quartis/fallback, audiência e referências por papel. O novo período substitui a coordenada mensal, mas não os controles do segmento.
- **Cronologia e versão:** storage verifica fim observado e execução contra o relógio real e o timestamp registrado. Futuro permanece pendente com motivo específico; relógio injetável permite testes posteriores verdadeiros. Replay por variável explícita mostra SIMULAÇÃO na UI e nos eventos. Decisões antigas continuam legíveis; método 1.0.0 não gera nova comparação automática com 2.0.0.
- **História independente da fila:** cada decisão mostra seu snapshot sem upload. Com hash correspondente, resolve referências do alvo/comparador no CSV original, mesmo com categoria ativa diferente e decisão fora das prioridades. Datas customizadas usam alinhamento de timezone do motor; quality, níveis/motivos de insuficiência, engagement_rate ignorada, estratos patrocinados sem contraparte e cobertura condicional de audiência chegam à UI.
- **Feedback dos testes:** regressões antigas de futuro passaram a usar relógio controlado depois da janela, e seletores de evidência foram limitados ao próprio expander após a inclusão dos diagnósticos. Uma fixture serializava bool como `False` fora da gramática permitida; corrigida para `FALSE`, sem relaxar a validação. A regressão >int64 encontrou outra borda: Arrow quebrava a tabela antes da decisão. Totais extensos agora aparecem como texto exato apenas nessa tabela; banco/CSV mantêm inteiros. O teste de gravação/reabertura/download acima de int64 passou, junto aos quatro contratos de snapshot/segmento.
- **Gates finais:** `PYTHONWARNINGS=error /tmp/ai-master-004-s4.u57Rt2/.venv/bin/python -m unittest tests.test_decision_evidence tests.test_storage tests.test_app tests.test_exports tests.test_acceptance -q` passou **53/53 em 9,118 s**. A suíte completa `... -m unittest discover -s tests -p 'test_*.py' -q` passou **102/102 em 13,401 s**, já com subcasos que confrontam o relógio real com timestamp enviado, e impedem mudanças de contexto/estatística/unidade. `compileall -q .` com warnings como erro e `git diff --check` passaram. CWD dos comandos: `submissions/luis-roquette/solution/004-social`.
- **Chrome real:** aplicação isolada `127.0.0.1:8521`, banco temporário `ai-master-004-r2-s3-history.sqlite3`. Replay explícito em 14/01/2025 registrou decisão Tech com snapshot 8%/comparador 4%. Remover Tech da categoria ativa deixou somente Beauty na fila; o histórico continuou resolvendo 60 referências Tech originais. Após reiniciar em 22/01, a fixture Tech=9%/Beauty=99% com somente Beauty ativa produziu observação Tech=9%, delta +1 p.p., 30 taxas/cinco creators, rotulada SIMULAÇÃO. Reiniciar sem override preservou o rótulo do evento e bloqueou janela 01–07/10/2026 como `pending / observation_in_future` no relógio real de 22/09.
- **Download e persistência:** dois downloads reais, antes/depois de outro reinício, produziram **39 registros/95.680 bytes idênticos**, SHA-256 `2b20a1c923ede11742adef242b7dc8b56002bdcd922c3f94191c287aad3ce7fb`. Arquivos locais `Downloads/evidencias-decisoes (4).csv` e `(5).csv`; o parser padrão confirmou snapshot Tech, mediana observada 9, delta 1, simulação da observação retrospectiva e pendência da futura. Inspeção visual mostrou os dois estados e o aviso de simulação, sem substituir a prova por sucesso de clique.
- **Artefatos publicados:** CLI real com `--evidence`, `--summary`, `--report` em `/tmp/ai-master-004-r2-s3.4wG9nP` reproduziu CSV/Markdown byte a byte e o mesmo hash HTML `a90d85f64b20e0d2c556cba2bcfda09378e16f07c4507f25927ad0a5f29f7fb1`. Não há mudança na fila nem regeneração necessária dos artefatos estáticos de I39.
- **Handoff S4 e limites:** atualizar SPEC/matriz para snapshot/contrato, guardas de futuro, método incompatível e histórico independente da fila; atualizar screenshots de qualidade/contexto e substituir a antiga prova não rotulada de futuro como observado. Fixtures continuam somente em `/tmp`, não no Git; testes não substituem HR-01. Eventos legados sem snapshot permanecem legíveis, sem comparador inventado. A revisão independente seguinte decide a contagem de passadas limpas. Sem push, PR, deploy ou API paga.

## I41 — Redundância Necessária, passada 2: reconciliar contrato e prova final — 2026-09-22

- **Arquiteto → revisão:** o handoff ainda dizia 74 testes, apontava para I37 e usava uma captura antiga em que uma janela futura aparecia como `observed`. A obra funcional estava correta após I38–I40, mas contrato e prova pública não acompanhavam a construção.
- **Correção documental:** SPEC, plano e READMEs passaram a declarar `METHOD_VERSION = "2.0.0"`, 102 testes, hashes de I39, snapshot alvo/comparador e guardas do relógio. O histórico `1.0.0` permanece legível, porém incompatível para nova comparação automática (`pending / method_mismatch`). A matriz I27 foi ligada a I38–I41 sem reescrever decisões anteriores.
- **Prova focal, sem composto:** o Chrome recebeu novamente o CSV canônico de 23,3 MB e mostrou fonte `693a2df6e609…`, 52.214 linhas, período, método 2.0.0, qualidade, insuficiência de audiência, primeira prioridade, taxa-alvo, benchmark, quartis e amostras. Cinco capturas CUA exatas foram persistidas separadamente: fonte/qualidade `c2444f7c70a8…`; audiência/prioridade `0d5a4616a9ba…`; contexto `9109a48feeb2…`; snapshot histórico `e9264a8264ea…`; outcomes `1d634f6c7174…`. Todas têm 2550×877 px.
- **História e cronologia:** após reinício e sem CSV ativo, a decisão aceita e seu escopo salvo continuam visíveis. A prova de outcomes mostra lado a lado o replay observado com o aviso **SIMULAÇÃO / REPLAY RETROSPECTIVO** e a janela 01–07/10/2026 como `pending / observation_in_future`; nenhuma evidência futura é apresentada como produção observada.
- **Autoria preservada:** a Passada 2 segue a regra de Luis: o arquiteto confronta o contrato, o engenheiro corrige, o feedback exige nova prova e o diário registra inclusive o erro visual removido. A conclusão técnica depende dos gates limpos abaixo; HR-01 continua reservado ao Gestor de Social Media humano.
- **Gate limpo S4:** venv novo `/tmp/ai-master-004-s4-refresh.zJWJLH`, Python 3.14.2, `pip check` sem dependências quebradas. Suíte com `PYTHONWARNINGS=error`: **102/102 em 11,717 s** (20,40 s total), pico RSS 235.798.528 bytes e zero swap. Duas CLIs reais: 18,88 s e 19,51 s; CSV/Markdown/HTML idênticos byte a byte entre si e aos artefatos publicados aplicáveis. Verificador independente: 6.700 registros, 679.596 vínculos, 52.214 IDs, maior campo 4.500 e limite padrão 131.072. PDFs normal e adversarial: uma página A4, 594,96 × 841,92 pt; o texto extraído preservou título, prioridades, limites, revisão e omissão explícita da outra fonte.

## I42 — Redundância Necessária, passada 3: datas e ações determinísticas nas bordas — 2026-09-22

- **Planejamento → gate vermelho:** quatro probes reproduziram o contrato quebrado: `today`/`now` dependiam do relógio; timezone desconhecido era descartado; inteiros com mais de 4.300 dígitos escapavam em exceção; datas válidas para nanossegundos quebravam janelas derivadas; post negativo com C=0,06 recebia orientação de evitar repetição.
- **Fronteira temporal:** a importação aceita somente ISO-8601 explícito ou o legado `%m/%d/%y %I:%M %p`. Nanosegundos e offsets válidos são preservados; datas relativas, zonas desconhecidas e gramática inferida geram diagnóstico de linha/coluna. A faixa operacional declarada é 1971-01-01 a 2262-04-10, com margem representável para próximo dia, visão padrão, período anterior e fallbacks de 90/365 dias.
- **Inteiros sem limite global:** zeros à esquerda são removidos apenas para a comparação lexical com int64. Cinco mil zeros viram zero exato; cinco mil noves retornam `integer_out_of_range`, sem chamar `int()` antes da prova nem alterar `sys.set_int_max_str_digits`.
- **Guarda de ação:** força é avaliada antes da direção. Post negativo com `C<0,40` agora usa `test/creator` e texto de coleta em escala limitada; não usa `review/stop`. Um negativo com `C≥0,40` continua `review/stop`. Export e persistência foram reconciliados pela mesma ação do motor, sem regra duplicada.
- **Versão:** a mudança de gramática/faixa e guarda de ação eleva o método para `2.1.0`. Eventos `1.0.0` e `2.0.0` permanecem legíveis, mas não são comparáveis automaticamente ao método novo. IDs canônicos mudam por versão; estatísticas e ordem não foram recalibradas.
- **Feedback looping:** a primeira implementação restringiu também a margem derivada da janela padrão e falhou no limite inferior aceito. A validação permaneceu na fonte; cálculos internos usam a margem segura. Cinco regressões específicas passaram em 0,203 s.
- **CSV real:** 52.214 linhas carregadas em 0,603 s. Recente interativo: 2.131 posts, 1.898 alertas e 9.211 níveis em 6,556 s. Histórico interativo: 52.214 posts, zero alertas e 261.070 níveis em 18,367 s; pico do processo combinado 510.115.840 bytes, zero swap. A CLI canônica concluiu em 20,88 s.
- **Impacto canônico/handoff S2:** contextos, ordem, scores e ações continuam YouTube/lifestyle/2025-04 (0,4245579676), RedNote/beauty/2025-03 (0,0190581570) e YouTube/beauty/2024-12 (0,0000029337). IDs `2.1.0`: `sponsorship-93a467ffd9919121`, `sponsorship-36711ab0619490d7`, `sponsorship-1859a20bddf0e6f8`. S2 deve regenerar CSV/Markdown/HTML; nenhum artefato gerado foi alterado por S1.
- **Gate acumulado:** após ampliar a prova para offsets `Z`/`-0300`, rejeição de `+15:00`, zeros extensos e limite global intacto, a suíte completa final com warnings como erro aprovou **106/106 em 12,183 s**. `compileall -q` e `git diff --check` passaram. Sem push, PR, deploy ou API paga.

## I43 — Redundância Necessária, passada 3: fechar todos os caminhos de saída — 2026-09-22

- **Arquitetura → revisão:** a proteção existia, mas uma linha de resumo e os rótulos de dimensão escapavam dela. O feedback mudou a correção: não basta adicionar outro caso especial; a exportação precisa de uma barreira final que alcance todo campo, inclusive metadados de fragmentos, enquanto o resumo impresso precisa abreviar todos os textos livres.
- **Construção sem mudar achados:** summary/source_ref passam pela projeção limitada. Uma barreira final preserva linhas normais byte a byte e usa `export_field` somente se ainda houver campo extenso, ligado ao ordinal determinístico da linha-base. A reconstrução dessa camada antecede analysis_field/history_field e preserva a proteção contra fórmulas. Rótulos de dimensão e IDs/cadência/fonte recebem limites visíveis com reticências; valores integrais permanecem no CSV.
- **Teste como feedback:** a primeira fixture de impressão não garantia que a dimensão longa entrasse nas cinco evidências selecionadas; a asserção também contava uma letra a mais. A fixture foi reforçada: seis campos reais da fonte têm 140 mil caracteres adicionais, além das seis decisões longas e revisão. A prova terá parser padrão, round-trip exato e impressão real; nenhuma regra de entrada foi relaxada.
- **Fechamento das regressões:** a contagem manual do prefixo da fixture ainda estava incorreta; a asserção passou a exigir os primeiros 79 caracteres mais reticências, exatamente 80 caracteres visíveis. Os 26 testes de reconstrução/export passaram em 2,454 s. Três regressões novas provam o scope integral da primeira summary, todos os campos da barreira final (incluindo metadados de fragmentos) e rótulos de fonte abreviados com íntegra no CSV; limite padrão 131.072 permanece intacto. A suíte completa `PYTHONWARNINGS=error /tmp/ai-master-004-s4.u57Rt2/.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -q` passou **109/109 em 18,621 s**. `compileall -q .` com warnings como erro e `git diff --check` passaram; logging do AppTest foi preservado. CWD: `submissions/luis-roquette/solution/004-social`.
- **Compatibilidade e regeneração:** o exportador anterior de `a1d2140` recebeu o mesmo resultado 2.1.0 e produziu exatamente os mesmos bytes do novo exportador no caso canônico; a barreira não altera células normais. CLI real em **18,83 s**, RSS **463.699.968 bytes**, zero swap; repetição da CLI confirmou CSV/Markdown/HTML idênticos. Comando: `python analysis.py /tmp/social-dataset.tEuI48/social_media_dataset.csv --evidence evidence.csv --summary /tmp/ai-master-004-r3-summary.html --report analysis.md`. CSV: 21.821.804 bytes, SHA-256 `3a91736cd23c52b2c1603f2ebb0d0324195a41997b6f15c331ad1f042626394b`; Markdown: 19.947 bytes, `8fd5a1e524b798294553cfc4eb5e538001c258623b54cd6adf42281e224deba7`; HTML: 6.681 bytes, `a5cf43b65d561d13f65709da7334d1ca69c26b3536f2b7a4d704f3b479691f9b`.
- **Achados preservados:** comparação com a fila publicada anterior confirmou scores, ações `test` e textos intactos; somente IDs/método mudaram para 2.1.0. O verificador independente recompôs `sponsorship-93a467ffd9919121` = 0,4245579676237061, `sponsorship-36711ab0619490d7` = 0,01905815702457926 e `sponsorship-1859a20bddf0e6f8` = 0,0000029337478494917338. Reconstruiu os mesmos 52.214 IDs/linhas, 679.596 vínculos, 6.700 registros, maior campo canônico 4.500 caracteres. Audiência continua sem célula elegível: 8.749 estratos por dimensão, 21.644/19.024/28.638 células e máximos de 19/23/12 taxas para idade/gênero/localização; cobertura 0%, não ausência demonstrada de diferença.
- **A4 medido, não presumido:** novo gate reproduzível `python tests/verify_print.py /tmp/ai-master-004-r3-summary.html /tmp/ai-master-004-r3-a4` exige Chrome e Poppler, sem instalar dependências. Normal e adversarial produziram **uma página A4** cada; extração confirmou revisão, omissão da outra fonte, reticências e limites de ROI/causalidade. Pela skill PDF, os dois PNGs foram inspecionados: sem corte/sobreposição, limitações essenciais visíveis. Chrome não encerrou sozinho após imprimir; cada processo isolado foi encerrado após timeout de 15 s, explicitamente reportado pelo gate. A prova usa PDFs novos validados, não saída limpa do navegador. Hashes PDF normal/adversarial: `844a9ede624e4c49726ec90374f1b9bb58d9c5fd8166001e3ff0f34dbd830556` / `af87bbdc724ba1f508cdba66abc3745fbafb5303a4e7f838ed7b4aaa24169385`.
- **Handoff e limites:** R3-04/R3-05 corrigidos em S2; app/storage não foram editados. S3 conserva a API pública de exportação e recebe a barreira automaticamente; pode conferir o download com filtro longo. S4 deve reconciliar método 2.1.0, 109 testes, hashes e protocolo `export_field` nos documentos/provas do pacote. CSV bruto, fixtures HTML/PDF e perfis temporários ficam fora do Git. Sem push, PR, deploy ou API paga; a próxima auditoria independente decide a passada limpa.

## I44 — Redundância Necessária, passada 3: reconciliar contrato, prova e handoff — 2026-09-22

- **Arquiteto → revisão:** a construção já operava em `METHOD_VERSION = "2.1.0"`, mas SPEC, plano, READMEs, matriz I27 e a captura de fonte ainda descreviam 2.0.0/102 testes. A lacuna era de contrato público e evidência, não de resultado analítico.
- **Engenheiro → correção:** os documentos passaram a declarar datas ISO-8601 ou legado explícito, faixa 1971-01-01 a 2262-04-10, inteiros provados lexicalmente contra `int64`, sinal negativo fraco direcionado a coleta/teste e reconstrução `export_field` antes de `analysis_field`/`history_field`. Os adendos I41–I43 foram preservados como história; não houve reescrita retroativa.
- **Prova visual fiel:** o Chrome recebeu novamente o CSV canônico real e mostrou fonte `693a2df6e609…`, 52.214 linhas, período, cobertura e método 2.1.0. A captura exata da aba, com qualidade expandida, foi persistida em `cockpit-source-quality-proof.png` (2550×918 px; SHA-256 `8c77eb840566a8f561fb5be70898604da803edd5fe9467fdee766c2207da2053`). As provas de snapshot/outcomes foram mantidas porque sua semântica não mudou; as legendas agora as identificam como eventos históricos 2.0.0, legíveis porém incompatíveis com nova comparação 2.1.0.
- **Feedback e limite humano:** esta passagem registra a jornada definida por Luis: o arquiteto compara intenção e obra, o engenheiro corrige a divergência, o feedback exige evidência renovada e o diário preserva a autoria da correção. HR-01 continua reservado ao Gestor de Social Media humano cronometrado; publicação na branch exigida continua sendo gate externo.
- **Gate limpo S4:** venv novo `/tmp/ai-master-004-s4-r3.7bTO7E`, Python 3.14.2 e `pip check` sem dependências quebradas. A suíte com `PYTHONWARNINGS=error` passou **109/109 em 12,539 s** (21,00 s total), pico RSS 348.815.360 bytes e zero swap. Duas CLIs reais (18,91 s e 21,21 s) produziram CSV/Markdown/HTML idênticos byte a byte; CSV e Markdown também coincidiram com os publicados. Hashes: CSV `3a91736cd23c…`, Markdown `8fd5a1e524b7…`, HTML `a5cf43b65d56…`.
- **Reconstrução, impressão e escopo:** o leitor padrão independente recompôs 6.700 registros, 679.596 vínculos e 52.214 IDs, com maior campo canônico de 4.500 e limite padrão 131.072. `tests/verify_print.py` gerou normal/adversarial em uma página A4, visualmente sem corte; hashes PDF `fc2c44b7caff…` / `b215c3dea556…`. `compileall`, `git diff --check`, 30 links locais, cinco PNGs e a auditoria de arquivos proibidos passaram. O branch local ainda é `submission/luis-roquette-004-social`; publicar em `submission/luis-roquette` exige autorização externa.

## I45 — Redundância Necessária, passada 4: quatro achados corrigidos — 2026-09-22

- **Estado da passada:** `clean=false`, quatro achados médios e contador reiniciado em **0 de 2 passadas limpas**. O relatório independente em `.specs/scratchpad/redundancy-pass-4-20260922-1212.md` confrontou contrato, código, exports, cinco imagens e probes adversariais; HR-01 e branch de publicação permaneceram corretamente fora da contagem.
- **R4-01 — mediana temporal:** 100 posts editoriais divididos em dois instantes centrais expuseram o uso do elemento superior: 14/01, recência 1,0 e score 95, em vez da mediana real 11/01, recência 0,742997 e score 70,584729. `d2d5c879` passou a usar a mediana temporal real e elevou `METHOD_VERSION` a `2.2.0`; os IDs canônicos agora são `sponsorship-9bc1a9a0add291a4`, `sponsorship-311c45798ab57cdf` e `sponsorship-d2421615bf5d4277`.
- **R4-02 — calendário civil:** 60 posts elegíveis em 09/04/2262 derrubavam a frequência ao calcular a segunda-feira seguinte fora do tipo. A correção usa `date` para semana/mês e faz clipping antes de converter para `Timestamp`; post, editorial, patrocínio e UI semanal/mensal nos extremos aceitos têm regressões.
- **R4-03 — fila completa e probe UI:** quatro contextos elegíveis produziam somente três opções/expanders na UI. A primeira tentativa do probe serializou `False`, que o contrato corretamente rejeitou; repetida com `FALSE`, confirmou a perda. `d2d5c879` preservou `all_recommendations` e snapshots; `92a05dc` adicionou “Outras ações elegíveis”, drill-down e decisão da quarta ação sem alterar filtros ou scores. O CSV canônico recente também apresentou quatro ações, comprovadas no Chrome real.
- **R4-04 — período parcial:** mês janeiro sobre fonte 01–14 mostrava “cobertura parcial” na UI, mas CSV/HTML/Markdown perdiam modo e janela solicitada. `6499f7c` propagou `period_mode`, `requested_start`, `requested_end` e `partial_period`; semana/mês parciais e intervalo explícito completo fazem round-trip, enquanto eventos legados não recebem metadado inventado.
- **Jornada construtiva:** o arquiteto encontrou divergências entre o contrato e uma obra já verde; o engenheiro corrigiu cada camada responsável; o feedback do probe UI distinguiu erro da fixture de erro do produto; testes, exports e Chrome decidiram o fechamento técnico. Como houve correções, esta não é uma passada limpa e não avança o goal de redundância.
- **Provas visuais renovadas:** fonte/qualidade exibe método 2.2.0 (`f557df55016f…`); a quarta ação mostra seletor, componentes e evidência completa (`14f75f4f2128…`); contexto prioritário usa o novo ID 2.2.0 (`f573b65cfe75…`). As três têm 2550×918 px. Snapshot/outcomes 2.0.0 foram preservados como história legível, explicitamente incompatível com 2.2.0.
- **Gate limpo pós-correção:** venv novo `/tmp/ai-master-004-s4-r4.FOaW4r`, Python 3.14.2 e `pip check` sem dependências quebradas. `PYTHONWARNINGS=error` aprovou **116/116 em 14,704 s** (24,10 s total), pico RSS 379.600.896 bytes e zero swap; mensagens conhecidas de `ScriptRunContext` foram logging, não warnings Python suprimidos. `compileall` e `git diff --check` passaram.
- **Determinismo e artefatos:** duas CLIs reais (22,98 s e 18,99 s; pico RSS até 566.116.352 bytes; zero swap) produziram os três arquivos idênticos byte a byte, e CSV/Markdown coincidiram com os publicados. CSV: 21.821.815 bytes, `9fb2d4dbc769…`; Markdown: 19.947 bytes, `4038018d466e…`; HTML: 6.681 bytes, `99a493cbc7cd…`.
- **Reconstrução, impressão e escopo:** o leitor padrão independente recompôs 6.700 registros, 679.596 vínculos e 52.214 IDs; maior campo 4.500, limite padrão 131.072. `verify_print.py` produziu normal/adversarial em uma página A4, inspecionados sem corte; hashes PDF `59bbd7c1b361…` / `1c77b4b744f2…`, incluindo período parcial no adversarial. Trinta links locais, cinco PNGs, escopo Git e arquivos proibidos passaram. HR-01 humano e publicação em `submission/luis-roquette` continuam externos; sem push, PR, deploy ou API paga.

## I46 — Redundância Necessária, passada 5: fila integral e calendário da fonte — 2026-09-22

- **Estado da passada:** `clean=false`, dois achados médios e contador reiniciado em **0 de 2 passadas limpas**. O relatório independente `.specs/scratchpad/redundancy-pass-5-20260922-124700.md` encontrou perda da cauda da fila no CSV/baseline e mistura de datas civis da fonte com UTC nos outcomes. HR-01 e branch de publicação permanecem gates externos, não achados técnicos.
- **R5-01 — fila e baseline integrais:** `d2d2dbe` faz o CSV percorrer `all_recommendations`, com fallback legado, e preserva no baseline rank, score, normalização, componentes, frequência e ação. O top 3 continua sendo a síntese HTML/Markdown; as seis ações auditáveis ficam na mesma ordem do CSV e da UI. O artefato canônico agora tem 6 recomendações e 6.703 registros.
- **R5-02 — calendário civil da fonte:** `56546aa` projeta decisão, registro, relógio, execução e observação no offset declarado em `target_start`/`target_end_exclusive`. Regressões cobrem `+14:00`, `-12:00`, fonte naive, futuro e reabertura. Sem offset, a parede civil é preservada; nenhum offset é inventado. Eventos históricos já persistidos não são retroclassificados.
- **Jornada construtiva:** o arquiteto confrontou novamente a promessa de auditabilidade com o pacote exportado; o engenheiro devolveu cada lacuna à camada responsável; o feedback confirmou fila e cronologia com probes adversariais; a evidência decidiu o fechamento técnico. Como houve correções, a Passada 5 não avança o goal de redundância.
- **Gate limpo pós-correção:** venv novo `/tmp/ai-master-004-s4-r5.BG4UrK`, Python 3.14.2 e `pip check` sem dependências quebradas. `PYTHONWARNINGS=error` aprovou **119/119 em 16,000 s** (23,69 s total), pico RSS 379.863.040 bytes e zero swap. `compileall` e `git diff --check` passaram; as mensagens conhecidas de `ScriptRunContext` são logging do AppTest, não warnings Python silenciados.
- **Determinismo e artefatos:** duas CLIs reais terminaram em 19,23 s e 18,63 s, pico RSS até 553.877.504 bytes e zero swap. CSV/Markdown/HTML foram idênticos byte a byte entre execuções; CSV e Markdown coincidiram com os publicados. Hashes: CSV `7e94c3352f596bb912ccad74346b4aa3796e7290a748d36ac06300653f80e2fc`, Markdown `10e043722772a349676194febcbed1a8a4b9bed2864e0c60da1352ea47831fe0`, HTML `8098fa88096e252782636a548b29b5a9b2e748f3ad3179fa5f3833efa36cacef`.
- **Reconstrução, A4 e prova visual:** o leitor padrão independente recompôs 6.703 registros, 679.596 vínculos e 52.214 IDs; maior campo 4.500 e limite 131.072. Normal/adversarial permaneceram em uma página A4, visualmente sem corte, hashes PDF `d67573f574ab…` / `a65934ea2637…`. Chrome real recebeu o CSV canônico e renovou três capturas 2550×918: fonte/qualidade 2.3.0 `6a093fe50c97…`, quarta ação `c125589d2243…` e contexto prioritário `339a3a564c32…`. Snapshot/outcomes 2.0.0 permanecem históricos, legíveis e incompatíveis com 2.3.0.
- **Limites:** HR-01 continua reservado a um Gestor de Social Media humano cronometrado; publicação na branch exigida depende de autorização. Sem push, PR, deploy ou API paga.

## I47 — Redundância Necessária, passada 6: primeira passagem limpa — 2026-09-22

- **Estado da passada:** `clean=true`, nenhum erro, falha, lacuna, melhoria ou otimização executável; contador em **1 de 2 passadas limpas consecutivas**. O relatório independente está em `.specs/scratchpad/redundancy-pass-6-20260922-131341.md`.
- **Revisão em cascata:** o arquiteto confrontou contrato, fronteiras temporais, troca de fonte, filtros vazios, fila integral, exports e outcomes; o engenheiro não encontrou correção responsável a executar. Probes dirigidos e reconstrução independente sustentaram o resultado, sem transformar ausência de achado em garantia abstrata.
- **Jornada de Luis:** a obra só avança quando planejamento, revisão, execução e teste concordam. Esta foi a primeira confirmação limpa; ainda não encerrou o goal de duas passadas consecutivas.

## I48 — Redundância Necessária, passada 7: estado vazio e delta ausente — 2026-09-22

- **Estado da passada:** `clean=false`, dois achados corrigidos; contador reiniciado em **0 de 2 passadas limpas consecutivas**. O relatório independente está em `.specs/scratchpad/redundancy-pass-7-20260922-132225.md`.
- **R7-01 — interseção vazia:** filtros/período incompatíveis exibiam KPIs zerados e downloads, embora não houvesse população analisável. `138f803` introduziu `analysis_state = ready | empty_scope`; `bdeb546` mantém fonte, filtros e histórico visíveis, mas remove KPIs, prioridades e downloads do estado vazio e apresenta orientação explícita ao operador.
- **R7-02 — ausência não é zero:** delta sem comparador elegível aparecia como `+0`. O método `2.4.0` preserva `None` e renderiza “não definido — sem comparador elegível”; zero real continua zero. Eventos `1.0.0`–`2.3.0` permanecem legíveis, sem comparação automática com o método atual.
- **Arquiteto → engenheiro → feedback → evidência:** a revisão encontrou semântica enganosa em algo tecnicamente estável; a correção voltou às camadas de análise e apresentação; regressões, UI real e exports decidiram o fechamento. Como houve correções, a passagem não avança o goal.
- **Gate pós-correção:** venv novo `/tmp/ai-master-004-s4-r7.zQ4Wka`, Python 3.14.2, `pip check` verde e **122/122 testes** com `PYTHONWARNINGS=error` em 16,909 s (27,58 s total), pico RSS 377.815.040 bytes e zero swap. `compileall` e `git diff --check` passaram.
- **Determinismo e reconstrução:** duas CLIs reais (18,81 s e 18,47 s; zero swap) produziram CSV/Markdown/HTML idênticos byte a byte. Hashes: CSV `9c01467b7242bf0bd1af3180d1f56fae0c3e527719b4b8e5d716ab0ce674e66d`; Markdown `a1a1692f3e448169b612a83d2006657173feb26eced0eecf592138d2414d6dbc`; HTML `40e7d9ea711c630512c6a48fcfc4aba13cb0a0734b3f0e6b6f064a12027fca77`. O leitor padrão recompôs 6.703 registros, 679.596 vínculos e 52.214 IDs; maior campo 4.500, limite padrão 131.072.
- **A4 e provas visuais:** normal/adversarial permaneceram em uma página A4, visualmente sem corte; hashes PDF `5f75dcc5ded58404e164eca9f06d17bb5c064ec5d4bf8534c3abb6f03b06d6ad` / `8a1c507feb571b4ae3113ad19a8bfa88d98ce6ba57d8be1cf67800e3c8070a37`. O Chrome real renovou fonte/qualidade, fila integral e contexto no método 2.4.0. As capturas históricas 2.0.0 continuam rotuladas como história incompatível.
- **Limites honestos:** a prova automatizada cobre o estado vazio e delta ausente por regressão e inspeção do contrato; não substitui HR-01. O teste humano cronometrado e a publicação na branch exigida continuam externos. Sem push, PR, deploy ou API paga.

## I49 — Redundância Necessária, passada 8: validar o offset antes da normalização — 2026-09-22

- **Estado da passada:** `clean=false`, um achado médio corrigido; contador mantido em **0 de 2 passadas limpas consecutivas**. O relatório independente está em `.specs/scratchpad/redundancy-pass-8-20260922-1400.md`.
- **R8-01 — offset lexical inválido:** a expressão ISO aceitava minutos fora de `00–59`, e o Pandas podia normalizar silenciosamente entradas como `+00:99` ou `+13:60` antes da guarda de magnitude. Isso alterava o calendário civil informado pela fonte sem gerar o diagnóstico `invalid_date` exigido pelo contrato.
- **Correção na fronteira:** `07f27af` valida os componentes textuais antes de chamar Pandas: minutos até 59, horas até 14 e, no limite `±14`, somente `:00`. A regra cobre `±HH:MM` e `±HHMM`; `Z`, offsets fracionários válidos e `±14:00` permanecem aceitos. O diagnóstico existente conserva linha e coluna.
- **Feedback e evidência focal:** a regressão dirigida aprovou **1/1**; `py_compile` e `git diff --check` passaram. O método continua `2.4.0`: a correção faz cumprir a política temporal já declarada, sem recalibrar cálculo ou identidade. CSV, Markdown, HTML e capturas permanecem byte a byte os artefatos de I48; nenhuma regeneração foi necessária.
- **Jornada construtiva:** o arquiteto encontrou uma aceitação silenciosa atrás de uma biblioteca tolerante; o engenheiro moveu a validação para antes da interpretação; o feedback comprovou inválidos positivos/negativos e limites válidos. Como houve correção, a Passada 8 não avança o goal.
- **Escopo autorizado:** por decisão explícita, não foram repetidos suíte completa, CLI real, UI ou A4. Os **122/122**, determinismo e impressão de I48 permanecem evidência anterior, não revalidação desta passada. HR-01 humano e publicação na branch exigida continuam externos. Sem push, PR, deploy ou API paga.

## I50 — Redundância Necessária, passada 9: primeira passagem limpa após a correção — 2026-09-22

- **Estado da passada:** `clean=true`, zero achados novos; contador em **1 de 2 passadas limpas consecutivas**. A auditoria partiu do HEAD `c8cf752` e está detalhada em `.specs/scratchpad/redundancy-pass-9-20260922-141011.md`.
- **Probes mínimos:** seis datas inválidas — hora/minuto/segundo fora da faixa, dia inexistente e offsets compactos `+1360`/`-1499` — foram rejeitadas com `invalid_date`. A composição texto externo → filtro sem correspondência preservou `empty_scope` e filas vazias no CSV; cinco variações de prefixos de fórmula foram neutralizadas; NUL foi rejeitado com linha/coluna. Uma asserção inicial esperava `nul_byte`, mas o contrato retorna `nul_character`; somente o probe foi corrigido.
- **Revisão de obra:** entrada, estado vazio, fila integral, persistência, outcomes, exports, segurança textual, documentação e gates externos permaneceram coerentes. Hashes publicados coincidiram com I48; nenhum erro, falha, lacuna ou melhoria necessária e executável foi confirmado.
- **Bypass explícito:** sem suíte completa, CLI sobre o dataset real, A4 ou preflight adicional. Os **122/122**, determinismo e impressão de I48 permanecem a última evidência pesada, não validação nova. HR-01 e branch de publicação seguem externos.

## I51 — Redundância Necessária, passada 10: segunda passagem limpa e objetivo atingido — 2026-09-22

- **Estado da passada:** `clean=true`, zero achados novos; contador em **2 de 2 passadas limpas consecutivas**. O objetivo de **Redundância Necessária foi atingido** no escopo autorizado. A revisão independente permaneceu sobre o HEAD `c8cf752`, sem alteração versionada desde a Passada 9.
- **Probes mínimos:** uma fixture de 200 linhas manteve métricas, fila completa, CSV, HTML e Markdown idênticos após permutação; ID opaco com dois-pontos e quebra de linha permaneceu rastreável. Texto `<script>` foi escapado no HTML. Em SQLite `:memory:`, replay de evento foi idempotente, FK de fonte ausente foi rejeitada e a decisão anterior permaneceu íntegra.
- **Artefatos somente leitura:** o leitor padrão confirmou 6.703 registros, seis recomendações em ranks 1–6 e método 2.4.0; os IDs e hashes coincidiram com README, SPEC e I48. A captura vigente de fonte/qualidade foi apenas inspecionada, sem nova sessão de navegador ou regeneração.
- **Decisão de fechamento:** duas passadas consecutivas não encontraram bug, contrato quebrado, afirmação sem suporte nem otimização necessária. Isso fecha o goal de assimilação/redundância, sem alegar ausência absoluta de defeitos e sem ampliar o MVP.
- **Bypass e limites:** sem suíte completa, CLI real, A4, preflight ou UI adicional. Os **122/122**, determinismo e impressão de I48 continuam a última evidência pesada. HR-01 humano e publicação na branch exigida não foram encerrados. Sem push, PR, deploy ou API paga.

## I52 — Lapidação e melhoria/otimização, passada 1: sessão ágil e contexto visível — 2026-09-22

- **Estado da passada:** `clean=false`, duas melhorias relevantes implementadas; contador em **0 de 2 passadas limpas consecutivas**. A auditoria está em `.specs/scratchpad/polish-pass-1-20260922-141554.md`; o goal de Redundância já concluído não foi reclassificado.
- **L1-01 — reaproveitamento seguro:** `a3bfdf7` evita repetir parsing e análise em interações que não mudam dados. A chave da fonte usa `source_hash`; a chave analítica combina `source_hash`, `METHOD_VERSION` e escopo canônico completo. Mudança de bytes, método, filtros, período ou metadados do recorte invalida o nível responsável. Upload inválido preserva o último resultado válido; persistência e histórico não são cacheados.
- **L1-02 — contexto antes do detalhe:** cards e seletores passam a mostrar plataforma, formato, categoria, faixa de creator e mês quando disponível. O operador distingue ações de texto semelhante sem abrir cada expander; `recommendation_key`, score, ordem e persistência permanecem intactos.
- **Medição:** selecionar outra recomendação sobre a mesma fonte/escopo caiu de **2,875 s para 0,203 s**, economia de **2,672 s**, aproximadamente **93%**. A medição compara a mesma interação e não promete eliminar custos de renderização ou banco.
- **Feedback e verificação focal:** testes dirigidos confirmaram reutilização sem chamadas adicionais, invalidação estrita por fonte/escopo, preservação diante de upload inválido, decisão/download atualizados e rótulos contextuais sem troca de identidade. `py_compile` e `git diff --check` passaram.
- **Contrato e limites:** `METHOD_VERSION = "2.4.0"` e artefatos analíticos permanecem inalterados; não houve recalibração, nova dependência ou cache global. Pelo bypass autorizado, não foram executados suíte completa, CLI real, A4, preflight ou nova prova visual. Os **122/122** de I48 continuam a última evidência pesada. HR-01 e branch de publicação seguem externos; sem push, PR, deploy ou API paga.

## I53 — Lapidação e melhoria/otimização, passada 2: mês correto e rótulos limitados — 2026-09-22

- **Estado da passada:** `clean=false`, duas melhorias relevantes corrigidas; contador reiniciado/mantido em **0 de 2 passadas limpas consecutivas**. A auditoria está em `.specs/scratchpad/polish-pass-2-20260922-142639.md`.
- **L2-01 — mês efetivo:** o formatter consultava `month`, mas o contrato analítico fornece `period_month`. `00a8fb3` passa a exibir o mês real da recomendação patrocinada nos cards e seletores, sem renomear nem alterar o contexto original.
- **L2-02 — apresentação limitada, identidade integral:** valores livres do contexto são abreviados individualmente em **32 caracteres**, com reticências quando necessário. O valor completo continua no objeto da recomendação, drill-down, baseline, evidência e export; seleção e `recommendation_key` não mudam.
- **Feedback e verificação focal:** **2/2 testes focais** e **3/3 controles dirigidos** passaram; eles cobrem mês, abreviação, identidade preservada, reuso/invalidação do cache e nova tentativa após falha de persistência. `py_compile` e `git diff --check` passaram.
- **Contrato e limites:** `METHOD_VERSION = "2.4.0"` e artefatos permanecem inalterados. Pelo bypass autorizado, não foram executados suíte completa, CLI real, A4, preflight ou nova sessão de navegador. Os **122/122** de I48 seguem como última evidência pesada. HR-01 e branch de publicação permanecem externos; sem push, PR, deploy ou API paga.

## I59 — Simulação operacional do roteiro de cinco minutos pela IA — 2026-09-22

- **Decisão e autoria:** Luis perguntou qual era o próximo passo; a resposta apontou o único gate local restante, HR-01. Luis decidiu que a IA incorporaria o papel operacional de Gestor de Social Media e pediu o registro integral dos passos e da conversa. A execução abaixo usa esse enquadramento explícito.
- **Limite ético e metodológico:** esta é uma **simulação operacional por IA**, válida como evidência técnica suplementar. Ela **não substitui um Gestor de Social Media humano genuíno**, requisito textual de HR-01. Portanto, HR-01, DoD-01 e DoD-03 permanecem BLOCKED; nenhum status foi promovido por representação ou inferência.
- **Método e primeira correção:** a skill `webapp-testing` orientou o fluxo real. O primeiro harness Playwright falhou porque `input[type=file]` não estava disponível para seleção direta. A causa foi corrigida usando o evento `filechooser`, sem alterar o produto.
- **Segunda correção, sem repetição cega:** a tentativa seguinte concluiu upload e análise, mas o harness falhou ao exigir a palavra “Taxa” visível em um nó oculto. A correção foi inspecionar e controlar diretamente a UI efetivamente renderizada, derivando o próximo passo do estado visível; não houve nova tentativa cega da mesma asserção.
- **Fonte real:** dataset com hash iniciado por `693a2df6e609`, **52.214 linhas**, período de `2023-05-29T00:15` a `2025-05-28T11:08` e cinco plataformas.
- **Leitura da prioridade 1:** contexto `YouTube / video / beauty / 100,000–499,999`; ação **testar**. Componentes: impacto `0,803554`, força `0,993127`, atualidade `0,552045`; prioridade `44,0549`.
- **Contexto e evidência lidos:** ERv alvo `21,3682%`; `9.823` visualizações; `2.099` interações; benchmark `19,9429%`; Q1/Q3 `19,6376% / 20,2659%`; delta `1,42534` p.p.; amostra-alvo `1 post / 1 creator`; benchmark `291 posts / 280 creators`.
- **Decisão e persistência:** a IA aceitou e registrou localmente a decisão `f43cc922-531a-483d-b62d-b05a68b40a5d`, baixou HTML e CSV, reiniciou o processo Streamlit com o mesmo SQLite isolado e confirmou histórico, estado `accepted`, snapshot e outcome pendente.
- **Tempos medidos:** fluxo do operador `49,981 s`; reinício e verificação `15,971 s`; sessão medida total `97,242 s`, abaixo de cinco minutos. O resultado é **APROVADO como simulação por IA**, não como HR-01 humano.
- **Encerramento e limites:** servidor encerrado; banco isolado temporário; nenhuma publicação, push, PR, deploy ou API paga. A branch/publicação continua um gate externo separado. O próximo passo obrigatório permanece a execução do mesmo roteiro por um Gestor de Social Media humano, com identidade/papel e cronômetro registrados.

## I56 — Lapidação e melhoria/otimização, passada 5: primeira passagem limpa — 2026-09-22

- **Estado da passada:** `clean=true`, zero melhorias relevantes e executáveis; contador em **1 de 2 passadas limpas consecutivas**. A auditoria está em `.specs/scratchpad/polish-pass-5-20260922-144932.md`; o HEAD de fechamento foi `0cfdfeb`, cujo avanço durante a revisão continha somente o diário da Passada 4.
- **Superfícies revisitadas:** literalização de captions, precisão numérica, contexto/mês/identidade, cache e invalidações de sessão, histórico, exports, layout nativo e limites de acessibilidade. Não surgiu justificativa para redesign, nova dependência, cache global ou refatoração adicional.
- **Probes mínimos:** **3/3 testes focais** passaram em 1,210 s. Eles cobriram rótulos adversariais como texto literal com valor integral preservado, pequeno positivo/negativo sintético/zero real e reutilização/invalidação da análise com decisão imediatamente presente no download.
- **Bypass explícito:** sem suíte completa, CLI real, A4, preflight, instalação ou nova sessão de navegador. Os **122/122** de I48 permanecem a última evidência pesada, não prova nova desta passada. HR-01 e branch de publicação continuam externos.

## I57 — Lapidação e melhoria/otimização, passada 6: segunda passagem limpa e objetivo atingido — 2026-09-22

- **Estado da passada:** `clean=true`, zero melhorias relevantes e executáveis; contador em **2 de 2 passadas limpas consecutivas**. O objetivo de **Lapidação e melhoria/otimização foi atingido** no escopo autorizado. A revisão permaneceu no HEAD `0cfdfeb`, sem mudança versionada entre as passadas limpas.
- **Probes de estado pós-otimização:** upload, decisão aceita e revisão editada mantiveram apenas uma execução do motor; CSV e HTML refletiram imediatamente os dois eventos append-only, com `revision_of` correto. Uma falha injetada de proveniência não ativou a fonte nem o cache; no rerun seguinte, a importação foi revalidada, persistida e analisada normalmente.
- **Transparência do feedback:** o primeiro probe de retry consultou um atributo interno indisponível do AppTest; corrigido para a interface pública, terminou com código 0 em 0,707 s. O erro do harness não foi atribuído ao produto. Não surgiu regressão de histórico, retry, identidade, apresentação ou segurança textual.
- **Decisão de fechamento:** duas passadas consecutivas não identificaram correção ou otimização mínima restante. Isso encerra o goal de lapidação sem prometer ausência absoluta de defeitos, validar HR-01 ou ampliar o MVP.
- **Bypass e limites:** sem suíte completa, CLI real, A4, preflight, instalação ou nova prova visual. Os **122/122**, determinismo e impressão de I48 continuam a última evidência pesada. HR-01 humano e publicação na branch exigida permanecem externos; sem push, PR, deploy ou API paga.

## I58 — Verificação formal da Definition of Done — 2026-09-22

- **Estado verificado:** no HEAD `04ae066`, **CK-01–11 e HR-02–04 estão PASS**; **HR-01 está BLOCKED**, pois exige um Gestor de Social Media humano executar o fluxo cronometrado. Resultado: **14/15 critérios PASS, 1/15 BLOCKED, zero FAIL constatado**.
- **DoD:** DoD-02, DoD-04 e DoD-05 estão PASS. DoD-01 e DoD-03 permanecem BLOCKED pelo mesmo HR-01 — respectivamente, todos os critérios obrigatórios e a medição humana do fluxo em até cinco minutos. A task continua em `.specs/tasks/in-progress/implement-social-media-cockpit.feature.md`; não deve ser movida para `done` por inferência.
- **Próximo passo exato:** um Gestor de Social Media humano deve seguir `submissions/luis-roquette/solution/004-social/README.md`, seção **“Roteiro de cinco minutos”** (`#roteiro-de-cinco-minutos`), com instalação e CSV já disponíveis. Registrar operador/papel, início, fim, duração real de até 300 segundos, contexto/evidência explicados e decisão persistida.
- **Evidência e bypass:** por autorização explícita, esta verificação formal não repetiu suíte, CLI analítica, A4, preflight, instalação ou navegador. Os **122/122**, determinismo e impressão de I48 permanecem a última evidência pesada; I49–I57 e os relatórios independentes registram os deltas e probes focais posteriores. Isso não declara preflight completo no HEAD atual.
- **Publicação separada:** a branch local ainda difere da branch exigida; rename/integração, push e PR dependem de autorização e dos gates aplicáveis ao diff exato. Esse bloqueio externo de publicação não é o HR-01 nem altera a matriz local da DoD. Sem push, PR, deploy ou API paga.

## I55 — Lapidação e melhoria/otimização, passada 4: valores externos como texto literal — 2026-09-22

- **Estado da passada:** `clean=false`, uma melhoria relevante corrigida; contador reiniciado/mantido em **0 de 2 passadas limpas consecutivas**. A auditoria está em `.specs/scratchpad/polish-pass-4-20260922-144143.md`.
- **L4-01 — fronteira Markdown:** valores válidos vindos do CSV podiam chegar aos captions como sintaxe ativa de imagem, link, autolink ou ênfase. `313e611` passa a literalizar a pontuação ASCII relevante somente na fronteira dos captions, inclusive contexto da recomendação e plataformas da fonte ativa.
- **Escopo exato:** o conteúdo continua abreviado quando exibido, mas não é interpretado como Markdown. Seletores permanecem texto nativo; valores integrais, DataFrame, contexto, snapshot, baseline, identidade, decisão e exports não são modificados nem rejeitados.
- **Feedback e verificação focal:** **3/3 testes focais** passaram, cobrindo categoria/plataforma adversariais, mês, abreviação, identidade integral e precisão numérica. `py_compile` e `git diff --check` passaram. Não se alegou XSS ou requisição de rede; a correção fecha a interpretação visual indevida comprovada.
- **Contrato e limites:** `METHOD_VERSION = "2.4.0"` e artefatos permanecem inalterados. Pelo bypass autorizado, não foram executados suíte completa, CLI real, A4, preflight ou nova sessão de navegador. Os **122/122** de I48 seguem como última evidência pesada. HR-01 e branch de publicação permanecem externos; sem push, PR, deploy ou API paga.

## I54 — Lapidação e melhoria/otimização, passada 3: preservar prioridades pequenas na leitura — 2026-09-22

- **Estado da passada:** `clean=false`, uma melhoria relevante corrigida; contador reiniciado/mantido em **0 de 2 passadas limpas consecutivas**. A auditoria está em `.specs/scratchpad/polish-pass-3-20260922-1436.md`.
- **L3-01 — pequenos valores não são zero:** quatro scores positivos do artefato real apareciam como `0.0000`, e componentes pequenos como `0.00`. `92d2035` passa a usar **seis algarismos significativos** na apresentação: valores positivos pequenos preservam sinal e ordem de magnitude, valores ordinários continuam legíveis e zero exato permanece `0`.
- **Fronteira da mudança:** somente textos e formatos dos widgets foram alterados. Cálculo, score integral, componentes, ordenação, CSV/HTML/Markdown, `recommendation_key` e identidades permanecem intactos; cards principais e ações adicionais usam a mesma regra.
- **Feedback e verificação focal:** **2/2 testes focais** e **3/3 controles dirigidos** passaram, cobrindo pequeno positivo, zero real, valor ordinário e cauda da fila sem perda de identidade. `py_compile` e `git diff --check` passaram.
- **Contrato e limites:** `METHOD_VERSION = "2.4.0"` e artefatos permanecem inalterados. Pelo bypass autorizado, não foram executados suíte completa, CLI real, A4, preflight ou nova sessão de navegador. Os **122/122** de I48 seguem como última evidência pesada. HR-01 e branch de publicação permanecem externos; sem push, PR, deploy ou API paga.

## I60 — Feedback humano durante o teste: separador de milhar na interface — 2026-09-22

- **Observação de Luis:** durante o teste local na porta `8502`, após enviar o CSV real, Luis apontou uma regra básica de leitura: todas as contagens com milhares devem usar ponto como separador. A captura mostrava `4724954` visualizações e `940289` interações; a expectativa correta era `4.724.954` e `940.289`.
- **Correção centralizada:** a interface ganhou um único formatter de inteiros com agrupamento brasileiro. Ele foi aplicado aos KPIs, número de linhas da fonte, volumes e amostras do drill-down, contagens de qualidade/patrocínio, referências históricas, dias observados e colunas inteiras das tabelas. Cálculos, floats, IDs, banco e exports não foram alterados.
- **Feedback looping:** o primeiro teste focal encontrou somente uma expectativa antiga com crases, porque `st.write` passou a receber a contagem já formatada como texto. A expectativa de apresentação foi corrigida. Uma tentativa seguinte informou erro apenas porque o nome digitado do segundo método de teste não existia; o produto não foi executado nesse item. Localizado o nome correto, as três regressões afetadas terminaram verdes.
- **Validação focal:** `py_compile` e `git diff --check` passaram. Na UI real da porta `8502`, após o hot reload exigir novo envio do arquivo, o cockpit mostrou `468` posts, `4.724.954` visualizações e `940.289` interações. O reenvio serviu somente à verificação visual; nenhuma decisão foi registrada.
- **Limites:** o bypass de preflight permaneceu ativo; não houve suíte completa, CLI, A4, publicação, push, PR, deploy ou API paga. Os **122/122** de I48 continuam a última evidência pesada, e HR-01 ainda depende do restante do teste humano cronometrado.

## I61 — Rodada profunda de front-end: UI/UX com a skill `frontend-design` — 2026-09-22

- **Decisão de Luis:** durante o teste humano local, Luis pediu que fosse registrada e executada uma rodada profunda de melhoria do front-end, concentrada principalmente em UI e UX, usando explicitamente a skill `frontend-design`. A rodada foi tratada como parte da jornada construtiva — o desenho do arquiteto antecedendo o refinamento do produto em uso.
- **Direção escolhida:** **mesa editorial de inteligência**. O propósito permanece levar o Gestor de Social Media de uma fonte extensa a uma decisão auditável em poucos minutos. A linguagem visual combina papel técnico, tinta carvão e coral de sinal; tipografia editorial para hierarquia e uma trilha memorável `01 Importar → 02 Interpretar → 03 Decidir`. Não foram adicionadas dependências, imagens decorativas, JavaScript ou gradientes genéricos de produto de IA.
- **Sistema visual:** tokens CSS centralizam tinta, papel, linha, sinal e prova. Fundo quadriculado discreto, cabeçalho editorial, largura de leitura controlada, KPIs como cartões de decisão, upload técnico, expanders e formulários com bordas deliberadas, botões com resposta tátil, tabelas enquadradas e código em verde de evidência formam uma linguagem única. O conteúdo, a ordem do fluxo e os widgets nativos continuam funcionais.
- **UI/UX e acessibilidade:** a hierarquia deixa fonte, período, KPIs e prioridades escaneáveis; `:focus-visible` mantém foco de teclado evidente; `prefers-reduced-motion` remove transições; o layout reorganiza a trilha em uma coluna abaixo de 720 px. Na primeira inspeção móvel, o chrome `Deploy` do Streamlit sobrepôs o cabeçalho. A barra técnica foi ocultada e a segunda inspeção em 390 × 844 confirmou o cabeçalho sem colisão.
- **Feedback looping e provas:** quatro testes focais de renderização, upload válido/inválido, evidência e estado vazio passaram; `py_compile` e `git diff --check` ficaram verdes. O primeiro comando incluiu um nome inexistente de teste; três testes reais passaram e o quarto foi executado depois pelo nome correto, sem atribuir o erro do harness ao produto. Inspeções visuais reais cobriram topo/KPIs em desktop, cards de prioridade e viewport móvel.
- **Fronteira preservada:** análise, scores, método 2.4.0, persistência, CSV, HTML, identidade e decisões não mudaram. O hot reload preservou a fonte na confirmação final, mas esta intervenção ocorreu durante a sessão humana; portanto, o cronômetro formal de HR-01 deve ser reiniciado após a interface estabilizada. O bypass permaneceu ativo: sem suíte completa, CLI, A4, push, PR, deploy ou API paga.

## I62 — Gate de 99% para responder às três perguntas do Head de Marketing — 2026-09-22

- **Decisão de Luis:** como uma das últimas etapas, verificar com confiança mínima de 99% que o output responde diretamente: o que gera engajamento, se vale patrocinar influenciadores e qual deve ser a estratégia de conteúdo. As respostas deveriam aparecer logo na dashboard, ser definitivas e não permitir dupla interpretação.
- **Critério fixado antes da implementação:** 15 verificações obrigatórias — cinco por pergunta: resposta direta, KPI, comparação, amostra/cobertura e ação. O intervalo aceito foi **[99%, 100%]**; 14/15 equivaleria a 93,3% e não encerraria o goal. A medida representa cobertura determinística do requisito, não probabilidade causal ou estatística inventada.
- **Arquitetura mínima:** uma função compartilhada gera as três respostas para dashboard, HTML e Markdown. A dashboard calcula essa síntese uma vez por hash da fonte e versão do método sobre todo o histórico; filtros operacionais recentes não alteram a resposta executiva. Nenhuma dependência ou segundo motor analítico foi criado.
- **Resposta 1 — engajamento:** **não há driver causal comprovado; texto lidera numericamente**. ERv mediano de texto `19,912%` contra vídeo `19,895%`, diferença de `+0,0167 p.p.`, sobre `52.214` posts e `5.198` posts de texto. Ação: não redistribuir o mix apenas por formato; testar o contexto de forma controlada.
- **Resposta 2 — patrocínio:** **não escalar patrocínio agora**. Cobertura comparável de `1,56%`; zero de 12 comparações atingiu força `≥ 0,40`; deltas de `-0,136` a `+0,161 p.p.`; `5.216` estratos foram insuficientes. Sem custos e conversões não existe ROI calculável. Ação: coletar esses dados e testar antes de ampliar investimento.
- **Resposta 3 — estratégia:** **manter o mix e testar YouTube / vídeo / estilo de vida / 500.000+ por sete dias**. Hipótese de `1 post/creator/semana`, delta `+0,027 p.p.`, força `0,30`, alvo/comparador `31/38` posts, `18` creators e três semanas ISO completas. Ação: teste limitado nos próximos sete dias, revisão sete dias depois e nenhuma escala automática.
- **Validação:** o probe independente sobre o CSV real confirmou **15/15 = 100,0%**, dentro de `[99%, 100%]`, e os três veredictos esperados. Onze testes focais passaram, cobrindo contrato, renderização dos três veredictos, cache/invalidação, saída vazia, HTML seguro, relatório publicado e exports temporais. A CLI real regenerou Markdown e HTML; o CSV permaneceu byte a byte idêntico, pois o método e as evidências não mudaram.
- **Feedback local:** o hot reload do Streamlit tentou importar a nova função antes de recarregar `analysis.py`; reiniciar somente o servidor `8502` corrigiu o estado e devolveu HTTP 200. O upload automatizado no Chrome ficou bloqueado pela permissão da extensão para arquivos locais; a renderização foi comprovada pelo AppTest, mas esta rodada não alegou nova prova visual do CSV real no navegador.
- **Limites e integridade:** resposta definitiva significa decisão operacional explícita, não certeza causal indevida. A primeira resposta recusa atribuir causalidade à diferença observacional; a segunda recusa declarar ROI sem dados financeiros. O bypass de preflight completo continuou ativo; não houve push, PR, deploy ou API paga. HR-01 humano permanece um gate separado.

## I63 — Otimização do plano para a meta executiva ≥9,5 — 2026-09-22

- **Decisão de Luis:** antes da nova implementação, revisar novamente o plano com a skill `writing-plans`, em cascata e sem interrupção, até obter pelo menos duas passadas consecutivas sem melhorias ou otimizações substanciais. A documentação desta decisão e da jornada é parte central da entrega.
- **Meta interna:** partir da avaliação média preliminar de `8,7/10` e planejar `≥9,5/10`, com referência estimada de `9,58`; isso é um gate interno de qualidade, não garantia de nota externa. O plano deve aprofundar ranking multivariado, decisão condicional de patrocínio, estratégia de 30 dias, confiança por resposta e matriz executiva 15/15.
- **Efeito da skill:** o adendo foi incorporado à SPEC e convertido nas Tasks 7–11 do `IMPLEMENTATION-PLAN.md`, com arquivos exatos, interfaces, TDD vermelho/verde, resultados esperados, comandos, commits pequenos e gate final humano. A solução preserva Python, Pandas, Streamlit e SQLite; não adiciona dependência, serviço ou segundo motor.
- **Passadas 1–5 (`clean=false`):** foram removidos placeholders e helpers implícitos; corrigidos fixtures, exportação e propriedade de testes; incluídos trade-off ERv × volume, janelas/cadência do plano, estrato financeiro explícito, estabilidade e evidência em cada resposta, dez creators no conjunto e ação manual para calcular o cenário.
- **Passadas 6–10 (`clean=false`):** foram adicionados determinismo sob empate/embaralhamento, fixture executiva com três meses de patrocínio, isolamento entre fixtures de drivers e patrocínio, melhor/pior contexto comparável, e estabilidade temporal de patrocínio agrupada pelo mesmo contexto — nunca por composição global.
- **Passada 11 (`clean=false`):** os testes publicados do método 2.4 foram incluídos na migração 2.5, preservando asserções e ampliando rastreabilidade para IDs de drivers e estratégia.
- **Passada 12 (`clean=true`):** nenhum novo achado substancial; contador chegou a `1/2`.
- **Passada 13 (`clean=false`):** a Task 11 ainda não trazia resultados esperados e usava um placeholder no preflight remoto. Foram registrados resultados terminais e o comando canônico completo via `codespace-manager`; contador reiniciado para `0/2`.
- **Passadas 14 e 15 (`clean=true`):** duas revisões consecutivas não encontraram nova correção ou otimização substancial. O goal foi atingido em `2/2` passadas limpas.
- **Estado de encerramento:** planejamento e documentação concluídos; implementação das Tasks 7–11 ainda não iniciada. Nesta etapa não houve alteração de runtime, suíte, preflight, push, PR, deploy ou API paga. `.claude/`, `.specs/` e `skills-lock.json` permaneceram locais e fora do commit.

## I64 — Feedback looping, Task 7: ranking multivariado estável — 2026-09-22

- **Planejamento e revisão:** a implementação começou pelo contrato TDD da Task 7. A revisão da fixture mostrou que cinco creators alternados deixariam a força abaixo de `0,40`; o conjunto balanceado passou a usar dez creators por mês, mantendo o mínimo de 30 posts por braço/mês.
- **Teste vermelho:** quatro testes falharam exclusivamente por ausência de `engagement_drivers`, confirmando o ponto correto de implementação.
- **Execução:** o motor passou a comparar contextos orgânicos `platform + content_type + content_category + follower_band` contra outros formatos/categorias da mesma plataforma/faixa/mês. O método `2.5.0` registra materialidade, estabilidade, força, amostras, referências, volume guard, líder, vice e pior contexto sem alegar causalidade.
- **Feedback 1:** o teste de determinismo reserializava o CSV invertido e mudava corretamente o hash/IDs de origem. O harness foi corrigido para embaralhar o DataFrame já carregado, preservando identidades.
- **Feedback 2:** a regressão ampla encontrou uma expectativa fixa em `2.4.0` e um rótulo externo ilimitado no resumo executivo. A expectativa migrou para `2.5.0`; a saída visível reutiliza `_short`, enquanto o valor integral permanece nos dados/export.
- **Validação:** `ContextEvidenceTests + ReconstructionTests` aprovou **41/41**; `py_compile` e `git diff --check` passaram. Task 7 validada antes do avanço; sem preflight pesado, push, PR ou deploy.

## I65 — Feedback looping, Task 8: decisão financeira condicional — 2026-09-22

- **Planejamento e revisão:** o cenário financeiro foi mantido como função pura, vinculado a um estrato comparável explícito e separado de evidência observada, persistência e ROI alegado. A fixture mensal usa três meses, dez creators por braço e um contexto isolado do ranking orgânico.
- **Teste vermelho:** os três testes falharam no import da função inexistente, confirmando o contrato antes da execução.
- **Execução:** `sponsorship_break_even` valida custos, taxas, valor por conversão, views, contexto e evidência; calcula conversões/valor incrementais hipotéticos, custo máximo e uplift mínimo. A síntese de patrocínio passou a nomear melhor e pior contexto comparável sem misturar plataformas ou faixas.
- **Feedback:** a primeira execução verde encontrou somente ruído binário (`2.799,999999999999`). As saídas financeiras passaram a nove casas decimais, preservando fórmula e decisão.
- **Validação:** testes focais e de decisão aprovaram **7/7**; a regressão ampliada `ContextEvidenceTests + ReconstructionTests` aprovou **44/44**. `py_compile` e `git diff --check` passaram; inputs manuais não aparecem no CSV analítico. Task 8 validada antes do avanço.

## I66 — Feedback looping, Task 9: respostas completas e estratégia de 30 dias — 2026-09-22

- **Planejamento e revisão:** o contrato executivo foi ampliado para onze campos por resposta, sem criar segundo motor: veredicto, KPI, comparação, amostra, ação, força, cobertura, estabilidade, evidência e gatilho de mudança derivam do mesmo resultado analítico.
- **Teste vermelho:** os testes falharam pela ausência de `content_strategy_30d` e das linhas `driver_context`/`strategy_week` no CSV, confirmando as fronteiras previstas.
- **Execução:** o sistema passou a gerar quatro janelas relativas `D1–D7`, `D8–D14`, `D15–D21` e `D22–D30`, sempre com Gestor de Social Media, cadência observada ou coleta explícita, preservação do mix fora do teste e nenhuma publicação ou verba automática. HTML, Markdown e CSV reutilizam o mesmo contrato.
- **Feedback 1:** o primeiro ciclo encontrou gatilho sem a expressão inequívoca “a decisão mudaria” e excedeu em 198 caracteres o limite de impressão. O texto foi normalizado; IDs e gatilhos completos permanecem em detalhe expansível e no CSV.
- **Feedback 2:** a regressão ampliada encontrou uma expectativa antiga de seis campos e uma suíte inexistente digitada no comando. O teste antigo migrou para o contrato de onze campos; o erro de nome não foi atribuído ao produto.
- **Validação:** os focais aprovaram **34/34** e a regressão ampliada válida aprovou **95/95**. `py_compile` e `git diff --check` passaram. Task 9 validada antes do avanço; sem preflight pesado, push, PR, deploy ou API paga.

## I67 — Feedback looping, Task 10: cockpit executivo e cenário efêmero — 2026-09-22

- **Planejamento e teste vermelho:** três AppTests foram criados para cards completos/plano de quatro semanas, cenário financeiro manual sem mutação e isolamento entre filtros operacionais e síntese histórica. Falharam somente pelos componentes ausentes; a fixture prevista no plano também serializava booleanos como `True/False`, fora do contrato, e foi corrigida para `TRUE/FALSE`.
- **Execução:** a dashboard agora mostra onze campos nas três respostas, tabela de drivers contextuais, semanas 1–4 e cenário financeiro manual sobre um estrato elegível. As cinco premissas e o resultado ficam apenas na sessão; não entram em `active_result`, SQLite ou `evidence.csv`. O HTML baixado pode receber o cenário calculado.
- **Feedback 1:** selecionar um ID do resultado operacional falhou quando a UI usava estratos do escopo histórico, cujos IDs incluem outro escopo. O cenário foi movido para o resultado operacional visível, alinhando opção, evidência e filtros e invalidando premissas quando fonte/estrato/valores mudam.
- **Feedback 2:** a regressão completa da UI encontrou um mock antigo que exigia quatro recomendações também na análise histórica. O mock passou a alterar apenas resultados com quatro itens; o produto não foi flexibilizado.
- **Validação funcional:** **3/3** testes novos e **30/30** testes da UI/export HTML passaram; `py_compile` e `git diff --check` ficaram verdes. Cards usam uma coluna abaixo de 720 px, foco permanece visível e o conteúdo não depende somente de cor.
- **Validação visual honesta:** após reiniciar a porta `8502`, a interface real carregou sem exceção e expôs o fluxo por acessibilidade. A extensão do Chrome bloqueou o seletor de arquivo local; portanto, não se alegou nova captura visual com o CSV real nem inspeção manual 390×844 nesta rodada. A renderização com dados foi comprovada pelo AppTest; o bloqueio visual permanece registrado, sem push, PR, deploy ou API paga.

## I68 — Feedback looping, Task 11: gate executivo 2.5 e artefatos reais — 2026-09-22

- **Matriz e teste:** a regressão técnica cobre as três respostas × cinco critérios — resposta direta, sustentação multivariada, estabilidade temporal, decisão operacional e estratégia executável — e aprovou **15/15**. Um caso separado confirma que ausência de meses comparáveis resulta em “não escalar” e estabilidade não mensurável.
- **Feedback 1 — candidato inválido:** a primeira geração 2.5 respondeu corretamente que não havia vencedor sustentado, mas o plano de 30 dias escolheu o primeiro contexto lexical, com zero meses elegíveis. O motor passou a publicar `best_candidate`; a estratégia usa o melhor candidato elegível apenas para validação, nunca como vencedor ou escala automática.
- **Feedback 2 — rastreabilidade:** o relatório citava o overview de drivers e o programa de 30 dias, mas o CSV exportava somente contextos/semanas. Foram acrescentadas evidências `driver_overview` e `strategy_30d`; todos os IDs citados agora existem no export.
- **Reconciliação independente:** um cálculo Pandas separado das funções sob teste confirmou 52.214 linhas, limiar material `0,1620304722 p.p.`, 20 contextos, 18 elegíveis, zero líderes e candidato YouTube/vídeo/estilo de vida/100.000–499.999 (`3` meses, delta `+0,070754717 p.p.`, estabilidade `100%`, `C=0,95`). Patrocínio confirmou 12 estratos, cobertura `1,5589689%`, melhor contexto `+0,0973704 p.p.` e pior `-0,1362255 p.p.`.
- **Eficiência e determinismo:** CLI real em `18,01 s`, RSS máximo `556.072.960 bytes`, zero swap. Upload/análise fria até os cards em AppTest: `21,404 s`; rerun da mesma fonte: `0,232 s`; ambos dentro de `≤30 s` e `≤1 s`. Uma segunda CLI produziu CSV, Markdown e HTML byte a byte idênticos.
- **Artefatos:** `evidence.csv` tem 6.830 registros, seis recomendações, 20 `driver_context`, um `driver_overview`, quatro `strategy_week` e um `strategy_30d`; nenhuma premissa financeira manual foi exportada. SHA-256: CSV `e982cd2fcc346951d4c6ab5d9a3af4443858548a1786fe0424d4f71d84c2f30a`; Markdown `d4e5ee40430d97f1430db7c95e54eb83a818eddc8e1692b63f66e5347f2b8537`; HTML `0284af6d3e1a602e057feb720a1d22fc54de71aab7e5739b45332b4c78ac011f`.
- **Nota preliminar, sem autoaprovação:** clareza `9,7` (veredictos e gatilhos no primeiro bloco); objetividade `9,8` (decisões explícitas sem causalidade/ROI inventados); eficiência `9,6` (limites medidos e atingidos); profundidade `9,5` (contexto multivariado, estabilidade e cenário condicional); capacidade decisória `9,5` (manter/não escalar/validar com quatro gates). Média IA: **9,62/10**, nenhuma dimensão abaixo de `9,0`. A nota final permanece **PENDING** até leitura humana de Luis ou avaliador designado; HR-01 também permanece pendente.
- **Gates e fronteira:** o gate focal final aprovou **45/45**, além de `py_compile` e `git diff --check`; 146 testes estão catalogados. Pelo bypass explícito, o preflight completo não foi repetido localmente nem em Codespace e continua obrigatório antes de PR. A prova visual com CSV real não foi substituída sem captura válida. Sem push, PR, merge, deploy ou API paga.

## I69 — Planejamento do pacote final de entrega — 2026-09-22

- **Decisão de Luis:** fechar o projeto com uma entrega multimodal: wizard guiado no estilo Arcade, narrativa da construção em Markdown, DOCX e texto simples, visual da evolução dos prompts, vídeo explicativo, mapa mental e infográfico produzidos com NotebookLM.
- **Ajuste arquitetural:** para evitar versões concorrentes, foi definida uma única narrativa canônica. O Arcade explicará **como usar o sistema**; o vídeo e as peças do NotebookLM explicarão **como ele foi construído**; o README será o índice do avaliador.
- **Metodologia preservada:** a história mostrará SDD, ondas socráticas adaptativas, SPEC, lapidação, feedback looping, redundância necessária, erros, correções, evidências e contribuição humana. O visual ligará cada prompt principal à decisão e à mudança observável no produto.
- **Pesquisa antes do plano:** a documentação oficial confirma que o Arcade cobre captura interativa, hotspots, capítulos, compartilhamento e analytics; o NotebookLM cobre Video Overviews, Mind Maps, Infographics e artefatos documentais. As ferramentas atendem aos papéis definidos sem criar mídia redundante.
- **Plano e gate:** o plano executável foi salvo em `docs/004-social/DELIVERY-PLAN.md`, dentro da pasta permitida pela submissão. A entrega final exigirá links públicos testados em janela anônima, fidelidade numérica, paridade entre formatos e duas passadas consecutivas sem correção relevante antes do PR.
- **Limites atuais:** esta etapa planejou e documentou a entrega; não criou conta, publicou Arcade/NotebookLM, abriu PR, executou preflight ou acionou API paga.

## I70 — Entrega, Task 1: narrativa canônica e índice do avaliador — 2026-09-22

- **Planejamento e revisão:** o plano aprovado foi relido contra o briefing, o guia de submissão, a SPEC, a análise 2.5, a pesquisa, o diário e o histórico Git. A entrega foi dividida em rota rápida de até cinco minutos e rota de aprofundamento.
- **Execução:** `CONSTRUCTION-STORY.md` passou a ser a fonte narrativa canônica. O texto organiza desafio, pesquisa, 24 ondas socráticas, SDD, feedback loops, redundância, lapidação, erros, resultado e limites, sempre ligando decisão humana, ação da IA e efeito no produto.
- **Índice executivo:** o README agora começa pelas três respostas do Head de Marketing e oferece dois percursos: ver a solução ou entender a construção. A síntese foi atualizada para o método 2.5, removendo recomendações superadas pelo ranking multivariado final.
- **Verificação:** todos os números do estudo de caso foram confrontados com `analysis.md`, `evidence.csv` ou I68; os links permanecem dentro da pasta da submissão. `git diff --check` é o gate textual desta fase.
- **Limites:** a leitura humana cronometrada continua pendente; DOCX, TXT, linha do tempo, Arcade e NotebookLM pertencem às fases seguintes. Nenhuma publicação, assinatura, API paga, commit, push ou PR foi executado.

## I71 — Entrega, Task 2: três formatos a partir da mesma fonte — 2026-09-22

- **Decisão de formato:** `CONSTRUCTION-STORY.md` permanece como única fonte editável. O texto simples e o DOCX foram derivados dessa fonte; nenhum deles recebeu conteúdo narrativo exclusivo.
- **Execução:** foram gerados `CONSTRUCTION-STORY.txt` e `CONSTRUCTION-STORY.docx`. O documento Word usa página Letter, capa, índice, hierarquia de títulos, duas tabelas, links clicáveis, cabeçalho lógico de tabela e paginação.
- **Feedback e correção:** a primeira renderização revelou uma borda azul herdada pelo estilo Title; ela foi removida. A auditoria de acessibilidade encontrou duas tabelas sem cabeçalho semântico; ambas foram marcadas e a segunda auditoria terminou com zero achados.
- **Validação:** as sete páginas finais foram renderizadas e inspecionadas em resolução original, sem corte, sobreposição ou tabela quebrada. Os seis marcadores críticos têm contagens idênticas em Markdown, TXT e DOCX: `52.214`, `1,56%`, `0,280`, `0,950`, `45 de 45` e `146`.
- **Limites:** o renderizador empacotado não encontrou `pdf2image`; o fluxo manual previsto pela própria skill usou LibreOffice e `pdftoppm`. O PDF e os PNGs serviram apenas à inspeção e não foram incluídos na entrega.

## I72 — Entrega, Task 3: linha do tempo prompt → produto — 2026-09-22

- **Planejamento:** oito marcos foram selecionados do diário: absorção, pesquisa, ondas socráticas, SDD, feedback loops, redundância, lapidação e método 2.5. Cada marco conserva um fragmento de prompt, uma mudança observável e a referência do diário.
- **Execução:** `assets/methodology-evolution.png` foi produzido de forma determinística em 2.000 × 2.800 pixels, usando a mesma direção de mesa editorial do cockpit. O rodapé conecta o processo às três decisões finais.
- **Verificação:** a imagem foi aberta na resolução original; textos, acentos, ordem, contraste, hierarquia e referências permanecem legíveis. Nenhum caminho local, segredo, dado pessoal ou alegação nova foi incluído.
- **Limite e escolha técnica:** a skill `imagegen` foi consultada, mas o próprio contrato recomenda um ativo code-native para diagramas. SVG temporário e conversão local produziram o PNG final sem API paga ou geração probabilística.

## I73 — Entrega, Task 4: tour guiado no Arcade — 2026-09-22

- **Execução:** foi criado o rascunho `Cockpit de Social Media — decisões em 3 minutos` no Arcade, usando a captura real do cockpit e sete etapas ligadas por callouts.
- **Roteiro:** abertura e volume do dataset; validação da fonte; três respostas executivas; ausência de vencedor sustentado; condição mínima para patrocínio; programa de 30 dias; evidência, exportação e diário.
- **Verificação:** o modo Preview exibiu a aplicação real, o título correto, o callout legível e a navegação entre etapas. A alternativa de upload manual evitou instalar extensão ou aplicativo.
- **Limite externo:** após o fim do trial, o Arcade exige uma seleção irreversível de até três arquivos que continuarão editáveis; todos os demais permanecem publicados, mas bloqueados para edição. O tour novo está completo, porém ainda retorna “not published yet” em acesso sem sessão. Nenhuma seleção irreversível ou compra foi feita sem confirmação humana.

## I74 — Entrega, Task 5: fontes e ativos do NotebookLM — 2026-09-22

- **Fontes:** foi criado o notebook `Challenge 004 — Social Media | Construção e entrega` com quatro fontes equivalentes à narrativa canônica, análise 2.5, SPEC e guia de uso. Como o seletor bloqueou os arquivos Markdown, o conteúdo integral foi inserido como texto copiado, sem alterar a fonte local.
- **Mapa mental:** o prompt preservou os quatro ramos Desafio, Método de construção, Produto e Evidências. Todos os ramos foram expandidos antes do download; o PNG final registra 52.214 posts, a sequência metodológica, a stack e as provas.
- **Vídeo:** a primeira geração de 6min31s foi rejeitada porque excedeu o intervalo e permitia confundir 18,01 segundos de execução da CLI com tempo para gerar código. A segunda geração tornou a distinção explícita; a versão final foi acelerada uniformemente em `1,1×`, sem cortes, e ficou em 5min57,54s. O MP4 H.264/AAC decodificou integralmente e teve seis quadros distribuídos mais o encerramento inspecionados.
- **Infográfico:** a primeira geração foi rejeitada por escrever “download em 5 minutos” e `1,55%`. A versão final corrigiu a promessa para decisão rastreável em até cinco minutos e a cobertura para `1,56%`; imagem completa inspecionada em 1.536 × 2.752 px.
- **Estado desta anotação:** mapa, infográfico e vídeo finais estão versionados; os binários e hashes constam em `DELIVERY-MANIFEST.md`. O notebook permanece privado até o gate explícito de permissões.

## I75 — Gate de publicação e manifesto — 2026-09-22

- **Manifesto:** `DELIVERY-MANIFEST.md` registra percurso, URLs, estados reais, propriedades, tamanhos e SHA-256 de cinco binários. Nenhum link privado foi rotulado como público.
- **Arcade:** o Preview confirma sete etapas; uma requisição anônima ao link de compartilhamento recebeu HTTP 200 com a página “not published yet”. A publicação depende da seleção irreversível de até três arquivos editáveis no plano gratuito.
- **NotebookLM:** Luis questionou a necessidade de expor a conta quando os arquivos já estavam baixados. A decisão foi manter o notebook `Restrito` e entregar somente MP4 e PNGs versionados; o avaliador não precisa entrar no ambiente proprietário.
- **Gates locais:** links Markdown relativos, integridade ZIP do DOCX, dimensões dos PNGs, decodificação integral do MP4 e `git diff --check` passaram. O preflight pesado, as duas passadas finais, o push e o PR ainda não foram executados nesta anotação.
- **Decisão de conta:** Luis autorizou explicitamente excluir os cinco projetos antigos do Arcade e preservar apenas o novo Cockpit. Foram removidos `Swen.ia.br`, `Upload and Enrich Company Data for Lead Insights`, `Start a Free Trial and Deploy an AI Agent`, `Untitled (Wed Mar 18 2026)` e `Set Up a Custom AI Agent With Communication Channel`; o Arcade os moveu para `Recently deleted`.
- **Publicação:** após a remoção, o botão Share publicou `https://app.arcade.software/share/VHx5b51f94IAFSr6pmds`. Uma requisição sem cookies retornou HTTP 200, URL final idêntica, 25.844 bytes e o título correto, sem o marcador `notPublished`.

## I76 — QA final do pacote multimodal — 2026-09-22

- **Prova pública:** o Arcade foi aberto em uma segunda sessão do Chrome e percorreu as sete etapas: abertura, fonte, três respostas, ausência de vencedor, condição de patrocínio, programa de 30 dias e trilha auditável. O encerramento e o watermark gratuito apareceram corretamente.
- **Passada 1 (`clean=true`):** links relativos, hashes dos cinco binários, duração e decodificação do vídeo, integridade do DOCX, ausência de link privado do NotebookLM e resposta pública do Arcade passaram sem correção.
- **Passada 2 (`clean=true`):** estrutura exigida pelo template, três perguntas do Head, presença dos dez artefatos finais, entrypoints, ausência de vazamento do notebook privado, HTTP 200 do Arcade e `git diff --check` passaram sem correção.
- **Goal:** duas passadas finais consecutivas sem erro, gap ou otimização relevante: `2/2`. A entrega multimodal está pronta para o preflight pesado e o PR; HR-01 continua sendo o único gate humano declarado.

## I77 — Preflight remoto da entrega — 2026-09-22

- **Ambiente:** o gate pesado foi executado no Codespace limpo `codex-preflight-4v9q95gxxx5fj6v5`, exclusivamente pelo `codespace-manager`, sobre o commit publicado `d055bf9987f3cbcd2206a9d3fc321e36c5cb211f`.
- **Correção do executor:** a primeira chamada continha um SHA digitado incorretamente na asserção do próprio comando. O produto não foi executado nessa tentativa; o SHA foi conferido no Git e a chamada foi corrigida.
- **Evidência confirmada:** `pip check` retornou `No broken requirements found`; a descoberta integral executou **146 testes em 68,762 segundos**, todos aprovados (`OK`).
- **Integridade do relato:** o shell remoto não devolveu um status terminal inequívoco depois da suíte. Portanto, esta passagem não é declarada como preflight completo; `compileall`, `git diff --check`, árvore limpa e saída zero serão novamente exigidos no SHA documental final antes do PR.

## I78 — Enxugamento da jornada e vídeo obrigatório de arquitetura — 2026-09-22

- **Decisão de Luis:** otimizar a entrega para um avaliador humano com pouco tempo, sem descartar os materiais já criados no NotebookLM, e tornar obrigatório o vídeo em que o próprio autor explica a arquitetura.
- **Hierarquia final:** o README funciona como porta de entrada; o avaliador lê as três respostas, percorre o Arcade e assiste ao vídeo de arquitetura. Vídeo-síntese, mapa mental e infográfico do NotebookLM permanecem entregues em uma rota visual secundária. Estudo de caso, DOCX, linha do tempo, análise, evidências e diário ficam agrupados como auditoria e anexos.
- **Tratamento do vídeo:** a fonte aprovada tinha 232.879.349 bytes, acima do limite normal de 100 MB do GitHub. Foi criada uma cópia H.264/AAC de 1.280 × 720 px e 46.065.676 bytes, sem cortes, preservando a duração de 6min05s e as legendas incorporadas. Hash da fonte: `a968a524dbe45443a066717e5d63523e5336f958fb3a6dcd50d0d0887dbbea4a`; hash entregue: `3bd2642074715c082212388c9672aa3afcd8a1037351f071736661e33125f907`.
- **Validação:** o MP4 otimizado decodificou integralmente; duração, codecs e cinco pares de quadros distribuídos foram comparados com o original. As legendas permaneceram legíveis e não foi encontrada perda material de conteúdo.
- **Gate humano:** README, manifesto e vídeo serão apresentados a Luis antes de qualquer commit, push ou atualização do PR. A aprovação explícita continua obrigatória para a entrega.

## I79 — Auditoria final de aderência às regras — 2026-09-22

- **Decisão de Luis:** a submissão deve atingir aderência integral ao challenge, ao guia de submissão, ao template e às regras de PR; qualquer requisito esquecido deve ser corrigido antes da entrega.
- **Achados:** a auditoria encontrou quatro lacunas de apresentação ou submissão: resposta obrigatória de audiência escondida, percurso recomendado superior a cinco minutos, decisões de frequência/threshold/parada/quick win dispersas e LinkedIn não preenchido. Também identificou conflito externo com a regra de um PR por pessoa.
- **Correções de conteúdo:** o contrato executivo passou a responder também qual perfil de audiência mais engaja. Para o dataset real, o veredicto é não eleger uma persona: idade, gênero e localização tiveram 0% de cobertura em comparações controladas. README, dashboard, HTML e Markdown compartilham a mesma quarta resposta.
- **Correções de entrega:** o percurso executivo passou a durar aproximadamente quatro minutos — leitura e Arcade. O vídeo de arquitetura continua obrigatório como artefato, mas não bloqueia a compreensão do output em cinco minutos. O README agora explicita esforço, cadência, política/threshold de patrocínio, o que parar e o quick win da semana, além do LinkedIn confirmado publicamente.
- **Validação:** dez testes focais passaram no Mac, incluindo o contrato de quatro respostas e o limite de impressão. No Codespace, o SHA `1080f8f` aprovou **146/146 testes** em 65,370 segundos; `py_compile` e `git diff --check` também passaram localmente. O gerenciador encerrou a sessão após a suíte antes de devolver um status combinado para `compileall` e árvore limpa, portanto esses dois sinais não foram inventados como prova remota terminal.
- **Aderência do PR:** os PRs #140 e #141 foram encerrados com o motivo registrado, preservando somente o PR #145 e cumprindo a regra de um PR por pessoa. A atualização do #145 com o SHA final permanece como última ação de publicação.

## I80 — Publicação final aderente — 2026-09-22

- **Publicação:** o branch `submission/luis-roquette-004-social` foi enviado e o PR #145 atualizado com as quatro respostas executivas, o percurso rápido, os limites analíticos e as provas de validação.
- **Provas externas:** o PR #145 é o único PR aberto de `luisroquette`, contém somente arquivos sob `submissions/luis-roquette/` e responde HTTP 200. O tour público do Arcade também responde HTTP 200.
- **Integridade:** o commit executável validado e o commit publicado anterior diferiam apenas por duas linhas deste diário; nenhum código foi alterado após os 146/146 testes verdes. O branch remoto temporário de validação foi removido depois da publicação.
- **Higiene:** os dois Codespaces criados para esta validação foram apagados após confirmação de árvore limpa e trabalho salvo no GitHub; um Codespace limpo com mais de três dias também foi removido conforme a política global de cota. Codespaces sujos de outras tarefas foram preservados.

## I81 — Auditoria independente das regras de entrega — 2026-09-22

- **Escopo:** challenge 004, guia de submissão, README raiz, CONTRIBUTING, índice de challenges e template foram relidos integralmente no mesmo SHA de `origin/main` e `upstream/main` (`4aed364`).
- **Achados:** solução, process log, setup, PR único, título e escopo já estavam conformes. Restavam duas lacunas de apresentação: títulos explícitos `Executive Summary` e `Evidências` ausentes no README e uma frase obsoleta que ainda tratava o preflight como pendente.
- **Correções:** o README passou a espelhar os campos do template e a nomear os quatro formatos de evidência escolhidos; o setup agora registra que 146 testes passaram no estado executável final e que os commits seguintes foram apenas documentais.
- **Limite preservado:** custo implícito e ROI não foram inventados porque o dataset não contém custos, receita ou conversões; o cockpit oferece cenário manual de ponto de equilíbrio. A branch mantém o prefixo exigido `submission/`, e a regra de um único PR continua atendida pelo #145.
