# Capacidade recuperada, despesa evitada e ROI

**Simulação para decisão; nenhum saving observado.** Cenários solicitados por Dhiego em 21/09/2026. Calculadora local em `/economia`; fórmulas em [economics.py](../solution/economics.py), com testes de casos positivos, negativos e sem conversão financeira.

## Referência salarial

Empregos.com.br informa **mediana de R$ 3.630/mês**, faixa central R$ 2.705–5.431 para analista de Customer Success, com atualização de 24/07/2026. A fonte combina registros formais e sua base e reconhece limites de enquadramento e remuneração variável. É referência aproximada para planejamento; CS não equivale a todos os cargos de suporte/CX. [Fonte consultada em 21/09/2026](https://www.empregos.com.br/salario/analista-de-customer-success).

Usamos **R$ 4.000 de salário bruto** como premissa editável, não como média nacional. Fator de custo total **1,7** → R$ 6.800/mês; **160 horas produtivas/mês** → R$ 42,50/h. Fator e horas são premissas de orçamento, não coeficientes legais nem dados medidos. Substituir por folha, benefícios e disponibilidade da operação.

## Premissas comuns

- 30.000 tickets/ano: contexto do desafio, não volume anual inferido dos arquivos.
- Implantação, integração e treinamento: R$ 6.000, hipótese a orçar.
- APIs, infraestrutura e manutenção: R$ 500/mês, hipótese a orçar. A comparação isolada de inferência não cobre esse custo total.
- Conversão de capacidade em despesa evitada: 50%, hipótese. Exige mecanismo concreto, como horas extras, fornecedor ou contratação evitada. Se não existir, usar 0%.
- Doze meses de operação constante, sem curva de adoção, valor do dinheiro no tempo, inflação ou impostos. Payback simples; não é previsão de calendário de implantação.

## Sensibilidade da eficiência

Todos os percentuais e minutos abaixo são hipóteses, não a acurácia do modelo, a cobertura do limiar ou as menções encontradas nos textos.

| Premissa / resultado | Conservador | Base | Otimista |
|---|---:|---:|---:|
| Elegibilidade | 20% | 40% | 60% |
| Uso efetivo entre elegíveis | 60% | 80% | 90% |
| Minutos líquidos por ticket | 2 | 4 | 6 |
| Tickets com uso/mês | 300 | 800 | 1.350 |
| Capacidade recuperada/mês | 10 h | 53,33 h | 135 h |
| Valor da capacidade/mês | R$ 425 | R$ 2.266,67 | R$ 5.737,50 |
| Despesa evitada/mês (50%) | R$ 212,50 | R$ 1.133,33 | R$ 2.868,75 |
| Saldo mensal após operação | −R$ 287,50 | R$ 633,33 | R$ 2.368,75 |
| Saldo no primeiro ano, incluindo implantação | −R$ 9.450 | R$ 1.600 | R$ 22.425 |
| ROI financeiro em 12 meses | −78,75% | 13,33% | 186,88% |
| Recuperação simples do investimento | Não recupera | 9,47 meses | 2,53 meses |

**Leitura:** o cenário base é positivo, mas com margem pequena. Nas mesmas condições, seriam necessários **3,53 minutos líquidos por ticket** para recuperar implantação e operação em doze meses. Se não houver despesa evitada, ainda haverá capacidade para reduzir fila ou absorver crescimento, porém o ROI financeiro será negativo com os custos assumidos. Não somar valor da capacidade e despesa evitada: esta já é uma parcela daquele.

## Memória de cálculo

```
Tickets com uso/mês = volume anual / 12 × elegibilidade × uso efetivo
Horas/mês = tickets com uso × minutos líquidos / 60
Custo/hora = salário bruto × fator de custo total / horas produtivas
Valor da capacidade = horas recuperadas × custo/hora
Despesa evitada = max(valor da capacidade, 0) × conversão em despesa evitada
Saldo mensal = despesa evitada − operação mensal
Custo de 12 meses = implantação + 12 × operação mensal
ROI de 12 meses = (12 × despesa evitada − custo de 12 meses) / custo de 12 meses
Payback = implantação / saldo mensal, somente se saldo > 0
```

Percentuais nas fórmulas são frações (40% = 0,4). ROI com custo total zero é indefinido. Minutos negativos representam trabalho adicional, mostrado como consumo de capacidade; não se presumem desembolsos de folha adicionais sem mecanismo real. O saldo financeiro não incorpora esse custo de oportunidade, que deve ser considerado na decisão.

## Aplicação aos três caminhos

Autosserviço: comparar tempo humano anterior com esforço residual, incluindo falhas/recontatos. Atendimento preparado: descontar leitura, revisão e correção. Investigação humana: medir se preparar contexto ajuda, permitindo ganho zero ou negativo. Usar grupos exclusivos e calcular o total pela soma dos minutos líquidos; não contar triagem e resolução integral duas vezes no mesmo ticket.

O cenário agregado da calculadora não estima a divisão entre os três caminhos. Validar essa divisão, elegibilidade e minutos no [piloto operacional](piloto-operacional.md). Não monetizamos retenção, CSAT ou resolução mais rápida sem medir relação causal e valor.
