# Guia de escrita: como escrever com a cara do G4 e não de IA

Vale para README, process log, texto de interface, mensagens de erro e as explicações de score do Lead Scorer. Três fontes: o que o G4 escreve no próprio site e na documentação do G4 OS; a skill "humanize" que o G4 publica no g4os-skills (feita para inglês, segundo o README dela, por isso os exemplos e a lista de vocabulário abaixo são adaptação nossa para PT-BR); e a página "Wikipedia: Signs of AI writing", que é a base da skill. Fontes numeradas no fim.

Por que importa: o README do challenge diz que o G4 já rodou o brief em Claude, GPT e Gemini e que "parecido com o baseline não é suficiente". A lista de submissão fraca inclui "output genérico que poderia ser sobre qualquer empresa". [1] Texto com cara de IA é o jeito mais rápido de parecer baseline.

## Como o G4 fala

Headlines literais do site, com fonte:

- "Para quem quer mais" (slogan, título do site) [2]
- "Sua empresa parou de crescer e você não sabe exatamente por quê" / "Em 4 dias, você sai com um plano de gestão e estratégia validado por quem já escalou negócios como o seu." [2]
- "No G4, só ensina quem faz" / "Mentores que vivem a realidade dos negócios no Brasil" [2]
- "Existe um G4 para cada fase da sua empresa" / "Responda 3 perguntas rápidas e a gente te mostra o caminho certo." [2]
- "Nossa missão era gerar 1 milhão de novos empregos até 2030." / "Em maio de 2026, chegamos lá." / "Missão dada, missão cumprida." [2]
- "Não somos para todo mundo. Somos para quem quer mais." [3]
- "O G4 nasceu de uma convicção simples: crescimento real se constrói com método, não com sorte. Com ambição calibrada por responsabilidade. Com resultado sustentado, não performado." [3]
- "Fundado por quem já fez antes." / "O G4 não foi criado por teóricos de gestão. Nasceu da experiência de quem escalou empresas reais — com os acertos e as cicatrizes que isso traz." [3]
- "Um ecossistema. 3 frentes." / "O G4 não é uma escola. Não é uma plataforma de software. Não é uma rede de networking. É os três ao mesmo tempo" [3]
- "6 anos. Resultados que falam." [3]
- "Não há excesso. Há intenção." [3]
- "Pronto para crescer com método?" / "Mais de 87 mil empresas já percorreram esse caminho com o G4. A próxima pode ser a sua." [3]
- "Nascemos ensinando. Crescemos conectando. Hoje, orientamos." / "liderança não se exerce com narrativa. Exerce-se com método." [4]
- "Um OS com IA para o seu negócio." / "Como ter um Chief of Staff digital." / "O que resolve na prática." / "Como funciona por dentro." / "Configure uma vez, rode para sempre." [5]
- "Do pedido ao trabalho feito" / "A sua empresa já usa IA. Só não tira resultado dela." / "Não é um chatbot. Não é um wrapper. É uma camada operacional real para o seu negócio." / "Sua IA deveria fazer o trabalho, não só descrevê-lo." [6][7]
- CTAs em primeira pessoa do cliente: "Quero meu ingresso", "Quero Participar", "Evoluir como líder agora", "Desenvolver meu time", "Ver qual G4 é para mim", "Realizar diagnóstico gratuito" [2][8]
- Dores nas páginas de programa: "Máquina de vendas que não funciona sem o dono tocando cada negociação", "Decisões por intuição, sem dados nem rituais de gestão estruturados" [9]
- Frases dos sócios: "Ter ideia é fácil, difícil é executar" (Tallis) [10]; "Não seja refém dos seus vendedores. Sua empresa não é um condomínio", "Nunca abandone sua intuição, mas use os dados para refiná-la" (Alfredo) [11]; "O papel do líder, de um CEO, é se tornar dispensável" (Nardon) [12]

O que esses trechos têm em comum:

1. Frases curtas, muitas sem verbo. Duas sentenças com corte no meio ("Não há excesso. Há intenção.").
2. Negação contrastiva: "não X, mas Y", "não é A, não é B, é os dois". Isso é marca do G4, não sinal de IA, mas só funciona quando o segundo termo é concreto.
3. Segunda pessoa direta e informal-empresarial ("a gente te mostra", "você sai com um plano").
4. Número como prova, sempre com contexto ("Em 4 dias", "87 mil empresas", "1 milhão de empregos", "6 anos").
5. Dor nomeada antes da promessa. A promessa é concreta e datada.
6. Vocabulário fixo: método, execução, prática, disciplina, resultado real, empresas reais, quem já fez, cicatriz, rituais, previsível, escala, ambição.
7. Anglicismos de negócio sem tradução: pipeline, forecast, win rate, ICP, CAC, LTV, OTE, track record, BHAG.
8. Zero adjetivo vazio. Não aparece "inovador", "robusto", "poderoso", "completo" sem lista.
9. Tom de quem já pagou o preço: "cicatrizes", "CPF na reta", "dinheiro desamparado".

A documentação do G4 OS segue o mesmo registro em formato técnico: segunda pessoa ("Você descreve o que precisa"), frases curtas, tabela "Preciso de… / Comece por aqui", definições em prosa e não em lista com rótulo em negrito, avisos concretos ("Alguns recursos são beta ou dependem da conta"), e uma seção "Limites" que declara o que não foi testado. Regras editoriais explícitas: não inventar dados, mostrar o denominador de cada taxa, sinalizar amostras pequenas, revisar antes de enviar, citar de onde veio cada informação. [13][14][15]

## Padrões a evitar, com exemplos do Lead Scorer

Os 18 primeiros vêm da skill humanize do G4; do 19 ao 22, da página da Wikipédia. Os exemplos são nossos. [16][17]

| # | Padrão | Ruim | Bom |
|---|---|---|---|
| 1 | Significado inflado | "Este scorer representa um marco na forma como o time comercial prioriza oportunidades." | "Este scorer ordena as 8.800 oportunidades do pipeline por chance de fechar nos próximos 30 dias." |
| 2 | Gerúndio decorativo no fim da frase | "O score combina cinco sinais, garantindo uma priorização assertiva." | "O score combina cinco sinais. O peso de cada um está na tabela abaixo." |
| 3 | Tom de folheto | "Uma solução robusta e completa para a gestão do seu pipeline." | "Lê o CSV do CRM, calcula um score de 0 a 100 por deal e mostra o porquê." |
| 4 | Fonte vaga | "Estudos mostram que deals parados esfriam rápido." | "No dataset, deals parados há mais de 45 dias em Engaging fecham 12% das vezes; os com menos de 15 dias, 41% (n = 2.310 e 1.874)." |
| 5 | Vocabulário de IA | "É crucial ressaltar que a ferramenta potencializa a atuação do vendedor." | "A ferramenta mostra ao vendedor os 10 deals que valem a manhã dele." |
| 6 | Travessão em toda frase | "O score é simples — cinco regras — e roda em segundos." | "O score tem cinco regras e roda em segundos." |
| 7 | Tudo em trios | "Rápido, claro e acionável." | "Roda em 2 segundos. Cada score vem com o motivo." |
| 8 | Paralelismo negativo genérico | "Não se trata apenas de um número, mas de uma nova forma de vender." | "O número diz onde focar. A frase ao lado diz por quê." |
| 9 | Rodízio de sinônimos | "O vendedor abre o app. O usuário filtra. O profissional de vendas age." | "O vendedor abre, filtra pela região dele e liga para os três primeiros." |
| 10 | Fuga do "é/tem" | "A coluna `score` serve como indicador consolidado de prioridade." | "A coluna `score` é a prioridade, de 0 a 100." |
| 11 | Intervalo falso | "Da prospecção ao pós-venda, cobre tudo." | "Cobre Prospecting e Engaging. Não avalia Won nem Lost." |
| 12 | "Apesar dos desafios" | "Apesar das limitações do dataset, o modelo está bem posicionado para evoluir." | "O dataset não tem data de última atividade. O sinal de 'esfriando' usa a data de criação, o que superestima o risco em deals antigos ainda ativos." |
| 13 | Title Case | "## Lógica De Scoring E Pesos" | "## Lógica de scoring e pesos" |
| 14 | Negrito em tudo | "**Importante:** o **score** depende do **estágio** e do **valor**." | "O score depende do estágio e do valor." |
| 15 | Lista com rótulo em negrito e dois-pontos | "- **Estágio:** peso 30. - **Valor:** peso 20." | Tabela de duas colunas (sinal, peso) ou prosa: "Estágio pesa 30 pontos, valor 20." |
| 16 | Emoji | "## 🚀 Como rodar" | "## Como rodar" |
| 17 | Linguagem meta | "Neste README vamos explorar a solução. Espero que gostem!" | "Instale com `pip install -r requirements.txt` e rode `streamlit run app.py`." |
| 18 | Aspas curvas e retas misturadas | "Use o filtro “região” no menu 'Vendedor'." | "Use o filtro \"região\" no menu \"Vendedor\"." |
| 19 | Disclaimer de conhecimento | "Até onde se sabe, o dataset tem cerca de 8 mil linhas." | "O dataset tem 8.800 linhas em sales_pipeline.csv." |
| 20 | Título sem conteúdo abaixo ou salto de nível | "## Método" seguido direto de "#### Pesos" | Todo título tem pelo menos um parágrafo; níveis em sequência. |
| 21 | Linha horizontal entre toda seção, tabela para o que seria uma frase | "---" após cada H2; tabela com duas células | Sem linhas horizontais. Duas células viram uma frase. |
| 22 | Restos de ferramenta | "[cite: 3]", "oaicite", "turn0search0", "utm_source=", "[CITATION NEEDED]", "Aqui está a versão revisada" | Apagar. |

Padrão extra que a Wikipédia chama de "copula avoidance": trocar "é" e "tem" por "serve como", "funciona como", "conta com", "apresenta", "oferece", "possui", "dispõe de". Voltar para "é" e "tem". [17]

## Vocabulário a evitar em PT-BR

Adaptação nossa. A skill humanize lista 33 palavras em inglês (delve, leverage, crucial, comprehensive, navigate, robust, seamless, landscape, tapestry, testament, pivotal, showcase, underscore, foster, garner, vibrant, multifaceted, myriad, plethora, noteworthy, commendable, meticulous, entre outras). Os equivalentes que aparecem em português: [16]

Conectivos de enchimento: além disso, ademais, outrossim, vale ressaltar, vale destacar, é importante notar, é importante mencionar, cabe salientar, nesse sentido, nesse contexto, dessa forma, em suma, por fim, em última análise, não obstante.

Adjetivos de brochura: robusto, abrangente, completo (sem dizer o que cobre), poderoso, inovador, revolucionário, disruptivo, essencial, crucial, fundamental, vital, imprescindível, vibrante, rico (figurado), profundo, holístico, sinérgico, escalável (sem número), fluido, intuitivo, assertivo, de ponta, de última geração, sem precedentes.

Verbos e figuras: mergulhar em, desbloquear, destravar, potencializar, alavancar, impulsionar, fomentar, promover (figurado), elevar, empoderar, navegar (figurado), explorar (quando é só "ver"), garantir (sem garantia real), evidenciar, ressaltar, sublinhar, otimizar (sem métrica), transformar, revolucionar, maximizar.

Substantivos abstratos: cenário atual, panorama, jornada (do cliente é termo do G4; "jornada" como enfeite não), experiência (como enfeite), sinergia, paradigma, patamar, pilar (o G4 usa "5 pilares" com nome; sozinho não), solução (em vez do nome da coisa), ferramenta poderosa, abordagem inovadora, insights valiosos, melhores práticas, ponto de virada, marco.

Aberturas e fechos: "No cenário atual...", "No mundo de hoje...", "Na era da IA...", "Em um mundo cada vez mais...", "Neste guia vamos explorar...", "Espero que ajude", "Fique à vontade para...", "Não hesite em...", "Sinta-se livre para...", "Vamos lá!", "Aqui está".

Substitutos: "além disso" → nada ou "também"; "é importante notar que X" → "X"; "robusto" → o que aguenta ("processa 9 mil linhas em 2 s"); "abrangente" → a lista do que cobre; "mergulhar em" → "ver", "ler"; "desbloquear" → "liberar"; "no cenário atual" → apagar; "serve como" → "é"; "conta com" → "tem"; "possui" → "tem"; "realizar" → "fazer"; "utilizar" → "usar"; "efetuar" → "fazer"; "visando" → "para"; "assertivo" → "certo" ou o número; "insight" → o fato.

Palavras que o G4 usa e você pode usar: método, execução, prática, disciplina, ritual, previsível, previsibilidade, forecast, pipeline, funil, ICP, ciclo de venda, win rate, esfriar, avançar oportunidade, Comitê de Receita, cicatriz, quem já fez, resultado real, "na segunda-feira de manhã". Usar porque descrevem a coisa, não como enfeite.

## Regras de estrutura

README. A primeira frase diz o que a coisa faz. A segunda é o comando para rodar. Nada de "Bem-vindo" nem "Neste documento". Seções em caixa baixa (só a primeira letra e nomes próprios). Parágrafos de 2 a 5 frases com tamanhos diferentes. Uma seção "Limites" ou "O que não faz", com fatos e números, vale mais que uma seção "Próximos passos" com promessas; a documentação do G4 OS tem "Limites" e o docs-audit deles declara o que não foi testado. [14][18] Negrito no máximo uma vez por seção, para aviso que evita perda de dados. Sem linha horizontal entre seções, sem parágrafo-resumo no fim de seção, sem "Conclusão".

Bullet ou prosa. Prosa quando há causa, sequência de raciocínio ou exceção ("X porque Y, exceto quando Z"). Bullets quando os itens são paralelos e independentes (pré-requisitos, flags, arquivos). Lista numerada só para passos com ordem. Tabela quando há duas ou mais colunas comparáveis (sinal / peso; erro / o que fazer), como o "Preciso de… / Comece por aqui" do G4 OS. [13] Listas podem ter 2, 4 ou 6 itens; se toda lista tem 3, é sinal.

Interface. Verbo no imperativo curto nos botões ("Filtrar", "Exportar", "Ver motivo"); CTAs que o G4 escreve em primeira pessoa do cliente também servem ("Quero ver meu pipeline"). Rótulo de coluna é substantivo curto ("Deal", "Conta", "Dias parado", "Score", "Por quê"). Mensagem de erro diz o que aconteceu e o que fazer ("sales_pipeline.csv não encontrado. Coloque o arquivo em data/ e recarregue."), nunca "Ops! Algo deu errado." Estado vazio diz o que fazer ("Nenhum deal aberto para este vendedor. Troque o filtro."). Sem emoji, sem ponto de exclamação.

Explicação de score. Cada deal tem uma frase de motivo, no formato dos workflows do G4 OS ("Esse canal está no quadrante APOSTAR porque..."). [19] Ruim: "Alta probabilidade de conversão devido a múltiplos fatores positivos." Bom: "Score 82. Engaging há 9 dias, conta já comprou 2 vezes, produto com win rate de 58% neste escritório. Risco: sem atividade nos últimos 7 dias." A frase tem número, estágio e um risco quando existe. Se o sinal depende de uma amostra pequena, dizer ("win rate calculado sobre 14 deals").

Números. Toda taxa com denominador ("41% de 1.874 deals"). Totais separados de médias. Datas absolutas ("21/09/2026"), não "recentemente". Moeda em R$ com separador de milhar. Não arredondar para parecer bonito quando o dado exato existe. [15]

Process log. Cronológico, com o que você pediu à IA, o que veio, o que jogou fora e por quê. Erros ficam no log. O G4 desclassifica sem evidência de processo. [1]

## Checklist final (15 itens)

1. A primeira frase do README diz o que a ferramenta faz e a segunda diz como rodar; não há saudação nem "neste documento".
2. Busca por "além disso", "vale ", "importante notar", "robust", "abrang", "cenário", "jornada" (fora "jornada do cliente"), "potencializ", "alavanc", "assertiv", "insight" retorna zero.
3. Nenhuma frase termina em gerúndio decorativo ("garantindo", "permitindo", "proporcionando", "possibilitando").
4. Toda afirmação de resultado tem número com denominador, arquivo, issue ou link. Nada de "estudos mostram" ou "especialistas".
5. Nenhum trio automático de adjetivos; as listas têm o tamanho que os fatos têm.
6. Nenhum "não se trata apenas de X, mas de Y". Negação contrastiva só quando o segundo termo é concreto, como o G4 faz.
7. O mesmo objeto tem o mesmo nome do começo ao fim: deal é deal, vendedor é vendedor, score é score.
8. "É", "tem", "fica" no lugar de "serve como", "conta com", "possui", "representa", "consiste em".
9. Títulos em caixa baixa, sem emoji, com pelo menos um parágrafo abaixo, sem pular nível.
10. Negrito no máximo um por seção. Nenhum bullet no formato "**Rótulo:** texto".
11. Travessão no máximo um a cada vários parágrafos; o resto virou vírgula, parêntese ou ponto.
12. Sem linha horizontal entre seções, sem parágrafo-resumo, sem "Conclusão". Existe uma seção "Limites" com fatos.
13. Tamanho das frases varia (há frases de 4 palavras e de 25); os parágrafos não têm todos o mesmo tamanho.
14. Cada score na interface tem um motivo com número, estágio e risco; cada taxa tem denominador; amostras pequenas estão sinalizadas.
15. Busca final por restos ("[cite", "oaicite", "turn0", "utm_source", "[CITATION", "Aqui está", "Espero que", "Fique à vontade", aspas curvas em código) retorna zero. Depois, leitura em voz alta: se soa como pitch de vendas ou como texto que serviria para qualquer empresa, reescrever.

## Fontes

1. https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge/blob/main/README.md
2. https://g4educacao.com/ (home, título, headlines e CTAs; acessado 21/09/2026)
3. https://g4educacao.com/sobre
4. https://g4business.com/blog/rebranding-g4-por-que-mudamos
5. https://g4educacao.com/g4-os
6. https://g4oscloud.com/
7. https://github.com/Gestao-Quatro-Ponto-Zero/g4os-docs/blob/main/landing.html
8. https://g4business.com/g4-skills
9. https://g4business.com/programas-presenciais/g4-gestao-e-estrategia
10. https://g4business.com/biografias/tallis-gomes
11. https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills/blob/main/workflows/ecossistema-vendas/knowledge/framework-reference.md
12. https://startups.com.br/semana-caldeira-2024/o-papel-do-ceo-e-se-tornar-dispensavel-diz-bruno-nardon-do-g4/
13. https://github.com/Gestao-Quatro-Ponto-Zero/g4os-docs/blob/main/index.mdx
14. https://github.com/Gestao-Quatro-Ponto-Zero/g4os-docs/blob/main/README.md
15. https://github.com/Gestao-Quatro-Ponto-Zero/g4os-docs/blob/main/use-cases/index.mdx e use-cases/marketing-vendas/performance-comercial.mdx
16. https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills/blob/main/skills/humanize/SKILL.md e README.md (a skill tem só SKILL.md, README.md e icon.svg; o README diz que é voltada para inglês)
17. https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
18. https://github.com/Gestao-Quatro-Ponto-Zero/g4os-docs/blob/main/.github/docs-audit/README.md
19. https://github.com/Gestao-Quatro-Ponto-Zero/g4os-skills/blob/main/workflows/ecossistema-vendas/WORKFLOW.md

Não encontrado: guia de tom de voz oficial do G4 ou do G4 OS; lista oficial de vocabulário de IA em português (a seção de vocabulário é adaptação nossa).
