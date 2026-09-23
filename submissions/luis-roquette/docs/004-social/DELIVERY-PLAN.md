# Plano de entrega — Challenge 004

> **Para Luis:** executar em fases, seguindo `Planejamento → Revisão → Execução → Teste`; uma fase só avança depois de validada.

**Goal:** transformar a solução técnica e o diário já existentes em uma entrega executiva que um avaliador compreenda em até cinco minutos e possa aprofundar sem perder rastreabilidade.

**Architecture:** uma única narrativa canônica alimentará todos os formatos. O `README.md` da submissão será o índice; o Arcade demonstrará o produto; o estudo de caso explicará a construção; o NotebookLM produzirá vídeo, mapa mental e infográfico a partir das mesmas fontes verificadas. Não haverá uma narrativa concorrente por mídia.

**Tech Stack:** Markdown como fonte canônica; Pandoc ou conversor documental já disponível para DOCX/TXT; Arcade para demonstração interativa; NotebookLM para Video Overview, Mind Map e Infographic; Git/GitHub para versionamento e PR.

**Spec:** `submissions/luis-roquette/solution/004-social/SPEC.md`

**Global Constraints:** alterar somente `submissions/luis-roquette/`; não versionar o CSV bruto; não expor caminhos locais, segredos ou dados pessoais; não transformar associação em causalidade ou ROI; manter HR-01 e preflight como pendências explícitas até validação real; todos os números devem apontar para `analysis.md` ou `evidence.csv`; links externos devem abrir em janela anônima; nenhum artefato pode contradizer o método `2.5.0`; nenhuma assinatura ou upgrade pago será acionado sem autorização explícita.

**Review Focus:** clareza executiva em cinco minutos; fidelidade entre formatos; contribuição humana visível; evolução prompt → decisão → produto; evidência verificável; ausência de duplicação e de alegações infladas.

---

## Decisão de embalagem

Entregar um percurso com duas velocidades:

1. **Rota rápida, 3–5 minutos:** `README.md` → três respostas → Arcade → decisão para segunda-feira.
2. **Rota de aprofundamento:** estudo de caso → infográfico/mapa mental → vídeo → SPEC, diário, análise e evidências.

O item visual proposto não será um quarto relato independente. Ele será a representação gráfica da mesma jornada documentada no estudo de caso. O Arcade explicará **como usar o sistema**; o vídeo do NotebookLM explicará **como o sistema foi construído**.

## Estrutura final

```text
submissions/luis-roquette/
├── README.md
├── docs/004-social/
│   ├── DELIVERY-PLAN.md
│   ├── CONSTRUCTION-STORY.md
│   ├── CONSTRUCTION-STORY.docx
│   ├── CONSTRUCTION-STORY.txt
│   ├── PRODUCTION-BRIEF.md
│   ├── DELIVERY-MANIFEST.md
│   └── assets/
│       ├── methodology-evolution.png
│       ├── notebooklm-mind-map.png
│       ├── notebooklm-infographic.png
│       └── notebooklm-video.mp4
├── process-log/004-social.md
└── solution/004-social/
    ├── README.md
    ├── analysis.md
    ├── evidence.csv
    └── SPEC.md
```

`DELIVERY-MANIFEST.md` só será criado quando URLs e arquivos finais existirem; assim, a submissão não carregará links fictícios.

---

### Task 1: Criar a narrativa canônica e o índice do avaliador

**Files:**

- Create: `submissions/luis-roquette/docs/004-social/CONSTRUCTION-STORY.md`
- Modify: `submissions/luis-roquette/README.md`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Planejamento:** estruturar o estudo de caso em oito blocos curtos: desafio; premissas; pesquisa; ondas socráticas; SDD/SPEC; feedback loops; erros e correções; resultado e limites. Cada bloco deve ligar intenção, decisão humana, ação da IA, evidência e efeito no produto.

**Revisão:** confrontar cada afirmação com o diário, Git e artefatos atuais. Remover cronologia reconstruída, superlativos sem prova e detalhes que não alteram a compreensão do avaliador.

**Execução:** escrever `CONSTRUCTION-STORY.md` como fonte única. Atualizar o `README.md` para abrir com três respostas do desafio e oferecer somente dois caminhos: “ver a solução” e “entender a construção”.

**Teste:** leitura cronometrada por Luis ou avaliador designado. Em até cinco minutos, a pessoa deve conseguir dizer: o que gera engajamento, quando patrocinar, qual é a estratégia de 30 dias, qual foi a contribuição humana e onde está a evidência.

**Aceite:** zero números sem fonte; zero divergências com método 2.5.0; jornada proprietária compreensível sem ler o diário integral.

**Estimativa:** 90–120 minutos.

---

### Task 2: Gerar texto, DOCX e Markdown sem divergência

**Files:**

- Source: `submissions/luis-roquette/docs/004-social/CONSTRUCTION-STORY.md`
- Create: `submissions/luis-roquette/docs/004-social/CONSTRUCTION-STORY.docx`
- Create: `submissions/luis-roquette/docs/004-social/CONSTRUCTION-STORY.txt`
- Create: `submissions/luis-roquette/docs/004-social/PRODUCTION-BRIEF.md`

**Planejamento:** usar o Markdown como única fonte editável. DOCX e TXT serão derivados, nunca mantidos manualmente.

**Revisão:** definir antes da conversão títulos, ordem, legendas, links e texto alternativo. Registrar no `PRODUCTION-BRIEF.md` os comandos de geração e a checklist de paridade.

**Execução:** gerar DOCX e TXT. O DOCX deve ter capa curta, sumário, hierarquia visual, tabelas legíveis e links clicáveis; o TXT deve preservar títulos, evidências e URLs em texto simples.

**Teste:** comparar automaticamente títulos e contagens principais entre os três formatos; abrir o DOCX no Microsoft Word ou LibreOffice; verificar paginação, tabelas, hyperlinks e ausência de conteúdo cortado.

**Aceite:** paridade semântica entre MD/DOCX/TXT; nenhum ajuste manual exclusivo no DOCX; arquivos abrem sem alerta de reparo.

**Estimativa:** 35–50 minutos.

---

### Task 3: Produzir a linha do tempo visual “prompt → produto”

**Files:**

- Modify: `submissions/luis-roquette/docs/004-social/PRODUCTION-BRIEF.md`
- Create: `submissions/luis-roquette/docs/004-social/assets/methodology-evolution.png`

**Planejamento:** selecionar de seis a oito marcos, não despejar a conversa completa. Sequência obrigatória: absorção iterativa; pesquisa; ondas socráticas; SDD/SPEC; lapidação; feedback looping; redundância necessária; refinamento executivo 2.5.

**Revisão:** para cada marco, registrar um fragmento de prompt, a decisão de Luis, a mudança concreta e a evidência correspondente. Redigir os prompts sem corrigir retroativamente o conteúdo histórico; apenas corrigir ortografia em legendas explicativas.

**Execução:** criar uma linha do tempo horizontal ou vertical, legível em desktop e A4, com no máximo duas frases por marco. O visual deve mostrar causa e efeito, não apenas datas.

**Teste:** abrir em 100% e em largura móvel; validar contraste, ortografia e legibilidade. Confirmar que cada marco existe no diário e que nenhum segredo, caminho local ou transcrição excessiva foi exposto.

**Aceite:** o avaliador entende em até 90 segundos como a metodologia mudou o produto; todos os marcos são rastreáveis.

**Estimativa:** 60–90 minutos.

---

### Task 4: Gravar o wizard guiado no Arcade

**Files:**

- Modify: `submissions/luis-roquette/docs/004-social/PRODUCTION-BRIEF.md`
- Modify after publication: `submissions/luis-roquette/README.md`

**Planejamento:** confirmar primeiro que a conta disponível permite captura, publicação e compartilhamento público sem compra. Congelar depois o conteúdo da interface. Roteiro de sete cenas: contexto; upload; três respostas executivas; driver multivariado; regra de patrocínio; estratégia de 30 dias; evidência/decisão/exportação.

**Revisão:** cada cena terá uma ação, um callout e uma conclusão. Remover navegação sem valor, esperas, detalhes internos e qualquer fluxo que dependa do CSV privado do avaliador.

**Execução:** capturar a aplicação real com dados permitidos, aplicar blur quando necessário, organizar capítulos e publicar um link público. Alvo: 2–3 minutos, com navegação no ritmo do avaliador.

**Teste:** abrir o link em janela anônima e em viewport móvel; percorrer todos os hotspots; confirmar texto, sequência, CTA final e ausência de bloqueio por login. Registrar tempo, conclusão e URL real no manifesto.

**Aceite:** primeira resposta aparece em até 30 segundos; as três perguntas do Head ficam respondidas; 100% dos hotspots funcionam; nenhuma informação sensível aparece.

**Estimativa:** 45–75 minutos.

---

### Task 5: Gerar NotebookLM, montar o manifesto e fechar a entrega

**Files:**

- Source: `submissions/luis-roquette/docs/004-social/CONSTRUCTION-STORY.md`
- Source: `submissions/luis-roquette/solution/004-social/analysis.md`
- Source: `submissions/luis-roquette/solution/004-social/SPEC.md`
- Source: `submissions/luis-roquette/solution/004-social/README.md`
- Create: `submissions/luis-roquette/docs/004-social/assets/notebooklm-mind-map.png`
- Create: `submissions/luis-roquette/docs/004-social/assets/notebooklm-infographic.png`
- Create: `submissions/luis-roquette/docs/004-social/DELIVERY-MANIFEST.md`
- Modify: `submissions/luis-roquette/README.md`
- Modify: `submissions/luis-roquette/process-log/004-social.md`

**Planejamento:** confirmar primeiro que Video Overview, Mind Map, Infographic e compartilhamento público estão habilitados na conta disponível. Criar então um notebook exclusivo da entrega com apenas as fontes canônicas. Não enviar o CSV bruto nem o diário integral; o estudo de caso já contém a seleção documentada. Pedir um vídeo de 4–6 minutos para avaliadores não técnicos, um mapa mental da arquitetura metodológica e um infográfico executivo da evolução. Se uma capacidade estiver indisponível, registrar o bloqueio real antes de escolher substituto.

**Revisão:** verificar roteiro e peças contra as fontes antes de publicar. Corrigir qualquer número, causalidade indevida, promessa de ROI, nota autoatribuída ou afirmação de HR-01/preflight concluídos.

**Execução:** gerar e exportar vídeo, mapa mental e infográfico. Salvar as imagens no repositório; compartilhar o vídeo por URL pública verificada e arquivar o MP4 no repositório somente se o arquivo final tiver até 50 MB. Criar `DELIVERY-MANIFEST.md` com URL do Arcade, URL do vídeo/notebook, arquivos, duração, data de verificação e SHA-256 dos binários versionados. Como `submissions/` está no `.gitignore` do repositório-base, adicionar explicitamente somente os novos arquivos pretendidos com `git add -f`, sem incluir `.claude/`, `.specs/` ou `skills-lock.json`.

**Teste:** abrir todos os links em janela anônima; conferir áudio, legendas, imagens, nomes, números e duração; validar que o `README.md` chega a cada artefato em um clique. Executar o preflight obrigatório no Codespace sobre o diff exato antes do PR.

**Aceite:** nenhum link quebrado; vídeo entre 4 e 6 minutos; três imagens legíveis; MD/DOCX/TXT disponíveis; Arcade funcional; manifesto completo; preflight verde; PR pronto no formato exigido pelo repositório.

**Estimativa:** 90–135 minutos, além do tempo de geração do NotebookLM.

---

## Gate final de qualidade

| Critério | Prova exigida |
|---|---|
| Valor em 30 segundos | `README.md` apresenta as três respostas e o próximo passo |
| Produto em 3 minutos | Arcade conclui o roteiro sem login ou hotspot quebrado |
| Método em 6 minutos | vídeo explica decisões, erros, loops e contribuição humana |
| Rastreabilidade | toda alegação aponta para diário, análise, SPEC, evidência ou Git |
| Consistência | MD, DOCX, TXT, Arcade, vídeo e imagens não se contradizem |

O gate só fecha após duas passadas consecutivas sem correção relevante nos artefatos finais. Uma correção reinicia o contador. O PR só será aberto depois do preflight pesado no Codespace e da verificação anônima dos links públicos.

## Ordem crítica

`CONSTRUCTION-STORY.md` → `README.md` → DOCX/TXT → linha do tempo → Arcade → NotebookLM → manifesto → QA → preflight → PR.

**Tempo total estimado:** 5h20–7h50 de trabalho ativo, mais filas de geração e upload.

## Pesquisa de capacidade

- Arcade transforma a captura do produto em walkthrough interativo, oferece hotspots/callouts, capítulos, compartilhamento, incorporação e analytics: <https://docs.arcade.software/kb/build/interactive-demo>
- NotebookLM oferece Video Overviews e Mind Maps; sua evolução também inclui Infographics e artefatos documentais: <https://blog.google/innovation-and-ai/models-and-research/google-labs/notebooklm-video-overviews-studio-upgrades/> e <https://blog.google/innovation-and-ai/products/notebooklm/better-research-notebooklm/>
