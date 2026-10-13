# 00 — Hipóteses antes de abrir os dados

> Registrado antes de abrir qualquer linha dos datasets. As perguntas foram preparadas pela IA; os insights, palpites e previsões das respostas são meus, e a IA elaborou o texto a partir deles.
> Commit deste arquivo: ver `git log -- process-log/00-hipoteses.md` (a data do commit é a prova).
> Correção de 13/10/2026, depois de uma avaliação externa: a versão commitada dizia "Não usar IA para redigir este arquivo", o que não descrevia como o texto foi feito. As respostas não mudaram.

## 0. O que eu já sei antes de começar

**0.1** O que aprendi lendo os PRs públicos de outros candidatos (Challenge 002) e o que considero já estabelecido — e o que ainda quero verificar por conta própria?

> 

**0.2** Da minha experiência profissional: onde uma operação de suporte real costuma perder tempo? Dê um exemplo concreto que já vivi ou vi.

> 

## 1. Dataset 1 — tickets de suporte (~30K segundo o brief)

**1.1** O que espero encontrar quando abrir os dados? Quais sinais me fariam concluir que é sintético?

> 

**1.2** Se o Dataset 1 for sintético, o que muda na resposta às três perguntas do Diretor? O que ainda dá para responder com honestidade?

> 

**1.3** Se eu não puder medir gargalos nem drivers de CSAT nestes dados, o que eu recomendaria medir primeiro numa operação real — e por quê?

> 

## 2. Dataset 2 — tickets de TI (~48K, 8 categorias)

**2.1** Outros candidatos ficaram em 84–87% de acurácia. Por que eu acho que existe esse teto? Quanto do erro restante eu acho que é ruído de rótulo (rótulos errados ou ambíguos) e não limitação do modelo?

> 

**2.2** Qual categoria espero que seja a mais difícil, e por quê?

> 

## 3. Automação — onde IA entra e onde não entra

**3.1** O que eu nunca automatizaria num suporte ao cliente, mesmo com 99% de acurácia? Por quê (risco, regulação, relação com o cliente)?

> 

**3.2** Qual é o custo de um ticket roteado errado comparado ao custo da triagem manual? Que precisão mínima eu exigiria antes de rotear automaticamente — e o que acontece com o resto?

> 

## 4. Rascunhos de resposta em pt-BR (diferencial 1)

**4.1** O que torna um rascunho de resposta aceitável para um agente enviar? O que o torna inaceitável (promessa indevida, tom, informação inventada)?

> 

**4.2** Como eu saberia se os rascunhos estão bons sem confiar só na opinião de outra IA?

> 

## 5. Construir vs. comprar (diferencial 2)

**5.1** Para 2.500 tickets/mês e ~10 agentes, meu palpite antes de calcular: construir ou comprar (Zendesk, Intercom Fin, Freshdesk...)? Por quê?

> 

**5.2** O que normalmente se esquece no custo de "construir"?

> 

## 6. Previsões numéricas (pré-registradas)

Preencho a coluna "Minha previsão" agora. As colunas "Resultado" e "Errei por quê?" ficam para depois da medição.

| # | Pergunta | Minha previsão | Como vou medir | Resultado | Errei por quê? |
|---|---|---|---|---|---|
| P1 | Nº real de tickets no Dataset 1 | | Contagem após parsing correto do CSV | | |
| P2 | Correlação entre tempo de resolução e CSAT | | Spearman + teste de permutação | | |
| P3 | Acurácia de TF-IDF + regressão logística no Dataset 2 (teste) | | Split estratificado, conjunto de teste intocado | | |
| P4 | % do erro explicado por ruído de rótulo | | Duplicatas conflitantes + reetiquetagem manual de amostra | | |
| P5 | % dos tickets que dá para rotear automaticamente com ≥95% de precisão | | Limiar calibrado na validação, medido no teste | | |
| P6 | Queda de acurácia ao aplicar o modelo em texto em português | | Amostra traduzida + tickets escritos à mão | | |
| P7 | Volume mensal a partir do qual construir sai mais barato que comprar | | Modelo de custo com preços datados e citados | | |
| P8 | % dos rascunhos pt-BR aprovados sem edição pela minha rubrica | | Conjunto de teste de 60–100 mensagens, incluindo casos adversariais | | |

## 7. O que me faria mudar de ideia

**7.1** Que resultado me faria abandonar ou mudar a proposta de automação?

> 

## 8. Divisão de papéis

**8.1** O que eu decido e verifico pessoalmente, e o que delego à IA? Onde não confio na IA sem checar?

> 

Minhas respostas: 
0.1 O que aprendi lendo os PRs públicos?
Antes de abrir qualquer arquivo eu li uns PRs públicos do desafio. Já tinha gente fazendo auditoria dos dados, classificando com TF-IDF, falando de abstenção e de passar pro humano quando o modelo não tem certeza. Vi o número de 8.469 tickets no Dataset 1 e a observação de que tempo de resolução e CSAT quase não se relacionam. Essas ideias já estão na mesa, mas eu não tratei como fato até conferir eu mesmo. Quero ver a contagem real depois de limpar linha vazia e duplicata, entender o que cada campo significa de verdade, checar se o dado está sujo e se a forma de avaliar faz sentido. E separo acurácia de macro-F1 desde o começo. As duas métricas contam histórias diferentes e misturar elas só confunde.
0.2 Onde uma operação real costuma perder tempo?
Na operação o tempo some mais em transferência, falta de contexto e espera por autorização do que no momento de digitar a resposta pro cliente. Teve um chamado de um cara que não conseguia entrar no sistema depois de trocar a senha. O L1 abriu, viu que precisava de reset de permissão, passou pro L2. O L2 pediu print e horário exato, o cliente já tinha mandado isso no primeiro contato, o ticket ficou parado quase dois dias, o cliente reabriu reclamando que ninguém resolvia. O tempo de trabalho real de cada pessoa foi curto, mas a espera e o retrabalho de explicar de novo fizeram o CSAT despencar. Isso é o tipo de coisa que o número de resolução sozinho não mostra.
1.1 O que espero encontrar? Quais sinais indicariam dados sintéticos?
No Dataset 1 eu espero achar campo faltando, ticket que ainda está aberto, texto repetido e diferença clara entre canal e tipo de problema. Se for sintético, o sinal mais forte pra mim é descrição padronizada demais, combinação que não faz sentido (tipo prioridade alta com texto genérico e canal que não combina) ou distribuição muito regular. Correlação perto de zero sozinha não me faz concluir que é falso; pode ser só que as variáveis não se relacionam mesmo.
1.2 O que muda se o dataset for sintético?
Se confirmar que é sintético, eu descrevo a base, mostro o método de diagnóstico e deixo explícito que os padrões são dos dados que me deram, não de uma operação real. Não transformo isso em promessa de economia. Entrego o que encontrei, as limitações e um plano pra testar a ideia numa base de verdade.
1.3 O que recomendaria medir primeiro?
O que eu mediria primeiro é entrada do ticket, primeira resposta, número e motivo de transferência, tempo parado esperando cliente ou outra equipe, resolução e reabertura. Separar tempo de trabalho do agente do tempo de espera. Registrar motivo do contato, motivo da transferência e taxa de resposta ao CSAT. Sem isso é fácil confundir espera com esforço e achar que a satisfação representa todo mundo, quando na verdade só quem respondeu a pesquisa.
2.1 Por que poderia existir um teto? Quanto seria ruído de rótulo?
No Dataset 2 eu ainda não assumo que existe teto de 84 a 87%. Pode ser que os candidatos tenham usado split, métrica ou limpeza diferentes. Minha hipótese é que os erros misturem categoria que se sobrepõe, ticket com mais de uma intenção, texto curto demais, rótulo inconsistente e limitação do modelo. Palpite inicial é que uns 20% dos erros que a gente auditar tenham a ver com rótulo errado ou ambíguo, mas isso só sai de revisão manual. Não vou tratar todo erro do modelo como erro do dataset.
2.2 Qual categoria espero que seja mais difícil?
A categoria que eu espero que seja mais difícil é Access, se ela existir: senha, permissão, conta e problema de aplicação costumam aparecer no mesmo texto e a definição da categoria pode ser frouxa.
3.1 O que não automatizaria mesmo com 99% de acurácia?
Mesmo com 99% de acurácia eu não automatizaria a decisão final de dar privilégio, liberar informação sensível, executar ação irreversível ou abrir exceção de política. Conflito mais delicado com cliente também fica com humano. A IA pode organizar o caso e sugerir o próximo passo, mas acurácia global alta não prova que ela é segura nesses pontos.
3.2 Qual custo do erro e qual precisão mínima?
Roteamento errado gera nova triagem, transferência, atraso e retrabalho; quero medir esse custo incremental em vez de escolher limiar só pelo score do modelo. Pra um piloto de baixo risco eu começaria exigindo pelo menos 95% de precisão nos tickets que a gente deixar a IA tratar, com amostra suficiente e olhando por categoria. O que ficar abaixo do limiar, fora de domínio ou em caso crítico continua na triagem humana.
4.1 O que torna um rascunho aceitável?
Um rascunho aceitável precisa entender o pedido, usar informação que dá pra verificar, oferecer o próximo passo certo e ter tom respeitoso. Não pode inventar procedimento, prometer prazo ou reembolso sem autorização, nem dizer que algo já foi feito. Texto bem escrito não salva informação errada.
4.2 Como avaliaria a qualidade?
Eu avaliaria com rubrica humana num conjunto separado, registrando aprovação sem edição, com edição, rejeição, tipo de erro e tempo de revisão. Incluiria caso ambíguo e adversarial. Outra IA pode ajudar a achar problema, mas não seria a única avaliadora.
5.1 Meu palpite para 2.500 tickets/mês e dez agentes?
Pra 2.500 tickets por mês e dez agentes meu palpite é comprar a plataforma de atendimento e construir só a camada específica que faltar. Nesse volume eu não quero carregar manutenção, integração e disponibilidade de um sistema completo. Só mudaria de ideia se o custo total ou uma necessidade bem clara justificasse construir. Vou comparar soluções com funcionalidade equivalente.
5.2 O que costuma ficar fora do custo de construir?
O que costuma ficar fora da conta de construir é manutenção, integração, monitoramento, incidente, avaliação contínua, atualização da base de conhecimento, segurança, treinamento e o tempo da pessoa que fica responsável. O custo do protótipo não é o custo de manter a coisa rodando.
6 Previsões numéricas
As previsões abaixo são palpites pra eu mesmo revisar, não número medido. P1 e P2 já foram influenciados pelo que vi nos PRs.
P1 Número real de tickets no Dataset 1: 8.469, como apareceu em PR público. Vou contar depois do parsing certo, tirando linha vazia e duplicata.

P2 Correlação entre resolução e CSAT: Spearman perto de zero, entre -0,10 e +0,10. Validar o que os tempos significam de verdade, calcular só em pares válidos, com permutação e olhar a cobertura.

P3 Acurácia de TF-IDF + regressão logística: 86% como palpite, não como reprodução do macro-F1 dos outros. Split estratificado, duplicata agrupada, teste intocado; reportar macro-F1 também.

P4 Fração dos erros ligada a ruído de rótulo: 20% dos erros auditados. Amostra aleatória dos erros, revisão independente e análise de duplicata conflitante.

P5 Cobertura com precisão ≥95%: 50% dos tickets. Escolher limiar na validação e medir precisão, cobertura e incerteza no teste.

P6 Queda de acurácia em português: 40 pontos percentuais sem adaptação. Avaliar tradução e ticket originalmente em português separadamente.

P7 Volume em que construir fica mais barato: 20 mil tickets/mês, com baixa confiança. Custo total equivalente, preço datado, manutenção e análise de sensibilidade. Pode nem existir ponto de equilíbrio nas condições que a gente olhar.

P8 Rascunhos aprovados sem edição: 65%. Rubrica humana em 60 a 100 mensagens, separado pra caso comum e adversarial.
7.1 Quando abandonaria ou mudaria a proposta?
Eu mudaria ou abandonaria a proposta se a precisão necessária deixasse cobertura muito baixa, se o desempenho em português fosse ruim ou se a revisão humana comesse o tempo que a gente achava que ia economizar. Falha grave em resposta também me faria suspender essa parte. Nesse caso reduziria o escopo pra assistência ao agente ou iria pra solução comercial em vez de insistir na automação.
8.1 O que decido e verifico pessoalmente?
Eu decido o problema prioritário, os riscos aceitáveis, a rubrica e a recomendação final. Verifico exemplo, métrica, custo e interpretação. A IA pode sugerir abordagem, código inicial, teste e possíveis falhas. Não confio sem checar em número, explicação causal, fonte ou recomendação que afete cliente. Meu papel é assumir a responsabilidade pelo resultado, não só aprovar o que saiu.
