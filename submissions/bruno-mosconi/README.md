# Submissão — Bruno Mosconi — Challenge 003

## Sobre mim

- **Nome:** Bruno Mosconi
- **LinkedIn:** https://www.linkedin.com/in/bruno-mosconi
- **Challenge escolhido:** 003 — Lead Scorer

---

## Executive Summary

"Onde focar" é o app que o vendedor abre na segunda de manhã: ele mostra por qual negócio começar e por quê, numa frase com o mesmo número da conta. O gestor vê onde a equipe travou. Os dados mostram que 82% do valor dos 1.589 negócios com data (US$ 3,2 mi de US$ 3,9 mi, a preço de lista) está aberto há mais de 138 dias, idade em que nenhum negócio da base fechou. Por isso a regra ordena pelo **potencial**: preço de lista vezes a chance de fechar, que depende só da idade. Testada no passado, os 10 primeiros de cada vendedor trouxeram 41% do que a carteira vendeu nos três meses seguintes, contra 33% ordenando por preço e 14% no sorteio. Recomendação: cada vendedor começa a semana pelos 5 primeiros, e a equipe atualiza ou dá perda nos 1.291 negócios frios.

---

## Solução

- **App publicado:** https://ai-master-challenge-solution-bruno.vercel.app
- **Rodar local:** `cd submissions/bruno-mosconi/solution && npm ci && npm run dev` (Node 22.18+; detalhes em Setup).
- **Para avaliar em 2 minutos:** na tela "Quem é você?", abra Zane Levy e o negócio nº 1 ("Ver o motivo"); depois Anna Snelling (uma semana que começa pela prospecção); depois Summer Sewald (a visão da gestora); e, por fim, "Como funciona".
- **Código:** `solution/` (React, Vite e TypeScript, sem servidor; o núcleo da regra fica em `solution/src/core/`, coberto por testes)

### Abordagem

1. **Revisar antes de construir.** Todo o material de partida tinha sido preparado com IA. Antes de escrever código, o Claude Code recalculou cada número de forma independente e revisou regras, código e documentos (`process-log/01-revisao-inicial.md`). A revisão achou um viés de sobrevivência na chance: calculada só com negócios já ganhos ou perdidos, a chance parecia subir com a idade.
2. **Corrigir a base.** A base começa cortada em março de 2017: os negócios iniciados antes só aparecem se ainda estavam abertos naquele mês. Cada um passou a entrar na conta a partir da idade que tinha em março (entrada tardia), e uma data só fica disponível no app se toda faixa de idade tem margem de erro de até 5 pontos.
3. **Testar a regra no passado** contra seis alternativas e um modelo de machine learning, com o vendedor como unidade do teste.
4. **Construir para quem usa.** Uma tela por pessoa (vendedor e gestor), com protótipos em três rodadas (duas reprovadas por mim) e testes de uso com três personas, medindo o tempo até a resposta.

### Resultados / Findings

O app em uso (prints em `process-log/screenshots/03-app/`, em 1280 e 390 px, claro e escuro):

| Tela | O que mostra | Print |
|---|---|---|
| Minha semana (Zane Levy, 31/12/2017) | O nº 1 é o GTX Plus Pro da The New York Inquirer, aberto há 21 dias: US$ 5.482 × 47% = US$ 2.577 de potencial, score 98. Motivo: "De cada 100 negócios iniciados, 47 fecharam venda." | `02-vendedor-1280-claro.webp`, `03-painel-1280-claro.webp` |
| Minha semana (Anna Snelling) | O único negócio dela com prazo tem score 0. O herói passa a ser a prospecção: 55 negócios em prospecção para iniciar contato (US$ 77.845 a preço de lista) | `11-heroi-acao-1280-claro.webp` |
| Minha equipe (Summer Sewald) | "US$ 718 mil frios na equipe. Kary concentra US$ 229 mil." O seletor "Ver a equipe de" mostra qualquer uma das 6 equipes, agrupadas por regional | `06-gestor-1280-claro.webp` |
| Como funciona | A regra numa tela, as três provas e as limitações | `09-como-funciona-1280-claro.webp` |

**O que os dados mostraram** (detalhes em `docs/analise-exploratoria.md`):
- A chance de fechar cai com a idade: 47% para negócios de 0 a 29 dias, 31% aos 90, 9% aos 120 e nenhum fechamento depois de 138.
- Vendedor, produto, regional, setor e porte da empresa não mudam a taxa de ganho entre negócios concluídos: todos os testes dão diferenças do tamanho que o acaso produz (p de 0,10 a 0,97).
- O vendedor muda quanto do funil fica parado: de 0% a 31% dos negócios iniciados há mais de 138 dias ainda estão abertos, conforme o vendedor. Isso aparece na tela do gestor, como retrato da carteira e não como ranking: os dados não separam vendedor, carteira e região.

**Checagens:**
- Distribuição em 31/12/2017, conferida na auditoria: 110 negócios quentes, 188 esfriando, 1.291 frios e 500 em prospecção, somando os 2.089 em andamento; nenhum concluído depois de 138 dias.
- `npm run check`: tipos, lint e 82 testes. Os testes conferem os números contra a análise em Python e as funções estatísticas contra o scipy.
- `npm run e2e`: 21 testes no navegador, inclusive o de que nenhuma requisição sai do próprio site.
- `npm run auditoria`: recalcula todos os números citados nos documentos.

### Lógica do score

**A regra:**

1. **A idade diz a temperatura:**
   - quente, até 89 dias;
   - esfriando, de 90 a 138;
   - frio, depois de 138, porque nenhum negócio da base fechou depois disso.
2. **O potencial decide a ordem:** preço de lista × chance de fechar, pelo histórico. A chance vem de uma faixa de idade, calculada com os negócios que chegaram àquela idade ainda abertos. Quem nunca fechou conta como não ganho.
3. **O score (0 a 100) é a posição do potencial** entre os negócios quentes e esfriando de todos os vendedores. Score 98 quer dizer mais potencial que 98% deles. O score não muda a ordem: só a diz em outra forma.

**Chance por faixa de idade, em 31/12/2017:**

| 0–29 dias | 30–59 | 60–89 | 90–103 | 104–119 | 120–138 | mais de 138 |
|---|---|---|---|---|---|---|
| 47,3% | 42,9% | 41,2% | 30,8% | 19,9% | 8,6% | 0% |

**As três listas de cada vendedor:**
- **Prioridades da semana:** quentes e esfriando, pelo potencial, com o prazo "Esfria em N dias" ou "Fica frio em N dias".
- **Atualize ou dê perda:** frios, do mais caro para o mais barato.
- **Prospecção:** só na data mais recente, porque o CRM não registra quando cada prospecção começou.

Empates são desempatados pelo ID.

**Voltar no tempo.** Numa data passada, o app reconstrói o funil e recalcula a chance só com o que se sabia naquele dia. A empresa fica oculta nessas datas: os negócios sem empresa no CRM são justamente os que continuaram abertos, então mostrar a falta de empresa entregaria o que aconteceu depois.

**O que foi testado e ficou fora:**

| Fator | Resultado | Por que ficou fora |
|---|---|---|
| Vendedor, gestor, regional, produto, setor, empresa, porte | p de 0,10 a 0,97 na taxa de ganho entre concluídos | não mudam a chance além do acaso |
| "Sem empresa" no CRM | 1.425 de 2.089 negócios em andamento sem empresa, nenhum concluído sem empresa | denuncia o desfecho |
| Mês do trimestre | 81% de ganho no último mês, contra 49% no primeiro | só se sabe depois que o negócio fecha |
| Modelo de machine learning (gradient boosting) | 43,2% contra 40,9% da regra (p = 0,33) | não ganha além do acaso e não explica o motivo |

**Validação no passado.** A lista foi montada em 31/07, 31/08 e 30/09/2017 só com o que se sabia em cada dia. A medida é quanto da receita ganha nos 90 dias seguintes veio dos 10 primeiros de cada vendedor.

| Método | Receita capturada |
|---|---|
| Machine learning (gradient boosting) | 43,2% |
| **Potencial (a regra do app)** | **40,9%** |
| Quente, depois esfriando, depois frio; dentro de cada um, por preço | 40,7% |
| Preço, com os frios no fim | 37,6% |
| Só preço | 33,2% |
| Sorteio | 14,1% |

O potencial ganha de "só preço" por +7,66 pontos (margem de erro de 3,49 a 12,62; p = 0,0004) e em cada uma das três datas. Ele empata com "quente, depois esfriando, depois frio, e por preço" (+0,12 pontos; p = 0,90). O potencial ficou porque dá a frase de motivo e o score. Com a coorte limpa, que só usa os iniciados a partir de março de 2017 e não depende da hipótese da entrada tardia, sobra só 30/09: +18,69 pontos sobre "só preço". As duas formas chegam à mesma conclusão.

**Quanto a lista se parece com a ordem por preço.** Bastante, e é bom dizer antes que a auditoria mostre. Em 31/12/2017, em média 88,6% dos 10 primeiros de cada vendedor também estão entre os 10 mais caros, e em 9 vendedores as listas são iguais. Em parte, isso acontece porque muitas listas são curtas. Pôr os frios no fim explica a maior parte do ganho sobre "só preço" (de 33,2% para 37,6%). A curva de chance soma mais +3,22 pontos (margem de erro de 0,63 a 6,41; p = 0,022), porque muda a ordem quando a idade pesa. Exemplo do Zane: o GTX Pro da Gogozoom (66 dias, US$ 4.821) fica em 2º pelo potencial e estaria em 5º pelo preço. O painel diz isso ("Pela ordem de preço, estaria em 5º").

Fonte de todos os números: `npm run auditoria` (`solution/analysis/saidas/auditoria-ts.md`).

### Setup

Requer o Node 22.18 ou superior. Na raiz do repositório clonado:

```bash
cd submissions/bruno-mosconi/solution
npm ci
npm run dev          # app em http://localhost:5173
npm run check        # tipos, lint e testes
npm run build        # build de produção em dist/
npx playwright install chromium   # só na primeira vez, para os testes de navegador
npm run e2e          # testes de navegador no build de produção
npm run auditoria    # recalcula os números dos documentos
npm run bench        # mede o núcleo com os dados multiplicados por 100 (os tempos variam com a máquina)
```

Os scripts Python de referência são opcionais; as instruções estão em `submissions/bruno-mosconi/solution/analysis/README.md`.

**URL:** https://ai-master-challenge-solution-bruno.vercel.app

A Vercel compila com o Node 24.x. O build publicado é idêntico ao do Node 22: os dois geram o mesmo nome de arquivo (`index-*.js`).

### Recomendações

1. **Segunda de manhã, cada vendedor começa pelos 5 primeiros da semana.** Na validação, os 10 primeiros da lista trouxeram 41% do que a carteira vendeu nos três meses seguintes.
2. **Limpar os frios.** São 1.291 negócios, US$ 3,2 mi a preço de lista, abertos há mais de 138 dias, idade em que nenhum negócio da base fechou. Cada vendedor confirma com o cliente ou dá perda, do mais caro para o mais barato. O funil fica menor e honesto.
3. **A regional Central precisa transformar prospecção em negócio.** Os 500 negócios em prospecção da base são todos da Central, que tem só 5 negócios quentes ou esfriando entre 11 vendedores (7 sem nenhum) e 99,2% do valor em andamento frio. East e West têm 107 e 186 negócios quentes ou esfriando e nenhuma prospecção. Nos gestores da Central, a tela da equipe mostra isso.
4. **O gestor acompanha quanto da carteira de cada vendedor esfria**, não a taxa de ganho: é o que varia entre vendedores (de 0% a 31%).
5. **Registrar no CRM a data de início das prospecções e a empresa de todo negócio.** Sem a data, a prospecção não entra na conta da chance; sem a empresa, setor e porte não podem ser testados nos negócios em andamento.

### Limitações e como escalar

**O que a ferramenta não faz:**
- **A chance é histórico, não previsão, e superestima a venda.** Em 31/07/2017, a chance média dos negócios em andamento era 52%, e 37% viraram venda até o fim do ano. O app usa a chance para ordenar, não para prever receita.
- **Hipótese da entrada tardia.** Ela supõe que o corte da base foi exatamente "os concluídos antes de 01/03/2017 saíram". Nenhuma conclusão aparece antes dessa data, e os inícios sobem de 7 para cerca de 800 por mês. Se a hipótese não valer, a coorte limpa, que não depende dela, chega à mesma conclusão.
- **A regra usa só a idade e o preço.** Sinais de atividade (e-mails, reuniões, data prevista de fechamento) não existem na base. Seriam os próximos candidatos, e só entrariam se ganhassem no teste do passado.
- **Só leitura.** O vendedor não registra "dei perda" no app; faz isso no CRM. Não há login: a escolha da pessoa fica salva no aparelho.
- **Uma foto fixa do CRM**, de 31/12/2017, com 3 datas passadas para comparação (31/07, 31/08 e 30/09/2017; a de 30/06 fica bloqueada por falta de histórico).

#### Como escalar (detalhe técnico em `docs/como-escalar.md`)

**O que já está provado**
- O cálculo não é o gargalo. Com os dados multiplicados por 100 (880 mil negócios), a semana de um vendedor é calculada em 143 ms no navegador, e as listas dos 35 vendedores em 616 ms (`npm run bench`). Os tempos não incluem baixar os dados.
- O núcleo é puro (sem rede e sem estado) e recebe os dados por um contrato (`Dataset`). Ele roda igual no navegador e no Node. Um adaptador de CSV e outro no formato de uma API de CRM dão o mesmo resultado (`adapters.test.ts`).

**O que muda quando muitas pessoas usam**
- O custo cresce com o número de negócios, não com o de pessoas: cada pessoa só lê a própria lista. O desenho é calcular em lote e servir leituras pequenas e já prontas.
- O score muda com o passar dos dias, mesmo sem ninguém mexer no CRM: a chance é recalculada a cada data e cai quando o negócio passa de uma faixa de idade para a outra. E o score é a posição do potencial entre todos os negócios quentes e esfriando da empresa, então um negócio não pode ser calculado isolado. As duas coisas pedem um job diário, e não um cálculo a cada pedido.
- O limite de hoje é privacidade, não desempenho: o navegador recebe a base inteira. Na plataforma, cada pessoa recebe só o que tem permissão para ver.

**Arquitetura alvo** (projeto, não implementado)

```mermaid
flowchart TB
  CRM["CRM"] -- "sync + webhooks" --> ING["Ingestão + validação"]
  ING --> DB["Banco"]
  DB -- "lê negócios" --> JOB["Job diário: mesmo núcleo"]
  JOB -- "grava scores" --> DB
  CAL["Calibração mensal"] --> JOB
  DB --> API["API: SSO e papéis"]
  API <--> APP["App React de hoje"]
  API --> FILA["Fila"]
  FILA -- "dar perda, próximo passo" --> CRM
```

- **Ingestão:** sincronização incremental com o CRM. O adaptador atual vira a porta de entrada, e o contrato é validado a cada lote.
- **Cálculo:** o mesmo núcleo roda num job diário em Node e grava score, estado, motivo, data e versão da curva. Mudanças durante o dia recalculam só o negócio afetado, usando os cortes de percentil gravados pelo lote.
- **Calibração:** um job mensal recalcula a chance pela idade, por empresa. A curva nova só é publicada se ganhar da atual no backtest.
- **Acesso:** login único da empresa (SSO), papéis (vendedor, gestor, RevOps) e isolamento por linha no banco.
- **Ações:** "dar perda" e "próximo passo" voltam para o CRM por uma fila, com nova tentativa e registro. O CRM continua sendo a fonte da verdade.
- **Operação:** a lista fica pronta antes do expediente. Se o job falhar, o app mostra a lista anterior, com a data dela.

**Três fases, com o gatilho para mudar de uma para outra**

| Fase | Quando | O que entra |
|---|---|---|
| 1. Foto diária | Um time piloto, até cerca de 250 mil negócios (arquivo de até ~5 MB com gzip) | Exportação diária do CRM; o mesmo app, com acesso restrito |
| 2. Serviço | Mais de um time, ou quando cada pessoa só pode ver a própria carteira | Banco, job diário, API com SSO e papéis, ações gravadas de volta no CRM |
| 3. Plataforma | Várias empresas ou unidades, ou quando o comportamento das vendas mudar | Isolamento por empresa, calibração mensal com portão, monitor de calibração, medição de impacto com grupo de controle |

**O que não muda em nenhuma fase:** a regra (preço de lista × chance pela idade), a frase de motivo com o mesmo número da conta e o backtest como portão. Nenhuma mudança de regra entra sem ganhar da atual no teste com o passado.

**O que melhoraria o score com mais dados:** registrar atividades (último contato, próxima ação) e o motivo de perda. Hoje a idade é o sinal mais forte que os dados têm. Com atividade, dá para testar se um negócio frio está mesmo parado, passando pelo mesmo portão.

---

## Process Log — Como usei IA

O detalhamento está em `process-log/` (comece pelo `README.md` da pasta).

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| Claude Code (Opus 5.5) | Orquestrador: revisão inicial, recálculo independente, implementação, testes e documentos |
| Agentes do Claude Code: `critico` e `revisor` (Opus 5.5), `testador-de-uso` (Sonnet 5.5) | Crítica do plano e da regra; revisão de código, segurança e números; testes de uso com três personas |
| Skills `frontend-design` e `dataviz` | Direção visual; validação da paleta para daltonismo e contraste |
| Skill `mattpocock-skills:handoff` | Passagem de contexto entre a primeira e a segunda sessão |
| Claude (Cowork) | Consultor do Bruno: formatar os prompts e sugerir caminhos |
| Krea (MCP, modelo Nano Banana Pro) | As duas imagens do app (entrada e "Como funciona") |
| Playwright | Testes de navegador, prints, vídeos e medição das personas |

Antes desta etapa, houve uma preparação com o Claude (Cowork) como assistente. Ela não faz parte do processo registrado; ver a nota em `process-log/README.md`.

### Workflow

1. **Revisão do material de partida.** O Claude Code recalculou cada número com consultas novas e comparou com os scripts Python da preparação. O `critico` revisou as regras e a lógica do score; o `revisor`, o código e os documentos. Dos 9 erros encontrados na preparação, o pior foi o viés de sobrevivência na chance.
2. **Portão G1.** Decidi as questões abertas: a entrada tardia como regra final, a chance como histórico e o prazo sem previsão de queda (D27 a D30).
3. **Telas, primeira versão.** Reprovei-a no portão visual: parecia planilha. A IA tinha seguido ao pé da letra um briefing antigo ("densa, sem animação").
4. **Protótipos em três rodadas.** A segunda também foi reprovada: ainda tinha cara de painel genérico. A terceira, no estilo do apple.com, com o termômetro como assinatura, foi aprovada com ajustes (D41 a D44).
5. **Telas na direção aprovada e o "Como funciona".** Ao fim de cada incremento, o `revisor` e o `testador-de-uso` rodaram, e cada achado grave foi reproduzido antes de ser corrigido.
6. **Escala e deploy.** Bench, segundo adaptador de dados, conferência dos documentos contra a auditoria e varredura de dados pessoais antes de publicar.

As decisões estão em `process-log/decisoes.md` (D1 a D59), com quem decidiu e a evidência.

### Onde a IA errou e como corrigi

São 34 erros registrados em `process-log/erros-da-ia.md`: 9 da preparação e 25 desta etapa. Os principais:

- **Viés de sobrevivência (preparação).** A chance calculada só com concluídos subia com a idade (68,7% aos 14 dias, 71,1% aos 90). Corrigida com a coorte, ela cai para 9% aos 120 dias.
- **Vazamento do futuro nas datas passadas.** O plano mostrava a empresa em todas as datas, mas "sem empresa" entrega que o negócio ainda estará aberto em 31/12. O `critico` pegou no plano. Depois, a troca do herói com animação vazou a empresa por 280 ms; o `revisor` pegou e o Claude Code reproduziu o vazamento antes de corrigir.
- **Interface que não atendia o pedido.** Duas rodadas reprovadas por parecerem painel genérico feito por IA.
- **XSS no protótipo**, por um parâmetro da URL. Achado por uma revisão automática de segurança e reproduzido antes e depois da correção.
- **Afirmações sem lastro.** Os documentos davam como pronta uma interface de dados que não existia, e uma curva estava trocada pela de outra coorte. Achado ao conferir os documentos contra a auditoria; a interface foi construída e testada.

### O que eu adicionei que a IA sozinha não faria

A IA escreveu quase todo o código e os textos. O meu papel foi decidir o que estava bom o suficiente, e várias vezes dizer que não estava.

**Não confiei no que a IA entregou**
- Antes de qualquer código, exigi que o Claude Code revisasse todo o material de partida e recalculasse cada número sem olhar os scripts antigos (D16). A revisão achou 9 erros da preparação, entre eles um viés de sobrevivência que inflava a chance.
- Usei o app publicado como um vendedor usaria. Ao notar que os primeiros nomes da lista não tinham score, a investigação mostrou que a regional Central concentra os 500 negócios em prospecção e quase não tem negócio ativo. O que parecia defeito virou recomendação para a Head de RevOps (D53 a D55).

**Mantive o foco em quem vai usar**
- Reprovei a interface duas vezes (D38, D41): a primeira parecia uma planilha, a segunda um painel genérico de IA. Defini a direção: estilo Apple, um protagonista por tela, animação só com propósito.
- Exigi a língua do vendedor. Nada de "backtest", "coorte" ou "margem de erro" na tela; escolhi quente, esfriando, frio e potencial (D40).
- Percebi que o score existia, mas ninguém o via. Ele virou um número de 0 a 100, com a conta ao lado (D39).

**Tomei as decisões difíceis**
- Sem servidor nem banco, mas com escala provada: com 880 mil negócios, a semana de um vendedor é calculada em 143 ms no navegador (D15).
- Quando a revisão mostrou que a base começava cortada, escolhi o tratamento que se sustentava em três datas, e não em uma (D27).
- Quando a estatística empatou entre duas formas de ordenar, decidi olhando negócios reais: um GTK 500 de US$ 26 mil esfriando vale mais que um MG Advanced quente. Fiquei com o potencial.
- Quando o nº 1 de uma vendedora valia US$ 5, troquei o destaque pela ação que mais pesa para ela, a prospecção (D46).
- Deixei de fora o modelo de machine learning: ele chegou a 43% contra 41% da regra, uma diferença que o acaso explica, e o vendedor não conseguiria entender por que um negócio estava em primeiro.

**Como usei a IA**
O Claude Code construiu, com três agentes: um crítico, um revisor e um testador de uso. Usei o Claude (Cowork) como consultor, para formatar meus prompts e sugerir caminhos. As sugestões vieram das duas IAs. As escolhas foram minhas e estão registradas com o meu nome em `process-log/decisoes.md`.

---

## Evidências

- [x] Screenshots: `process-log/screenshots/` (app) e `process-log/prototipos/` (as três rodadas)
- [x] Screen recording: vídeos dos movimentos em `process-log/screenshots/03-app/` e `process-log/prototipos/`
- [x] Chat exports: `process-log/chat-exports/` (limpos com `tools/limpar-exports.mjs`)
- [x] Git history: um commit por etapa, com as decisões no corpo
- [x] Outro: auditoria reproduzível (`npm run auditoria`), revisões dos agentes (`process-log/revisoes-incremento-4.md` e `-5.md`) e scripts de análise (`solution/analysis/`)

---

_Submissão enviada em: 10/10/2026_
