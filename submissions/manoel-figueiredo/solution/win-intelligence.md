# WIN INTELLIGENCE

## Objetivo
Aprender com resultados históricos Won/Lost sem alterar automaticamente o FocusScore.

## Dataset validado
- Total: 8.800
- Closed: 6.711
- Won: 4.238
- Lost: 2.473
- Open: 2.089
- Overall win rate: 63,2%

## Falha descoberta
A primeira execução mostrou Won 4.238, Lost 0 e win rate 100%.

Os Lost estavam arquivados no Odoo (`active=false`) e não eram devolvidos pela leitura inicial. Depois da correção, ativos e arquivados passaram a ser considerados.

## Dimensões
Sector, Product, Region, Sales Agent, Manager e Employee Band.

## Cruzamentos
Sector × Product, Region × Product, Region × Sector e Sales Agent × Product.

## Exemplos exploratórios
- telecommunications × MG Special: 85 fechados, win rate ~72,9%
- medical × MG Advanced: 164 fechados, win rate ~57,3%

## Robustez estatística
A versão atual calcula Wilson 95% CI, delta vs média, lift, comparação segmento vs restante universo, p-value, Benjamini-Hochberg FDR, shrinkage e evidência strong/moderate/weak.

## Próximo passo
Antes de recalibrar o FocusScore: split temporal, validação out-of-sample, análise multivariável, controlo de confundidores e teste do novo score.

## Limitação
Correlação não implica causalidade. Produto, região, setor, vendedor, manager e dimensão da empresa podem estar confundidos.
