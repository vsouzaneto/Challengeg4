# Hipóteses registradas antes da análise

**Registrado em:** 2026-09-23 (antes de rodar qualquer script de `analysis/`). **Vereditos acrescentados em:** 2026-09-23, após `01_eda.py`, `10_backtest.py`, `11_diagnostics.py`, `20_model_candidates.py`. Texto original das hipóteses intacto. **Confirmação independente (data-engineer, via gold `opportunity_features`/`labels`):** H3 e H11 — conta presente em ~30% dos Engaging em todo mês de engajamento (0,21–0,54, sem tendência); 100% dos deals com desfecho têm conta vs 32% dos ainda abertos (71% em T=2017-06-30, 58% em 2017-09-30) ⇒ `account_*` **proibido como feature preditiva** (só `confidence`/`reasons`); 1.291/1.589 Engaging > 138 d com picos de `engage_month` em 2017-07 (402) e 2017-08 (173) ⇒ lote nunca atualizado. Nenhuma hipótese nossa é refutada por esses achados; eles endurecem as consequências de H3 (de "peso zero" para "proibido") e de H11 (fila separada com valor nominal: R$ 3,19 mi vs R$ 0,69 mi do pipeline vivo — `11_diagnostics.md` §5).
**Dados:** `solution/data/raw/*.csv`, snapshot `2017-12-31`. Únicas leituras prévias: contagens por estágio, faixa de datas e quantis do ciclo (fatos já listados na skill `crm-dataset`).
**Regra:** o texto original de cada hipótese não é editado depois. Veredito e números são acrescentados na seção "Veredito" de cada uma, com o script que os produziu.

Convenções: IC = intervalo de confiança 95% (Wilson para proporções, bootstrap percentil com 2.000 reamostras para diferenças e métricas de ranking). "pp" = pontos percentuais. Vereditos possíveis: **confirmada**, **refutada**, **inconclusiva**, **confirmada parcialmente**.

---

## H1 — Sobrevivência em Engaging é sinal positivo até ~90 dias e depois vira zumbi

**Predição:** entre deals fechados, `P(Won | ainda aberto após d dias)` sobe de ~63% (d=0) para ≥70% em d∈[30,90] e depois cai; nenhum deal fechou com ciclo >138 dias. Portanto, no snapshot, deals Engaging com idade >138 dias estão fora de qualquer padrão histórico.
**Teste:** curva empírica `won_after_d / (won_after_d + lost_after_d)` por faixa de idade com IC de Wilson; distribuição da idade dos 1.589 Engaging no snapshot.
**Se refutada:** a idade não entra como sinal positivo; só como risco de zumbi.

### Veredito

**Confirmada parcialmente** (`01_eda.py`, tabela H1 em `docs/figures/01_eda.md`, figura `eda_h1_survival.png`). P(Won | aberto após d) sobe de 0,632 [0,620; 0,643] em d=0 para 0,687 em d=14, 0,711 [0,687; 0,735] em d=90 e 0,756 [0,691; 0,812] em d=120; **não cai** depois de 90 (a predição de queda foi refutada). Nenhum deal fechou com ciclo > 138 dias. **Porém**, no backtest (H9) a idade em T não discrimina o desfecho posterior (AUC-ROC de "mais antigo primeiro" = 0,499 e 0,505): a curva agregada existe, mas em um corte fixo T ela é anulada pelo efeito de calendário (fim de trimestre, ver H4). Consequência: `SURVIVAL_POSITIVE` fica **informativo**, sem peso em `p_win`; `ZOMBIE_RISK` (> 138 d) permanece como regra dura.

---

## H2 — Poder discriminativo: agente > produto > setor, todos modestos

**Predição:** o spread (máx − mín) de win rate suavizado (a=20) é maior por agente (~15 pp) que por produto (~5 pp) e por setor (~5 pp). Nenhum fator isolado gera AUC > 0,60 em holdout temporal.
**Teste:** win rate por grupo com Wilson; Cramér's V de cada fator com o desfecho; AUC-ROC de um score univariado (taxa histórica do grupo até T=2017-09-30) nos deals fechados depois de T.
**Se refutada:** reordenar pesos da camada de regras conforme o fator mais forte.

### Veredito

**Confirmada na ordem, refutada na utilidade** (`01_eda.py`, tabela H2). Spread suavizado (a=20): agente 13,9 pp > produto 4,4 pp > setor 3,6 pp; agente×produto 26,2 pp (176 grupos pequenos). Cramér's V: 0,070 / 0,031 / 0,021. **Fora do tempo** (histórico ≤ 2017-09-30 aplicado aos 935 deals abertos em T com desfecho): AUC-ROC produto 0,495, agente 0,493, setor 0,475, agente×produto 0,504 — indistinguível de 0,5. O spread por agente é ruído amostral que não se repete no futuro. Consequência: `AGENT_TRACK_RECORD`, `AGENT_PRODUCT_FIT` e `SECTOR_FIT` entram como reason codes **informativos** (direção `i`, peso 0 em `p_win`) até que um backtest mostre o contrário.

---

## H3 — Conta ausente é artefato de preenchimento tardio, não sinal de qualidade

**Predição:** entre deals fechados, `account` nunca é nulo (0%), então o efeito direto da conta ausente no desfecho **não é estimável**. Entre Engaging, a proporção de `account_known` deve **aumentar com a idade** do deal (conta preenchida ao longo do ciclo). Se não aumentar, a ausência é artefato do dataset e só afeta a confiança, não `p_win`.
**Teste:** taxa de `account_known` por faixa de `days_in_engaging` com Wilson; Spearman idade × account_known.
**Se refutada (taxa constante):** `ACCOUNT_UNKNOWN` fica como redutor de confiança, com contribuição zero em `p_win`.

### Veredito

**Refutada** (`01_eda.py`, tabela H3). `account_known` entre Engaging é plano em relação à idade: 38,9% (0–30 d, n=18), 33,3% (30–60), 20,8% (60–90), 30,9% (90–138), 31,0% (138–200), 31,9% (200–300), 34,5% (300–500); Spearman(idade, account_known) = 0,025. Conta nula entre fechados: 0,0%; entre Prospecting: 32,6% conhecida. A ausência é artefato do dataset (não é preenchimento progressivo). Consequência: `ACCOUNT_UNKNOWN` reduz **confiança** (nunca `alta`), contribuição zero em `p_win`, e a UI pede para completar o CRM.

---

## H4 — Sazonalidade: mês de engajamento tem efeito modesto; mês de fechamento tem efeito de fim de trimestre (não utilizável)

**Predição:** win rate por `engage_month` varia < 10 pp entre meses; win rate por `close_month` mostra picos em mar/jun/set/dez (> 15 pp acima dos meses adjacentes). O segundo é leakage (só se conhece após o desfecho) e **não pode** virar feature; o primeiro pode, se estável entre 2016 e 2017.
**Teste:** win rate por mês de engajamento e por mês de fechamento, com Wilson; comparação entre anos.
**Se refutada (engage_month forte e estável):** incluir sazonalidade de engajamento na camada de regras.

### Veredito

**Refutada como formulada; efeito real é de calendário, não de mês de engajamento** (`01_eda.py` H4; `11_diagnostics.py` seção 2). Spread por `engage_month` = 24,9 pp (dez 80,3%, jan 73,3%, jul 55,4%) — mas dez/2016–fev/2017 são inflados por truncamento à esquerda (`close_date` só começa em 2017-03-01: deals rápidos, majoritariamente Lost, engajados antes de março não existem no dataset) e só há um ano de dados para testar estabilidade (out/2016 n=7). Por mês de fechamento: fim de trimestre 80,7% vs outros 51,9% (spread 34,2 pp); 49,0% dos Won e 20,1% dos Lost fecham em mar/jun/set/dez. Em **todo** corte mensal T, deals abertos em T que fecharam em mês de fim de trimestre ganharam 78–83% vs 50–58% os demais. Isso é conhecido só após o desfecho → **leakage, não é feature**. Consequência: nenhuma feature de sazonalidade; a proximidade do fim de trimestre vira **contexto de urgência** (informativo, sem peso), e é a principal questão aberta para Bernardo/RevOps validar com o negócio.

---

## H5 — Carga do agente: mais deals abertos ao mesmo tempo → menor win rate

**Predição:** para cada corte T, agentes no quartil superior de deals abertos em T têm win rate posterior ≥ 5 pp menor que os do quartil inferior. Correlação de Spearman (carga × win rate posterior) negativa.
**Teste:** carga = nº de deals com `engage_date ≤ T` e (`close_date > T` ou nulo) por agente; win rate dos mesmos deals depois de T; T ∈ {2017-06-30, 2017-09-30}; bootstrap da diferença entre quartis.
**Se refutada:** `AGENT_OVERLOAD` fica como informativo (direção `i`), sem peso em `p_win`.

### Veredito

**Refutada** (`01_eda.py`, tabela H5). Diferença de win rate posterior entre agentes no quartil superior e inferior de carga em T: −4,8 pp [−12,8; +3,6] em 2017-06-30 e +4,7 pp [−4,9; +13,6] em 2017-09-30 — sinais opostos, ambos os ICs contêm zero; Spearman no nível do deal −0,039 / +0,050. Consequência: `AGENT_OVERLOAD` é informativo (direção `i`), acionado quando a carga do agente está no quartil superior; serve ao manager, não ao score.

---

## H6 — Preço × win rate: produtos mais caros fecham menos

**Predição:** win rate decresce com `sales_price`; GTK 500 (26.768) tem o menor win rate (< 60%) e MG Special (55) o maior. Spearman(preço, win rate por produto) < −0,5.
**Teste:** win rate por produto com Wilson; Spearman.
**Se refutada:** `expected_value` domina o ranking sem contrapeso de probabilidade e o risco de "ordenar por valor disfarçado" aumenta — verificar invariante Spearman(score, preço) < 0,9 no backtest.

### Veredito

**Confirmada na direção, irrelevante na magnitude** (`01_eda.py`, tabela H6). Spearman(preço, win rate por produto) = −0,54. MG Special 64,8% [62,1; 67,5] é o maior; GTK 500 60,0% [40,7; 76,6] (n=25!) e MG Advanced 60,3% os menores. Faixa total 60–65%: a probabilidade **não** contrabalança o valor. Confirmado o risco previsto: `Spearman(priority_score, sales_price)` = 0,90–0,93 nos frames de backtest com as regras simplificadas (0,47 no snapshot, porque os zumbis dominam a variância) — ver H9 e a grade de pesos em `11_diagnostics.md`.

---

## H7 — Histórico da conta prevê o futuro da conta

**Predição:** contas com win rate histórico (fechados até T, n ≥ 10) acima da mediana das contas têm win rate posterior ≥ 5 pp maior que as abaixo da mediana.
**Teste:** T=2017-06-30 e 2017-09-30; diferença entre grupos com bootstrap.
**Se refutada:** `ACCOUNT_HISTORY` sai da camada de regras (ou fica como informativo).

### Veredito

**Refutada** (`01_eda.py`, tabela H7). Contas com histórico (n ≥ 10, fechados ≤ T) acima da mediana vs abaixo: −5,6 pp [−11,7; +0,6] em 2017-06-30 e +0,5 pp [−5,7; +7,0] em 2017-09-30; AUC-ROC do histórico da conta 0,475 / 0,489. Consequência: `ACCOUNT_HISTORY` fica informativo ("esta conta fechou X de Y com a gente") sem peso em `p_win`.

---

## H8 — `close_value / sales_price` dos Won é estável e independente de agente

**Predição:** a razão tem mediana ≈ 1,0 e IQR < 0,2 em todos os produtos; a variação entre agentes é < 5%. Logo `expected_value = sales_price × razão_mediana_do_produto × p_win` é uma estimativa honesta e sem leakage.
**Teste:** quantis da razão por produto e por agente (só Won, só para calibrar o multiplicador; nunca usado como feature).
**Se refutada:** o multiplicador precisa de mais dimensões (agente, conta) ou o EV deve vir do preço de lista puro.

### Veredito

**Confirmada** (`01_eda.py`, tabela H8). Mediana da razão `close_value/sales_price` entre Won: 0,967 (GTK 500, n=15) a 1,004 (GTX Plus Pro); IQR 0,127–0,142 em todos os produtos; spread da mediana entre agentes 0,043. Lost: `close_value` = 0 em 100%. Consequência: `expected_value = sales_price × razão_mediana_produto(as_of) × p_win` é estimativa honesta; o multiplicador vem de `compute_history` e nunca do próprio deal.

---

## H9 — "Mais novo primeiro" é um baseline forte que a camada de regras precisa bater

**Predição:** no backtest, ordenar deals abertos em T por idade crescente (mais novo primeiro) atinge AUC-PR maior que a taxa-base por produto e que `sales_price`, porque Lost morre cedo (mediana 14 d). As regras (com curva de sobrevivência) devem bater "mais novo primeiro" em AUC-PR e em receita capturada no top 20%, mas com margem pequena (< 0,05 AUC-PR).
**Teste:** `10_backtest.py`, T ∈ {2017-06-30, 2017-09-30}, bootstrap dos ICs.
**Se refutada (regras não batem):** dizer isso explicitamente e reposicionar a ferramenta: valor está em expected_value, urgência, reason codes e confiança — não no ranking de probabilidade.

### Veredito

**Refutada — e a premissa também** (`10_backtest.py`, `docs/figures/10_backtest.md`; `11_diagnostics.py` seção 3). Entre deals abertos em T **com desfecho realizado** (970 em 2017-06-30, 935 em 2017-09-30), **nenhum** candidato bate o aleatório: AUC-PR aleatório 0,664 [0,621; 0,706] / 0,619 [0,577; 0,666]; taxa-base por produto 0,651 / 0,605; regras p_win 0,621 / 0,605; mais novo primeiro 0,619 / 0,581; mais antigo primeiro 0,616 / 0,579; preço 0,634 / 0,593. AUC-ROC de todos entre 0,47 e 0,53. "Mais novo primeiro" **não é forte entre deals vivos** (AUC-ROC 0,501 / 0,495); só parece forte quando os censurados (ainda abertos no snapshot) são tratados como Lost (AUC-ROC 0,73 / 0,83) — ou seja, o sinal é inteiramente o efeito zumbi, não sobrevivência. O que a ferramenta entrega além do ranking de probabilidade: **receita realizada capturada no top 20%** por `expected_value` 0,508 [0,459; 0,554] / 0,488 [0,441; 0,542] vs aleatório 0,204 / 0,206 (2,4×); demoção dos zumbis (81% do pipeline Engaging no snapshot); urgência por hazard de fechamento; reason codes e confiança; higiene do CRM (68% sem conta). As regras de `p_win` foram **simplificadas** para taxa-base por produto (melhor Brier: 0,235 / 0,243) + penalidade zumbi; ajustes por agente/sobrevivência viram informativos.

---

## H10 — Tamanho da conta (receita, funcionários) tem efeito positivo pequeno

**Predição:** win rate no quartil superior de `revenue` é ≥ 3 pp maior que no inferior; efeito menor que o do agente.
**Teste:** quartis de `revenue` e `employees` entre deals fechados, com Wilson e bootstrap da diferença.
**Se refutada:** `ACCOUNT_SIZE` fica como informativo (direção `i`).

### Veredito

**Refutada** (`01_eda.py`, tabela H10). Receita Q4 − Q1 = −2,1 pp [−5,3; +1,4]; funcionários Q4 − Q1 = −0,9 pp [−4,1; +2,3]; Spearman ≈ −0,006 / −0,003. Consequência: `ACCOUNT_SIZE` informativo (direção `i`), útil como contexto ("conta de US$ 1,1 bi, 2.822 funcionários"), sem peso.

---

## H11 — Idade no snapshot: a maioria do pipeline Engaging já ultrapassou o ciclo máximo histórico

**Predição (derivada do primeiro `describe` das idades, antes de qualquer análise de desfecho):** mais de 50% dos 1.589 Engaging têm `days_in_engaging` > 138 no snapshot. Isso significa que a "urgência" no snapshot é dominada por `ZOMBIE_RISK`, e que o backtest em T=2017-06-30 terá poucos deals abertos-em-T que continuam abertos no snapshot (todos com idade > 184 d, censurados).
**Teste:** distribuição de idade dos Engaging no snapshot; contagem de censurados por corte T.
**Consequência:** a UI precisa separar "pipeline vivo" (≤ 138 d) de "pipeline a confirmar" (> 138 d); o backtest reporta censurados à parte e faz análise de sensibilidade tratando-os como Lost.

### Veredito

**Confirmada com folga** (`01_eda.py`, tabela H11, figura `eda_h11_snapshot_ages.png`). Idade dos 1.589 Engaging no snapshot: mín 9, p25 148, mediana 165, p75 263, máx 423 dias; **1.291 (81,2%) > 138 dias**; apenas 110 (6,9%) ≤ 90 dias. Correção à predição secundária: os censurados têm idade ≥ 184 no **snapshot**, não em T (em T=2017-06-30 há 716 censurados com idade a partir de 0). Nos cortes: 2017-06-30 → 1.686 abertos, 970 com desfecho, 716 censurados, 149 zumbis em T; 2017-09-30 → 2.409 / 935 / 1.474 / 530. **Nenhum** deal que já estava com > 138 d em T fechou depois. Consequência: a UI separa "pipeline vivo" de "a confirmar"; zumbis nunca em tier A; backtest reporta censura e sensibilidade pessimista.
