# Challenge 001 Delivery Package Implementation Plan

> **Status:** substituído pelo plano enxuto `2026-09-22-lean-delivery-package.md` após a incorporação do vídeo obrigatório de arquitetura.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** produzir uma entrega multimodal do Challenge 001 que preserve uma única verdade verificável e evidencie o método autoral de construção.

**Architecture:** o PR permanece autoritativo. Uma narrativa canônica alimenta as versões `.txt`/`.docx`, o pacote de fontes do NotebookLM e o roteiro do Arcade; todos os derivados passam por reconciliação factual antes de entrar no manifesto final.

**Tech Stack:** Markdown, texto UTF-8, DOCX, NotebookLM Studio, Arcade Interactive Demo, Git/GitHub e dashboard Streamlit existente.

**Spec:** `.specs/tasks/todo/package-challenge-001-deliverables.feature.md`

## Global Constraints

- Nenhuma nova análise ou métrica será calculada.
- `ceo_answer.json` e os diários são as fontes factuais.
- Materiais públicos não contêm segredo, dado pessoal, caminho local ou cadeia de pensamento privada.
- NotebookLM e Arcade só recebem conteúdo público do desafio.
- Publicação externa exige confirmação final de Luis.
- Links externos complementam, mas nunca substituem, README, relatório e Process Log no PR.

## Review Focus

- Divergência numérica entre texto, vídeo, infográfico e dashboard.
- Linguagem visual transformando hipótese inconclusiva em causa.
- Tour longo demais e focado em features em vez da pergunta do CEO.
- Documento metodológico genérico, sem erros, decisões e evolução mensurável.
- Link externo privado, quebrado ou dependente de login do avaliador.

---

### Task 1: Congelar o contrato editorial e o inventário

**Files:**
- Create: `deliverables/delivery-manifest.md`
- Create: `deliverables/notebooklm/source-pack.md`
- Modify: `../../README.md`

**Interfaces:**
- Consumes: `artifacts/ceo_answer.json`, `artifacts/report.md`, `docs/executive-answer-rubric.md` e `process-log/000-004`.
- Produces: inventário de entregáveis e fonte factual única para todos os derivados.

- [ ] **Step 1: criar o manifesto com estado explícito**

Registrar cada arquivo, finalidade, fonte, formato, estado `draft|validated|published`, checksum e link quando existir. Nenhum item inexistente recebe link ou estado `validated`.

- [ ] **Step 2: montar o source pack sem recalcular números**

Copiar somente a pergunta do CEO, as seis verdades do contrato, a linha do tempo metodológica, decisões humanas, falhas/correções e limitações. Referenciar o arquivo canônico ao lado de cada seção.

- [ ] **Step 3: validar números e termos proibidos**

Run:

```bash
rg -n "12,4%|7,0 pp|1\.622\.337|0,336|0,493|0,349|0,304|3,96|4,02|4,50|3,67|Causa ainda não demonstrada" deliverables/notebooklm/source-pack.md
! rg -n "causa comprovada|receita recuperável garantida|mecanismo vencedor" deliverables/notebooklm/source-pack.md
```

Expected: todos os fatos presentes e nenhum overclaim.

- [ ] **Step 4: checkpoint**

```bash
git add -f deliverables/delivery-manifest.md deliverables/notebooklm/source-pack.md ../../README.md
git commit -m "docs(churn): define final delivery contract"
```

### Task 2: Escrever a narrativa canônica da construção

**Files:**
- Create: `deliverables/construction-story.md`
- Generate: `deliverables/construction-story.txt`
- Generate: `deliverables/construction-story.docx`

**Interfaces:**
- Consumes: source pack e quatro diários contemporâneos.
- Produces: conteúdo humano/IA semanticamente equivalente em três formatos.

- [ ] **Step 1: escrever a versão Markdown em seis atos**

Usar: problema; método autoral; descoberta socrática; construção por feedback; viradas decisivas; resultado e limites. Limite recomendado: 2.000–3.000 palavras, com uma tabela de evolução `7,0 → 8,6 → 9,5 → 9,9`.

- [ ] **Step 2: selecionar prompts decisivos**

Incluir apenas 6–8 fragmentos curtos, corrigidos ortograficamente e marcados como contribuição de Luis. Para cada fragmento, registrar `intenção → mudança provocada → evidência`.

- [ ] **Step 3: gerar TXT e DOCX a partir do Markdown**

Usar a skill `documents` para o DOCX. O TXT remove somente marcação, nunca conteúdo. Não manter três fontes editáveis independentes.

- [ ] **Step 4: reconciliar os três formatos**

Extrair o texto do DOCX e comparar títulos, números e conclusão com o Markdown. Expected: zero divergência substantiva; diferenças apenas de formatação.

- [ ] **Step 5: checkpoint**

```bash
git add -f deliverables/construction-story.md deliverables/construction-story.txt deliverables/construction-story.docx
git commit -m "docs(churn): package construction narrative"
```

### Task 3: Criar o sistema visual da evolução

**Files:**
- Create: `deliverables/notebooklm/generation-prompts.md`
- Receive: `deliverables/visuals/method-mind-map.png`
- Receive: `deliverables/visuals/method-evolution-infographic.png`

**Interfaces:**
- Consumes: `construction-story.md` e `source-pack.md` no NotebookLM.
- Produces: mapa mental e infográfico derivados, factualmente reconciliados.

- [ ] **Step 1: preparar o prompt do mapa mental**

```text
Crie um mapa mental em português brasileiro com o nó central “Método de Construção AI Master — Luis Roquette”. Ramifique em: pesquisa e absorção; cinco ondas socráticas; SDD e SPEC; lapidação; feedback looping; redundância necessária; resposta ao CEO; auditoria. Em cada ramo, mostre decisão, evidência e efeito. Não invente etapas nem números.
```

- [ ] **Step 2: preparar o prompt do infográfico**

```text
Crie um infográfico vertical, executivo e legível, intitulado “De uma pergunta confusa a uma decisão confiável”. Mostre oito etapas cronológicas e a evolução 7,0 → 8,6 → 9,5 → 9,9. Destaque três viradas: separar agregados de coortes; recusar causalidade frágil; transformar incerteza em plano de validação. Use somente números das fontes.
```

- [ ] **Step 3: gerar no NotebookLM**

Enviar somente fontes públicas selecionadas. Registrar nome do notebook, data, arquivos usados, prompt e formato exportado. Não aceitar geração sem export ou link verificável.

- [ ] **Step 4: executar revisão factual visual**

Checklist: oito etapas; quatro notas; nenhuma causa provada; nenhum número novo; texto legível; crédito a Luis. Se qualquer item falhar, regenerar antes de avançar.

- [ ] **Step 5: checkpoint**

```bash
git add -f deliverables/notebooklm/generation-prompts.md deliverables/visuals
git commit -m "docs(churn): add methodology visual assets"
```

### Task 4: Produzir o Video Overview no NotebookLM

**Files:**
- Receive: `deliverables/video/construction-overview.mp4`
- Create: `deliverables/video/README.md`

**Interfaces:**
- Consumes: as mesmas fontes aprovadas na Task 3.
- Produces: vídeo de 5–8 minutos, registro de geração e link/arquivo acessível.

- [ ] **Step 1: usar steering prompt executivo**

```text
Crie um Video Overview em português brasileiro para avaliadores do processo seletivo de AI Master. Conte a construção, não uma lista de features. Abra com a pergunta do CEO; explique a metodologia autoral; mostre três correções em que julgamento humano mudou o resultado; apresente a resposta final e encerre com as três ações. Duração alvo: 5–8 minutos. Não declare causalidade nem nota externa garantida.
```

- [ ] **Step 2: gerar e registrar proveniência**

Salvar duração, idioma, fontes, prompt, data e URL/arquivo. Se o recurso estiver limitado pela conta, registrar o bloqueio e preservar o roteiro sem alegar vídeo concluído.

- [ ] **Step 3: revisar o vídeo completo**

Conferir números, pronúncia, ritmo, autoria, ausência de overclaim e qualidade visual. Anotar timestamps dos seis fatos do contrato.

- [ ] **Step 4: checkpoint**

```bash
git add -f deliverables/video
git commit -m "docs(churn): add grounded construction video"
```

### Task 5: Construir o wizard interativo no Arcade

**Files:**
- Create: `deliverables/arcade/arcade-script.md`
- Create: `deliverables/arcade/README.md`

**Interfaces:**
- Consumes: dashboard local validado em `127.0.0.1:8503` e contrato editorial.
- Produces: demo interativa de 10 passos e registro do link/configuração.

- [ ] **Step 1: roteirizar exatamente 10 passos**

1. Pergunta do CEO.
2. Churn: 12,4% e +7,0 pp.
3. Impacto: US$ 1.622.337 observado.
4. Produto: agregado sobe, coorte de churn cai.
5. CS: satisfação cobre respondentes e piora na coorte.
6. Segmentos: nenhuma concentração material.
7. Causalidade: causa ainda não demonstrada.
8. Plano: Dados, Produto e CS com prazos.
9. Evidências: rastreabilidade e `analysis_id`.
10. Encerramento: decisão e acesso ao Process Log.

- [ ] **Step 2: escrever callouts curtos**

Cada hotspot deve ter até 60 caracteres e cada instrução até 30 palavras. O primeiro valor aparece antes do passo 3; nenhuma tela explica mais de uma ideia.

- [ ] **Step 3: capturar o dashboard local**

Usar dados sintéticos, ocultar barra do navegador, notificações e caminhos locais. Misturar screenshots com no máximo dois trechos curtos de vídeo somente onde a interação melhora compreensão.

- [ ] **Step 4: revisar o rascunho antes de publicar**

Verificar desktop/mobile, ordem dos 10 passos, números, links, acesso anônimo e ausência de dados sensíveis. Parar antes do compartilhamento público e solicitar confirmação final de Luis.

- [ ] **Step 5: registrar e versionar**

Depois da confirmação, salvar URL, data, acesso e screenshots de abertura/encerramento no README do Arcade.

### Task 6: Fechar o pacote e o Pull Request

**Files:**
- Modify: `deliverables/delivery-manifest.md`
- Modify: `../../README.md`
- Modify: `../../process-log/004-planejamento-entregaveis.md`

**Interfaces:**
- Consumes: todos os entregáveis validados.
- Produces: índice final navegável e evidência de qualidade.

- [ ] **Step 1: validar arquivos e links**

Run:

```bash
find deliverables -type f -empty -print
rg -n "draft|provisório|pendente" deliverables ../../README.md
```

Expected: nenhum arquivo vazio; nenhum estado provisório em item declarado final.

- [ ] **Step 2: revisão cruzada de conteúdo**

Conferir os seis fatos, a metodologia em oito etapas, limitações, autoria e ausência de segredo em cada formato. O vídeo e o Arcade são assistidos do início ao fim.

- [ ] **Step 3: atualizar o README de submissão**

Ordenar links por tempo do avaliador: resposta executiva; Arcade; documento; vídeo; infográfico/mapa; Process Log; reprodução técnica.

- [ ] **Step 4: atualizar manifesto e diário**

Marcar somente itens comprovados como `validated` ou `published`, registrar URLs, checksums, datas, limitações e decisões humanas.

- [ ] **Step 5: preparar PR sem enviar automaticamente**

Montar descrição curta com resposta, entregáveis, reprodução e Process Log. Revisar links pelo GitHub renderizado; submissão ao upstream continua uma ação externa sujeita à confirmação de Luis.

## Self-review

- Cobertura: documento, formatos para IA, infográfico, mapa, vídeo, Arcade, manifesto e PR estão mapeados.
- Autoridade: nenhum derivado calcula ou substitui fatos canônicos.
- Custo: nenhuma nova biblioteca, site ou pipeline foi criado; usamos formatos e plataformas escolhidos por Luis.
- Risco principal: divergência entre mídias geradas por IA; mitigado por source pack único e revisão factual completa.
- Publicação: geração pode ser automatizada dentro do escopo, mas links públicos e PR upstream aguardam confirmação final.
