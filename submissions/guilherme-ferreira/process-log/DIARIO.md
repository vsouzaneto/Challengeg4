# Diário

Uma entrada por fase, sempre no mesmo formato: o que eu queria saber, o que pedi, o que a IA respondeu, como conferi, o que decidi e a fase em uma frase. As decisões, com as minhas falas citadas, estão em `DECISOES.md`; as explicações de cada opção estão nos transcripts.

---

## Fase 0 — Preparação do ambiente (25/09/2026)

**O que eu queria saber.** Se dava para começar sem risco de estragar a entrega: pasta certa, nenhum arquivo indevido no PR e um ambiente que outra pessoa consiga reproduzir.

**O que pedi.** "Vamos começar o teste." O Claude Code leu o meu plano, preparou o ambiente e parou para eu decidir cada escolha.

**O que a IA respondeu.**
- O próprio repositório do desafio manda o git ignorar a pasta `submissions/` inteira (linha 16 do `.gitignore` da raiz). Sem forçar, nenhum arquivo da entrega entraria no PR. Forçando a pasta inteira, a base de 23 MB entraria junto.
- As pastas criadas antes não batiam com o plano.
- Gráfico em plotly pode não aparecer no notebook visto pelo GitHub. Sugeriu matplotlib, que grava o gráfico como imagem.
- A captura automática de tela falhou: o macOS não dá ao Claude Code permissão para gravar a tela.

**Como conferi.** Comandos e saídas estão no transcript.
- `git check-ignore -v` mostrou a regra `submissions/` na linha 16 do `.gitignore` da raiz.
- 21 PRs de outros candidatos alteraram esse arquivo. Não alterei: o `CONTRIBUTING.md` diz que PR com arquivo fora da pasta do candidato é rejeitado.
- O ambiente novo abriu a base inteira (52.214 linhas, 27 colunas), e as versões instaladas batem com o `requirements.txt`.
- Antes do commit, a lista de arquivos preparados tinha só três: `.gitignore`, `requirements.txt` e este diário.

**O que decidi.**
- Criar a minha cópia do repositório no GitHub (fork).
- Dependências enxutas, com matplotlib no lugar de plotly.
- E-mail "noreply" do GitHub nos commits, para não expor meu e-mail.
- Não mexer no `.gitignore` da raiz. Cada arquivo entra pelo nome.
- Screenshots só da aplicação. Depois mudei: guardei também prints das minhas respostas nas perguntas de decisão.
- Aprovação manual durante a criação do fork e do ambiente. Depois disso, modo automático.

**Em uma frase.** Preparei o ambiente e descobri que o próprio repositório esconde a pasta de entrega do git, o que pede cuidado em cada commit.

**Transcript.** Sessão 1, em `evidencias/transcripts/`.

**Print.** `evidencias/screenshots/00-setup_01.png`: minhas respostas às perguntas sobre modo, fork, dependências e e-mail.

---

## Fase 1 — Baseline (feita no fechamento, 25/09/2026)

**O que eu queria saber.** O que uma IA entrega quando recebe só o enunciado e o CSV. Sem isso, não dá para mostrar onde a minha entrega vai além de "colei o enunciado na IA".

**O que pedi.** Um Claude sem nenhum contexto meu, só com o enunciado e o CSV. A IA tinha recomendado usar uma IA de outro fornecedor.

**O que a IA respondeu.**
- A primeira tentativa rodou como subagente da sessão de trabalho. A IA estranhou o agente escrevendo testes automáticos, que é uma regra minha, e foi olhar: ele tinha herdado o meu CLAUDE.md global e o do projeto, que descreve o meu método (limiar de 10%, Benjamini-Hochberg, mínimo de 30 posts). Ela parou o agente e descartou o resultado.
- Refez no modo seguro do Claude Code, numa pasta nova com o CSV, com o enunciado sem nenhuma alteração.
- Em 4 minutos, o baseline concluiu sozinho que o resultado não tem sinal e que o dado parece gerado.
- Ele não olhou a operação de patrocínio, não provou que o método acharia um efeito, usou o tamanho do creator depois de mostrar que essa coluna não é confiável e escreveu o process log como se fosse o candidato.

**Como conferi.**
- Antes do baseline, um teste curto na mesma configuração perguntou ao modelo se ele tinha recebido CLAUDE.md, memória ou regras. Resposta: "NENHUMA". O registro da sessão do baseline também não tem nenhum anexo de instruções.
- Conferi no dado uma afirmação dele que eu não tinha: a mistura de idiomas é a mesma em todas as plataformas, inclusive nas chinesas. Confere.
- Conferi cada contradição apontada contra o próprio texto dele e contra a minha análise.

**O que decidi.**
- Baseline num Claude sem contexto, do mesmo fornecedor, declarado como tal.

**Em uma frase.** Uma IA sem contexto descobre em 4 minutos que o dado não tem sinal; o que ela não entrega é o que fazer com isso na segunda-feira.

**Transcript.** Sessão 1, em `evidencias/transcripts/`, e a sessão do baseline em [`evidencias/baseline/transcript.md`](evidencias/baseline/transcript.md). A comparação completa está em [`evidencias/baseline/comparacao.md`](evidencias/baseline/comparacao.md).

---

## Fase 2 — Métricas, método e laudo do dado (25/09/2026)

**O que eu queria saber.** Se o arquivo consegue dizer o que funciona e se o método de análise acharia um efeito caso ele existisse.

**O que pedi.** "Segue ai." O Claude Code executou a Fase 2 do plano, escrevendo cada teste automático antes do código.

**O que a IA respondeu.**
- Views, likes, shares e comentários se comportam como sorteio em torno de um valor fixo: nas quatro métricas, o desvio-padrão é igual à raiz da média.
- O número de seguidores é sorteado de novo a cada post. Os 5.000 creators mudam de tamanho de um post para outro, então a faixa do creator não é confiável.
- As proporções são redondas, o patrocinador não tem relação com o conteúdo e os textos são palavras sorteadas.
- Na simulação, um efeito de +15% vira sinal sempre, +10% em metade das vezes e +3% nunca, sem nenhum falso sinal.
- A camada de "alocação" do meu plano também sai de sorteio, e o achado "95% dos posts em creators de 50 mil ou mais" não se sustenta.

**Como conferi.** Comandos, testes e saídas estão no transcript.
- 43 testes automáticos, cada um escrito antes do código e visto falhando antes de passar.
- Um teste de fronteira pegou um erro da IA: ela implementou a regra como "10% ou mais", mas o plano diz "mais de 10%". Corrigido.
- A simulação desmentiu o próprio plano, que dizia que um efeito de +10% "deve ser encontrado". Na prática, 10% é a fronteira da regra, e esse efeito vira sinal em 51,5% das rodadas.
- Na revisão do laudo, a IA viu que uma conta dela ("nenhum grupo difere em mais de cerca de 1%") só vale para grupos grandes. Para um grupo com 0,2% dos posts, a mesma conta deixaria espaço para cerca de 13% em shares. A afirmação saiu do laudo e do notebook, e a medição grupo a grupo ficou para a análise.
- O notebook roda do zero, e cada número do laudo aponta para a seção que o gera.

**O que decidi.**
- Manter as duas camadas, reescritas: "Resultado: sem sinal. Operação: sem critério." O achado das faixas de creator sai.
- Manter a simulação com +15%, +10% e +3% e explicar que 10% é a fronteira.
- Manter o limiar de 10%.
- Fazer push para o meu fork no fim de cada fase.

**Em uma frase.** O arquivo não diz o que funciona, e o método provou que diria se houvesse algo a dizer.

**Transcript.** Sessão 1, em `evidencias/transcripts/`.

**Print.** `evidencias/screenshots/02-laudo_01.png`: minhas respostas sobre a tese, a simulação e o push.

---

## Fase 3 — Análise das perguntas do Head (25/09/2026)

**O que eu queria saber.** O que o arquivo responde, e o que não responde, sobre cada pergunta do Head de Marketing.

**O que pedi.** "Pega os prints e segue pra próxima etapa." O Claude Code organizou os prints das decisões e executou a Fase 3, com os testes de cada função nova escritos antes do código.

**O que a IA respondeu.**
- Nenhuma das 240 comparações de plataforma, categoria e formato, para quatro objetivos, virou sinal. A maior diferença foi de 0,86%.
- Patrocinado e orgânico rendem igual (-0,01% de engajamento), mesmo comparando só posts da mesma plataforma, categoria e formato.
- Público, horário, volume de postagem e duração do vídeo também não mudam nada. Das 970 hashtags testadas, 59 pareceriam "campeãs ou vilãs" sem a correção para muitas comparações; nenhuma sobrevive a ela.
- A operação patrocina sem critério. O patrocinador combina com o conteúdo em 39,9% dos casos, igual a um sorteio. A parcela patrocinada é a mesma em toda plataforma, categoria e formato.
- O problema de "parceria de uma vez só", que o meu plano atribuía aos creators, está nos patrocinadores: 90% deles aparecem num post só, enquanto cada creator tem 10 ou 11 posts.

**Como conferi.** Comandos, testes e saídas estão no transcript.
- 4 testes novos (47 no total), escritos antes do código.
- Um teste do efeito estratificado falhou. A IA não mexeu no código antes de achar a causa. Comparou a regressão com a conta feita à mão, e as duas bateram. Depois rodou 400 sorteios, e o intervalo de 95% acertou em 93,8% deles. O erro estava no teste, que cobrava acerto num único sorteio, e ele foi reescrito.
- Outro teste foi ajustado antes de rodar. Com um efeito grande num grupo grande, os outros grupos pareceriam piores só por comparação: é o efeito espelho de comparar cada grupo com todos os outros.
- Cada número do `02_analise.md` foi conferido contra a saída do notebook. Três frases foram corrigidas.

**O que decidi.**
- As quatro práticas sem critério entram no "parar de fazer": patrocínio sem fit, divulgação fraca, patrocínio sem foco e parcerias de um post só.
- O mapa de patrocinador que combina com o conteúdo fica como premissa declarada.

**Em uma frase.** Nenhuma escolha muda o resultado neste arquivo; o que dá para corrigir é o jeito de patrocinar.

**Transcript.** Sessão 1, em `evidencias/transcripts/`.

**Print.** `evidencias/screenshots/03-analise_01.png`: minhas respostas sobre o "parar de fazer" e o mapa de fit.

---

## Fase 4 — Estratégia e plano de rastreamento (25/09/2026)

**O que eu queria saber.** O que o Head de Marketing pode fazer na segunda-feira, se o arquivo não diz o que funciona.

**O que pedi.** Seguir para a estratégia, usando as skills de influencer marketing, testes A/B e analytics como base.

**O que a IA respondeu.**
- A premissa de custo do meu plano (preço por faixa de creator) não funciona, porque a faixa não é confiável. Aplicar as faixas daria cerca de US$ 281 milhões em dois anos, calculados sobre seguidores sorteados.
- Cinco regras de patrocínio, cada uma com o número que a motiva, como medir e quando revisar: fit, divulgação explícita, foco, parceria recorrente e rastreamento.
- 94,3% dos posts patrocinados têm pelo menos um de três problemas: sem fit, divulgação implícita ou parceria de um post só.
- Com a variação das métricas ainda desconhecida, um teste que procure 10% precisa de cerca de 15 semanas; um que procure 20% cabe em 4.
- Plano de rastreamento com 9 eventos, cada um ligado à decisão que alimenta e ao que falta no arquivo do desafio.

**Como conferi.**
- A calculadora de amostra tem testes escritos antes do código. O resultado bate com a fórmula feita à mão e com a biblioteca statsmodels (52 testes no total).
- Cada número da estratégia foi procurado na saída do notebook (seção 3) antes do commit.
- A regra de divulgação cita fontes conferidas na web: a página da FTC e a atualização do guia do CONAR de 13/05/2026. Como não achei o documento oficial de 2026 do CONAR, o texto cita dele só o princípio de identificar a publicidade.
- As faixas de preço e a janela de direito de uso aparecem como referência da skill, não como fato de mercado verificado.

**O que decidi.**
- Custo implícito: premissa única de US$ 1.500 por post patrocinado, com sensibilidade de US$ 500 a US$ 5.000, ajustável no Radar.
- Ordem dos testes: H1 (fit), H2 (parceria recorrente), H3 (portfólio micro e nano), pela nota ICE.
- Donos das regras: time de parcerias (fit e recorrência), jurídico e social (divulgação), Head de Marketing (foco), analista de dados (rastreamento).
- Primeira rodada de testes procura efeitos de 20%, para caber em 30 dias.

**Em uma frase.** A estratégia corrige o patrocínio já e usa testes rastreados, o primeiro em 30 dias, para gerar o dado que o arquivo não tem.

**Transcript.** Sessão 1, em `evidencias/transcripts/`.

**Prints.** `evidencias/screenshots/04-estrategia_01.png` (custo por post) e `04-estrategia_02.png` (ordem dos testes, donos das regras e efeito mínimo).

---

## Fase 5 — Radar de Conteúdo (25/09/2026)

**O que eu queria saber.** Se dava para entregar ao time uma ferramenta de segunda-feira que funcionasse hoje com o arquivo do desafio e amanhã com o dado real, com a cara do G4.

**O que pedi.** Usar o site do G4 como base de UX. Depois aprovei o desenho parte por parte, a especificação ([docs/radar_desenho.md](../docs/radar_desenho.md)) e o plano, e pedi a execução nesta sessão.

**O que a IA respondeu.**
- Um desenho em quatro partes, que aprovei uma a uma: dados vindos de resumos gerados por script (a base bruta não entra no repositório), as quatro telas, o visual do G4 com rodapé de protótipo, e testes e deploy.
- No Streamlit Cloud, com o app numa subpasta, o arquivo de tema teria de ficar na raiz do repositório, o que as regras do desafio proíbem. Por isso o visual foi aplicado por CSS.
- Um plano de 10 tarefas, cada uma com os testes escritos antes do código. Ao fim das 10 tarefas, eram 83 testes; com as correções da revisão, 91; com os filtros de checkbox, 95.

**Como conferi.**
- Cada tarefa terminou com a suíte inteira passando e um commit. As decisões fora do plano ficaram registradas, com motivo e custo se estiverem erradas.
- Rodei o app e olhei cada tela, na largura normal e na de celular (375 px, sem rolagem lateral).
- A conferência na tela pegou quatro problemas que os testes não pegavam, e todos foram corrigidos:
  - com o sistema em modo escuro, os controles e as tabelas ficavam escuros sobre o fundo claro;
  - com seis indicadores numa linha, os números ficavam cortados;
  - "abaixo do limiar" aparecia sem explicação;
  - a tabela do mapa mostrava uma coluna de índice.
- A versão 1.64 do Streamlit recusa fixar o tema pelo código ("cannot be set on the fly"). Isso foi testado antes de escolher o caminho do CSS.
- **Revisão final independente.** Outra instância do Claude, no modelo Opus, que não participou da implementação:
  - conferiu a estatística contra a conta feita post a post;
  - regerou os resumos a partir do CSV;
  - olhou as telas em modo claro, escuro e no celular.

  Não achou nenhum problema crítico. Achou quatro importantes, todos corrigidos, cada um com um teste escrito antes da correção ou com medição na tela antes e depois:
  - no celular, as tabelas escondiam a coluna "Classe";
  - no modo escuro, os ícones de ajuda e os botões de opção sumiam;
  - o brief quebraria com dados de outro formato;
  - a semana padrão estava diferente da especificação, por um erro do plano.

  Duas observações menores foram tratadas como importantes e corrigidas: a legenda tinha contraste baixo e um texto dizia "dos posts" onde deveria dizer "dos posts patrocinados". Outras oito ficaram registradas para depois.

**O que decidi.**
- UX do g4business.com, com o logo do G4 e o rodapé "Protótipo de candidato ao AI Master Challenge, sem vínculo oficial com o G4".
- Dados vindos de resumos gerados por script; as quatro telas; top 3 e bottom 3 por grupo da semana.
- Execução nesta sessão, com uma revisão final independente.
- Depois de ver a tela, pedi para trocar a seleção múltipla dos filtros do mapa, que vazia ficava com texto invisível e borda vermelha. Primeiro virou caixa de seleção de um valor só. Depois, para poder marcar mais de um, virou uma caixa que abre com checkboxes e mostra o resumo da escolha ("Todas", "3 de 5").

**Em uma frase.** O Radar leva para a segunda-feira o que a análise mostrou: não mudar o mix por causa de ruído, corrigir o patrocínio e calcular o próximo teste antes de rodá-lo.

**Transcript.** Sessão 1, em `evidencias/transcripts/`.

**Prints.** `evidencias/screenshots/05-radar_01_brief.png` a `05-radar_06_brief_celular.png`: as telas do Radar, tiradas pela IA com o Chrome sem janela no fechamento. `05-radar_07_filtro_reprovado.png`: o filtro que reprovei na tela.

---

## Fase 6 — Fechamento (25/09/2026)

**O que eu queria saber.** Se a entrega se sustenta sozinha para quem abrir o PR: cada número rastreável, o processo à mostra, nenhum dado pessoal desnecessário e nenhum arquivo proibido.

**O que pedi.** "Segue pra fase 6." Escolhi o formato dos transcripts, tirar deles o meu CLAUDE.md global e manter o do projeto, e pus no README o LinkedIn do meu CV e o meu portfólio. No fim, pedi para usar o roteiro de decisões montado pela IA como `DECISOES.md`, para a IA tirar os prints e abrir o PR, dispensei a revisão por uma IA de outro fornecedor, mandei tirar dos transcripts a lista de pastas do meu vault e pedi um resumo das skills por etapa.

**O que a IA respondeu.**
- Um script que exporta cada sessão em Markdown legível e em JSONL compactado. Além do e-mail e dos caminhos da pasta pessoal, ele teve de tirar dado pessoal de lugares que a primeira versão não pegava: o CLAUDE.md global guardado em formato estruturado, o ID da organização, a cópia do prompt de sistema, caminhos usados como chave em registros internos, a lista de pastas do vault, os nomes dos meus outros projetos e os emojis que o próprio Claude Code grava.
- O README no template oficial, com a fonte de cada número e a comparação com o baseline, o `00_COMO_LER.md` em uma página e o `SKILLS.md`.
- Os prints das telas do Radar, tirados com o Chrome sem janela, porque a captura de tela do macOS não funciona para o Claude Code. Os prints que eu tinha colado no chat foram recuperados do registro da sessão.
- Uma revisão final independente, feita por outra instância do Claude, no modelo Opus. Ela conferiu cada número do README contra as fontes e o notebook, e todos batem. Reexecutou o notebook, os resumos e a simulação numa cópia limpa, com saídas idênticas, e rodou os testes sem o CSV. Apontou 20 problemas, quase todos afirmações imprecisas:
  - o limiar foi fixado antes de comparar os grupos, mas depois do perfil inicial do arquivo;
  - só o primeiro dos três testes cabe em 30 dias;
  - o papel do Fable na pesquisa estava subestimado;
  - três linhas do `DECISOES.md` estavam na seção errada.

**Como conferi.**
- O script conta o que sobrou de cada dado removido, em cada exportação. Resultado: zero para e-mail, pasta pessoal, CLAUDE.md global, ID da organização, prompt de sistema, lista do vault, nomes dos outros projetos e emojis.
- Cada imagem foi aberta e conferida antes de entrar no repositório.
- Os links relativos de todos os documentos foram conferidos por script.
- A branch só altera arquivos dentro da minha pasta.
- Cada ponto da revisão foi conferido no registro das sessões antes de ser corrigido. A seção do README "O que eu adicionei que a IA sozinha não faria" ficou como eu tinha pedido, só com uma correção de fato. A revisão observou que ela inclui escolhas em que aceitei a recomendação da IA; o `DECISOES.md` mostra quais.
- 95 testes passando, também numa cópia sem o CSV.

**O que decidi.**
- Transcripts em Markdown e JSONL compactado, sem o meu CLAUDE.md global e com o do projeto.
- LinkedIn e portfólio no README.
- Usar a lista montada pela IA como `DECISOES.md`, sem reescrevê-la.
- A IA tira os prints, o Radar fica rodando local e o PR sai no padrão do desafio.
- Sem revisão da análise por uma IA de outro fornecedor.
- Tirar dos transcripts a lista de pastas do meu vault e os nomes dos meus outros projetos.

**Em uma frase.** A entrega fecha com cada número rastreável, o processo à mostra e nenhum dado pessoal além do necessário.

**Transcript.** Sessão 1, em `evidencias/transcripts/`.
