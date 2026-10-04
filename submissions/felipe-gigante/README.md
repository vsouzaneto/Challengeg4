# Submissão — Felipe Gigante — Challenge 002 (Redesign de Suporte)

## Sobre mim

- **Nome:** Felipe Gigante
- **LinkedIn:** (https://www.linkedin.com/in/felipegigante/)
- **Challenge escolhido:** 002 — Redesign de Suporte (Operações / CX)
- **Demo ao vivo:** **https://ai-support-os.vercel.app** — login demo `demo@g4.com.br` / `g4demo2026` 

---

## Executive Summary

Construí o **AI Support OS**, um produto que junta uma Smart Inbox no estilo Zendesk e um agente conversacional no estilo Botpress. Ele roda sobre os **8.469 tickets reais** do Dataset 1 e usa um classificador treinado nos **47.837 tickets** do Dataset 2 (acurácia de 86,6% no teste; **97,3% na faixa de confiança ≥ 0,85**, que cobre 60% dos tickets).

O diagnóstico teve um achado que muda a conversa com o Diretor. O Dataset 1 é sintético e **não sustenta conclusões de "driver"**: 49% dos tickets fechados têm resolução *antes* da primeira resposta, o CSAT é uniforme e um Random Forest prevê satisfação pior que o chute (19,7% vs 21,1%). Mesmo assim, os dados mostram gargalos inequívocos:
- **33% dos tickets sem nenhuma primeira resposta**;
- **50% marcados como High/Critical**, ou seja, a prioridade não prioriza;
- **45% do volume** em assuntos documentáveis.

A recomendação central:
- A IA responde ou prepara **100% dos tickets na hora**, o que zera o "sem primeira resposta".
- A IA automatiza só onde há conhecimento validado e risco baixo.
- **55% dos tickets permanecem humanos por desenho**: reembolso, cancelamento, cobrança, perda de dados, jurídico e fraude.
- Cada pergunta sem resposta vira conhecimento novo.

Potencial estimado com premissas editáveis no app: **~2.600 h/ano (1,5 FTE), ~R$ 106 mil líquidos/ano, ROI ~560%** para 30 mil tickets/ano.

---

## Solução

### Abordagem

1. **Decomposição do problema antes de abrir qualquer ferramenta.** O brief pede três coisas: onde perdemos tempo, o que automatizar e "me mostre que funciona". Escrevi minha visão de produto (Zendesk + Botpress, LLM barata, CSAT, KB com gaps, HITL upstream/downstream, guardrails, evals, MCP) e iterei com o ChatGPT até virar um PRD com regras de negócio ([`docs/PRD.md`](docs/PRD.md)).
2. **Auditoria dos dados antes de analisar.** Antes de calcular médias, testei se os dados conseguiam responder às perguntas. Não conseguiam do jeito ingênuo, e isso virou o primeiro achado do diagnóstico.
3. **Diagnóstico com estatística, não com médias:** Kruskal-Wallis, Mann-Whitney, teste de permutação, Cramér's V e Random Forest com validação cruzada ([`solution/analysis/diagnostico.py`](solution/analysis/diagnostico.py)).
4. **Classificador com evidência.** Comparei 4 approaches, separei train/val/test, calibrei os thresholds do gate no conjunto de validação e exportei o modelo para TypeScript com **100% de paridade** com o sklearn ([`solution/analysis/train_classifier.py`](solution/analysis/train_classifier.py)).
5. **Produto funcional com pipeline real.** Nada na demo é pré-classificado: os 8.469 tickets e os cenários de demo passam pelo mesmo pipeline que atende o portal ao vivo.
6. **Evals como gate de qualidade.** A primeira execução pegou uma automação insegura; corrigi e o histórico fica registrado no app.

### Resultados / Findings

#### 1. Diagnóstico operacional (Dataset 1)

| Pergunta | Achado | Evidência |
|---|---|---|
| Os dados respondem? | **Parcialmente.** Sem timestamp de criação (o FRT não é duração); 49,3% com TTR < FRT; CSAT uniforme (χ² p=0,80); tipo independente do assunto (V=0,03); o texto não prevê o tipo (20,3% vs 20% do acaso); resoluções em lorem ipsum. | `diagnostico.py`, página **/diagnostico** |
| Onde o fluxo trava? | **No backlog e na priorização, não em canal ou tipo.** 33,3% dos tickets abertos sem 1ª resposta (692 deles "Critical"); 34% parados aguardando o cliente; 49,8% High/Critical. Canal, tipo e prioridade **não** diferem em tempo de resolução (KW p=0,77 / 0,14 / 0,07). A "pior combinação" (Chat · Technical · Low, mediana 13,2h) **não** é significativa no teste de permutação (p=0,13). | 1.402 durações válidas |
| O que impacta a satisfação? | **Nada que esteja no dataset.** Nenhuma variável é significativa; Spearman entre tempo de resolução e CSAT ρ=0,02; RF 19,7% vs baseline de 21,1%; R² = −0,05. "Chat tem o melhor CSAT (3,08)" é ruído. | 2.769 tickets fechados |
| Quanto desperdiçamos? | **~3.100 h/ano** (de 6.875 h totais) gastas em tickets de assuntos documentáveis; **~2.600 h/ano recuperáveis** (triagem 1.083 h, automação 472 h, sugestão 593 h, preparo para humano 462 h). | Calculadora em **/diagnostico** (premissas editáveis) |

#### 2. Proposta de automação

- **Automatizar:** triagem e roteamento (classificador, 8 categorias → time), prioridade por sinais observáveis, primeira resposta imediata, respostas ancoradas na KB para setup, bateria, compatibilidade, rede, acesso e instalação, sugestão de resposta para o agente, agrupamento de perguntas repetidas, detecção de frustração.
- **NÃO automatizar** (vai para humano mesmo com alta confiança): reembolso e chargeback, cancelamento/churn, cobrança indevida, ameaça jurídica (Procon, advogado, LGPD), fraude e conta invadida, perda de dados, emoção severa ou frustração crescente. A IA prepara o caso, mas quem decide é o humano. Nos dados, isso é **54,8%** dos tickets pela Opportunity Matrix e **55,7%** pelo pipeline: os dois métodos convergem.
- **Fluxo:** `Input guardrail → Classificação → Sentimento → Risco → Prioridade → KB → Confidence gate (AUTO ≥0,85 · SUGESTÃO ≥0,60 · HUMANO) → Output guardrail → Cliente → CSAT → Knowledge Gap → novo artigo`. Upstream: a IA passa para o humano com resumo e motivo. Downstream: o humano decide e devolve, e a IA confirma, encerra e pede CSAT. Detalhes em [`docs/automacao.md`](docs/automacao.md).

#### 3. Protótipo — AI Support OS

**Stack:** Next.js 16 + TypeScript, SQLite (libsql/Turso), deploy na Vercel. Código e instruções em [`solution/app`](solution/app/README.md).

| Área | O que demonstra |
|---|---|
| **/login, /signup** | Autenticação com cadastro (scrypt + sessão em SQLite) |
| **/dashboard** | KPIs com filtros de 24h/7d/30d/60d/90d: volume por decisão do gate, backlog, CSAT, TTR/FRT, Safe Resolution Rate (North Star), AI Acceptance Rate, KB coverage, guardrail rate, top assuntos com tendência, motivos de escalonamento, sentimento, prioridade declarada × calculada, roteamento e CSAT × automação |
| **/diagnostico** | O diagnóstico acima em abas (onde trava, satisfação, o que automatizar, ROI, limites dos dados) |
| **/perguntas** | Text-to-SQL "Pergunte aos dados": pergunta em português → SQL somente leitura (LLM ou biblioteca de consultas) → tabela + gráfico; SQL editável |
| **/confianca** | Governança do gate: fórmula do score, thresholds mínimo/máximo e pesos ajustáveis, simulação do impacto nos 8.469 tickets, evidência de acerto por faixa e teste no golden set antes de salvar |
| **/simulador** | Emulador do cliente dentro do console (portal num navegador simulado) com cenários de demo clicáveis |
| **/inbox** | Smart Inbox em 3 colunas (lista, conversa, AI Insights) com categoria, confiança, prioridade, sentimento, risco, artigos, trace de cada etapa e as ações enviar (accepted/edited), rejeitar, regenerar, assumir (upstream), devolver para IA (downstream) e resolver |
| **/portal** | Portal do cliente (o mesmo do simulador), estilo Botpress: abre o ticket, recebe resposta na hora ou handoff, conversa com o humano, avalia com CSAT e tem um painel "por dentro da IA" |
| **/knowledge** | Gaps pendentes agrupados por similaridade → "aprovar conhecimento" → artigo publicado → a próxima pergunta similar é respondida |
| **/evals** | Comparação de modelos, métricas por classe, matriz de confusão, curva de calibração do gate, golden set comportamental (58 casos) e histórico de execuções |
| **MCP** | `mcp/server.ts`: 7 tools (`knowledge.search_articles`, `support.triage_ticket`…) reutilizáveis por outros agentes |
| **LLM (opcional)** | Cascata local → `llama-3.1-8b-instant` → `llama-3.3-70b` (Groq) quando a confiança está baixa. Sem chave, roda 100% local, com custo zero e determinístico |

**Números do protótipo (eval atual):**
- Classificação: 84,2% no golden set de 480 tickets do teste do D2 e 100% de paridade com o Python.
- Escalonamento: recall de 100% e **0 automações inseguras**.
- Detecção de injeção: 100%, sem falsos positivos.
- Retrieval: 19/19 acertos.
- Gaps detectados: 8/8.
- Prioridade: 100% dentro de ±1 nível.

**Roteiro de demo (5 min):** [`docs/demo.md`](docs/demo.md)

### Recomendações (priorizadas)

1. **Semana 1 — Primeira resposta imediata em 100% dos tickets.** É o maior gargalo visível (33% sem resposta) e o de menor risco, porque a IA confirma o recebimento, classifica e roteia.
2. **Semanas 1–2 — Triagem e prioridade automáticas.** Trocar a prioridade declarada (50% "urgente") pela calculada; rotear pelo classificador. São ~1.000 h/ano só em triagem.
3. **Semanas 2–4 — Modo SUGESTÃO antes do AUTO.** Ligar a resposta sugerida para todos os agentes e medir o AI Acceptance Rate. Só promover uma categoria para AUTO quando acceptance ≥ 90% e o eval tiver 0 automações inseguras.
4. **Contínuo — Rotina de Knowledge Gaps.** Um dono de KB revisa os gaps semanalmente, ordenados por ocorrência.
5. **Instrumentação.** Coletar CSAT por ticket com o contexto (automação, categoria, sentimento, tempo) e um timestamp real de criação. Em 60 dias, refazer o diagnóstico de drivers com dados confiáveis.
6. **Re-treinar o classificador com labels da própria operação.** O modelo do D2 (TI interna) classifica 88% dos tickets B2C como "Hardware"; o feedback do agente na Inbox gera esses labels.

### Limitações

- **Dataset 1 sintético:** as conclusões sobre tempos e drivers de CSAT são "não há evidência", não "não há efeito". O volume anual (30k) vem do brief; o AHT e o custo/hora são premissas de mercado, editáveis no app.
- **As datas do D1 foram redistribuídas** nos últimos 90 dias para viabilizar os filtros do dashboard (seed determinístico, documentado). O FRT só é medido nos tickets criados no app.
- **O golden set comportamental foi escrito por mim**, conhecendo as regras: os 58/58 têm viés otimista. O próximo passo é um golden set de 200–500 tickets rotulados por agentes que não escreveram as regras.
- **Busca da KB lexical (TF-IDF × cobertura), não por embeddings:** foi escolhida por custo zero, explicabilidade e nenhuma infraestrutura. Ela falha em paráfrases sem termos em comum e no cruzamento PT↔EN (ex.: "trade-in" não agrupa com "troca do aparelho antigo"). A evolução natural é trocar `retrieve()` por embeddings mantendo a mesma interface.
- **O tier LLM não foi avaliado neste deploy** (sem chave configurada durante o desenvolvimento). Todos os números acima são do tier local.
- **Deploy:** Vercel + Turso (SQLite gerenciado, mesmo driver libsql do ambiente local). A demo é compartilhada: tickets e artigos criados por avaliadores ficam visíveis para todos.
- **Sem integrações reais** (WhatsApp, CRM, billing), conforme os não-objetivos do PRD.

---

## Process Log — Como usei IA

> Narrativa completa, com erros, decisões e iterações: [`process-log/README.md`](process-log/README.md)

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| ChatGPT | Brainstorm a partir da minha visão de produto e geração do PRD com regras de negócio ([prompt original](process-log/chat-exports/01-chatgpt-prompt-inicial.md)) |
| Claude Code (Opus) | Auditoria dos dados, análise estatística, treino e comparação de modelos, construção do app (Next.js/TS), evals, debugging e documentação |
| Groq (Llama 3.x) — opcional | Tier LLM da cascata (classificação estruturada, resumo, resposta ancorada) |

### Workflow

1. Li o desafio, escolhi o 002 e escrevi minha visão de produto (Zendesk + Botpress, HITL, guardrails, evals, MCP).
2. Iterei com o ChatGPT até ter um PRD com regras de negócio, thresholds, o que não automatizar e o escopo de 4–6h. Li o PRD inteiro e o usei como norte.
3. No Claude Code: baixei os datasets reais e, **antes de analisar, auditei**. Descobri que o D1 é sintético, e isso mudou o diagnóstico.
4. Diagnóstico com testes estatísticos; Opportunity Matrix com julgamento de risco por assunto.
5. Classificador: comparei 4 approaches, calibrei thresholds no conjunto de validação, exportei para TS e verifiquei a paridade.
6. Construí o pipeline e rodei sobre os 8.469 tickets. **Cinco iterações** de calibração guiadas pelos resultados (detalhes no process log).
7. Escrevi o golden set e rodei os evals. A v2 pegou uma automação insegura; corrigi.
8. Construí as telas, testei no navegador o fluxo completo (portal → gap → artigo → resposta) e documentei.

### Onde a IA errou e como corrigi

- **Bug de substring:** "sue" (processar) casava dentro de "issue", e quase todos os tickets ganhavam um sinal de "ameaça". Detectei porque 74% dos tickets saíram "Frustrated", e corrigi com word boundaries.
- **Busca da KB com falsos positivos:** "alterar endereço de cobrança na nota emitida" casava com "Formas de pagamento" (0,59) só por causa de "cobrança/nota". Criei o score `similaridade × cobertura de termos raros`, e a pergunta sem resposta caiu para 0,06.
- **Automação insegura no eval v2:** "Quero meu dinheiro de volta" foi respondida em AUTO, porque o regex de risco só tinha "money back". O eval pegou, corrigi, e agora `npm run eval` falha se houver qualquer automação insegura.
- **Primeira calibração do pipeline mandava 100% do D1 para humano**, porque o texto sintético não tem sinal. Decidi usar o assunto do formulário como sinal estruturado com peso 0,8, para que ele nunca sozinho gere resposta automática.
- **Análise ingênua:** a feature importance de um RF sobreajustado apontaria "tempo de resolução" como driver de CSAT. Rejeitei porque o modelo é pior que o baseline.

### O que eu adicionei que a IA sozinha não faria

- A **visão de produto** (Zendesk + Botpress, HITL upstream/downstream, CSAT com contexto, KB que aprende com gaps, guardrails de entrada e saída, MCP para reuso entre agentes) e a decisão de entregar **produto em TypeScript na Vercel** em vez de notebook/Streamlit.
- **Desconfiar dos dados antes de concluir**, e transformar "os dados não sustentam" em recomendação acionável (instrumentar a operação).
- O **julgamento de risco** por assunto (o que nunca automatizar) e a regra de que dúvidas de cobrança no máximo viram sugestão.
- **Validar thresholds com dados** em vez de aceitar os números do PRD, e exigir paridade TS × Python antes de confiar no modelo em produção.

---

## Evidências

- [x] Screenshots das conversas com IA → `process-log/screenshots/`
- [ ] Screen recording do workflow *(opcional)*
- [x] Chat exports → [`process-log/chat-exports/`](process-log/chat-exports/) (prompt inicial no ChatGPT)
- [x] Git history (commits da branch de submissão)
- [x] Outro: histórico de evals versionado no app (**/evals**), `npm run eval` e o PRD gerado com IA em [`docs/PRD.md`](docs/PRD.md)

---

_Submissão enviada em: 04/10/26
