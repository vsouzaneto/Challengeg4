# Relatório 5 — Head de Revenue Operations

> Relato do agente, gravado sem edição. Vale como simulação de uso, não como evidência de usuários reais.

## A. Contexto

Sou o Head de Revenue Operations (cerca de 12 anos de operações comerciais, sem formação técnica em dados ou IA). Pedi uma ferramenta que o vendedor abra, veja o pipeline e saiba onde focar. Avaliei o Rankio em http://localhost:3000 como quem recebe a entrega. Usei só o navegador embutido, em uma aba própria que fechei no fim. Procurei responder seis perguntas:
- onde concentrar atenção;
- o que requalificar;
- quais problemas operacionais existem;
- como saber se os vendedores usam a ferramenta;
- como saber se ela melhorou resultados;
- quais deficiências de dados existem e como a ferramenta as informa.

Também olhei a experiência de vendedor e de gerente.

## B. Jornada executada

1. Abri http://localhost:3000. Caí em "Carteira · Rankio" (/carteira), com a mensagem "Saiba onde focar. Venda com mais direção." e um seletor "Escolha seu nome". O selo no topo diz "Dados até 31/12/2017".
2. Abri o seletor de vendedor, que tem campo de busca, e escolhi Anna Snelling.
   - Resumo: "112 abertas = 0 Focar + 1 Acompanhar + 56 Confirmar + 55 Qualificar + 0 Completar".
   - Aviso: "69 de 112 sem cliente registrado".
   - "Seu próximo passo": "Nenhuma aberta há até 106 dias. Comece por Acompanhar: veja no CRM o último avanço de cada uma." Sugere a oportunidade B08R55ET (MG Special, valor 55, 138 d).
   - A explicação da ordem está escrita na tela: "maior valor de tabela primeiro; a idade aparece, mas não muda a ordem".
3. Na carteira da Anna, abri a aba "Confirmar" (56).
   - Texto: "Abertas há mais de 138 dias, mais do que qualquer venda já fechada aqui. O sistema não vê ligações nem reuniões. Próximo passo: Confirme com o cliente ou no CRM se a negociação segue: o tempo aberta não prova que ela terminou."
   - Primeiras linhas: 11 oportunidades GTX Plus Pro a 5.482 (1FEHFRKX, Labdrill, 164 d; 1T5WFCEJ; 513PSPBN; 7FZ9CBZ3, Scotfind; entre outras), depois 7 MG Advanced a 3.393.
4. Abri o painel "Por que está aqui" da 1FEHFRKX. Ele diz "Confirmar porque está aberta há 164 dias, mais do que qualquer venda já fechada aqui (138 d)". Diz também "Valor de tabela 5.482 (...): preço de catálogo do GTX Plus Pro, não valor negociado" e "O sistema só vê datas, produto e preço de tabela". Fechei o painel.
5. Abri a aba "Qualificar" (55) da Anna.
   - Texto: "Ainda em prospecção, sem data de início da negociação."
   - Todas as linhas têm "—" em "Engajada em" e em "Idade".
   - Abri o painel da 0D8Y5JA0 (GTX Plus Pro, 5.482, sem cliente): "Qualificar porque ainda está em prospecção".
6. Fui em "Equipe" (visão de gerente).
   - Cartões: Focar 157, Acompanhar 141, Confirmar 1.291, Qualificar 500, Completar 0, "de 2.089 abertas".
   - Tabela "Por vendedor" (35 pessoas) com colunas Abertas / Focar / Acompanhar / Confirmar / Qualificar / Completar / Sem cliente, em ordem alfabética ("A tabela não ordena pessoas por resultado").
   - Vendedores com 0 abertas: Carl Lin, Carol Thompson, Donn Cantrell, Elizabeth Anderson, Garret Kinder, Mei-Mei Johns, Natalya Ivanova e Reed Clapper.
7. Na Equipe, abri "Por oportunidade" (2.089).
   - Aviso: "1.425 de 2.089 sem cliente registrado".
   - Lista da aba Focar (157): 1LY8CAXD (Rosalina Dieter, GTK 500, 26.768, 95 d) em primeiro, depois 24 GTX Plus Pro a 5.482 (por exemplo 01XZ9CRY de Zane Levy, FZWU2I30, RDHTQLNI), com paginação.
8. Filtrei Gerente = Melvin Marxen. Ele tem 511 abertas: 0 Focar, 2 Acompanhar, 213 Confirmar, 296 Qualificar, 0 Completar.
   - O filtro Escritório só oferece "Central".
   - Voltei para "Por vendedor" e vi 6 vendedores dele (Darcel Schlecht 194 abertas, Gladys Colclough, Jonathan Berthelot, Marty Freudenburg, Mei-Mei Johns 0, Niesha Huffines).
   - Na aba "Por oportunidade" desse gerente, vi a oportunidade ?Q3VXO8 de Niesha Huffines (GTX Pro, 4.821) em "Acompanhar".
9. Fui em "Inteligência" ("Inteligência comercial").
   - Indicadores: Receita ganha 10,01 mi; Vendas ganhas 4.238 de 6.711 fechadas; Taxa de ganho 63,2% ("faixa provável: 62,0% a 64,3%"); Ciclo mediano de ganho 57 dias.
   - Carteira aberta: 2.089 abertas, 4,97 mi em valor de tabela, com o aviso "Valor de tabela não é receita e não se soma a ela".
   - Tabela por produto: 7 produtos, com receita, ticket e taxa de ganho.
   - Matriz "O que cada vendedor vende".
   - "Tempo e resultado" e "Ritmo mensal" (novas negociações caem de 761 em out/2017 para 283 em nov e 121 em dez).
10. Abri "Ver análises (14)", com as abas Processo (7) e Resultados (7).
    - Processo, itens e números que anotei:
      - "1.291 negociações abertas há mais de 138 dias" (81,2% das 1.589 em andamento).
      - "1.425 abertas sem cliente registrado" (68,2%; nas fechadas todas têm cliente).
      - "500 em prospecção sem nenhuma data".
      - "5 de 35 vendedores sem nenhuma oportunidade" (Carl Lin, Carol Thompson, Elizabeth Anderson, Mei-Mei Johns, Natalya Ivanova).
      - "Ganhos concentrados no último mês do trimestre" (80,7% de ganho contra 52,3% nos outros meses).
      - "A entrada de novas negociações caiu".
      - "Clientes atendidos por muitos vendedores" (mediana de 10).
      - "O que o CRM não registra": motivo da perda, atividades, histórico de estágio, valor proposto nas perdidas.
    - Resultados: "A taxa de ganho não separa os recortes"; "3 de 7 produtos somam 83,5% da receita"; "A diferença vem sobretudo do ticket"; "As fechadas sem venda se decidem cedo" (metade em até 14 dias); "Os clientes já compram quase todo o catálogo".
    - Fechei o painel.
11. Fui em "Evidência". A pergunta: "Se cada vendedor trabalhasse as 10 primeiras da lista, quanto do valor vendido nos 90 dias seguintes estaria nelas?".
    - Resultados da simulação (7 datas, 31/03 a 30/09/2017): Regra atual 58,4%; Só valor de tabela 53,8%; Ordem aleatória 23,2%; Regra anterior 56,9%.
    - Há também uma seção "E sem as negociações que nunca fecham na base?". Nela, "Só valor de tabela" rende 1,0 ponto a mais que a regra atual, e o texto diz que a vantagem da regra "vem dessas negociações, e elas podem ser um efeito de como a base foi montada".
    - Seção "O que esta evidência não mostra": não mostra se a equipe seguiu a lista, não garante o futuro, exige teste com parte da equipe, não avalia prospecção e usa "um CRM de exemplo".
12. Troquei "Linguagem de negócio" para "Linguagem técnica". Apareceram "Val@10", "oráculo", "Backtest", "IC95%", "AUC", "engage_date" e "Base provavelmente sintética". Voltei sem usar mais.
13. Fui em "Como funciona". Há os cinco grupos, as faixas de valor (alto a partir de 3.000, médio 500 a 2.999, baixo até 499) e os dois limites de idade (106 e 138 dias).
    - "O que a ferramenta não faz": "Não calcula chance de fechar por oportunidade", "Não escreve no CRM", "Não ordena vendedores", "Não se atualiza sozinha".
14. Voltei em "Carteira". A página lembrou da Anna Snelling. Troquei para Kary Hendrixson.
    - Resumo: 103 abertas = 14 Focar + 7 Acompanhar + 82 Confirmar.
    - Primeira oportunidade sugerida: JJGRAQ2K (GTX Plus Pro, Rangreen, 5.482, 69 d).
    - O painel explica "Focar porque está aberta há 69 dias; 90% das vendas ganhas fecharam em até 106 dias".
    - Lista de Focar: 4 GTX Pro a 4.821 (D55HTKRU, RTWE19SU, SQ71BWHG, VVE9HGLD), 4S17VJ7O e outras.
15. Escolhi Carl Lin. A tela mostra só "Nenhuma oportunidade aberta para este vendedor", sem explicação.
16. Em Inteligência, abri Filtros. Há Produto, Vendedor, Gerente, Escritório, Setor, Cliente e Porte do cliente. Não há filtro de período. Filtrei Vendedor = Anna Snelling.
    - Receita 275,06 mil; 208 ganhas de 336 fechadas; taxa 61,9%; as análises passaram de 14 para 11.
    - Apareceu o texto "volume de fechadas, -30,3%; ticket por venda (mix de produto), 138,7%; taxa de ganho, -8,4%".
17. Voltei em Equipe e fui à página 2 da tabela de vendedores. Natalya Ivanova e Reed Clapper têm 0 abertas. Vicki Laflamme tem 104 abertas e Zane Levy 88.
18. Cliquei no nome Zane Levy, que me levou à carteira dele.
    - 88 abertas = 13 Focar + 18 Acompanhar + 57 Confirmar.
    - "Comece por estas 2 oportunidades de mesmo valor de tabela (GTX Plus Pro, 5.482)": 01XZ9CRY (Initech, 104 d) e FZWU2I30 (The New York Inquirer, 21 d).
    - Uma está quase no limite de 106 dias e outra tem 21 dias, e ficam empatadas.
19. Passei pelo ícone de informação de "Valor de tabela" ("Preço de catálogo do produto, não o valor negociado") e tentei abrir a aba Completar (0, sem conteúdo). Fechei a aba do navegador.

## C. Respostas às perguntas

1. **Onde o time deveria concentrar atenção: respondeu em parte.**
   - Cada carteira e a Equipe mostram os grupos Focar, Acompanhar, Confirmar, Qualificar e Completar, com contagem por vendedor. Cada vendedor tem um "Seu próximo passo" e uma lista ordenada. Exemplo: Kary Hendrixson tem JJGRAQ2K em primeiro lugar.
   - A resposta é fraca por três motivos:
     - Para a Anna Snelling, a primeira sugestão é uma oportunidade de valor 55 (B08R55ET), porque ela não tem Focar.
     - O time inteiro tem só 157 oportunidades em Focar contra 1.291 em Confirmar.
     - A ordem é só valor de catálogo, e a própria tela diz que a idade não muda a ordem, então um negócio de 21 dias empata com um de 104 dias.
   - Não há chance de fechar por oportunidade ("Não calcula chance de fechar por oportunidade").

2. **Quais oportunidades merecem requalificação: respondeu em parte.**
   - "Confirmar" (1.291) e "Qualificar" (500) são os candidatos, com próximo passo escrito ("Confirme com o cliente ou no CRM...", "registre a data de engajamento quando houver contato").
   - O que falta: o sistema não diz quais das 1.291 provavelmente morreram nem quais valem esforço. Diz que "o tempo aberta não prova que ela terminou". Como é quase 62% do pipeline aberto (1.291 de 2.089), é uma lista enorme e quase sem priorização além do valor de catálogo.

3. **Problemas operacionais do pipeline: respondeu.**
   - O painel "Ver análises > Processo" lista com números:
     - 1.291 abertas há mais de 138 dias (81,2% das em andamento);
     - 1.425 sem cliente;
     - 500 prospecções sem data;
     - 5 vendedores sem oportunidade;
     - ganhos concentrados no fim do trimestre (80,7% contra 52,3%), com o pedido de checar se é registro em lote;
     - queda de novas negociações em nov e dez/2017;
     - clientes atendidos por muitos vendedores.
   - Cada item traz um "Próximo passo" para o RevOps.

4. **Como verificar se os vendedores estão usando a ferramenta: não respondeu.**
   - Não achei nenhuma tela de uso: acessos, quem abriu a carteira, ações feitas ou oportunidades trabalhadas.
   - Em "Como funciona" a ferramenta diz que "Não escreve no CRM" e "Não se atualiza sozinha". A "Evidência" diz que "Não mostra se a equipe seguiu a lista".
   - Hoje eu não teria como saber quem usa.

5. **Como saber se ela ajudou a melhorar os resultados: respondeu em parte, e com ressalva importante.**
   - Existe a página "Evidência", honesta. Ela é uma simulação no passado: a regra atual capturaria 58,4% do valor vendido nas 10 primeiras, contra 23,2% da ordem aleatória e 53,8% de "só valor de tabela".
   - Mas a própria tela diz que sem as negociações que nunca fecharam "Só valor de tabela" rende 1,0 ponto a mais que a regra atual.
   - Também diz que isso é uma simulação e que "para medir o efeito de verdade, é preciso testar com parte da equipe".
   - Não há antes/depois, grupo piloto versus controle nem filtro de período para acompanhar o resultado depois. O resultado real da ferramenta em uso não aparece.

6. **Deficiências de dados e como o sistema informa: respondeu bem.**
   - Avisos visíveis em todas as carteiras ("Aviso: 69 de 112 sem cliente registrado"; na Equipe, 1.425 de 2.089).
   - Sem data em 500 prospecções, vendedores sem oportunidade, e a lista "O que o CRM não registra" (motivo da perda, atividades, histórico de estágio, valor proposto nas perdidas).
   - A ferramenta avisa nos painéis que só vê "datas, produto e preço de tabela".
   - A Evidência diz que a base é um CRM de exemplo e, em modo técnico, "Base provavelmente sintética".
   - O grupo "Completar" (produto, preço ou data faltando) tem 0 em toda a base. Não consegui verificar se isso é porque está tudo preenchido ou porque a regra não pega nada.

## D. Dificuldades encontradas

- **Termos que não entendi:**
  - "Valor de tabela" demorou a ficar claro; o tooltip "Preço de catálogo do produto, não o valor negociado" ajudou.
  - "Engajada em": presumo que seja a data em que a oportunidade foi iniciada, mas não sei.
  - "Acompanhar" e "Confirmar" parecem verbos parecidos; precisei ler o texto de cada aba para entender a diferença.
  - Na Inteligência: "faixa provável: 62,0% a 64,3%" e "Ciclo mediano de ganho" são pouco intuitivos.
  - Em Inteligência > Resultados: "A receita varia 80,2 vezes entre 7 produtos. Quanto da diferença cada fator explica: volume de fechadas, 10,9%; ticket por venda (mix de produto), 89,6%". Com a Anna filtrada apareceram "volume de fechadas, -30,3%; ... 138,7%; taxa de ganho, -8,4%". Porcentagens negativas e acima de 100% eu não consegui ler.
  - Em linguagem técnica: "Val@10", "oráculo", "IC95%", "AUC", "engage_date". Não entendi. Em linguagem de negócio, o rótulo "Comparação com o acaso" também ficou vago.
- **Interpretação possivelmente equivocada:** pensei que o número em destaque na primeira sugestão (por exemplo "55" ou "5.482") fosse a nota da oportunidade; é o valor de tabela.
- **Informações que faltaram:**
  - Não existe carteira "do gerente" com ações. A Equipe mostra só contagens por vendedor.
  - Não há uso/adesão e não há acompanhamento de resultado depois da implantação (sem filtro de período e sem antes/depois).
  - Não sei o que acontece depois que o vendedor "avança no CRM". A ferramenta não registra o que foi feito.
  - A tela de Carl Lin só diz "Nenhuma oportunidade aberta para este vendedor", sem explicar (a Inteligência cita 5 vendedores sem oportunidade, mas não diz isso na carteira).
  - O seletor de Escritório só tem "Central" (um único escritório), apesar de eu ter "escritórios regionais". Não consegui avaliar a visão por regional.
- **Interface:**
  - O texto da página às vezes demorou para refletir cliques; precisei esperar.
  - O painel "Ver análises" lateral tem muito texto.
  - Depois de ter escolhido a Anna, a carteira "lembra" dela e eu não percebi isso de imediato.
- **Momento sem saber como continuar:** na carteira da Anna Snelling, com 0 em Focar e a primeira sugestão sendo uma oportunidade de valor 55, não ficou claro o que priorizar entre 56 "Confirmar" de 5.482 cada.

## E. Compreensão da recomendação

Do que li na tela, a ferramenta calcula a idade de cada oportunidade aberta e a compara com dois limites tirados do histórico: 106 dias (em que 90% das vendas ganhas já tinham fechado) e 138 dias (a venda mais longa já fechada).
- Até 106 dias vai para "Focar".
- Entre 106 e 138 dias vai para "Acompanhar".
- Acima de 138 dias vai para "Confirmar": a ideia é que provavelmente já esfriou ou terminou, e é preciso confirmar.
- As sem data de início ficam em "Qualificar".
- Falta de dado fica em "Completar".

Dentro de cada grupo, ordena pelo valor de tabela, do maior para o menor, e a idade não muda a ordem. Para mim, a "inteligência" é uma separação por tempo mais o preço de catálogo do produto, e não uma previsão por oportunidade (a ferramenta diz que não calcula chance de fechar). Não sei o que o sistema faz com o cliente, o setor ou o vendedor, e não parece usar nada disso na ordem.

## F. Valor percebido

- **Melhorou:**
  - Dá uma lista inicial ordenada e uma explicação do "por que está aqui" para cada oportunidade.
  - Mostra o tamanho do problema de higiene do pipeline (1.291 abertas além do maior ciclo histórico, 1.425 sem cliente).
  - Dá ao gerente uma visão rápida por vendedor.
  - É muito honesta sobre as limitações: diz "O sistema não vê ligações nem reuniões" e que a Evidência é uma simulação.
- **Não melhorou / não atendeu:**
  - A priorização do vendedor continua grosseira: valor de catálogo, com empates grandes de dezenas de oportunidades iguais (por exemplo 24 GTX Plus Pro a 5.482 só em Focar, e 11 só na aba Confirmar da Anna).
  - Não há chance de fechar por oportunidade, não há uso por vendedor e não há medição de resultado com a ferramenta em produção.
  - Para vendedores como Anna Snelling e Darcel Schlecht (111 em Qualificar), a lista é sobretudo de "confirmar/qualificar" e quase nada de "foque aqui".
- **Dependeu de outras fontes:** o CRM, para ver o último avanço, o cliente, ligações e reuniões; qualquer medição de adoção; qualquer medição de resultado real.

## G. Veredito

**Resolve parcialmente.**

- **Consegui concluir a tarefa de navegação e leitura.** Abri a carteira de três vendedores (Anna Snelling, Kary Hendrixson, Zane Levy) e a de Carl Lin (vazia). Vi a visão de equipe e de gerente (Melvin Marxen), os problemas de pipeline, as deficiências de dados e a evidência. Tudo funcionou, sem erro de tela.
- **Não foi demonstrado resultado de negócio.** A Evidência é uma simulação em dados do passado. A vantagem da regra sobre "só valor de tabela" (4,6 pontos) some e se inverte (1,0 ponto a favor do valor de tabela) quando se tiram as negociações que nunca fecham. A própria tela pede um piloto com controle.
- **Perguntas sem resposta:** uso pelos vendedores (nenhuma evidência na tela) e melhoria de resultado (só simulação).

**Decisão sobre o piloto: aprovaria com condições, como piloto controlado e não como lançamento geral.** Condições:
1. Rodar com parte da equipe e manter um grupo de controle, para medir de verdade (a Evidência recomenda isso).
2. Incluir uma forma de ver adoção: quem abriu a carteira, quais oportunidades foram trabalhadas e o que mudou no CRM depois.
3. Os vendedores e gerentes confirmarem no CRM as 1.291 oportunidades abertas além do ciclo máximo antes de começar (a ferramenta sugere uma "rotina de confirmação"). Sem isso, o pipeline que o vendedor vê é majoritariamente "Confirmar".
4. Corrigir o cadastro (cliente obrigatório, data de criação, vendedores sem carteira) antes de esperar melhor priorização.
5. Melhorar o desempate dentro do grupo, porque hoje dezenas de oportunidades empatam só por valor de catálogo.
6. Simplificar o texto dos números de explicação da receita (porcentagens negativas e acima de 100%) e os termos da Inteligência, que um vendedor não entende sozinho.

Sem as condições 1 e 2 eu não conseguiria dizer, ao fim do piloto, se a ferramenta ajudou nem se foi usada.

## Resposta à pergunta de explicabilidade (cenário F)

Pergunta feita pelo coordenador, sem consulta à tela: "Explique, com suas próprias palavras, por que o Rankio colocou uma oportunidade concreta que você abriu e considerou importante (a que você achar mais relevante da sua jornada) nessa categoria e nessa posição."

Resposta original:

Resposta à pergunta extra, só com o que lembro de ter visto na tela.

Escolho a oportunidade 1FEHFRKX, que abri na carteira da Anna Snelling. É um GTX Plus Pro do cliente Labdrill, engajado em 20/07/2017, com 164 dias. Estava na aba "Confirmar" e era a primeira da lista, "1 de 56". Escolhi esta porque o painel "Por que está aqui" explicou os dois pontos de forma clara.

**Por que está em "Confirmar":**
- O painel diz mais ou menos: "Confirmar porque está aberta há 164 dias, mais do que qualquer venda já fechada aqui (138 d)".
- Entendo que o Rankio olhou o histórico e viu que a venda mais longa já fechada levou 138 dias. Esta está aberta há 164, então passou do que já aconteceu na base.
- Ele não diz que a oportunidade está perdida. O próximo passo diz: "Confirme com o cliente ou no CRM se a negociação segue: o tempo aberta não prova que ela terminou". Para mim, é um alerta de "provavelmente esfriou, vá checar", e não uma previsão.

**Por que está nessa posição (primeira):**
- O painel diz mais ou menos: "Valor de tabela 5.482 (valor de tabela alto): preço de catálogo do GTX Plus Pro, não valor negociado".
- Dentro do grupo, a regra ordena do maior valor de tabela para o menor. Ela estava na faixa "alto" e no topo da lista, junto de outras 10 oportunidades de mesmo valor (GTX Plus Pro, 5.482).
- Essas outras tinham idades diferentes, como 157, 160 e 144 dias. A tela diz que a idade aparece mas não muda a ordem.
- Pelo que vi, a ordem entre as empatadas parecia seguir o código (1FEHFRKX, 1T5WFCEJ, 513PSPBN...). Isso é uma impressão minha. A tela não explicou o critério de desempate.

**Minha leitura crítica:**
- Ela está em primeiro lugar entre as 56 de "Confirmar" só porque o produto dela tem preço de catálogo alto. Isso não prova que seja a oportunidade mais promissora, nem a que mais precisa de atenção.
- O Rankio não sabe se houve ligação ou reunião ("O sistema só vê datas, produto e preço de tabela"). Também não sei se o cliente Labdrill está ativo.
- Para o vendedor, a mensagem útil é "esta é a primeira a checar, porque é antiga e de produto caro". Eu não leria isso como "é a melhor chance".
- Se a Anna não tem nenhuma em "Focar", ela passa a trabalhar de cima para baixo uma fila de 56, e a posição 1 ou 20 nessa fila quase não carrega informação.
