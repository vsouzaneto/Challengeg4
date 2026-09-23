# Process log — como a IA foi usada

> Registro cronológico escrito **durante** o trabalho, não reconstruído no final.
> **Pedro** decide, dá contexto e revisa. **Claude Code** (Claude Opus, agente no terminal) explora, escreve código,
> roda testes e revisa o próprio trabalho. O histórico de commits da branch `submission/pedro-polido` é a outra metade
> deste log, e o export da conversa está em [`chat-export/`](chat-export/).

## Resumo

| | |
|---|---|
| Decisões do Pedro que definiram a entrega | 4 (desafio, narrativa, LLM, formato do protótipo) + revisão dos rótulos |
| Hipóteses da IA refutadas pelos dados | 4 |
| Erros da IA pegos pela verificação antes de entrar na entrega | 11 ([lista](#erros-da-ia-pegos-pela-verificação)) |
| Verificação automática do protótipo | 308/308 textos com a mesma fila e a mesma faixa em Python e no navegador |

---

## 1. Entender o desafio antes de escolher (22/09)

- O Claude Code clonou o repositório, leu o README, o guia de submissão e os 4 challenges e resumiu.
- **Pergunta do Pedro:** "qual desafio dá para fazer algo mais diferente que chame a atenção de forma eficiente?"
- **Recomendação da IA:** 002, com uma *hipótese a verificar*: o Dataset 1 (Kaggle `suraj520`) seria sintético, e a
  resposta de referência de qualquer LLM "acharia" gargalos em ruído.
- **Decisão do Pedro:** 002. Ele baixou os dois datasets.

## 2. Tentar derrubar a hipótese antes de construir

A primeira coisa feita com os dados foi tentar *refutar* a hipótese. Ela sobreviveu a tudo:

| Teste | Resultado |
|---|---|
| Volume | 8.469 linhas, não ~30.000 como diz o brief |
| Placeholders de template (`{product_purchased}`) | 100% das descrições |
| Resolução antes da primeira resposta | 49,3% dos tickets fechados |
| Tipo × assunto | independentes (p = 0,98) |
| Prever CSAT com todas as variáveis | 20,9% de acerto, igual a chutar a nota mais comum |

Em paralelo, um primeiro classificador no Dataset 2 (texto real, com bigramas) mostrou que 61% dos tickets podiam ser
roteados com 97,7% de acerto quando o modelo só age com confiança ≥ 0,9. Esse número virou a espinha da proposta.

## 3. Decisões do Pedro

| Pergunta | Decisão | Por quê |
|---|---|---|
| Como posicionar o dataset sintético? | **Abrir a entrega com ele** | É o que separa a entrega do baseline: a IA sozinha reporta padrões no ruído |
| Qual LLM? | **Gemini** (chave própria) | Disponível; a chave fica num `.env` fora do git e nunca passou pelo chat |
| Formato do protótipo? | **Web app na Vercel** | O avaliador abre uma URL e usa em 30 segundos; Streamlit ficaria parecido com o de todo mundo |

## 4. Auditoria reproduzível (`01_auditoria_dataset1.py`)

A exploração virou um script em que cada afirmação sai com um número calculado.

- **Erro da IA: contagem escrita à mão.** Na exploração, a análise de combinações foi rotulada como "60 combos". São 80
  (4 × 4 × 5). Agora o script calcula.
- **Erro da IA: afirmação mais forte que os dados.** "Todos os campos são uniformes": gênero não é (p = 0,007). A
  afirmação foi restrita aos campos operacionais.
- **Tentação evitada: ajustar a métrica ao discurso.** "Resoluções com vocabulário de suporte" deu 1%, não 0%. Em vez de
  apertar a regex, olhamos os 23 casos: "order" e "account" soltos ("Account eat tax accept."). O card reporta as duas
  coisas.
- **Evidência fraca removida.** Os e-mails em `example.com` saíram da lista de evidências. Anonimizar assim é prática
  legítima ao publicar dados reais, então sozinho não prova nada.
- **Permutation test para cada "achado" ingênuo.** A "pior combinação" (+3,4 h) aparece com dados embaralhados em 78%
  das simulações.

## 5. Detector de gargalos (`02_diagnostico_gargalos.py`)

- **Erro da IA: validação com defeito.** A primeira versão usava p-valores de permutação com 500 sorteios, e a curva de
  poder dizia que nem um gargalo de **+12 h** seria detectado. Z ≈ 5 e poder zero é implausível, então fomos atrás da
  causa: o menor p possível (1/501) é maior que o limiar de Benjamini-Hochberg para 149 testes (0,05/149). O "poder
  zero" era limite do método de validação. Trocamos por teste t de Welch unilateral + BH (caudas exatas).
- Resultado: 0 gargalos nos dados reais; em ruído puro, 8% das rodadas com algum alarme (a "pior média" erra em 100%);
  +3 h em canal × prioridade é detectado em 82%.

## 6. Dataset 2: hipóteses da IA refutadas pelos dados (`03_triagem_dataset2.py`)

| Hipótese da IA | O que os dados disseram |
|---|---|
| Cadeias de e-mail são mais difíceis de classificar | Falso: 85,7% / 85,5% / 85,8% com 1, 2 e 3+ mensagens |
| "Pedidos vazios" são um volume relevante | Falso: 0,5% |
| O modelo erra nos pedidos vazios | Falso, e mais interessante: ele acerta 92,7% porque 61% deles estão rotulados como HR Support. **Vício do rótulo**, não entendimento |
| Um critério cumulativo basta para a faixa assistida | Falso: a média da faixa escondia a cauda (o limiar parava no piso da grade, 0,30). Com critério local, o limiar ficou em 0,48: dali para cima, as 2 primeiras sugestões acertam ≥ 90% em cada faixa |

Outras decisões desta etapa:
- **Regex de tema sensível com falso positivo massivo:** "discipline" casava 2.273 vezes. No dataset é cargo ("discipline
  lead"). "Dismiss" era botão de sistema. A lista foi refeita olhando os casos, e o erro residual ("salary module") ficou
  do lado barato: vai para humano.
- **Unigramas em vez de bigramas:** +0,5 p.p. de acerto não pagam 4 a 17 vezes mais peso no navegador e explicações
  mais difíceis para o atendente.
- **Limiares escolhidos só no treino** (validação cruzada fora-da-dobra); o teste foi usado uma vez, para medir.

## 7. Protótipo (`solution/app`)

- **Paridade Python × navegador verificada, não presumida:** 300/300 tickets com a mesma fila (diferença máxima de
  probabilidade de 3e-5), depois estendido para 308 textos comparando também a faixa de decisão.
- **Revisão visual por captura de tela.** O painel do navegador estava oculto e as capturas saíam vazias, então as
  capturas passaram a ser feitas com o Edge headless, página inteira, nos temas claro e escuro. A revisão pegou erros de
  **conteúdo**, não só de layout:
  - **Erro da IA:** o texto dizia que o "tempo de resolução" era plano; o gráfico mostrava um **triângulo**. A segunda
    explicação ("diferença de dois horários uniformes na janela de 27 h") também estava errada: o teste KS rejeitou
    (p < 0,001). O mecanismo real, medido: cada horário é um instante-base ± 12 h; a diferença tem desvio de 9,6 h e
    curtose de −0,5, contra 9,8 h e −0,6 teóricos.
  - Um percentual aproximado ("44%", calculado por faixas de 0,1) virou o valor exato (45%).
- **Erro da IA: exemplo enganoso.** O botão "Senha bloqueada" mostrava um ticket em que o modelo discordava do rótulo,
  porque o critério de seleção não exigia acerto. Os exemplos "típicos" passaram a exigir acerto; o caso de divergência
  tem o botão próprio.
- **Bug de segurança pego no teste:** um ticket em português com 3 de 14 palavras conhecidas saiu como "Administrative
  rights" com **100% de confiança** e era roteado sozinho. Medimos a cobertura de vocabulário: nos tickets reais a
  mediana é 100% e o percentil 1 é 88%; em português e espanhol fica entre 8% e 30%. Nova regra: abaixo de 50%, o
  ticket vai para uma pessoa (ou é traduzido antes). Afeta 1 de 9.568 tickets reais.

## 8. Auditoria de rótulos (`auditoria-rotulos/`)

- No teste há 143 tickets em que o modelo tinha ≥ 90% de confiança e discordou do rótulo. Sorteamos 40.
- **Veredito da IA** (Claude, lendo caso a caso): 15 o modelo está certo, 13 o rótulo está certo, 9 ambíguos, 3 nenhum
  dos dois. Ou seja, cerca de 1/3 dos "erros" de alta confiança são erros do rótulo.
- **Revisão do Pedro:** coluna `veredito_pedro` em [`candidatos.csv`](auditoria-rotulos/candidatos.csv).
  _[PEDRO: em quantos casos discordou da IA e por quê]_
- **Terceira opinião (Gemini):** _[resultado do `04_benchmark_llm.py`]_

## 9. Honestidade na escrita

- **Erro da IA na redação da entrega:** o primeiro rascunho da seção "O que eu adicionei que a IA sozinha não faria"
  foi escrito em primeira pessoa e atribuía ao Pedro coisas que a IA tinha proposto (o desenho das faixas, o "modo
  sombra"), além de um "exigi a prova" que não aconteceu. Foi reescrito só com fatos, e os pontos que dependem do Pedro
  ficaram marcados para ele completar.

## 10. LLM × classificador (`04_benchmark_llm.py`)

_[resultado pendente: roda quando a chave do Gemini estiver no `.env`]_

---

## Erros da IA pegos pela verificação

| # | Erro | Como foi pego | Seção |
|---|---|---|---|
| 1 | "60 combinações" escrito à mão (são 80) | o script passou a calcular | 4 |
| 2 | "Todos os campos são uniformes" (gênero não é) | teste de aderência por campo | 4 |
| 3 | E-mail `example.com` usado como prova de dado falso | revisão da força de cada evidência | 4 |
| 4 | Curva de poder dizendo que +12 h nunca é detectado | resultado implausível → causa: resolução da permutação | 5 |
| 5 | Regex de tema sensível casando "discipline" 2.273 vezes | leitura dos casos que casaram | 6 |
| 6 | Tempo de resolução descrito como "plano" (é triângulo) | revisão visual do gráfico | 7 |
| 7 | Explicação "diferença de uniformes em 27 h" | teste KS, p < 0,001 | 7 |
| 8 | Percentual aproximado por faixa (44%) | recálculo exato (45%) | 7 |
| 9 | Exemplo "Senha bloqueada" mostrando um caso de divergência | clique em cada exemplo, leitura do resultado | 7 |
| 10 | Texto em português roteado sozinho com 100% de confiança | teste manual com frase em português | 7 |
| 11 | Contribuições da IA atribuídas ao Pedro no README | releitura da seção antes do commit | 9 |
