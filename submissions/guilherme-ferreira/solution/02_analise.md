# Análise: o que o arquivo responde

**Em uma frase:** neste arquivo, nenhuma escolha de plataforma, formato, categoria, público, patrocínio, horário ou hashtag muda o resultado dos posts; o que ele mostra é uma operação que patrocina sem critério.

Todos os números saem da seção 2 de [`notebooks/analise.ipynb`](notebooks/analise.ipynb) (indicada como §2.1, §2.2...). O porquê de o arquivo se comportar assim está no [laudo do dado](01_laudo_do_dado.md).

## Resposta curta

| Pergunta do Head de Marketing | Resposta | Onde |
|---|---|---|
| O que gera engajamento? | Nada que o arquivo consiga medir. Nenhuma das 240 comparações de plataforma, categoria e formato passa perto do limiar: a maior diferença é de 0,86%. | §2.1 |
| Patrocínio funciona? | Pelo resultado, patrocinado e orgânico rendem igual: -0,01% de engajamento, mesmo comparando só posts da mesma plataforma, categoria e formato. O custo não está no arquivo. | §2.2 |
| Em que condições? | Nenhuma condição muda o resultado. O que muda é o risco: patrocinador sem relação com o conteúdo em 60,1% dos casos, divulgação implícita em 47,2%. | §2.2 |
| Qual audiência mais engaja? | Nenhuma. Idade, gênero e país ficam no máximo a 0,06% do resto. | §2.3 |
| O que não funciona? | Pelo resultado, nada fica abaixo do resto. Pela operação, há quatro práticas sem critério (fim deste documento). | §2.4 |
| Onde concentrar? Com que frequência? | O arquivo não sustenta concentrar em plataforma, formato, dia ou horário. Postar mais num dia não mudou o engajamento. | §2.5 |

## Como ler os números

- **Diferença** é o quanto um grupo de posts rende acima ou abaixo de todos os outros posts. O **intervalo** mostra onde a diferença real provavelmente está, com 95% de confiança.
- **Sinal** segue a regra do laudo: a diferença tem que passar de 10%, continuar confiável depois da correção para muitas comparações ao mesmo tempo e vir de pelo menos 30 posts.
- **Faixa do creator** (nano, micro, mid, macro) aparece só para completar as perguntas do brief. Como o número de seguidores muda a cada post (laudo, teste 2), nenhuma conclusão depende dela.

## 1. O que gera engajamento? (§2.1)

**Uma característica por vez.** Nenhuma plataforma, formato ou categoria se afasta do resto em mais de 0,05%. Vídeo, que é a resposta "óbvia" que o brief pede para evitar, fica em -0,03% (intervalo de -0,07% a +0,01%).

**Combinações.** São 60 combinações de plataforma, categoria e formato (a menor tem 187 posts), olhadas para quatro objetivos diferentes:

| Objetivo | Comparações | Viraram sinal | Maior diferença |
|---|---|---|---|
| Engajamento geral | 60 | 0 | +0,28% |
| Alcance (views) | 60 | 0 | -0,16% |
| Conversa (comentários por view) | 60 | 0 | +0,86% |
| Compartilhamento (shares por view) | 60 | 0 | +0,66% |

O gráfico da §2.1 mostra as 60 células de engajamento: todas coladas no zero, com o limiar de 10% longe dos dois lados.

**O que isso quer dizer:** com este arquivo, não há como justificar pelo resultado a escolha de uma plataforma, formato ou categoria.

## 2. Patrocínio funciona? Em que condições? (§2.2)

**Resultado.** A comparação justa olha só posts da mesma plataforma, categoria e formato, para que diferenças de mix não se passem por efeito do patrocínio.

| Objetivo | Patrocinado contra orgânico (comparação justa) | Intervalo de 95% |
|---|---|---|
| Engajamento | -0,01% | de -0,05% a +0,04% |
| Alcance (views) | +0,00% | de -0,01% a +0,02% |
| Conversa | +0,02% | de -0,11% a +0,14% |
| Compartilhamento | -0,04% | de -0,15% a +0,06% |

A comparação direta, com todos os patrocinados contra todos os orgânicos, dá praticamente os mesmos números. Entre os patrocinados, nenhuma condição muda o resultado em mais de 0,1%: divulgação explícita ou implícita, divulgação na legenda, no vídeo ou nas hashtags, categoria do patrocinador, patrocinador que combina ou não com o conteúdo.

**Custo.** O arquivo não tem nenhuma coluna de custo. Sem custo, não há ROI. A estimativa de custo implícito fica na estratégia, como premissa declarada.

**Como a operação patrocina.** Independentemente do resultado, o registro mostra as escolhas feitas:

- **Sem foco.** 42,7% dos posts são patrocinados, e essa parcela é praticamente a mesma em todo lugar: de 41,9% a 43,5% por plataforma, de 42,5% a 43,1% por categoria, de 42,4% a 42,9% por formato. Só 21 dos 5.000 creators nunca foram patrocinados (laudo, teste 3).
- **Sem relação com o conteúdo.** O patrocinador combina com o conteúdo em 39,9% dos posts patrocinados, exatamente o que daria se a escolha fosse sorteada (39,9%). "Combinar" segue um mapa declarado como premissa: cosméticos com beauty; moda com beauty e lifestyle; eletrônicos e games com tech; comida e viagem com lifestyle.
- **Sem parceria recorrente.** São 18.005 patrocinadores diferentes para 22.314 posts patrocinados, e 90,0% deles aparecem num post só. O que mais aparece tem 32 posts.
- **Divulgação fraca.** 47,2% dos patrocínios têm divulgação implícita, e 27,4% ficam só nas hashtags.

## 3. Qual audiência mais engaja? (§2.3)

Nenhuma faixa etária, gênero ou país se afasta do resto em mais de 0,06%. Combinando cada rótulo de público com plataforma, formato e categoria, são 204 comparações: nenhuma virou sinal, e a maior diferença é de 0,23%.

Uma ressalva: o brief fala em "distribuição" de público, mas o arquivo tem um único rótulo por post (por exemplo, "19-25"). Para responder de verdade, cada post precisaria trazer a distribuição real de quem o viu, que é um dos itens do plano de rastreamento.

## 4. O que não funciona? (§2.4)

- **Pelo resultado, nada fica abaixo do resto.** Não há formato ou plataforma para cortar por desempenho ruim.
- **O arquivo não tem fracassos.** O brief alerta para o viés de sobrevivência: quantos posts tiveram engajamento zero? Nenhum. Todo post fica entre 17,9% e 22,2% de engajamento, e o que tem menos views tem 9.676. Ou a base guardou só posts que deram certo, ou os números foram gerados. Nos dois casos, o arquivo não mostra o que fracassa.
- **Uma lista de "melhores hashtags" seria escolhida por acaso.** Das 972 hashtags, 970 aparecem em pelo menos 100 posts e foram testadas. Sem a correção para muitas comparações, 59 pareceriam campeãs ou vilãs. Depois da correção, nenhuma é confiável, e a maior diferença é de 0,72%.

## 5. Onde concentrar e com que frequência? (§2.5)

- **Volume:** 71,4 posts por dia em média (de 31 a 98), ao longo de 731 dias. Isso dá 14,3 por plataforma por dia e 10,4 posts por creator em dois anos.
- **Mais posts no dia não mudaram o engajamento do dia.** A correlação é de 0,070, sem significância (p = 0,06).
- **Dia da semana, hora, mês e duração do vídeo por categoria:** 80 comparações, incluindo o exemplo do brief ("vídeos de 30 a 60 segundos") para engajamento e para compartilhamento. Nenhuma virou sinal, e a maior diferença é de 0,32%.

**O que isso quer dizer:** onde concentrar tem que sair do objetivo do negócio e de testes, não deste arquivo. A estratégia traz os testes.

## Para decidir: o que a operação faz sem critério

Nenhum desses pontos depende do resultado dos posts. Todos se corrigem com regras.

| Prática | Número | Onde |
|---|---|---|
| Patrocinar sem relação entre patrocinador e conteúdo | 60,1% dos posts patrocinados | §2.2 |
| Divulgação implícita ou só em hashtag | 47,2% implícita; 27,4% só nas hashtags | §2.2 |
| Patrocínio espalhado sem foco | cerca de 43% em toda plataforma, categoria e formato; 4.979 de 5.000 creators | §2.2 e laudo, teste 3 |
| Parcerias de um post só | 90,0% dos 18.005 patrocinadores | §2.2 |

Há também um problema de registro: o número de seguidores muda a cada post do mesmo creator (laudo, teste 2), então hoje não dá para escolher creator por tamanho com este dado.

## Limites

- "Sem diferença" aqui quer dizer "nenhuma diferença acima de 10%, e nenhuma confiável". Não quer dizer que patrocínio, formato ou horário não importem no mundo real; quer dizer que este arquivo não permite saber.
- O mapa de patrocinador que "combina" com o conteúdo é uma premissa, e outro mapa mudaria o 60,1%. Mas, com qualquer mapa, a parcela observada ficaria igual à esperada num sorteio, porque patrocinador e conteúdo são independentes (laudo, teste 3).
- A unidade de `content_length` não é documentada. Em vídeo, tratamos como segundos.
