# Plano — Challenge 003: Lead Scorer

Análise inicial realizada em **30/09/2026**. Direção de produto revisada na mesma data para incorporar o **Top 10 diário com missões e card expandido**, conforme a referência escolhida pelo usuário. Documento preparado para ser levado a um repositório independente. Status: planejamento; nenhuma implementação do desafio ou alteração funcional do CRM foi realizada.

## 1. Direção recomendada

Construir uma aplicação web em português que responda: **“Quais oportunidades devo trabalhar primeiro, por quê e qual é a próxima ação?”**

A experiência do CRM do Futuro fornece o conceito de produto: transformar informações comerciais em uma rotina de trabalho. A entrega será uma aplicação independente, usando o dataset do desafio e um motor de priorização reproduzível. Sua identidade visual será própria, seguindo a [referência do Top 10 escolhida pelo usuário](referencias/lead-scorer-top10-referencia.png), sem depender da identidade ou da infraestrutura do CRM.

**A tela principal será uma sequência de até dez missões para o vendedor**, com uma oportunidade expandida por vez e as demais em cards compactos. Ao esvaziar os itens pendentes do lote, carregar automaticamente as próximas dez prioridades elegíveis. O progresso diário, as conclusões e a sequência de dias com a meta cumprida dão o tom de gamificação.

O diferencial proposto é a combinação de interface acionável, explicações calculadas pelo próprio motor, tratamento explícito das limitações dos dados e validação temporal. Usar IA durante análise, implementação e revisão, registrando decisões e verificações desde o começo. IA generativa em tempo de execução é um complemento opcional, não uma dependência do MVP.

## 2. Regras oficiais e caminho de entrega

O desafio pede software executável com dados reais, lógica de priorização além do valor e explicações compreensíveis para o vendedor. Exige documentação de instalação, critérios e limitações, além de evidências do processo com IA. O orçamento sugerido é de 4–6 horas. [Brief oficial](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/challenges/build-003-lead-scorer/README.md).

**Repositório novo é o ambiente de desenvolvimento; a entrega oficial exige fork e PR.** Ao finalizar, transportar a solução para `submissions/<seu-nome>/` no fork, usando a branch `submission/<seu-nome>`. O PR deve alterar somente essa pasta, com título `[Submission] Seu Nome — Challenge 003`. Um link para o repositório independente pode acompanhar a entrega, mas não substitui esse procedimento. [CONTRIBUTING](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/CONTRIBUTING.md).

Manter o README final conforme o [template de submissão](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/templates/submission-template.md), incluindo perfil do candidato, abordagem, resultados, recomendações, limitações e processo. O [guia de submissão](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/submission-guide.md) aceita narrativas, conversas exportadas, capturas, gravações e histórico Git como evidência; registrar iterações reais, verificações e correções, sem inventar etapas.

## 3. O que foi verificado nos dados

Foi consultado o arquivo público do [dataset indicado](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics) e seus CSVs foram lidos em memória. As observações abaixo resultam dessa inspeção, não apenas das estimativas do brief. Nenhum arquivo do dataset foi adicionado ao CRM.

| Arquivo | Registros | Papel |
| --- | ---: | --- |
| `sales_pipeline.csv` | 8.800 | Oportunidades e resultados |
| `accounts.csv` | 85 | Dados das empresas |
| `products.csv` | 7 | Produtos, séries e preços de catálogo |
| `sales_teams.csv` | 35 | Vendedores, gestores e escritórios regionais |
| `metadata.csv` | 21 | Descrições dos campos; arquivo adicional útil para documentação |

### Distribuição e problemas concretos

| Estágio | Quantidade | Sem conta | Sem data de engajamento |
| --- | ---: | ---: | ---: |
| Prospecting | 500 | 337 | 500 |
| Engaging | 1.589 | 1.088 | 0 |
| Won | 4.238 | 0 | 0 |
| Lost | 2.473 | 0 | 0 |

- Há **2.089 oportunidades abertas** e **6.711 encerradas**. A fila operacional deve trabalhar as abertas; as encerradas fornecem histórico e resultados para avaliação.
- As datas de engajamento vão de `2016-10-20` a `2017-12-27`; o último fechamento é `2017-12-31`. Usar `2017-12-31` como data de referência inicial da demonstração e exibi-la na interface. Calcular idade com a data real de 2026 tornaria todas as oportunidades artificialmente antigas.
- **1.480 registros usam `GTXPro`; o catálogo usa `GTX Pro`.** Aplicar um alias explícito e documentado antes do vínculo de produtos. Preservar o valor original para auditoria. Um join literal perde esses registros.
- Não foram encontrados IDs de oportunidade duplicados, contas não vazias desconhecidas, vendedores desconhecidos ou fechamento anterior ao engajamento. Isso não equivale a uma auditoria completa de qualidade.
- A ausência de conta está concentrada nas oportunidades abertas. Não aprender que “conta preenchida = venda ganha”, nem usar completude como atalho para previsão. Essa distribuição também limita a comparação entre histórico e carteira aberta.
- `engage_date` marca entrada em **Engaging**; não é data de último contato nem de criação da oportunidade. `close_value` é receita realizada, não valor disponível previamente.
- O dicionário informa receita anual da conta em **milhões de USD**. Preço de catálogo não representa quantidade vendida, desconto, margem ou valor final. Explicitar unidades e não converter os dados para reais sem fundamento.

Como diagnóstico exploratório, a taxa de vitória por produto entre negócios encerrados varia aproximadamente de 60% a 65%. O produto mais caro tem somente 25 resultados encerrados. Esses números usam todo o histórico e **não são métricas de validação**: indicam que produto isolado pode diferenciar pouco e que amostras pequenas precisam de suavização.

## 4. O que o CRM oferece como referência

A análise foi feita no código, nos SQLs e nos contratos de workflows locais. Não foi consultado o banco em produção, e não foi verificado quais migrações estão efetivamente aplicadas.

| Evidência no CRM | Comportamento observado | Aplicação no desafio |
| --- | --- | --- |
| `frontend/src/pages/Home.tsx` | Alertas por prioridade, acompanhamento atrasado e oportunidades esfriando | Tela inicial com uma fila curta de ações justificadas |
| `frontend/src/pages/Leads/index.tsx` | Lista, filtros, score e ordenação | Ranking que alimenta lotes de dez missões |
| `frontend/src/pages/Leads/LeadDetail.tsx` | Resumo, sugestão de contato e detalhamento do lead | Painel de contexto, motivos e próxima ação |
| `frontend/src/services/matchingService.ts` | Score determinístico e breakdown por dimensão | Estrutura de retorno explicável para o novo motor |
| `frontend/src/components/leads/LeadScoreChart.tsx` e `SQLs Supabase/supabase_lead_score_history.sql` | Histórico persistido de score | Inspiração futura; o dataset não fornece esse histórico |
| `SQLs Supabase/supabase_ai_prompt_real_estate_human_follow_up_v6.sql` | Classificação por intenção, ação contextual, limites contra invenção e confirmação humana de arquivamento | Recomendações limitadas às evidências disponíveis |
| `n8n_workflows/Follow-up infinito/Processamento de IA (On-Demand) - CRM.json` | Resolução de prompt, contexto limitado, normalização de JSON e controle de reanálise | Separar contexto, cálculo, explicação e contrato de saída |
| `frontend/tests/matchingService.test.ts` e `frontend/tests/leadAiOnDemandWorkflowContract.test.ts` | Cobertura de regras e contratos | Testes de integridade, ranking e ausência de vazamento |
| `Referencias/design.md` | Clareza e próxima ação | Referência de princípio de UX; a identidade visual seguirá a nova imagem |

### Distinções que precisam permanecer claras

O CRM possui dois conceitos diferentes: **score de intenção do lead**, orientado por análise de conversas, e **score de compatibilidade lead–imóvel**, calculado por regras. O segundo não estima fechamento. O desafio pede priorização de oportunidades B2B com dados estruturados; precisa de um motor próprio.

O arquivo de orientação descreve threshold de matching de 60, mas o código atual e seu teste estabelecem **80**, com banheiros como dimensão adicional quando informados. A análise usa a implementação atual como evidência. Esse threshold não será transportado para o desafio.

Não há, nos arquivos analisados, comprovação de calibração estatística do score de intenção do CRM como probabilidade de venda. A entrega deve apresentar esse contexto como experiência de produto, sem atribuir ao CRM resultados preditivos não demonstrados.

Reaproveitar padrões, componentes pequenos e conhecimento de UX quando útil. Reescrever módulos que dependam de entidades imobiliárias, Supabase ou autenticação. Não transportar workflows completos, credenciais, endpoints do CRM ou dados de clientes. A gamificação deste produto será própria: missão, progresso e sequência diária. XP, níveis, ranking entre vendedores, imóveis, radar e WhatsApp ficam fora do escopo inicial.

## 5. Produto e escopo do MVP

### Jornada principal

1. Vendedor escolhe seu nome e recebe as dez primeiras oportunidades elegíveis da sua carteira. Na primeira visita, usar um seletor simples; depois, lembrar a escolha.
2. A tela cumprimenta pelo primeiro nome, mostra o progresso do lote e abre a primeira missão pendente.
3. O vendedor lê os motivos e a próxima ação, pode escolher outra missão, marcar a ação como feita ou adiar para amanhã.
4. Quando não houver missões pendentes no lote, carregar as próximas dez elegíveis, preservando o histórico do dia. Se restarem menos de dez, carregar somente as disponíveis.

**Simplificação aprovada:** retirar da tela inicial a tabela da carteira completa, os cinco cards paralelos, o painel lateral permanente e os filtros avançados. O card expandido reúne contexto, explicação e ação. “Como priorizamos” e opções de equipe ficam em acessos secundários, sem competir com o trabalho diário.

Prospecting e Engaging participam da mesma seleção operacional, com estágio e ação apropriada identificados em cada missão. Para Prospecting, usar “Qualificar oportunidade” e declarar que o tempo em prospecção é desconhecido. A mistura é uma decisão de produto; o score continua um índice operacional, sem presumir engajamento dos 500 registros em Prospecting.

### Composição da tela e interação dos cards

A referência visual é o arquivo `referencias/lead-scorer-top10-referencia.png`, incluído junto deste plano. Usar fundo claro, títulos em azul profundo, azul para progresso e laranja para a missão ativa, bordas delicadas e respiro. A imagem orienta composição e tom; os dados e textos serão calculados ou adaptados ao contrato real.

- **Cabeçalho:** data do dia, “Bom dia, Darcel. Seu Top 10 de hoje.”, contador de conclusões do lote, progresso segmentado e sequência diária quando houver histórico real.
- **Progresso:** até dez segmentos; azul para concluída, laranja para selecionada, neutro para pendente e ícone de relógio para adiada. Mostrar legenda textual e estado acessível.
- **Resumo de conclusões:** “3 concluídas hoje”, com nomes e possibilidade de abrir o histórico. Conta desconhecida pode aparecer pelo ID curto da oportunidade.
- **Cards recolhidos acima:** missões pendentes anteriores à selecionada, em sua ordem original. Mostrar posição, conta/produto, motivo curto, score e controle para expandir.
- **Card expandido:** “Agora · missão 4”, conta, produto, estágio, preço de catálogo identificado como tal, score de prioridade, explicações e próxima ação.
- **Cards recolhidos abaixo:** missões pendentes seguintes, também na ordem original. A tela mostra apenas o lote corrente de até dez oportunidades de trabalho.
- **Rodapé discreto:** data de referência do scoring, acesso ao método e histórico de ações. Concluídas e adiadas ficam em resumos recolhidos; não formam uma segunda lista extensa na tela.

**Ao selecionar a missão 7**, as missões 1–6 ainda pendentes ficam compactas acima, a missão 7 expande e as 8–10 ficam compactas abaixo. O card anteriormente expandido recolhe na posição original; seleção não conclui, adia nem muda o ranking. Permitir reabrir qualquer card compacto acima ou abaixo.

Sempre haverá no máximo um card expandido. Manter IDs e posição de ranking estáveis no lote, mesmo após conclusão de outras missões. Na troca, levar o foco ao título do card selecionado e garantir sua visibilidade, com movimento curto e suporte a `prefers-reduced-motion`. Em celular, manter a mesma sequência vertical, com ações legíveis e sem rolagem horizontal.

### Ações da missão e regras dos lotes

| Ação | Efeito esperado |
| --- | --- |
| Selecionar card | Troca somente a oportunidade em destaque |
| Feito | Registra conclusão da ação sugerida, atualiza progresso e avança à primeira missão ainda pendente do lote |
| Desfazer conclusão | Reverte o registro e o progresso; não duplica recompensas nem muda o estágio comercial |
| Adiar para amanhã | Retira do trabalho de hoje, registra a data de retorno e avança à primeira pendente; não conta como conclusão |
| Copiar orientação | Copia a próxima ação para apoiar o atendimento; não conclui a missão |
| Abrir no CRM | Disponível somente com URL real configurada para a oportunidade; abrir o link não conclui a missão |

“Feito” significa **ação realizada pelo vendedor**, declarada manualmente, e não negócio ganho, contato confirmado por integração ou resultado de venda. Usar feedback curto e opção de desfazer. Visitar, expandir ou copiar uma missão não gera progresso.

Ao desfazer uma conclusão do lote corrente, a missão retorna à sua posição original como pendente. Se pertencer a um lote anterior, devolver à fila elegível para o próximo lote, mantendo o lote atual com no máximo dez itens. Oferecer desfazer adiamento com a mesma regra de retorno. O cursor não pode fazer essas oportunidades se perderem: manter também uma fila explícita de retornos. Eventos de duplo clique e atualização de estado devem ser tratados de forma idempotente.

Ao gerar o lote, excluir oportunidades encerradas, ações já concluídas naquele dia, adiadas com retorno futuro e IDs já presentes no lote. A ordem vem do motor e é congelada durante o lote. Guardar o ranking diário e o cursor de consumo para evitar repetição entre lotes. Trocar vendedor isola seleção, progresso e histórico.

O lote termina quando todos os seus itens estiverem concluídos ou adiados. Nesse momento, carregar automaticamente o próximo lote e abrir sua primeira missão, com mensagem “Próximas 10 prioridades carregadas”, adaptando o número ao tamanho real do lote. **Adiar esvazia a fila, mas não preenche o contador de conclusões nem cumpre a meta diária.** Se todas foram feitas, celebrar brevemente antes da transição; se houve adiamentos, informar os totais com neutralidade.

Após o último lote, mostrar “Você revisou todas as prioridades disponíveis”, distinguindo feitas e adiadas. Para um lote menor, o progresso usa o tamanho real, como `3/6`. O primeiro é “Top 10 de hoje”; os seguintes mostram “Mais 10 prioridades · lote 2” e o total concluído no dia, evitando que o reinício do contador pareça perda de progresso.

No dia seguinte, gerar a fila com as oportunidades adiadas para esse dia primeiro, ordenadas pelo score entre si, seguidas das demais elegíveis. Uma oportunidade permanece aberta no dataset mesmo após uma ação feita; pode reaparecer em outro dia, sem ser repetida no mesmo dia. Não inventar uma nova etapa comercial a partir do clique.

### Gamificação proporcional à tarefa

- Missões numeradas, barra segmentada, contador e breve feedback ao concluir.
- Meta diária inicial de dez ações únicas; se houver menos de dez oportunidades disponíveis no início do dia, usar essa quantidade como meta explícita.
- Sequência baseada em dias consecutivos com a meta atingida. Mais lotes no mesmo dia não geram dias extras. Dia sem oportunidades não gera uma conquista de meta; a regra de sequência usa datas consecutivas de metas efetivamente cumpridas.
- “Adiar”, visitar e concluir novamente a mesma ação não pontuam. Desfazer recalcula meta e sequência. Começar com histórico vazio, sem simular “7 dias seguidos”.
- Usar linguagem adulta e positiva. A conquista é cumprir a rotina de ações, sem afirmar que isso aumentou conversão. XP, níveis, medalhas e ranking de vendedores podem ser evoluções posteriores.

### Informação por oportunidade

- Conta ou “Conta não informada”, produto, vendedor e estágio.
- Score de prioridade de 0 a 100, identificado como índice operacional. O círculo da referência pode ser usado com o rótulo **“prioridade”**, substituindo “chance de fechar”.
- Tempo desde o engajamento, quando disponível.
- Dois ou três motivos produzidos pelo cálculo, com valores e tamanho das amostras. Barras mostram contribuição em pontos para o score; percentuais históricos, quando exibidos, precisam de rótulo e amostra próprios.
- Alertas de informação ausente e força da evidência histórica.
- Próxima ação curta: qualificar necessidade, confirmar situação atual ou revisar estratégia de uma oportunidade antiga.

Exemplo de linguagem, ainda sem valores reais de score: “O produto possui histórico suficiente; a conta não foi identificada; confirme quem decide a compra e se a oportunidade continua ativa.” Não afirmar que houve silêncio, proposta, reunião ou intenção urgente: esses eventos não existem nos CSVs.

As frases da referência “conta grande”, “você fecha 72% neste produto” e “sem contato há 6 dias” dependem de evidência específica. Tamanho de conta não aumenta prioridade automaticamente; estatística por vendedor/produto exige estudo, suavização e amostra; tempo desde o último contato não existe na base. Para o MVP, mostrar fatores do motor aprovado e fatos realmente conhecidos. Um preço exibido será **“Preço de catálogo”**, não valor negociado.

O dataset não fornece telefone ou URL de CRM. A ação principal disponível será “Copiar orientação”, acompanhada de “Feito” e “Adiar para amanhã”. Reservar “Abrir no CRM e ligar” para uma evolução com contato e integração reais.

### Superfícies secundárias

“Como priorizamos” abre página ou modal com metodologia, qualidade e avaliação histórica. Um detalhe adicional pode aprofundar o cálculo, acessível no próprio card, sem exigir navegação para entender a ação. Seleção de gestor/região e exportação CSV ficam em “Opções da equipe”; a visão gerencial inspeciona um vendedor por vez e não mistura conquistas de pessoas diferentes. A carteira completa pode ser uma evolução posterior.

### Escopo adicional somente depois do núcleo pronto

Hospedagem estática, comparação visual de métodos e breve gravação de demonstração. Um assistente generativo para resumir fatos estruturados pode ser uma evolução, mas não deve consumir o tempo da ingestão, explicação e avaliação.

## 6. Arquitetura para o novo repositório

**Stack proposta:** Vite, React, TypeScript, Tailwind e Vitest/Testing Library, aproveitando familiaridade com o CRM. Fixar versões e lockfile no novo projeto; não copiar indiscriminadamente todas as dependências atuais.

Processar os CSVs com scripts TypeScript executados por um runner apropriado, gerar JSONs estáticos e carregar os resultados no frontend. Para 8.800 oportunidades, não é necessário criar API, banco ou autenticação para demonstrar a solução.

Persistir seleção, lotes e ações no `localStorage`, com contrato versionado e namespace por versão do dataset e vendedor. Esse estado é local ao navegador: não comprova identidade, não sincroniza dispositivos e não atualiza o CRM. Documentar a limitação. Tratar armazenamento indisponível ou corrompido com fallback para a sessão e aviso discreto sobre a persistência.

```text
CSV originais → validação e aliases → joins preservando linhas
             → histórico elegível na data de corte → motor de prioridade
             → oportunidades + explicações + relatório de qualidade
             → fila diária do vendedor → lotes de até dez missões
             → aplicação React + registro local de ações/progresso
```

Separar módulos puros de ingestão, estatísticas, scoring, explicações e próxima ação. A explicação deve ser derivada dos mesmos fatores que calculam o score; não pedir a um LLM que invente uma justificativa depois.

Adicionar módulos puros para elegibilidade, composição de lotes, seleção, transições de missão e cálculo de progresso/sequência. Estados mínimos: `pending`, `completed` e `deferred`; a seleção é um `activeOpportunityId` independente. Registrar por ação `opportunityId`, `salesAgent`, `dayKey`, `status`, `completedAt` e `deferredUntil`, conforme aplicável, usando valores explícitos para ausência de data. Calcular “amanhã” pelo calendário operacional, não por adição de 24 horas a um timestamp.

**Dois relógios distintos:** scoring e idade usam `asOfDate` histórico, inicialmente `2017-12-31`; cabeçalho, conclusão, adiamento e sequência usam a data operacional real, em `America/Sao_Paulo`. Exibir a referência histórica discretamente e gerar dia da semana e saudação automaticamente, sem copiar a data fixa da imagem. Virada do dia renova a fila; recarregar no mesmo dia restaura o lote e seus estados. Reavaliar o dia também ao retornar à aba.

Estrutura sugerida no repositório independente:

```text
README.md
PLANO_CHALLENGE_003_LEAD_SCORER.md
referencias/
  lead-scorer-top10-referencia.png
solution/
  package.json
  package-lock.json
  data/raw/                   # CSVs originais e proveniência
  data/generated/             # qualidade, estatísticas e avaliação
  scripts/                    # prepare-data e evaluate
  src/domain/                 # tipos, datas, scoring, lotes e ações
  src/data/                   # dados preparados para o app
  src/components/             # DailyTopTen, MissionCard, CompactMission, DailyProgress
  src/state/                  # persistência local por vendedor/dataset
  tests/
docs/
  DATA.md
  SCORING.md
  VALIDATION.md
process-log/
  README.md
  decisions.md
  chat-exports/
  screenshots/
```

No fork oficial, essa estrutura inteira ficará dentro de `submissions/<seu-nome>/`. Os comandos deverão funcionar a partir de `solution/`, sem depender da raiz do repositório independente.

Registrar fonte, licença declarada, data de obtenção e hashes dos CSVs. Preferir incluir os CSVs permitidos pela licença para execução reproduzível, confirmando a licença na preparação. Não fazer o avaliador depender de uma conta Kaggle ou de um download em tempo de execução.

Comandos a implementar e documentar: `npm ci`, `npm run prepare:data`, `npm run evaluate`, `npm test`, `npm run build` e `npm run dev`. Não estão disponíveis neste momento; são contratos previstos para a execução.

## 7. Motor de priorização proposto

### Princípios

- Score de prioridade **não é probabilidade de fechamento**, nem receita esperada.
- Resultados Won/Lost podem alimentar estatísticas históricas de outros negócios, respeitando a data de corte. Não podem entrar como atributos da oportunidade avaliada.
- Não usar `close_value` da oportunidade como feature. Usar `close_date` para selecionar histórico e resultados de avaliação, nunca para calcular idade ou prioridade do negócio aberto.
- Manter Won/Lost fora das filas operacionais, sem score operacional.
- Ausência de dado exige fallback e sinalização; não equivale a desinteresse do cliente.
- Receita e tamanho da conta, escritório e desempenho do vendedor são hipóteses exploratórias, não sinais positivos automáticos. Inicialmente usar vendedor/manager/região para filtros.

### Primeira versão a validar

Combinar três componentes normalizados entre 0 e 1:

```text
priority_score = round(100 × (0,65 × H + 0,25 × A + 0,10 × V))
```

- **H — evidência histórica:** combinação inicial de taxas suavizadas por produto (50%), setor (30%) e conta (20%). Calcular somente sobre Won/Lost conhecidos na data de corte. Para segmentos ausentes, usar a taxa global elegível.
- **A — idade desde o engajamento:** comparar com duração típica histórica de negócios encerrados, usando estatísticas robustas e fallback global. Primeira regra candidata: `A = exp(-idade / (2 × mediana_do_ciclo))`; mediana zero ou sem histórico exige fallback seguro. Sem data, usar referência neutra de 0,5 e explicar a ausência.
- **V — valor de catálogo:** normalização logarítmica do preço positivo dentro do catálogo; sem preço, referência neutra de 0,5. É uma aproximação de valor unitário, não previsão de receita.

Os pesos e a regra de idade são **hipóteses de implementação**, não conclusões demonstradas. Fixá-los antes da avaliação final; alterá-los somente com análise em cortes anteriores, documentando a decisão. Testar também a versão sem V e sem idade para identificar se esses componentes realmente ajudam.

Suavização proposta para cada grupo:

```text
taxa_grupo = (vitórias_grupo + 20 × taxa_global) / (encerrados_grupo + 20)
```

O parâmetro 20 é uma escolha inicial de regularização. Exibir contagem e taxa usada, sem confundir tamanho da amostra com confiança estatística calibrada. Não transformar 3 vitórias em 3 negócios em uma promessa de 100% de chance.

Explicar o resultado com a contribuição ponderada de cada componente. Guardar versão da regra, data de referência, dados ausentes e origem dos fallbacks. Usar ID da oportunidade como desempate estável.

**Atenção:** oportunidade antiga pode merecer revisão, não insistência automática. A ação sugerida deve ser “confirmar situação e atualizar o pipeline”, sem afirmar que idade causa perda. Prospecting participa do Top 10 com fallback de idade e ação de qualificação, deixando explícita a ausência de evidência de engajamento. A gamificação e a seleção do card não alteram o score comercial; adiamento muda elegibilidade/data de retorno, não probabilidade ou estágio.

## 8. Validação histórica possível e seus limites

Uma consulta inicial confirmou a viabilidade do seguinte corte:

| Recorte | Quantidade |
| --- | ---: |
| Encerrados até `2017-09-30`, para estatísticas | 4.726 |
| Já engajados e ainda abertos em `2017-09-30`, reconstruídos pelas datas | 2.409 |
| Desses, encerrados no quarto trimestre | 935 |
| Resultados desses 935 | 559 Won e 376 Lost |
| Sem resultado conhecido até `2017-12-31` nesse conjunto | 1.474 |

### Procedimento

1. Congelar pesos e regras. Gerar estatísticas somente de negócios com fechamento até `2017-09-30`.
2. Reconstruir candidatos com `engage_date <= corte` e `close_date > corte` ou ausente. O estágio histórico desses candidatos será **Engaging**, inclusive se hoje aparecem como Won/Lost.
3. Calcular idade na data do corte. Excluir totalmente resultado futuro do contrato de scoring.
4. Avaliar os resultados conhecidos até `2017-12-31`, separando os 1.474 casos ainda sem desfecho. Eles são censurados, não Lost.
5. Comparar com preço de catálogo, engajamento mais recente e ranking aleatório com seed fixa. Reportar casos em que o motor perde para uma referência.

Reportar taxa de Won entre os negócios resolvidos no top K, lift em relação aos resolvidos elegíveis e captura de Won no horizonte. Para o top K da **fila completa**, mostrar separadamente Won, Lost e sem resultado; Won/K representa vitória observada no período, não precisão eventual. **K=10 por vendedor é a métrica principal**, alinhada ao produto; apresentar também 20 e 50 quando houver volume. Avaliar ranking e cobertura antes das ações locais: conclusões de missões são comportamento de uso, não resultados comerciais. A política de retorno dos adiados não está validada pelo backtest e precisa de teste operacional próprio.

Essa avaliação é parcial: não sabemos quando os campos de conta foram preenchidos, não temos snapshots de cadastro, atividades nem transições completas. Metadados atuais são proxies. O backtest não valida Prospecting, porque não existe data de criação que permita reconstruí-lo. A comparação somente entre resolvidos tem viés de seleção; declarar isso junto às métricas.

Não prometer melhoria de conversão, receita incremental ou ganho causal. Uma avaliação desfavorável deve levar à simplificação do score ou a uma conclusão honesta sobre falta de sinal, não à fabricação de resultados.

## 9. Testes e critérios de aceite

### Cobertura automatizada prevista

- Ingestão mantém 8.800 IDs únicos e preserva linhas sem conta.
- Alias `GTXPro → GTX Pro` resolve os 1.480 vínculos sem alterar IDs.
- Join de produto, vendedor e conta preserva cardinalidade e reporta vínculos desconhecidos.
- Datas históricas usam referência fixa; data ausente permanece desconhecida.
- Score é finito, limitado a 0–100 e reproduzível; explicações correspondem aos fatores usados.
- Alterar `close_value` ou resultado futuro de um candidato não muda seu score no corte histórico.
- Negócios fechados depois do corte não afetam estatísticas daquele corte.
- Fila operacional exclui Won/Lost; Prospecting e Engaging permanecem elegíveis com explicações adequadas.
- Amostra pequena, produto desconhecido e setor/conta ausentes acionam fallbacks documentados.
- Top 10 pertence ao vendedor escolhido, respeita ranking estável e carrega até dez IDs únicos.
- Seleção mantém somente um card expandido e distribui pendentes anteriores acima e seguintes abaixo, sem concluir nem reordenar oportunidades.
- “Feito” é idempotente, atualiza progresso uma única vez e não altera Won/Lost; desfazer reverte ação, meta e sequência.
- Desfazer conclusão ou adiamento após avanço de lote devolve a missão à fila sem perder o ID, duplicá-lo ou exceder dez cards no lote corrente.
- Adiar exclui do dia, retorna na data correta e não conta como conclusão ou conquista.
- Esgotar pendentes carrega o próximo lote automaticamente, sem repetir feitos/adiados; validar também lote final menor, todos adiados e carteira vazia.
- Trocar vendedor e versão do dataset isola histórico; recarregar restaura lote, conclusão, seleção e adiamentos.
- Virada do dia em `America/Sao_Paulo`, inclusive retorno à aba, renova a fila sem alterar a referência histórica do scoring.
- Sequência usa dias efetivos de meta cumprida, sem recompensa extra por lotes, cliques repetidos ou seleção.
- Falha de armazenamento tem fallback; keyboard/foco, estado dos segmentos e movimento reduzido funcionam.
- Método, opções de equipe e CSV correspondem ao recorte do vendedor; link externo só existe com destino real configurado.

### Aceite da entrega

Em checkout limpo, o avaliador consegue instalar, preparar dados, testar, compilar e abrir a aplicação seguindo o README. Seleciona um vendedor, recebe até dez missões, expande um card da fila e encontra os anteriores recolhidos acima. Conclui e adia ações, vê progresso correto, recebe o próximo lote automaticamente e recupera os estados ao recarregar. A tela mostra a referência histórica, explica um negócio com cadastro incompleto e oferece uma próxima ação coerente. Há relatório de qualidade, avaliação com limitações e process log verificável.

Não executar testes contra Supabase, n8n ou clientes do CRM. Por ser planejamento documental, testes do CRM não foram executados nesta etapa.

## 10. Sequência de execução em até 6 horas

| Tempo | Trabalho | Saída verificável |
| --- | --- | --- |
| 0:00–0:20 | Criar projeto e process log; trazer dados e registrar fonte/hashes | Estrutura reproduzível |
| 0:20–1:00 | Parser, alias, joins, datas e relatório de qualidade | Contagens e integridade verificadas |
| 1:00–2:00 | Motor, explicações, elegibilidade/lotes e testes centrais | Scores reproduzíveis e Top 10 correto |
| 2:00–3:25 | Tela diária, expansão dos cards, feito/adiar e persistência | Jornada de missões funcional |
| 3:25–4:15 | Corte temporal, referências e relatório de avaliação | Evidência de desempenho e limitações |
| 4:15–5:00 | Progresso/sequência, lotes seguintes, casos limite e build | Fluxo completo verificado |
| 5:00–6:00 | README, process log, capturas e montagem da submissão | Pacote revisável e instruções testadas |

Registrar o tempo efetivamente gasto, incluindo análise prévia. Se houver atraso, cortar assistente generativo, gráficos adicionais, exportação/opções gerenciais e hospedagem. Preservar dados reais, motor, explicação, Top 10, expansão dos cards, feito/adiar, novos lotes, progresso, persistência, testes essenciais e evidências. Implementar sequência com cálculo simples sobre os registros existentes, sem infraestrutura adicional de gamificação.

## 11. Evidências e narrativa do candidato

A apresentação pode conectar a experiência anterior à proposta: “No CRM imobiliário, aprendi a transformar sinais comerciais em próxima ação. Aqui adaptei esse princípio para oportunidades B2B, respeitando os dados disponíveis e verificando o ranking.” Complementar com exemplos reais da execução, sem alegar resultados ainda não medidos.

Para cada etapa do process log, registrar: objetivo, pedido à IA, saída recebida, verificação, correção ou decisão humana e link para evidência/commit. Guardar esta conversa como análise inicial quando for exportada; este plano sozinho não substitui as evidências de implementação.

Decisões já fundamentadas para registrar:

- Separar desenvolvimento independente de submissão oficial via PR.
- Adaptar a experiência de produto do CRM e criar scoring adequado ao dataset.
- Corrigir o alias de produto identificado na leitura real dos CSVs.
- Não tratar cadastro completo como preditor confiável diante da distribuição observada.
- Usar data histórica, excluir resultados futuros e distinguir censura de perda.
- Priorizar explicações e validação antes de adicionar IA generativa à interface.
- Substituir a visão de carteira completa por missões em lotes de dez, seguindo a nova referência visual.
- Manter seleção separada de conclusão e distinguir adiamento de conquista.
- Separar calendário operacional real de referência histórica do score.

## 12. Pendências para iniciar a implementação

- Preencher nome, usuário GitHub e LinkedIn na submissão.
- Confirmar prazo recebido por e-mail; o orçamento do repositório não substitui instruções individuais do recrutamento.
- Confirmar licença e congelar a versão dos arquivos ao trazê-los para o novo projeto.
- Verificar se a primeira versão do score supera as referências e ajustar somente com validação anterior ao corte final.
- Decidir hospedagem depois de o fluxo local estar pronto.
- Incluir a pasta `referencias/` ao transportar este plano, preservando a imagem escolhida.

**Próximo passo:** levar este arquivo ao novo repositório e executar primeiro a preparação dos dados e os testes de integridade. O primeiro marco é um conjunto de oportunidades corretamente ligado e auditável; então construir o ranking e a interface.
