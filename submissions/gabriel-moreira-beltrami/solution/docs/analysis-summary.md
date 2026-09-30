# Síntese da análise dos dados

## Estrutura

`sales_pipeline.csv` é a tabela central: 8.800 oportunidades ligadas a `accounts` por `account`, a `products` por `product` e a `sales_teams` por `sales_agent`. Há 85 contas, 7 produtos e 35 vendedores. A grafia `GTXPro` aparece em 1.480 registros e foi normalizada para `GTX Pro` antes dos joins.

| Estágio | Oportunidades | Uso |
| --- | ---: | --- |
| Prospecção | 500 | Fila de primeiro contato; sem `engage_date`. |
| Em negociação | 1.589 | Fila de atenção; sem campos de fechamento. |
| Ganho | 4.238 | Histórico positivo. |
| Perdido | 2.473 | Histórico negativo. |

Os 6.711 negócios fechados formam o histórico de taxa de vitória. Os 2.089 abertos são as oportunidades pontuadas. `close_date`, `close_value` e o resultado final são campos pós-desfecho e não entram na pontuação.

## Achados que orientam a prioridade

- Produtos premium (`MG Advanced`, `GTX Pro`, `GTX Plus Pro`) representam 87,5% da receita ganha e têm conversão próxima à dos produtos de entrada. `GTX Plus Pro` (64,3% em 745 negócios fechados) e `GTX Pro` (63,6% em 1.147) são as prioridades premium mais bem sustentadas.
- `GTK 500` tem alto potencial de catálogo, mas apenas 25 negócios fechados. A regra usa cobertura de histórico para não deixá-lo dominar a fila só pelo preço.
- Receita, funcionários e idade da empresa exibem uma associação bruta fraca com valor ganho. Depois de controlar por produto, não acrescentam sinal útil para estimar o valor da mesma venda.
- Uma validação independente por empresa observou mudanças pequenas no mix de produtos por porte, mas melhoria de apenas 0,17% na previsão fora da amostra. Não há suporte para multiplicar o score por porte ou idade.
- 337 dos 500 leads em Prospecção não têm conta vinculada. Eles devem ser pesquisados e qualificados antes de receberem esforço comercial alto.

## Dados que fariam a próxima versão melhor

Uma tabela de atividades por `opportunity_id` com chamadas, e-mails, reuniões, direção, duração e resultado permitiria avaliar esforço comercial. Também são necessários origem do lead, atribuição, desconto, concorrente e timestamps de criação, troca de estágio e último contato.
