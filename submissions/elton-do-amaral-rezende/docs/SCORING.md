# Motor de prioridade

Versão: **candidate-v1:full**, implementada com os pesos originais do plano. Eles foram mantidos antes da avaliação final; não houve busca de pesos ou ajuste pelo resultado de setembro–dezembro.

```text
score = round(100 × (0,65H + 0,25A + 0,10V))
H = 0,50 × taxa_produto + 0,30 × taxa_setor + 0,20 × taxa_conta
 taxa_grupo = (vitórias + 20 × taxa_global) / (encerrados + 20)
A = exp(-idade / (2 × mediana_do_ciclo))
V = (log(1 + preço) - log(1 + menor_preço)) / (log(1 + maior_preço) - log(1 + menor_preço))
```

Histórico considera somente Won/Lost com fechamento até `asOfDate`. O contrato `ScoringOpportunity` não possui resultado, data de fechamento nem receita realizada do candidato. O ranking operacional inclui somente Prospecting e Engaging; score decrescente, ID crescente para desempate.

## Fallbacks e explicações

- Segmento ausente ou sem histórico usa taxa global; histórico vazio usa 0,5. Contagem e taxa usada são explicitadas no texto.
- Mediana por produto é usada quando positiva; caso contrário, mediana global. Sem mediana positiva ou data de engajamento, A=0,5.
- Sem preço positivo, catálogo vazio ou sem variação, V=0,5. Normalização é limitada a 0–1.
- Contribuições são armazenadas sem arredondar. A interface mostra uma casa decimal por fator; o total é arredondado somente ao final, portanto a soma dos rótulos pode diferir ligeiramente do total.
- Prospecting recebe ação de qualificação e declaração de tempo desconhecido. Engajamentos antigos pedem revisão de situação; não inventam silêncio, proposta, urgência ou contato.

Contagem de amostra não é confiança estatística calibrada. Cadastro ausente é sinalizado; não penaliza automaticamente a prioridade. A versão sem V renormaliza os outros pesos para somar 1; a versão sem A faz o mesmo. São comparações previamente definidas, não versões escolhidas após o resultado final.

## Dois relógios e rotina

Score e idade usam 31/12/2017 na demonstração. Cabeçalho, ações, adiamentos e sequência usam datas reais em America/Sao_Paulo. Amanhã é calculado pelo calendário, não adicionando 24 horas a um timestamp. Seleção, feito e adiar não alteram o score ou estágio comercial.

A fila congela ranking e posição durante o lote. Cada dia exclui feitos e adiados com retorno futuro. Retornos vencidos ficam primeiro no início do dia, ordenados por score. Desfazer em lote anterior usa fila explícita; o lote corrente não passa de dez itens. A meta é fixada com o volume inicial do dia; adiar não a reduz.

Estado é validado, isolado por dataset/vendedor e persistido no navegador. Não sincroniza abas/dispositivos nem comprova identidade. Dias sem oportunidades não geram meta conquistada. Desfazer recalcula os totais e a sequência. O score é um índice operacional, sem validação como probabilidade de fechamento.
