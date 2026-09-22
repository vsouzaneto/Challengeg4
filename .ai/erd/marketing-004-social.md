# ERD — 004 Social — schema observado

Fonte: `datasets/marketing-004-social/social_media_dataset.csv` (52 214 × 27). Leitura 2026-09-21.

```
                    post (52214)
                    PK id (int)
                    UK content_id (string)   id ≠ content_id
                              │
     ┌────────────┬───────────┼────────────┬────────────┐
     ▼            ▼           ▼            ▼            ▼
 platform     content      metrics      creator     audience
 5 enums      type 4       views…       id 5000     3 categorias
              cat 3        (sem rate)   name N:1    (não é JSON)
              hashtags
                              │
                              ▼
                         sponsorship
                    is_sponsored + 3 disclosure
                    sponsor sempre preenchido
```

Não há tabela creator/sponsor. Rollup = `GROUP BY` na fato.

## Colunas físicas (27)

| Coluna | nunique / null | Notas |
|--------|----------------|-------|
| `id` | 52 214 PK | int 1… |
| `platform` | 5 | Bilibili 10 598, YouTube 10 495, Instagram 10 423, RedNote 10 402, TikTok 10 296 |
| `content_id` | 52 214 UK | `content_*` — **≠** `id` |
| `creator_id` | 5 000 | chave de creator |
| `creator_name` | 42 213 | **~10 nomes por id** — não usar como PK |
| `content_url` | 28 037 | 24 177 dups |
| `content_type` | 4 | video 31 500, image 10 303, mixed 5 213, text 5 198 |
| `content_category` | 3 | beauty 21 023, lifestyle 20 761, tech 10 430 |
| `post_date` | 50 905 | string `M/D/YY I:MM AM` → 2023-05-29 … 2025-05-28 |
| `language` | 5 | English 26 110, Chinese, Hindi, Spanish, Japanese |
| `content_length` | 10–599 | |
| `content_description` | 52 214 | texto |
| `hashtags` | 8 743 null (16,7%) | lista tipo `car,hair,save` — não `#tag` |
| `views` | 9 676–10 551 | faixa **muito estreita** |
| `likes` | 1 354–1 668 | |
| `shares` | 227–380 | |
| `comments_count` | 140–258 | |
| `comments_text` | 8 688 null | |
| `follower_count` | 1 013–999 998 | |
| `is_sponsored` | 29 900 false / 22 314 true | |
| `disclosure_type` | none / explicit / implicit | `none` ⇔ not sponsored |
| `sponsor_name` | 18 006 | **nunca null** |
| `sponsor_category` | 7 | `Not sponsors` nos orgânicos; senão food, electronics, fashion, cosmetics, gaming, travel |
| `disclosure_location` | none / caption / video / hashtags | |
| `audience_age_distribution` | 5 | **bucket**: 19-25, 26-35, 13-18, 36-50, 50+ |
| `audience_gender_distribution` | 4 | male, female, non-binary, unknown |
| `audience_location` | 8 | China, UK, Japan, Brazil, USA, Germany, India, Russia (~iguais) |

## Ausente / derivado

| Brief | Disco |
|-------|-------|
| Engagement rate | **não há coluna**. `(likes+shares+comments_count)/views` ≈ **0,199 ± 0,005** (orgânico ≈ patrocinado) |
| “distribution” de audiência | um rótulo por post |
| ROI / custo de patrocínio | **não há** custo — “custo implícito” é hipótese, não campo |

## Traps

1. Comparar orgânico vs ads **sem** controlar creator/plataforma/categoria ainda é obrigatório (SPEC-004), mas a taxa bruta **quase não se move** — o insight não pode ser “patrocínio não muda engagement médio” sem dizer que o dump é quase constante.
2. `creator_name` mente. Use `creator_id` + `follower_count` (este último varia por post, não é atributo estável do creator).
3. Hashtags parecem tokens aleatórios — análise de combinação exige saneamento.
