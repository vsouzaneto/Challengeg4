# Síntese do painel de arquitetura (3 designs + 3 juízes), 2026-09-21

Documento gerado por agentes ANTES da exploração dos dados; serviu de insumo. O que foi adotado ou descartado está em `methodology.md` e no ledger.

# Design final — Lead Scorer 003 "Pauta de Segunda Auditável"

**Status:** design consolidado a partir de 3 designs independentes + 3 juízes, **revisado contra os dados reais já explorados** (`docs/data_health_report.md`, `docs/exploration_results.md`). Onde um número abaixo vem dessa exploração, ele é preliminar: o valor final é o que os scripts numerados gravarem em `docs/artifacts/*.json`.

**Base escolhida:** motor estatístico e anti-leakage do design 1 (rigor), camada de produto e explicação do design 2 (produto-vendedor), andaime de engenharia e rastreabilidade do design 3 (reprodutível). Cortes de escopo seguem o juiz 2 (orçamento).

---

## 0. Sumário executivo (1 parágrafo)

O produto é uma pauta de segunda-feira em Streamlit que classifica cada deal aberto em uma de cinco categorias de ação com regra de entrada e saída, ordena dentro da categoria por valor esperado e explica cada deal em português de vendedor. O score é `100 × P̂(fechar Won nos próximos H dias | deal aberto hoje)`, estimado num painel de segundas-feiras reconstruídas do histórico (nunca em Won/Lost estático), com corte temporal em toda taxa, fatores que só entram se provarem sinal fora da amostra, e um backtest com comparadores (aleatório, preço de lista, só idade, fórmula do baseline). Os dados reais já derrubaram a maior parte dos fatores dos baselines (produto, setor, porte, subsidiária, vendedor, vendedor×produto: todos indistinguíveis de ruído) e revelaram que 81% do pipeline Engaging está além da linha de 138 dias em que nenhum deal, ganho ou perdido, fechou. O produto se sustenta, portanto, em três coisas que os dados sustentam: idade do deal (curva estimada no painel), valor esperado (USD) e achados de processo (deals órfãos sem conta, pipeline inflado, carga por vendedor) — e diz isso na interface em vez de fingir precisão.

---

## 1. Princípio central

1. **Nenhum número sem medida fora da amostra e no tempo certo.** Toda taxa usa só `close_date < as_of`; todo rótulo de validação vem de um snapshot reconstruído em uma segunda-feira passada, medindo o que fechou nos H dias seguintes.
2. **Tudo é função pura de (tabelas, as_of, Config).** `score_pipeline(tables, as_of, config, model)` alimenta a tela, o backtest e os exemplos do README. Não há caminho especial para nenhum deles.
3. **Fator só entra se provar sinal; fator fraco continua visível como "não muda nada aqui".** Regra de inclusão pré-registrada (seção 4.3), medida no conjunto acionável (Engaging com idade ≤ T_max), não no pipeline inteiro.
4. **O produto é a decisão, não o número.** Cinco categorias com regra de entrada/saída, must-acts com orçamento de atenção (≤ 5), bloco "o que não fazer", camada de manager e camada de RevOps.
5. **Honestidade operacionalizada.** Se o limite inferior do IC da AUC nos snapshots de teste for < 0,55, a UI e o README abrem com "o score separa pouco; confie nas categorias por idade e no valor esperado". Fatores testados e descartados aparecem como mérito, com o número.
6. **Rastreabilidade mecânica.** Todo número em docs/README é marcador `{{artefato.chave}}` resolvido por script a partir de JSONs gerados; `test_docs` falha se sobrar marcador ou se o hash do Config divergir do código.

---

## 2. O que os dados reais já mudaram no design

| Achado (fonte: `02_explore.py`, preliminar) | Consequência no design |
|---|---|
| Vendedor: spread 15,4 pp mas χ² p=0,26; vendedor×produto: gap interquartil 8,7 pp **vs. 9,9 pp esperado por ruído binomial** (permutação p=0,886) | D16 decidido com dado: histórico do vendedor **fora do score** e fora da camada de "fit" do manager. O que #86 chamou de "54 pp de fit" é o tamanho do ruído em células pequenas; a UI diz isso. |
| Produto 4,8 pp (p=0,37), setor 3,7 pp (p=0,97), porte p=0,50, subsidiária p=0,74, preço de lista ρ=−0,01 | Entram só como candidatos; expectativa: "testado e descartado". Nenhum peso manual para eles. |
| Ciclo máximo = 138 dias **para Won e para Lost** (0 Lost além do máximo Won) | A "linha dos 138" é regra de encerramento do CRM/dataset, não sinal comercial. Frase da categoria: "nenhum deal, ganho ou perdido, fechou depois de 138 dias" (não "nunca fecha"). T_max = 138 derivado, não hardcoded. |
| 1.291 de 1.589 Engaging (81,2%) têm idade > 138 d na data de referência; mediana 165 d | O pipeline acionável hoje tem ~300 Engaging + 500 Prospecting. "Qualificar ou descartar" será a maior categoria; isso é achado de RevOps ("pipeline inflado em USD X"), não defeito do produto. |
| P(Won \| ciclo ≥ a) entre fechados **sobe** com a idade (63% → 75% aos 120 d); Lost morre cedo (mediana 14 d vs 57 d dos Won) | A curva "entre fechados" (designs 2 e 3) inflaria deals velhos. A curva de momentum **tem de vir do painel de snapshots**: P(Won em H dias \| aberto com idade a), onde zumbis contam 0. |
| 0 fechados sem conta; 68,5% dos Engaging e 67,4% dos Prospecting sem conta | Conta é preenchida no fechamento (ou só deals que progridem ganham conta). **Vazamento novo, não visto por nenhum design:** no painel, `has_account` do dataset final prevê "vai fechar" por construção. Indicador de conta **nunca** entra no modelo; taxa da conta é medida com ressalva (seção 3, F3). Sem conta = flag de RevOps, nunca portão. |
| close_value / sales_price: mediana 0,998 (P10 0,87, P90 1,12); spread entre vendedores 0,043 | Ticket = preço de lista (USD), com a mediana dos Won reportada como conferência. Sem cadeia de fallbacks de desconto. |
| Carga por vendedor × win rate: ρ=−0,45 (p=0,019); abertos por vendedor de 31 a 194 | "Sobrecarga" na camada de manager usa deals **vivos** (idade ≤ T_max), não abertos brutos. Candidato a fator do score, decisão do Marcus (seção 13). |
| Mês de engajamento: spread 11,8 pp na janela limpa (p<1e-6) | Efeito de período: não é fator prospectivo. Vira coluna de drift no backtest e recomendação de investigação para RevOps. |
| close_date só a partir de 2017-03-01 (truncamento à esquerda); 972 deals engajados antes, win rate inflada 72,8% | MIN_HISTORY = 500 fechados antes do primeiro snapshot; a taxa-base do modelo vem do painel (rótulo prospectivo), não do histórico fechado. |
| Top 20% dos deals abertos = 50,1% do valor de lista (417 deals para 50%) | Valor esperado como eixo de ordenação e KPI de cobertura importa; nunca dentro do score. |

---

## 3. Fatores: fórmula, validação, anti-leakage

Notação: `as_of = T`; `hist(T)` = deals com `close_date < T`; `open(T)` = deals com `engage_date ≤ T` e (`close_date` nula ou `> T`), reconstruídos como Engaging mesmo que hoje sejam Won/Lost; `base(T)` = P(Won em H dias) no painel de treino.

### F1 — Momentum por idade, estimado no painel (fator principal)
- **Fórmula.** `age = T − engage_date`. Curva `m̂(b)` = fração de linhas do painel de TREINO no bucket de idade `b` com rótulo Won-em-H. Buckets iniciais `[0–14, 15–30, 31–60, 61–90, 91–120, 121–138, >138]`, vizinhos fundidos até `n ≥ MIN_BUCKET_N = 100`; IC de Wilson por bucket. Feature: `x_mom = logit(m̂(b(age))) − logit(base)`.
- **Limiares derivados.** `T_max` = maior ciclo observado entre fechados (Won **e** Lost, reportados separadamente; esperado 138/138). `T_reeng` = limite inferior do primeiro bucket cujo limite superior do IC de `m̂` fica abaixo de `base`. Se nenhum, `T_reeng = None` e Reengajar fica vazia (sem erro).
- **Validação.** ICs disjuntos em ≥ 2 buckets; AUC univariada de `x_mom` nos snapshots de teste, com IC bootstrap por deal; ΔAUC por ablação; **spread P10–P90 da contribuição em pp medido só entre Engaging com idade ≤ T_max** (conjunto acionável), para provar que o fator não é apenas "morto/vivo".
- **Anti-leakage.** Curva só do painel de treino (rótulos conhecidos em `T_split + H`). Deal sem `engage_date` (Prospecting) não entra no painel. Testes: `close_date`/`close_value` de abertos não alteram `x_mom`; painel nunca contém `engage_date > T` nem `close_date ≤ T`.
- **Frases.** `age < 14`: "deal novo: cedo para cobrar". Bucket com `m̂ ≥ base`: "{k} em 10 deals abertos com essa idade fecharam em {H} dias". Bucket abaixo: "passou da janela em que a maioria fecha ({T_reeng} d)". `age > T_max`: "nenhum deal, ganho ou perdido, fechou com mais de {T_max} dias".

### F0 — Estágio (regra estrutural, não estimada)
- Prospecting não tem `engage_date` nem, em 67%, conta: não pode ser posicionado no tempo nem entrar no painel. **Não recebe P̂ nem score** (recomendação; decisão do Marcus, seção 13). Cai sempre em Requalificar, ordenado por valor de lista. Sem multiplicador arbitrário (0,4/0,6/40).
- Declarado como não validável com este dataset; recomendação de instrumentação para RevOps: registrar data de entrada em Prospecting e histórico de mudança de estágio.

### F2 — Histórico da conta (candidato, com ressalva de vazamento)
- **Fórmula.** Sobre `hist(T)`: `r_global`, `r_setor = (W_s + k·r_global)/(n_s + k)`, `r_conta = (W_c + k·r_setor)/(n_c + k)`. `k` por Bayes empírico (método dos momentos beta-binomial, limitado a [3, 30], fallback 10), valor final fixado em `config.py` com o número que o justificou (resposta a #75). `x_acc = logit(r_conta) − logit(r_global)`; deal sem conta: `x_acc = 0`, `orphan = True`.
- **Ressalva (nova).** Como 100% dos fechados têm conta e 68% dos abertos não, no painel a presença de conta em T é desconhecida para deals que fecharam depois de T. Portanto: (a) `has_account` **nunca** é feature; (b) o poder de `x_acc` é medido na camada A (fechados, todos com conta, sem seleção) e, no painel, só entre deals com conta; (c) `β_acc` é estimado no painel com a ressalva escrita em `methodology.md`; (d) teste H22 (seção 7.1) mede se o % sem conta difere entre Engaging vivos (≤ T_max) e zumbis — se vivos também são órfãos, é prática de preenchimento; se não, "sem conta" marca deal que nunca progrediu.
- **Validação.** Spread P10–P90 de `r_conta` ponderado; AUC univariada na camada A e no painel (entre deals com conta); ΔAuC; cobertura (% dos abertos com conta, esperado ≈ 32%) exibida na UI ("fator disponível para X% do seu pipeline").
- **Anti-leakage.** Denominador Won+Lost; corte `close_date < T`; LOO explícito na camada A; teste: inverter o resultado de um deal fechado depois de T não altera `r_conta` em T.

### F3 — Produto / setor / porte (candidatos; esperado: descartados)
- Mesma fórmula suavizada de F2 (`x_prod`, `x_sector`, `x_size` por tercil de receita). Entram na grade de candidatos; a tabela nominal×efetivo mostra spread, AUC, ΔAUC, estabilidade H1×H2 (Spearman entre taxas de dois semestres, **reportada, não eliminatória**). Se descartados, aparecem no breakdown como "Produto: GTX Pro fecha 64% vs 63% geral — não muda nada aqui" (sem pontos, sem ícone).

### F4 — Carga viva do vendedor (candidato; decisão do Marcus)
- `load_a(T)` = nº de deals do vendedor em `open(T)` com idade ≤ T_max. `x_load = −(load_a − mediana_time)/dp_time` (padronizado, sinal esperado negativo). Conhecido em T (sem leak). Recomendação: **fora do score do vendedor** (penalizaria deals de quem está sobrecarregado, que é problema do manager), **dentro da camada de manager** como bloco "Sobrecarga". Gate mede e registra; o ledger registra a decisão.

### F5 — Valor esperado (eixo separado, nunca peso do score)
- `ticket(produto) = sales_price` (USD); conferência: mediana de `close_value` dos Won do produto em `hist(T)` publicada ao lado (esperado ≈ 1,0×). `EV = P̂ × ticket`. Ordena dentro da categoria, decide empates, alimenta KPI "% do valor coberto pelo top-N". `log(ticket)` entra na grade de candidatos do modelo de P̂ (H5 diz que não discrimina; esperado descartado).
- **Validação.** Captura de valor: % do `close_value` Won-em-H capturado pelo top-20% por EV vs. top-20% por `sales_price` (B1) vs. aleatório, com IC.

### Vendedor e vendedor×produto — testados, fora
- H1/H2b: fora do score e fora da camada de "fit". A tela Metodologia e o README mostram o gap observado vs. o gap nulo. Decisão registrada em `decisions.md` com número; teste `test_agent_history_not_in_score`.

---

## 4. Agregação, calibração, explicação

### 4.1 Modelo
`logit(P̂) = β0 + β_mom·x_mom + Σ_f β_f·x_f` sobre os fatores que sobreviverem ao gate. Regressão logística com L2 fraca, ajustada em `scipy.optimize.minimize` (já pinado; sem scikit-learn) sobre o painel de treino. IC95% dos β por bootstrap em cluster de `opportunity_id` (`N_BOOT = 200`, seed fixa). `β_f = 1` significa "a taxa histórica vale o que diz"; o texto de vendedor nunca usa β.

### 4.2 Score, probabilidade e explicação
- `score = round(100 × P̂)`; exibido junto com "**{k} em 10** deals abertos como este fecharam em {H} dias" (`k = round(10·P̂)`), nunca com casas decimais.
- **Contribuições sequenciais que fecham exatamente** (design 2): `p0 = σ(β0 + β_mom·x_mom)` é a base "idade"; cada fator seguinte, em ordem fixa (conta → produto → ...), soma `pp_f = σ(logit anterior + β_f·x_f) − p anterior`. Assim `p0 + Σ pp_f = P̂` (teste `test_contributions_sum`). Exibido: "Base 5 em 10 (Engaging há 40 d) · Conta +1 · Produto 0 (fraco) · = 6 em 10".
- Três estados por fator (`explain.py`, vocabulário fixo): **forte** (|pp| ≥ 3 e fator ativo), **neutro/fraco** ("não muda nada aqui", com o spread medido), **pouca evidência** (`n < 5` na célula: "tratado como média"). Sem ícone automático.
- **Confiança por deal** (separada do score, como #84): Alta se todos os fatores ativos têm `n ≥ 20` na célula; Média se o principal (idade) tem `n ≥ 100` no bucket mas algum outro tem `n < 20` ou o deal é órfão; Baixa para Prospecting/sem estimativa.

### 4.3 Regra de inclusão pré-registrada (D3)
Fator entra no score se, nos snapshots de teste: `ΔAUC (ablação) ≥ 0,01` **e** IC95% de `β_f` exclui 0 **e** spread P10–P90 da contribuição em pp **no conjunto acionável** ≥ 3 pp. Senão: "testado e descartado" (tabela em `methodology.md`, linha no README, frase neutra na UI). Estabilidade H1×H2 é coluna informativa. Regra escrita **antes** de rodar `03_fit.py`.

### 4.4 Faixas e desempate (D6)
- Cortes `q20/q40/q60/q80` de P̂ no painel de **treino**, congelados em `docs/artifacts/model.json`. A proporção observada por faixa em cada as-of é exibida ("drift de faixa" = sinal de RevOps). Histograma do score na as-of na tela Metodologia.
- Tie-break determinístico e testado com CSV embaralhado: `EV desc → P̂ desc → n_evidência desc → opportunity_id asc`. **Contagem de grupos de empate por categoria publicada** (lacuna apontada pelos juízes).

### 4.5 Calibração
Por decil de P̂ nos snapshots de teste: P̂ média vs. observada, ECE. Se `ECE > 5 pp`, ajuste de Platt só no treino, antes/depois publicados.

---

## 5. Categorias de ação (D9) — semântica de #94, limiares derivados

Precedência de cima para baixo; partição garantida (todo deal aberto em exatamente uma). Sem conta **não** é portão.

| Categoria | Entrada | Saída | Frase / "sai em N dias" |
|---|---|---|---|
| **Requalificar** | Prospecting (sem `engage_date`) | Quando `engage_date` é registrada | "Sem data de engajamento: registre o primeiro contato antes de priorizar. {n} sem conta." Ordenado por valor de lista. |
| **Qualificar ou descartar** | Engaging com `age > T_max` | Só por Won/Lost ou correção de data; valor nunca promove | "Nenhum deal, ganho ou perdido, fechou com mais de {T_max} d. Feche ou traga evidência nova." |
| **Reengajar** | Engaging, `T_reeng < age ≤ T_max` | `age > T_max` → Qualificar; `engage_date` atualizada → volta | "Passou da janela; {T_max − age} dias até a linha." |
| **Focar agora** | Engaging, `age ≤ T_reeng`, `P̂ ≥ q80` | `P̂ < q80 − 2 pp` (histerese, opcional) ou `age > T_reeng` | "{k} em 10 fecham; sai de Focar em {T_reeng − age} dias." Ligar esta semana. |
| **Follow-up** | Demais Engaging com `age ≤ T_reeng` | Sobe se `P̂ ≥ q80`; desce por idade | "Acompanhe; sai da janela quente em {T_reeng − age} dias." |

- Histerese exige a categoria de T−7: o app chama `score_pipeline(T − 7)` (uma chamada extra, cacheada). Está na lista de corte (nível 3).
- Fallback do brief (design 3): se um vendedor tem < 3 deals em Focar, o brief completa com Follow-up **rotulado** ("Focar: 1 · Follow-up sugerido: 2").
- Órfão (sem conta) aparece como badge no deal e como bloco de RevOps; no brief do vendedor vira um must-act de higiene ("vincule a conta destes {n} deals vivos") só se H22 mostrar que vivos também são órfãos.

---

## 6. Data as-of (D7)

- Controle global `st.date_input`, arredondado para a segunda-feira anterior, limitado a `[T_min, ref_date]`, onde `T_min` = primeira segunda com `≥ MIN_HISTORY = 500` fechados e `≥ 200` Engaging abertos (esperado ≈ 2017-04-24) e `ref_date = max(close_date) = 2017-12-31`. Datas antes de `T_min` são bloqueadas com a razão.
- `asof.split_as_of(pipeline, T) -> (history, open)` é a **única** porta de entrada. Taxas, `T_max`, ticket e carga recomputados com corte em T. Curva `m̂`, β e cortes de faixa vêm congelados de `model.json` (ajustados em snapshots `≤ T_split`); para `T < T_split + H` a UI mostra a nota "coeficientes ajustados com rótulos até {T_split + H}; nesta data a simulação usa informação posterior" (leakage declarada, não escondida).
- Prospecting só existe na data mais recente (não tem datas); em datas passadas a UI diz isso e mostra só o Engaging reconstruído. Screenshots em duas datas no README.

---

## 7. Backtest (D5) — executado, com IC

Tudo em `04_backtest.py` → `docs/artifacts/backtest.json` + `docs/backtest.md`. Roda em < 1 min; hash do CSV pontuado gravado.

### 7.1 Camada 0 — auditoria e hipóteses (já feita; completar)
`01_audit.py` e `02_explore.py` existem. Acrescentar: **H22** (% sem conta entre Engaging vivos vs. zumbis), **H23** (valor de lista em USD preso além de T_max), **H24** (idade dos Engaging vivos por vendedor: quem tem pauta e quem não tem), **H25** (`T_max` por coorte de engajamento, para descartar censura). `hypotheses.md` recebe as hipóteses do Marcus com origem definitiva (ver decisão 1).

### 7.2 Camada A — fechados pontuados no tempo certo (valida F2/F3, não valida idade nem estágio)
Rolling O(n) com contadores cumulativos por chave em ordem de `close_date` (design 3): cada deal fechado recebe `x_acc`, `x_prod` etc. calculados só com fechados anteriores (LOO automático), após `MIN_HISTORY`. Tabela de win rate por quintil do sub-score de probabilidade com IC de Wilson, Spearman quintil×WR, lift Q5/Q1. Ressalva escrita: não valida momentum (idade não é observável aqui) nem estágio.

### 7.3 Camada B — painel de segundas-feiras (valida momentum, faixas, categorias, valor)
- **Datas.** Segundas `W-MON` de `T_min` até `max(close_date) − H`. `H = 90` (padrão; decisão do Marcus) → ≈ 25 snapshots; sensibilidade `H = 60` e `H = T_max`.
- **Pipeline em T.** `open(T)`; Prospecting fora (limitação declarada na 1ª linha de `backtest.md`). Rótulo `y = 1` se Won com `close_date ≤ T + H`; Lost, Won depois de T+H ou ainda aberto = 0. Snapshots com `T + H > max(close_date)` excluídos (censura).
- **Split temporal estrito.** Treino = snapshots `T ≤ T_split`; teste = `T ≥ T_split + H` (nenhum rótulo do período de teste entra no treino). `T_split` escolhido para equilibrar nº de snapshots (com H=90: ≈ 7 treino / 7 teste; com H=60: ≈ 11/11). Walk-forward com refit é extensão opcional (nível de corte 2); trajetória dos β publicada se houver.
- **Métricas** por snapshot (média ± dp) e agregadas com IC bootstrap por deal (linhas do mesmo deal são correlacionadas): AUC; lift do quintil superior (`WR_top20 / WR_pipeline`); recall dos Won-em-H no top-20%; precision@5 por vendedor; % do valor Won-em-H capturado pelo top-20% por EV; calibração por decil/ECE; monotonicidade das 5 faixas e das 4 categorias Engaging (Focar > Follow-up > Reengajar > Qualificar em WR observada). **Tudo reportado duas vezes: pipeline inteiro e conjunto acionável (idade ≤ T_max).**
- **Comparadores nas mesmas datas.** B0 aleatório; B1 preço de lista ("ordenar por valor"); B2 só idade (só F1); B3 fórmula do baseline A reproduzida (pesos 70/45); B4 mais recente primeiro (o "momentum" dos baselines). "Supera o baseline" vira número com IC.
- **Poder por fator** (`05_factor_power.py`, mesma origem da tela Metodologia): AUC univariada com IC, ΔAUC por ablação, spread P10–P90 da contribuição no conjunto acionável, β com IC, estabilidade H1×H2, n por célula, status ativo/descartado.
- **Banner de sinal fraco.** IC inferior da AUC no conjunto acionável < 0,55 → banner na UI e frase no README. **Plano B pré-definido** (lacuna apontada pelos juízes): se isso ocorrer, o ranking dentro da categoria passa a ser `idade asc → evidência n desc → EV desc`, documentado como decisão e não como falha.

### 7.4 Camada C — reprodutibilidade
`python 04_backtest.py --h 90` de ponta a ponta; mesmo código roda na fixture nos testes (assert de estrutura); markdown idêntico em duas execuções.

---

## 8. Produto (Streamlit, 3 telas + detalhe, sem LLM, sem chave)

Cabeçalho fixo: as-of (segunda), filtros escritório → manager → vendedor, badge com hash curto do Config efetivo e "dados verificados" (sha256 dos CSVs vs. `data_manifest.json`). Moeda: **USD** em toda parte.

**Tela 1 — Brief de segunda.**
- *Vendedor:* parágrafo de abertura ("Você tem {n} deals abertos. {a} merecem foco esta semana, {b} saem da janela quente até sexta, {c} estão além da linha dos {T_max} dias — decida se ficam."). Must-acts ≤ 5: top-3 Focar por EV com frase-líder do fator dominante e ação; 1 Follow-up mais próximo de sair da janela ("sai em 4 dias"); 1 item de limpeza (contagem e USD dos Qualificar ou descartar). Bloco **"O que não fazer"** ("não gaste a semana nos {c} deals além da linha"). Reengajar listados com dias até a linha.
- *Manager:* **Intervir** (Focar com EV no top-10% do time e ≤ 14 dias de sair da janela); **Sobrecarga** (deals vivos > P90 do time ou > C); **Pipeline morto** (> 50% do Engaging além de T_max); **Sem pauta** (0 Focar). Nada de "fit do vendedor": a UI diz "não há evidência de diferença entre vendedores acima do ruído (H1, H2b)".
- *RevOps (sempre visível ao manager):* órfãos por estágio/região com hipótese de causa (conta não obrigatória no CRM; preenchida no fechamento), USD de lista preso além de T_max, fatores testados e descartados ("não vale enriquecer setor/porte"), variação mensal 55–67% para investigar, drift das faixas vs. treino, linhas antes/depois dos joins.

**Tela 2 — Pipeline.** Tabela dos abertos: categoria, score, "k em 10", confiança, idade, "sai em N dias", EV (USD), vendedor, produto, conta/órfão, fator dominante; ordenação padrão categoria → EV; filtro por categoria; export CSV. Clique → **Detalhe do deal**: barras de contribuição em pp que fecham, frase por fator com estado, fonte do ticket, regra de entrada e de saída da categoria.

**Tela 3 — Método e saúde dos dados.** Renderiza `methodology.md`/`backtest.md` dos artifacts: tabela nominal×efetivo com gates, curva `m̂` com IC, backtest vs. B0–B4, calibração, histograma de score com cortes, contagem de empates, banner de sinal fraco se aplicável, 3 breakdowns fixos (os mesmos do README, gerados por `07_examples.py`).

**README.** Template oficial preenchido; sumário executivo de 1 parágrafo (B5); tabela fator → evidência → coeficiente → status; 3 breakdowns reais (Focar, Reengajar, Qualificar); **Recomendações priorizadas para a Head de RevOps com impacto estimado em USD e premissas declaradas** (B6, seção 14); Limitações; "Como saber se funcionou" (D13, seção 14); papel do Marcus vs. IA com contagem do ledger; tabela de ferramentas; log da validação em venv limpo gerado por `99_clean_env_check.ps1`.

**Deploy.** Streamlit Community Cloud com dados via API Kaggle usando *secrets* do Cloud (credencial manuseada só pelo Marcus, nunca no repo) ou instrução manual; se falhar, a tela Método funciona só com os artifacts e o README traz screenshots + vídeo curto. Não bloqueador.

---

## 9. Layout de módulos (mantém o pacote `leadscorer` já existente)

```
submissions/marcus-barbosa/
  README.md
  .gitignore                          # já existe; data/raw, caches, .pkl fora
  solution/
    requirements.txt                  # pinado; remover plotly (st native charts); sem sklearn
    download_data.py                  # já existe; + data_manifest.json (sha256, linhas)
    01_audit.py  02_explore.py        # já existem; 02 ganha H22–H25
    03_fit.py                         # painel → curva m̂, gates, β com IC, cortes → docs/artifacts/model.json
    04_backtest.py                    # camadas A/B, comparadores B0–B4 → backtest.json + docs/backtest.md
    05_factor_power.py                # tabela nominal×efetivo → factor_power.json
    06_render_docs.py                 # {{artefato.chave}} → docs/methodology.md, backtest.md, README (seções numéricas em arquivo à parte)
    07_examples.py                    # 3 deals fixos por opportunity_id → examples.json
    99_clean_env_check.ps1 / .sh      # venv limpo: pip install, pytest, import app → log em methodology.md
    app.py                            # só UI: cabeçalho + 3 telas + detalhe; st.cache_data por (as_of, config_hash)
    leadscorer/
      data.py      # existe: load_tables, normalize_product, reference_date, enrich
      audit.py     # existe: data_health
      config.py    # @dataclass(frozen) Config: H=90, SNAPSHOT_FREQ="W-MON", MIN_HISTORY=500, MIN_OPEN=200,
                   #   MIN_BUCKET_N=100, AGE_BUCKETS, K_BOUNDS=(3,30), K_FALLBACK=10, GATE(dauc=0.01, spread_pp=3),
                   #   QUANTILES, HYSTERESIS_PP=2, N_BOOT=200, SEED, BRIEF_BUDGET=5, TIE_BREAK; config_hash(); VERSION
      asof.py      # split_as_of(pipeline, T) -> (history, open); monday_before; snapshot_dates(); guards MIN_HISTORY
      rates.py     # smoothed_rate hierárquica com corte temporal; empirical_k; rolling_rates (O(n), LOO) para camada A
      snapshots.py # build_panel(pipeline, dates, H) -> linhas deal×segunda com rótulo, censura, idade
      momentum.py  # age_curve(panel_train) com fusão de buckets e Wilson; t_max(history); t_reeng(curve, base)
      features.py  # x_mom, x_acc, x_prod, x_sector, x_size, x_load, log_ticket para (open, history, model); só hist < T
      model.py     # fit_logistic (scipy), cluster_bootstrap, gates, to_json/from_json (model.json)
      scoring.py   # score_pipeline(tables, T, config, model) -> DataFrame com schema fixo; puro, sem I/O
      categories.py# assign(df, thresholds, prev=None); exit_rule(row) -> "sai em N dias"; RULES exportada p/ docs
      explain.py   # sentence(factor, pp, status, n); headline(row); vocabulário fixo; "k em 10"
      brief.py     # seller_brief, manager_brief, revops_layer -> dataclasses
      validation.py# auc_ci, lift, recall_at, precision_at_k, value_capture, calibration, monotonicity, comparators
    tests/
      conftest.py               # existe; fixture ampliada (~60 oportunidades, datas 2017, casos nomeados)
      fixture/make_fixture.py   # gera os CSVs da fixture deterministicamente (casos: GTXPro, órfão, Prospecting sem data,
                                #   Won depois da as_of, ciclo negativo, engage > as_of, aberto com close_value lixo,
                                #   conta inexistente em accounts, vendedor sem time)
      test_data.py (existe) test_asof.py test_rates.py test_snapshots.py test_momentum.py test_model.py
      test_scoring.py test_categories.py test_explain.py test_brief.py test_validation.py test_leakage.py test_docs.py
  docs/
    design.md (este) marcos.md data_health_report.md exploration_results.md backtest.md methodology.md
    artifacts/ model.json backtest.json factor_power.json examples.json data_manifest.json config_effective.json
    templates/ methodology.md.tmpl backtest.md.tmpl readme_numbers.md.tmpl
    screenshots/ (app em duas as-of, brief, pipeline, detalhe, manager, filtros)
  process-log/
    hypotheses.md decisions.md ai-errors.md workflow.md critique-synthesis.md differentiation-rubric.md
    baselines/ prompts/ screenshots/ (≥10 das sessões) chat-exports/ (Markdown/JSONL)
```

---

## 10. Plano de testes (≥ 30 novos, sem CSV real; 5 já existem em `test_data.py`)

**asof / snapshots / leakage**
1. `history` só tem `close_date < T`; `open` só `engage_date ≤ T` e (`close_date` nula ou `> T`).
2. Deal com `engage_date > T` não aparece em nenhum conjunto.
3. Deal Won com `close_date = T + 10` aparece em `open` como Engaging; seu `deal_stage` original não é lido.
4. Ciclo negativo vai para `history` com flag `bad_dates` e fica fora de `t_max` e da curva.
5. `monday_before` devolve segunda e é idempotente; datas < `T_min` levantam erro nomeado.
6. `build_panel`: nenhuma linha com `engage_date > T`, `close_date ≤ T` ou sem `engage_date`; rótulo Won ≤ T+H → 1, Won > T+H → 0, Lost → 0, aberto → 0; máscara de censura para `T > max_close − H`.
7. **Anti-leakage 1:** alterar `close_value`/`close_date`/`deal_stage` de todos os deals com `close_date ≥ T` (ou abertos) não muda nenhuma coluna de `score_pipeline(T)`.
8. **Anti-leakage 2:** inverter o resultado de um deal fechado depois de T não altera nenhuma taxa em T.
9. **Anti-leakage 3 (LOO):** na camada A, a taxa usada para o deal X não muda ao inverter X.
10. **Anti-leakage 4 (novo):** `has_account` nunca está entre as features do modelo (assert no schema de `features.py`); `x_acc` de órfão é exatamente 0.
11. Split temporal: todo snapshot de teste tem `T ≥ max(T_treino) + H`.

**rates / momentum**
12. Win rate = Won/(Won+Lost); adicionar N abertos não altera `r_global`.
13. Suavização: `n=0 → prior`; `k=0 → taxa crua`; `k→∞ → r_global`; hierarquia conta→setor→global.
14. `empirical_k ∈ [3,30]`; variância zero → fallback 10; valor gravado no `model.json`.
15. Buckets fundidos até `n ≥ MIN_BUCKET_N`; soma dos n = linhas do painel de treino.
16. Wilson: p=0,5, n=100 contém 0,5 e largura ≈ 0,196 ± 0,005.
17. `t_max` = maior ciclo da fixture (Won e Lost reportados); muda quando a fixture muda; `t_reeng ≤ t_max` ou `None` sem erro.

**model / scoring / explain**
18. Logística recupera β conhecidos em dados simulados (tolerância); bootstrap com seed fixa é reprodutível; `IC_inf ≤ β ≤ IC_sup`.
19. Gate: feature de ruído puro → "descartado"; feature perfeitamente informativa → "ativo"; fator descartado nunca aparece em `contributions`.
20. `model.json` round-trip reproduz os mesmos scores; `config_hash` gravado == hash do código.
21. Score ∈ [0,100] inteiro para todo Engaging; Prospecting sem P̂ (NaN) e sem score, categoria Requalificar; nunca NaN em EV.
22. Determinismo: duas chamadas produzem DataFrames idênticos (`assert_frame_equal`) mesmo com CSV embaralhado.
23. `p0 + Σ pp_f == P̂` (1e-9) em todo deal; sequência em ordem fixa.
24. Faixas: cortes iguais aos quantis do painel de treino; proporção por faixa na as-of é reportada, não forçada.
25. Tie-break: EV → P̂ → n → `opportunity_id`; contagem de grupos de empate por categoria devolvida.
26. Confiança: regras Alta/Média/Baixa; órfão nunca Alta; Prospecting Baixa.
27. `explain`: |pp| < 1 → frase neutra sem ícone; `n < 5` → "tratado como média"; texto usa "k em 10", nunca "%,d".
28. `test_agent_history_not_in_score`: embaralhar `sales_agent` não altera nenhum score nem categoria.

**categories / brief**
29. Partição: cada aberto em exatamente uma categoria; união = pipeline.
30. Precedência: Prospecting → Requalificar mesmo com EV alto; `age > T_max` → Qualificar mesmo com P̂ alto; `T_reeng < age ≤ T_max` → Reengajar; `age ≤ T_reeng` e `P̂ ≥ q80` → Focar.
31. `exit_rule`: Focar → `T_reeng − age`; Reengajar → `T_max − age`; texto "sai em N dias".
32. Histerese (se implementada): P̂ = q80 − 1 pp permanece em Focar com `prev=Focar`; q80 − 3 pp sai.
33. `seller_brief` ≤ 5 must-acts, todos do vendedor filtrado; fallback com Follow-up rotulado quando Focar < 3; bloco "não fazer" presente.
34. `manager_brief`: Sobrecarga contém exatamente os agentes com vivos > max(P90, C); Intervir ⊆ Focar; só vendedores do manager.
35. `revops_layer`: contagem de órfãos e USD além de T_max batem com a fixture.

**validation / backtest / docs**
36. AUC de ranking aleatório ∈ [0,4; 0,6]; ranking = rótulo → 1,0; captura de valor top-20% por EV ≥ aleatório na fixture com sinal injetado.
37. Comparadores B0–B4 devolvem métricas com o mesmo schema; monotonicidade das categorias na fixture desenhada para isso.
38. Backtest na fixture roda de ponta a ponta duas vezes com markdown idêntico; snapshot com horizonte além de `max(close_date)` é rejeitado.
39. `test_docs`: nenhum `{{` sobrando em `.md` gerados; todo marcador existe nos artifacts; `config_effective.json` tem `VERSION` e `config_hash` iguais ao pacote.
40. App smoke: importar `app.py` e montar as três telas com a fixture não levanta exceção (sem servidor).

---

## 11. Plano de commits (autor Marcus Barbosa, `git add` com pathspec de exclusão; `pytest -q` verde em cada um)

Já existentes: scaffold + requirements + fixture; data.py + testes; audit → data_health_report; explore (30 hipóteses).

| # | Commit | Conteúdo |
|---|---|---|
| c05 | `feat(asof): corte temporal history/open, calendário de segundas, guarda MIN_HISTORY + testes anti-leakage` | config.py, asof.py, tests |
| c06 | `feat(rates): taxas suavizadas hierárquicas com corte temporal, k por Bayes empírico, rolling LOO` | rates.py, tests |
| c07 | `feat(panel): painel deal×segunda com rótulo Won-em-H e censura; curva de idade com Wilson; T_max/T_reeng` | snapshots.py, momentum.py, tests |
| c08 | `feat(model): deslocamentos de log-odds, logística scipy, bootstrap por cluster, gates pré-registrados, model.json` | features.py, model.py, tests |
| c09 | `feat(score): P̂, score, contribuições que fecham, confiança, EV, categorias com regra de saída, desempate` | scoring.py, categories.py, explain.py, tests |
| c10 | `analysis: 03_fit sobre dados reais — curva, gates, coeficientes; hypotheses.md com H22–H25 e resultados` | 03_fit.py, 05_factor_power.py, artifacts, hypotheses.md, decisions.md |
| c11 | `feat(backtest): camadas A e B, comparadores B0–B4, calibração, IC por deal; docs/backtest.md` | validation.py, 04_backtest.py, backtest.json |
| c12 | `feat(brief): pauta do vendedor, manager (intervir/sobrecarga/morto/sem pauta) e camada RevOps` | brief.py, tests |
| c13 | `feat(app): cabeçalho as-of + filtros, Brief, Pipeline + detalhe, Método` | app.py, smoke test |
| c14 | `docs: render por marcadores a partir dos artifacts; methodology.md; test_docs` | 06_render_docs.py, templates, tests |
| c15 | `docs: README (sumário, lógica, 3 breakdowns, recomendações RevOps, como saber se funcionou, limitações), venv limpo` | README.md, 07_examples.py, 99_clean_env_check |
| c16 | `process-log: ledger, erros da IA, workflow, auditoria adversarial, screenshots, chat-exports` | process-log/* |
| c17 | `chore: deploy Streamlit Cloud, screenshots do app em duas datas` | README (URL), docs/screenshots |

---

## 12. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| **Sinal fraco dentro do conjunto acionável** (fora dele a idade separa zumbis trivialmente; dentro, pode ficar AUC ≈ 0,55) | Métricas sempre em duas versões (inteiro / acionável); banner e plano B pré-definidos (idade → evidência → EV); o produto se sustenta nas categorias e no EV; README abre com o número. |
| **Vazamento da conta no painel** (conta preenchida no fechamento) | `has_account` nunca é feature; `x_acc` avaliado na camada A e entre deals com conta; ressalva escrita; H22 testa a alternativa. |
| **Escopo vs. 6–8 h** | Cronograma por passo (seção 15) com ordem de corte: (1) walk-forward → split fixo; (2) histerese; (3) render de docs → tabela número→script gerada; (4) deploy → screenshots+vídeo; (5) bootstrap 200 → 100. Nunca cortar: corte temporal, testes de leakage, backtest por snapshot executado, brief, 3 breakdowns reais. |
| Linhas do painel correlacionadas (mesmo deal em várias semanas) | Bootstrap por cluster de deal; métricas também por snapshot (média ± dp). |
| Poucos snapshots de teste com H = 90 e split estrito (≈ 7) | Reportar H = 60 como sensibilidade (≈ 11/11); nunca afirmar lift com uma casa decimal sem IC. |
| Truncamento à esquerda (fechamentos só desde 2017-03-01) e efeito de período (mês de engajamento) | MIN_HISTORY; base do modelo vem do painel; calibração por decil no teste; drift reportado. |
| `T_max = 138` pode ser artefato do dataset | H25 por coorte; frase da UI já diz "ganho ou perdido"; categoria continua operacionalmente correta. |
| Prospecting sem score pode ser lido como lacuna | Uma frase na UI e no README; recomendação de instrumentação (data de Prospecting, histórico de estágio) na lista de RevOps. |
| Faixas congeladas + pipeline final 81% zumbi → Focar vazio para alguns vendedores | Fallback rotulado com Follow-up; bloco "Sem pauta" do manager; proporção por faixa exibida como drift. |
| Doc ≠ código (o que reprovou #7) | Marcadores + `test_docs` + hash do Config na UI; nenhum número digitado à mão em docs gerados. |
| Origem das hipóteses marcada como "MB?" | Marcus fixa a origem antes do commit c10; hipóteses de IA ficam como IA (honestidade vale mais que contagem). |
| Streamlit deprecations / venv | Versões pinadas (1.41.1); `99_clean_env_check` com log; sem plotly. |
| Deploy depende de credencial Kaggle | Secrets do Cloud manuseados só pelo Marcus; fallback manual; tela Método funciona só com artifacts. |
| Uso do histórico do vendedor visto como ranking de pessoas | Não usado; a UI diz por quê com o número (gap 8,7 vs 9,9 pp nulo). |
| Avaliação lida primeiro por LLM | README direto, tabelas com mesma origem do app, sem instrução ao avaliador, sem jargão sem tradução (cada termo estatístico tem a frase de vendedor ao lado). |

---

## 13. Mapa rubrica D1–D16 → onde é atendido

| Item | Onde |
|---|---|
| D1 Auditoria etapa 0 | `01_audit.py` → `data_health_report.md` (feito); `data_manifest.json`; conferência de sha256 no app |
| D2 Hipóteses antes dos dados | `hypotheses.md` (origem definitiva pelo Marcus) + `02_explore.py` com H1–H25 e veredito numérico; fatores só de hipóteses sobreviventes |
| D3 Nominal vs. efetivo | `05_factor_power.py` → tabela em `methodology.md` e tela Método: β (IC), ΔAUC, spread no acionável, estabilidade, status; frase neutra na UI |
| D4 Corte temporal / anti-leakage | `asof.split_as_of` única porta; `rates.py` só com history; testes 7–11 |
| D5 Backtest 2 camadas | `04_backtest.py`: camada A rolling LOO, camada B painel semanal com split estrito, comparadores B0–B4, IC por deal |
| D6 Faixas por quantil e desempate | Cortes congelados em `model.json`, histograma e drift na tela Método, tie-break testado, contagem de empates publicada |
| D7 As-of na interface | `st.date_input` com limites derivados; `split_as_of` reexecutado; screenshots em duas datas |
| D8 Brief 3 camadas | `brief.py`: vendedor (≤ 5 must-acts, "não fazer"), manager (4 blocos), RevOps (causa raiz, USD preso, descartados) |
| D9 Cinco categorias com entrada/saída | `categories.py` com `RULES` exportada, `exit_rule` em dias, um teste por transição |
| D10 ≥ 30 testes sem CSV real | 40 testes listados + 5 existentes sobre fixture gerada por script |
| D11 Versões fixas, venv limpo, sem chave, deploy | requirements pinado; `99_clean_env_check` com log; sem LLM; Cloud opcional |
| D12 Process log | ledger com origem e contagem; `ai-errors.md` ≥ 5 (mecanismo: todo teste que falhou por sugestão da IA vira entrada com hash do commit); `critique-synthesis.md`; ≥ 10 screenshots de sessão; chat-exports; ≥ 10 commits; registro de "edição automática desligada" (C9) com captura do `settings.json` |
| D13 Critério de sucesso | Seção "Como saber se funcionou" (seção 14) |
| D14 Metodologia rastreável | Marcadores `{{artefato.chave}}` + link para o script; `test_docs` |
| D15 Explicação honesta | `explain.py` com três estados, "k em 10", contribuições que fecham, 3 breakdowns reais |
| D16 Vendedor decidido com dado | H1/H2b (permutação) em `decisions.md`; `test_agent_history_not_in_score`; UI explica |

---

## 14. Cobertura fora de D1–D16 cobrada pelo avaliador

**B6 — Recomendações priorizadas para a Head de RevOps (lista ordenada, impacto e premissas; números finais dos artifacts):**
1. Decidir os ~1.291 Engaging além de 138 d (USD {{revops.stuck_value}} de lista): limpar ou requalificar. Impacto: pipeline real visível; premissa: 138 d é regra de encerramento.
2. Tornar conta obrigatória no engajamento (68% dos abertos sem conta; 0 fechados sem conta). Impacto: fator conta passa a cobrir 100% do pipeline; premissa: conta é preenchida no fechamento.
3. Instrumentar histórico de mudança de estágio e data de entrada em Prospecting (500 deals sem qualquer data). Impacto: estágio passa a ser validável; premissa: CRM permite.
4. Registrar contatos/atividades por deal para reset de momentum e feedback do vendedor.
5. Rebalancear carga viva (ρ = −0,45 entre abertos e win rate; 31–194 abertos por vendedor). Premissa: correlação, não causa.
6. Não investir em enriquecimento de setor/porte/produto para conversão (refutados com p > 0,3).
7. Investigar a variação mensal de conversão (55–67% por mês de engajamento): campanhas, sazonalidade ou processo.

**D13 — Como saber se funcionou.** Métricas do backtest: lift do quintil superior com IC, % do valor Won-em-H coberto pelo top-20% por EV, ganho vs. "ordenar por valor". Piloto de 8 semanas: vendedores sorteados dentro de cada manager (estratificação; contaminação declarada: deals e contas compartilhados no time), metade com brief. Métricas antecedentes (mensuráveis nas 8 semanas): USD preso além de T_max reduzido em ≥ 20%, órfãos vivos vinculados, taxa de contato dos Focar. Métrica primária lida na semana 21: win rate em 90 d dos deals marcados Focar vs. controle. Gate go/no-go: lift ≥ 1,3× com IC95% excluindo 1. Tamanho de amostra declarado: com ~10 deals vivos por vendedor, +5 pp **não** é detectável em 8 semanas; o piloto mede adoção e antecedentes.

**C9.** `process-log/README.md` já registra edição automática desligada; adicionar captura do `settings.json` e do fluxo de aprovação de cada edição.

---

## 15. Cronograma e ordem de corte

Ver `plano_de_implementacao` (passos de 20–60 min, ≈ 8 h). Checkpoints: h2 (asof+rates+painel+leakage verdes), h4 (score+categorias+backtest rodando nos dados reais), h6 (app 3 telas), h8 (docs+process-log+deploy). Se no checkpoint h4 o backtest não roda, corta-se o app para 2 telas antes de cortar qualquer teste.
