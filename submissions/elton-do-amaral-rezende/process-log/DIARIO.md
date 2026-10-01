# Diário do Lead Scorer

## 1º passo — escolhendo o desafio

Joguei o repo do desafio no meu ChatGPT acompanhado do seguinte prompt:

> Seguinte, estou participando de um desafio que é uma etapa qualificatória para uma entrevista de emprego, o uso de IA é 100% liberado, então quero que me ajude para que não só resolvamos o desafio mas superemos as expectativas, segue abaixo o repo do desafio, quero que analise os challenges e com base na minha expertise faça um ranking de qual desafio tenho maiores chances de superar as expectativas.
>
> https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge

A conversa ficou aqui: [análise dos desafios no ChatGPT](https://chatgpt.com/c/6ab702e2-6f20-83e9-a123-c83a01136231).

Depois da análise decidi que o Lead Scorer realmente era onde eu tinha mais chances de brilhar, afinal isso é exatamente o que eu venho construindo no Agiliza Corretagem. Porém, ali no chat ele não tinha todo o contexto do CRM que eu construí, então fui para o Codex dentro do meu repo do CRM para pensar na solução com esse contexto disponível.

## 2º passo — dando um passo para trás

Depois de conversar com o GPT por dentro do meu repositório, traçamos um plano de como iríamos construir a solução, porém achei que ele deixou tudo complexo demais. Então decidi dar um passo para trás e pensar primeiro em como seria a interface final para o usuário, que aqui é o vendedor.

Ela vai ser o principal ponto de contato dele com a solução, então é aqui onde temos que mais acertar. Nos bastidores fica a lógica do que mostrar, mas na frente ele precisa entender rápido o que fazer.

Voltei ao ChatGPT e pedi para ele imaginar algumas telas, porém achei que ele estava enviesado pela memória e pelo contexto de tudo que converso com ele. As telas ficaram muito parecidas com as do meu CRM, e não achei que aquilo fosse resolver o que eu queria aqui.

Então fui para o Claude. A ideia era ter algo simples, mostrando apenas as prioridades que o vendedor precisa trabalhar naquele dia, com um pouco de gamificação para incentivar a rotina. A tela que saiu dessa conversa virou a referência visual do projeto, que depois transformamos na aplicação que vocês têm acesso agora.

## 3º passo — saindo do plano e começando a construir

**30 de setembro de 2026**

Com a ideia da tela mais clara, fui para o repositório novo e pedi ao Codex para criar a base do projeto seguindo o plano. Também pedi um plano de implementação por etapas, para conseguirmos acompanhar o que faltava até a conclusão.

Depois autorizei a construção completa e a publicação para eu revisar no final. Pedi também um diário simples do que fosse sendo feito, porque queria registrar as decisões e os problemas do caminho, sem transformar isso em mais um documento técnico enorme.

A primeira base ainda era só a estrutura. Tínhamos os lugares para os dados, o cálculo, os cards e os testes, mas ainda não existia uma carteira funcionando na tela. A partir daí começamos a ligar as coisas.

## 4º passo — colocando os dados de verdade

Trouxemos os cinco arquivos do Kaggle e registramos a origem e a licença CC0 declarada pela fonte. A leitura confirmou as 8.800 oportunidades do plano, sendo 2.089 ainda abertas.

Aqui apareceu um detalhe que precisava de cuidado: o mesmo produto estava escrito como GTXPro em parte das oportunidades e GTX Pro no catálogo. Corrigimos essa ligação, mas preservamos o nome original nos registros para não perder a referência do que veio da base.

Também havia oportunidades sem conta informada. A decisão foi manter essas oportunidades e mostrar que faltava informação, em vez de descartar ou tratar isso como falta de interesse do cliente. Depois dos ajustes, não ficaram vínculos desconhecidos de conta, produto ou vendedor.

## 5º passo — calculando a prioridade e vendo se ela fazia sentido

O cálculo seguiu a primeira regra do plano: combinar o histórico das negociações, o tempo desde o engajamento e o preço de catálogo. A explicação de cada oportunidade vem desse mesmo cálculo, para o texto não inventar uma justificativa que os dados não sustentam.

Um ponto que mantivemos desde o começo foi separar prioridade de chance de fechar. Também separamos a data histórica dos dados, de 2017, da data real em que o vendedor usa a aplicação. Concluir uma tarefa hoje não muda o resultado comercial de uma negociação antiga.

Quando rodamos a avaliação histórica, apareceu um resultado que precisava ficar explícito: entre os negócios já resolvidos no Top 10 de cada vendedor, o score ficou com 56,4% de vitórias, abaixo dos 60,7% da referência aleatória. Ele colocou mais vitórias observadas na fila, mas também escolheu muito mais negócios que já tinham um resultado conhecido. Então não dava para dizer que isso provava uma melhoria de conversão.

Mantivemos os pesos que estavam no plano, sem mexer neles olhando o resultado final só para melhorar os números. Essa limitação ficou na documentação e na própria explicação do método dentro do app.

## 6º passo — fazendo a rotina do vendedor funcionar

Com os dados e o cálculo prontos, fomos para as missões. A ideia ficou assim: o vendedor escolhe sua carteira, recebe até dez prioridades e trabalha uma por vez. Ele pode abrir outro card, copiar a orientação, marcar como feito ou adiar para amanhã.

Abrir um card não conclui nada e não muda a ordem da fila. Quando termina um lote, o próximo entra automaticamente. Também colocamos o desfazer, inclusive para uma missão de um lote anterior, para ela não se perder no caminho.

A rotina fica salva no navegador, separada por vendedor e versão dos dados. Recarregar a página recupera o que estava sendo feito, e a troca do dia segue o horário de São Paulo. Se o navegador bloquear o armazenamento ou houver um registro corrompido, a aplicação continua funcionando durante a sessão e avisa sobre a limitação.

A gamificação ficou simples: meta diária, progresso e sequência de dias em que a meta foi cumprida. Tudo começa vazio, sem conquistas inventadas. Adiar não conta como concluir, e desfazer corrige os contadores. As opções de equipe e a exportação ficaram em um acesso secundário, para não tomar o espaço da rotina principal.

## 7º passo — testando e corrigindo os detalhes

Os testes encontraram um problema na própria forma de verificar a interface: duas oportunidades podem ter o mesmo nome, produto e pontuação. Então comparar só o texto do card não garantia que era a mesma missão. Corrigimos a verificação para usar o ID da oportunidade.

A primeira rodada dessa integração passou em 27 testes. Depois vieram mais verificações dos casos de armazenamento e de desfazer, até chegar aos 31 testes aprovados.

Também fizemos a revisão no navegador: abrir a missão 7 mantendo as anteriores acima, concluir uma ação, adiar outra, desfazer e recarregar para ver se o registro continuava lá. Conferimos a tela no tamanho de celular e guardamos capturas reais. Nessa revisão ajustamos até o texto inicial, que passou a pedir a escolha da carteira em vez de dizer que os dados ainda não estavam disponíveis.

Por fim, repetimos a instalação e a execução em uma pasta limpa, sem as dependências e sem os arquivos gerados do ambiente anterior. A preparação dos dados, a avaliação, os testes e o build funcionaram. Queria que outra pessoa conseguisse abrir o projeto seguindo o README, sem depender do que já estava instalado na minha máquina.

## 8º passo — colocando no ar

A publicação deu um pouco de trabalho por causa do ambiente Windows. Foi preciso registrar o primeiro commit e ajustar as ferramentas que empacotavam os arquivos, porque os caminhos do Windows estavam causando erro no envio.

Depois desses ajustes, a hospedagem confirmou a publicação. A aplicação ficou com acesso privado para a minha revisão: [abrir Lead Scorer](https://lead-scorer-missoes-003.pokernachapa.chatgpt.site).

A documentação e o diário acompanharam a entrega. Colocar a aplicação no ar é uma etapa; enviar a candidatura pelo fork e PR oficial é outra, que ficou separada e ainda depende de preencher meu perfil e confirmar o prazo do recrutamento.

## 9º passo — revisando como a aplicação conversa com o vendedor

**1 de outubro de 2026**

Na revisão da tela, não gostei de algumas explicações. “Idade desde o engajamento”, “taxa suavizada” e “escala logarítmica” até fazem sentido para quem construiu o cálculo, mas não são intuitivos para um vendedor lendo a oportunidade e tentando decidir o que fazer.

Marquei esses trechos no navegador e pedi ao Codex para simplificar a linguagem. “Idade” virou “tempo desde o engajamento”, e os detalhes passaram a explicar, de forma mais direta, o que as negociações anteriores mostram, o que fazemos quando falta a data e como o preço de tabela entra na prioridade.

Não era para mudar a regra, era para tornar a explicação compreensível. Conferimos a oportunidade Plusstrip que usei no exemplo: ela continuou com os mesmos 62 pontos, percentuais e quantidades de negociações anteriores. Os 31 testes e o build passaram, e a revisão foi publicada.

Depois voltei para este diário. A primeira versão estava escrita pela perspectiva do assistente, então pedi para reescrever como um relato meu, aproveitando o começo que eu já tinha escrito à mão. Queria que ele contasse o caminho desde a escolha do desafio e as decisões de interface, porque o projeto não começou só quando o primeiro arquivo de código foi criado.
