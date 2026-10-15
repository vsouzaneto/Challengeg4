# Agente 3: revisão de conformidade da entrega

_Revisor exigente com a postura de um avaliador do G4. Somente leitura: nenhum arquivo do projeto foi alterado. Data: 2026-10-14. Estado avaliado: branch `submission/arthur-leite`, HEAD `ae391b0`, contra `upstream/main` (Gestao-Quatro-Ponto-Zero/ai-master-challenge)._

Fontes lidas na íntegra: `README.md`, `CONTRIBUTING.md`, `submission-guide.md`, `templates/submission-template.md`, `challenges/README.md`, `challenges/process-002-support/README.md` e a descrição da vaga (fornecida pelo orquestrador). Da submissão li `README.md`, `PROCESS_LOG.md`, `proposta.md`, `auditoria.md`, `modelo_desperdicio.md`, `motor_final.md`, o texto do `relatorio-executivo.html` (o PDF tem 6 páginas), `fase5_final_parecer.md`, as mensagens do candidato no `chat-exports/conversa_claude_code.md` e a estrutura do `app.py`.

---

## 0. Veredito em uma linha

A entrega supera o baseline em análise e em julgamento: a auditoria da base sintética, a política "rotear ≠ executar ≠ responder" e o benchmark honesto contra LLM são diferenciais reais. **O maior risco não é técnico. É de atribuição.** A vaga pede "demonstre com clareza qual foi o seu papel e qual foi o papel da IA", e o chat export versionado mostra que **ideias que o README atribui ao candidato foram propostas pela IA**. Um avaliador que abrir o export vai notar. O segundo risco são lacunas de forma: o PR ainda não foi aberto, há um placeholder `{{DATA}}` e o ROI está em h/ano, enquanto o case pede h/mês.

---

## 1. Matriz de conformidade

Legenda: **A** = ATENDE · **P** = PARCIAL · **N** = NÃO ATENDE · **—** = não se aplica ou pendente de ação externa.

### 1.1 README raiz (regras gerais e o que é avaliado)

| # | Exigência / frase | Onde a entrega atende | Veredito | O que falta |
|---|---|---|---|---|
| R1 | Fork → escolher **um** desafio | Fork `arthurroleite/ai-master-challenge`; só o 002 | A | — |
| R2 | Solução em `submissions/seu-nome/` | `submissions/arthur-leite/` | A | — |
| R3 | Abrir **Pull Request** | — | **N (pendente)** | Não há PR de `arthurroleite` no upstream (checado com `gh pr list`). Abrir |
| R4 | "Use IA. Queremos ver *como* você usa" | Process log, chat export, juízes, benchmark de LLM | A | — |
| R5 | "Envie evidências do seu processo. Sem evidência = desclassificado" | `process-log/` (diário, chat export de 6.087 linhas, 3 pareceres, 5 screenshots), 9 commits com `Co-Authored-By: Claude` | A | — |
| R6 | Superar substancialmente o baseline (profundidade, julgamento, execução, criatividade) | Auditoria estatística da base (ponto que o baseline erraria), política de não automação, benchmark pareado contra LLM, travas de domínio testadas com o DS1 | A | O mérito precisa ser **atribuído corretamente** (ver G1) |
| R7 | "Saber o que pedir, quando desconfiar, o que ajustar, e o que só um humano com contexto consegue fazer" | "O que eu adicionei" no README | **P** | O export mostra que a desconfiança da base veio da IA (linhas 361 e 454). O que só o humano fez precisa ser reescrito com honestidade (G1) |
| R8 | Avaliado: "entendeu o problema antes de sair executando?" | Fase 0.3 (hipótese antes dos dados) e Fase 1 (auditoria antes do diagnóstico) | A | — |
| R9 | Avaliado: "usou IA de forma inteligente ou só deu copy-paste?" | Juiz adversarial, benchmark de 4 variantes de LLM, erros corrigidos | A | — |
| R10 | Avaliado: "o resultado resolve o problema de verdade?" | Triagem medida em 9.568 tickets; app no ar | A/P | O motor foi treinado em TI interna, não no suporte a clientes do Diretor. A ponte precisa ficar explícita (G6) |
| R11 | Avaliado: "alguém consegue entender e agir?" | Relatório com "Resposta em 1 minuto" e "O que preciso de você" | A | — |
| R12 | Time budget de 4–6 h; "40 horas não recebem pontos extras" | Tudo feito em 14/10 (process log) | P | O tempo gasto não é declarado. Declarar ajuda (G9) |
| R13 | "Vibe code uma solução funcional tem vantagem" | Streamlit no ar + scripts reproduzíveis | A | — |

### 1.2 CONTRIBUTING.md

| # | Exigência | Onde | Veredito | O que falta |
|---|---|---|---|---|
| C1 | Branch `submission/seu-nome` | `submission/arthur-leite` | A | — |
| C2 | Pasta `submissions/seu-nome` | ok | A | — |
| C3 | Commit e push na branch | 9 commits em `origin` | A | — |
| C4 | PR para `main` com título `[Submission] Seu Nome — Challenge XXX` | — | **N (pendente)** | Título exato: `[Submission] Arthur Leite — Challenge 002` (travessão "—", como nos PRs aceitos #189/#186) |
| C5 | Estrutura: `README.md` | ok | A | — |
| C6 | `solution/` | `solution/01-diagnostico`, `02-proposta-automacao`, `03-prototipo`, relatório | A | — |
| C7 | `process-log/` com `screenshots/` e `chat-exports/` | Os dois existem e estão versionados | A | — |
| C8 | `docs/` "(se houver)" | Não existe | A (opcional) | Não é obrigatório; não criar só por criar |
| C9 | Checklist: escolhi e li o README completo | Fase 0.1 | A | — |
| C10 | Checklist: solução na pasta | ok | A | — |
| C11 | Checklist: process log com evidências | ok | A | — |
| C12 | Checklist: README segue o template | Todas as seções presentes | A/P | `_Submissão enviada em: {{DATA}}_` ainda é placeholder (G2) |
| C13 | Checklist: instruções de setup se construiu código | "Como rodar" (local + Cloud + reprodução) | A | Após o redesign do app pelo Agente 1, reverificar se os comandos continuam válidos |
| C14 | Checklist: não modifiquei nada fora da minha pasta | `git diff --name-only upstream/main...HEAD` → **0 arquivos fora** de `submissions/arthur-leite/` (43 arquivos, +10.644 linhas) | A | Manter. **Atenção:** o `.gitignore` da raiz ignora `submissions/`, então todo arquivo novo (inclusive esta pasta `agentes/`) exige `git add -f` |
| C15 | Um PR por pessoa; atualizar com push na mesma branch | — | — | Abrir um PR só e não fechar e reabrir |
| C16 | Dados e segredos fora do repo | `data/` e `.env` ignorados pelo `.gitignore` da submissão; só `.env.example` versionado | A | — |

### 1.3 Submission guide

| # | Exigência / frase | Onde | Veredito | O que falta |
|---|---|---|---|---|
| S1 | Parte 1: a solução | `solution/` | A | — |
| S2 | Parte 2: process log obrigatório | `process-log/` | A | — |
| S3 | Formatos: screenshots | 5 screenshots do protótipo | A/P | São do app, não das **conversas com a IA** (o guia cita "prints das conversas com AI"). O chat export compensa. Depois do redesign, os prints ficam desatualizados: refazer (G8) |
| S4 | Screen recording | — | N (opcional) | Um Loom de 2–3 min do app aumenta a força do "me mostre que funciona" (G10) |
| S5 | Chat export | `conversa_claude_code.md` | A | Ver G1: ele expõe a atribuição |
| S6 | Narrativa escrita | `PROCESS_LOG.md` | A/P | Voz mista: parte em 1ª pessoa da IA, que fala "do Arthur" (G1) |
| S7 | Git history | 9 commits por fase | A | — |
| S8 | **Quais ferramentas e por quê** | Tabela no README e Fase 0.4 (Gemini por falta de chave Anthropic; LLM local inviável) | A | O "porquê" de cada ferramenta está espalhado; a tabela do README só diz "para quê" |
| S9 | **Como decompôs antes de promptar** | Fase 1 "Como decompus" (4 perguntas) e Abordagem | P | A decomposição registrada é a da IA (msg de arquitetura, linha 454 do export). A única instrução estrutural do candidato é a msg 8 ("toda conclusão passa por um juiz"). Ver G1 |
| S10 | **Onde a IA errou e como corrigiu** | Tabela com 13 linhas no README, coluna "Quem pegou" | A | Excelente. Mas há 2 linhas "Eu, ao ler a tabela" e "Eu, ao reler" que o export indica terem sido pegas pela própria IA (linha 1690: o comentário de código é da IA). Corrigir a coluna (G1) |
| S11 | **O que você adicionou que a IA sozinha não faria** | Seção no README | **P** | 2 dos 4 itens ("desconfiar da base", "escolher ROI menor") foram propostos pela IA ou pelo juiz. O item genuíno e forte é a **exigência de revisão adversarial** (msg 8). Reescrever (G1) |
| S12 | **Quantas iterações** | Implícito (fases, 3 pareceres, tabelas de antes × depois) | P | Não há contagem explícita. Adicionar uma linha: "N mensagens minhas, 3 rodadas de juiz, X versões do ROI, 2 deploys" (G5) |
| S13 | Formato sugerido: executive summary de 1 parágrafo | 4 parágrafos curtos (~8 frases) | P | O template pede 3–5 frases. Enxugar (G9) |
| S14 | Abordagem / Resultado / Recomendações / Limitações | Todas presentes | A | — |
| S15 | Forte: entendeu o problema antes | Auditoria antes do diagnóstico | A | — |
| S16 | Forte: IA estratégica, não "Google glorificado" | Juiz, benchmark, travas | A | — |
| S17 | Forte: output acionável amanhã | Piloto de 4 semanas com critérios para avançar; "O que preciso de você" | A | — |
| S18 | Forte: process log com iteração e julgamento | Sim | A | — |
| S19 | Forte: técnico e não técnico entendem | Relatório | A/P | Jargão restante no relatório: "IC", "p = 0,0003", "McNemar" no README, "RAG" implícito. Uma nota de rodapé de 1 linha resolve |
| S20 | Fraca: output genérico | Específico (tickets reais citados, #36521 etc.) | A (evitado) | — |
| S21 | Fraca: zero verificação | Juiz recalcula do zero; IC por bootstrap | A (evitado) | — |
| S22 | Fraca: 1 prompt → 1 resposta → submissão | — | **Risco** | O export tem **13 mensagens do candidato**, quase todas logísticas (chave de API, fork, deploy). Lido com má vontade, parece "1 pedido → a IA fez tudo". Mitigação no G1 |
| S23 | Fraca: parecer inteligente em vez de resolver | Resolve: app, piloto, decisão pedida | A | — |
| S24 | Fraca: 40 páginas onde 5 resolveriam | README 175 linhas, relatório 6 págs, proposta 138 linhas | A/P | Há redundância (as mesmas tabelas em README, relatório e proposta). O caminho de leitura para o avaliador está claro. Não alongar mais nada: tudo o que entrar deve substituir algo |

### 1.4 Template de submissão (item a item)

| Item do template | Presente? | Veredito | Observação |
|---|---|---|---|
| Título "Submissão — [Nome] — Challenge [XXX]" | "Submissão — Arthur Leite — Challenge 002" | A | — |
| Sobre mim: Nome | ok | A | — |
| Sobre mim: LinkedIn | ok | A | — |
| Sobre mim: Challenge | ok | A | — |
| Executive Summary (3–5 frases) | ok, longo | P | ~8 frases |
| Solução → Abordagem | 6 passos | A | — |
| Solução → Resultados / Findings | Tabelas | A | — |
| Solução → Recomendações (priorizadas) | 5 itens em ordem | A | — |
| Solução → Limitações | 6 itens | A | — |
| Process Log → Ferramentas usadas (tabela) | ok | A | Falta "por quê" em algumas linhas |
| Process Log → Workflow (passo a passo; "onde a IA entrou em cada etapa?") | 7 passos | **P** | Os passos não dizem **quem fez o quê** em cada etapa. É exatamente a pergunta do template e da vaga (G1) |
| Process Log → Onde a IA errou e como corrigi | Tabela | A/P | Corrigir a atribuição "Eu" (G1) |
| Process Log → O que eu adicionei | 4 itens | P | G1 |
| Evidências: checkboxes | 6 marcados | A | Screen recording não marcado (opcional) |
| "Submissão enviada em: [data]" | `{{DATA}}` | **N** | Preencher (G2) |

### 1.5 Challenge 002: o que entregar

| # | Exigência | Onde | Veredito | O que falta |
|---|---|---|---|---|
| D1 | **Onde o fluxo trava?** Gargalos por canal, prioridade e tipo; piores combinações | `auditoria.md` §4b (3 piores e 3 melhores de 80, IC, permutação p = 0,68); relatório §1 | A | Resposta literal + prova de ruído. Mantém o "não dá para afirmar" sem parecer fuga. **Não deixar o redesign do app esconder isso** |
| D2 | **O que impacta a satisfação?** | `auditoria.md` §4 (10 testes, Bonferroni, poder = 0,21 ponto) | A | — |
| D3a | **Quanto desperdiçamos, em horas** | `modelo_desperdicio.md`: 750 / 1.500 / 2.500 h/ano de triagem; 552 / 1.218 / 2.106 h/ano liberadas | A/P | Só em **h/ano**. O case pede "Y horas/**mês**" (dica de ROI). Ver G3 |
| D3b | **…e estime custo** | R$ 21 / 47 / 81 mil/ano, custo/hora com fonte | A | — |
| D3c | **"Onde está o maior desperdício recuperável?"** | Só implícito ("tempo de espera na fila errada, provavelmente o maior ganho", sem número) | **P** | Não há uma frase que responda à pergunta com essas palavras. O juiz final já apontou ("Parcial") e isso não foi corrigido. Ver G4 |
| D4 | **O que automatizar** (classificação, roteamento, sugestões, triagem de prioridade, duplicatas) | `proposta.md` §1: classificação/roteamento em 3 faixas, sugestão top-2, rascunho, urgência sobe prioridade | A | Duplicatas não são tratadas; o kNN de "3 tickets parecidos" já é o alicerce. Uma linha "detecção de duplicatas: fora do escopo, porque ..." fecharia o item |
| D5 | **O que NÃO automatizar**, "justifique com exemplos dos dados" | `proposta.md` §2: 6 regras com frequência + 4 tickets reais (#36521, #5461, #31874, #8682) | A | Ponto mais forte da entrega |
| D6 | **Como funcionaria na prática** (entra → etapas → onde a IA atua → onde o humano intervém) | `proposta.md` §3, diagrama com [IA]/[humano] e "onde o humano intervém: 100% / 34,5% / 100%" | A | — |
| D7 | Protótipo funcional (diferencial) | App Streamlit no ar, 5 abas: Triagem ao vivo, Fila de teste, Diagnóstico, ROI, Como funciona | A | Reverificar após o redesign (ver §3) |
| D8 | Process log | ok | A/P | G1 |

### 1.6 Challenge 002: critérios de qualidade

| # | Critério | Onde | Veredito | O que falta |
|---|---|---|---|---|
| Q1 | **Usou ambos os datasets?** ("o poder está no cruzamento") | DS1 = auditoria + estrutura da operação + **teste fora do domínio que calibra as travas** (34% → 11%); DS2 = treino e prova. Parágrafo explícito no topo da proposta | A/P | O cruzamento é inteligente, mas **defensivo**: o DS1 entra como "o que a IA não deve decidir", nunca como a operação do Diretor. Falta a ponte de produto (G6) |
| Q2 | Diagnóstico com números concretos ou genérico? | Muitos números com p-valor e IC | A | — |
| Q3 | Automação realista? ("100% é red flag") | 65,5% auto, 34,5% com humano no roteamento, 27,7% com ação humana obrigatória, piloto em modo sombra | A | — |
| Q4 | Distingue onde a IA ajuda de onde o humano é insubstituível? | "Rotear ≠ executar ≠ responder" + 6 regras + LGPD | A | — |
| Q5 | Protótipo com dados reais, não 3 exemplos escolhidos a dedo? | Aba "Fila de teste" com os 9.568 tickets de teste por padrão; matriz de confusão; screenshot 04 | A | **Requisito para o Agente 1:** manter o padrão = conjunto de teste inteiro e os números batendo com o README (65,5 / 23,3 / 11,2) |

### 1.7 Challenge 002: dicas

| # | Dica | Onde | Veredito | O que falta |
|---|---|---|---|---|
| T1 | DS2 com 48K textos em 8 categorias, "excelente para treinar/testar classificadores" | Benchmark completo + motor final | A | — |
| T2 | "Classificar tickets em 8 categorias com 92% de acurácia usando embeddings + zero-shot" é específico | "TF-IDF + regressão logística: 86,0% no teste (F1-macro 0,86); faixa automática 96,4% em 65,5%; embeddings 78–81%; zero-shot 44%" | A | Mais específico que o exemplo, e mostra que o caminho sugerido (embeddings + zero-shot) **perde**. Isso é julgamento, mas precisa ser apresentado como escolha deliberada, não como "não usamos IA generativa" (G7) |
| T3 | "Pense no agente de suporte: o que facilitaria a vida dele?" | `proposta.md` §1.3 "Copiloto, não piloto": palavras que levaram à decisão, 3 tickets parecidos, rascunho; escolha com 1 clique | A/P | Falta o "dia do agente" em linguagem de agente: o que ele deixa de fazer e o que passa a fazer. E falta o **ciclo de feedback visível** (o agente corrige → vira retreino) no protótipo. Ver G7/§3 |
| T4 | "ROI: automação X economiza Y horas/**mês**" | Tudo em **h/ano** | **P** | Converter: base ≈ **101 h/mês**; faixa ≈ **46 a 176 h/mês** (G3) |
| T5 | "Cuidado com a armadilha de automatizar tudo; os melhores sabem onde parar" | Política, travas, faixas, modo sombra, "não fechar tickets", "não enviar resposta sem revisão" | A | — |

### 1.8 Verificações específicas pedidas pelo orquestrador

| Verificação | Resultado |
|---|---|
| 3 perguntas do diagnóstico | Trava: **A** · Satisfação: **A** · Desperdício: horas e custo **A**; "maior desperdício recuperável" **P**; unidade mensal **P** |
| O que automatizar / o que não / como funciona | A / A (com exemplos reais) / A |
| Usou ambos os datasets? | A/P (cruzamento real, mas a ponte com a operação do Diretor está fraca) |
| Protótipo com dados reais? | A (fila com 9.568 tickets de teste). Manter após o redesign |
| Process log: ferramentas e porquê | A |
| Process log: decomposição antes de promptar | P (a decomposição registrada é da IA) |
| Process log: onde a IA errou | A (13 erros documentados), com atribuição a corrigir |
| Process log: o que adicionou | P (G1) |
| Process log: quantas iterações | P (não declarado em número) |
| README segue o template | A, exceto `{{DATA}}` |
| Estrutura de pastas | A (`docs/` é opcional e ausente) |
| Título do PR | **PR não aberto**. Título a usar: `[Submission] Arthur Leite — Challenge 002` |
| Só arquivos na pasta | **A**: 0 arquivos fora de `submissions/arthur-leite/` |
| Papel do candidato × papel da IA | **P/N, o gap mais grave** (G1) |
| Concisão | A/P (sem excesso, com redundância entre documentos) |

---

## 2. As 5 frentes da vaga e os critérios eliminatórios

### 2.1 Frentes

| Frente | Evidência | Força | Onde está fraca |
|---|---|---|---|
| **1. Mapeamento** (problema certo; oportunidade × ruído) | Auditoria provando que o DS1 é ruído; "o 1º gargalo é de medição"; plano de instrumentação | **Forte** | — |
| **2. Orquestração técnica** (LLMs, RAG, agentes, integrações, pipelines) | Benchmark TF-IDF × embeddings × kNN × LLM (zero-shot, few-shot, RAG, modelo forte); LLM para rascunho; subagentes juízes; pipeline reproduzível; deploy | **Média** | (a) **Não há arquitetura de integração**: como o motor se pluga no helpdesk (webhook/API → classificar → escrever a fila/tag de volta → logar a correção). (b) "Agentes" aparecem só no processo (juízes), não no produto. (c) A orquestração multiagente usada para construir e revisar a própria entrega (juízes e este time de 5 agentes) é uma evidência forte que está subnarrada |
| **3. Entrega end-to-end** | App no ar, scripts reproduzíveis, reprodução a frio pelo juiz, bug do pandas 3 corrigido | **Forte** | Depende de o redesign não quebrar o deploy (reteste a frio obrigatório) |
| **4. Suporte, sustentação, melhoria contínua** (monitorar, ajustar, treinar o time, adoção) | Retreino mensal; concordância como sinal de deriva; métricas do piloto; donos das regras | **Fraca** | Faltam: (a) **painel de monitoramento** com indicadores e gatilhos (concordância na faixa auto < 95% por 2 semanas → volta a sugestão; taxa de override por categoria; % fora do domínio subindo → investigar); (b) **plano de treinamento e adoção do time** (quem treina os agentes, em quê, como medir o uso do rascunho e da sugestão); (c) **kill switch / rollback**; (d) dono do modelo (RACI) |
| **5. Comunicação executiva** (C-level decide em 5 min) | "Resposta em 1 minuto"; "O que preciso de você" com 3 decisões; limitações honestas | **Forte** | Relatório com 6 págs (ok); jargão residual; ROI anual quando o Diretor pensa em mês |

### 2.2 Critérios eliminatórios

| Critério | Veredito | Comentário |
|---|---|---|
| Execução com resultados quantificáveis | A | 96,4% com IC; 65,5% de cobertura; 34% → 11%; ROI em faixas |
| Uso avançado de IA generativa (agentes, RAG, integrações, pipelines) | **P** | RAG e LLM foram testados e **perderam**: decisão correta, mas o leitor apressado lê "o produto não usa GenAI". A IA generativa no produto se limita ao rascunho opcional. O uso avançado real está no processo (agentes juízes, time de 5 agentes) e não é vendido como tal. Ver G7 |
| Raciocínio estruturado de negócio | A | Piloto com critérios de avanço; ROI bruto × caixa; custo assimétrico |
| Perfil analítico (dados/SQL/Python) | A | Testes, permutação, McNemar, bootstrap, poder estatístico |
| Comunicação executiva | A | — |
| Autonomia / ownership | **P (risco)** | No export, o candidato aparece fazendo 13 pedidos, majoritariamente logísticos. O ownership real (exigir o juiz, decidir o piloto, revisar) precisa estar documentado com as decisões dele, com data |

---

## 3. O que o app precisa conter (para o Agente 1)

Requisitos funcionais derivados do enunciado e dos documentos. Sem eles, a narrativa e o app se contradizem:

1. **Triagem ao vivo:** categoria + confiança + faixa (auto/sugestão/humano), **palavras que pesaram**, **3 tickets parecidos**, política aplicada (ex.: phishing → Segurança, sobrepondo o classificador), trava de domínio (texto em português ou fora do tema → humano) e rascunho por LLM opcional (o app funciona sem a chave).
2. **Fila de teste:** padrão = **9.568 tickets** do teste, com os números 65,5 / 23,3 / 11,2 e 96,4% iguais aos do README; matriz de confusão; decomposição da faixa humana (9,7 + 1,5).
3. **Diagnóstico:** as 3 perguntas do Diretor com a resposta literal (inclusive as piores combinações + permutação p = 0,68).
4. **ROI:** premissas ajustáveis; **mostrar h/mês e h/ano**, FTE e R$; deixar claro que é tempo bruto liberado.
5. **Selo "IA × humano" por ticket** (quem decide o quê) e um botão "corrigir categoria" que grava a correção para retreino. Isso demonstra a frente 4 (melhoria contínua) com custo baixo.
6. (Desejável) **Aba ou bloco de monitoramento** com taxa de override, concordância na faixa auto e % fora do domínio, mesmo que simulados sobre o conjunto de teste e rotulados como tal.
7. Depois do redesign: **reteste a frio** (venv limpo com as versões do Streamlit Cloud) e **refazer os 5 screenshots**.

---

## 4. Gaps priorizados com a correção sugerida

### G1 (P0, crítico): atribuição "papel do candidato × papel da IA" não é fiel ao chat export

**Evidência.**
- README, "O que eu adicionei", item 1: "Desconfiar da base antes de analisar". No export, quem propõe é a IA (linha 361: "os datasets do Kaggle são sintéticos..."; linha 454: "Suspeito que tenha uns 8,5 mil tickets..."). O PROCESS_LOG 0.3 diz "levantei a suspeita" sem dizer quem.
- README, tabela de erros: "Faixa 'sugere' com 60%… Quem pegou: **Eu**, ao ler a tabela" e "IC se sobrepõem… **Eu**, ao reler". No PROCESS_LOG, o mesmo erro aparece na voz da IA ("Eu usava a precisão acumulada... Corrigi").
- PROCESS_LOG mistura narradores: "Decisão (pendente de validação **com o Arthur**)", "pedido **do Arthur**", "eu cheguei a dizer isso **ao Arthur**", "Ele estava na minha mensagem **ao Arthur**". O título diz "Process Log — Arthur Leite" e "Diário de trabalho": o leitor não sabe quem é "eu".
- O export tem 13 mensagens do candidato. A mais substantiva é a msg 8 (exigir um juiz para toda conclusão). As demais tratam de chave, fork e deploy.

**Por que é grave:** a vaga pede literalmente "demonstre com clareza qual foi o seu papel e qual foi o papel da IA". Uma atribuição inflada e verificável no próprio repo é pior que uma atribuição modesta: derruba a credibilidade do resto, numa entrega cujo diferencial é o rigor.

**Correção.**
1. No README, trocar a tabela "Ferramentas" + "Workflow" por um bloco **"Quem fez o quê"** e ajustar a coluna "Quem pegou" (usar "IA (autocorreção)", "Juiz (IA)" e "Arthur" só onde houver registro):

```markdown
### Quem fez o quê

| Etapa | Arthur (decisão e governança) | IA (execução) |
|---|---|---|
| Escopo | Escolhi o 002 a partir da recomendação da IA, pelo encaixe com a minha operação de agentes de atendimento em produção (Mavra) | Leu a vaga e o repo inteiro; comparou os 4 cases |
| Restrições | Sem chave da Anthropic: decidi usar o Gemini gratuito, com o LLM opcional e o app rodando sem chave | Avaliou alternativas (LLM local inviável) |
| Rigor | **Exigi que toda conclusão passasse por um agente juiz independente** antes de entrar na entrega. Esse protocolo derrubou o "backlog de 67%", o ROI inflado e o bug do pandas 3 | Desenhou o protocolo; os subagentes recalcularam tudo do zero |
| Análise | Validei o enquadramento "o 1º gargalo é de medição" e a política do que não automatizar | Levantou a hipótese da base sintética, escreveu os testes, o benchmark e o motor |
| Produto | Defini as regras de negócio a partir da operação real (rotear ≠ executar ≠ responder; humano em aprovação, desligamento e saúde) | Implementou o motor, a política e o app |
| Entrega | Fiz o deploy, testei o app, revisei os documentos e coordenei a revisão final com 5 agentes especializados | Escreveu o código e os rascunhos dos documentos |
```

> Ajustar cada célula ao que é **verdade**. Exemplo: se a regra "rotear ≠ executar ≠ responder" veio da IA (linha 2615 do export) e não do Arthur, escrever "validei e calibrei", não "defini".

2. No PROCESS_LOG, adicionar uma nota no topo: "**Convenção:** este diário foi redigido pelo Claude Code durante o trabalho, sob minha direção. 'Eu' nas entradas técnicas = a IA; minhas decisões aparecem marcadas como **Decisão do Arthur**." Isso é honesto e transforma o problema em evidência de método.
3. Reescrever "O que eu adicionei que a IA sozinha não faria" com o que é demonstrável: (a) exigir revisão adversarial em toda conclusão (msg 8, citar a linha 1354 do export); (b) contexto de operação real para validar a política; (c) restrições de produto (rodar sem chave, sem dado sensível no LLM); (d) a orquestração do time de revisão final; (e) a decisão de apresentar um ROI menor e defensável, **se** essa decisão foi dele.
4. Recomendação forte: o Arthur **acrescentar 2 ou 3 verificações próprias, feitas à mão e registradas** (ex.: leu 30 tickets da faixa automática e concordou com X; testou um caso real da Mavra no app). É o que transforma "governança" em "julgamento demonstrado".

### G2 (P0, rápido): PR não aberto e placeholder no README
- Preencher `_Submissão enviada em: {{DATA}}_` → `_Submissão enviada em: 14/10/2026_` (ou a data real do PR).
- Abrir o PR: base `Gestao-Quatro-Ponto-Zero/ai-master-challenge:main` ← `arthurroleite:submission/arthur-leite`, título **`[Submission] Arthur Leite — Challenge 002`**. Corpo curto: link do app, link do relatório, 3 bullets de achados e "Quem fez o quê".
- Antes do push final: `git diff --name-only upstream/main...HEAD | grep -v '^submissions/arthur-leite/'` deve sair vazio. Novos arquivos exigem `git add -f`.

### G3 (P1): ROI em h/mês, como pede a dica do Diretor
Hoje está só em h/ano. Sugestão de texto (README, relatório §5, proposta §5, `modelo_desperdicio.md`, aba ROI):

> **A triagem com IA libera ~100 horas de agente por mês no cenário base** (≈ 1.218 h/ano; faixa de 46 a 176 h/mês), o equivalente a 0,7 pessoa, ≈ R$ 3,9 mil/mês. Tempo bruto liberado, a confirmar no piloto.

Conta: 552/12 = 46; 1.218/12 = 101,5; 2.106/12 = 175,5; R$ 46.563/12 ≈ R$ 3.880. Na headline do relatório, usar o mês; o ano pode ficar entre parênteses.

### G4 (P1): "Onde está o maior desperdício recuperável?" sem resposta explícita
O juiz final marcou "Parcial" e isso não foi corrigido. Inserir em `modelo_desperdicio.md` ("Resposta curta"), no relatório §1 ou §5 e no README (linha "Quanto estamos desperdiçando?"):

> **Maior desperdício recuperável hoje:** a triagem manual. Ela consome ~1.500 h/ano (≈ 125 h/mês) no cenário base, e a IA recupera ~80% disso (≈ 100 h/mês). O desperdício **provavelmente maior**, o tempo do cliente parado em fila errada, não é mensurável com estes dados; a instrumentação da semana 0 existe para medi-lo em 30 dias.

### G5 (P1): iterações não quantificadas
Adicionar ao Workflow do README uma linha como: "**Iterações:** N mensagens minhas na sessão; 3 rodadas de juiz (fases 1, 3 e 5) + revisão final com 5 agentes; 13 erros corrigidos; ROI em 2 versões (1.496 → 1.218 h/ano); motor em 3 versões (limiar global → por categoria → travas de domínio); 2 deploys." Conferir os números reais antes.

### G6 (P1): ponte entre o motor (TI interna) e a operação do Diretor (suporte a clientes)
O Diretor opera Billing, Refund, Technical, Product e Cancellation; o motor roteia Hardware, HR Support... As limitações dizem "retreina", mas não mostram como fica **na operação dele**. Adicionar à proposta (§1 ou §4) e ao relatório §2, uma ou duas frases:

> **Na sua operação**, as filas viram os 5 tipos do seu sistema (Billing, Refund, Technical, Product, Cancellation) e os canais Email/Chat/Phone/Social. O método é o mesmo: retreino no seu histórico rotulado (minutos, em CPU), limiar por fila calibrado para ≥ 95% e as mesmas travas. O DS1 não serve para treinar porque o texto é sintético: o classificador fica abaixo do chute (19,5% × 20,7% no tipo). Por isso a prova foi feita no DS2, que é real.

### G7 (P2): reforçar orquestração, IA generativa e sustentação (frentes 2 e 4 da vaga)
Um bloco curto na proposta ("Operação contínua"), de ~10 linhas, sem alongar o resto:
- **Integração:** webhook do helpdesk (Zendesk/Freshdesk/HubSpot) → serviço `/triagem` (o motor atual + a política) → escreve fila, tags e faixa no ticket → a correção do agente volta por webhook e vira um rótulo de retreino. O LLM entra só no rascunho, atrás de um filtro de política (saúde e segurança nunca saem).
- **Monitoramento semanal:** concordância na faixa auto (gatilho: < 95% por 2 semanas → a categoria volta para a sugestão); taxa de override por categoria; % barrado pela trava de domínio (subida = assunto novo → rotular e retreinar); uso e edição do rascunho.
- **Adoção e treinamento do time:** sessão de 1 h com os agentes antes do modo sombra (como ler a faixa, contestar a IA e corrigir com 1 clique); um ponto focal por turno; a métrica de adoção é o % de tickets com a sugestão aceita ou corrigida.
- **Kill switch:** desligar a faixa automática por categoria, sem deploy.
- **Dono:** o AI Master é o dono do modelo; Segurança, RH e Financeiro são donos das regras.
- No README, renomear a frase da IA generativa para enfatizar a **escolha**: "Testei GenAI em 4 configurações (zero-shot, few-shot, RAG, modelo mais forte); ela perdeu na classificação e ganhou na redação, e foi para onde ganha." Citar a orquestração multiagente (juízes + time de revisão) como uso avançado de agentes.

### G8 (P2): screenshots e app após o redesign
Refazer os 5 screenshots com o app novo; garantir que os números da tela batam com o README; retestar a frio (venv limpo, pandas 3) e repetir o smoke test no Streamlit Cloud. Se o app ganhar abas, citar no README o que cada uma prova.

### G9 (P3): concisão e acabamento
- Executive Summary: reduzir para 5 frases. Proposta:
  > A base de métricas do suporte (Dataset 1) é sintética: tempos impossíveis, satisfação aleatória e nenhuma combinação de canal × prioridade × tipo distinguível do acaso. O primeiro gargalo é de medição. Nos 48 mil tickets reais do Dataset 2, uma triagem com três faixas de confiança roteia sozinha 65,5% dos tickets com 96,4% de acerto, sugere 2 opções em 23,3% e envia 11,2% a humanos. Ações sensíveis e respostas nunca são automatizadas. Um classificador treinado no histórico superou o LLM em todas as configurações testadas, e o LLM ficou onde agrega: redigir rascunhos. Ganho estimado de ~100 h/mês de agente (46 a 176), a confirmar em 4 semanas de piloto em modo sombra.
- Declarar o tempo investido (ex.: "~X h em 1 dia, incluindo deploy"), alinhado ao time budget de 4–6 h.
- Relatório: substituir "p = 0,0003" por "diferença estatisticamente significativa" (o p fica no rodapé) e explicar "RAG" na primeira menção.
- Pequena inconsistência: o PROCESS_LOG diz "8,1% são escalados" e o `motor_final.md` diz "7,9%" (base diferente). Indicar a base ou unificar.

### G10 (P3): evidência opcional que eleva a barra
- Um screen recording de 2–3 min (Loom) mostrando o phishing escalado, o português barrado e a fila de 9.568, linkado no README e no PR.
- Versionar um resumo dos relatórios deste time de 5 agentes em `process-log/agentes/` (com `git add -f`), citado no README como "revisão final multiagente orquestrada por mim". Isso conta a favor das frentes 2 e 4 e do ownership.

---

## 5. Resumo do que **não** mexer

- A auditoria da base sintética, a tabela das piores combinações com permutação, a política com os 4 tickets reais, o benchmark contra LLM com McNemar, a decomposição 9,7 + 1,5 e a tabela de erros: tudo isso está acima do baseline e reproduz.
- Não acrescentar documentos novos de peso. Cada adição acima é de 1 frase a 10 linhas e, sempre que possível, substitui texto existente.
