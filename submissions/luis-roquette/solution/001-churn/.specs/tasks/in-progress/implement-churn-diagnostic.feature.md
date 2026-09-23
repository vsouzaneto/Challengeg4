---
title: Implementar diagnóstico acionável de churn da RavenStack
status: in-progress
---

## Initial User Prompt

### Solicitações originais relevantes, preservadas

> Challege 1 por tanto. a) Você vai registrar,s eguindo nossa metodologia de diário, tudoq ue fizemos até aqui [claro,d e forma reusmida] e explicar nosso briefing pré-inicio

> https://github.com/luisroquette/ai-master-challenge/tree/main/challenges/data-001-churn > > Leia o challenge, em todas as minucias, utilizando o modo /loop até que o /goal seja atingido: Goal é: pelo menos duas passdas consecutivas sem novos achados/descobertas ao reavaliar o briefing do desafio escolhido. Dessa forma, garantimos que o modelo abosrvue na totalidade tudo que foi trazido pelo texto/conteudo a ser avaliado. Registre no nosso diário tmabém essa decisao que é um diferencial criativo meu, gosto sempre de garantir com esse prompt a maior absorcaçao possível do conteúdo a ser analisado antes de criar qualquer coisa!

> agora, antes de seguirmos, registre tambem no nosso diário a decisao de seguir com a metodologia SDD {Spec-Driven} e, para isso, usaremos uma skillq ue gosto muito. Instale e use: https://claudecowork.im/resources/sdd npx skills add NeoLabHQ/context-engineering-kit --skill sdd --agent claude-code

### Requirements

#### Objetivo e decisão

- Responder o que causa o churn, quais segmentos e contas estão em risco e quais ações priorizar.
- Ajudar o CEO a escolher qual problema sistêmico corrigir primeiro em até cinco minutos.
- Cruzar obrigatoriamente as cinco tabelas do Challenge 001.
- Priorizar contenção executável em uma semana e correção estrutural em 30–90 dias.

#### Método analítico

- Construir painel de conta por data de corte sem informação futura.
- Usar horizonte operacional de 30 dias e visão adicional da renovação anual.
- Calcular sinais de 7, 30 e 90 dias somente quando houver cobertura suficiente.
- Confrontar explicitamente as alegações executivas de crescimento de uso e satisfação adequada no agregado versus a coorte que churnará nos 30 dias seguintes.
- Separar fato observado, associação controlada e hipótese causal.
- Usar `reason_code` e feedback somente no diagnóstico retrospectivo.
- Tratar evidência insuficiente como inconclusiva e suprimir rankings instáveis.
- Exibir MRR perdido como métrica principal e “MRR exposto — oportunidade máxima” como teto teórico.

#### Contradições reais dos dados que o plano deve tratar

- O dataset público foi inspecionado antes do planejamento detalhado; os cinco arquivos somam 33.100 registros.
- Existem 21 grupos de `usage_id` duplicados com linhas conflitantes; preservar as linhas com chave técnica derivada e registrar a anomalia, sem deduplicação silenciosa.
- Existem 19.142 eventos de uso anteriores ao `start_date` da assinatura, dos quais 13.198 também antecedem o `signup_date` da conta.
- Existem 1.077 tickets anteriores ao `signup_date`; datas de ciclo de vida não podem ser aceitas como verdade temporal sem análise de sensibilidade.
- `accounts.churn_flag`, `subscriptions.churn_flag` e os eventos não concordam; usar o primeiro churn não reativação como rótulo temporal primário e tratar os flags como fontes de reconciliação e sensibilidade.
- Manter uma visão com timestamps observados e outra restrita à cronologia válida; rebaixar ou suprimir findings que mudem materialmente entre as duas.
- Creditar River @ Rivalytics conforme o README do dataset e verificar os checksums das entradas.

#### Solução aprovada

- Implementar um pipeline Python único que valide dados e gere artefatos canônicos.
- Produzir relatório executivo em Markdown, dashboard Streamlit com três visões e fila operacional CSV.
- Disponibilizar `make reproduce` para validar e regenerar tudo e `make app` para abrir a interface.
- Manter execução local como requisito e demonstração pública somente leitura como diferencial não bloqueante.
- Excluir API, banco, autenticação, CRM, contato automático e chamadas pagas de IA.

#### Qualidade e aceite

- Rastrear cada finding até fontes, corte temporal, cálculo, evidência contrária, limitação e recomendação.
- Bloquear a entrega em falhas de schema, chaves, joins, receita, isolamento temporal, consistência de artefatos ou fumaça do dashboard.
- Incluir modelo preditivo apenas se superar baseline simples fora do tempo e agregar valor operacional por segmento.
- Manter relatório, dashboard e CSV consistentes e derivados da mesma execução.
- Preservar as duas verificações das alegações do CEO como artefato canônico, mesmo quando nenhuma hipótese causal passar pelos gates.
- Documentar setup, limitações, decisões humanas e todo o uso de IA no process log.

#### Fontes de contexto

- Briefing oficial: `challenges/data-001-churn/README.md`.
- Regras de submissão: `submission-guide.md` e `CONTRIBUTING.md`.
- Descoberta aprovada: `submissions/luis-roquette/process-log/001-descoberta-socratica.md`.

## Description

Implementar uma solução local e reproduzível para o Challenge 001, limitada a `submissions/luis-roquette/`. Um pipeline Python validará e reconciliará os cinco CSVs, construirá painéis temporais `observed` e `strict`, avaliará causas e segmentos com gates explícitos e publicará artefatos canônicos. O relatório executivo, o dashboard Streamlit e a fila CSV consumirão esses mesmos artefatos.

O plano executável, com arquivos, interfaces, testes TDD, comandos, commits, timebox e preflight, está em:

`docs/superpowers/plans/2026-09-21-ravenstack-churn-diagnostic.md`

### Critérios de aceite desta task

- As cinco tabelas são cruzadas com contratos, checksums e reconciliação de cardinalidade e receita.
- Nenhum atributo usa informação posterior ao cutoff; o modelo opcional usa somente a cronologia `strict`.
- Findings frágeis ou instáveis ficam inconclusivos e sem ranking; nenhuma causa é fabricada.
- Relatório, dashboard e fila compartilham IDs, métricas e manifesto da mesma execução.
- `make reproduce` funciona em ambiente Python 3.12 limpo e `make check` confirma equivalência sem sujar o worktree.
- O diário registra decisões, erros, correções, rodadas, uso de IA e a revisão executiva cronometrada.
