# Process Log — Challenge 003 | Lead Scorer

**Responsável:** Maria Alice Dantas · **Período:** 14/10/2026 12:55 a 19/10/2026 14:24 · **Status:** finalizado

## 1. Como usei IA, em um parágrafo

Usei o Claude Code como par de trabalho em todas as etapas (00 a 11) e tratei cada resposta como proposta a verificar, não como fato. Decompus o problema antes de pedir qualquer coisa, deixei as restrições escritas no prompt (o que a IA pode ou não alterar, o que separa fato de hipótese) e conferi os números contra os CSVs. Onde a IA errou, ou onde a evidência não sustentava a ideia, corrigi o rumo e registrei por quê. Este documento não transcreve tudo: conta as decisões que mudaram o projeto e mantém um índice com todas as 61 interações ([seção 9](#9-índice-das-61-interações)), para quem quiser rastrear.

**Como ler:** a [seção 4](#4-episódios-principais) traz os episódios que mais mostram julgamento. A [seção 5](#5-decisões-independentes) lista minhas decisões contra a recomendação da IA, ou sem ela. A [seção 6](#6-erros-da-ia-e-meus) reúne os erros, e a [seção 7](#7-o-que-este-processo-não-comprova), o que ele não comprova.

> **Nome do grupo:** "Revisar" é o nome antigo de **Confirmar**. Nas interações das Etapas 05 a 10 aparece o nome da época; o README e a versão final usam "Confirmar".

## 2. Ferramentas utilizadas

| Ferramenta | Para que usei | Etapas |
| --- | --- | --- |
| Claude Code (Claude Sonnet 5.5 e Opus 5.5) | Discovery, auditoria dos dados, ADRs, PRD, construção do back, da API e da tela, backtest, testes, correção pelas personas, priorização assistida, entrega e este registro | 00 a 11 |
| Subagentes do Claude Code (Plan, Explore e general-purpose) | Três propostas independentes de ADR (PL-018); mapeamentos de código e dados; planos da regra A e da Inteligência; as seis personas que usaram o Rankio no navegador (PL-049) | 05, 08, 09, 10 |
| Navegador do app Claude Code e Chrome headless | Ensaio das jornadas, conferência em 375, 768 e 1280 px nos dois temas, medição de contraste, jornadas das personas e capturas de tela | 07 a 11 |
| Busca na web | Técnicas de scoring em vendas, uplift e calibração (PL-019) | 05 |
| ChatGPT | Desenho do template deste log e otimização de prompts antes de enviá-los | 00 a 10 |

## 3. Linha do tempo

| Etapa | Início | Fim | Duração efetiva |
| --- | --- | --- | --- |
| 00 — Setup | 14/10 12:55 | 14/10 19:30 | ≥ 02:35 |
| 01 — Business Discovery | 15/10 07:37 | 15/10 18:52 | ≥ 00:55 |
| 02 — Domain & Value | 15/10 09:16 | 15/10 19:02 | ≥ 00:22 |
| 03 — Data Discovery | 15/10 12:49 | 15/10 22:00 | ≥ 02:48 |
| 04 — Prioritization | 15/10 19:26 | 15/10 19:46 | 00:20 |
| 05 — Baseline & Architecture | 15/10 20:17 | 15/10 22:08 | ≥ 01:32 |
| 06 — MVP Definition | 15/10 22:16 | 15/10 22:49 | ≥ 00:33 |
| 07 — Development | 15/10 23:13 | 18/10 17:20 | ≥ 02:03 |
| 08 — Validation & Iteration | 16/10 11:37 | 18/10 17:30 | ≥ 08:10 |
| 09 — Validation com personas | 17/10 17:03 | 18/10 17:57 | ≥ 00:54 |
| 10 — Correção pelas personas e priorização assistida | 17/10 18:48 | 18/10 18:01 | ≥ 04:38 |
| 11 — Delivery | 18/10 18:20 | 19/10 14:24 | não cronometrada |

**Nota sobre o tempo.** Os horários vêm do transcript do Claude Code e intervalos de 15 min ou mais sem atividade foram descartados da soma. A soma (≥ 24:50) é um piso aproximado, portanto não deve ser lida como tempo total de construção.

## 4. Episódios principais

Cada episódio segue o mesmo formato: o problema, como usei a IA, o que saiu, minha decisão e onde está a evidência. Os números das interações (PL) remetem ao [índice](#9-índice-das-61-interações).

### 4.1 Discovery e limites dos dados

#### PL-003 — Tratar o briefing como percepção a validar (15/10, 07:37)

- **Problema.** O briefing da Head de RevOps traz uma queixa ("gastam tempo demais em deals que não vão fechar"), mas nenhum custo, baseline ou número.
- **Uso da IA.** Pedi a análise como consultor sênior, em cinco blocos, com salvaguardas escritas no prompt: separar fato, percepção e hipótese; não afirmar causa comprovada; não inventar custo; não recomendar tecnologia nesta etapa. Na iteração, pedi a coluna "Mudança esperada (hipótese)" no mapa stakeholder → decisão → KPI.
- **O que saiu.** O briefing não tem baseline; a "ferramenta" já vem como solução, quando o gargalo pode ser capacidade, critério ou incentivo; `close_value` só existe depois do fechamento, então um deal aberto não tem valor definido; o histórico de resultados pode refletir a priorização passada.
- **Minha decisão.** Tratar o problema como percepção a validar e adiar tecnologia e funcionalidades. O mapa virou a base das seções 1.3, 1.4 e 1.6 do `discovery.md`.
- **Evidência.** `docs/discovery.md`, seção 1.

As interações seguintes de discovery (PL-004 a PL-007, PL-010 a PL-014) foram de construção e consolidação do `discovery.md`. Nelas corrigi a primeira versão dos mapas da IA (conceitos mesclados em uma linha, a decisão "qual forecast comprometer" ausente, limitação do dado misturada com distorção de interpretação) e decidi que as limitações dos dados viram **requisitos de projeto**, e não pendências.

#### PL-008 — Auditoria reproduzível dos dados (15/10, 12:49)

- **Problema.** Saber o que os 8.800 registros permitem afirmar antes de escolher qualquer abordagem.
- **Uso da IA.** Pedi um script reproduzível com CSVs intactos, integridade das junções, definição da variável-alvo, detecção de vazamento e cada conclusão classificada como FATO MEDIDO, INTERPRETAÇÃO, HIPÓTESE ou NÃO VERIFICÁVEL, sem declarar teste concluído sem execução. A IA devolveu quatro perguntas antes de executar (o arquivo de requisitos citado não existia, a pasta do script, o Python do sistema sem pandas, o número de relatórios).
- **O que saiu.** 6.711 com resultado (63,15% Won) e 2.089 abertas; `GTXPro` ≠ `GTX Pro` faz o join por nome perder 1.480 linhas em silêncio; `account` nula em 68,2% das abertas e 0% das fechadas; nenhum sinal legítimo discrimina de forma estável (AUC de 0,47 a 0,57), e o maior efeito do dataset, o mês de fechamento, é vazamento; 1.291 de 1.589 Engaging (81,2%) estão abertas há mais do que o maior ciclo fechado (138 dias).
- **Verificação.** Quatro execuções: a 2ª falhou com `UnboundLocalError` (erro da IA) e foi corrigida; a 3ª e a 4ª saíram idênticas, então o script é determinístico; o SHA-256 dos CSVs ficou igual antes e depois. A revisão cética da IA pegou antes da entrega: 81,3% → 81,2%, uma sonda de vazamento no mês errado do trimestre, a carga confundida com o truncamento e três afirmações sobre AUC e Brier que a saída não sustentava.
- **Minhas decisões.** Usar o `venv` em `solution/` em vez do "só biblioteca padrão" que a IA recomendou; um único relatório; o README do desafio como fonte de requisitos.
- **Evidência.** `solution/scripts/audit_data.py`, `solution/data/processed/audit_results.json` e `audit_log.txt`, `docs/data-audit.md`.

#### PL-009 — Contestar as definições de Lost, "zumbi" e vazamento (15/10, 13:50)

- **Problema.** Eu precisava entender o que o script realmente fazia antes de usar seus números.
- **Uso da IA.** Pedi a explicação exata do script e o que ele não consegue dizer. Questionei Lost, "zumbi", vazamento, conta preenchida e registros idênticos, e contestei a leitura de Lost como "limpeza de CRM" com o README do desafio.
- **O que saiu.** A IA admitiu que "zumbi" era hipótese dela e que o dado mede idade, não abandono. Concordou que o README define Lost como estágio terminal. Propôs rebaixar o risco #7, e **essa proposta não foi aplicada**.
- **Minha decisão.** Lost é terminal (Won = 1, Lost = 0); a palavra passa a ser "envelhecido"; princípio que adotei: "se não tem nos dados, não é possível definir".

### 4.2 Scoring e arquitetura

#### PL-018 — Três propostas independentes de ADR (15/10, 20:17)

- **Problema.** Decidir estratégia de scoring, manipulação de dados e tecnologia com alternativas comparadas, sem depender de uma só voz.
- **Uso da IA.** Três subagentes Plan, cada um com uma lente (arquiteto, engenheiro de entrega e revisor), sobre o mesmo escopo, enquanto eu respondia às perguntas que fechavam decisões.
- **O que saiu.** Convergiram no motor de regras, na rejeição de ML, em normalizar `GTXPro`, em `as_of` como parâmetro e em conta nula como aviso. Divergiram em soma de pontos × matriz lexicográfica, em interface (Streamlit, HTML estático), em limite de ciclo global × por produto e no papel do backtest. O revisor achou inconsistências entre documentos e executou o teste T-B, que o discovery tinha deixado pendente.
- **Minha decisão.** FastAPI + Next.js sobre um núcleo Python puro, **contra a recomendação dos três agentes**, porque exigi desacoplar apresentação e lógica e consultar o ranking por API; registrei o custo de setup como risco aceito (ADR-003). Também não tratei a convergência como prova: os três leram os mesmos documentos, cujas conclusões já apontavam para regras.
- **Verificação.** Reconferi os números dos agentes (298 e 1.291 Engaging dentro e fora do ciclo; 351, 298, 160 e 34 em Focar nos quatro `as_of`). O acúmulo de abertas acima do maior ciclo ao longo do tempo, reportado por dois agentes, não foi reconferido.
- **Evidência.** `docs/architecture.md`. Os relatórios completos dos agentes não estão anexados.

Nas interações seguintes (PL-019 a PL-021 e PL-023), defendi a estratégia contra sete abordagens e exigi o impacto de cada padrão antes de aprovar, o que gerou as sondas de ML e de empresa e região que a auditoria não tinha feito. Empresa e região viraram filtros fora do cálculo; ML e uplift saíram do MVP; e a conta nula passou a ser tratada como artefato da base, com um aviso único no cabeçalho em vez de um por linha.

#### PL-022 — Retirar a idade da ordenação (15/10, 21:37)

- **Problema.** O desempate "mais antigo primeiro" colocava no topo de Focar a borda do ciclo, e eu não entendia por que a revisão o considerava uma falha.
- **Uso da IA.** Pedi a explicação antes de decidir, e depois a aplicação da opção A:

  > Aplique a opção A nos ADRs: tirar a idade da chave de ordenação (estado, faixa de valor, preço exato, ID estável) e exibir a idade como coluna.

- **O que saiu.** Os 20 primeiros de Focar têm de 135 a 138 dias, e a taxa de resolução em 30 dias cai de 12–62% (45 a 104 dias) para 1–5% nessa faixa, mas confundida com o calendário e com o teto de 138 d. A IA corrigiu um número próprio ("44% a 62%" omitia uma célula de 12%) e reclassificou a falha de "alta" para "média".
- **Minha decisão.** A evidência é fraca nos dois sentidos, então **não apostei em uma direção**: a idade aparece, mas não ordena. Aceitei a consequência (deals do mesmo produto e estado ficam em empate). Os rótulos de valor passam a ser sempre "de tabela", nunca "alta" ou "baixa" isolados.
- **Verificação.** Teste novo no ADR-001: embaralhar `engage_date` entre deals do mesmo estado e produto não muda a ordem.

#### PL-034 — Revisão crítica da regra A antes de aprovar (16/10, 14:12)

- **Problema.** A abordagem A (dois limites de idade, 106 e 138 dias) parecia melhor no backtest, e eu não queria adotá-la só pelo número.
- **Uso da IA.** Pedi, antes de qualquer aprovação, (1) a separação entre o que é observado e o que é reconstrução no histórico, (2) sensibilidade dos limites (90, 100, 106, 115 e 120 dias), sem escolher o P90 só por ser P90, (3) robustez com cortes sobrepostos e (4) o que o backtest comprova e o que é hipótese.
- **O que saiu.** "Mantenho A, mas rebaixo o que ela promete." O ganho é de +1,5 ponto de Val@10 (IC95% +0,2 a +2,7), cerca de 0,18 venda a mais por lista de 10 a cada 90 dias, e **vem inteiro das negociações que nunca recebem desfecho**: sem elas, a regra fica 1,0 ponto atrás de "só valor de tabela". Os limites de 100 a 120 d formam um platô. A IA mudou o cálculo de Val@10 entre as rodadas (média por corte → razão agregada), o que levou A a 58,4% contra 56,9%.
- **Minha decisão.** Corrigir o backtest antes de mexer no produto (PL-035, commit `c0b64da`: a versão original selecionava a população pelo desfecho). Depois, adotar a regra A (PL-043, contrato v5) como **ajuste de coerência, não como capacidade preditiva**, com o argumento do pior caso (−1,0 contra −1,5 ponto) e a dependência das negociações sem desfecho visível na página Evidência.
- **Evidência.** `solution/data/processed/backtest_report.md`, `scripts/backtest.py`, commits `c0b64da` e `ab0f56f`.

#### PL-037 — Fronteira entre back e front (16/10, 15:31)

- **Problema.** Nomes de grupos e frases do painel estavam no núcleo Python, e o front é Next.js.
- **Uso da IA.** Pedi que avaliasse como desenvolvedora sênior. A IA defendeu primeiro os textos no núcleo (ADR-003) e só na última resposta reconheceu: "isso corrige a minha recomendação anterior".
- **Minha decisão.** Decisão no back, apresentação no front. O back entrega grupos, ordem, ação e motivos como código mais valores; o front e a CLI escrevem as frases; o vocabulário proibido passa a ser testado no front. É o ADR-004, executado no plano F1 a F6 (PL-038).

### 4.3 Build e validação técnica

#### PL-024 e PL-025 — PRD enxuto e teste de mesa (15/10, 22:16 a 22:36)

- **Uso da IA.** Pedi um PRD de no máximo duas páginas, com três P0 e critérios DADO/QUANDO/ENTÃO, sem reabrir o discovery. Em seguida, pedi um teste de mesa como vendedor e QA, limitado a três correções.
- **O que saiu.** O teste achou três lacunas antes de qualquer código: faltava próximo passo para Focar, Qualificar e Focar vazio (os 6 vendedores sem Focar concentram 317 das 500 Prospecting); a regra de ordem não aparecia na tela; a tela não tinha critério de aceite. A IA reconheceu que criou a primeira ao condensar o PRD para caber nas duas páginas.
- **Minhas decisões.** Manter os CSVs fora do repositório, contra a recomendação da IA, e corrigir a premissa do prazo: as 4 a 6 h são estimativa, não restrição, o que eliminou o gatilho de corte de 2 h. Aprovei duas decisões do PRD: `as_of` mínimo e produto desconhecido como erro.

#### PL-026 — Plano de build em quatro specs (15/10, 23:13)

A IA propôs a menor fatia vertical (a lista de um vendedor na CLI, sem Node), quatro specs ordenadas por risco e 14 incrementos com teste e critério de pronto. Concordei com a ordem. Ao simular o checkpoint de Git, a IA achou que o `git add -f` do meu fluxo de commit incluiria os 5 CSVs e 6.670 arquivos do `.venv`, e que exclusões por pathspec anulam o `-f`, deixando docs e scripts de fora sem aviso. O fluxo foi corrigido para um `git add` por `find` antes do primeiro commit da solução.

#### PL-032 — Primeiro backtest temporal (16/10, 08:32)

Pedi o backtest opcional com 5 cortes, comparando a regra com o acaso, com "só valor de tabela" e com a taxa por produto, e a armadilha do mês de fechamento. Resultado: nenhuma ordenação legítima supera o acaso (AUC por volta de 0,5); só a armadilha passa de 0,6 (0,632); ordenar por preço captura cerca de metade do valor nos 20% primeiros por construção, sem prever quem fecha. Rodado de novo a partir da árvore do commit, o resultado saiu idêntico. Esta versão foi depois substituída: o PL-035 mostrou que selecionava a população pelo desfecho, e o backtest final tem 7 cortes e toda negociação aberta em cada corte.

### 4.4 Personas e priorização assistida

#### PL-049 — Seis personas independentes (17/10, 17:35)

- **Problema.** Eu não tinha vendedores à mão e corria o risco de achar tudo claro por conhecer tudo.
- **Uso da IA.** Seis subagentes, **um por vez**, cada um com papel e missão (vendedor iniciante, experiente, sobrecarregado, gerente, Head de RevOps e diretor comercial), usando o Rankio no navegador. Proibi ler arquivos, usar shell, chamar a API ou pesquisar, e pedi que o coordenador separasse "tarefa concluída" de "decisão correta" e "observável" de "impacto em produção".
- **O que saiu.** Todos chegaram ao painel "Por que está aqui" sem instrução, e **todos fecharam em "resolve parcialmente"**. Achados: dentro de um empate a ordem é por ID e a tela não avisava; o "próximo passo" de Focar era a regra de ordenação, não uma ação; 66 a 68% das abertas não têm cliente; 62% da carteira fica em Confirmar. A Head simulada aprovaria um piloto com grupo de controle.
- **Verificação.** A IA conferiu três pontos antes de consolidar (a ordem do empate, a paginação, um clique não reproduzido) e corrigiu quatro imprecisões próprias na consolidação.
- **O que não prova.** São agentes do mesmo modelo, a instrução "não seja gentil" pode ter empurrado os relatos para o lado crítico, e os testes rodaram numa versão que já mudou. Isso mostra se a estrutura se entende, não que a ferramenta decide bem. Não é validação com usuários reais.
- **Evidência.** `docs/testes-personas/` (consolidação e seis relatos).

Nas interações seguintes (PL-050 a PL-055), a IA propôs "Retome o contato com <cliente>" e "está a N dias do limite", o que presumia atividade e urgência que a base não registra; apontei, e ela retirou as quatro propostas. Descartei "Minha sessão de trabalho" (repetiria o "O que verificar agora" de cada painel) e aceitei a objeção da IA a uma barra de score de 10 a 100, por poder ser lida como chance de fechar.

#### PL-052 — Mudar a ordem dos grupos: uma aposta de produto, não um achado (17/10, 20:06)

- **Problema.** Eu achava que colocar Confirmar à frente de Qualificar significava gastar tempo com deals que não vão fechar, e usei a vendedora Anna Snelling como caso.
- **O que a investigação mostrou.** Nada na lógica de scoring tinha mudado. Os números que citei para a Anna ("5 qualificações" e "11 acima de 106 dias") não conferiam: ela tem 55 Qualificar, 1 Acompanhar e 56 Confirmar, e eu os li em outra tela, de uma versão que não guardei. O ciclo dela é comum, não rápido (mediana de 60 d contra 57 d da empresa), e nenhuma diferença por vendedor, produto ou conta passa na correção para múltiplos testes. A IA disse que Qualificar antes de Confirmar é **plausível, mas não demonstrável** (nenhuma Prospecting tem desfecho na base) e que não trocaria a regra com base em um vendedor.
- **Minha decisão.** Mudei a ordem para Focar → Qualificar → Acompanhar → Confirmar → Completar (contrato v7), ciente disso. **É uma hipótese de política operacional, não uma conclusão dos dados.** O backtest não a sustenta (Qualificar fica fora dele, por não ter data) e não o rodei de novo depois da troca. Só um piloto com grupo de controle mostraria se a ordem ajuda. O README repete a ressalva ("decisão de produto, não evidência").
- **Não implementei** as três propostas da IA (coluna de ciclo, fato histórico em Confirmar, cartão de Focar vazio mais honesto).
- **Evidência.** Commits `a17471f`, `44298a5`, `007b677`, `65eda15`, `04f2289`; ADR-009.

#### PL-056 — Pontos de qualificação: pesos são hipótese comercial (17/10, 22:48)

- **Problema.** A base não tem atividade nem estágio para separar oportunidades empatadas, e o plano da IA (camadas de categorias com critérios em sequência) eu não conseguia explicar.
- **Uso da IA.** Rejeitei o plano e propus pontos por resposta, numa escala de 0 a 100, com sete dimensões inspiradas no BANT, com pesos meus:

  > Acredito que a categorizacao pode ser feita por pontos. Definir pontos para cada resposta, em seguida rankear por quem atingiu mais pontos.

- **O que saiu.** A IA percebeu que **os pesos que propus somavam 110, não 100**, e fez quatro perguntas (ajustar a soma, número de perguntas, valor de "Não sei", papel da categoria). Eu decidi: reduzir a Urgência de 25 para 15, sete perguntas, "Não sei" = 0 ponto confirmado com a faixa visível ("55 confirmados, até 80 se o que você não sabe se confirmar"), e pontos que ordenam com a categoria dizendo o que fazer.
- **Como ler o resultado.** A soma errada foi detectada **antes** da implementação. O ajuste da Urgência foi uma escolha provisória para fechar 100, não uma inferência do dataset, e os pesos e os pontos por resposta são **hipóteses comerciais, sem calibração estatística**. Estar explicável e ser determinístico não os valida: faltam validação com especialistas de vendas e resultados observados, e o reteste com 5 vendedores reais não foi feito. A tela diz "Pesos iniciais, a validar. Baseado nas suas respostas; não é previsão de fechamento."
- **Por que existe.** Foi a resposta ao caso da Darcel Schlecht: 13 oportunidades empatadas no topo e nenhum dado para separá-las. Exigi também que "nada seja gravado no backend" (ADR-010, exceção declarada ao ADR-004).
- **Evidência.** ADR-010; commits `fa23ae9` e `4140f8d`.

## 5. Decisões independentes

As decisões em que divergi da IA ou decidi sem a recomendação dela, no que mais pesou:

1. **Tratar o briefing como percepção a validar** e adiar tecnologia (PL-003).
2. **Rejeitar "Lost = limpeza de CRM"** e fixar a definição pelo README (PL-009).
3. **Tratar as limitações dos dados como requisitos de projeto**, e não pendências, e deixar o scoring para a Arquitetura em vez de executar T-A e T-B (PL-013, PL-014).
4. **FastAPI + Next.js contra os três agentes**, e **não aceitar a convergência deles como prova** (PL-018 e PL-019).
5. **Retirar a idade da ordenação** em vez de apostar em uma direção (PL-022).
6. **CSVs fora do repositório e prazo como estimativa**, recusando o gatilho de 2 h que cortaria o front (PL-024).
7. **Não aprovar a regra A só pelo ganho**: exigir incerteza, sensibilidade e a separação entre comprovado e hipótese (PL-034).
8. **Fronteira entre back e front:** decisão no back, apresentação no front (PL-037).
9. **Personas isoladas, sem roteiro**, tratando opinião simulada como não evidência (PL-049).
10. **Recusar a nota de 10 a 100** e manter "score" fora do vocabulário da tela (PL-051).
11. **Trocar a ordem dos grupos**, contra a cautela da IA, **declarando-a como aposta de produto** (PL-052).
12. **Priorização assistida:** transformar o buraco dos dados em recurso do produto, com pontos por resposta, nada gravado no servidor e pesos declarados como hipótese (PL-054 a PL-056).

## 6. Erros da IA e meus

**Da IA, pegos por mim ou pela revisão:**

- **Auditoria (PL-008):** `UnboundLocalError`, 81,3% → 81,2%, sonda de vazamento no mês errado do trimestre, carga confundida com truncamento, afirmações de AUC e Brier sem sustentação.
- **Termos que sugeriam o que a base não diz:** "zumbi" (o dado mede idade, não abandono); "nenhuma foi ganha acima de 138 dias" (sugeria perda; virou "sem desfecho registrado"); "Retome o contato" e "N dias do limite" (PL-050).
- **Escopo:** escreveu no `discovery.md` sem autorização (PL-016, revertido; como o arquivo é ignorado pelo git, só a contagem de linhas prova a reversão); moveu `data/raw` para `/tmp` sem perguntar (devolveu e conferiu o hash).
- **Arquitetura:** defendeu textos de tela no núcleo (PL-037); condensou o PRD e deixou uma lacuna (PL-025).
- **Números:** "44% a 62%" omitia uma célula (PL-022); Val@10 mudou de cálculo entre rodadas (PL-034); a consolidação das personas tinha quatro imprecisões; defeitos da Inteligência pegos na conferência (taxa arredondada duas vezes, largura do painel, filtro de vendedor sem restringir gerente e escritório).
- **Agentes não independentes:** os três ADRs partiram dos mesmos documentos.

**Meus:**

- **Pesos que somavam 110** onde eu escrevi "Total 100" (PL-056).
- **Números da Anna** lidos em uma tela que não guardei (PL-052).
- **Perguntas da IA que não entendi** ("O que é hoje", "papel do momento"): respondi "não entendi" três vezes, e o fluxo só destravou com exemplos e um relatório do zero (PL-055).
- **Checagem de escopo depois do commit:** perguntei se o fluxo de commit foi seguido e a IA reconheceu que só rodou a checagem formal depois de commitar; a proteção anterior era indireta (PL-052).
- **Trabalho antigo no primeiro commit da Etapa 10:** arquivos da Inteligência (ADR-007) nunca versionados entraram junto com o contrato v7; as mensagens dizem isso. A Inteligência foi commitada em outra conversa, sem a revisão pedida.
- **Pasta `.claude/` criada na raiz** pelo Claude Code na Etapa 00; identificada antes de qualquer commit e removida.

## 7. O que este processo não comprova

- **Não há usuários reais.** As seis personas são agentes do mesmo modelo; os testes rodaram numa versão que já mudou, e um segundo conjunto de relatórios existiu e está fora do repositório. O teste com 3 a 5 pessoas não técnicas e a validação da priorização assistida com 5 vendedores reais não foram feitos.
- **Não há efeito comercial medido.** O backtest mede quem teria ganhado de qualquer forma; só um piloto com grupo de controle mostra se trabalhar a lista vende mais.
- **A regra A depende de negociações sem desfecho**, e a ordem dos grupos e os pesos da priorização assistida são hipóteses (PL-034, PL-052, PL-056).
- **Muitas conferências rodaram fora do repositório** (sondas, consultas diretas, conferências do PRD, a sonda de gradient boosting com AUC 0,503); só a auditoria principal e o backtest são reproduzíveis no projeto.
- **Não anexei** exports de chat nem gravação de tela, e dos PL-060 e PL-061 só tenho as mensagens de commit, não os prompts. O texto de cada interação traz trechos representativos dos prompts, com resposta e decisão; **não é uma transcrição integral** (a IA tinha "linhas omitidas" em vários prompts longos).
- **Os 505 testes** (221 do back e 284 do front) mostram que a solução se comporta como especificado, não que a ordem maximiza vendas.

## 8. Reflexão final

**Onde a IA mais ajudou.** Na auditoria dos dados e no backtest, que eu não faria nesse tempo; na construção em ciclos curtos, com verificação a cada um; e na simulação de usuários, que me mostrou problemas que eu, por conhecer tudo, não via.

**Onde meu julgamento fez diferença.** Em recusar a nota e declarar o limite dos dados; em contestar a IA quando a evidência não sustentava a ideia (Lost, "zumbi", a convergência dos agentes, a regra A pelo ganho); em transformar o buraco dos dados na priorização assistida; e em declarar como hipótese o que é aposta minha (a ordem dos grupos e os pesos).

**O que faria diferente.** Reduziria o tempo e o escopo do discovery e construiria mais cedo, para ter mais tempo de ajustar o que as personas mostraram. Também deixaria de documentar interações rotineiras (fluxo de Git, revisões de formato) com o mesmo peso das decisões.

## 9. Índice das 61 interações

Todas as interações com IA, por etapa. A coluna "Commits" traz os commits da época quando existem.

### Etapa 00 — Setup

| PL | Interação | Resultado | Commits |
| --- | --- | --- | --- |
| PL-001 | Revisão independente do workspace antes do primeiro commit | Achou que `submissions/` é ignorada (exige `git add -f`) e que faltavam Setup e Lógica no README; acrescentei ao template o campo "Decomposição do Problema". | |
| PL-002 | Fluxo de commit seguro para a pasta da submissão | Preferi comandos manuais, que eu executo e confiro, ao script automático da IA; fluxo em `docs/commit-flow.md` (DEC 001). | `85339bb` |

### Etapa 01 — Business Discovery

| PL | Interação | Resultado | Commits |
| --- | --- | --- | --- |
| PL-003 | Análise do briefing e Business Decision & Value Map | Episódio em 4.1. | |
| PL-004 | Preenchimento da seção 1 do `discovery.md` | Template mantido; stakeholders não citados no briefing marcados como "inferidos". | |

### Etapa 02 — Domain & Value

| PL | Interação | Resultado | Commits |
| --- | --- | --- | --- |
| PL-005 | Relatório de domínio do briefing e do mapa de decisões | Usado como insumo dos mapas, sem tratá-lo como conclusão. | |
| PL-006 | Construção dos cinco mapas de discovery | Aprovados como primeira versão, sujeitos às correções do PL-007. | |
| PL-007 | Revisão dos mapas e incorporação ao `discovery.md` | Corrigi conceitos mesclados, a decisão de forecast ausente e a mistura entre limitação do dado e distorção; seção 2 preenchida. | |

### Etapa 03 — Data Discovery

| PL | Interação | Resultado | Commits |
| --- | --- | --- | --- |
| PL-008 | Auditoria reproduzível dos dados | Episódio em 4.1. | |
| PL-009 | Questionamento do script e das definições de Lost, "zumbi" e vazamento | Episódio em 4.1. | |
| PL-010 | Síntese do Data Discovery | Registrada só na seção 3; T-A e T-B ficaram como testes não executados. | |
| PL-011 | Avaliação do alinhamento entre as etapas do discovery | Usada como guia da consolidação (PL-013). | |
| PL-012 | Avaliação do discovery e relatório de handoff | Base para consolidar; as regras de scoring ficam para a Arquitetura. | |
| PL-013 | Decisões de consolidação do discovery | Scoring decidido na Arquitetura; T-A e T-B não executados; usuário central é o vendedor e a decisão central é qual deal trabalhar na segunda-feira. | |
| PL-014 | Reenquadramento das limitações de taxa de ganho e KPIs | Limitações viram requisitos de projeto, não pendências. | |

### Etapa 04 — Prioritization

| PL | Interação | Resultado | Commits |
| --- | --- | --- | --- |
| PL-015 | Matriz de oportunidades de produto | 13 oportunidades, 6 P0 candidatas e 10 incertezas; a IA escreveu no `discovery.md` sem autorização (PL-016). | |
| PL-016 | Correção de rota: escrita não autorizada no `discovery.md` | Reversão pedida e conferida por contagem de linhas (1.419); relatório mantido no chat. | |
| PL-017 | Registro estruturado em `architecture.md` | `architecture.md` como veículo; `discovery.md` e `data-audit.md` ficam sem alteração. | |

### Etapa 05 — Baseline & Architecture

| PL | Interação | Resultado | Commits |
| --- | --- | --- | --- |
| PL-018 | ADR com três propostas independentes | Episódio em 4.2. | |
| PL-019 | Defesa da estratégia contra 7 abordagens, pesquisa e empresa/região | Questionei a convergência dos agentes; empresa e região viram filtros fora do cálculo; ML e uplift rejeitados no MVP. | |
| PL-020 | Nome da estratégia e escrita dos 3 ADRs | Limite de 138 d global e parametrizável; faixas de valor como política provisória. | |
| PL-021 | Revisão adversarial do P0 | Troca de rótulos e opção A no desempate (PL-022); falha 1 reclassificada como artefato do dado (PL-023). | |
| PL-022 | Troca de rótulos e retirada da idade da ordenação | Episódio em 4.2. | |
| PL-023 | Conta nula como artefato da base | Aviso único no cabeçalho, no lugar de um por linha; causa registrada como hipótese no ADR-002. | |

### Etapa 06 — MVP Definition

| PL | Interação | Resultado | Commits |
| --- | --- | --- | --- |
| PL-024 | PRD enxuto e congelamento do escopo | Episódio em 4.3. | |
| PL-025 | Teste de mesa do PRD e aplicação das correções | Episódio em 4.3. | |

### Etapa 07 — Development

| PL | Interação | Resultado | Commits |
| --- | --- | --- | --- |
| PL-026 | Plano de build em quatro specs | Episódio em 4.3. | |
| PL-027 | Spec 1: fatia vertical na CLI e correção do commit-flow | Nenhum commit sem a minha aprovação explícita. | `9e1927b`, `dce69ec` |
| PL-028 | Histórico de commits por etapa, sem o process log | Três commits de documentação e dois da Spec 1; o log fica fora até ficar pronto. | `dee21e9`, `ecfcc7f`, `137d094`, `9e1927b`, `dce69ec` |
| PL-029 | Spec 2: explicação "Por que está aqui" | Commit aprovado. | `18e9b6a` |
| PL-030 | Spec 3: erros, bordas e API | Commit aprovado, sem o process log. | `e02d963` |
| PL-031 | Spec 4: tela, ensaio da jornada e README | Commit aprovado, sem o process log. | `ada3db2` |
| PL-032 | Backtest temporal e armadilha do mês de fechamento | Episódio em 4.3. | `fe4e318` |

### Etapa 08 — Validation & Iteration

| PL | Interação | Resultado | Commits |
| --- | --- | --- | --- |
| PL-033 | Auditoria crítica do scoring e da priorização | Entregáveis só no chat; exigi respostas metodológicas antes de aprovar a abordagem A (PL-034). | |
| PL-034 | Revisão crítica da abordagem A antes de aprovar | Episódio em 4.2. | |
| PL-035 | Correção do backtest antes de mexer no produto | Backtest corrigido antes de qualquer mudança de produto, em commit separado. | `c0b64da` |
| PL-036 | Interrogação dos achados em linguagem de negócio | A ordem segue por preço no grupo; "acima de 138 d" é descrito como sem desfecho, nunca como perdido. | |
| PL-037 | Fronteira entre back e front: contrato orientado a dados | Episódio em 4.2. | |
| PL-038 | Plano e execução do contrato (F1 a F6) | Três commits: backtest, contrato e documentação. | `734893d`, `c0b64da`, `dd9eb32` |
| PL-039 | Rankio: design system, navegação central e páginas | Três commits: front, back v4 e documentação. | `8b0e8d4`, `b0ceef7`, `f054dab` |
| PL-040 | Revisão visual e Evidência em duas linguagens | Um commit com os ajustes. | `735e9fd` |
| PL-041 | Equipe em abas | Commit separado, antes de começar a regra A. | `94ca259` |
| PL-042 | Auditoria da lógica alterada na sessão | Preparou a evolução para a regra A. | |
| PL-043 | Regra A: plano, decisão honesta e contrato v5 | Regra A, com Prospecting depois das Engaging; um commit de código e um de documentação. | `ab0f56f`, `55869f8` |
| PL-044 | A solução vista pela Head de RevOps | Sem mudança de código; o pedido da Inteligência já estava decidido. | |
| PL-045 | Inteligência comercial: proposta confrontada com os dados e contrato v6 | Página descritiva, sem previsão e sem ranking de pessoas; escolhi o escopo completo (P0 e P1) contra a recomendação da IA. | `a17471f` |
| PL-046 | Iterações de tela da Inteligência | Quatro mudanças aplicadas; números antes do texto, filtros num botão e análises em painéis. | `44298a5`, `a17471f` |
| PL-047 | Análises sem implementação: filtros, posição de Qualificar e "O que decidir" | Só análise; a posição de Qualificar foi decidida no PL-052. | |

### Etapa 09 — Validation com personas

| PL | Interação | Resultado | Commits |
| --- | --- | --- | --- |
| PL-048 | Avaliação do PRD: o que foi implementado e o que falta | Quatro P0 implementados e verdes (219 testes no back, 176 no front); pendências: README ainda no template, teste de compreensão não feito, política de faixas sem validação da Head, `/api/intelligence` com 252 a 337 ms contra o limite de 300 ms. | |
| PL-049 | Avaliação multiagente com seis personas comerciais | Episódio em 4.4. | |

### Etapa 10 — Correção pelas personas e priorização assistida

| PL | Interação | Resultado | Commits |
| --- | --- | --- | --- |
| PL-050 | Plano da Persona 1 e teste da conta ausente | "O que verificar agora" no lugar do próximo passo; filtro neutro de conta; a IA retirou as 4 propostas prescritivas. | |
| PL-051 | "Minha sessão de trabalho" descartada e score de 10 a 100 vetado | Retirei a sessão de trabalho e abandonei a barra de score. | |
| PL-052 | Ordem dos grupos, scoring intacto e ciclo da Anna | Episódio em 4.4. | `a17471f`, `44298a5`, `007b677`, `65eda15`, `04f2289` |
| PL-053 | Persona 2: botão de definição dos grupos e linguagem estatística | Botão "O que significa cada grupo?" e linguagem comum. | `36a68a8`, `2676b65` |
| PL-054 | Persona 3: empate no topo e da ideia à especificação | Faixa por página, frase em Confirmar e README; segui pela minha ideia de avaliação interativa. | `fa23ae9` |
| PL-055 | Escopo da priorização assistida e rodadas de perguntas | Motor no front (ADR-010), "Não sei" em bloco à parte; mandei recomeçar a estruturação do zero. | |
| PL-056 | Virada para pontos de qualificação | Episódio em 4.4. | |
| PL-057 | Implementação da priorização assistida e commits | Dois commits; reteste e vendedores reais ficam para depois. | `fa23ae9`, `4140f8d` |
| PL-058 | Botão branco e remoção da avaliação | Remoção por oportunidade, com confirmação. | `76f10a8` |
| PL-059 | Personas 4 a 6, revisão antes do commit e dois commits | Botões escuros e AC-4.4 corrigidos; dois commits em vez de cinco. Não implementei o roteiro de piloto da persona 5 nem o título de faixa com valores da persona 4. | `76f10a8`, `2b2945b` |

### Etapa 11 — Delivery

| PL | Interação | Resultado | Commits |
| --- | --- | --- | --- |
| PL-060 | Título da faixa, pasta no formato do guia e README | Link no título da faixa; pasta no layout do guia. | `9cab309`, `5feecb3`, `c5cd5f8`, `5bfbe37` |
| PL-061 | Painel na linha, cruzamentos e ajustes de uso | "Por que está aqui" na própria linha, priorização assistida em diálogo e cruzamentos na Inteligência. | `aa67cdd`, `56bbb01` |

## 10. Evidências e resumo de execução

O guia aceita narrativa escrita e histórico do git, sozinhos ou combinados. Uso este documento, o histórico do git e capturas de tela da versão final.

| Indicador | Resultado |
| --- | --- |
| Período | 14/10/2026 12:55 a 19/10/2026 14:24 (Etapas 00 a 11) |
| Interações com IA documentadas | 61 (PL-001 a PL-061), todas no índice da seção 9 |
| Commits | 41 na branch `submission/alice-dantas` (`85339bb` até o `HEAD`), só em `submissions/alice-dantas/`; os 4 últimos são a revisão final da entrega |
| Testes (19/10/2026) | `pytest` 221 e `vitest` 284 passam, `tsc` sem erros |

**Entregáveis:** solução em `solution/` (núcleo Python, CLI, API FastAPI e tela Next.js); README da submissão no template; documentação em `docs/` (PRD, discovery e ADRs condensados, auditoria dos dados, design system, testes com personas) e notas técnicas em `solution/README.md`; este log.

### Histórico do git

```bash
git log --reverse --date=format:'%d/%m %H:%M' --format='%h %ad %s' 85339bb^..HEAD
```

| Etapas | Commits |
| --- | --- |
| 00 — Setup | `85339bb` chore: initialize challenge structure |
| 01 a 06 — Discovery, auditoria, arquitetura e PRD | `dee21e9` discovery · `ecfcc7f` data-audit · `137d094` architecture (ADR-001 a 003) e PRD |
| 07 — Núcleo, API, tela e backtest | `9e1927b`, `dce69ec` (Spec 1) · `18e9b6a` (Spec 2) · `e02d963` (Spec 3) · `ada3db2` (Spec 4) · `fe4e318` (backtest) |
| 08 — Contrato, Rankio, regra A e Inteligência | `734893d`, `c0b64da`, `dd9eb32` (contrato e backtest corrigido) · `b0ceef7`, `f054dab`, `8b0e8d4` (Rankio v4) · `735e9fd` · `94ca259` · `ab0f56f`, `55869f8` (regra A, contrato v5) |
| 10 — Personas e priorização assistida | `a17471f`, `44298a5`, `007b677` (contrato v7) · `65eda15`, `04f2289` · `36a68a8`, `2676b65` · `fa23ae9`, `4140f8d` (priorização assistida) · `76f10a8`, `2b2945b` |
| 11 — Delivery | `9cab309` · `5feecb3` (pasta no formato do guia) · `c5cd5f8` · `5bfbe37` (README) · `aa67cdd` · `56bbb01` |
| Revisão final (19/10) | Os 4 últimos commits (`git log -4`): correção do PRD e do data audit, nova versão deste log com as capturas, timeout do `vitest` e ajuste final do texto do log |

### Capturas de tela

Capturadas em 19/10/2026, com a API e a tela rodando localmente sobre os dados reais (versão do commit `56bbb01`). As respostas de exemplo da priorização assistida nas capturas 05 e 06 são ilustrativas.

| Arquivo | O que mostra |
| --- | --- |
| [01-carteira-zane-levy.png](screenshots/01-carteira-zane-levy.png) | Carteira da Zane Levy: "O que verificar agora", empatadas no topo de Focar e abas dos grupos |
| [02-por-que-esta-aqui.png](screenshots/02-por-que-esta-aqui.png) | Painel "Por que está aqui" na linha de `01XZ9CRY` |
| [03-carteira-darcel-empates.png](screenshots/03-carteira-darcel-empates.png) | Carteira da Darcel Schlecht, sem Focar: abre em Qualificar com empatadas |
| [04-selecao-para-avaliar.png](screenshots/04-selecao-para-avaliar.png) | Três empatadas marcadas e a barra "Avaliar estas oportunidades" |
| [05-avaliacao-perguntas.png](screenshots/05-avaliacao-perguntas.png) | Priorização assistida, etapa 2: as sete perguntas, com "Não sei" |
| [06-priorizacao-assistida-resultado.png](screenshots/06-priorizacao-assistida-resultado.png) | Etapa 3: ordem por pontos, quebra por pergunta e aviso de que a ordem oficial não mudou |
| [07-equipe.png](screenshots/07-equipe.png) | Equipe, com filtros de gerente e escritório |
| [08-inteligencia.png](screenshots/08-inteligencia.png) | Inteligência comercial |
| [09-evidencia.png](screenshots/09-evidencia.png) | Evidência: o que a base permite afirmar sobre a regra e o que não permite |
| [10-como-funciona.png](screenshots/10-como-funciona.png) | Como funciona: grupos, limites de idade e regra de ordem |
| [11-carteira-celular-375px.png](screenshots/11-carteira-celular-375px.png) | Carteira em 375 px |

### Outros registros

- Relatos das seis personas e a consolidação: `docs/testes-personas/`.
- Auditoria dos dados e backtest reproduzíveis: `solution/data/processed/` e `solution/scripts/`.
- Decisões de arquitetura, PRD e design system: `docs/`.
