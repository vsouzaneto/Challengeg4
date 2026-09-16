# Diário Desafio AI Master 002
## 16 de Setembro de 2026 15:21 gmt-3

Primeiramente escolhi este desafio por ser parecido com algo que já lido no dia-a-dia e tambem por conter maior variedade de aspectos a serem avaliados para a vaga.

Antes de verificar os CSVs, o enunciado fala em cerca de 30 mil tickets, dataset público do kaggle costuma, muitas vezes, ser sintético. Antes de usar qualquer tempo ou nota, vou testar se os dados se comportam como operação real.

Se forem reais, espero telefone e chat com primeira resposta rápida e e-mail com a resolução mais lenta. Rede social deve ter volume baixo e prioridade alta, porque é reclamação pública. Tikcet crítico deveria fechar antes do ticket baixo; se não fechar, a priorização não está funcionando.

Sobre satisfação, supomnho correlação negativa fraca com o tempo de resolução e nenhum efeito relevante de canal. Em operação real, o que mais derruba nota é ticket reaberto e resposta genérica, e isso o dataset provavelmente não registra.

Desconfio do texto da descrição. Se for gerado por template, ele não vai descrever o problema do ticket, e o teste é simples: um classificador de texto contra o tipo do próprio ticket tem que bater o baseline da classe majoritária. Se não bater, o texto é decorativo.

No segundo dataset, com 48 mil tickets rotulados em 8 cstegorias, espero que o texto preveja bem a categoria. Um TF-IDF com regressão logística deve passar de 80% de acurácia global, com as classes pequenas bem abaixo disso. A confusão deve concentrar-se entre acesso, hardware e armazenamento, que compartilham vocabulário.

Sobre onde o humano é insubstituível, antes de ler um ticket: tudo que envolve pessoa e vínculo (RH, desligamento, licença), concessão de acesso privilegiado, compra e reembolso acima de um valor, e cliente já irritado. Isso a máquina pode classificar, mas não pode decidir.

Sobre prioridade crítica fechar antes da baixa, não tenho aposta; em operação real depende de SLA contratado, e o dataset não diz se existe SLA. verei nos dados.

Sobre produto e idade do cliente pesarem na nota, nao tenho aposta nenyma; entram na análise só para descartar.

Ferramentas que vou usar: Claude Code como agente na pasta do trabalho e Codex para revisão independente no fim; Gemini Flash na camada de produto, para medir custo real.

## 16/09 16:10 gmt-3, teste da API

Verifiquei a tabela publica de modelos gemini para decidir LLM para a classificação.
Pedi: script de teste da API Gemini por REST, chave só por ambiente, e chamada no gemini-2.5-flash-lite, o mais barato da tabela pública (US$ 0,10 entrada / 0,40 saída por milhão de tokens, ai.google.dev, 16/09).
Saiu: 404, modelo indisponível para contas novas. O agente pulou direto para o 3.5-flash-lite porque a mensagem de erro sugeriu.
Corrigi: mandei testar o 3.1-flash-lite antes, que é mais barato (0,25 / 1,50 contra 0,30 / 2,50). Respondeu 200, 6 tokens de entrada e 1 de saída.
Decidi: gemini-3.1-flash-lite, o mais barato que responde nesta conta. Tem desligamento anunciado para maio de 2027; substituto é o 3.5-flash-lite, mais caro. Vai para Limitações. Custo calculado pelo preço público.
Iterações: 3.


## 16/09 16:27 gmt-3, primeira olhada nos dados

O primeiro arquivo tem 8.469 linhas, não 30 mil. Toda descrição começa com "I'm having an issue with the {product_purchased}. Please assist." e emedna frases sem ligação entre si; apareceu também um {error_message} sem coluna de origem. A coluna Resolution é farse sem sentido ("Write economy could station face wall thus."). Todas as horas de primeira resposta e de resolução caem em 2023-06-01, e numa linha a resolução vem antes da resposta; compras são de 2020 e 2021. E-mails são todos example.com/net/org. O segundo arquivo tem 47.837 linhas e duas colunas; o texto já veio pré-processado, minúsculo, sem pontuação e sem nomes, com sobras de saudação e assinatura ("kind regards administrator"). Um ticket sobre "updated rights query" está rotulado Hardware e um "new starter access" está em HR Support, não em Access.

Suspeito: o primeiro arquivo é gerado, com datas sorteadas num único dia e texto montado por template; tempos e nota não devem servir para diagnóstico. No segundo, as sobras de assinatura podem estar ensinando o classificador a reconhecer quem escreveu, não o assunto, e o rótulo tem ruído na fronteira entre Access, HR Support e Administrative rights.

Decidi: manter a auditoria completa e acrescentar três testes: cotnar placeholders órfãos além de {product_purchased}; verificar se 100% das datas de resposta e resolução caem no mesmo dia; e listar os termos de maior peso por classe no baseline do segundo arquivo, para ver se ele aprende assunto ou assinatura.

## 16/09 16:55 gmt-3, auditoria dos dois arquivos

Pedi: script de auditoria com 18 testes, saída em solution/01_auditoria_dados.txt.

Saiu: 8.469 linhas; tempos de resposta e resolução em 27 h com 49,3% de reoslução antes da resposta; nota uniforme (p=0,80) e sem relação com nada (ANOVA p>0,27, r=0,02); todas as categóricas uniformes; 100% das descrições com placeholder, 289 variantes, texto prevê o tipo em 19,8% contra 20,7% do chute; Resolution é frase aleatória. Arquivo 2: 47.837 textos, baseline 85,8%, macro-F1 0,85, Administrative rights com recall 0,61 caindo em Hardware, 6% com vizinho acima de 0,9.

Comparei: bateram volume, texto decorativo e faixa do baseline; caíram a nota e o par de confusão (é Administrative rights × Hardware, não acesso × armazenamento); canal e prioridade ficaram sem teste, os tempos são sorteio.

Decidi: tempos, nota, descrição e resolução do arquivo 1 fora do diagnóstico; estrutura de demanda só como volume de referência; arquivo 2 inteiro, com dedup antes do split. O relatório vai dizer que "onde perdemos tempo" não tem resposta nestes dados e propor como medir. Administrative rights é instalação de software com privilégio (outlook, upgrade, install), o que muda a fronteira humana.

Iterações: 1.

## 16/09 17:22 gmt-3, hipótese antes do modelo de custo

Hipótese: Triagem manual de 30 mil tickets a 5 minutos e R$ 35 por hora fica perto de R$ 90 mil por ano, ou 1,4 FTE; a automação absorve entre 70% e 85% disso e o retrabalho dos erros come uma parte. Acredito que o resultado por mil tickets fica abaixo de R$ 3 mil e que o número é pequeno perto do custo de resolver, não de triar.

## 16/09 17:31 gmt-3, modelo de custo

Pedi: modelo parametrizado com premissas nomeadas e fonte ao lado, três cenários pareados, lendo a cobertura da triagem automática de um arquivo que o protótipo vai gerar.
Saiu: triagem manual hoje entre 1.500 e 4.000 h/ano; economia líquida entre 790 e 3.290 h/ano, ou 0,45 a 1,87 FTE; 8 premissas empilhadas, impressas pelo script. Em solution/02_modelo_custo.txt.

Comparei: a aposta de 1,4 FTE bateu (base deu 1,42) e o valor por mil tickets ficou em R$ 2.088, abaixo dos R$ 3 mil que eu esperava. A absorção ficou em 100% porque ainda não há abstenção; isso muda no protótipo.

Decidi: resultado prnicipal em hors e FTE, reais numa linha só, porque custo/hora é a premissa mais frágil. O número é pequeno e vai ficar pequeno no relatório: a triagem automática não paga o projeto sozinha; o que pode pgaar é tempo de fila, que estes dsdos não têm. Acurácia por classe entra no modelo depois do protótipo.

Iterações: 1.

## 16/09 17:40 gmt-3, fronteira humana

Pedi: 30 tickets sorteados de HR Support, Administrative rights e Access, e 20 erros do modelo em cada uam das duas primeiras, com texto completo. Em solution 03_leitura_fronteira.txt.

Li: 90 sorteados e 40 errados. Escolhi 42710 (contas de desligados reativadas, auditoria), 15296 (licença-maternidade) e 30478 (aprovador de férias que saiu) como casos em que a máquina classifica e a pessoa decide.

Corrigi: a leitura de que Administrative rights é a "classe fraca do modelo". Nos 20 erros lidos, boa parte tem rótulo errado na origem: impressora, som de TV, Safari, portas de emergência não são direito administrativo. O recall de 0,61 é teto do rótulo, não do modelo. O piloto corrige rótulo antes de tentar modelo maior.

Decidi: regra de escalonamento por conteúdo, aciam da confiança: pessoa entrando ou saindo, conta e privilégio, auditoria e incidente, segurança física, urgência marcada, custo com aprovação. Ação automática só se for no reversível e padronizado.

Iterações: 1.

## 16/09 17:55 gmt-3, hipótese antes do protótipo
Hipótese: a dedup por similaridade tira entre 3% e 5% das linhas e a acurácia global cai 1 a 2 pontos, para perto de 84%. com abstenção, acredito que em limiiar 0,70 a máqiuna decide uns 75% dos tikcets com acurácia acima de 93%, e que para passar de 95% a cobertura cai para 60% ou menos. Administrative rights vai ser a classe que mais vai para fila humana. nas descrições do primeiro arquivo, espero masi de 80% abaixo de 0,70, porque o texto não fala de nada. Se a acurácia sobre os decididos passar de 98% em cobertura alta, desconfio de vazamento antes de comemorar.

## 16/09 18:17 gmt-3, classificador com abstenção

Pedi: dedup por similaridade antes do split, TF-IDF com regressão logística, curva de abstenção e teste fora de domínio nas descrições do primeiro arquivo.

Saiu: dedup tirou 4.955 linhas (10,4%), acurácia foi de 85,8% para 84,0%. Em 0,70 a máquina decide 59,7% com 96,3% de acerto; 62,6% de Administrative rights vai para humano. 78% dos textos do primeiro arquivo ficam abaixo de 0,70, mas 7.645 dos 8.469 caem em Hardware. 201 grupos de quase-duplicatas têm rótulos diferentes. Em solution/04_classificador.txt.

Comparei: errei a dedup por muiot (apostei 5%, deu 10%) e a cobertura (apostei 75%, deu 60%); acertei a queda de acurácia e a classe que mais vai para fila.

Decidi: limiar 0,70, porque cruza 95% com folga e ainda cobre 60%; subir para 0,80 custaria 11 pontos de cobertura por 1,5 de acerto. Hardware é o ralo de texto sem sentido, então o fluxo ganha uma trava de fora de dominio e o piloto mede reversão humana em Hardware. Rótulo inconsistente em 201 grupos confirma que corrigir rotulo vem antes de modelo maior.

Iterações: 1.


## 16/09 18:24 gmt-3, modelo de custo com abstenção

Pedi: rodar o modelo de custo lendo cobertura.json.

Saiu: economia líquida de 784 a 2.276 h/ano, 0,45 a 1,29 FTE. O teto caiu de 1,87 porque a máquina decide 60%; o piso não mudou porque o retrabalho dos erros comia a diferença.

Decidi: o README leva a faixa com abstenção, não a anterior.

Iterações: 2 rodadas do mesmo script.


## 16/09 18:30 gmt-3, piloto

Decidi: piloto de 30 dias em uma categoria, metade sorteada com triagem automática e metade como hoje, com regra de decisão fixada antes: expandir abaixo de 5% de reversão humana, manter entre 5% e 10%, desligar acima de 10% ou se a espera não cair. Escolhi Access pelo volume e pelos 96% de acerto medidos. Acrescentei três registros que hoje não existem e sem os quais "onde perdemos tempo" não tem resposta: hora de abertura, trocas de fila e espera pelo cliente. Em docs/piloto.md.

Iterações: 1.


## 16/09 18:36 gmt-3, LLM como segunda camada

Pedi: gemini-3.1-flash-lite zero-shot em 320 tickets do teste, 40 por classe, com cache e custo medido.

Saiu: 55% balanceada contra 76% do TF-IDF nos mesmos tickets; McNemar p < 10⁻⁹. Na zona de abstenção o LLM acerta 39%, pior que o TF-IDF forçado (56%). Custo R$ 0,32 por mil tickets, contra R$ 2.917 do humano. Em solution/05_llm_amostra.txt e cache em solution/cache/.

Comparei: eu esperava o LLM acima do TF-IDF na cauda. Errei. A taxonomia é da casa: Hardware inclui sala de reunião, Storage é pasta compartilhada, e o LLM chamou de Access.

Decidi: antes de concluir, uma iteração com 3 exemplos reais do treino por categoria. Se não passar do TF-IDF, a segunda camada é humana, e o LLM sai da arquitetura com o número que prova.

Iterações: 1, com a segunda a caminho.


