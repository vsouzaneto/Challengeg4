# `dados/` — Social (challenge 004)

Contado no disco em 2026-09-21. Não inventar coluna.

| Arquivo | Linhas | Colunas |
| --- | ---: | --- |
| `social_media_dataset.csv` | 52214 | `id`, `platform`, `content_id`, `creator_id`, `creator_name`, `content_url`, `content_type`, `content_category`, `post_date`, `language`, `content_length`, `content_description`, `hashtags`, `views`, `likes`, `shares`, `comments_count`, `comments_text`, `follower_count`, `is_sponsored`, `disclosure_type`, `sponsor_name`, `sponsor_category`, `disclosure_location`, `audience_age_distribution`, `audience_gender_distribution`, `audience_location` |

Grain = post. Sem `engagement_rate` — derivar `(likes + shares + comments_count) / views` (≈ 0,199). `creator_name` não é PK. Audiência é bucket. Sem custo de patrocínio.
