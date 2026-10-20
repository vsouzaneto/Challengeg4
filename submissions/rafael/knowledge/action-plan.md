# Plano de ação (fornecido pelo usuário, gerado com outra IA) — 2026-10-18

Objetivo: identificar quais características dos posts mais se associam a likes, views e comments.
Implementação: `solution/notebooks/04_plano_de_acao.ipynb` (seções = passos abaixo).

1. Inspeção/limpeza: tipos, nulos, duplicados, outliers; separar variáveis pré-publicação × métricas pós-publicação.
2. Alvos: distribuição, média, mediana, percentis, assimetria, log.
3. Métricas normalizadas: like rate, comment rate, likes/seguidor, views/seguidor.
4. Correlações Pearson e Spearman (priorizar Spearman), por alvo.
5. Categóricas: plataforma, formato, categoria, dia, horário… com mediana/distribuição + testes.
6. Não linearidade: faixas de horário, hashtags, legenda, duração.
7. Top 10% × 90% por views, likes, comments; características mais frequentes nos tops.
8. Modelos por alvo: Random Forest, XGBoost, CatBoost.
9. Dois cenários: explicativo (com outras métricas) × pré-publicação.
10. Interpretação: feature importance, SHAP, interações.
11. Entrega: relações, fatores, top × demais, gráficos, recomendações práticas, correlação × causalidade.

## Ressalvas registradas antes da execução
- Razões por seguidor têm correlação espúria com follower_count (o denominador é compartilhado).
- O cenário explicativo depende de as métricas se correlacionarem entre si (EDA: ρ ≈ 0).
