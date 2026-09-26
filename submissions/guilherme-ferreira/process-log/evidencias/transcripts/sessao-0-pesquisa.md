# Sessão 0: pesquisa e plano (25/09/2026)

Exportado da sessão do Claude Code. Aparecem as mensagens enviadas ao Claude, as respostas às perguntas de decisão, as mensagens do Claude e uma linha por ferramenta usada. Os resultados das ferramentas, e o raciocínio interno do modelo onde o Claude Code o gravou, ficam só no JSONL compactado ao lado. Nos dois formatos, as imagens viram uma nota, e saem o e-mail, os caminhos da pasta pessoal, a configuração pessoal do Claude, o ID da organização, a cópia do prompt de sistema, emojis e os nomes de outros projetos do candidato, quando aparecem.

### Candidato (25/09 13:29)

Cria uma pasta no projetos escrito Teste G4 e analisa esse teste: https://github.com/gestao-Quatro-Ponto-Zero/ai-master-challenge/

**Ferramentas:**
- `Bash`: Create folder and clone challenge repo
- `Bash`: Read all challenge documents
- `Read`: ~/.claude/projects/-HOME/f782c26b-5264-4a68-bd84-5d0d8febda31/tool-results/b06byd2ww.txt
- `Bash`: Check commit history and PR counts per challenge
- `Write`: ~/PROJETOS/Teste G4/ANALISE.md

### Claude (25/09 13:30)

Criei a pasta `~/PROJETOS/Teste G4/`, clonei o repositório dentro dela (`ai-master-challenge/`) e salvei a análise completa em `~/PROJETOS/Teste G4/ANALISE.md`.

#### O que é o teste

É o processo seletivo do G4 Educação para a vaga de **"AI Master"**, alguém que entra numa área e resolve problemas reais usando IA. Você escolhe 1 entre 4 desafios, com tempo sugerido de 4 a 6 horas. A entrega é **só por Pull Request**, e saber usar git já faz parte do teste.

**O que decide se você passa** (README.md e submission-guide.md do repositório):
1. **Registro do processo (process log) obrigatório.** Sem evidência de como você usou IA, a candidatura é desclassificada. Eles querem ver onde a IA errou, como você corrigiu, quantas iterações fez e o que você acrescentou.
2. **Comparação com o baseline.** Eles já rodaram cada enunciado no Claude, GPT e Gemini. Se sua resposta parecer "colei o enunciado na IA", você é reprovado.
3. **Regras do PR.** Só pode alterar arquivos dentro de `submissions/seu-nome/`, e o título tem que seguir o formato `[Submission] Nome — Challenge XXX`.
4. **Texto curto e acionável.** Eles citam como ponto fraco um documento de 40 páginas onde 5 bastariam.

#### Os 4 desafios e a concorrência

A contagem de PRs é de hoje, via `gh pr list`: são 159 no total, e 17 não indicam o desafio no título.

| # | Desafio | Entrega principal | PRs |
|---|---------|-------------------|-----|
| 001 | Churn (SaaS, 5 tabelas) | Relatório com a causa raiz, as contas em risco e as ações | 33 |
| 002 | Suporte (30K + 48K tickets) | Diagnóstico, o que automatizar e o que não, e um protótipo | 33 |
| 003 | Lead Scorer (CRM, 8.800 deals) | **Software funcionando** que explique o score de cada deal | 65 |
| 004 | Social Media (52K posts) | Análise, estratégia e uma ferramenta de acompanhamento | 11 |

#### Minha leitura

- Cada enunciado tem uma armadilha embutida. No 001 é "a satisfação está ok e o uso cresceu", mas a média esconde os segmentos com problema. No 002 é "automatizar 100% é red flag". No 004 é comparar orgânico com patrocinado sem controlar por plataforma e tamanho do creator.
- **O 003 é o mais disputado** (cerca de 40% dos PRs). O **004 é o menos disputado** (11 PRs).
- **Uma forma de se destacar:** os datasets vêm do Kaggle e vários parecem sintéticos. Ao baixar os dados, vale checar se as variáveis têm sinal real antes de concluir qualquer coisa. Dizer isso com evidência mostra o julgamento que eles pedem e que o baseline não entrega. **Não verifiquei nenhum desses pontos.** Os problemas específicos que listei no arquivo vêm de relatos ou da minha memória. Exemplos: placeholders nas descrições de tickets do 002 e nomes de produto que não batem entre tabelas no 003.
- Com o Claude Code, o registro do processo sai quase sem esforço: commits pequenos no git, export das sessões e um `process-log.md` narrando as decisões.

**Minha recomendação:** o 004 ou o 001 se você quer menos concorrência. O 003 se seu forte é construir software, mas aí o scoring precisa ir além do óbvio.

Qual desafio você quer fazer? Posso seguir com o fork e o perfil dos dados. Esse projeto ainda não tem `graphify-out/`, mas acho que só vale rodar o `/graphify` depois que houver código ou dados.

### Candidato (25/09 13:31)

analisa os PR dos outros canditados

**Ferramentas:**
- `Bash`: Fetch metadata for all PRs
- `Bash`: Fetch PR metadata without bodies

### Claude (25/09 13:32)

Use REST instead.

**Ferramentas:**
- `Bash`: Fetch all PRs via REST API
- `Bash`: Check maintainer comments and closed PRs
- `Bash`: Download all comments and PR reviews
- `Bash`: Tabulate evaluator verdicts and scores per PR
- `Bash`: Export evaluator review bodies and preview
- `Bash`: Fetch all PR branches and list scored PRs
- `Agent`: Synthesize evaluator review criteria
- `Agent`: Inspect top and rejected submissions

### Claude (25/09 13:37)

Enquanto isso, calculo a taxa de aprovação por desafio.

**Ferramentas:**
- `Bash`: Compute approval rate per challenge

### Claude (25/09 13:37)

Os dois agentes ainda estão rodando. Aguardo os resultados para consolidar.

### Relatório de subagente (25/09 13:39)

<details><summary>Ver o relatório</summary>

Li o arquivo inteiro: `~/PROJETOS/Teste G4/prs/reviews_evaluator.md`, com 2841 linhas e PRs de #2 a #107. As contagens abaixo são manuais e aproximadas, com o PR como unidade.

#### 1. Rubrica implícita
- **Process log vale 30%.** Está explícito no PR 6 ("Isso vale 30% da avaliação") e no PR 7 ("Sem isso, não conseguimos avaliar 30% dos critérios").
- **Quatro dimensões nomeadas** aparecem no PR 13: "Leitura do problema", "Qualidade do output", "Uso de IA", "Comunicação". O PR 33 repete "Qualidade do output" e "Aprofundamento analítico". O PR 43 fala em "todos os eixos": descoberta estatística, evolução metodológica no uso de IA, rastreabilidade do processo e qualidade do protótipo.
- **Faixas de nota com rótulo:**
  - **Excepcional:** 9.0 a 9.3.
  - **Forte:** 7.0 a 8.7.
  - **Ressalvas:** 5.3 a 6.4.
  - **Reprova:** 2.5 (#79). O #82 recebeu "Reprova" com 6.4 por falta de higiene do repo.
  - Em julho as notas deram lugar a rótulos ("⭐ Excepcional", "✅ Forte").
- **Formato fixo:** "O que funcionou bem / Pontos de melhoria (não bloqueadores)" nas aprovações, e "O que precisa ser corrigido / O que foi bem" nos pedidos de mudança.
- **Hierarquia de evidências:** o PR 18 diz que "a rubrica do challenge lista screenshots como primeira forma de evidência". O PR 24 cita "screenshots e chat exports como formas preferidas".

#### 2. Motivos de bloqueio (cerca de 60 PRs com CHANGES_REQUESTED ou rejeição)
1. **Process log ausente, insuficiente ou não auditável: cerca de 47 PRs.** É de longe o motivo mais comum. Os subtipos são:
   - Sem screenshots do processo: 18, 25, 27, 30, 39, 40, 56, 59, 97.
   - Só links externos: 7 ("Links podem expirar, não são auditáveis offline"), 34, 48.
   - Formato binário (.docx/.pdf): 24, 28, 58, 98.
   - Log só narrativo, sem exports: 57, 58, 60, 65, 93, 103.
   - Log inexistente: 2, 45, 74, 79, 92. Para o PR 45 ele escreveu "critério eliminatório".
2. **Delegação sem julgamento próprio: 12, 13, 15, 20, 17.** No PR 12: "o julgamento analítico presente na entrega veio da ferramenta, não do candidato".
3. **Bugs ou calibração do scoring (003): 12 PRs** (6, 7, 9, 22, 25, 33, 44, 47, 60, 65, 74, 80). Incluem fator que não diferencia os deals, data de referência errada e pesos sem justificativa.
4. **Higiene do repositório: 12 PRs.**
   - node_modules commitado: 7, 48 (32.994 arquivos), 82, 96 (6.176 arquivos).
   - Chave de API ou caminho local no código: 22, 54.
   - Arquivos fora da pasta da submissão: 46, 55.
   - Pasta com nome errado: 11, 102 ("submission/" em vez de "submissions/").
   - models/ e data/ commitados: 78.
   - Problema de engenharia no repo não especificado: 41.
5. **Código ou artefatos fora do repo (Lovable, zip, só PDF): 12 PRs** (5, 15, 19, 21, 26, 28, 50, 54, 55, 70, 79, 92).
6. **Afirmações sem código, ou documentação que diverge do código: 9 PRs** (4, 5, 7, 15, 24, 36, 62, 74, 78). No PR 5: "claim sem evidência computacional". No PR 7 o README diz pesos 35/30 e o código usa 40/25.
7. **Não reproduzível ou não utilizável: 9 PRs** (4, 6, 21, 32, 47, 51, 70, 73, 78). Exemplos: notebook com `!wget` de uma URL inexistente, entrega que só roda no terminal, gestor que dependeria de Python.
8. **Leakage, overfitting ou AUC mal explicado: 5 PRs.**
   - PR 2: AUC=1.0.
   - PR 62 e PR 78: AUC 0.9975, com leakage vindo de `upgrade_flag`/`downgrade_flag`, que só existem em `churn_events`.
   - PR 66: AUC em torno de 0.5 sem contextualizar.
   - PR 46: modelo que não diferencia as contas.
9. **Não usou os dados do challenge: 47, 85 (dados sintéticos gerados pelo candidato), 11 (Dataset 2 ignorado).**
10. **Commits:** autoria "Claude" (PR 2), e um único commit com 229 arquivos (57, 103).

#### 3. O que as aprovações com nota mais alta tiveram de concreto
- **#83 (9.3):** Codex + crítica do Sonnet + crítica do Opus usados como "validação adversarial". Humildade causal ("candidata observacional, não causal"). `critique-synthesis.md`. Exports que qualquer pessoa consegue reproduzir. 4 commits com narrativa coerente.
- **#69 (9.1):** método "baseline-then-exceed", com 3 baselines documentados (`prompt-used.md` + `raw-output.md`). `differentiation-rubric.md` escrita antes do código. LLM-as-judge com cache, para o avaliador não precisar de chave de API. 8 bugs com causa raiz. `ref_date = max(close_date)`. 27% de deals órfãos identificados.
- **#76 (9.0):** integrou os 4 challenges num relatório único e quantificou anomalias (95% dos deals abertos sem close_date). Recusou "AI everywhere".
- **#81 (9.0):** guardrails em 3 níveis (AUTO_RESOLVE / AGENT_ASSIST / HUMAN_ESCALATION) com thresholds tirados dos dados (85% / 60%). Diagnosticou 49.3% de timestamps invertidos. Model card e `automation_policy.md` dizendo o que não automatizar.
- **#84 (8.7):** app público no ar, 6 fatores com peso justificado, camada de confiança separada do score, Monday Brief, `SETUP_SCORING_LIMITATIONS.md` e QA report.
- **#68 (8.2):** achou target leakage no CSAT (r=-0.019). Reframe "deflection-first" com RAG. Cada ferramenta com papel definido. 52 screenshots e 3.371 linhas de chat. MVP deployado.
- **#71 (8.2):** r=-0.001 entre ciclo e satisfação redirecionou a proposta. Baseline TF-IDF+LR sem LLM. Domain gap de -36,5 pp quantificado. 6 decisões humanas com evidência.

Pontos que se repetem nesses PRs: decisão de produto antes do código, honestidade sobre as limitações, erros da IA documentados com causa raiz, e o que não automatizar.

#### 4. O que ele confere em cada challenge
- **001 Churn:**
  - Leakage vindo da tabela de target e validação por cohort ou data, não por split aleatório (78).
  - AUC fraco é aceito quando declarado: 73 (0.61) e 90 (0.50) foram aprovados.
  - Paradoxo de satisfação igual entre quem cancela e quem fica (90, 39). Fontes de churn contraditórias (46, 90).
  - Notebook com outputs renderizados (73, 78). Priorização por MRR em risco (54, 90).
- **002 Suporte:**
  - Timestamps negativos: mínimo de -23h e média negativa no PR 5; "49,3%" nos PRs 71, 81, 100; "metade negativa, tudo comprimido em 27h" no PR 101; falta timestamp de abertura no PR 104. O PR 5 foi aprovado usando `abs()` com justificativa.
  - CSAT aleatório, r de -0,001 (5, 27, 71).
  - Placeholder `{product_purchased}` nos textos do Dataset 1 (26, 27).
  - Usar os dois datasets (11) e medir o domain shift do classificador treinado no Dataset 2 (5, 71, 107).
  - Não automatizar Refund/Cancel/Critical (5, 27, 71, 99, 105).
  - ROI com premissas explícitas (15, 99, 100, 104). Gate de confiança ou abstenção (81, 97, 104, 105, 107).
- **003 Lead scorer:**
  - Data de referência = max da data do dataset, não now(): 9, 22, 7, 31, 75 (days_open de 3.199 para todos os deals), 60, 82.
  - GTXPro vs GTX Pro (16, 63, 70, 94, 95). Deals sem account (24, 69, 75).
  - Win rate com denominador Won+Lost (60, 82). Fator que não diferencia os deals (22, 65).
  - Estágio Won/Lost que nunca aparece no pipeline aberto, e close_date planejado usado como timing (47).
  - Leakage de close_value (18, 94). Linha dos 138 dias (56, 95). Joins das 4 tabelas (9).
  - Precisa ser usável por vendedor (6). Exemplos de output e sanity checks (13, 16, 21, 18). Testes (23, 25, 75, 94).
- **004 Social:**
  - Dataset sintético: views com std=100 e correlações perto de zero (30).
  - Diferenças de 0,1% apresentadas como insight (17). Testes de significância, IC95% e effect size (17, 91).
  - Filtro n≥80 (4), células com no mínimo 30 posts (72), checagem de alucinação da LLM (72).
  - Bug que descartava 40% dos dados (36).
  - Entrega "que possa ser usada, não só lida" (4). Só um `analysis.md` recebeu 2.5 (79).

#### 5. Reenvios e evolução ao longo do tempo
- **Corrigir costuma levar à aprovação, e rápido.**
  - Mesmo dia ou 1 dia: 5 (3 a 4 de março), 9, 11, 19, 22, 34, 36, 44, 54, 56, 57.
  - Mais demorados: 82 (6 dias), 85 (12 dias), 30 (13 dias).
  - Também vale abrir um PR novo: 59 virou 77 (aprovado com 8.0) e 65 virou 86 (8.1).
- **Quem não atacou a causa foi descartado** após 2 a 4 rodadas: 7, 33, 39, 40, 45, 46, 47, 48, 50/58, 55, 62/78. A frase do PR 78 resume: "Quase estagnou".
- **Linha do tempo:**
  - Primeira review em 03/03. Lote grande em 13/03.
  - Em 14/03 houve correções assinadas "Avaliação por G4 OS — assistente de avaliação". Ele admitiu erros nos PRs 6 e 21 ("Pedimos desculpas pelo erro"), e no PR 22 ("foi um erro meu").
  - Em 18 e 19/03 surgem as notas. Em 20/03 houve um endurecimento: "Revisando sua submissão com o critério atual do processo". Dez aprovações viraram CHANGES_REQUESTED (6, 13, 15, 17, 18, 21, 24, 25, 27, 30), quase sempre por falta de screenshots ou de raciocínio próprio.
  - Entre 23/03 e 02/04, aprovações curtas ("Parabéns..."). Em 13/04, recusas genéricas encerrando PRs ("não atingiu o critério").
  - Hiato de 17/04 a 09/06. Retomada em junho e julho, com lote grande em 22/07.
  - Em 03/08, reaprovações de PRs antigos (17, 18, 21, 24, 25) e aprovações de 97 e 107.
- **Última review: 03/08/2026.**
- **O template "banco de talentos" aparece só no PR 2 (13/03).** Depois as recusas passam a usar "Desejamos sucesso nos próximos desafios" (46, 48, 50, 51) ou "Reprova" (58, 79, 92).

#### 6. O que ele espera sobre uso de IA
- **Autoria dos commits (PR 2):** "Todos os 5 commits da submissão têm author 'Claude'. O challenge espera evidência de trabalho humano guiando a IA — commits com identidade do candidato".
- **Controle humano:**
  - PR 17: ter "Edit automatically" ligado é "sinal negativo", e o prompt "você é um programador senior..." "delega expertise".
  - PR 71: AGENTS.md e CLAUDE.md "reduz[em] transparência sobre o que foi steering".
  - PR 15: log estruturado pelo Copilot é "artefato da ferramenta".
- **Prova de que o processo aconteceu:**
  - PR 39: "se o processo de fato aconteceu como descrito".
  - PR 48: "não lembro de erros expressivos" é "improvável".
  - PR 54: o log parece "template gerado por IA".
  - PR 103: 1 commit com 229 arquivos "levanta dúvidas".
- **O que é valorizado:** exports brutos (JSONL, PDF, transcript) mais screenshots, erros da IA com correção, separação entre decisões humanas e da IA (PR 53: "8 de iniciativa do candidato, 4 por consenso, 0 só da IA"), auditoria com um segundo modelo (53, 57, 75, 77, 83, 90) e análise própria dos dados antes de chamar a IA (20, 25, 13).
- **Commits:** concentrar tudo em um único commit é sempre apontado como fraqueza (27, 68, 69, 76, 77, 84, 86). Bloqueou quando o log também estava fraco (57, 103).

</details>

### Claude (25/09 13:39)

Primeiro relatório recebido. Aguardo o segundo agente, que está inspecionando as submissões.

### Aviso do sistema (25/09 13:39)

Tarefa em segundo plano terminou: Agent "Synthesize evaluator review criteria" finished

### Claude (25/09 13:39)

Ainda falta o agente que inspeciona as submissões.

### Relatório de subagente (25/09 13:40)

<details><summary>Ver o relatório</summary>

Analisei os PRs só em modo leitura (`git show` e `git diff merge-base..pr/N`). Todos os caminhos citados são relativos a `~/PROJETOS/Teste G4/ai-master-challenge`.

#### 1. Os 9 PRs avaliados

**PR 83 (C001, 9.3), kadug**
- **Volume:** 42 arquivos (13 md, 13 json, 13 csv, 2 py). 4 commits, 1 autor.
- **Solução:** pipeline pandas reproduzível em `submissions/kadug/solution/analysis/build_exports.py` (2.068 linhas, com flag `--validate-only`). Gera camada limpa, 16 exports CSV (`priority_accounts.csv`, `action_backlog.csv`, `executive_findings.csv`), `data_quality_report.md` e um dashboard Streamlit local. Não tem deploy.
- **README:** 162 linhas, cerca de 1.500 palavras, segue o template à risca. Traz ranking de causas com MRR em risco, segmentos com playbook e uma seção que desmonta as duas falas do CEO: 19.432 de 25.000 linhas de uso estão fora da janela de assinatura, e a satisfação só parece ok porque só olha quem respondeu.
- **Process log:** narrativa por sessão em `process-log/ai-workflow-log.md` (183 linhas). Inclui críticas de outros modelos (Sonnet e Opus) e decisões aceitas ou rejeitadas. Já em `docs/` ficam o plano de 4h, os checkpoints e a síntese das críticas.
- **Destaque:** a seção "onde a IA errou" é concreta: dupla contagem de MRR e qualidade de dado ranqueada como causa de churn.

**PR 69 (C003, 9.1), anderson-hirota**
- **Volume:** 205 arquivos, dos quais 163 são JSON de cache do LLM-judge. 1 commit.
- **Solução:** Streamlit com 6 módulos, cerca de 4.500 linhas (`app.py` tem 2.399). É um "Morning Brief" com modo Manager e modo Rep, ações Done/Defer/Skip e LLM-as-judge via Claude CLI com cache já gerado, então roda sem chave de API. Não tem deploy.
- **README:** o da raiz é curto (35 linhas) e aponta para `solution/README.md` (289 linhas, template completo).
- **Distintivo, "baseline-then-exceed":** em `process-log/baseline-v1..v3/` estão três versões geradas só pela IA, cada uma com `prompt-used.md`, `raw-output.md` e código. Há também `differentiation-rubric.md`, um contrato escrito antes da fase final. O candidato mede o próprio trabalho contra o que a IA faz sozinha.

**PR 81 (C002, 9.0), sara-andrade**
- **Volume:** 42 arquivos (13 png, 11 md, 4 py, 3 joblib). 1 commit.
- **Solução:** API FastAPI de triagem (`solution/triage.py`, `train_models.py`, `test_batch.py`), com três rotas (AUTO_RESOLVE, AGENT_ASSIST, HUMAN_ESCALATION) e um corte de confiança (≥ 0,80) para automatizar. Não tem deploy.
- **README:** 248 linhas. O ponto forte é a seção "auditar antes de automatizar": uma tabela de testes mostra que o Dataset 1 é sintético (100% dos textos com placeholder `{product_purchased}`, 49,3% de tempos negativos, CSAT uniforme com p=0,797). A candidata também corrige a leitura do número 67,3%.
- **Process log:** `process-log.md`, `prompts-used.md`, `ai-errors-and-corrections.md` e 6 screenshots da API funcionando.
- **Documentos extras:** `docs/roi_model.md` e `docs/automation_policy.md`.

**PR 76 (C003, 9.0), pedro-lima**
- **Volume:** 23 arquivos. 1 commit.
- **Estrutura errada:** a submissão está aninhada em `ai-master-challenge-submission-pedro-lima/submissions/pedro-lima/`, com cópia do repo inteiro, e mesmo assim recebeu 9.0.
- **Solução:** `scoring_engine.py` com 5 sinais e suavização bayesiana, mais um `index.html` single-file com login, kanban drag and drop e plano de ação. Não tem deploy.
- **README:** 213 linhas, cerca de 1.900 palavras. Mostra um backtest (top 10% fecha 82% contra 39% do bottom 10%) e a evolução v1 a v5 com precisão por versão.
- **Process log:** `process-log/workflow-narrative.md`, mais 3 docs técnicos.
- **Destaque:** achou um bug conceitual (suavização aplicada duas vezes) e rejeitou os 70,3% da v3 por suspeita de overfitting.

**PR 84 (C003, 8.7), lucas-da-mata**
- **Volume:** 102 arquivos (61 tsx, 13 ts). 2 commits.
- **Solução:** app React/TanStack gerado com Lovable, publicado em https://pipeline-focus-buddy.lovable.app/. O score é por regras e explicável.
- **README:** 118 linhas, template completo, mas a análise é mais rasa: lista funcionalidades, não traz findings numéricos do dado.
- **Evidências:** `process-log/PROCESS_LOG.md` (166 linhas), 3 screenshots do app e `docs/QA_REPORT_2026-06-29.md`.

**PR 68 (C002, 8.2), pedro-henrique**
- **Volume:** 200 arquivos (46 md, 32 png, 43 ts/tsx). 2 commits.
- **Solução:** Next.js com Supabase/pgvector, RAG com GPT-4o-mini e Whisper, publicado em https://g4-help.vercel.app/login.
- **README:** 221 linhas. Tem findings com estatística e um modelo de ROI em R$.
- **Process log:** o mais volumoso da amostra, com 4 exports de chat (Claude, Codex, Manus, Perplexity), cerca de 30 screenshots e spec-kit.
- **Por que ficou abaixo:** o README tem 11 comentários `<!-- TODO -->` esquecidos, por exemplo "adicione sua perspectiva pessoal aqui". Além disso, `.agents/`, `.specify/` e `CLAUDE.md` foram comitados em `solution/`. Volume e deploy não compensaram o acabamento.

**PR 28 (C001, 3.0), dyego-cordeiro**
- **Conteúdo:** 3 arquivos. `submissions/dyego-cordeiro/README.md` é só um link para um PDF anexado no GitHub. `process-log/README.md` tem 1 byte, vazio e na raiz do repo. `process-log/NARRATIVA CONSTRUÇÃO CASE.docx` também está na raiz.
- **Commits:** 9, todos de upload ou remoção de PDF.
- Não tem código, análise versionada nem template.

**PR 79 (C004, 2.5), JoaoCouto1**
- **Conteúdo:** 1 arquivo, e ele altera o próprio diretório do desafio (`challenges/marketing-004-social/analysis.md`) em vez de `submissions/`. 1 commit.
- É um plano de análise sem nenhum número calculado ("A análise deve focar em...", listas de "Comparar: TikTok, Instagram..."). Não tem process log, código nem dados.

**PR 80 (C003, 6.0), rggpiva**
- **Conteúdo:** 32 arquivos. App desktop C# .NET 8 WinForms com ML.NET, que exige Windows e Visual Studio 2022, fora de `submissions/` (`rggpiva/`). 3 commits "Add files via upload".
- **README:** 166 linhas, mas não segue o template: faltam Sobre mim, Executive Summary e Findings.
- **Process log:** `rggpiva/process-log/PROCESS_LOG.md`, 79 linhas, genérico. Tem 8 screenshots e PDFs do tipo "Declaração de uso de IA".
- **Problema grave:** a linha 79 desse log admite que "o ambiente onde esta versão foi montada não possui o SDK do .NET", ou seja, o código C# não foi compilado. A validação foi feita à parte, em Python.

#### 2. O que separa os melhores dos piores, em concreto

1. **Questionar o dado antes de construir.** Os quatro primeiros têm uma seção explícita de desconfiança:
   - 83: uso fora da janela de assinatura e dois rótulos de churn divergentes (352 contra 110).
   - 81: prova com p-values que o dataset é sintético e decide não calcular ROI em cima dele.
   - 76: rejeita a própria métrica de 70,3% por suspeita de overfitting.
   - 69: mede contra baselines gerados só pela IA.

   Os de nota baixa não têm nenhum número (79) ou aceitam o próprio output sem conferir (80).
2. **Seção "onde a IA errou" com bugs específicos**, não frases genéricas: dupla contagem de MRR (83), suavização aplicada duas vezes (76), tela de upload removida (84). No 80 a "correção" é "não treinava ML, agora treina".
3. **Template seguido e README autossuficiente**, com números, recomendações com dono e limitações honestas. O 28 terceiriza tudo para um PDF externo, o 80 ignora o template e o 68 perde pontos por TODOs esquecidos.
4. **Rodar com um comando.** Os melhores rodam com `pip install` mais `streamlit run`, `uvicorn` ou `http-server`, e deixam cache ou arquivos gerados incluídos (69, 76). O 80 exige Windows e Visual Studio e nunca foi compilado.
5. **O que não decide:**
   - Deploy: os três primeiros não têm; só 84 e 68 têm, e ficaram abaixo.
   - Número de commits: o 69 tem 1 e o 28 tem 9.
   - Volume de arquivos ou de process log: o 68 tem o maior e ficou em 8.2.
   - Pasta correta: o 76 está aninhado errado e tirou 9.0.

   O avaliador parece pesar raciocínio analítico e honestidade muito acima de infraestrutura.
6. **Process log bom é narrativa de decisões**, com o que foi aceito ou rejeitado e por quê (83, 69, 81). Um despejo de prints e chats (68) conta menos, e um log vazio ou genérico (28, 80) derruba a nota.

#### 3. Censo dos 40 PRs abertos mais recentes criados depois de 2026-08-03

Há 48 PRs abertos criados depois de 2026-08-03. Olhei os 40 mais recentes: #116 a #160, criados entre 2026-09-11 e 2026-09-25.

**Challenge declarado no README:**

| Challenge | PRs |
|---|---|
| C001 | 11 |
| C002 | 12 |
| C003 | 12 |
| C004 | 3 |
| Não são submissões | 2 |

- Três PRs fazem vários challenges: #156 faz os 4, #147 faz os 4 com o 001 como principal, e #117 faz 001 e 003. Cada um foi contado pelo principal.
- Os 2 que não são submissões: #139 é um projeto não relacionado ("tumorsense", 1.058 arquivos fora de `submissions/`) e #125 só edita o README e o CONTRIBUTING da raiz.

**Stack (pela extensão dos arquivos e por imports):**

| Stack | PRs | Quais |
|---|---|---|
| Streamlit | 12 | 127, 129, 130, 135, 136, 137, 143, 147, 150, 156, 160, 120 |
| Front Node (Next/Vite/React) | 13 | 117, 121, 124, 126, 132, 133, 146, 152, 154, 155, 158, 159, 160 |
| FastAPI/Flask | 4 | 132, 134, 142, 155 |
| Notebook como entrega central | 2 | 130, 153 |
| HTML single-file ou HTML+JS | 5 | 116, 118, 123, 144, 151 |
| Só scripts Python, ou só imagens e markdown | cerca de 5 | 122, 128, 131, 148, 157 |

A tabela tem sobreposições (o #160 usa Streamlit e Next, o #132 usa Vite e FastAPI). Python domina no geral: cerca de 30 dos 40 têm arquivos .py.

**Process log:**
- 26 têm pasta `process-log/` com vários arquivos. Os maiores: #135 (68), #152 (67), #160 (52), #142 (44).
- 9 têm só um arquivo lá.
- 5 não têm nenhum: #118, #121, #125, #139, #146.

**Deploy:** pelo menos 13 PRs têm link de app publicado no README: Vercel em 8 (118, 121, 124, 126, 130, 133, 152, 158), Streamlit Cloud em 2 (135, 147), além de Railway (129), Netlify (144) e GitHub Pages (159). O #149 publica só uma página de linha do tempo do processo. Os links vieram de um grep nos READMEs, então podem existir outros deploys citados em outros arquivos.

**Sinais de nota baixa já visíveis (padrão parecido com 28/79/80):**
- #125 e #139 estão fora de `submissions/` ou nem são submissões.
- #116, #128, #153 e #144 têm de 4 a 9 arquivos com process log mínimo.
- #148 tem só imagens.
- #154 declara o challenge como "Lead Scoring" sem o número.

Não abri os READMEs desses para confirmar a qualidade; é uma triagem por estrutura.

</details>

**Ferramentas:**
- `Write`: ~/PROJETOS/Teste G4/ANALISE_PRS.md

### Aviso do sistema (25/09 13:40)

Tarefa em segundo plano terminou: Agent "Inspect top and rejected submissions" finished

### Claude (25/09 13:41)

O mais útil é que o avaliador do G4 (`joaovitor2763`) deixou **176 reviews públicas nos próprios PRs**, com aprovação ou pedido de ajustes e, em vários casos, nota de 0 a 10. Isso mostra o critério real de aprovação, não só o que o README diz.

Salvei o relatório completo em `~/PROJETOS/Teste G4/ANALISE_PRS.md`; os dados brutos estão em `Teste G4/prs/`.

#### Números gerais

- **159 PRs**: 138 abertos, 21 fechados e nenhum mergeado. Aprovar o PR significa "avançou para a próxima fase", e aí é preciso se inscrever na vaga do ATS.
- Dos 100 PRs revisados, **66 foram aprovados** (contando os aprovados depois de reenvio).

| Desafio | Taxa de aprovação | Sem review |
|---|---|---|
| 001 Churn | 45% | 15 |
| 002 Suporte | 89% | 15 |
| 003 Lead Scorer | 65% | 18 |
| 004 Social | 86% | 4 |

- **A última review é de 03/08/2026.** Há 59 PRs parados na fila, e a maioria chegou depois de junho.

#### Como ele avalia

- **Process log vale 30% da nota**, escrito com essas palavras nos PRs 6 e 7. Também é de longe o **maior motivo de reprovação** (cerca de 47 PRs):
  - faltar screenshots;
  - mandar só links externos;
  - mandar .docx ou .pdf;
  - mandar narrativa sem os exports das conversas.
- **Outros motivos de reprovação:**
  - Julgamento delegado à IA. No PR 12: "o julgamento analítico veio da ferramenta, não do candidato".
  - Commits assinados como "Claude" (PR 2).
  - node_modules commitado ou arquivos fora de `submissions/`.
  - README que diz uma coisa e código que faz outra.
  - AUC 1.0 aceito sem questionar.
- **Ele confere as armadilhas dos dados.** No 002, 49% dos tempos de resolução são negativos, o CSAT é aleatório e os textos têm o placeholder `{product_purchased}`. No 003, a data de referência tem que ser o `max(close_date)` e não a data de hoje, e há o `GTXPro` vs `GTX Pro`. No 001, há vazamento de informação da tabela de churn.
- **Reenviar funciona**, muitas vezes com aprovação no mesmo dia. Ao longo de março ele ficou mais rigoroso e chegou a revogar 10 aprovações.

#### O que tiveram em comum as notas mais altas (9.0 a 9.3: PRs 83, 69, 81, 76)

1. **Desconfiaram dos dados antes de construir.** O PR 81 provou estatisticamente que o dataset do 002 é sintético. O PR 83 derrubou com números as duas afirmações do CEO no 001.
2. **A seção "onde a IA errou" traz bugs concretos**, como MRR contado duas vezes ou uma suavização aplicada duas vezes.
3. **O PR 69 comparou o próprio trabalho com o baseline da IA.** Rodou o enunciado cru na IA três vezes, versionou essas respostas e escreveu antes do código os critérios que usaria para superá-las.
4. **O PR 83 usou um segundo modelo como revisor**: pediu ao Sonnet e ao Opus para criticarem o que o Codex tinha gerado.

**O que não decidiu a nota:** ter o app no ar (os três primeiros não têm), o volume do process log (o PR 68 tinha o maior e ficou em 8.2, penalizado por comentários TODO esquecidos no README) e o número de commits.

#### O que isso significa para você

- Salve screenshots e os exports brutos das conversas dentro do repositório, desde o início.
- Faça commits com o seu nome.
- Comece com uma seção de auditoria dos dados.
- Não inclua CLAUDE.md nem AGENTS.md na entrega; o PR 71 foi criticado por isso.
- **Antes de investir as 6 horas, confirme se o processo continua aberto.** As reviews estão paradas desde 03/08. Dá para perguntar abrindo uma issue no repositório ou olhar se a vaga ainda está no ATS.

Um aviso: as reviews são públicas, então os candidatos mais novos também conseguem ler as armadilhas. Conhecer esses pontos já não é diferencial por si só; o que vai pesar é como você trata eles.

Quer que eu confirme se a vaga continua aberta, ou prefere já escolher o desafio?

### Candidato (25/09 13:49)

a vaga ta aberta. Não se precoupxa.

Cria a estratégia para o 004 Social. QUer uma abordagem com todos os pontos de sucesso do outros candidatos, quero um log melhor e mais claro para pessoas fora do contexto de tecnologia analisarem. 
Começa.

**Ferramentas:**
- `Bash`: Check Kaggle, git identity and Python stack
- `Bash`: Extract evaluator reviews for challenge 004
- `Bash`: Download the 004 dataset from Kaggle
- `Bash`: Quick profile of the social media dataset
- `Write`: ~/PROJETOS/Teste G4/ESTRATEGIA_004.md

### Claude (25/09 13:51)

Estratégia escrita. Agora começo a Fase 0 no que não depende de aprovação: branch local, estrutura de pastas e dados fora do git.

**Ferramentas:**
- `Bash`: Create submission branch and folder structure
- `AskUserQuestion`

### Candidato responde (25/09 13:52)

Your questions have been answered: "Posso criar o ambiente Python do projeto com estas dependências: pandas, numpy, scipy, statsmodels, plotly, streamlit e jupyter (via uv, Python 3.12, isolado em .venv dentro da pasta da submissão)?"="Sim, pode instalar", "Posso criar o fork do repositório na sua conta do GitHub (Gchapolin)? O fork é público; o PR só seria aberto no final, com sua revisão."="Sim, criar o fork agora", "Os commits vão com seu nome (Gchapolin). Quer manter a linha 'Co-Authored-By: Claude' nos commits?"="Manter (Recomendado)".

### Candidato (mensagem enviada durante uma resposta) (25/09 13:51)

me mostra

### Candidato (mensagem enviada durante uma resposta) (25/09 13:51)

não começa ainda

### Claude (25/09 13:52)

Parei. Não criei o ambiente Python nem o fork. Antes da sua mensagem eu já tinha feito três coisas, todas locais e reversíveis: criei a branch `submission/guilherme-ferreira` no clone, criei a estrutura de pastas vazia e copiei o CSV para `solution/data/`, que fica fora do git.

A estratégia completa está em `~/PROJETOS/Teste G4/ESTRATEGIA_004.md`.

#### Estratégia para o 004

#### Ponto de partida
Todo mundo aprovado no 004 percebeu que o dataset é sintético. Isso virou o mínimo, não é mais diferencial. O perfil que rodei confirma:
- **Views praticamente iguais:** variam só 1% (de 9.676 a 10.551).
- **Seguidores não mudam o alcance:** correlação entre seguidores e views de 0,005. Um creator com 1 mil seguidores tem o mesmo alcance de um com 1 milhão.
- **Proporções redondas demais:** 60/20/10/10, típicas de um sorteio.
- **Textos aleatórios:** frases sem sentido geradas automaticamente.
- **Colunas que o brief promete e não existem:** "engagement rate" e custo de patrocínio.

A régua atual é o PR 91, avaliado como "Excepcional": intervalos de confiança, a decisão de não construir modelo preditivo, dashboard público, plano de 30 dias e roteiro de experimentos.

#### A tese
Estes dados não respondem o que o Head de Marketing perguntou, e eu provo isso de três formas. Mesmo assim entrego três coisas:
1. uma estratégia que continua certa sem sinal nos dados;
2. uma ferramenta que roda com os dados reais da empresa e separa sozinha sinal de ruído;
3. um plano de testes que gera o dado que falta.

#### O que vai além dos outros candidatos
| # | Diferencial |
|---|---|
| D1 | **Teste do sinal plantado.** Coloco de propósito um efeito conhecido nos dados e mostro que o método encontra. Isso prova que "não achei nada" é culpa dos dados, e não de um método cego. Nenhum candidato fez isso nas reviews que li. |
| D2 | **Laudo dos dados para leigo**, incluindo o tamanho mínimo de efeito que daria para detectar com esse ruído. |
| D3 | **Orgânico contra patrocinado comparado entre grupos equivalentes**, com intervalo de confiança e um mapa de semáforo: verde é sinal, cinza é ruído. |
| D4 | **Ferramenta "Radar de Conteúdo":** você sobe o CSV real da empresa e ela checa a saúde dos dados, mostra o mapa de sinal e ruído e calcula quantos posts um teste precisa. Também gera um resumo para a segunda-feira. |
| D5 | **Política de patrocínio como regras de decisão**, cada uma com uma condição para parar, mais o que deixar de fazer, ganhos rápidos e um plano de 30 dias. |
| D6 | **Comparação com o baseline:** colo o brief cru em 2 ou 3 IAs e mostro, item por item, o que elas afirmaram de errado. |
| D7 | **Um segundo modelo revisa a entrega final como crítico**, e registro o que foi aceito e rejeitado. |
| D8 | **Registro do processo pensado para quem não é de tecnologia.** |

#### O registro do processo para leigos
```
process-log/
├── 00_COMO_LER.md    1 pagina, 2 minutos, sem jargao
├── DIARIO.md         o log principal
├── LINHA_DO_TEMPO.md hora, etapa, quem decidiu, resultado
├── DECISOES.md       so as decisoes humanas: o que a IA sugeriu x o que voce escolheu
├── ERROS_DA_IA.md    o que ela errou, como foi percebido, como foi corrigido
├── GLOSSARIO.md      IC95%, p-valor, celula... em 1 linha cada
├── baseline/, screenshots/, transcripts/  evidencias brutas
```
Cada entrada do diário segue sempre o mesmo formato: o que eu queria saber, o que pedi à IA, o que ela respondeu, como conferi, o que decidi e uma frase em linguagem simples.

#### Plano (cerca de 6h)
São sete fases, cada uma terminando com uma **decisão sua** que fica registrada:
1. Configuração do ambiente e do repositório.
2. Baseline das IAs.
3. Auditoria dos dados.
4. Análise.
5. Estratégia.
6. Ferramenta.
7. Revisão crítica e fechamento.

Essas decisões são o que o avaliador chama de "steering", e pesam: foi a diferença entre as notas 7 e 9 nas reviews. Nas duas primeiras só fica o trabalho de mecânica, por isso as decisões que pesam de verdade entram a partir da auditoria dos dados.

---

Você já aprovou as dependências, o fork e a co-autoria com o Claude nos commits; faço isso quando você mandar começar. O que quer mudar ou discutir na estratégia antes disso?

### Candidato roda um comando (25/09 13:56)

`/model`

### Saída do comando (25/09 13:56)

Set model to `Fable 5.1` and saved as your default for new sessions

### Candidato (25/09 13:56)

reavalia o plano com fable e veja as falhas.

### Claude (25/09 13:58)

Reavaliei o plano do zero. Encontrei 9 falhas; três delas derrubariam a nota se ficassem como estão.

#### Falhas graves

**1. O semáforo do D3 daria "verde" para ruído.** Com 52 mil linhas e desvio de 100 views, o erro padrão de uma média de 10 mil posts é de cerca de 1 view. Uma diferença de 3 views entre plataformas sairia como "estatisticamente significativa", e é exatamente a armadilha que rebaixou o PR 17: diferença de 0,1% apresentada como insight. Pior: com mais de 60 células (5 plataformas x 3 categorias x 4 formatos x faixas de creator), cerca de 3 ficariam verdes por puro acaso.
Correção: o semáforo tem que ser por **tamanho de efeito com limiar de relevância prática definido antes** (por exemplo, só é sinal se a diferença passar de X% do baseline), com correção para múltiplas comparações. O IC95% entra como segundo filtro, não como o critério.

**2. Esta sessão roda em modo automático.** É o "Edit automatically" que o avaliador chamou de "sinal negativo" no PR 17 e que virou pedido de correção. Os transcripts vão mostrar isso.
Correção: o trabalho da submissão precisa rodar em sessão nova, com aprovação manual de cada edição, e o process log deve dizer isso explicitamente.

**3. O plano não cabe em 6 horas.** Oito diferenciais, app com upload, checagem de saúde, mapa, calculadora e brief, deploy, sete arquivos de log, baseline em três IAs e revisão adversarial dão de 10 a 12 horas. O avaliador marcou "ampliação de escopo" como ponto de atenção no PR 17 e "redundância entre README e análise" no PR 72. Meu log com sete arquivos mais três documentos de solução é redundância anunciada.
Correção: D1 e D2 viram um único laudo curto, onde a simulação é só um dos testes. D6 fica com uma IA, não três. O app perde o upload de CSV genérico. O log cai para quatro arquivos: como ler, diário, decisões e evidências.

#### Falhas de risco alto

**4. O sinal plantado pode ser lido como dado fabricado.** Os PRs 47 e 85 foram criticados por "dados sintéticos gerados pelo candidato". Se a simulação não ficar isolada e claramente rotulada como validação do método, o avaliador pode ler como manipulação.
Correção: script separado, nome explícito (`validacao_metodo_simulacao.py`), nunca misturado com os achados, e uma frase no README dizendo que nenhum número da análise vem dele.

**5. O log "para leigos" é o que o PR 54 chamou de "template gerado por IA".** Eu escreveria o diário, os erros da IA e as decisões. Ou seja, a IA relatando os próprios erros num formato rígido e polido. O avaliador quer o julgamento do candidato.
Correção: o arquivo de decisões é escrito por você, com suas palavras, mesmo que curtas e informais. Eu organizo o resto e aponto para os transcripts. E os screenshots precisam ser seus, do terminal, como o PR 30 fez depois de corrigido.

**6. Os transcripts vão incluir esta sessão.** Aqui tem análise dos outros candidatos e engenharia reversa do critério do avaliador. É informação pública e mostra pesquisa, mas precisa ser uma escolha sua: declarar abertamente ("li as reviews públicas para entender o critério") ou começar a submissão em sessão limpa. Também tem seu e-mail e caminhos locais nos transcripts, que precisam ser limpos.

#### Falhas de escopo

**7. A tese está desbalanceada.** Três dos oito diferenciais provam que não há sinal. "Dataset sintético" já é o padrão: 3 dos 6 aprovados no 004 fizeram isso. O que diferencia é o que se entrega apesar disso. Além disso, há dados reais mesmo aqui: a alocação de esforço (43% dos posts patrocinados, esforço distribuído igualmente entre plataformas, 5 mil creators sem concentração) é fato sobre a operação, não sobre engajamento, e responde "o que parar de fazer".

**8. As quatro perguntas do brief não estão mapeadas.** O avaliador conferiu no PR 17 se "as 4 hipóteses cobrem as perguntas do Head". Meu D3 detalha só orgânico contra patrocinado. "Perfil de audiência" e "o que não funciona" ficaram implícitos. Também faltou definir as métricas que o brief cita e o CSV não tem: engagement rate (likes + shares + comentários sobre views), faixas de creator e uma premissa explícita para o custo de patrocínio.

**9. Não há testes.** Minha regra global exige testes em todo código novo, e o avaliador cobrou testes em várias reviews do 003. As funções de estatística e do score da ferramenta precisam de pytest.

#### Falhas menores
- D7 com "um segundo modelo" Claude não é independente. Use ChatGPT ou Gemini, rodado por você.
- A revisão adversarial com 40 minutos no fim não deixa tempo para agir sobre ela. Trazer para depois da análise.
- "Roda com o CSV real da empresa" é promessa demais. O CSV real teria outro formato. O correto é "mesmo formato deste dataset".

#### O que eu mudaria no plano

| Antes | Depois |
|---|---|
| 8 diferenciais | 5: laudo com simulação, comparação por células com limiar de efeito prático, estratégia com regras e condições de parada, ferramenta com calculadora de teste, log com decisões suas |
| Log em 7 arquivos | 4 arquivos |
| Baseline em 3 IAs | 1 IA, rodada por você |
| Revisão adversarial no fim | Depois da análise, em IA de outro provedor |
| Sessão em modo automático | Sessão nova com aprovação manual, declarada no log |
| Sem testes | pytest para estatística e score |

Quer que eu reescreva o `ESTRATEGIA_004.md` com essas correções, ou prefere discutir algum ponto antes, especialmente o 6, que é a decisão de expor ou não esta sessão de pesquisa?

### Candidato (25/09 13:58)

sim, mas antes, usa as skills de mkt que temos aqui com base nesse escopo e crie o plano.

### Claude (25/09 13:58)

Vou carregar as skills de marketing relevantes para o escopo: social, influencer-marketing, ab-testing, analytics e content-strategy.

**Ferramentas:**
- `Skill`: marketing-skills:social
- `Skill`: marketing-skills:influencer-marketing
- `Skill`: marketing-skills:ab-testing
- `Skill`: marketing-skills:analytics
- `Skill`: marketing-skills:content-strategy
- `Bash`: Profile creator tiers and sponsorship disclosure
- `Write`: ~/PROJETOS/Teste G4/ESTRATEGIA_004.md

### Claude (25/09 14:01)

Plano v2 escrito em `~/PROJETOS/Teste G4/ESTRATEGIA_004.md`. O que mudou com as skills:

#### A tese agora tem duas camadas

| Camada | Veredicto |
|---|---|
| **Resultado** (views, likes, shares) | Sem sinal. Tudo rende igual. |
| **Alocação** (onde e com quem se patrocina) | Com sinal, e ruim: 95% em creators de 50k+, 47% com divulgação implícita, patrocinador combinado ao acaso com o conteúdo, todo creator patrocinado. |

Isso muda a frase para o Head: "os dados não dizem o que funciona, mas dizem o que você está fazendo errado, e dá para corrigir na segunda-feira sem esperar dado novo".

#### O que cada skill trouxe para a entrega

- **Influencer marketing:** as faixas nano/micro/mid/macro viram a unidade de análise; as faixas de preço por tier resolvem o "custo implícito" que o brief pede e o CSV não tem (como premissa declarada); as regras de compliance de divulgação e o teste de alinhamento de audiência dão dois achados reais para "parar de fazer"; deal híbrido e direitos de uso entram na política de patrocínio.
- **A/B testing:** a política vira um programa de 3 hipóteses no formato "porque X, acreditamos que Y...", cada uma com métrica primária, guardrail, MDE e amostra calculada; backlog por ICE; template de playbook; cadência semanal.
- **Analytics:** o quick win principal é um plano de rastreamento de 1 página (evento, propriedades, gatilho) para gerar o dado que falta.
- **Social:** decomposição do engajamento por objetivo (conversa = comentários, compartilhamento = shares), ritual semanal top 3 / bottom 3 no Radar.
- **Content strategy:** pilares (beauty, lifestyle, tech já são os pilares) com proposta de % por objetivo.

#### Correções das 9 falhas
- Semáforo por **tamanho de efeito com limiar prático definido antes**, mais correção de múltiplas comparações e mínimo de 30 por célula.
- Sessão nova em **modo de aprovação manual**, declarado no log.
- 5 diferenciais em vez de 8; log em 4 arquivos; baseline em 1 IA; estimativa honesta de 7 a 8 horas com ordem de corte.
- Simulação isolada em script próprio, com aviso no README.
- `DECISOES.md` **escrito por você**, com suas palavras; screenshots seus.
- As 4 perguntas do brief mapeadas uma a uma; métricas definidas antes da análise.
- pytest para métricas, células, estatística e score do Radar.

#### Fica faltando você decidir

1. Declarar no log que leu as reviews públicas do avaliador, ou deixar esta sessão de pesquisa fora dos transcripts. Recomendo declarar.
2. Limiar de efeito prático: 5% ou 10% do baseline. Recomendo 5%.
3. Se mantém o deploy no Streamlit Cloud no escopo ou deixa como corte.

Quando disser "começa", abro sessão limpa em modo manual e sigo a Fase 0.

### Candidato (25/09 14:09)

1. pode declarar 2. o mais agressivo possível. 3. pode fazer de acordo como teste.

### Claude (25/09 14:09)

Registrando as três decisões no plano. Sobre a 2, interpretei "mais agressivo" como o filtro mais rigoroso: 10% do baseline. Com esse limiar, a simulação precisa plantar efeitos acima dele (10% e 15%) e um abaixo (3%) para mostrar o filtro rejeitando. Se você quis o contrário, me corrige.

**Ferramentas:**
- `Edit`: ~/PROJETOS/Teste G4/ESTRATEGIA_004.md
- `Edit`: ~/PROJETOS/Teste G4/ESTRATEGIA_004.md
- `Edit`: ~/PROJETOS/Teste G4/ESTRATEGIA_004.md
- `Edit`: ~/PROJETOS/Teste G4/ESTRATEGIA_004.md
- `Write`: ~/PROJETOS/Teste G4/CLAUDE.md

### Claude (25/09 14:10)

Decisões registradas no plano e handoff pronto. Nada foi executado da Fase 0 nesta sessão, de propósito: ela roda em modo automático, e o log vai declarar que a submissão foi feita com aprovação manual. Isso precisa ser verdade desde o primeiro commit.

#### O que ficou registrado
1. **Declarar a pesquisa:** o `00_COMO_LER.md` vai dizer que você leu as reviews públicas e as submissões anteriores antes de começar; esta sessão entra nos transcripts.
2. **Limiar de 10% do baseline** (o mais rigoroso). A simulação planta efeitos de 15% e 10% para o método encontrar, e um de 3% para o método rejeitar.
3. **Deploy no Streamlit Cloud fica no escopo**, como teste; se falhar, roda local e o README diz isso.

#### Como abrir a sessão da submissão

```
cd ~/PROJETOS/Teste\ G4/ai-master-challenge
claude
```

Na sessão nova:
- Se ela abrir em modo automático, troque para o modo com aprovação manual (`Shift+Tab` alterna os modos; o log precisa refletir "aprovação por edição").
- O `CLAUDE.md` que deixei em `Teste G4/` é carregado sozinho, porque fica numa pasta pai. Ele aponta para o plano, o critério do avaliador e o estado atual, e traz as regras da entrega. Ele não entra no repositório.
- Primeira mensagem sugerida: `Lê o CLAUDE.md e o ESTRATEGIA_004.md e executa a Fase 0.`

Durante o trabalho, três coisas são suas e não minhas: os screenshots do terminal em cada etapa, o `DECISOES.md` com suas palavras, e rodar o brief cru numa IA para o baseline (Fase 1). Se preferir seguir nesta sessão mesmo assim, me diga e eu começo aqui, mas o log não poderá alegar modo manual para o setup.

### Candidato roda um comando (25/09 14:27)

`/save-session`

**Ferramentas:**
- `Bash`: Resolve session paths for save
- `Bash`: Check iCloud folder and create local Sessoes dir
- `Write`: ~/PROJETOS/Teste G4/notes/Sessoes/2026-09-25-1427.md
- `Write`: ~/.claude/projects/-HOME/memory/session_2026-09-25-1427.md
- `Edit`: ~/.claude/projects/-HOME/memory/MEMORY.md

### Claude (25/09 14:28)

```
Sessao salva:
  Vault:   ~/PROJETOS/Teste G4/notes/Sessoes/2026-09-25-1427.md
  Memory:  ~/.claude/projects/-HOME/memory/session_2026-09-25-1427.md
  Index:   ~/.claude/projects/-HOME/memory/MEMORY.md (entrada adicionada no topo)
  Grafo:   pulado (sem graphify-out/)
```

Duas observações:

- O CWD desta sessão é `~` e não a pasta do projeto, então associei ao projeto `Teste G4` sem perguntar, porque a conversa inteira foi sobre ele. A memória ficou no diretório de `~`, que é o carregado quando você abre o Claude a partir da home; a sessão da submissão, aberta dentro de `ai-master-challenge/`, vai receber o contexto pelo `Teste G4/CLAUDE.md`.
- `Teste G4` não tem pasta no iCloud (`ClaudeBrain-Mobile/`), então `notes/Sessoes/` foi criada local. O celular não vê essa sessão até você rodar `/claudebrain-init` na Fase 6. E vale rodar `/graphify` no projeto quando houver código, para criar o grafo.

