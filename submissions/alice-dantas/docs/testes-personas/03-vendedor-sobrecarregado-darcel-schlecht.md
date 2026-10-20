# Relatório 3 — Vendedor com carteira sobrecarregada (Darcel Schlecht, Central)

> Relato do agente, gravado sem edição. Vale como simulação de uso, não como evidência de usuários reais.

## A. Contexto
Sou Darcel Schlecht, vendedor comercial do escritório Central, com cerca de quatro anos de vendas e sem conhecimento técnico de dados. Tenho duas horas hoje e uma carteira grande. Minha missão era abrir o Rankio pela primeira vez, escolher em quais negócios gastar essas duas horas, explicar o porquê, dizer o que deixaria para depois e avaliar se a ferramenta reduziu o esforço da decisão. Usei só o navegador embutido, numa aba própria que fechei no fim. Não li arquivos, não usei Bash, API ou documentação, e não usei o javascript_tool. Cerca de 40 ações de navegação.

## B. Jornada executada
1. Abri http://localhost:3000. Ele redirecionou para /carteira, "Minha carteira". Vi "Escolha seu nome" e a mensagem "Saiba onde focar. Venda com mais direção." O menu tem Carteira, Equipe, Inteligência, Evidência e Como funciona. No alto aparece "Dados até 31/12/2017".
2. Abri o seletor de nome, vi a lista de vendedores e escolhi "Darcel Schlecht". A tela mostrou "Seu próximo passo": "Todas as negociações em andamento estão abertas há mais de 138 dias. Comece por Confirmar: confirme no CRM quais seguem ativas." Também mostrou 6 oportunidades "de mesmo valor de tabela (GTX Plus Pro, 5.482)": 5NGPM4C3, 7TFHGN6O (Inity), I3KQNE9V (Isdom), R55U5QI4 (Scottech), RCJRB8W8 e Z4OOTJAJ.
3. Li o resumo: "194 abertas = 0 Focar + 0 Acompanhar + 83 Confirmar + 111 Qualificar + 0 Completar". Li também "Ordem: Focar → Acompanhar → Confirmar → Qualificar → Completar; em cada grupo, maior valor de tabela primeiro; a idade aparece, mas não muda a ordem." E o aviso "134 de 194 sem cliente registrado".
4. Rolei até a tabela da aba Confirmar. Colunas: ID, Produto, Cliente, Valor de tabela, Engajada em, Idade. A lista traz "Valor de tabela alto (55)", com 6 GTX Plus Pro a 5.482 e 40 GTX Pro a 4.821.
5. Cliquei na aba Qualificar (111). Texto: "Ainda em prospecção, sem data de início da negociação." Próximo passo: "avance no CRM os de maior valor de tabela e registre a data de engajamento quando houver contato." Vi 13 GTX Plus Pro a 5.482 (28EJ0L9T, 6RQUXORL, 74LCNGIK, A4TA5P1B, CVMNBKGH/Hatfan, FU2PQZR4/Green-Plus, JVXGG70X, KIKV29M0, LZW4N9KF/Zathunicon, ODSFN0YA...), com "—" em data e idade.
6. Abri o detalhe de 28EJ0L9T (Qualificar). O painel "Por que está aqui" diz: "Qualificar porque ainda está em prospecção" e "Valor de tabela 5.482 (...): preço de catálogo do GTX Plus Pro, não valor negociado". Diz ainda "O sistema só vê datas, produto e preço de tabela: não vê ligações, reuniões nem e-mails." Fecha com "Próximo passo: Ainda em prospecção: avance no CRM...". Fechei o painel.
7. Voltei à aba Confirmar e abri o detalhe de 7TFHGN6O (GTX Plus Pro, Inity, 158 d). Texto: "Confirmar porque está aberta há 158 dias, mais do que qualquer venda já fechada aqui (138 d)". Próximo passo: "Confirme com o cliente ou no CRM se a negociação segue: o tempo aberta não prova que ela terminou."
8. Passei o mouse sobre o ícone "i" de Valor de tabela: "Preço de catálogo do produto, não o valor negociado." Tentei o da Idade, mas a captura de tela não mostrou o balão. Vi o texto "Dias em negociação, da data de engajamento até a data dos dados" só na leitura da estrutura da página.
9. Fui à página 4 de Confirmar (76–83 de 83): "Valor de tabela baixo (9)", com 9 do MG Special a 55 (3PPHOXTT, HMWIP0F2/Finjob, T1SITEI0, T9QD8U1Y/Betasoloin, UAX2OR58, VAL8O4PH, WSQHC199, YWGU40CP...). A página mostrou só 8 linhas, embora o grupo diga 9.
10. Abri /equipe. Vi os totais: Focar 157, Acompanhar 141, Confirmar 1.291, Qualificar 500, Completar 0, de 2.089 abertas. Cada grupo traz um texto explicativo. Vi a tabela "Por vendedor" com as 35 pessoas, em ordem alfabética. Na minha linha: 194 abertas, 0/0/83/111/0 e 134 sem cliente. Outros vendedores têm negócios em Focar e Acompanhar, e eu não tenho nenhum.
11. Abri /inteligencia. Vi "Taxa de ganho 63,2%", "Ciclo mediano de ganho 57 dias", receita ganha de 10,01 mi e uma tabela por produto. Na linha "O que cada vendedor vende", Darcel Schlecht aparece com 553 fechadas e 265 (47,9%) em GTX Pro.
12. Abri /evidencia: "A lista ajuda a escolher onde investir o próximo esforço?". A regra atual acerta 58,4% do valor vendido nas 10 primeiras. "Só valor de tabela" acerta 53,8% e a ordem aleatória, 23,2%. Há um bloco "E sem as negociações que nunca fecham na base?", em que "Só valor de tabela" rende 1,0 ponto a mais que a regra atual. O texto diz que a vantagem da regra vem dessas negociações e "podem ser um efeito de como a base foi montada". Também diz que a evidência "não mostra se a equipe seguiu a lista" e "não garante o mesmo resultado daqui para frente".
13. Abri /como-funciona. Li a definição dos 5 grupos. Focar é aberta há até 106 dias, pois 90% das vendas ganhas fecharam nesse prazo. Acompanhar vai de 106 a 138 dias, que é a venda mais longa já fechada. Confirmar passa de 138 dias. Qualificar é prospecção sem data. Completar é CRM sem produto, preço ou data. A faixa alta de valor de tabela começa em 3.000. A seção "O que a ferramenta não faz" diz: "Não calcula chance de fechar por oportunidade", "Não escreve no CRM".
14. Reabri a carteira de Darcel, fui à página 2 de Confirmar (26–50 de 83) e abri o detalhe de L6223VHA (GTX Pro, Sumace, 158 d). Vi o mesmo texto do item 7. Li os controles da página e não achei filtro, busca nem ordenação por coluna. Fechei a aba.

## C. Decisões comerciais
O Rankio não me deu nenhuma oportunidade "quente". Todas as 83 negociações em andamento têm de 139 a 165 dias, e a ferramenta diz que isso é mais do que qualquer venda já fechada. Meus grupos "Focar" e "Acompanhar" estão vazios. Decidi assim:

Ordem das duas horas:
1. Primeiros contatos, com os que têm cliente nomeado, para confirmar se ainda estão vivos:
   - 7TFHGN6O (Inity, GTX Plus Pro, 5.482)
   - I3KQNE9V (Isdom, GTX Plus Pro, 5.482)
   - R55U5QI4 (Scottech, GTX Plus Pro, 5.482)
2. Em seguida, GTX Pro de 4.821 com cliente nomeado:
   - 0TC6I9SJ (Dontechi)
   - 1QKDD1OI (Isdom)
   - 9B7FS6YL (Konex)
   - GQ7H31ZJ (Funholding)
   - L6223VHA (Sumace)
   - TJ95PY76 (J-Texon)
   - YI1V6SOX (The New York Inquirer)
   - ZJLW1OPF (Xx-zobam)
3. As de GTX Plus Pro sem cliente (5NGPM4C3, RCJRB8W8, Z4OOTJAJ) ficam depois. Mesmo sendo as de maior valor, ninguém registrado para ligar, então preciso primeiro descobrir quem é no CRM. Isso foi decisão minha. O Rankio colocou 5NGPM4C3 no topo e não distinguiu entre quem tem cliente e quem não tem.

Deixaria para depois:
- Os GTX Pro e MG Advanced sem cliente (a maioria, 134 de 194 sem cliente).
- Os 9 MG Special de 55 de valor de tabela, como 3PPHOXTT e HMWIP0F2. Não compensam o tempo.
- As 111 em Qualificar (por exemplo 28EJ0L9T, CVMNBKGH/Hatfan, FU2PQZR4/Green-Plus). Não têm data de início. Só vale olhar o que tem cliente nomeado, se sobrar tempo.

Esta lista é só o que eu faria. Não tenho como saber se esses nomes são os que realmente fecham.

## D. Dificuldades encontradas
- "Valor de tabela": entendi pelo balão como preço de catálogo, não o valor da venda. Mesmo assim, o ranking é todo baseado nisso, e não sei quanto o cliente realmente paga.
- "Confirmar", "Qualificar", "Completar", "Acompanhar": o nome do grupo não diz por si só o que fazer. "Confirmar" me pareceu "fechar/confirmar venda" antes de eu ler que é "confirmar se a negociação ainda existe".
- "Abertas há mais de 138 dias, mais do que qualquer venda já fechada aqui": entendi, mas não sei se isso significa que as negociações estão mortas ou só esquecidas. A ferramenta mesmo diz que "o tempo aberta não prova que ela terminou", e não ajuda a decidir qual delas confirmar primeiro.
- "Engajada em" e "Idade": só entendi a idade depois de ver o balão. O sinal do que é "engajada" não ficou claro.
- Na lista de Confirmar, as linhas são muito parecidas (mesmo produto, mesmo valor de tabela, idades de 139 a 165). Pareceu uma lista longa sem diferença real entre elas. O texto diz "Comece por estas 6 oportunidades de mesmo valor de tabela", mas essas 6 são empate, e a ferramenta não diz qual das 6 escolher.
- A ferramenta fala em "mesmo valor de tabela" como grupo, mas a ordem dentro do grupo parece alfabética por ID. Isso me levou a achar que o 5NGPM4C3 (sem cliente) era a melhor, o que é uma conclusão errada: ele só vem primeiro por ser o primeiro código.
- Não existe filtro nem busca por cliente, produto ou "com cliente registrado". Para separar quem tem cliente nomeado tive de ler as linhas uma a uma e comparar na mão. Não consegui completar essa parte da tarefa com a ferramenta.
- Não vi nenhum histórico do cliente, data de último contato, nem valor negociado. O detalhe dos negócios repete o mesmo texto para todos ("Confirme com o cliente ou no CRM...").
- A página 4 diz "9 oportunidades" no grupo de valor baixo, mas listou 8 linhas na página 4. Pode ser que uma esteja em outra página; não verifiquei a página 3.
- Em /inteligencia e /equipe há muita informação (taxa de ganho com faixa provável, "% da receita", "Ver por Produto"). "faixa provável: 62,0% a 64,3%" e "margem de erro" são termos que não entendi bem. Não ajudam a escolher o que fazer hoje.
- Em /evidencia, "Regra atual 58,4% do valor vendido estava nas 10 primeiras" e "Regra anterior (só o maior ciclo)" são difíceis. O trecho que diz que, sem as negociações que nunca fecham, "Só valor de tabela" rende mais que a regra atual me deixou em dúvida sobre se a regra funciona.
- Algumas capturas de tela atrasaram uma ação (a aba só mudou na captura seguinte), então precisei repetir cliques; isso não é da ferramenta, mas atrasou.

## E. Compreensão da recomendação
Pelo que li, o Rankio olha só a data em que a negociação começou, o produto e o preço de tabela. Separa cada negócio aberto em grupos pela idade: até 106 dias fica em Focar; de 106 a 138 em Acompanhar; acima de 138 em Confirmar; sem data em Qualificar; sem dados no CRM em Completar. Os grupos aparecem nessa ordem, e dentro de cada grupo vai do maior preço de tabela ao menor. Não olha cliente, não olha o que conversei, não calcula chance de fechar ("Não calcula chance de fechar por oportunidade"). No fundo, é "negociações mais novas primeiro, e entre elas as de produto mais caro". No meu caso, como todas passaram de 138 dias, vira só "as de produto mais caro primeiro".

## F. Valor percebido
O que melhorou:
- Em uns segundos vi o tamanho da carteira (194 abertas), quantas são prospecção (111) e quantas estão velhas (83), com uma explicação por grupo e por negócio.
- Descobri que nenhuma das minhas 83 está dentro do prazo normal das vendas ganhas. A tela de equipe mostra que colegas têm negócios em Focar e Acompanhar e eu não. Isso é um alerta útil para mim.
- A ferramenta é franca em várias telas: diz que não vê ligações nem reuniões, que valor de tabela não é o valor negociado, e que a evidência vem de simulação com dados passados.
- A página de evidência mostra que a lista foi testada contra ordem aleatória (58,4% contra 23,2%).

O que não melhorou:
- Minha pergunta era "em quais negócios gasto minhas duas horas". Para mim, a resposta da ferramenta foi "todos estão velhos, confirme no CRM", com 83 deles empatados em 3 faixas de valor. Não consegui sair da tela com uma lista curta e confiável de 10 ou 15.
- Dentro de cada faixa de preço, não há nada para separar um negócio do outro.
- Preciso do meu próprio julgamento (quem é o cliente, quando falei por último, se ele já comprou antes) e de dados que a ferramenta não tem (valor negociado, histórico de contatos).
- A principal informação de trabalho, "quem é o cliente", está faltando em 134 das 194 abertas. A ferramenta avisa, mas não ajuda a resolver.
- Reduziu pouco o esforço: tive de montar à mão a lista dos que têm cliente nomeado.

## G. Veredito
**Resolve parcialmente.**

Consegui concluir a tarefa: escolhi e ordenei negócios usando a ferramenta, com IDs (7TFHGN6O, I3KQNE9V, R55U5QI4 primeiro). Mas isso não prova que tomei a decisão comercial correta. A ferramenta me deu um critério claro e honesto (idade em grupos e depois preço de tabela), mostrou que meu pipeline está todo "velho" e que não há negócio quente. Porém, para o meu caso, ela ordenou por preço de catálogo entre negócios praticamente iguais, e a escolha final dos três primeiros foi minha (priorizei quem tem cliente nomeado). A própria tela de Evidência reconhece que não sabe se isso funciona na prática daqui pra frente e que, sem as negociações que nunca fecham, ordenar só por valor de tabela foi ligeiramente melhor. Não há filtro, busca ou informação de cliente que me tire da leitura manual. Para a Head de RevOps, a ferramenta abre, mostra o pipeline e diz onde olhar primeiro. Para mim, vendedor com 83 negócios velhos empatados, ela reduziu pouco o esforço.

## Resposta à pergunta de explicabilidade (cenário F)

Pergunta feita pelo coordenador, sem consulta à tela: "Explique, com suas próprias palavras, por que o Rankio colocou a oportunidade que você considerou a mais importante da sua carteira nessa categoria e nessa posição."

Resposta original:

A oportunidade que considerei a mais importante foi a 7TFHGN6O (GTX Plus Pro, cliente Inity, 158 dias). Respondo só com o que lembro de ter visto.

**Por que está em Confirmar.** No painel "Por que está aqui", o texto era mais ou menos: "Confirmar porque está aberta há 158 dias, mais do que qualquer venda já fechada aqui (138 d)". Entendi assim: o sistema comparou a idade dela com o histórico de vendas fechadas. A venda mais longa já fechada levou 138 dias, e a minha já passou disso. Então ela não vai para "Focar", que é o grupo das mais novas. O Rankio sugere "confirme com o cliente ou no CRM se a negociação segue: o tempo aberta não prova que ela terminou". Ou seja, ele não diz que a venda é boa. Diz que ela está velha demais para confiar que está viva. Todas as minhas 83 negociações em andamento caíram nesse mesmo grupo pelo mesmo motivo, então o grupo não separa a Inity das outras.

**Por que está nessa posição (a segunda da lista, "2 de 83").** O painel dizia: "Valor de tabela 5.482 (valor de tabela alto): preço de catálogo do GTX Plus Pro, não valor negociado". Entendi que dentro do grupo a ordem é do produto de preço de catálogo mais alto para o mais baixo. O GTX Plus Pro é o mais caro que tenho, então fica no topo.

**O que o Rankio não explica.** Ela empata com outras cinco GTX Plus Pro de 5.482 e ficou em segundo lugar. Não vi nenhuma explicação de por que ela vem antes ou depois das outras. Cheguei a imaginar que fosse a ordem do código, mas isso foi suposição minha, não vi escrito na tela. Eu a escolhi como a mais importante por um critério meu: ela tem cliente registrado (Inity). A idade de 158 dias, o histórico com o cliente e o que foi negociado não pesaram na ordem do Rankio. A tela diz que "a idade aparece, mas não muda a ordem".

**Resumo.** Ela está em Confirmar porque passou do prazo máximo histórico de 138 dias. Está perto do topo porque o produto tem preço de tabela alto. Essa posição não prova que seja a melhor oportunidade para eu trabalhar. O Rankio só viu datas, produto e preço de catálogo.
