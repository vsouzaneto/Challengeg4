# ARRAYFORMULAs e MAP+LAMBDA — Indicadores Calculados

Este documento lista as fórmulas usadas para calcular os 23 indicadores derivados na aba `main` do Google Sheets, agrupadas por bloco.

Todas as fórmulas são coladas na linha 1 (cabeçalho) da coluna correspondente e propagam-se automaticamente para as 8.800 linhas de dados. Assim, a planilha mantém-se leve e reativa a qualquer mudança nos dados originais.

**Contexto crítico:** todas as fórmulas usam `DATA(2017;12;31)` como referência de "hoje" em cálculos temporais, porque o dataset é um snapshot de 2017. Usar `HOJE()` distorceria completamente análises de tempo em pipeline.

---

## Bloco 1 — Indicadores Descritivos

### days_since_engage
Dias desde o engajamento, apenas para deals abertos.

```
=ARRAYFORMULA(SE(LIN(A:A)=1;"days_since_engage";SE((A:A="");"";SE((B:B="Won")+(B:B="Lost")+(C:C="");"";DATA(2017;12;31)-C:C))))
```

### engage_month
Ano e mês do engajamento no formato AAAA-MM.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "engage_month"; SE((A:A=""); ""; SE(C:C=""; ""; TEXTO(C:C; "yyyy-mm")))))
```

### engage_quarter
Ano e trimestre do engajamento no formato AAAA-Qx.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "engage_quarter"; SE((A:A=""); ""; SE(C:C=""; ""; ANO(C:C) & "-Q" & ARREDONDAR.PARA.CIMA(MÊS(C:C)/3; 0)))))
```

### account_size_tier
Categoriza clientes por porte (funcionários) em quartis Q1-Q4.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "account_size_tier"; SE((A:A=""); ""; SE((P:P="")+(P:P="-"); "sem dados"; SE(P:P<1238; "Q1 (Pequena)"; SE(P:P<3492; "Q2 (Média-Baixa)"; SE(P:P<7523; "Q3 (Média-Alta)"; "Q4 (Gigante)")))))))
```

### revenue_tier
Categoriza clientes por receita em quartis Q1-Q4.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "revenue_tier"; SE((A:A=""); ""; SE((O:O="")+(O:O="-"); "sem dados"; SE(O:O<527; "Q1 (Baixa)"; SE(O:O<1420; "Q2 (Média-Baixa)"; SE(O:O<2953; "Q3 (Média-Alta)"; "Q4 (Alta)")))))))
```

### product_tier
Agrupa produtos em faixas de preço (entry, mid, premium, ultra-premium).

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "product_tier"; SE((A:A=""); ""; SE((I:I="GTX Basic")+(I:I="MG Special"); "entry"; SE((I:I="GTX Plus Basic")+(I:I="MG Advanced"); "mid"; SE((I:I="GTXPro")+(I:I="GTX Plus Pro"); "premium"; SE(I:I="GTK 500"; "ultra-premium"; "outros")))))))
```

### is_international
Sinaliza se o cliente é internacional (fora dos EUA).

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "is_international"; SE((A:A=""); ""; SE((Q:Q="")+(Q:Q="-"); ""; SE(Q:Q<>"United States"; "sim"; "não")))))
```

### is_subsidiary
Sinaliza se o cliente é subsidiária de um grupo maior.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "is_subsidiary"; SE((A:A=""); ""; SE((R:R="")+(R:R="-"); "não"; "sim"))))
```

### company_age
Idade da empresa cliente em anos (referência 2017).

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "company_age"; SE((A:A=""); ""; SE((N:N="")+(N:N="-"); ""; 2017 - N:N))))
```

### account_missing_data
Sinaliza problemas de qualidade no cadastro da conta.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "account_missing_data"; SE((A:A=""); ""; SE((L:L="")+(L:L="-"); "sim"; "não"))))
```

### price_to_revenue_ratio
Impacto financeiro do produto no orçamento do cliente (share of wallet).

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "price_to_revenue_ratio"; SE((A:A=""); ""; SE((O:O="")+(O:O="-")+(O:O=0); ""; K:K / O:O))))
```

---

## Bloco 2 — Indicadores Preditivos

Estes indicadores usam `MAP + LAMBDA` porque `CONT.SES` e `MÉDIASES` não funcionam dentro de `ARRAYFORMULA` tradicional (retornam o mesmo valor em todas as linhas).

### agent_win_rate_global
Taxa de conversão global do vendedor.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "agent_win_rate_global"; SE((A:A=""); ""; SE((CONT.SES(F:F; F:F; B:B; "Won") + CONT.SES(F:F; F:F; B:B; "Lost"))=0; ""; CONT.SES(F:F; F:F; B:B; "Won") / (CONT.SES(F:F; F:F; B:B; "Won") + CONT.SES(F:F; F:F; B:B; "Lost"))))))
```

### agent_win_rate_product
Taxa de conversão do vendedor especificamente para o produto negociado.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "agent_win_rate_product"; SE((A:A=""); ""; SE((CONT.SES(F:F; F:F; I:I; I:I; B:B; "Won") + CONT.SES(F:F; F:F; I:I; I:I; B:B; "Lost"))=0; ""; CONT.SES(F:F; F:F; I:I; I:I; B:B; "Won") / (CONT.SES(F:F; F:F; I:I; I:I; B:B; "Won") + CONT.SES(F:F; F:F; I:I; I:I; B:B; "Lost"))))))
```

### agent_win_rate_sector
Taxa de conversão do vendedor no setor do cliente.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "agent_win_rate_sector"; SE((A:A=""); ""; SE((CONT.SES(F:F; F:F; M:M; M:M; B:B; "Won") + CONT.SES(F:F; F:F; M:M; M:M; B:B; "Lost"))=0; ""; CONT.SES(F:F; F:F; M:M; M:M; B:B; "Won") / (CONT.SES(F:F; F:F; M:M; M:M; B:B; "Won") + CONT.SES(F:F; F:F; M:M; M:M; B:B; "Lost"))))))
```

### agent_avg_ticket
Ticket médio dos negócios ganhos pelo vendedor.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "agent_avg_ticket"; SE((A:A=""); ""; SE(CONT.SE(F:F&B:B; F:F&"Won")=0; ""; SOMASE(F:F&B:B; F:F&"Won"; E:E) / CONT.SE(F:F&B:B; F:F&"Won")))))
```

### agent_avg_discount_pct
Percentual médio de desconto concedido pelo vendedor.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "agent_avg_discount_pct"; SE((A:A=""); ""; SE((CONT.SE(F:F&B:B; F:F&"Won")=0)+(SOMASE(F:F&B:B; F:F&"Won"; K:K)=0); ""; 1 - (SOMASE(F:F&B:B; F:F&"Won"; E:E) / SOMASE(F:F&B:B; F:F&"Won"; K:K))))))
```

### agent_avg_cycle
Ciclo de vendas médio do vendedor.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "agent_avg_cycle"; SE((A:A=""); ""; SE(CONT.SE(F:F&B:B; F:F&"Won")=0; ""; (SOMASE(F:F&B:B; F:F&"Won"; D:D) - SOMASE(F:F&B:B; F:F&"Won"; C:C)) / CONT.SE(F:F&B:B; F:F&"Won")))))
```

### manager_win_rate
Taxa de conversão agregada por gestor de vendas.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "manager_win_rate"; SE((A:A=""); ""; SE((CONT.SE(G:G&B:B; G:G&"Won") + CONT.SE(G:G&B:B; G:G&"Lost"))=0; ""; CONT.SE(G:G&B:B; G:G&"Won") / (CONT.SE(G:G&B:B; G:G&"Won") + CONT.SE(G:G&B:B; G:G&"Lost"))))))
```

### regional_win_rate
Taxa de conversão agregada por escritório regional.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "regional_win_rate"; SE((A:A=""); ""; SE((CONT.SE(H:H&B:B; H:H&"Won") + CONT.SE(H:H&B:B; H:H&"Lost"))=0; ""; CONT.SE(H:H&B:B; H:H&"Won") / (CONT.SE(H:H&B:B; H:H&"Won") + CONT.SE(H:H&B:B; H:H&"Lost"))))))
```

### product_base_win_rate
Taxa de conversão global do produto (baseline).

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "product_base_win_rate"; SE((A:A=""); ""; SE((CONT.SE(I:I&B:B; I:I&"Won") + CONT.SE(I:I&B:B; I:I&"Lost"))=0; ""; CONT.SE(I:I&B:B; I:I&"Won") / (CONT.SE(I:I&B:B; I:I&"Won") + CONT.SE(I:I&B:B; I:I&"Lost"))))))
```

### product_avg_cycle
Ciclo médio histórico do produto (baseline de tempo).

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "product_avg_cycle"; SE((A:A=""); ""; SE(CONT.SE(I:I&B:B; I:I&"Won")=0; ""; (SOMASE(I:I&B:B; I:I&"Won"; D:D) - SOMASE(I:I&B:B; I:I&"Won"; C:C)) / CONT.SE(I:I&B:B; I:I&"Won")))))
```

### sector_win_rate
Taxa de conversão global histórica por setor.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "sector_win_rate"; SE((A:A=""); ""; SE((CONT.SE(M:M&B:B; M:M&"Won") + CONT.SE(M:M&B:B; M:M&"Lost"))=0; ""; CONT.SE(M:M&B:B; M:M&"Won") / (CONT.SE(M:M&B:B; M:M&"Won") + CONT.SE(M:M&B:B; M:M&"Lost"))))))
```

### account_prior_deals
Histórico de negociações finalizadas da conta.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "account_prior_deals"; SE((A:A=""); ""; SE((L:L="")+(L:L="-"); ""; CONT.SE(L:L&B:B; L:L&"Won") + CONT.SE(L:L&B:B; L:L&"Lost")))))
```

### account_prior_win_rate
Taxa histórica de sucesso por conta.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "account_prior_win_rate"; SE((A:A=""); ""; SE((L:L="")+(L:L="-"); ""; SE((CONT.SE(L:L&B:B; L:L&"Won") + CONT.SE(L:L&B:B; L:L&"Lost"))=0; ""; CONT.SE(L:L&B:B; L:L&"Won") / (CONT.SE(L:L&B:B; L:L&"Won") + CONT.SE(L:L&B:B; L:L&"Lost")))))))
```

### account_prior_avg_ticket
Ticket médio histórico da conta.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "account_prior_avg_ticket"; SE((A:A=""); ""; SE((L:L="")+(L:L="-"); ""; SE(CONT.SE(L:L&B:B; L:L&"Won")=0; ""; SOMASE(L:L&B:B; L:L&"Won"; E:E) / CONT.SE(L:L&B:B; L:L&"Won"))))))
```

### is_repeat_customer
Sinalizador booleano para clientes recorrentes.

```
=ARRAYFORMULA(SE(LIN(A:A)=1; "is_repeat_customer"; SE((A:A=""); ""; SE((L:L="")+(L:L="-"); ""; SE(CONT.SE(L:L&B:B; L:L&"Won")>0; "sim"; "não")))))
```

---

## Bloco 3 — Scoring e Priorização

### probability_score
Score heurístico de 0 a 100 combinando 4 fatores com pesos transparentes.

**Pesos:**
- 40% — Win rate do vendedor com o produto específico (sinal mais preciso)
- 20% — Tração de mercado (média entre win rate do produto e do setor)
- 20% — Cliente recorrente (multiplicador 0.7 se sim, 0.5 se não)
- 20% — Frescor no pipeline (0.8 se <30 dias, 0.5 se <60 dias, 0.2 se >=60 dias)

```
={"probability_score"; MAP(B2:B; AE2:AE; AL2:AL; AN2:AN; AR2:AR; S2:S; LAMBDA(stage; awrp; pwr; swr; repeat; dias; SE(stage=""; ""; SE(OU(stage="Won"; stage="Lost"); ""; ARRED((0,4 * N(awrp) + 0,2 * ((N(pwr)+N(swr))/2) + 0,2 * SE(repeat="sim"; 0,7; 0,5) + 0,2 * SE(dias=""; 0,7; SE(dias<30; 0,8; SE(dias<60; 0,5; 0,2)))) * 100; 0)))))}
```

### expected_value
Valor esperado ponderado pela probabilidade (EMV).

```
={"expected_value"; MAP(A2:A; B2:B; K2:K; AS2:AS; LAMBDA(id; stage; price; prob; SE(id=""; ""; SE(OU(stage="Won"; stage="Lost"); ""; (prob/100) * N(price)))))}
```

### priority_quadrant
Matriz de segmentação estratégica em 4 quadrantes.

**Cortes:** probability_score >= 60 (alta chance) e expected_value >= 1000 (alto impacto).

- **A - Foco Máximo:** alta chance + alto valor
- **B - Quick Win:** alta chance + baixo valor
- **C - Estratégico (Risco):** baixa chance + alto valor
- **D - Baixa Prioridade:** baixa chance + baixo valor

```
={"priority_quadrant"; MAP(A2:A; AS2:AS; AT2:AT; LAMBDA(id; prob; expval; SE(id=""; ""; SE(prob=""; ""; SE(E(prob>=60; expval>=1000); "A - Foco Máximo"; SE(E(prob>=60; expval<1000); "B - Quick Win"; SE(E(prob<60; expval>=1000); "C - Estratégico (Risco)"; "D - Baixa Prioridade")))))))}
```

---

## Régua ALTA/MÉDIA/BAIXA aplicada no webapp

A tradução final dos quadrantes para a régua visível ao vendedor:

- **ALTA** = Quadrante A (107 deals no snapshot = 5% dos abertos)
- **MÉDIA** = Quadrantes B + C (938 deals = 45%)
- **BAIXA** = Quadrante D (1.044 deals = 50%)

Ordenação secundária dentro de cada faixa sempre por `expected_value` decrescente.

Distribuição validada empiricamente antes de adotar, para evitar o efeito "quando tudo é prioridade, nada é prioritário".
