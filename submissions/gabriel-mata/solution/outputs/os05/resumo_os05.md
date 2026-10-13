# OS-05 — Gráficos para os relatórios

Script: `solution/analysis/os05_graficos.py`
Fonte: `datasets/social_media_dataset.csv` (52.214 posts), mais as saídas da OS-02 e da OS-03c
Saídas: `solution/outputs/os05/` (4 arquivos .png)

**Padrão visual dos 4 gráficos:** matplotlib, PNG, 150 dpi, 10 × 6 polegadas, fundo branco, fonte de 11 pt para cima, grade horizontal leve, textos em português e números com vírgula decimal. Duas cores: cinza `#9A9A9A` para o padrão e vermelho `#C0392B` para o destaque. Os títulos e rótulos são os textos fixos da OS, sem alteração.

| Arquivo | Origem dos dados |
|---|---|
| `grafico_01_engajamento_por_faixa.png` | recalculado do CSV (Bloco 5 da OS-03) |
| `grafico_02_segmentos_vs_limite.png` | `solution/outputs/os02/nivel1.csv` a `nivel4.csv` |
| `grafico_03_controle_positivo.png` | recalculado do CSV (Nível 4 da OS-02 + sorteio do Bloco 3b da OS-03c) |
| `grafico_04_efeito_maximo.png` | `solution/outputs/os03c/bloco1_equivalencia.csv` |

---

## 1. `grafico_01_engajamento_por_faixa.png`

Média de `engajamento` (likes + shares + comments_count) por faixa de seguidores × `is_sponsored`, recalculada do CSV com a lógica do Bloco 5 da OS-03. Barras agrupadas (orgânico em cinza, patrocinado em vermelho), IC 95% bootstrap (1.000 reamostragens, seed 42) como barra de erro, eixo Y de 0 a 2.350.

| Faixa de seguidores | Grupo | n | Média | IC 95% inferior | IC 95% superior |
|---|---|---|---|---|---|
| até 50K | Orgânico | 1.450 | 2.009,96 | 2.007,64 | 2.012,38 |
| até 50K | Patrocinado | 1.114 | 2.010,84 | 2.008,35 | 2.013,60 |
| 50–100K | Orgânico | 1.488 | 2.010,78 | 2.008,52 | 2.013,09 |
| 50–100K | Patrocinado | 1.109 | 2.010,35 | 2.007,62 | 2.013,24 |
| 100–500K | Orgânico | 12.057 | 2.010,02 | 2.009,26 | 2.010,84 |
| 100–500K | Patrocinado | 8.967 | 2.010,63 | 2.009,73 | 2.011,58 |
| 500K–1M | Orgânico | 14.905 | 2.010,58 | 2.009,90 | 2.011,26 |
| 500K–1M | Patrocinado | 11.124 | 2.009,92 | 2.009,05 | 2.010,79 |

Rótulo escrito sobre cada barra, sem casas decimais, na ordem do eixo X: 2.010, 2.011, 2.011, 2.010, 2.010, 2.011, 2.011, 2.010.

## 2. `grafico_02_segmentos_vs_limite.png`

Lifts de `taxa_engajamento` dos 693 segmentos dos níveis 1 a 4 da OS-02, lidos dos .csv de `solution/outputs/os02/`. Um ponto cinza por segmento numa faixa horizontal, com dispersão vertical uniforme em [−0,33; 0,33] (seed 42) para não sobrepor. Faixa sombreada entre 0,90 e 1,10 e eixo X de 0,85 a 1,15, rotulado de −15% a +15%.

| Item | Valor |
|---|---|
| Segmentos por nível (1 / 2 / 3 / 4) | 52 / 260 / 253 / 128 |
| Total de segmentos | 693 |
| Menor lift | 0,995435 (−0,46%) |
| Maior lift | 1,004772 (+0,48%) |
| Maior desvio absoluto vs. a média | 0,4772% |
| Segmentos fora de ±2% | 0 |
| Segmentos fora de ±10% (faixa sombreada) | 0 |

## 3. `grafico_03_controle_positivo.png`

Busca do Nível 4 da OS-02 (platform × content_type × content_category × faixa_seguidores, n ≥ 100, `taxa_engajamento`) recalculada do CSV em dois cenários: sem injeção e com +5% no segmento sorteado. 240 segmentos existentes, 128 no ranking. Segmento da injeção: `Bilibili | video | beauty | 50-100K` (n = 137), reproduzido com o sorteio do Bloco 3b da OS-03c (seed 42). Linha tracejada no p95 do maior lift por acaso (200 permutações dentro da plataforma, seed 42). Os dois painéis compartilham o eixo Y (−1% a +6%).

| Painel | Lift do segmento sorteado | Posição | p95 do maior lift por acaso |
|---|---|---|---|
| Dados originais | 0,996816 (−0,32%) | 128º de 128 | 1,006675 (+0,67%) |
| Com +5% inserido em um segmento | 1,045982 (+4,60%) | 1º de 128 | 1,006690 (+0,67%) |

Faixa dos 128 lifts no painel 1: 0,996816 a 1,004772. No painel 2: 0,997221 a 1,045982.

## 4. `grafico_04_efeito_maximo.png`

Maior efeito máximo plausível (%) entre os segmentos de cada variável, só para `taxa_engajamento`, lido de `solution/outputs/os03c/bloco1_equivalencia.csv`. Barras horizontais cinza ordenadas da maior para a menor, valor ao lado com 2 casas decimais, eixo X de 0 a 1,2% e linha tracejada vermelha em 1%.

| Variável (rótulo do gráfico) | Coluna de origem | Efeito máximo plausível |
|---|---|---|
| Idade da audiência | `audience_age_distribution` | 0,1292% |
| Faixa de seguidores | `faixa_seguidores` | 0,1272% |
| País da audiência | `audience_location` | 0,1151% |
| Formato | `content_type` | 0,1106% |
| Plataforma | `platform` | 0,0796% |
| Categoria | `content_category` | 0,0706% |
| Gênero da audiência | `audience_gender_distribution` | 0,0701% |
| Patrocínio | `is_sponsored` | 0,0350% |

---

## Pontos suspeitos ou problemas encontrados

1. **Gráfico 1 — as 8 barras são visualmente idênticas.** As médias ficam entre 2.009,9 e 2.010,8 interações: amplitude de 0,9 interação (0,05%). O IC 95% mais largo mede 5,6 interações, cerca de 0,24% da altura do eixo — as barras de erro saem do tamanho de um traço e praticamente não aparecem no PNG. É o que os números mostram, nada foi ajustado.

2. **Gráfico 1 — IC levemente diferentes dos do Bloco 5 da OS-03.** As 8 médias e os 8 n batem casa a casa com `solution/outputs/os03/bloco5_engajamento_por_faixa.csv`. Os IC mudam na 1ª ou 2ª casa decimal (ex.: faixa até 50K patrocinado, 2.008,35–2.013,60 aqui contra 2.008,21–2.013,48 na OS-03) porque na OS-03 o gerador seed 42 já tinha sido consumido pelos Blocos 1 a 4 antes do Bloco 5, e aqui ele começa do zero. Mesma lógica, mesmo número de reamostragens; só o fluxo de números aleatórios é outro.

3. **Gráfico 2 — o título fixo confere.** São 693 segmentos (níveis 1 a 4, métrica `taxa_engajamento`). O maior desvio absoluto vs. a média da plataforma é 0,4772%: 0 segmentos passam de ±2% e 0 passam de ±10%. Consequência visual: dentro de um eixo de −15% a +15%, os 693 pontos viram uma mancha estreita sobre o 0% e a faixa sombreada fica vazia.

4. **Gráfico 3 — reprodução confere, com uma diferença esperada no p95.** O sorteio do Bloco 3b foi refeito e caiu no mesmo segmento (`Bilibili | video | beauty | 50-100K`, n = 137, entre 29 candidatos), o lift com +5% deu 1,045982 — igual ao do `bloco3b_injecao_na_busca.csv` da OS-03c — e as posições saíram 128º e 1º de 128. O p95 do acaso sem injeção deu 1,006675 aqui contra 1,006406 no `teste_acaso.csv` da OS-02 (0,03% de diferença): mesma lógica e mesmas 200 permutações, mas na OS-02 o gerador seed 42 chega nesse teste em outro ponto do fluxo e o nível 4 era avaliado junto com as outras métricas. A posição da linha tracejada não muda no olho.

5. **Gráfico 4 — o título fixo confere.** O maior efeito máximo plausível é 0,1292% (Idade da audiência) e 0 variáveis passam de 0,15%. Consequência visual: com o eixo de 0 a 1,2%, as 8 barras ocupam no máximo um oitavo da largura e a linha de 1% fica isolada à direita.

