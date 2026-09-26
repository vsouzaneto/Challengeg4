# Laudo do dado

**Em uma frase:** o arquivo não diz o que funciona, porque todo post rende igual dentro do sorteio; mas diz como a operação trabalha, e ela trabalha sem critério.

- **Resultado (views, likes, shares, comentários): sem sinal.** As quatro métricas se comportam como um sorteio em torno de valores fixos. A análise confere, grupo a grupo, cada comparação que o brief pede.
- **Operação (onde se posta, com quem, como se patrocina): sem critério.** Patrocinador sem relação com o conteúdo, patrocínio espalhado por quase todos os creators, divulgação implícita em quase metade dos casos.

Todos os números abaixo saem da seção 1 de [`notebooks/analise.ipynb`](notebooks/analise.ipynb) (indicada como §1.1, §1.2...) ou do script [`validacao_metodo_simulacao.py`](validacao_metodo_simulacao.py).

---

## Por que conferir antes de analisar

O Head de Marketing pediu "uma estratégia baseada em dados". Antes de perguntar o que dá mais engajamento, é preciso saber se o arquivo consegue responder. Foram quatro testes simples e uma prova de que o método funciona.

## Teste 1: cada número é um sorteio em torno de um valor fixo (§1.1)

Em redes sociais, é comum alguns posts viralizarem e outros não saírem do lugar. Aqui, o post com mais views tem só 9% a mais que o post com menos (10.551 contra 9.676).

Quando um número é sorteado ao acaso em torno de uma média fixa, a variação dele tem um tamanho conhecido: o desvio-padrão fica igual à raiz da média. É exatamente o que acontece:

| Métrica | Média | Desvio-padrão | Raiz da média | Índice de dispersão |
|---|---|---|---|---|
| views | 10.100 | 100,0 | 100,5 | 0,991 |
| likes | 1.510 | 38,9 | 38,9 | 1,003 |
| shares | 300 | 17,3 | 17,3 | 0,999 |
| comentários | 200 | 14,1 | 14,1 | 0,993 |

O **índice de dispersão** (variância dividida pela média) dá 1 quando só o sorteio explica a diferença entre os posts. Se plataforma, formato, creator ou patrocínio mudassem o resultado de muitos posts, o índice ficaria acima de 1. Ele fica entre 0,991 e 1,003. Este teste olha o arquivo inteiro de uma vez. Grupos pequenos, como uma combinação específica de plataforma e formato, são conferidos um a um na análise.

## Teste 2: o mesmo creator muda de tamanho a cada post (§1.2)

O número de seguidores de um creator muda devagar. No arquivo, **todos os 5.000 creators** aparecem com números diferentes de um post para outro. Na mediana, o maior número do mesmo creator é 13,8 vezes o menor. O gráfico da §1.2 mostra 12 creators pulando de "mid" para "macro" e de volta.

As faixas batem com um sorteio uniforme entre 1 mil e 1 milhão de seguidores:

| Faixa | No arquivo | Se fosse sorteio |
|---|---|---|
| nano (menos de 10 mil) | 0,9% | 0,9% |
| micro (10 a 50 mil) | 4,0% | 4,0% |
| mid (50 a 500 mil) | 45,2% | 45,0% |
| macro (500 mil ou mais) | 49,9% | 50,1% |

A correlação entre seguidores e views é 0,005 (zero é nenhuma relação). As views médias por faixa vão de 10.091 a 10.101.

**Consequência:** a faixa do creator não é uma característica confiável neste arquivo. Nenhuma conclusão desta entrega depende dela.

## Teste 3: proporções redondas e patrocínio distribuído ao acaso (§1.3)

Uma operação real não posta exatamente 60% em vídeo. No arquivo:

- **Formato:** vídeo 60,3%, imagem 19,7%, misto 10,0%, texto 10,0%.
- **Categoria:** beauty 40,3%, lifestyle 39,8%, tech 20,0%.
- **Idioma:** inglês 50,0%, chinês 20,0%, hindi 10,1%, espanhol 10,0%, japonês 9,9%.
- **Plataformas** entre 19,7% e 20,3%. **Oito países** do público entre 12,4% e 12,7%. **Seis categorias de patrocinador** entre 16,3% e 17,2%.

O patrocínio segue o mesmo padrão:

- **Patrocinador sem relação com o conteúdo.** Todo patrocinador, de games a cosméticos, aparece em cerca de 40% de posts de beauty, 40% de lifestyle e 20% de tech. O teste de independência dá p = 0,70, ou seja, nenhuma evidência de que o conteúdo dependa do patrocinador.
- **Patrocínio espalhado por quase todos.** Só 21 dos 5.000 creators nunca tiveram post patrocinado. Se o patrocínio fosse sorteado post a post, o esperado seria 15.
- **Divulgação fraca.** Entre os posts patrocinados, 47,2% têm divulgação implícita. Quanto ao lugar da divulgação, 27,4% estão só nas hashtags, 32,5% no vídeo e 40,1% na legenda.

## Teste 4: os textos são palavras sorteadas (§1.4)

Descrições, comentários e hashtags são palavras em inglês sem sentido. Um exemplo de descrição de um post de tecnologia: "Personal address produce affect young right those specific smile task usually Republic". Dos 20.877 posts marcados como chinês, japonês ou hindi, **nenhum** tem um caractere dessas línguas.

## O método acha efeitos quando eles existem (§1.5)

"Não achei nada" só vale se o método acharia algo que existisse. O script [`validacao_metodo_simulacao.py`](validacao_metodo_simulacao.py) planta efeitos conhecidos numa **cópia** do dado. Ele aumenta likes, shares e comentários de uma célula sorteada (uma combinação de plataforma, categoria, formato e faixa, com pelo menos 30 posts) e roda o mesmo método, 200 vezes para cada efeito. Nenhum número da análise vem dessa cópia. A saída fica em [`resultados/validacao_metodo_resumo.csv`](resultados/validacao_metodo_resumo.csv).

| Efeito plantado | Vira sinal | Percebido, mas abaixo do limiar | Efeito medido (média) | Outras células que viraram sinal por engano |
|---|---|---|---|---|
| +15% | 100% | 0% | +15,04% | 0 |
| +10% | 51,5% | 48,5% | +10,02% | 0 |
| +3% | 0% | 99,5% | +3,01% | 0 |

Como ler:

- **+15%** é sempre encontrado.
- **+3%** é percebido como real, mas não vira sinal: a regra existe para não tratar diferença pequena como descoberta.
- **+10%** é a fronteira. A regra pede diferença **acima** de 10%, e o efeito medido fica em torno de 10%, às vezes um pouco acima, às vezes um pouco abaixo. Por isso vira sinal em cerca de metade das rodadas. É o comportamento esperado de um limiar, não uma falha.
- Nenhuma célula sem efeito virou sinal por engano em 600 rodadas.

**A regra de sinal**, definida antes de comparar os grupos: a diferença precisa passar de 10% sobre a média dos outros posts, continuar confiável depois da correção para muitas comparações ao mesmo tempo (Benjamini-Hochberg, p ajustado abaixo de 0,05) e vir de pelo menos 30 posts. O código está em [`src/estatistica.py`](src/estatistica.py) e é coberto por testes automáticos.

## O que o brief promete e o arquivo não tem

- O brief lista uma coluna de "engagement rate". O CSV não tem essa coluna; o engajamento foi calculado como (likes + shares + comentários) / views.
- O brief fala em "distribuição" de idade, gênero e local do público. O CSV traz um único rótulo por post (por exemplo, "19-25"), não uma distribuição.

## O que isso quer dizer para a estratégia

1. **Perguntas sobre resultado não devem ter resposta neste arquivo.** "Vídeo engaja mais que imagem?", "patrocínio aumenta engajamento?", "qual público engaja mais?": com as métricas se comportando como sorteio, a expectativa é que nenhuma diferença passe do limiar. A análise mede cada uma, com margem de erro.
2. **O registro da operação é o diagnóstico.** Dentro da história do desafio, o arquivo é o que a empresa fez: patrocinou sem relação com o conteúdo, espalhou patrocínio por quase todos os creators e deixou a divulgação implícita em quase metade dos posts patrocinados. Isso se corrige com regras, sem esperar dado novo.
3. **Para saber o que funciona, é preciso gerar o dado.** Isso pede rastreamento e experimentos com tamanho de amostra calculado antes, que é o que a estratégia propõe.

## Limites deste laudo

- Os testes mostram que o arquivo se comporta como dado gerado por sorteio. Eles não provam como o arquivo foi gerado.
- O Teste 1 olha o arquivo inteiro: um efeito grande num grupo muito pequeno quase não mexe no índice. Por isso a análise testa cada grupo separadamente.
- Nada aqui diz o que funcionaria com dados reais da empresa.
