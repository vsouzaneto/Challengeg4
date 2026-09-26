# Skills e ferramentas por etapa

Uma skill é um conjunto de instruções que o Claude Code carrega quando a tarefa pede: um método pronto para um tipo de trabalho. Os horários vêm dos transcripts (Brasília, 25/09/2026; "S0" é a sessão de pesquisa e "S1" a de execução).

## Origem das skills

| Skill | De onde vem |
|---|---|
| social, influencer-marketing, ab-testing, analytics, content-strategy | Plugin marketing-skills 2.10.0 ([coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills), licença MIT) |
| brainstorming, writing-plans, executing-plans, test-driven-development | Plugin superpowers 6.4.1 ([obra/superpowers](https://github.com/obra/superpowers), licença MIT) |
| dataviz | Vem com o Claude Code |
| save-session | Minha, instalada na minha máquina, junto com o vault do Obsidian |
| graphify | De terceiros ([safishamsi/graphify](https://github.com/safishamsi/graphify)), instalada por mim no mesmo setup |

## Por etapa

| Etapa | Skill ou ferramenta | Para que serviu |
|---|---|---|
| **Pesquisa** (S0, 13:28 a 14:32) | GitHub CLI e dois subagentes | Ler os PRs e as reviews públicas do avaliador e montar o critério de qualidade |
| | Modelo Claude Fable 5.1 (S0 13:56 em diante) | Revisar o primeiro plano, que era do Opus (achou 9 falhas), e conduzir o resto da pesquisa: o plano refeito, que foi o executado, e o CLAUDE.md do projeto |
| | social, influencer-marketing, ab-testing, analytics, content-strategy (S0 13:58) | Refazer o plano com frameworks de marketing: métricas por objetivo, faixas de creator, divulgação, hipóteses, rastreamento |
| | save-session (S0 14:27) | Gravar o resumo da pesquisa em `notes/Sessoes/`, na pasta do projeto, e na memória do Claude |
| **Fase 0, ambiente** (S1 14:43) | Consulta ao grafo, ao vault e às notas | Antes de ler código, o Claude procura o grafo do projeto, a pasta dele no vault e as notas de sessão. Não havia grafo nem pasta no vault; havia o resumo da pesquisa, lido às 14:44 |
| | executing-plans (S1 14:44) | Executar o plano fase a fase, parando nas decisões marcadas como minhas |
| **Fase 2, laudo** (S1 15:12 e 15:23) | test-driven-development | Cada teste automático escrito e visto falhando antes do código |
| | dataviz | Regras dos gráficos do notebook: forma, cor e rótulos |
| **Fase 3, análise** | test-driven-development e dataviz, já carregadas | Funções novas com teste antes; gráfico do mapa de células |
| **Fase 4, estratégia** (S1 16:00 a 16:19) | influencer-marketing | Política de patrocínio: fit, divulgação, parceria recorrente, direito de uso, faixas de preço como premissa |
| | ab-testing | Hipóteses no formato "Porque... acreditamos...", nota ICE, efeito mínimo, amostra, guardrails, playbook |
| | analytics | Plano de rastreamento com 9 eventos |
| **Fase 5, Radar** (S1 16:33 a 20:54) | brainstorming (16:33) | Desenho em quatro partes, cada uma aprovada por mim antes da seguinte |
| | writing-plans (17:14) | Plano de 10 tarefas, cada uma com os testes antes do código |
| | executing-plans e test-driven-development | Execução tarefa a tarefa, com registro das decisões fora do plano |
| | Navegador do app e um subagente no modelo Opus | Conferir as telas; revisão final independente |
| **Fase 1, baseline** (S1 21:18) | Claude Code em modo seguro | O enunciado cru sem nenhum contexto meu (sem CLAUDE.md, memória, skills ou plugins) |
| **Fase 6, fechamento** | Meu CV e o grafo dele (S1 21:05) | Achar o LinkedIn (na página do CV) e o portfólio (no grafo do CV) para o README |
| | Chrome sem janela, controlado por script | Prints das telas do Radar |

## Obsidian: o vault como memória entre sessões

Uso um vault do Obsidian como "segundo cérebro" de desenvolvimento: uma pasta por projeto, com notas de sessão, pendências e conhecimento operacional, sincronizada com o celular. Duas peças fazem o Claude usá-lo:

- **Uma regra minha:** no início de cada sessão, o Claude consulta primeiro o grafo do projeto, a pasta dele no vault e as notas de sessão, e só depois lê código.
- **A skill save-session**, que eu rodo no fim de uma sessão: ela grava um resumo estruturado em `notes/Sessoes/`, na pasta do projeto, e na memória do Claude.

Neste projeto, foi assim que a pesquisa passou para a execução: a sessão de pesquisa foi salva às 14:27, e a de execução começou às 14:44 lendo esse resumo, com o plano e as decisões já tomadas, sem depender de copiar a conversa. A pasta do projeto ainda não estava ligada ao vault, então o resumo ficou só no computador; a própria skill avisou disso (transcript da sessão 0, 14:28).

## Por que usar os grafos

A skill graphify transforma uma pasta de arquivos (código, documentos, notas) num grafo de conhecimento que o Claude consegue consultar: arquivos e conceitos viram nós, e as ligações entre eles viram arestas. O que a documentação da skill descreve:

- o grafo fica salvo na pasta do projeto e vale de uma sessão para outra;
- cada ligação é marcada como extraída do arquivo, inferida ou ambígua;
- a detecção de comunidades junta arquivos e ideias relacionados em documentos diferentes;
- o resultado sai em três formatos: página interativa, JSON e um relatório em texto, além do vault do Obsidian.

Por que eu uso:

- **Memória que não depende da conversa.** A sessão seguinte consulta o grafo em vez de reler todos os arquivos ou confiar no que ficou na conversa.
- **Dá para conferir.** Como cada ligação diz de onde veio, uma resposta tirada do grafo pode ser checada no arquivo.
- **O mesmo mapa para mim e para a IA.** Eu navego no grafo pelo Obsidian, no computador ou no celular, e o Claude consulta o mesmo grafo.

**Neste projeto, o grafo não foi gerado.** Quando a pesquisa foi salva, a pasta ainda não tinha código, e a save-session registrou "Grafo: pulado (sem graphify-out/)" (transcript da sessão 0, 14:28). A passagem de contexto ficou por conta do resumo de sessão. O grafo que entrou no trabalho foi o do meu CV: o link do portfólio saiu dele.
