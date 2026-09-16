# Piloto de 30 dias: triagem automática em uma categoria

## O que vamos passar a registrar

A extração que recebi guarda a hora da primeira resposta e a hora da resolução, e nada mais; se esses registros existirem em outra tabela do sistema, o piloto só precisa ligá-los. Com isso não dá para saber onde o tempo se perde: se é na fila antes de alguém pegar o ticket, se é nas trocas entre equipes, ou se é esperando o cliente responder. O piloto começa registrando oito informações por ticket, cada uma para responder uma pergunta.

Hora de abertura, para medir quanto tempo o ticket espera até alguém olhar. Hora do primeiro toque humano, para separar espera de trabalho. Cada encaminhamento entre filas, com hora, para ver quantas vezes o ticket muda de mão e quanto tempo se perde em cada troca. Tempo esperando o cliente, para não contar como lentidão nossa o que é lentidão dele. Hora da resolução. Se foi reaberto, porque um ticket reaberto é trabalho feito duas vezes. A categoria que a máquina sugeriu e com que confiança. E a categoria final, decidida pela pessoa.

As duas últimas são o mecanismo de melhoria: toda vez que a pessoa corrige a máquina, a correção vira um exemplo novo para treinar. Não é preciso nenhum projeto para isso; é uma coluna a mais no sistema de tickets. Pelos dados de treino, a categoria mais fraca melhora um ponto a cada 160 correções, mais ou menos, o que a operação inteira produz em cerca de oito semanas.

## Como o piloto funciona

Uma categoria só, durante 30 dias. Recomendo a de acesso a sistemas, senhas e contas, que corresponde a cerca de 15% do volume, uns 370 tickets por mês, e onde a máquina acertou 96% das vezes em que se sentiu segura para decidir. Não começar por hardware, pois é onde a máquina despeja o que não entende, nem por direitos administrativos, onde os dados de treino têm rótulos errados e precisam ser corrigidos antes.

Como ninguém sabe a categoria antes de ler, o classificador roda em todos os tickets que entram, e o piloto vale para os que ele aponta como acesso. Metade desses tickets, sorteada ticket a ticket, passa pela triagem automática: a máquina classifica e encaminha quando tem confiança, e manda para uma pessoa quando não tem. A outra metade segue exatamente como hoje. No fim de 30 dias, comparamos as duas metades em três números: tempo de espera até o primeiro toque humano, quantas vezes a pessoa reverteu a decisão da máquina, e quantos tickets a máquina decidiu sozinha.

Custo do piloto: o classificador roda num computador comum e não usa serviço pago. O custo é o tempo de uma pessoa revisando as reversões, que estimo em 15 minutos por dia; é premissa, não medição, e o piloto registra o tempo real. Com cerca de 185 tickets em cada metade, diferenças pequenas de tempo de espera não serão visíveis em 30 dias; o piloto detecta diferenças grandes, e o tamanho do efeito mínimo fica para ser calculado com a primeira semana de dados.

## O que decide o resultado

A regra é definida agora, antes de começar, para que o piloto não vire demonstração.

Se as pessoas reverterem menos de 5% das decisões da máquina e o tempo de espera cair, expandimos para a categoria seguinte, na ordem de acerto medido: armazenamento, depois diversos e compras; RH e direitos administrativos ficam por último, porque concentram os casos que exigem pessoa. Se a reversão ficar entre 5% e 10%, mantemos a categoria e ajustamos o nível de confiança exigido, sem expandir. Se passar de 10%, ou se o tempo de espera não cair, desligamos a triagem automática nessa categoria e voltamos aos dados para entender por quê.

Independentemente do resultado, a primeira ação de melhoria já está definida: reclassificar os tickets de direitos administrativos, porque a leitura dos erros mostrou que boa parte estava rotulada errado na origem. Nenhum modelo maior compensa dado de treino errado.