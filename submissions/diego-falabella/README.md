# Submissão — Diego Falabella — Challenge 004 (Estratégia Social Media)

## Sobre mim

- **Nome:** Diego Falabella
- **LinkedIn:** https://www.linkedin.com/in/diego-falabella/
- **Challenge escolhido:** 004 — Estratégia Social Media (Marketing)

---

## Executive Summary

O dataset de 52.214 posts não contém sinal: todas as métricas são sorteadas de forma independente (views ~ Normal(10.100 ± 100) para todo post, correlação entre métricas ≈ 0, 1 teste significativo em 80 quando 4 seriam esperados por acaso, ranking de segmentos que não se replica entre metades da amostra, modelo preditivo com R² = −0,001, "creator" com 10 nomes e 10 contagens de followers por id). Qualquer estratégia "baseada nesses dados" seria achismo com verniz estatístico — exatamente o que o Head de Marketing disse não querer. Em vez de fingir insight, entrego três coisas: **(1)** a prova reproduzível de que o dado não responde à pergunta, com a análise ingênua ao lado para mostrar o que a IA sem supervisão teria recomendado; **(2)** uma ferramenta de acompanhamento (HTML único, roda no navegador) com um **portão de sinal** que bloqueia o painel de performance quando o export não sustenta conclusões e o libera quando sustenta; **(3)** um plano de 30 dias para instrumentação e para decidir patrocínio por experimento controlado com métrica de custo por resultado. Principal recomendação: congelar decisões baseadas nesta base, consertar a coleta e responder "vale patrocinar?" com um teste de 4 semanas, não com um benchmark.

---

## Solução

| Arquivo | O que é |
|---|---|
| [`solution/01-auditoria-de-dados.md`](solution/01-auditoria-de-dados.md) | Prova de que o dataset é ruído + o que a análise ingênua teria dito |
| [`solution/02-estrategia-e-plano-30-dias.md`](solution/02-estrategia-e-plano-30-dias.md) | O que fazer na segunda-feira: congelar, instrumentar, testar patrocínio, parar de fazer |
| [`solution/dashboard/index.html`](solution/dashboard/index.html) | **Ferramenta**: Social Signal Gate — abre com duplo clique, aceita CSV, bloqueia/libera o painel |
| [`solution/analysis/run_audit.py`](solution/analysis/run_audit.py) | Script reproduzível que gera todos os números, gráficos e o `summary.json` |

### Abordagem

1. **Li o repositório inteiro antes dos dados** — README, os 4 challenges, CONTRIBUTING, guia, template e `.gitignore`. Achei duas armadilhas de processo: `submissions/` está no `.gitignore` (quem segue o passo a passo faz push de pasta vazia; precisa `git add -f`) e a regra de não tocar em arquivo fora da própria pasta impede "consertar" isso.
2. **Auditoria antes de análise.** Primeira coisa com o CSV: perfil de colunas, distribuições, correlações, consistência de entidades. Em 10 minutos ficou claro que o texto era gerado por Faker e as métricas eram Gaussianas estreitas. Em vez de seguir para "engajamento por plataforma", parei e formalizei a suspeita com testes.
3. **Prova em cinco frentes independentes** (forma das distribuições, correlações, testes por fator, replicação split-half, modelo preditivo), para que a conclusão não dependa de um único método que alguém possa contestar.
4. **Decisão de entrega.** Com dado nulo, três caminhos: fingir sinal (o baseline), entregar só o diagnóstico, ou entregar diagnóstico + ferramenta + plano. Escolhi o terceiro porque é o que eu entregaria de verdade a um Head de Marketing: ele não quer saber que o dado é ruim, quer saber o que fazer agora.
5. **Ferramenta testada nos dois cenários**: com o dataset do challenge (portão vermelho, painel bloqueado) e com um CSV com sinal plantado (portão verde, painel liberado, r = 0,99). Teste automatizado com Playwright, sem erros de console.

### Resultados / Findings

Resumidos no executive summary; detalhados com tabelas e 5 gráficos em `solution/01-auditoria-de-dados.md`. Os números-chave:

| Teste | Resultado | O que significaria em dados reais |
|---|---|---|
| Coef. de variação de views | 1,0% | > 100% (cauda longa) |
| Maior correlação entre métricas | 0,007 | likes×views > 0,8 |
| Testes fator × métrica com p<0,05 | 1 de 80 | dezenas |
| Replicação split-half do ranking de 120 segmentos | r = −0,22 | r > 0,8 |
| R² de gradient boosting (eng, views, shares) | −0,001 | 0,3–0,7 |
| Followers distintos por creator_id | 10,4 | 1–2 |

Screenshots da ferramenta: `solution/dashboard/screenshot_dataset_kaggle.png` (bloqueado) e `screenshot_csv_com_sinal.png` (liberado) — e as figuras em `solution/analysis/outputs/` são SVG geradas pelo script.

### Recomendações

Priorizadas em `solution/02-estrategia-e-plano-30-dias.md`: (1) congelar decisões citando esta base; (2) instrumentar o export com reach, saves, custo, creator estável e conversão; (3) política de patrocínio por experimento de 4 semanas com métrica pré-registrada de custo por resultado, comparando 3 faixas de creator contra orgânico; (4) adotar o Social Signal Gate como rotina mensal; (5) parar de usar engagement rate médio como KPI de decisão e de contratar influenciador por faixa de seguidores.

### Limitações

- Não é possível distinguir se o dataset foi escolhido pelo G4 como teste deliberado ou sem checagem; a resposta certa é a mesma nos dois casos, mas registro a incerteza.
- O plano usa a minha experiência em marketing de food service multi-loja como lente; os thresholds de custo e as métricas de negócio precisariam ser calibrados com o Head real.
- O portão de sinal foi calibrado com dois extremos (ruído puro e sinal forte sintético). Em dados reais os limiares merecem revisão após o primeiro mês de uso.
- Não usei benchmarks públicos de engajamento como substituto dos dados, por decisão: seria trocar "dado da empresa" por "opinião de terceiros".
- Tempo total: cerca de 4 horas de trabalho efetivo numa única sessão de IA, dentro do budget.

---

## Process Log — Como usei IA

> Narrativa completa em [`process-log/narrativa.md`](process-log/narrativa.md); prints da conversa em `process-log/screenshots/`.

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| Claude (Cowork + Claude in Chrome, modelo Claude Fable 5.1) | Leitura do repositório, caça às armadilhas, auditoria estatística, geração dos scripts, da ferramenta e dos textos — em uma única sessão, com decisões minhas em cada bifurcação |
| Python (pandas, scipy, scikit-learn, matplotlib) | Executado pela IA dentro da sessão: testes estatísticos, modelo, gráficos |
| Playwright (Chromium headless) | Teste automatizado da ferramenta nos dois cenários + screenshots |
| Git / GitHub | Fork, branch `submission/diego-falabella`, PR |

### Workflow

1. Abri o repositório e pedi à IA que lesse tudo **com a instrução explícita de procurar pegadinhas**. Ela clonou o repo, leu os 10 arquivos e listou as armadilhas (`.gitignore`, baseline, formato do PR, suspeita de dados sintéticos).
2. Pedi uma comparação de custo (tokens/tempo) entre os 4 challenges antes de escolher; escolhi o 004 por ser minha área, sabendo que não era o mais barato.
3. Baixei o dataset do Kaggle manualmente (a sessão não tinha acesso) e subi na conversa.
4. A IA fez o perfil inicial, levantou a hipótese de dado sintético e propôs **confirmar com testes formais** antes de qualquer análise de performance; concordei — dali saíram os 80 testes, o split-half e o modelo.
5. Com a prova em mãos, a IA me apresentou três caminhos de entrega com prós e contras. Escolhi "auditoria + ferramenta + plano" e autorizei usar minha experiência profissional como contexto, de forma genérica.
6. A IA escreveu o script reproduzível, gerou os gráficos, construiu o dashboard com o portão de sinal e o testou com Playwright nos dois cenários antes de me mostrar.
7. Revisei os textos (README, auditoria e estratégia), aprovei sem alterações, e fizemos o fork, a branch e o PR pelo conector GitHub da sessão (quem usa git local precisa de `git add -f`, porque `submissions/` está no `.gitignore`).

### Onde a IA errou e como corrigi

- **Tentou baixar o Kaggle sem login e falhou** (bloqueio de rede). Resolvi baixando manualmente — trivial, mas mostra que o processo precisa de humano no loop para acesso a dados.
- **Recomendou o challenge 004 pelo encaixe com meu perfil antes de ver os dados.** A recomendação se sustentou, mas por sorte: se eu tivesse escolhido pelo custo (003), teria evitado o dataset nulo. Lição: encaixe de perfil e qualidade do dado são critérios independentes.
- **Na primeira passada de auditoria, o script reportou 2 testes com p<0,05 (um deles dia da semana × comentários).** Um analista apressado — ou uma IA respondendo ao brief sem a instrução de desconfiar — transformaria isso em "poste às terças". A leitura correta, que a própria IA fez porque a pergunta era "isso é ruído?", é que 2 em 90 é *menos* do que o acaso produz (4,5). Isso virou o gráfico de p-values. O ponto é que a pergunta feita muda a resposta que a IA dá.
- **O portão de sinal foi calibrado pela própria IA com um CSV sintético que ela mesma gerou com sinal plantado.** É circular: ela testou a ferramenta contra o que ela mesma inventou. Registrei isso como limitação explícita em vez de esconder.
- **Benchmarks de mercado** ("engajamento médio no TikTok é X%") eram o caminho fácil para preencher a lacuna de dados. Decidimos não usar: o Head pediu dado, não opinião de terceiros, e benchmark genérico é exatamente o conteúdo de baseline que o G4 já tem.

### O que eu adicionei que a IA sozinha não faria

- **A instrução de desconfiar antes de analisar.** Sem ela, o caminho natural da IA (e o baseline que o G4 descreve) é segmentar, rankear e recomendar. A auditoria só existiu porque a primeira pergunta foi "onde está a pegadinha?".
- **A decisão de não fingir.** A IA apresentou "fingir que há sinal" como opção; a escolha de entregar um "não" fundamentado para o Head é uma decisão de carreira e de credibilidade, não técnica.
- **A lente de negócio**: a métrica que paga a conta não é like, é cliente na loja e pedido no delivery. Isso reorganizou a estratégia em torno de custo por resultado e experimento, e deu origem à ideia de a ferramenta *bloquear* o painel em vez de só mostrar um aviso.
- **Economia de tempo como critério**: perguntei o custo de cada caminho antes de começar e cortei escopo (sem modelo de hashtags, sem clustering de audiência) porque, com dado nulo, seriam enfeite.

---

## Evidências

- [x] Screenshots das conversas com IA — `process-log/screenshots/`
- [x] Narrativa escrita passo a passo — `process-log/narrativa.md`
- [x] Git history — commits desta branch
- [x] Teste automatizado da ferramenta — `solution/dashboard/screenshot_*.png`
- [ ] Screen recording — não gravado

---

_Submissão enviada em: 11 de outubro de 2026_
