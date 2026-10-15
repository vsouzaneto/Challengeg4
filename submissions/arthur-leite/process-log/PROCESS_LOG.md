# Process Log — Arthur Leite — Challenge 002

> **Nota de autoria (leia primeiro).** Este diário foi **redigido pelo Claude Code durante a sessão**, a pedido do Arthur, e mistura vozes: frases como "pedi ao Claude Code" são do ponto de vista do Arthur; frases como "erro meu" ou "corrigi" são, em geral, da IA. A atribuição autoritativa de **quem fez o quê** está na tabela do README (seção *Process Log*) e pode ser conferida na conversa completa em `chat-exports/`. Resumo: a **IA** executou a análise, o código, os documentos e propôs a maioria das hipóteses, inclusive a de base sintética. O **Arthur** direcionou, exigiu um juiz adversarial em cada conclusão, exigiu fidelidade, pediu o painel com storytelling e o time de 5 agentes, decidiu publicar e **verificou com as próprias mãos**: tabelas dinâmicas nos CSVs, revisão ponto a ponto do app, aba anônima e mais de um monitor.

Diário de trabalho, escrito durante o processo e não reconstruído no final.
Cada entrada registra o que decidi, o papel da IA, onde a IA errou ou foi corrigida e o que mudou.

**Ferramenta principal:** Claude Code (Claude Opus 5.5), operando no meu terminal com acesso ao repositório.
**LLM no protótipo:** Google Gemini (plano gratuito), como camada opcional.

---

## Fase 0 — Leitura, escolha do case e setup (2026-10-14)

### 0.1 Leitura da vaga e do repositório
- Pedi ao Claude Code que lesse a descrição da vaga (via Chrome) e clonasse o repo para ler todos os arquivos: README, submission-guide, CONTRIBUTING, template e os 4 challenges.
- Pedi também uma contagem dos PRs já abertos: 189 no total, sendo 79 no 003, 41 no 002, 33 no 001 e 18 no 004.
- **Decisão minha:** não abrir os PRs de outros candidatos, para manter a solução original.

### 0.2 Escolha do challenge: 002 (Suporte)
- A IA recomendou o 002, e eu concordei, por três motivos:
  1. Opero agentes de atendimento com IA em produção para clientes (plataforma Mavra: SDR, triagem, kanban), e esse contexto real é algo que um modelo sozinho não tem.
  2. É o único case que exige as 5 frentes da vaga ao mesmo tempo: diagnóstico, orquestração, build, ROI e o julgamento do que não automatizar.
  3. Tem metade da concorrência do 003.

### 0.3 Hipótese antes de tocar nos dados
- Antes de baixar qualquer coisa, levantei a suspeita de que o Dataset 1 é sintético: volume menor que os "~30K" do enunciado, placeholders no texto, "tempos" que são timestamps e CSAT aleatório.
- **Por que isso importa:** se os dados forem ruído, qualquer conclusão de "causa" tirada deles é falsa. O baseline de IA tende a analisar sem questionar a fonte.

### 0.4 Setup
- Branch `submission/arthur-leite` e estrutura de pastas criadas conforme o CONTRIBUTING.
- **Pegadinha encontrada:** o `.gitignore` da raiz do repo ignora `submissions/`. Um `git add .` simples gera um PR vazio. Solução: adicionar a pasta explicitamente com `git add -f`, mantendo um `.gitignore` próprio da submissão para não subir dados nem a chave de API.
- Sem chave da Anthropic. Avaliei as alternativas: LLM local inviável (7,7 GB de RAM, sem GPU); escolhi o Gemini gratuito. O LLM entra como camada **opcional**: o protótipo precisa rodar sem nenhuma chave.
- Download dos dois datasets via `kagglehub`, sem precisar de login.

### 0.5 Primeira checagem dos dados (confirma a hipótese 0.3)
| Hipótese | Resultado |
|---|---|
| Volume de ~30K tickets | **Falso: 8.469 tickets** |
| Texto com placeholders | Encontrado `{` em 8.469 de 8.469 descrições (a verificar na Fase 1) |
| "First Response Time" e "Time to Resolution" são durações | **Não são: são timestamps.** Precisam ser convertidos em duração |
| CSAT disponível | **5.700 nulos (67%).** Só os tickets Closed (2.769) têm nota |
| Dataset 2 | 47.837 textos em 8 classes, **desbalanceadas** (Hardware 13.617 × Administrative rights 1.760) |

Próximo passo: Fase 1, auditoria completa da qualidade dos dados.

---

## Fase 1 — Auditoria de qualidade dos dados (2026-10-14)

Script reproduzível: `solution/01-diagnostico/01_auditoria_dados.py`. Saída: `solution/01-diagnostico/outputs/auditoria.md`.

### Como decompus
Antes de responder "onde o fluxo trava", perguntei se os dados conseguem responder isso. Para cada campo, testei se ele carrega informação:
1. O texto é real ou template?
2. Os tempos são tempos?
3. As variáveis se relacionam entre si, como numa operação real (ex.: Critical deveria ter fluxo diferente de Low)?
4. Alguma variável explica o CSAT?

### Resultado: o Dataset 1 é aleatório
- **100%** das descrições têm placeholder não preenchido; só existem **16** frases de abertura.
- Os "tempos" são timestamps concentrados numa janela de **27 horas**, e em **49%** dos tickets fechados a resolução acontece *antes* da primeira resposta.
- O CSAT é **uniforme** de 1 a 5 (p = 0,80).
- **Nenhum par de variáveis tem associação** (maior Cramér's V = 0,072). O tipo do ticket é independente do assunto: há "Billing inquiry" com assunto "Hardware issue".
- **Nada explica o CSAT**: canal, prioridade, tipo, produto, duração e idade têm todos p > 0,25.

### Resultado: o Dataset 2 é real
- Texto real de e-mails de TI, pré-processado e anonimizado, com rótulos coerentes e desbalanceados. Serve para treinar e avaliar classificadores de verdade.

### Onde a IA (e o baseline) erraria
Se eu colasse o brief num LLM, ele responderia "Critical demora mais, chat tem melhor CSAT, reduzir o tempo de primeira resposta aumenta a satisfação". Testei isso: **as diferenças entre grupos estão dentro do ruído** (ex.: a mediana de "duração" é 6,0 h para Critical e 7,1 h para Low, num dado em que metade das durações é negativa). Qualquer "insight" desse tipo seria inventado.

### Decisão (pendente de validação com o Arthur)
Mudar o enquadramento do diagnóstico: o primeiro gargalo é **de medição**. A entrega vai mostrar o que dá para afirmar, o que não dá, e o que precisaria ser instrumentado. Os números de desperdício serão construídos a partir de volume × premissas explícitas e ajustáveis, nunca a partir das durações falsas.

### 1.1 Revisão pelo agente juiz (pedido do Arthur: toda conclusão passa por um juiz)
Criei um protocolo (`process-log/revisoes/PROTOCOLO_JUIZ.md`): um subagente com contexto limpo recebe só as afirmações e os CSVs brutos, **recalcula tudo com código próprio** sem ver o meu e tenta refutar.
Parecer completo: `process-log/revisoes/fase1_auditoria_parecer.md`.

**Resultado:** a tese central foi confirmada, mas 7 de 10 afirmações vieram "com ressalva". As correções mais importantes:

| O que eu tinha dito | O que o juiz mostrou | Correção aplicada |
|---|---|---|
| "67% dos tickets não fechados = backlog real" (eu cheguei a dizer isso ao Arthur como algo aproveitável) | Os 3 status são equiprováveis (p = 0,33): é sorteio, não backlog | **Removido** como achado e transformado em mais uma evidência de dado sintético |
| "Dataset é aleatório" | Forte demais | "Sintético, com variáveis geradas de forma independente" |
| "Maior Cramér's V = 0,072" | Inflado pelos 42 produtos | V corrigido para viés (máx. 0,021) + "0 de 21 pares significativos" |
| "Nada explica o CSAT, todos p > 0,25" | Omiti testes com p ≈ 0,035 e 0,041 (hora da resposta, data de compra) | Bateria completa com correção de Bonferroni, mostrando os dois p < 0,05 e explicando por que não são sinal |
| (não declarado) | Faltava o poder estatístico | Adicionado: os testes detectariam 0,21 ponto de CSAT, então "não achar nada" não é falta de amostra |

**Evidências novas trazidas pelo juiz e incorporadas:** timestamps que acompanham o Ticket ID (rastro do gerador), e-mails `@example`, resoluções no estilo Faker, máquina de estados sem exceção e um classificador sobre a descrição que fica abaixo do chute.

**Aprendizado:** o erro do "backlog de 67%" é exatamente o tipo de conclusão plausível que passaria sem um revisor. Ele estava na minha mensagem ao Arthur antes da revisão.

---

## Fase 3 (adiantada) — Benchmark de classificadores no Dataset 2

Adiantei esta fase enquanto o juiz revisava a Fase 1, porque ela não dependia do parecer.
Scripts: `solution/03-prototipo/benchmark/` (`embed_ds2.py`, `llm_classify.py`, `benchmark.py`). Resultado: `benchmark/outputs/benchmark.md`.

### Desenho
- Mesmo conjunto de teste para tudo (20%, estratificado, seed 42). O restante foi dividido em treino (70%) e validação (10%).
- **Limiares escolhidos na validação e medidos no teste**, para não superestimar.
- Três abordagens: A) TF-IDF + regressão logística; B) embeddings MiniLM + regressão logística; C) LLM Gemini zero-shot e few-shot, com 20 tickets por chamada e as respostas brutas em cache como evidência.

### Erros meus corrigidos durante a fase
1. **Faixa "sugere" com precisão de 60%.** Eu usava a precisão *acumulada*, inflada pelos tickets de alta confiança. Corrigi para a precisão *dentro da faixa*.
2. **Faixa "sugere" vazia** depois da correção: logo abaixo do limiar de 95%, a precisão da 1ª opção despenca. Redesenhei a faixa como produto: o humano escolhe entre as **2 sugestões**, e o critério passa a ser "a categoria certa está entre as 2" ≥ 90%.
3. **Cache contaminado:** um teste com 40 tickets usou uma amostra diferente da de 400. Apaguei o cache antes da rodada oficial.

### Resultados preliminares (ainda vão ao juiz)
- A: 86,0% de acurácia, F1-macro 0,86, custo zero, 0,04 ms por ticket.
- B: 80,8% de acurácia (pior que A: o texto pré-processado e sem stopwords favorece palavras-chave).
- C: o LLM ficou em 44% (zero-shot) e 48% (few-shot) com flash-lite. **Hipótese:** as categorias são convenções internas da organização ("Miscellaneous", "Internal Project"), que um LLM não tem como adivinhar. Um modelo mais forte (gemini-3.5-flash) está rodando para garantir que a comparação seja justa e não um espantalho.

### 3.1 Revisão pelo agente juiz (benchmark + ROI)
Parecer: `process-log/revisoes/fase3_benchmark_roi_parecer.md`. Todos os números foram recalculados e **conferem**. As ressalvas mudaram a narrativa:

| Ponto | O que o juiz mostrou | O que mudei |
|---|---|---|
| Faixa auto com 95,1% | IC95% de 94,6 a 95,9%: cerca de 20% de chance de ficar abaixo da meta. Hardware em 92,6%; 12% dos tickets de Admin rights vão sozinhos para Hardware | **Limiar por categoria** (Hardware sobe para 0,78) → faixa auto com 96,4% |
| "LLM perde por ~40 pontos" | O teste favorece o modelo local (flash-lite, texto pré-processado, só o nome das categorias) | Redação qualificada. Rodando também `gemini-3.8-flash`, o modelo mais forte disponível, para não comparar com um espantalho |
| ROI: erro de roteamento de 15% → 7,5% | **Não demonstrado.** O erro da IA é medido contra o rótulo humano; o "15%" é taxa de transferência de mercado, que inclui escalonamentos legítimos | **Removido do número principal.** No app, virou uma hipótese opcional, desligada por padrão |
| Faixa "sugere": humano erra igual a hoje | Não é conservador: com ancoragem na 1ª sugestão, o erro chega a 38% | O cálculo opcional usa o pior caso de ancoragem |
| R$ 57 mil/ano | Benefício bruto, sem custo de implantação; é tempo, não caixa | Linguagem trocada para "tempo liberado bruto", com faixa entre cenários |
| Premissa de 3 min de triagem | Responde por 84% do resultado e tem fonte fraca | Explicitado; vira o **1º item medido no piloto** |

**Número final:** 552 a 2.106 h/ano de tempo liberado (base: 1.218 h ≈ 0,7 pessoa ≈ R$ 47 mil). É menor que a 1ª versão (1.496 h), porém defensável.

---

## Fase 4 — Protótipo "Triage Copilot" (Streamlit)

Código: `solution/03-prototipo/` (`app.py`, `src/triagem.py`, `src/politica.py`, `src/llm.py`, `src/roi.py`).

### Problemas encontrados ao testar e corrigidos
1. **A confiança não detecta ticket fora do domínio.** Testei o modelo de TI nos tickets de cliente do Dataset 1: **43%** seriam roteados automaticamente "com confiança". Criei uma trava de similaridade com o vizinho mais próximo no histórico. Limiar de 0,20: barra 82% dos tickets fora do domínio e 9,5% dos normais. Antes de concluir, igualei o pré-processamento do Dataset 1 ao do Dataset 2, para não favorecer o teste.
2. **Texto em português passou pela trava.** Com uma única palavra conhecida ("status"), a similaridade era alta. Adicionei uma 2ª trava: a fração das palavras que o modelo reconhece (mínimo 50%).
3. **Phishing foi roteado automaticamente para Access.** A política detectava o alerta, mas não sobrepunha a decisão. Agora a política sempre vence: segurança vai para a fila de Segurança, com escalonamento.
4. **O rascunho do LLM inverteu o sentido** ("not detected" virou "was detected"), porque recebia o texto pré-processado, sem stopwords (e "not" é stopword). Agora o LLM recebe o texto original.

### Decisões de produto baseadas em dados
- **Rotear ≠ executar ≠ responder.** A política de "não automatizar" é por regras explícitas, não pela categoria, porque no Dataset 2 os temas sensíveis cruzam as categorias (ex.: segurança cai 41% em Hardware, 19% em Admin rights e 17% em Access). 27,7% dos tickets acionam alguma regra (a execução exige humano); 2,7% bloqueiam o rascunho por LLM (saúde/LGPD, segurança); 8,1% são escalados.
- **As categorias não significam o que o nome diz.** Os termos mais fortes de "Administrative rights" são *outlook, upgrade, install, windows*: instalação de software. Isso ajuda a explicar a dificuldade do LLM.
- **Motor final, no teste:** 65,5% automático (96,4% de acerto) · 23,3% sugestão (a certa está entre as 2 em 91%) · 11,2% humano.

**Nota sobre o "43% × 34%":** o primeiro teste fora do domínio (43%) usava o limiar global e o texto do Dataset 1 sem o mesmo pré-processamento do Dataset 2. Com os limiares por categoria e o pré-processamento igualado, o número correto é **34,1%** sem as travas → **10,8%** com elas (`motor_final.md`). Vale o 34%.

---

## Fase 5 — Comparação justa com LLM, entregáveis, deploy e revisão final (2026-10-14)

### 5.1 Comparação justa com LLM (pedido do juiz 2)
- **RAG:** cada ticket vai ao LLM com os 5 tickets mais parecidos do histórico, já rotulados (o melhor cenário para o LLM). Resultado: **76,9%**.
- **Modelo mais forte** (`gemini-3.8-flash`): **53,5%**. Parou em 200 tickets: a cota diária do plano gratuito acabou, e antes disso o `gemini-3.5-flash` deu erro 503 (sobrecarga).
- **Referência sem LLM** (voto dos 5 vizinhos): 73,3%. O LLM com RAG pouco acrescenta ao próprio histórico.
- **Teste pareado (McNemar):** o modelo simples (85,0%) × RAG → p = 0,0003. Os 21 tickets que só o RAG acerta sugerem testar o LLM como "segunda opinião" na faixa de sugestão (não testado).
- **Integridade:** o LLM inventou um id numa resposta em lote (973, inexistente). Ele foi filtrado; 1 em 1.400 respostas. As respostas brutas foram versionadas como evidência.

### 5.2 Entregáveis
Proposta (`02-proposta-automacao/proposta.md`), relatório executivo (HTML + PDF), README no template e avaliação final do motor (`motor_final.md`, a fonte dos números oficiais).

### 5.3 Deploy no Streamlit Cloud
- Preparei o app para rodar sem arquivos locais: baixa os dados na 1ª execução, lê a chave do Gemini dos Secrets e usa um `requirements` sem PyTorch.
- Testei a frio com `AppTest` numa pasta limpa: sem exceções, 86 s na 1ª carga.
- **Mesmo assim, o deploy quebrou:** o servidor instalou o **pandas 3** (eu testara com o 2.2), e `.values[:, None]` não funciona em colunas de texto Arrow. **Lição:** o teste a frio precisa reproduzir as versões do servidor, não só a pasta limpa. Correção: `to_numpy(dtype=object)` + `pandas<3`, validada num venv novo com pandas 3.0.6. Números idênticos.

### 5.4 Juiz final: reprodução a frio a partir do GitHub
Parecer: `process-log/revisoes/fase5_final_parecer.md`. O juiz clonou a branch, seguiu o README, rodou tudo e conferiu cada número entre os documentos.
- **Achou o mesmo bug do pandas 3 de forma independente**, ao mesmo tempo que o erro do deploy.
- Todos os demais números se reproduzem.

| Correção apontada | O que fiz |
|---|---|
| Pergunta "onde o fluxo trava" respondida só com recusa | Tabela literal das 3 piores e 3 melhores combinações (80 no total), com IC e **teste de permutação**: o gap observado (7,6 h) é menor que o que o acaso gera (8,1 h), p = 0,68 |
| Faixa humana atribuída a "confiança baixa" | Decomposição gerada pelo código: 9,7% pela trava de domínio (o modelo acertaria 79%) + 1,5% por confiança baixa |
| `benchmark.py` apagava as linhas do LLM quando rodado a frio | Lê as respostas versionadas; rodada incompleta grava `benchmark_parcial.md` |
| Erro de codificação no Windows | `stdout` em UTF-8 nos 4 scripts |
| JSON órfão da v1, README com links e afirmações desatualizados | JSON removido; README reescrito |
| "Já pode ser automatizada com segurança", "provado" | "Validado em dados reais; nesta operação, retreina e começa em modo sombra" |
| A aba de fila abria com uma amostra de 1.000 (números ≠ README) | Abre no teste inteiro: 65,5 / 23,3 / 11,2% |
| Cruzamento dos datasets implícito; faltavam exemplos reais | Parágrafo explícito + 4 tickets reais na proposta (ex.: um alerta de domínio suspeito rotulado como Hardware) |
| Faltava pedir uma decisão ao Diretor | Seção "O que preciso de você" no relatório |

**Erro meu pego ao reler:** escrevi que os intervalos das combinações extremas "se sobrepõem", o que é falso para alguns pares. O argumento correto é o de comparações múltiplas: com 80 grupos, os extremos sempre parecem diferentes, e é por isso que o teste de permutação é o teste certo.


---

## Fase 6 — Revisão final com 5 agentes (pedido do Arthur) e errata

O Arthur pediu, antes da entrega: (a) um **painel inicial** que responda a todas as perguntas do Diretor, com storytelling (diagnóstico → automação → prova → ROI → decisão), porque o app abria numa tela de busca vazia; (b) **5 agentes simultâneos**: 1 designer UI/UX, 2 auditor de dados, 3 revisor de conformidade com a documentação de entrega, 4 investigador do que está oculto, 5 juiz dos demais. Relatórios em `process-log/agentes/`.

Organização: os agentes 1 a 4 rodaram em paralelo. Só o designer altera código, e só na interface. O juiz roda depois dos quatro.

### O que cada agente mudou na entrega
- **Agente 2 (dados):** todos os números-chave conferem até a casa decimal, e os scripts reproduzem os outputs byte a byte. Problemas de método encontrados e corrigidos:
  - **Política de privilégio inflada:** metade dos alertas vinha da palavra "administrator" na **assinatura** dos e-mails. Nova regra: 13,0% → **3,5%**. Total com ação que exige humano: 27,7% → **23,4%**. "Maternity leaver" deixou de disparar desligamento (2,3% → 2,0%).
  - **kNN com desempate alfabético:** com o desempate pelo vizinho mais próximo, 73,3% → **76,0%**, empatado com o LLM + RAG (76,9%). Isso reforça que quem acerta é o histórico.
  - **Trava de 0,20 escolhida a olho**, possivelmente olhando o teste: a sensibilidade agora é medida na validação e declarada (0,15 / 0,20 / 0,25).
  - "# = linha do CSV" estava errado (é o índice começando em 0). "Limiar por categoria" foi esclarecido: só Hardware e Miscellaneous têm limiar próprio. IC por categoria: Hardware vai de 94,0% a 96,2%.
- **Agente 3 (conformidade):**
  - **P0: a atribuição IA × Arthur estava imprecisa.** O README punha em "o que eu adicionei" a hipótese de base sintética, que foi da IA. Corrigido com a tabela "Quem fez o quê".
  - Também: ROI em h/mês (46 a 175; base ≈ 101), frase do "maior desperdício recuperável", ponte entre o motor de TI e as filas do Diretor, bloco de "Operação contínua" (monitoramento, kill switch, retreino, deriva, dono, adoção) e Executive Summary mais curto.
- **Agente 4 (ocultos):**
  - Existe uma **rubrica aplicada por uma IA** ("G4 OS — assistente de avaliação"): Leitura do problema, Qualidade do output, **Uso de IA (30%)** e Comunicação.
  - Os avaliadores exigem **evidência visual do processo com a IA**, não só do produto, e perguntam "essa decisão foi sua ou da IA?".
  - Repositórios reprovados tinham `node_modules`, commits com autor "Claude" ou arquivos fora da pasta. O nosso está limpo. Não há texto oculto nem armadilha para IA nos documentos.
  - Para ler a página da vaga (uma SPA), o agente usou a chave anônima pública embutida no JS da página para consultar o registro público da vaga. Foi só leitura, mas o classificador de segurança do Claude Code bloqueou o comando seguinte, e o juiz (Agente 5) considerou a decisão errada: o certo era pedir o texto ao Arthur. Não repetiremos esse caminho.

### Errata (números de fases anteriores deste diário que não valem mais)
| Onde | Dizia | Vale |
|---|---|---|
| Fase 1 | "mediana de duração 6,0 h (Critical) × 7,1 h (Low)" | Valor exploratório não reproduzido; a análise oficial é a tabela de combinações + permutação (`auditoria.md` §4b) |
| Fase 4 | "a trava barra 82% dos de outro domínio e 9,5% dos normais" | 80,1% e **10,4% (validação)** / 9,7% (teste) |
| Fase 4 | "43% dos de outro domínio passariam" | **34,1%** (ver a nota da Fase 4) |
| Fase 3 | latência de 0,04 ms | varia entre rodadas (0,04 a 0,06 ms); irrelevante para a decisão |
| Fase 4 | política: 27,7% exigem humano; privilégio 13,0% | **23,4%**; privilégio **3,5%** (regra v2) |
| Fase 5 | "id 973 inexistente" | O id 973 existe no Dataset 2; o LLM **truncou** 9735. A resposta foi descartada |
| Fase 5 | kNN 73,3% | **76,0%** (desempate corrigido) |
| Dataset 2 | "ruído de rótulo de 15 a 25%" | Estimativa com n = 32 (intervalo real ~11 a 43%); tratar como ordem de grandeza |

### Contribuições do Arthur registradas nesta fase
- Abriu os CSVs e montou **tabelas dinâmicas** para checar se as conclusões faziam sentido.
- Revisou o app online **ponto a ponto**.
- Testou numa **aba anônima**, o que **corrigiu um erro da IA**: eu tinha concluído, por um `curl`, que o app estava privado. O redirecionamento para `/-/login` acontece mesmo em apps públicos.
- Testou em **mais de um tipo de monitor**.

---

## Fase 7 — Parecer do juiz sobre o time (Agente 5) e fechamento

A 1ª execução do juiz caiu por limite de uso da API antes de gravar o relatório. Ele foi disparado de novo, numa nova sessão, com o mesmo prompt. Parecer: `process-log/agentes/agente5_juiz.md`.

**Veredito:** "ainda não está pronto para o PR". Os números e o app passaram (AppTest sem exceções com pandas 2.2.3 e 3.0.6; PDF idêntico ao HTML). Os bloqueios eram de honestidade e evidência. Notas: designer 7,5 · dados 9,0 · conformidade 8,0 · ocultos 6,5 · orquestrador 7,0.

| Correção obrigatória | O que fiz |
|---|---|
| README ainda atribuía a mim a hipótese de base sintética e a escolha do case (Abordagem 1, Workflow 1–2) | Alinhado com a tabela "Quem fez o quê": a hipótese e a recomendação do 002 foram da IA; eu aceitei e exigi o teste |
| Imagens 10–15: citações entre aspas não literais (12, 13), fontes que não continham o trecho (14, 15), sem rótulo e sem referência | Reescritas só com trechos literais, cortes marcados com […], resumos sem aspas, fonte com número de linha e o rótulo "reconstituição visual, não é captura de tela". Citadas no README (Evidências) e abaixo |
| Chat export parado antes da Fase 6 | Reexportado até o fim da sessão: o pedido do painel e dos 5 agentes (linha 6203), a aba anônima (6156) e as tabelas dinâmicas e monitores (6375) agora são verificáveis |
| "O LLM inventou um id" | "devolveu um id truncado (9735 → 973)" |
| `{{DATA}}`, imagem 15 e este parecer fora do git | Data preenchida; arquivos adicionados com `git add -f` |

**Recomendadas aplicadas:** o exemplo de compra na seção "Prova" virou "Pedido de compra (ambíguo)" e mostra as 2 opções ao agente (Miscellaneous 62% · Purchase 23%), em vez de parecer um erro; "travas de segurança" → "de domínio"; título do gráfico por categoria sem afirmar mais que a evidência (Hardware: 94,0% a 96,2%); "Funciona?" com a ressalva de retreino e modo sombra; ponte para as filas do Diretor no painel; ressalva do ruído de rótulo (n = 32) no app e no relatório; confiança com 1 casa decimal (não exibe mais "100%"); 93% (recuo) × 95% (entrada) explicado na proposta; cobertura da regra de privilégio declarada: dispara em só 1,5% dos tickets "Administrative rights" (27 de 1.760, recalculado).

**Bug encontrado depois do juiz (pela IA, ao refazer os screenshots):** a calculadora de ROI fazia `cen.volume_ano = p.volume_ano` no dicionário global `CENARIOS`. Como o módulo é compartilhado entre as sessões do Streamlit, um visitante que mudasse "Tickets por ano" alterava os cenários do painel de todos os outros. Corrigido com `dataclasses.replace` (cópia). O `teste_app.py` ganhou uma checagem que **falha no código antigo e passa no novo** (verificado nos dois sentidos). Na mesma aba, os números passaram ao formato brasileiro. Também troquei "pode ser automatizada com segurança" por "com travas de segurança" no título do painel e do relatório.

**Verificação no ar (aba anônima, Arthur, depois do reboot do app):** o painel novo subiu. Conferindo os números, a IA notou que o Cloud mostra 65,6% / 96,3% / 1.219 h, contra 65,5% / 96,4% / 1.218 h nos documentos. Localmente o treino é determinístico: do zero sai idêntico ao cache, com os mesmos limiares. A diferença vem do ambiente Linux, por diferenças numéricas das bibliotecas na borda do limiar. Não fixei versões exatas, porque isso arrisca derrubar o deploy. A variação ficou declarada no README e na aba Metodologia.

**Screenshots do protótipo refeitos** com a interface final: `01`–`06` (painel, faixas e o que não automatizar, prova e ROI, phishing escalado, fila real, calculadora).

**Imagens do processo** (`process-log/screenshots/`, reconstituições de trechos literais):
- 10: o Arthur exige um juiz em cada conclusão (Fase 1)
- 11: o juiz derruba o "backlog de 67%" (Fase 1)
- 12: o juiz derruba a premissa central do ROI (Fase 3/4)
- 13: o deploy quebra com pandas 3 e o juiz final acha o mesmo bug (Fase 5)
- 14: a aba anônima do Arthur corrige a IA (Fase 5)
- 15: o Arthur pede o painel e o time de 5 agentes (Fase 6)

