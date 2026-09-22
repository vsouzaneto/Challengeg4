---
status: passing
canonical: false
area: frontend
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-016 Rotas de modelo por challenge

Reverse da página viva `http://localhost:3020/model` (2026-09-21) e contrato das rotas que recontam essa oficina com o Lab 04 de cada challenge.

A página `/model` (SVM Wisconsin) foi removida. Modelo aponta para `/model-challenge-00N`.

## Reverse — anatomia observada

Chrome igual às outras páginas internas. Miolo `max-w-[1400px]`, `pt-32` / `lg:pt-40`, sem `space-y` no wrapper: o espaçamento mora em `ModelWorkshop`.

| Bloco | O que a página faz |
| --- | --- |
| Cabeçalho | Sobrancelha "Oficina do modelo · SVM". Atalho para `/model-2`. Título "Sondar o modelo. / Ver o que ele vê." |
| Seletor | Quatro kernels. Cada um mostra nome, acurácia e uma frase. |
| Entrada | Sliders das features que o kernel vê. |
| Saída | Fronteira de decisão e cartão da predição, ao vivo. |
| Estatísticas | Curva, viés/variância, hiperparâmetros do kernel escolhido. |
| Explicabilidade | Por que esta predição, com trechos recuperados. |
| Snapshot | JSON da entrada e da predição. |

Não há `id` de âncora. A rota inteira é a oficina.

## Contrato das rotas

Cada challenge repete a oficina: seletor de variante, o que entra, o que devolve, estatísticas, explicabilidade, snapshot. O número só entra se o notebook citado o escreve. Acurácia impressa em runtime e não salva no arquivo aparece como "—".

| Menu | Challenge | Rota | Notebook |
| --- | --- | --- | --- |
| Modelo | 001 churn | `/model-challenge-001` | `notebook-data-001-churn/04_ANALISE_retention/saas-retention-revenue-risk-analytics.ipynb` |
| Modelo | 002 support | `/model-challenge-002` | `notebook-process-002-support/04_ANALISE_supportiq/supportiq-customer-support-intelligence-platform.ipynb` |
| Modelo | 003 lead | `/model-challenge-003` | `notebook-build-003-lead-scorer/04_ANALISE_crm/0-2-do-crm-fields-actually-predict-deal-outcomes.ipynb` |
| Modelo | 004 social | `/model-challenge-004` | `notebook-marketing-004-social/04_ANALISE_social/social-media-engagement-analyser.ipynb` |

Header (desktop e menu mobile): **Modelo** é dropdown. Opções `001 churn`, `002 support`, `003 lead`, `004 social`, sem hash.

## O que cada oficina sonda

| Rota | Variantes | O que o notebook é |
| --- | --- | --- |
| 001 | Ciclo de vida, movimento de plano, coorte, país | Diagnóstico. Não há classificador. Taxas do snapshot `churn_flag`. |
| 002 | Floresta (150 árvores) e logística TF-IDF 5.000 | Dois classificadores da nota em Closed. Acurácia não arquivada. `resolution_hours` fica de fora da floresta. |
| 003 | Baseline AUC ≈ 0,526; core+vendedor ≈ 0,540; contexto ≈ 0,543 | Logística Won/Lost. `close_value` excluído. Perto do acaso 0,5. |
| 004 | Fusão XGB 300 árvores; bloco de texto; split por `creator_id` | Cinco quintis de taxa derivada. TF-IDF 15.000. Acurácia não arquivada. |

## Verificação

- [x] Quatro rotas respondem 200.
- [x] Header expõe `/model-challenge-001` … `/model-challenge-004`.
- [x] `/model` responde 404.

## Notas

Fonte dos hrefs: `modelPath` em `src/frontend/lib/research/stories.ts`. Texto da oficina: `src/frontend/lib/model/workshops.ts`.
