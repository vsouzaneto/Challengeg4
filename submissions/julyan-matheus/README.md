# Submissão — Julyan Matheus — Challenge 003 (Lead Scorer)

## Sobre mim

- **Nome:** Julyan Matheus
- **LinkedIn:** https://www.linkedin.com/in/julyan-moura-5389843ab/
- **Challenge escolhido:** 003 — Lead Scorer (Vendas / RevOps)

**App no ar:** https://ai-master-challenge-two.vercel.app

---

## Executive Summary

Construí uma ferramenta web que o vendedor abre na segunda de manhã e vê o pipeline dele dividido em 4 grupos: **Focar** (recebe score), **Requalificar** (sem conta no CRM), **Iniciar** (sem primeiro contato) e **Limpar** (passou do limite histórico). Antes de escrever código, testei 7 hipóteses nos dados e descobri que o problema não é priorização — é higiene de CRM: dos 2.089 deals abertos, **68% não têm conta vinculada** (nenhum deal sem conta fechou, nunca) e **81% passaram de 138 dias** (nenhum deal fechou depois disso). Só **89 deals** estão em condição real de fechar. Um terço dos vendedores não tem nenhum. A recomendação principal é parar de ranquear lixo cadastral e usar a ferramenta pra limpar o CRM antes de otimizar.

---

## Solução

### Abordagem

1. **Hipóteses antes dos dados.** Escrevi 7 palpites sobre o que faz um deal fechar e testei cada um com número (`docs/hipoteses.md`). 3 caíram (tamanho da empresa, produto, gerente/região), 1 foi parcial (vendedor), 2 confirmaram (carga do vendedor, conta vinculada), 1 inverteu (tempo aberto — deal que sobrevive 14 dias fecha *mais*, não menos).
2. **Decisões registradas.** 8 decisões de produto em `docs/decisoes.md`, cada uma com origem (minha, da IA, ou consenso) e motivo.
3. **Spec antes do código.** `docs/spec.md` escrita e aprovada antes do Claude Code abrir um arquivo. O Claude Code propôs 4 mudanças na spec; aceitei todas (Decisão 5).
4. **Backtest.** Score calculado em 01/09/2017 com dados só até essa data, resultado real conferido até 31/12/2017.
5. **Auditoria independente.** Código revisado pelo ChatGPT sem acesso às minhas conclusões. 8 pontos: 4 corrigidos, 2 documentados, 1 rejeitado, 1 mantido (Decisão 8).

### O que os dados mostraram

| Hipótese | Resultado |
|---|---|
| Empresa maior fecha mais | **Caiu.** Win rate entre 61% e 66% em todas as faixas |
| Produto caro × empresa grande | **Caiu.** Todas as combinações entre 57% e 67% |
| Vendedor influencia | **Parcial.** 55% a 70% entre o pior e o melhor |
| Vendedor sobrecarregado fecha menos | **Confirmada.** 68,8% com carga baixa → 59,9% com carga muito alta |
| Deal parado não fecha | **Invertida.** Lost morre em 14 dias (mediana); Won leva 57. Mas ninguém fechou após 138 dias |
| Deal sem conta não fecha | **Confirmada.** 0 de 6.711 fechados sem conta. 68% dos abertos estão sem |
| Vendedor × produto (sugestão da IA) | **Confirmada.** Fator mais forte: 54% no pior grupo, 73% no melhor. Ex: Niesha Huffines fecha 80% de GTX Plus Pro e 14% de GTX Pro |

### Como o score funciona

Só o balde **Focar** (Engaging, ≤138 dias, com conta) recebe score. Três fatores, pesos proporcionais ao efeito medido:

- **Afinidade vendedor × produto (50%)** — win rate histórico da combinação, suavizado pra média do vendedor quando há pouco histórico (K=15)
- **Momentum (31%)** — chance histórica de ganhar dado que o deal sobreviveu até X dias
- **Capacidade do vendedor (19%)** — quantos deals abertos ele tem; menos = mais chance de agir

**Valor esperado** (chance × preço do produto) é uma coluna separada, não entra no score — misturar os dois bagunçou a ordenação no backtest (Decisão 4).

Cada deal mostra 3 linhas de "por quê", uma por fator, em português simples:

> **Afinidade:** Você fecha 65% de MG Special (108 deals)
> **Momentum:** Aberto há 136 dias — perto do limite de 138
> **Capacidade:** Você tem 68 deals abertos — abaixo da média (77)

Fora do score, com justificativa nos dados: tamanho da empresa, produto isolado, gerente, região.

### Backtest

Score calculado em 01/09/2017 usando só o histórico até essa data. Resultado real dos 893 deals que fecharam até dezembro:

| Grupo | Win rate | Receita média |
|---|---|---|
| Q1 (frio) | 71,4% | $922 |
| Q4 (quente) | **78,9%** | **$2.746** |

O grupo quente fecha mais e vale 3x. O meio (Q2–Q3) não ordena bem — por isso separei chance e valor na tela. A afinidade, que deu 19 pontos no teste inicial, deu 8 no backtest (o teste inicial era otimista; ainda é o maior fator).

### Achados de negócio

- **Pipeline vivo real: 89 de 2.089 deals.** O resto ou não tem conta, ou passou do prazo, ou não começou.
- **9 dos 27 vendedores têm 0 em Focar.** O time inteiro do Melvin Marxen (5 vendedores) e 4 de 5 do Dustin Brinkmann.
- **Darcel Schlecht**, maior vendedor em receita ($1,15M), tem 194 deals abertos e nenhum em Focar: 74 sem conta, 83 mortos, 37 sem primeiro contato.
- **MG Advanced** aparece em 6 das 8 piores combinações vendedor × produto. Problema do produto, não do vendedor.
- **`GTXPro` e `GTX Pro`** são o mesmo produto escrito diferente. Sem normalizar, ~1.480 deals perdem a afinidade.

### Recomendações

1. **Semana 1 — higiene, não priorização.** Vincular conta nos 546 deals em Requalificar. É a única ação que move um deal pro balde vivo.
2. **Fechar os 1.291 em Limpar** como Lost ou reabrir do zero. Historicamente nenhum fecha depois de 138 dias; mantê-los abertos infla o pipeline e esconde o problema.
3. **Conversa com gerente, não com vendedor**, nos times do Melvin Marxen e Dustin Brinkmann — o padrão é do time inteiro.
4. **Redistribuir MG Advanced** pros poucos vendedores que fecham bem, ou revisar o produto.
5. **Só depois disso** o score de Focar vira a rotina de segunda-feira.

### Limitações

- **O score ranqueia, não calibra.** Um deal com 70 não tem 70% de chance — tem mais chance que um de 62. Calibrar exigiria validação separada (apontado na auditoria externa).
- **Valor esperado usa preço de tabela.** O dataset não tem valor do deal aberto e `close_value` seria leakage.
- **Data de referência é 31/12/2017** (última do dataset), não hoje. Em produção seria a data atual.
- **Cold start:** vendedor ou produto sem histórico cai na média global (63%). Num CRM novo o score não funciona.
- **O muro de 138 dias é histórico**, não físico. Alguns dos 1.291 podem ser recuperáveis — por isso a ação é "reabrir do zero", não "apagar".
- **Sem login, sem edição.** O app sugere ações; não executa no CRM.
- **Afinidade com poucos deals é instável** mesmo com suavização. Combinações com <15 deals são puxadas pra média do vendedor.

### Como rodar

```bash
cd submissions/julyan-matheus/solution
npm install
npm run dev        # http://localhost:3000
npm test           # 15 testes
npm run sanity     # números da seção de sanity check
```

Sem variáveis de ambiente, sem API externa, sem banco. Os CSVs estão em `solution/data/`.

**Sanity check** (`npm run sanity`):

| Item | Valor |
|---|---|
| Baldes | Focar 89, Requalificar 546, Iniciar 163, Limpar 1.291 |
| Momentum | ≥0d 63%, ≥14d 69%, ≥30d 68%, ≥60d 69%, ≥90d 71%, ≥120d 75% |
| Score no Focar min / mediana / max | 62 / 66 / 78 |
| Carga por vendedor min / média / max | 31 / 77 / 194 |

---

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usei |
|---|---|
| Claude (chat) | Exploração dos dados: eu escolhia a hipótese, ele rodava a análise e mostrava o número. Backtest. Rascunho da spec e deste README. Guia de git e Vercel. |
| Claude Code | Construção do app a partir da spec. Modo manual, aprovando cada edição. |
| ChatGPT | Auditoria independente do `scoring.ts`, sem acesso às conclusões. |

### Workflow

1. Li o repo do challenge e os reviews dos PRs anteriores pra entender o que o avaliador valoriza (com Claude).
2. Fork, clone, branch. Achei a armadilha do `.gitignore` que ignora `submissions/` — resolvido com `git add -f`.
3. Escrevi hipóteses **antes** de analisar. Testei uma por vez, commitando cada resultado.
4. Registrei decisões de produto separadas das hipóteses.
5. Escrevi a spec, o Claude Code propôs ajustes, aceitei os 4.
6. Claude Code construiu `scoring.ts` + testes primeiro; só depois as telas. Aprovei cada arquivo.
7. Backtest temporal antes de qualquer tela.
8. Deploy na Vercel (errei o framework preset na primeira, corrigi).
9. Auditoria com ChatGPT. Corrigi 4 pontos, documentei 2, rejeitei 1, mantive 1.

### Onde a IA errou e como corrigi

- **Spec com contagem dupla.** Eu (com o Claude) escrevi que o bloco "Hoje" ordenaria por score × valor esperado. O Claude Code apontou que valor esperado já contém a chance — contava duas vezes. Aceitei e mudei pra só valor esperado (Decisão 5).
- **Min-max instável.** A spec normalizava cada fator pelo min-max do balde Focar, o que faria o score de um deal mudar quando outro deal entra. O Claude Code propôs escala natural. Aceitei.
- **Print redundante.** O Claude me mandou tirar print do `hipoteses.md`, que já vai no repo em texto. Depois percebeu que era inútil e mudou a regra: print só de resultado, nunca de arquivo. Os prints 06–10 foram refeitos.
- **Teste otimista da H7.** A afinidade deu 19 pontos porque calculou e mediu nos mesmos deals. O Claude avisou na hora que era otimista; o backtest confirmou: 8 pontos.
- **Tempo de fechamento na H4.** A tabela mostrava que vendedor com carga alta "fecha em 13 dias". O Claude apontou que era viés de recorte (deals recentes só aparecem fechados se fecharam rápido) e a coluna foi descartada da conclusão.
- **Compressão do score.** Com escala natural, o score ficou entre 62 e 78. O Claude Code ofereceu esticar visualmente pra 0–100. Recusei — um deal de 62% pareceria zero. Adicionei etiqueta relativa em vez disso (Decisão 6).
- **Auditoria externa** achou 4 bugs reais: histórico e carga não filtravam pela data de referência (só morderia num backtest), capacidade podia sair de 0–1, e etiqueta "Top" aparecia pra vendedor com 1 deal.

### O que eu adicionei que a IA sozinha não faria

- **A pergunta certa.** Pedi pra cruzar tamanho da empresa com fechamento antes de qualquer outra coisa — e caiu. Isso mudou a direção: parei de procurar "o deal bom" e fui procurar "o que impede de fechar".
- **Carga do vendedor como hipótese.** Apareceu na H3 (Darcel com 194 abertos vs Wilburn com 31). Eu pedi pra testar. Deu 9 pontos.
- **Triagem em baldes em vez de ranking.** Quando vi que 81% do pipeline passou do limite, decidi que ranquear tudo escondia o problema. A IA tinha proposto score pra todos.
- **Deals sem conta visíveis, com ação, sem nota.** A IA sugeriu esconder ou dar "baixa probabilidade". Recusei: não é probabilidade baixa, é dado incompleto. Vira instrução ("vincular conta"), não número.
- **Dois indicadores na tela.** Quando o backtest mostrou que valor bagunçava o meio, escolhi separar em vez de escolher um.
- **Manter os três alertas do gerente.** A IA sugeriu simplificar pra só "0 em Focar". Mantive os outros pra quando o CRM estiver mais limpo.
- **Recusar esticar o score.** Ver acima.

### Evidências

- [x] Screenshots: `process-log/screenshots/` (22 prints, numerados na ordem do processo)
- [x] Chat exports: `process-log/chat-exports/` (conversa completa com Claude + auditoria ChatGPT)
- [x] Git history: 20+ commits incrementais, um por hipótese/decisão/etapa
- [x] Hipóteses e decisões em texto: `docs/hipoteses.md`, `docs/decisoes.md`, `docs/spec.md`

---

_Submissão enviada em: 15/09/2026_
