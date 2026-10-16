# Registro correlação vs causalidade

| Claim | Evidência | Classificação |
|-------|-----------|---------------|
| Uso agregado não explica churn líquido | Médias ~10 usage_count/linha iguais | Correlação fraca / não separa |
| Escalação associada a churn líquido | 6,1% vs 4,3% | Correlação observada |
| DevTools / event pior churn | segment_net_churn.csv | Correlação segmentar |
| Porta giratória existe | 277 revolving, MRR sum | Fato descritivo |
| reason_code explica causa | Distribuição uniforme ~100/tipo | **Não usar** como causal |
| Modelo prediz churn | AUC ~0,62 hold-out | Predição fraca — triagem only |

**Testes que faltam para causalidade:** experimento CS, A/B onboarding DevTools, intervenção pós-escalação.
