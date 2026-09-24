# Achados iniciais dos dados (exploração antes de construir)

*23/09/2026. Primeira leitura de cada base baixada. Isto já é material para o relatório de entrega e para o process log: "entender a estrutura antes de analisar" é critério explícito do desafio.*

> **O achado mais importante:** as bases do **002** e do **004** são sintéticas **quase sem sinal**. As métricas são praticamente iguais em todos os grupos. Um candidato que "cola o brief na IA" vai inventar insights ("vídeo engaja mais", "chat satisfaz mais"). Nós vamos **provar com estatística que as diferenças não existem** e construir ferramentas que funcionam quando o sinal existe. Esse é o diferencial que eles chamam de *"saber quando desconfiar"*.

---

## 001 — Churn (RavenStack)
- 5 tabelas completas, com chaves íntegras (conferido nos arquivos).
- Dados sintéticos, com reativações e nulos propositais. Se o modelo preditivo tiver sinal fraco, é preciso dizer isso com honestidade (conferido depois: AUC 0,56).
- Tickets **sem texto** (só métricas) → no cruzamento Churn → Suporte, só a parte operacional do módulo de suporte se aplica.

## 002 — Suporte
### Dataset 1 (`customer_support_tickets.csv`)
| Ponto | Achado |
|---|---|
| Volume | **8.469 tickets**, e não os ~30 mil que o README diz |
| Status | Closed 2.769 · Pending 2.881 · Open 2.819 |
| Resolução e satisfação | Só existem nos **2.769 Closed** (os outros 5.700 são nulos) |
| First Response Time | Nulo nos 2.819 Open |
| ⚠️ **Tempos** | "First Response Time" e "Time to Resolution" **não são durações, são datas/horas**, todas numa janela de ~26 h (31/05 a 02/06/2023). **Não existe a hora de abertura do ticket.** A resolução acontece **antes** da 1ª resposta em **49%** dos casos (1.365 de 2.769) → as durações precisam de uma definição cuidadosa e documentada |
| ⚠️ **Satisfação** | Média ≈ **3,0** em todo canal (2,95–3,08), prioridade (2,96–3,05) e tipo (2,93–3,03); correlação com o tempo = **0,02** → **nenhum driver real** |
| ⚠️ Tipo × Assunto | Independentes (um "Refund request" com assunto "Display issue" é comum) → rótulos gerados aleatoriamente |
| ⚠️ Texto | **100%** das descrições têm o marcador literal `{product_purchased}` (template não preenchido); a **Resolution é texto aleatório** ("Case maybe show recently my computer follow.") |
| Colunas extras | `Date of Purchase` e `Ticket Type` com 5 valores (inclui Refund e Cancellation request) |

### Dataset 2 (IT Service Ticket Classification)
⬜ **Ainda não está na pasta.** É obrigatório: o desafio exige usar **os dois datasets**, e é nele que o classificador é treinado e testado (~48 mil textos, 8 categorias). **Precisa baixar:** https://www.kaggle.com/datasets/adisongoh/it-service-ticket-classification-dataset → `02/dados/002-suporte/`.

## 003 — Lead Scorer (CRM)
| Ponto | Achado |
|---|---|
| Pipeline | 8.800 oportunidades: **Won 4.238 · Lost 2.473 · Engaging 1.589 · Prospecting 500** |
| Taxa de ganho histórica | **63,2%** (Won / (Won+Lost)) |
| Datas | Engaging de 20/10/2016 a 27/12/2017; fechamentos até **31/12/2017** → "hoje" da análise = **31/12/2017** |
| Prospecting | Sem engage_date e sem close_date (esperado) |
| Deals sem conta | **1.425** (1.088 Engaging + 337 Prospecting) → score precisa funcionar sem dados da conta |
| ⚠️ Nome de produto | Pipeline usa **"GTXPro"**, catálogo usa **"GTX Pro"** → normalizar |
| ⚠️ Setor | Erro de digitação **"technolgy"** → normalizar |
| Vendedores | 35 no time, **30 com deals** (5 sem nenhum) |
| `close_value` | Nos Won ≈ preço de catálogo (razão mediana 1,00; 0,66–1,34) |
| **Sinal real (fraco a moderado)** | Win rate por **vendedor: 55% a 70%** (maior diferença); produto 60–65%; setor 61–65%; região 63–64%; manager 62–64% |
| ⚠️ Armadilha de vazamento | Deals **Lost fecham rápido** (mediana 14 dias) e **Won demoram** (57 dias). "Ciclo longo = ganha" **não pode** virar regra para deals abertos, porque a duração só é conhecida depois de fechar |
| Deals esfriando | Engaging abertos têm idade mediana de **165 dias** (em 31/12/2017), muito acima do ciclo típico de um Won (57) → sinal de "deal parado" |

## 004 — Social Media (`social_media_dataset.csv`)
| Ponto | Achado |
|---|---|
| Volume | **52.214 posts**, 27 colunas, 5 mil criadores, 29/05/2023 a 28/05/2025 |
| Distribuição | ~10,4 mil posts por plataforma (Bilibili, YouTube, Instagram, RedNote, TikTok); patrocinados 22.314 (43%) |
| Categorias | Só **3** (beauty, lifestyle, tech) |
| ⚠️ **Views** | ~**10.100 ± 100** em TODOS os posts (mín. 9.676, máx. 10.551) |
| ⚠️ **Engajamento** | Taxa (likes+shares+comments)/views ≈ **0,199** em toda plataforma, tipo e patrocínio (diferença na 4ª casa decimal) |
| ⚠️ Seguidores × alcance | Correlação views × seguidores = **0,005** → criador de 1 mil ou de 1 milhão de seguidores tem o mesmo alcance |
| Engajamento zero | **Nenhum post** (o viés de sobrevivência que eles citam não se aplica, e isso também é um achado) |
| Texto | Descrições e comentários são texto aleatório; hashtags são palavras soltas |
| Coerência | `disclosure_type` = none ⇔ não patrocinado (consistente) |

**Conclusão para o 004:** o dataset **não permite** dizer que plataforma, formato, categoria, tamanho de criador ou patrocínio mudam o engajamento. A estratégia honesta: (1) **provar** isso com testes e tamanho de efeito; (2) recomendar decisões pelo **custo** (se o resultado é igual, o mais barato vence: por exemplo, não pagar a mais por criador grande); (3) entregar a **ferramenta** de análise controlada, que acha diferenças quando elas existem, validada com um **teste de sanidade** (injetar um efeito conhecido numa cópia dos dados e mostrar que a ferramenta o encontra).

---

## Consequência para o planejamento
1. Todo módulo mostra **tamanho de efeito + intervalo de confiança + tamanho de amostra**, e não só médias.
2. Todo módulo tem um bloco **"Qualidade e confiabilidade dos dados"** no resultado.
3. **Teste de sanidade com sinal injetado** para os módulos 002 e 004 (e para o score do 001), rotulado como teste e **nunca** misturado aos resultados reais.
4. As recomendações dizem quando a decisão é por **evidência** e quando é por **custo/risco** na ausência de evidência.
