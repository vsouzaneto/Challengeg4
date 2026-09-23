# Sessão 7 — Entrega 2: fork 2

> Export da sessão do Claude Code (app desktop), de 23/09/2026 13:39 a 23/09/2026 13:39 (UTC). Conversão para leitura: ficam os prompts do Rafael, as respostas da IA, as perguntas de múltipla escolha com a resposta escolhida e uma linha por ação da IA. Foram removidos o raciocínio interno, a saída bruta das ferramentas, os lembretes de sistema, e-mails e chaves.


---

### 👤 Rafael

certo e agora qual proximo passo ?

- `Bash`: Check state of new worktree vs previous

- `Bash`: Read submission guide requirements

### 🤖 Claude

O próximo passo é a **Entrega 3, o protótipo**. O Diretor pediu "quero ver algo rodando", e hoje isso é o que falta. Antes dela, porém, há um risco para resolver: a Entrega 2 inteira ainda não foi salva no git.

## 1. Primeiro: salvar a Entrega 2 (urgente, 5 min)

Esta worktree nova começou de novo da Fase 1. Tudo da Entrega 2 e do aprofundamento está **sem commit** na worktree `adoring-golick-e2b20d`: a proposta, o harness, a economia, os 3 scripts e o process log 03. Se aquela worktree for limpa, o trabalho se perde. Cada sessão nova também começa sem ele.

Proposta: commitar lá com `git add -f` (a raiz ignora `submissions/`) na branch da submissão, e trazer para cá antes de começar a Entrega 3.

## 2. Entrega 3: o protótipo

Tudo o que ele precisa já existe como código testado; falta juntar numa coisa que roda na frente do Diretor.

**Proposta de escopo:** uma aplicação local em que o Diretor cola um ticket, ou escolhe um real dos datasets, e vê o fluxo inteiro acontecer:
- normalização, duplicata, classe com confiança, gatilhos de risco, prioridade e SLA;
- a rota (1A, 1B, 2 ou 3) **com o motivo de cada decisão**;
- para a rota 3, o template de coleta de dados; para as rotas 1 e 2, o rascunho e o dossiê.

Uma segunda tela seria o painel da operação, rodando sobre os 8.469 tickets reais: rotas, backlog repriorizado, monitor de devoluções e as métricas de aprendizado.

**A decisão que depende de você: a LLM.** Hoje ela não foi medida (não há chave de API neste ambiente), e esse é o maior buraco que o harness apontou.

| Opção | O que muda |
|---|---|
| **Com chave da API Anthropic** | Rascunho e dossiê reais. E rodamos o critério que a proposta exige: a LLM rotula 500 tickets e medimos o acerto contra o rótulo humano (meta ≥ 90%). Isso fecha a maior lacuna com número |
| **Sem chave** | O protótipo roda completo na parte determinística e no modelo supervisionado. O rascunho sai de templates da base de conhecimento, marcado como "simulado" |

## 3. Fechar a submissão (Entrega 4 + PR)

- **README final** no template, preenchendo o LinkedIn e o que mais está pendente.
- **Evidências do process log:** o guia aceita narrativa escrita (já temos 3), mas prints ou export do chat fortalecem. Faltam em `process-log/chat-exports/`.
- **Um resumo curto para o Diretor.** O guia pune "documento de 40 páginas onde 5 resolveriam", e já temos 7 documentos. Uma página com as três respostas (onde perde tempo, o que automatizar, o que está rodando), apontando para os detalhes, protege contra isso.
- **PR**, que é o único canal aceito.

## Minha recomendação de ordem

1 → 2 → 3. Começo pelo commit agora, se você aprovar. Para o protótipo, duas perguntas:
- Você tem uma chave da API Anthropic para usarmos?
- Prefere a interface em **Streamlit** (rápido, em Python, reaproveita os scripts) ou em **HTML** publicável como link?

