# Diário de Bordo — Process Log (Juliano Ananias)
## Challenge 003: Lead Scorer — G4 AI Master

Este documento registra cronologicamente como a Inteligência Artificial foi orquestrada estrategicamente para construir a solução, documentando prompts, análises, divergências e as decisões humanas que superaram o output padrão dos modelos.

---

### 10:00 — Entendimento do Problema & Hipóteses Iniciais
- **Ação:** Leitura cuidadosa do repositório oficial, guias de contribuição e datasets no Kaggle.
- **Divergência com a IA:** A IA propôs inicialmente treinar um modelo de Machine Learning tradicional (Random Forest / XGBoost) para predizer a probabilidade de conversão.
- **Julgamento Humano:** **Rejeitei essa abordagem.** O brief da Head de RevOps do G4 foi explícito: *"Não quero um modelo no Jupyter Notebook que ninguém vai usar. Quero uma ferramenta que o vendedor abra na segunda-feira de manhã e saiba onde focar."* Um modelo de ML opaco não gera ação comercial imediata nem explicabilidade para o vendedor. Decidi construir um **Sistema Web Interativo (Next.js 16 + Glassmorphism)** orientado a **Filas de Ação RevOps**.

---

### 11:15 — Exploração de Dados & Descoberta das Armadilhas Ocultas
- **Ferramentas:** Python 3.13, Pandas, OpenPyXL.
- **Descoberta Crítica 1 (Armadilha de 68,2% dos deals):** Ao cruzar o pipeline com a tabela de contas, descobri que **1.425 de 2.089 deals ativos não possuíam conta identificada**. 
  - *Decisão Humana:* Criar a fila prioritária **"3. Qualificar"** para orientar o vendedor a mapear porte e decisor antes de ligar.
- **Descoberta Crítica 2 (O Paradoxo do Tempo de Fechamento):** A mediana de fechamento dos negócios ganhos é de **57 dias**, enquanto os perdidos fecham ou são descartados em **14 dias**.
  - *Decisão Humana:* Deals que avançam rápido demais são frequentemente descarte prematuro; deals que estão entre 20 e 60 dias estão no sweet-spot de conversão. Criamos a métrica de *Idade Relativa* (`days_since_engage / median_days_won`).
- **Descoberta Crítica 3 (O Unicórnio GTK 500):** Produto com apenas 40 deals no histórico, mas ticket médio de **$26.707** (49x maior que a linha MG). Mereceu destaque imediato na fila **"1. Agir Hoje"**.

---

### 12:45 — Engenharia da Solução & Motor de Scoring
- **Lógica dos 5 Pilares de Scoring (0 a 100):**
  1. *Potencial Financeiro (25%)*
  2. *Qualidade da Conta & Setor (20%)*
  3. *Timing & Sweet-Spot de Ciclo (25%)*
  4. *Taxa Histórica do Vendedor (15%)*
  5. *Força do Relacionamento / Recompra (15%)*
- **Persistência & Ações em Tempo Real:** Permitir que o vendedor aponte prospecção hoje, atribua conta e altere etapas com recálculo instantâneo de score.

---

### 13:40 — Condução Guiada em Telas Primárias & Design Vítrico (Glassmorphism)
- **Refinamento de UX:** Em vez de abrir com um painel complexo e sobrecarregado, implementei uma **Condução em Telas Primárias Separadas**:
  - *Tela 1:* "Por onde começaremos a prospectar hoje?" (Missão)
  - *Tela 2:* Praça & Ofensores Regionais (West, East, Central)
  - *Tela 3:* Ranges de Ticket e Tempo de Fundação da Empresa
- **Copiloto Gemini 2.5 Flash:** Integrado com botão de **DeepResearch™** para diagnóstico dinâmico de qualquer recorte do pipeline, e análise tática por oportunidade individual antes de ligar.

---

### 14:15 — Validação em Produção & Teste de Resiliência
- Build de produção validado (`next build`).
- Servidor executando em tempo real na porta 3005 com resposta instantânea e fallback de alta confiabilidade.
