---
status: passing
canonical: false
area: frontend
created: 2026-09-21
last_updated: 2026-09-21
---

# SPEC-020 Rotas da oficina de imagens por challenge

Reverse de `http://localhost:3020/model-2` (2026-09-21). A página Wisconsin permanece. Imagens no header passa a ser dropdown.

## Reverse — seções observadas

| Seção | O que é na página |
| --- | --- |
| Ranking de benchmark | Leaderboard de redes (acurácia, F1, AUC, latência) |
| Galeria de entrada | 36 patches histológicos 50×50 |
| Classificação | Rótulo do patch · arquitetura 3D e forward pass |
| Segmentação | Aba U-Net |
| Segmentação de imagem | Máscara por pixel (mock) |
| Estatísticas do modelo | Acurácia, F1, ROC-AUC, latência, precisão, recall, parâmetros, épocas |
| Matriz de confusão | TN/FP/FN/TP do holdout de 280 patches |
| Curva de aprendizado | Treino × validação por época |
| Viés / variância | Erro × complexidade |

## O que cabe em cada pacote

Leitura dos README de `notebook-*-00N`. Número de rede só entra se o Lab 04 o escreve. Traço = o notebook imprime e não arquiva.

| Seção | 001 churn | 002 support | 003 lead | 004 social |
| --- | --- | --- | --- | --- |
| Ranking | impacto (volume × taxa) | rota da fila aberta | AUC dos blocos | célula de taxa por view |
| Galeria de imagens | não | não | não | não |
| Entrada tabular | 5 CSVs | campos do ticket | campos anteriores ao desfecho | texto + metadados |
| Classificação | não | floresta e TF-IDF, sem número salvo | ranking, não classe dura | 5 quintis, sem número salvo |
| Segmentação / imagem | não | não | não | não |
| Acurácia, F1, precisão, recall | não | — | não (métrica é AUC) | — |
| ROC-AUC | não | não | ≈ 0,526 | código calcula, não grava |
| Latência, épocas | não | não | não | não |
| Parâmetros | não | 150 árvores | logística | 300 árvores |
| Matriz, curva | não | não salvas | não | não salvas |
| Viés / variância | não | não | sinal fraco (0,526 vs 0,5), sem curva | não |

| Menu | Rota |
| --- | --- |
| 001 churn | `/model-2-challenge-001` |
| 002 support | `/model-2-challenge-002` |
| 003 lead | `/model-2-challenge-003` |
| 004 social | `/model-2-challenge-004` |

## Dashboards (Lab 03)

Cada `lab03_dashboard.ipynb` ganha um tile de ranking que o README pedia e a página não inventa:

| Pack | Tile novo |
| --- | --- |
| 001 | País por volume de `churn_events`, não por taxa |
| 002 | Contagem de `route` na fila aberta |
| 003 | Produto órfão no pipe aberto (`GTXPro` depois do replace) |
| 004 | Top 15 de `eng_per_view` com `NULLIF(views, 0)` |

## Verificação

- [x] Quatro rotas respondem 200.
- [x] Header expõe `/model-2-challenge-001` … `004`.
- [x] `/model-2` continua no ar.
