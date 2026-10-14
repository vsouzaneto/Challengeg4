# Process Log: Jessé Rodolfo Machado, Challenge 002

Ferramentas: Claude Code (sessão dirigida pelo CLAUDE.md da pasta), Python, Git.
Regra deste log: escrito durante o trabalho, por mim, com horário. A IA lista o que fez; eu escrevo o que decidi e por quê.

---

Véspera (13/10, até 19:33): estrutura da pasta, kit de sessão (CLAUDE.md, commit.sh, guia de git), script de download e download dos CSVs. Nenhum dado aberto ou analisado; não conta no tempo.

---

## Bloco 0: Leitura do problema (antes de abrir qualquer dado)

Início: 07:30  Fim: 07:55

O que o diretor quer saber: onde o time está perdendo tempo, o que dá pra deixar a IA fazer sem estragar o atendimento, e ver alguma coisa funcionando de verdade, não slide.

O que eu acho antes de olhar os dados:

O tempo não se perde resolvendo o problema, se perde esperando. Ticket parado sem ninguém pegar, ticket esperando o cliente responder, fila de um canal mais lenta que a de outro. Vi isso na fábrica e vi na logística: espera é o desperdício mais fácil de cortar e o que ninguém mede.
Desconfio que o ticket marcado como crítico não está sendo resolvido mais rápido que o médio. Se for isso, a prioridade é só uma etiqueta que ninguém usa.
Telefone e rede social devem demorar mais pra resolver que e-mail e chat, porque não fica registro organizado do que o cliente pediu.
O que derruba a nota do cliente é demorar pra dar a primeira resposta, mais do que demorar pra resolver. Cliente aguenta esperar a solução se alguém falou com ele logo.
Reembolso, problema de pagamento e cancelamento são os tickets que mais custam quando atrasam. Reembolso é dinheiro saindo, pagamento é dinheiro entrando, cancelamento é cliente indo embora. Esses merecem uma fila separada.
Classificar ticket pelo texto a IA faz bem e barato. O que não pode ser automático é decidir sobre dinheiro e lidar com cliente que já está irritado. Aprendi isso operando meus próprios agentes.

Como vou usar os dois arquivos: o dataset 1 é a operação que eu vou diagnosticar; o dataset 2 é o material para provar que a classificação automática funciona antes de propor ela para a operação. São duas organizações diferentes e não vou misturar.

O que vai me fazer desconfiar dos dados: coluna de tempo que na verdade é data e hora, não duração; nota de satisfação preenchida só em parte dos tickets; texto de ticket com cara de inventado; quantidade de linhas diferente dos 30 mil que o brief fala; e aquele “outros” do Kaggle, que eu já percebi que pode ser só o jeito do site resumir a coluna, e não uma categoria perdida.

O que eu decidi não fazer: não vou propor automação antes de fechar o diagnóstico; não vou misturar os dois arquivos como se fossem a mesma empresa; e não vou montar tela bonita antes de medir se o classificador acerta.

**Problema de setup encontrado:** o .gitignore da raiz do repositório ignora submissions/. Resolvido com `git add -f` dentro da minha pasta, sem tocar em arquivo fora dela.

Commit: 15166ae

---

## Bloco 1: Auditoria dos dados

Início: 07:58  Fim: 08:15

8:00 a 8:02 parado por bloqueio de permissão do macOS na pasta Documentos, resolvido liberando acesso para o Terminal. Tempo de setup, não de análise.

**O que pedi à IA:**

**O que a IA afirmou e eu mandei verificar:**

**Onde a IA errou e como corrigi:**
- Primeira versão de `solution/analise/01_auditoria.py` usou a coluna `Product`, que não existe no dataset 1 (o nome real é `Product Purchased`). O script quebrou com KeyError antes de calcular qualquer coisa. Corrigido o nome e rodado de novo; nenhum número foi afirmado com a versão errada.

**Hipóteses do Bloco 0 confirmadas pela auditoria (escritas às 07:30, antes de abrir os dados):**
- Tempo como carimbo de hora: First Response Time e Time to Resolution são data e hora, todos entre 2023-05-31 21:53 e 2023-06-02 00:55. Não existe data de abertura, então não há duração calculável.
- O "outros" do Kaggle: o dataset 2 tem exatamente 8 categorias nomeadas, somando 47.837 de 47.837 linhas, sem nulo e sem categoria "Other". O "outros" era resumo da página do Kaggle, não categoria perdida.
- Satisfação preenchida só em parte: Customer Satisfaction Rating existe em 2.769 de 8.469 tickets (33%), só nos de status Closed.
- Texto com cara de inventado: 8.469 de 8.469 descrições têm o placeholder `{product_purchased}` sem substituir, e só 16 frases de abertura distintas.
- Quantidade diferente dos 30 mil: o D1 tem 8.469 tickets (28% dos 30 mil do brief).

**Lista da IA: o que fez e o que achou (para eu editar):**
- Escreveu e rodou `solution/analise/01_auditoria.py` nos dois CSVs brutos; resultado completo em `docs/auditoria-dados.md`.
- D1: 8.469 tickets (28% dos 30 mil do brief), 0 duplicados, 139 e-mails repetidos sempre com nome diferente.
- D1: nulos seguem o status. Open (2.819) sem nenhum tempo; Pending Customer Response (2.881) só com primeira resposta; Closed (2.769) com tudo.
- D1: Time to Resolution menos First Response Time é negativo em 1.365 de 2.769 fechados (49%).
- D1: CSAT só nos fechados, plano de 1 a 5, nenhum teste significativo (chi2 e Kruskal com p entre 0,148 e 0,876 para prioridade, canal, tipo, assunto, produto, gênero).
- D1: texto gerado. 100% com `{product_purchased}` sem substituir, 16 frases de abertura distintas, Resolution aleatório, tipo x assunto independentes (p=0,981).
- D1: categorias uniformes; prioridade não depende do tipo (p=0,561) nem do canal (p=0,078).
- D2: 47.837 textos realistas, 8 categorias desbalanceadas (Hardware 28,5% a Administrative rights 3,7%), ruído de rótulo visível.
- D1 x D2: categorias não correspondem; classificador não pode ser medido no texto do D1.

**O que os dados permitem concluir e o que não permitem:**

**Decisão minha:**
O D1 não serve para medir tempo nem satisfação, e eu vou provar isso em vez de fingir que serve. O que ele tem de confiável é a estrutura do backlog: 67% não fechados (33% abertos e 34% esperando o cliente), o que já sustenta a minha hipótese de que o desperdício está na espera. O diagnóstico vai dizer com clareza o que dá para afirmar, o que não dá, e o que a operação precisa registrar para passar a dar. O desperdício eu calculo em faixa, por premissa, sobre os 30 mil tickets por ano do brief, com cada premissa escrita para o diretor trocar pelo número dele. O D2 fica para provar que classificar ticket por texto funciona. Já vivi essa situação na logística: o indicador oficial escondia 500 pedidos, e a decisão certa foi consertar a medição antes de expandir. Aqui é a mesma coisa: instrumentar antes de automatizar.

Commit: 76fe526

---

## Bloco 2: Diagnóstico

Início: 08:18  Fim: 09:12

**Os cinco números que importam:**
1. 67% dos tickets não fechados (33% abertos e 34% esperando o cliente). O desperdício está na espera.
2. Nada explica a satisfação: modelo com todas as variáveis acerta 20,0%, chutar a nota mais comum acerta 20,9%.
3. Os campos de tempo não medem tempo: em 49% dos fechados a resolução vem antes da primeira resposta.
4. Desperdício estimado de 1.042 a 11.400 horas por ano, caso base 3.950 (2,5 agentes), com cada premissa escrita.
5. Maior item recuperável: cobrança de cliente parado, 1.700 horas por ano, recuperável por automação.

**Premissas que eu defini para o cálculo de desperdício:**
- As premissas originais do cálculo foram propostas pela IA, sem medição.
- Custo da hora substituído por dado da minha operação de atendimento, que era de venda e não de suporte: só comissão deu R$ 56 a 74 por hora (10% de ticket médio R$ 297, 15 a 20 vendas por dia, 8 horas); fixo mais comissão deu R$ 29 a 37 (R$ 1.200 fixo mais 4%, 22 dias, 176 horas). Usei piso R$ 30, base R$ 50, teto R$ 70.
- Horas produtivas mantidas em 1.600 por agente por ano: conservador para CLT de 44 horas, descontando férias e feriados.
- Triagem substituída por medição minha (abaixo): piso 20 s, base 30 s, teto 3 min.
- Repasse e cobrança ficaram como premissa declarada, marcadas "premissa não medida, a confirmar na primeira semana do piloto", por falta de medição. Isso é a recomendação 1.

**Cronometragem da triagem (5 tickets aleatórios do dataset 2, seed 20261014, categoria escondida):**

| Ticket | Tempo | Minha resposta sem ajuda | Depois da revisão com segundo modelo | Rótulo do dataset |
|---|---|---|---|---|
| 1 (linha 1461, "new pool and reservations") | 34,65 s | Internal Project ❌ | Internal Project ❌ | Miscellaneous |
| 2 (linha 34400, "warning laptop anti software") | 21 s | HR Support ❌ | Hardware ✅ | Hardware |
| 3 (linha 13309, "admin rights on groups") | 10 s | HR Support ❌ | Administrative rights ❌ | Miscellaneous |
| 4 (linha 21921, "confluence external users to remove") | 24,81 s | Access ✅ | Access ✅ | Access |
| 5 (linha 18186, "access unable log permission") | 9,24 s | Access ❌ | Access ❌ | Hardware |

Média 19,94 s. Acerto contra o rótulo do dataset: sem ajuda 1 de 5; depois da revisão com segundo modelo 2 de 5.

Correção deste log: a primeira versão registrou Hardware e Administrative rights nos tickets 2 e 3 como respostas minhas. Eram a leitura do meu revisor (segundo modelo). Minhas respostas originais, sem ajuda, foram HR Support nos dois.

Minhas observações sobre a medição: o texto veio pré-processado, sem pontuação, com palavras repetidas e sem separar a assinatura do e-mail do corpo do pedido. A leitura foi de palavra-chave, não de entender o problema. Com o texto original um humano triaria melhor e levaria uns 10 segundos a mais por ticket. No ticket 2 a assinatura "annual leave december" me puxou para RH, quando o pedido era um aviso de antivírus no laptop.

Consequências que levo para a proposta:
1. Triagem humana em texto ruim erra. Isso justifica classificador com limiar de confiança e humano confirmando o que tiver confiança baixa.
2. Em produção o classificador recebe o texto original do ticket, não o pré-processado, com a assinatura do e-mail removida antes de classificar.

**Etiquetas de recuperação:** a IA propôs cobrança do cliente como recuperável por processo. Discordei: é recuperável por automação, com lembrete automático e encerramento após prazo.

**Lista da IA: o que fez e o que achou (para eu editar):**
- Escreveu e rodou `solution/analise/02_diagnostico.py`; resultado em `solution/01-diagnostico.md`. Testes estatísticos movidos para `docs/auditoria-dados.md`.
- Status não depende de prioridade (p = 0,227), canal (p = 0,771) nem tipo (p = 0,339). A amplitude de 24 pontos entre 80 combinações cabe no acaso (permutação: 17,9 a 27,1 pontos).
- CSAT: modelo com todas as variáveis acerta 20,0%, abaixo dos 20,9% do chute da nota mais comum.
- Desperdício com as premissas finais: 1.042 a 11.400 h/ano, base 3.950 h, 2,5 agentes, R$ 198 mil/ano. Maior item recuperável: cobrança do cliente, 1.700 h no base.
- Sensibilidade: as duas premissas que mais mexem no total são do ciclo de cobrança (amplitude 1.700 h cada), seguidas da triagem (1.333 h). Repasse fica empatado com pendente e reabertura (1.000 h).
- 60,0% dos tickets do dataset 1 são do tipo Refund, Billing inquiry (dúvida ou disputa de fatura) ou Cancellation; só 18,8% têm assunto Refund, Payment ou Cancellation.

**Onde a IA errou e como corrigi:**
- A IA propôs triagem de 1,5 a 5 minutos por ticket, sem medição. Cronometrei 5 tickets aleatórios: média 19,94 s. A premissa de triagem caiu para 20 s a 3 min, e a triagem no caso base caiu de 1.500 h/ano para 250 h/ano. O total base caiu de 5.200 h para 3.950 h.

**O que eu adicionei que a IA sozinha não faria:**
Desconfiei do dado antes de abrir e provei que ele não mede tempo nem satisfação. A IA desta sessão fez a auditoria antes de qualquer média porque o CLAUDE.md que eu escrevi mandou desconfiar primeiro. Sem essa direção, o caminho padrão seria calcular médias por canal e prioridade e apresentar como gargalo. Troquei as premissas dela pelo custo da hora da minha operação e pela triagem cronometrada em mim mesmo, e deixei por escrito o que ninguém mediu. Decidi responder as três perguntas do diretor mesmo com dado ruim, em faixa e com sensibilidade, em vez de só dizer que o dado não serve. Classifiquei o desperdício por recuperabilidade e coloquei a cobrança de cliente como automação, porque já operei isso. E mantive a tabela de sensibilidade como saiu, sem mexer em premissa para o resultado ficar como eu esperava.

Commit: ce37da8

---

## Bloco 3: Proposta de automação

Início: 09:58  Fim: 11:00

Pausa de 09:28 a 09:43 para café, fora do tempo de trabalho.

**Fluxo decidido (ticket entra até humano):**
- Piloto: um canal, só a cobrança do cliente, com três contadores: lembretes enviados, encerrados automaticamente e reabertos depois do encerramento.
- Triagem e roteamento ficam como fase 2, que só entra em produção depois dos quatro campos instrumentados e do limiar de confiança calibrado com tickets reais.
- O protótipo do Bloco 4 é a prova de viabilidade da fase 2, não o piloto.
- Não escolhi juntar cobrança e triagem no mesmo piloto porque com os dois juntos não dá para saber qual causou o resultado. Essa é a regra de piloto que eu uso desde a fábrica.
- Quatro portões humanos: confiança abaixo do limiar, cliente já insatisfeito, disputa financeira (reembolso, cobrança, cancelamento) e ticket crítico com sugestão da IA mas sem resposta automática.

**O que NÃO automatizar e o exemplo dos dados que justifica cada item:**
Não automatizar: os portões de autoridade (reembolso, dúvida ou disputa de fatura, cancelamento, crítico, cliente já insatisfeito), 75,3% dos tickets do dataset 1, e qualquer resposta que não esteja no banco validado.

**Fechamento do Bloco 3 (decisões minhas, substituem as anteriores onde houver conflito):**
- Regra mestra: a IA só responde o que existe no banco de respostas validadas; o que não existe vai para humano validar uma vez e entra no banco. É o desenho do meu produto de atendente de IA, não resultado medido em escala.
- Portões por autoridade, mesmo com resposta no banco: reembolso, dúvida ou disputa de fatura, cancelamento, crítico e cliente já insatisfeito. Acesso à conta e perda de dados saem dos portões e vão para entrada estruturada.
- Crítico por regra operacional (serviço fora, pagamento bloqueado, perda de dados confirmada), não por escolha do cliente.
- Passo zero: entrada estruturada com menu e 2 ou 3 campos obrigatórios por tipo; classificador confere o texto livre; se divergir, humano. Entra na recomendação 1.
- Piloto "Lembrete de cliente parado": só e-mail, lembretes em 2 e 5 dias úteis, encerramento em 7, 8 semanas, parada acima de 20% de reabertura. Chat fica para onda posterior com régua de inatividade em minutos.
- Implantação 20 a 40 horas, pela minha experiência. O piloto se justifica como instrumentação.
- Fase 2 com parada: menos de 60% acima do limiar de confiança ou mais de 15% de correção humana.
- Aprendizado: resolução repetida com nota 4 ou 5 vira resposta sugerida; nota 1 ou 2 vai para revisão. Resolução ligada à nota vira o quinto campo.

**De onde veio o critério do portão humano:**
Da regra do meu projeto de atendente de IA, que não inventa: responde só o que está no banco validado e chama humano para validar o resto uma vez. Dinheiro e crítico são portão por falta de autoridade, não por falta de resposta: reembolso tem resposta conhecida, mas quem aprova é gente. Crítico vem da fábrica: parada de linha se resolve com gente com autoridade, não com procedimento automático.

**Onde a IA quis automatizar demais e eu segurei:**
Não aconteceu. Aconteceu o contrário: a IA ampliou "não automatizar" de quatro portões para sete itens, incluindo acesso à conta e perda de dados, que são os mais padronizáveis. Segurei para o outro lado. A IA ofereceu estender o piloto a dois canais e eu fiquei só com e-mail, porque pendência significa coisas diferentes em cada canal.

**O que eu adicionei que a IA sozinha não faria:**
A regra mestra do banco de respostas validadas, que é o meu produto; a entrada estruturada, que vem das empresas em que vi funcionar e da minha própria triagem errando por assinatura no texto. A IA tratou o texto do ticket como entrada fixa a classificar; eu tratei como algo a padronizar antes de chegar na ferramenta.

**Lista da IA: o que fez e o que achou (para eu editar):**
- Escreveu e rodou `solution/analise/03_proposta.py`; resultado em `solution/02-proposta-automacao.md`, contagens no anexo de `docs/auditoria-dados.md`.
- Primeira versão da proposta: 7 itens em "não automatizar" (incluía acesso à conta e perda de dados), canal Email, régua 2/5/7 dias, 8 semanas, parada em 20%, implantação 120/60/30 h. Lembrete para todo pendente, encerramento automático só fora dos portões.
- Corrijo: eu disse que 78,8% dos tickets caem em portão; com acesso à conta e perda de dados fora dos portões, os portões de autoridade (financeiro ou Critical) somam 75,3%.
- Só 24,2% dos pendentes são elegíveis a encerramento automático. Email: cerca de 50 pendentes e 4 encerramentos por semana na escala de 30 mil/ano; 34 em 8 semanas.
- ROI recalculado com implantação 40/30/20 h: líquido 97 / 1.161 / 4.855 h/ano em todos os canais; só Email R$ 0,7 mil / R$ 14,7 mil / R$ 86 mil por ano; retorno da implantação 19,6 / 1,2 / 0,2 meses. Premissas da IA mantidas e declaradas: substituição 50/70/90%, encerrados 50/35/20%, reabertura 20/10/5%.
- Dataset 2: até 84,9% dos textos têm "thanks", "regards", "best" ou "annual leave"; "out of office" não aparece. É teto, porque "thank" também é cortesia no meio do pedido.
- Resolution: 2.769 textos únicos em 2.769 fechados, nenhum repetido no mesmo assunto. A regra de aprendizado não é testável neste dataset.

Commit: aace227

---

## Bloco 4: Protótipo

Início: 11:05  Fim: 11:15

Executor trocado de Opus 5.5 para Sonnet 5.5 neste bloco, por limite de uso do Opus (89% às 10:57, janela volta às 12:20). Os Blocos 0 a 3 foram feitos com Opus 5.5; o código do protótipo e a medição do Bloco 4 foram feitos com Sonnet 5.5.

**O que construí e o que deixei de fora de propósito:**
O que construí: três arquivos em solution/prototipo. treinar.py treina o classificador e mede. rotear.py recebe o texto do ticket e devolve categoria, confiança e rota (automático ou humano). test_rotear.py com 5 testes. README do protótipo com a tabela de limiar. Sem Streamlit por decisão minha: CLI com testes já prova o fluxo, e guardei a cota de uso pro Bloco 5.

**Como medi (tamanho da amostra aleatória, acurácia, matriz de confusão):**
Como medi: os 47.837 tickets do dataset 2 já vinham com categoria marcada. Separei 20% (9.568) antes de treinar, treinei nos 80%, classifiquei os escondidos e comparei com a marcação. Acurácia 85,69% contra 28,47% de chutar sempre Hardware. Depois medi cobertura e acerto nos aceitos pra limiares de 0,5 a 0,9 e escolhi 0,7: 62,9% dos tickets passam do limiar; tirando os portões, 57,3% ficam automáticos com 96,5% de acerto. Limite da medição: o texto do dataset 2 já vem limpo; com texto real a cobertura pode cair.

**Testes de regressão escritos:**
Testes de regressão: 5 testes pytest, todos passando. Modelo carrega; texto vazio vai pro humano; confiança baixa vai pro humano; categoria de portão vai pro humano mesmo com confiança 0,9; texto claro de Purchase acerta a categoria. Protegem a regra de roteamento, não a acurácia do modelo.

**Onde a IA errou (código, avaliação, categorias) e como corrigi:**
- A IA apontou que o texto do campo "Como medi" dava 62,9% como automático com 96,7% de acerto. Esse é o número de passar do limiar; o automático, tirando os portões Purchase e Administrative rights, é 57,3% com 96,5% de acerto. Correção aceita por mim e aplicada no texto.

**Iterações até funcionar:**
Uma passada: `treinar.py`, `rotear.py` e `test_rotear.py` rodaram na primeira execução (5 testes passando). Depois, um ajuste no teste do portão para afirmar confiança de 0,9 ou mais, em vez de só desligar o limiar.

**Decisões minhas no Bloco 4:**
- Limiar 0,7 e portões `Purchase` e `Administrative rights` foram propostos pela IA e confirmados por mim com este raciocínio. Purchase é dinheiro e precisa de quem aprova a compra. Administrative rights é alçada: dar privilégio de administrador é decisão de segurança. Access fica fora dos portões, coerente com o Bloco 3, onde acesso à conta saiu dos portões.
- Limiar 0,7 porque categoria errada vira resposta validada errada para o cliente. Um erro em 30 nos aceitos é o máximo que aceito no piloto. O limiar 0,9 cobre só 38,7% e não paga o piloto.
- A cobertura de 62,9% no limiar 0,7 ficou perto da parada de 60% da fase 2. A regra de parada não muda depois de ver o número; o piloto com texto real decide.
- Ideia minha para depois da fase 1: o portão de Administrative rights pode virar verificação contra uma lista de autorizados mantida por quem tem alçada, e o humano só vê a exceção. O mesmo raciocínio vale para Purchase, com teto de valor. Fica como portão na fase 1 porque essa lista não existe no dataset.

- Limite levantado na revisão com o segundo modelo e confirmado por mim: Administrative rights com recall de 61,4%. Quatro em 10 pedidos saem como outra categoria. Medido no held-out: 30 dos 352 (8,5%) chegam a "automático"; os outros vão para humano pelo limiar. Na fase 2 o portão não pode depender só do classificador: palavra-chave (admin, rights, permission) como segunda trava, e ticket cuja segunda categoria mais provável é portão vai para o humano. Dos 30 que escapam, 25 têm segunda categoria portão; a regra mandaria também 447 dos 5.486 automáticos (8,1%) para humano.
- O segundo commit "bloco4: prototipo" é a correção do 62,9% para 57,3% no texto "Como medi".

**Lista da IA: o que fez e o que achou (para eu editar):**
- Escopo seguido como pedido: `treinar.py`, `rotear.py`, `test_rotear.py` e `README.md` em `solution/prototipo/`. Sem Streamlit.
- Held-out de 9.568 tickets (20% estratificado, seed 42): acurácia 85,69%, contra 28,47% da classe majoritária (Hardware).
- Limiar 0,5 / 0,6 / 0,7 / 0,8 / 0,9: cobertura 82,7 / 73,1 / 62,9 / 52,0 / 38,7%; acurácia nos aceitos 92,1 / 94,6 / 96,7 / 98,0 / 99,3%.
- Escolhas minhas, a confirmar: limiar padrão 0,7 e portões `Purchase` e `Administrative rights` (as duas categorias do dataset 2 mais próximas de dinheiro e autoridade). Com elas, 57,3% do held-out vai para "automático" com 96,5% de acerto.
- Resíduo removido: "thanks", "thank", "regards", "best", "annual leave". Incluí "thank" além de "thanks", como na contagem da auditoria.
- Para o modelo não subir no commit: `.gitignore` local e uma exclusão em `commit.sh`, porque `git add -f` ignora o `.gitignore`.
- Cobertura de 62,9% no limiar 0,7 está perto da regra de parada da fase 2 (pausar abaixo de 60%).

Commit: 071cae3 e 9b1efb9 (o segundo corrige 62,9% para 57,3%)

---

## Bloco 5: Fechamento

Início: 11:35  Fim: 12:30

Executor do Bloco 5: Sonnet 5.5, o mesmo do Bloco 4 (limite de uso do Opus; janela volta às 12:20).

**O que cortei do documento final para ficar curto:**
A tabela de premissas (ficou a linha apontando pro diagnóstico), o fluxo 0 a 6 (ficou em duas linhas), abordagem, workflow e limitações encurtados, e a duplicata entre "o que adicionei" e "o que fiz diferente do baseline". Motivo: README é pra decisão em cinco páginas; o detalhe está nos documentos de solution/.

**Limitações que assumi por escrito:**
Dataset 1 sintético, desperdício por premissa e não por medição; repasse, cobrança e reabertura não medidos; piloto com volume pequeno; acurácia contra rótulo com ruído; limiar e portões não calibrados com tickets reais; Administrative rights com recall de 61,4% e 8,5% escapando do portão; sem interface gráfica.

**Falha da ferramenta de commit, encontrada na revisão final e corrigida:**
A revisão final (Opus 5.5, só leitura) achou `.pytest_cache/` (4 arquivos) e `solution/prototipo/__pycache__/` (3 .pyc) commitados no `071cae3`. O padrão `:!.../**/__pycache__` do `commit.sh` não excluía nada, porque sem a opção glob do git o caminho precisa bater inteiro, e `.pytest_cache` não tinha exclusão. Correção: os 7 arquivos saíram do índice com `git rm -r --cached` (continuam no disco); o `commit.sh` passou a usar `:(exclude,glob)` para `__pycache__`, `.pytest_cache`, `*.pyc` e `.ipynb_checkpoints`; o `.gitignore` local ganhou `.pytest_cache/`; e o `commit.sh` ganhou uma trava que recusa `.pyc` ou `.pytest_cache` no commit, igual à do CSV. Testado com `git add -n -f`: nenhum desses arquivos entra.

**Tempo total:**
4 h 43 líquidas em 5 h decorridas (07:30 a 12:30, 17 min de pausa). Intervalos entre blocos foram checkpoints com o revisor, log e commits.

Commit: ef81233, mais o commit final deste fechamento

---

## Resumo para o README (preencher no fim)

| Ferramenta | Para que usei |
|---|---|
| Claude Code | Executor em todos os blocos (Opus 5.5 nos Blocos 0 a 3, Sonnet 5.5 nos Blocos 4 e 5) |
| Python | Análise, classificador e testes |
| Git | Um commit por bloco via commit.sh |

Iterações totais: 5 blocos, uma rodada de pendências em cada, correção extra nos Blocos 2 e 4.
Maior erro da IA no processo: triagem de 1,5 a 5 min sem medir, 1.250 h a mais no caso base.
Maior contribuição minha: regra mestra com portões de autoridade, entrada estruturada e auditar os dados antes de diagnosticar.
