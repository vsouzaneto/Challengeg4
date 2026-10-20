# Respostas e estratégia — Challenge 004

## 1. O que gera engajamento?

**Resposta:** Nenhum fator nem combinação gera engajamento diferente. 450 segmentos testados, 22 com p<0,05 cru (~22 esperados por acaso) e 0 após correção. Maior diferença entre grupos: 0.07%.

|    | dimensão         | melhor        | pior        |   diferença melhor−pior (%) |   epsilon² |   p_value |   q_value | significativo   |
|---:|:-----------------|:--------------|:------------|----------------------------:|-----------:|----------:|----------:|:----------------|
|  0 | platform         | RedNote       | Instagram   |                     0.05282 |  8.31e-05  |    0.3621 |    0.4828 | False           |
|  1 | content_type     | text          | video       |                     0.06093 |  8.395e-05 |    0.2229 |    0.4828 | False           |
|  2 | content_category | lifestyle     | tech        |                     0.03765 |  4.768e-05 |    0.288  |    0.4828 | False           |
|  3 | follower_tier    | mid (50–100K) | nano (<10K) |                     0.07206 |  3.821e-05 |    0.7366 |    0.7366 | False           |

### Segmentos com maior índice (aparente)
|    | segmento                                      | dimensões                                                  |   n |   índice |   p_value |   q_value | significativo   |
|---:|:----------------------------------------------|:-----------------------------------------------------------|----:|---------:|----------:|----------:|:----------------|
|  0 | Bilibili · video · lifestyle · micro (10–50K) | platform × content_type × content_category × follower_tier | 109 |    100.5 |  0.02389  |    0.8825 | False           |
|  1 | Bilibili · video · beauty · micro (10–50K)    | platform × content_type × content_category × follower_tier | 107 |    100.5 |  0.06001  |    0.8825 | False           |
|  2 | Bilibili · video · micro (10–50K)             | platform × content_type × follower_tier                    | 272 |    100.5 |  0.00419  |    0.8038 | False           |
|  3 | Instagram · text · beauty · macro (100–500K)  | platform × content_type × content_category × follower_tier | 151 |    100.4 |  0.02517  |    0.8825 | False           |
|  4 | TikTok · video · beauty · mid (50–100K)       | platform × content_type × content_category × follower_tier | 120 |    100.4 |  0.09012  |    0.8825 | False           |
|  5 | TikTok · text · lifestyle · mega (500K+)      | platform × content_type × content_category × follower_tier | 202 |    100.3 |  0.05212  |    0.8825 | False           |
|  6 | TikTok · mixed · beauty · mega (500K+)        | platform × content_type × content_category × follower_tier | 196 |    100.3 |  0.03824  |    0.8825 | False           |
|  7 | RedNote · image · lifestyle · mega (500K+)    | platform × content_type × content_category × follower_tier | 449 |    100.3 |  0.003464 |    0.8038 | False           |
|  8 | Bilibili · text · beauty · macro (100–500K)   | platform × content_type × content_category × follower_tier | 197 |    100.3 |  0.06785  |    0.8825 | False           |
|  9 | RedNote · text · beauty · macro (100–500K)    | platform × content_type × content_category × follower_tier | 141 |    100.3 |  0.1119   |    0.8825 | False           |

### Segmentos significativos
| segmento   | dimensões   | n   | índice   | p_value   | q_value   | significativo   |
|------------|-------------|-----|----------|-----------|-----------|-----------------|

---

## 2. Patrocínio funciona?

**Resposta:** Não: no mesmo estrato (plataforma × formato × categoria × porte), patrocinado vs. orgânico = +0.008% de engajamento e +0.004% de alcance (p=0.72 / 0.63). 0 de 17 condições têm efeito. Como as views não crescem com os seguidores, o custo por mil views (CPM implícito) cresce com o porte: nano (<10K) US$ 5.55 vs. mega (500K+) US$ 744 (premissa: US$ 10 por mil seguidores). Se patrocinar, use creators pequenos e negocie por resultado.

|                                |   diferença |   IC95 inf |   IC95 sup |   diferença (%) |   p_value |   estratos |   q_value |
|:-------------------------------|------------:|-----------:|-----------:|----------------:|----------:|-----------:|----------:|
| eng_rate_views — estratificado |   1.56e-05  | -6.846e-05 |  9.965e-05 |       0.007836  |    0.7161 |        269 |    0.9725 |
| views — estratificado          |   0.4213    | -1.31      |  2.152     |       0.004171  |    0.6334 |        269 |    0.9725 |
| likes — estratificado          |   0.01182   | -0.6593    |  0.683     |       0.0007824 |    0.9725 |        269 |    0.9725 |
| comments_count — estratificado |   0.06128   | -0.1821    |  0.3047    |       0.03064   |    0.6217 |        269 |    0.9725 |
| eng_rate_views — regressão     |  -1.091e-05 | -9.551e-05 |  7.37e-05  |     nan         |    0.8005 |        nan |    0.9725 |

### Em que condições? (uplift do patrocínio por condição)
|    | condição                         |   uplift engajamento (%) |   p_value |   q_value | significativo   |
|---:|:---------------------------------|-------------------------:|----------:|----------:|:----------------|
|  6 | follower_tier = micro (10–50K)   |                  0.1606  |   0.1326  |    0.479  | False           |
|  7 | follower_tier = mid (50–100K)    |                  0.1393  |   0.1382  |    0.479  | False           |
| 16 | content_category = tech          |                  0.123   |   0.01003 |    0.1705 | False           |
| 11 | content_type = mixed             |                  0.08652 |   0.2009  |    0.5693 | False           |
|  1 | platform = Instagram             |                  0.0495  |   0.3157  |    0.5963 | False           |
|  2 | platform = RedNote               |                  0.04947 |   0.3075  |    0.5963 | False           |
| 12 | content_type = text              |                  0.04297 |   0.518   |    0.629  | False           |
| 10 | content_type = image             |                  0.03779 |   0.4384  |    0.629  | False           |
|  4 | platform = YouTube               |                  0.02765 |   0.5551  |    0.6292 | False           |
|  8 | follower_tier = macro (100–500K) |                  0.0249  |   0.4649  |    0.629  | False           |
| 15 | content_category = lifestyle     |                  0.02258 |   0.5115  |    0.629  | False           |
|  0 | platform = Bilibili              |                 -0.01546 |   0.7468  |    0.7934 | False           |

### Custo implícito por porte de creator (patrocinados)
| follower_tier    |        posts |   custo_mediano |   views_medianas |   cpm_implicito_mediano |   engajamento_medio |
|:-----------------|-------------:|----------------:|-----------------:|------------------------:|--------------------:|
| nano (<10K)      |  192         |            55.8 |        1.009e+04 |                   5.554 |              0.1992 |
| micro (10–50K)   |  922         |           295.5 |        1.01e+04  |                  29.31  |              0.1991 |
| mid (50–100K)    | 1108         |           763.5 |        1.01e+04  |                  75.41  |              0.1991 |
| macro (100–500K) | 8968         |          2986   |        1.01e+04  |                 296.4   |              0.1991 |
| mega (500K+)     |    1.112e+04 |          7508   |        1.01e+04  |                 744.3   |              0.199  |

### Engajamento vs. orgânico por categoria de patrocinador (%)
| sponsor_category   |   diferença (%) |
|:-------------------|----------------:|
| cosmetics          |        0.04938  |
| electronics        |       -0.004529 |
| fashion            |       -0.07636  |
| food               |        0.02551  |
| gaming             |       -0.03338  |
| travel             |        0.00634  |

### Engajamento vs. orgânico por tipo de disclosure (%)
| disclosure_type   |   diferença (%) |
|:------------------|----------------:|
| explicit          |         0.01563 |
| implicit          |        -0.0289  |

---

## 3. Qual audiência mais engaja?

**Resposta:** Nenhum perfil de audiência engaja mais: 36 testes (por plataforma, formato e categoria) e 0 significativos. A melhor 'persona' (gênero × idade × país) tem índice 100.5 com q=0.86. Escolha a audiência por objetivo de negócio (quem compra), não por engajamento.

|    | dimensão                     | melhor   | pior       |   diferença melhor−pior (%) |   epsilon² |   p_value |   q_value |
|---:|:-----------------------------|:---------|:-----------|----------------------------:|-----------:|----------:|----------:|
|  0 | audience_gender_distribution | unknown  | non-binary |                    0.003207 |  8.842e-06 |    0.9272 |    0.9272 |
|  1 | audience_age_distribution    | 50+      | 13-18      |                    0.06314  |  6.243e-05 |    0.5153 |    0.773  |
|  2 | audience_location            | UK       | India      |                    0.1061   |  0.0001311 |    0.4454 |    0.773  |

### Por contexto (plataforma, formato, categoria)
|    | contexto                     | audiência                    | segmento que mais engaja   |   diferença melhor−pior (%) |   p_value |   q_value | significativo   |
|---:|:-----------------------------|:-----------------------------|:---------------------------|----------------------------:|----------:|----------:|:----------------|
|  2 | platform = Bilibili          | audience_location            | UK                         |                     0.2923  |   0.06137 |    0.8666 | False           |
|  7 | platform = RedNote           | audience_age_distribution    | 19-25                      |                     0.1259  |   0.1077  |    0.8666 | False           |
|  5 | platform = Instagram         | audience_location            | Brazil                     |                     0.278   |   0.1498  |    0.8666 | False           |
| 32 | content_category = lifestyle | audience_location            | UK                         |                     0.1643  |   0.1556  |    0.8666 | False           |
|  4 | platform = Instagram         | audience_age_distribution    | 26-35                      |                     0.175   |   0.1655  |    0.8666 | False           |
|  1 | platform = Bilibili          | audience_age_distribution    | 50+                        |                     0.1828  |   0.172   |    0.8666 | False           |
| 25 | content_type = video         | audience_age_distribution    | 50+                        |                     0.1023  |   0.1917  |    0.8666 | False           |
| 12 | platform = YouTube           | audience_gender_distribution | male                       |                     0.1038  |   0.261   |    0.8666 | False           |
| 27 | content_category = beauty    | audience_gender_distribution | unknown                    |                     0.06513 |   0.3172  |    0.8666 | False           |
|  8 | platform = RedNote           | audience_location            | USA                        |                     0.2146  |   0.4092  |    0.8666 | False           |
| 35 | content_category = tech      | audience_location            | UK                         |                     0.2385  |   0.425   |    0.8666 | False           |
| 26 | content_type = video         | audience_location            | UK                         |                     0.1215  |   0.4252  |    0.8666 | False           |

### Personas (gênero × idade × país)
|    | segmento                   | dimensões                                                                    |   n |   índice |   p_value |   q_value | significativo   |
|---:|:---------------------------|:-----------------------------------------------------------------------------|----:|---------:|----------:|----------:|:----------------|
|  0 | male · 50+ · UK            | audience_gender_distribution × audience_age_distribution × audience_location | 123 |    100.5 |  0.01911  |    0.8587 | False           |
|  1 | non-binary · 26-35 · China | audience_gender_distribution × audience_age_distribution × audience_location | 213 |    100.5 |  0.002527 |    0.5938 | False           |
|  2 | 50+ · UK                   | audience_age_distribution × audience_location                                | 340 |    100.3 |  0.01526  |    0.8587 | False           |
|  3 | non-binary · 26-35 · UK    | audience_gender_distribution × audience_age_distribution × audience_location | 189 |    100.3 |  0.09662  |    0.9287 | False           |
|  4 | unknown · 13-18 · Japan    | audience_gender_distribution × audience_age_distribution × audience_location | 103 |    100.3 |  0.1846   |    0.9952 | False           |
|  5 | unknown · 26-35 · Germany  | audience_gender_distribution × audience_age_distribution × audience_location | 205 |    100.3 |  0.07395  |    0.8587 | False           |
|  6 | unknown · 50+              | audience_gender_distribution × audience_age_distribution                     | 257 |    100.3 |  0.05434  |    0.8587 | False           |
|  7 | female · 50+ · Russia      | audience_gender_distribution × audience_age_distribution × audience_location | 128 |    100.3 |  0.1613   |    0.9952 | False           |
|  8 | unknown · 19-25 · Japan    | audience_gender_distribution × audience_age_distribution × audience_location | 210 |    100.3 |  0.1674   |    0.9952 | False           |
|  9 | non-binary · 26-35 · Japan | audience_gender_distribution × audience_age_distribution × audience_location | 228 |    100.3 |  0.09741  |    0.9287 | False           |

---

## 4. O que NÃO funciona?

**Resposta:** 11 de 11 crenças comuns não se sustentam nesta base: Mais seguidores → mais alcance; Mais seguidores → mais engajamento; Mais hashtags → mais alcance; Vídeo engaja mais que imagem/texto; Conteúdo curto (<60) engaja mais; Postar à noite (18–24h) dá mais alcance; Fim de semana dá mais alcance; Patrocínio aumenta alcance; Disclosure explícito derruba engajamento; Legenda longa engaja mais; Mais views → mais likes. Nenhum segmento é significativamente pior em nenhuma plataforma. Investir para mudar um atributo que não altera o resultado (ex.: pagar mais por seguidores, otimizar horário) não traz retorno nesta base.

|    | crença de mercado                        | métrica        |     efeito | unidade        |   p_value |   q_value | se sustenta?   |
|---:|:-----------------------------------------|:---------------|-----------:|:---------------|----------:|----------:|:---------------|
|  0 | Mais seguidores → mais alcance           | views          |  0.004628  | ρ de Spearman  |    0.2903 |    0.5322 | não            |
|  1 | Mais seguidores → mais engajamento       | eng_rate_views | -0.002608  | ρ de Spearman  |    0.5513 |    0.8196 | não            |
|  2 | Mais hashtags → mais alcance             | views          | -0.006172  | ρ de Spearman  |    0.1584 |    0.5322 | não            |
|  3 | Vídeo engaja mais que imagem/texto       | eng_rate_views | -0.03168   | % de diferença |    0.1478 |    0.5322 | não            |
|  4 | Conteúdo curto (<60) engaja mais         | eng_rate_views | -0.01399   | % de diferença |    0.6491 |    0.8196 | não            |
|  5 | Postar à noite (18–24h) dá mais alcance  | views          | -0.01243   | % de diferença |    0.2162 |    0.5322 | não            |
|  6 | Fim de semana dá mais alcance            | views          |  0.01108   | % de diferença |    0.249  |    0.5322 | não            |
|  7 | Patrocínio aumenta alcance               | views          |  0.002854  | % de diferença |    0.7451 |    0.8196 | não            |
|  8 | Disclosure explícito derruba engajamento | eng_rate_views |  0.04454   | % de diferença |    0.1776 |    0.5322 | não            |
|  9 | Legenda longa engaja mais                | eng_rate_views | -0.0004897 | ρ de Spearman  |    0.9109 |    0.9109 | não            |
| 10 | Mais views → mais likes                  | likes          |  0.00149   | ρ de Spearman  |    0.7335 |    0.8196 | não            |

### Pior segmento por plataforma
|    | plataforma   | pior segmento (aparente)             |   índice |   q_value | significativo   |
|---:|:-------------|:-------------------------------------|---------:|----------:|:----------------|
|  0 | Instagram    | lifestyle · mid (50–100K)            |    99.61 |    0.578  | False           |
|  1 | TikTok       | mixed · lifestyle · macro (100–500K) |    99.72 |    0.6738 | False           |
|  2 | YouTube      | image · beauty · mega (500K+)        |    99.74 |    0.7656 | False           |
|  3 | Bilibili     | video · beauty · mid (50–100K)       |    99.68 |    0.6918 | False           |
|  4 | RedNote      | mixed · beauty · mega (500K+)        |    99.85 |    0.8414 | False           |

---

## 1. Onde concentrar esforço?

**Decisão:** Plataforma: nenhuma vence (diferenças ≤ 0.01%), então concentre em 1–2 por custo operacional e presença do público-alvo. Formato: nenhum engaja mais (diferenças ≤ 0.06%), então vale o mais barato de produzir; pela premissa de custo, text, mas a escolha depende do custo real e do formato que cada plataforma comporta. Creators: o porte não muda o engajamento nem as views, então não há motivo para pagar mais por creators grandes. Frequência: dias com mais posts (mediana de 14 por plataforma, somando todos os creators) não têm pior desempenho por post; o limite é a capacidade de produção, e a cadência da marca deve ser medida com os dados dela.

| platform   |     n |    média |   vs. melhor (%) |   p_value |   q_value | equivalente ao melhor   |   vs. melhor (%) (engajamento) | equivalente ao melhor (engajamento)   |
|:-----------|------:|---------:|-----------------:|----------:|----------:|:------------------------|-------------------------------:|:--------------------------------------|
| RedNote    | 10402 | 1.01e+04 |         0        |    1      |         1 | True                    |                       0        | True                                  |
| TikTok     | 10296 | 1.01e+04 |        -0.001891 |    0.8904 |         1 | True                    |                      -0.01881  | True                                  |
| Instagram  | 10423 | 1.01e+04 |        -0.004287 |    0.7538 |         1 | True                    |                      -0.05279  | True                                  |
| Bilibili   | 10598 | 1.01e+04 |        -0.008445 |    0.5363 |         1 | True                    |                      -0.006355 | True                                  |
| YouTube    | 10495 | 1.01e+04 |        -0.009929 |    0.4677 |         1 | True                    |                      -0.03035  | True                                  |

### Formato (engajamento × custo)
| content_type   |     n |   média |   vs. melhor (%) |   p_value |   q_value | equivalente ao melhor   |   custo de produção (US$) |
|:---------------|------:|--------:|-----------------:|----------:|----------:|:------------------------|--------------------------:|
| text           |  5198 |  0.1992 |         0        |   1       |    1      | True                    |                        50 |
| mixed          |  5213 |  0.1991 |        -0.005419 |   0.9099  |    1      | True                    |                       150 |
| image          | 10303 |  0.199  |        -0.056    |   0.1774  |    0.3548 | True                    |                       100 |
| video          | 31500 |  0.199  |        -0.06089  |   0.09482 |    0.3548 | True                    |                       300 |

### Faixa de creator
| follower_tier    |     n |   média |   vs. melhor (%) |   p_value |   q_value | equivalente ao melhor   |   custo mediano patrocinado (US$) |
|:-----------------|------:|--------:|-----------------:|----------:|----------:|:------------------------|----------------------------------:|
| mid (50–100K)    |  2596 |  0.1991 |          0       |    1      |    1      | True                    |                             763.5 |
| micro (10–50K)   |  2110 |  0.1991 |         -0.01287 |    0.8599 |    1      | True                    |                             295.5 |
| macro (100–500K) | 21025 |  0.1991 |         -0.03001 |    0.5556 |    0.9628 | True                    |                            2986   |
| mega (500K+)     | 26029 |  0.199  |         -0.04272 |    0.3965 |    0.9628 | True                    |                            7508   |
| nano (<10K)      |   454 |  0.199  |         -0.07201 |    0.5777 |    0.9628 | True                    |                              55.8 |

### Frequência (saturação por plataforma)
| plataforma   |   posts/dia (mediana) |   ρ volume × resultado |   p_value |   resultado em dias de baixo volume |   resultado em dias de alto volume |   q_value | saturação   |
|:-------------|----------------------:|-----------------------:|----------:|------------------------------------:|-----------------------------------:|----------:|:------------|
| Bilibili     |                    14 |              -0.05467  |   0.1398  |                            1.01e+04 |                           1.01e+04 |    0.3494 | False       |
| Instagram    |                    14 |              -0.04479  |   0.2264  |                            1.01e+04 |                           1.01e+04 |    0.3774 | False       |
| RedNote      |                    14 |              -0.008784 |   0.8126  |                            1.01e+04 |                           1.01e+04 |    0.8126 | False       |
| TikTok       |                    14 |              -0.0653   |   0.07766 |                            1.01e+04 |                           1.01e+04 |    0.3494 | False       |
| YouTube      |                    14 |              -0.01193  |   0.7475  |                            1.01e+04 |                           1.01e+04 |    0.8126 | False       |

**Ações:**
1. Não pagar a mais por formato esperando engajamento: levantar o custo real de produção por formato e usar o mais barato que a plataforma comporta (pela premissa atual, text).
2. Não pagar prêmio por porte de creator: escolher pelo preço por resultado e pelo público-alvo.
3. Concentrar o time em 1–2 plataformas (critério: onde está o cliente-alvo e o menor custo operacional).
4. Aumentar a frequência até o limite da capacidade e reavaliar a saturação mensalmente (`frequency_effect`).

---

## 2. Política de patrocínio

**Decisão:** Patrocinar para ganhar desempenho: não. O patrocínio não muda engajamento nem alcance. Nenhuma condição tem efeito. Regra que vale com qualquer preço: como as views não crescem com os seguidores, um cachê proporcional aos seguidores deixa o creator mega (500K+) ~134x mais caro por mil views que o nano (<10K). Por isso, pagar por resultado, não por post. Com as premissas atuais (US$ 10 por mil seguidores, até US$ 10 por mil views e US$ 0.05 por interação), o post de preço fixo se paga até ~10,050 seguidores; com outros preços o teto vai de 1,000 a 40,400 (tabela de sensibilidade). O desempenho histórico do creator não serve de critério, porque não diferencia creators.

|                                |   diferença |   IC95 inf |   IC95 sup |   diferença (%) |   p_value |   estratos |   q_value |
|:-------------------------------|------------:|-----------:|-----------:|----------------:|----------:|-----------:|----------:|
| eng_rate_views — estratificado |   1.56e-05  | -6.846e-05 |  9.965e-05 |       0.007836  |    0.7161 |        269 |    0.9725 |
| views — estratificado          |   0.4213    | -1.31      |  2.152     |       0.004171  |    0.6334 |        269 |    0.9725 |
| likes — estratificado          |   0.01182   | -0.6593    |  0.683     |       0.0007824 |    0.9725 |        269 |    0.9725 |
| comments_count — estratificado |   0.06128   | -0.1821    |  0.3047    |       0.03064   |    0.6217 |        269 |    0.9725 |
| eng_rate_views — regressão     |  -1.091e-05 | -9.551e-05 |  7.37e-05  |     nan         |    0.8005 |        nan |    0.9725 |

### Ponto de equilíbrio por tamanho de creator
|   seguidores |   custo do post (US$) |   CPM esperado (US$) |   CPE esperado (US$) |   views necessárias p/ CPM-alvo |   engajamento necessário p/ CPE-alvo | vale a pena?   |
|-------------:|----------------------:|---------------------:|---------------------:|--------------------------------:|-------------------------------------:|:---------------|
|         5000 |                50     |                4.95  |              0.02488 |                      5000       |                              0.09901 | True           |
|        10000 |               100     |                9.901 |              0.04975 |                         1e+04   |                              0.198   | True           |
|        25000 |               250     |               24.75  |              0.1244  |                         2.5e+04 |                              0.495   | False          |
|        50000 |               500     |               49.5   |              0.2488  |                         5e+04   |                              0.9901  | False          |
|       100000 |              1000     |               99.01  |              0.4975  |                         1e+05   |                              1.98    | False          |
|       250000 |              2500     |              247.5   |              1.244   |                         2.5e+05 |                              4.95    | False          |
|       500000 |              5000     |              495     |              2.488   |                         5e+05   |                              9.901   | False          |
|      1000000 |                 1e+04 |              990.1   |              4.975   |                         1e+06   |                             19.8     | False          |

### Teto de seguidores por premissa (sensibilidade)
| preço do creator          |   CPM-alvo US$ 5 |   CPM-alvo US$ 10 |   CPM-alvo US$ 20 |
|:--------------------------|-----------------:|------------------:|------------------:|
| US$ 5 por mil seguidores  |         1.01e+04 |          2.02e+04 |          4.04e+04 |
| US$ 10 por mil seguidores |      5000        |          1.01e+04 |          2.02e+04 |
| US$ 20 por mil seguidores |      2500        |       5000        |          1.01e+04 |
| US$ 50 por mil seguidores |      1000        |       2000        |       4000        |

### Perfil de influenciador (patrocinados)
| follower_tier    |   posts |   cpm_mediano |   cpe_mediano |   engajamento | dentro do threshold   |
|:-----------------|--------:|--------------:|--------------:|--------------:|:----------------------|
| nano (<10K)      |     192 |         5.554 |       0.02794 |        0.1992 | True                  |
| micro (10–50K)   |     922 |        29.31  |       0.1469  |        0.1991 | False                 |
| mid (50–100K)    |    1108 |        75.41  |       0.379   |        0.1991 | False                 |
| macro (100–500K) |    8968 |       296.4   |       1.485   |        0.1991 | False                 |
| mega (500K+)     |   11124 |       744.3   |       3.738   |        0.199  | False                 |

### Condições testadas
|    | condição                         |   uplift engajamento (%) |   p_value |   q_value | significativo   |
|---:|:---------------------------------|-------------------------:|----------:|----------:|:----------------|
|  6 | follower_tier = micro (10–50K)   |                  0.1606  |   0.1326  |    0.479  | False           |
|  7 | follower_tier = mid (50–100K)    |                  0.1393  |   0.1382  |    0.479  | False           |
| 16 | content_category = tech          |                  0.123   |   0.01003 |    0.1705 | False           |
| 11 | content_type = mixed             |                  0.08652 |   0.2009  |    0.5693 | False           |
|  1 | platform = Instagram             |                  0.0495  |   0.3157  |    0.5963 | False           |
|  2 | platform = RedNote               |                  0.04947 |   0.3075  |    0.5963 | False           |
| 12 | content_type = text              |                  0.04297 |   0.518   |    0.629  | False           |
| 10 | content_type = image             |                  0.03779 |   0.4384  |    0.629  | False           |
|  4 | platform = YouTube               |                  0.02765 |   0.5551  |    0.6292 | False           |
|  8 | follower_tier = macro (100–500K) |                  0.0249  |   0.4649  |    0.629  | False           |
| 15 | content_category = lifestyle     |                  0.02258 |   0.5115  |    0.629  | False           |
|  0 | platform = Bilibili              |                 -0.01546 |   0.7468  |    0.7934 | False           |

**Ações:**
1. Contratar por resultado: até US$ 10 por mil views ou US$ 0.05 por interação, em vez de preço fixo por post (vale com qualquer cachê).
2. Enquanto o preço for fixo por post: teto de ~10,050 seguidores (sai das premissas; recalcular com o cachê real).
3. Exigir rótulo de publicidade verificável no próprio texto (#publi/#ad): hoje 47% dos patrocinados usam disclosure implícito (risco regulatório alto) e só 2.3% mostram o rótulo no texto; o tipo de disclosure não muda o engajamento.
4. Todo novo patrocínio entra com grupo de comparação (posts orgânicos parecidos, ≥ 30 por grupo) para medir o ganho real.

---

## 3. O que parar de fazer

**Decisão:** Parar de pagar preço fixo por seguidores: as views não acompanham o porte. Pelas premissas de preço, 99% dos posts patrocinados ficam acima do teto e 98% do gasto implícito com patrocínio é excedente sobre o preço justo (~US$ 109 mi neste histórico; valor ilustrativo, não contábil). Parar de pagar a mais por formatos caros esperando engajamento: nenhum formato engaja mais. Parar de usar como regra geral 11 práticas testadas sem efeito (horário, hashtags, legenda, duração...).

| investimento                                                   |       posts |   % dos patrocinados |   gasto implícito (US$) |   excedente sobre preço justo (US$) | evidência                                      |
|:---------------------------------------------------------------|------------:|---------------------:|------------------------:|------------------------------------:|:-----------------------------------------------|
| Patrocínio acima de 10,050 seguidores                          |   2.212e+04 |                99.14 |               1.115e+08 |                           1.093e+08 | views e engajamento não crescem com seguidores |
| Formatos mais caros que text sem ganho                         |   4.702e+04 |               nan    |               1.152e+07 |                           8.911e+06 | engajamento equivalente entre formatos         |
| Otimizar com base em: Mais seguidores → mais alcance           | nan         |               nan    |             nan         |                         nan         | efeito nulo (q ≥ 0,05)                         |
| Otimizar com base em: Mais seguidores → mais engajamento       | nan         |               nan    |             nan         |                         nan         | efeito nulo (q ≥ 0,05)                         |
| Otimizar com base em: Mais hashtags → mais alcance             | nan         |               nan    |             nan         |                         nan         | efeito nulo (q ≥ 0,05)                         |
| Otimizar com base em: Vídeo engaja mais que imagem/texto       | nan         |               nan    |             nan         |                         nan         | efeito nulo (q ≥ 0,05)                         |
| Otimizar com base em: Conteúdo curto (<60) engaja mais         | nan         |               nan    |             nan         |                         nan         | efeito nulo (q ≥ 0,05)                         |
| Otimizar com base em: Postar à noite (18–24h) dá mais alcance  | nan         |               nan    |             nan         |                         nan         | efeito nulo (q ≥ 0,05)                         |
| Otimizar com base em: Fim de semana dá mais alcance            | nan         |               nan    |             nan         |                         nan         | efeito nulo (q ≥ 0,05)                         |
| Otimizar com base em: Patrocínio aumenta alcance               | nan         |               nan    |             nan         |                         nan         | efeito nulo (q ≥ 0,05)                         |
| Otimizar com base em: Disclosure explícito derruba engajamento | nan         |               nan    |             nan         |                         nan         | efeito nulo (q ≥ 0,05)                         |
| Otimizar com base em: Legenda longa engaja mais                | nan         |               nan    |             nan         |                         nan         | efeito nulo (q ≥ 0,05)                         |

### Crenças testadas
|    | crença de mercado                        | métrica        |     efeito | unidade        |   p_value |   q_value | se sustenta?   |
|---:|:-----------------------------------------|:---------------|-----------:|:---------------|----------:|----------:|:---------------|
|  0 | Mais seguidores → mais alcance           | views          |  0.004628  | ρ de Spearman  |    0.2903 |    0.5322 | não            |
|  1 | Mais seguidores → mais engajamento       | eng_rate_views | -0.002608  | ρ de Spearman  |    0.5513 |    0.8196 | não            |
|  2 | Mais hashtags → mais alcance             | views          | -0.006172  | ρ de Spearman  |    0.1584 |    0.5322 | não            |
|  3 | Vídeo engaja mais que imagem/texto       | eng_rate_views | -0.03168   | % de diferença |    0.1478 |    0.5322 | não            |
|  4 | Conteúdo curto (<60) engaja mais         | eng_rate_views | -0.01399   | % de diferença |    0.6491 |    0.8196 | não            |
|  5 | Postar à noite (18–24h) dá mais alcance  | views          | -0.01243   | % de diferença |    0.2162 |    0.5322 | não            |
|  6 | Fim de semana dá mais alcance            | views          |  0.01108   | % de diferença |    0.249  |    0.5322 | não            |
|  7 | Patrocínio aumenta alcance               | views          |  0.002854  | % de diferença |    0.7451 |    0.8196 | não            |
|  8 | Disclosure explícito derruba engajamento | eng_rate_views |  0.04454   | % de diferença |    0.1776 |    0.5322 | não            |
|  9 | Legenda longa engaja mais                | eng_rate_views | -0.0004897 | ρ de Spearman  |    0.9109 |    0.9109 | não            |
| 10 | Mais views → mais likes                  | likes          |  0.00149   | ρ de Spearman  |    0.7335 |    0.8196 | não            |

**Ações:**
1. Congelar renovações por preço fixo acima do teto até renegociar por resultado.
2. Formatos caros só com motivo de marca ou teste A/B aprovado, não por expectativa de engajamento.
3. Tirar "melhor horário", "número ideal de hashtags" e "legenda longa" do checklist como regra geral; horário só por plataforma e depois de teste (ver fila de testes).

---

## 4. Quick wins (esta semana)

**Decisão:** 6 ações para esta semana, sem contratação nem ferramenta nova. As 4 primeiras valem também com os dados reais da empresa; as 2 últimas dependem das premissas de preço e devem ser recalculadas com os preços reais.

|    | ação                                                                                | base                                              | esforço                 | impacto                                                                                                                                                        | dono                  |
|---:|:------------------------------------------------------------------------------------|:--------------------------------------------------|:------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------------|
|  0 | Novos contratos e renovações por resultado (views ou interações), não por post      | robusta (vale com dados reais)                    | médio                   | o custo por view deixa de crescer com o porte (hoje o maior porte paga ~134x mais por mil views)                                                               | Parcerias / Compras   |
|  1 | Rótulo de publicidade verificável no texto (#publi/#ad) como padrão                 | robusta (vale com dados reais)                    | baixo                   | hoje 47% dos patrocinados usam disclosure implícito (risco regulatório alto) e só 2.3% mostram o rótulo no texto; o tipo de disclosure não muda o engajamento. | Social media          |
|  2 | Todo patrocínio novo com grupo de comparação orgânico                               | robusta (vale com dados reais)                    | baixo                   | mede o ganho real; ≥ 30 posts por grupo para ver +5% de engajamento                                                                                            | AI Master / Analytics |
|  3 | Não pagar a mais por creator "campeão" e tirar horário/hashtags ideais do checklist | robusta (vale com dados reais)                    | baixo                   | desempenho passado e essas regras não mudam o resultado; horas do time liberadas                                                                               | Social media          |
|  4 | Teto de ~10,050 seguidores para contratos de preço fixo                             | depende de premissa (recalcular com preços reais) | baixo (regra de compra) | pelas premissas, 98% do gasto implícito com patrocínio é excedente                                                                                             | Head de Marketing     |
|  5 | Formato padrão pelo custo real de produção (pela premissa, text)                    | depende de premissa (recalcular com preços reais) | baixo                   | mesmo engajamento com menor custo por post                                                                                                                     | Conteúdo              |

### Base: onde concentrar
|    | decisão                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|---:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  0 | Plataforma: nenhuma vence (diferenças ≤ 0.01%), então concentre em 1–2 por custo operacional e presença do público-alvo. Formato: nenhum engaja mais (diferenças ≤ 0.06%), então vale o mais barato de produzir; pela premissa de custo, text, mas a escolha depende do custo real e do formato que cada plataforma comporta. Creators: o porte não muda o engajamento nem as views, então não há motivo para pagar mais por creators grandes. Frequência: dias com mais posts (mediana de 14 por plataforma, somando todos os creators) não têm pior desempenho por post; o limite é a capacidade de produção, e a cadência da marca deve ser medida com os dados dela. |

**Ações:**
1. Novos contratos e renovações por resultado (views ou interações), não por post
2. Rótulo de publicidade verificável no texto (#publi/#ad) como padrão
3. Todo patrocínio novo com grupo de comparação orgânico
4. Não pagar a mais por creator "campeão" e tirar horário/hashtags ideais do checklist
5. Teto de ~10,050 seguidores para contratos de preço fixo
6. Formato padrão pelo custo real de produção (pela premissa, text)

---

## 5. Fila de testes

**Decisão:** Só 3 hipóteses merecem teste; o resto das variações encontradas está no nível do acaso. Nenhuma vira regra antes do teste: os números de posts mostram o custo de confirmar cada uma.

|   # | tipo       | hipótese                                                      | evidência                                                                                                                                                           |   posts por grupo | como tratar                                         |
|----:|:-----------|:--------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------:|:----------------------------------------------------|
|   1 | bolsão     | TikTok · beauty · Spanish aumenta a chance de top 5% em likes | 10.0% vs. 4.9% (2.0x), nos 2 anos; q global = 0.035 entre 14,763 testes                                                                                             |              1430 | teste A/B                                           |
|   2 | horário    | YouTube: posts até 12h entram mais no top 1% de comentários   | 1.45% vs. 0.85%; hora típica do top 9h vs. 12h (q = 0.02)                                                                                                           |             17049 | acompanhar no histórico (A/B exigiria posts demais) |
|   3 | patrocínio | Patrocínio aumenta o engajamento em pelo menos 5%             | nenhum efeito neste histórico; aqui as métricas variam só ~1% entre posts, por isso bastam poucos posts (mínimo prático); com os dados da empresa a conta é refeita |                30 | teste A/B                                           |

### Brief do teste 1
| campo               | valor                                                                                                                       |
|:--------------------|:----------------------------------------------------------------------------------------------------------------------------|
| Grupos              | beauty · Spanish no TikTok (teste) × o mesmo conteúdo em English (controle)                                                 |
| Formato             | video (61% do segmento); o mesmo nos dois grupos                                                                            |
| Faixa de creator    | nano (<10K) (menor custo por mil views); a mesma nos dois grupos                                                            |
| Público-alvo        | Japan (15% do segmento) e 19-25 anos (36%): os mais frequentes                                                              |
| Horário             | sem evidência de horário para likes no TikTok (q = 0.97): distribuir os horários igualmente entre os grupos                 |
| Duração             | ~172 segundos (mediana do segmento); a duração não mudou o resultado em nenhum formato                                      |
| Critério de sucesso | taxa de top 5% em likes ≥ 7.5% no grupo Spanish (resto do TikTok: 4.9%), p < 0.05, com 1,430 posts por grupo (poder de 80%) |

**Ações:**
1. TikTok · beauty · Spanish aumenta a chance de top 5% em likes: teste A/B; 1,430 posts por grupo.
2. YouTube: posts até 12h entram mais no top 1% de comentários: acompanhar no histórico (A/B exigiria posts demais); 17,049 posts por grupo.
3. Patrocínio aumenta o engajamento em pelo menos 5%: teste A/B; 30 posts por grupo.

---

## 6. Provas do resumo executivo

**Resposta:** Medida por seguidor, o nano (<10K) parece ~138x melhor que o mega (500K+) (0.368 × 0.0027). É efeito da conta: por view, todas as faixas ficam em ~0.199, com ~10,100 views medianas. 0 posts com zero em views, likes, compartilhamentos ou comentários (mínimo de 1,354 likes; views de 9,676 a 10,551): a base não tem posts que fracassaram. Engajamento médio entre 0.1990 e 0.1991 nos 9 trimestres (2023Q2 a 2025Q2; p = 0.99): estável, sem sazonalidade.

|    | o que a IA diria                                                                                           | o que os dados mostram                                                  | veredito                                                                 |
|---:|:-----------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------|:-------------------------------------------------------------------------|
|  0 | Bilibili · video · lifestyle · micro (10–50K) é o segmento que mais engaja: concentre o investimento nele. | índice 100.5 (média = 100), n = 109, p = 0.02, q = 0.88                 | maior diferença bruta entre centenas de segmentos; some após a correção  |
|  1 | Creators maiores entregam mais alcance: priorize macro e mega.                                             | ρ = 0.005 (views), q = 0.53                                             | não se sustenta                                                          |
|  2 | Vídeo é o formato que mais engaja: migre o mix para vídeo.                                                 | -0.03% (eng_rate_views), q = 0.53                                       | não se sustenta                                                          |
|  3 | Publique à noite (18–24h), quando o alcance é maior.                                                       | -0.01% (views), q = 0.53                                                | não se sustenta                                                          |
|  4 | TikTok · beauty · Spanish aumenta a chance de top 5% em likes.                                             | 10.0% vs. 4.9% (2.0x), nos 2 anos; q global = 0.035 entre 14,763 testes | único que passou no filtro: vai para teste A/B com 1,430 posts por grupo |

### Engajamento por seguidor × por view, por faixa de creator
| follower_tier    |        posts |   interações por seguidor (mediana) |   interações por view (mediana) |   views (mediana) |
|:-----------------|-------------:|------------------------------------:|--------------------------------:|------------------:|
| nano (<10K)      |  454         |                            0.3683   |                          0.1988 |         1.009e+04 |
| micro (10–50K)   | 2110         |                            0.06649  |                          0.199  |         1.01e+04  |
| mid (50–100K)    | 2596         |                            0.02661  |                          0.1991 |         1.01e+04  |
| macro (100–500K) |    2.102e+04 |                            0.006698 |                          0.199  |         1.01e+04  |
| mega (500K+)     |    2.603e+04 |                            0.002676 |                          0.1989 |         1.01e+04  |

### Posts sem resultado (survivorship)
|                |   posts com zero |   mínimo |   máximo |
|:---------------|-----------------:|---------:|---------:|
| views          |                0 |     9676 |    10551 |
| likes          |                0 |     1354 |     1668 |
| shares         |                0 |      227 |      380 |
| comments_count |                0 |      140 |      258 |

### Engajamento por trimestre
| trimestre   |   posts |   engajamento |
|:------------|--------:|--------------:|
| 2023Q2      |    2429 |        0.199  |
| 2023Q3      |    6546 |        0.1991 |
| 2023Q4      |    6531 |        0.1991 |
| 2024Q1      |    6501 |        0.1991 |
| 2024Q2      |    6481 |        0.199  |
| 2024Q3      |    6715 |        0.1991 |
| 2024Q4      |    6591 |        0.1991 |
| 2025Q1      |    6273 |        0.199  |
| 2025Q2      |    4147 |        0.1991 |