# Todos os atributos × views, likes e comentários — achados e como usar

Fonte: `solution/src/social_insights/attribute_scan.py` · notebook: `solution/notebooks/07_atributos_x_metricas.ipynb` · gerado em 2026-10-18 sobre 52.214 posts.

## Manchete
**96 combinações atributo × métrica, 0 efeitos reais.** Nenhum atributo explica mais que **0,06%** de views, likes ou comentários. Os 5 "achados" com p < 0,05 sem correção são exatamente os ~5 esperados por acaso.

## O que foi testado (33 atributos × 3 métricas)
| Tipo | Atributos | Teste |
|---|---|---|
| Categórico (18) | platform, content_type, content_category, language, is_sponsored, disclosure_type, disclosure_location, sponsor_category, audience_gender/age/location, follower_tier, length_bin, daypart, weekday, month, url_tld, url_https | Kruskal-Wallis + η² |
| Numérico (8–9) | follower_count, content_length, n_hashtags, hour, post_day (tendência no tempo), caption_words, comment_sentences + as outras métricas (views, likes, shares, comments_count) | Spearman + ρ² |
| Alta cardinalidade | creator_id (5 mil creators, ~10 posts cada) | ANOVA, η² acima do acaso |
| Texto (3) | content_description, hashtags, comments_text | TF-IDF + Ridge, R² de validação cruzada |

**Fora da varredura:** content_id (único por post), id (= ordem cronológica, coberto por post_day), creator_name (muda a cada post), sponsor_name (1,2 post por patrocinador), content_url (testada via TLD e https), interactions/eng_rate (derivadas das métricas).

## Números-chave
- **Maior variância explicada:** creator_id × likes = 0,06% (p = 0,37, acaso). Escala de referência: em redes reais, seguidores sozinhos costumam ser o principal fator e explicar uma parte grande das views.
- **Maiores efeitos de negócio:**
  - views: faixa de creator 0,11% (melhor micro vs. pior nano)
  - likes: faixa de creator 0,19%
  - comentários: mês 0,53% (junho vs. janeiro) = **~1 comentário em 200**
  - todos com q ≥ 0,70
- **"Melhores aparentes" (menor p por métrica):**
  - views: período do dia (madrugada/manhã +1,5 view vs. tarde) e hora
  - likes: período do dia e idioma
  - comentários: mês e dia da semana
  - todos q ≥ 0,70; diferenças de 1–3 views ou ~1 comentário
- **Textos:** R² ≤ 0 nos 9 testes (3 textos × 3 métricas).
- **Creators:** η² = 0,096 contra 0,096 esperado por acaso. Nenhum creator é consistentemente melhor; a dispersão entre creators vem de ~10 posts cada.

## Descobertas sobre o dado (qualidade)
1. **As métricas não se relacionam entre si** (views × likes × shares × comentários: |ρ| < 0,01). Em redes reais, likes e comentários sobem com as views.
2. **`comments_text` × `comments_count` são incoerentes:** a contagem diz ~200 comentários, mas o texto tem 0–5 frases, sem relação com a contagem.
3. **URLs são domínios aleatórios** (smith.com aparece em mais de 100 posts), sem efeito.

## Mensagem para o site
"Percorremos **todos** os atributos: 33 colunas × 3 métricas, com o teste certo para cada tipo (categórico, numérico, texto, creator). Nada explica mais que 0,06% do resultado. Os falsos 'insights' que apareceriam sem correção estatística (ex.: 'post de manhã tem mais likes') somem quando se corrige para os 96 testes."

**Gráficos sugeridos:** heatmap atributo × métrica (escala até 1%, quase todo branco); barras de |efeito| vs. marcador de MDE por métrica; painel dos "melhores aparentes" com IC95; heatmap de correlação entre métricas.

---

## Como utilizar
```python
import sys; sys.path.insert(0, "solution/src")
from social_insights import data, attribute_scan as sc

df = data.load_posts()
table = sc.scan(df)                          # todas as combinações (padrão: views, likes, comments_count)
table = sc.scan(df, targets=["shares"])      # qualquer métrica
sc.summary_matrix(table)                     # atributo × métrica (variância explicada %)
sc.group_profile(df, "daypart", "likes")     # média ± IC95 por grupo/quintil
sc.skipped_attributes()                      # o que ficou fora e por quê
```
- **Colunas da tabela:** atributo, alvo, tipo, teste, grupos, variância explicada (%), efeito de negócio (%), leitura do efeito, MDE (%), p_value, q_value, significativo.
- **Para incluir um atributo novo:** adicione o nome à lista do tipo (`CATEGORICAL`, `NUMERIC`, `HIGH_CARDINALITY`, `TEXT`). Se for derivado, crie-o em `attribute_frame`.
- **Qualidade:** `solution/tests/test_attribute_scan.py`. A varredura fica quieta no ruído e acusa o atributo certo com efeitos plantados em plataforma (categórico), seguidores (numérico), creator (alta cardinalidade) e legenda (texto).
