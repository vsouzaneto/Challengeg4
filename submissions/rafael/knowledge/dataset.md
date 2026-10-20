# Dataset — achados

Fonte: Kaggle `omenkj/social-media-sponsorship-and-engagement-dataset` (MIT), via API pública de metadados.

- Arquivo: `social_media_dataset.csv` (~23 MB, ~52K linhas). Download exige login Kaggle.
- **⚠️ Dados SIMULADOS — CONFIRMADO, ver `eda-findings.md`** (descrição oficial): views via Poisson, datas aleatórias em 2 anos, `creator_id` cicla 5.000 creators, amostra balanceada sponsored/orgânico.
  - Hipótese a testar: métricas podem ser ruído independente das features → diferenças entre grupos ≈ 0.
  - Se confirmado, é o principal divisor de águas: a entrega honesta é "os dados não sustentam X" + framework/ferramenta que funciona com dados reais.
- **Divergências vs. README do challenge**:
  - Não existe coluna `engagement_rate` → calcular (ex.: (likes+shares+comments)/views e /followers).
  - Não há custo de patrocínio → "custo implícito" precisa ser proxy (ex.: follower_count como preço).
  - Categorias: só `beauty`, `lifestyle`, `tech`.
  - Audiência é categórica (grupo predominante), não distribuição.
- Colunas: id, platform, content_id, creator_id, creator_name, content_url, content_type, content_category, post_date, language, content_length, content_description, hashtags (0–5), views, likes, shares, comments_count, comments_text, follower_count, is_sponsored, disclosure_type, sponsor_name, sponsor_category, disclosure_location, audience_age_distribution, audience_gender_distribution, audience_location.

## Próximos passos
1. ~~Obter CSV~~ (feito, 52.214 linhas, em `data/raw/`).
2. EDA: distribuições, correlações, testes de independência (views/likes vs. features).
3. Verificar consistência interna (likes ≤ views? follower_count estável por creator?).
