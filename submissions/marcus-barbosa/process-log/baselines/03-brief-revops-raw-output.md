# Baseline 3 — brief-revops — saída bruta (sem edição)

# Lead Scorer — Desenho da Solução (visão de consultor sênior de RevOps)

**Challenge:** 003 — Lead Scorer (Vendas / RevOps) · **Tipo:** Build · **Time budget:** 4–6 h
**Objetivo deste documento:** definir *quais* critérios de priorização usar, *com que pesos*, *por quê*, e *como apresentar* o resultado para um vendedor não-técnico — de modo que o time construa uma ferramenta que rode, use os dados reais, tenha lógica de scoring explicável e ajude a decidir (não só mostre dados).

---

## 1. Reenquadrando o problema

A Head de RevOps foi clara: **não é um modelo, é uma ferramenta de foco**. O vendedor abre na segunda-feira de manhã e precisa responder três perguntas em menos de 30 segundos:

1. **Em quais deals eu devo agir hoje?** (prioridade)
2. **Por que esses e não os outros?** (explicabilidade)
3. **O que exatamente eu faço em cada um?** (próxima ação)

Isso muda o desenho: o score não é um "índice de probabilidade" abstrato. É um **ranking de onde o tempo do vendedor rende mais**. Por isso a fórmula precisa combinar três dimensões independentes:

| Dimensão | Pergunta que responde | Por que entra |
|---|---|---|
| **Probabilidade de ganhar** | Esse deal tende a fechar? | Evita gastar tempo em deals que não vão fechar |
| **Valor esperado** | Quanto vale se fechar? | Prioriza o que move a meta |
| **Urgência / risco de esfriar** | Se eu não agir agora, perco? | Evita deixar oportunidade boa esfriar (a segunda dor citada no brief) |

Score final = **Probabilidade × Valor × Urgência**, normalizado para 0–100, com cada componente exposto ao vendedor.

> Regra de ouro: cada ponto do score precisa ser rastreável a uma frase em português que o vendedor entenda ("conta grande do setor X, produto com alta conversão, parado há 40 dias").

---

## 2. O que os dados permitem (e o que não permitem)

Com as quatro tabelas descritas no brief, dá para derivar:

**Direto do `sales_pipeline.csv`**
- `deal_stage` (Prospecting, Engaging, Won, Lost) → só **Prospecting** e **Engaging** são deals abertos; Won/Lost viram **histórico para calibrar as taxas**.
- `engage_date` → **idade do deal** (dias em pipeline) para deals abertos.
- `close_date` e `close_value` (nos fechados) → **ciclo médio de venda** e **ticket médio** por produto, setor, vendedor.

**Cruzando com `products.csv`**
- Preço de lista do produto → **valor esperado** de um deal aberto (já que `close_value` só existe quando fechou).
- Série do produto → agrupamento para taxas de conversão.

**Cruzando com `accounts.csv`**
- Setor, receita, nº de funcionários → **porte e perfil da conta**.
- Empresa-mãe → sinal de conta estratégica / cross-sell.
- Histórico da conta no pipeline → **já compramos dessa conta antes?** (cliente recorrente tende a converter melhor).

**Cruzando com `sales_teams.csv`**
- Vendedor, manager, escritório → **filtros** (o bônus do brief) e **taxa histórica de conversão do vendedor** (com cuidado — ver §4.3).

**O que NÃO temos** (e é importante deixar explícito nas limitações):
- Nenhum dado de atividade (e-mails, reuniões, ligações) → não dá para medir engajamento real.
- Nenhuma data de "último contato" → a urgência precisa ser inferida pela idade do deal vs. ciclo típico.
- Nenhuma probabilidade fornecida pelo CRM → toda taxa é calculada do histórico Won/Lost.
- Contas sem cadastro (deals com `account` vazio) → tratar com valor neutro, não penalizar cegamente.

---

## 3. Critérios de priorização, pesos e justificativa

A recomendação é um **scoring baseado em regras + taxas históricas** (heurísticas calibradas nos dados), não ML. Motivos: 4–6 h de budget, explicabilidade é critério de avaliação, e o brief diz literalmente que "regras + heurísticas bem apresentadas valem mais que XGBoost sem interface".

### 3.1 Estrutura do score

```
Score (0–100) = 100 × [ P_win_ajustada × Valor_normalizado ]^0.5 × Fator_urgência
```

Ou, de forma mais simples e mais fácil de explicar (recomendo esta para a v1):

```
Score = 0,45 × Probabilidade  +  0,30 × Valor  +  0,25 × Urgência
```

onde cada componente está em 0–100. A forma aditiva é mais fácil de decompor visualmente ("desses 78 pontos, 35 vêm de probabilidade, 24 de valor, 19 de urgência"). A forma multiplicativa é mais "correta" economicamente (valor esperado), mas mais difícil de explicar em uma tela. Para o vendedor, aditiva com pesos claros ganha.

### 3.2 Componente 1 — Probabilidade de fechar (peso 45%)

**Por que 45%:** é a dimensão que mais separa "deal bom" de "deal ruim", e é a única que ataca diretamente a dor nº 1 ("tempo demais em deals que não vão fechar"). Também é a mais rica em sinais derivados dos dados.

Sub-critérios (somam 100 pontos dentro do componente):

| Sub-critério | Pontos | Como calcular | Por quê |
|---|---|---|---|
| **Stage atual** | 30 | Engaging = 30; Prospecting = 10 | Engaging já passou por um filtro; historicamente converte mais. Calibrar com a taxa real Won/(Won+Lost) por stage de origem, se disponível. |
| **Taxa de conversão do produto** | 20 | `Won / (Won + Lost)` por produto, escalado 0–20 | Produtos diferentes têm ciclos e taxas muito diferentes; o dataset tem só 7 produtos, então a estatística é robusta. |
| **Taxa de conversão do setor da conta** | 15 | idem, por `sector` | Setores respondem diferente à oferta. |
| **Histórico da conta** | 15 | Conta já tem deal Won = 15; só Lost = 3; sem histórico = 8 | Cliente que já comprou tem relação e confiança; conta que só perdeu é sinal de alerta. |
| **Taxa de conversão do vendedor no produto** | 10 | Won rate do agente naquele produto, escalado | Cada vendedor tem produtos em que é mais forte. Peso baixo de propósito (ver §4.3). |
| **Porte da conta (fit)** | 10 | Faixas de `revenue`/`employees` com maior win rate histórica recebem mais pontos | "Fit" de ICP: contas de determinado porte convertem melhor para determinados produtos. |

Todos os sub-critérios usam **suavização** (por exemplo, taxa = (Won + k·média) / (Won + Lost + k), com k≈5) para que um produto ou setor com 3 deals não distorça o ranking.

### 3.3 Componente 2 — Valor esperado (peso 30%)

**Por que 30%:** o ranking precisa mover a meta, mas se o valor pesar demais, o vendedor volta a "só ordenar por valor" — que o brief diz explicitamente que não é aceitável. 30% é o ponto em que um deal médio com alta probabilidade ainda supera um deal enorme com probabilidade baixa.

| Sub-critério | Pontos | Como calcular |
|---|---|---|
| **Valor estimado do deal** | 70 | `sales_price` do produto (ou ticket médio histórico Won daquele produto × conta, se houver), normalizado por percentil dentro do pipeline aberto (p90 = 70 pts). Usar **percentil**, não escala linear, para o produto mais caro não dominar. |
| **Potencial da conta** | 30 | Receita da conta em faixas (percentis) → 0–30. Conta grande sugere expansão e upsell futuros. |

### 3.4 Componente 3 — Urgência / risco de esfriar (peso 25%)

**Por que 25%:** é a dimensão que responde à dor nº 2 ("deixam oportunidades boas esfriar") e a que dá **acionabilidade** — transforma o score em "faça agora". Sem ela, a ferramenta é um ranking estático que o vendedor olha uma vez.

A lógica é comparar a **idade do deal** (hoje − `engage_date`) com o **ciclo típico** daquele produto (mediana de `close_date − engage_date` nos deals Won).

| Situação | Pontos | Leitura para o vendedor |
|---|---|---|
| Idade entre 50% e 100% do ciclo típico | 100 | **"Janela de decisão"** — é quando os deals costumam fechar; agir agora tem retorno máximo. |
| Idade entre 100% e 150% do ciclo | 70 | **"Esfriando"** — passou da média, ainda dá pra salvar. |
| Idade < 50% do ciclo | 50 | **"Cedo"** — nutrir, sem pressa. |
| Idade > 150% do ciclo | 20 | **"Provavelmente morto"** — qualificar ou desistir; não gastar tempo. |
| Deal em Prospecting há mais que o ciclo típico inteiro | 10 | Nunca avançou — candidato a limpeza. |

Observação importante: urgência **não é monotônica** com a idade. Um deal muito velho recebe pontuação baixa (não alta), porque a evidência histórica diz que ele não vai fechar. Isso é o que impede a ferramenta de mandar o vendedor correr atrás de "zumbis".

### 3.5 Ajustes e travas (regras de negócio explícitas)

- **Deals fechados** (Won/Lost) ficam fora do ranking, mas aparecem em uma aba de histórico para contexto.
- **Cap de concentração:** se um vendedor tiver 40 deals com score > 80, o ranking ainda mostra top-10 como "foco da semana" — o objetivo é decidir, não listar.
- **Deal sem conta cadastrada:** componentes de conta recebem valor neutro (mediana), com aviso "conta não identificada — cadastre para melhorar o score".
- **Sem penalização por vendedor fraco no score exibido para o próprio vendedor** (ver §4.3).

### 3.6 Como validar que os pesos fazem sentido (backtest de 30 minutos)

Mesmo sendo heurístico, dá para checar:
1. Aplicar o score aos deals **já fechados** (Won/Lost), usando só informação que existiria enquanto estavam abertos.
2. Dividir em quintis de score e medir a **taxa real de Won** em cada quintil.
3. Se o quintil superior converte, por exemplo, 2–3× mais que o inferior, o scoring "funciona". Registrar isso na documentação — é o argumento mais forte para a Head de RevOps.
4. Se algum sub-critério não separar nada (win rate igual em todos os quintis), reduzir o peso ou tirar. Iterar 1–2 vezes; não mais.

Isso também dá a **calibração dos pesos**: os 45/30/25 são um ponto de partida defensável; o backtest é o que os torna justificados.

---

## 4. Decisões de desenho que evitam armadilhas comuns

### 4.1 Não ordenar por valor
O brief proíbe explicitamente. O peso de 30% com normalização por percentil garante que valor influencia sem dominar.

### 4.2 Não usar `close_value` como feature de deals abertos
`close_value` é 0 em Lost e preenchido em Won — é **vazamento**. Para deals abertos, usar preço de lista ou ticket médio histórico do produto.

### 4.3 Cuidado com "taxa do vendedor"
Tecnicamente é um dos sinais mais fortes, mas colocar peso alto cria dois problemas: (a) o próprio vendedor vê seus deals rebaixados por ele mesmo — desmotivador e politicamente ruim; (b) reforça viés (quem vende menos recebe deals piores ranqueados). Solução: peso baixo (10 pts do componente de probabilidade), calculado **por produto**, e exibido como "sua força neste produto", não como penalidade. A visão do **manager** pode ter esse sinal com mais destaque.

### 4.4 Deals velhos não são "urgentes"
Pontuação de urgência é em formato de sino, não crescente. Deals muito atrasados vão para uma lista separada de "revisar / limpar", não para o topo.

### 4.5 Suavização estatística
Setor com 4 deals, conta com 1 deal: sempre usar prior (média global) para evitar rankings absurdos.

### 4.6 Simplicidade acima de precisão
Cada sub-critério tem que caber em uma frase. Se não cabe, sai.

---

## 5. Como apresentar para o vendedor

### 5.1 Princípio: uma tela, uma decisão

A interface responde "o que eu faço hoje?" e só depois permite explorar. Recomendo **Streamlit** (ou HTML+JS estático se quiser zero infra) — sobe em minutos, filtros nativos, roda local com um comando.

### 5.2 Layout recomendado (tela única)

**Topo — barra de filtros (o bônus do brief)**
- Vendedor (default: selecionado na abertura) · Manager · Escritório regional · Produto · Stage
- Toggle "Ver como manager" (agrega o time)

**Faixa 1 — "Seu foco da semana" (cards, 5 a 10 deals)**
Cada card mostra:
- Conta · Produto · Valor estimado
- **Score grande** (ex.: 84) com selo de cor (verde ≥ 70, amarelo 40–69, cinza < 40)
- **Uma linha de "por quê"**, gerada automaticamente a partir dos 2–3 sub-critérios que mais contribuíram:
  > "Conta já cliente · produto com 68% de conversão · na janela de decisão (dia 42 de ~50)"
- **Próxima ação sugerida**, derivada da urgência + stage:
  - Engaging + janela de decisão → "Fechar: propor proposta/negociação esta semana"
  - Engaging + esfriando → "Reativar: ligar hoje, descobrir bloqueio"
  - Prospecting + cedo → "Qualificar: agendar reunião de descoberta"
  - Qualquer + provavelmente morto → "Decidir: requalificar ou marcar como perdido"

**Faixa 2 — "Pipeline completo" (tabela ordenável)**
Colunas: Conta · Produto · Stage · Dias em pipeline · Valor est. · Score · Prob · Valor · Urgência · Motivo resumido.
Clicar em uma linha abre o **detalhe do score** (Faixa 3).

**Faixa 3 — Detalhe do deal (painel lateral ou expander)**
- Decomposição visual do score: três barras (Probabilidade 45%, Valor 30%, Urgência 25%) mostrando quantos pontos vieram de cada uma.
- Lista dos sub-critérios com o valor observado e os pontos atribuídos:
  ```
  Stage: Engaging ............................ +30
  Conversão do produto (GTX Pro: 63%) ........ +17
  Conversão do setor (Technology: 59%) ....... +12
  Histórico da conta: 2 deals ganhos ......... +15
  Sua conversão neste produto: 71% ........... +9
  Porte da conta: médio (fit alto) ........... +8
  ```
- Uma frase de "o que mudaria o score": "Se avançar para negociação esta semana, o deal permanece na janela de decisão; após 15 dias passa a 'esfriando'."

**Faixa 4 — "Para limpar" (colapsada por padrão)**
Deals com urgência ≤ 20 (provavelmente mortos). Ajuda a higienizar o pipeline — RevOps agradece.

### 5.3 Vocabulário na tela (sem jargão)

| Não escrever | Escrever |
|---|---|
| "P(win) suavizado" | "Chance de fechar" |
| "Percentil de valor" | "Tamanho do deal" |
| "Z-score de idade" | "Tempo no pipeline vs. normal" |
| "Feature importance" | "O que mais pesou" |

### 5.4 Visão do manager

Mesma ferramenta, filtro por manager/região: ranking dos deals do time, distribuição de score por vendedor, contagem de deals "esfriando" por vendedor. Nada além disso na v1.

---

## 6. Arquitetura mínima (para caber em 4–6 h)

```
lead-scorer/
├── data/                  # os 4 CSVs do Kaggle
├── scoring.py             # carrega, cruza tabelas, calcula taxas históricas e o score
├── app.py                 # Streamlit: filtros, cards, tabela, detalhe
├── backtest.py            # aplica score ao histórico Won/Lost e imprime win rate por quintil
├── requirements.txt       # pandas, streamlit
└── README.md              # setup, lógica, limitações, process log
```

- `scoring.py` expõe uma função `score_pipeline(df) -> df` com colunas `score`, `p_score`, `v_score`, `u_score`, `reasons` (lista de strings) e `next_action`.
- Pesos e cortes ficam em um dicionário `WEIGHTS` no topo do arquivo — fácil de ajustar sem mexer na lógica.
- Sem banco, sem API, sem autenticação. Roda com `streamlit run app.py`.

**Distribuição sugerida do tempo**
1. 1 h — carregar, cruzar, calcular taxas históricas e ciclos por produto.
2. 1,5 h — função de score + geração de motivos/próxima ação.
3. 1,5 h — interface Streamlit (filtros, cards, tabela, detalhe).
4. 0,5 h — backtest e ajuste de pesos.
5. 0,5–1 h — README (setup, lógica, limitações) e process log.

---

## 7. Documentação obrigatória — o que dizer

**Setup:** `pip install -r requirements.txt` · colocar os CSVs em `data/` · `streamlit run app.py` · abre em `http://localhost:8501`.

**Lógica:** reproduzir a tabela de pesos deste documento, os cortes de urgência e o resultado do backtest (win rate por quintil).

**Limitações (ser honesto — é critério de avaliação):**
- Não há dados de atividade (contato, reuniões); urgência é inferida pela idade do deal.
- Taxas históricas assumem que o passado se repete; mudanças de produto ou mercado exigem recalibração.
- Dataset estático: em produção, precisaria conectar ao CRM (API ou export agendado) e recalcular diariamente.
- Vendedor com pouco histórico recebe taxas suavizadas (menos personalizadas).
- Pesos são heurísticos calibrados por backtest simples, não por modelo estatístico; um próximo passo seria regressão logística com os mesmos sub-critérios como features, mantendo a explicabilidade.
- Sem autenticação nem controle de acesso; para escalar, colocar atrás do SSO da empresa.

---

## 8. Resumo executivo (para apresentar em 2 minutos à Head de RevOps)

1. **O que é:** um ranking diário de deals abertos por vendedor, com score 0–100 e explicação em uma linha.
2. **Como funciona:** 45% chance de fechar (stage, produto, setor, histórico da conta, fit), 30% valor (tamanho do deal e da conta), 25% urgência (idade do deal vs. ciclo típico — deals na janela de decisão sobem, deals mortos descem).
3. **Por que confiar:** no histórico, os deals do quintil superior de score converteram X× mais que os do inferior (preencher com o backtest).
4. **Como o vendedor usa:** abre segunda de manhã, vê 5–10 deals de foco com "por quê" e "próxima ação", filtra por si/manager/região.
5. **O que não faz ainda:** não lê atividade do CRM, não se recalibra sozinho, não tem login. Tudo isso é v2.

O diferencial não é o algoritmo — é que **cada número na tela tem uma frase ao lado dizendo por que ele está ali e o que fazer com ele**.

