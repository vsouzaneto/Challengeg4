# Submissão — Luis Fernando Roquette — Challenge 001

> **Entrega principal e prioritária:** Challenge 001 — Diagnóstico de Churn. Os Challenges 002, 003 e 004 seguem como trabalhos complementares para demonstrar amplitude; a avaliação deve priorizar o Challenge 001.

## Comece aqui

1. [Leia em 2 minutos](solution/001-churn/deliverables/delivery-brief.md) — [versão DOCX](solution/001-churn/deliverables/delivery-brief.docx).
2. [Veja funcionando em 90 segundos](https://app.arcade.software/share/aIAtdPLJilhZOtM7ao5O) — tour público; [roteiro e validação](solution/001-churn/deliverables/arcade/README.md).
3. [Entenda a arquitetura do trabalho em 6 minutos](solution/001-churn/deliverables/video/architecture-overview.mp4) — vídeo autoral; [metadados e capítulos](solution/001-churn/deliverables/video/README.md).
4. [Veja a síntese visual](solution/001-churn/deliverables/infographic-challenge-001.png) — [SVG editável](solution/001-churn/deliverables/infographic-challenge-001.svg), [PDF](solution/001-churn/deliverables/infographic-challenge-001.pdf) e [Video Overview do NotebookLM](solution/001-churn/deliverables/notebooklm/paradoxo-de-churn-do-ceo.mp4).
5. [Audite o processo](solution/001-churn/deliverables/delivery-manifest.md) — relatório, código, testes e diários.

O Arcade foi validado sem autenticação. Vídeos e infográfico são entregues no próprio repositório; o SVG preserva texto e números exatos sem depender de uma geração externa.

## Entregas complementares

- [Challenge 001 — ficha completa da submissão](solution/001-churn/SUBMISSION.md): diagnóstico temporal de churn e resposta executiva.
- [Challenge 002 — ficha completa da submissão](solution/002-support/SUBMISSION.md): diagnóstico operacional e copiloto funcional.
- [Challenge 003 — ficha completa da submissão](solution/003-lead-scorer/SUBMISSION.md): priorização explicável e aplicação funcional.
- [Challenge 004 — ficha completa da submissão](solution/004-social/SUBMISSION.md): cockpit de decisão, evidências e plano de execução.

Essas entregas são complementares. O **Challenge 001 permanece como resposta oficial, principal e mais importante** deste PR.

### Challenge 002 — resposta executiva resumida

- **Onde estamos perdendo tempo?** O diagnóstico separa histórico observado, desempenho medido e cenários projetados, sem atribuir causalidade onde os dados não sustentam.
- **O que pode ser automatizado com IA?** Triagem e rascunhos somente quando os gates de evidência, confiança e segurança forem atendidos.
- **Como isso funciona na prática?** O protótipo executável registra decisões, bloqueios e intervenção humana; veja a [Screenshot real da demonstração](solution/002-support/evidence/screenshot.png).
- **Estado do CK-12:** zero consultas elegíveis; a validação humana permanece opcional e os rascunhos continuam bloqueados.
- **Registro original do perfil no Challenge 002:** LinkedIn:** Não informado.

## Sobre mim

- **Nome:** Luis Fernando Roquette
- **LinkedIn:** [linkedin.com/in/luisroquette](https://br.linkedin.com/in/luisroquette)
- **Challenge principal e prioritário:** 001 — Diagnóstico de Churn
- **Challenges complementares:** 002, 003 e 004

## Executive Summary

Cruzei as cinco tabelas em um painel temporal reproduzível, com leituras `observed` e `strict`. O churn recente chegou a **12,4%**, alta de **7,0 pontos percentuais**, e o MRR perdido observado foi de **US$ 1.622.337**. O uso agregado subiu de **0,336 para 0,493**, mas caiu de **0,349 para 0,304** entre futuros churners. A satisfação descreve apenas respondentes de tickets; não houve causa nem concentração material demonstrada — o maior risco relativo elegível foi **1,08×**, abaixo do limiar de **1,25×**. Recomendo validar dados, uso e satisfação antes de intervir, sem transformar correlação frágil em certeza executiva.

## Solução

### Abordagem

1. Imobilizei os cinco CSVs com SHA-256 e contratos explícitos.
2. Modelei conta por data de corte, com janelas de 7, 30 e 90 dias sem vazamento.
3. Comparei cronologias `observed` e `strict` e avaliei seis hipóteses pré-definidas.
4. Separei diagnóstico do modelo opcional e apliquei gates fora do tempo.
5. Gerei relatório, dashboard e fila a partir do mesmo objeto, protegidos por manifesto.

### Resultados / Findings

- [Relatório executivo](solution/001-churn/artifacts/report.md): decisão e evidências verificáveis.
- [Dashboard local e reprodução](solution/001-churn/README.md): três visões, filtros e exportação.
- [Findings canônicos](solution/001-churn/artifacts/findings.csv): seis hipóteses inconclusivas com motivo explícito.
- [Claims canônicos](solution/001-churn/artifacts/claim_checks.csv): uso sobe no agregado, cai na coorte de churn e satisfação permanece `concern`.
- [Contas para validação](solution/001-churn/artifacts/account_watchlist.csv): sinais descritivos nomeados, sem autorização de intervenção.
- [Qualidade dos dados](solution/001-churn/artifacts/quality_report.json): 19.142 usos pré-assinatura, 13.198 pré-cadastro e 1.077 tickets pré-cadastro.

### Recomendações

| Prioridade | Ação | Impacto estimado | Confiança |
|---|---|---|---|
| 1 semana | Sanear eventos fora do ciclo de vida e reproduzir as métricas. | Impedir dados temporalmente inválidos de sustentar decisões; impacto financeiro não estimável antes do saneamento. | Alta para o ganho de qualidade; não causal. |
| 30 dias | Acompanhar uso e churn prospectivamente com cobertura mínima de 70%. | Produzir a primeira estimativa prospectiva comparável; impacto financeiro ainda não estimável. | Condicionada ao gate de cobertura. |
| 30 dias | Medir satisfação fora dos tickets, com resposta mínima de 70% por estrato. | Remover o viés de respondentes e comparar coortes; impacto financeiro ainda não estimável. | Condicionada à representatividade. |

O teto observado é US$ 1.622.337 de MRR perdido no período recente. Ele mede exposição histórica, não receita recuperável nem retorno prometido pelas ações.

### Limitações

Os dados são observacionais, contraditórios e aparentemente sintéticos. Não há histórico de intervenção para estimar receita recuperável ou efeito causal. Feedback de churn não entra em score prospectivo. As métricas de segmento usam o último snapshot diagnóstico elegível por conta e não representam uma taxa histórica populacional.

## Process Log — Como usei IA

### Ferramentas usadas

| Ferramenta | Para que usei |
|---|---|
| OpenAI Codex | pesquisa, leitura do desafio, perguntas socráticas, SPEC, implementação, testes e documentação |
| SDD — Context Engineering Kit | sequência SPEC → plano → execução → validação |
| Ponytail | controle de escopo, reuso e menor implementação suficiente |
| Pesquisa web/GitHub | busca prévia de padrões e soluções existentes antes da criação |

### Workflow

1. Li o briefing em loop até duas passadas consecutivas sem novos achados.
2. Conduzi cinco ondas socráticas adaptativas antes de escrever a SPEC.
3. Refinei o plano até duas rodadas consecutivas sem melhoria substancial.
4. Implementei cada fase em `Planejamento → Revisão → Execução → Teste`, repetindo quando um gate falhou.
5. Mantive decisões, erros, correções e provas em diários contemporâneos.

**Iterações registradas:** 5 ondas socráticas com 25 decisões, 20 passadas de otimização do primeiro plano, 9 fases de implementação, 3 rodadas de redundância e 5 rodadas de lapidação visual. A suíte final executa 86 testes.

### Onde a IA errou e como corrigi

A IA inicialmente herdou um teste de caminho incompatível com a resolução real do `AppTest`; corrigi para caminho absoluto e preservei a prova pela raiz. Também tentou capturar exceções amplas no modelo estatístico e recebeu bloqueio do Ruff; restringi às falhas numéricas conhecidas. No painel, rejeitei um teste conceitualmente impossível que exigia cobertura histórica antes do cadastro. Finalmente, um smoke revelou `pd.NA` incompatível com sklearn, levando à normalização explícita das features aprovadas.

### O que eu adicionei que a IA sozinha não faria

Defini documentação como parte principal da entrega — “ganha quem documenta” — e exigi absorção por loop, cinco ondas socráticas e SDD antes de qualquer implementação. Também determinei que abstenção é melhor que uma narrativa causal instável, que toda recomendação precisa de um portão de confiança e que relatório, dashboard e CSV devem compartilhar a mesma verdade canônica.

## Evidências

- [x] Narrativa escrita: [diário pré-início](process-log/000-pre-inicio.md), [descoberta socrática](process-log/001-descoberta-socratica.md), [otimização do plano](process-log/002-otimizacao-plano-loop.md), [implementação](process-log/003-implementacao-feedback-looping.md) e [entregáveis](process-log/004-planejamento-entregaveis.md).
- [x] [Template oficial preenchido para as quatro soluções](process-log/005-template-quatro-solucoes.md).
- [x] Git history: [evolução da branch canônica](https://github.com/luisroquette/ai-master-challenge/commits/submission/luis-roquette/).
- [x] Vídeo autoral: arquitetura e construção documentadas em [metadados, capítulos e checksum](solution/001-churn/deliverables/video/README.md).

---

_Submissão preparada em: 23 de setembro de 2026._
