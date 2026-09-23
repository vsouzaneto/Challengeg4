# Lean Challenge 001 Delivery Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** entregar a resposta do Challenge 001 em menos de dois minutos de navegação inicial, preservando profundidade técnica sob demanda.

**Architecture:** cinco entradas visíveis formam a entrega: Comece aqui, Veja funcionando, Entenda a arquitetura, Veja a síntese e Audite. O vídeo obrigatório explica a arquitetura em primeira pessoa; o Video Overview do NotebookLM sintetiza método e evolução; o infográfico fixa a jornada visual. O relatório e o Process Log ficam como profundidade, não como porta de entrada.

**Tech Stack:** Markdown, DOCX, NotebookLM Video Overview e Infographic, Arcade Interactive Demo, vídeo H.264 existente, Git/GitHub e Streamlit.

**Spec:** `.specs/tasks/todo/package-challenge-001-deliverables.feature.md`

## Global Constraints

- O avaliador deve alcançar a resposta principal sem rolar um documento longo.
- O vídeo obrigatório tem 6min05s, 1920×1080, 60 fps, H.264/AAC e legendas queimadas.
- O MP4 de 232.879.349 bytes não será commitado no Git.
- Markdown é o formato para IA; DOCX é a cópia humana. Não produzir TXT redundante.
- Os dois vídeos têm funções distintas: arquitetura autoral versus síntese da construção.
- Não gerar mapa mental, slide deck ou landing page.
- Publicação dos vídeos, Arcade e PR upstream exige confirmação final de Luis.
- Nenhum push final ou PR ocorre antes de todos os gates abaixo estarem verdes.
- O Challenge 001 é o desafio principal e único desta submissão; será publicado na branch `submission/luis-roquette` e no único PR permitido por pessoa.

## Review Focus

- O primeiro bloco do README demora mais de 30 segundos para revelar resposta e decisão.
- Um dos vídeos está inacessível sem login ou sem permissão pública adequada.
- Os dois vídeos repetem o mesmo conteúdo em vez de cumprir funções distintas.
- Arcade repete metodologia em vez de demonstrar o sistema.
- Brief, vídeos ou infográfico introduzem números ou causalidade não sustentados.
- A quantidade de links devolve ao avaliador o trabalho de decidir por onde começar.

---

### Task 1: Criar a porta de entrada de duas páginas

**Files:**
- Create: `deliverables/delivery-brief.md`
- Generate: `deliverables/delivery-brief.docx`
- Create: `deliverables/delivery-manifest.md`
- Modify: `../../README.md`

**Interfaces:**
- Consumes: `artifacts/ceo_answer.json`, `docs/executive-answer-rubric.md` e `process-log/000-004`.
- Produces: brief canônico de até 1.200 palavras e índice de cinco entradas.

- [x] **Step 1: escrever a abertura de 30 segundos**

Usar cinco blocos: resposta em seis linhas; decisão; ações; método em oito etapas; links. Cada ação deve declarar prioridade, impacto mensurável, impacto financeiro e confiança. Quando o efeito causal não for estimável, escrever isso explicitamente e tratar US$ 1.622.337 somente como exposição histórica. A abertura deve conter 12,4%, +7,0 pp, US$ 1.622.337 e “Causa ainda não demonstrada”.

- [x] **Step 2: mostrar a evolução sem contar toda a história**

Incluir uma única tabela `Momento | Problema encontrado | Decisão humana | Nota`, com `7,0 → 8,6 → 9,5 → 9,9`. Limitar prompts a quatro fragmentos decisivos.

- [x] **Step 3: gerar o DOCX a partir do Markdown**

Usar a skill `documents`; o Markdown permanece a fonte editável. O DOCX deve caber em duas páginas A4, com links clicáveis e sem anexos incorporados.

- [x] **Step 4: validar o brief**

Run:

```bash
test "$(wc -w < deliverables/delivery-brief.md)" -le 1200
rg -n "12,4%|7,0 pp|1\.622\.337|Causa ainda não demonstrada|Impacto estimado|não estimável|7,0 → 8,6 → 9,5 → 9,9" deliverables/delivery-brief.md
```

Expected: limite e cinco âncoras atendidos.

- [x] **Step 5: checkpoint**

```bash
git add -f deliverables/delivery-brief.md deliverables/delivery-brief.docx deliverables/delivery-manifest.md ../../README.md
git commit -m "docs(churn): create lean delivery entrypoint"
```

### Task 2: Incorporar o vídeo obrigatório de arquitetura

**Files:**
- Source: `2026-09-22 18-24-32_LEGENDADO_1,25x.mp4`
- Create: `deliverables/video/README.md`
- Create: `deliverables/video/poster.png`

**Interfaces:**
- Consumes: MP4 local de 6min05s.
- Produces: link acessível, capítulos, metadados, poster e SHA-256; nunca o binário no Git.

- [ ] **Step 1: assistir integralmente e registrar capítulos**

Marcar timestamps reais para: problema; arquitetura; metodologia; implementação; validação; conclusão. Não deduzir capítulos apenas pelo nome do arquivo.

Pré-revisão concluída: 366 amostras visuais e OCR das legendas produziram os capítulos. Falta a reprodução integral em tempo real para fechar o passo.

- [ ] **Step 2: validar mídia e legendas**

Conferir áudio do início ao fim, legibilidade das legendas queimadas, ausência de segredo/tela privada e sincronia a 1,25×. Registrar duração exata `365,533 s`.

Metadados, legendas e trechos de áudio foram conferidos. Falta ouvir o áudio integral e verificar transições menores que um segundo.

- [x] **Step 3: gerar poster e checksum**

Extrair um quadro representativo sem informação privada e registrar `shasum -a 256` no README do vídeo.

- [x] **Step 4: preparar hospedagem externa**

Recomendação: YouTube não listado, por reprodução imediata sem download de 222 MiB. Parar antes do upload/publicação e solicitar confirmação de Luis.

- [ ] **Step 5: validar o link publicado**

Depois da confirmação, abrir o link em sessão anônima, reproduzir início/meio/fim e verificar título, legenda, capítulos e acesso sem login.

### Task 3: Criar o Arcade de até 90 segundos

**Files:**
- Create: `deliverables/arcade/arcade-script.md`
- Create: `deliverables/arcade/README.md`

**Interfaces:**
- Consumes: dashboard validado em `127.0.0.1:8503`.
- Produces: demo interativa focada no produto, com oito passos.

- [x] **Step 1: roteirizar os oito passos**

1. A pergunta e a resposta curta.
2. Churn e impacto econômico.
3. Produto: agregado versus coorte.
4. CS: respondentes versus coorte.
5. Sem concentração material.
6. Causa ainda não demonstrada.
7. Três validações com donos e prazos.
8. Evidência, `analysis_id` e chamada para o brief.

- [x] **Step 2: limitar a carga cognitiva**

Cada instrução possui até 22 palavras; nenhum passo mostra mais de uma ideia; o tour completo deve caber em 60–90 segundos.

Roteiro fechado em oito passos e 83 segundos estimados. O fluxo permanece linear porque branching acrescentaria escolha sem melhorar a resposta executiva.

- [x] **Step 3: capturar e revisar o rascunho**

Usar screenshots do dashboard e no máximo um trecho de vídeo de interação. Conferir números, foco, desktop/mobile e ausência de caminhos locais.

Rascunho privado `aIAtdPLJilhZOtM7ao5O` criado com oito screenshots reais e oito hotspots. Previews desktop e mobile revisados; nenhum caminho local aparece.

- [x] **Step 4: preparar publicação**

Parar antes do compartilhamento público. Após confirmação de Luis, salvar URL, data e acesso anônimo no README do Arcade.

Publicação preparada e interrompida antes do Share. O CTA final será ligado ao brief somente quando a URL remota definitiva existir.

### Task 4: Gerar Video Overview e infográfico no NotebookLM

**Files:**
- Create: `deliverables/notebooklm/source-pack.md`
- Create: `deliverables/notebooklm/generation-prompts.md`
- Create: `deliverables/notebooklm/README.md`
- Receive: `deliverables/visuals/method-evolution-infographic.png`

**Interfaces:**
- Consumes: brief e diários públicos.
- Produces: Video Overview compartilhável e uma peça visual sobre método e evolução.

- [x] **Step 1: montar fonte curta e fechada**

Incluir somente oito etapas metodológicas, quatro notas, três viradas humanas e seis fatos do diagnóstico. Excluir logs extensos, código e dados brutos.

Fonte fechada criada com as contagens exatas e limites causais explícitos.

- [x] **Step 2: gerar o Video Overview com função própria**

```text
Crie um Video Overview em português brasileiro, com duração alvo de 3–5 minutos, para avaliadores de um processo seletivo de AI Master. Sintetize a evolução do trabalho: pergunta do CEO, método autoral, três decisões humanas que corrigiram o rumo, resposta final e próximos passos. Não faça walkthrough técnico da arquitetura, pois existe um vídeo autoral separado. Não invente causa, número ou nota externa.
```

Notebook privado criado com uma fonte. A primeira geração foi rejeitada porque transformou seis hipóteses inconclusivas em “rejeitadas”. O prompt foi corrigido uma vez. A segunda geração explicativa, “Paradoxo de Churn do CEO”, foi aceita após decodificação integral, transcrição completa do áudio e OCR de 360 quadros.

- [ ] **Step 3: gerar o infográfico com o prompt editorial**

```text
Crie um infográfico vertical em português brasileiro: “De uma pergunta confusa a uma decisão confiável”. Mostre oito etapas, a evolução 7,0 → 8,6 → 9,5 → 9,9 e três viradas humanas: separar agregados de coortes; recusar causalidade frágil; converter incerteza em validação. Use somente as fontes e não acrescente números.
```

Configuração validada em português brasileiro, orientação retrato e estilo editorial. O NotebookLM bloqueou a geração pelo limite diário de infográficos; nenhum upgrade foi contratado.

- [ ] **Step 4: revisar e exportar os dois outputs**

Assistir o Video Overview integralmente e conferir texto, notas, números, autoria e ausência de causa inventada no vídeo e no infográfico. Se a primeira geração falhar, corrigir o prompt uma vez; depois, editar a fonte em vez de iterar indefinidamente. Registrar links, duração, fontes e data no README do NotebookLM.

- [ ] **Step 5: checkpoint**

```bash
git add -f deliverables/notebooklm deliverables/visuals
git commit -m "docs(churn): add one-page methodology infographic"
```

### Task 5: Fechar a entrega em cinco entradas

**Files:**
- Modify: `deliverables/delivery-manifest.md`
- Modify: `../../README.md`
- Modify: `../../process-log/004-planejamento-entregaveis.md`

**Interfaces:**
- Consumes: brief, vídeo obrigatório, Arcade, Video Overview, infográfico e evidências existentes.
- Produces: entrada final do avaliador e PR pronto para revisão.

- [x] **Step 1: ordenar a abertura**

Mostrar somente: `Leia em 2 minutos`; `Veja funcionando em 90 segundos`; `Entenda a arquitetura em 6 minutos`; `Veja a síntese do NotebookLM`; `Audite o processo`. O infográfico acompanha a síntese; relatório e código ficam dentro de “Audite”.

README e manifesto agora apresentam exatamente as cinco entradas. O DOCX acompanha o brief, em vez de competir como uma sexta entrada.

- [ ] **Step 2: validar tudo como avaliador anônimo**

Abrir cada link sem sessão; confirmar que nenhum exige permissão; assistir Arcade e os dois vídeos; abrir DOCX; verificar o infográfico em mobile.

- [ ] **Step 3: reconciliar fatos e limites**

Comparar as seis verdades em brief, Arcade, vídeos e infográfico. Qualquer divergência bloqueia a entrega; corrigir o derivado, nunca a fonte canônica.

Brief, README, roteiro do Arcade e fonte fechada do NotebookLM passaram pela reconciliação automatizada. O gate permanece aberto até revisar os outputs gerados.

- [ ] **Step 4: atualizar manifesto e diário**

Registrar URL, checksum, data, formato, status e limitação. Resumir a quantidade de ondas, decisões, passadas, fases, rodadas e testes. Atualizar a data real da submissão e o link do histórico para a branch final. Itens não produzidos não aparecem como entrega.

- [ ] **Step 5: consolidar a branch final sem enviar**

Fast-forward da branch local `submission/luis-roquette` para o commit integralmente validado e consolidar nela os Challenges 002, 003 e 004. O regulamento permite mais de um desafio, mas somente um PR por pessoa. Confirmar que `git diff --name-only upstream/main...submission/luis-roquette` contém exclusivamente `submissions/luis-roquette/`.

Auditoria remota de 22 de setembro de 2026: PRs #140 e #141 estão fechadas; a PR #145 está aberta na branch não canônica `submission/luis-roquette-004-social`. Antes do envio final, encerrar a PR #145 e publicar somente o Challenge 001 na branch canônica, sem manter dois PRs simultâneos.

- [ ] **Step 6: executar o gate formal do PR**

Validar README contra `templates/submission-template.md`, instruções de setup, solução, Process Log, data final, histórico Git e todos os links em sessão anônima. Executar o setup e o gate canônico do Challenge 001 no Codespace a partir do SHA final. O único PR para `upstream/main` usará o título `[Submission] Luis Fernando Roquette — Challenge 001`.

Conferir uma matriz final com: cinco tabelas cruzadas; causa ou abstenção justificada; segmentos e contas específicas; recomendações priorizadas com impacto estimado; correlação separada de causalidade; leitura executiva; solução funcional; Process Log com ferramentas, decomposição, erros, contribuição humana e contagem de iterações.

- [ ] **Step 7: parar antes do push final e do PR**

Somente declarar 100% quando conteúdo, mídia, branch, diff, setup e links estiverem verdes. Luis autorizou concluir e publicar após todos os gates objetivos passarem.

## Self-review

- Escopo reduzido para cinco entradas visíveis com funções distintas.
- Mapa mental e TXT foram removidos por redundância; Video Overview e infográfico foram mantidos por decisão de Luis.
- O vídeo obrigatório existente virou a peça central da construção.
- Arcade demonstra o produto; vídeo obrigatório explica arquitetura; NotebookLM sintetiza; brief responde; Process Log prova.
- Nenhum binário de 222 MiB entra no Git.
