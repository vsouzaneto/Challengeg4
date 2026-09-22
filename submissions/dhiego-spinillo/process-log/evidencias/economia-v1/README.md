# Evidências — resumo executivo e cenários econômicos

Capturas do aplicativo local em 21/09/2026. Docker, rota `/economia` e `/resumo`. Valores de eficiência e custos são hipóteses; capturas não demonstram saving operacional.

| Captura | Estado reproduzido |
|---|---|
| [Cenário base em desktop](base-desktop.png) | 30 mil tickets/ano, 40% elegíveis, 80% uso, 4 minutos; salário 4 mil × 1,7 / 160h; conversão 50%, operação R$500/mês, implantação R$6 mil. Resultado: 53,33h/mês e ROI 13,33% em 12 meses. |
| [Sem despesa evitada](sem-despesa-evitada.png) | Mesmo cenário, conversão 0%. Mantém 53,33h e mostra R$0 de despesa evitada; ROI financeiro −100%. |
| [Conservador no celular](conservador-mobile.png) | Selecionar Conservador com demais custos padrão e conversão 50%: 10h/mês e ROI −78,75%. |
| [Resumo em desktop](resumo-desktop.png) | Síntese dos dados, experimento, fronteiras e proposta de evolução; links para memória de cálculo. |
| [Resumo no celular](resumo-mobile.png) | Mesma informação, colunas empilhadas e navegação com quebra de linha. |

Verificação visual em 1440×1000 e 390×844. A calculadora pede recálculo quando uma premissa muda; a API valida faixas e números finitos. Nenhum ticket ou dado operacional é enviado a IA para esses cálculos. Capturas do atendimento atual estão em [investigação v2](../investigacao-v2/README.md); os caminhos autônomos propostos não têm capturas de funcionamento porque ainda não foram implementados.
