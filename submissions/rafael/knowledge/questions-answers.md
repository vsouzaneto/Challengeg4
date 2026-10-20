# As 4 perguntas do desafio — achados e como usar

Fonte: `solution/src/social_insights/questions.py` · relatório completo: `docs/respostas.md` · gerado em 2026-10-18 sobre 52.214 posts.
Estrutura pensada para virar seções de site: cada pergunta tem **manchete**, **números-chave** (cards), **recomendação**, **armadilha evitada** e **gráfico sugerido**.

> **Contexto obrigatório no site:** o dataset é sintético (métricas sorteadas de forma independente das características do post). Os achados descrevem *este* dataset. O valor entregue é o **método validado**: ele detecta efeitos de 2–10% quando existem (testes com efeito plantado).

---

## 1. O que gera engajamento?

- **Manchete:** nenhuma plataforma, formato, categoria ou porte de creator (nem combinações entre eles) gera engajamento diferente.
- **Números-chave:**
  - 450 segmentos testados (das dimensões isoladas até plataforma × formato × categoria × porte)
  - 22 com p < 0,05 sem correção = **exatamente os ~22 esperados por acaso**
  - 0 significativos após correção (FDR)
  - maior diferença entre grupos: **0,07%**
- **Exemplo de falso insight evitado:** "Vídeos de lifestyle no Bilibili com micro creators engajam mais" (índice 100,5; q = 0,88).
- **Recomendação:** escolher formato, tema e plataforma por **custo de produção e estratégia de marca**, não por engajamento esperado.
- **Gráfico sugerido:** barras de lift por segmento com a faixa de acaso destacada.
- **Métrica:** engajamento = (likes + shares + comentários) / views.

## 2. Patrocínio funciona?

- **Manchete:** não. Patrocinado = orgânico em engajamento e alcance, comparando dentro do mesmo contexto. E o custo cresce com o tamanho do creator, mas o alcance não.
- **Números-chave:**
  - diferença em engajamento: **+0,008%** (IC95 inclui zero; p = 0,72)
  - diferença em alcance (views): **+0,004%** (p = 0,63)
  - **0 de 17** condições (plataforma, porte, formato, categoria) com efeito
  - CPM implícito: **US$ 5,55 (nano) → US$ 29 (micro) → US$ 75 (mid) → US$ 296 (macro) → US$ 744 (mega)**, ou seja, **134x** mais caro por mil views no mega. Os valores em US$ vêm da premissa; a razão de 134x não, porque vale para qualquer cachê proporcional aos seguidores
- **Comparação justa:** diferença estratificada em 269 estratos idênticos (plataforma × formato × categoria × porte), confirmada por regressão com controles.
- **Recomendação (política de patrocínio):**
  1. Não pagar prêmio por seguidores: views não crescem com o porte.
  2. Se patrocinar, usar **nano/micro** e negociar **por resultado** (CPM/CPE), não por post.
  3. Disclosure explícito não prejudica o engajamento (+0,02% vs. orgânico), então exigir rótulo verificável no texto (#publi/#ad) não tem custo de desempenho. O rótulo da base não aparece no texto (ver `audits.md`), então não prova compliance.
  4. Categoria do patrocinador não muda nada (de −0,08% a +0,05%).
- **Premissa:** custo = US$ 10 por mil seguidores por post (`COST_PER_FOLLOWER`). Trocar pelo preço real.
- **Gráfico sugerido:** CPM implícito por porte (barras) + diferença patrocinado − orgânico com IC (forest plot).

## 3. Qual o perfil de audiência que mais engaja?

- **Manchete:** nenhum. Gênero, idade e país engajam igual em toda plataforma, formato e categoria.
- **Números-chave:**
  - 36 testes de contexto (5 plataformas + 4 formatos + 3 categorias × 3 dimensões de audiência): **0 significativos**
  - melhor "persona" (gênero × idade × país): homens 50+ do Reino Unido, índice **100,5** (q = 0,86), ou seja, ruído
  - maior diferença entre segmentos: **0,1%** (país)
- **Recomendação:** definir o público-alvo por **objetivo de negócio** (quem compra), não por engajamento. Neste dado, nenhum público "responde melhor".
- **Gráfico sugerido:** heatmap contexto × segmento (índice 100 = média), com escala que mostre como tudo fica em ~100.

## 4. O que NÃO funciona?

- **Manchete:** 11 de 11 "verdades" comuns de social media não se sustentam nos dados.

| Crença | Efeito medido | Se sustenta? |
|---|---|---|
| Mais seguidores → mais alcance | ρ = 0,005 | não |
| Mais seguidores → mais engajamento | ρ = −0,003 | não |
| Mais hashtags → mais alcance | ρ = −0,006 | não |
| Vídeo engaja mais que imagem/texto | −0,03% | não |
| Conteúdo curto (<60) engaja mais | −0,01% | não |
| Postar à noite dá mais alcance | −0,01% | não |
| Fim de semana dá mais alcance | +0,01% | não |
| Patrocínio aumenta alcance | +0,003% | não |
| Disclosure explícito derruba engajamento | +0,04% | não |
| Legenda longa engaja mais | ρ = −0,0005 | não |
| Mais views → mais likes | ρ = 0,001 | não |

- **Pior segmento por plataforma:** índice entre 99,6 e 99,9, nenhum significativo.
- **Recomendação (parar de fazer):** pagar mais por creators grandes, otimizar horário e quantidade de hashtags, e investir em formatos caros "porque engajam mais".
- **Gráfico sugerido:** tabela de "mitos" com selo ✗.

---

## Mensagens transversais (para a home do site)
1. **Correção para muitos testes é o que separa análise de achismo:** sem ela, ~5% dos testes viram "insights" falsos.
2. **Comparação justa:** patrocinado vs. orgânico só dentro do mesmo contexto.
3. **Custo importa:** se o resultado é igual, o mais barato vence. Hoje o CPM implícito varia 134x entre os portes.
4. **Método validado:** com efeitos plantados de 2–10%, as funções respondem "sim" e apontam o segmento certo.

---

## Como utilizar

### Relatório completo (linha de comando)
```bash
cd submissions/rafael
.venv/bin/python solution/cli/answer_questions.py --out docs/respostas.md   # ou sem --out para imprimir
```

### Em Python (notebook, API ou backend do site)
```python
import sys; sys.path.insert(0, "solution/src")
from social_insights import data, questions

df = data.load_posts()                         # lê data/raw/social_media_dataset.csv e cria as features
answer = questions.does_sponsorship_work(df)   # ou: what_drives_engagement, audience_that_engages, what_does_not_work
answer.verdict      # str — resposta executiva (gerada a partir dos números)
answer.evidence     # DataFrame — tabela principal
answer.details      # dict[str, DataFrame] — tabelas de apoio
answer.to_markdown()                           # bloco pronto para página
questions.answer_all(df)                       # as 4 respostas
```
Para o site: `answer.evidence.to_json(orient="records")` / `to_html()` alimentam tabelas e gráficos. `verdict` é a manchete dinâmica.

### Parâmetros
| Parâmetro | Onde | Padrão | Para quê |
|---|---|---|---|
| `COST_PER_FOLLOWER` | `questions.py` (ou argumento `cost_per_follower`) | 0,01 (US$ 10/mil seguidores) | Custo implícito do patrocínio |
| `ENGAGEMENT` | `questions.py` | `eng_rate_views` | Métrica de engajamento |
| `MIN_SEGMENT` | `questions.py` | 100 posts | Tamanho mínimo de segmento testado |
| `ALPHA` | `questions.py` | 0,05 | Limite de significância (após FDR) |

### Rodar com dados reais da empresa
Basta um CSV com as mesmas colunas do Kaggle (ver `knowledge/dataset.md`) em `data/raw/social_media_dataset.csv`. Mínimo necessário: `post_date`, `platform`, `content_type`, `content_category`, `language`, `views`, `likes`, `shares`, `comments_count`, `follower_count`, `content_length`, `hashtags`, `content_description`, `comments_text`, `is_sponsored`, `disclosure_type`, `sponsor_category`, `audience_*`.
Os vereditos se reescrevem sozinhos a partir dos novos números.

### Garantia de qualidade
`.venv/bin/python -m pytest -q`. Os testes em `solution/tests/test_questions.py` plantam efeitos (ex.: +10% de likes em TikTok × vídeo) e exigem que cada função os detecte e fique quieta no ruído.
