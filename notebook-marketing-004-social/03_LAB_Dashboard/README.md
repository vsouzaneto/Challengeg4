<img src="https://raw.githubusercontent.com/Databricks-BR/lab_agosto_2025/main/images/head_lab.png">

# LAB 03 — Dashboard AI/BI

Notebook: `lab03_dashboard.ipynb` — análise controlada + estratégia (SPEC-004 / ENTREGAVEIS).

Publicado: [lab-004-social-media](https://dbc-0dea39b3-be1e.cloud.databricks.com/dashboardsv3/01f1b611d0801412b387d62b0dc4d8d6/published?o=7474644277755368) (`lab-004-social-media.lvdash.json`).

Pré-requisito: tabela `social_media_dataset` do Lab 01.

Sugestão de tiles (colunas reais):

- Volume por `platform` (inclua Bilibili e RedNote), `content_type`, `content_category`
- Taxa derivada `(likes + shares + comments_count) / views` por `is_sponsored` **e** por plataforma × categoria
- Faixa de `follower_count` × sponsor (controle de tamanho de creator)
- Audiência como bucket: `audience_age_distribution` / `audience_location`
- Top 15 de taxa por view (`NULLIF(views, 0)`), célula com pelo menos 30 posts

Não invente `engagement_rate` nativo. Não use `creator_name` como dimensão de creator.

Painéis gráficos (Run All no notebook + página **Paineis** no `.lvdash.json`):

| Seção | Dado real |
| --- | --- |
| Ranking de benchmark | Taxa derivada por plataforma / célula |
| Galeria de entrada | Amostra de posts |
| Classificação | `content_type` |
| Segmentação | `platform` × `content_category` |
| Segmentação de imagem | Proxy por `content_type` (sem pixels) |
| Estatísticas / matriz / curva / viés | Baseline logístico, label = taxa acima da mediana |

Cabeçalho opcional:

```
![Image](https://raw.githubusercontent.com/Databricks-BR/lab_agosto_2025/refs/heads/main/images/head_lab.png)
```
