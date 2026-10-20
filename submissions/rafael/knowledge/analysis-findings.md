# Achados — notebooks 02 (geral) e 03 (por plataforma)

Código: `solution/src/social_insights/` · testes: `solution/tests/` · notebooks gerados por `solution/notebooks/build/`.

## Métodos (e por quê)
- **Top post** = top 10% por métrica (global ou dentro da plataforma).
- **Lift + qui² + FDR (Benjamini-Hochberg)**: atributos e pares de atributos (regras de associação). Sem correção, cerca de 5% dos testes "acertam" por acaso.
- **Gradient boosting com CV (R², AUC)** + permutation importance + árvore rasa legível.
- **K-Means** em 2 espaços (desempenho; atributos via one-hot+SVD) comparado com um **nulo por permutação de colunas**. Hopkins foi descartado: ele dá ~0,9 em nuvem gaussiana única (falso "há clusters").
- **Audiência**: V de Cramér, resíduos ajustados (|r| > 3), índice de engajamento por segmento.
- **NLP**: VADER (sentimento), log-odds com prior de Dirichlet (Monroe 2008) para palavras distintivas, NMF (tópicos). Sugestão aplicada: o mesmo método em legendas e hashtags (que o time controla).
- **Controle positivo**: +2% de views em TikTok×vídeo×tech precisa ser detectado.

## Resultados
- Top em views fica só ~1,3% acima da média; a sobreposição entre tops de métricas diferentes (Jaccard 0,05) é a esperada por independência.
- Geral: 0 de 69 atributos e 0 de 2.108 pares significativos (FDR) nas 4 métricas; ~105 p < 0,05 crus = exatamente o acaso. "Melhor" par aparente: lift 1,5, q = 1.
- Modelos: R² ≈ 0, AUC ≈ 0,50. Clusters: ganho de silhueta sobre o nulo ≈ 0.
- Clusters de atributos separam receitas (patrocinado moda/comida; creators mega), mas as métricas são iguais (Kruskal p > 0,3).
- Audiência: 0 associações conteúdo×audiência (V < 0,04); 0 células com |resíduo| > 3; índice por segmento 99,8–100,2.
- NLP: sentimento igual entre top e demais (p > 0,77); nenhuma palavra com |z| > 1,96; tópicos sem semântica (texto Faker).
- Por plataforma: 23.208 regras; 3 passam no FDR por tabela (espanhol+beleza/vídeo → likes TikTok; 4 hashtags+sexta → shares Bilibili) e **0 passam na correção global**.
- Controle positivo: efeito de 2% detectado (q ≈ 0, R² 0 → 0,08; AUC 0,81 só no TikTok). O método é sensível; a ausência de sinal é real.

## Plano de ação (notebook 04)
- Qualidade: 0 duplicados, 0 valores impossíveis; nulos só em hashtags (17%). Outliers de Tukey < 1%, no máx. +4,5% (views) / +29% (comentários) da mediana → nada removido.
- Alvos sem assimetria (skew ≈ 0, CV 1–7%) → log não muda a forma; mantido nos modelos por padronização.
- Likes/seguidor × seguidores: ρ = −0,999, idêntico com likes embaralhados → artefato de razão. Likes × seguidores: ρ ≈ 0.
- Pearson/Spearman: 0 de 24 significativas (máx. |ρ| 0,011). Kruskal categóricas: 0 de 39 (ε² máx. 0,00025). Faixas: 1 p < 0,05 em 15 (acaso).
- RF/XGBoost/CatBoost × pré-publicação/explicativo × 3 alvos: R² validação ≈ 0 (≤ 0). RF R² treino ~0,1 → overfitting.
- SHAP: importâncias ≤ 0,12% da previsão, mesma magnitude do modelo com alvo embaralhado; interações ~0,01%.
