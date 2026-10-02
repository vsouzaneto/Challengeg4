# Submissão — Manoel Figueiredo — Challenge 003

## Sobre mim

- **Nome:** Manoel Figueiredo
- **LinkedIn:** https://www.linkedin.com/in/manoelfigueiredo/
- **Challenge escolhido:** 003 — Lead Scorer
- **Ambiente funcional:** https://g4.mftechsolutions.pt

---

## Executive Summary

Construí uma solução operacional de priorização comercial utilizando **Odoo Community** como CRM e **n8n** como camada de integração, scoring e automação.

Em vez de tratar o desafio apenas como “qual oportunidade tem maior probabilidade de ganhar?”, reformulei o problema para uma pergunta operacional:

> **Em que oportunidade deve o vendedor investir o próximo minuto?**

Dessa pergunta nasceu o **G4 FocusScore**, um sistema de priorização explicável integrado diretamente no CRM. O vendedor não recebe apenas um número: recebe prioridade visual, contexto, tags, sinais de risco e próxima ação recomendada.

A solução processa o dataset completo de aproximadamente **8.800 oportunidades** e transforma os dados históricos num CRM utilizável. Numa segunda etapa, foi criado o módulo **WIN INTELLIGENCE**, para analisar resultados Won/Lost e testar estatisticamente se as premissas do scoring são suportadas pelos dados.

---

## Solução

### Abordagem

Antes de escolher tecnologia, analisei primeiro o problema e a experiência do utilizador final.

A decisão foi construir uma solução próxima de uma operação comercial real, usando:

- **Odoo Community** — CRM operacional
- **n8n** — integração, enrichment, scoring e automação
- **ChatGPT** — pair programmer, crítico técnico e apoio à análise
- **g4.mftechsolutions.pt** — ambiente dedicado

A arquitetura evoluiu para quatro workflows principais:

1. **G4 — PRODUCTS**
2. **G4 — IMPORT / SYNC**
3. **G4 — ENRICH / PRIORITIZE**
4. **G4 — WIN INTELLIGENCE**

Mais detalhes em [solution/architecture.md](./solution/architecture.md).

### Lógica de priorização

O FocusScore foi construído inicialmente como um motor determinístico e explicável. A decisão foi evitar começar com um modelo de ML complexo antes de existir uma ferramenta que o vendedor pudesse realmente utilizar.

Também evitámos utilizar variáveis como `close_date` ou `close_value` para priorizar oportunidades abertas, porque essas informações só existem após o resultado e introduziriam data leakage.

A solução transforma o score em comportamento operacional através de:

- estrelas de prioridade
- tags como **🔥 Prioridade Alta**
- **💰 Alto Valor**
- **⚠️ Em Risco**
- atividades recomendadas
- deadlines
- equipas/regiões

Mais detalhes em [solution/scoring-logic.md](./solution/scoring-logic.md).

### Resultados / Findings

O dataset completo processado contém:

- **8.800 oportunidades**
- **6.711 negócios fechados**
- **4.238 Won**
- **2.473 Lost**
- **2.089 Open**
- **Win rate histórico: 63,2%**

A primeira execução do WIN INTELLIGENCE mostrou `Lost = 0` e `Win Rate = 100%`. Em vez de aceitar o resultado, investigámos a causa e descobrimos que os Lost estavam arquivados no Odoo (`active=false`) e não eram lidos pelo node inicial. Depois da correção, a distribuição real apareceu corretamente.

Exemplos de diferenças encontradas:

- **telecommunications × MG Special**: 85 fechados, win rate ~72,9%
- **medical × MG Advanced**: 164 fechados, win rate ~57,3%

Esses sinais não são automaticamente convertidos em pesos do FocusScore.

O WIN INTELLIGENCE foi reforçado com:

- intervalo de confiança Wilson 95%
- comparação segmento vs restante população
- diferença absoluta em pontos percentuais
- lift
- p-value
- correção Benjamini-Hochberg
- shrinkage para amostras pequenas
- evidência `strong`, `moderate` ou `weak`

Mais detalhes em [solution/win-intelligence.md](./solution/win-intelligence.md).

### Recomendações

O próximo passo é validar se os sinais históricos são estáveis e generalizam:

1. validação temporal / out-of-sample
2. análise multivariável
3. controlo de confundidores
4. comparação entre scorer atual e scorer recalibrado
5. monitorização em produção

### Limitações

A análise atual encontra associações, não causalidade. Vendedor, manager, produto, setor, região e dimensão da empresa podem estar confundidos entre si.

A estrutura de utilizadores do ambiente de demonstração também foi simplificada. Em vez de criar artificialmente os 35 utilizadores do dataset, foi criada uma estrutura representativa com RevOps, managers e vendedores regionais, preservando o vendedor histórico nos dados.

---

## Process Log — Como usei IA

O processo foi iterativo e não um fluxo “um prompt → uma resposta”.

A IA foi usada como **pair programmer, arquiteto e crítico técnico**, enquanto as decisões de produto, experiência do vendedor e aceitação/rejeição das sugestões permaneceram humanas.

### Ferramentas usadas

| Ferramenta | Para que usei |
|---|---|
| ChatGPT | arquitetura, crítica, geração/revisão de lógica, debugging e análise estatística |
| n8n | integração, automação e scoring |
| Odoo Community | interface operacional do vendedor |
| GitHub | documentação e submissão |

### Workflow de construção

1. Leitura do problema e reformulação da pergunta de negócio.
2. Decisão de construir uma solução operacional em CRM real.
3. Escolha de Odoo Community + n8n.
4. Importação e sincronização dos dados.
5. Criação do FocusScore e explainability.
6. Transformação do score em prioridade visual e próxima ação.
7. Testes progressivos e correção de problemas de escala.
8. Criação do WIN INTELLIGENCE.
9. Correção de leitura dos Lost arquivados.
10. Reforço estatístico para evitar conclusões frágeis.

### Onde a IA errou e como corrigi

- autenticação inicial inadequada para o ambiente
- credencial Odoo errada durante testes
- duplicação nos primeiros imports
- parsing incorreto de HTML
- Code node a devolver apenas 1 item
- análise inicial com `Lost = 0`
- uso inicial de cutoff fixo como proxy de confiança estatística

### O que eu adicionei que a IA sozinha não faria

A principal contribuição humana foi decidir que o problema não deveria ser resolvido como um notebook de previsão.

A solução foi orientada para a experiência real do vendedor e para comportamento operacional no CRM.

Um exemplo foi separar claramente:

- **stage** = onde o negócio está no processo
- **priority** = onde o vendedor deve concentrar atenção

O principal ciclo de construção foi:

> **ideia → crítica → implementação → teste → erro → correção**

Process log completo em [process-log/PROCESS.md](./process-log/PROCESS.md).

---

## Evidências

As evidências visuais da solução estão versionadas em [solution/screenshots](./solution/screenshots/).

### CRM operacional

![Pipeline comercial no Odoo](./solution/screenshots/Screenshot%202026-09-24%20114551.png)

### Workflows e automação

![Workflow n8n — evidência 1](./solution/screenshots/Screenshot%202026-09-24%20114804.png)

![Workflow n8n — evidência 2](./solution/screenshots/Screenshot%202026-09-24%20114913.png)

![Workflow n8n — evidência 3](./solution/screenshots/Screenshot%202026-09-24%20120559.png)

![Workflow n8n — evidência 4](./solution/screenshots/Screenshot%202026-09-24%20120828.png)

![Workflow n8n — evidência 5](./solution/screenshots/Screenshot%202026-09-24%20121001.png)

### Dados / resultado no CRM

![Evidência adicional do ambiente funcional](./solution/screenshots/Screenshot%202026-09-24%20121101.png)

> O repositório contém as imagens originais como evidência do ambiente funcional. O vídeo demonstrativo é opcional e pode ser acrescentado como link antes da revisão final.

---

_Submissão enviada em: 23/09/2026_
