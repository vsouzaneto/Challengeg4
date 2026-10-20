# Duração do vídeo × views — achados

Fonte: `solution/notebooks/09_duracao_views.ipynb` · figuras para o site: `docs/figures/duracao_x_views_hist2d.png` e `docs/figures/views_por_faixa_de_duracao.png` · 2026-10-19.
Base: 31.500 vídeos (`content_type == "video"`), duração = `content_length` (10–599 s).

## Manchete
**A duração do vídeo não muda as views.** Vídeos de 10 s e de 10 min têm a mesma mediana (~10.100 views).

## Números
| Faixa | Vídeos | Mínimo | Média | Mediana | Máximo |
|---|---|---|---|---|---|
| curto (<60 s) | 4.344 | 9.751 | 10.099,8 | 10.099 | 10.483 |
| médio (60–180 s) | 11.974 | 9.717 | 10.100,7 | 10.100 | 10.491 |
| longo (180–360 s) | 7.265 | 9.725 | 10.100,9 | 10.102 | 10.474 |
| muito longo (360+ s) | 7.917 | 9.748 | 10.099,7 | 10.100 | 10.477 |

**Máximos e mínimos por faixa de 30 s:** máximo entre 10.399 e 10.491, mínimo entre 9.717 e 9.809, sem tendência com a duração.
A amplitude (máx − mín) acompanha o **nº de vídeos da faixa** (ρ = +0,58, p = 0,008): faixas abaixo de 200 s têm ~3x mais vídeos e, por isso, extremos mais abertos (mais sorteios → extremos mais distantes). O "vídeo recordista" e o "pior vídeo" são acaso, não efeito da duração.

Spearman duração × views ρ = +0,001 (p = 0,83) · Kruskal entre faixas p = 0,83 · < 200 s vs. ≥ 200 s: 10.100,2 vs. 10.100,5 (p = 0,79).

## Forma da duração (descoberta sobre o dado)
- 58% dos vídeos ficam entre ~20 e 200 s, com ~2,9x mais vídeos por segundo de duração que acima de 200 s. Entre 200 e 600 s, a distribuição é plana.
- A **mesma forma** aparece em imagem, texto e misto (quartis ~95 / 174 / 359 em todos os formatos), então `content_length` não é uma duração real por formato.

## "Mais picos entre 20 e 150 s?" (questão levantada na análise visual)
Figura: `docs/figures/picos_por_duracao.png` (3 painéis).
- **Contagem:** sim, há mais vídeos no top 5% entre 30 e 180 s (134–166 por faixa de 30 s, contra 34–60 acima de 200 s), porque essas faixas têm ~3x mais vídeos.
- **Taxa por vídeo:** igual. Entre 20 e 150 s, 4,9% chegam ao top 5%, contra 5,1% nas demais (p = 0,50). No top 1%, 0,98% contra 1,04% (p = 0,66). Qui² entre as 20 faixas p = 0,27; tendência com a duração p = 0,79.
- **Máximos:** caem dentro do esperado só pelo nº de vídeos (sorteio da distribuição geral: ~10.450 para faixas com ~3.000 vídeos e ~10.420 para ~950). Com amostras do mesmo tamanho, a diferença (+14,5 views) não é significativa (permutação p = 0,24).
- **Ressalva:** acima de 480 s, a taxa de picos é um pouco menor (4,1% vs. 5,2%; p = 0,007 isolado), mas a janela foi escolhida depois de ver o gráfico, e os testes pré-definidos não acusam nada. Fica como **hipótese a confirmar com dados novos**.
- **Mensagem para o site:** "mais picos" na contagem ≠ "mais chance de pico". Decisões devem usar a **taxa por vídeo**.

## Leitura dos gráficos (para legenda no site)
- **Histograma 2D:** a mancha escura à esquerda é **quantidade de vídeos, não mais views**. A linha de mediana é reta, e as linhas de máximo (roxo) e mínimo (verde) oscilam sem tendência.
- **Histogramas por faixa:** as 4 curvas de views se sobrepõem.

## Recomendação
Escolher a duração por **custo de produção e formato nativo da plataforma**, não por alcance esperado.

## Como reproduzir
`.venv/bin/jupyter nbconvert --to notebook --execute --inplace solution/notebooks/09_duracao_views.ipynb` (regera as figuras em `docs/figures/`).
