# Avaliação simulada do comitê G4 — Challenge 003 · Lead Scorer

**Avaliador:** `g4-evaluator` (somente leitura) · **Data:** 2026-09-23, 13:00–13:20 · **Escopo:** `submissions/bernardo-couto/` no estado em que estava durante a avaliação (outros agentes ainda editavam `web/` e o `README.md` da submissão; onde o estado mudou entre duas medições, os dois são registrados).

**Como avaliei:** li a rubrica (`.claude/skills/eval-rubric`), o brief oficial, o guia de submissão e o README raiz; rodei `docker compose up -d --build`, `curl` na API (`/api/v1/*`, `/docs`, `/openapi.json`), o container `web` por dentro (porta 5173 do host estava ocupada por um dev server) e `make test` com JDK 21; li `docs/`, `process-log/`, `models/latest`, o código de scoring e os testes; olhei os 7 screenshots.

---

## 1. Portões

| Portão | Resultado | Evidência |
|---|---|---|
| Roda seguindo o README? | **Passa, com ressalva.** Às 13:00 `docker compose up --build` **falhou**: a imagem `web` não compilava (3 erros TS em `web/src/mocks/fixtures.ts:344,363` e `web/src/pages/QueuePage.tsx:269`). Às 13:14 o mesmo build passou (`lead-scorer-web Built`). API e docs subiram nas duas tentativas. | Saída do compose; `curl /api/v1/health` → `{"status":"ok"}`; `curl /api/v1/meta` → `open_deals: 2089`, `model_version: 2017-12-31-rules-v1`; `wget` dentro do container web → `<title>Lead Scorer · Vendas` e proxy `/api/v1/health` OK; MkDocs em `:8001` → 200. |
| Dados reais do dataset? | Passa. | `solution/data/raw/*.csv` com `SHA256SUMS`; `/api/v1/deals` devolve 2.089 deals abertos com `opportunity_id` reais (`059K86LU`, `A04V2WB3`…). |
| Scoring além de ordenar por valor? | Passa. | `scoring/weights.py:23-25` (25/35/40); Spearman(score, preço) = 0,46 no snapshot (`models/…/metrics.json` `spearman_score_price`); tier A tem 5 produtos diferentes (22 GTX Pro, 15 GTX Plus Basic, 11 GTX Plus Pro, 11 GTX Basic, 8 MG Advanced — `curl ?tier=A`). |
| Vendedor entende por quê? | Passa (com lacuna, ver C3). | `reasons[].text_pt` em voz de vendedor com números; `next_action` por deal (`curl /api/v1/deals/059K86LU`). |
| Process log presente? | Passa. | `process-log/{01-narrativa,02-erros-da-ia,decisions}.md`, 1 chat export (1.731 linhas), 7 screenshots. |
| Só arquivos dentro da pasta? | Passa, **mas nada está commitado**. `git status --short` na raiz: limpo; `git ls-files submissions/bernardo-couto` → **0 arquivos**; branch atual `main` (não `submission/bernardo-couto`). O portão não é violado, porém o PR ainda não existe e o "git history com commits pequenos" citado em `process-log/README.md:15` hoje devolve vazio. | `git ls-files`, `git branch --show-current`. |

Nenhum portão reprova. Dois avisos: a volatilidade do build durante a avaliação e a ausência de qualquer commit.

---

## 2. Critérios (0–5)

| # | Critério | Nota | Evidência | O que faltou para 5 |
|---|---|---|---|---|
| C1 | Funciona de verdade? | **4** | Caminho curto sem JDK funciona (ADR 0006; `models/latest` → `2017-12-31-rules-v1`; `gold/scores/as_of=2017-12-31` commitável). `make test` às 13:13: contracts 5/5, pipeline 64/64 (63 s), api 57/57, **web 32/33** (`team.test.tsx:16` esperava `Parado (R$)`, UI já dizia `Parado (R$ tabela)`); às 13:15: web 33/33. Compose com healthcheck, `cap_drop`, `no-new-privileges`. | Estado estável: build da web e suite verdes no mesmo instante; `solution/README.md:70` ainda diz que `train`/`score` "são stubs" (falso — rodam e geraram o modelo); tempo total do `--build` fica perto do limite de 5 min em máquina limpa (uv sync + npm ci + mkdocs). |
| C2 | Scoring faz sentido, vai além do óbvio? | **4** | 11 hipóteses registradas **antes** dos dados, 7 refutadas (`pipeline/analysis/00_hypotheses.md`). Walk-forward em 2 cortes com 5 baselines e IC bootstrap (`model_card.md` §5). Vazamento de `account_known` descoberto e proibido como feature (`data-quality-report.md` "artefato temporal"; teste `FEATURES ∩ FORBIDDEN = ∅`). Zumbi > 138 d como classe: 0/679 fecharam depois. `p_win` reduzido à taxa-base porque nada bate o acaso (AUC-ROC 0,44–0,53) — dito sem eufemismo. LR em sombra com regra de promoção explícita e **não promovida** (`ml-pipeline.md` §4). Grade de pesos mostra que 25/50/25 vira lista de preços (Spearman 0,93; `figures/11_diagnostics.md:11`). | O baseline mais óbvio de todos — **"preço decrescente + esconder parados"** — não está na tabela, e é exatamente o que um avaliador vai perguntar: o `priority_score` perde para "preço" em receita (0,38 vs 0,50) e para o aleatório em AUC; o ganho da urgência é argumentado, não medido. Efeito colateral não discutido: o hazard atinge o pico perto de 138 d, então o top 5 de todo vendedor é composto só por deals com 122–135 dias ("faltam N dias" em 5 de 5 — `curl ?sales_agent=Kami%20Bicknell&queue=work&limit=5`); um GTX Pro com 20 dias nunca chega ao tier A. Pode ser desejado, mas precisa de uma frase e, idealmente, de uma métrica (ex.: receita fechada nos 14 dias seguintes ao corte pelo top N). |
| C3 | Vendedor não-técnico entende? | **4** | Reason codes com número e `n` ("GTX Plus Pro fecha em 64% dos casos (745 deals…)"), `next_action` que pede data, confiança visível, duas filas com dois verbos, lista "o que esta ferramenta não faz" na primeira abertura, sem a palavra "zumbi" na UI (0 ocorrências em `i18n/pt-BR.ts`). Revisão de RevOps corrigiu textos que prometiam previsão (`revops-review.md` §1). | **O drawer explica ~1/3 do score.** Em `059K86LU` (85,9 pts) a seção "Por que este score" lista só `HIGH_TICKET +29,57` e `PRODUCT_BASE_RATE +0,56`; os 40 pontos de urgência e os ~17 de `p_win` não têm linha (não existe reason code de urgência; `DealDrawer.tsx:174-179` só renderiza `reasons.score`). Texto de `HIGH_TICKET` diz "R$ 5.503 esperados se fechar" enquanto a linha mostra "R$ 3.537 esperados" — dois "esperados" diferentes na mesma tela. Nenhuma evidência de teste com um vendedor real. |
| C4 | Interface ajuda a decidir? | **4** | Filas "Trabalhar" / "Confirmar ou encerrar" com cota diária e barra de progresso (`QueuePage.tsx:253-280`); visão Time por manager com "parados fora do forecast" e tabela por vendedor sem coluna de posição; página Qualidade abre dizendo que não acerta mais que o acaso; CSV; seletor as-of (3 partições servidas: `as_of_available`); feedback persistido (`POST /api/v1/feedback` → 201, gravado em `actions.parquet`, `GET` devolve). Filtros região/manager/vendedor. | Feedback **não realimenta** o score (só armazena; `spec §4` deixa para "ciclo futuro"). Os 7 screenshots são em **"Modo demonstração: dados fictícios (MSW)"** com `model_version 2017-12-31-lr-v1`, que não existe — não verificam a UI com dados reais; a UI real só pude verificar por `wget` do HTML. Dois valores para "parado nominal": API `nominal_zombie_value` = R$ 3.198.664 (preço de tabela) vs model card R$ 3.185.048 (preço × razão). |
| C5 | Código limpo o suficiente? | **4** | Monorepo com contrato único (`shared/lead_scorer_contracts`, ADR 0007), regras como funções puras em Spark SQL (`scoring/rules.py`), constantes nomeadas (`weights.py`), API só lê (`routers/deals.py`), UI só apresenta, tipos TS gerados do OpenAPI (`openapi.json` exportado em sync: `cooling_min_days` presente), `uv.lock`/`package-lock.json`, lint configurado, 159 testes Python + 33 Vitest, Dockerfiles endurecidos, `tools/git-stage.sh` com validação. | Zero commits — "outro dev dar manutenção" pressupõe histórico. Suite vermelha em um instante da avaliação (teste desatualizado após mudança de texto). Caches (`.mypy_cache`, `.ruff_cache`, `.pytest_cache`), `web/dist/` e `docs-site/site/` presentes na árvore (ignorados, mas o staging precisa ser verificado no PR). |
| C6 | Documentação: setup, lógica, limitações | **4** | Às 13:00 o `README.md` da submissão era o template com `TODO` em todas as seções; às **13:14 estava preenchido** seção a seção (Executive Summary com números do `_manifest.json`/model card, tabelas de backtest, 7 recomendações com dono, seis erros da IA em tabela, "o que eu adicionei") e `docs/limitations.md` (11,7 kB) existia, consolidando as limitações com fonte por linha. `solution/README.md` com caminho curto/completo verificados; `scoring-logic.md` com números em cada peso; 7 ADRs; MkDocs em `:8001`. | Restam `TODO(Bernardo)` em LinkedIn (`README.md:6`), screenshots (`:50`, `:172`), chat exports das sessões 2+ (`:171`), git history (`:173`) e data de envio (`:181`). `solution/README.md:70` ainda diz que `train`/`score` "são stubs" (falso). A página `limitacoes.md` do site não foi verificada após a criação do arquivo (build da imagem docs foi anterior). README longo (~180 linhas + tabelas) para um comitê que pune "40 páginas onde 5 bastariam" — está denso, não inchado, mas o Executive Summary deveria bastar sozinho. |
| C7 | Process log: iteração e julgamento | **4** | 16 decisões datadas com alternativas descartadas (`decisions.md`); 8 erros da IA com causa-raiz e evidência (`02-erros-da-ia.md`: E7 staging com 45 mil arquivos, E10 premissas derrubadas pelo backtest); hipóteses pré-registradas; objeção técnica registrada (Spark) e decidida pelo humano; hooks versionados e testados (`settings.json`, `guard_leakage.py`). | Evidência de **julgamento do Bernardo** enfraquece a partir da sessão 4: seis decisões dizem "(orquestrador; a confirmar pelo Bernardo)" (`decisions.md` 12:30, 13:40, 13:45, 14:30, 15:20, 15:50, 16:40). Só a sessão 1 tem chat export. Git history vazio. Screenshots de app são mock. Volume alto para 4–6 h declaradas — o comitê vai perguntar quanto tempo de fato foi. |
| C8 | Distância do baseline | **4** | Um avaliador que viu o baseline reconhece: resultado negativo reportado com IC em vez de escondido; `account_known` como leakage temporal; fila de zumbis com R$ 3,19 mi; modelo em sombra com gate de promoção; hook que bloqueia `close_value` em código de scoring; "mais novo primeiro" desmontado (só ganha com censurados = Lost). Nada disso sai de um prompt. | Risco de "parecer inteligente": Spark para 8.800 linhas, 15 agentes, MkDocs, 7 ADRs — a própria IA objetou (E8). Está justificado como decisão de arquitetura, mas o brief pede útil, não completo. A prova que falta é a de valor incremental do score sobre a heurística óbvia (C2). |

**Média simples: 4,0 / 5.** Com commits na branch, screenshots reais e o drawer fechando a conta do score, o piso sobe para ~4,4.

---

## 3. Teste do baseline por componente ("um único prompt com o brief produziria isso?")

| Componente | Baseline? | Comentário |
|---|---|---|
| Achados do dataset (63% win rate, 68% sem conta, GTXPro, 14 vs 57 d, 138 d, snapshot 31/12) | **Sim** | Qualquer EDA cuidadosa chega aqui. A própria submissão já reconhece (E4). |
| Soma ponderada 25/35/40 com tiers A–D e filtros | **Sim** | Forma é baseline. O que não é baseline é *como* os pesos foram escolhidos (grade com Spearman) e *o que foi retirado* (agente, setor, conta → peso zero por refutação). |
| Reason codes + próxima ação + confiança | **Parcialmente** | Formato é o mínimo esperado. A voz ("Isso não muda a ordem da sua fila — no passado não previu o fechamento") e os `n` são julgamento. |
| Backtest temporal com 5 baselines e IC bootstrap; hipóteses antes dos dados | **Não** | Diferencial real. |
| Descoberta de que conta = "já fechou", não "vai fechar" | **Não** | Diferencial real; mudou o modelo. |
| Fila de zumbis com valor nominal e desempate "mais novo primeiro" | **Não** | Diferencial real; vira recomendação executiva com número (win rate cai a 53% se marcar Lost). |
| LR em modo sombra com regra de promoção e PSI | **Não** | Diferencial real, embora o ganho prático hoje seja zero (por desenho). |
| FastAPI + React + Docker + MkDocs + Swagger | **Não é baseline, mas também não é mérito** | Stack não conta; o comitê declara que não avalia ferramenta. Conta o que a stack entrega: OpenAPI completo e as-of na API. |
| Hooks que bloqueiam leakage/relógio/split aleatório | **Não** | Diferencial real de processo — se ficar visível no PR. |
| "Limitações" | **Não** | `docs/limitations.md` é específico, com fonte por linha ("não prevê fechamento", "conta é artefato temporal", "81% parado"); nada de "precisaria de mais dados". |

---

## 4. Indistinguível do baseline

- Os seis achados do dataset listados na calibração da rubrica, quando citados sozinhos.
- A forma "score = soma ponderada + tiers + filtros por vendedor/manager/região + tabela ordenada".
- A página de KPIs da visão Time (tiles de valor esperado, cobertura de conta) — só deixa de ser baseline pela coluna "parado fora do forecast".
- Screenshots em modo mock: um avaliador não consegue distinguir de um protótipo sem dados.

## 5. Diferenciais reais

1. **Resultado negativo publicado com número**: "nenhum critério acerta quem vai fechar melhor que o acaso" (AUC-ROC 0,44–0,53, ICs sobrepostos) e o produto reposicionado por causa disso — em vez de vender "IA que prevê".
2. **`account_known` como vazamento temporal** (100% dos fechados têm conta vs 32% dos abertos) → proibido como feature, com teste que impede regressão.
3. **Zumbis como classe, não como ponto na curva**: 0/679 fecharam depois nos cortes; fila separada; R$ 3,19 mi fora do forecast; alerta de que a limpeza derruba o win rate de 63% para 53%.
4. **"Mais novo primeiro" desmontado**: AUC-ROC 0,50 entre vivos; sobe a 0,73–0,83 só quando censurados = Lost — e a submissão explica por quê.
5. **Grade de pesos com critério objetivo** (Spearman com preço < 0,9) para não virar lista de preços.
6. **Modelo em sombra com gate de promoção** e a observação de que `regParam=0,1` zera todos os coeficientes — a prova mais direta da ausência de sinal.
7. **Revisão de RevOps que vetou textos da própria equipe** ("Prob. de fechar", `QUARTER_END_WINDOW` com percentuais) — 0 ocorrências de "Prob. de fechar" na UI confirmam que a correção foi aplicada.
8. **Guardrails executáveis versionados** (hooks) e erros da IA com causa-raiz (E7, E10).

---

## 6. Inconsistências e riscos específicos encontrados

- `solution/README.md:70`: "`train` e `score` são stubs" — falso; corrigir.
- `process-log/README.md:15` aponta `git log` como evidência; hoje devolve vazio (0 arquivos rastreados, branch `main`).
- Screenshots em `process-log/screenshots/` mostram `Modo demonstração … MSW` e `modelo 2017-12-31-lr-v1` (inexistente; o real é `rules-v1`).
- Dois valores para "parado nominal" (R$ 3.198.664 na API vs R$ 3.185.048 no model card) e dois "esperados" na mesma linha do drawer (R$ 5.503 "se fechar" vs R$ 3.537).
- O drawer não explica os 40 pontos de urgência nem o componente `p_win` — o score mostrado não fecha com a soma das razões exibidas.
- Top N de todo vendedor dominado por deals de 122–135 dias: consequência do hazard; precisa ser dita como escolha ou revista.
- `README.md` da submissão foi preenchido durante a avaliação; restam 6 `TODO(Bernardo)` (LinkedIn, screenshots reais, chat exports 2+, git history, data de envio).
- Suite e build estiveram vermelhos durante a avaliação; o `Stop` hook (`stop_quality_gate.py`) não impediu o estado inconsistente de coexistir na árvore.

---

## 7. Top 3 mudanças de maior alavancagem (em ordem)

| # | Mudança | Esforço | Ganho esperado |
|---|---|---|---|
| 1 | **Fechar o git e as evidências reais.** Criar a branch `submission/bernardo-couto` e commitar em passos pequenos com `tools/git-stage.sh`, validando que `git diff --cached --name-only` não contém `dist/`, `site/`, caches (hoje: 0 arquivos rastreados, branch `main`); trocar os 7 screenshots MSW por capturas contra a API real (`scripts/screenshots.mjs` sem mock; o `model_version` na tela passa a ser `rules-v1`); exportar as sessões 2+; corrigir `solution/README.md:70` ("stubs"); resolver os 6 `TODO(Bernardo)` do README; verificar `mkdocs build --strict` com o novo `limitations.md`. | 1–2 h | C7 4→5, C6 4→5, C5 +0,5; destrava o PR (sem commit a submissão não existe para o comitê). |
| 2 | **Fazer o score fechar na tela.** No drawer, mostrar a decomposição `25·p̂ = X pts · 35·valor = Y pts · 40·urgência = Z pts` (os três números já vêm em `p_win`, `expected_value`, `urgency` do `ScoredDeal`) ou emitir um reason code `CYCLE_WINDOW`/urgência com peso em pontos; unificar "esperados" (um único número por deal: `expected_value`; o bruto entra como "preço de tabela"); alinhar `nominal_zombie_value` da API com o model card (um só estimador, declarado). Adicionar teste de UI: soma das linhas exibidas ≈ score. | 1–2 h | C3 4→5, C4 +0,5. É a exigência literal do brief: "se o vendedor entender POR QUE o deal tem score 85". Hoje ele entende 30. |
| 3 | **Provar o valor incremental do score sobre a heurística óbvia.** Incluir na tabela de backtest e no `metrics.json` o baseline **"preço decrescente excluindo parados (> 138 d)"** e, além de receita no top 20%, uma métrica que a urgência deveria mover: receita fechada nos **14/30 dias seguintes ao corte** pelo top N por vendedor. Se o `priority_score` não bater esse baseline, dizer e simplificar (a honestidade já é a marca da entrega); se bater, o número vai para o README e para a página Qualidade. Documentar a escolha de que o hazard concentra o top N em 120–138 dias. | 2–3 h | C2 4→5, C8 4→5. Transforma "argumentamos que a urgência vale a perda de receita" em "medimos". |

---

## 8. Veredito

Na voz do comitê: **entrega tecnicamente forte e incomumente honesta — descobriu que os dados não preveem fechamento e construiu o produto certo para isso (valor × momento + higiene de R$ 3,19 mi), com README e limitações agora à altura —, mas ainda não existe como submissão (zero commits, branch `main`, screenshots de mock) e o score que o vendedor vê explica só um terço de si mesmo; resolva isso antes do PR e ela passa de "promissora" a "referência".**
