# Decision log — Lead Scorer (Challenge 003)

Registro cronológico de decisões, erros da IA corrigidos e insights humanos. Cada entrada aponta para evidência verificável. Este arquivo alimenta as seções "Onde a IA errou e como corrigi" e "O que eu adicionei que a IA sozinha não faria" do README da submissão.

## [2026-09-22 23:20] marco — Leitura completa da documentação e escolha do Challenge 003

**Contexto:** primeira sessão com Claude Code (modelo Fable 5.1) na raiz do repositório forkado. Pedido: ler toda a documentação e montar o time de agentes para o Challenge 003.
**O que a IA propôs / fez:** leu README raiz, índice de challenges, os 4 briefs, CONTRIBUTING, submission-guide, template e .gitignore antes de qualquer decisão.
**O que estava errado ou incompleto:** n/a.
**Decisão humana:** Challenge 003 (Lead Scorer), por ser o mais "mão na massa" e o único cujo deliverable principal é software rodando.
**Alternativas descartadas:** 001/004 (análise) e 002 (diagnóstico + protótipo) — menos aderentes ao perfil de construção.
**Evidência:** `../../challenges/build-003-lead-scorer/README.md`; este arquivo.
**Impacto na entrega:** define o time de agentes e a stack.

## [2026-09-22 23:22] insight — Perfil real do dataset antes de desenhar qualquer agente

**Contexto:** em vez de escrever agentes com base em suposições sobre o dataset, a IA baixou a cópia CC0 do Kaggle (funcionou sem credenciais via endpoint público) e rodou um perfil com pandas.
**O que a IA propôs / fez:** contagens, nulos por estágio, faixas de datas, win rates, ciclos, checagem de integridade referencial.
**O que estava errado ou incompleto:** n/a (os achados foram verificados por código; ver `.claude/skills/crm-dataset/SKILL.md`).
**Decisão humana:** transformar os achados em guardrails codificados, não só em texto: hook `guard_leakage.py` bloqueia `close_value`/`close_date` em features e `now()/today()` em código de solução; CLAUDE.md fixa `SNAPSHOT_DATE = 2017-12-31`.
**Alternativas descartadas:** confiar no conhecimento prévio do modelo sobre o dataset (ele "lembrava" da quirk `GTXPro`, mas não do fato de 68% dos deals abertos estarem sem `account` — isso só apareceu ao rodar o código).
**Evidência:** saída do perfil colada na conversa (chat export a anexar em `process-log/chat-exports/`); `.claude/skills/crm-dataset/SKILL.md`.
**Impacto na entrega:** o scoring precisará degradar com elegância para deals sem conta; ordenar por valor concentraria tudo em GTK 500 (baseline a bater).

## [2026-09-22 23:25] decisao — Configuração do Claude Code dentro da pasta de submissão

**Contexto:** a regra do G4 proíbe alterar arquivos fora de `submissions/<nome>/`, e o `.gitignore` da raiz ignora `submissions/` inteira.
**O que a IA propôs / fez:** colocar `CLAUDE.md`, `.claude/agents`, `.claude/skills`, `.claude/hooks` e `.claude/settings.json` dentro de `submissions/bernardo-couto/`, rodando o Claude Code a partir dessa pasta. Assim a configuração vira evidência versionada do processo e nenhum arquivo externo é tocado.
**O que estava errado ou incompleto:** a primeira versão do `settings.json` usava regras `Edit(../../.gitignore)`; a sintaxe de caminho `../` não está documentada para permissões. Removido; o hook `guard_paths.py` (testado) já bloqueia qualquer edição fora da pasta.
**Decisão humana:** manter tudo dentro da pasta; documentar a necessidade de `git add -f` no CLAUDE.md, na skill `submission-rules` e no `/pr-check`.
**Alternativas descartadas:** `.claude/` na raiz (violaria a regra do PR ou exigiria lembrar de não commitar).
**Evidência:** `CLAUDE.md`, `.claude/settings.json`, saída dos testes de hook nesta sessão.
**Impacto na entrega:** o avaliador vê o "sistema" de trabalho, não só o resultado.

## [2026-09-23 00:05] decisao — Renomear agentes e adicionar security-engineer e machine-learning-engineer

**Contexto:** revisão do time de agentes antes do primeiro commit.
**O que a IA propôs / fez:** nomes `app-engineer` e `qa-engineer`.
**O que estava errado ou incompleto:** n/a (preferência de nomenclatura); faltava um papel de segurança e, com a entrada de Spark ML, um papel de MLOps.
**Decisão humana:** renomear para `application-engineer` e `quality-engineer`; criar `security-engineer` (pedido do Bernardo). A IA sugeriu e o Bernardo aceitou tacitamente `machine-learning-engineer` para operacionalizar o pipeline, separando desenho estatístico (data-scientist) de operação (jobs, versionamento, model card).
**Alternativas descartadas:** manter data-scientist responsável por tudo de ML (mistura análise com infraestrutura e enfraquece a revisão cruzada).
**Evidência:** `.claude/agents/`, `docs/agents-architecture.md`.
**Impacto na entrega:** 10 agentes; fluxo atualizado no CLAUDE.md.

## [2026-09-23 00:10] decisao — Pipeline de ML em Spark, UI sem Spark

**Contexto:** o Bernardo pediu Spark para construir um modelo de ML que "sempre execute a classificação", seguindo boas práticas.
**O que a IA propôs / fez:** alertou que 8.800 linhas não justificam Spark por volume e que um avaliador cético perguntaria "por quê Spark?". Propôs justificar como pipeline operacional (bronze/silver/gold em parquet por `as_of`, Spark ML Pipeline persistido e versionado, jobs idempotentes, PSI) e manter o Streamlit lendo só o parquet final, sem JVM em runtime.
**O que estava errado ou incompleto:** o JDK padrão da máquina é o 23, não suportado pelo Spark 3.5; a IA identificou o Corretto 21 instalado e transformou isso em guardrail (`spark.py` resolve `JAVA_HOME`; hook de sessão alerta).
**Decisão humana:** Spark confirmado pelo Bernardo como decisão de arquitetura. Registrar a justificativa honesta na documentação (não vender como necessidade de escala).
**Alternativas descartadas:** pandas + scikit-learn puro (mais simples, mas não atende ao requisito de pipeline reexecutável/escalável declarado pelo Bernardo); Delta Lake/MLflow (adiam-se: ganho marginal frente ao custo de dependências no protótipo; citados como evolução).
**Evidência:** `docs/solution-architecture.md`, `.claude/skills/spark-ml-practices/SKILL.md`, testes do hook `guard_leakage.py` bloqueando `randomSplit`, `current_date()` e `inferSchema=True`.
**Impacto na entrega:** stack, DoD e `/pr-check` atualizados (JDK, jobs reexecutáveis, modelo versionado, pip-audit).

## [2026-09-23 00:40] insight — Separar o que é mínimo esperado do que é diferencial

**Contexto:** revisão crítica do desenho antes do primeiro commit, com o g4-evaluator em mente.
**O que a IA propôs / fez:** na primeira versão, tratava os achados do dataset (68% sem conta, GTXPro, 14 vs 57 dias, 138 dias) como diferenciais. São achados que qualquer análise cuidadosa do dataset produz; o diferencial está no que se faz com eles.
**O que estava errado ou incompleto:** rubrica interna e CLAUDE.md inflavam o valor dos achados. Corrigido.
**Decisão humana:** (1) baseline "mais novo primeiro" com IC obrigatório no backtest; (2) seletor as-of e ações persistidas na UI; (3) commitar `gold/scores/as_of=2017-12-31` e `models/latest` para a UI abrir sem JDK; (4) documentar hooks como diferencial com evidência de bloqueio real.
**Alternativas descartadas:** manter a rubrica original.
**Evidência:** diffs em `CLAUDE.md`, `.claude/skills/eval-rubric/SKILL.md`, `.claude/agents/{data-scientist,application-engineer}.md`, `.gitignore`.
**Impacto na entrega:** prioridades da próxima sessão redefinidas.

## [2026-09-23 10:30] decisao — Entrega em Python + React + Docker, com Swagger e documentação navegável

**Contexto:** o Bernardo definiu que a entrega precisa ter código em Python e React, rodar via Docker, expor Swagger bem documentado e ter documentação HTML navegável gerada do Markdown, seguindo o design system do G4.
**O que a IA propôs / fez:** substituir o Streamlit por FastAPI (API lendo o parquet de scores) + React/Vite/Tailwind (tipos gerados do OpenAPI), Docker Compose com serviços `api`, `web`, `docs` e perfil `pipeline` (JDK 17) para o Spark; MkDocs Material para as docs; tokens do G4 extraídos do CSS público do site (`#001F35`, `#B9915B`, `#F5F4F3`, Manrope, Libre Baskerville).
**O que estava errado ou incompleto:** a visão geral da arquitetura estava em ASCII e ilegível; substituída por Mermaid. Faltavam papéis de produto e liderança técnica: criados `product-manager`, `product-owner`, `product-designer`, `tech-lead` (pedido do Bernardo) e `backend-engineer` (sugerido pela IA, para separar API de frontend). `ml-engineer` renomeado para `machine-learning-engineer`.
**Decisão humana:** stack confirmada pelo Bernardo. Logo do G4 não será embutido (wordmark textual), por cautela com marca.
**Alternativas descartadas:** Streamlit (ADR 0002); Next.js full-stack (contrato já nasce em Pydantic); Docusaurus (ADR 0004).
**Evidência:** `docs/adr/0002…0004`, `docs/solution-architecture.md`, `.claude/skills/{g4-design-system,api-documentation}`, `.claude/agents/`.
**Impacto na entrega:** três serviços em Compose; caminho curto sem JDK graças aos artefatos commitados.

## [2026-09-23 10:45] decisao — Jev (System One model) avaliado e rejeitado para o scoring

**Contexto:** pergunta do Bernardo: vale usar o Jev (typesafe.ai) nesta solução? Critério dele: não trazer complexidade sem necessidade.
**O que a IA propôs / fez:** leu o anúncio oficial (modelo de decisão estruturada, saídas tipadas, probabilidades calibradas, 70–500 ms, sem geração de texto, API em early access nos EUA). Concluiu que o problema é tabular e supervisionado com 6.711 desfechos próprios, onde um modelo treinado nos nossos dados é mais preciso, explicável e offline; Jev não é treinável nos nossos dados e só faria sentido com texto livre (notas, e-mails), que o dataset não tem.
**Decisão humana:** não usar (ADR 0005). Reavaliar se o CRM passar a ter texto por deal.
**Alternativas descartadas:** Jev como classificador paralelo "para comparar" (custo de integração e chave de API sem ganho no backtest); LLM para redigir explicações (templates determinísticos são auditáveis e não alucinam).
**Evidência:** `docs/adr/0005-sem-llm-no-scoring.md`; `https://typesafe.ai/blog/introducing-system-one-models-and-jev`.
**Impacto na entrega:** zero dependência de rede ou chave em runtime; "IA" na solução = modelo treinado + engenharia assistida por IA, dito explicitamente nas limitações.

## [2026-09-23 11:10] marco — Process log estruturado e exportação da sessão

**Contexto:** pedido do Bernardo para popular o process-log antes de iniciar o código.
**O que a IA propôs / fez:** escreveu `tools/export_claude_session.py` (converte o JSONL da sessão do Claude Code em Markdown legível, sem blocos de raciocínio interno), gerou o primeiro chat export, a narrativa cronológica e a consolidação de erros da IA.
**Decisão humana:** o process log é gerado por script a cada sessão, sem screenshots manuais como única evidência.
**Evidência:** `process-log/{01-narrativa.md,02-erros-da-ia.md,chat-exports/,tools/}`.
**Impacto na entrega:** process log deixa de depender de screenshots manuais; cada sessão futura gera um export com o mesmo script.

## [2026-09-23 12:30] decisao — Padrões visuais assumidos pelo orquestrador (pendentes de confirmação do Bernardo)

**Contexto:** o `product-designer` entregou `docs/design/{ux-spec,design-tokens,accessibility,review-checklist}.md` e deixou quatro decisões visuais (V1–V4). O Bernardo não estava acompanhando em tempo real.
**O que a IA propôs / fez:** assumiu padrões para não bloquear o `application-engineer`: tiers C/D com fundo tinta e texto escuro (contraste AA); aviso de conta não informada como ícone + texto discreto na fila e faixa completa só no drawer; serif apenas em h1 e wordmark; densidade de 3 linhas por deal com fallback de 2.
**O que estava errado ou incompleto:** o scaffold usava texto branco sobre dourado e sobre os cinzas de tier C/D — contraste 2,89:1 a 4,39:1, abaixo de AA. Pego pela tabela de contraste calculada pelo designer.
**Decisão humana:** pendente — o Bernardo confirma ou ajusta ao ver no navegador.
**Evidência:** `docs/design/design-tokens.md` (tabela de contraste com script).
**Impacto na entrega:** paleta de tiers e rodapé ajustados no web; token `g4.muted` adicionado.

## [2026-09-23 13:40] erro-ia — Hipótese "a conta é preenchida ao longo do ciclo" refutada pelos dados

**Contexto:** a skill `crm-dataset`, escrita na sessão 1, interpretava a ausência de conta em 68% dos abertos como preenchimento progressivo ao longo do ciclo.
**O que a IA propôs / fez:** a interpretação foi da IA, sem teste. O `data-engineer`, ao construir a camada gold com cortes temporais, mediu: fração de Engaging com conta ≈ 0,3 em todo mês de engajamento (0,21–0,54, sem tendência); 100% de conta nos deals rotulados de qualquer corte vs. 32% no lote a pontuar no snapshot.
**O que estava errado ou incompleto:** a conta é um artefato temporal (parece registrada no fechamento), não um sinal de progresso. Se usada como feature, `account_known` prevê "já fechou", não "vai fechar".
**Decisão humana (orquestrador; a confirmar pelo Bernardo):** proibir `account_known` como feature preditiva; avaliar o modelo com e sem features de conta; PSI obrigatório em `account_*`; skill corrigida.
**Alternativas descartadas:** manter a hipótese e "explicar" o PSI depois.
**Evidência:** `docs/data-quality-report.md`; `.claude/skills/crm-dataset/SKILL.md` (item 4).
**Impacto na entrega:** spec do scoring e backtest ajustados; vira exemplo concreto de "onde a IA errou" no README.

## [2026-09-23 13:45] insight — 81% do pipeline aberto é um lote zumbi; a ferramenta precisa de uma fila de decisão

**Contexto:** `days_in_engaging` no snapshot: mínimo 9, mediana 165, máximo 423; 1.291 de 1.589 Engaging acima de 138 dias (maior ciclo já fechado). Picos de engajamento em jul/ago 2017.
**O que a IA propôs / fez:** tratar como achado de negócio (higiene do CRM) e criar uma fila "Decidir / limpar" com valor nominal em risco, em vez de marcar tudo como "agir agora". O score continua ordenando dentro da fila, mas a narrativa da tela muda.
**Decisão humana:** pendente de confirmação do Bernardo; encaminhado ao `data-scientist` e ao `product-designer`/`application-engineer`.
**Evidência:** `docs/data-quality-report.md`.
**Impacto na entrega:** recomendação executiva concreta para a Head de RevOps; reason code `ZOMBIE_RISK` deixa de ser exceção e vira classe de deal.

## [2026-09-23 14:30] erro-ia — Duas premissas da skill de dados caíram no backtest temporal

**Contexto:** a skill `crm-dataset` (sessão 1) afirmava que "sobreviver em Engaging é sinal positivo até ~90 dias" e o CLAUDE.md tratava "mais novo primeiro" como baseline forte a ser batido.
**O que a IA propôs / fez:** ambas as afirmações vieram de estatísticas descritivas (curva de sobrevivência 63%→76%) sem teste fora do tempo.
**O que estava errado ou incompleto:** o `data-scientist` mostrou que, em corte temporal fixo, a idade não discrimina entre deals vivos (AUC-ROC 0,50) e que "mais novo primeiro" só parece forte quando censurados são contados como Lost (efeito do lote zumbi). Mais amplo: nenhum sinal (agente, produto, setor, conta, carga, LR) prevê fechamento melhor que o aleatório nos dois cortes.
**Decisão humana (orquestrador; a confirmar pelo Bernardo):** aceitar o posicionamento honesto — a ferramenta ordena por valor esperado × timing e separa a fila de zumbis (R$ 3,19 mi nominais); p_win usa só taxa-base por produto; demais sinais viram reason codes informativos; LR fica em modo sombra com critério de promoção explícito. Manter urgência com peso 40 para o score não virar lista de preços, mesmo custando receita no top 20% (0,38 vs 0,51 de "ordenar por preço").
**Alternativas descartadas:** manter fatores sem poder preditivo no score "porque o vendedor espera vê-los" (viraria ruído com cara de precisão); otimizar receita bruta ordenando por preço (a Head já sabe fazer isso sem ferramenta).
**Evidência:** `docs/figures/10_backtest.md`, `docs/scoring-logic.md`, `solution/pipeline/analysis/00_hypotheses.md` (11 hipóteses, 7 refutadas).
**Impacto na entrega:** skills `crm-dataset` e `scoring-methodology` corrigidas; README e UI dirão explicitamente o que a ferramenta não faz; `QUARTER_END_WINDOW` entra como reason code informativo.

## [2026-09-23 15:20] decisao — Revisão de RevOps: linguagem honesta, duas filas, sem fim de trimestre

**Contexto:** `docs/revops-review.md` validou os 14 reason codes e o enquadramento de produto após o backtest.
**O que a IA propôs / fez:** o `product-designer` havia rotulado `p_win` como "Prob. de fechar" e dado direção/ação a reason codes sem poder preditivo; o `data-scientist` propusera `QUARTER_END_WINDOW` com percentuais.
**O que estava errado ou incompleto:** `p_win` é a taxa do produto (igual para todos os deals daquele produto), não probabilidade individual. Fim de trimestre: Won é plano ao longo do mês e do ano (566–805/mês); o que varia é o Lost (110–140 em mar/jun/set/dez vs 287–367 nos demais) — artefato de registro, não comportamento de fechamento.
**Decisão humana (orquestrador; a confirmar pelo Bernardo):** rótulo "Fecham {p}% dos {product}"; reason codes informativos como "Contexto", sem pontos nem ação; `QUARTER_END_WINDOW` vetado; duas filas ("Trabalhar" / "Confirmar ou encerrar"), sem a palavra "zumbi" na UI; "Ocultar da minha fila" em vez de "Descartar"; lista "o que a ferramenta não faz" na primeira abertura; pesos 25/35/40 mantidos (25/50/25 daria Spearman 0,93 com preço).
**Alternativas descartadas:** peso ajustável pelo manager na v1; exibir percentuais de fim de trimestre.
**Evidência:** `docs/revops-review.md` §1, §3, §5, §7 (comando reproduzível).
**Impacto na entrega:** UI e textos do pipeline ajustados; sprint de limpeza do CRM (561 deals / R$ 1,25 mi em 139–180 dias como primeira onda) vira recomendação executiva; marcar os 1.291 como Lost derrubaria o win rate de 63% para 53% — reportar como coorte separada.

## [2026-09-23 15:50] decisao — Revisão de segurança: correções aplicadas e riscos aceitos

**Contexto:** `docs/security-review.md` (0 críticos/altos em runtime; 5 médios; 7 baixos; `pip-audit` 0 CVEs; `detect-secrets` 0).
**O que a IA propôs / fez:** corrigiu nginx (headers herdados perdidos em `/assets/`, CSP, `server_tokens off`, limite de body), contextos Docker (`.dockerignore` por serviço; contexto do docs de toda a submissão para 378 kB), `no-new-privileges` e `cap_drop` no compose, `.gitignore` e `tools/git-stage.sh`. Recomendou endurecer os hooks (fail-closed; variantes `git -C … push --force`, refspec `+main`) — aplicado pelo orquestrador e testado.
**O que estava errado ou incompleto:** os hooks originais liberavam a ação quando o payload era inválido e não cobriam `git -C`. O `COPY . .` do web arrastava `node_modules` do host para a imagem.
**Decisão humana (orquestrador; a confirmar pelo Bernardo):** manter API sem autenticação no protótipo (documentado como limitação); manter portas em `0.0.0.0` para demo; adiar bump de `vite`/`vitest` (dev) e `react-router-dom` v7 para depois de o frontend estabilizar, em commit isolado; `nginx-unprivileged` e Mermaid vendorizado como recomendações ao `tech-writer`/`application-engineer`.
**Evidência:** `docs/security-review.md`; testes dos hooks nesta sessão (deny em `git -C … --force`, `+main`, payload inválido; allow em push normal).
**Impacto na entrega:** seção de riscos do modelo e LGPD vai para `docs/limitations.md`.

## [2026-09-23 16:40] decisao — Pipeline de scoring entregue; modelo sombra não promovido; convenções finais

**Contexto:** `machine-learning-engineer` implementou regras em Spark SQL, LR em modo sombra, jobs `train`/`score`, model card e validação linha a linha do parquet contra `ScoredDeal`.
**O que a IA propôs / fez:** com `regParam=0,1` (spec) a elastic-net zerava todos os coeficientes; ajustado para 0,01 para o sombra não ser degenerado. A calibração isotônica no último mês do frame piorou o Brier (0,273/0,276 vs 0,235/0,243 da taxa-base) porque esse mês só tem deals rápidos.
**O que estava errado ou incompleto:** a spec misturava unidades nos pesos dos reason codes (Δp_win vs pontos) e a UI assumia frações; unificado em pontos de `priority_score` (0–100) para todos os códigos.
**Decisão humana (orquestrador; a confirmar pelo Bernardo):** LR **não promovida** (`blend_model_weight = 0`) porque falha o critério explícito (AUC-PR 0,628/0,582 vs taxa-base 0,661/0,600; Brier pior). `sales_price` gravado no parquet e adicionado ao contrato (schema 1.1.0). `QUARTER_END_WINDOW` não existe. Snapshot final idêntico ao protótipo do data-scientist (A 67 / B 516 / C 771 / D 735; 1.291 parados; R$ 3,185 mi nominais; Spearman 0,461).
**Alternativas descartadas:** promover o modelo "por ter um modelo"; esconder o resultado negativo do backtest.
**Evidência:** `solution/models/2017-12-31-rules-v1/{metrics.json,model_card.md}`, `solution/data/gold/scores/as_of=2017-12-31/_manifest.json`, `docs/ml-pipeline.md`, 64 testes em `solution/pipeline/tests`.
**Impacto na entrega:** a tela Qualidade mostra o empate com o acaso como frase padrão; o valor da ferramenta está em valor × timing e na fila de limpeza.
