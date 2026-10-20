# Architecture — Challenge 003 | Lead Scorer

**Última atualização:** 19/10/2026 · Versão condensada. Origem: [discovery.md](./discovery.md) e [data-audit.md](./data-audit.md). Rotas, versões do contrato, testes e desvios do plano: [solution/README.md](../solution/README.md). Requisitos de produto e critérios de aceite: [prd.md](./prd.md).

<a id="secao-1"></a>
## 1. Entradas de produto

**O que os dados sustentam [Dados].** Uma ferramenta de **triagem explicável**: ordenar por valor em jogo (preço de tabela ≈ valor fechado, ±20% em 95,9% dos Won), sinalizar o que passou do ciclo já observado e declarar o que não dá para pontuar. Não sustentam probabilidade de ganho por deal (AUC de 0,47 a 0,57) nem esfriamento (sem log de atividade). Os pesos do "scoring" são **política**, não aprendizado, e o ganho sobre "ordenar por preço" só um piloto com grupo de controle pode medir. Nada aqui comprova efeito da ferramenta.

**Requisitos.** RB-01 a RB-08 vêm do briefing e do repositório (dados reais, lógica além de ordenar por valor, explicação, documentação, filtros, só `submissions/alice-dantas/`).

- **Dados:** RD-01 sem probabilidade por deal · RD-02 sem `close_*`, ciclo, mês de fechamento nem `opportunity_id`, com verificação automática · RD-03 "não pontuável" é saída válida, com motivo · RD-04 normalizar rótulos e provar que nenhuma linha se perde · RD-05 taxa-base só como faixa · RD-06 vendedor, manager e escritório só como escopo, nunca ranking de pessoas · RD-07 "hoje" como parâmetro · RD-08 registrar eventos de uso · RD-09 backtest temporal contra baselines.
- **Escolha:** RE-01 o usuário central é o vendedor · RE-02 a precisão exibida não excede a dos dados · RE-03 a ferramenta lê o CRM e não escreve nele · RE-04 toda frase aponta para um campo verificável.

**Funcionalidades.** P0 é o que o MVP precisa para cumprir o briefing sem enganar o usuário; P1 melhora adoção ou uso gerencial; P2 depende de dado inexistente.

| ID | Funcionalidade | Prioridade |
| --- | --- | --- |
| F-01 | Lista "Onde focar", por grupo e faixa de valor | P0 |
| F-02 | Painel "Por que está aqui", com o que não se sabe | P0 |
| F-03 | Estado explícito por oportunidade, com motivo | P0 |
| F-04 | Grupos por idade, em tom factual | P0 |
| F-05 | Normalização e contagem por junção | P0 (base) |
| F-06 | Validação temporal e guarda de vazamento | P0 (base) |
| F-07 | Marcação de ação e registro de eventos | P1 |
| F-08 | Filtros de manager e escritório, resumo descritivo | P1 |
| F-09 | Faixa de referência da taxa-base | P1 |
| F-10 a F-13 | Painel de carga; alerta de esfriamento (exige atividade); forecast ponderado; piloto com controle | P2 |

**Rejeitado no MVP.** RJ-01 probabilidade de ganho por deal · RJ-02 `close_date` ou fim de trimestre como sinal (vazamento) · RJ-03 ranking de vendedores, ou vendedor, conta e setor como feature · RJ-04 alertas de esfriamento · RJ-05 forecast e ROI na tela · RJ-06 score contínuo de 0 a 100 · RJ-07 texto livre de LLM. Só voltam com o dado que falta.

<a id="secao-2"></a>
## 2. Decisões (ADR)

A regra de grupos vigente é a do ADR-006 com a ordem do ADR-009.

<a id="adr-001"></a>
### ADR-001 — Scoring (15/10/2026; estados substituídos em parte pelos ADR-006 e 009)

- **Decisão:** regras, sem probabilidade por deal nem número contínuo. Estado → faixa de valor de tabela (alto ≥ 3.000, médio 500 a 3.000, baixo < 500) → preço exato → `opportunity_id` (só estabilidade). A idade é exibida e não ordena. Pesos e faixas são **política provisória (U-06)**, à espera da RevOps.
- **Rejeitado:** pontos ponderados; segmentos estatísticos (sem sinal); ML (GBM com todos os campos: AUC médio 0,503); valor esperado (vira ranking por produto); híbrido; uplift.
- **Sacrifica:** discriminação por deal; o topo é dominado por valor.
- **Revisitar:** atividade ou histórico de estágio com AUC acima de 0,5 em ao menos 4 de 5 cortes, ou piloto com controle.

<a id="adr-002"></a>
### ADR-002 — Dados (15/10/2026)

- **Decisão:** normalização por mapa explícito (`GTXPro` → `GTX Pro`; rótulo desconhecido falha, não descarta); junções com contagem antes e depois; 461 linhas idênticas mantidas; "hoje" é o parâmetro `as_of` (padrão 2017-12-31); referência de ciclo só com fechadas até o `as_of`; CSV somente leitura.
- **Rejeitado:** join direto (perde 1.480 linhas); deduplicar ou imputar conta; auto-junção por conta.
- **Sacrifica:** fidelidade a uma data real de extração.
- **Revisitar:** data de extração real, regra de deduplicação da empresa ou fonte viva.

<a id="adr-003"></a>
### ADR-003 — Tecnologias (15/10/2026)

- **Decisão:** núcleo Python puro (pandas) sem dependência de web, API FastAPI fina, front Next.js e CLI, com pytest. Apresentação desacoplada da lógica, e o núcleo mantém o P0 de pé se API ou front falharem. Camadas separadas para escalar (fonte viva, mais usuários ou telas) e para que um modelo possa entrar no núcleo quando o pipeline tiver mais dados, sem mudar API nem tela. O contrato foi corrigido pelo ADR-004.
- **Rejeitado:** Streamlit, HTML estático, planilha e banco. **Sacrifica:** simplicidade (dois runtimes).
- **Revisitar:** mais de ~30 usuários, escrita ou fonte viva.

<a id="adr-004"></a>
### ADR-004 — Contrato orientado a dados (16/10/2026)

- **Decisão:** o back devolve só códigos, parâmetros e números; nomes, frases e layout ficam no front (`web/copy/pt-BR.ts`) e na CLI (`cli_text.py`). O contrato é tipado (pydantic, OpenAPI, zod gerado), o front recusa código desconhecido e **não calcula valor de negócio**. Hoje é a versão 7.
- **Rejeitado:** texto no núcleo; camada BFF; catálogo de textos único. **Sacrifica:** dois catálogos de texto e artefatos gerados a manter.
- **Revisitar:** mais de um front, ou vários idiomas.

<a id="adr-005"></a>
### ADR-005 — Design system e navegação (16/10/2026)

- **Decisão:** shadcn (Radix + Tailwind v4) com tokens próprios, claro e escuro, contraste AA medido. Abas no lugar de seções colapsáveis; cinco páginas (Carteira, Equipe, Inteligência, Evidência, Como funciona) com menu central. Padrões em [design-system.md](./design-system.md).
- **Rejeitado:** CSS próprio; biblioteca fechada (MUI, Chakra). **Sacrifica:** mais dependências no front.
- **Revisitar:** mais de seis páginas, ou um design system corporativo.

<a id="adr-006"></a>
### ADR-006 — Regra A: dois limites de idade (16/10/2026)

- **Decisão:** **L1** = P90 das ganhas (106 d) e **L2** = maior ciclo fechado (138 d), calculados só com fechadas até o `as_of`. Engaging vira Focar (≤ L1, 157), Acompanhar (até L2, 141) ou Revisar (acima, 1.291; "Confirmar" na tela). Qualificar é Prospecting (500). A ordem dentro do grupo segue faixa e preço. Com Focar vazio, o cartão aponta o primeiro grupo seguinte com itens (**Q-01**). Sem venda ganha até o `as_of`, erro `no_won_history`.
- **Rejeitado:** só 138 d (Focar misturava 10 e 130 dias); só preço; limite fixo escolhido olhando o teste.
- **Sacrifica:** o ganho é pequeno. Em Val@10, 58,4% contra 53,8% do "só preço" e 23,2% do sorteio. Sem as negociações que nunca fecham, "só preço" fica 1,0 pp à frente; a Evidência mostra isso.
- **Revisitar:** dados com atividade mostrando que a idade não separa ganho; em produção, trocar L2 por um quantil robusto.

<a id="adr-007"></a>
### ADR-007 — Inteligência comercial descritiva (17/10/2026)

- **Decisão:** uma página que descreve o histórico, sem prever nem mudar a lista. Toda taxa leva n, faixa de Wilson 95% e veredito de acaso (Bonferroni, 7 dimensões). Receita decomposta em volume, taxa e ticket só por dimensão. Pessoas em ordem alfabética, sem índice. O padrão de fim de trimestre aparece só como conferência do registro (RJ-02).
- **Rejeitado:** painel de BI com rankings (RD-06, RJ-03); texto de LLM (RJ-07). **Sacrifica:** o "quem vende mais"; a receita varia por volume e mix, não por conversão.
- **Revisitar:** atividade, motivo de perda ou vários anos de histórico.

<a id="adr-008"></a>
### ADR-008 — Orientação de verificação e conta neutra (17/10/2026)

- **Decisão:** o "próximo passo" vira "O que verificar agora", uma consulta ao CRM que depende só do grupo e de a conta estar registrada, sem citar atividade nem intenção. Conta ausente é lacuna de cadastro, sem efeito em grupo nem ordem. A idade aparece ao lado da mediana, de L1 e de L2, sem semáforo. Empatadas ficam "sem ordem entre si".
- **Rejeitado:** barra de score (lida como chance); desempate por idade. **Sacrifica:** não prova que as escolhidas fecham mais. A validação com vendedores iniciantes reais não foi executada ([README](../README.md), recomendação 4).
- **Revisitar:** teste com vendedores reais.

<a id="adr-009"></a>
### ADR-009 — Qualificar antes de Acompanhar e Confirmar (17/10/2026)

- **Decisão:** ordem Focar → Qualificar → Acompanhar → Confirmar → Completar. Os 10 vendedores sem Focar começam por Qualificar.
- **Motivo [Dados]:** acima de L2, 1.469 observações de backtest e nenhuma ganha em 90 dias (Acompanhar: 10,2%; Focar: 39,3%). Nenhuma Prospecting tem desfecho, então não há prova a favor nem contra Qualificar.
- **Sacrifica:** a ordem é hipótese de produto; só o piloto mede se funciona.

<a id="adr-010"></a>
### ADR-010 — Priorização assistida, no navegador (18/10/2026)

- **Decisão:** um segundo mecanismo, declarado pelo vendedor e separado do scoring, para escolher entre oportunidades que a base não separa. Sete perguntas e pontos de 0 a 100 (pesos 20/20/15/15/15/10/5). Nenhuma resposta altera grupo, ordem, contrato, API, backtest ou Evidência. Pontos por resposta (`web/lib/assisted/model.ts`, `assisted-points-v1`): interesse 20 ou 0; momento 20 (até 30 d), 12 (31 a 90 d), 4 (depois) ou 0; necessidade 15, 7 (investigando) ou 0; urgência 15, 7 (possível) ou 0; orçamento 15, 7 (depende de aprovação) ou 0; decisão 10, 5 (sem acesso) ou 0; próxima ação 5 (com data até 30 d), 4 (data depois), 3 (sem data) ou 0. "Não sei" vale 0 e, com 4 ou mais, a oportunidade vai para "Investigar primeiro", sem posição. Roda no front (`lib/assisted/`), com respostas em `localStorage` e nada gravado no back: é a exceção declarada ao ADR-004.
- **Rejeitado:** motor no núcleo com POST (primeira rota não-GET, respostas de clientes no servidor); pontuação a partir dos dados (não há dado que a sustente).
- **Sacrifica:** pesos e pontos são hipóteses, e a tela diz "pesos iniciais, a validar". Os dados somem se o navegador for limpo: serve para demonstração e piloto pequeno.
- **Revisitar:** se vendedores reais lerem o número como previsão, ou se o piloto pedir persistência por usuário.

<a id="limites"></a>
## Limites

- As sondas desta etapa (GBM, conta, escritório, resolução por idade) e as "consultas diretas" (298 dentro do ciclo, 27 vendedores com carteira aberta) **não têm script no repositório** e não constam do data-audit. Os números do backtest vêm de `scripts/backtest.py`.
