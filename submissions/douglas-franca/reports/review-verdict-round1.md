# Review adversarial G8 — round 1

> _Nota de publicação: referências a submissões de outros candidatos e a arquivos locais de consulta foram retiradas deste relatório antes da publicação; as comparações com os PRs #91 e #72, usados como régua, foram mantidas._

**Avaliador simulado:** `g4-reviewer` (baseado nos critérios públicos do repositório)
**Escopo:** `submissions/douglas-franca/` na branch `submission/douglas-franca` (HEAD `df2f903`)
**Data:** 2026-09-18

---

**Score 9/10 — ⭐ Excepcional, com acabamento pendente antes do PR**

A submissão faz o que o PR #91 fez e vai além em quatro frentes verificáveis: **prova o mecanismo** do "sem sinal" (Poisson com λ fixo, não só "dataset sintético"), **pré-registra a régua** e conclui por **equivalência** em vez de ausência de significância, **mede a IA contra si mesma** (5 baselines com as 19 afirmações conferidas por código) e **reproduz byte a byte** a partir de um checkout limpo. O ponto mais forte não é estatístico: é que a entrega responde "qual falha de processo gerou esta lacuna e quem conserta na segunda-feira", com matriz AUTO/ASSIST/HUMANO, regra de promoção de nível e RACI com um único responsável por decisão.

Não segura a aprovação. Mas o process log anuncia três buracos que ele mesmo não fechou, um número de doc não passa na conferência, e 52.214 linhas do dataset do challenge estão versionadas em `.parquet` — dois motivos de reprovação que aparecem nos reviews públicos do repositório (higiene e process log incompleto). São correções de minutos; deixá-las é regalar o único ângulo de ataque que a submissão tem.

## Bloqueadores B1–B9: **nenhum**

| ID | Verificação | Resultado |
|---|---|---|
| B1 | `git diff --name-only main...HEAD \| grep -v '^submissions/douglas-franca/'` → vazio; 141 arquivos, todos na pasta | **PASS** |
| B2 | `git ls-files submissions/douglas-franca \| grep -E 'venv\|pycache\|pytest_cache\|pkl'` → vazio; `.gitignore` presente (`submissions/douglas-franca/.gitignore:1-33`) bloqueia `data/`, `.venv/`, `.intel/`, `*.pkl` | **PASS com ressalva** (ver C4) |
| B3 | `find process-log -type f` → só `.md` e `.png`; zero PDF/DOCX | **PASS** |
| B4 | 48 PNGs (`ls process-log/screenshots/*.png \| wc -l` → 48) + 5 baselines literais em texto + narrativa (`decisions.md`, `ai-errors.md`). O guia aceita "escolha um ou combine" (`submission-guide.md:22`) | **PASS** (ver C1) |
| B5 | 16 commits, um por gate, máx. 31 arquivos num commit (`git log --format=%h main..HEAD \| tail -r \| while read c; do git show --name-only --format= $c \| grep -c .; done`). Referência: #91 aprovado com 19 commits | **PASS** |
| B6 | 30+ afirmações numéricas conferidas contra `outputs/tables/` e contra execução do código. 1 erro encontrado, não decisório (ver C3) | **PASS com ressalva** |
| B7 | Nenhuma diferença irrelevante vendida como insight; a submissão faz o oposto de forma sistemática (`docs/statistical-report.md:47` desmonta "moda é o pior patrocinador"; `:67` desmonta `#religious`) | **PASS** |
| B8 | `.claude/settings.json` nega `Bash(gh pr create:*)` e `gh pr merge`; `CLAUDE.md:7-9` exige aprovação por edição; `decisions.md` traz 14 decisões nas palavras literais do Douglas, com alternativa rejeitada | **PASS** |
| B9 | Roda do zero. Comando e saída reais abaixo | **PASS** |

### B9 — evidência de reprodutibilidade

Checkout limpo da branch em diretório temporário (`git archive submission/douglas-franca | tar -x`), sem `data/` (ignorada), seguido de `uv sync` e do pipeline do `README.md:178-188`:

```
uv run python src/audit/run_audit.py          → 16 achados DQ-01..DQ-16 impressos
uv run python src/analysis/run_inference.py   → inf-summary.json completo
uv run python src/analysis/implied_cost.py    → 3 tabelas de custo implícito
uv run python src/audit/verify_baseline_claims.py → 19 + 4 checagens
uv run pytest -q                              → 24 passed in 9.61s
diff -rq <outputs regerados> <outputs versionados> → (vazio)
```

**Os CSVs regerados são idênticos aos versionados.** Nenhum número da entrega é órfão de código. Isso está acima do #91 e responde ao ponto de melhoria que o avaliador deixou no #72 ("em uma entrega real, isso pediria um snippet de código/notebook para validação independente").

O único pré-requisito externo é `scripts/download_data.py` (kagglehub, sem login — `scripts/download_data.py:3`), documentado no README. `data/` ausente não quebra nada além dos scripts que dependem dela, e o app publicado não depende de `data/`.

---

## O que se destacou

1. **Mecanismo, não sintoma** — `docs/data-quality-report.md:9-21` + `outputs/tables/dq-poisson.csv`. Conferido: var/média views 0,9906 · likes 1,0030 · shares 0,9986 · comments 0,9931; **76 segmentos** entre 0,9444 e 1,0381 (`python3 -c` sobre o CSV: 80 linhas, 76 não-TOTAL). O #91 identificou "dataset sintético"; aqui o gerador é nomeado e provado, com p de qualidade de ajuste e λ constante entre segmentos. **Owner: data-auditor.**

2. **Régua antes do teste, e equivalência em vez de ausência** — `process-log/decisions.md:12` registra ±1 p.p. **antes** de qualquer teste, com as alternativas rejeitadas (±0,5 e ±2 p.p.) e o motivo ("evita escolher depois a régua que favorece um resultado"). `docs/statistical-report.md:14-22` distingue EQUIVALENTE / DIFERENTE-MAS-IRRELEVANTE / DIFERENTE / INCONCLUSIVO. As 335 comparações somam exatamente: 50 fatores + 23 condições + 81 células + 16 hashtags + 160 perfis + 4 desfechos ajustados + 1 seguidores (`outputs/tables/inf-summary.json`). **Owner: statistician.**

3. **A IA auditada por código, não por impressão** — `process-log/baseline/README.md` + `outputs/tables/g1-baseline-claims-check.csv`. A execução confirma o que o doc afirma: a célula "3,2x" do Gemini tem **n=5 e razão 1,02x** ("teto real 1.02x" na saída de `verify_baseline_claims.py`); a "vantagem nano 51,7%" do Grok é artefato 1/x. Nenhuma outra submissão do repositório mediu o baseline e o desmontou numericamente. **Owner: data-auditor + process-log-keeper.**

4. **Lacuna do dado → falha de processo → dono** — `docs/gap-to-process-map.md:9-20` liga cada DQ a um FP com rótulo **[evidência] / [hipótese]** explícito, e `docs/process/02-pontos-de-falha.md` distingue **[dado] / [operação] / [hipótese]**. Essa disciplina de procedência aparece entre os critérios de "Excepcional" nos reviews públicos. **Owner: process-architect.**

5. **Matriz de IA com threshold de promoção** — `docs/process/04-matriz-ia.md:28-37`: ASSIST vira AUTO só com correção humana < 5% por 8 semanas, sem erro de impacto e com aprovação escrita; volta um nível acima de 10%; lista fechada do que nunca automatizar. É o driver "guardrails com thresholds" entregue de forma mais concreta que em qualquer review aprovado que eu li. **Owner: process-architect.**

6. **RACI que fecha as duas pendências do #91** — `docs/process/05-raci.md:17` (FIN é A/R em "Validar custo e break-even") e `:21` (AM é A/R em "Montar e operar o grupo de comparação"). O avaliador pediu exatamente isso no #91: "mapear owners efetivos para os 3 testes (quem valida break-even, quem opera o grupo de controle)". Um único **A** por linha, seis papéis, sem contratação. **Owner: process-architect.**

7. **Custo implícito paramétrico, ancorado em preço real** — `outputs/tables/str-implied-cost.csv` + `str-market-fees.csv`. Conferido por execução: 0,774 interação extra por post (= IC sup 0,007663 p.p. × 10.099,93 views), R$ 3,87 a R$ 5/interação, fee de micro **129x–775x** o teto, grande **3.876x–25.841x**. Nenhum fee inventado; a conta de break-even (R$ 3.000 ÷ R$ 50 = 60 vendas) fecha. **Owner: marketing-strategist.**

8. **Ferramenta que executa o processo, com health check no ar** — 11 regras, 9 reprovações no próprio arquivo do challenge, confirmado por execução de `src.audit.health.health_check` (`total regras: 11 / reprovadas: 9`), batendo com `README.md:83`. `curl https://decision-social-doug.streamlit.app/healthz` → **HTTP 200, `{"status":"ok"}`, content-type application/json**, exatamente como `app/README.md:30` promete. Isso fecha o outro ponto de melhoria do #91 ("vale considerar status page ou healthcheck visível"). 24 testes passam. **Owner: tool-builder.**

9. **Erros da IA registrados no momento, com o rastro do que era falso** — `process-log/ai-errors.md` tem 19 entradas, incluindo autocorreções desconfortáveis: veredito escrito antes de rodar a conta (`:7`), "154 comparações" corrigido para 335 (`:14`), amplitudes de 5 redes usadas numa estratégia de 3 canais (`:17`), e a linha `:25` em que o próprio Claude Code misturou −0,0011 p.p. com −0,005%. Process log que expõe o erro do autor vale mais que process log que expõe o erro do modelo. **Owner: process-log-keeper.**

10. **Comunicação executiva** — `reports/executive-one-pager.md` cabe em 5 minutos, sem uma sigla estatística, e mantém o número ("menos de 1 interação a mais por post"; "micro cobra R$ 500 a R$ 3.000"). `README.md` segue o template oficial seção por seção (conferido contra `templates/submission-template.md`). **Owner: executive-writer.**

---

## Pontos de melhoria (não bloqueadores)

- **M1 · O esqueleto é o mesmo do #91.** 52.214 posts, método em gates, NO-GO de ML, Streamlit público com n e IC, recomendações priorizadas, "instrumentar antes de otimizar", commits por gate. A diferença é real (ver seção final), mas está **dentro** das camadas, não na silhueta. Um avaliador com pressa lê a silhueta. Vale uma frase no `README.md`, logo após o Executive Summary, dizendo em uma linha o que esta entrega faz que a análise honesta padrão não faz. **Owner: executive-writer.**

- **M2 · Otimizar contra os reviews do avaliador é visível no texto.** Em alguns documentos, a justificativa cita avaliações anteriores em vez do brief. A transparência é correta e eu prefiro assim. Mas convida a pergunta "isto resolve o problema ou resolve o avaliador?". Sugestão: manter a honestidade e reancorar a justificativa no **brief** (que pede comparação justa e recomendações priorizadas), citando o review como confirmação, não como origem. **Owner: executive-writer + process-log-keeper.**

- **M3 · `README.md:13` diz "variância/média entre 0,99 e 1,00"**, mas likes = 1,0030 (`outputs/tables/dq-poisson.csv`, linha `likes,TOTAL`). Arredonda para 1,00 e o relatório de qualidade mostra 1,003 aberto, então não é erro — é uma faixa apertada demais para o próprio dado. "entre 0,99 e 1,00" → "≈ 1,00 nas quatro métricas". **Owner: data-auditor.**

- **M4 · O app carrega 52.214 linhas para computar IC por grupo.** Estatísticas suficientes por célula (n, soma, soma dos quadrados) dariam o mesmo IC com ~2% do peso e tirariam o dado bruto do versionamento (ver C4). Decisão de arquitetura, não de última hora. **Owner: tool-builder.**

- **M5 · `docs/statistical-report.md:17` usa IC 90% para o veredito de equivalência** enquanto todo o resto reporta IC 95%. É a formulação correta do TOST, mas o Head vai tropeçar. Uma nota de uma linha ("TOST a 5% equivale a checar o IC 90%; os ICs das tabelas são 95%") remove a dúvida. **Owner: statistician.**

- **M6 · Nenhuma menção ao time budget** de 4-6 horas do brief contra ~31 horas de calendário entre o primeiro e o último commit (`git log --date=format:'%m-%d %H:%M'`: 09-16 16:18 → 09-17 23:24). Nenhum review aprovado penalizou isso, e o trabalho não é contínuo. Só não force o tema. **Owner: process-log-keeper.**

---

## O que precisa ser corrigido

Ordenado por dano se ficar como está.

**C1 · O process log anuncia três buracos que ele mesmo não fechou.** *(o mais grave)*
- `README.md:170` — checkbox **desmarcado**: "Transcript da sessão de trabalho: `process-log/chat-exports/` _(exportar no G9)_". `ls process-log/chat-exports/` → só `.gitkeep`.
- `process-log/README.md:10` promete `critique/` = "Críticas adversariais multi-modelo + síntese (G8)". `ls process-log/critique/` → só `.gitkeep`. Isso deixa **D10 da própria rubrica sem cumprir** (`docs/differentiation-rubric.md:18` exige "crítica multi-modelo"), e `:3` afirma que "a submissão só vai para PR com todos os itens em ✅".
- `process-log/README.md:16` cita `chat-exports/g0-calibracao-e-plano.md` "(a exportar)"; `:19-21` abre a tabela "Linha do tempo por gate" e preenche **só a linha do G0**.

Por que importa: os 46 prints são todos do **baseline** (as 5 IAs respondendo o brief cru), não da sessão que construiu a solução. A evidência da sessão de trabalho é hoje só narrativa. Formalmente basta (`submission-guide.md:22`, "escolha um ou combine"), e o #72 levou esse mesmo gap como não-bloqueador — mas process log incompleto aparece como motivo de correção nos reviews públicos, e um checkbox desmarcado no README aponta o dedo para o próprio buraco.
Correção: exportar o transcript da sessão para `chat-exports/`, rodar a crítica multi-modelo para `critique/`, completar a tabela G0–G8 e marcar a caixa. Se algo não for entregue, **apagar a promessa** em vez de deixá-la pendente.
**Owner: process-log-keeper.**

**C2 · Placeholder no rodapé do README.** `README.md:192` → `_Submissão enviada em: [data do PR]_`. Colocar a data ou remover a linha. Verificação: `grep -n '\[data do PR\]' README.md`.
**Owner: executive-writer.**

**C3 · Número que não passa na conferência.** `docs/data-quality-report.md:21` afirma que as diferenças entre segmentos são "**≤ 0,012 p.p.**". Conferido no dado:

```
platform                  amplitude p.p. = 0.01051
content_type              amplitude p.p. = 0.01213   ← acima
content_category          amplitude p.p. = 0.00749
is_sponsored              amplitude p.p. = 0.00107
audience_age_distribution amplitude p.p. = 0.01256   ← acima
```

O teto real é **0,0126 p.p.**, não 0,012. O erro é de 0,0006 p.p. e não muda nenhuma conclusão — mas é o **único número da entrega que não vive em CSV nenhum** (`grep -rn "0,012" docs/ reports/ README.md` → uma única ocorrência, sem tabela de suporte) e viola a regra 4 do próprio `CLAUDE.md:10` ("todo número vem de código executado em `src/`. Nada de estimativa no texto"). Corrigir para 0,013 ou emitir a amplitude por segmento numa tabela em `outputs/tables/`.
**Owner: data-auditor.**

**C4 · 52.214 linhas do dataset do challenge estão versionadas.** `app/assets/posts.parquet` (1,4 MB) tem as mesmas 52.214 linhas do CSV bruto, com `views`, `likes`, `shares`, `comments_count`, `platform` e `creator_name` **byte a byte idênticos** ao arquivo do Kaggle:

```
parquet rows 52214 | csv rows 52214
views identico ao CSV bruto: True   likes:  True
shares identico ao CSV bruto: True  comments_count: True
platform: True                      creator_name: True
```

`app/README.md:35` chama de "derivado", mas é uma **projeção de colunas**, não uma agregação. E a entrada da `.gitignore` foi removida de propósito para que ele entrasse (`process-log/ai-errors.md:20`) — decisão documentada, com motivo válido (o app publicado abriria vazio), o que a salva de ser bloqueador. Ainda assim, dataset bruto versionado é motivo de reprovação por higiene nos reviews públicos, e a `.gitignore:1-2` da submissão anuncia "Dados brutos: baixar com `scripts/download_data.py`" enquanto eles estão ali.
Correção (uma das duas): (a) substituir por estatísticas suficientes por célula (M4) e reativar a regra de `.parquet`; ou (b) manter e declarar em uma linha no `app/README.md` **por que** o arquivo é necessário para o deploy, que é um subconjunto de colunas do dataset público MIT, e que os 23 MB brutos seguem fora.
**Owner: tool-builder.**

**C5 · O 303 em loop no acesso sem cookie.** `curl -L https://decision-social-doug.streamlit.app` sem cookie jar → `curl: (47) Maximum (50) redirects followed`, `http_code=303`, 20,7 s. Com cookie jar e UA de navegador → **200 em 2,1 s**. Num navegador real funciona, e `/healthz` responde 200 fora do loop. Mas o avaliador do #91 pediu justamente atenção ao acesso do app, e qualquer checagem automatizada dele vai bater no loop. Correção: apontar no `README.md:21` que a verificação de estado é `/healthz` (já está em `app/README.md:3`, mas não onde o avaliador chega primeiro), e confirmar o app desperto antes de abrir o PR.
**Owner: tool-builder.**

**C6 · A hibernação do Streamlit Community Cloud não foi verificada — e não é verificável por HTTP.** O shell HTML retorna 200 tanto desperto quanto dormindo; o estado real só aparece pelo websocket. No meu teste o app respondeu em 2,1 s, o que indica desperto, mas **não verifiquei o render das 4 abas**. Os prints em `outputs/figures/app/` são de 2026-09-17. Antes do PR: abrir as 4 abas no navegador e, se possível, tirar um print datado do dia do envio.
**Owner: tool-builder.**

---

## Em que esta submissão difere do PR #91 e do #72 — e onde só empata

### Contra o #91 (mesmo challenge, "⭐ Excepcional", 2026-07-22)

**Difere, com evidência:**

| # | Diferença | #91 entregou | Aqui |
|---|---|---|---|
| 1 | **Mecanismo do "sem sinal"** | "diagnóstico de dataset sintético identificado e comunicado" | Gerador provado: Poisson com λ fixo, var/média 0,99–1,00, 76 segmentos em 0,94–1,04, λ variando ≤ 0,29% (`dq-poisson.csv`) |
| 2 | **Equivalência vs ausência de significância** | IC95% reportado; efeito do patrocínio −0,0010 p.p. (IC −0,0095 a +0,0074) | Régua ±1 p.p. **pré-registrada** (`decisions.md:12`), TOST, MDE, BH por família; veredito EQUIVALENTE em 335/335 (`inf-summary.json`) |
| 3 | **Medir a IA crua** | não fez | 5 baselines, 19 afirmações conferidas por código, rubrica escrita antes de construir (`g1-baseline-claims-check.csv`, `differentiation-rubric.md`) |
| 4 | **Arquitetura de processo** | "strategy register com owners/KPIs/stop conditions" | AS-IS → 8 FP → TO-BE em ciclo 15/30 → matriz AUTO/ASSIST/HUMANO com regra de promoção → RACI → contrato de dados → 30/60/90 (`docs/process/01..07`) |
| 5 | **As duas pendências do #91, fechadas** | o avaliador pediu healthcheck visível e owners de break-even/grupo de controle | `/healthz` → 200 `{"status":"ok"}` (verificado por curl); `05-raci.md:17` e `:21` nomeiam FIN e AM |
| 6 | **Falsos positivos como produto** | não aparece | "moda é o pior patrocinador" (IC 95% excluindo zero, `p_bh` = 0,244) e `#religious` desmontados como ruído (`statistical-report.md:47,67`) |
| 7 | **Custo implícito contra preço de mercado** | break-even no dashboard | 0,77 interação/post → R$ 3,87 → fee de micro 129x–775x, grande 3.876x–25.841x, com fontes (`str-market-fees.csv`) |
| 8 | **Reprodutibilidade** | 19 commits auditáveis | checkout limpo regenera **todos** os CSVs byte a byte idênticos |

**Empata (e um avaliador cansado vai ver só isto):** dataset de 52.214 posts; método em gates numerados; NO-GO honesto de ML com R² ≈ 0; app Streamlit público expondo n, IC e limitações; recomendações priorizadas com owner, KPI e stop condition; sequência "congelar → instrumentar → testar → escalar só com evidência incremental"; commits incrementais (16 vs 19); conclusão central idêntica ("o dado não sustenta decisão de verba"); efeito do patrocínio na mesma vizinhança (−0,003 p.p. aqui vs −0,0010 p.p. lá).

**Leitura honesta:** as 8 diferenças são substantivas e verificáveis, mas todas vivem **dentro** de camadas que o #91 já tinha. A única camada genuinamente nova é a arquitetura de processo (#4) — e é ela, não a estatística, que justifica o "Excepcional" aqui. O Executive Summary atual abre pelo achado estatístico, que é o terreno onde a submissão empata. Ver M1.

### Contra o #72 (mesmo challenge, "Excepcional", 2026-06-22)

**Difere:** o #72 foi elogiado por análise em **células de performance** (plataforma × categoria × formato × faixa, ≥30 posts). Aqui as mesmas 81 células existem (`inf-sponsorship-cells.csv`, ≥30 por braço) **mais** correção de múltiplas comparações — e o resultado é que o método do #72 produziria **6 células com p < 0,05 e nenhuma com correção** (`inf-summary.json`: `p_bruto_menor_005: 6`, `p_bh_menor_005: 0`). Ou seja: esta submissão mostra que a abordagem premiada no #72 gera vencedores falsos neste dataset. Além disso o avaliador apontou no #72 "uniformidade suspeita nas medianas (views sempre próximas de 10.100)… pediria um snippet de código para validação independente" — aqui a uniformidade é **o achado**, provada e explicada, com o código e a reprodução byte a byte que ele pediu.

**Empata:** protótipo de ferramenta de decisão; documentação de alucinação da IA como etapa do método (o #72 com 99 prints; aqui 48 + 19 entradas em `ai-errors.md`); honestidade sobre limitações de amostra.

**Onde o #72 ainda ganha:** volume e granularidade de prints da **sessão de trabalho** (99 prints organizados por prompt, com os prompts visíveis). Aqui os 46 prints são todos do baseline, e a sessão que construiu a solução não tem print nem transcript. É o C1.

---

## Veredito operacional

**Aprovar.** Nenhum bloqueador B1–B9. A submissão está acima do #91 em conteúdo verificável e resolve as duas melhorias que o avaliador deixou lá.

Antes de abrir o PR, fechar **C1** (o mais importante: process log que não anuncia o que não tem), **C2**, **C3** e decidir **C4**. C5 e C6 são checagem de 10 minutos no navegador. Feito isso, a submissão fica em 9,5/10 de fato — o meio ponto restante é estrutural (M1/M2) e não se resolve com edição de arquivo.
