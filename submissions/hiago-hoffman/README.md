# Submissão — Hiago Hoffman — Challenge 003

## Sobre mim

- **Nome:** Hiago Hoffman
- **LinkedIn:** _(preencher)_
- **Challenge escolhido:** 003 — Lead Scorer

---

## Executive Summary

Construí uma aplicação web que abre no pipeline do vendedor já ordenado por **receita esperada** (chance de ganhar × valor). Ela aponta qual oportunidade atacar primeiro e explica cada score no próprio card, com o detalhamento a um clique.

A análise da base mostrou algo que muda o problema: **produto, setor, região, vendedor e conta não preveem ganho ou perda** (nenhum teste significativo). O que separa os deals é o **valor** e o **tempo**. Além disso, **81% dos deals "Engaging" estão abertos há mais tempo do que qualquer deal que já fechou**.

Por isso o score não tem regra por nome nem peso fixo. Ele reaprende a cada base nova:
- cada dimensão só ganha peso se variar mais do que o acaso;
- cada versão do modelo disputa um teste em datas passadas antes de substituir a vigente.

Na base do challenge, o modelo captura **55,6% da receita ganha nos 20% do topo da lista, contra 46,7% ordenando só por preço**.

**Recomendação principal:** mandar para uma fila de revalidação os 1.331 deals parados além do histórico e concentrar o time nos 258 deals vivos em Engaging e nos 500 de Prospecting. Dentro da lista, os marcados "Esfriando" pedem ação na mesma semana.

---

## Solução

- **App:** [`solution/`](solution/). Setup, lógica e limitações em [`solution/README.md`](solution/README.md).

  ```bash
  cd solution
  npm install
  npm run dev
  ```

  Abre em http://localhost:3000.
- **Análise e modelo:** [`docs/analise-lead-scorer.md`](docs/analise-lead-scorer.md).
- **Process log:** [`process-log/README.md`](process-log/README.md).

### Abordagem

1. **Dados antes de tela.** Análise exploratória completa, com testes estatísticos, leitura mês a mês e separação explícita entre fato e heurística.
2. **Revisão cruzada.** Uma segunda IA criticou a análise; conferi cada afirmação dela na base, corrigi três erros meus e rejeitei dois dela.
3. **Modelo definido antes do código.** Estrutura fixa, parâmetros aprendidos, sem nomes no código, com um ciclo de aprendizado que só promove versões melhores.
4. **Produto.** Workflow `intento-product-design` sobre o `intento-product-starter`: estrutura → implementação → validação no navegador (filtros, tooltip, detalhamento, upload válido e inválido, mobile).

### Resultados

**O que o vendedor vê**
- Raias com os nomes do CRM (`Prospecting`, `Engaging`, `Won`, `Lost`).
- O **#1** destacado como "Comece por este" e o selo **Comece aqui** na raia dele.
- **Esfriando:** deals que passaram do tempo em que 75% dos ganhos já tinham fechado.
- **Revalidar:** bloco no fim da raia com os deals parados além do histórico.
- **Tooltip no score:** receita esperada = chance × valor, idade e o que puxa o score.
- **Detalhamento ao clicar:** o cálculo passo a passo, a posição do deal na linha do tempo, o que fazer agora e as pendências de cadastro.
- **Filtros** por região, manager e vendedor. O ranking é refeito dentro do filtro.

**O que o gestor / RevOps vê** (tela *Modelo e base*)
- Versão vigente do modelo.
- Teste em datas passadas contra a referência sem modelo.
- Curva de chance por idade.
- Peso aprendido por grupo.
- Qualidade da base.
- Upload de uma nova base e histórico de versões.

| Backtest (mar–ago/2017) | Brier | Receita no top 20% |
|---|---|---|
| Sem modelo (taxa histórica + preço) | 0,314 | 46,7% |
| Modelo em uso | 0,231 (0,221 calibrado) | 55,6% |

### Recomendações

1. **Saneamento imediato:** revalidar ou encerrar os 1.331 deals do bloco *Revalidar*. Eles inflam o pipeline e consomem atenção.
2. **Rotina de segunda-feira:** cada vendedor filtra o próprio nome, trabalha de cima para baixo e age na mesma semana nos marcados "Esfriando".
3. **Higiene do CRM:** vincular conta (1.425 deals abertos sem conta) e registrar a entrada em Engaging. Isso destrava estimativas melhores.
4. **Instrumentar o próximo passo:** histórico de estágios, atividades e o score exibido. Cada campo novo entra no modelo como candidato e só ganha peso se o backtest aprovar.

### Limitações

- **Prospecting sem data de entrada:** a conversão Prospecting → Engaging não existe na base, então a chance desses deals é uma estimativa otimista (sinalizada no card).
- **Foto única do CRM:** sem histórico de mudanças de estágio nem atividades.
- **Sem autenticação por usuário:** o filtro por vendedor não é uma permissão.
- **Efeito da própria ferramenta:** o sistema ainda não registra a ação tomada após o score, o que é necessário para medir impacto e evitar que a lista reforce os próprios erros.

Detalhes em [`solution/README.md`](solution/README.md#limitações).

---

## Process Log — Como usei IA

> Versão completa, com linha do tempo e commits: [`process-log/README.md`](process-log/README.md).

### Ferramentas usadas

| Ferramenta | Para que usou |
|---|---|
| Claude Code (Claude Opus 5.5) | Fork e setup, download do dataset, análise estatística, desenho do modelo, implementação, testes, validação no navegador, documentação |
| Segunda IA | Revisão crítica independente da análise ([`process-log/revisao-externa-ia.md`](process-log/revisao-externa-ia.md)) |
| Skills Intento (`intento-product-design`, `shadcn`) | Workflow de produto e componentes |

### Workflow

1. Li o challenge e conferi as regras de PR nos PRs reais do repositório original.
2. Pedi a análise da base antes de qualquer código, mês a mês, sem inventar dados e marcando heurísticas.
3. Fiz perguntas de negócio: produto mais vendido, maior receita, especialistas.
4. Gerei o documento de análise e o submeti a outra IA para crítica.
5. Pedi a crítica da crítica. Exigi uma regra geral, sem nomes, que aprenda com os resultados.
6. Defini o modelo de cálculo e só então liberei o desenvolvimento.
7. Tomei as decisões de produto por perguntas objetivas: fonte de dados, raias encerradas, ordem das raias.
8. Implementação com testes que conferem o motor contra a análise em Python, backtest, calibração e validação no navegador.

### Onde a IA errou e como corrigi

- **Viés de seleção:** a primeira tabela de sobrevivência ignorava os deals abertos. A revisão externa apontou; refeita com riscos competitivos, a conclusão se inverteu.
- **Significância sem correção:** um vendedor foi chamado de "caso forte" sem correção para múltiplos testes. Com Benjamini–Hochberg, q = 0,30.
- **A outra IA também errou:** criticou propostas que não estavam no documento. Isso foi identificado checando linha a linha.
- **Escopo:** a IA começou a opinar sobre o que cabia no challenge. Corrigi: a decisão de escopo é minha.
- **Probabilidades otimistas** na primeira versão do motor: detectadas pelo backtest e corrigidas com calibração.
- **Bugs de interface** (hidratação, rolagem, ordenação, cache do Tailwind, página congelada no build): detectados rodando o app, não lendo o código.

### O que eu adicionei que a IA sozinha não faria

- **Revisão cruzada entre IAs**, com a exigência de que cada afirmação fosse conferida na base.
- **A diretriz de que a regra não pode depender de nomes nem ser fixa.** Isso transformou um score de regras num modelo que se recalibra e se testa a cada base.
- **O recorte de produto:** raias com os nomes do CRM, resumo no hover, detalhe no clique, filtros, e "o vendedor não pode ter dúvida de por onde começar".
- **Controle do escopo e das decisões**, sem aceitar as sugestões da IA como padrão.

---

## Evidências

- [ ] Screenshots das conversas com IA
- [ ] Screen recording do workflow
- [ ] Chat exports
- [x] Git history (branch `submission/hiago-hoffman`)
- [x] Outro: scripts de análise ([`process-log/analysis/`](process-log/analysis/)), revisão externa ([`process-log/revisao-externa-ia.md`](process-log/revisao-externa-ia.md)), testes automatizados

---

_Submissão enviada em: (preencher)_
