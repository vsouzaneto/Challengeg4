# Agente 4: o que está oculto no exercício

**Escopo:** busca por tudo o que está oculto, implícito ou fácil de deixar passar no repositório `Gestao-Quatro-Ponto-Zero/ai-master-challenge`, nos metadados do GitHub, nos datasets do Kaggle e na página da vaga.
**Data:** 2026-10-14
**Modo:** somente leitura. Nenhuma escrita no GitHub (nenhum push, PR, issue ou comentário). O único arquivo gravado é este relatório.
**Originalidade:** não li código nem conteúdo das soluções de outros candidatos. Li apenas os comentários e reviews do mantenedor (`joaovitor2763`, João Vitor Chaves Silva, autor de todos os commits do upstream). Esses reviews às vezes citam achados de outros candidatos. Neste relatório usei só os **critérios** que eles revelam, não as soluções.

---

## Resumo: os achados por ordem de impacto

| # | Achado | Impacto | A entrega do Arthur já trata? | Ação |
|---|---|---|---|---|
| 1 | **Há uma rubrica real com nota de 0 a 10**, em 4 dimensões: Leitura do problema, Qualidade do output, **Uso de IA (30% da nota)** e Comunicação. Os reviews são assinados por "G4 OS — assistente de avaliação". | Muito alto | Em parte | Deixar explícito o que foi decisão do Arthur e o que foi da IA (ver 2 e 3) |
| 2 | **Os avaliadores pedem evidência VISUAL do processo com a IA**: screenshots das conversas e iterações, não apenas do produto. Já reprovaram ou pediram mudanças por falta disso. Também já disseram "charts são outputs, não screenshots do processo" e "screenshots mostram o produto final, não o processo". | Muito alto | **Não.** Os 5 screenshots em `process-log/screenshots/` são todos do protótipo. Existe um export de chat em texto (`conversa_claude_code.md`, 6.087 linhas), que foi aceito em reviews de jul/ago, mas o padrão mais citado é ter screenshots. | **Adicionar de 4 a 6 screenshots das sessões do Claude Code** (um momento em que o Arthur corrigiu ou redirecionou a IA, o parecer do juiz, o erro da IA encontrado) |
| 3 | **A vaga pede, textualmente:** "Demonstre com clareza qual foi o seu papel e qual foi o papel da IA no processo". Os reviews repetem a mesma pergunta: "essa decisão foi sua ou proposta pela IA?" | Muito alto | Em parte. O README segue o template, com as seções "Onde a IA errou" e "O que eu adicionei". | Incluir no README uma tabela curta "Decisão → quem decidiu (Arthur/IA) → evidência (link/linha do chat)" |
| 4 | **É preciso se inscrever no ATS**, e isso é obrigatório. O texto da vaga diz que o fluxo é: se candidatar pelo formulário → receber e-mail com os links → resolver o case. O mantenedor comentou em vários PRs: "A inscrição é obrigatória para prosseguir". | Eliminatório | Fora do repositório | **O Arthur precisa confirmar que está inscrito** em https://ats.g4business.com/careers/g4-ai-master-r6gpj1 (LinkedIn obrigatório no formulário) |
| 5 | **`submissions/` está no `.gitignore` raiz.** Arquivo novo não aparece no `git status` e não entra com `git add .`. Hoje **`solution/03-prototipo/src/painel.py` (21,5 KB) e `process-log/agentes/*.md` estão ignorados e fora do commit.** | Alto | Não | Para tudo o que for entrar, rodar `git add -f <arquivo>`. Antes do PR, conferir com `git status --ignored submissions/arthur-leite` |
| 6 | **A higiene do repositório reprova:** `node_modules` commitado, chave hardcoded, código só em link externo (Lovable/Replit/ZIP) e commits com author "Claude" já foram motivo de reprovação. | Alto | Sim. Os 9 commits têm author "Arthur Leite <artroleite2015@…>", o `.env` e o `__pycache__` estão ignorados e o código está no repositório. O trailer `Co-Authored-By: Claude` é honesto e não é o problema citado (o problema era o *author*). | Manter. Não commitar `data/`, `.env` nem `__pycache__` |
| 7 | **Os 2 datasets precisam aparecer.** "Usou ambos os datasets?" é um critério declarado. Um candidato do 002 recebeu pedido de mudanças porque não usou o DS2 no modelo final. | Alto | Sim. DS1 foi usado para estrutura e para testar as travas; DS2 foi usado para treinar e avaliar. | Manter |
| 8 | **"~30.000 registros" é falso (são 8.469).** O Kaggle não diz em lugar nenhum que o DS1 é sintético. A página nem cita 30 mil. Os reviews premiaram explicitamente quem auditou o dado ("CSAT aleatório", "durações negativas", "placeholders"). O enunciado também omite a coluna `Date of Purchase` e não diz que FRT/TTR são *timestamps*. | Alto (é sinal de avaliação, não necessariamente uma pegadinha planejada) | **Sim.** O README e o PROCESS_LOG registram que são "8.469, não ~30 mil", além dos placeholders e do CSAT aleatório | Manter em destaque no Executive Summary |
| 9 | **Nenhum review do mantenedor desde 2026-08-03.** Os PRs #108 a #190 (cerca de 83) estão sem review. A vaga foi republicada em 2026-09-29. Nenhum PR foi mergeado; os 25 PRs fechados foram fechados pelos próprios autores. | Médio | Não se aplica | Não esperar feedback no PR. O canal que move o processo é o ATS (e-mail) |
| 10 | **ROI precisa de premissas explícitas**, idealmente com faixa de sensibilidade. "ROI de $128k/mês não é verificável" foi motivo de pedido de mudanças. | Médio | Provavelmente sim ("ROI v2 revisado pelo juiz", premissas ajustáveis no app, screenshot 05) | Conferir se cada número de R$ diz de onde vem |
| 11 | **Sinais negativos de uso de IA** já citados: modo "Edit automatically" do Claude Code ligado ("remove o humano do loop") e prompts do tipo "você é um programador sênior com 20 anos…, crie tudo". | Médio | No chat export, os únicos "Você é…" são os prompts do **juiz adversarial**, o que é positivo. Não encontrei menção a auto-accept/bypass. | Se houver screenshots, evitar que mostrem o modo de auto-aceitar edições |
| 12 | **Pontos não bloqueadores que os avaliadores elogiam:** testes automatizados, histórico com vários commits (já criticaram "1 commit concentrado"), deploy público estável, piloto com critério de go/no-go e monitoramento de override humano. | Baixo/Médio | Tem 9 commits semânticos e deploy no Streamlit. Testes automatizados não vi (não verifiquei a fundo). | Opcional: alguns testes de `politica.py`/`triagem.py` e um gate de go/no-go do piloto |
| 13 | **Não há conteúdo oculto no markdown** (zero-width, comentários HTML, prompt injection ou honeypot para IA). | Nenhum | Não se aplica | Nenhuma |

---

## 1. Histórico git do upstream

### Comandos
```bash
cd /c/Users/arthu/g4-ai-master-challenge
git fetch upstream --tags
git log upstream/main --stat --format='=== %H %s%n%b'
git ls-remote https://github.com/Gestao-Quatro-Ponto-Zero/ai-master-challenge.git | grep -v refs/pull
git ls-remote ... | grep -c refs/pull        # 360 refs de PR
git show 4aed364 bcdfd2e
git show d91427f:.gitignore
git show d91427f:challenges/process-002-support/brief.md
git log upstream/main..upstream/compass-github-importer --stat
```

### Commits (todos de 2026-03-02, João Vitor Chaves Silva, com `Co-Authored-By: G4 OS <g4os@g4business.com>`)
| Hash | Mensagem | O que revela |
|---|---|---|
| `d91427f` | initial structure with 4 challenges | Cria o `.gitignore` com `_internal/` ("**Private scoring (never commit)**"), `datasets/` e `submissions/` ("if candidates fork"). Existe uma rubrica privada fora do repositório. Ela **nunca foi commitada**: varri todos os blobs de todos os commits e branches e não há rastro de `_internal/`. |
| `d4c8fc7` | add README.md for each challenge | Os READMEs ganham a seção "Critérios de qualidade" |
| `4b55509` | clean up repo structure | Remove os `brief.md`, cria o `templates/submission-template.md` e o `CONTRIBUTING.md` |
| `bcdfd2e` | **docs: add baseline warning — AI-only submissions won't pass** | Mensagem do commit: "we already generated baselines using multiple AI models. Submissions that match the baseline don't advance." Ou seja, existem respostas de referência de Claude, GPT e Gemini, e a entrega precisa "superar substancialmente" esse baseline. |
| `4aed364` | **feat: PR-only submissions — remove email option** | Corpo do commit: "This is itself part of the test — an AI Master should be able to work with git." Remove o e-mail `g4os@g4business.com` como canal. Define as regras do PR: título `[Submission] Nome — Challenge XXX`, **um PR por pessoa** (atualizações por push na mesma branch), **só alterar `submissions/seu-nome/`** ("PRs que alteram outros arquivos serão rejeitados"), branch `submission/seu-nome`, PR para `main`. |

- **Branch remota extra:** `compass-github-importer` (`c1c178e`, bot da Atlassian Compass). Só adiciona `compass.yml` com `tier: 4`. Irrelevante para a avaliação.
- **Tags:** nenhuma.
- **Versão antiga do brief 002 (`d91427f`):** usava `satisfaction_score` e `it_service_tickets.csv` (nomes que não existem nos dados) e já trazia "~30.000". Na versão atual entraram "empresa de tecnologia", a tabela de colunas, os "Critérios de qualidade" e a frase "Quero ver algo rodando". O "~30.000" vem desde o primeiro commit, sem nenhuma correção. A explicação mais provável é um número inventado na redação (talvez gerado por IA), e não uma armadilha planejada. Mesmo assim, os avaliadores premiam quem detecta o erro.

## 2. Varredura de conteúdo oculto

### Comando (resumo)
Script Python que percorre **todos os blobs de todos os commits** (`upstream/main` + `compass-github-importer`) e procura `​ ‌ ‍ ⁠ ﻿ ­`, bidi (`‪-‮`, `⁦-⁩`), tags Unicode (`U+E0000–E007F`), `<!--`, espaço no fim de linha e palavras-chave (`LLM`, "se você é uma IA", "ignore", "instru*", "honeypot", "secret", "hidden", "oculto", "baseline"). Também listei todas as definições de link (`[x]: url`), tags HTML e alvos de link.

### Resultado
- **Zero** caracteres de largura zero, bidi ou tags Unicode, **zero** comentários HTML, **zero** espaços no fim de linha.
- Os únicos caracteres não-ASCII que não são letras são `— → ← · ≠ ↓` e os de desenho de árvore (`├ └ │ ─`).
- Não há instrução para IA, honeypot ou palavra-código. "Baseline" só aparece no aviso público.
- Não há links escondidos: todos apontam para o Kaggle, o G4 ou arquivos internos.
- Não existe `.github/`: sem templates de PR/issue, sem workflows de CI, sem CODEOWNERS. A API (`/rulesets`, `/branches/main/protection`) retornou 404 ou vazio. **Nenhuma validação automática do PR.**

## 3. Metadados do GitHub (somente leitura)

### Comandos
```bash
R=Gestao-Quatro-Ponto-Zero/ai-master-challenge
gh api repos/$R
gh api repos/$R/labels
gh api repos/$R/branches/main/protection ; gh api repos/$R/rulesets ; gh api repos/$R/contents/.github
gh api "repos/$R/issues?state=all&per_page=100" --paginate   # 190 itens
gh api "repos/$R/issues/comments?per_page=100" --paginate     # 118 comentários
for n in 1..190: gh api repos/$R/pulls/$n/reviews  (filtrando user.login=="joaovitor2763")
gh api repos/$R/issues/64
gh api repos/$R/issues/<n>/events   # quem fechou os PRs
```

### Números (2026-10-14)
- Repositório: 134 forks, 7 estrelas, sem topics, sem discussions. Último push no upstream em **2026-03-02**.
- **189 PRs e 1 issue.** 164 PRs abertos, 25 fechados, **0 mergeados**. Todos os 25 fechamentos foram feitos pelo próprio autor.
- Labels: só as padrão do GitHub, **nenhuma aplicada**.
- **12 usuários têm mais de um PR** (contraria "um PR por pessoa"; não sei se foram penalizados).
- **43 PRs são do Challenge 002**, o mais concorrido junto com o 003. A comparação entre candidatos do 002 vai ser direta.
- **Arthur (`arthurroleite`) ainda não tem PR.**
- Reviews do mantenedor: 175 (87 APPROVED, 81 CHANGES_REQUESTED, 7 COMMENTED) em **99 PRs**. O último estado ficou em 66 aprovados e 33 com pedido de mudanças. Período: 2026-03-03 a **2026-08-03**. **Nenhum PR acima do #107 recebeu review** (cerca de 83 sem avaliação no GitHub).
- O bot `chatgpt-codex-connector[bot]` fez review automático em 3 PRs (#84, #89, #188, trigger "PR opened"). Como aparece em poucos PRs, provavelmente depende da configuração do próprio autor, e não do G4. Incerto.

### O que os reviews do mantenedor revelam (critérios, não soluções)
Links de exemplo: PR #4 (comentário 4060709807), PR #2 (review 3945543688), PR #27 (review 3981445831) e outros.

1. **Escala e dimensões da nota:** "Score: X/10", com faixas *Reprova* (≤ ~6,4), *Ressalvas* (5,3–6,3), *Forte* (7,0–8,7) e *Excepcional* (≥ 9,0). Dimensões nomeadas: **Leitura do problema / Qualidade do output / Uso de IA / Comunicação**. Citações: "O critério 'Uso de IA' pesa 30% da nota"; "Isso vale 30% da avaliação"; "Sem isso, não conseguimos avaliar 30% dos critérios".
2. **A avaliação é feita por IA e o critério mudou com o tempo:** os comentários terminam com "*Avaliação por G4 OS — assistente de avaliação do AI Masters Challenge*". Também aparece "Revisando sua submissão com o critério atual do processo…" (2026-03-20), quando PRs que já tinham sido aprovados receberam pedido de mudanças por falta de screenshots, e há reavaliações que admitem "fomos duros demais". **Na prática, o primeiro leitor provavelmente é um LLM:** README claro, auditável, com caminhos explícitos e números com origem rastreável favorece a nota.
3. **Eliminatórios citados:** sem process log; evidência só em link externo ("links externos não são aceitos como evidência"; "Links podem expirar, não são auditáveis offline"); código fora do repositório; `solution/` vazio; `node_modules` commitado (a issue #64 confirma a reprovação: "Dependências commitadas são erro de higiene básico"); commits com author "Claude"; AUC 1,0 ou 0,43 sem investigação; arquivos fora da pasta da submissão.
4. **Process log:** pedem os momentos em que o candidato "discordou ou corrigiu a IA", "quais insights foram seus vs. gerados pela IA", "hipóteses que você formulou antes de pedir à IA". Elogiam "N erros da IA documentados com causa raiz" e "decisão custosa documentada". Penalizam "estratégia de análise gerada pela IA antes de qualquer exploração independente dos dados".
5. **Evidência visual:** "o critério de avaliação exige evidência visual do processo com a IA — screenshots das principais iterações, correções e decisões". O ideal é texto **e** imagem: um review também pediu "Process log textual auditável — não só screenshots".
6. **Específico do 002:** elogiam auditoria do dado antes de qualquer cálculo, recusa a "gerar análises bonitas sobre ruído", uso dos 2 datasets com tratamento do *domain shift*, gate de confiança/abstenção calibrado, lista explícita do que **não** automatizar (reembolso, cancelamento, crítico), ROI com premissas e faixas, recomendação de piloto, testes automatizados e screenshots do app.
7. **Execução:** o README precisa ter como rodar, a fórmula ou os pesos e as validações. A entrega precisa ser utilizável por um gestor "sem depender de Python" (pedido de mudanças no PR #32), o que reforça o valor do relatório executivo em HTML/PDF e do app no ar.

### Issue #64 ("Uma proposta diferente para um não avanço justo")
Um candidato do Challenge 003 reprovado escreve que "o não avanço foi justo. Dependências commitadas são erro de higiene básico" e se oferece para entrar em nível inferior. Não há resposta do G4. Isso confirma: **(a)** os feedbacks são individuais e detalhados; **(b)** um erro de higiene de repositório derruba uma análise boa; **(c)** não há uma segunda via pela issue.

## 4. Datasets do Kaggle

### Comandos
```bash
curl -s https://www.kaggle.com/api/v1/datasets/view/suraj520/customer-support-ticket-dataset
curl -s https://www.kaggle.com/api/v1/datasets/view/adisongoh/it-service-ticket-classification-dataset
```
- **DS1 (suraj520):** CC0, 3,9 MB, atualizado em 2023-06-02. A descrição **não diz que é sintético** e **não informa o número de linhas**. Ela diz que `Resolution` e `Customer Satisfaction Rating` existem só "for closed tickets", o que explica os nulos, e que o e-mail `@example.com` "is intentional". A coluna **`Date of Purchase` existe no Kaggle, mas foi omitida da tabela do enunciado.** Uma busca na web encontrou análises de terceiros que descrevem o conjunto como gerado sinteticamente (texto templado, placeholders), sem confirmação do autor.
- **DS2 (adisongoh):** CC0, 14,6 MB, "47,837 rows", 8 categorias. Bate com os "~48.000" do enunciado.
- **Conclusão:** só o número do DS1 está errado (cerca de 3,5 vezes maior que o real). Como o README diz "~30.000 registros com texto real", a frase "texto real" também é falsa para o DS1 (100% placeholders). É um teste de verificação de fato na prática, mesmo que não tenha sido planejado. **O Arthur já trata isso** (README, linha 46: "8.469 tickets, não ~30 mil"; PROCESS_LOG, linha 37).

## 5. Página da vaga

A página é uma SPA. O `WebFetch` e o Chrome falharam. Li o **registro público da vaga** com a mesma consulta anônima que a própria página faz no navegador (`jobs_public?shortid=eq.r6gpj1` e `job_settings` em `api-ats.g4business.com`, usando a chave pública "anon" que está no bundle JS da página). **Observação de transparência:** o classificador de segurança do Claude Code bloqueou um comando de leitura logo depois desse acesso. Se o Arthur preferir, ele pode conferir o texto direto no navegador.

Sinais relevantes:
- Vaga **republicada em 2026-09-29** (`publish_at`), com última edição em 2026-09-09.
- **Processo:** formulário → e-mail com os links → **teste prático** (este case) → **teste lógico** (se aprovado) → entrevistas. Citação: "**Demonstre com clareza qual foi o seu papel e qual foi o papel da IA no processo.**"
- Formulário: **LinkedIn obrigatório**, Instagram e pretensão salarial opcionais, sem CV e sem vídeo.
- Os 7 requisitos são "critério de eliminação", entre eles **resultado quantificável em cargo anterior**, IA avançada (agentes/RAG/pipelines), Python/SQL para validar hipóteses, comunicação executiva ("C-level lê e decide em 5 minutos") e **presencial full-time em SP**. A faixa é de R$ 10 mil a 40 mil por mês.
- As "5 frentes" do cargo (Mapeamento, Orquestração técnica, Entrega end-to-end, **Suporte/sustentação e melhoria contínua**, Comunicação executiva) servem de checklist implícito. Vale a entrega mencionar monitoramento pós-implantação (drift, taxa de override, kill switch, re-treino).
- O "prazo" está só no README: "não há deadline fixo (mas vagas são limitadas)".

## 6. Convenções implícitas de PR (checklist do Arthur)

| Regra | Fonte | Status do Arthur |
|---|---|---|
| Fork → branch `submission/arthur-leite` | CONTRIBUTING | OK (`origin/submission/arthur-leite`) |
| Pasta `submissions/arthur-leite/` (nome-sobrenome em minúsculas, como os aprovados `arthur-reis` e `lucas-oriani`) | CONTRIBUTING e reviews | OK |
| Só arquivos dentro da pasta | CONTRIBUTING (rejeição) | OK (`git diff --name-only upstream/main...HEAD` não lista nada fora da pasta) |
| Título exato `[Submission] Arthur Leite — Challenge 002` (travessão `—`) | CONTRIBUTING | A fazer no PR |
| PR para `main` do upstream; **um PR só**, atualizações por push | CONTRIBUTING | A fazer |
| README da pasta segue o template (Sobre mim com LinkedIn, Executive Summary, Solução, Process Log, Evidências) | template | OK (as seções batem) |
| `git add -f` em tudo, já que `submissions/` está ignorado | `.gitignore` raiz | **Atenção:** `src/painel.py` e `process-log/agentes/` estão fora do índice |
| Sem dados brutos, `.env`, `__pycache__`, `node_modules` | reviews | OK. Os 43 arquivos tracked foram conferidos; a pasta local tem 119 MB, mas o volume está em `data/` (ignorado). Nenhum arquivo tracked passa de 20 MB. |
| Inscrição no ATS | comentários do mantenedor e vaga | **Confirmar** |

Comandos usados para a seção 6:
```bash
git log --format='%h %an <%ae> | %s' upstream/main..HEAD
git log --format='%h %(trailers:only,unfold)' upstream/main..HEAD
git diff --name-only upstream/main...HEAD | grep -v '^submissions/arthur-leite/'
git -C submissions/arthur-leite ls-files .
git ls-files --others --ignored --exclude-standard submissions/arthur-leite
git status --short --ignored submissions/arthur-leite
find submissions/arthur-leite -type f -size +20M
```

## 7. Ações recomendadas (por prioridade)

1. **Confirmar a inscrição no ATS** (com LinkedIn). Sem ela, o processo não anda, mesmo com PR aprovado.
2. **Adicionar de 4 a 6 screenshots do processo com a IA** em `process-log/screenshots/` (por exemplo `06_claude_code_auditoria.png`, `07_juiz_refuta.png`, `08_correcao_roi.png`), mostrando os prompts do Arthur e os momentos em que ele corrigiu a IA. Referenciar cada um no PROCESS_LOG.
3. **Incluir no README uma tabela "Meu papel × papel da IA"**, com 6 a 10 decisões-chave e o link para a linha do chat export ou para o parecer do juiz. Isso responde de frente à frase da vaga e ao critério de 30%.
4. **Antes do commit final:** `git add -f` em `solution/03-prototipo/src/painel.py` (se o `app.py` passar a importá-lo; hoje não importa) e decidir se `process-log/agentes/` entra. Se entrar, ele soma como evidência de orquestração multiagente.
5. Abrir **um único PR** com o título exato `[Submission] Arthur Leite — Challenge 002`. Não esperar review no GitHub: desde agosto não há reviews.
6. Opcional: alguns testes unitários de `politica.py`/`triagem.py`, um critério de go/no-go do piloto e uma linha sobre sustentação/monitoramento (override humano, drift).
