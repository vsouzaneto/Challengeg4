---
status: passing
canonical: false
area: frontend
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-015 Rotas de pesquisa por challenge

Reverse da página viva `http://localhost:3020/research#analysis` (2026-09-21) e contrato das rotas que recontam essa estrutura para os quatro challenges.

A página `/research` (Wisconsin / SVM) foi removida. Contexto e Análise apontam para `/research-challenge-00N`.

## Reverse — anatomia observada

Chrome: `Navigation` fixo + `FooterSection`. Miolo `max-w-[1400px]`, `pt-32` / `lg:pt-40`, `space-y-24` / `lg:space-y-32`.

| Ordem | `id` | Sobrancelha | Título observado | Papel na história |
| --- | --- | --- | --- | --- |
| 1 | `background` | Contexto | Ler núcleos / como evidência | Problema, o que o trabalho é, o que não é. Quatro números. |
| 2 | `eda` | Análise exploratória de dados | O sinal escondido nos histogramas | Vários recortes; um fica em foco. |
| 3 | `feature-selection` | Seleção de features | Eliminação recursiva de features | O que entra e o que sai, com motivo. |
| 4 | `analysis` | Análise | Escolha uma lente / Mesmos dados, outra postura | Três posturas sobre o mesmo material. |

Menu que levava a essas âncoras (header, antes desta spec):

- Contexto → `/research#background`
- Análise → `/research#analysis`

## Contrato das rotas

Cada challenge repete os quatro `id` acima. O miolo troca o caso Wisconsin pelo brief do challenge. Números só entram se já estão no README do pack, na SPEC-00N ou no notebook Lab 04 citado.

| Menu | Challenge | Rota |
| --- | --- | --- |
| Contexto | 001 churn | `/research-challenge-001#background` |
| Contexto | 002 support | `/research-challenge-002#background` |
| Contexto | 003 lead | `/research-challenge-003#background` |
| Contexto | 004 social | `/research-challenge-004#background` |
| Análise | 001 churn | `/research-challenge-001#analysis` |
| Análise | 002 support | `/research-challenge-002#analysis` |
| Análise | 003 lead | `/research-challenge-003#analysis` |
| Análise | 004 social | `/research-challenge-004#analysis` |

Header (desktop e menu mobile): **Contexto** e **Análise** são dropdowns. Cada um lista `001 churn`, `002 support`, `003 lead`, `004 social` com o hash da tabela. Sobre, Modelo, Imagens e Resultados permanecem links simples.

Fonte única dos hrefs: `src/frontend/lib/research/stories.ts`.

## Storytelling por rota

| Rota | Contexto (`#background`) | Sinal (`#eda`) | Corte (`#feature-selection`) | Lentes (`#analysis`) |
| --- | --- | --- | --- | --- |
| 001 | CEO vs. CS vs. Produto; cinco tabelas; label = `churn_events` | Lab 04 (`churn_flag`): downgrade, upgrade, trial, país, indústria | Manter join + impacto. Descartar uma tabela, `churn_flag` como verdade, satisfação sem cruzamento | Causa, segmentos, ações |
| 002 | 8 469 tickets (o CSV ganha do brief ~30 k); horas = TTR − FRT só em Closed | Tipo, status, Dataset 2 ausente, PII | Manter horas derivadas e zona humana. Descartar ~30 k, `Topic_group`, TTR como horas nativas | Gargalo, satisfação, automação |
| 003 | 85 / 7 / 35 / 8 800; ferramenta do vendedor, não o ranking Won/Lost | `GTXPro`, account nulo, `close_value` nulo no aberto, 0 = Lost | Manter score + porquê no pipe aberto. Descartar ordenar por `close_value` | Score, explicação, limites |
| 004 | 52 214 × 27; sem `engagement_rate` | Taxa derivada, audiência em bucket, `creator_name` ≠ chave, sem custo de sponsor | Manter comparação controlada. Descartar taxa nativa, nome como PK, custo inventado | Engajamento, patrocínio, estratégia |

## Verificação

- [x] Quatro rotas respondem 200 e contêm `id="background"` e `id="analysis"`.
- [x] Header deixa de usar `/research#background` e `/research#analysis` como destino único de Contexto e Análise.
- [x] `/research` responde 404.

## Notas

O primeiro rascunho do pedido apontava o challenge 004 para `/research-challenge-003#background`. O dropdown fecha o contrato em `/research-challenge-004`.
