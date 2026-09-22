# Submissão — Rodrigo Santiago — Challenge 003

## Sobre mim

- **Nome:** Rodrigo Santiago
- **LinkedIn:** https://www.linkedin.com/in/rodrigo-christo/
- **Challenge escolhido:** 003 — Lead Scorer (Vendas / RevOps)

---

## Executive Summary

Consolidei os 4 CSVs originais em uma base única no Google Sheets via Apps Script, padronizando inconsistências como `technolgy`/`technology` e `GTXPro`/`GTX Pro`, tratando valores monetários com problema de locale e definindo regras para campos vazios. Criei uma aba `legend` documentando o significado de cada campo em linguagem acessível, garantindo que qualquer pessoa entenda a base. Enriqueci a base com mais de 20 indicadores derivados usando ARRAYFORMULA e MAP+LAMBDA (win rates cruzados por vendedor/produto/setor, tiers de porte de conta, ciclos médios, flags de recorrência) e defini um modelo heurístico de scoring 0-100 ponderado em 4 fatores explicáveis. Sobre essa base construí uma ferramenta web (Google Apps Script + Netlify wrapper) com painel, listagem filtrada e kanban drag-and-drop, integrada ao Gemini via Google AI Studio para análise contextual de cada deal. A análise dos indicadores revelou que apenas 5% dos deals abertos (107 de 2.089) se qualificam como alta prioridade real, validando uma régua ALTA/MÉDIA/BAIXA enxuta em vez da inflação de "tudo é urgente" — recomendação central para a Head de RevOps focar esforço concreto e mensurável na semana.

---

## Solução

**Link ao vivo:** https://desafio-g4-003.netlify.app/
**Credenciais de acesso (pré-preenchidas):** `admin@garoconsultoria.com.br` / `garo2026`

### Abordagem

Ataquei o problema em 5 fases sequenciais, com contenção deliberada de escopo em cada uma para não cair no "quanto mais features, melhor".

**Fase 1 — Entendimento e preparação dos dados.** Baixei os 4 CSVs do Kaggle e importei em abas separadas de um Google Sheets. Fiz auditoria de estrutura com IA, identifiquei inconsistências reais (erro de digitação `technolgy`, diferença `GTXPro`/`GTX Pro`, conflito de locale nos valores monetários, distribuição de campos vazios). Consolidei tudo numa aba `main` via Apps Script temporário (`criarBaseMain()`) usando padrão LEFT JOIN em memória com dicionários, aplicando todas as correções e formatando colunas monetárias como USD.

**Fase 1.5 — Documentação da base (aba `legend`).** Criei uma aba separada `legend` com dicionário de dados descrevendo o significado de cada campo em linguagem acessível para leigos, indicando se o campo é original do dataset ou calculado por mim, e qual a heurística de cálculo dos derivados. Fundamental para explicabilidade e para qualquer pessoa (técnica ou não) entender o que está sendo analisado.

**Fase 2 — Feature engineering com ARRAYFORMULA.** Optei por criar todas as colunas derivadas via fórmulas de matriz direto na aba `main` em vez de scripts assíncronos. Motivo: mantém a planilha viva e reativa, qualquer mudança nos dados recalcula tudo automaticamente. Descoberta técnica importante: `CONT.SES` e `MÉDIASES` não funcionam dentro de `ARRAYFORMULA` (retornam o mesmo valor em todas as linhas), então usei a combinação moderna `MAP + LAMBDA` para as fórmulas agregadas.

**Fase 3 — Definição do modelo de scoring.** Rejeitei a ideia de usar um modelo de ML tipo XGBoost pela perda de explicabilidade (a Head de RevOps pediu que o vendedor entenda por quê). Defini um score heurístico 0-100 ponderando 4 fatores: proficiência do vendedor com o produto (40%), tração de mercado do produto+setor (20%), cliente recorrente (20%) e frescor no pipeline (20%). Sobre esse score, apliquei uma matriz 2x2 (probabilidade × valor esperado) gerando quadrantes A/B/C/D.

**Fase 4 — Diagnóstico da régua de prioridade.** Antes de definir a tradução final ALTA/MÉDIA/BAIXA, rodei uma função de diagnóstico para verificar se o quadrante A não estava inflacionado. Resultado: apenas 5% dos deals em quadrante A, o que validou usar a régua direta A=ALTA, B+C=MÉDIA, D=BAIXA sem forçar terça parte artificial.

**Fase 5 — Construção do webapp e deploy.** Stack Google Apps Script (backend em `.gs` lendo a planilha) + HTML/CSS/JS vanilla no frontend + Gemini via Google AI Studio para análise contextual de cada deal + Netlify wrapper com iframe para manter URL fixa entre deploys. Interface com sidebar (Painel Principal / CRM Listagem / CRM Kanban), filtros multi-select, drag-and-drop, modal de análise IA.

### Resultados / Findings

**Base consolidada e enriquecida.** Aba `main` com 8.800 linhas e 47 colunas (24 originais + 23 derivadas calculadas via ARRAYFORMULA), aba `legend` com o dicionário completo, ambas vivas e reativas a mudanças nos dados.

**Decisão crítica de data de referência.** O dataset é um snapshot de 2017 (última data: 31/12/2017). Usar `HOJE()` faria deals abertos aparecerem com mais de 3.000 dias, distorcendo qualquer análise de ciclo. Congelei a "data atual" em 31/12/2017 em toda a lógica temporal — decisão que percebi antes da IA sugerir.

**Distribuição real dos deals abertos (2.089 no total):**
- Quadrante A (Foco Máximo — alta chance + alto valor): 107 deals (5%)
- Quadrante B (Quick Win — alta chance + baixo valor): 146 deals (7%)
- Quadrante C (Estratégico com Risco — baixa chance + alto valor): 792 deals (38%)
- Quadrante D (Baixa Prioridade): 1.044 deals (50%)

**Régua de prioridade final:**
- **ALTA** = Quadrante A (107 deals). Foco máximo da semana.
- **MÉDIA** = Quadrantes B + C (938 deals). Deals rápidos ou grandes com risco.
- **BAIXA** = Quadrante D (1.044 deals). Nutrir ou descartar.

Ordenação secundária dentro de cada faixa sempre por `expected_value` decrescente.

**Solução funcional publicada:** https://desafio-g4-003.netlify.app/ com login pré-preenchido, painel, listagem filtrada, kanban interativo, análise IA embutida.

### Recomendações

**Adotar a régua ALTA/MÉDIA/BAIXA como norte semanal.** Cada vendedor abre a Listagem, filtra por seu nome + Prioridade=ALTA, e obtém a lista curada. Managers filtram por sua equipe. A Head de RevOps filtra por regional para diagnóstico geográfico.

**Usar o botão "Analisar com IA" como ferramenta de coaching contextual.** Vendedor com dúvida sobre o próximo passo em um deal específico clica e recebe em 3 frases: diagnóstico do score, status do ciclo comparado ao histórico do produto, ação tática recomendada. Não substitui julgamento humano, mas dá um piso analítico.

**Institucionalizar as descobertas de dados sujos.** As inconsistências detectadas (`technolgy`/`technology`, `GTXPro`/`GTX Pro`, campos vazios sem padrão) provavelmente existem em outros pipelines do CRM. Vale documentar as regras de padronização e aplicar no processo de entrada de dados, não só na análise.

**Rever mensalmente os pesos do scoring.** Os 40/20/20/20 são hipóteses de negócio defensáveis, não verdade absoluta. Comparar a lista sugerida pela ferramenta com os deals que efetivamente fecharam nos meses seguintes permite calibrar.

### Limitações

**Análise temporal ausente.** A ferramenta olha o snapshot atual do pipeline, mas não mostra evolução mês a mês, sazonalidade ou tendência de win rate ao longo do tempo. Seria a próxima feature.

**Scoring heurístico, não preditivo.** Os pesos foram definidos por raciocínio de negócio, não por regressão sobre dados históricos. Um modelo calibrado nos ~6.700 deals fechados provavelmente melhoraria o ranking marginalmente, ao custo de perder explicabilidade.

**Sem drill-down por vendedor personalizado.** Filtros permitem isolar um vendedor, mas não há uma "visão pessoal" com tarefas do dia, calendário integrado, notificações.

**Análise IA propositalmente enxuta.** Modelo `gemini-flash-lite` com `maxOutputTokens: 250` e prompts curtos foram escolha consciente de custo. Em produção, modelo maior e prompts mais elaborados aumentariam a profundidade.

**Escalar para outros CRMs exigiria refatoração da camada de dados.** A solução está acoplada ao Google Sheets. Migrar para Salesforce, HubSpot ou Pipedrive exigiria substituir a leitura por chamadas de API do CRM, mantendo scoring e interface.

**Layout mobile básico.** Funciona, mas o kanban vira coluna única. Uma versão mobile-first mereceria repensar a experiência (lista sequencial com swipe em vez de kanban horizontal).

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| **Google Gemini (chat web)** | Auditoria estrutural dos 4 CSVs, identificação de inconsistências, geração dos Apps Scripts de consolidação e padronização, criação da aba `legend`, definição das ARRAYFORMULAs e MAP+LAMBDA para indicadores derivados, definição dos clusters (tiers de porte, ciclos, produtos) |
| **Claude** | Arquitetura do webapp em Apps Script (backend, frontend, prompts), escrita do código dos 3 arquivos (`Code.gs`, `Prompts.gs`, `Index.html`), iterações de UX e design system, resolução de bugs (escape HTML do caractere `&`), calibração dos prompts do Gemini para respostas curtas |
| **Google AI Studio (Gemini API)** | Integração runtime no webapp para análise contextual de cada deal e análise agregada do pipeline. Modelo `gemini-flash-lite` com `maxOutputTokens: 250` e `temperature: 0.4` |
| **Google Apps Script + Google Sheets** | Ambiente de execução do backend e da lógica de scoring. Ferramenta escolhida por familiaridade prévia (construo Apps Scripts desde 2018) |

### Workflow

1. Baixei os 4 CSVs do Kaggle e importei cada um em uma aba do Google Sheets. Enviei amostras iniciais ao Gemini pedindo análise estrutural, chave em comum entre planilhas e identificação de inconsistências. **Momento importante:** no primeiro prompt, o Gemini já quis sair gerando código; freei explicitamente com "não, opa, peraí, vamos com calma" pedindo primeiro o entendimento e a metodologia antes de qualquer script. Isso mudou o tom do resto da conversa.

2. Consolidei os 4 CSVs na aba `main` via Apps Script (`criarBaseMain()`) gerado pelo Gemini, com correções embutidas: `technolgy`→`technology`, unificação `GTXPro`/`GTX Pro`, `forceNumber()` para tratar locale brasileiro nos valores monetários, regra de padronização de vazios ("-" para texto, vazio para número e data).

3. Criei a aba `legend` via segundo Apps Script (`criarAbaLegend()`) com dicionário de dados de cada campo em linguagem acessível para leigos, marcando origem (original ou calculado) e heurística de cálculo.

4. **Percebi sozinho** que usar `HOJE()` distorceria o cálculo de dias por ser dataset de 2017. Levei essa preocupação ao Gemini, que confirmou com Python que a última data era 31/12/2017. Adotamos 31/12/2017 como "hoje" de referência em todos os cálculos temporais.

5. Discuti com o Gemini a viabilidade técnica de criar 20+ indicadores derivados via ARRAYFORMULA. Ele identificou que `CONT.SES` e `MÉDIASES` não funcionam nesse contexto, sugeriu a combinação `MAP + LAMBDA` para as fórmulas agregadas (win rates por vendedor/produto/setor/conta). Colei as fórmulas resultantes na linha 1 de cada nova coluna da aba `main`.

6. **Combinei duas IAs no mesmo passo:** as fórmulas conceituais do scoring vieram do Claude (que sugeriu a estrutura de blocos e a lógica geral), e trouxe para o Gemini adaptar para a sintaxe correta do ARRAYFORMULA no Google Sheets em português. Prompt literal usado: "Veja campos que o Claude me sugeriu. Ele mandou a fórmula mais ou menos da lógica. Mas a gente teria que transformar para ARRAYFORMULA com título certinho já."

7. Antes de definir a régua ALTA/MÉDIA/BAIXA final, discuti com o Claude o risco de "quando tudo é prioridade, nada é prioritário". Escrevi uma função de diagnóstico (`analisarPrioridades()`) que rodou nos 2.089 deals abertos e retornou a distribuição por quadrante. Com base no resultado (5% em A), validei a régua sem forçar terça parte artificial.

8. Migrei para o Claude para construir o webapp. Discutimos a arquitetura em 3 arquivos (`Code.gs`, `Prompts.gs`, `Index.html`) e ele gerou o código, sempre em blocos incrementais que eu colava e testava. Iteramos várias vezes na UX (primeira versão foi rejeitada por parecer "genérica de consultoria", refizemos na direção "Attio/Pipedrive vibe").

9. Publiquei o webapp com deploy Anyone no Apps Script e criei um site simples no Netlify (`desafio-g4-003.netlify.app`) com HTML+iframe apontando para a URL do Apps Script. Assim mantenho URL fixa entre deploys.

### Onde a IA errou e como corrigi

**Erro do Gemini mapeando colunas erradas para o Bloco 3 do scoring.** Ele "chutou" as letras das colunas (AL, AM, AN) sem verificar a planilha real. Corrigi mandando um print e um "Você está errado. veja como está a foto atual". Depois disso ele mapeou corretamente (S, AE, AL, AN, AR) e as fórmulas funcionaram.

**Bug crítico no frontend gerado pelo Claude: parser HTML quebrando com caractere `&`.** Uma conta chamada "Gekko & Co" (existente no dataset) fazia a página inteira ficar em branco porque o `&` no atributo `data-value` do dropdown de filtros era interpretado como início de entidade HTML mal-formada. Diagnostiquei escrevendo uma função de verificação (`checarNomes()`) que varreu os 8.800 registros e retornou apenas 1 nome com caracteres especiais. Corrigi com escape explícito de `&`, `<`, `>`, `"`, `'` em toda concatenação de HTML.

**Análise IA saindo longa demais na primeira versão.** O Gemini vinha com parágrafos inteiros, contexto de mais, tudo que eu não pedi. Iterei os prompts travando saída em "3 frases numeradas, máximo 80 palavras", troquei do modelo `gemini-flash` para `gemini-flash-lite` e adicionei `generationConfig` explícito (`maxOutputTokens: 250`, `temperature: 0.4`, `topP: 0.8`). Velocidade caiu de 8-15s para 2-4s e respostas ficaram consultivas.

**Sugestões da IA que rejeitei ativamente.** Em vários momentos, a IA quis expandir escopo (adicionar dashboard temporal, sugerir modelo ML complexo, criar feature de envio automático de email). Recusei todas por não agregarem ao problema específico ou por perderem a explicabilidade solicitada pela Head de RevOps.

### O que eu adicionei que a IA sozinha não faria

**Contenção de escopo repetida.** A IA tende a expandir. Freei em vários momentos: no primeiro prompt do Gemini ("não, opa, peraí, vamos com calma"), na recusa de ML complexo em favor de heurística explicável, na definição de que a análise IA seria propositalmente enxuta por consciência de custo.

**Decisão da data de referência 31/12/2017.** Percebi antes da IA sugerir. Levei o problema já formulado para validação, não pedi solução aberta.

**Escolha da stack Apps Script + Netlify wrapper.** Baseada em experiência prévia de 8 anos com Apps Script, não em sugestão da IA. Trade-off consciente: performance limitada (17s primeira carga) compensada por deploy simples, zero manutenção de servidor, acesso nativo ao Google Workspace.

**Régua ALTA/MÉDIA/BAIXA validada empiricamente antes de adotar.** Não segui cegamente a proposta da IA. Rodei diagnóstico para confirmar que o quadrante A não estava inflado, só então adotei a régua.

**Design system reaproveitado da Garô Consultoria.** Contexto pessoal (sou co-fundador da consultoria) que a IA não tinha. Reaproveitamento consciente para simular contexto de entrega real ao cliente, com paleta petróleo+laranja, tipografia Manrope e breadcrumb estilo Garô.

**Bug do `&` diagnosticado com abordagem sistemática, não chute.** Em vez de aceitar sugestões aleatórias de correção do frontend, escrevi função de auditoria específica para achar o culpado. Só então apliquei a correção certa (escape HTML universal), evitando falsos positivos.

---

## Evidências

- [x] **Chat exports:** conversa completa com o Gemini em `process-log/chat-gemini-completo.md`, cobrindo consolidação de dados, ARRAYFORMULAs, MAP+LAMBDA, criação da aba `legend` e Bloco 3 de scoring.
- [x] **Link público:** conversa completa com o Claude em `process-log/chat-claude-link.md`, cobrindo arquitetura do webapp, iterações de código, resolução de bugs e refinamento de prompts.
- [x] **Git history:** commits desta submissão mostram evolução dos arquivos.
- [x] **Código fonte da solução:** disponível em `solution/` com os 3 arquivos do webapp (`Code.gs`, `Prompts.gs`, `Index.html`), os Apps Scripts temporários de preparação dos dados em `solution/apps-scripts-preparacao/` e a documentação das ARRAYFORMULAs em `solution/formulas-arrayformula.md`.
- [x] **Solução ao vivo:** https://desafio-g4-003.netlify.app/ (credenciais `admin@garoconsultoria.com.br` / `garo2026` pré-preenchidas).

---

*Submissão enviada em: 22/09/2026*
