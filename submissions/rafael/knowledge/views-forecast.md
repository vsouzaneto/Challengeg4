# Prever views antes de postar — achados e como usar

Fonte: `solution/src/social_insights/views_forecast.py` · notebook: `solution/notebooks/08_previsao_views.ipynb` · CLI: `solution/cli/predict_views.py` · gerado em 2026-10-19 sobre 52.214 posts.

## Manchete
**Nada do que se sabe antes de postar prevê as views** melhor que a média histórica (10.100 views, intervalo de 90%: 9.935–10.267). Nem conteúdo, nem quem posta, nem patrocínio, horário ou audiência, testados com validação temporal (treino no passado, teste nos posts mais recentes).

## 1. Inventário: o que se sabe antes de postar
| Bloco | Colunas (conhecidas antes) | Observação |
|---|---|---|
| Conteúdo | platform, content_type, content_category, language, content_length, content_description (nº de palavras), hashtags (nº) | `content_length` vai de 10 a 599 em **todos** os formatos (inclusive imagem), então não é um "tamanho do vídeo" confiável |
| Quem posta | creator_id (via **histórico**), follower_count | `creator_name` e seguidores **mudam a cada post** do mesmo creator_id |
| Patrocínio | is_sponsored, sponsor_category, disclosure_type, disclosure_location | sponsor_name fica de fora (1,2 post por patrocinador) |
| Horário | post_date → hora, dia da semana | agendamento |
| Audiência | gênero, idade e país predominantes | perfil histórico do creator |
| **Só depois** | views (alvo), likes, shares, comments_count, comments_text | resultado |
| Identificadores | id, content_id, content_url | sem uso preditivo |

**"Quem postou" vira histórico do creator**, calculado só com os posts anteriores (sem vazamento): nº de posts anteriores, média de views anterior, views do último post e dias desde o último post.

## 2. Resultados (treino: 41.771 posts até 2024-12-31 · teste: 10.443 posts mais recentes)
| Abordagem | Melhor modelo | R² teste | Erro vs. média |
|---|---|---|---|
| Média histórica (baseline) | — | 0,000 | 0% (erro médio 0,79% ≈ 80 views) |
| Média passada do creator | — | −0,120 | **+5,8% de erro** |
| 1. Conteúdo | CatBoost | −0,001 | +0,02% |
| 2. + Quem posta | CatBoost | −0,004 | +0,20% |
| 3. + Patrocínio | CatBoost | −0,003 | +0,16% |
| 4. + Horário | CatBoost | −0,002 | +0,13% |
| 5. + Audiência | CatBoost | −0,002 | +0,10% |

- **Overfitting:** o LightGBM chega a R² 0,10 no treino conforme ganha variáveis e fica < 0 no teste.
- **Creators não mantêm o nível:** a média de views da 1ª metade dos posts × a 2ª metade dá ρ = −0,007. Em redes reais, isso costuma ser alto (o creator tem audiência própria).

## 3. Controle positivo (o método funciona?)
Com um nível persistente por creator (±3%) + efeito de conteúdo (+3% em TikTok × vídeo × tech):
- consistência do creator: ρ = 0,97
- "média passada do creator": R² 0,86, com 64% menos erro
- **bloco "+ quem posta" (LightGBM): R² 0,88, com 66% menos erro**, e o previsor adota esse modelo sozinho

**Conclusão:** se quem posta (ou o que posta) importasse, o método mostraria. A ausência de previsão nos dados originais é real.

## Mensagens para o site
1. "Separamos o que se sabe **antes** de postar do que só se mede depois. Usar likes para prever views seria trapaça."
2. "Validação como no mundo real: treinamos no passado e testamos no futuro."
3. "Quem posta não importa neste dataset: o desempenho passado de um creator não diz nada sobre o próximo post (ρ ≈ 0)."
4. "O previsor é honesto: enquanto nada ajudar, devolve a média e avisa. Com sinal (testado com efeito plantado), adota o histórico do creator e acerta 88%."

**Gráficos sugeridos:** tabela de inventário (antes × depois); dispersão de consistência do creator (nuvem redonda vs. diagonal no controle positivo); barras de ganho de erro por bloco; linhas de R² treino × teste.

---

## Como utilizar
```bash
cd submissions/rafael
.venv/bin/python solution/cli/predict_views.py --creator_id creator_586 --platform TikTok --content_type video \
    --content_category tech --content_length 45 --is_sponsored True --hour 19 --weekday Friday
# Modelo: média histórica (supera a média histórica: não)
# Views previstas: 10,100  (intervalo 90%: 9,935 – 10,267)
.venv/bin/python solution/cli/predict_views.py --retrain   # refaz a avaliação (~25 s) e salva em solution/models/
```
`--creator_id` puxa o histórico do creator. Campos omitidos assumem o post típico (moda/mediana).

```python
import sys; sys.path.insert(0, "solution/src")
from social_insights import data, views_forecast as vf

df = data.load_posts()
vf.inventory()                          # o que é conhecido antes de postar
vf.add_creator_history(df)              # histórico do creator sem vazamento
evaluation = vf.evaluate(df)            # baselines + 5 blocos × (LightGBM, CatBoost), validação temporal
vf.creator_consistency(df)              # creators mantêm o nível?
forecaster = vf.ViewsForecaster.train(df, evaluation)
forecaster.predict(posts_planejados)    # views previstas + intervalo 90% + modelo usado
vf.creator_snapshot(df, "creator_586")  # histórico para o próximo post de um creator
```
- **Parâmetros:** `TEST_SHARE` (0,20, fração mais recente usada como teste), `BLOCKS` (blocos de variáveis), `INVENTORY` (classificação antes × depois de cada coluna).
- **Qualidade:** `solution/tests/test_views_forecast.py` verifica:
  - o inventário (resultados marcados como "depois");
  - que o histórico do creator não olha o futuro;
  - que o split temporal não se sobrepõe;
  - o fallback para a média no ruído;
  - a detecção do efeito do creator.
