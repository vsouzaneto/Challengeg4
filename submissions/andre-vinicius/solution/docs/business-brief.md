# Case 003 — brief de produto

Resumo do ponto de partida. A especificação completa, com regras numeradas e rastreabilidade para código e testes, está em [business-spec.md](business-spec.md).

## Problema e usuário

O [brief oficial do G4](https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/challenges/build-003-lead-scorer/README.md) descreve um vendedor que abre o pipeline e precisa decidir onde agir primeiro. O usuário primário deste protótipo é esse vendedor; o manager pode filtrar a própria região/equipe para acompanhar a fila. O objetivo é reduzir tempo perdido com uma lista de próximas ações compreensível, sem tratar dados históricos frágeis como previsão de fechamento.

## Três decisões que a tela deve apoiar

1. Quais conversas engajadas ainda estão recentes o bastante para avançar agora?
2. Quais oportunidades antigas precisam ser confirmadas, atualizadas ou encerradas?
3. Quais oportunidades em prospecção precisam de primeiro contato e cadastro completo?

## Critérios de aceite

- Abrir localmente com os quatro CSVs indicados pelo G4 e sem serviço externo ou dependência paga.
- Mostrar somente oportunidades abertas, com filtro por vendedor, manager e região.
- Explicar a fila, o índice de atenção e uma próxima ação para cada oportunidade.
- Normalizar `GTXPro` para `GTX Pro` e lidar com conta ausente sem falhar.
- Não ler `close_date`, `close_value` ou o resultado `Won/Lost` para pontuar uma oportunidade aberta. A referência histórica é fixa em 31/12/2017; datas de fechamento servem apenas para a avaliação separada da hipótese histórica.
- Incluir instruções reproduzíveis, testes relevantes, limites e evidências reais do processo.

## Limite da solução

O dataset é de uma empresa fictícia e termina em 2017. O índice não é probabilidade de fechar nem recomendação automática para descartar negócios. A fila é uma hipótese operacional que precisaria ser validada com o time comercial e métricas reais de tempo, avanço e conversão antes de uso produtivo.

## Descoberta com usuários para uma próxima versão

Antes de adaptar a solução a uma operação real, conversar com vendedores e gerentes sobre como hoje escolhem a próxima oportunidade, onde perdem tempo, que informação consideram confiável e quais ações gostariam de registrar. Comparar as respostas com o uso observado em uma tarefa concreta; então priorizar uma mudança pequena e medir se ela ajudou. Essa pesquisa ainda não foi realizada no case e não fundamenta os pesos atuais.
