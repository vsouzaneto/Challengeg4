# Lead Scorer — Problemática, Plano e Análise Exploratória

> Documento de trabalho (rascunho). Challenge 003 — Vendas / RevOps.
> Data de referência da análise: **31/12/2017** (último `close_date` da base).
> Convenção: tudo que é **fato** vem de cálculo direto na base. O que está marcado com 🔶 **Heurística** é inferência plausível, não comprovada pelos dados.

---

## 1. A problemática

O time comercial tem **35 vendedores**, **6 managers** e **3 escritórios regionais** (Central, East, West), trabalhando um pipeline de **8.800 oportunidades**. A priorização hoje é feita "no feeling".

Nas palavras da Head de Revenue Operations:

> *"Nossos vendedores gastam tempo demais em deals que não vão fechar e deixam oportunidades boas esfriar. Preciso de algo funcional — não um modelo no Jupyter Notebook que ninguém vai usar. Quero uma ferramenta que o vendedor abra, veja o pipeline, e saiba onde focar."*

Dois problemas distintos estão embutidos nessa fala:

1. **Tempo desperdiçado** em deals que não vão fechar → precisa identificar deals mortos/parados.
2. **Oportunidades boas esfriando** → precisa destacar deals com alto valor e ainda "vivos".

---

## 2. O que devemos entregar

### Requisitos do challenge

| Entregável | Requisito |
|---|---|
| **Solução funcional** (obrigatório) | Precisa **rodar**; usar os **dados reais**; ter **lógica de scoring** (não só ordenar por valor); o vendedor precisa entender **por que** o deal tem score alto ou baixo |
| **Documentação** (obrigatório) | Setup (como rodar), Lógica (critérios e porquê), Limitações (o que não faz / o que precisaria pra escalar) |
| **Process log** (obrigatório) | Evidências de como a IA foi usada. **Sem process log = desclassificado** |
| Bônus | Filtro por vendedor / manager / região |

### Critérios de avaliação
- Funciona de verdade? Dá pra rodar seguindo as instruções?
- O scoring faz sentido? Usa as features certas? **Vai além do óbvio?**
- Um vendedor não-técnico consegue usar e entender?
- A interface ajuda a **tomar decisão** ou só mostra dados?
- Código limpo o suficiente para manutenção?
- A entrega precisa **superar substancialmente o baseline** (o G4 já rodou o brief em Claude, GPT e Gemini).

### Regras do PR (verificadas no `CONTRIBUTING.md` e nos PRs existentes)

| Item | Regra |
|---|---|
| Branch | `submission/nome-sobrenome` |
| Pasta | `submissions/nome-sobrenome/` → `README.md` (template), `solution/`, `process-log/`, `docs/` |
| Título do PR | `[Submission] Nome Sobrenome — Challenge 003` |
| Restrição | **Nenhum arquivo fora da pasta** pode ser alterado; 1 PR por pessoa (atualizações = push na mesma branch) |
| Cuidado | Um PR concorrente do Challenge 003 subiu 13.923 arquivos (provável `node_modules`). Usar `.gitignore` na pasta |

### Workflow planejado
`intento-product-design` → estrutura (usuários, tarefas, entidades, jornadas, estados) → implementação → Preview → testes de interação → refinamento. Commits pequenos e frequentes para o git history servir de process log.

---

## 3. Os dados

Fonte: [CRM Sales Predictive Analytics](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics) (CC0).

| Tabela | Registros | Conteúdo |
|---|---|---|
| `sales_pipeline.csv` | 8.800 | Oportunidades: vendedor, produto, conta, stage, `engage_date`, `close_date`, `close_value` |
| `accounts.csv` | 85 | Setor, ano de fundação, receita, funcionários, país, empresa-mãe |
| `products.csv` | 7 | Produto, série, preço de tabela |
| `sales_teams.csv` | 35 | Vendedor, manager, escritório regional |

**Distribuição de stages:** Won 4.238 · Lost 2.473 · Engaging 1.589 · Prospecting 500.

### 3.1 Qualidade dos dados

| Problema | Impacto |
|---|---|
| Produto grafado `GTXPro` no pipeline (catálogo: `GTX Pro`) | Join com `products` quebra se não normalizar |
| Setor `technolgy` (typo) | Setor duplicado se não normalizar |
| **1.425 deals abertos sem conta** (1.088 Engaging = 68% dos Engaging; 337 Prospecting) | Setor, porte e país **inexistentes para a maioria dos deals a pontuar** |
| Prospecting (500) não tem `engage_date` | Idade do deal não calculável |
| 5 vendedores cadastrados sem nenhum deal (Mei-Mei Johns, Carl Lin, Carol Thompson, Natalya Ivanova, Elizabeth Anderson) | 🔶 Heurística: contratações recentes |
| Engajamentos desde out/2016, mas o 1º fechamento é em mar/2017 | Base provavelmente truncada no início (censura) |
| Deals fechados: 0 sem conta; `close_value` = 0 em todo Lost | Consistente |

---

## 4. Análise

### 4.1 Achado central: nenhum atributo estático prevê ganho vs perda

Win rate geral (Won / (Won + Lost)): **63,2%** (n = 6.711).

Teste qui-quadrado de independência entre resultado e cada dimensão:

| Dimensão | Faixa de win rate | p-valor | Leitura |
|---|---|---|---|
| Produto | 60,3% – 64,8% | 0,37 | ruído |
| Setor | 61,2% – 64,8% | 0,97 | ruído |
| Região | 62,6% – 63,9% | 0,60 | ruído |
| Manager | 62,1% – 64,4% | 0,79 | ruído |
| **Vendedor** | 55,0% – 70,4% | 0,26 | ruído |
| **Conta** | 53,1% – 75,0% | 0,94 | ruído |
| País da conta | 56,1% – 75,0% | 0,42 | ruído |
| Receita / funcionários / idade da conta (quartis) | ±3 p.p. | — | ruído |
| Subsidiária vs independente | 63,6% vs 63,1% | — | ruído |

**Provas adicionais de que é ruído:**
- Win rate do vendedor no 1º semestre **não prevê** o do 2º (r = 0,15; p = 0,43). Por conta: r = −0,21.
- O desvio-padrão do win rate entre vendedores (3,7 p.p.) é praticamente o esperado só por acaso com ~200 deals por vendedor.

**Armadilhas descartadas (efeitos espúrios):**

| Efeito aparente (dado bruto) | Controlando pelo mês de fechamento |
|---|---|
| Após perda da conta, WR 57,9%; após ganho, 65,7% | Diferença cai para +2,1 p.p. |
| Após perda do vendedor, WR 58,2%; após ganho, 65,9% | Diferença cai para −0,3 p.p. |
| Vendedor com mais deals abertos simultâneos: WR 65,9% → 59,8% | Diferença some (oscila ±5 p.p. sem direção) |

Os três efeitos eram **calendário** (ganhos e perdas se agrupam em certos meses), não comportamento.

➡️ **Implicação:** usar win rate histórico de vendedor, conta, setor ou produto como peso do score seria dar ao vendedor uma explicação falsa.

### 4.2 O que realmente diferencia deals: **valor**

| Produto | Preço | Ganhos | % ganhos | Receita | % receita | Ticket real | Win rate | Abertos |
|---|---|---|---|---|---|---|---|---|
| GTX Pro | $4.821 | 729 | 17,2% | $3.510.578 | **35,1%** | $4.816 | 63,6% | 333 |
| GTX Plus Pro | $5.482 | 479 | 11,3% | $2.629.651 | 26,3% | $5.490 | 64,3% | 223 |
| MG Advanced | $3.393 | 654 | 15,4% | $2.216.387 | 22,2% | $3.389 | 60,3% | 328 |
| GTX Plus Basic | $1.096 | 653 | 15,4% | $705.275 | 7,0% | $1.080 | 62,1% | 332 |
| GTX Basic | $550 | **915** | **21,6%** | $499.263 | 5,0% | $546 | 63,7% | 430 |
| GTK 500 | $26.768 | 15 | 0,4% | $400.612 | 4,0% | $26.707 | 60,0% | 15 |
| MG Special | $55 | 793 | 18,7% | $43.768 | **0,4%** | $55 | 64,8% | 428 |

- **Mais vendido:** GTX Basic. **Maior receita:** GTX Pro.
- GTX Pro + GTX Plus Pro + MG Advanced = **84% da receita** com 44% dos ganhos.
- MG Special: 2º em volume, último em receita. 15 GTK 500 geraram mais receita que 793 MG Special.
- **Preço de tabela é proxy confiável do valor:** `close_value / sales_price` tem mediana 0,998 (90% entre 0,83 e 1,16). Não há padrão de desconto por vendedor (desvio 0,9 p.p.).

### 4.3 O que realmente diferencia deals: **tempo**

**Ciclo (engage → close) é bimodal:** um bloco fecha em ≤ 14 dias, outro entre 60 e 110 dias.

| | Mediana | P10 | P90 | Máx |
|---|---|---|---|---|
| Won | 57 dias | 5 | 106 | 138 |
| Lost | **14 dias** | 2 | 100 | 138 |

**Quem perde, perde rápido.** Win rate por faixa de ciclo:

| Ciclo | n | Win rate |
|---|---|---|
| 0–7 dias | 1.413 | 53,5% |
| 8–14 | 1.393 | 57,5% |
| 15–30 | 357 | 72,8% |
| 31–60 | 569 | ~66% |
| 61–90 | 1.621 | 66,5% |
| 91–120 | 1.165 | 70,4% |
| 121–150 | 193 | 75,6% |

**Probabilidade condicional de ganho dado que o deal sobreviveu X dias:**

| Sobreviveu > X dias | n | P(ganho) |
|---|---|---|
| 0 | 6.711 | 63,2% |
| 14 | 3.905 | 68,7% |
| 60 | 2.979 | 68,6% |
| 90 | 1.358 | 71,1% |
| 120 | 193 | 75,6% |
| **> 138** | **0** | **nenhum deal fechado jamais passou de 138 dias** |

> ⚠️ **Correção (após revisão externa):** a tabela acima usa **só deals encerrados** e por isso tem viés de seleção — ignora os deals que sobreviveram até a data de referência sem fechar. Refazendo com **riscos competitivos em tempo discreto** (semanas), tratando os abertos como censurados (sem desfecho, não como perda):
>
> | Idade | Em risco | P(ganho em algum momento) | P(ganho em 30 dias) |
> |---|---|---|---|
> | 0 d | 8.300 | 51,9% | 21,8% |
> | 14 d | 5.580 | 50,3% | 7,2% |
> | 30 d | 5.138 | 48,5% | 5,6% |
> | 60 d | 4.681 | 46,8% | 19,4% |
> | 90 d | 3.262 | 38,8% | 28,8% |
> | 120 d | 1.624 | 11,2% | 11,2% |
> | 133 d | 1.358 | 2,1% | 2,1% |
> | ≥ 140 d | 1.273 | **0% — nenhum evento observado após a semana 19** | 0% |
>
> **Conclusão corrigida:** sobreviver **não** aumenta a chance de ganho; ela cai com a idade, e desaba depois de ~90 dias. A chance em 30 dias é bimodal (pico nos deals recém-abertos e em 60–90 dias), refletindo o ciclo bimodal.

### 4.4 Visão mês a mês

| Mês | Novos engajamentos | Won | Lost | Win rate | Receita | Abertos no fim do mês |
|---|---|---|---|---|---|---|
| out/16 | 7 | – | – | – | – | 7 |
| nov/16 | 115 | – | – | – | – | 122 |
| dez/16 | 236 | – | – | – | – | 358 |
| jan/17 | 312 | – | – | – | – | 670 |
| fev/17 | 515 | – | – | – | – | 1.185 |
| mar/17 | 792 | 531 | 116 | **82%** | $1,13M | 1.330 |
| abr/17 | 874 | 285 | 301 | 49% | $0,72M | 1.618 |
| mai/17 | 722 | 438 | 367 | 54% | $1,03M | 1.535 |
| jun/17 | 792 | 531 | 110 | **83%** | $1,34M | 1.686 |
| jul/17 | **1.198** | 308 | 319 | 49% | $0,70M | 2.257 |
| ago/17 | 793 | 446 | 339 | 57% | $1,05M | 2.265 |
| set/17 | 779 | 503 | 132 | **79%** | $1,24M | 2.409 |
| out/17 | 761 | 279 | 287 | 49% | $0,73M | **2.604** |
| nov/17 | **283** | 406 | 362 | 53% | $0,94M | 2.119 |
| dez/17 | **121** | 511 | 140 | **79%** | $1,13M | 1.589 |

**Sazonalidade trimestral (fato):**

| Mês do trimestre (fechamento) | n | Win rate | Ciclo mediano |
|---|---|---|---|
| 1º (jan/abr/jul/out) | 1.779 | **49,0%** | 7 dias — **todos** os fechamentos são de ciclo ≤ 14 dias |
| 2º | 2.358 | 54,7% | 68 dias |
| 3º (fim de trimestre) | 2.574 | **80,7%** | 75 dias |

- Deals **engajados** no 1º mês do trimestre têm WR menor (58,1%) que os do 2º (64,7%) e 3º (67,4%).
- Dia do mês e dia da semana **não** têm efeito.
- 🔶 Heurística: o padrão lembra o "empurrão de fim de quarter", mas pode ser artefato da geração do dataset (que aparenta ser sintético). Não afirmamos causa.

**Geração de pipeline:** cresce até o pico de jul/17 (1.198) e **despenca** em nov/dez (283 → 121).
- 🔶 Heurística: Q1/2018 tende a ser fraco por falta de pipeline novo. Parte da queda pode ser efeito de fim da base.

### 4.5 O pipeline aberto é majoritariamente "zumbi"

1.589 deals em Engaging na data de referência. **Idade mediana: 165 dias** (média 199; máx 423).

| Idade | Deals |
|---|---|
| 0–14 dias | 7 |
| 15–30 | 11 |
| 31–60 | 39 |
| 61–90 | 53 |
| 91–106 | 47 |
| 107–138 | 141 |
| **> 138 (além de qualquer deal já fechado)** | **1.291 (81%)** |

- Só julho/2017 deixou **402 deals** ainda em Engaging.
- Ter ou não conta preenchida não muda a idade (mediana 164–165 dias nos dois grupos).
- 🔶 Heurística: esses deals estão mortos na prática ou sem atualização no CRM. É exatamente o "tempo gasto em deals que não vão fechar".
- **A lista real de foco tem ~300 deals**; o resto é saneamento de pipeline.

Deals Engaging ainda em janela viva (≤ 138 dias), por produto:

| Produto | Vivos | Parados |
|---|---|---|
| GTK 500 | **1** | 14 |
| GTX Basic | 58 | 279 |
| GTX Plus Basic | 55 | 203 |
| GTX Plus Pro | 37 | 139 |
| GTX Pro | 56 | 197 |
| MG Advanced | 29 | 213 |
| MG Special | 62 | 246 |

Os **$401 mil** de GTK 500 "em aberto" são quase todos pipeline parado.

### 4.6 Produtos × especialistas

Especialização medida de duas formas: **concentração de volume** (quanto do produto passa pelo vendedor) e **conversão** (WR no produto vs média do produto, teste binomial).

| Produto | Quem concentra o volume | Converte acima da média? |
|---|---|---|
| **GTK 500** | **100% no West, time Celia Rouche**: Elease Gluck (7 ganhos, $185k), Rosalina Dieter (5, $132k), Markita Hansen (3, $84k). Central e East nunca venderam | n = 25, sem poder estatístico |
| **GTX Pro** | **Darcel Schlecht = 22% dos ganhos** ($773k; 46% da carteira dele). Time **Dustin Brinkmann nunca fechou GTX Pro** | Não — Darcel 60,4% vs 63,6%: especialista em **volume**, não em conversão |
| **MG Advanced** | Hayden Neloms (55% da carteira dele) | **Sim — 76,6% vs 60,3%, p = 0,003.** Único caso forte |
| **MG Special** | Central = 50% dos ganhos; Versie Hillebrand, Anna Snelling, Violet Mclelland (50–67% da carteira) | Não significativo |
| **GTX Plus Pro** | James Ascencio (maior receita no produto, $241k) | Não significativo |
| **GTX Plus Basic** | Maureen Marcano (74,3% vs 62,1%, p = 0,036) | Sinal fraco |
| **GTX Basic** | Distribuído (8 vendedores fazem 50%). Moses Frase 79,7% vs 63,7% (p = 0,01) | Sinal fraco |

- Região × win rate por produto: só **GTX Pro** mostra diferença (Central 58% vs East/West 65–67%, p = 0,025).
- ⚠️ **Múltiplas comparações:** foram **178** testes vendedor × produto. Com correção de Bonferroni para 14 testes (limiar 0,0036), o GTX Pro × região não se sustenta.
- ⚠️ **Correção (após revisão externa):** com correção Benjamini–Hochberg sobre os 178 testes, **Hayden/MG Advanced não se sustenta (q = 0,30)**. O único par com q < 0,10 é Niesha Huffines × GTX Pro (q = 0,039), com **apenas 14 deals** — exemplo de por que o modelo usa encolhimento em vez de teste isolado.
- **Fato:** a concentração de volume (estrutura do time). **Não há evidência** de que "especialista converte melhor".

### 4.7 Padrões operacionais

- **Prospecting só existe na região Central** (Dustin Brinkmann 204, Melvin Marxen 296). East e West não usam o stage.
  - 🔶 Heurística: diferença de processo / uso do CRM entre regiões, não de comportamento do cliente.
- **Darcel Schlecht**: 553 deals fechados, **$1,15M** (2× o segundo colocado), 194 abertos. WR na média (63,1%). Volume, não taxa.
- Receita por deal varia entre vendedores por **mix de produto**, não por conversão (ex.: Versie Hillebrand e Violet Mclelland são majoritariamente MG Special → ~$700/deal).

---

## 5. Proposta inicial de scoring (v0 — substituída pela seção 6)

> Mantida para comparação. Problemas: faixas de idade fixas, 138 dias como constante, tabela de sobrevivência com viés de seleção e afinidade vendedor × produto sem regra de peso definida.

| # | Componente | Base nos dados |
|---|---|---|
| 1 | **Valor esperado** = P(ganho \| stage, idade) × preço de tabela | Valor é o que realmente diferencia (4.2); P(ganho) varia com a idade (4.3) |
| 2 | **Janela de idade**: 0–14d = risco de perda rápida · 15–138d = zona saudável · > 138d = **"Parado — revalidar ou encerrar"** (fora da lista de foco) | 4.3 e 4.5 |
| 3 | **Afinidade vendedor × produto com encolhimento bayesiano** (puxa o WR do par para a média do produto conforme o tamanho da amostra) | 4.6 — evita dar bônus sem amostra; pares com n pequeno ficam neutros |
| 4 | **Especialização como contexto / roteamento**, não como nota. Ex.: "GTK 500 → quem fecha é o time Celia Rouche" | 4.6 |
| 5 | **Contexto de trimestre** exibido, sem peso forte no score | 4.4 |
| 6 | **Flags de higiene** (sem conta, Prospecting sem data) como tarefas, sem penalizar a nota | 3.1 |
| 7 | **Explicação honesta**: "produto, setor e conta não mudam sua chance; o que muda é valor e tempo" | 4.1 |

**Descartado:** modelo de ML (XGBoost etc.). Com variáveis estáticas sem sinal, o modelo aprenderia ruído — e perderia explicabilidade.

---

## 6. Modelo de cálculo v1 (adaptativo)

### 6.1 Princípios
1. **Estrutura fixa, parâmetros aprendidos** a cada leitura da base.
2. **Nenhum nome no código.** Vendedor, produto, conta e região são chaves de agrupamento. Entidade nova herda do nível acima.
3. **Peso de cada dimensão é aprendido.** Sem sinal → peso zero automaticamente; se o sinal surgir, o peso sobe sozinho.
4. **Probabilidade, valor e prioridade** calculados e exibidos separadamente.
5. **Só informação disponível no momento da previsão.** `close_value` e `close_date` só servem como rótulo de treino. Presença de conta fica fora (todo deal fechado tem conta → provável preenchimento no fechamento).

### 6.2 Cálculo

**Entradas por deal:** stage, `engage_date`, produto (→ série, preço), vendedor (→ manager, região). Data de referência `t` = data máxima da base. Idade `a = t − engage_date`.

**Passo 1 — Chance-base pela idade `p_base(a)`** — riscos competitivos em tempo discreto (semanas):
- Todos os deals com `engage_date`. Fechados contribuem com ciclo e desfecho; abertos contribuem até `t` como censurados.
- `h_ganho(k) = ganhos(k) / em_risco(k)`; `h_perda(k) = perdas(k) / em_risco(k)`
- `S(s) = 1`; `S(k+1) = S(k) × [1 − h_ganho(k) − h_perda(k)]`; `p_base(a) = Σ_{k ≥ s} S(k) × h_ganho(k)`
- Peso de recência `2^(−(t − data do evento) / meia-vida)`; meia-vida aprendida (6.3).
- Curva por série de produto quando houver volume, encolhida para a curva global.

**Passo 2 — Ajustes hierárquicos com peso aprendido**

```text
logit(p) = logit(p_base(a)) + Σ w_g · δ_g
```
- Níveis, ajustados em sequência sobre o resíduo dos anteriores (evita contar o mesmo efeito duas vezes): série → produto; região → manager → vendedor; região × produto; vendedor × produto; mês do trimestre de entrada.
- `δ_g` = logit(win rate observado no grupo) − logit(win rate previsto pelo modelo até ali), em deals encerrados, com peso de recência.
- `w_g = n_g / (n_g + k_nível)`; `k_nível` por método dos momentos:
  `τ² = max(0, variância observada − variância binomial esperada)`; `k = p̄(1−p̄)/τ² − 1` (τ² = 0 → k = ∞ → peso 0).

| Nível | k aprendido hoje | Peso num grupo típico |
|---|---|---|
| Produto, série, região, manager, conta | ∞ | 0 |
| Vendedor | 2.004 | 0,10 (n ≈ 220) |
| Região × produto | 1.510 | 0,19 (n ≈ 344) |
| Vendedor × produto | 498 | 0,06 (n ≈ 29) |

**Passo 3 — Valor se ganhar:** `v = preço_tabela × ρ`, com `ρ = close_value / preço` encolhido produto → série → global (hoje 0,985–1,004).

**Passo 4 — Receita esperada:** `R = p × v`.

**Passo 5 — Estado pela idade** (percentil é política; dias são aprendidos, por série quando houver volume):

| Estado | Regra | Dias hoje |
|---|---|---|
| Início | idade < mediana do ciclo das perdas | < 14 |
| Em andamento | ≤ P75 do ciclo dos ganhos | 14–88 |
| **Esfriando** | P75–P95 dos ganhos | 88–116 |
| Tardio | P95–P99 dos ganhos | 116–130 |
| **Fora do histórico** | > P99 dos ganhos | > 130 — `p` não é exibido; fila **Revalidar** |

**Passo 6 — Score 0–100:** percentil de `R` entre os deals abertos com estimativa (empresa inteira), fixo por versão do modelo; não recalcula ao filtrar.

**Passo 7 — Casos especiais**

| Caso | Tratamento |
|---|---|
| Prospecting (sem `engage_date`) | `p = p_base(0) × c`; `c` = conversão Prospecting → Engaging, inexistente na base → `c = 1` com marca "estimativa de entrada" |
| Vendedor / produto / região / combinação nova | `n = 0` → `w = 0` → herda o nível acima; nunca erro nem chance zero |
| Produto sem série conhecida | Curva e `ρ` globais |
| Deal sem conta | Tarefa de cadastro; fora do cálculo |

**Passo 8 — Explicação:** gerada dos componentes usados — valor (preço × ρ); idade e estado; ajustes com impacto ≥ 1 p.p. (os demais: "sem diferença no histórico: usa a média"); tamanho da amostra que sustenta a estimativa.

### 6.3 Ciclo de aprendizado (a cada leitura da base)
1. Normalizar e validar (grafias, integridade, datas impossíveis).
2. Reestimar curvas, `k`, `w`, `δ`, `ρ` e limiares em dias.
3. Selecionar a meia-vida de recência entre {90, 180, 365, ∞} por backtest.
4. Backtest com cortes mensais (usa só o que se sabia em cada corte): versão vigente × candidata × ordenação só por preço. Métricas: Brier, receita capturada no topo da lista, calibração por faixa, desempenho em entidades com pouco histórico.
5. Promover a candidata se for ≥ vigente em Brier **e** receita capturada; senão manter a vigente.
6. Registrar versão: data de corte, parâmetros, métricas e o score exibido por deal.

**Políticas (definidas pelo negócio, não aprendidas):** percentis dos estados, intervalo semanal, candidatos de meia-vida, critérios de promoção, tamanho do "topo da lista".

### 6.4 O que a implementação mostrou (v1.1)

- **O motor TypeScript reproduz a análise em Python**: `p_base(0) = 51,9%`, `p_base(90d) = 38,8%`, última semana com evento = 19, limiares 14/88/116/130 dias (sem recência). Conferido em teste automatizado.
- **Backtest (6 cortes mensais, mar–ago/2017, 16 configurações):**

| | Brier | Receita ganha no top 20% |
|---|---|---|
| Sem modelo (taxa histórica + ordenação por preço) | 0,314 | 46,7% |
| Melhor configuração: recência 90d · curva global · só tempo | 0,231 | 55,6% |
| Mesma, com grupos (produto, região, vendedor…) | 0,231 | 55,2% |

  Os grupos **não melhoraram** a previsão: a regra adaptativa confirmou sozinha o achado da seção 4.1.
- **Calibração adicionada (Platt):** as probabilidades altas saíam otimistas (previsto 78%, observado 47%). Com o calibrador aprendido no backtest, o Brier cai para **0,221** (validação deixando cada mês de fora).
- **Efeito do `c = 1` em Prospecting:** a chance de um deal recém-engajado é o ponto mais alto da curva, então deals de Prospecting de produtos caros aparecem no topo da lista. É consequência direta da premissa otimista; ver a seção 7.

---

## 7. Questões em aberto

- Data de referência: usar 31/12/2017 (fim da base) como "hoje"? → **v1: sim, data máxima da base.**
- Deals parados: → **v1: estado "Fora do histórico", fila Revalidar.**
- Prospecting (sem data): → **v1: `p_base(0) × c`, marcado como estimativa de entrada.** Pendente: definir `c` (hoje 1) enquanto a base não traz a conversão Prospecting → Engaging.
- Especialização: → **v1: capturada pelos níveis vendedor × produto e região × produto com peso aprendido; sem regra por nome.**

---

## 8. Metodologia e reprodutibilidade

- Python 3.14 + pandas 3.0 + scipy.
- Normalizações: `GTXPro → GTX Pro`; `technolgy → technology`.
- Win rate = Won / (Won + Lost). Ciclo = `close_date − engage_date`. Idade = 31/12/2017 − `engage_date`.
- Testes: qui-quadrado de independência (dimensão × resultado); binomial (vendedor × produto vs média do produto); Pearson para persistência entre semestres.
- Controle de confusão temporal: comparações feitas **dentro do mesmo mês de fechamento**.
- Ferramenta: Claude Code (Opus 5.5), com scripts pandas iterativos; cada hipótese foi testada antes de virar afirmação.
