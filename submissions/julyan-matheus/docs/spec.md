# Spec — Lead Scorer (Challenge 003)

Rascunho gerado com IA a partir das hipóteses (H1–H7) e decisões (1–4) documentadas em `docs/`. Revisado por Julyan antes de virar código.

---

## 1. Pra quem e pra quê

Vendedor abre na segunda de manhã e em 30 segundos sabe: quais deals atacar hoje, quais precisam de cadastro antes de qualquer coisa, e quais estão mortos.

Gerente abre e vê: quanto do pipeline de cada vendedor está vivo de verdade.

## 2. Stack

- Next.js + Tailwind, deploy na Vercel
- Sem backend, sem banco, sem API externa, sem chave de API
- Os 4 CSVs ficam em `solution/data/` e são lidos em build time
- Toda lógica de score em `lib/scoring.ts` (funções puras, testáveis)
- Testes com Vitest em `lib/scoring.test.ts`

## 3. Preparação dos dados

- Data de referência = `max(close_date)` do dataset (31/12/2017). **Nunca usar a data de hoje.**
- Normalizar `GTXPro` → `GTX Pro` no pipeline antes de qualquer join
- Joins: pipeline → accounts (por `account`), → products (por `product`), → sales_teams (por `sales_agent`)
- Win rate sempre = Won / (Won + Lost). Deals abertos nunca entram no denominador.
- `close_value` e `close_date` **nunca** entram como fator de deal aberto (leakage)

## 4. Triagem em 4 baldes (Decisão 1)

Aplicada a todo deal em `Prospecting` ou `Engaging`, nesta ordem:

| Balde | Regra | Ação sugerida |
|---|---|---|
| **Limpar** | Engaging e dias aberto > 138 | Fechar como Lost ou reabrir do zero |
| **Requalificar** | Sem `account` (qualquer estágio) | Vincular conta no CRM |
| **Iniciar** | Prospecting com conta (sem `engage_date`) | Fazer primeiro contato |
| **Focar** | Engaging, ≤ 138 dias, com conta | Recebe score |

Dias aberto = data de referência − `engage_date`.

Só o balde **Focar** recebe score. Os outros aparecem na tela com a ação, sem número (Decisão 2).

## 5. Score de chance (0–100) — só balde Focar

Três fatores, pesos da Decisão 3 sem o fator valor, renormalizados:

| Fator | Peso | Como calcular |
|---|---|---|
| Afinidade vendedor × produto | 50% | Ver 5.1 |
| Momentum | 31% | Ver 5.2 |
| Capacidade do vendedor | 19% | Ver 5.3 |

Cada fator vira um número de 0 a 1 (min-max entre os deals do balde Focar). Score = soma ponderada × 100, arredondado.

### 5.1 Afinidade vendedor × produto

Win rate histórico da combinação vendedor + produto, suavizado pra média do vendedor quando há pouco histórico:

```
afinidade = (wins_combo + K × wr_vendedor) / (deals_combo + K), com K = 15
```

Se a combinação não existe no histórico, usa `wr_vendedor`. Se o vendedor não tem histórico, usa o win rate global (63,2%).

### 5.2 Momentum

Chance histórica de ganhar dado que o deal sobreviveu até `d` dias aberto:

```
momentum(d) = win rate dos deals fechados que levaram >= d dias
```

Calculado do histórico. Referência (H5): d=0 → 63%, d≥14 → 69%, d≥90 → 71%, d≥120 → 75%. Se menos de 30 deals no recorte, usa o win rate global.

### 5.3 Capacidade do vendedor

Quantos deals o vendedor tem abertos (Prospecting + Engaging) na data de referência. Quanto menos, maior o fator. Normalizado invertido: `1 − minmax(carga)`.

## 6. Valor esperado (Decisão 4)

Coluna separada, não entra no score:

```
chance = 0,5 × afinidade + 0,3 × momentum + 0,2 × (wr_global + (0,5 − minmax(carga)) × 0,1)
valor_esperado = chance × sales_price do produto
```

Mostrar em dólar, sem casas decimais.

## 7. Explicabilidade — "por quê"

Cada deal do balde Focar mostra 3 linhas, uma por fator, em português simples e com número:

- **Afinidade:** "Você fecha 80% de GTX Plus Pro (18 deals)" / "Você fecha 14% de GTX Pro — abaixo da sua média de 60%"
- **Momentum:** "Aberto há 42 dias — deals que chegam aqui fecham 69%" / "Aberto há 130 dias — perto do limite de 138"
- **Capacidade:** "Você tem 19 deals abertos — abaixo da média (57)" / "Você tem 104 abertos — priorize"

Cada linha marcada como positivo / neutro / alerta (cor).

## 8. Telas

### Tela 1 — Meu pipeline (vendedor)

- Seletor de vendedor no topo (só os 27 com deal aberto)
- Cards no topo: total aberto / Focar / Requalificar / Iniciar / Limpar
- 4 abas, uma por balde, com contagem
- **Aba Focar:** tabela ordenada por score desc. Colunas: deal, conta, produto, dias aberto, score, valor esperado. Clicar expande o "por quê".
- **Aba Requalificar:** tabela ordenada por dias aberto asc (mais recentes primeiro). Colunas: deal, produto, dias aberto, ação "vincular conta".
- **Aba Iniciar:** deal, conta, produto, ação "primeiro contato".
- **Aba Limpar:** deal, conta, produto, dias aberto, ação "fechar ou reabrir".
- **Bloco "Hoje":** os 3 deals do Focar com maior score × valor esperado. É o que o vendedor faz se só tiver tempo pra 3.

### Tela 2 — Visão do gerente

- Seletor de gerente (6)
- Tabela: um vendedor por linha. Colunas: total aberto, Focar, Requalificar, Iniciar, Limpar, % do pipeline vivo, valor esperado total do Focar.
- Linha de total do time
- Destaque em alerta pra vendedor com > 60% em Requalificar ou > 80% em Limpar

### Fora de escopo (v1)

- Login / permissões
- Editar deal ou vincular conta pelo app (só sugere a ação)
- Mobile otimizado (responsivo básico basta)
- Filtro por região

## 9. Testes obrigatórios (`scoring.test.ts`)

- Score sempre entre 0 e 100
- Score é determinístico (mesma entrada → mesma saída)
- Deal sem conta nunca cai em Focar
- Deal > 138 dias nunca cai em Focar
- Mudar `close_value` ou `close_date` de um deal aberto não altera o score
- `GTXPro` e `GTX Pro` produzem a mesma afinidade
- Contagem dos 4 baldes soma 2.089
- Sanity: balde Focar tem 89 deals na data de referência

## 10. Sanity checks a incluir no README

- Distribuição do score no Focar (min / mediana / max)
- 3 exemplos de deal com score e "por quê" completos
- Resultado do backtest (docs/decisoes.md, Decisão 4)
