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
| Erros da IA pegos pela verificação | 38 ([lista](#erros-da-ia-pegos-pela-verificação)): 21 antes de entrar na entrega e 17 depois (9 na revisão pedida pelo Pedro, 2 pela segunda opinião, 1 no teste do chat, 4 na validação final, 1 na revisão do export) |
| Verificação automática do protótipo | 308/308 textos com a mesma fila e a mesma faixa em Python e no navegador |
| Validação cruzada (Claude Chat) | 19 afirmações recalculadas: 16 confirmam, 2 divergem, 1 não verificável; 2 pontos novos entraram na revisão |

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
| Volume | 8.469 registros em 29.808 linhas físicas; os ~30.000 do brief batem com as linhas, não com os tickets |
| Placeholders de template (`{product_purchased}`) | 100% das descrições |
| Resolução antes da primeira resposta | 49,3% dos tickets fechados |
| Tipo × assunto | sem associação detectável (p = 0,98) |
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
- **Revisão do Pedro:** coluna `veredito_pedro` em [`candidatos.csv`](auditoria-rotulos/candidatos.csv). Ele revisou
  os 40 casos e concordou com o veredito da IA em todos. A observação dele foi outra: boa parte dos ambíguos não se
  resolve relendo o ticket, e sim consultando outro sistema (conta bloqueada, chamado do equipamento, pedido de compra
  existente). Ele levou essa ideia ao Claude Chat para testar se fazia sentido
  ([print](auditoria-rotulos/claude-chat-agente-de-verificacao.png)). Daí a proposta de um agente de verificação só de
  leitura, que nunca executa nada, avaliado no modo sombra pela fração de ambíguos que passa a ser resolvida.
- **Terceira opinião (Gemini 3.5 Flash-Lite, sem ver o rótulo nem a previsão do modelo):** nos 15 casos em que a IA
  julgou o rótulo errado, o Gemini **nunca** escolheu o rótulo e ficou com a fila do modelo em 10. Nos 13 em que julgou
  o rótulo certo, ficou com o rótulo em 8. Concordância nos 28 casos categóricos: 64%. Em 38% dos 40 casos ele escolheu
  uma terceira fila, o que confirma o quanto esses tickets são ambíguos.

## 9. Honestidade na escrita

- **Erro da IA na redação da entrega:** o primeiro rascunho da seção "O que eu adicionei que a IA sozinha não faria"
  foi escrito em primeira pessoa e atribuía ao Pedro coisas que a IA tinha proposto (o desenho das faixas, o "modo
  sombra"), além de um "exigi a prova" que não aconteceu. Foi reescrito só com fatos, e os pontos que dependem do Pedro
  ficaram marcados para ele completar.

## 10. LLM × classificador (`04_benchmark_llm.py`)

**Antes de rodar, dois episódios:**
- **A chave foi salva como `.env.md`.** O script não achou a variável e o Google respondeu 403. A investigação foi feita
  sem exibir a chave, só nomes de variáveis e tamanhos. Além de não carregar, havia um risco: a regra local do git
  cobria `.env`, não `.env.md`, e um `git add` descuidado publicaria a chave num repositório público. O arquivo foi
  renomeado e a regra passou a cobrir `.env*`.
- **Erro da IA: modelo descontinuado.** O padrão do benchmark **e da função do app** era `gemini-2.5-flash`, que devolve
  404 para chaves novas ("no longer available to new users"). O protótipo teria quebrado no deploy. Um teste rápido com
  7 modelos pegou isso e mostrou a troca: `gemini-3.5-flash` leva ~25 s por causa do raciocínio (369 tokens de
  "pensamento" para 3 tickets); `gemini-3.5-flash-lite` acerta os mesmos casos em ~1 s. O app ficou com o flash-lite.

**Resultado** (234 tickets de teste, os mesmos para todos; logs brutos em [`benchmark-llm/`](benchmark-llm/)):

| Abordagem | 1ª execução | Final | Tokens/ticket |
|---|---|---|---|
| Classificador linear | 85,9% | 85,9% | 0 |
| Gemini 3.5 Flash-Lite, só nomes das filas | 44,0% | 42,3% | 48 |
| + descrições das filas | 59,0% | 58,5% | 53 |
| + 24 exemplos rotulados | 62,0% | 64,1% | 89 |

- **Temperatura 0 não garante repetição:** as duas execuções variaram até 2,1 p.p. Por isso o README reporta faixas, e
  o cache por rodada deixa os números finais reproduzíveis.
- **Onde o LLM perde:** nas filas cujo significado é da casa. Hardware 47% contra 89% do linear, Miscellaneous 50%
  contra 76%, HR Support 64% contra 87%. Nas filas autoexplicativas (Access, Storage, Internal Project), fica perto.
- **Modelos maiores indisponíveis:** `gemini-3.5-flash` devolveu 429/503 nas três execuções; `3.6-flash` e
  `flash-latest` só foram tentados na terceira e também falharam. Isso ficou registrado no resultado, e não derrubou o
  script.
- **Dois defeitos de engenharia pegos durante a execução** (erro 13 da lista, e um desperdício): os resultados só eram
  gravados no fim, e o script ainda esperava 8 minutos depois da última tentativa falha antes de desistir. Correção:
  cache por rodada (uma nova execução pula o que já terminou), nenhuma espera depois da última tentativa, e 3
  tentativas (não 6) para os modelos opcionais.

## 11. Revisão só com o CSV, e a auditoria da revisão

- **Pedido do Pedro (23/09):** revisar tudo ponto a ponto usando só o CSV de tickets, porque ele desconfiou da contagem
  ("deveria conter cerca de 30.000 tickets"), com regras explícitas: número só de código executado, separar FATO /
  INFERÊNCIA / PREMISSA, exemplo real com ID.
- **Etapa 1:** o arquivo é o mesmo (SHA-256 idêntico) e tem 8.469 registros em 29.808 linhas físicas (1 cabeçalho +
  8.469 registros + 21.338 quebras de linha dentro das descrições). Os IDs vão de 1 a 8.469, sem buracos. A contagem
  8.469 estava certa; os "~30 mil" do brief batem com as linhas.
- **Etapas 2–3:** 5 agentes analistas mediram cada candidata a automação com código, e 5 verificadores independentes
  recalcularam tudo do zero: 199 fatos, 7 divergências (de formulação, não de contagem), 71 exemplos conferidos
  literalmente no CSV.
- **Página de revisão** (`05_revisao_csv.py` → `revisao.html`): 2 auditores leram a página e a submissão inteira e
  acharam 35 problemas: 17 na página e 18 de inconsistência entre a revisão e o README ou a página principal. Os três
  graves estavam também na resposta dada ao Pedro por chat (erros 18, 19 e 21). Com a elegibilidade corrigida, o ROI
  provável das automações que o CSV sustenta passou de −39,6% para −65,0%.

## 12. Chat de atendimento (`solution/app/chat.html`)

- **Pedido do Pedro (23/09):** "constrói o chat do diferencial". A escolha do formato foi dele, pela experiência com
  agentes de atendimento.
- **Política separada da tela:** `js/chat-policy.js` é uma função pura. Regras de risco em português e inglês, avaliadas
  no texto original e na tradução (financeiro, perda de dados, invasão, insatisfação forte ou menção jurídica, tema
  sensível), mandam para uma pessoa antes de qualquer modelo. Depois vêm pedido vago (pedir detalhes), texto fora do
  vocabulário (pessoa) e a confiança do mesmo classificador da triagem ao vivo (automático, assistido ou pessoa).
  `tests/chat.mjs` testa 13 cenários e a detecção de idioma em Node.
- **Quem faz o quê na conversa:** a IA confirma o recebimento com protocolo, roteia quando a confiança passa do limiar e
  manda o link de autoatendimento de senha (🤖). O Gemini traduz o ticket e redige rascunhos; **nada que ele escreve
  chega ao cliente sem o clique do atendente** (🤝). No assistido, o atendente escolhe entre as 2 primeiras filas; na
  operação, a escolha viraria rótulo de treino (na demonstração, não é gravada).
- **Verificado no navegador, com o Gemini ativo:** os 7 cenários caíram na faixa prevista. O fluxo completo também foi
  percorrido: pedido vago → rascunho aprovado → cliente completa → nova triagem → Equipamentos com 99%. Também foram
  testados a escolha da 2ª fila no assistido, a mensagem do cliente depois da passagem para uma pessoa (anexada ao
  ticket), HTML digitado pelo cliente (escapado, nenhum elemento criado) e a tela de 375 px (sem rolagem horizontal).
  Console sem erros. Capturas 07 a 09 em `screenshots/`.
- **Erro da IA: rascunho sem acento.** 1 em 6 rascunhos do Gemini voltou sem nenhum acento. A função passou a pedir de
  novo quando o rascunho em português não tem acento; 8 de 8 depois da mudança.
- **Erro da IA: nome de fila.** "Minha senha expirou e não consigo entrar no Outlook" foi para *Administrative rights*
  com 96% a 97% (a tradução do Gemini varia entre execuções). No Dataset 2, 76% dos tickets com "outlook" estão nessa
  fila, então o modelo está certo. O nome em português que o chat mostrava ("Instalação de software") é que era
  estreito: virou "Software (Outlook, Windows)".
- **Erro da IA: a mesma faixa descrita de dois jeitos.** A página principal dizia "resposta automática pede o que falta";
  a revisão e o chat dizem que a IA redige e o atendente aprova. Ficou a versão com aprovação nos três lugares.

## 13. Validação cruzada: segunda opinião do Claude Chat (`validacao-cruzada/`)

- **O Pedro trouxe uma segunda opinião** do Claude Chat sobre o Dataset 1, pedida sem mostrar os achados desta
  entrega ([prints](validacao-cruzada/prints/)). Cada afirmação foi recalculada por
  `06_validacao_cruzada.py`: 19 afirmações, 16 confirmam, 2 divergem ("ruído uniforme", que é triangular, e "gênero
  uniforme", que não é), 1 não é verificável (o hash dos dois anexos).
- **Dois pontos que a análise principal não tinha:** 392 descrições são cópia exata de outra (47 grupos, nenhum com o
  mesmo e-mail ou assunto: é texto de template reaproveitado), e o brief lista 3 tipos de ticket enquanto o CSV tem 5.
  Os 2 tipos que faltam no brief (reembolso e cancelamento, 40,7% dos tickets) são os que a política manda para uma
  pessoa. Os dois entraram na revisão, Etapa 1, e o ROI não muda.
- **Erro da IA na própria verificação:** a primeira versão do script agrupou a "pior combinação" por assunto e achou
  outro resultado (n = 9). O n = 31 da segunda opinião só fecha agrupando por tipo (4 × 4 × 5 = 80 combinações).
  Refeito por tipo, confirma: desvio entre combinações 0,241, contra 0,240 com a nota embaralhada.

## 14. Validação final, export da conversa e fork (24/09)

- **Pedido do Pedro:** uma última checagem com portão de decisão. Se os números, as contagens e as conclusões batessem
  com os dados de origem, seguir para os prints, o export da conversa, o fork e o teste do protótipo; se não, parar e
  mostrar a divergência. Parte desta etapa rodou com o Claude Fable (o Pedro trocou o modelo com `/model`); o resto,
  com o Claude Opus.
- **Recálculo:** o pipeline reexecutado gerou JSONs idênticos aos commitados. 9 verificadores recalcularam em código
  784 afirmações da entrega; cada divergência passou por 3 refutadores (42 agentes). 7 alarmes foram refutados e **4
  confirmados, todos de texto**: a revisão humana dos rótulos marcada como feita com a coluna vazia; "errar quase
  metade" onde o erro é 55%; Purchase, Storage e Access como as filas mais precisas, sem Internal Project (90,4%); e os
  3 modelos maiores do Gemini "nas três execuções", quando dois só foram tentados na terceira. **A IA parou no
  portão.** O Pedro revisou os 40 casos (concordou com a IA em todos), as outras 3 frases foram corrigidas, e o portão
  foi reconferido em código antes de seguir.
- **Export:** o zip do app (31 MB, conversa + 54 subagentes) virou [`chat-export/`](chat-export/) por um gerador que
  confere a saída contra o bruto: 11 de 11 mensagens do Pedro e 100 de 100 textos do Claude idênticos, 471 chamadas de
  ferramenta, 0 dado pessoal. Uma revisão independente (7 lentes, 2 refutadores por achado, 63 agentes) confirmou 23
  de 28 achados; 22 foram corrigidos no gerador.
- **Erro da IA: chave do Gemini no export.** Na validação, a IA afirmou que nenhuma chave aparecia na transcrição. A
  busca só conhecia o formato antigo (`AIza…`), e a chave do Pedro está no formato novo, na saída do comando que
  renomeou o `.env`. Ela não está no repositório, no histórico do git nem na versão legível; está no zip bruto, que não
  é publicado. Recomendação: revogar.
- **Fork:** `P0lid0/ai-master-challenge`, criado em 24/09 com a conta pessoal do Pedro. A branch não foi enviada (o
  pedido era só o fork).
- **Teste final do protótipo**, com o servidor reiniciado do zero: rotas e API (tradução ok, entradas inválidas com
  400, caminho `../.env` com 404); página principal (ticket em inglês roteado sozinho para Hardware com 99,9% e rascunho
  do Gemini; ticket em português com 39% vai para uma pessoa, e depois da tradução vai sozinho para Access com 90,7%;
  tema sensível para uma pessoa; pedido vago pede detalhes; os 8 exemplos); simulador (2.500 tickets/mês: 91 h e
  R$ 43,6 mil por ano; 353/mês: 13 h); revisão (os 3 cenários iguais aos publicados, e o volume editável recalcula);
  chat (tradução e roteamento, pedido de detalhes aprovado e retriagem, regra de risco com rascunho enviado pelo
  atendente, escolha de fila no assistido); 3 suítes de teste; console e log do servidor sem erro.

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
| 12 | Modelo padrão do app e do benchmark já descontinuado (`gemini-2.5-flash`) | teste de fumaça com 7 modelos antes de rodar | 10 |
| 13 | Benchmark só gravava resultados no fim: uma falha na última rodada jogaria fora as anteriores | o modelo maior começou a devolver 503 e 429 em sequência | 10 |
| 14 | Chamou o arquivo de "o de 30 mil tickets" antes de medir | o Pedro questionou a contagem e pediu a reanálise | 11 |
| 15 | ROI com 2.500 tickets/mês chamado de "premissas conservadoras", sem avisar que o CSV não informa o volume | revisão pedida pelo Pedro + auditor de consistência | 11 |
| 16 | Percentuais 60/32/8 apresentados sem dizer que vêm da outra base | revisão pedida pelo Pedro | 11 |
| 17 | "Independentes" no README, quando o correto é "sem associação detectável" | verificador independente | 11 |
| 18 | Na revisão por chat: 5.868 descrições tratadas como "genéricas", mas todas continuam com mais texto | auditor da página de revisão | 11 |
| 19 | Na revisão por chat: elegibilidade do ROI fora do fluxo proposto (contou tickets que o fluxo manda para uma pessoa) | auditor da página de revisão | 11 |
| 20 | Na revisão por chat: C6 declarado "sem falsos alarmes" sem ler os 19 casos (4 são falsos positivos) | auditor + leitura caso a caso | 11 |
| 21 | Proxy de volume (registros ÷ meses de compra) rotulado como INFERÊNCIA, e é PREMISSA | auditor da página de revisão | 11 |
| 22 | Duas medidas de urgência misturadas numa frase (p = 0,024 da frase e 393 Low da lista ampla) | conferência ao montar a página | 11 |
| 23 | Teste do chat esperava "pedir detalhes" para português sem tradução; a regra de cobertura manda para uma pessoa | `tests/chat.mjs` | 12 |
| 24 | Rascunho do Gemini sem nenhum acento (1 em 6) | teste dos cenários no navegador + 6 chamadas repetidas | 12 |
| 25 | Fila *Administrative rights* chamada de "Instalação de software" no chat (76% dos tickets com "outlook" estão nela) | caso de senha do Outlook roteado para ela no teste | 12 |
| 26 | "Pedir detalhes" descrito como resposta automática na página principal, com aprovação na revisão e no chat | leitura do painel durante o teste | 12 |
| 27 | Caixa de mensagem do chat herdando 190 px de altura; texto branco sobre roxo claro no tema escuro | captura de tela com o Edge headless | 12 |
| 28 | "0 registros repetidos" sem conferir o texto sozinho: 392 descrições são cópia exata | segunda opinião do Claude Chat, recalculada | 13 |
| 29 | Tipos do CSV não comparados com os do enunciado (3 no brief, 5 no CSV) | segunda opinião do Claude Chat, recalculada | 13 |
| 30 | Script de verificação agrupando a "pior combinação" por assunto em vez de tipo | n = 9 não batia com o n = 31 afirmado | 13 |
| 31 | Documento da validação cruzada escrito em 1ª pessoa, atribuindo ao Pedro erros que foram da IA | releitura antes do commit | 13 |
| 32 | README com a revisão humana dos rótulos marcada como feita, com a coluna `veredito_pedro` vazia | validação final (recálculo + 3 refutadores) | 14 |
| 33 | "Rotear sozinho seria errar quase metade", com erro de 55% | validação final | 14 |
| 34 | Purchase, Storage e Access apresentadas como as filas mais precisas (Internal Project, 90,4%, estava acima de Access) | validação final | 14 |
| 35 | 3 modelos maiores do Gemini "falharam nas três execuções" (dois só foram tentados na terceira) | validação final, contra os logs brutos | 14 |
| 36 | "Nenhuma chave do Gemini aparece na transcrição": a busca só conhecia o formato antigo | revisão independente do export | 14 |
| 37 | Primeira versão do export legível com 22 defeitos (notificações que sumiam, escapes do markdown, prints cortando o pedido sem aviso, horário dos workflows) | revisão independente do export | 14 |
| 38 | O nome a omitir do export ficou gravado no próprio gerador, que seria publicado | varredura da pasta antes do commit | 14 |
