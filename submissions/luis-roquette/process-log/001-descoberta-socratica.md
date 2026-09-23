# Diário de processo: descoberta socrática

- **Início:** 21 de setembro de 2026
- **Estado:** exploração, `add-task`, especificação e planejamento concluídos; implementação autorizada
- **SPEC:** draft criado após a aprovação integral do desenho

## Protocolo de registro

Cada pergunta e resposta será registrada durante a sessão. A resposta literal de Luis será preservada; interpretação e consequência serão descritas separadamente, em português revisado. Nenhuma interpretação será apresentada como decisão humana sem confirmação.

## Onda 1: problema, decisão e usuário

### Pergunta 1

Qual deve ser a decisão principal que o CEO conseguirá tomar após cinco minutos com nossa entrega?

- A. Onde investir para reduzir churn de receita.
- B. Quais contas o CS deve abordar imediatamente.
- C. Qual problema de produto ou suporte corrigir primeiro.

### Resposta de Luis

> C

### Interpretação

A entrega deve ajudar o CEO a escolher qual problema sistêmico de produto ou suporte merece correção prioritária. O centro da solução será a causa raiz e a decisão de intervenção, não apenas uma previsão de churn ou uma fila de contas.

### Consequência para o desenho

Precisaremos comparar problemas concorrentes por evidência, receita exposta, quantidade de contas afetadas e possibilidade de ação. A lista de contas em risco continua obrigatória pelo briefing, mas funcionará como evidência e instrumento operacional da recomendação principal.

### Ponto ainda aberto

Ainda não sabemos se devemos começar com uma hipótese sobre a área responsável ou deixar os dados escolherem entre produto, suporte e fatores comerciais.

### Pergunta 2

Devemos iniciar sem uma área culpada e deixar os dados escolherem?

- A. Sim: produto, suporte, cobrança/plano e aquisição competem igualmente.
- B. Produto deve ser a hipótese principal.
- C. Suporte deve ser a hipótese principal.
- D. Cobrança, plano ou contrato deve ser a hipótese principal.

### Resposta de Luis

> A

### Interpretação

A investigação começa com tese zero. Nenhuma área será favorecida antes da análise; produto, suporte, cobrança/plano e aquisição competirão pela força da evidência.

### Consequência para o desenho

A solução precisará aplicar critérios comparáveis às causas candidatas e mostrar evidências contrárias, não somente as que confirmam a narrativa vencedora. Isso reduz o risco de adaptar os dados a uma hipótese escolhida cedo demais.

### Ponto ainda aberto

Precisamos definir como priorizar uma causa quando quantidade de contas afetadas e receita exposta apontarem para direções diferentes.

### Pergunta 3

Quando quantidade de contas e receita exposta apontarem para causas diferentes, como devemos priorizar?

- A. Maior receita mensal exposta.
- B. Maior quantidade de contas afetadas.
- C. Matriz multicritério: receita, contas, confiança da evidência e possibilidade de ação.
- D. Dois rankings separados, sem prioridade final única.

### Resposta de Luis

> C

### Interpretação

A prioridade não será definida por uma única métrica. Cada causa candidata será avaliada por impacto financeiro, alcance entre contas, confiança da evidência e viabilidade de intervenção.

### Consequência para o desenho

A solução deverá mostrar as dimensões separadamente e explicar qualquer síntese de prioridade. Pesos e thresholds não poderão parecer precisão científica se forem escolhas de negócio; precisarão estar visíveis e passar por análise de sensibilidade.

### Ponto ainda aberto

Precisamos definir o horizonte da recomendação: resposta imediata, correção estrutural ou sequência das duas.

### Pergunta 4

Qual horizonte deve orientar a recomendação principal?

- A. Ação emergencial executável em até uma semana.
- B. Correção estrutural para os próximos 30–90 dias.
- C. Sequência das duas: contenção imediata seguida da correção estrutural.
- D. Estratégia anual de retenção.

### Resposta de Luis

> C

### Interpretação

A recomendação deverá operar em duas velocidades. Primeiro, uma contenção que reduza exposição imediata; depois, uma correção estrutural que remova ou reduza a causa sistêmica.

### Consequência para o desenho

Cada causa prioritária precisará de duas ações conectadas: uma medida de curto prazo, executável em até uma semana, e uma iniciativa de 30–90 dias com responsável, métrica e resultado esperado. A contenção não poderá ser apresentada como solução definitiva.

### Ponto ainda aberto

Precisamos escolher qual artefato apresentará essa decisão ao CEO primeiro, antes dos detalhes analíticos e operacionais.

### Pergunta 5

Qual artefato o CEO deve encontrar primeiro?

- A. Memorando executivo de uma página com causa e decisão recomendada.
- B. Dashboard interativo com filtros e comparações.
- C. Fila operacional de contas e ações para o CS.
- D. Entrega em camadas: decisão executiva primeiro, dashboard como evidência e fila de contas para execução.

### Resposta de Luis

> D

### Interpretação

A entrega atenderá três níveis de leitura sem obrigar o CEO a percorrer detalhes técnicos: decisão executiva primeiro, evidência explorável para verificação e fila operacional para transformar a recomendação em ação.

### Consequência para o desenho

As três camadas deverão compartilhar a mesma fonte de dados e os mesmos critérios. Não serão três produtos independentes. A arquitetura deverá permitir leitura progressiva, evitando números ou prioridades divergentes entre resumo, dashboard e fila de contas.

## Síntese provisória da Onda 1

- **Decisão principal:** escolher qual problema sistêmico corrigir primeiro.
- **Postura analítica:** tese zero; nenhuma área começa favorecida.
- **Priorização:** matriz transparente de impacto, alcance, confiança e possibilidade de ação.
- **Horizonte:** contenção em até uma semana e correção estrutural em 30–90 dias.
- **Entrega:** decisão executiva, dashboard de evidências e fila operacional conectados.

### Estado da onda

Síntese confirmada por Luis sem ajustes. A Onda 1 está encerrada.

## Onda 2: sucesso, evidências e prioridades mensuráveis

### Pergunta 1

Qual nível mínimo de evidência devemos exigir antes de apresentar um fator como provável causa raiz do churn?

- A. Diferença descritiva relevante entre clientes que cancelaram e clientes que permaneceram.
- B. Associação que continue relevante após controlar diferenças de segmento, plano e valor da conta.
- C. Convergência de três sinais: associação controlada, coerência temporal e confirmação em mais de uma tabela, deixando explícito que dados observacionais não provam causalidade.
- D. Somente um experimento controlado permite mencionar causa raiz; sem ele, não faremos recomendação causal.

**Recomendação técnica preliminar do agente:** C, porque oferece rigor compatível com dados observacionais sem prometer uma causalidade que o dataset não consegue provar sozinho.

### Estado da pergunta

Respondida por Luis.

### Resposta de Luis

> C

### Interpretação

Um fator somente poderá ser apresentado como provável causa raiz quando três tipos de evidência convergirem: associação que resista aos principais controles disponíveis, precedência temporal compatível e confirmação por sinais de tabelas diferentes.

### Consequência para o desenho

O relatório separará fato, associação e hipótese causal. Cada conclusão principal deverá exibir os controles aplicados, a sequência temporal observada e as fontes que a sustentam. Como os dados são observacionais, a linguagem não poderá afirmar causalidade comprovada; recomendações estruturais deverão incluir uma forma posterior de validação experimental ou quase experimental.

### Ponto ainda aberto

Precisamos definir qual resultado de negócio terá precedência ao medir risco, priorizar intervenções e avaliar sucesso.

### Pergunta 2

Qual deve ser a métrica principal de sucesso da estratégia de retenção?

- A. Redução da quantidade de contas canceladas, independentemente do valor.
- B. Redução do MRR perdido por churn, independentemente da quantidade de contas.
- C. MRR perdido como métrica principal, com quantidade de contas e concentração por segmento como métricas de proteção.
- D. Acurácia do modelo preditivo, mesmo sem comprovação de impacto financeiro.

**Recomendação técnica preliminar do agente:** C, porque protege receita sem esconder um problema disseminado entre contas menores ou concentrado em um segmento específico.

### Estado da pergunta 2

Respondida por Luis.

### Resposta de Luis

> C

### Interpretação

A estratégia será avaliada principalmente pela redução do MRR perdido por churn. A quantidade de contas afetadas e a concentração do resultado por segmento funcionarão como métricas de proteção para evitar que a otimização financeira esconda deterioração ampla ou desigual.

### Consequência para o desenho

Resumo executivo, dashboard e fila operacional usarão a mesma hierarquia de métricas: MRR perdido como resultado principal; churn de contas e distribuição por segmento como proteções obrigatórias. Acurácia preditiva será uma métrica técnica auxiliar, nunca substituta do impacto de negócio.

### Ponto ainda aberto

Precisamos transformar impacto, alcance, confiança e possibilidade de ação em uma regra de prioridade verificável, sem produzir uma pontuação arbitrária com aparência científica.

### Pergunta 3

Como devemos ordenar as causas candidatas e as intervenções?

- A. Soma ponderada fixa das quatro dimensões, usando pesos definidos antecipadamente.
- B. Ordenação apenas pelo MRR total exposto, depois de atingido um nível mínimo de evidência.
- C. Portão mínimo de confiança; depois, ordenação pelo MRR realisticamente recuperável, com alcance e possibilidade de ação como desempate e análise de sensibilidade.
- D. Ranking produzido por IA sem fórmula fixa, acompanhado de uma justificativa em texto.

**Recomendação técnica preliminar do agente:** C, porque elimina hipóteses frágeis antes do ranking e prioriza valor recuperável, não apenas exposição bruta, mantendo os critérios auditáveis.

### Estado da pergunta 3

Respondida por Luis.

### Resposta de Luis

> C

### Interpretação

A prioridade será definida em duas etapas. Primeiro, hipóteses frágeis serão eliminadas por um nível mínimo de confiança. Entre as hipóteses restantes, o MRR realisticamente recuperável orientará a ordem; alcance e possibilidade de ação funcionarão como desempate, com análise de sensibilidade para testar a estabilidade do ranking.

### Consequência para o desenho

A solução não usará uma nota única opaca. Ela mostrará quais causas passaram pelo portão de evidência, como o valor recuperável foi estimado e se a prioridade muda quando premissas razoáveis variam. Exposição bruta e recuperação esperada serão métricas distintas.

### Ponto ainda aberto

O dataset não contém o resultado futuro das intervenções propostas. Precisamos decidir como estimar MRR recuperável sem apresentar suposições como fatos.

### Pergunta 4

Como devemos estimar o MRR recuperável quando não há histórico confiável das intervenções propostas?

- A. Considerar recuperável todo o MRR exposto ao fator de risco.
- B. Aplicar uma única taxa de recuperação escolhida pelo time e apresentar o resultado pontual.
- C. Apresentar cenários conservador, base e otimista, com premissas explícitas, intervalo de impacto e separação entre dado observado e estimativa.
- D. Pedir que um modelo de IA estime a taxa de recuperação a partir dos textos de feedback.

**Recomendação técnica preliminar do agente:** C, porque permite decidir sob incerteza sem transformar uma premissa não observada em falsa precisão.

### Estado da pergunta 4

Respondida por Luis.

### Resposta de Luis

> A

### Interpretação

Para fins de priorização, todo o MRR exposto ao fator de risco será inicialmente considerado recuperável. Portanto, o valor usado no ranking corresponderá à oportunidade financeira bruta associada à causa, sem desconto por probabilidade de sucesso da intervenção.

### Consequência para o desenho

Essa escolha simplifica o cálculo e evita taxas de recuperação inventadas, mas cria uma premissa forte que os dados não comprovam. O valor não poderá ser tratado silenciosamente como impacto esperado. O relatório deverá tornar explícito que se trata de um teto teórico, sujeito à sobreposição entre causas e à impossibilidade prática de recuperar toda a receita exposta.

### Ponto ainda aberto

Precisamos definir o nome e o tratamento visual desse valor para que o CEO não interprete a oportunidade máxima como previsão de recuperação.

### Pergunta 5

Como esse valor deve aparecer na entrega?

- A. “MRR recuperável projetado”, sem ressalva adicional.
- B. “MRR exposto — oportunidade máxima”, separado de impacto esperado e acompanhado das limitações.
- C. “Impacto financeiro da recomendação”, usando o mesmo valor no resumo executivo.
- D. Mostrar apenas a quantidade de contas e omitir o valor financeiro.

**Recomendação técnica preliminar do agente:** B, porque preserva sua decisão de usar 100% do MRR exposto no ranking sem transformar um limite superior em promessa de resultado.

### Estado da pergunta 5

Respondida por Luis.

### Resposta de Luis

> B

### Interpretação

O valor financeiro será apresentado como **“MRR exposto — oportunidade máxima”**. Ele representará o limite superior de receita associado ao fator de risco, não uma previsão de recuperação.

### Consequência para o desenho

O rótulo, a definição e as limitações acompanharão o valor no resumo executivo e no dashboard. A entrega não usará “MRR recuperável” nem “impacto esperado” para esse cálculo. Esta decisão refina a resposta anterior: o ranking usará exposição financeira bruta com nome honesto, e não recuperação estimada.

## Síntese provisória da Onda 2

- **Padrão de evidência:** associação controlada, coerência temporal e confirmação entre tabelas; sem alegar causalidade comprovada.
- **Métrica principal:** redução do MRR perdido, protegida por churn de contas e concentração por segmento.
- **Regra de prioridade:** portão mínimo de confiança; depois, MRR exposto, alcance e possibilidade de ação, com análise de sensibilidade.
- **Estimativa financeira:** 100% do MRR exposto entra como oportunidade bruta, sem taxa presumida de recuperação.
- **Comunicação:** o valor será chamado de “MRR exposto — oportunidade máxima”, nunca de impacto esperado.

### Estado da onda

Síntese confirmada por Luis sem ajustes. A Onda 2 está encerrada.

## Onda 3: dados, tempo, unidade de análise e prevenção de vazamentos

### Pergunta 1

Qual deve ser a unidade principal da análise de risco e causa raiz?

- A. Uma linha por conta, resumindo toda a história disponível.
- B. Uma linha por assinatura, mesmo quando uma conta possui várias assinaturas.
- C. Uma linha por conta em cada data de corte, agregando apenas assinaturas, uso e suporte conhecidos até aquele momento.
- D. Uma linha por evento de uso, deixando o modelo combinar os eventos diretamente.

**Recomendação técnica preliminar do agente:** C, porque preserva a decisão no nível da conta, permite observar mudanças ao longo do tempo e impede que informações posteriores ao corte contaminem a análise.

### Estado da pergunta 1

Respondida por Luis.

### Resposta de Luis

> C

### Interpretação

A base analítica será estruturada como um painel de **conta × data de corte**. Em cada corte, atributos de assinatura, uso e suporte serão agregados no nível da conta usando somente informações que já existiam naquele momento.

### Consequência para o desenho

Junções e atributos deverão respeitar o tempo. Eventos de churn, feedback posterior ao cancelamento e qualquer dado gerado após a data de corte não poderão entrar como preditores. Múltiplas assinaturas serão consolidadas de forma documentada, preservando métricas como MRR total, plano e frequência de cobrança.

### Ponto ainda aberto

Assinaturas mensais e anuais possuem ritmos diferentes de decisão. Precisamos definir um horizonte operacional comparável sem ignorar as janelas de renovação.

### Pergunta 2

Como devemos definir o horizonte de risco para assinaturas mensais e anuais?

- A. Prever churn nos próximos 30 dias para todas as contas.
- B. Prever churn nos próximos 90 dias para todas as contas.
- C. Usar 30 dias como horizonte operacional comum e acrescentar uma visão específica da janela de renovação para contratos anuais.
- D. Usar 30 dias para mensais e 365 dias para anuais, comparando os riscos diretamente.

**Recomendação técnica preliminar do agente:** C, porque mantém uma fila operacional comparável e, ao mesmo tempo, evita tratar uma conta anual distante da renovação como se tivesse a mesma oportunidade imediata de churn.

### Estado da pergunta 2

Respondida por Luis.

### Resposta literal de Luis

> c

### Interpretação

A resposta corresponde à opção **C**. Todas as contas terão uma visão operacional de risco nos próximos 30 dias. Contratos anuais também terão uma leitura específica de proximidade e risco na janela de renovação.

### Consequência para o desenho

A fila operacional continuará comparável entre contas, mas o dashboard não misturará risco imediato com risco de renovação anual. Frequência de cobrança e distância até a renovação deverão aparecer como contexto obrigatório na análise e nos controles estatísticos.

### Ponto ainda aberto

Precisamos escolher quanto histórico anterior a cada corte será usado para distinguir nível atual, deterioração recente e padrão persistente.

### Pergunta 3

Quais janelas de observação devem gerar os sinais de uso e suporte?

- A. Somente os 30 dias anteriores ao corte.
- B. Todo o histórico disponível até o corte.
- C. Janelas de 7, 30 e 90 dias, comparando nível, tendência e volatilidade, desde que a cobertura real dos dados sustente cada janela.
- D. Eventos brutos, sem agregação temporal, entregues diretamente a um modelo.

**Recomendação técnica preliminar do agente:** C, porque separa choque recente de deterioração gradual e comportamento persistente, sem usar uma janela que os dados não consigam preencher.

### Estado da pergunta 3

Respondida por Luis.

### Resposta literal de Luis

> c

### Interpretação

A resposta corresponde à opção **C**. Sinais de uso e suporte serão calculados em janelas de 7, 30 e 90 dias anteriores a cada corte, permitindo comparar estado recente, tendência e persistência. Uma janela só será usada se a cobertura efetiva dos dados for suficiente.

### Consequência para o desenho

Os atributos deverão distinguir volume, taxa, tendência e volatilidade, sem confundir ausência de histórico com valor zero. A auditoria inicial dos dados poderá reduzir ou remover uma janela, mas não substituí-la silenciosamente; qualquer adaptação será registrada.

### Ponto ainda aberto

O arquivo de churn contém motivo e feedback que podem ter sido registrados após a decisão de cancelar. Precisamos separar seu uso retrospectivo do uso preditivo.

### Pergunta 4

Como devemos usar `reason_code` e o texto de feedback dos eventos de churn?

- A. Como atributos do modelo de risco e como evidência do diagnóstico.
- B. Excluí-los completamente para evitar qualquer contaminação.
- C. Usá-los somente no diagnóstico retrospectivo e na triangulação das causas; nunca como atributos de previsão anteriores ao churn.
- D. Usá-los no modelo desde que os textos sejam anonimizados.

**Recomendação técnica preliminar do agente:** C, porque esses campos ajudam a explicar cancelamentos já ocorridos, mas revelam informação indisponível no momento em que uma conta ainda poderia ser salva.

### Estado da pergunta 4

Respondida por Luis.

### Resposta de Luis

> C

### Interpretação

`reason_code` e feedback textual serão usados para explicar churn já ocorrido e triangular hipóteses com sinais anteriores. Eles serão proibidos na construção de atributos, escores ou rankings destinados a prever quais contas ainda ativas podem cancelar.

### Consequência para o desenho

O pipeline deverá separar explicitamente conjuntos de campos retrospectivos e preditivos. Testes de contrato verificarão que colunas geradas no evento ou após o cancelamento não entram na matriz de atributos anterior ao corte.

### Ponto ainda aberto

Além das colunas, a divisão entre treino e avaliação também pode vazar contas ou padrões futuros. Precisamos definir uma validação compatível com o uso real.

### Pergunta 5

Como devemos validar um eventual modelo de risco?

- A. Divisão aleatória entre linhas do painel, permitindo que datas da mesma conta apareçam em treino e teste.
- B. Divisão aleatória por conta, ignorando a ordem temporal.
- C. Avaliação fora do tempo, mantendo contas agrupadas e usando backtests temporais adicionais se houver cortes suficientes.
- D. Treinar com todos os dados e apresentar somente o desempenho dentro da própria amostra.

**Recomendação técnica preliminar do agente:** C, porque reproduz a previsão do futuro e impede que a mesma conta ensine ao modelo padrões que depois reaparecem no teste.

### Estado da pergunta 5

Respondida por Luis.

### Resposta de Luis

> C

### Interpretação

O desempenho será medido em períodos posteriores aos usados no treinamento. As contas permanecerão agrupadas para impedir que observações da mesma empresa atravessem indevidamente treino e teste. Se a quantidade de datas de corte permitir, backtests temporais adicionais testarão a estabilidade.

### Consequência para o desenho

Divisões aleatórias entre linhas e métricas calculadas na amostra de treino serão proibidas como evidência de desempenho. A avaliação deverá registrar datas, contas, prevalência de churn e métricas operacionais, sempre no conjunto fora do tempo.

## Síntese provisória da Onda 3

- **Unidade:** painel de conta × data de corte, usando apenas informação conhecida naquele momento.
- **Horizonte:** risco operacional em 30 dias, com visão adicional da janela de renovação anual.
- **Observação:** janelas de 7, 30 e 90 dias para nível, tendência e volatilidade, condicionadas à cobertura real.
- **Campos pós-churn:** `reason_code` e feedback somente no diagnóstico retrospectivo, nunca como preditores.
- **Validação:** avaliação fora do tempo, contas agrupadas e backtests temporais quando a amostra permitir.

### Estado da onda

Síntese confirmada por Luis sem ajustes. A Onda 3 está encerrada.

## Onda 4: arquitetura mínima, artefatos, automação e experiência de uso

### Gate de pesquisa externa antes da arquitetura

Antes de propor componentes, revisitamos soluções públicas atuais que cobrem partes do problema:

- [`profpius/customer-churn-prediction`](https://github.com/profpius/customer-churn-prediction): pipeline local, scoring em lote, Streamlit e explicações SHAP; serve como referência para separar processamento, modelo e interface.
- [`PrajwalShekar22/customer-360-revenue-intelligence`](https://github.com/PrajwalShekar22/customer-360-revenue-intelligence): combina análise de receita, risco, planejamento de ações, tabelas de saída e Streamlit; é a referência mais próxima da entrega em camadas definida nas ondas anteriores.
- [`Augusto-98/churn_llm_explainer`](https://github.com/Augusto-98/churn_llm_explainer): demonstra explicação por cliente e interface Streamlit, mas a dependência de API paga de IA será rejeitada por padrão; o padrão visual pode ser reaproveitado sem essa chamada.
- Relatos no Reddit reforçam que mostrar métricas sem recomendar ações não resolve o trabalho operacional. São sinais qualitativos, não validação técnica.

Nenhum repositório será copiado integralmente. A pesquisa valida padrões de solução; código só será reutilizado após verificação de licença, qualidade, compatibilidade com os cinco datasets e ausência de vazamento temporal.

### Aplicação do Ponytail

A menor solução que atende às três camadas parece ser um pipeline Python reproduzível que grava saídas tabulares, um relatório executivo em Markdown e uma aplicação Streamlit que lê essas mesmas saídas. API, banco, autenticação e serviços separados não têm necessidade demonstrada neste desafio.

### Pergunta 1

Qual arquitetura deve orientar a entrega?

- A. Somente notebook e relatório estático, sem interface operacional.
- B. Pipeline Python único → arquivos tabulares versionáveis → relatório Markdown + dashboard Streamlit + fila CSV, todos derivados das mesmas saídas.
- C. API FastAPI, banco PostgreSQL, frontend React e serviço separado de modelo.
- D. Dashboard em ferramenta proprietária de BI, com transformação manual dos dados.

**Recomendação técnica preliminar do agente:** B, porque reutiliza um padrão recorrente nas soluções pesquisadas, satisfaz as três camadas e evita infraestrutura que não melhora o diagnóstico.

### Estado da pergunta 1

Respondida por Luis.

### Resposta de Luis

> B

### Interpretação

A solução terá um único pipeline Python como fonte dos artefatos. Ele produzirá tabelas reutilizáveis; o relatório em Markdown, o dashboard Streamlit e a fila CSV consumirão essas mesmas saídas, evitando cálculos divergentes entre as três camadas.

### Consequência para o desenho

API, banco de dados, autenticação, frontend separado e chamadas pagas de IA ficam fora do escopo inicial. Só serão reconsiderados se um requisito posterior não puder ser satisfeito com arquivos locais e execução reproduzível.

### Ponto ainda aberto

O repositório não possui task runner, ambiente Python ou automação existentes para reutilizar. Precisamos escolher o menor contrato de execução que permita ao avaliador reproduzir os resultados.

### Pergunta 2

Como o avaliador deve executar e reproduzir a solução?

- A. Abrir o notebook e executar manualmente todas as células na ordem indicada.
- B. Usar `make reproduce` para validar dados e regenerar os artefatos, e `make app` para abrir o dashboard, com comandos Python simples por baixo.
- C. Subir vários serviços com Docker Compose antes de executar a análise.
- D. Acessar somente uma versão hospedada, sem caminho local reproduzível.

**Recomendação técnica preliminar do agente:** B, porque oferece uma porta de entrada curta e auditável sem adicionar um orquestrador ou infraestrutura permanente.

### Estado da pergunta 2

Respondida por Luis.

### Resposta de Luis

> B

### Interpretação

O contrato de execução terá duas entradas curtas: `make reproduce` validará os dados e regenerará todos os artefatos; `make app` abrirá o dashboard usando as saídas já produzidas. Os alvos apenas encapsularão comandos Python explícitos.

### Consequência para o desenho

O processo não dependerá da ordem manual de células nem de serviços externos. O README deverá informar pré-requisitos, comandos, entradas, saídas e falhas esperadas. Cada execução deverá produzir resultados determinísticos com os mesmos dados e versões de dependências.

### Ponto ainda aberto

Precisamos definir a navegação do dashboard sem duplicar o relatório ou transformar a solução em uma vitrine técnica extensa.

### Pergunta 3

Como o dashboard deve organizar a leitura?

- A. Uma única página longa com todos os gráficos, tabelas e métricas.
- B. Três visões: decisão executiva, evidências por causa e segmento, e fila de contas; metodologia fica em um painel recolhível.
- C. Sete ou mais abas separadas por dataset, algoritmo e métrica técnica.
- D. Uma interface de chat como navegação principal.

**Recomendação técnica preliminar do agente:** B, porque espelha as três camadas já aprovadas, reduz carga cognitiva e mantém detalhes metodológicos disponíveis sem competir com a decisão.

### Estado da pergunta 3

Respondida por Luis.

### Resposta literal de Luis

> b

### Interpretação

A resposta corresponde à opção **B**. O dashboard terá três visões alinhadas ao fluxo de decisão: resumo executivo, evidências por causa e segmento, e fila operacional de contas. Definições, limitações e validações ficarão acessíveis em um painel metodológico recolhível.

### Consequência para o desenho

Cada visual deverá responder a uma pergunta concreta e compartilhar filtros e métricas com as outras visões. Abas por dataset, catálogo de modelos e chat ficam fora do escopo inicial porque não melhoram diretamente a decisão aprovada.

### Ponto ainda aberto

A fila operacional precisa sair da tela e chegar ao trabalho diário do CS, mas ainda não há CRM ou canal externo autorizado no desafio.

### Pergunta 4

Qual deve ser a automação inicial da fila de Customer Success?

- A. Exibir a tabela apenas no dashboard, sem exportação.
- B. Gerar um CSV baixável com conta, prioridade, MRR exposto, sinais, ação imediata, ação estrutural e campos vazios de responsável e status.
- C. Integrar diretamente com um CRM e criar tarefas automaticamente.
- D. Enviar mensagens automáticas aos clientes classificados como alto risco.

**Recomendação técnica preliminar do agente:** B, porque entrega um artefato utilizável amanhã sem pressupor CRM, credenciais ou autorização para contatar clientes.

### Estado da pergunta 4

Respondida por Luis.

### Resposta de Luis

> B

### Interpretação

A primeira automação será uma fila CSV pronta para importação ou uso direto pelo CS. Cada linha representará uma conta priorizada e incluirá evidências, oportunidade financeira máxima, ação imediata, ação estrutural e campos operacionais editáveis.

### Consequência para o desenho

O pipeline será responsável por gerar o CSV; o dashboard apenas filtrará e oferecerá seu download. Integração com CRM e contato automático ficam fora do escopo porque exigiriam sistema-alvo, credenciais, regras de negócio e autorização inexistentes no desafio.

### Ponto ainda aberto

Precisamos decidir se a experiência do avaliador dependerá apenas da execução local ou se também haverá uma demonstração acessível por link.

### Pergunta 5

Como devemos disponibilizar a solução final?

- A. Somente execução local reproduzível.
- B. Execução local reproduzível e demonstração Streamlit pública, somente leitura, sem segredos nem APIs pagas.
- C. Aplicação privada com login, banco de dados e gestão de usuários.
- D. Somente capturas de tela e PDF, sem dashboard executável.

**Recomendação técnica preliminar do agente:** B, porque reduz o atrito da avaliação sem substituir a prova de reprodução local nem adicionar infraestrutura de produto.

### Estado da pergunta 5

Respondida por delegação explícita ao agente.

### Resposta literal de Luis

> Você quem deve me dizer, avaliando o que diz a regra do desafio. Você não pode errar nessa avaliação: revise novamente o repositório onde consultou o desafio proposto e responda com absoluta certeza.

### Verificação realizada

Relemos no GitHub o `README.md`, `submission-guide.md`, o README do Challenge 001, `templates/submission-template.md` e `CONTRIBUTING.md`. O fork de Luis e o repositório oficial estavam idênticos no commit `4aed364d572fabe0f1fff1f0c6f32960b30fe575` no momento da consulta.

As regras confirmam:

- relatório de diagnóstico e process log são obrigatórios;
- a submissão é exclusivamente por Pull Request;
- código funcional precisa incluir instruções de setup;
- dashboard e automação são diferenciais não obrigatórios;
- hospedagem pública não aparece como requisito.

### Decisão técnica do agente

> B

Adotaremos execução local reproduzível **e** uma demonstração Streamlit pública, somente leitura, sem segredos nem APIs pagas. A reprodução local será o critério obrigatório de aceite. A demonstração pública será um diferencial de baixo atrito e não poderá bloquear nem atrasar a submissão caso o provedor externo falhe.

### Consequência para o desenho

O README funcionará mesmo sem o link público. A aplicação hospedada consumirá somente artefatos derivados permitidos e terá a mesma versão do código validado localmente. Não serão adicionados login, banco ou serviços externos apenas para sustentar a demonstração.

## Síntese provisória da Onda 4

- **Arquitetura:** pipeline Python único → tabelas → relatório Markdown, dashboard Streamlit e fila CSV.
- **Reprodução:** `make reproduce` regenera e valida; `make app` abre a interface.
- **Experiência:** decisão executiva, evidências e fila operacional, com metodologia recolhível.
- **Automação:** CSV baixável para o CS; sem CRM ou contato automático.
- **Disponibilização:** local reproduzível como requisito e Streamlit público como diferencial não bloqueante.

### Estado da onda

Síntese confirmada por Luis sem ajustes. A Onda 4 está encerrada.

## Onda 5: critérios de aceite, testes, limites e definição de pronto

### Pergunta 1

Qual deve ser o critério principal para aceitar uma conclusão como finding final?

- A. O pipeline executou sem erro e gerou um gráfico plausível.
- B. Existe uma trilha reproduzível ligando finding, tabelas de origem, recorte temporal, números, evidência contrária ou limitação e recomendação correspondente.
- C. O finding aparece entre as variáveis mais importantes do modelo preditivo.
- D. O finding parece convincente para um leitor executivo.

**Recomendação técnica preliminar do agente:** B, porque transforma cada afirmação importante em algo verificável e reduz o risco de uma narrativa visualmente forte, mas estatisticamente frágil.

### Estado da pergunta 1

Respondida por Luis.

### Resposta literal de Luis

> B, sem dúvidas.

### Interpretação

A opção **B** é um critério obrigatório, não apenas uma preferência. Nenhuma conclusão principal entrará no relatório sem uma trilha reproduzível que conecte fontes, tempo, cálculo, resultado, contraprova ou limitação e ação recomendada.

### Consequência para o desenho

Os findings terão identificadores estáveis compartilhados pelo relatório, tabelas derivadas e dashboard. Uma matriz de rastreabilidade permitirá reconstruir cada número e localizar as limitações sem depender da narrativa do autor.

### Ponto ainda aberto

Precisamos definir a menor suíte de testes capaz de proteger essa trilha, o recorte temporal e a consistência entre artefatos.

### Pergunta 2

Qual conjunto mínimo de testes deve bloquear a entrega?

- A. Apenas um teste de fumaça confirmando que o pipeline termina.
- B. Contratos de schema e chaves, invariantes de junção e receita, bloqueio de vazamento temporal, consistência entre artefatos e teste de fumaça do dashboard.
- C. Cobertura unitária próxima de 100% para todas as funções e componentes visuais.
- D. Somente revisão manual do relatório e do dashboard.

**Recomendação técnica preliminar do agente:** B, porque cobre os modos de falha que poderiam alterar uma conclusão sem criar testes sobre código trivial.

### Estado da pergunta 2

Respondida por Luis.

### Resposta de Luis

> B

### Interpretação

A entrega será bloqueada por falhas nos contratos de dados, cardinalidades e chaves, invariantes financeiros, isolamento temporal, consistência entre relatório, dashboard e CSV, ou inicialização da interface. Cobertura ampla de código trivial não será objetivo.

### Consequência para o desenho

`make reproduce` deverá executar esses gates antes de declarar sucesso. Cada teste protegerá uma conclusão ou um risco real já identificado. Um artefato gerado com teste vermelho será considerado inválido, mesmo que pareça correto visualmente.

### Ponto ainda aberto

O modelo preditivo é um diferencial opcional. Precisamos definir um portão objetivo para impedir que um modelo fraco entre apenas para tornar a entrega mais sofisticada.

### Pergunta 3

Quando o modelo preditivo deve fazer parte da entrega final?

- A. Sempre, porque o desafio cita previsão de churn como diferencial.
- B. Somente se superar um baseline simples na avaliação fora do tempo, produzir risco útil para a fila e apresentar desempenho e limitações por segmento; caso contrário, será removido.
- C. Quando atingir boa acurácia no conjunto de treinamento.
- D. Mesmo sem validação suficiente, desde que as explicações SHAP sejam visualmente claras.

**Recomendação técnica preliminar do agente:** B, porque “um modelo preditivo que funcione” é diferencial; um modelo sem ganho fora do tempo enfraquece a credibilidade do diagnóstico.

### Pedido de esclarecimento de Luis

> B ou C? Qual recomenda?

### Esclarecimento do agente

A recomendação permanece **B, sem dúvida**. A opção C mede o desempenho nos mesmos dados usados para aprender e, portanto, pode recompensar memorização, sobreajuste ou vazamento. Ela não demonstra que o modelo funcionará em contas e períodos futuros. A opção B testa exatamente o uso pretendido, exige ganho sobre uma regra simples e permite retirar o modelo se ele não agregar valor real.

### Estado da pergunta 3

Respondida por Luis após o esclarecimento.

### Resposta de Luis

> B então.

### Interpretação

O modelo só fará parte da entrega se demonstrar ganho sobre um baseline simples em dados futuros, contribuir para uma fila operacional útil e expor desempenho e limitações por segmento. A decisão de removê-lo será considerada sinal de rigor, não falha do projeto.

### Consequência para o desenho

O pipeline terá um caminho de diagnóstico que funciona sem modelo. A etapa preditiva será desacoplada e condicionada a um relatório de avaliação fora do tempo. SHAP ou outra explicação local só será incluída após o modelo passar nesse portão.

### Ponto ainda aberto

Mesmo sem um modelo, amostras pequenas, dados ausentes ou evidências conflitantes podem não sustentar uma conclusão. Precisamos definir como a solução deve declarar incerteza.

### Pergunta 4

Como devemos tratar segmentos ou causas com evidência insuficiente?

- A. Mantê-los no ranking para que nenhuma oportunidade seja perdida.
- B. Marcar como inconclusivos ou baixa confiança, suprimir rankings instáveis e mostrar amostra, cobertura e motivo da abstenção.
- C. Agrupá-los automaticamente até surgir uma diferença estatística.
- D. Pedir que a IA complete a conclusão usando conhecimento geral de SaaS.

**Recomendação técnica preliminar do agente:** B, porque reconhecer que os dados não sustentam uma resposta é mais confiável do que fabricar prioridade ou precisão.

### Estado da pergunta 4

Respondida por Luis.

### Resposta de Luis

> B

### Interpretação

Quando amostra, cobertura, estabilidade ou convergência de evidências forem insuficientes, a solução deverá declarar a conclusão como inconclusiva ou de baixa confiança. Rankings instáveis serão suprimidos em vez de apresentados como decisão segura.

### Consequência para o desenho

Tabelas e visuais deverão exibir tamanho da amostra, cobertura e nível de confiança. A matriz de rastreabilidade registrará o motivo de cada abstenção. A IA não poderá preencher lacunas com padrões gerais de mercado.

### Ponto ainda aberto

Resta definir o conjunto completo e verificável de condições que encerra a implementação e autoriza a submissão.

### Pergunta 5

Quando o Challenge 001 poderá ser marcado como pronto?

- A. Quando o pipeline executar e o dashboard abrir localmente.
- B. Quando as três perguntas do desafio estiverem respondidas com evidências das cinco tabelas; findings rastreáveis; recomendações priorizadas; relatório, dashboard e CSV consistentes; gates verdes; setup reproduzível; limitações e process log completos; e revisão executiva de cinco minutos aprovada.
- C. Quando a demonstração pública estiver visualmente convincente, mesmo com testes ou documentação pendentes.
- D. Quando o tempo planejado acabar, registrando o restante como trabalho futuro.

**Recomendação técnica preliminar do agente:** B, porque cobre os requisitos oficiais, as decisões das cinco ondas e a prova técnica sem tornar a hospedagem opcional um bloqueador.

### Estado da pergunta 5

Respondida por Luis.

### Resposta de Luis

> B

### Interpretação

“Pronto” significa conformidade simultânea com o desafio, evidência analítica, consistência dos artefatos, validação técnica, reprodução e documentação do processo. Execução sem erro ou aparência visual não bastam isoladamente.

### Consequência para o desenho

A SPEC deverá converter cada item da opção B em critério de aceite verificável. A demonstração pública continuará fora do caminho crítico; o modelo preditivo continuará condicionado ao portão definido na Pergunta 3.

## Síntese provisória da Onda 5

- **Aceite de findings:** trilha reproduzível entre fonte, tempo, cálculo, evidência, limitação e recomendação.
- **Testes bloqueantes:** schemas, chaves, joins, receita, isolamento temporal, consistência dos artefatos e fumaça da interface.
- **Modelo opcional:** só entra se superar baseline fora do tempo e agregar valor operacional por segmento.
- **Abstenção:** evidência insuficiente será mostrada como inconclusiva; rankings instáveis serão suprimidos.
- **Definição de pronto:** requisitos oficiais, cinco tabelas, três respostas, artefatos consistentes, gates verdes, setup, limitações, process log e revisão executiva aprovados.

### Estado da onda

Síntese confirmada por Luis sem ajustes. A Onda 5 e a descoberta socrática estão encerradas. A SPEC ainda não foi criada.

## Transição para o SDD

A releitura da skill SDD instalada confirmou o fluxo `brainstorm → add-task → plan-task → implement-task`. Antes do `add-task`, o desenho será apresentado e validado em seções curtas. Só depois da aprovação integral ele será materializado como SPEC em estado `draft`.

## Consolidação do desenho — Seção 1: arquitetura e fluxo de dados

A solução terá um único pipeline Python reproduzível. Os cinco CSVs originais serão tratados como entradas imutáveis. A primeira etapa validará schemas, tipos, chaves, duplicidades, cobertura temporal e cardinalidades. A segunda construirá um painel de **conta × data de corte**, agregando assinaturas, uso e suporte conhecidos até cada corte. Campos produzidos no churn, como `reason_code` e feedback, permanecerão em uma trilha retrospectiva separada e nunca entrarão na previsão anterior ao cancelamento.

Sobre esse painel, a camada analítica calculará sinais de 7, 30 e 90 dias, condicionados à cobertura real, e cruzará produto, suporte, contrato, aquisição e churn. Findings aceitos serão gravados com identificador, métricas, fontes, recorte temporal, confiança, limitações e recomendação. A etapa preditiva será opcional: só publicará escores se superar um baseline simples fora do tempo e demonstrar utilidade operacional por segmento.

O pipeline produzirá arquivos tabulares versionáveis como fonte única do relatório executivo em Markdown, das três visões do Streamlit e da fila CSV de CS. Assim, números, prioridades e filtros não serão recalculados independentemente em cada interface. `make reproduce` executará validações, testes e geração; `make app` abrirá o dashboard. Não haverá API, banco, autenticação ou chamada paga de IA. A demonstração pública usará os mesmos artefatos e não bloqueará a entrega local.

### Estado da seção 1

Seção aprovada por Luis sem ajustes.

## Consolidação do desenho — Seção 2: componentes, experiência e artefatos

O código será dividido apenas pelos limites reais do fluxo: carregamento e validação; construção temporal; análise e findings; modelo opcional; publicação dos artefatos; aplicação Streamlit. Não haverá classes, serviços ou interfaces genéricas sem mais de uma implementação. Um arquivo de configuração concentrará somente parâmetros que precisam ser auditáveis, como datas de corte, janelas, thresholds de confiança e sementes aleatórias.

A publicação produzirá um conjunto pequeno de artefatos canônicos. O registro de findings conterá identificador, afirmação, força da evidência, métricas, segmentos, MRR exposto, limitações e ações. A fila operacional conterá `account_id`, prioridade, MRR exposto — oportunidade máxima, sinais explicativos, ação imediata, ação estrutural, responsável e status. Um resumo de qualidade registrará cobertura, perdas nos joins, datas, contagens e resultados dos gates. O relatório executivo e o dashboard lerão esses arquivos; não manterão cópias manuais dos números.

O Streamlit terá três visões. **Decisão executiva** mostrará a causa prioritária, oportunidade máxima, confiança, contenção de uma semana e correção de 30–90 dias. **Evidências** permitirá examinar causas, segmentos, evolução temporal, métricas de proteção e sinais contrários. **Fila operacional** permitirá filtrar contas e baixar o CSV. Metodologia, definições e limitações ficarão em painel recolhível. Cada gráfico deverá responder a uma pergunta explícita; visualizações sem consequência decisória serão removidas.

O README da submissão será a porta de entrada: executive summary, comandos, estrutura, findings, recomendações, limitações e links para o diário. A demonstração pública será somente leitura e não terá funcionalidade exclusiva ausente na execução local.

### Estado da seção 2

Seção aprovada por Luis sem ajustes.

## Consolidação do desenho — Seção 3: erros, incerteza e abstenção

O pipeline falhará cedo quando uma condição puder invalidar a análise: arquivo ausente, coluna obrigatória ausente, tipo incompatível, chave inválida, duplicidade inesperada, data impossível, cardinalidade divergente ou valor financeiro incoerente. A mensagem identificará arquivo, regra violada, quantidade de registros afetados e ação esperada. Nenhum erro estrutural será convertido silenciosamente em valor nulo ou linha descartada.

Cada junção produzirá reconciliação de linhas, entidades e valores antes e depois. Ausência de evento será diferente de ausência de cobertura: “nenhum ticket” não poderá ser inferido quando a conta simplesmente não estiver observada. Limites para amostra e cobertura serão definidos após o profiling e ficarão visíveis na configuração e no relatório. Um manifesto registrará hashes ou metadados equivalentes das entradas, parâmetros e artefatos, impedindo que dashboard e relatório misturem execuções diferentes.

As conclusões usarão três rótulos: **fato observado**, **associação controlada** e **hipótese causal**. Uma hipótese só avançará quando associação, coerência temporal e sinais de tabelas diferentes convergirem. Evidência contrária será exibida junto da favorável. Segmentos pequenos, resultados instáveis ou cobertura insuficiente serão marcados como inconclusivos; não receberão ranking executivo. O “MRR exposto — oportunidade máxima” será sempre identificado como teto teórico, nunca previsão de recuperação.

Se o modelo falhar no portão fora do tempo, o pipeline publicará diagnóstico e fila baseados em evidência sem escores preditivos. Se os artefatos estiverem ausentes ou incompatíveis, o Streamlit interromperá a leitura e instruirá a executar `make reproduce`; ele não recalculará resultados nem exibirá dados parciais.

### Estado da seção 3

Seção aprovada por Luis sem ajustes.

## Consolidação do desenho — Seção 4: testes, aceite e definição de pronto

Os testes serão organizados pelos riscos da decisão, não pela quantidade de funções. Contratos verificarão presença e tipos das colunas, unicidade e integridade das chaves e relações entre as cinco tabelas. Invariantes de transformação confirmarão que joins não multiplicam contas, tickets ou receita, que agregações preservam totais reconciliados e que ausência de cobertura não vira zero. Testes temporais usarão casos-sentinela para provar que nenhum evento posterior ao corte entra nos atributos.

Testes de publicação compararão identificadores e métricas do registro de findings, relatório, dashboard e fila CSV. O manifesto deverá corresponder às entradas e parâmetros da execução. Um teste de fumaça iniciará o Streamlit e verificará as três visões e o download. Se houver modelo, o gate exigirá avaliação fora do tempo, comparação com baseline simples, métricas adequadas ao desbalanceamento e recortes por segmento; falha removerá o modelo, não o diagnóstico.

`make reproduce` executará os contratos, o pipeline, os testes e a geração dos artefatos. Antes do Pull Request, o mesmo comando será provado em ambiente limpo, seguindo o fluxo obrigatório de Codespaces quando o gate for pesado. O resultado só poderá ser declarado verde para o mesmo commit e conjunto de dados da submissão.

A entrega estará pronta quando responder às três perguntas oficiais usando as cinco tabelas; possuir findings rastreáveis, recomendações imediatas e estruturais, contas específicas e MRR exposto corretamente rotulado; manter relatório, dashboard e CSV consistentes; documentar setup, limitações e processo de IA; passar todos os gates; e permitir que um leitor não técnico identifique decisão, evidência e próxima ação em cinco minutos. O link público será desejável, mas nunca substituirá nem bloqueará a reprodução local.

### Estado da seção 4

Seção aprovada por Luis sem ajustes. O desenho completo está fechado.

## Criação da SPEC pelo estágio SDD `add-task`

Após a aprovação das quatro seções, criamos a SPEC draft em `solution/001-churn/.specs/tasks/draft/implement-churn-diagnostic.feature.md`. O arquivo preserva as solicitações originais relevantes e registra, em `Initial User Prompt → Requirements`, o desenho aprovado. A seção `Description` permanece com o placeholder exigido pela metodologia e será preenchida no estágio `plan-task`.

### Adaptação necessária da skill

O script `create-folders.sh` da instalação cria `.specs` e `.claude` na raiz Git. Isso violaria a regra oficial de modificar somente `submissions/luis-roquette/`. Aplicamos o fallback previsto pela skill e criamos a estrutura manualmente dentro de `submissions/luis-roquette/solution/001-churn/`, sem alterar arquivos fora da submissão.

## Fechamento da exploração e criação da SPEC draft

### Escopo concluído

Esta fase começou sem solução ou SPEC. Encerramos com o briefing relido até estabilização, pesquisa externa registrada, cinco ondas socráticas completas, 25 decisões respondidas, quatro seções de desenho aprovadas e uma SPEC criada no estado `draft`. Todas as perguntas, respostas literais, interpretações e consequências foram preservadas neste diário.

### Decisões que orientam a próxima fase

- O produto principal é um diagnóstico que ajuda o CEO a escolher qual problema sistêmico corrigir primeiro.
- A entrega terá relatório executivo, dashboard de evidências e fila CSV, derivados da mesma execução.
- O rigor temporal, a rastreabilidade e a capacidade de declarar “inconclusivo” têm precedência sobre uma narrativa mais impressionante.
- O modelo preditivo é opcional e será removido se não superar um baseline fora do tempo.
- Reprodução local e process log são obrigatórios; demonstração pública é diferencial não bloqueante.

### Evidências produzidas

- Diário pré-início com regras, pesquisa, releitura em loop, SDD e Ponytail.
- Diário socrático com as cinco ondas e o desenho validado incrementalmente.
- Histórico Git granular, com um commit por decisão ou pequeno conjunto coerente.
- SPEC draft em `solution/001-churn/.specs/tasks/draft/implement-churn-diagnostic.feature.md`.

### O que deliberadamente ainda não foi feito

Nenhum dataset foi transformado, nenhum código da solução foi escrito, nenhum modelo foi treinado e nenhum dashboard foi iniciado. Essa contenção foi intencional: o contrato precisava ser discutido e aprovado antes da implementação. A seção `Description`, os critérios formais de aceite e a decomposição em subtarefas pertencem ao próximo estágio, `plan-task`.

### Erro operacional registrado

Ao tentar abrir a SPEC, o comando foi quebrado em duas linhas após `submissions/luis-roquette/`. O shell interpretou `solution/...` como um segundo comando e retornou `no such file or directory`. O arquivo estava correto; a causa foi apenas a quebra de linha. O comando corrigido usa caminho absoluto entre aspas:

```bash
open "/Users/luisroquette/Projects/ai-master-challenge/submissions/luis-roquette/solution/001-churn/.specs/tasks/draft/implement-churn-diagnostic.feature.md"
```

### Gate de saída

A exploração está encerrada e o desenho foi aprovado por Luis. A SPEC draft existe, está versionada e mantém o placeholder exigido pelo SDD. O próximo passo autorizado será executar `plan-task`; implementar antes dessa promoção violaria a metodologia acordada.

## Atualização do gate após o planejamento

O estágio `plan-task` foi concluído e revisado em vinte passadas. As duas últimas passadas consecutivas não encontraram melhoria substancial, atingindo o goal de estabilidade. A SPEC recebeu descrição e critérios de aceite, e o plano canônico passou pela auditoria final de aderência ao desafio, stack e capacidade operacional.

Luis autorizou a implementação em fases sequenciais. A continuação passa a ser registrada em `003-implementacao-feedback-looping.md`; este arquivo permanece como transcrição canônica das 25 perguntas e respostas, incluindo interpretações, consequências e confirmações de cada onda.
