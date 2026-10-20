# Estratégia recomendada — decisões e como usar

Fonte: `solution/src/social_insights/strategy.py` · relatório: `docs/respostas.md` (seções 1–5 de estratégia) · atualizado em 2026-10-19 sobre 52.214 posts.
Complementa `questions-answers.md` (diagnóstico) com as **decisões**. Mesmo formato para o site: manchete, números-chave, ações, premissas.

> **Regra de decisão (vale para tudo):** opções que **não são significativamente piores** que a melhor são "equivalentes" (teste de Welch + correção FDR). **Entre equivalentes, vence a mais barata.** Com dados reais, se uma opção for de fato melhor, ela vence mesmo sendo cara (coberto por teste).

> **Duas classes de recomendação (revisão de 2026-10-19, `review/critica-entrega.md`):**
> - **robusta**: decorre de um resultado dos dados que não depende de preço (ex.: views não crescem com seguidores) e continua válida com os dados reais da empresa;
> - **depende de premissa**: sai das premissas de custo abaixo. É ilustrativa e precisa ser recalculada com os preços reais.

> **Premissas de custo** (o dataset não tem preços, e todas são parâmetros configuráveis):
> custo de patrocínio = US$ 10 por mil seguidores por post · produção própria por post: texto US$ 50, imagem US$ 100, misto US$ 150, vídeo US$ 300 · CPM-alvo US$ 10 · CPE-alvo US$ 0,05.

---

## 1. Onde concentrar esforço?

- **Manchete:** nenhuma plataforma, formato ou faixa de creator entrega mais, então a escolha é pelo menor custo por resultado.

| Decisão | Escolha | Evidência | Classe |
|---|---|---|---|
| Plataforma | Nenhuma vence: concentrar em 1–2 pelo custo operacional e por onde está o cliente-alvo | diferenças ≤ 0,01% em views e ≤ 0,05% em engajamento | robusta (o dataset não diz onde está o cliente: audiência uniforme entre plataformas) |
| Formato | Nenhum engaja mais: usar o mais barato **que a plataforma comporta**, pelo custo real (pela premissa, texto) | 4 formatos equivalentes (diferença ≤ 0,06%) | depende de premissa |
| Faixa de creator | Não pagar prêmio por porte | 5 faixas equivalentes em engajamento e views | robusta |
| Frequência | Limite = capacidade de produção | dias de alto volume não têm pior desempenho por post (0 de 5 plataformas com saturação). Os ~14 posts/dia somam **todos os creators** da base, não a cadência de uma marca | robusta para esta base; medir a cadência da marca com os dados dela |

- **Ações:** não pagar a mais por formato nem por porte esperando engajamento; levantar o custo real de produção por formato; focar 1–2 plataformas; aumentar a frequência e monitorar a saturação mensalmente.

## 2. Política de patrocínio

- **Manchete:** patrocinar **não** compra desempenho. Como as views não crescem com os seguidores, **pague por resultado (CPM/CPE), não por post**.
- **Números-chave:**
  - uplift do patrocínio: **+0,008%** de engajamento e **+0,004%** de alcance (nulos; 269 estratos comparáveis)
  - **0 de 17** condições com efeito (plataforma, porte, formato, categoria)
  - **~134x**: quanto o creator mega paga a mais por mil views que o nano quando o cachê é proporcional aos seguidores. **Essa razão independe do valor do cachê** (o preço por seguidor se cancela), então é o número mais confiável da política.
  - teto para preço fixo por post: **~10.050 seguidores** com as premissas atuais. É uma conta das premissas (CPE-alvo × interações ÷ preço por seguidor = 0,05 × 2.010 ÷ 0,01), não um efeito medido.
- **Sensibilidade do teto (regra do CPM):**

| Preço do creator | CPM-alvo US$ 5 | CPM-alvo US$ 10 | CPM-alvo US$ 20 |
|---|---|---|---|
| US$ 5 / mil seguidores | 10.100 | 20.200 | 40.400 |
| US$ 10 / mil seguidores | 5.000 | 10.100 | 20.200 |
| US$ 20 / mil seguidores | 2.500 | 5.000 | 10.100 |
| US$ 50 / mil seguidores | 1.000 | 2.000 | 4.000 |

- **Ressalvas:** a base tem ~20% de interações por view, bem acima do que se vê no mercado, o que favorece a regra do CPE. Os seguidores são ~Uniforme(0, 1M), então "só 1% dos patrocinados abaixo do teto" descreve o gerador, não um portfólio real (`description-gaps.md`, E5/E6).
- **Ações:**
  1. Contratar por resultado (até US$ 10 por mil views ou US$ 0,05 por interação), não por post fixo. **Robusta.**
  2. Enquanto o preço for fixo: teto de ~10 mil seguidores. **Depende de premissa**, recalcular com o cachê real.
  3. Rótulo de publicidade verificável no texto (#publi/#ad): hoje 47% dos patrocinados usam disclosure implícito (risco alto) e só 2,3% mostram o rótulo no texto; o tipo de disclosure não muda o engajamento (ver `audits.md`). **Robusta.**
  4. Todo patrocínio novo com grupo de comparação orgânico (≥ 30 posts por grupo nesta base; refazer a conta com os dados da empresa). **Robusta.**

## 3. O que parar de fazer

| Parar | Evidência | Classe |
|---|---|---|
| Pagar preço fixo por seguidores | views não crescem com o porte (ρ = 0,005) | robusta |
| Pagar a mais por formatos caros esperando engajamento | engajamento equivalente entre formatos | robusta (o tamanho da economia depende do custo real) |
| Usar como regra geral horário, nº de hashtags, legenda longa, conteúdo curto, fim de semana… | 11 práticas testadas sem efeito | robusta; horário volta só **por plataforma e após teste** (seção 5) |

- **Ordem de grandeza (ilustrativa):** pelas premissas, 98% do gasto implícito com patrocínio é excedente sobre o preço justo (~US$ 109 mi em 2 anos de posts de 5 mil creators). **Não é o gasto da empresa.** No site aparece em %, não em US$.

## 4. Quick wins (esta semana)

As 4 primeiras valem também com os dados reais da empresa. As 2 últimas dependem das premissas de preço.

| # | Ação | Classe | Impacto | Dono |
|---|---|---|---|---|
| 1 | Novos contratos e renovações por resultado (views ou interações), não por post | robusta | o custo por view deixa de crescer com o porte (hoje ~134x entre mega e nano) | Parcerias / Compras |
| 2 | Rótulo de publicidade verificável no texto (#publi/#ad) como padrão | robusta | reduz o risco regulatório (47% em risco alto) sem custo de engajamento | Social media |
| 3 | Todo patrocínio novo com grupo de comparação orgânico | robusta | mede o ganho real do patrocínio | AI Master / Analytics |
| 4 | Não pagar a mais por creator "campeão" e tirar horário/hashtags ideais do checklist | robusta | desempenho passado é sorte (`creators.md`) e essas regras não mudam o resultado | Social media |
| 5 | Teto de ~10 mil seguidores para contratos de preço fixo | depende de premissa | pelas premissas, 98% do gasto implícito é excedente | Head de Marketing |
| 6 | Formato padrão pelo custo real de produção | depende de premissa | mesmo engajamento com menor custo por post | Conteúdo |

## 5. Fila de testes (`strategy.test_queue`)

Das ~14,7 mil variações testadas por plataforma, só estas merecem teste. O resto está no nível do acaso. Nenhuma vira regra antes do teste.
"Posts por grupo" é o necessário para confirmar **ao menos metade** da diferença observada (80% de poder, α = 5%), porque a diferença achada numa busca costuma ser inflada.

| # | Hipótese | O que os dados mostram | Posts por grupo | Como tratar |
|---|---|---|---|---|
| 1 | TikTok · beauty · espanhol aumenta a chance de top 5% em likes | 10,0% vs. 4,9% (2,0x), nos 2 anos; q global = 0,035 | ~1.430 | teste A/B (mesmo conteúdo em espanhol × inglês) |
| 2 | YouTube: posts até 12h entram mais no top 1% de comentários | 1,45% vs. 0,85%; hora típica 9h vs. 12h (q = 0,02) | ~17.000 | acompanhar no histórico; usar como desempate de agenda |
| 3 | Patrocínio aumenta o engajamento em ≥ 5% | nenhum efeito nesta base | 30 (mínimo prático; a variação aqui é de ~1%) | teste A/B com os contratos da empresa |

- **Por que a hipótese 1 não é "prioridade":** não aparece nas outras plataformas (beauty·espanhol: 4,5–5,5%) nem nas outras métricas do TikTok (views 4,7%, shares 4,4%), e a média de likes sobe só 0,4%. Num gerador declaradamente aleatório, 1 achado em 14,7 mil testes pede confirmação antes de mudar o mix.
- **Por que a hipótese 2 não substitui a regra "sem melhor horário":** a média de comentários não muda; só a chance de entrar no top 1%. Confirmar custaria ~17 mil posts por grupo.

---

## Como utilizar

### Relatório (diagnóstico + estratégia)
```bash
cd submissions/rafael
.venv/bin/python solution/cli/answer_questions.py --out docs/respostas.md
```

### Em Python
```python
import sys; sys.path.insert(0, "solution/src")
from social_insights import data, strategy

df = data.load_posts()
rec = strategy.sponsorship_policy(df, cost_per_follower=0.008, target_cpm=12, target_cpe=0.04)  # premissas próprias
rec.verdict    # decisão executiva (gerada dos números)
rec.actions    # list[str] — próximos passos
rec.evidence   # DataFrame principal; rec.details: tabelas de apoio
rec.to_markdown()
strategy.recommend_all(df)  # as 4 decisões
```

| Função | Pergunta | Retorna |
|---|---|---|
| `where_to_focus(df, production_cost, cost_per_follower)` | Onde concentrar esforço | plataforma, formato, faixa de creator, saturação de frequência |
| `sponsorship_policy(df, cost_per_follower, target_cpm, target_cpe)` | Política de patrocínio | decisão, threshold, ponto de equilíbrio, perfil |
| `stop_doing(df, ...)` | O que parar | investimentos de baixo retorno com excedente estimado |
| `quick_wins(df, ...)` | Quick wins | ações com esforço, impacto e dono |
| `test_queue(df, by_platform)` | Fila de testes | até 3 hipóteses com evidência e posts necessários por grupo |
| `break_even(df, ...)` | (apoio) | teto de seguidores e engajamento necessário por porte |
| `threshold_sensitivity(df, costs, cpms)` | (apoio) | teto de seguidores para cada preço × CPM-alvo |
| `tier_cost_ratio(df)` | (apoio) | quantas vezes o maior porte paga a mais por mil views (independe do preço) |
| `ab_sample_size(p0, p1)` · `mean_sample_size(df, metric)` | (apoio) | posts por grupo de um teste A/B |
| `frequency_effect(df, metric)` | (apoio) | saturação por plataforma (volume diário × desempenho por post) |
| `equivalence_table(df, by, metric)` | (apoio) | opções equivalentes à melhor |

### Parâmetros (premissas)
| Constante | Padrão | Trocar por |
|---|---|---|
| `COST_PER_FOLLOWER` | 0,01 | preço real por seguidor (ou tabela de cachês) |
| `PRODUCTION_COST` | texto 50 · imagem 100 · misto 150 · vídeo 300 | custo interno real por formato |
| `TARGET_CPM` | 10 | CPM máximo aceito (benchmark de mídia paga) |
| `TARGET_CPE` | 0,05 | custo máximo por interação |

### Qualidade
`solution/tests/test_strategy.py` testa a fórmula do threshold e a regra "mais barato entre equivalentes". Também testa, com efeitos plantados, que o formato melhor vence mesmo sendo caro, que a saturação é detectada e que o patrocínio vira "SIM" quando há efeito.

## Provas do resumo executivo (2026-10-19)
Fonte: `strategy.deliverable_evidence`, `strategy.claims_vs_data`, `strategy.test_brief` (seção 6 e brief da seção 5 de `docs/respostas.md`).
- **Taxa por seguidor × por view** (`exploration.engagement_rate_by_tier`): mediana de interações por seguidor 0,368 (nano) × 0,002676 (mega) = **137,6x**. Os ~136x da nota anterior vêm de dividir valores arredondados (0,368 / 0,0027). Por view, todas as faixas ficam em ~0,199; views medianas de 10.090 a 10.101.
- **Survivorship** (`cleaning.survivorship_check`): 0 posts com zero em views, likes, shares ou comentários; mínimos de 9.676 views, 1.354 likes, 227 shares e 140 comentários.
- **Trimestres** (`exploration.engagement_by_quarter`): 0,19901–0,19909 em 9 trimestres (2023Q2–2025Q2), Kruskal p = 0,99.
- **Maior diferença bruta entre segmentos (Q1):** Bilibili · video · lifestyle · micro, índice 100,5, n = 109, p = 0,02, q = 0,88. TikTok · video · beauty · mid (100,4, n = 120, p = 0,09) é o 5º; as notas anteriores citavam este.
- **Brief do teste 1** (TikTok · beauty · Spanish × English): vídeo (61% do segmento); nano (menor CPM); Japão 15% e 19–25 anos 36% (distribuição quase uniforme); horário sem evidência para likes no TikTok (q = 0,97); duração ~172 s; sucesso = top 5% em likes ≥ 7,5% (resto do TikTok 4,9%), p < 0,05, 1.430 posts por grupo, poder de 80%.
