# Segmentação de audiência com clustering

Gerado por `solution/scripts/audience_clustering.py` (mesmo cálculo da aba *Agrupamento de audiência* do site).

## Todas as plataformas

160 perfis, 2 grupos — **não se sustentam**
(separação 0.28 vs. acaso até 0.45; estabilidade 0.03).

| grupo   |   perfis | posts   | traço do público                       | consome mais                                                                          |
|:--------|---------:|:--------|:---------------------------------------|:--------------------------------------------------------------------------------------|
| A       |      133 | 95%     | gender_distribution=female (+6%)       | language=Japanese (+3%), content_type=image (+3%), platform=RedNote (+2%)             |
| B       |       27 | 5%      | gender_distribution=non-binary (+352%) | language=Spanish (+18%), platform=Instagram (+18%), content_category=lifestyle (+12%) |

## Instagram

122 perfis, 2 grupos — **não se sustentam**
(separação 0.11 vs. acaso até 0.15; estabilidade 0.02).

| grupo   |   perfis | posts   | traço do público              | consome mais                                                                   |
|:--------|---------:|:--------|:------------------------------|:-------------------------------------------------------------------------------|
| A       |       78 | 68%     | age_distribution=26-35 (+18%) | language=Japanese (+6%), content_type=video (+6%), content_category=tech (+5%) |
| B       |       44 | 32%     | location=India (+39%)         | content_type=mixed (+22%), content_type=image (+19%), language=Hindi (+18%)    |

## TikTok

127 perfis, 2 grupos — **não se sustentam**
(separação 0.09 vs. acaso até 0.16; estabilidade -0.00).

| grupo   |   perfis | posts   | traço do público       | consome mais                                                                   |
|:--------|---------:|:--------|:-----------------------|:-------------------------------------------------------------------------------|
| A       |       71 | 56%     | location=USA (+33%)    | language=Japanese (+14%), content_type=video (+7%), language=Chinese (+5%)     |
| B       |       56 | 44%     | location=Russia (+58%) | content_type=image (+16%), content_type=text (+13%), content_type=mixed (+11%) |

## YouTube

124 perfis, 2 grupos — **não se sustentam**
(separação 0.11 vs. acaso até 0.17; estabilidade 0.02).

| grupo   |   perfis | posts   | traço do público      | consome mais                                                                    |
|:--------|---------:|:--------|:----------------------|:--------------------------------------------------------------------------------|
| A       |       76 | 71%     | location=China (+15%) | language=English (+8%), content_category=beauty (+7%), content_type=mixed (+4%) |
| B       |       48 | 29%     | location=USA (+77%)   | language=Chinese (+16%), language=Japanese (+13%), language=Hindi (+10%)        |

## Bilibili

128 perfis, 2 grupos — **não se sustentam**
(separação 0.11 vs. acaso até 0.23; estabilidade -0.00).

| grupo   |   perfis | posts   | traço do público       | consome mais                                                                      |
|:--------|---------:|:--------|:-----------------------|:----------------------------------------------------------------------------------|
| A       |       78 | 63%     | location=Russia (+26%) | language=Japanese (+8%), content_category=lifestyle (+6%), language=English (+4%) |
| B       |       50 | 37%     | location=UK (+44%)     | language=Hindi (+29%), language=Chinese (+12%), content_type=image (+12%)         |

## RedNote

128 perfis, 2 grupos — **não se sustentam**
(separação 0.13 vs. acaso até 0.14; estabilidade -0.00).

| grupo   |   perfis | posts   | traço do público                  | consome mais                                                                |
|:--------|---------:|:--------|:----------------------------------|:----------------------------------------------------------------------------|
| A       |       84 | 72%     | gender_distribution=female (+14%) | content_type=image (+10%), language=Chinese (+10%), language=Hindi (+9%)    |
| B       |       44 | 28%     | location=UK (+74%)                | language=Japanese (+12%), language=English (+11%), content_type=video (+8%) |
