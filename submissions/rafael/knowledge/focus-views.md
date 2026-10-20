# Foco: 4 relações com views — achados e como usar

Fonte: `solution/src/social_insights/focus.py` · notebook: `solution/notebooks/06_foco_views.ipynb` · gerado em 2026-10-18 sobre 52.214 posts.
Formato para o site: manchete, números-chave, gráfico sugerido.

> **Conceito-chave para o site: efeito mínimo detectável (MDE).** É o menor efeito que os dados encontrariam com 80% de chance (α = 5%).
> Se o MDE é pequeno e nada aparece, a ausência de efeito é **comprovada**, não falta de dados. Aqui o MDE é de ~3 views (0,03%), enquanto um efeito de negócio relevante (5%) seria de ~505 views, ou seja, **~150–200x maior** que o detectável.

## Síntese

| Relação | Efeito observado | Detectável a partir de | Conclusão |
|---|---|---|---|
| `content_category` × views | 1,6 views (máx. entre categorias, 0,015%) | 3,4 views | sem efeito (comprovado) |
| `content_description` × views | \|ρ\| ≤ 0,002; R² do modelo de texto = −0,0009 | ρ = 0,012 | sem efeito; texto sem semântica |
| `follower_count` × views | ρ = 0,005; elasticidade 0,0001 | ρ = 0,012 | sem efeito (atípico vs. redes reais) |
| `is_sponsored` × views | +0,3 views (+0,003%) | 2,5 views | sem efeito (comprovado) |

## 1. Categoria × views
- **Manchete:** beauty, lifestyle e tech alcançam o mesmo público.
- **Números:** médias 10.099,9 / 10.100,0 / 10.101,5 (IC95 sobrepostos); medianas 10.100 / 10.100 / 10.102; Kruskal p = 0,27; ε² = 0,00005; pares com q ≥ 0,32. Dentro de cada plataforma, ±0,03%.
- **Gráfico:** média ± IC95 por categoria com faixa de ±5% sombreada (tudo cabe dentro dela) + heatmap plataforma × categoria.

## 2. Legenda (`content_description`) × views — NLP
- **Manchete:** nem o tamanho, nem o tom, nem as palavras da legenda mudam as views.
- **Números:** tamanho (palavras/caracteres) e sentimento VADER com |ρ| ≤ 0,002 (p ≥ 0,72); 0 palavras significativas entre top e bottom 10% (maior |z| = 1,8 < 1,96); TF-IDF (5 mil termos, uni e bigramas) + Ridge: R² = −0,0009.
- **Descoberta sobre o dado:** as legendas são frases aleatórias geradas (ex.: *"Professional radio usually something letter half pattern…"*), sem relação com a categoria. Nenhuma tem "?" ou "!".
- **Gráfico:** hexbin palavras × views com mediana por quintil; média ± IC por tom; barras de z das palavras com linhas de ±1,96.

## 3. Seguidores × views
- **Manchete:** um creator de 1 mil e um de 1 milhão têm a mesma mediana de views (~10.100).
- **Números:** ρ = 0,0046 (MDE 0,012); +0,17 views por +100 mil seguidores (IC95 −0,13 a +0,47); elasticidade 0,0001 (dobrar a base = +0,004% de views). Views por seguidor: de ~10 (nano) a ~0,01 (mega).
- **Contraste:** em redes reais, a elasticidade costuma ficar entre 0,5 e 1. Com 0,7, 100x mais seguidores dariam ~25x mais views; aqui dão 0x.
- **Implicação:** pagar por seguidores é pagar por algo que não vira alcance (ver threshold em `strategy-recommendations.md`).
- **Gráfico:** hexbin seguidores × views com mediana por decil + gráfico log-log "observado (plano) × esperado numa rede real (inclinado)".

## 4. Patrocínio × views
- **Manchete:** post patrocinado alcança o mesmo que o orgânico.
- **Números:** bruta +0,3 views (+0,003%, IC95 −1,4 a +2,0, p = 0,75); estratificada (plataforma × formato × categoria × porte) +0,4 views (p = 0,63); MDE 2,5 views. 0 de 21 condições (porte, plataforma, categoria, patrocinador, disclosure) com efeito após correção; maior ponto: TikTok +3,8 views (q = 0,95).
- **Gráfico:** histogramas sobrepostos (as curvas coincidem) + forest plot das 21 condições.

## Mensagem para o site
"A impressão de que os dados não trazem insight está correta e agora está **quantificada**: tínhamos poder para ver efeitos 150x menores que qualquer efeito relevante, e não há nenhum. O insight de negócio é que **tema, legenda, tamanho do creator e patrocínio não compram alcance**, então a decisão deve ser por custo."

> Por que o MDE é tão pequeno? As views quase não variam (desvio de 100 em 10.100, 1%). Em dados reais, a variação costuma passar de 100%, e o MDE cresce na mesma proporção. As funções calculam isso automaticamente.

---

## Como utilizar
```python
import sys; sys.path.insert(0, "solution/src")
from social_insights import data, focus

df = data.load_posts()
a = focus.followers_vs_views(df)   # ou category_vs_views, description_vs_views, sponsorship_vs_views
a.verdict; a.evidence; a.details; a.to_markdown()
focus.focus_all(df)                 # as 4
focus.mde_two_groups(sd, n1, n2); focus.mde_correlation(n)   # poder estatístico
```

| Função | Retorna |
|---|---|
| `category_vs_views(df, target)` | média/mediana/IC por categoria, pares com BH e MDE, tabela por plataforma |
| `description_vs_views(df, target)` | tamanho/tom × views (ρ, MDE), palavras distintivas (log-odds), R² do modelo TF-IDF, views por quintil de tamanho |
| `followers_vs_views(df, target)` | ρ, r, inclinação por +100 mil seguidores, elasticidade log-log (IC95), decis |
| `sponsorship_vs_views(df, target)` | diferença bruta e estratificada (IC95, MDE), 21 condições com BH |

`target` aceita qualquer métrica (ex.: `"likes"`, `"eng_rate_views"`).
**Qualidade:** `solution/tests/test_focus.py` cobre as fórmulas de MDE e a detecção de efeitos plantados (+50 views em tech, elasticidade 0,5, +30 views no patrocínio, palavra que prevê views).
