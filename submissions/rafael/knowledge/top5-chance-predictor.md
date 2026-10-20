# Chance de cair no top 5% antes de postar — achados e como usar

Fonte: `solution/src/social_insights/hit_probability.py` · notebook: `solution/notebooks/12_chance_top5.ipynb` · CLI: `solution/cli/predict_hit.py` · 2026-10-19.

## O que a ferramenta responde
"Se eu postar **isto**, qual a % de chance de ficar entre os **5% melhores do formato** (vídeo, imagem, texto, misto) em **views**, **likes** e **comentários**?"
Ela mostra o mesmo post nos 4 formatos para comparar.

## Modelos (um por métrica × formato = 12 combinações)
| Modelo | Ideia |
|---|---|
| taxa base | ~5% para todo post (referência) |
| segmento | taxa histórica de plataforma × categoria × idioma, encolhida para a base (Bayes empírico, 200 pseudo-posts) |
| regressão logística | todas as variáveis pré-postagem (+ histórico do creator) |
| LightGBM calibrado | árvores com calibração sigmoide |

**Validação:** treino no passado e teste nos posts mais recentes. **Adoção:** vencer a base no Brier **e** AUC > 0,5 com q < 0,05 (correção para os 36 testes).

## Resultados
- **0 de 12** combinações adotaram um modelo, então a **chance oficial é a taxa base** (5,0–5,5%; um pouco acima de 5% por empates no valor de corte).
- AUC no teste entre 0,42 e 0,60. Os melhores: comentários·misto (segmento, AUC 0,60), likes·misto (LightGBM 0,60 / logística 0,58) e likes·imagem (segmento 0,57). Todos com p < 0,05 isolado e **q ≥ 0,15** após a correção. São formatos com poucos posts no teste (~1–2 mil, ~55 hits).
- Ganho máximo de Brier: 0,7%. **Calibração:** as previsões ficam espremidas perto de 5% e a taxa real oscila sem acompanhar, então não há informação para prometer, por exemplo, "15% de chance".

## O sinal que aparece: TikTok · beauty · espanhol
| Formato | Views | Likes | Comentários |
|---|---|---|---|
| vídeo (276 posts no segmento) | 4,9% (3,3–6,6) | **9,3% (7,2–11,5)** | 5,1% (3,5–6,8) |
| imagem (83) | 4,6% | 5,5% | 6,7% (4,4–9,3) |
| misto (44) | 5,0% | 6,0% | 5,5% |
| texto (48) | 4,9% | 5,0% | 5,1% |
(sinal do segmento e intervalo de 90%; base ≈ 5%)
- **Likes em vídeo** nesse segmento: ~**9%**, quase 2x a base, com intervalo que não cruza 5%. É o achado robusto do notebook 11 aparecendo na ferramenta, e a hipótese nº 1 da fila de testes (não uma regra).

## Mensagens para o site
1. "Antes de postar, a ferramenta mostra a chance de o post virar destaque em views, likes e comentários, em cada formato."
2. "Honestidade embutida: se nada do que se sabe antes de postar melhora a previsão, ela mostra a taxa base (5%) e avisa. Não inventa '15% de chance'."
3. "O que ela já encontra: no TikTok, beauty em espanhol tem ~9% de chance de top 5% em likes de vídeo, quase o dobro do normal."
4. "Testada com efeito plantado: quando um segmento realmente rende mais, a ferramenta adota o modelo e a chance do segmento sobe."

**Gráficos sugeridos:** heatmap de AUC (métrica×formato × modelo); curva de calibração; simulador "mesmo post em 4 formatos" com o sinal do segmento ± IC90.

## Como utilizar
```bash
cd submissions/rafael
.venv/bin/python solution/cli/predict_hit.py --platform TikTok --content_category beauty --language Spanish --hour 19
.venv/bin/python solution/cli/predict_hit.py --content_type video --platform YouTube --content_category tech --follower_count 50000
.venv/bin/python solution/cli/predict_hit.py --retrain       # ~25 s; salva em solution/models/hit_predictor.joblib
```
A saída traz 3 tabelas (formato × métrica): chance oficial (%), sinal do segmento (%) e IC90 do sinal. Campos omitidos assumem o post típico.

```python
from social_insights import data, hit_probability as hp
df = data.load_posts()
predictor = hp.HitPredictor.train(df)          # avalia 12 combinações × 4 modelos e adota com correção
predictor.evaluation                           # AUC, Brier, q, adotável
predictor.predict(posts_planejados)            # 1 linha por post × métrica
hp.evaluate(df, "likes", "video")              # tabela + previsões de teste
hp.calibration_table(y, p)                     # previsto × observado por faixa
```
- **Parâmetros:** `TOP_Q` (0,95), `SEGMENT` (plataforma, categoria, idioma), `PRIOR_STRENGTH` (200), `CATEGORICAL`/`NUMERIC` (variáveis pré-postagem).
- **Qualidade:** `solution/tests/test_hit_probability.py` verifica:
  - o encolhimento e o intervalo do segmento;
  - que a adoção exige correção;
  - que um segmento plantado é aprendido e eleva a chance em mais de 2x;
  - o fallback para a base em dados de ruído.
