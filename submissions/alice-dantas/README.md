# Submissão — Maria Alice Dantas — Challenge 003

## Sobre mim

- **Nome:** Maria Alice Dantas
- **LinkedIn:** [Alice Dantas](https://www.linkedin.com/in/alice-dfl/)
- **Challenge escolhido:** 003 — Lead Scorer (Vendas / RevOps)

---

## Executive Summary

O **Rankio** é uma ferramenta de priorização de oportunidades, que ajuda o vendedor a organizar sua carteira para focar em deals que se enquadram na janela histórica de maior quantidade de fechamentos da empresa, evitando que boas oportunidades esfriem. A ideia é que o vendedor abra a carteira na segunda de manhã e saiba por onde começar. Para construir, auditei os 8.800 registros do CRM: produto, vendedor e conta não separam quem ganha (AUC perto de 0,5). Por isso o Rankio não inventa uma nota: ordena por regras declaradas, a partir da idade da negociação. No backtest, essa regra captura 58,4% do valor ganho nas 10 primeiras de cada vendedor, contra 53,8% de "só valor de tabela" e 23,2% do sorteio, mas parte da vantagem vem de negociações que nunca fecham.
Como a base não tem histórico de atividades das negociações, algumas oportunidades ficam empatadas, e para isso criei a **priorização assistida**: o vendedor responde 7 perguntas rápidas e as empatadas são reordenadas por pontos. A principal recomendação é limpar o cadastro (68% das abertas sem cliente e 1.291 acima de 138 dias) e rodar um piloto com grupo de controle antes de afirmar qualquer efeito.

---

## A Solução

O Rankio responde, em uma tela, à pergunta que a Head de RevOps fez no briefing: **"como priorizar os deals?"**

| O que o briefing pede | O que o Rankio entrega |
| --- | --- |
| "Gastam tempo demais em deals que não vão fechar" | As 1.291 abertas acima de 138 dias (a venda mais longa já fechada) ficam separadas em **Confirmar**, com a ação "verifique no CRM se ainda está ativa". O vendedor deixa de tratá-las como carteira viva. |
| "Deixam oportunidades boas esfriar" | **Focar** reúne as abertas dentro do tempo em que 90% das vendas ganhas fecharam (até 106 dias), e **Acompanhar** as que já passaram disso. A idade aparece em cada linha. |
| "Não um modelo no Jupyter": precisa **rodar** | Núcleo Python, CLI, API FastAPI e tela Next.js; 221 testes de back e 284 de front passam ([Como rodar](#como-rodar)) |
| Usar os **dados reais** | As 4 tabelas do CRM, 8.800 linhas após cada junção, 2.089 abertas (`check-data`) |
| **Lógica de priorização**, não só valor | 5 grupos pela idade da negociação, ordem declarada dentro de cada um e desempate pelo vendedor ([Regra de scoring](#regra-de-scoring)) |
| O vendedor entende o **porquê** | A primeira tela é a carteira do vendedor: cartão **"O que verificar agora"** e painel **"Por que está aqui"**, em cerca de 1 minuto, com os números que decidiram e o que o sistema não vê |
| Filtro por vendedor, gerente e região (bônus) | Carteira por vendedor; página Equipe com filtros de gerente e escritório, que se restringem entre si |

As **cinco páginas** do Rankio, cada uma com a pergunta que responde. O núcleo do brief é a Carteira (lista, explicação e filtros); as outras quatro e a priorização assistida são extras para o gestor e a Head de RevOps:

| Página | Para quem | Pergunta |
| --- | --- | --- |
| Carteira | Vendedor | Qual é o meu próximo passo? |
| Equipe | Gestor e Head de RevOps | Como a equipe está distribuída? |
| Inteligência | Head de RevOps | Onde o processo pode melhorar? |
| Evidência | Head de RevOps | A lista ajuda a escolher onde investir? |
| Como funciona | Todos | Como a lista é montada? |

<a id="regra-de-scoring"></a>
### Regra de scoring e por que ela foi escolhida

**O ponto de partida.** A auditoria mostrou que o único sinal legítimo nos dados é **há quanto tempo a negociação está aberta**. O sinal mais forte que o dataset oferece, o mês de fechamento (AUC 0,64), é vazamento: só existe depois do resultado. Por isso o Rankio **não calcula probabilidade nem nota**: classifica e ordena por regras declaradas ([ADR-001](./docs/architecture.md#adr-001)).

**Regras avaliadas.** Todas foram comparadas no mesmo backtest temporal (7 cortes, as 10 primeiras de cada vendedor, desfecho em 90 dias; [relatório](./solution/data/processed/backtest_report.md)). "Val@10" é a parte do valor ganho que cai nas 10 primeiras.

| Regra | Val@10 | AUC médio | Leitura |
| --- | --- | --- | --- |
| Aleatório | 23,2% | 0,510 | Piso de referência |
| Taxa de ganho por produto | 14,0% | 0,494 | Pior que o sorteio: o produto não separa |
| Só idade (mais nova primeiro) | 26,6% | 0,616 | Separa melhor, mas ignora o valor |
| Só valor de tabela | 53,8% | 0,505 | Forte em valor, nenhuma habilidade |
| Regra anterior: até 138 dias, depois preço | 56,9% | 0,574 | Focar misturava negociações de 10 e de 130 dias |
| **Regra A (adotada): até 106 dias, até 138 dias, depois preço** | **58,4%** | 0,604 | Melhor em valor e em acerto |

Também foram descartados, ainda na arquitetura: pontos ponderados, segmentos estatísticos (sem sinal), valor esperado (vira ranking por produto, com empates em massa), nota contínua de 0 a 100 e uplift.

**Critérios usados para escolher:**
1. **Só campos legítimos.** Nada que só exista depois do resultado (data e valor de fechamento, ciclo, mês).
2. **Explicável.** Cada posição precisa ser justificada com campos que o vendedor confere no CRM.
3. **Resultado no backtest temporal**, com intervalo de confiança, e não em um único corte.
4. **Perder pouco no pior caso.** Sem as negociações que nunca fecham, "só valor de tabela" fica 1,0 ponto à frente da regra A; a regra anterior ficaria 1,5 ponto atrás.
5. **Não prometer o que a base não sustenta:** sem chance de fechar por oportunidade.

**Por que a regra A.** Ela vence a regra anterior em valor (+1,5 ponto) e em acerto (+1,7 ponto) e tira do topo de Focar as negociações entre 106 e 138 dias. Os dois limites são calculados só com o que se sabia em cada corte: **106 dias** é o tempo em que 90% das vendas ganhas fecharam, e **138 dias** é a venda mais longa já fechada. Nenhum limite fixo a supera quando o limite é escolhido sem olhar o teste ([ADR-006](./docs/architecture.md#adr-006)).

| Grupo | Quem entra | Com os dados auditados |
| --- | --- | --- |
| **Focar** | Em andamento, abertas há até 106 dias | 157 |
| **Qualificar** | Em prospecção, sem data de início | 500 |
| **Acompanhar** | Em andamento, acima de 106 e até 138 dias | 141 |
| **Confirmar** | Em andamento, acima de 138 dias (a idade não prova que o negócio terminou) | 1.291 |
| **Completar** | Falta produto, preço ou data; o item diz o que corrigir | 0 |

A ordem dos grupos é Focar, Qualificar, Acompanhar, Confirmar, Completar. Dentro de cada grupo: faixa de valor de tabela, depois preço de tabela, depois ID só para a ordem ser estável. A idade aparece, mas não muda a ordem. Oportunidades do mesmo grupo e produto são **empate** e aparecem agrupadas, sem numerar uma como melhor. Cada oportunidade tem exatamente **dois motivos**, os que decidiram, e o texto é escrito a partir de códigos que um teste reconstrói para as 2.089 abertas.

### Escolha de stack

Núcleo Python (pandas) sem dependência de web, API FastAPI fina, front Next.js e CLI. Separei as camadas para a solução poder **escalar**: trocar o CSV por uma fonte viva, atender mais usuários ou mais telas sem reescrever a regra. E para que, **quando os dados do pipeline estiverem mais completos** (atividade, histórico de estágio), um modelo possa entrar no núcleo sem mexer na API nem na tela, porque o contrato devolve só códigos e números ([ADR-003](./docs/architecture.md#adr-003) e [ADR-004](./docs/architecture.md#adr-004)). Streamlit seria mais simples; mantive esta stack contra a recomendação dos agentes de IA e aceitei o custo de dois runtimes.

### Duas decisões que mudam o jogo

#### 1. Priorização Assistida: score baseado no método BANT

**O problema.** A Darcel Schlecht tem 194 abertas e **13 delas empatadas** em GTX Plus Pro, valor de tabela 5.482. A base não tem atividade, estágio nem contato para separá-las, e qualquer ordem que o sistema escolhesse seria só o código do ID. Os dados têm um buraco, e a pergunta "por qual eu começo?" ficaria sem resposta.

**A saída.** Em vez de fingir que o dado existe, o Rankio **pergunta a quem sabe**. O vendedor escolhe de 2 a 5 oportunidades empatadas e responde 7 perguntas curtas, sempre com **"Não sei"** disponível:

| Pergunta | Peso |
| --- | --- |
| O cliente demonstrou interesse ou respondeu recentemente? | 20 |
| O cliente informou quando pretende decidir? | 20 |
| O cliente confirmou qual problema quer resolver? | 15 |
| Existe uma razão concreta para comprar em breve? | 15 |
| O cliente indicou orçamento ou aprovação? | 15 |
| Você sabe quem decide e tem acesso? | 10 |
| Existe uma próxima ação combinada? | 5 |

O resultado é uma ordem por **pontos de qualificação declarada (0 a 100)**, com a quebra por pergunta, o que ainda falta saber e **o que fazer agora** com cada oportunidade ("Definir continuidade", "Verificar o compromisso", "Investigar primeiro").

Um exemplo ilustrativo (respostas inventadas, só para mostrar a conta):

| Oportunidade | Pontos confirmados | Até onde iria | O que o Rankio diz |
| --- | --- | --- | --- |
| A (tudo confirmado) | 100 | 100 | Primeira da lista |
| B (3 respostas "Não sei") | 47 | 87 | Segunda, com a faixa 47 a 87 visível |
| C (necessidade ainda em investigação) | 27 | 27 | Terceira |
| D (tudo "Não sei") | 0 | 100 | **À parte, sem posição:** "investigar primeiro" |

O que cuida para esse número não enganar:
- **"Não sei" vale 0 ponto confirmado, mas não é um "não".** A tela mostra a faixa, até onde a pontuação iria se o que se desconhece se confirmasse.
- **Nada é gravado no servidor.** As respostas ficam só no navegador do vendedor.
- **É uma camada declarada, separada do scoring** ([ADR-010](./docs/architecture.md#adr-010)). A ordem oficial da Carteira não muda.
- **Nunca aparece como chance de fechar.** Sem porcentagem, sem cor de temperatura, com o aviso fixo "pesos iniciais, a validar".

#### 2. Personas simuladas para validar a entrega

**O problema.** Eu não tinha 35 vendedores à mão para testar a ferramenta antes de entregar. E o risco de quem constrói é achar tudo claro porque conhece tudo.

**A saída.** Montei um teste com **seis agentes de IA independentes**, um por vez, cada um com papel e missão próprios, usando o Rankio no navegador, sem acesso a código, documentos nem ao relato dos outros:

| Persona | O que testou |
| --- | --- |
| Boris Faz, vendedor iniciante | "O que eu faço na segunda?" |
| Kary Hendrixson, vendedora experiente | A ordem faz sentido ou é o que eu já faria sozinha? |
| Darcel Schlecht, vendedora sobrecarregada | Uma carteira sem nenhuma oportunidade em Focar |
| Melvin Marxen, gerente regional | A visão da equipe serve para a reunião de segunda? |
| Head de RevOps | Dá para decidir um piloto? Os números se leem? |
| Diretor comercial | O que isso diz sobre vender mais? |

**O que saiu.** Os seis chegaram sozinhos ao painel "Por que está aqui" em cerca de 1 minuto e os seis fecharam em **"resolve parcialmente"**. Foi o relato da Darcel que deu origem à priorização assistida. Por causa dos relatos, mudei: empates sem falsa ordem ("sem ordem entre si"); orientação própria para carteira sem Focar; textos que dizem que "Confirmar é limpar a carteira, não prever venda"; a ordem dos grupos (Qualificar antes de Acompanhar e Confirmar, contrato v7); o botão "O que significa cada grupo?", busca e filtros; e linguagem de negócio na Inteligência. Relatos completos em [docs/testes-personas](./docs/testes-personas/).

### Como rodar

**Requisitos:** Python 3.9 ou superior e Node 22.12 ou superior. Sem banco, sem segredo e sem LLM.

**Dados:** os CSVs não estão no repositório (o dataset é CC0). Baixe o [CRM Sales Predictive Analytics](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics) no Kaggle e copie `sales_pipeline.csv`, `products.csv`, `sales_teams.csv` e `accounts.csv` para `solution/data/raw/`.

**Comandos** (a partir da raiz desta pasta; no Windows, troque `.venv/bin/` por `.venv\Scripts\`):

```bash
cd solution
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m leadscorer check-data                    # confere arquivos, hash e junções
.venv/bin/pytest                                             # testes do back
.venv/bin/python -m leadscorer list --seller "Zane Levy"     # a lista de um vendedor, sem Node
.venv/bin/python -m leadscorer explain --id 01XZ9CRY         # "Por que está aqui"
.venv/bin/uvicorn api.main:app --port 8000                   # API (deixe rodando; contrato em /docs)
```

Em outro terminal, para a tela:

```bash
cd solution/web
npm ci && npm run dev                                        # tela em http://localhost:3000
npm run typecheck && npm test                                # testes do front, sem a API no ar
```

**O que você deve ver:** `check-data` mostra 8.800 linhas após cada junção, hash 4 de 4 igual ao auditado e 2.089 abertas. Sem os CSVs, todos os comandos param com uma mensagem que diz qual arquivo falta e onde baixá-lo.

**Roteiro de 2 minutos:**
1. Abra `localhost:3000` e escolha **Zane Levy**. O cartão "O que verificar agora" mostra 2 oportunidades empatadas no topo (`01XZ9CRY` e `FZWU2I30`, GTX Plus Pro de 5.482).
2. Abra `01XZ9CRY`: "aberta há 104 dias; 90% das vendas ganhas fecharam em até 106 dias", o valor de tabela e o que o sistema não vê.
3. Troque para **Darcel Schlecht**. Ela não tem nenhuma em Focar, então a tela abre em Qualificar, com 13 oportunidades empatadas no topo.
4. Clique em **Avaliar estas oportunidades**, escolha 2 ou 3, responda as perguntas e veja a ordem por pontos.
5. Em **Evidência** e **Inteligência**, veja o que a base permite afirmar e o que não permite.

As camadas, o contrato da API, como regenerá-lo e os desvios do plano estão em [solution/README.md](./solution/README.md).

### Abordagem

Entendi o problema antes de abrir qualquer ferramenta: tratei o briefing como percepção a validar, não como fato, e procurei nos dados o que separa quem ganha de quem perde. Só então escolhi regras em vez de nota, e exigi evidência (backtest, incerteza e pior caso) antes de adotar a regra A. Construí em ciclos curtos, com teste de mesa antes do código e seis personas depois. Cada decisão está nos [ADRs](./docs/architecture.md), e o passo a passo, no Workflow abaixo.

### Resultados / Findings

**A solução foi verificada:** `pytest` 221 e `vitest` 284 passam, `tsc` sem erros. As 8.800 linhas se reconciliam após cada junção, e as 2.089 abertas são 157 + 141 + 1.291 + 500 + 0. Nas 2.089 há exatamente dois motivos, e um teste reconstrói o grupo e a ordem só a partir deles. CLI, API e tela entregam a mesma lista para os 35 vendedores, e nenhum termo proibido ("probabilidade", "prazo", "perdida", "score") aparece nos textos, conferido por teste. O setup foi repetido do zero em 19/10/2026.

**O que os dados dizem:**
- **Produto, vendedor, conta, setor e região não separam quem ganha** (AUC entre 0,47 e 0,57; [data-audit.md](./docs/data-audit.md)). O que separa é a idade, e só por causa das negociações que nunca recebem desfecho na base.
- **O pipeline tem um problema que a ferramenta expõe:** 1.291 das 1.589 negociações em andamento estão abertas há mais tempo do que qualquer venda já fechada; 1.425 das 2.089 abertas (68%) não têm cliente registrado; 5 dos 35 vendedores não têm nenhuma oportunidade.
- **A taxa de ganho (63,2%) não muda além do acaso em nenhum recorte:** a diferença de receita entre vendedores vem do volume e do mix, não da conversão.

**Backtest temporal** (tabela completa em [Regra de scoring](#regra-de-scoring)): a regra captura 58,4% do valor ganho nas 10 primeiras, contra 53,8% de "só valor de tabela" e 23,2% do aleatório. A leitura honesta: a regra supera o acaso com folga e fica 4,6 pontos acima de "só valor de tabela". **Mas essa vantagem vem das negociações que nunca fecham.** Sem elas, "só valor de tabela" fica 1,0 ponto à frente. A página Evidência mostra isso, e a regra A foi adotada por perder menos no pior caso, não por ganhar sempre. Valor capturado não é efeito causal: só um piloto com controle mostra o efeito de trabalhar a lista.

### Recomendações

**Para usar a ferramenta:**
1. **Comece a semana por Focar e Qualificar.** Abra a carteira na segunda, leia "O que verificar agora" e trabalhe de cima para baixo.
2. **Trate Confirmar como "verificar no CRM", não como perda.** A idade alta não prova que o negócio terminou: confirme ou encerre.
3. **Leia a idade como tempo aberto, não como chance de fechar.** A ferramenta não prevê quem vai fechar.
4. **Use a priorização assistida só para desempatar** oportunidades do mesmo grupo e produto, e lembre que os pesos são hipóteses.

**Para melhorar a qualidade dos dados** (cada item destrava um limite da ferramenta):
1. **Cliente obrigatório e data de início da negociação.** Hoje 68% das abertas não têm cliente e as 500 em Prospecting não têm data, então não dá para ordená-las por idade.
2. **Registrar atividade e mudança de estágio.** Sem isso, nenhuma ferramenta detecta esfriamento nem separa os empates.
3. **Faxina das 1.291 abertas acima de 138 dias**, confirmando ou encerrando no CRM. Sem isso, a maior parte da lista é "Confirmar".
4. **Registrar o motivo de perda, a data de extração e a definição de "Lost".** Hoje não dá para saber se o que está sem desfecho foi abandonado.
5. **Padronizar produto e deduplicar:** `GTXPro` e `GTX Pro` perdem 1.480 linhas numa junção direta, e há 461 linhas idênticas.

### Limitações

**Da ferramenta:**
- **Não prevê quem vai fechar.** A ferramenta não dá chance por oportunidade.
- **Não detecta esfriamento nem sugere reativação:** o dataset não tem atividade nem histórico de estágio.
- **Só lê o CRM.** Não escreve nele, não registra uso e não tem login: serve um usuário, com os CSVs em memória.
- **Priorização assistida:** pesos e pontos são hipóteses, as respostas ficam só no navegador (outro navegador não as vê, limpar os dados as apaga) e "Avaliada em" usa o relógio real, enquanto "hoje" nas regras é 31/12/2017.
- **A ordem dos grupos** (Qualificar antes de Acompanhar) é decisão de produto, não evidência: Qualificar não tem desfecho na base e fica fora do backtest.

**Dos dados, para o ranking das oportunidades:**
- **O valor é o preço de tabela**, e só foi validado como substituto do valor fechado nas vendas ganhas. Como nenhum outro campo separa o resultado, o topo da lista é dominado por valor.
- **Há empates em massa:** dentro de um grupo, a ordem se resume a produto e preço, e a base não traz nada para desempatar.
- **O ganho da regra A depende de 1.291 negociações sem desfecho**, acima do maior ciclo fechado. Não sabemos se foram abandonadas, são legítimas ou efeito da extração.
- **Retrato único, sem data de extração:** assumi 31/12/2017 como "hoje". Com o maior `engage_date` (27/12/2017), as negociações acima do maior ciclo seriam 77,9% e não 81,2%; com datas mais tardias, Focar esvazia rápido (84 em 31/01/2018 e 9 em 31/03/2018). Não há esforço, atividade, capacidade, custo nem metas.
- **O histórico reflete a priorização passada**, então não mostra o que aconteceria com outra ordem. Os padrões (por exemplo, 28,4% de fechamentos em fim de semana) são compatíveis com dado sintético, o que é hipótese.

**Para escalar:** fonte viva (API do CRM) no lugar do CSV; registro de ações do vendedor; log de atividade; validação da política com a RevOps; autenticação e banco se houver escrita. Antes de afirmar qualquer efeito, um **piloto com grupo de controle** (parte do time usa a lista, parte não, com a métrica definida antes: valor ganho, conversão, tempo até a primeira ação em Focar), dizendo ao time que a regra rende 4,6 pontos sobre "só valor de tabela" e perde 1,0 sem as negociações que nunca fecham. E rodar a priorização assistida com **5 vendedores reais**, uma pessoa por vez, cerca de 25 minutos e sem explicação prévia: passa se pelo menos 4 de 5 avaliarem duas empatadas sozinhos e explicarem a ordem, e nenhum ler os pontos como previsão de fechamento.

---

## Process Log — Como usei IA

> O registro, etapa por etapa, está em [process-log/PROCESS_LOG.md](./process-log/PROCESS_LOG.md): os episódios que mais mostram julgamento, as decisões contra a recomendação da IA, os erros (da IA e meus), o que o processo não comprova e o índice das 61 interações. As capturas de tela estão em [process-log/screenshots](./process-log/screenshots/).

### Ferramentas usadas

| Ferramenta | Para que usei |
| --- | --- |
| Claude Code | Discovery, auditoria dos dados, ADRs, PRD, construção do back, da API e da tela, backtest, testes, correção pelas personas e priorização assistida |
| Subagentes do Claude Code (Plan e Explore) | Três propostas independentes de arquitetura (lentes de arquiteto, de engenharia de entrega e de revisor); mapeamentos de código e dados |
| Subagentes do Claude Code (general-purpose) | **As seis personas** que usaram o Rankio no navegador |
| Navegador do app Claude Code | Ensaio das jornadas, conferência em 375, 768 e 1280 px nos dois temas e medição de contraste |
| Busca na web | Técnicas de scoring em vendas, incerteza e calibração |
| ChatGPT | Desenho do template do process log e otimização de prompts |

### Workflow

1. **Setup (00):** revisei o workspace e defini o fluxo de commit seguro ([commit-flow.md](./docs/commit-flow.md)).
2. **Business Discovery e Domain & Value (01 e 02):** transformei o briefing em problema, decisões de cada papel e hipóteses ([discovery.md](./docs/discovery.md)).
3. **Data Discovery (03):** auditei os dados com a IA e questionei cada definição ("Lost" não é "limpeza de CRM"). Produto, vendedor e conta não separam quem ganha, e a idade só separa por causa das negociações que nunca fecham ([data-audit.md](./docs/data-audit.md)).
4. **Prioritization e Baseline & Architecture (04 e 05):** matriz de oportunidades, pesquisa e três propostas de ADR; escolhi regras em vez de nota e FastAPI + Next.js contra a recomendação dos agentes ([architecture.md](./docs/architecture.md)).
5. **MVP Definition (06):** PRD e teste de mesa antes de qualquer código; três lacunas corrigidas antes de codar ([prd.md](./docs/prd.md)).
6. **Development (07):** núcleo, explicações, API e tela em quatro especificações, com backtest temporal em 7 cortes.
7. **Validation & Iteration (08):** contrato orientado a dados, o Rankio com design system, a regra A e a Inteligência comercial; só adotei a regra de idade depois de pedir incerteza e pior caso.
8. **Validation com personas (09):** seis agentes isolados usaram a ferramenta e consolidei os achados ([consolidação](./docs/testes-personas/00-consolidacao.md)).
9. **Correção e priorização assistida (10):** avaliei cada relato, corrigi o que era texto e apresentação e desenhei a camada em que o vendedor desempata (contrato v7 e ADR-010).
10. **Delivery (11):** reorganização da pasta no formato do guia, este README, o process log com evidências e as capturas de tela.

**Tempo:** ≥ 24:50 de trabalho efetivo, sem contar intervalos de 15 min ou mais (o brief estima 4 a 6 h). As etapas de discovery (00 a 06) somam ≥ 09:05, mais de um terço do total, antes da primeira linha de código. Em uma próxima versão eu encurtaria o discovery e construiria mais cedo.

### Onde a IA errou e como corrigi

- **Auditoria dos dados:** a IA errou um percentual (81,3% em vez de 81,2%), pôs a sonda de vazamento no mês errado do trimestre e afirmou coisas sobre AUC sem sustentação. A revisão cética pegou, e corrigi antes de entregar.
- **Texto de tela dentro do núcleo:** a IA defendeu escrever as frases no back. Corrigi a fronteira: o back decide, a tela escreve ([ADR-004](./docs/architecture.md#adr-004)).
- **Frases que sugeriam o que a base não diz:** "nenhuma foi ganha acima de 138 dias" sugeria perda, e corrigi para "sem desfecho registrado". Para a Persona 1, a IA propôs "retome o contato" e "está a N dias do limite", presumindo atividade e urgência que a base não registra; apontei, e ela retirou as quatro propostas.

### O que eu adicionei que a IA sozinha não faria

- **Contestei a IA nas decisões que mais pesaram:** mantive FastAPI + Next.js contra a recomendação dos três agentes; tirei a idade da ordenação; recusei "Lost = limpeza de CRM"; recusei o gatilho de 2 horas para cortar escopo.
- **Exigi evidência antes de aprovar a regra A e recusei a nota:** pedi incerteza, sensibilidade e a separação entre comprovado e hipótese, e a dependência das negociações sem desfecho virou veredito visível na Evidência. Aceitei a objeção da IA à barra de 10 a 100 e mantive "score" fora do vocabulário, porque a Head já tinha lido o valor de tabela como "nota".
- **Transformei o buraco dos dados em recurso do produto:** troquei as 3 perguntas orientativas que a IA propôs pela priorização assistida. Exigi que "nada seja gravado no backend", propus pontos por resposta no lugar do ranking por camadas e escolhi os pesos.
- **Desenhei o teste com personas para ele valer algo:** personas isoladas, sem roteiro de telas, e opinião simulada tratada como não evidência. E defini com a IA um fluxo de commit que mantém o histórico rastreável sem levar CSVs, ambientes virtuais nem segredos ([commit-flow.md](./docs/commit-flow.md)), exigindo minha aprovação antes de cada commit.

---

## Evidências

O guia aceita narrativa escrita e git history, sozinhos ou combinados.

- [x] Git history: 41 commits na branch `submission/alice-dantas`, só em `submissions/alice-dantas/` (`git log --reverse --oneline 85339bb^..HEAD`)
- [x] Narrativa escrita: [process-log/PROCESS_LOG.md](./process-log/PROCESS_LOG.md)
- [x] Capturas de tela da versão final, em 11 telas: [process-log/screenshots](./process-log/screenshots/)
- [x] Outro: relatos das seis personas em [docs/testes-personas](./docs/testes-personas/)
- [ ] Screenshots das conversas com IA, gravação do workflow e chat exports: não anexei. O process log traz trechos representativos dos prompts, com a resposta e a decisão de cada episódio.

---

_Submissão enviada em: 19/10/2026_
