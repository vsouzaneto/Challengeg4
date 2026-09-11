# Submissão — Mikael Allef Alves Gusmão de Oliveira — Challenge 003

## Sobre mim

- **Nome:** Mikael Allef Alves Gusmão de Oliveira
- **LinkedIn:** https://www.linkedin.com/in/mikael-allef-21a61122b/
- **Challenge escolhido:** Challenge 003 — Lead Scorer

---

## Executive Summary

O desafio propunha transformar um pipeline de aproximadamente 8.800 oportunidades em uma priorização comercial funcional, substituindo decisões baseadas apenas em percepção por uma fila de oportunidades explicável.

Desenvolvi o **Radar de Oportunidades**, uma aplicação de Sales Intelligence que calcula um **Priority Score de 0–100**, organiza as oportunidades por prioridade e explica quais fatores estão influenciando cada posição. Durante a análise, identifiquei e corrigi problemas de distribuição no potencial comercial, uma inversão na lógica de Aging e validei hipóteses sobre Prospecting e Historical Fit antes de incorporá-las ao produto.

Além do scoring, evoluí a solução para o **Strategy Lab**, permitindo que gestores simulem diferentes estratégias comerciais e visualizem como elas alterariam o ranking do pipeline antes de aplicar uma mudança.

A principal recomendação é utilizar o Radar como uma **camada de apoio à decisão comercial**, mantendo o score como indicador de prioridade relativa — e não como probabilidade de fechamento.

---

## Solução

### Radar de Oportunidades

O produto transforma o pipeline em uma fila dinâmica de prioridades:

**Pipeline → Score → Ranking → Por quê? → Próxima ação**

Cada oportunidade possui:

- Priority Score;
- nível de prioridade;
- ranking global;
- fatores que compõem o score;
- explicação dos principais sinais;
- ação recomendada;
- Data Confidence.

### Componentes do score

| Fator | Peso |
|---|---:|
| Commercial Potential | 25% |
| Funnel Position | 25% |
| Urgency / Aging | 30% |
| Historical Fit | 20% |

O score é **determinístico e explicável**.

A aplicação não tenta responder:

> “Qual a probabilidade de fechar?”

Ela responde:

> **“Qual oportunidade merece mais atenção neste momento?”**

### Strategy Lab

A evolução principal do produto foi transformar o ajuste de pesos em uma experiência de **simulação estratégica**.

O gestor pode testar cenários como:

- Balanceada;
- Proteger pipeline;
- Maximizar valor;
- Avançar oportunidades.

A simulação recalcula o score e o ranking sem alterar imediatamente o modelo oficial.

O usuário consegue visualizar:

- score atual vs. simulado;
- ranking atual vs. simulado;
- oportunidades que subiram;
- oportunidades que desceram;
- Top 10 atual vs. Top 10 simulado;
- impacto dos diferentes fatores.

Assim, o Strategy Lab responde:

> **“Se minha estratégia comercial mudar, como meu pipeline muda?”**

A alteração só se torna oficial após uma ação explícita de aplicação.

### Onboarding

Foi criado um onboarding específico para novos usuários do Strategy Lab.

O fluxo explica em poucas etapas:

1. o que é o Strategy Lab;
2. como os pesos representam diferentes estratégias;
3. como visualizar o impacto;
4. que a simulação não altera o modelo oficial até ser aplicada.

O objetivo foi evitar uma explicação técnica extensa e levar o usuário rapidamente ao ciclo:

**Alterar → Simular → Entender → Decidir**

---

## Abordagem

Comecei pela **auditoria dos dados**, antes de escolher a técnica de scoring.

Analisei estrutura, relacionamentos, distribuição das oportunidades, produtos, vendedores, estágios, datas, valores ausentes e comportamento histórico.

A partir disso, construí uma primeira hipótese de scoring e comecei a confrontá-la com os dados.

O processo foi iterativo:

```text
Problema
   ↓
Hipótese
   ↓
Análise
   ↓
Implementação
   ↓
Teste
   ↓
Descoberta
   ↓
Correção
   ↓
Validação
```

Uma decisão importante foi não transformar toda variável disponível em um fator do score.

Por exemplo, vendedor e porte da conta foram investigados, mas não demonstraram evidência suficiente para justificar um peso direto relevante. Eles permaneceram como contexto e filtros.

Também evitei adicionar Machine Learning ou LLM apenas para aumentar a complexidade técnica.

---

## Resultados / Findings

### 1. O pipeline precisava de uma priorização explicável

O problema não era falta de dados. Era transformar os dados disponíveis em uma decisão operacional.

Por isso, a solução foi construída em torno de uma fila de prioridade, e não de um dashboard puramente analítico.

### 2. O primeiro scoring tinha concentração artificial no GTK 500

Um percentil simples entre as sete SKUs favorecia um produto com apenas 40 oportunidades históricas.

A solução foi utilizar um **percentil ponderado pelo volume real de negócios**, reduzindo a vantagem artificial do produto.

### 3. A lógica inicial de Aging tinha uma inversão

A implementação anterior fazia a urgência cair após aproximadamente 138 dias.

Isso contrariava a interpretação comercial de uma oportunidade que permanece parada por mais tempo.

A curva foi corrigida para ser monotônica e continuar aumentando, com crescimento mais lento após o período histórico.

### 4. Prospecting não estava sendo prejudicado pelo Aging

Uma hipótese inicial sugeria que Prospecting poderia estar recebendo uma penalização artificial.

O teste mostrou que a diferença vinha principalmente do **Funnel Position**, e não do Aging.

A decisão foi não manipular artificialmente o score.

### 5. Historical Fit não apresentou forte poder preditivo

O componente apresentou AUC de aproximadamente **0,48**, próximo ao acaso isoladamente.

Por isso, ele permaneceu como sinal heurístico/contextual e não foi apresentado como um forte preditor.

### 6. Explainability tornou-se parte central do produto

O usuário consegue decompor o score e entender exatamente como cada componente contribuiu.

Isso evita uma “caixa-preta” e torna o ranking auditável.

### 7. O Strategy Lab transformou configuração em decisão estratégica

Em vez de simplesmente permitir:

> “alterar pesos”

a solução permite:

> **“simular uma estratégia e observar suas consequências no pipeline.”**

Esse foi o principal salto de produto em relação ao scoring inicial.

---

## Recomendações

### Prioridade 1 — Usar o Radar como camada de priorização

O Radar deve funcionar como apoio à rotina comercial, ajudando vendedores e gestores a identificar onde concentrar atenção.

### Prioridade 2 — Usar o Strategy Lab para testar estratégias

Alterações de estratégia devem ser simuladas antes de serem aplicadas, permitindo visualizar o impacto no ranking.

### Prioridade 3 — Não interpretar o score como probabilidade

O Priority Score deve permanecer como **prioridade relativa**, e não como previsão de fechamento.

### Prioridade 4 — Melhorar a qualidade dos dados

O volume de informações ausentes, especialmente em oportunidades abertas, limita a qualidade de alguns sinais.

Uma evolução natural seria melhorar a completude do CRM.

### Prioridade 5 — Só evoluir para ML quando houver dados suficientes

Antes de introduzir modelos preditivos mais complexos, seria necessário obter histórico longitudinal mais rico, incluindo transições de estágio, ações realizadas e resultados posteriores.

---

## Limitações

- O dataset não possui histórico completo de transição entre estágios.
- O score não representa probabilidade de fechamento.
- Historical Fit apresentou AUC aproximadamente 0,48 isoladamente.
- As faixas de prioridade são relativas ao pipeline atual.
- Algumas oportunidades possuem dados incompletos.
- O valor de oportunidades abertas é estimado a partir do catálogo quando o valor real de fechamento não está disponível.
- O dataset representa um snapshot histórico, não uma operação CRM em tempo real.
- O Strategy Lab permite testar sensibilidade a diferentes pesos, mas não determina qual estratégia é comercialmente correta.
- Os presets são cenários de simulação, não recomendações matematicamente ótimas.

---

## Process Log — Como usei IA

> **Este bloco é obrigatório.**

### Ferramentas usadas

| Ferramenta | Para que usei |
|---|---|
| **ChatGPT** | Decomposição do problema, hipóteses de scoring, análise crítica, validação conceitual, revisão de UX e documentação |
| **Claude Code** | Exploração dos dados, implementação, testes, investigação de problemas, QA e evolução do protótipo |

### Workflow

#### 1. Entendimento do problema

Primeiro decompus o desafio como problema de negócio:

> **“Como transformar 8.800 oportunidades em uma fila de atenção que um vendedor consiga utilizar?”**

Antes de escolher tecnologia, defini o resultado esperado.

#### 2. Auditoria dos dados

Utilizei Claude Code para explorar os CSVs, relacionamentos, distribuições, valores ausentes e comportamento histórico.

Isso permitiu identificar limitações do dataset antes de definir o scoring.

#### 3. Primeira hipótese de scoring

Criei uma primeira estrutura com cinco fatores.

A hipótese foi posteriormente confrontada com os dados.

#### 4. Iteração baseada em evidências

Durante os testes, encontrei problemas que exigiram revisão:

- concentração artificial no GTK 500;
- inversão no Aging;
- hipótese de penalização do Prospecting;
- baixo poder discriminativo do Historical Fit.

Esses pontos foram investigados antes de decidir se deveriam gerar alterações.

#### 5. Construção do produto

Claude Code foi utilizado para implementar:

- processamento dos dados;
- feature engineering;
- scoring;
- ranking;
- explainability;
- filtros;
- recomendações;
- Data Confidence;
- interface web;
- QA.

#### 6. Evolução para Strategy Lab

Depois que o scoring estava estabilizado, transformei o ajuste de pesos em uma camada de simulação estratégica.

A implementação reutiliza os mesmos fatores do modelo oficial.

Não foi criado um segundo modelo.

#### 7. Validação

Foram criadas **29 checagens automatizadas** para validar:

- limites;
- unicidade;
- joins;
- fórmula;
- pesos;
- explainability;
- consistência do score.

Depois foram definidos testes adicionais específicos para o Strategy Lab.

#### 8. Revisão final

Por fim, revisei:

- linguagem;
- nomenclatura;
- UX;
- limitações;
- documentação;
- onboarding;
- consistência entre score, ranking e explicações.

---

## Onde a IA errou e como corrigi

Esse foi um dos pontos mais importantes do processo.

### Erro 1 — Concentração artificial no GTK 500

A abordagem inicial utilizava um percentil simples entre produtos.

Isso dava uma vantagem desproporcional a uma SKU com baixo volume histórico.

**Correção:** percentil ponderado pelo volume.

### Erro 2 — Aging decaía depois de determinado período

A lógica inicial fazia oportunidades muito antigas perderem urgência.

**Correção:** curva monotônica, sem decaimento da urgência por envelhecimento.

### Erro 3 — Hipótese incorreta sobre Prospecting

Foi levantada a possibilidade de que Prospecting estivesse sendo penalizado pelo Aging.

A análise mostrou que a diferença vinha principalmente de Funnel Position.

**Correção:** não alterar artificialmente o score.

### Erro 4 — Interpretação excessiva do Historical Fit

A análise mostrou AUC aproximadamente 0,48.

**Correção:** manter o componente como sinal heurístico/contextual e retirar qualquer linguagem que sugerisse forte capacidade preditiva.

---

## O que eu adicionei que a IA sozinha não faria

O principal diferencial não foi adicionar mais tecnologia.

Foi decidir **o que não adicionar** e transformar os resultados técnicos em uma experiência de decisão.

Algumas decisões importantes foram:

- não usar vendedor como fator direto do score;
- não usar porte da conta sem evidência suficiente;
- não adicionar XGBoost apenas para ter ML;
- não usar LLM para gerar explicações que poderiam ser determinísticas;
- não criar chatbot;
- não criar integrações externas desnecessárias;
- não transformar o score em probabilidade de fechamento;
- não criar otimização automática de pesos sem uma função objetivo válida.

A principal evolução de produto foi o **Strategy Lab**.

Em vez de entregar apenas um configurador técnico de pesos, criei uma experiência que permite ao gestor responder:

> **“Se eu mudar minha estratégia, quem sobe, quem cai e como meu pipeline muda?”**

Isso conecta a metodologia diretamente à decisão de negócio.

---

## Evidências

As evidências da construção são apresentadas por meio do Process Log, dos exports das conversas utilizadas no desenvolvimento e do histórico de desenvolvimento via Git.

### Chat Export — ChatGPT

[Export da conversa no ChatGPT](https://chatgpt.com/share/6aa34348-d63c-83e9-85d8-f729fe589084)

### Chat Export — Claude

[Export da conversa no Claude](https://claude.ai/export/83e330f5-06a8-4904-a221-c3dca4198709/download/8645538b0c61da79130f23f970fe9a53)

### Documentação da solução

- [README da solução](solution/README.md)
- [Process Log detalhado](process-log/PROCESS_LOG.md)
- [Protótipo funcional](solution/radar_de_oportunidades.html)

### Evidências adicionais

- Histórico de desenvolvimento / Git history.
- O protótipo funcional incluído na submissão permite avaliar a evolução do produto e suas funcionalidades.

---

## Nota de evidência

As sugestões produzidas pelas IAs não foram consideradas decisões finais. Hipóteses e alterações só foram incorporadas após análise dos dados, testes ou validação do comportamento do produto.
