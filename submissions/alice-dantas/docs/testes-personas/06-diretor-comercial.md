# Relatório 6 — Diretor comercial

> Relato do agente, gravado sem edição. Vale como simulação de uso, não como evidência de usuários reais.

## A. Contexto

Sou o diretor comercial, com cerca de 15 anos em vendas e nenhum conhecimento técnico de dados. A empresa tem 35 vendedores e cerca de 8.800 oportunidades históricas. A Head de RevOps pediu algo funcional: o vendedor abre, vê o pipeline e sabe onde focar.

Avaliei o Rankio só pela tela, em aba própria do navegador embutido. Não li código, documentação nem API. Minha pergunta era: que decisão comercial eu tomo melhor com isso, o que continua com o vendedor e vale adotar?

## B. Jornada executada

1. Abri http://localhost:3000. Ele foi para "Carteira" (Minha carteira). Vi "Escolha seu nome", o selo "Dados até 31/12/2017" e o menu: Carteira, Equipe, Inteligência, Evidência, Como funciona.
2. Abri o seletor de vendedor, que lista os nomes com busca, e escolhi Anna Snelling.
   - A tela mostrou "Seu próximo passo: Nenhuma aberta há até 106 dias. Comece por Acompanhar: veja no CRM o último avanço de cada uma."
   - Mostrou "112 abertas = 0 Focar + 1 Acompanhar + 56 Confirmar + 55 Qualificar + 0 Completar".
   - Mostrou "Aviso: 69 de 112 sem cliente registrado".
3. Cliquei na aba Confirmar (56 oportunidades).
   - Texto: "Abertas há mais de 138 dias, mais do que qualquer venda já fechada aqui. O sistema não vê ligações nem reuniões."
   - O "Próximo passo" diz: "Confirme com o cliente ou no CRM se a negociação segue: o tempo aberta não prova que ela terminou."
   - A lista vem agrupada em "Valor de tabela alto (18)", "médio (12)" e assim por diante. Há paginação (1–25 de 56).
   - Exemplos: 1FEHFRKX (GTX Plus Pro, Labdrill, 5.482, 164 d), 1T5WFCEJ (sem cliente registrado), 7FZ9CBZ3 (Scotfind), LD4F6QTP (Groovestreet), NSX4NR40 (Bioholding).
4. Abri o detalhe da oportunidade 1FEHFRKX (painel "Por que está aqui").
   - Neste grupo: "Confirmar porque está aberta há 164 dias, mais do que qualquer venda já fechada aqui (138 d)."
   - Nesta posição: "Valor de tabela 5.482 (valor de tabela alto): preço de catálogo do GTX Plus Pro, não valor negociado."
   - Também diz "O sistema só vê datas, produto e preço de tabela: não vê ligações, reuniões nem e-mails."
   - Próximo passo: o mesmo texto de confirmar com o cliente ou no CRM.
5. Cliquei na aba Qualificar (55) e abri 9P9ISECL (GTX Plus Pro, Sumace, 5.482).
   - Texto: "Qualificar porque ainda está em prospecção."
   - A coluna "Engajada em" vem com "—" e a idade vem vazia.
   - Próximo passo: "avance no CRM os de maior valor de tabela e registre a data de engajamento quando houver contato".
6. Cliquei na aba Acompanhar (1) e abri B08R55ET (MG Special, sem cliente, valor de tabela 55, 138 d).
   - Texto: "Acompanhar porque está aberta há 138 dias: mais do que 90% das vendas ganhas levaram (106 d), sem passar da venda mais longa já fechada (138 d)."
   - Próximo passo: "Veja no CRM o último avanço e o que falta para fechar."
7. Fui para "Equipe". Sem filtro: Focar 157, Acompanhar 141, Confirmar 1.291, Qualificar 500, Completar 0, de 2.089 abertas.
   - Li a tabela "Por vendedor" (25 de 35 na primeira página). Vários vendedores aparecem com 0 abertas: Carl Lin, Carol Thompson, Donn Cantrell, Elizabeth Anderson, Garret Kinder, Mei-Mei Johns.
   - Exemplos de linhas: Darcel Schlecht 194 abertas (83 Confirmar, 111 Qualificar, 0 Focar); Kary Hendrixson 103 (14 Focar); Anna 112.
   - A nota diz: "A tabela não ordena pessoas por resultado."
8. Filtrei Gerente = Dustin Brinkmann: 397 abertas, 0 Focar, 3 Acompanhar, 190 Confirmar, 204 Qualificar, 5 vendedores (Anna, Cecily Lampkin, Lajuana Vencill, Moses Frase, Versie Hillebrand).
9. Mudei para "Por oportunidade" nessa equipe. Vi XGHMOHYQ (Lajuana Vencill), B08R55ET (Anna) e W1XRTUT2 (Versie Hillebrand, cliente Finhigh). O filtro Escritório desse gerente só oferece "Central".
10. Cliquei em "Limpar filtros". O filtro Escritório então lista Central, East e West. Escolhi West: 748 abertas, 101 Focar, 85 Acompanhar, 562 Confirmar, 0 Qualificar.
    - A lista por oportunidade traz o vendedor em cada linha. Topo: 1LY8CAXD (Rosalina Dieter, GTK 500, Betasoloin, 26.768, 95 d).
    - Depois vêm 15 do GTX Plus Pro (5.482), por exemplo 01XZ9CRY (Zane Levy, Initech) e FZWU2I30 (Zane Levy, The New York Inquirer, 21 d).
    - Depois vêm 17 do GTX Pro (4.821).
11. Abri o detalhe de 1LY8CAXD: "Focar porque está aberta há 95 dias; 90% das vendas ganhas fecharam em até 106 dias." Valor de tabela 26.768. Próximo passo: "Avance primeiro as de maior valor de tabela; as do mesmo produto valem o mesmo."
12. Abri "Inteligência". Vi:
    - Receita ganha 10,01 mi; 4.238 vendas ganhas de 6.711 fechadas; taxa de ganho 63,2% ("faixa provável: 62,0% a 64,3%"); ciclo mediano de ganho 57 dias.
    - "Carteira aberta: 2.089 abertas · 4,97 mi em valor de tabela. Valor de tabela não é receita e não se soma a ela."
    - Tabela por produto: receita, ticket e taxa de ganho (60,0% a 64,8% entre os 7 produtos).
    - "O que cada vendedor vende": mix por vendedor.
    - "Tempo e resultado", com a taxa de ganho por faixa de ciclo.
    - "Ritmo mensal", com a queda de novas negociações em nov e dez/2017.
13. Abri "Ver análises (14)". A aba "Processo" traz:
    - "1.291 negociações abertas há mais de 138 dias" (81,2% das em andamento).
    - "1.425 abertas sem cliente registrado".
    - "500 em prospecção sem nenhuma data".
    - "5 de 35 vendedores sem nenhuma oportunidade".
    - "Ganhos concentrados no último mês do trimestre" (80,7% de ganho contra 52,3%).
    - "A entrada de novas negociações caiu".
    - "Clientes atendidos por muitos vendedores".
    - "O que o CRM não registra": motivo da perda, atividades, histórico de estágio e valor proposto nas perdidas.

    Cada análise traz um "Próximo passo" para a Head de RevOps.
14. Na aba "Resultados" das análises li:
    - "A taxa de ganho não separa os recortes."
    - "3 de 7 produtos somam 83,5% da receita."
    - "O que explica a diferença de receita entre vendedores... Não mede habilidade."
    - "As fechadas sem venda se decidem cedo" (metade em até 14 dias).
    - "Os clientes já compram quase todo o catálogo."
15. Abri "Evidência". A pergunta é: se cada vendedor trabalhasse as 10 primeiras da lista, quanto do valor vendido nos 90 dias seguintes estaria nelas?
    - Regra atual 58,4%; só valor de tabela 53,8%; ordem aleatória 23,2%; regra anterior 56,9%; taxa de ganho do produto 14,0%.
    - A seção "E sem as negociações que nunca fecham na base?" mostra que, sem elas, "Só valor de tabela" rende 1,0 ponto a mais que a regra atual. A tela diz que a vantagem da regra "vem dessas negociações, e elas podem ser um efeito de como a base foi montada".
    - Em "O que esta evidência não mostra": não mostra se a equipe seguiu a lista, não garante o mesmo resultado daqui para frente, e usa "um CRM de exemplo".
16. Abri "Como funciona". Li os grupos, as faixas de valor de tabela (alto a partir de 3.000, médio 500 a 2.999, baixo até 499) e os dois limites de idade (106 e 138 dias). Em "O que a ferramenta não faz": "Não calcula chance de fechar por oportunidade", "Não escreve no CRM", "Não ordena vendedores", "Não se atualiza sozinha".
17. Voltei à Carteira. Ela lembrou a Anna da visita anterior. Busquei "Kami" e escolhi Kami Bicknell.
    - Resultado: 90 abertas = 14 Focar + 11 Acompanhar + 65 Confirmar. Primeira da lista: P5C842B5 (GTX Plus Pro, 5.482, 64 d, sem cliente).
    - Abri 7FLPKZN7 (GTX Pro, Kan-code, 4.821, 99 d): "Focar porque está aberta há 99 dias".
18. Fechei minha aba.

Não consegui ler os textos dos ícones de ajuda ao lado de "Valor de tabela" e "Idade" nas colunas. Não os abri, então não sei o que dizem.

## C. Decisões comerciais

**O que consigo decidir melhor:**

- **Fila de trabalho diária.** O vendedor abre o nome dele e vê uma ordem: primeiro o que está dentro do ciclo normal de venda, com maior preço de tabela no topo. Isso tira o "feeling" do ponto de partida.
- **Higiene do pipeline.** Descobri que 1.291 das 2.089 abertas (62%) têm mais de 138 dias, mais do que qualquer venda já fechada. Com "Confirmar" posso cobrar dos gerentes uma rotina de confirmar ou encerrar essas oportunidades. Para mim isso é o achado de maior valor e já é uma decisão concreta.
- **Onde há carteira viva.** Na Equipe vejo quem tem trabalho em "Focar" e quem só tem lixo ou prospecção:
  - Dustin Brinkmann: 0 Focar em 397 abertas.
  - West: 101 Focar.
  - Darcel Schlecht: 194 abertas e 0 Focar.

  Dá para redistribuir carteira ou conversar com os gerentes.
- **Cadastro.** Vendedores sem oportunidade (5 de 35), 68% das abertas sem cliente, 500 em prospecção sem data. Isso orienta a RevOps sobre o que exigir do CRM.
- **Receita.** A receita vem do mix de produto (ticket), e a taxa de ganho é parecida entre produtos e vendedores. Isso me diz que não adianta cobrar conversão por vendedor ou produto, e que o que muda receita é o mix e o volume.

**O que não consigo decidir:**

- Qual das 10 oportunidades de Focar tem mais chance de fechar. A ferramenta diz que não calcula chance por oportunidade.
- Quanto a empresa vai faturar com a carteira aberta. O "valor de tabela" não é receita e a tela avisa que não se soma a ela.
- Em quem o vendedor deve investir tempo de fato. O sistema não vê ligação, reunião nem e-mail. Dentro do mesmo grupo e produto a ordem é quase empate (por exemplo, 15 GTX Plus Pro iguais com 5.482).
- Por que as vendas se perdem. O CRM não tem motivo da perda.
- Avaliar ou premiar vendedor. A ferramenta evita isso de propósito.

**Decisão de adoção:** eu adotaria em piloto controlado, não em toda a empresa. Condições:
1. Testar com parte da equipe e uma parte de controle, porque a própria tela admite que a evidência é simulação do passado.
2. Fazer primeiro a faxina de "Confirmar": 1.291 oportunidades velhas.
3. Exigir cliente e data de engajamento no CRM.
4. Definir uma métrica de sucesso minha, como receita ou conversão do grupo que usou a lista contra o grupo que não usou.

Hoje eu não investiria em escala com base só nesta tela.

## D. Dificuldades encontradas

**Termos que não entendi ou que me exigiram esforço:**
- "Valor de tabela". Entendi, pela explicação no detalhe, que é o preço de catálogo do produto e não o que foi negociado. Fiquei com a dúvida de se ele serve para priorizar, já que vendedor que já negocia sabe o valor real.
- "Engajada em". Interpretei como data em que o contato com o cliente começou, mas a tela não explica.
- "Idade" e o ícone de ajuda ao lado. Interpretei como dias desde o engajamento, mas não li o ícone.
- "Focar", "Acompanhar", "Confirmar", "Qualificar" e "Completar". Entendi pelos textos, mas o nome "Confirmar" não deixa claro para um vendedor que a oportunidade pode estar morta.
- "mesmo valor de tabela (GTX Plus Pro, 5.482)". Entendi que agrupa itens iguais, mas isso mostra que a ordem dentro do grupo é basicamente empate.
- "faixa provável: 62,0% a 64,3%", "margem de erro", "pontos a menos", "Comparação com o acaso" e "dentro do que o acaso explica". Isso é linguagem estatística. Entendi a ideia geral, mas não saberia explicar a um vendedor. Há um seletor "Linguagem de negócio" na Evidência, mas eu não abri outras opções.
- "Ticket por venda (mix de produto)" e "volume de fechadas, 10,9%". Entendi só que a receita vem mais do produto vendido do que da conversão.

**Interpretação que tive de ajustar:** pelo nome "Focar", esperava que fossem as melhores chances. Depois vi que Focar significa apenas aberta há pouco tempo, dentro do ciclo histórico. Não é probabilidade.

**Informações que faltaram:**
- Para a Anna, nas 112 abertas, 0 estão em Focar. A ferramenta diz "comece por Acompanhar", mas a única opção ali é B08R55ET (valor 55, MG Special, sem cliente). Ela não tem o que priorizar; só o que limpar.
- Falta o valor real negociado e o estágio do funil.
- Falta uma data de última atividade.
- Falta qualquer sinal de cliente (porte, setor, histórico) para 68% das oportunidades abertas.
- Não achei como marcar uma oportunidade como "já confirmei" ou "perdida". A ferramenta não escreve no CRM, então o trabalho de confirmar fica fora dela e a lista não mostra se alguém agiu.
- A página abre sem login e o vendedor escolhe o próprio nome. Não vi controle de quem enxerga a carteira de quem.
- "Dados até 31/12/2017" e "não se atualiza sozinha": para uso diário isso é um bloqueio.

**Perguntas de negócio sem resposta:**
- Qual o ganho de receita esperado com a ferramenta? A Evidência mostra "58,4% do valor vendido estava nas 10 primeiras", mas isso depende de a lista ter sido seguida.
- A vantagem da regra desaparece sem as negociações que nunca fecham. Sem elas, ordenar só por valor de tabela fica 1,0 ponto à frente da regra atual. Para mim isso significa que a diferença entre a regra nova e simplesmente ordenar por preço é pequena.
- Quanto tempo o vendedor economiza em deals que não vão fechar? Não vi nenhum indicador disso.
- Quais vendedores estão com carteira ruim ou boa. Não há ranking, por escolha da ferramenta.

**Momentos de travamento:**
- Na carteira da Anna, perdi um tempo achando que a aba "Confirmar" não tinha mudado; era atraso de carregamento.
- Na carteira da Anna nada estava em Focar. Não soube como o vendedor "sabe onde focar" quando a ferramenta só devolve "veja no CRM".

## E. Compreensão da recomendação

Com minhas palavras: o Rankio olha cada oportunidade aberta e calcula há quantos dias ela está aberta.
- Se a idade está dentro do tempo em que 90% das vendas ganhas fecharam (até 106 dias), ela vai para "Focar".
- Entre 106 e 138 dias (a venda mais longa já fechada), vai para "Acompanhar".
- Acima de 138 dias, vai para "Confirmar": a ferramenta presume que provavelmente morreu, e pede para o vendedor checar.
- Sem data de início (prospecção), vai para "Qualificar".
- Sem produto, preço ou data, vai para "Completar".

Dentro de cada grupo, ordena pelo preço de catálogo do produto, do maior para o menor. A idade aparece, mas não altera a ordem. Portanto é uma regra simples de calendário mais preço de tabela, não uma previsão de quem vai comprar. A ferramenta diz isso: "Não calcula chance de fechar por oportunidade".

## F. Valor percebido

**O que a ferramenta permitiu fazer melhor:**
- Ver rápido, por vendedor, gerente e escritório, quanto do pipeline está vivo e quanto está parado (157 Focar contra 1.291 Confirmar).
- Ter uma lista inicial de prioridade por vendedor, com justificativa em linguagem simples ("Por que está aqui").
- Receber diagnóstico de qualidade do CRM, com próximos passos para a RevOps: clientes ausentes, datas ausentes, vendedores sem carteira.
- Entender que a taxa de ganho é parecida entre produtos e vendedores, e que a receita é ditada pelo mix.

**O que não melhorou:**
- A decisão fina de qual deal trabalhar primeiro dentro do mesmo grupo e produto: é empate.
- A previsão de receita.
- O diagnóstico de perda.
- A avaliação de vendedor.

**O que continua dependendo dos vendedores ou de outras fontes:**
- Toda a confirmação real: ligar, olhar o CRM, saber se o cliente ainda está no jogo.
- Registrar desfecho e datas no CRM.
- Julgar potencial do cliente, relacionamento e momento da compra.
- Qualquer dado de atividade (ligações, reuniões, e-mails).

## G. Veredito

**Resolve parcialmente.**

**Consegui concluir a tarefa de navegação.** Em cerca de 50 ações no navegador, escolhi vendedores (Anna Snelling, Kami Bicknell), abri oportunidades (1FEHFRKX, 9P9ISECL, B08R55ET, 1LY8CAXD, 7FLPKZN7) e li o motivo de cada posição. Também usei os filtros da Equipe (Dustin Brinkmann, West) e percorri Inteligência, Evidência e Como funciona. A ferramenta responde "onde começo" para um vendedor com carteira recente, como Kami (14 Focar com a primeira P5C842B5). Para um vendedor como Anna, a resposta é só "confirme no CRM", sem um alvo de venda.

**O resultado de negócio não foi demonstrado.**
- A única prova de valor é a página Evidência, e é uma simulação com dados passados e uma base de exemplo, sem prova de que a equipe seguiu a lista.
- Essa simulação mostra que a regra atual (58,4%) fica a apenas 4,6 pontos de "só ordenar por valor de tabela" (53,8%). Sem as negociações que nunca fecham, o "só valor de tabela" empata ou ganha por 1,0 ponto.
- A própria ferramenta diz que, para medir o efeito de verdade, é preciso testar com parte da equipe.
- Por isso concluo que a ferramenta organiza e expõe o problema (62% do pipeline parado, cadastro incompleto), mas ainda não prova que o vendedor vai vender mais ou perder menos tempo.

## Resposta à pergunta de explicabilidade (cenário F)

Pergunta feita pelo coordenador, sem consulta à tela: "Explique, com suas próprias palavras, por que o Rankio colocou uma oportunidade concreta que você abriu e considerou importante (a que você achar mais relevante da sua jornada) nessa categoria e nessa posição."

Resposta original:

Escolho a oportunidade 1LY8CAXD (vendedora Rosalina Dieter, produto GTK 500, cliente Betasoloin, valor de tabela 26.768, engajada em 27/09/2017, 95 dias). Foi a que apareceu no topo da lista do escritório West e me pareceu a mais relevante, porque é de longe a de maior valor.

**Por que está em Focar.** Pelo que vi no painel "Por que está aqui": ela está aberta há 95 dias, e a tela diz que 90% das vendas ganhas no histórico fecharam em até 106 dias. Como 95 é menor que 106, ela cai em Focar. Entendo que Focar significa "ainda está dentro do tempo normal de uma venda desta empresa". Não entendo como "esta tem mais chance de fechar". A própria ferramenta diz que não calcula chance por oportunidade.

**Por que está nessa posição.** Dentro de Focar, a ordem é pelo valor de tabela, do maior para o menor. O painel diz que o valor de tabela é 26.768, classificado como "alto", e que é o preço de catálogo do GTK 500, "não valor negociado". Esse valor é muito maior que o do GTX Plus Pro (5.482) e o do GTX Pro (4.821), que vinham logo depois. Por isso ela ficou em primeiro. A idade de 95 dias, o cliente Betasoloin e o fato de ser da Rosalina não pesaram na posição. A regra de ordem diz que a idade aparece, mas não muda a ordem.

**O que eu não sei e a tela não me diz.**
- Se o cliente está de fato interessado, porque o sistema não vê ligações, reuniões nem e-mails.
- Se 26.768 é o valor real do negócio, porque é preço de catálogo.
- Se 95 dias, sendo perto do limite de 106, é um sinal bom ou um sinal de que a negociação está esfriando. A ferramenta trata como dentro do normal, mas não diferencia uma de 20 dias de uma de 95.
- Lembro também que o histórico mostrava poucas vendas de GTK 500 (a tabela de produto indicava cerca de 25 fechadas, com faixa de incerteza larga). Isso me deixa em dúvida se este produto tem base suficiente para uma regra de calendário confiável. Esse número eu lembro de forma aproximada.

**Próximo passo na tela:** "Avance primeiro as de maior valor de tabela; as do mesmo produto valem o mesmo". Ou seja, a recomendação concreta é só "trabalhe primeiro a de maior preço de catálogo dentro do prazo normal". Para mim, comercialmente, isso é uma regra razoável de partida, mas não é uma recomendação de venda baseada em sinais do cliente.
