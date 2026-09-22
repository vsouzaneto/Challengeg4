# Recap: resultado exploratório, ainda não aprovado para adoção

O gerador Claude Sonnet5 recebeu16textos do D2, com4por faixa de comprimento (menos de20,20–49,50–99,100+palavras). A escolha veio do teste de categoria com seed própria20260921; não usamos rótulos de categoria como referência de resumo. Essa amostra enfatiza diversidade de comprimento, não representa proporcionalmente a base.

## Primeiro, uma falha de integração

A primeira rodada teve2/16saídas aceitas e14falhas. Em um exemplo separado do treino usado para diagnóstico, constatamos JSON válido envolto num bloco Markdown apesar de `json_mode`. Corrigimos apenas a leitura de um único invólucro completo; não reparamos campos, fatos ou citações. Testes cobrem prosa adicional, blocos incompletos/duplicados e citações inventadas.

A primeira rodada está preservada em `reports/recap-evaluation-initial/`. Ela não reteve o corpo bruto de todas as falhas, portanto não atribuímos individualmente as14 ao mesmo problema. A segunda rodada registra também respostas brutas disponíveis. O prompt e a seleção dos16textos foram mantidos, mas são novas chamadas; a geração pode variar.

## Segunda rodada

- **15/16** saídas passaram pelo esquema e pela verificação de presença literal de todas as citações; um caso falhou antes de disponibilizar um recap válido.
- **15** saídas foram avaliadas por Grok4.7 usando a rubrica congelada e o texto original, sem ver parecer de outro avaliador.
- Aprovações do revisor automatizado: **fidelidade6/15; cobertura14/15; preservação de tentativas15/15; incerteza11/15; próximo passo15/15**.

[Resumo e objeções](reports/recap-evaluation/summary.json) · [Manifesto, prompt e rubrica](reports/recap-evaluation/manifest.json).

O revisor apontou, por exemplo, possível inferência de urgência a partir de `currently out`, atribuição de autoria a partir de uma assinatura fragmentada e resolução anterior inferida de uma cadeia sem cronologia. Essas objeções são sinais para revisão; não apresentamos o veredito de Grok como verdade humana nem os percentuais como acurácia operacional.

## Decisão

O recap permanece **experimental e desligado por padrão**, acessível para investigação com revisão do texto. O núcleo entregue é a classificação com confirmação humana. Citação real não garante que a paráfrase ou a conclusão estejam corretas. Falha de recap mantém a classificação disponível e aparece explicitamente na interface.

Não foi medido ganho de tempo, redução de retrabalho ou benefício ao cliente. Antes de adoção, precisamos de conversas completas, referência humana, critérios de erro relevantes à operação e amostra separada para nova avaliação. A revisão do candidato, quando ocorrer, deve ser registrada como evidência própria, não retroativamente atribuída às notas do revisor automatizado.
