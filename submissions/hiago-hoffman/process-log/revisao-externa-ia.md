# Análise e proposta de score comercial adaptativo

## 1. Diretriz principal

O score deve aprender padrões gerais do processo comercial, sem regras associadas a nomes específicos de vendedores, produtos, contas ou regiões. A base atual é uma amostra para formular e testar hipóteses; não é um conjunto de verdades permanentes sobre vendas.

Novos vendedores, produtos e regiões devem receber estimativas úteis desde o primeiro registro. Conforme resultados se acumulam, essas estimativas podem se especializar, com ajustes proporcionais à quantidade, atualidade e consistência da evidência.

**A estrutura da decisão deve ser estável e auditável; seus parâmetros devem ser aprendidos e atualizados.** Aprender continuamente não significa alterar a regra em produção a cada venda: significa incorporar novos dados, produzir uma versão candidata, avaliá-la e promover mudanças quando houver evidência suficiente.

Este documento propõe a arquitetura e a lógica de cálculo. Não representa um modelo já treinado, calibrado ou validado em produção.

## 2. O que muda em relação à proposta anterior

| Proposta anterior | Revisão proposta |
|---|---|
| Pesos fixos de 70% para valor e 30% para tempo | Substituir pela estimativa de receita em um horizonte definido, com efeito de tempo aprendido. |
| Faixas de idade com multiplicadores arbitrários | Aprender a relação entre idade, calendário e desfechos, admitindo relações não lineares. |
| 138 dias como fronteira de atuação | Tratar como máximo histórico observado nesta amostra; aprender alertas de idade e não usá-lo como regra universal. |
| Maior preço do catálogo como referência de normalização | Usar valor monetário estimado e uma transformação de apresentação versionada, sem depender do nome ou preço de um produto específico. |
| Exclusão inicial de vendedor e região | Investigar efeitos de vendedor × produto e região × produto com regularização, recuo para grupos mais amplos e validação temporal. |
| Probabilidades calculadas apenas com Won e Lost | Incorporar o tempo de observação e oportunidades ainda abertas. |

Os pesos heurísticos anteriores poderiam servir como baseline experimental, mas não deveriam ser a arquitetura definitiva de uma solução que precisa aprender.

## 3. O que a base atual permite concluir

Na verificação independente dos arquivos do dataset, com referência em 31/12/2017, foram encontrados:

- 8.800 oportunidades: 4.238 Won, 2.473 Lost, 1.589 Engaging e 500 Prospecting.
- Conversão de 63,15% entre oportunidades encerradas. Essa não é automaticamente a probabilidade de ganho das abertas.
- 1.291 Engaging acima de 138 dias, o maior ciclo observado entre os encerrados.
- 1.425 oportunidades abertas sem conta; nenhum encerrado sem conta.
- Diferenças expressivas de valor entre produtos, sem evidência forte de efeito agregado de produto, vendedor ou região sobre ganho/perda nos testes realizados.
- Interações vendedor × produto que merecem investigação, mas não autorizam regras especiais por nome. Foram testadas 178 combinações; o destaque de Hayden/MG Advanced não se sustentou após correção Benjamini–Hochberg, com q aproximado de 0,30.
- Forte estrutura temporal: todos os 1.779 encerramentos nos primeiros meses de trimestre observados tiveram ciclo de no máximo 13 dias.

Esses resultados sugerem testar valor, tempo, interações e qualidade da observação. Não demonstram que os mesmos padrões se repetirão em outra empresa ou período.

A base descreve uma empresa fictícia. É apropriada para demonstrar o funcionamento da solução, mas a estabilidade de suas regularidades em operação real precisa ser verificada.

## 4. Definir o que o score pretende otimizar

Antes de escolher algoritmos, é necessário definir a decisão: quais oportunidades merecem atenção comercial dentro da capacidade disponível?

O objetivo inicial recomendado é **priorizar receita provável em um horizonte H**, por exemplo 30 dias. O horizonte é uma configuração do negócio, e não um número escolhido automaticamente para fazer o modelo parecer melhor.

Para uma oportunidade i, na data t:

```text
p_i(H) = P(ganhar entre t e t + H | ainda aberta em t, informações disponíveis em t)

v_i(H) = E(valor realizado | ganhar entre t e t + H, informações disponíveis em t)

R_i(H) = p_i(H) × v_i(H)
```

`R_i(H)` é a receita esperada dentro do horizonte. A definição de valor condicionada ao mesmo horizonte torna a decomposição consistente.

O score não deve confundir três conceitos:

| Conceito | Significado |
|---|---|
| Probabilidade | Chance de um evento definido dentro de um prazo. |
| Receita esperada | Probabilidade multiplicada pelo valor esperado quando o evento ocorre. |
| Prioridade | Posição operacional que também pode considerar capacidade e restrições explícitas do negócio. |

Receita esperada ainda não mede o benefício incremental de uma ligação ou reunião. Uma oportunidade pode fechar sem intervenção. Para aprender o efeito da ação comercial, serão necessários registros de intervenções e avaliação experimental ou causal adequada.

## 5. Como calcular o score exibido

Recomendo ordenar oportunidades comparáveis por `R_i(H)` e apresentar separadamente probabilidade, valor e receita esperada. O número de 0 a 100 deve ser apenas uma transformação monotônica de apresentação:

```text
Score_i = 100 × R_i(H) / (R_i(H) + K)
```

`K` é uma referência positiva de receita esperada, calculada em uma população de referência explicitamente definida e registrada na versão do score. Uma opção inicial é a mediana das receitas esperadas positivas dessa população.

- Receita esperada igual a K produz score 50.
- Receita esperada igual a 3K produz score 75.
- Receita esperada igual a 9K produz score 90.
- A transformação não altera a ordem das oportunidades.
- K não deve ser recalculado ao filtrar a tela por vendedor ou região.
- Se não houver histórico suficiente para definir K, exibir receita esperada e ordenação, sem fabricar um score normalizado.

Exemplo apenas ilustrativo, sem representar parâmetros aprendidos da base:

| Oportunidade | p em 30 dias | Valor se ganhar | Receita esperada | Score com K = 1.000 |
|---|---:|---:|---:|---:|
| A | 40% | 5.000 | 2.000 | 66,7 |
| B | 60% | 2.000 | 1.200 | 54,5 |
| C | 10% | 20.000 | 2.000 | 66,7 |

A e C empatam em receita esperada, mas têm riscos diferentes. A interface deve mostrar essa diferença. Preferências por previsibilidade, margem ou esforço precisam ser políticas explícitas, não ajustes ocultos da probabilidade.

A referência K pode mudar em uma nova versão. Comparações históricas devem preservar a versão utilizada e privilegiar probabilidade e receita esperada, pois scores de versões diferentes não são necessariamente equivalentes.

## 6. Como aprender a probabilidade

### 6.1 Aprender com oportunidades abertas e encerradas

Uma oportunidade ainda aberta não é uma perda. Ela contém informação de que nenhum encerramento foi observado até determinada data.

Uma abordagem adequada é modelar dois eventos concorrentes: ganho e perda. Em intervalos de tempo, estimar:

```text
h_ganho(k) = chance de ganhar no intervalo k, dado que segue aberta
h_perda(k) = chance de perder no intervalo k, dado que segue aberta

S(0) = 1
S(k) = S(k-1) × [1 - h_ganho(k) - h_perda(k)]

p_i(H) = soma de S(k-1) × h_ganho(k) nos intervalos até H
```

As probabilidades dos dois eventos devem ser estimadas conjuntamente ou com uma parametrização que respeite soma menor ou igual a 1. Registros sem desfecho contribuem até o fim de sua observação; não são convertidos artificialmente em Lost.

Um modelo de sobrevivência em tempo discreto com regularização é um candidato inicial. Alternativamente, um modelo de ganho em horizonte fixo pode usar apenas exemplos com acompanhamento suficiente. A escolha deve ser orientada pela validação, não por preferência tecnológica.

### 6.2 Variáveis gerais candidatas

| Grupo | Exemplos | Condição de uso |
|---|---|---|
| Tempo | Idade desde entrada no estágio, tempo desde última atividade | Datas conhecidas no momento da previsão. |
| Estágio | Estágio atual e tempo nele | Definições consistentes e histórico de alterações. |
| Produto | Família, preço, atributos e efeitos aprendidos por produto | Produto novo deve funcionar sem histórico próprio. |
| Responsabilidade | Vendedor, equipe, região e suas interações com produto | Regularização e tratamento de mudanças de carteira. |
| Conta | Setor, porte, histórico comercial anterior | Não preencher retrospectivamente atributos que eram desconhecidos. |
| Atividade | Respostas, reuniões, próximo compromisso, proposta | Não existem na base atual; requerem instrumentação. |
| Calendário | Data atual e calendário comercial conhecido | Nunca usar a data futura real de fechamento. |

Não é necessário usar todos esses campos. Uma variável permanece no modelo quando sua contribuição se sustenta em avaliação futura e sua disponibilidade operacional é confiável.

Características futuras ainda desconhecidas não podem ser fornecidas ao modelo na previsão. Em horizontes de vários intervalos, variáveis como idade e calendário podem evoluir deterministicamente; atividades futuras precisam ser marginalizadas, modeladas ou tratadas sob uma hipótese explícita.

### 6.3 Vendedor e região por produto

Essas interações devem ser candidatas, sem regras como “dar bônus ao vendedor X”. O princípio geral é:

> Estimar se o desempenho recente dessa combinação difere da referência, considerando exposição, calendário, características das oportunidades e incerteza.

Um modelo hierárquico pode combinar efeitos globais, de família/produto, de região × produto e de vendedor × produto. Os efeitos devem ser estimados conjuntamente para evitar contar duas vezes a mesma associação regional e individual.

Em uma ilustração simplificada de encolhimento:

```text
estimativa ajustada = w × estimativa local + (1 - w) × referência
w = n_efetivo / (n_efetivo + força_de_regularização)
```

Essa fórmula explica o mecanismo; não substitui o modelo temporal e não deve ser aplicada ingenuamente à taxa Won/(Won+Lost). A referência, a força de regularização e a composição dos grupos devem ser selecionadas com dados de treinamento e validação.

Muitas linhas históricas da mesma oportunidade não equivalem a muitas oportunidades independentes. A confiança e o tamanho efetivo de amostra devem respeitar esse agrupamento.

## 7. Novos vendedores, produtos e regiões

| Situação | Comportamento esperado |
|---|---|
| Novo vendedor | Começa com a referência da equipe/região/produto quando sustentada; caso contrário, referência mais ampla. Sem punição por falta de histórico. |
| Novo produto | Usa atributos conhecidos, como família e preço. Sem pares comparáveis, recua para referência global e indica maior incerteza. |
| Nova região | Usa referências de produto e população mais ampla, sem inventar uma vantagem regional. |
| Combinação nova de vendedor e produto | Usa componentes mais amplos já estimados; o efeito específico começa neutro. |
| Mudança de equipe ou região | Usa a atribuição válida na data da previsão. Não reescreve o passado com a estrutura atual. |
| Poucos resultados recentes | Mantém maior encolhimento e evita mudanças bruscas. |

Identificadores podem existir como chaves para estimar efeitos; o que não pode existir são exceções programadas por nome. IDs desconhecidos devem ser tratados sem erro e sem probabilidade zero.

Generalização também tem limite: um produto sem semelhantes, com preço ou processo comercial muito diferente, exige indicação de baixa sustentação histórica e acompanhamento. O modelo não deve apresentar precisão artificial.

## 8. Como aprender o valor

Usar primeiro o valor da proposta conhecido na data da previsão, quando confiável. Caso não exista, estimar o valor condicionado ao ganho a partir do catálogo e do histórico disponível.

Uma abordagem inicial é aprender a relação entre valor realizado e preço de tabela, com recuo entre produto, família e população global. Produtos novos podem começar pelo preço de tabela como proxy explícita até existir evidência melhor.

Não usar `close_value` realizado como entrada para prever uma oportunidade antes de seu fechamento. Esse valor é um resultado para treinamento, não informação disponível antecipadamente.

Descontos, quantidades, moeda e atualização de catálogo precisam ser tratados quando existirem. A proximidade entre preço e valor observada nesta base não garante que uma venda futura seja de uma única unidade ou siga a mesma política comercial.

## 9. Idade atípica e qualidade cadastral

### Idade

O limiar de alerta pode ser aprendido por grupos com amostra suficiente, considerando a distribuição de tempo até encerramento e negócios ainda abertos. Grupos pequenos recuam para referências mais amplas.

A política que define o nível de alerta — por exemplo, o grau de excepcionalidade que merece revisão — é uma decisão operacional. O valor em dias correspondente pode mudar com os dados.

O alerta não deve encerrar o negócio nem impor probabilidade zero. O caso deve ser apresentado para revalidação, com a evidência que motivou o alerta. O número 138 não deve aparecer como constante universal no código.

### Cadastro

Ausência de conta, contato ou próximo passo deve gerar tarefas. Não implica automaticamente menor chance de ganho.

Um campo ausente só pode influenciar previsão após verificar se a ausência era conhecida naquele momento e se o efeito se repete fora da amostra. Na base atual, todas as oportunidades encerradas têm conta e muitas abertas não; isso pode refletir preenchimento administrativo associado ao encerramento.

Probabilidade, sustentação histórica da estimativa e condição de executar a próxima ação devem ser exibidas separadamente. Evitar multiplicar a probabilidade por uma nota arbitrária de qualidade cadastral.

## 10. Como o sistema aprende continuamente

Separar atualização de dados, recálculo de previsões e atualização do modelo:

1. **Ingestão:** ler mudanças do CRM em frequência compatível com a operação, preservando IDs, datas de evento e de ingestão.
2. **Validação:** verificar duplicidades, mudanças de esquema, datas impossíveis, moeda, estágios e integridade dos relacionamentos. Preservar o dado bruto e registrar correções.
3. **Histórico:** armazenar o estado conhecido em cada data; manter oportunidades reabertas e mudanças de responsável como eventos.
4. **Pontuação:** recalcular quando uma informação relevante mudar, usando a versão aprovada do modelo.
5. **Formação de resultados:** observar ganhos, perdas e duração sem antecipar rótulos ainda não conhecidos.
6. **Treinamento candidato:** incorporar resultados novos, comparar janelas e pesos de recência e estimar novos parâmetros.
7. **Validação:** comparar candidato, modelo vigente e baseline por preço em períodos posteriores ao treinamento.
8. **Promoção:** publicar somente quando os critérios previamente definidos forem atendidos.
9. **Monitoramento:** acompanhar resultados, segmentos, falhas de dados e possibilidade de retorno à versão anterior.

Uma cadência inicial possível é atualizar dados e previsões diariamente e avaliar retreinamento semanalmente. Esses intervalos são configurações operacionais, não conclusões da base. Sem volume suficiente de resultados novos, manter o modelo vigente e aguardar mais evidência.

Para reduzir a dependência de resultados antigos, pode-se testar ponderação por recência:

```text
peso do resultado = 2 ^ (-tempo desde o resultado / meia-vida)
```

A meia-vida deve ser selecionada por validação temporal. Não escolher um prazo arbitrário nem contar oportunidades ainda sem desfecho como perdas. Modelos de duração precisam tratar corretamente seus intervalos observados.

Mudança no perfil dos dados deve disparar investigação e avaliação de candidatos; não promoção automática. Falhas de extração também parecem mudanças de comportamento.

## 11. O que pode mudar automaticamente e o que exige decisão explícita

| Elemento | Política recomendada |
|---|---|
| Efeitos de tempo, produto, vendedor e região | Aprendidos em cada treinamento candidato, com regularização. |
| Relação entre preço e valor realizado | Atualizada com resultados disponíveis e validação. |
| Calibração das probabilidades | Reestimada em dados temporais separados, quando houver volume suficiente. |
| Janela de treinamento e peso de recência | Selecionados entre alternativas documentadas por validação. |
| Limiares de idade em dias | Reestimados sob uma política operacional estável e documentada. |
| Referência K de apresentação | Atualizada apenas em versões identificadas; nunca ao mudar filtros da tela. |
| Objetivo, horizonte e restrições comerciais | Definidos pelo negócio; não alterados silenciosamente pelo treinamento. |
| Novos campos e mudanças de significado | Exigem verificação de disponibilidade, vazamento e compatibilidade. |
| Encerramento de oportunidades ou troca de responsável | Não são consequências automáticas do score. |

Não é necessário permitir que uma IA reescreva livremente fórmulas e código. Um pipeline de treinamento e seleção de versões permite adaptação com rastreabilidade.

## 12. Validação e critérios de promoção

Reconstruir carteiras em datas históricas. Para cada data, usar somente informações e resultados disponíveis até aquele momento. Avaliar o que aconteceu no horizonte seguinte.

Comparar pelo menos:

- Ordenação apenas por valor estimado.
- Modelo geral de tempo e características da oportunidade.
- Modelo com região × produto.
- Modelo com região × produto e vendedor × produto.

Medir:

| Métrica | Pergunta respondida |
|---|---|
| Receita realizada nas primeiras K posições | A lista encontra mais receita dentro da capacidade do time? |
| Calibração por horizonte | O grupo com previsão de 30% ganha aproximadamente nessa proporção no prazo definido? |
| Brier score ou log loss apropriados à observação | As probabilidades são melhores que as referências? |
| Cobertura e desempenho em entidades novas | A regra funciona para quem não tinha histórico? |
| Estabilidade entre períodos e segmentos | A melhora é persistente ou concentrada em um recorte? |
| Mudança de posição entre versões | O ganho justifica a alteração na rotina comercial? |

Testes devem usar períodos futuros separados da escolha de parâmetros, tratar censura quando aplicável e evitar vazamento entre observações da mesma oportunidade. A reconstrução precisa representar o momento real da previsão; um split aleatório de linhas não resolve isso.

O limiar de promoção deve ser definido antes da avaliação, segundo volume, incerteza e relevância comercial. Não há evidência nesta análise para inventar uma melhora mínima universal em percentual.

Backtest mede capacidade preditiva sob a política comercial histórica. Demonstrar aumento de receita causado pela ferramenta requer piloto prospectivo, idealmente com comparação controlada e unidade de randomização compatível com a operação.

## 13. Evitar que o aprendizado reforce seus próprios erros

Quando o time passa a agir pela lista, os negócios bem posicionados recebem mais atenção. Seus resultados deixam de ser independentes do score.

O sistema deve registrar score exibido, versão, ação recomendada, ação realizada e desfecho. Também precisa acompanhar oportunidades pouco priorizadas e entidades novas.

Uma política explícita de exploração pode reservar parte da capacidade para oportunidades com incerteza elevada, sob critérios comerciais. O tamanho dessa reserva precisa ser acordado e avaliado; não deve ser um desconto ou bônus oculto na probabilidade.

Sem esse cuidado, o sistema pode confundir “recebeu mais esforço” com “era naturalmente melhor” e perpetuar a distribuição atual de oportunidades entre vendedores e regiões.

## 14. Dados adicionais necessários

O dataset atual é um retrato com datas de engajamento e encerramento, não um histórico completo do CRM. É possível reconstruir parcialmente a condição aberta/encerrada sob hipóteses, mas não saber quando conta, produto ou responsável foram alterados.

Para aprendizado operacional confiável, registrar:

- Histórico de estágios, responsáveis, região, produto e valor proposto.
- Data de criação e entrada em Prospecting.
- Interações, respostas, reuniões, última atividade e próxima ação.
- Ganho, perda, reabertura e motivos com data de ocorrência.
- Preço, quantidade, moeda e condições comerciais disponíveis em cada previsão.
- Score, versão e recomendações efetivamente exibidas.
- Ações do vendedor após a recomendação, inclusive ausência de ação.

Esses campos não devem ser fabricados ou inferidos como fatos a partir do resultado final. Enquanto estiverem ausentes, as limitações precisam acompanhar a avaliação.

## 15. Explicação ao vendedor e rastreabilidade

Cada previsão deve guardar:

```text
opportunity_id
scored_at
data_cutoff
model_version
score_version
horizon_days
win_probability
estimated_value_if_won
expected_revenue
priority_score
historical_support
reason_codes
next_action
```

As explicações devem vir dos componentes efetivamente utilizados. Exemplo:

> Receita esperada em 30 dias: 2.000. Chance estimada de ganho: 40%. Valor estimado se ganhar: 5.000. A combinação vendedor/produto tem pouco histórico; a estimativa usa principalmente referências mais amplas. Revalidar próxima ação porque não há atividade recente registrada.

O exemplo de atividade só é válido quando o sistema realmente possuir esse histórico. Não usar explicações comerciais plausíveis que o modelo e os dados não sustentem.

Evitar alegações causais como “este vendedor aumenta sua chance em 10 pontos”. Um efeito aprendido pode refletir seleção de carteira ou processo, não habilidade isolada.

## 16. Implementação recomendada

### Primeira entrega

- Preparar dados e contratos de qualidade.
- Manter baseline por valor.
- Construir modelo temporal simples, regularizado e com tratamento de abertos.
- Implementar recuo para entidades novas.
- Comparar interações regionais e individuais em validação temporal.
- Exibir receita esperada, score, limitações e tarefas cadastrais separadamente.
- Registrar versões e permitir reverter uma publicação.

### Evolução com uso real

- Incorporar atividades e histórico completo do CRM.
- Aprimorar valor, calibração e efeitos de recência.
- Automatizar avaliação e promoção de candidatos sob critérios previamente definidos.
- Medir impacto em piloto prospectivo.
- Investigar priorização por margem, esforço e efeito incremental da ação quando houver dados para isso.

**A regra geral recomendada é estimar o resultado econômico futuro com informação disponível no presente, aprender diferenças sustentadas pelos dados e recuar para referências amplas quando a evidência é insuficiente.** Novos nomes não exigem novas regras; novos resultados alimentam versões avaliadas da mesma arquitetura.

## Fontes e escopo

- Documento analisado: `analise-lead-scorer.md`, fornecido pelo usuário, e discussão subsequente nesta conversa.
- Dataset efetivamente consultado: [CRM Sales Predictive Analytics — Kaggle](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics), arquivos `sales_pipeline.csv`, `products.csv`, `sales_teams.csv`, `accounts.csv` e `metadata.csv`.
- Contexto da base fictícia: [CRM Sales Opportunities — Maven Analytics](https://mavenanalytics.io/data-playground/crm-sales-opportunities).
- Referência metodológica: [Analysis of Competing Risks — scikit-survival](https://scikit-survival.readthedocs.io/en/v0.25.0/user_guide/competing-risks.html).
- Os resultados numéricos são os cálculos independentes realizados na etapa anterior desta conversa. As fórmulas e o ciclo de aprendizado deste documento são propostas; seu desempenho ainda precisa ser testado.
