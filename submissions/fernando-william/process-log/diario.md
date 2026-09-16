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