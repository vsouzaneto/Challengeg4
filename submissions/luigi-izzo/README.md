# Submissão — Challenge 003 — Lead Scorer

## Sobre mim

- **Nome:** Luigi Formica Izzo
- **LinkedIn:** https://www.linkedin.com/in/luigi-formica-izzo-a406ab209
- **Challenge escolhido:** Challenge 003 — Lead Scorer (Vendas / RevOps)

---

## Executive Summary

_Em 3-5 frases: o que você fez, o que encontrou, e qual a principal recomendação._

Desenvolvi uma solução fim a fim de Lead Scoring integrada ao Databricks e ao Slack para priorização automatizada das ~8.800 oportunidades do pipeline de vendas. Ao analisar os dados históricos de conversão, identifiquei que a taxa de vitória é estável (~60-65%), tornando o tempo de pipeline (*ageing*) e o risco de estagnação os fatores mais determinantes para o sucesso do fechamento. Construí uma regra de scoring transparente (0 a 100) baseada em 4 pilares ponderados e automatizei o envio de alertas diários diretamente no canal dos vendedores com justificativas claras (*Explainability*) e ações recomendadas. Recomendo a adoção imediata da notificação via Slack na rotina semanal dos vendedores para focar o tempo em oportunidades quentes e evitar o esfriamento de deals estratégicos.

---

## Solução

A solução foi estruturada em pipelines automatizadas no Databricks, alimentando notificações acionáveis no Slack.

### Abordagem

_Como você atacou o problema. Por onde começou? Como decompôs? O que priorizou?_

1. **Análise Exploratória e Entendimento dos Dados:** Carga e denormalização das 4 bases (`accounts`, `products`, `sales_teams`, `sales_pipeline`) no Delta Lake (`workspace.default`). Análise do comportamento histórico de conversão (*Win Rate*) por setor, produto, ticket e tempo de ciclo de vida.
2. **Definição da Regra do Lead Score:** Criação de um modelo transparente de 0 a 100 pontos dividido em 4 pilares:
   - **Estágio Atual (até 25 pts):** Pondera o progresso do deal (`Engaging` vs `Prospecting`).
   - **Timing & Estagnação (até 30 pts / penalidade -15 pts):** Pondera a idade do deal em relação à mediana histórica de vitória (57 dias) e ao limite de estagnação (88 dias - P75).
   - **Fit da Conta (até 25 pts):** Analisa a taxa de conversão histórica do setor e o porte/receita do cliente.
   - **Ticket do Produto (até 20 pts):** Prioriza produtos com maior valor financeiro de tabela.
3. **Pipeline de ETL e Consolidação:** Desenvolvimento de um notebook PySpark que saneia os dados, executa as regras de scoring e gera a tabela consolidada `workspace.default.lead_scoring_pipeline`.
4. **Notificação Ativa no Slack (Block Kit):** Desenvolvimento de um dispatcher em Python que formata e envia mensagens ricas com os prós, contras e ações sugeridas (*Explainability*), entregando o direcionamento direto onde o vendedor trabalha.

### Resultados / Findings

_O que você encontrou/construiu. Mostre dados, screenshots, links._

- **Tabela Consolidada Delta:** `workspace.default.lead_scoring_pipeline` contendo os scores recalculados, classificação por Tiers (`High`, `Medium`, `Low Priority`) e tags de explicabilidade.
- **Estrutura dos Notebooks:**
  - `01_eda_and_lead_scoring_pipeline.py`: Leitura, denormalização, regras de negócio e persistência em Delta.
  - `02_slack_lead_dispatcher.py`: Separação em células independentes para geração dos payloads em memória (Block Kit) e envio HTTP para o Slack Webhook.
- **Mensagem do Slack com Explainability:** Cada alerta inclui:
  - **Score Final e Tier:** Ex.: `🔥 High Priority (85/100)`.
  - **Prós (Ponto Forte):** Ex.: `+15 pts: Setor de Marketing possui alta conversão histórica`.
  - **Contras (Alerta/Risco):** Ex.: `Deal parado no pipeline há 92 dias (estagnado)`.
  - **Ação Sugerida:** Ex.: `Entrar em contato nas próximas 24 horas`.

### Recomendações

_O que a empresa deveria fazer com base nos seus findings. Priorize._

1. **Implementar a Notificação Diária/Semanal no Slack:** Substituir a priorização "no feeling" pelos alertas automatizados toda segunda-feira de manhã.
2. **Revisar Deals Estagnados (>90 dias):** Treinar o time comercial para aplicar rotinas de limpeza e descarte em deals que ultrapassaram o P75 de ganho sem movimentação.
3. **Focar Força de Vendas em High Ticket & Top Sectors:** Garantir que contas dos setores de Marketing, Software e Entertainment recebam atendimento prioritário dentro do SLA de 24h.

### Limitações

_O que você não conseguiu resolver, verificar, ou que precisaria de mais tempo/dados._

- **Falta de Dados Recentes em Tempo Real:** O cálculo do *ageing* depende do intervalo entre a `engage_date` e a maior data registrada no dataset; uma integração via API em tempo real com o CRM seria ideal.
- **Histórico de Interações Semânticas:** O dataset não contém registros não-estruturados (ex.: e-mails trocados, notas de reuniões) para alimentar análise de sentimento no score.

---

## Process Log — Como usei IA

> **Este bloco é obrigatório.** Sem ele, a submissão é desclassificada.

### Ferramentas usadas

_Liste as ferramentas de IA que usou e para quê._

| Ferramenta | Para que usou |
|------------|--------------|
| _Gemini_ | _Análise exploratória dos dados, definição das regras de scoring, prototipação das queries PySpark/SQL no Databricks e estruturação das mensagens do Slack em Block Kit_ |
| _Databricks_ | _Criação de notebooks e datasets para geração de dataset consolidado e envio de informações para vendedores_ |

### Workflow

_Descreva passo a passo como você trabalhou. Onde a IA entrou em cada etapa?_

1. **Alinhamento do Problema e EDA:** Utilizei a IA para analisar a estrutura das 4 tabelas, validar hipóteses de negócios e gerar as queries SQL para calcular *Win Rates* e métricas de tempo de ciclo (*median* e *P75*).
2. **Modelagem do Score:** Co-criei a lógica dos 4 pilares de pontuação (0 a 100) com a IA, definindo os critérios e os pesos com base nos insights extraídos das consultas.
3. **Desenvolvimento dos Notebooks:** Solicitei à IA a construção dos scripts PySpark para geração da tabela Delta e a criação do código Python divido em duas células (geração de payload e disparo opcional via Slack Webhook).
4. **Formatação do Deliverable:** Estruturei a documentação de submissão e os logs de explicação com auxílio da IA.

### Onde a IA errou e como corrigi

- **Dependência do Envio no Slack:** A versão inicial proposta unificava a geração de dados e o envio via HTTP em uma única função. Ajustei a abordagem para dividir em duas células independentes no Databricks, garantindo que a geração das mensagens pudesse ser testada na memória mesmo sem credenciais configuradas.
- **Formatos de Exportação:** Na apresentação da regra do score, solicitei a correção da formatação para um bloco Markdown contínuo, facilitando a cópia para a documentação técnica.

### O que eu adicionei que a IA sozinha não faria

- **Visão Prática do Fluxo de Trabalho Comercial:** Defini a estratégia de usar o Slack como a interface primária do vendedor, entendendo que um dashboard web adicional geraria atrito e baixa adesão no dia a dia do time de vendas.
- **Validação das Métricas de Negócio:** Conduzi a interpretação dos resultados do Databricks para garantir que a nota de estagnação (-15 pts) estivesse alinhada com o P75 real do histórico de perdas.

---

## Evidências

_Anexe ou linke as evidências do processo:_

- [x] Screenshots das conversas com IA / Export do Chat
- [x] Imagem da mensagem formatada no Slack enviada ao vendedor
- [x] Código dos Notebooks Databricks (ETL, Scoring e Dispatcher Slack)

---

_Submissão enviada em: 16/10/2026_