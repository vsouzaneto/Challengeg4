# Challenge 003 — Lead Scorer (G4 Educação)
**Candidato / Autor:** Ivaldo Junior

Submissão oficial de projeto para o desafio *ai-master-challenge* do G4 Educação.

## 1. Visão Geral
Temos 35 vendedores distribuídos por equipas comerciais gerindo milhares de oportunidades de negócio no CRM. A priorização "no feeling" é o gargalo.

Esta solução oferece um **Motor de Inteligência Analítica Pura** (`Pipeline Intelligence Engine`), processado localmente em Python (Pandas e NumPy) para extrair o real valor do pipeline e entregar os leads ordenados por propensão.

## 2. Setup e Execução

1. **Clone/Navegue para o diretório:**
   ```bash
   cd challenges/build-003-lead-scorer/submission-ivaldo-junior/
   ```
2. **Dados do CRM:**
   Garantir a presença dos ficheiros (`accounts.csv`, `products.csv`, `sales_teams.csv`, `sales_pipeline.csv`).
3. **Dependências:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Execução da Interface:**
   ```bash
   streamlit run app.py
   ```
5. **Rotina de Garantia de Qualidade (QA):**
   Execute a suíte de testes automatizados local para validar a integridade e resiliência:
   ```bash
   pytest test_pipeline_qa.py
   ```

## 3. Motor Analítico (Decisão Arquitetural: Zero LLM)
Para resolver problemas de negócio massivos (1.000+ linhas/dia), optou-se deliberadamente por **NÃO utilizar Modelos de Linguagem (LLM)** no loop de avaliação por lead.

- **Vantagens Obtidas:** 
  - **Latência de <20ms:** Cálculos vetorizados no CPU em microssegundos.
  - **Custo Zero Constante:** Sem limites de API (rate limits) e ausência total de tokens a pagar.
  - **Determinismo Perfeito:** 100% reproduzível. Ideal para ambientes de pagamento de comissões RevOps.

### Algoritmo de Scoring:
- **Baseline Dinâmico:** Cálculos de *Win Rate* usando `.groupby().mean()` cruzado do histórico "Won/Lost" da empresa inteira.
- **Peso Segmentado:** Favorecimento das contas Enterprise vs PME, gerido programaticamente.
- **Stagnation Decay:** Introdução de uma **penalização de decaimento logarítmica/sigmóide**. Após 45 dias sem movimento, o lead perde viabilidade rápida e estruturada, acendendo sinais de alerta.
- **Explainability Natural (NLG determinística):** Construção baseada em concatenação (Fatores Fortes 🟢 e Alertas 🔴).

## 4. UI/UX: Heurísticas de Usabilidade e Estética G4
Interface refatorada em concordância com a marca oficial G4 (Midnight Blue & Dourado).

- **Visibilidade de Estado (Heurística 1):** Feedback de registos a ser renderizados ("A exibir X de Y").
- **Correspondência ao Mundo Real (Heurística 2):** Barras de pontuação gamificadas (`ProgressColumn`).
- **Consistência Visual (Heurística 4):** Painel executivo superior (4 cartões com métricas globais e de valor projetado).
- **Reconhecimento (Heurística 6):** Colunas largas na tabela interativa dispensam cliques adicionais para "Por que priorizar este lead?".

## 5. Garantia de Qualidade (QA) e Resiliência
A aplicação conta com uma camada rigorosa de tolerância a falhas testável (`pytest test_pipeline_qa.py`):
- **Tratamento Dinâmico de Esquemas:** O pipeline lida graciosamente com diferenças em nomes de colunas, como `stage` e `deal_stage`.
- **Limpeza e Formatação (Stripping):** Todas as colunas de tipo texto recebem `.str.strip()` para eliminar espaçamentos maliciosos ou acidentais provenientes dos CSVs.
- **Tratamento de Nulos (NaN Handling):** As variáveis quantitativas (como valores financeiros) e qualitativas nulas recebem substituição segura, prevenindo *crashes* na interface.
- **Comportamento Seguro de Filtros Vazios:** Se uma pesquisa ou filtro não retornar resultados, o painel mantém os KPIs zerados e exibe um aviso amistoso (em vez de levantar exceções).
