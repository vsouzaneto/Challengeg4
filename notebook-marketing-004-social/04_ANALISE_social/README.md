# LAB 04 — Social Media Engagement Analyser

Notebook: `social-media-engagement-analyser.ipynb`

Origem: [aba Code do dataset](https://www.kaggle.com/datasets/omenkj/social-media-sponsorship-and-engagement-dataset/code) (SPEC-008). Slug direto 404 nesta leitura.

Alterações para Databricks:

- Remove `/kaggle/input/...`
- Primeiro tenta `spark.table(catalog.schema.social_media_dataset)` (Lab 01)
- Fallback: `pd.read_csv` em `dados/`
- `is_sponsored` e `post_date` normalizados

O kernel deriva `engagement_rate` = engagement / `follower_count` (não / `views`). A taxa por view do dump é quase constante (~0,199). Dependências extras (`xgboost`, `textblob`, `shap`) são instaladas pela célula `%pip` no job serverless.
