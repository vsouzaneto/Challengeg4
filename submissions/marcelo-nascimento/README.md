# Submissão — Marcelo Soares do Nascimento — Lead Scoring

## Sobre mim

**Nome:** Marcelo Soares do Nascimento  
**LinkedIn:** https://www.linkedin.com/in/cello-nascimento/  
**Challenge escolhido:** Lead Scoring

---

# Executive Summary

Desenvolvi uma aplicação de **Lead Scoring para priorização comercial**, capaz de analisar dados históricos de oportunidades e atribuir automaticamente um score de **0 a 100** para cada lead.

O objetivo não foi apenas produzir uma pontuação, mas criar um mecanismo **determinístico, explicável e auditável**, no qual seja possível entender exatamente quais evidências contribuíram para a classificação de cada oportunidade.

A solução utiliza exclusivamente oportunidades históricas finalizadas como **Won** ou **Lost** como fonte de evidência e divide o cálculo em quatro dimensões:

- Produto × Cliente — até 35 pontos
- Produto × Setor — até 30 pontos
- Perfil Empresarial — até 20 pontos
- Financeiro — até 15 pontos

Além do score, a aplicação apresenta os fatores que influenciaram o resultado, permitindo ao time comercial compreender por que determinada oportunidade recebeu maior ou menor prioridade.

A aplicação foi desenvolvida com **React + Vite no frontend, Node.js no backend e PostgreSQL**, utilizando Docker para execução dos serviços.

O desenvolvimento seguiu uma abordagem de **Spec-Driven Development (SDD)**: primeiro defini problema, regras, comportamento esperado, critérios de aceitação e interface; somente depois as especificações foram entregues ao agente de IA responsável pela implementação.

---

# Solução

A solução é uma aplicação web que transforma o histórico comercial da empresa em um **pipeline priorizado de leads**.

Em vez de o vendedor analisar manualmente diversas características para decidir quais oportunidades atacar primeiro, o sistema calcula um score entre 0 e 100 e ordena os leads de acordo com sua aderência aos padrões observados no histórico de vendas.

O produto possui:

- autenticação;
- dashboard com visão geral do pipeline;
- listagem priorizada de leads;
- score individual entre 0 e 100;
- classificação visual dos leads;
- explicação dos fatores que compõem cada score;
- relatórios visuais;
- listagem e acompanhamento dos scores;
- gerenciamento de usuários.

A interface utiliza uma identidade visual dark, com destaque em **Holographic Teal (`#06D6A0`)** para leads com maior intenção de conversão e **Iridescent Violet (`#8B5CF6`)** para navegação, filtros e elementos secundários.

A intenção foi fazer o score funcionar como uma ferramenta operacional: o usuário abre o sistema e consegue rapidamente identificar **onde concentrar seu esforço comercial e por quê**.

---

# Abordagem

## 1. Começar pela regra de negócio

Minha primeira decisão foi não começar pelo dashboard.

O principal problema do challenge não era criar uma interface de CRM, mas responder:

**Como transformar o histórico de vendas em uma priorização defensável de novos leads?**

Por isso, a primeira especificação foi dedicada à engine de scoring.

A interface e os relatórios foram especificados somente depois que o comportamento dessa engine estava definido.

---

## 2. Separação do score em dimensões

Em vez de produzir um score monolítico, dividi o problema em quatro dimensões independentes:

| Dimensão | Peso máximo |
|---|---:|
| Produto × Cliente | 35 |
| Produto × Setor | 30 |
| Perfil Empresarial | 20 |
| Financeiro | 15 |
| **Total** | **100** |

Essa divisão permite identificar não apenas se um lead parece interessante, mas **por quais razões**.

Uma oportunidade pode, por exemplo, possuir forte aderência entre produto e setor, mas pouca evidência histórica específica daquele cliente.

Essas informações permanecem separadas durante o cálculo e são consolidadas apenas no score final.

---

## 3. Histórico válido

Nem toda oportunidade existente no banco deve servir como evidência.

O cálculo considera somente oportunidades concluídas:

- **Won**
- **Lost**

Oportunidades ainda abertas não são utilizadas para inferir sucesso ou fracasso, porque seu resultado ainda é desconhecido.

Essa decisão evita contaminar o histórico com exemplos cujo desfecho ainda não ocorreu.

---

## 4. Score sem pontos arbitrários

Uma regra importante da solução é:

**ausência de evidência não é evidência positiva.**

O lead não começa, por exemplo, com 50 pontos simplesmente por existir.

Cada parcela do score precisa ser consequência de informação encontrada no histórico ou de uma regra explicitamente definida.

Quando uma determinada dimensão não possui evidência suficiente, sua contribuição pode ser zero.

Isso também significa que o sistema não tenta artificialmente fazer todos os leads parecerem oportunidades razoáveis.

---

## 5. Normalização dos dados

Durante a análise, identifiquei que pequenas diferenças textuais poderiam fragmentar artificialmente o histórico.

Valores semanticamente equivalentes precisam ser tratados como a mesma informação.

Por exemplo:

`GTXPro`

e

`GTX Pro`

não deveriam criar dois produtos diferentes apenas por uma diferença de representação textual.

A engine portanto normaliza os valores relevantes antes de utilizá-los nas agregações.

---

## 6. Proteção contra amostras pequenas

Outro problema é o risco de supervalorizar coincidências em amostras muito pequenas.

Um produto com uma única venda histórica bem-sucedida não deveria automaticamente receber o mesmo nível de confiança de outro com dezenas de oportunidades consistentes.

Para reduzir esse efeito, a lógica utiliza **smoothing**, evitando que poucos registros produzam conclusões excessivamente fortes.

O objetivo não é apenas medir taxa histórica, mas considerar também a quantidade de evidência disponível.

---

## 7. Explicabilidade

O resultado da engine não é apenas:

`score = 82`

Ela retorna também os componentes utilizados para chegar ao resultado.

O sistema consegue apresentar:

- score total;
- contribuição de cada dimensão;
- fatores encontrados;
- evidências históricas utilizadas;
- justificativa do resultado.

Essa característica foi tratada como requisito funcional, não como detalhe visual.

O vendedor deve conseguir responder:

**“Por que esse lead está acima daquele?”**

sem depender de uma interpretação opaca de um modelo.

---

## 8. Decisão sobre uso de IA

Uma decisão deliberada foi **não utilizar uma LLM para calcular o score**.

Uma LLM poderia receber os dados de um lead e responder que ele possui, por exemplo, “87% de chance”, mas esse número seria difícil de reproduzir, testar e auditar.

Para uma regra central de negócio, preferi uma engine determinística.

A IA foi utilizada no **processo de desenvolvimento**, não como autoridade sobre a decisão comercial.

---

# Arquitetura

A aplicação utiliza:

**Frontend**
- React
- Vite
- JavaScript/TypeScript
- Bootstrap via CDN oficial
- Font Awesome via CDN oficial
- Roboto via Google Fonts

**Backend**
- Node.js

**Banco de dados**
- PostgreSQL

**Infraestrutura**
- Docker
- containers único para frontend, backend e banco de dados.

O frontend não contém a regra central de scoring.

A responsabilidade pela lógica de negócio permanece no backend, permitindo que diferentes interfaces consumam a mesma engine futuramente.

---

# Interface

A interface foi projetada para que a informação principal seja percebida rapidamente.

A paleta definida foi:

| UI Layer | Cor | Hex | Aplicação |
|---|---|---|---|
| Canvas Base | Void Black | `#09090F` | Background principal |
| Surface Layer | Charcoal Deep Blue | `#12121E` | Cards, tabelas e métricas |
| Primary Text | Cool Silver-White | `#E2E8F0` | Dados principais |
| Accent / Focus | Holographic Teal | `#06D6A0` | Hot Leads e aumento de score |
| Secondary Accent | Iridescent Violet | `#8B5CF6` | Navegação, filtros e badges |
| Muted Action | Deep Slate | [HEX] | Elementos secundários |

O dashboard prioriza métricas comerciais e a visualização dos leads de maior score.

A listagem permite comparar rapidamente oportunidades e identificar quais devem receber atenção primeiro.

O score possui destaque visual, mas permanece acompanhado de sua justificativa para evitar transformar o número em uma “caixa-preta”.

---

# Resultados / Findings

O principal resultado do trabalho foi transformar uma definição subjetiva — **“qual lead parece melhor?”** — em um conjunto explícito de regras.

Durante o desenvolvimento, alguns pontos se mostraram especialmente importantes.

### Score alto não significa necessariamente probabilidade

O score de 0 a 100 é uma **medida de priorização**, não uma afirmação de que um lead com score 80 possui exatamente 80% de probabilidade de fechar.

Essa distinção evita apresentar uma precisão estatística que os dados não sustentam.

### Quantidade de evidência importa

Uma taxa histórica aparentemente excelente pode ser pouco significativa quando baseada em apenas uma ou duas oportunidades.

Por isso, quantidade e qualidade do histórico precisam participar da interpretação dos dados.

### Dados ausentes não devem gerar pontos

Dar um score-base aos leads faria o sistema introduzir confiança que não veio dos dados.

A ausência de histórico foi tratada explicitamente como ausência de evidência.

### Explicabilidade aumenta a utilidade

Um ranking sozinho poderia indicar ao vendedor qual lead abordar primeiro.

A decomposição do score acrescenta outra informação importante: **por que abordá-lo primeiro**.

Isso também facilita identificar problemas nas regras e evoluir a engine posteriormente.

### Determinismo facilita validação

Como os mesmos dados produzem o mesmo score, é possível escrever testes automatizados para a regra de negócio.

Mudanças futuras na engine também podem ser avaliadas contra casos conhecidos, reduzindo o risco de regressões silenciosas.

---

# Recomendações

O próximo passo mais importante seria validar o score utilizando um volume maior de dados históricos.

Com dados suficientes, seria possível medir a taxa real de conversão por faixa de score, por exemplo:

- 0–20
- 21–40
- 41–60
- 61–80
- 81–100

Isso permitiria descobrir empiricamente se leads classificados nas faixas superiores realmente convertem com maior frequência.

Também seria possível recalibrar os pesos atualmente utilizados.

Os pesos 35/30/20/15 representam a modelagem inicial do problema. Com histórico suficiente, esses valores poderiam ser ajustados utilizando análise estatística ou Machine Learning supervisionado.

Outra evolução possível seria adicionar novas dimensões conforme novos dados comerciais se tornassem disponíveis, como:

- tempo desde o último contato;
- origem do lead;
- duração média do ciclo de venda;
- interações anteriores;
- comportamento ao longo do funil;
- recorrência do cliente.

Mesmo nesse cenário, manteria explicabilidade e auditabilidade como requisitos do produto.

---

# Limitações

A principal limitação da solução é a mesma de qualquer sistema baseado em histórico: **o resultado depende da qualidade dos dados disponíveis**.

Pouco histórico significa pouca evidência.

Dados inconsistentes podem produzir associações incorretas, razão pela qual normalização e validação são importantes.

Os pesos iniciais também não foram aprendidos estatisticamente a partir de uma grande base de dados. Eles representam uma modelagem inicial do problema e deveriam ser recalibrados caso o sistema fosse colocado em produção com maior volume histórico.

O score também não deve ser interpretado como probabilidade matemática de fechamento.

Finalmente, padrões históricos podem mudar. Produtos, clientes, setores e comportamento comercial evoluem, portanto uma implementação de produção deveria acompanhar periodicamente a qualidade do ranking.

---

# Process Log — Como usei IA

## Ferramentas usadas

Utilizei IA durante praticamente todo o processo de desenvolvimento, mas com responsabilidades diferentes.

**ChatGPT**

Usei principalmente como parceiro de análise e especificação.
As conversas foram utilizadas para:

- analisar o problema;
- questionar regras de scoring;
- identificar ambiguidades;
- discutir alternativas;
- estruturar as especificações;
- definir critérios de aceitação;
- discutir arquitetura;
- estruturar a interface;
- revisar decisões antes da implementação.

**OpenCode / Space Bunny**

Depois das regras serem especificadas, utilizei um agente de desenvolvimento para implementar o sistema.
Em vez de entregar apenas um prompt descrevendo genericamente o produto, o agente recebeu especificações e ADR delimitando o comportamento esperado.

---

# Workflow

O projeto seguiu um processo de **Spec-Driven Development**.

Meu fluxo foi:

**Problema → discussão → decisão → especificação → implementação → validação**

Em vez de:

**prompt → código → correções sucessivas**

Antes de permitir que o agente começasse a implementar, discuti com a IA as decisões relevantes do domínio.

A primeira especificação foi dedicada à engine de scoring.

Nela foram definidos:

- quais dados poderiam ser utilizados;
- quais oportunidades pertenciam ao histórico;
- dimensões do score;
- pesos;
- normalização;
- comportamento sem evidência;
- tratamento de amostras pequenas;
- explicabilidade;
- comportamento esperado da engine.

Somente depois dessa definição avancei para a especificação da interface.

Na segunda etapa foram definidos:

- estrutura visual;
- dashboard;
- listagens;
- relatórios;
- navegação;
- identidade visual;
- estados da interface;
- apresentação do score e das justificativas.

Depois das especificações, defini um roadmap curto para implementação, priorizando primeiro a regra central e depois as camadas de apresentação.

O agente de implementação passou então a executar uma especificação já delimitada, em vez de decidir simultaneamente produto, arquitetura, regra de negócio e código.

---

# Onde a IA errou e como corrigi

Nas primeiras análises descartadas, a IA insistia em score mínimo fixo, e desconsiderava uma relação entre venda de produto - cliente, que em minha visão era essencial. Excluí histórico e ajustei o prompt inicial em conversas diferentes, para a análise chegar onde eu queria diretamente.

---

# O que eu adicionei que a IA sozinha não faria

O problema real é decidir:

- o que representa um bom lead;
- quais dados podem sustentar essa conclusão;
- quanto cada evidência deve contribuir;
- o que fazer quando ela não existe;
- como evitar conclusões fortes com poucas amostras;
- como representar incerteza;
- como explicar o resultado para uma pessoa;
- onde a IA deve ou não participar da decisão.

Minha decisão foi **não colocar IA generativa na engine**.

Seria fácil tornar a solução aparentemente mais “AI” enviando cada lead para uma LLM ou Laya e pedir um score de 0 a 100, mas isso produziria uma solução menos previsível e mais difícil de auditar.

Usei IA onde considero que ela possui maior valor neste projeto: **como acelerador do processo de engenharia**.

Mantive regras críticas de negócio em código determinístico.

Também impus uma separação entre especificação e implementação.

O agente responsável por escrever código não deveria descobrir sozinho o produto enquanto o implementava.

As principais decisões foram tomadas antes e registradas como especificações, fazendo com que a implementação fosse consequência das decisões, e não o lugar onde essas decisões surgiam acidentalmente.

---

# Evidências

As evidências do processo incluem:

- histórico das conversas utilizadas para análise;
- especificações produzidas antes da implementação;
- código-fonte;
- testes automatizados;
- aplicação funcionando;
- screenshots de conversa;

**Screenshots:** /process-log/screenshots

**Historico de Conversa:**  /process-log/chat-exports/chatgpt.url

**Specs:** /docs

---

Após baixar o projeto, abra a pasta solution e execute:
cd solution
docker compose up --build -d
Acesse http://localhost:5173 e entre com admin@leadscore.local / lead@teste55. 
Não é necessário instalar Node.js, criar banco ou executar migrations manualmente.
Para verificar ou encerrar:
docker compose ps
docker compose down

---

**Submissão enviada em:** 24/09/2026
