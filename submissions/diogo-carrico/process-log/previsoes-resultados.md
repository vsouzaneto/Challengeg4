# Previsões e resultados

> As previsões estão em `00-hipoteses.md`, commitadas antes do download dos dados (commit `d899d17`).
> Cada resultado aponta para o arquivo que o produziu. Atualizado a cada fase.

## Previsões numéricas

| # | Previsão | Resultado | Acertou? | Fonte |
|---|---|---|---|---|
| P1 | 8.469 tickets no Dataset 1 (influenciada pelos PRs) | 8.469 registros; 0 duplicados; 0 IDs repetidos. As 29.808 linhas físicas vêm de 6.150 descrições com quebra de linha | Sim | `solution/outputs/audit/audit_d1.json` → `counts` |
| P2 | Spearman entre resolução e CSAT entre −0,10 e +0,10 (influenciada pelos PRs) | ρ = 0,022 (p = 0,25, n = 2.769); só durações não negativas: ρ = 0,003 (p = 0,92, n = 1.404) | Sim | `audit_d1.json` → `csat` |
| P3 | Acurácia de TF-IDF + regressão logística ≈ 86% | O modelo escolhido na validação foi TF-IDF + SVM linear: 86,7% de acurácia no teste (IC 95% 85,8% a 87,6%). A melhor regressão logística teve 85,9% de macro-F1 na validação; o teste só avalia o modelo escolhido, para não ser gasto comparando vários | Sim, com o modelo vizinho | `solution/outputs/classifier/metrics.json` → `test`, `model_selection` |
| P4 | ~20% dos erros auditados ligados a ruído de rótulo | Não testada: cortada do escopo (D13). Evidência parcial: 105 grupos de quase-duplicatas (617 tickets) com rótulos diferentes | Não testada | `metrics.json` → `data.near_duplicates`; `docs/proximos-passos.md` |
| P5 | ~50% dos tickets roteáveis com precisão ≥ 95% | Fluxo completo da demo: 43,5% (precisão 97,7%, IC 97,0% a 98,2%), só com as 4 classes que provaram 95% no teste; 64,1% se o piloto confirmar as outras 3. O classificador sozinho chega a 64,9% com limiares por classe | Não: o fluxo completo roteia menos do que eu previ | `metrics.json` → `end_to_end_dataset2_test` |
| P6 | Queda de ~40 p.p. em português | Não testada: cortada do escopo (D13) | Não testada | `docs/proximos-passos.md` |
| P7 | Construir fica mais barato a partir de ~20 mil tickets/mês | Não testada: o comparativo virou uma tabela de custos no README, sem cálculo de ponto de equilíbrio (D13). A triagem construída custa cerca de US$ 8 por mês de infraestrutura, quase todo fixo; o custo real é o de manutenção | Não testada | `README.md`, seção Custos |
| P8 | ~65% dos rascunhos aprovados sem edição | Não testada: cortada do escopo (D13) | Não testada | `docs/proximos-passos.md` |

## Hipóteses qualitativas

| Hipótese | Resultado | Fonte |
|---|---|---|
| 1.1 Sinais de dado sintético: descrição padronizada demais | Confirmado: duas frases fixas aparecem em cerca de 6.000 das 8.469 descrições, e `{product_purchased}` em 100% | `audit_d1.json` → `description_text` |
| 1.1 Combinação que não faz sentido | Confirmado: assunto e tipo não se relacionam (V de Cramér 0,03; p = 0,98) | `audit_d1.json` → `associations` |
| 1.1 Distribuição muito regular | Confirmado: tipo, prioridade, canal, status, produto, CSAT e idade indistinguíveis de partes iguais | `audit_d1.json` → `categoricals`, `csat`, `age` |
| 1.1 Diferença clara entre canal e tipo de problema | Não confirmado: canal e tipo não se relacionam (V de Cramér 0,02; p = 0,46) | `audit_d1.json` → `associations.channel_vs_type` |
| 1.1 Correlação perto de zero sozinha não prova que é sintético | Mantido: o veredito de dado sintético se apoia em oito sinais, não na correlação | `docs/auditoria-dados.md` |
| 2.2 Access é a categoria mais difícil | Não confirmado: a mais difícil é Administrative rights (F1 78,9%, recall 71,0%), e a maior parte dos erros dela vai para Hardware (37 de 176), não para Access (1). Access tem o segundo melhor F1 (88,8%) | `metrics.json` → `test.per_class`; `confusion_matrix.csv` |
| 3.1 Não automatizar a concessão de privilégio | Os dados chegaram à mesma conclusão: Administrative rights não alcança 95% de precisão com confiança na validação e nunca é roteado sozinho | `metrics.json` → `thresholds.per_class_thresholds` |
| 3.2 Pelo menos 95% de precisão, olhando por categoria | Adotado. Com limiar único, Hardware ficaria em 92,9%; com limiares por classe, todas ficam em 95% ou mais, exceto Storage (94,5% no teste, IC 90,7% a 96,8%) | `metrics.json` → `thresholds` |
