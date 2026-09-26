# Baseline: o enunciado cru num Claude sem contexto

O que uma IA entrega quando recebe só o enunciado e o CSV, sem nada do meu trabalho, e onde a minha entrega vai além.

## Como foi feito

- **Mesmo fornecedor de IA:** Claude Opus 5.5, o mesmo modelo da sessão de trabalho, rodando no Claude Code em modo seguro, que desliga CLAUDE.md, skills, plugins, hooks e servidores MCP. A memória também ficou de fora: a pasta de trabalho era nova.
- **Entrada:** o enunciado do desafio sem nenhuma alteração, mais uma nota com o caminho do CSV e do Python ([`prompt.md`](prompt.md)). Pasta nova, com o CSV e os arquivos da própria execução (o prompt e os de registro de tempo e saída). Busca na web e subagentes bloqueados.
- **Execução:** 4 minutos, 10 turnos, US$ 1,01, nenhuma permissão negada. A resposta final está em [`resposta.md`](resposta.md); os arquivos que ele criou estão em [`arquivos/`](arquivos/), sem edição; a sessão inteira está em [`transcript.md`](transcript.md).
- **Isolamento conferido de duas formas:** um teste na mesma configuração perguntou ao modelo se ele tinha recebido CLAUDE.md, memória ou regras (resposta: "NENHUMA"), e o registro da sessão do baseline não tem nenhum anexo de instruções.
- **Primeira tentativa descartada.** Rodou como subagente da sessão de trabalho e herdou o meu CLAUDE.md global e o do projeto, que descreve o meu método (limiar de 10%, Benjamini-Hochberg, mínimo de 30 posts). A IA parou o agente antes do fim, e nada dele foi usado.

## O que o baseline acertou

Sozinho, em 4 minutos, ele chegou à conclusão da camada de resultado:

- as métricas variam como sorteio em torno de valores fixos;
- o mesmo creator muda de número de seguidores a cada post, e o alcance não depende de seguidores;
- nenhum post fracassou, o que aponta para viés de sobrevivência ou dado gerado;
- das 970 hashtags, 59 parecem "significativas" sem correção e nenhuma depois;
- patrocínio não muda o engajamento, e sem custo não há ROI;
- a "distribuição" de audiência é um rótulo só por post.

**Consequência para a entrega:** "não há sinal no resultado" é o que a IA acha sozinha quando pode rodar código. O README não trata essa conclusão como diferencial.

## O que ele fez e eu não fiz

- Conferiu se o "melhor segmento" de um ano se repete no ano seguinte: não se repete, e a correlação entre os rankings dos dois anos é 0,10. Ele também só aceita como sinal o que aparece nas duas metades do período. A minha regra não tem essa checagem de estabilidade.
- Mostrou que a mistura de idiomas é a mesma em todas as plataformas, inclusive nas chinesas Bilibili e RedNote. Conferi no dado, e confere: o inglês fica perto de 50% nas cinco plataformas (comando e saída no transcript da sessão 1).
- Mostrou a armadilha de dividir engajamento por seguidores: com essa conta, creators pequenos parecem engajar 100 vezes mais.
- Testou um modelo de previsão em um período que ele não usou para treinar. O modelo prevê pior do que a média.

## Onde ele erra ou se contradiz

1. **Diz que a maior diferença entre dois grupos quaisquer fica abaixo de 0,3%**, mas o próprio texto cita um segmento com +0,56% em 2023-24. Nas células da minha análise, a maior diferença chega a 0,86%, no objetivo conversa ([análise](../../../solution/02_analise.md), §2.1). Em todos os casos, longe de 10%.
2. **Controla a comparação de patrocínio pelo tamanho do creator** depois de mostrar que o número de seguidores muda a cada post. Controlar por uma coluna sorteada não deixa a comparação mais justa. Na minha entrega, nenhuma conclusão depende do tamanho do creator ([laudo](../../../solution/01_laudo_do_dado.md), teste 2).
3. **Recomenda começar com creators de 10 mil a 100 mil seguidores** porque custariam menos por post. Não há custo no arquivo nem fonte para a afirmação, e a faixa é justamente a coluna que ele mostrou não ser confiável. Na minha estratégia, o tamanho do creator é uma hipótese a testar (H3), e o custo é uma premissa declarada e ajustável.
4. **Não mostra que o método acharia um efeito se ele existisse.** "0 de 19 segmentos com sinal" também seria o resultado de um método fraco. O meu laudo planta efeitos conhecidos numa cópia do dado: +15% vira sinal em todas as rodadas, e nenhum sinal falso aparece em 600 ([laudo](../../../solution/01_laudo_do_dado.md), §1.5).
5. **Escreve o process log como se fosse o candidato** ("Decisão que tomei"), com decisões que a própria IA tomou. É o tipo de registro que o avaliador chamou de template gerado por IA.

## O que ele não viu

- **A operação de patrocínio.** Ele olhou divulgação e categoria do patrocinador só como possíveis causas de engajamento. Não viu que 47,2% dos patrocínios têm divulgação implícita e 27,4% ficam só nas hashtags, um risco legal (FTC nos EUA, CONAR no Brasil); que o patrocinador não tem relação com o conteúdo em 60,1% dos casos; nem que 90,0% dos 18.005 patrocinadores aparecem num post só ([análise](../../../solution/02_analise.md), §2.2). A política de patrocínio da minha entrega sai daí, e as práticas atingem 94,3% dos posts patrocinados ([estratégia](../../../solution/03_estrategia.md), seção 3).
- **Donos, métricas e condição de revisão** para cada regra, e hipóteses com guardrail e nota ICE.
- **Amostra calculada para o volume real.** Ele estima "entre 200 e 400 posts por grupo" para detectar 15% a 20%, sem a conta. A minha: 393 posts por grupo para detectar 20%, cerca de 4 semanas com os 214 posts patrocinados por semana ([estratégia](../../../solution/03_estrategia.md), seção 5).
- **Uma ferramenta que o Head use em 5 minutos.** O `signal_check.py` dele roda na linha de comando. O Radar é uma aplicação de quatro telas, com o brief de segunda-feira e a calculadora de teste.
