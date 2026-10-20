# Modelo preditivo de engajamento — achados e como usar

Fonte: `solution/src/social_insights/engagement_model.py` · notebook: `solution/notebooks/05_modelo_engajamento.ipynb` · CLI: `solution/cli/predict_engagement.py` · gerado em 2026-10-18 sobre 52.214 posts.
Mesmo formato dos outros arquivos para o site: manchete, números-chave, gráficos sugeridos, uso.

## Problema
- **Entrada:** características conhecidas **antes** de publicar: plataforma, formato, categoria, idioma, dia, hora, seguidores, duração, nº de hashtags, palavras da legenda, patrocínio/disclosure, audiência (gênero, idade, país).
- **Saída:** engajamento estimado = (likes + shares + comentários) / views, com **intervalo de 90%**.
- **Protocolo:** mesmos 5 folds para todos; baseline = chutar a média; adoção só se o modelo for **significativamente melhor** que o baseline (t pareado entre folds); R² de treino ao lado do de validação.

## Manchete
**Nenhuma das 14 abordagens supervisionadas prevê engajamento melhor que a média.** O previsor entregue detecta isso e adota a média (19,9%), avisando o usuário. Com sinal plantado, ele troca sozinho para CatBoost.

## Resultados — regressão (5 folds)

| Modelo | Família | R² validação | R² treino | MAE vs. média |
|---|---|---|---|---|
| Média (baseline) | baseline | −0,0001 | 0,000 | 0,00% |
| Média por plataforma | baseline | −0,0002 | 0,000 | 0,00% |
| Lasso | linear | −0,0002 | 0,000 | −0,01% |
| ElasticNet | linear | −0,0004 | 0,001 | −0,02% |
| CatBoost | boosting | −0,0005 | 0,005 | −0,02% |
| HistGradientBoosting | boosting | −0,0007 | 0,005 | −0,03% |
| Ridge | linear | −0,0009 | 0,001 | −0,05% |
| Random Forest | florestas | −0,0018 | **0,093** | −0,07% |
| Extra Trees | florestas | −0,0030 | **0,093** | −0,14% |
| Árvore de decisão | árvore | −0,0039 | 0,004 | −0,23% |
| XGBoost | boosting | −0,0049 | 0,045 | −0,22% |
| LightGBM | boosting | −0,0088 | **0,114** | −0,45% |
| MLP (rede neural) | rede neural | −0,0134 | −0,008 | −0,56% |
| KNN (k=50) | vizinhos | −0,0206 | 0,019 | −1,04% |

- **Overfitting:** Random Forest, Extra Trees e LightGBM "explicam" 9–11% do treino e ficam piores que a média em dados novos. Sem validação, seriam vendidos como "o modelo explica 10% do engajamento".
- **Classificação (top 10% de engajamento):** AUC 0,500 (logística), 0,493 (HistGB) e 0,497 (XGBoost), ou seja, cara ou coroa.
- **Curva de aprendizado (LightGBM):** de 4 mil para 42 mil posts, o R² de treino cai de 0,59 para 0,11 e o de validação sobe de −0,08 para −0,01, **sem nunca passar de 0**. Mais dados com as mesmas colunas não resolvem.

## Teste de sensibilidade (efeito plantado de +5% nos likes)

| Modelo | A. Segmento (TikTok × vídeo × tech, 2,4% dos posts) | B. Não linear (duração 100–200 & 18–22h, 5,4%) |
|---|---|---|
| CatBoost | **R² 0,048** ✓ | **R² 0,102** ✓ |
| Árvore de decisão | 0,043 ✓ | 0,100 ✓ |
| LightGBM | 0,040 ✓ | 0,097 ✓ |
| Random Forest | 0,042 ✓ | 0,061 ✓ |
| MLP | 0,043 ✓ | 0,027 ✓ |
| Ridge | 0,009 (capta ~1/5) | 0,008 (quase nada) |
| KNN | ✗ | ✗ |

- **Conclusão:** quando há sinal, a escolha importa. **O boosting (CatBoost/LightGBM) é o recomendado para os dados reais.** Lineares não representam interações e o KNN se dilui em 30 dimensões.

## Mensagens para o site
1. "Testamos 14 abordagens de machine learning; nenhuma bate a média, e mostramos por quê."
2. "Modelo que decora não prevê": gráfico R² treino vs. validação (halteres).
3. "O método funciona": com +5% plantado, o CatBoost detecta, e um previsor honesto troca de modelo sozinho.
4. "Mais dados não salvam variáveis sem sinal": curva de aprendizado.

**Gráficos sugeridos:** halteres R² treino × validação por modelo; barras de ganho de MAE vs. média; curva de aprendizado; barras agrupadas do teste de sensibilidade (A × B).

---

## Como utilizar

### Linha de comando (estimar um post planejado)
```bash
cd submissions/rafael
.venv/bin/python solution/cli/predict_engagement.py --platform TikTok --content_type video --content_category tech --follower_count 25000
# Modelo: Média (baseline) (R² validação -0.0001; supera baseline: não)
# Engajamento estimado: 19.91%  (intervalo 90%: 19.11% – 20.71%)
.venv/bin/python solution/cli/predict_engagement.py --retrain     # refaz a comparação (~75 s) e salva em solution/models/
```
Campos não informados assumem o post típico (moda/mediana). Aceita qualquer coluna de entrada como `--<coluna>`.

### Em Python
```python
import sys; sys.path.insert(0, "solution/src")
from social_insights import data, engagement_model as em

df = data.load_posts()
summary, fold_errors = em.compare_models(df)          # 14 modelos × 5 folds
predictor = em.EngagementPredictor.train(df, summary) # adota o melhor que supera o baseline (ou a média)
predictor.predict(novos_posts)                        # engajamento estimado + intervalo 90% + nome do modelo
predictor.save(path); em.EngagementPredictor.load(path)
em.compare_classifiers(df, top_flag)                  # formulação top 10% (AUC)
em.learning_curve_table(df, "LightGBM")               # mais dados ajudariam?
```

| Função/classe | Para quê |
|---|---|
| `candidate_models()` | as 14 abordagens (nome → família, estimador) |
| `compare_models(df, target, models, folds)` | CV pareada + teste contra o baseline |
| `compare_classifiers(df, top)` | AUC da formulação "top 10%" |
| `learning_curve_table(df, model)` | R² × tamanho do treino |
| `EngagementPredictor` | treino, previsão com intervalo, save/load |
| `validation.inject_engagement_uplift` | teste de sensibilidade (efeito plantado) |

### Com dados reais
Mesmas colunas do Kaggle em `data/raw/social_media_dataset.csv`, depois `--retrain`. Se algum modelo superar a média, o previsor o adota automaticamente e o intervalo se estreita.

### Qualidade
`solution/tests/test_engagement_model.py` verifica três coisas: nenhum modelo é adotado em ruído; o LightGBM é adotado com efeito plantado; o intervalo e o save/load funcionam.
