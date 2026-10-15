# Do desafio à entrega: o fluxo completo do case 003 (Lead Scorer)

> **Rascunho para eu revisar. Nada foi publicado.** Este documento conta, em linguagem simples, como o desafio do G4 foi tratado de ponta a ponta por mim e pelos agentes de IA: o que foi pedido, quem fez o quê, o que deu errado, como foi corrigido e o que pode (e o que não pode) ser afirmado sobre o resultado. Cada afirmação aponta para uma evidência que qualquer pessoa pode conferir.

Estado das tarefas consultado em **13/10/2026**, depois das 12:22. Horários em Brasília (UTC−3).

---

## 1. Em um minuto

- **O desafio.** O G4 AI Master Challenge pede uma solução real para um de quatro problemas de negócio e, junto, a prova de *como* a IA foi usada. Sem essa prova, a submissão é desclassificada.
- **O case escolhido.** O 003, *Lead Scorer*: um vendedor abre o pipeline e precisa decidir em qual oportunidade agir primeiro.
- **O que construímos.** Um aplicativo local chamado **Foco**. Ele separa as 2.089 oportunidades abertas em três filas (**Avançar**, **Revisar**, **Qualificar**), mostra o motivo de cada posição e sugere a próxima ação.
- **O método.** Cada etapa registrada no quadro virou uma tarefa com objetivo, responsável, critério de aceite e revisão por *outro* agente. Quem aprovava era eu. (A construção do primeiro produto, em 09/10, é a tarefa `G4-LEAD-SCORER-01`. Ela existe no quadro, com revisão e aprovação, mas a ficha foi registrada em outro agrupamento, antes de o projeto G4 existir, e por isso não entrou na exportação do projeto G4; ver [`processo-no-demiurgo.md`](processo-no-demiurgo.md).)
- **O achado mais honesto.** A primeira ideia, prever fechamento a partir do histórico, **não funcionou** (AUC 0,4854, praticamente sorteio). Em vez de vender uma previsão, o Foco usa uma regra simples e transparente, e diz isso na própria tela.

---

## 2. O desafio e as regras

O repositório público do G4 reúne quatro cases: 001 Churn, 002 Suporte, 003 Lead Scorer e 004 Social Media. Regras que valeram para este trabalho:

| Regra | Onde está |
| --- | --- |
| Usar IA é esperado, e a **evidência do processo é obrigatória** | [Guia de submissão](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/submission-guide.md) |
| A entrega é por *pull request* (fork, branch, pasta própria) | [CONTRIBUTING](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/CONTRIBUTING.md) |
| Sugestão de 4 a 6 horas por case; preferem um case bem feito a dois superficiais | README do desafio e plano de esforço (etapa 2) |
| O brief do case 003 | [Brief oficial](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/challenges/build-003-lead-scorer/README.md) |

Fork, push e pull request são feitos **somente por mim**. Nenhum agente fez isso.

---

## 3. Quem fez o quê

Eu trabalho com um conjunto de agentes dentro do **Demiurgo**, uma aplicação local minha que organiza as tarefas, a documentação e os testes em um quadro (a página [`processo-no-demiurgo.md`](processo-no-demiurgo.md) mostra o quadro do G4). A construção foi feita junto: eu e os agentes.

| Parte | Papel neste trabalho |
| --- | --- |
| **Eu** | Escolhi o case, defini o que precisava funcionar, usei o produto, corrigi o rumo e aprovei cada tarefa. |
| **Demiurgo** | Quadro de tarefas onde cada passo tem objetivo, critério de aceite, responsável, revisão e aprovação. Guarda o histórico que esta vitrine usa. |
| **Claude Code** | Levantamento do desafio, desenho (brief) do plano de esforço, revisões cruzadas da construção, dos painéis e do redesign, documentação completa, integração da documentação e esta vitrine. |
| **Codex** | Auditoria dos dados, hipótese histórica, regra e interface do Foco (`G4-LEAD-SCORER-01`), painéis e redesign; revisão do levantamento e, em 13/10, da documentação; publicação do plano de esforço numa sessão comigo. |
| **Modelo local** | Primeiro rascunho de documentação, recusado (etapa 6). |

Regra do método: **quem faz não revisa o próprio trabalho**. Codex revisou o que Claude Code fez e vice-versa, e a aprovação final é minha. Duas exceções ficam declaradas: o plano de esforço (`G4-ESFORCO-01`) não tem revisão cruzada registrada, e esta vitrine não passa por revisão do Codex, porque eu decidi pular essa revisão e leio e aprovo direto.

---

## 4. O fluxo em sete etapas

### Etapa 1. Levantamento: ler tudo antes de escolher (`G4-RECON-01`)

**O que aconteceu.** Em 08/10, Claude Code leu o repositório público do desafio, sem fork, sem login e sem baixar dados. Montou uma ficha por case (problema, dados, o que entregar, critérios de qualidade, risco de ficar igual ao baseline), um resumo das regras de submissão e uma tabela comparando os quatro.

**Revisão.** O Codex revisou em seguida e corrigiu três pontos na própria cópia: uma resposta do FAQ que permitia mais de um case, um protótipo opcional do case 002 que faltava na tabela e uma afirmação sobre o dataset que não tinha fonte.

**Achado útil.** O repositório do G4 ignora a pasta `submissions/` no `.gitignore`; no fork será preciso `git add -f`.

| Item | Evidência |
| --- | --- |
| Tarefa concluída | `G4-RECON-01`, aprovada por mim em 09/10 às 00:09 |
| Revisão cruzada | Codex, veredito "aprovado" (08/10, 13:09 a 13:14) |
| Limite declarado | A revisão não pôde executar `node` no ambiente; o documento ficou escrito, mas não publicado na hora. Está dito na evidência da tarefa. |

### Etapa 2. Esforço e escolha (`G4-ESFORCO-01`)

**O que aconteceu.** Antes de escolher, eu pedi, em minhas palavras: "tamanho, horas, tarefas, complexidade, documentações necessárias de negócios e etc.. isso e mais a forma de poder demonstrar, printar e tal". O plano de esforço estimou os quatro cases em 4 a 6 horas cada (o 002 em 6 a 8 se o escopo fosse completo) e recomendou o 003 como principal porque era o caminho mais controlável para provar o método inteiro.

Duas coisas do plano valem destaque:

- Ele já listava o **risco do case 003**: "vazamento de informação do resultado para o score". Esse risco virou um teste automatizado (etapa 5).
- Ele dizia que as estimativas eram hipóteses, feitas sem olhar os dados, e que, se o dataset não estivesse acessível, o bloqueio seria registrado, sem fabricar resultado.

A decisão do case foi minha. O plano só recomendou.

| Item | Evidência |
| --- | --- |
| Tarefa concluída | `G4-ESFORCO-01`, aprovada por mim em 09/10 às 00:32 |
| Plano de esforço | Publicado na branch `codex/g4-esforco-01`, commit `de36a8a` |
| Registro da escolha | O case 003 é o único que aparece depois nas tarefas e nos commits |

### Etapa 3. Os dados antes do produto

**O que aconteceu.** Antes de qualquer tela, o agente baixou o conjunto público indicado no brief (licença CC0, SHA-256 do arquivo registrado), contou registros, conferiu chaves e datas e procurou campos vazios. O commit `3973e3e` (09/10, 00:31) traz a auditoria e a hipótese testada.

O que a auditoria encontrou:

- 8.800 negócios: 4.238 ganhos, 2.473 perdidos, 1.589 em negociação e 500 em prospecção. As **2.089 abertas** são as que importam.
- O produto aparece como `GTXPro` no pipeline e `GTX Pro` no catálogo (1.480 linhas): foi preciso normalizar.
- **1.425 oportunidades abertas não têm conta.** Por isso a conta não pode ser requisito para gerar a fila.
- O arquivo só guarda o estágio **final** dos negócios fechados. Não há histórico de mudanças. Logo, nenhuma regra pode ser "validada" como previsão completa.

**A hipótese que caiu.** Foi testado um índice de afinidade histórica por produto e setor, com corte cronológico (5.343 negócios para ajustar, 1.368 para testar). Resultado: AUC **0,4854** (0,5 é jogar moeda) e **63,45%** de ganhos no quartil "melhor" contra **64,84%** no teste inteiro. O "melhor" grupo ganhou *menos* que a média. A ideia foi descartada e **não** entra na fila.

| Item | Evidência |
| --- | --- |
| Commit da auditoria | `3973e3e` |
| Números e método | [`docs/data-audit.md`](../data-audit.md) |
| Como reproduzir | `python audit.py` e `python evaluate.py` (precisam dos CSVs públicos em `data/`) |

### Etapa 4. O primeiro produto: uma regra que qualquer vendedor entende

**O que aconteceu.** Com a hipótese descartada, a solução virou uma regra operacional e explicável, implementada em [`scoring.py`](../../scoring.py). O motor nasceu no commit `3973e3e`; o servidor, a interface e os testes vieram no commit `bc5c7a5` (09/10, 00:42), e a regra tomou a forma atual com o ajuste de QA de 10/10. Hoje ela é assim:

| Situação do negócio | Fila | Pontos de partida |
| --- | --- | ---: |
| Em negociação, engajado há **até 90 dias** | Avançar | 65 |
| Em negociação, parado há **mais de 90 dias** | Revisar | 50 |
| Em prospecção | Qualificar | 35 |

Somam-se 10 pontos para conta identificada, 10 para produto com preço de catálogo de US$ 4.000 ou mais, 10 para quem está engajado há até 30 dias (em Avançar) e 10 para quem está parado há 180 dias ou mais (em Revisar). Cada oportunidade mostra os motivos da posição e uma próxima ação.

Três decisões de honestidade ficaram **escritas na tela e na documentação**:

1. O índice **não é probabilidade de fechar**.
2. Preço de catálogo é um indício de impacto, nunca valor esperado de venda.
3. Ganho comercial **não foi medido**: o conjunto é fictício, termina em 2017 e não tem histórico de atividades.

| Item | Evidência |
| --- | --- |
| Tarefa no quadro | `G4-LEAD-SCORER-01` (Codex): minha escolha em 09/10 ("escolhi o 3"), sessão minha com o Codex em 09/10 (00:37 a 00:52), QA em 09/10 (19:08 a 19:15), revisão do Claude Code aprovada (19:16 a 19:18) e minha aprovação em 10/10 às 06:51 |
| Código da regra | [`scoring.py`](../../scoring.py) (112 linhas, só biblioteca padrão do Python) |
| Descrição exata | [`docs/technical-spec.md`](../technical-spec.md), seção "Cálculo exato do índice" |
| Ajuste de QA | Commit `48c08c7` (10/10, 06:53): referência histórica fixada em 31/12/2017, para que mudar datas de fechamento nunca altere a fila |

### Etapa 5. Ciclos de uso, revisão e aprovação

Aqui o método aparece melhor. Eu usava o produto, pedia a próxima mudança, um agente construía, **outro** revisava e só então vinha a minha aprovação.

**5a. Painéis extras (`G4-003-PAINEIS-01`, 10/10).** Pedido meu depois de usar o app: uma página por vendedor, uma visão por gerente, mapa por região, painel de preço, fila em formato Kanban e anotação com status "parado/andando" em cada oportunidade.

| Momento | O que houve |
| --- | --- |
| 11:49 a 12:01 | Codex constrói (13 min). |
| 12:10 a 12:13 | Claude Code revisa e **pede ajustes**: a página do vendedor precisava mostrar as vendas históricas dele (ganhas, perdidas, valor), separadas do score, e com um teste provando que o score não muda. O revisor também corrigiu na hora o ícone e o link de Painéis nas barras laterais (commit `2026ea6`). |
| 12:14 a 12:18 | Codex ajusta (4 min) e cria o teste novo. Codex reporta 10 testes Python, 6 Node, auditoria, avaliação e conferência dos documentos passando. |
| 12:35 a 12:36 | Segunda revisão: **aprovado**. Conferiu o diff inteiro e que `scoring.py` não mudou. |
| 12:37 | Eu aprovo. |

**5b. Redesign com subpáginas (`G4-003-REDESIGN-01`, 10/10).** Pedido meu depois de aprovar a anterior: separar Gerente e Vendedor em subpáginas, criar "um mapa qualquer" de regiões com os vendedores dentro e dar a cada vendedor um cartão com avatar, "um RGzinho". Eu também trouxe uma referência visual de um CRM, e a instrução foi aproveitar a *estrutura*, não copiar o visual.

| Momento | O que houve |
| --- | --- |
| 12:56 a 13:09 | Codex constrói (13 min): menu Painéis com Gerente, Vendedor e Mapa de regiões; avatares gerados localmente; mapa explicitamente "ilustrativo". Reporta 10 testes Python com os arquivos reais e 7 Node. |
| 16:20 a 16:22 | Claude Code revisa: **aprovado**. Conferiu o diff contra os 7 critérios, que `scoring.py` ficou intacto e que os totais por região (908 + 748 + 433) somam as 2.089 oportunidades. |
| 16:22 a 19:30 | A tarefa **ficou parada** por uma regra do quadro (a entrega precisava de um link que abrisse) e só avançou às 19:30, depois de ajuste manual. |
| 19:31 | Eu aprovo. |

Depois disso, eu ainda refinei a interface com um agente (cartões de vendedor, separação entre "usar o produto" e "construção do case"), nos commits `26f3b65` e `d981caf`.

| Item | Evidência |
| --- | --- |
| Tarefas concluídas | `G4-003-PAINEIS-01` (aprovada 10/10, 12:37) e `G4-003-REDESIGN-01` (aprovada 10/10, 19:31) |
| Commits | `2ed6af2`, `2026ea6`, `ca944b1`, `6d965c1`, `26f3b65`, `d981caf` |
| Capturas reais | [`evidence/`](../../evidence/README.md) (desktop 1440 × 900 e celular 390 × 844) |
| Regra intacta | No histórico local de desenvolvimento, só dois commits alteraram `scoring.py` em 09 e 10/10; os oito seguintes não tocaram o arquivo. O código atual e os testes da submissão permitem conferir a regra entregue. |

### Etapa 6. Documentação e testes (`G4-003-DOCS-01` e `G4-INTEGRAR-DOCS-01`)

**O que aconteceu.** Eu pedi que a documentação fosse "o principal": como foi feito, o que pode ser testado, como é testado, como é validado e o trabalho dos agentes.

**Primeira tentativa recusada.** Em 09/10, o primeiro rascunho veio de um modelo local. Claude Code revisou duas vezes e devolveu: o texto era genérico, falava de login, microsserviços e banco de dados (a especificação técnica do próprio projeto diz que não há nada disso), não citava nenhum arquivo ou teste real, trazia seções vazias e estava no repositório errado. Foi **refeito do zero** no repositório do case.

**Segunda tentativa.** Em 13/10 (05:54 a 06:06), Claude Code reescreveu a documentação lendo o código: especificação de negócio com 18 regras e o código e o teste de cada uma, especificação funcional e técnica, plano de testes, guia de operação, registro do processo por tarefa e commit, e um arquivo novo de testes com as fronteiras da regra (30, 90 e 180 dias; US$ 4.000). Durante a leitura apareceram três fatos que a documentação antiga não dizia: o índice só assume valores de 10 em 10 e o teto de 100 nunca é alcançado (máximos 95, 80 e 55); negócio em negociação sem data de engajamento entra em Avançar; e o mapa só comporta as três regiões do dataset.

**Ajuste de 13/10 (06:44 a 06:46).** Eu li a documentação e apontei que havia "um print nada ver no meio da tela": as duas capturas da própria página de documentação, que mostravam um texto e não o app em uso. Uma segunda rodada removeu as duas e passou a ilustrar a especificação funcional só com capturas reais do aplicativo (gerente, vendedor, mapa, celular e tema escuro), com legenda e números conferidos nas imagens. Commit `85c461d`, na mesma branch.

**Revisão e aprovação (13/10).** De manhã, com o Codex indisponível, eu tinha dispensado a revisão. Quando ele voltou, revisou a documentação e deu o veredito "aprovado": segundo o registro, 21 testes Python, 7 Node e as verificações técnicas passaram. Eu aprovei às 11:40.

**Integração.** A primeira tentativa de merge da documentação deu conflito em 10 arquivos com um commit feito direto na branch de trabalho (`7830ecb`, 13/10, 11:42) e foi desfeita sem perder nada. A tarefa `G4-INTEGRAR-DOCS-01` resolveu: onde os dois diziam coisas diferentes, valeu o mais recente quando era fato do app e o conteúdo aprovado da documentação quando era narrativa. Merge na branch `claude-code/g4-integrar-docs-01` (commit `d985dec`), sem push. Eu aprovei às 12:22.

| Item | Evidência |
| --- | --- |
| Recusa do rascunho local | Duas revisões de Claude Code em 09/10 (10:26 a 10:35 e 10:37 a 10:49) com veredito "ajustes" |
| Documentação refeita | Branch `claude-code/g4-003-docs-01`, commits `f8ffed0` e `85c461d` |
| Revisão do Codex | Veredito "aprovado" em `G4-003-DOCS-01`; minha aprovação em 13/10, 11:40 |
| Integração | `G4-INTEGRAR-DOCS-01`, commit `d985dec`; minha aprovação em 13/10, 12:22 |
| Plano de testes | [`docs/test-plan.md`](../test-plan.md) |

### Etapa 7. Vitrine e entrega (`G4-VITRINE-01`, esta tarefa)

Reunir tudo isto em uma página de processo para a pasta `submissions/` do G4 e em um rascunho de post para o LinkedIn. A publicação, o fork e o pull request dependem de mim.

Depois da primeira versão, pedi três ajustes, todos nesta pasta:

- **Segunda versão (13/10, manhã).** Prints reais do app em [`prints-do-app.md`](prints-do-app.md), o quadro só do G4 em [`processo-no-demiurgo.md`](processo-no-demiurgo.md), no lugar das páginas de documentação.
- **Terceira versão (13/10, depois do meio-dia).** O nome Demiurgo no lugar de "Hub", em tudo, porque é como eu chamo a arquitetura de desenvolvimento.
- **Quarta versão (13/10).** Texto na primeira pessoa (a construção foi feita junto), o conceito do Demiurgo em palavras simples e o estado atualizado das tarefas.
- **Revisão de publicação (14/10).** Auditoria de privacidade e exposição: saíram as capturas do Demiurgo com caminhos locais, endereço local e tarefas de outros projetos, a exportação bruta do quadro, a galeria de conversa com o chat e os desenhos internos de funcionamento. Ficou só o que é do G4: tarefas, quadro e revisões.

A revisão do Codex desta vitrine foi dispensada por decisão minha em 13/10: eu leio e aprovo direto.

---

## 5. Linha do tempo

Montada a partir do quadro de tarefas do G4 e do histórico do git. Horários de Brasília.

| Data e hora | Marco | Quem | Registro |
| --- | --- | --- | --- |
| 08/10 13:03 a 13:08 | Levantamento dos 4 cases e das regras | Claude Code | `G4-RECON-01` |
| 08/10 13:09 a 13:14 | Revisão cruzada: aprovado, com 3 correções | Codex | `G4-RECON-01` |
| 08/10 23:38 | Plano de esforço dos 4 cases desenhado (brief) | Claude Code | `G4-ESFORCO-01` |
| 09/10 00:09 | Levantamento aprovado | Eu | `G4-RECON-01` |
| 09/10 00:12 a 00:16 | Plano de esforço publicado numa sessão comigo | Codex, eu | `G4-ESFORCO-01`, branch `codex/g4-esforco-01` |
| 09/10 00:31 | Auditoria dos dados e hipótese rejeitada | Codex (a meu pedido) | commit `3973e3e` |
| 09/10 00:32 | Plano de esforço aprovado; case 003 segue como foco | Eu | `G4-ESFORCO-01` |
| 09/10 00:42 | Primeiro app com regra explicável e testes | Codex | commit `bc5c7a5` |
| 09/10 09:30 a 12:00 | Três visões, tema claro/escuro, documentação, teste pelo celular na rede local | Eu com agente | commits `e43aff8`, `3e2702f`, `cd1e947`, `2d15357`, `3af65a4` |
| 09/10 10:25 a 10:27 | Primeira tentativa de painéis parou sem alterar nada: apontava para o repositório errado | Codex | `G4-003-PAINEIS-01` |
| 09/10 10:26 a 10:49 | Rascunho de documentação do modelo local, recusado duas vezes | Modelo local / Claude Code | `G4-003-DOCS-01` |
| 09/10 19:08 a 19:18 | QA da construção; revisão cruzada: aprovado | Codex, Claude Code | `G4-LEAD-SCORER-01` |
| 10/10 06:51 | Aprovo a construção do Foco | Eu | `G4-LEAD-SCORER-01` |
| 10/10 06:53 | QA consolidado: referência histórica fixa em 31/12/2017 | Eu com agente | commit `48c08c7` |
| 10/10 11:49 a 12:01 | Painéis, Kanban, anotações: construção | Codex | commit `2ed6af2` |
| 10/10 12:10 a 12:13 | Revisão pede ajustes e corrige ícone e links | Claude Code | commit `2026ea6` |
| 10/10 12:14 a 12:18 | Vendas históricas por vendedor e teste de score intacto | Codex | commit `ca944b1` |
| 10/10 12:35 a 12:37 | Revisão aprovada; eu aprovo | Claude Code, eu | `G4-003-PAINEIS-01` |
| 10/10 12:56 a 13:09 | Subpáginas Gerente, Vendedor e Mapa; avatares | Codex | commit `6d965c1` |
| 10/10 13:36 a 18:08 | Cartões refinados, produto separado da narrativa do case, processo explicado | Eu com agente | commits `26f3b65`, `d981caf`, `0a2be16`, `15bb553` |
| 10/10 16:20 a 16:22 | Revisão aprovada | Claude Code | `G4-003-REDESIGN-01` |
| 10/10 19:31 | Aprovo o redesign | Eu | `G4-003-REDESIGN-01` |
| 13/10 05:54 a 06:06 | Documentação completa refeita contra o código | Claude Code | `G4-003-DOCS-01`, commit `f8ffed0` |
| 13/10 06:06 a 06:16 | Vitrine, 1ª versão: fluxo completo, página de processo, post | Claude Code | `G4-VITRINE-01` |
| 13/10 06:34 | Codex indisponível: documentação e vitrine sem revisão dele; eu leio e aprovo direto | Eu | decisão registrada na tarefa |
| 13/10 06:44 a 06:46 | Prints das páginas de documentação trocados por prints reais do app | Claude Code | `G4-003-DOCS-01`, commit `85c461d` |
| 13/10 06:48 em diante | Vitrine, 2ª versão: prints reais, processo no Demiurgo só do G4 | Claude Code | `G4-VITRINE-01`, commit `4a13156` |
| 13/10 | Revisão da documentação: aprovado | Codex | `G4-003-DOCS-01` |
| 13/10 11:40 | Aprovo a documentação | Eu | `G4-003-DOCS-01` |
| 13/10 12:22 | Aprovo a integração da documentação | Eu | `G4-INTEGRAR-DOCS-01`, commit `d985dec` |
| 13/10 depois das 12:23 | Vitrine, 3ª versão: Demiurgo no lugar de "Hub" | Claude Code | `G4-VITRINE-01`, commit `098b8ea` |
| 13/10 depois das 12:26 | Vitrine, 4ª versão: primeira pessoa, conceito do Demiurgo, estado atualizado | Claude Code | `G4-VITRINE-01` |
| 14/10 | Auditoria de privacidade: capturas e textos internos removidos desta vitrine | Claude Code | `G4-PUBLICO-AUDITORIA-01` |

---

## 6. Onde a IA errou, ou o processo travou, e como foi corrigido

Esta é a parte que o G4 pede e que costuma faltar nas submissões.

| # | O que deu errado | Como foi percebido | Correção |
| --- | --- | --- | --- |
| 1 | A primeira hipótese (afinidade histórica) não separa ganhos de perdas. | Avaliação com corte cronológico: AUC 0,4854. | Descartada. Fila baseada em regra explicável; limite escrito na tela. |
| 2 | Rascunho de documentação do modelo local: genérico, no lugar errado, contradizia o código. | Revisão de Claude Code comparou com a especificação técnica do projeto. | Recusado duas vezes e refeito do zero a partir do código e dos testes. |
| 3 | A primeira tentativa de painéis começou no repositório errado. | O próprio agente parou antes de alterar. | Terminou sem mudanças; foi refeita em 10/10 no repositório certo. |
| 4 | Página do vendedor sem as vendas históricas. | Revisão contra o critério de aceite. | Codex ajustou e acrescentou um teste de que o score não muda. |
| 5 | O plano de testes dizia "celular pendente", mas o histórico mostrava o acesso já confirmado em 09/10. | Conferência do texto contra o histórico do git na documentação. | Texto reconciliado (branch da documentação). |
| 6 | Documentação antiga não dizia que o teto de 100 do índice nunca é alcançado. | Leitura do código durante a documentação. | Registrado na especificação (máximos 95, 80, 55) e fixado em testes. |
| 7 | Revisões de Claude Code não conseguiram rodar Python nem tinham a pasta de dados. | O ambiente bloqueou a execução. | Os vereditos dizem "não executado" e confiam, de forma explícita, na execução registrada pelo Codex. |
| 8 | Uma tarefa aprovada não avançou por falta de um link de entrega. | Regra do quadro, percebida na conferência de status. | Ajustada à mão; seguiu às 19:30. |
| 9 | A documentação trazia duas capturas da própria página de documentação, "um print nada ver no meio da tela". | Eu li a documentação em 13/10. | Removidas e trocadas por prints reais do app, com legenda e números conferidos nas imagens (commit `85c461d`). |
| 10 | Na primeira versão desta vitrine, o texto dizia que a construção do primeiro produto não aparecia no quadro; aparecia, como `G4-LEAD-SCORER-01`. | Consulta à ficha da tarefa na segunda versão. | Texto corrigido e a tarefa incluída no quadro e na linha do tempo. |
| 11 | O merge da documentação deu conflito em 10 arquivos com um commit feito direto na branch de trabalho. | Na tentativa de merge, logo depois da minha aprovação. | Desfeito sem perder nada; resolvido numa tarefa própria (`G4-INTEGRAR-DOCS-01`) e aprovado por mim. |
| 12 | Capturas da tela do Demiurgo mostravam uma pasta do computador, um endereço local e tarefas de outros projetos. | Cada imagem foi aberta e conferida antes do uso. | Nenhuma entrou como estava. Só ficou o quadro do G4 (ver [`processo-no-demiurgo.md`](processo-no-demiurgo.md)). |
| 13 | A vitrine dizia que a documentação estava "em andamento" e "sem revisão do Codex"; as duas coisas mudaram em 13/10. | Consulta ao estado das tarefas na quarta versão. | Texto e quadro atualizados (etapa 6). |

Duas lições se repetem: **o revisor compara com o código e com o critério de aceite, não com a confiança do autor**, e **o que não foi executado é dito como não executado**.

---

## 7. Testes: o que existe e o que foi executado

**O que existe** (conferido contra os arquivos da branch na primeira versão desta vitrine; a documentação integrada depois acrescentou `tests/test_rules.py`):

| Conjunto | Quantidade | Dados | O que cobre |
| --- | ---: | --- | --- |
| `tests/test_scoring.py` | 8 | Arquivos reais do desafio | Junções, só abertas, ordem estável, conta ausente, desfecho não vaza para o score, resposta HTTP |
| `tests/test_sales.py` | 2 | Sintéticos | Resumo de vendas por vendedor; mudar ganhos e perdas não muda a fila |
| `tests/test_rules.py` | 11 | Sintéticos | Fronteiras da regra: 30, 90 e 180 dias; US$ 4.000 (arquivo novo da documentação) |
| `tests/test_filters.cjs` | 2 | Sintéticos | Filtros combinados e busca |
| `tests/test_business.cjs` | 5 | Sintéticos | Agrupamentos, faixas de preço, RG e mapa, anotações |

**Resultados reais, com origem:**

| Data | Quem | Resultado | Fonte |
| --- | --- | --- | --- |
| 10/10 | Codex, painéis | 10 testes Python, 6 Node, auditoria, avaliação e conferência de documentos passaram | Evidência da tarefa `G4-003-PAINEIS-01` |
| 10/10 | Codex, redesign | 10 testes Python com os arquivos reais e 7 Node passaram | Evidência da tarefa `G4-003-REDESIGN-01` |
| 10/10 | Claude Code, revisões | Node 6/6 e 7/7 reexecutados; Python não executado | Veredito de cada revisão |
| 13/10 | Claude Code, vitrine | **Node 7/7 passou** nas duas primeiras versões (`node --test tests/test_filters.cjs tests/test_business.cjs`, Node v24.21.0) | Execução sobre o código da branch |
| 13/10 | Codex, revisão da documentação | **21 testes Python e 7 Node passaram**, mais verificações técnicas | Veredito em `G4-003-DOCS-01` |

O número 21 bate com 8 + 2 + 11 (os arquivos acima), mas o registro do veredito não detalha por arquivo.

**O que Claude Code não executou nesta vitrine:** a suíte Python, `audit.py`, `evaluate.py` e `download_data.py`. O ambiente desta vitrine não permitiu executar Python. Os números do conjunto de dados (8.800, 2.089, 1.425, 0,4854) vêm da auditoria registrada em [`docs/data-audit.md`](../data-audit.md) e das execuções do Codex, não de uma execução desta vitrine.

---

## 8. Segurança e privacidade

| Cuidado | Como está garantido | Onde conferir |
| --- | --- | --- |
| Entrega isolada | O case vive em repositório próprio, sem arquivos de outros projetos | `git ls-files` e [`.gitignore`](../../.gitignore) |
| Dados fora do Git | `data/`, `.env`, chaves e certificados, `captures-private/` e `internal/` são ignorados | `.gitignore` |
| Nada sai da máquina | Servidor padrão escuta só em `127.0.0.1`; sem serviço externo, sem conta; internet só para baixar o conjunto público | [`docs/technical-spec.md`](../technical-spec.md) |
| Rede local é opcional e avisada | A instância para o celular usa o IP da máquina, com aviso de que **não** tem autenticação e não deve ir para a internet | [`README.md`](../../README.md) |
| Anotações ficam no navegador | Guardadas no armazenamento local do navegador; o servidor só implementa leitura (`GET`), então não há por onde receber anotações | `app.py`, [`docs/technical-spec.md`](../technical-spec.md) e teste de leitura e gravação local em `test_business.cjs` |
| Resultado não vaza para o score | `close_value`, `close_date` e Won/Lost não entram na pontuação de uma oportunidade aberta | Testes de `test_scoring.py` e `test_sales.py` |
| Agentes com limites | Nos briefs: sem push, PR ou fork sem mim; sem foto real de pessoa; sem serviço pago; trabalho em cópia isolada | Brief de cada tarefa no quadro |
| Aprovação humana | Nenhuma tarefa foi concluída sem a minha aprovação | Registro "Aprovado por" de cada tarefa |
| Sem caminho local no material | Busca nos arquivos versionados por caminhos de disco, endereços locais e nomes de outros projetos. A busca de 13/10 não achou nada nos textos; a auditoria de 14/10 achou capturas e exportações com esses dados e as retirou | Busca por texto e conferência visual das capturas |

---

## 9. Resultado: o que pode e o que não pode ser afirmado

**Pode afirmar:**

- Existe um aplicativo local funcional que prioriza 2.089 oportunidades abertas em três filas, com motivo e próxima ação por item.
- Uma hipótese preditiva foi testada, falhou e foi descartada com número.
- A regra é determinística e o desfecho do negócio não influencia a fila (teste automatizado).
- O trabalho passou por tarefas, revisões cruzadas e aprovações humanas registradas, com erros e correções incluídos.

**Não pode afirmar:**

- Que o Foco aumenta conversão ou receita. Não foi medido, e o conjunto é fictício e termina em 2017.
- Que o índice é probabilidade de fechamento.
- Quantas horas foram gastas. O tempo real não foi cronometrado; o 4 a 6 horas do plano é estimativa.
- Que as filas são equilibradas. Com a referência fixa em 31/12/2017, a maioria das oportunidades em negociação já passou dos 90 dias: somando as caixas por gerente na captura [`gerentes-desktop.png`](../evidence/gerentes-desktop.png), a fila **Avançar** tem cerca de 110 itens, **Revisar** cerca de 1.479 e **Qualificar** 500 (total 2.089). É um efeito do conjunto histórico, e quem demonstrar o app deve saber disso antes de explicá-lo.
- Que a interface foi validada em celular real além da abertura que eu confirmei em 09/10 (rede local, commit `2d15357`). Legibilidade, interação e teclado seguem sem inspeção detalhada registrada.
- Que o Demiurgo usou Gemini ou outros modelos no G4: usamos Claude Code, Codex e um modelo local.

---

## 10. Como conferir sozinho

1. **A regra:** leia [`scoring.py`](../../scoring.py). São 112 linhas.
2. **Os testes que não precisam de dados:** `node --test tests/test_filters.cjs tests/test_business.cjs`.
3. **Os testes completos:** `python download_data.py`, depois `python -m unittest discover -s tests -v` e `python audit.py` / `python evaluate.py`.
4. **O processo:** a tabela da seção 5 e o [registro escrito](../../PROCESS_LOG.md). O histórico Git local anterior não acompanha esta submissão.
5. **O app:** `python app.py` e abrir o endereço local que o comando imprime (o [`README.md`](../../README.md) tem o passo a passo).

As afirmações sobre o produto podem ser conferidas no código, nos testes e nos documentos citados acima. O exemplo do quadro mostra somente as tarefas do G4.

---

## 11. Limites desta vitrine

- A versão pública desta vitrine foi conferida em 14/10 e ainda depende da minha aprovação para publicação.
- A figura `img/quadro-g4.svg` é montada a partir dos registros, não é captura da tela do Demiurgo, e não foi renderizada num navegador.
- Há uma captura real do quadro do G4 em [`processo-no-demiurgo.md`](processo-no-demiurgo.md). Faltam uma captura de tarefa em revisão e uma dos agentes trabalhando.
- As capturas finais da tela de oportunidades, no desktop e no celular, foram tiradas em 14/10 e estão em `evidence/final-oportunidades-desktop.png` e `evidence/final-oportunidades-celular.png`.
- Os commits do histórico aparecem, em sua maioria, com o autor humano. **O autor do commit não identifica quem produziu o trabalho**; para isso vale o registro da tarefa.
- O registro do quadro foi lido em 13/10/2026, depois das 12:22. Estados posteriores não estão refletidos.
