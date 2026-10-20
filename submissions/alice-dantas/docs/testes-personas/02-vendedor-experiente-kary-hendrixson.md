# Relatório 2 — Vendedor comercial experiente (Kary Hendrixson, West)

> Relato do agente, gravado sem edição. Vale como simulação de uso, não como evidência de usuários reais.

## RELATÓRIO DE TESTE DE USABILIDADE DO RANKIO (Kary Hendrixson, escritório West)

### A. Contexto
Sou Kary Hendrixson, vendedor B2B há cerca de 8 anos. Não tenho conhecimento técnico de dados. Minha missão era usar o Rankio pela primeira vez para organizar o meu próximo dia, ver se ele me mostra algo além do que eu já saberia sozinho, e questionar o que contrariasse o meu julgamento. Entendi que a ferramenta deveria me dizer onde focar e onde não perder tempo. Usei só a tela do navegador embutido, numa aba própria, que fechei no fim.

### B. Jornada executada (ações reais)
1. Abri a aba nova e fui a http://localhost:3000. Caiu em /carteira, "Minha carteira". Vi "Escolha seu nome" e "Saiba onde focar. Venda com mais direção." Vi também o selo "Dados até 31/12/2017".
2. Abri o seletor de vendedor e digitei "Kary". Escolhi "Kary Hendrixson".
3. Li o cabeçalho da carteira:
   - "Seu próximo passo: Avance primeiro as de maior valor de tabela; as do mesmo produto valem o mesmo."
   - "Comece por esta oportunidade: JJGRAQ2K, 5.482, GTX Plus Pro · Rangreen · 69 d".
   - "103 abertas = 14 Focar + 7 Acompanhar + 82 Confirmar + 0 Qualificar + 0 Completar".
   - "Ordem: Focar → Acompanhar → Confirmar → Qualificar → Completar; em cada grupo, maior valor de tabela primeiro; a idade aparece, mas não muda a ordem."
   - "Aviso: 66 de 103 sem cliente registrado".
4. Rolei a tabela da aba Focar. Os IDs que vi foram JJGRAQ2K (5.482, 69 d), D55HTKRU (Newex, 37 d), RTWE19SU (Conecom, 14 d), SQ71BWHG (Zencorporation, 57 d), VVE9HGLD (sem cliente, 87 d), 4S17VJ7O (MG Advanced, 3.393, sem cliente, 73 d). Na faixa média vi VL8YNHD7, YMWG4Z3S, 7EHJYKWE, J9PCNCUP, MYD4PBM9, ORYORRQV, WV2YBM8V e ZBDT3T2H (GTX Basic, 550, 104 d).
5. Cliquei em JJGRAQ2K. Abriu o painel "Por que está aqui". Ele diz:
   - "Focar porque está aberta há 69 dias; 90% das vendas ganhas fecharam em até 106 dias."
   - "Valor de tabela 5.482 (valor de tabela alto): preço de catálogo do GTX Plus Pro, não valor negociado."
   - "O sistema só vê datas, produto e preço de tabela: não vê ligações, reuniões nem e-mails."
6. Usei a seta do painel e vi D55HTKRU (2 de 14). Fechei.
7. Passei o mouse no ícone (i) de "Valor de tabela": "Preço de catálogo do produto, não o valor negociado."
8. Abri RTWE19SU (3 de 14) e depois VVE9HGLD (5 de 14). O texto é praticamente igual ao dos outros, só mudam o número de dias e o produto.
9. Cliquei na aba Acompanhar (7 itens). Vi H8XH5MFQ (GTX Plus Pro, 5.482, sem cliente, 119 d) e XRZNF1LQ (4.821, 122 d). Abri o detalhe de H8XH5MFQ. O próximo passo ali é "Veja no CRM o último avanço e o que falta para fechar."
10. Cliquei na aba Confirmar (82 itens, 41 de valor alto). Vi 04YGLJ3N (289 d), 5CAP1055 (Kan-code, 140 d), 5G4I94TF (Statholdings, 280 d), WALNFJ70 (388 d), entre outras. Abri 5CAP1055. O texto diz "Confirme com o cliente ou no CRM se a negociação segue: o tempo aberta não prova que ela terminou." A lista tem paginação (1–25 de 82).
11. Entrei em "Como funciona". Li a definição dos grupos, as faixas de valor (alto a partir de 3.000, médio 500 a 2.999, baixo até 499) e a seção "O que a ferramenta não faz": "Não calcula chance de fechar por oportunidade."
12. Entrei em "Inteligência". Li os totais:
    - receita ganha 10,01 mi;
    - 4.238 vendas ganhas de 6.711 fechadas;
    - taxa de ganho 63,2%;
    - ciclo mediano de 57 dias;
    - carteira aberta de 2.089, com 1.291 em Confirmar.
    Vi também as tabelas por produto, "O que cada vendedor vende" e "Tempo e resultado".
13. Abri "Ver análises (14)". A aba "Processo" traz, por exemplo, "1.291 negociações abertas há mais de 138 dias" e "1.425 abertas sem cliente registrado". Fechei o painel. A aba "Resultados" não consegui abrir; o clique não trocou de aba, não sei se era erro meu ou da tela.
14. Entrei em "Evidência". A pergunta é "Se cada vendedor trabalhasse as 10 primeiras da lista, quanto do valor vendido nos 90 dias seguintes estaria nelas?". Os números:
    - regra atual 58,4%;
    - só valor de tabela 53,8%;
    - ordem aleatória 23,2%;
    - mais recentes primeiro 26,6%;
    - taxa de ganho do produto 14,0%.
    Há ainda um bloco "E sem as negociações que nunca fecham na base?", em que "Só valor de tabela" rende 1,0 ponto a mais que a regra atual.
15. Entrei em "Equipe". Vi os totais por grupo (Focar 157, Acompanhar 141, Confirmar 1.291, Qualificar 500) e a tabela por vendedor. Na linha Kary Hendrixson: 103 / 14 / 7 / 82 / 0 / 0 / 66 sem cliente.
16. Voltei à Carteira da Kary para reconferir, fechei o painel e fechei a aba.

### C. Decisões comerciais
O que eu faria amanhã:
- **Começaria pelas negociações de Focar com cliente identificado e valor alto.** São JJGRAQ2K (Rangreen, 69 d), D55HTKRU (Newex, 37 d), RTWE19SU (Conecom, 14 d) e SQ71BWHG (Zencorporation, 57 d). Sei quem ligar e o ticket é grande. Ligaria primeiro nas mais jovens (RTWE19SU, D55HTKRU), porque o ciclo é curto e esfria rápido. Essa é uma decisão minha, não da ferramenta.
- **Trataria as "sem cliente registrado" de valor alto (VVE9HGLD, 4S17VJ7O, H8XH5MFQ, XRZNF1LQ) como "descobrir primeiro quem é".** Vou no CRM antes de investir tempo. Mesmo assim, a ferramenta as põe lado a lado com as que têm cliente.
- **Reservaria um bloco curto para as Acompanhar**, em especial H8XH5MFQ (5.482, 119 d) e 7P069DNF (Labdrill, 133 d). Seriam dois ou três contatos de "ainda está vivo?".
- **Deixaria para depois as 82 de Confirmar.** Pelo que o sistema diz, elas passaram do tempo de qualquer venda já fechada. Mas não vou fingir que estão mortas: 5CAP1055 (Kan-code, 140 d) pode ser um bom cliente que está só quieto. Faria uma varredura de limpeza, e não de venda.
- **As GTX Basic de 550, mesmo em Focar, ficam em segundo plano**, a não ser as com cliente conhecido (Xx-holding, Golddex, Hottechi).
- **Onde contrariei a ferramenta:** ela põe RTWE19SU (14 d) e VVE9HGLD (87 d, sem cliente) no mesmo patamar só porque o produto é o mesmo. Eu não faria isso.

### D. Dificuldades encontradas
- **Pedido de nome sem pista.** A tela inicial pede "Escolha seu nome" e eu precisei procurar o meu na lista.
- **Termos que não entendi de primeira:**
  - "Focar", "Acompanhar", "Confirmar", "Qualificar" e "Completar" são verbos. Só entendi o que cada um significa depois de ir ao "Como funciona".
  - "Engajada em" (data). Interpretei como a data em que a negociação começou, mas não tive certeza.
  - "Idade" com "d". Interpretei como dias desde a data de engajamento.
  - "Valor de tabela alto/médio" e "mesmo valor de tabela": entendi depois do tooltip que é o preço de catálogo, não o valor do negócio.
  - "mais do que 90% das vendas ganhas levaram, sem passar da venda mais longa já fechada" é pesado para quem não é de estatística. Entendi o espírito: fica mais difícil de fechar quanto mais velho.
  - "margem de erro" e "pontos a menos que a regra atual" (Evidência), "faixa provável: 62,0% a 64,3%" (Inteligência): não sei como usar isso no meu dia a dia.
  - "Ticket por venda (mix de produto)" e a fórmula de quanto cada fator explica: não entendi.
- **A informação que mais faltou:** a ferramenta não diz qual negociação tem mais chance de fechar. O próprio "Como funciona" diz "Não calcula chance de fechar por oportunidade." Ela também não vê ligações, reuniões ou e-mails, nem o valor negociado real (só o preço de catálogo).
- **66 de 103 sem cliente registrado**, ou seja, mais da metade da minha carteira. Isso esvazia boa parte da ordem: não sei quem ligar.
- **Mensagem repetida.** O "próximo passo" de todas as negociações de Focar é o mesmo texto genérico, "Avance primeiro as de maior valor de tabela...". Não me diz o que fazer em cada uma.
- **Nenhum filtro na Carteira**, por produto, cliente, faixa de dias ou "só com cliente". Também não achei busca por ID e não vi como marcar uma como "contatada hoje".
- **Falha de interação.** Algumas vezes o primeiro clique (trocar de aba, ir ao menu) não funcionava, precisei clicar duas vezes. Em "Ver análises", o clique em "Resultados" não trocou de aba.
- **Inteligência e Evidência são mais para a gestão.** Não achei utilidade direta para mim lá. Cheguei a pensar que "Equipe" servisse para me comparar com os colegas, e a ferramenta diz explicitamente que não ordena pessoas.

### E. Compreensão da recomendação
Do meu jeito de entender:
1. Ela olha **há quantos dias a negociação está aberta**, comparando com o histórico da empresa. Se é até 106 dias, é "Focar" (ainda dentro do tempo normal). De 107 a 138 dias é "Acompanhar". Acima de 138 dias, mais do que qualquer venda já fechada, vai para "Confirmar" (checar se ainda existe). "Qualificar" é para as ainda em prospecção, sem data de início, e "Completar" é para as com dado faltando no CRM.
2. Dentro de cada grupo, ela ordena por **preço de tabela do produto**. Quem tem produto de catálogo mais caro vem primeiro. A idade e o cliente não entram.
3. Ou seja, o que ela faz é basicamente "primeiro as de valor de catálogo mais alto que ainda estão dentro do prazo normal". Não é uma previsão de quem vai fechar.

### F. Valor percebido
**O que ajudou:**
- Separar 103 oportunidades em 14 para agir agora, 7 para checar e 82 para limpar. Essa divisão é algo que eu não tinha com clareza.
- Ver que 82 de 103 (cerca de 80%) da minha carteira estão "mais velhas do que qualquer venda já fechada". Isso me indica que boa parte da minha carteira talvez seja lixo de CRM.
- O painel "Por que está aqui" é honesto: diz que o valor é de tabela e que o sistema não vê ligações nem e-mails. Isso aumenta a confiança, porque ele não finge saber mais do que sabe.
- Na tela de Evidência, ele mostra que "só valor de tabela" é quase tão bom quanto a regra (53,8% contra 58,4%), e que sem as negociações que nunca fecham o "só valor de tabela" sai ligeiramente melhor. Fiquei com a impressão de que a regra é pouco mais do que ordenar por preço de catálogo.

**O que não melhorou:**
- Dentro de Focar, a ordem é praticamente "do produto mais caro para o mais barato". Qualquer vendedor experiente já faria isso. Não sei se a ferramenta me ensinou alguma coisa nova sobre quais negociações específicas fecham.
- Ela não diferencia uma negociação de 14 dias de uma de 87 dias dentro do mesmo produto.
- Com tantas sem cliente, a ordem fica de pouco valor prático.

**O que continua dependendo de mim:** saber se o cliente está engajado, o valor real negociado, quem é o decisor, o histórico de conversas, e se as "Confirmar" ainda estão vivas.

### G. Veredito
**Resolve parcialmente.**

**Evidências a favor:** consegui escolher meu nome, ver minha carteira dividida em grupos, abrir o motivo de cada uma e montar um plano do dia (Focar com cliente primeiro, bloco curto de Acompanhar, limpeza das Confirmar). A ferramenta é clara sobre o que não faz, e a divisão por idade de fato me mostrou que a maior parte da minha carteira está velha.

**Evidências contra:** a ordem dentro dos grupos é só preço de catálogo, o que eu já faria sozinho. O "próximo passo" é genérico, há mais de 60% de negociações sem cliente registrado, não existem filtros, e em nenhum momento a ferramenta me disse qual das negociações tem mais chance de fechar.

**Concluí a tarefa, mas isso não prova que a decisão foi a correta.** Escolhi começar por RTWE19SU, D55HTKRU, JJGRAQ2K e SQ71BWHG com base em valor de catálogo, cliente identificado e idade, mas não tenho como saber, só pela tela, se são as que realmente têm mais chance de fechar. Para isso eu dependeria do meu contato com o cliente e do CRM.

## Resposta à pergunta de explicabilidade (cenário F)

Pergunta feita pelo coordenador, sem consulta à tela: "Explique, com suas próprias palavras, por que o Rankio colocou a oportunidade que você considerou a mais importante da sua carteira nessa categoria e nessa posição."

Resposta original:

Resposta sobre a oportunidade que considerei mais importante, só com o que entendi e lembro da tela.

Escolho JJGRAQ2K (GTX Plus Pro, cliente Rangreen, preço de tabela 5.482, aberta há 69 dias). Foi a que o Rankio pôs em primeiro lugar. Eu também a considero a mais importante, porque tem o maior valor da minha carteira e tem cliente identificado. Uma ressalva honesta: na hora de ligar, eu mesmo começaria pela RTWE19SU (Conecom, 14 dias) e pela D55HTKRU (Newex, 37 dias). Faria isso por julgamento meu, porque as mais novas esfriam mais rápido, e não por algo que a ferramenta tenha dito.

Por que ela caiu em "Focar": pelo que li no painel "Por que está aqui", a ferramenta olha só há quantos dias a negociação está aberta. Ela está com 69 dias, e o painel diz que 90% das vendas ganhas fecharam em até 106 dias. Ou seja, está dentro do prazo normal de quem costuma fechar, e por isso entra na categoria de agir agora. Não entendi esse "106" a fundo. Entendi como "o tempo em que quase todas as vendas que deram certo costumam fechar".

Por que ela ficou na primeira posição: o painel diz que o motivo é o valor de tabela de 5.482, na faixa "alto". Entendi que, dentro de Focar, a ferramenta ordena do preço de catálogo mais alto para o mais baixo. O GTX Plus Pro tem o preço mais alto, então ela vem antes das GTX Pro (4.821) e das demais. O próprio texto avisa que é "preço de catálogo do GTX Plus Pro, não valor negociado".

O que a ferramenta não me explicou, e eu deixo claro:
- Ela não disse que essa oportunidade tem mais chance de fechar do que as outras. Entendi que ela não calcula chance de fechar.
- O fato de ter cliente não pesou na ordem, pelo que vi. Foi coincidência ser a de maior valor e ter cliente.
- Dos 69 dias, o que pesa é só estar abaixo de 106. Ela não distingue 69 de 14 ou de 87.
- Ela também não vê ligações, reuniões nem e-mails. Então não sabe se o Rangreen está realmente esperando proposta.

Resumindo: ela é a primeira porque o produto dela é o de maior preço de tabela entre as que ainda estão dentro do prazo histórico. Isso é uma regra de ordenação simples, não uma recomendação de que ali está a venda mais provável.
