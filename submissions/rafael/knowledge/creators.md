# Creator × views — quem posta importa?

Fonte: `solution/src/social_insights/creators.py` · notebook: `solution/notebooks/13_creators.ipynb` · site: Aprofundar → Descobertas → "Quem posta não muda as views" (`/descobertas#creators`) · 2026-10-19.

## Manchete
**Quem posta não muda as views (nem likes, nem comentários).** Os creators "campeões" são sorte.

## Números
| Teste | Resultado | Leitura |
|---|---|---|
| Identidade | `creator_id`: 5.000 creators, ~10 posts cada · `creator_name`: 42.213 nomes; o mesmo nome aparece em até 19 ids | só `creator_id` serve como identidade, e mesmo assim cada id tem ~10 nomes e seguidores diferentes |
| % da variação ligada ao creator (ICC) | views 0,0% · likes 0,07% · comentários 0,0% (p = 0,53 / 0,37 / 0,81) | saber quem postou não explica o resultado |
| Médias por creator × sorteio | desvio 31,0 views × 31,0 esperado por acaso (p = 0,53) | a diferença entre creators é **exatamente** a do acaso |
| Os melhores continuam? | 44 de 500 (8,8%) dos top 10% do 1º ano seguiram no top no 2º (acaso: 10%); ρ entre anos = −0,02 | não há persistência |
| Ranking honesto | top 10 com média bruta de 10.188–10.232 views → **10.100** descontada a sorte (peso do histórico 0%) | os "campeões" voltam à média |
| Seguidores × views por creator | ρ = 0,02 (p = 0,19) | creators maiores não têm mais views |

## Controle positivo
Com um nível próprio por creator (±3%), as funções acusam ICC > 50%, dispersão além do acaso, mais de 50% dos top continuando no top e peso do histórico > 80% (`solution/tests/test_creators.py`).

## Mensagem para o site / time
- "Não pague a mais por um creator por causa do desempenho passado: neste histórico, ele é sorte."
- "Com dados reais, este costuma ser o primeiro fator a aparecer (cada creator tem sua audiência), e as mesmas funções medem isso."

## Como utilizar
```python
from social_insights import data, creators as cr
df = data.load_posts()
cr.identity_check(df); cr.variance_share(df); cr.spread_vs_chance(df)
cr.persistence(df)      # top 10% do 1º ano × 2º ano
cr.leaderboard(df)      # média bruta × média ajustada (Bayes empírico)
```
