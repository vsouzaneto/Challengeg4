# Process Log — Radar de Oportunidades

**Challenge:** 003 — Lead Scorer  
**Produto:** Radar de Oportunidades  
**Evolução:** Strategy Lab + Onboarding  
**Versão:** 2.0  
**Data:** Setembro de 2026  
**Área:** Vendas / RevOps

---

## 1. Visão geral

Este documento registra o processo de construção e evolução do **Radar de Oportunidades**, uma ferramenta de priorização comercial desenvolvida para transformar dados de CRM em uma fila de oportunidades que ajuda o time de vendas a decidir **onde focar, por quê e qual ação considerar**.

O produto evoluiu de um scoring inicial para uma experiência de **Sales Intelligence / decision support**, com:

**Dados → Features → Score → Ranking → Explainability → Recommended Action → Data Confidence → Validação → Simulação → Decisão**

A versão atual possui duas camadas principais:

1. **Radar de Oportunidades:** identifica e explica as oportunidades que merecem mais atenção.
2. **Strategy Lab:** permite simular mudanças de estratégia e observar como elas alteram a priorização do pipeline.

Também foi criado um **onboarding inicial específico para o Strategy Lab**, para que novos usuários compreendam a funcionalidade sem precisar conhecer a metodologia estatística por trás dela.

O desenvolvimento utilizou IA de forma iterativa:

- **ChatGPT:** entendimento e decomposição do problema, análise crítica, discussão da metodologia de scoring, validação conceitual, revisão de UX e documentação.
- **Claude Code:** exploração dos dados e arquivos, implementação, testes, investigação de problemas, alterações no sistema, QA, evolução da interface e publicação do protótipo.

A IA não foi utilizada como um processo de “um prompt → uma resposta → entrega”. O trabalho seguiu ciclos de:

**problema → hipótese → análise/implementação → teste → descoberta → correção → nova validação**

---

## 2. Problema que precisava ser resolvido

O desafio apresentava aproximadamente 8.800 oportunidades comerciais distribuídas entre 35 vendedores, administrados por gestores regionais.

O problema de negócio era a priorização baseada em percepção ou “feeling”.

A necessidade não era construir apenas um modelo estatístico, mas entregar algo que um vendedor pudesse abrir e utilizar para responder:

> **“Qual oportunidade merece minha atenção primeiro?”**

E, principalmente:

> **“Por que essa oportunidade está acima das outras?”**

O produto precisava ser funcional, explicável e utilizável por pessoas não técnicas.

---

## 3. Entendimento e auditoria inicial dos dados

Antes da implementação, os arquivos foram explorados para entender:

- estrutura das tabelas;
- chaves de relacionamento;
- quantidade de registros;
- distribuição por estágio;
- produtos;
- vendedores;
- contas;
- datas;
- valores;
- dados ausentes;
- comportamento histórico.

A base principal possuía aproximadamente 8.800 oportunidades.

Foram identificados:

- **4.238 Won**
- **2.473 Lost**
- **1.589 Engaging**
- **500 Prospecting**
- **2.089 oportunidades abertas**

A taxa histórica agregada dos negócios já fechados foi de aproximadamente **63,2% de Won**.

Essa taxa foi posteriormente tratada apenas como referência histórica agregada. A base não possui log completo de transição entre estágios e, portanto, não permite afirmar uma conversão validada de Prospecting → Engaging → Won.

Também foram verificadas:

- unicidade de `opportunity_id`;
- joins entre pipeline, contas, produtos e vendedores;
- inconsistências de nomenclatura;
- valores ausentes;
- comportamento das datas.

Essa auditoria foi importante para evitar construir regras sobre interpretações que o dataset não sustentava.

---

## 4. Decomposição inicial do problema

A primeira abordagem identificou cinco dimensões:

- Tempo no pipeline — 20%
- Agente de vendas — 20%
- Porte da conta — 15%
- Estágio no funil — 20%
- Série do produto — 25%

Durante a análise, essa estrutura foi questionada.

A principal decisão metodológica foi separar:

**informação contextual**

de

**fatores que realmente deveriam alterar a prioridade.**

Vendedor e porte da conta foram retirados diretamente do cálculo.

O vendedor permaneceu disponível para:

- filtro;
- contexto;
- responsabilidade pela oportunidade;
- análise gerencial.

A estrutura final passou a utilizar quatro componentes:

- **Commercial Potential — 25%**
- **Funnel Position — 25%**
- **Urgency / Aging — 30%**
- **Historical Fit — 20%**

Essa mudança demonstrou que a IA não foi usada apenas para implementar a primeira solução sugerida, mas também para questionar suas premissas.

---

## 5. Construção e refinamento do scoring

### 5.1 Commercial Potential

Inicialmente, um percentil simples entre as sete SKUs dava peso excessivo a produtos com pouca representação no histórico.

O caso mais evidente foi o **GTK 500**.

Havia apenas 40 negócios no histórico, aproximadamente 0,45% do volume, mas a posição do produto entre apenas sete SKUs fazia com que ele recebesse uma vantagem desproporcional.

A solução foi substituir o percentil simples por um **percentil ponderado pelo volume real de negócios**.

O resultado reduziu a concentração artificial.

Na versão analisada, GTK 500 e GTX Plus Pro passaram de uma diferença aproximada de 16,7 pontos para valores muito mais próximos, de aproximadamente **99,8 contra 94,0**.

Também foram analisadas as concentrações do Top 10, Top 20 e Top 50.

**Aprendizado:** uma fórmula matematicamente válida não é suficiente. Sua distribuição precisa ser confrontada com o comportamento real dos dados.

---

### 5.2 Urgency / Aging

Foi encontrado um problema conceitual na primeira implementação de Aging.

A regra anterior aplicava decaimento depois de aproximadamente 138 dias. Isso produzia uma inversão:

> oportunidades que permaneciam paradas por mais tempo podiam receber menor urgência.

Um teste encontrou, na situação problemática, correlação de aproximadamente **-0,628** entre score e dias decorridos para GTX Plus Pro.

Isso contradizia o conceito do produto.

A lógica foi reformulada para que a urgência:

- aumente com o tempo;
- nunca decaia simplesmente por uma oportunidade estar mais antiga;
- mantenha diferenciação entre oportunidades;
- continue aumentando de forma mais lenta após o teto histórico.

A solução final evita tanto a inversão quanto a concentração excessiva de oportunidades em 100.

**Aprendizado:** corrigir um bug lógico pode criar outro problema de distribuição. Toda correção precisa ser validada novamente.

---

### 5.3 Prospecting

Foi levantada a hipótese de que oportunidades em **Prospecting** estavam sendo prejudicadas artificialmente pelo Aging.

Em vez de alterar o modelo imediatamente, a hipótese foi testada.

Mesmo atribuindo à etapa Prospecting uma urgência próxima à média de Engaging, sua mediana continuava abaixo.

A investigação indicou que a diferença era principalmente estrutural no componente **Funnel Position**, e não uma penalização artificial de Aging.

A decisão foi manter o comportamento do modelo e documentar a causa.

Não foi criado um ajuste artificial apenas para aumentar Prospecting no ranking.

**Aprendizado:** quando um resultado parece indesejado, investigar a causa antes de manipular a fórmula.

---

### 5.4 Historical Fit

O Historical Fit utiliza uma hierarquia:

**Account History → Product History → Baseline**

Foram consideradas proteções como:

- número mínimo de observações;
- histórico anterior à oportunidade;
- smoothing;
- prevenção de data leakage.

A validação apresentou **AUC aproximadamente 0,48**, próxima ao acaso para esse componente isoladamente.

Por isso, Historical Fit não é apresentado como um modelo preditivo forte.

Ele permanece como um componente heurístico/contextual do índice.

**Aprendizado:** uma feature pode ser útil como sinal contextual sem possuir poder preditivo forte.

---

## 6. Verificação estatística e contraexemplos

A análise não ficou limitada à inspeção visual.

Foram investigados:

- concentração do Top 10;
- composição do Top 20;
- composição do Top 50;
- correlação entre score e valor;
- comportamento do Aging;
- distribuição por produto;
- comportamento de Prospecting;
- limitações do Historical Fit.

Após os ajustes, a correlação entre valor e score permaneceu próxima da referência analisada, aproximadamente **0,53 contra 0,49**, evitando que o ranking se transformasse simplesmente em uma ordenação por preço.

Também foi verificado que o comportamento de Prospecting não resultava de uma penalização artificial.

---

## 7. Explainability

A explicabilidade foi tratada como requisito do produto.

Cada oportunidade pode decompor seu Priority Score em quatro componentes:

- Urgency / Aging;
- Funnel Position;
- Commercial Potential;
- Historical Fit.

A soma dos pontos exibidos deve fechar matematicamente com o Priority Score.

Exemplo:

```text
Urgency / Aging
92/100 · peso 30% · +27,6 pts

Funnel Position
100/100 · peso 25% · +25 pts

Commercial Potential
74/100 · peso 25% · +18,5 pts

Historical Fit
61/100 · peso 20% · +12,2 pts
```

Isso permite responder:

> **Por que esta oportunidade recebeu essa prioridade?**

A explicação é determinística e baseada nos próprios componentes matemáticos do score.

Não é necessário utilizar LLM para inventar uma justificativa.

---

## 8. Data Confidence

Foi identificada a necessidade de separar:

**qualidade/disponibilidade dos dados**

de

**risco comercial.**

Existem oportunidades abertas sem informação de conta e outras com dados incompletos.

A ausência de uma informação não deve ser automaticamente interpretada como um sinal negativo do negócio.

Por isso, **Data Confidence** representa a disponibilidade/completude das informações usadas na avaliação.

Não representa:

- probabilidade de fechamento;
- confiança estatística do modelo;
- qualidade comercial da oportunidade.

Essa distinção evita uma falsa sensação de precisão.

---

## 9. Thresholds de prioridade

As faixas de prioridade são baseadas na distribuição do pipeline.

A classificação é **relativa ao pipeline atual**.

Portanto, sempre haverá uma faixa superior mesmo quando a qualidade absoluta do pipeline não for alta.

As faixas não representam:

- probabilidade de fechamento;
- garantia de sucesso;
- qualidade absoluta do negócio.

O produto diferencia explicitamente:

**Priority Score = índice de priorização**

e não:

**Probability of Closing = probabilidade de fechamento.**

---

## 10. Ajuste dinâmico dos pesos

O sistema recebeu a capacidade de alterar os pesos dos quatro fatores.

Regras:

- os pesos devem totalizar exatamente 100%;
- nenhum peso deve ficar negativo;
- o score deve ser recalculado;
- os fatores individuais permanecem iguais;
- apenas suas contribuições relativas mudam.

Pesos atuais/default:

- Commercial Potential — 25%
- Funnel Position — 25%
- Urgency / Aging — 30%
- Historical Fit — 20%

Essa funcionalidade foi a base para a evolução posterior para o **Strategy Lab**.

---

# 11. Strategy Lab — Simulação de estratégia

## 11.1 Motivo da criação

O simples ajuste de pesos era funcional, mas ainda poderia ser interpretado como uma configuração técnica.

A evolução buscou transformar essa capacidade em uma experiência de decisão:

> **“Se minha estratégia comercial mudar, como meu pipeline muda?”**

Assim surgiu o **Strategy Lab**.

O objetivo não é encontrar automaticamente os melhores pesos.

O objetivo é permitir que um gestor teste uma hipótese estratégica e observe seu impacto.

---

## 11.2 Conceito

O Strategy Lab reutiliza exatamente os quatro fatores existentes.

Os scores individuais não mudam.

Somente os pesos são simulados.

Conceitualmente:

```text
Score atual
= soma dos fatores × pesos atuais

Score simulado
= soma dos mesmos fatores × pesos simulados
```

Não existe um novo modelo de ML.

Não existe treinamento.

Não existe previsão de fechamento.

Não existe otimização automática.

---

## 11.3 Estado atual versus estado simulado

O produto mantém dois estados conceituais:

```text
CURRENT_MODEL
SIMULATED_MODEL
```

O modelo atual permanece intacto durante a simulação.

O usuário pode alterar os pesos livremente e observar o resultado.

Somente após uma ação explícita de:

**“Aplicar estratégia”**

a nova configuração passa a ser oficial.

Também existe:

**“Restaurar estratégia atual”**

para cancelar a simulação.

Essa separação reduz o risco de uma alteração exploratória modificar o comportamento oficial do produto sem intenção.

---

## 11.4 Presets estratégicos

O Strategy Lab apresenta estratégias pré-configuradas para facilitar a exploração.

Exemplos:

- **Balanceada**
- **Proteger pipeline**
- **Maximizar valor**
- **Avançar oportunidades**

Esses presets são apresentados como **cenários de simulação**, não como estratégias matematicamente ótimas.

O sistema não afirma:

> “Esta é a melhor estratégia.”

Ele permite:

> “Veja o que aconteceria se você priorizasse mais este fator.”

---

## 11.5 Impacto no pipeline

A principal entrega do Strategy Lab não é o slider.

É a visualização do impacto.

Ao alterar a estratégia, o sistema recalcula:

- score simulado;
- ranking simulado;
- prioridade simulada;
- contribuição dos fatores;
- variação de posição.

Exemplo conceitual:

```text
Oportunidade A

Score: 76 → 84
Rank:  #18 → #5

+13 posições
```

Outra oportunidade pode apresentar:

```text
Oportunidade B

Score: 83 → 79
Rank:  #2 → #7

-5 posições
```

O objetivo é permitir ao gestor visualizar:

**quem ganhou prioridade, quem perdeu e por quê.**

---

## 11.6 Top Movers

Foi criada uma visão de:

**“Maiores mudanças de prioridade”**

Ela apresenta as oportunidades que mais subiram ou desceram no ranking.

São considerados:

- oportunidade;
- conta;
- score atual;
- score simulado;
- rank atual;
- rank simulado;
- variação;
- principal fator responsável.

Isso transforma a alteração de pesos em consequência comercial observável.

---

## 11.7 Quem ganhou e quem perdeu

O Strategy Lab também permite visualizar:

### Quem ganhou prioridade

Oportunidades favorecidas pela estratégia simulada.

### Quem perdeu prioridade

Oportunidades que perderam posição relativa.

A explicação utiliza as contribuições dos fatores.

Exemplo:

> “Esta oportunidade ganhou prioridade porque possui alto potencial comercial e a estratégia simulada aumentou o peso desse fator.”

Ou:

> “Esta oportunidade perdeu prioridade porque seu score era fortemente influenciado por Urgency/Aging e a estratégia simulada reduziu o peso desse fator.”

As explicações são determinísticas.

---

## 11.8 Comparação Top 10

Foi adicionada uma comparação:

**TOP 10 ATUAL**

versus

**TOP 10 SIMULADO**

A intenção é responder visualmente:

> **“Minha estratégia mudou de fato a fila de prioridade?”**

Esse elemento é importante porque mostra impacto estratégico sem exigir que o usuário examine centenas de oportunidades.

---

## 11.9 Ranking global

Uma regra crítica foi preservada:

O ranking deve ser calculado sobre **todas as oportunidades abertas**, e não apenas sobre o subconjunto filtrado na tela.

Assim, uma informação como:

> **Rank #2 de 2.089**

continua representando a posição global.

Filtros de vendedor, região, estágio ou outros critérios servem para exploração da carteira e não devem alterar silenciosamente a semântica do ranking global.

---

## 11.10 Performance

Como o pipeline aberto possui aproximadamente 2.089 oportunidades, a simulação foi desenhada para ser rápida.

Os quatro scores individuais são reutilizados.

A alteração dos pesos exige essencialmente:

- nova soma ponderada;
- novo ranking;
- novas faixas;
- comparação entre estados.

Não há necessidade de:

- chamada de API;
- LLM;
- novo treinamento;
- processamento pesado.

---

## 12. Onboarding do Strategy Lab

### 12.1 Objetivo

Como o Strategy Lab introduz uma interação nova, foi criado um onboarding específico para usuários que acessam a funcionalidade pela primeira vez.

O objetivo é ensinar apenas o necessário para o usuário chegar ao primeiro momento de valor.

A experiência deve responder:

> “O que é isso?”

> “O que posso fazer?”

> “O que muda?”

> “Posso testar sem risco?”

### 12.2 Estrutura

O onboarding foi projetado como um tour curto de aproximadamente 30–45 segundos, com no máximo quatro etapas.

#### Etapa 1 — O que é

**“Bem-vindo ao Strategy Lab”**

Explica que a área permite simular diferentes estratégias comerciais e observar como elas alteram a prioridade do pipeline.

Mensagem central:

> “Você não está treinando um novo modelo. Está testando diferentes formas de priorizar as mesmas oportunidades.”

#### Etapa 2 — Mude a estratégia

Apresenta os quatro fatores:

- Potencial comercial;
- Posição no funil;
- Urgência / Aging;
- Histórico da conta.

O usuário aprende que pode alterar os pesos para representar uma estratégia que deseja testar.

A matemática não é explicada nessa etapa.

#### Etapa 3 — Veja o impacto

Mostra que alterar os pesos pode mudar:

- score;
- ranking;
- prioridade.

Exemplo visual:

```text
#18 → #5
↑ 13 posições
```

E reforça:

> “Veja quem ganhou ou perdeu prioridade — e por quê.”

#### Etapa 4 — Teste antes de aplicar

Explica a diferença entre:

**SIMULAÇÃO**

e

**MODELO OFICIAL**

Mensagem central:

> “A simulação não altera o modelo oficial até você clicar em ‘Aplicar estratégia’.”

O onboarding termina com:

**“Começar a simular”**

### 12.3 Princípio de UX

O onboarding não deve se transformar em uma apresentação longa.

Ele existe para levar o usuário ao loop principal:

**alterar estratégia → observar impacto → entender mudança → decidir**

Também deve existir uma opção discreta de:

**“Como funciona?”**

para rever o conteúdo posteriormente.

---

# 13. Linguagem e nomenclatura

Durante a evolução do produto, também foi feita uma revisão da nomenclatura para reduzir ambiguidade.

### Aging

**Aging** é utilizado para representar o tempo que uma oportunidade permanece no pipeline.

Na interface, pode ser apresentado como:

**Tempo no pipeline (Aging)**

Isso permite manter o termo técnico sem exigir que o usuário conheça sua definição.

### Engaging

**Engaging** é um estágio original do dataset.

Ele não deve ser confundido com Aging.

Conceitualmente:

- **Engaging** = estágio da oportunidade;
- **Aging** = tempo da oportunidade no pipeline.

Na interface voltada ao usuário brasileiro, o estágio pode ser apresentado como:

**Em negociação / Engajamento**

enquanto o termo original permanece disponível quando necessário para rastreabilidade dos dados.

Essa distinção evita uma confusão importante entre nome de estágio e métrica temporal.

---

# 14. QA e validação

Foi criado um processo de QA automatizado.

A versão base do scoring possui **29 checagens**, incluindo:

- limites dos valores;
- unicidade;
- joins;
- fórmula do score;
- consistência dos pesos;
- explainability;
- fechamento matemático entre componentes e score final.

Na versão documentada, as 29 checagens da base estavam passando.

Com a evolução para o Strategy Lab, foram definidos requisitos adicionais de validação:

1. pesos totalizam 100%;
2. nenhum peso fica abaixo de zero;
3. score continua entre 0 e 100;
4. scores individuais dos fatores não mudam durante a simulação;
5. ranking global continua baseado em todas as oportunidades abertas;
6. score atual permanece intacto enquanto a simulação está ativa;
7. Top Movers corresponde às variações reais;
8. explainability usa os mesmos valores do cálculo;
9. reset retorna ao modelo atual;
10. aplicação explícita persiste a nova estratégia;
11. prioridades são recalculadas;
12. nenhuma oportunidade desaparece da base;
13. filtros não alteram silenciosamente o ranking global;
14. o funcionamento não depende de LLM ou API externa.

Esses pontos representam a nova superfície de QA introduzida pelo Strategy Lab.

---

# 15. Revisão da documentação e precisão das afirmações

Durante o processo, algumas afirmações foram deliberadamente enfraquecidas para não extrapolar o que os dados permitiam concluir.

## Funnel Position

Não foi mantida a interpretação de que 63,2% representaria uma conversão Prospecting → Engaging → Won.

O dataset não possui histórico completo de transição entre etapas.

O número é tratado como referência agregada da base de negócios já fechados.

## Associação estatística

Expressões como:

> “poder preditivo validado”

foram substituídas por:

> **“associação estatisticamente significativa”**

quando apropriado.

A ressalva é importante porque significância estatística não significa necessariamente associação forte ou capacidade preditiva robusta.

## Thresholds

Foi adicionada a ressalva de que as faixas são relativas ao pipeline atual.

Isso impede interpretar “Crítica” como uma avaliação absoluta ou como probabilidade de fechamento.

**Aprendizado:** precisão de linguagem também é parte da qualidade técnica.

---

# 16. Decisões que NÃO foram implementadas

Uma parte importante do processo foi decidir o que não adicionar.

Foram deliberadamente evitados:

### Vendedor como fator direto do score

O vendedor pode apresentar taxas históricas diferentes, mas transformá-lo em fator direto poderia introduzir viés de atribuição e penalizar ou beneficiar oportunidades pelo responsável, em vez das características do negócio.

O vendedor permanece como filtro e contexto.

### Porte da conta como fator principal

Quartis de receita e funcionários não apresentaram evidência suficientemente convincente para justificar peso relevante no score.

### XGBoost ou outro modelo complexo

A complexidade não foi adicionada apenas para afirmar que havia Machine Learning.

Historical Fit apresentou AUC aproximadamente 0,48 isoladamente, e não havia evidência suficiente de que um modelo mais complexo produziria ganho real para o MVP.

### LLM no scoring

O score precisa ser reproduzível, auditável e determinístico.

### LLM para explicar o score

As explicações já podem ser produzidas diretamente pelos componentes matemáticos.

Adicionar LLM aumentaria complexidade sem necessidade.

### Otimização automática dos pesos

O Strategy Lab não tenta encontrar a “melhor” configuração.

Isso exigiria uma definição de objetivo que não está disponível no dataset.

### Integração CRM completa

A integração com CRM, autenticação, banco de dados produtivo e sincronização em tempo real foram consideradas escopo futuro, não requisito do MVP.

### Notificações e automações externas

WhatsApp, Slack, e-mail automático e workflows externos não eram necessários para provar o valor central do produto.

### Chatbot

O problema não exige conversar com os dados.

Exige priorizar e explicar oportunidades.

**Princípio adotado:**

> **Não adicionar tecnologia porque ela existe. Adicionar somente quando resolve melhor o problema.**

---

# 17. Redesign visual

Depois da estabilização da lógica, o produto passou por uma revisão visual.

A direção inicial apresentava características associadas a produtos de IA/startups.

A nova direção foi:

**Sales Intelligence / BI corporativo / CRM Enterprise**

Principais decisões:

- modo claro como padrão;
- azul corporativo como cor de marca;
- verde reservado para semântica positiva;
- fundo cinza-azulado;
- IBM Plex Sans;
- IBM Plex Mono para números;
- remoção de Bricolage Grotesque;
- remoção de glassmorphism;
- redução de sombras;
- redução de border-radius;
- eliminação de efeitos visuais excessivamente futuristas.

O objetivo foi fazer a inteligência aparecer:

**no produto e na análise**

e não em uma estética visual de “AI tool”.

O redesign foi realizado preservando a lógica de scoring.

---

# 18. Evolução do produto

Os principais marcos foram:

1. entendimento do problema;
2. auditoria dos dados;
3. primeiro scoring de cinco fatores;
4. remoção de fatores sem evidência suficiente;
5. criação dos quatro componentes finais;
6. correção do Commercial Potential;
7. correção do Aging;
8. investigação de Prospecting;
9. construção do Historical Fit;
10. validação estatística;
11. criação da Explainability;
12. criação do Data Confidence;
13. criação dos thresholds relativos;
14. ajuste dinâmico dos pesos;
15. QA automatizado;
16. revisão da documentação;
17. redesign visual;
18. criação do Strategy Lab;
19. criação da comparação atual vs simulada;
20. criação de Top Movers;
21. criação do onboarding do Strategy Lab;
22. revisão de nomenclaturas e microcopy.

O processo não foi linear.

Cada etapa foi influenciada pelos resultados observados na etapa anterior.

---

# 19. Como a IA foi utilizada

## ChatGPT

O ChatGPT foi utilizado principalmente para:

1. entender o problema de negócio;
2. decompor o problema;
3. discutir alternativas de scoring;
4. questionar premissas;
5. interpretar resultados;
6. identificar inconsistências conceituais;
7. discutir UX e arquitetura do produto;
8. estruturar o Strategy Lab;
9. revisar a documentação;
10. apoiar a revisão final da interface.

## Claude Code

O Claude Code foi utilizado principalmente para:

1. explorar arquivos;
2. analisar dados;
3. implementar alterações;
4. executar comandos;
5. editar código;
6. testar hipóteses;
7. investigar problemas;
8. executar QA;
9. atualizar o dashboard;
10. atualizar documentação;
11. implementar o Strategy Lab;
12. iterar sobre a interface;
13. publicar versões do protótipo.

## Papel humano

As sugestões produzidas pelas IAs não foram consideradas decisões finais.

Hipóteses e alterações só foram incorporadas quando sustentadas por:

- análise dos dados;
- teste;
- comportamento observado;
- consistência matemática;
- necessidade de produto.

O processo foi:

**problema → hipótese → implementação/análise → teste → descoberta → correção → validação**

O principal valor da IA não esteve apenas na velocidade de geração de código.

Esteve na capacidade de:

- explorar alternativas;
- questionar premissas;
- encontrar inconsistências;
- testar hipóteses;
- iterar rapidamente.

---

# 20. Principais exemplos de julgamento humano

## Exemplo 1 — Aging

A implementação produzia uma inversão de urgência após determinado período.

A regra foi questionada, testada e reformulada.

## Exemplo 2 — GTK 500

O ranking apresentava concentração excessiva em um produto com poucas observações.

A causa foi investigada e o percentil foi substituído por uma abordagem ponderada pelo volume.

## Exemplo 3 — Prospecting

Havia uma hipótese de penalização indevida.

A hipótese foi testada antes de alterar o modelo.

A decisão final foi não manipular o score.

## Exemplo 4 — Historical Fit

A AUC próxima de 0,48 impediu que o componente fosse apresentado como um forte preditor.

A limitação foi incorporada à documentação.

## Exemplo 5 — Linguagem

Afirmações sobre conversão e poder preditivo foram revisadas para refletir exatamente o que o dataset permitia afirmar.

## Exemplo 6 — Strategy Lab

A necessidade de “impressionar” não foi resolvida adicionando IA ou um modelo mais complexo.

A evolução foi feita transformando o ajuste de pesos em uma ferramenta de simulação estratégica.

O foco passou de:

> “mude os pesos”

para:

> **“veja o que acontece com seu pipeline se a estratégia mudar.”**

---

# 21. Resultado final

O Radar evoluiu de um simples mecanismo de pontuação para uma ferramenta de **decision support comercial**.

O fluxo atual pode ser representado como:

```text
CRM / Dados
     ↓
Feature Engineering
     ↓
Scoring
     ↓
Ranking
     ↓
Explainability
     ↓
Recommended Action
     ↓
Data Confidence
     ↓
Strategy Lab
     ↓
Impacto da Estratégia
     ↓
Decisão do Gestor
```

O produto responde quatro perguntas principais:

### 1. Onde devo focar?

**Priority Score + Ranking**

### 2. Por que essa oportunidade está aqui?

**Quatro fatores explicáveis**

### 3. O que posso fazer?

**Recommended Action**

### 4. E se minha estratégia mudar?

**Strategy Lab**

O sistema não toma a decisão pelo vendedor.

Ele reduz o trabalho necessário para chegar a uma decisão melhor informada.

---

# 22. Limitações reconhecidas

O produto mantém explicitamente as seguintes limitações:

- não representa probabilidade de fechamento;
- não possui histórico completo de transição entre estágios;
- Historical Fit apresentou AUC aproximadamente 0,48 isoladamente;
- thresholds são relativos à distribuição atual do pipeline;
- ausência de dados pode reduzir a disponibilidade de informação;
- associação estatística não implica causalidade;
- associação estatisticamente significativa não significa associação forte;
- valor estimado de oportunidades abertas utiliza informação de catálogo quando o valor real de fechamento não está disponível;
- o dataset representa um snapshot histórico, e não uma operação CRM em tempo real;
- Strategy Lab demonstra sensibilidade do ranking aos pesos, mas não determina qual estratégia é comercialmente correta;
- presets do Strategy Lab são cenários de exploração e não recomendações ótimas.

Essas limitações são parte da solução, não algo a esconder.

---

# 23. Próxima evolução possível

Em um cenário de produção, poderiam ser adicionados:

- integração com CRM;
- atualização automática dos dados;
- banco de dados;
- autenticação;
- permissões por vendedor/gestor;
- histórico das estratégias aplicadas;
- acompanhamento de mudanças de pipeline ao longo do tempo;
- feedback do vendedor sobre ações realizadas;
- monitoramento contínuo da qualidade do score;
- eventual modelo preditivo, caso novos dados permitam validá-lo adequadamente.

Esses itens não fazem parte do MVP porque não são necessários para provar o valor central da solução.

---

# 24. Evidências recomendadas para a submissão

A evidência deve demonstrar processo, não apenas produto final.

## Evidência A — Entendimento do problema

Mostrar a decomposição inicial do problema e a definição do produto.

## Evidência B — Evolução do scoring

Mostrar a mudança dos cinco fatores iniciais para os quatro fatores finais.

## Evidência C — GTK 500

Mostrar a descoberta do problema de concentração e a adoção do percentil ponderado por volume.

## Evidência D — Aging

Mostrar a descoberta da inversão e a correção da curva.

## Evidência E — Prospecting

Mostrar hipótese, teste e decisão de não manipular o score.

## Evidência F — Historical Fit

Mostrar AUC aproximadamente 0,48 e a decisão de não apresentar o componente como forte preditor.

## Evidência G — QA

Mostrar as 29 checagens automatizadas passando.

## Evidência H — Precisão da documentação

Mostrar a revisão das afirmações sobre conversão, associação estatística e thresholds.

## Evidência I — Redesign

Mostrar a mudança de uma estética de AI/startup para Sales Intelligence / BI corporativo.

## Evidência J — Strategy Lab

Mostrar:

1. estratégia atual;
2. alteração dos pesos;
3. simulação ativa;
4. impacto no ranking;
5. quem ganhou/perdeu;
6. explicação da mudança;
7. aplicação da estratégia.

## Evidência K — Onboarding

Mostrar o fluxo de primeira utilização do Strategy Lab.

---

# 25. Conclusão

O processo demonstra uma utilização de IA orientada a problema, e não simplesmente geração de código.

A solução começou com uma hipótese de scoring, foi confrontada com os dados e evoluiu por meio de testes, descobertas e correções.

Os principais aprendizados foram:

- nem toda variável disponível deve entrar no score;
- uma fórmula correta pode produzir uma distribuição ruim;
- resultados inesperados devem ser investigados antes de serem “corrigidos”;
- explicabilidade é parte do produto;
- limitações precisam ser explicitadas;
- linguagem precisa evita interpretações incorretas;
- complexidade técnica não é sinônimo de qualidade;
- uma boa interface deve ajudar na decisão, não apenas mostrar dados;
- IA é mais valiosa quando acelera investigação, implementação e iteração;
- simulação estratégica pode gerar mais valor do que adicionar um modelo complexo sem evidência de ganho.

O produto final não tenta substituir o julgamento comercial.

Ele procura melhorar o contexto em que esse julgamento acontece.

A proposta central pode ser resumida em:

> **Transformar dados de pipeline em prioridades comerciais explicáveis e permitir testar diferentes estratégias antes de aplicá-las.**

Ou, em termos do fluxo do produto:

> **Pipeline → Prioridade → Por quê? → O que fazer? → E se? → Decisão**
