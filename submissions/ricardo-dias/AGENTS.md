# Guia do projeto — Challenge 002 (Redesign de Suporte)

Arquivo lido pelo **Codex** (`AGENTS.md`) e pelo **Claude Code** (`CLAUDE.md` importa este arquivo).
Dois agentes trabalham **em paralelo na mesma branch**. Leia tudo antes de mexer em qualquer coisa.

## Missão
Processo seletivo "AI Master" do G4. O Diretor de Operações pediu três coisas: **onde perdemos tempo**, **o que automatizar com IA (e o que NÃO automatizar)** e **algo rodando**. A banca avalia:
- números concretos
- uso dos 2 datasets
- proposta realista (automatizar 100% conta como red flag)
- protótipo rodando com dados reais, não com exemplos escolhidos a dedo
- **evidência de que verificamos o que a IA disse**

Texto voltado ao usuário: **PT-BR**. Código e identificadores: inglês.

## Regras invioláveis
1. **Só altere arquivos dentro de `submissions/ricardo-dias/`.** PRs que tocam outros caminhos são rejeitados.
2. **Nunca invente número.** Todo número em UI ou docs precisa vir de `solution/app/data/*.json`, gerado pelos scripts de `solution/analysis/`. Se o JSON ainda não existir, use `solution/app/data/fixtures/` com os valores marcados como `FIXTURE` na tela.
3. **Nunca versione dados brutos.** Os CSVs ficam em `C:\Users\rsdias\g4\data\raw\`, fora do repositório.
4. **Nunca exponha nem commite segredos** (`.env*` está no `.gitignore`).
5. Premissas, como custo por hora de agente ou tempo de triagem, são **explícitas**: ficam em `assumptions` no JSON, com fonte, e são editáveis na UI.
6. Não faça push, deploy nem PR. Isso só acontece com confirmação do Ricardo.

## Fatos já verificados nos dados (não refaça, não contradiga)
**Dataset 1 — `customer_support_tickets.csv`: é sintético.**
- São 8.469 linhas, não ~30 mil.
- Tipo, prioridade, canal, status e CSAT têm distribuição uniforme (todos os p do qui-quadrado > 0,1).
- `First Response Time` e `Time to Resolution` são **timestamps**, não durações. Todos caem entre 31/05 e 02/06/2023. Não existe horário de abertura do ticket.
- Em 49% dos tickets fechados (1.365 de 2.769), a resolução é **anterior** à primeira resposta.
- Resolução, TTR e CSAT só existem para `Closed` (2.769). `Open` (2.819) não tem FRT. `Pending Customer Response` tem 2.881.
- **Não detectamos associação** entre CSAT e tipo, prioridade, canal, gênero, produto, idade ou "duração" nos testes realizados (Kruskal-Wallis e Spearman, todos com p > 0,25). Diferenças de até ~±0,15 ponto não seriam detectáveis. Nunca escreva "não há efeito" ou "nenhuma variável explica".
- Status também não varia de forma detectável por canal, prioridade ou tipo (qui-quadrado, p ≥ 0,23).
- `Ticket Subject` é independente de `Ticket Type` (p = 0,98).
- `Ticket Description` contém o placeholder `{product_purchased}` em 100% dos tickets. `Resolution` é texto aleatório (Faker).
- TF-IDF + regressão logística em Pipeline (vetorizador ajustado dentro de cada fold) prevê o tipo no nível do acaso: 18,7% contra 20,7% da classe majoritária.

**O que isso significa:** o D1 não permite afirmar causa de atraso nem driver de CSAT. Backlog e pendências são **contagens descritivas do arquivo**, não evidência de gargalo. O diagnóstico separa observado, limitação e cenário estimado, e entrega **a metodologia pronta para dados reais**. Esse é o diferencial da entrega, não um defeito a esconder.

**Dataset 2 — `all_tickets_processed_improved_v3.csv`: é bom para classificação.**
- 47.837 linhas, 8 classes: Hardware 13.617, HR Support 10.915, Access 7.125, Miscellaneous 7.060, Storage 2.777, Purchase 2.464, Internal Project 2.119, Administrative rights 1.760.
- 0 duplicatas e 0 rótulos conflitantes.
- O texto já vem parcialmente pré-processado: minúsculas, sem dígitos, anonimizado, **com stopwords** (21,6% dos tokens). Mediana de 26 palavras.
- **Consequência para a UI:** textos colados pelo usuário precisam passar pela mesma normalização. Ela fica em `lib/classifier.ts`.

**Modelo e roteamento: protocolo e resultados** (fonte: `model_metrics.json` e `routing_eval.json`; não copie números daqui para a UI)
- Partições estratificadas: treino 33.485 / validação 7.176 / teste 7.176. **Tudo** é escolhido na validação e congelado antes do teste.
- Os números da primeira versão (86,4% / 69,7% automáticos / 95,7%) são **exploratórios**, porque foram medidos no mesmo conjunto usado para ajustes. Não publicar como resultado.
- Teste: acurácia 86,0% (IC 85,2–86,7%). Com a política completa da API, 65,3% automático com 94,9% de acerto, 28,1% revisão humana e 6,5% escalação. Vazamento de pedidos de privilégio: 5 de 264.
- Os números de roteamento publicados vêm de `scripts/evaluate-routing.ts`, que usa as funções da API. A réplica Python (`analysis/policy.py`) serve só para a seleção, e as duas concordam 100%.
- Fora do domínio (Dataset 1), o modelo erra com convicção. O guarda de vocabulário barra quase todo o Dataset 1.
- `model.json` é **versão 2**, validado ao carregar (`lib/model-schema.ts`). As regras de política ficam em `lib/policy-rules.json`, lido por TS e Python.

## Estrutura
```
submissions/ricardo-dias/
├── AGENTS.md / CLAUDE.md      ← este guia
├── HANDOFF.md                 ← quadro de coordenação entre agentes (leia e atualize)
├── README.md                  ← submissão final (template do G4)
├── docs/                      ← diagnostico.md, automacao.md, modelo.md
├── process-log/               ← PROCESS_LOG.md, transcripts, screenshots
└── solution/
    ├── analysis/              ← Python (uv): 01_audit.py, 02_diagnostico.py, 03_classifier.py, 04_llm_fallback.py
    └── app/                   ← Next.js 16 (App Router) + Tailwind 4 + AI SDK v7
        ├── lib/types.ts       ← CONTRATOS de dados (dono: Claude)
        ├── lib/classifier.ts  ← inferência TS do modelo exportado (dono: Claude)
        ├── data/*.json        ← gerado pela análise (dono: Claude; não editar à mão)
        ├── data/fixtures/     ← mocks no formato de types.ts (dono: Codex)
        ├── app/api/**         ← rotas: classify, sample, draft (dono: Claude)
        ├── app/(pages)        ← /, /triagem, /modelo, /proposta (dono: Codex)
        └── components/**      ← UI (dono: Codex)
```

## Divisão de trabalho (lanes). Não edite arquivos da lane do outro.
| Lane | Dono | Caminhos |
|---|---|---|
| Análise, modelo, números | **Claude Code** | `solution/analysis/**`, `solution/pipeline.sh`, `solution/app/data/*.json`, `solution/app/lib/{types,classifier,model-schema,policy-rules.json,validation,draft,server-data,waste,routing-eval,eval-data}.ts`, `solution/app/app/api/**`, `solution/app/scripts/**`, `solution/app/tests/**`, `docs/templates/**` (os `docs/*.md` são gerados) |
| Interface e experiência | **Codex** | `solution/app/app/**` (exceto `api/`), `solution/app/components/**`, `solution/app/lib/data.ts`, `solution/app/data/fixtures/**`, estilos, `solution/app/public/**` |
| Compartilhado (edição curta, com commit imediato) | ambos | `solution/app/package.json` (só adicionar dependência), `HANDOFF.md`, `process-log/PROCESS_LOG.md` (só acrescentar entradas no fim) |
| Ricardo decide | humano | `README.md` final, conteúdo de `docs/templates/automacao.md.tmpl` (o Claude rascunha, o Ricardo revisa), deploy, PR |

Se precisar de algo da lane do outro (um campo novo no JSON, mudança de contrato), **escreva o pedido no `HANDOFF.md`** em vez de editar.

## Backlog do Codex (em ordem)
1. **Layout e navegação:** header com as 4 páginas (Diagnóstico, Triagem, Modelo, Proposta). Visual sóbrio de ferramenta interna, legível para diretor não técnico. Mobile ok.
2. **Fixtures:** criar `data/fixtures/{audit,diagnostico,model_metrics}.json` seguindo `lib/types.ts`, com valores plausíveis marcados como fixture. Um helper `lib/data.ts` carrega o JSON real se existir e cai na fixture se não existir (aceitável na lane do Codex).
3. **`/` Diagnóstico:**
   - faixa "Antes de ler os números" com os achados da auditoria (`audit.json`, severidade bloqueante primeiro)
   - `observations` (descritivas, rotuladas como tal)
   - heatmap canal × prioridade (`backlogShare` com `backlogCI`), acompanhado da conclusão de `segmentTests`
   - `csatDrivers` mostrando `conclusion` (já redigida: "não detectamos associação...")
   - `limitations` visíveis
   - calculadora de desperdício com inputs nas `assumptions` editáveis e recálculo no cliente
4. **`/triagem` (protótipo):**
   - textarea + exemplos aleatórios vindos de `GET /api/sample`
   - `POST /api/classify` mostrando categoria, barra de confiança, probabilidades, termos que explicam, badge de rota (auto / revisão humana / escalar) com o motivo e tickets similares
   - botão "Gerar rascunho" que faz streaming de `POST /api/draft`, sempre rotulado "rascunho: agente revisa antes de enviar"
   - botão **"Testar em 200 tickets aleatórios"**: busca a amostra, classifica em lote e mostra a acurácia ao vivo, com a quantidade de tickets que foram para a fila humana
5. **`/modelo`:** partições e finalidade, seleção (validação), métricas de teste com IC, F1 por classe, matriz de confusão, roteamento por destino, motivo e categoria (`routing_eval.test`), vazamento de privilégio, guarda de domínio e o bloco "exploratório" rotulado como histórico.
6. **`/proposta`:** diagrama do fluxo (ticket entra → escalação? → classificação → guarda → confiança → privilégio → automático/humano → rascunho revisado → feedback), tabela "automatizar × manter humano" e ROI (`diagnostico.json → scenario`). O texto de referência está em `docs/automacao.md`.

Até as rotas da API existirem, a UI deve tratar erro e carregamento sem quebrar.

## Comandos
```bash
# App
cd solution/app && npm run dev        # http://localhost:3000
cd solution/app && npm test && npm run lint && npm run build

# Pipeline completo (análise → avaliação do roteamento → diagnóstico → docs → testes)
bash solution/pipeline.sh
```
**Next.js 16 tem breaking changes.** Leia `solution/app/node_modules/next/dist/docs/` antes de usar uma API de que não tenha certeza (veja também `solution/app/AGENTS.md`). O AI SDK está na **v7**: confira a API instalada em `node_modules/ai`, não confie na memória.

## Git (mesma branch, dois agentes)
- Branch: `submission/ricardo-dias`. **Nunca** rode `git add -A`, `git add .`, `reset --hard`, `rebase`, `commit --amend` ou force push.
- ⚠️ **O `.gitignore` da raiz do repositório ignora `submissions/`**, e não podemos alterá-lo (regra do PR). Por isso `git add` comum não faz nada, e `git add -f <pasta>` levaria `node_modules` e `.env` junto. **Sempre stageie com o script:**
  ```bash
  bash submissions/ricardo-dias/scripts/git-add.sh <caminhos da sua lane...>
  ```
  O script aplica `submissions/ricardo-dias/.gitignore` e recusa caminhos fora da submissão. Arquivos já rastreados funcionam normalmente.
- Commite só os arquivos da sua lane, listando os caminhos explicitamente.
- Commits pequenos, com prefixo do agente: `[claude] ...` ou `[codex] ...`. O histórico é evidência do processo.
- Antes de commitar, rode `git status` para ver se o outro agente deixou mudanças não commitadas. Não mexa nelas.

## Process log (obrigatório para a submissão)
Ao terminar uma tarefa relevante, acrescente no fim de `process-log/PROCESS_LOG.md`:
```
### [codex|claude] AAAA-MM-DD HH:MM — título
- O que foi pedido / feito
- Onde a IA errou ou precisou de correção (se houve)
- Decisão tomada e por quê
```
Seja honesto: erros encontrados e corrigidos valem mais que um log perfeito.
