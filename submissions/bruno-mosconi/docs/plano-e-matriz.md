# Plano, critérios de aceite e matriz de rastreabilidade

**Fontes dos requisitos:**
- enunciado: `challenges/build-003-lead-scorer/README.md` (R);
- `README.md` da raiz (P, processo seletivo);
- `CONTRIBUTING.md` (C);
- `submission-guide.md` (G);
- decisões do Bruno, D1–D26 (`AGENTS.md`, seção 7, e `process-log/decisoes.md`).

O resumo completo das regras do exercício está em `AGENTS.md`, seção 2.

**Prazo:** domingo, 11/10/2026, à noite.

## 1. Critérios de aceite

| ID | Critério | Origem |
|---|---|---|
| CA0 | **Revisão completa antes de construir:** regras, dados (recalculados de forma independente), código e documentação revisados; resultado em `process-log/01-revisao-inicial.md`; erros confirmados registrados. | D16; P "entendeu o problema antes de executar"; G "evidência de verificação" |
| CA1 | Roda seguindo o README: `npm ci`, `npm run dev` e `npm run build` funcionam com Node 22.18 ou superior (D20). A URL pública abre a mesma versão. (Atendido. A Vercel compila com o Node 24.x, por override do projeto em produção; o build publicado é idêntico ao do Node 22: no `7b82e3f`, o local com Node 22.23 e o publicado geram o mesmo `index-zdocz14R.js`.) | R "precisa rodar"; R Setup; D6 |
| CA2 | Usa as 4 tabelas originais (mais `metadata.csv`), versionadas sem alteração (hash SHA-256 conferido em teste). Contagens batem: 8.800 negócios; 4.238 / 2.473 / 1.589 / 500; 35 vendedores; 7 produtos; 85 empresas. | R "dados reais" |
| CA3 | O score vai além do valor: **potencial** = chance de fechar pelo histórico (entrada tardia, D27) × preço de lista, e a lista é ordenada pelo potencial. Cada negócio quente ou esfriando mostra um **score de 0 a 100** (D39): a posição do potencial entre todos os quentes e esfriando da empresa na data. Score 92 = mais potencial que 92% deles. A função do score é nova (`src/core/score.ts`), com testes: mesma ordem do potencial em toda lista e data, valores de 0 a 100, empates com o mesmo score. Frios e prospecção não têm score. No backtest com a regra final, o potencial ganha de "só preço" com IC 95% que não inclui o zero, calculado por `npm run auditoria` e fixado em teste (hoje, +7,66 p.p., IC de 3,49 a 12,62, em 31/07, 31/08 e 30/09). A coorte limpa, como sensibilidade, chega à mesma conclusão (+18,69 p.p. na única foto disponível, 30/09). | R "não é só ordenar por valor"; D5; D30; D39 |
| CA4 | O painel de cada negócio mostra o score, o potencial em US$, a conta por trás (preço de lista × chance) e a frase do motivo, na língua do vendedor (D40): "De cada 100 negócios que chegaram aos N dias ainda abertos, X fecharam venda". O X da frase é o mesmo número da conta (chance inteira; o potencial exibido é preço × essa chance, sem inverter a ordem em nenhuma das 6.016 linhas, conferido com os dados reais). "O que fazer" muda por situação: quente, esfriando, perto de ficar frio, frio. A chance é apresentada como histórico, não como previsão. Frase, conta e score vêm do mesmo cálculo (teste). | R "entender por quê"; R "Explainability ganha"; D5; D28; D36; D39; D40 |
| CA5 | Filtros regional → gestor → vendedor (atendido pela navegação por pessoa e pelo seletor de equipe, D57). Três listas: "Foque agora" (selo "Esfriando" a partir de 90 dias), "Revisar ou encerrar" (mais de 138 dias) e "Inicie contato" (Prospecting por preço, só em 31/12/2017). Vendedor sem negócios ou sem negócios recentes vê um estado vazio que diz o que fazer. | R bônus filtros; R "segunda de manhã"; D2; D4; D13 |
| CA6 | Data de referência padrão 31/12/2017. O seletor volta no tempo e reconstrói o funil só com o que se sabia na data. Teste anti-vazamento: mudar desfechos posteriores a T não altera o resultado em T. Só ficam disponíveis as datas em que toda faixa tem IC 95% de no máximo ±5 p.p. (`hasEnoughHistory`, D27). | D1; D27 |
| CA7 | `npm run auditoria` reproduz o backtest (44,41% · 43,16% · 40,10% · 36,17% · 32,23% · 15,40%), fixado em `src/core/reference.test.ts`. TypeScript e Python precisam concordar; se divergirem, a revisão decide qual está certo e registra o motivo (D22; revisão inicial, R1–R4). | R "o scoring faz sentido?"; G "zero evidência de verificação" é fraqueza |
| CA8 | Vendedor, produto, gestor, regional, setor e empresa ficam fora do score. A tela "Como funciona" mostra o que foi testado e descartado, com p-valores e backtest. | R "usa as features certas?"; D3 |
| CA9 | Sem servidor, sem banco, sem LLM, sem chamada de rede em tempo de execução. | D7; D8; D15 |
| CA10 | Código mantível e pronto para crescer: TypeScript estrito; núcleo puro separado da UI; contrato de dados `Dataset` com dois adaptadores (CSV e JSON) que dão o mesmo resultado (D51); testes do núcleo; lint e formatação. `npm run check` verde. `npm run bench` mede o núcleo com os dados multiplicados por 100. | R "código limpo"; D15 |
| CA11 | README no template, com: Setup; Lógica (fórmula e faixas); validações; 2–3 exemplos reais de saída; checagens de sanidade (distribuição por lista); Limitações; resumo de "Como escalar". | R Documentação; C; G "formato da solução" |
| CA12 | Process log da etapa do Claude Code: nota curta sobre a preparação; ferramentas; revisão inicial (leitura do problema antes de construir); decisões; erros da IA e correções; o que o Bruno adicionou; número de iterações (sem horas); prints; exports. | P; R; G "o que queremos ver no process log"; D17 |
| CA13 | O PR só altera `submissions/bruno-mosconi/` (checado por comando). Título `[Submission] Bruno Mosconi — Challenge 003`. Um PR. Sem chaves, arquivos de sistema ou artefatos derivados. | C |
| CA14 | Um vendedor não técnico entende: vocabulário de CRM brasileiro, moeda em US$, legível em 1280 px e 390 px. O testador de uso cumpre as tarefas das três personas. | R "vendedor consegue usar"; R "ajuda a tomar decisão"; D11 |
| CA16 | Página "Como funciona" (D19, incremento 5): a camada de cima explica a regra numa tela; a de baixo traz S1–S4 (os dados; a chance cai com a idade; o que não muda a ordem, incluindo o mês do trimestre; como validamos). Cada seção diz o que os dados mostraram, como foi conferido e que decisão mudou. Todo gráfico tem tabela. Todo número vem de função de `src/core` coberta por teste. Legível em 1280 e 390 px. Pode ser cortada (D25), menos o piso (D31): três tabelas vindas de `src/core`, sem gráfico (curva da coorte × só concluídos; backtest com IC; dimensões com p entre concluídos e na coorte) e uma linha no painel de motivo. | D19; P "entendeu o problema"; R "Explainability" |
| CA15 | `docs/como-escalar.md` completo: o que existe e foi medido (números de `npm run bench` preenchidos); o que muda com volume, frescor, usuários e ações; arquitetura em três fases; o que não muda; riscos e controles. O README resume e aponta para ele. (Atendido: os riscos estão na tabela "Riscos e controles", seção 12 do `docs/como-escalar.md`, D58.) | R Limitações ("o que precisaria pra escalar"); D15 |

## 2. Incrementos e agenda

A agenda é por dia. Não se declaram horas (D17); os commits registram a sequência.

| # | Quando | Incremento | Agentes | Pronto quando |
|---|---|---|---|---|
| 0 | sexta | Fork, clone, branch, pasta, setup do Claude Code e validação (seção 4) | — | todos os checks da seção 4 passam |
| 0b | sexta | **Revisão completa** (`AGENTS.md`, seção 8): regras, recálculo independente dos números, código, documentação | critico, revisor | CA0; resumo mostrado ao Bruno |
| 1–3 | sexta (feito na revisão, C1 e C2) | TS + Vitest + Biome; leitura dos dados; núcleo (coorte, faixas, valor ponderado, listas, backtest, estatística); testes à mão, contra o scipy e com os números reais; `npm run auditoria` | critico, revisor | CA2, CA3 (núcleo), CA6 (núcleo), CA7 |
| 4 | sábado (aprovado no G1, D25) | Interface do vendedor e do gestor: filtros, barra de números, três listas, painel de motivo, seletor com 5 datas (D1), estados vazios; Vite e React. Portão visual com prints em 1280 e 390 px antes de fechar (D12) | critico, revisor, testador-de-uso | CA4, CA5, CA6 (tela), CA14 |
| 5 | sábado/domingo | Página "Como funciona" com a investigação (D19) | revisor, testador-de-uso | CA8, CA9, CA16 |
| 6 | domingo | Revisão de segurança, correções, deploy na Vercel (com autorização) e teste contra a URL | revisor, testador-de-uso | CA1 |
| 7 | domingo | README, `docs/como-escalar.md` com as medições, process log, prints finais | revisor | CA11, CA12, CA15 |
| 8 | domingo | Banca simulada, checagem do PR, abertura do PR (com autorização) | critico, revisor | CA13 |

**Se o tempo apertar, cortar nesta ordem:**
1. A página "Como funciona" (CA16) fica só com o essencial; a tela do vendedor não pode ser cortada (D25).
2. O segundo adaptador JSON e o `bench` (os números medidos do CA15).
3. O layout de celular fica com uma lista simples.

Já aplicado: o seletor de data oferece só 31/12/2017 e as 4 datas do backtest (ajuste da D1).

**Não pode ser cortado:** CA0–CA5, CA7, CA11–CA13, CA15, o piso do CA16 (D31) e a tela do vendedor (D25).

## 3. Matriz requisito → artefato → validação → evidência

| Requisito | Artefato | Validação | Evidência no PR |
|---|---|---|---|
| CA0 Revisão | `process-log/01-revisao-inicial.md` | recálculo independente; achados reproduzidos | relatório + commit de correções |
| CA1 Rodar | `solution/package.json`, README Setup | clone limpo + comandos do README; abrir a URL | saída dos comandos; link Vercel; print |
| CA2 Dados reais | `solution/data/*`, `src/core/data.ts` | `data.test.ts` (hash) e `reference.test.ts` (contagens) | saída do `npm run check` |
| CA3 Score | `src/core/rules.ts`, `src/core/backtest.ts` | `reference.test.ts`: ganho sobre "só preço" com a regra final | testes; `auditoria-ts.md` |
| CA4 Motivo | frase gerada no núcleo (incremento 4), painel de motivo | teste frase = cálculo | teste + print |
| CA5 Listas e filtros | `src/ui/*` | testes do núcleo das listas + `npm run e2e` | prints do testador |
| CA6 Voltar no tempo | `src/core/rules.ts` (estado em T), seletor | teste anti-vazamento | teste |
| CA7 Backtest | `src/core/backtest.ts`, `analysis/*.py`, `reference.test.ts` | TS = Python, ou divergência decidida (D22) | saída do `npm run auditoria` |
| CA8 Descartados | "Como funciona", `docs/analise-exploratoria.md` | revisor confere números com a análise | print + texto |
| CA9 Sem rede | build estático | revisor procura `fetch` e URLs | parecer |
| CA10 Código e escala | `src/core` vs `src/ui`, `Dataset` e os dois adaptadores (CSV e JSON), Biome, TS estrito, `bench` | `npm run check`; `npm run bench`; revisor | saídas + parecer |
| CA11 README | `README.md` | critico (banca simulada) + leitura do Bruno | arquivo |
| CA12 Process log | `process-log/*` | revisor (dados pessoais) + critico | arquivos |
| CA13 Escopo do PR | branch `submission/bruno-mosconi`, `tools/adicionar-ao-git.sh` | travas do script a cada commit; `git diff --name-only upstream/main...HEAD` só lista a pasta | saída do comando |
| CA14 Entendível | textos da UI | testador-de-uso com 3 personas, 1280 e 390 px | prints + relatório |
| CA15 Como escalar | `docs/como-escalar.md`, resumo no README | critico confere se cada afirmação de "o que existe" tem prova; números do `bench` preenchidos | arquivo |

## 4. Incremento 0: aplicar e validar o setup

**Git** (feito pelo Bruno; o fork fica público no GitHub):
1. Fork de `Gestao-Quatro-Ponto-Zero/ai-master-challenge` para a conta `bmosconi`.
2. `mkdir -p ~/Projetos && cd ~/Projetos && git clone https://github.com/bmosconi/ai-master-challenge.git`. Pasta pessoal, fora das pastas de projetos da empresa.
3. `cd ~/Projetos/ai-master-challenge`.
4. `git remote add upstream https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge.git`.
5. `git config user.name "Bruno Mosconi"` e `git config user.email "<e-mail pessoal ou noreply do GitHub>"`. A configuração vale só neste repositório; os commits são públicos e não devem levar e-mail da empresa.
6. `git checkout -b submission/bruno-mosconi`.
7. Copiar a pasta `submissions/bruno-mosconi` do zip para dentro do clone.
8. `echo ".claude/settings.local.json" >> .git/info/exclude`. O Claude Code grava esse arquivo local na raiz do repositório quando a sessão abre numa subpasta.
9. `sh submissions/bruno-mosconi/tools/adicionar-ao-git.sh`. Não use `git add -f submissions/bruno-mosconi`, que levaria `node_modules/` e `.env` junto.
10. `git commit -m "chore: setup do Claude Code e material de partida"`.
11. Nada de `git push` até o Bruno decidir publicar.

**Skill de interface** (uma vez, no nível do usuário):
- Rode `/plugin install frontend-design@claude-plugins-official`.
- Se o marketplace não aparecer, rode antes `/plugin marketplace add anthropics/claude-plugins-official`.

**Claude Code** (abrir o Cursor na pasta `submissions/bruno-mosconi`, não na raiz):

| Check | Como | Esperado |
|---|---|---|
| Hook testado | `node --test .claude/hooks/guard-pasta.test.mjs` | 10 testes passando |
| Confiança no workspace | aceitar o diálogo ao abrir | permissões do projeto ativas |
| Configuração carregada | `/status` | "Setting sources" inclui as configurações do projeto; cwd termina em `submissions/bruno-mosconi` |
| Instruções carregadas | `/memory` | `CLAUDE.md` da pasta listado; o conteúdo do `AGENTS.md` aparece via import |
| Agentes | `/agents` | `critico` e `revisor` (Opus 5.5), `testador-de-uso` (Sonnet 5.5) |
| Hook registrado | `/hooks` | PreToolUse com `guard-pasta.mjs` |
| Hook bloqueia | pedir: "crie o arquivo ../../teste-guard.txt" | bloqueado com a mensagem do guard |
| Hook permite | pedir: "crie solution/teste-guard.txt" (apagar depois) | criado |
| Skill | `/plugin` | `frontend-design` instalada e habilitada |
| Modelo real dos agentes | acionar o `critico` com um plano curto; depois procurar `"model"` no transcript do subagente em `~/.claude/projects/` | `claude-opus-5-5` |
| MCP | `/mcp` | desligar neste projeto os servidores que não servem ao desafio |

A configuração aparece nos exports das sessões (`process-log/chat-exports/`) e nos testes do hook (`node --test .claude/hooks/guard-pasta.test.mjs`); não há prints desta etapa.
