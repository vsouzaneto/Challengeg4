# Case 003 — auditoria inicial dos dados

Fonte indicada pelo [brief do G4](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/challenges/build-003-lead-scorer/README.md): [CRM Sales Predictive Analytics, Kaggle](https://www.kaggle.com/datasets/agungpambudi/crm-sales-predictive-analytics), licença CC0. Download público pela API do Kaggle em 09/10/2026, sem login. SHA-256 do ZIP: `74d535826330b616758ebb6bb393abf701a5126364a72fbe71003cb6a7a87a9c`. Os CSVs ficam em `data/`, fora do Git; `python audit.py` reproduz contagens, campos e hashes individuais.

| Tabela | Linhas |
| --- | ---: |
| `sales_pipeline.csv` | 8.800 |
| `accounts.csv` | 85 |
| `products.csv` | 7 |
| `sales_teams.csv` | 35 |
| `metadata.csv` | 21 |

Há 4.238 Won, 2.473 Lost, 1.589 Engaging e 500 Prospecting. Não há `opportunity_id` duplicado, referências a vendedores ou contas inexistentes, datas de fechamento anteriores às de engajamento, nem fechamento preenchido em oportunidades abertas. A data mais recente dos arquivos é 31/12/2017; usá-la como data de referência do protótipo evita apresentar esses negócios como atuais.

Dois problemas exigem tratamento explícito: 1.480 linhas trazem o produto `GTXPro`, enquanto o catálogo usa `GTX Pro`; a normalização é uma equivalência nominal documentada. Em 1.425 oportunidades abertas a conta está vazia, então setor e tamanho da conta não podem ser requisitos para gerar a fila.

## Hipótese descartada antes do produto

Testamos uma afinidade histórica suavizada por produto e setor, sem usar `close_value` como entrada. Os negócios encerrados foram divididos cronologicamente: 5.343 para ajuste e 1.368 para teste, a partir de 03/11/2017. O AUC da afinidade foi **0,4854**; o quartil de maior afinidade teve **63,45%** de Won, contra **64,84%** no teste inteiro. A hipótese não ofereceu discriminação útil e não deve aparecer como chance de fechamento.

O CSV só contém o estágio **final** dos negócios fechados. Não há histórico de mudanças de estágio, atividades ou próximos passos. Portanto, uma regra operacional de urgência pode ser verificada por comportamento e utilidade, mas não validada retrospectivamente como preditor completo de fechamento. A escolha do produto será apresentada como índice de ação, com critérios explícitos e limites claros.

Comandos: `python audit.py` e `python evaluate.py`. Ambos usam apenas a biblioteca padrão de Python.
