# Radar de Oportunidades — Priority Score (v2)

## Objetivo

Priorizar oportunidades comerciais **abertas** (Prospecting/Engaging) por potencial de
atenção comercial — **não** prever probabilidade de fechamento.

O produto final é um **índice de prioridade**, não um modelo de propensão calibrado.
Nenhum componente do score deve ser lido como "chance de ganhar" ou "probabilidade de
conversão": o único componente que apresenta associação estatisticamente significativa
com o resultado fora da amostra é Urgency/Aging (ver seção Validação) — significativa
não é o mesmo que forte (ver detalhes na seção do próprio fator) — e mesmo ele é framed
como *"quanto tempo esse negócio está parado"*, não como *"qual a chance de ele
fechar"*.

## Fórmula

```
Priority Score = 25% × Commercial Potential
                + 25% × Funnel Position
                + 30% × Urgency / Aging
                + 20% × Historical Fit
```

Todos os quatro componentes são normalizados em `[0, 100]`; o Priority Score final
também fica em `[0, 100]` (na prática, o teto real fica bem abaixo de 100 — nenhuma
oportunidade zera todos os quatro fatores simultaneamente no máximo ao mesmo tempo).
Os pesos somam exatamente 100% e são ajustáveis ao vivo em "Ajustar pesos do modelo"
(ver seção "Pesos ajustáveis").

Removidos do cálculo, propositalmente: **Agente de vendas** e **Porte da conta**
(receita/funcionários). Nenhum dos dois mostrou poder de separar negócios Won de Lost
nesta base (mesmo teste de AUC aplicado a Historical Fit — ver Validação), e mantê-los
no score criava a aparência de que "o vendedor" ou "o tamanho da conta" definem
prioridade, o que não é sustentado pelos dados. Continuam disponíveis como **filtros e
contexto** (Vendedor(a), Gerente, Escritório regional, Setor, Receita, Funcionários).

### Commercial Potential (25%)

- **O quê:** preço de tabela do produto (`products.sales_price`), exibido na interface
  como **Estimated Deal Value**.
- **Nunca usa `close_value`** para oportunidades abertas — esse valor só existe quando
  o negócio já fechou, e usá-lo antes disso seria vazamento de dado futuro.
- **Normalização:** percentil que o preço do produto ocupa na distribuição real de
  negócios, **ponderado por volume** — não pela simples posição do produto entre as 7
  SKUs do catálogo. Essa escolha tem uma história: a primeira versão usava
  log-min-max, que deixava o preço bruto da GTK 500 (o produto mais caro, ~5× o
  próximo) esticar a escala inteira. A segunda versão trocou para percentil simples
  entre as 7 SKUs (cada produto = 1/7 do ranking), o que resolveu a sensibilidade ao
  outlier mas criou um novo problema: a GTK 500 tem apenas 40 negócios no histórico
  (0,45% do volume total) — um produto genuinamente raro — mas ainda assim recebia uma
  vantagem estrutural fixa de ~16,7 pontos de percentil sobre o próximo produto, só por
  ocupar 1 de 7 posições no catálogo. Essa vantagem sozinha já era grande o bastante
  para dominar o Top 10 do ranking. A versão final pondera o percentil pelo volume real
  de negócios de cada produto, de forma que um produto raro não ganhe uma vantagem
  desproporcional só por ser uma linha de catálogo distinta.
- **Validação:** correlação entre Priority Score e Estimated Deal Value ≈ **0,53** —
  moderada (Commercial Potential é 25% do peso), mas longe de 1,0. Evidência concreta:
  ordenando as oportunidades abertas só por valor estimado, apenas ~17 das 50 que
  apareceriam no topo também aparecem no Top 50 real do modelo — ou seja, o ranking não
  é "ordenar por valor".

### Funnel Position (25%)

- **O quê:** estágio no funil. Engaging pontua mais que Prospecting.
- **Importante sobre o número usado como referência:** o dataset registra apenas o
  estágio atual de cada negócio e, para Engaging, a data de engajamento — não guarda um
  histórico de transições de estágio por negócio (não dá para ver, retroativamente, que
  um negócio específico passou por Prospecting antes de virar Engaging e depois Won).
  Por isso o score de Engaging **não** é uma taxa de conversão Prospecting→Engaging→Won
  validada estágio a estágio. O número usado (63,2%) é a taxa de vitória agregada entre
  os negócios já fechados (Won/Lost) da base — uma referência histórica geral, não uma
  afirmação causal de que "chegar a Engaging" produz essa taxa de conversão. Prospecting
  usa uma estimativa heurística mais baixa (35 pontos fixos), por não ter nenhum sinal
  de desfecho histórico equivalente no dataset.

### Urgency / Aging (30%)

- **O quê:** tempo em Engaging, comparado à janela histórica de aging. É o **maior
  peso do modelo** porque é o único componente que apresenta associação
  estatisticamente significativa com o resultado fora da amostra (correlação
  ponto-bisserial `r ≈ 0,118`, `p < 0,0001` no conjunto de teste, holdout cronológico
  70/30). É importante não superinterpretar esse número: `r ≈ 0,118` é uma associação
  estatisticamente detectável, mas **fraca** em magnitude — Aging não é, sozinho, um bom
  previsor de resultado; é só o único dos quatro fatores em que essa associação existe e
  é estatisticamente significativa (`p < 0,0001`), o que já não é verdade para os
  outros três.
- **O que o score representa:** um índice de atenção/urgência, não uma probabilidade de
  fechamento. A regra central é *"mais tempo parado → maior urgência para
  intervenção"*, nunca o inverso.
- **Mecânica:** dentro da janela historicamente observada (até 138 dias — o ciclo mais
  longo já registrado entre negócios fechados), o score sobe com o tempo parado, até um
  teto de 90 pontos. Além de 138 dias — território sem precedente nos dados de negócios
  fechados, por viés de sobrevivência: um negócio que ficasse parado para sempre nunca
  apareceria no histórico de Won/Lost — o score **continua subindo, nunca cai**, rumo a
  100, mas cada vez mais devagar (curva saturante). Essa é a segunda versão dessa
  regra: a primeira versão testada decaía o score depois de 138 dias, o que invertia o
  conceito pretendido (negócios extremamente parados ficavam com pontuação de urgência
  MENOR que negócios moderadamente parados). A correção elimina essa inversão sem cair
  no erro oposto de tratar "mais dias" como sinônimo de "deal melhor": o score nunca
  extrapola além de 100, e a maior parte do ganho por dias adicionais é conquistada logo
  ao passar dos 138 dias, não indefinidamente.
- **138 dias** é mantido como referência visível na interface (linha tracejada no
  gráfico de aging, texto no drawer de cada oportunidade).

### Historical Fit (20%)

- **O quê:** taxa de conversão (win rate) histórica, suavizada, buscada em hierarquia:
  **Account History** (histórico da própria conta, exigindo no mínimo 5 negócios
  fechados) → **Product History** (histórico da série do produto) → **Baseline**
  (média geral da base). A suavização usa apenas negócios fechados **antes** do
  snapshot usado para pontuar as oportunidades abertas — sem vazamento de dado futuro.
- **Mede exclusivamente win rate** — não usa mais valor médio histórico no cálculo.
  Uma versão anterior misturava 70% valor + 30% win rate; isso duplicava, sob um nome
  diferente, o mesmo sinal de "produto caro" que Commercial Potential já captura (o
  produto/conta com maior valor médio histórico tende a ser, pela própria definição, o
  produto/conta de maior preço). Essa duplicação foi uma das causas da concentração
  excessiva em GTK 500 no ranking inicial: dois fatores com pesos somados de 45%
  (Commercial Potential 25% + Historical Fit 20%) empurravam na mesma direção pelo
  mesmo motivo. Isolar Historical Fit para win rate elimina essa redundância.
- **Validação:** nenhuma associação estatisticamente significativa com o resultado no
  teste fora da amostra (AUC ≈ 0,48 — equivalente a acaso), o mesmo padrão que Agente e
  Porte da conta já mostravam antes de saírem do cálculo. Historical Fit permanece no
  modelo (peso 20%, o menor entre os quatro) porque ainda captura um sinal legítimo de
  "esse tipo de conta/produto converte historicamente", mesmo sem associação validada
  fora da amostra isoladamente — mas o app deixa claro, no texto e na aba Validação, que
  esse componente não é uma probabilidade calibrada.

## Data Confidence

Cada oportunidade recebe um selo de confiança (Alta/Média/Baixa) baseado em quanto do
score depende de dado real vs. default neutro:

- **Alta:** conta vinculada no CRM e negócio já em Engaging (tem data de engajamento).
- **Média:** falta um dos dois sinais acima.
- **Baixa:** faltam os dois.

Isso é uma lacuna de **cadastro**, não um sinal de risco comercial — por isso é
separado explicitamente de "Risco comercial" (aging acima de 138 dias em Engaging),
que é um alerta de outra natureza.

## Recommended Action

Cada oportunidade recebe uma ação sugerida, derivada de regras simples sobre os
próprios componentes do score (nunca hardcoded independentemente do cálculo):

- Prospecting → "Qualificar antes de investir mais esforço."
- Aging acima de 138 dias em Engaging → "Reengajar e definir próximo passo."
- Commercial Potential ou Historical Fit ≥ 66/100 → "Priorizar contato e avançar
  estágio."
- Caso contrário → "Acompanhar no ritmo padrão do funil."

## Pesos ajustáveis

O painel "Ajustar pesos do modelo" permite simular como o ranking muda com pesos
diferentes para os 4 componentes (Commercial Potential, Funnel Position, Urgency/Aging,
Historical Fit — Vendedor(a) e Porte da conta não entram, porque não fazem parte do
score). Mover um slider redistribui automaticamente a diferença pelos outros três,
proporcionalmente ao peso atual de cada um — a soma dos pesos é **sempre exatamente
100%**, nunca precisa de aviso de inconsistência. Qualquer alteração recalcula, ao
vivo: pontuação → ranking → prioridade (Crítica/Alta/Média/Baixa) de todas as 2.089
oportunidades abertas.

## Strategy Lab (simulador de estratégia)

O Strategy Lab responde a uma pergunta específica: **"Se minha estratégia comercial
mudasse, como o pipeline mudaria — e por quê?"** Ele existe para transformar o ajuste
de pesos em uma decisão, não para adicionar um segundo modelo ao produto.

### O que o Strategy Lab NÃO é

- **Não é um modelo novo.** Não treina nada, não usa XGBoost/ML/rede neural, não chama
  nenhuma API ou LLM. A simulação inteira roda em memória, no navegador, sobre dados já
  calculados.
- **Não prevê fechamento.** Não estima probabilidade de venda, não é um motor de
  propensão. Simula apenas *reordenação de prioridade* sob pesos diferentes.
- **Não descobre pesos "ótimos" automaticamente.** As 4 estratégias prontas (Balanceada,
  Proteger pipeline, Maximizar valor, Avançar oportunidades) são combinações
  *ilustrativas* de pesos, escolhidas para mostrar diferentes ênfases possíveis — nunca
  apresentadas como a "melhor" configuração. Encontrar pesos ideais continua sendo uma
  decisão humana, feita nos sliders.
- **Não altera nenhum dado de oportunidade.** Os 4 scores de fator de cada negócio
  (Commercial Potential, Funnel Position, Urgency/Aging, Historical Fit) são fixos —
  só os **pesos** aplicados a eles mudam durante uma simulação.

### Como funciona

O Priority Score sempre foi `Σ(fator × peso)` — a única mudança é que essa soma agora
vive em uma função pura reutilizável, `calculateScore(oportunidade, pesos)`
(`factorContribs()` + `calculateScore()` em `dashboard_template.html`), chamada por
**todo** lugar do produto que precisa de um score: o modelo oficial
(`recomputeScores()`), a coluna "Sinal principal" da tabela, e o motor de simulação do
Strategy Lab. Não existem duas fórmulas — o Strategy Lab literalmente chama a mesma
função com um segundo objeto de pesos (`SIMULATED_MODEL`, mantido só em memória, em
`stratLab.weights`) em vez de reescrever a conta em outro lugar.

Ajustar um peso no Strategy Lab redistribui automaticamente a diferença pelos outros
três (mesma lógica de "Ajustar prioridades", generalizada em
`redistributeWeights(pesos, fatorMovido, novoValor)` para funcionar em qualquer objeto
de pesos) — os 4 pesos simulados sempre somam exatamente 100%, nunca ficam negativos.

Enquanto a simulação está ativa (pesos simulados ≠ pesos oficiais), a interface mostra
um aviso "Simulação ativa" e **nada é persistido**: o modelo oficial
(`state.weights`), o score/rank/prioridade exibidos em Oportunidades e Visão geral, e
os dados usados pelo resto do produto continuam exatamente como estavam antes de abrir
o Strategy Lab. Fechar a aba, trocar de tela ou recarregar a página sem clicar em
"Aplicar estratégia" descarta a simulação sem deixar rastro.

### Ranking e prioridade recalculados para a simulação

O ranking simulado é recomputado sobre **todas** as oportunidades abertas do pipeline
(as mesmas ~2.089 do modelo oficial) — nunca sobre um subconjunto filtrado da aba
Oportunidades, preservando a mesma semântica de "Rank #X de 2.089" usada em todo o
produto. As faixas de prioridade simuladas (Crítica/Alta/Média/Baixa) também são
recalculadas a partir dos percentis (p95/p75/p25) da distribuição de score **simulada**
— exceto quando os pesos simulados são idênticos aos oficiais, caso em que os mesmos
limites já em uso são reaproveitados diretamente, para que "simulação sem mudança
nenhuma" produza zero diferenças (e não ruído de arredondamento entre dois cálculos
independentes de percentil). Como sempre, essas faixas continuam relativas ao pipeline
atual — nunca uma probabilidade de fechamento.

### Explicação de cada mudança (determinística, sem IA)

Cada oportunidade que muda de posição no Top Movers mostra um "principal motivo" —
qual dos 4 fatores mais empurrou o score para cima ou para baixo, comparando a
contribuição em pontos **atual vs. simulada** da própria oportunidade
(`moverReason()`). Isso não é gerado por um modelo de linguagem: é a mesma matemática
usada para calcular o score, só exibida de forma legível (o fator cuja diferença de
contribuição, em pontos, é a maior em valor absoluto).

### Aplicar e restaurar

- **"Aplicar estratégia"** (com confirmação explícita: *"Aplicar esta estratégia ao
  Radar? Isso alterará a priorização exibida para todos os usuários."*) é o único jeito
  de a simulação deixar de ser simulação: os pesos simulados substituem os pesos
  oficiais (`state.weights`), as faixas de prioridade são recalculadas para o novo
  modelo, e Oportunidades/Visão geral são re-renderizados imediatamente com os novos
  valores. A partir daí, esse novo modelo *é* o modelo oficial — não existe mais
  distinção entre "atual" e "simulado" até alguém abrir uma nova simulação.
- **"Restaurar atual"** cancela a simulação em andamento e volta os sliders do Strategy
  Lab para os pesos oficiais vigentes, sem tocar em nada fora da própria tela.

### Performance

A simulação não faz nenhuma chamada de rede, não recalcula os 4 scores de fator
individuais (já computados uma vez por oportunidade) e não reprocessa dados brutos —
apenas uma soma ponderada + reordenação + reclassificação de faixa sobre valores já
prontos. Nas ~2.089 oportunidades abertas, isso é aritmética simples o bastante para
recalcular a cada movimento de slider sem perceptível atraso.

### Onboarding do Strategy Lab

Na primeira vez que qualquer usuário/navegador abre a aba Strategy Lab, um tour guiado
de 4 etapas (~30-45s) aparece sozinho, explicando a área sem jargão técnico (nunca
"algoritmo", "otimização", "modelo estatístico" ou "probabilidade de conversão"):
o que é o Strategy Lab, como ajustar os pesos, como ler quem ganhou/perdeu prioridade,
e que a simulação só se torna oficial ao clicar em "Aplicar estratégia". Cada etapa
destaca (com o mesmo anel azul usado no onboarding geral do produto) o elemento real da
tela que está sendo explicado — nunca uma captura de tela ou mockup à parte. "Pular
tutorial" e "Avançar" ficam disponíveis em toda etapa; ESC também fecha. Depois de
concluído ou pulado, o tour não reaparece sozinho (estado salvo em
`localStorage['roa-sl-onboarding-done']`, uma chave própria — independente da chave do
onboarding geral do produto); o link "Como funciona?" no topo da tela reabre quando
quiser.

Logo após clicar em "Começar a simular" (a etapa final do tour), um guia curto e
dispensável destaca em sequência os controles de peso, a área de impacto e a tabela de
maiores mudanças — sem escurecer a tela e sem bloquear nenhuma interação — para que a
primeira mudança de peso do usuário já aconteça no lugar certo, sem ele precisar
procurar onde está o resultado.

Tecnicamente, esse onboarding reaproveita **o mesmo mecanismo** do onboarding geral do
produto (função `createOnboarding()`, extraída para os dois usarem exatamente a mesma
lógica de passos/dots/destaque/persistência) — só o conteúdo e os elementos-alvo do
destaque são diferentes. Nenhuma arquitetura paralela foi criada.

## Faixas de prioridade

Os limites de Crítica/Alta/Média/Baixa são calculados a partir dos **percentis reais**
da distribuição do score deste modelo (p95/p75/p25), não de um corte fixo arbitrário —
um corte fixo em 90/75/50, por exemplo, deixaria a faixa "Crítica" praticamente vazia,
já que nenhuma oportunidade atinge o máximo simultâneo dos 4 fatores. Valores atuais:

| Faixa | Limite mínimo |
|---|---|
| Crítica | 79,5 |
| Alta | 72,5 |
| Média | 57,4 |
| Baixa | abaixo de 57,4 |

Estes limites são recalculados sempre que o modelo (pesos, normalização ou dados de
origem) muda — não são uma constante fixa no código.

**As faixas representam prioridade relativa dentro do pipeline atual — não um patamar
absoluto de qualidade.** Como os limites são percentis da própria distribuição, sempre
vai existir uma faixa "Crítica" (top ~5% do pipeline aberto), mesmo que o pipeline
inteiro melhore ou piore de um período para o outro. Uma oportunidade classificada como
Crítica é, por definição, uma das que mais merecem atenção *dentro do conjunto atual de
oportunidades abertas* — não necessariamente uma oportunidade crítica em termos
absolutos (ex.: mesmo com um pipeline geral mais fraco, ~5% dele ainda cairá em
Crítica). Recalcular os limites a cada atualização do modelo é o que garante que essa
comparação relativa continue fazendo sentido; não é o que garante um padrão absoluto de
qualidade — esse não é o objetivo desta faixa.

## QA automatizado

`qa_scoring.py` roda um conjunto de checagens automáticas sobre a saída do motor de
score e do payload consumido pela interface, entre elas: `score` sempre em `[0,100]`
e nunca `NaN`; `opportunity_id` único; apenas oportunidades abertas entram no ranking;
todo negócio tem join válido com `products.csv`; Estimated Deal Value bate exatamente
com `products.sales_price` (nunca `close_value`); `score = Commercial Potential ×
25% + Funnel Position × 25% + Urgency/Aging × 30% + Historical Fit × 20%` para
todas as oportunidades, dentro de tolerância numérica; e que o score exibido na
Explainability da interface é exatamente a soma dos 4 pontos por fator exibidos no
drawer, respeitando os pesos correntes.

`pw_strategylab_qa.py` cobre especificamente o Strategy Lab, com 15 checagens rodadas
via Playwright contra o HTML final (usando um hook somente-leitura,
`window.__RADAR_QA__`, que expõe `calculateScore`/`simulate`/`state`/`stratLab` para
inspeção — não altera comportamento nenhum do produto): pesos sempre somam 100% e
nunca ficam negativos; score sempre em `[0,100]`, inclusive em pesos extremos; mudar
peso nunca altera os 4 scores de fator individuais; ranking simulado cobre todas as
oportunidades abertas (nunca um subconjunto filtrado) e nenhuma desaparece; Top Movers
batem com um recálculo independente de rank/score; o score/rank/prioridade oficiais
não mudam enquanto uma simulação está ativa; "Aplicar estratégia" realmente
sobrescreve os pesos oficiais; "Restaurar atual" realmente reverte; a explicação de
cada mudança usa exatamente os mesmos valores do cálculo (mesma função, não uma
duplicata); as faixas de prioridade são recalculadas para a simulação; filtros da aba
Oportunidades não afetam o ranking global; e nenhuma simulação dispara chamada de
rede ou depende de termos/padrões de ML e LLM.

`pw_sl_onboarding_qa.py` cobre o onboarding do Strategy Lab: aparece sozinho só na
primeira entrada; 4 etapas com os títulos/CTAs corretos; cada etapa destaca o elemento
real esperado; copy sem jargão técnico e sem prometer estratégia "ideal"; Voltar/
Avançar/ESC/"Pular tutorial" funcionam; estado persiste numa chave própria
(`roa-sl-onboarding-done`) sem tocar na chave do onboarding geral; "Como funciona?"
reabre; o onboarding geral do produto continua funcionando normalmente e de forma
independente (mesma refatoração do mecanismo, comportamento original preservado); e o
guia curto pós-onboarding aparece na sequência esperada (pesos → impacto → maiores
mudanças) e some sozinho.

Há ainda `pw_uxround_qa.py`, com 63 checagens de UX/UI (onboarding, navegação,
drawer, filtros, painel de pesos, responsividade mobile). Todas as checagens — as 29
de scoring, as 15 do Strategy Lab, as do onboarding do Strategy Lab e as 63 de UX —
devem passar antes de publicar uma nova versão do dashboard.

## Limitações (documentadas explicitamente)

- **Dados históricos limitados:** o histórico Won/Lost usado para calibrar o modelo
  cobre um período específico (out/2016–dez/2017); padrões fora dessa janela podem não
  se repetir.
- **Ausência de conta vinculada em parte das oportunidades abertas:** quando isso
  acontece, Historical Fit cai para o baseline geral (não o da conta), e o selo de Data
  Confidence reflete essa lacuna.
- **`Estimated Deal Value` é baseado no catálogo (preço de tabela), não no valor
  final negociável:** o valor real de fechamento de um negócio aberto é desconhecido
  até ele fechar; o modelo nunca usa `close_value` para negócios abertos.
- **Ausência de histórico de transições de estágio:** o dataset não registra a
  sequência completa de mudanças de estágio de cada negócio, só o estágio atual e (para
  Engaging) a data de engajamento — então Funnel Position é um sinal de estágio atual,
  não de velocidade de progressão.
- **O score não é uma probabilidade.** Não é calibrado, não soma a 100% entre
  concorrentes, e não deve ser lido como "X% de chance de fechar". É um índice de
  prioridade comercial relativa.
- **Aging representa urgência de atenção, não qualidade da oportunidade.** Um negócio
  com aging elevado não é necessariamente "melhor" ou "pior" — é um negócio que está
  pedindo uma decisão (reengajar, escalar ou encerrar) há mais tempo que o normal.

## Arquivos

| Arquivo | Função |
|---|---|
| `scoring_model.py` | Baselines históricos (win rate, curva de aging, Commercial Potential, Historical Fit hierárquico) |
| `build_scores.py` | Motor de score — calcula os 4 componentes e o Priority Score para cada oportunidade aberta |
| `prepare_dashboard_data.py` | Gera `dashboard_data.json` (payload consumido pela interface), incluindo os dados de Validação |
| `qa_scoring.py` | Checagens automáticas de qualidade sobre o motor de score e o payload (29 checks) |
| `pw_strategylab_qa.py` | Checagens automáticas do Strategy Lab via Playwright (15 checks) |
| `pw_sl_onboarding_qa.py` | Checagens automáticas do onboarding do Strategy Lab via Playwright |
| `pw_uxround_qa.py` | Checagens automáticas de UX/UI via Playwright (63 checks) |
| `dashboard_template.html` | Template da interface (HTML/CSS/JS) — inclui o Strategy Lab — com `__DASHBOARD_DATA__` como placeholder |
| `inject.py` | Injeta `dashboard_data.json` no template, gerando `radar_oportunidades.html` |
