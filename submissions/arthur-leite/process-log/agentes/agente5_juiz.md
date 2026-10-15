# Agente 5: juiz da execução dos agentes 1–4 e da entrega final

_Postura adversarial e independente. Somente leitura no projeto (o único arquivo gravado é este). Data: 2026-10-15. Estado avaliado: branch `submission/arthur-leite`, HEAD `74a6dd8` (1 commit à frente de `origin`, não enviado). Nenhuma API de LLM foi chamada; `GEMINI_API_KEY` foi removida do ambiente em todos os testes do app._

---

## 0. Veredito

**A entrega ainda NÃO está pronta para o PR, mas fica pronta com cerca de 30 a 45 minutos de correções.** Recalculei os números do app, do README, da proposta e do relatório, e eles batem com os outputs oficiais. O app roda sem exceções com pandas 2.2.3 e com pandas 3.0.6. O que bloqueia o PR não é número. São quatro coisas: (1) a honestidade da atribuição, que ainda se contradiz dentro do próprio README; (2) as imagens de processo 10–15, que têm citações entre aspas que não são literais, fontes que não contêm o trecho citado e não estão referenciadas em lugar nenhum; (3) o placeholder `{{DATA}}`; (4) o estado do git e do deploy (a imagem 15 e este relatório estão ignorados pelo `.gitignore`, `74a6dd8` não foi enviado e o app publicado ainda roda a versão antiga).

| Agente | Nota (0–10) | Justificativa |
|---|---|---|
| 1 · Designer UI/UX | **7,5** | Cumpriu o pedido: o painel abre respondendo às 3 perguntas na ordem pedida, a triagem nunca abre vazia e os números são recalculados (não digitados). Testou nos 2 ambientes. Perde pontos por erros de narrativa que um Diretor percebe: o exemplo "Aprovação de compra" aparece na seção "Prova" como **Sugestão → Miscellaneous**; "travas de **segurança**" no lugar de "de domínio"; um título de gráfico que afirma mais que a evidência; o cartão "Funciona? **Sim**" sem a ressalva de domínio. Os screenshots do produto não foram refeitos e o script de teste dos "33 números" não foi salvo |
| 2 · Auditoria de dados | **9,0** | O melhor trabalho do time. Recalculou do zero com código próprio, reproduziu os scripts byte a byte e achou problemas reais que três juízes anteriores não pegaram (assinatura "administrator", desempate do kNN, id truncado, índice × linha do CSV, trava possivelmente calibrada no teste). Desconto: um erro de digitação no SHA-256 abreviado do DS1 (o sufixo "…9dd4d4" é do DS2; o hash completo está certo). A recomendação de tirar "administrator" da regra resolveu a inflação, mas **piorou a cobertura** que ele mesmo tinha apontado, e isso não foi antecipado |
| 3 · Conformidade | **8,0** | Matriz completa (README raiz, CONTRIBUTING, guia, template, enunciado, vaga) com texto de correção pronto. Identificou o risco nº 1 (atribuição). Desconto: algumas recomendações empurram para alongar a entrega (G7, G10), contra o próprio alerta de concisão, e a tabela sugerida tinha células a verificar que o orquestrador acabou preenchendo com afirmações sem evidência no repositório |
| 4 · Ocultos | **6,5** | Achados de alto valor: rubrica real (Uso de IA = 30%), exigência de evidência visual do processo, inscrição obrigatória no ATS e `.gitignore` raiz ignorando `submissions/`. **Desconto principal: a leitura da página da vaga usando a chave "anon" extraída do bundle JS do ATS do próprio empregador** (ver §1.4). Também não alertou que as "imagens do processo" que recomendou precisariam ser capturas ou citações literais rastreáveis |
| Orquestrador (aplicação das correções) | **7,0** | Aplicou corretamente a maioria das correções (política v2, kNN 76,0%, IC por categoria, sensibilidade da trava, h/mês, maior desperdício recuperável, ponte para as filas do Diretor, operação contínua, errata, "Quem fez o quê"). Deixou passar: `{{DATA}}`; "inventou um id" no README; contradições de atribuição em Abordagem/Workflow; imagens com citações não literais e fontes erradas; imagens não referenciadas; ruído de rótulo sem ressalva no relatório e no app; cobertura da regra de privilégio não declarada |

---

## 1. Avaliação de cada agente

### 1.1 Agente 1 (designer UI/UX)

**Cumpriu o pedido?** Sim, no essencial.
- A 1ª aba abre em "Resposta ao Diretor", com hero, "Decisão pedida" e 4 cartões (3 perguntas + "Quanto vale?").
- Seguem as 5 seções na ordem Diagnóstico → O que automatizar/não → Prova → Quanto vale → Decisões.
- A triagem ao vivo abre preenchida com "Hardware rotineiro". Testei texto vazio: aparece a orientação em vez da tela vazia.
- Restrição "não comprometer nenhum dado": **respeitada**. Ele não alterou `triagem.py`, `politica.py`, `roi.py`, os scripts nem os outputs (`git show 74a6dd8 --stat`: só `app.py`, `src/painel.py` e o relatório dele). `painel.py` reimplementa cálculos (permutação com `bincount`), e eu confirmei que os resultados são iguais aos oficiais (§2.2).

**Erros e exageros (no app final):**
1. **Seção 3 "Mostre que funciona":** o ticket "Please approve the purchase order for 3 new docking stations…" sai como **"Sugestão → Miscellaneous"**. Para um leigo, a "prova" mostra a IA mandando um pedido de compra para "Diversos". Ele escolheu o exemplo para ilustrar a faixa de sugestão, mas o efeito narrativo é negativo.
2. `app.py:199`: "inclui 9,7% barrados pelas **travas de segurança**". As travas são **de domínio**. "Segurança" é outra coisa no mesmo painel (a regra de phishing).
3. `app.py:211`: o título "Cada categoria só é automatizada acima de 95% de acerto" afirma uma garantia do mecanismo. Na verdade, só Hardware e Miscellaneous têm limiar próprio; as demais usam o global. O 95% é uma estimativa pontual no teste: Hardware tem IC de 94,0 a 96,2%, e Administrative rights, de 92,5 a 98,9%. O mesmo vale para `app.py:194` ("só decide sozinho quando a precisão medida é de pelo menos 95%", que foi medida na **validação**).
4. `app.py:146`: o cartão "3 · Funciona? **Sim**" não tem a ressalva de que a prova é em tickets de TI. Na operação do Diretor, o modelo só funciona depois de retreinar e passar pelo modo sombra. A ponte que está na proposta ("Da prova à operação do Diretor") não aparece no painel.
5. Números fixos no código que poderiam sair de cálculo: a frase "Todas as 8 categorias ficam em 95% ou mais" (`app.py:202`) e o IC "95,9% a 96,8%", "p = 0,80", "V = 0,021", "16 frases-modelo" e McNemar (aba Metodologia). Hoje estão corretos. `BENCHMARK_LLM` é fixo por bons motivos (cota de API) e está documentado.
6. `src/painel.py:9`: a docstring ainda diz "politica.py (docstring: 27,7%)". O valor certo é 23,4%.
7. "Confiança do modelo: **100%**" (arredondamento de 99,6% com 0 casas) dá uma impressão de certeza absoluta.
8. Lacunas: os 5 screenshots do produto (01–05) mostram a interface antiga, e o modo escuro não foi inspecionado (ele declara isso). O teste "confere 33 números-chave" não foi salvo no repositório, então não é reproduzível.

**O storytelling faz sentido?** Sim. A pirâmide invertida funciona, e a ordem pergunta → resposta → prova → valor → decisão é a certa para um C-level. Um leigo entende as 3 respostas na 1ª dobra. Os pontos 1, 2 e 4 acima são os que mais atrapalham a leitura.

### 1.2 Agente 2 (auditoria de dados)

**Rigor:** alto. Fiz recálculos próprios para conferir parte do trabalho dele:
- Política v2 no DS2: 0,71 / 1,95 / 1,99 / 10,42 / 3,46 / 7,70%; 23,42% no total; 2,66% bloqueiam o rascunho; 8,11% escalam.
- No teste: 23,41% / 2,75% / 7,88%.
- Faixas: 65,51% · 96,38% · 99,38% / 23,27% · 63,43% · 90,97% / 11,22% · 72,44% · 90,22%; humano = 928 pela trava + 146 por confiança.
- ROI: 552 / 1.218 / 2.106 h; 46,0 / 101,5 / 175,5 h/mês; R$ 3.880/mês.
- O SHA-256 completo do DS1 confere.

**Erros dele:** o hash abreviado do DS1 tem o sufixo do DS2 (cosmético). Em 4.2, recomendou tirar "administrator" da regra e também medir a cobertura por categoria. A 1ª parte foi feita, e a cobertura caiu de 4,5% para **1,5%** dos tickets "Administrative rights" (ver o item não aplicado A2-1).

**O orquestrador aplicou as recomendações dele?**

| # | Recomendação do Agente 2 | Situação | Evidência |
|---|---|---|---|
| 1 | Privilégio inflado pela assinatura + baixa cobertura da categoria | **Parcial.** A inflação foi corrigida (13,0% → 3,5%; 27,7% → 23,4%, conferido). A cobertura **não foi tratada nem declarada**: a regra v2 dispara em 1,53% dos 1.760 tickets "Administrative rights" (era 4,5%). Esses tickets falam de *upgrade* (37,7%) e *install* (21,4%), quase nunca de *admin/rights/privilege* (< 2%) | `src/politica.py`; recálculo próprio |
| 2 | Trava de 0,20 calibrada a olho, talvez no teste; tabela de sensibilidade | **Parcial.** A sensibilidade foi medida na validação e publicada (`motor_final.md` §3, proposta §1.1). A possibilidade de ter olhado o teste só aparece no PROCESS_LOG. O README e o `motor_final.md` falam só do Dataset 1 | README "Limitações"; PROCESS_LOG Fase 6 |
| 3 | "# = linha do CSV" | **Aplicada**: "índice da linha no CSV, começando em 0" | proposta §2 |
| 4 | Id 973 "inexistente" / "não voltou" | **Parcial.** Corrigido no `benchmark.md` e na errata. O README continua com "**O LLM inventou um id**" (tabela de erros, linha 153) | README.md:153 |
| 5 | kNN subestimado pelo desempate | **Aplicada**: `benchmark.py` corrigido e regenerado (0,760). README, proposta, relatório e app mostram 76,0% | `benchmark.md` §2 |
| 6 | "Limiar por categoria" impreciso | **Aplicada**: coluna "Origem do limiar" e texto explicativo | `motor_final.md` §2; proposta §1.1 |
| 7–10 | Mediana 6,0×7,1; 82%/9,5%; 43% (docstring); latência | **Aplicadas** (errata + docstring de `triagem.py`) | PROCESS_LOG errata |
| 11 | Exemplos #31874/#8682 com regras extras | **Resolvida pela v2**: agora acionam só saúde e só aprovação, respectivamente (conferido) | recálculo próprio |
| 12 | "30 dias" × "semana 0" | **Aplicada** (relatório: "semana 0 do piloto") | relatório §1 |
| 13 | Ruído de rótulo de 15–25% com n = 32 | **Parcial.** Ressalva no README e na errata. **Sem ressalva** no relatório (HTML e PDF), em `auditoria.md` e no app (`app.py:499`) | grep |
| 14 | Limiares com ponto decimal | **Aplicada** (0,71) | `motor_final.md` |
| — | IC por categoria (4.6) | **Aplicada**: IC por bootstrap no `motor_final.md`; Hardware 94,0–96,2% no README e na proposta | — |
| — | "Administrative rights é, na prática, instalação de software" | **Parcial.** Suavizado na proposta. O relatório mantém "é na prática" | relatório §2 |

### 1.3 Agente 3 (conformidade)

**Qualidade:** boa e útil. Leu todas as fontes e entregou uma matriz por item com texto de correção pronto. Acertou ao apontar a atribuição como o risco nº 1.

**Excessos:** G7 e G10 incentivam acrescentar conteúdo, contra o próprio alerta de concisão. A tabela "Quem fez o quê" sugerida trazia o aviso "ajustar cada célula ao que é verdade". O orquestrador a preencheu com afirmações que **não têm evidência no repositório** ("abriu os CSVs e montou tabelas dinâmicas", "mais de um monitor"), porque o chat export termina antes desses momentos (§3.3).

**O orquestrador aplicou as recomendações dele?**

| Gap | Situação |
|---|---|
| G1: atribuição | **Parcial.** Foram criadas a tabela "Quem fez o quê" e a nota de autoria no topo do PROCESS_LOG, e a coluna "Quem pegou" foi corrigida. **Mas o README ainda se contradiz:** Abordagem 1 diz "Antes de abrir os dados, **levantei** a hipótese de que a base era sintética"; Workflow 1 diz "**Li** a vaga e todos os arquivos do repo e escolhi o 002"; Workflow 2 diz "**Hipótese antes dos dados**". A tabela, logo abaixo, diz que a IA levantou a hipótese e leu o repo. No transcript, a msg da linha 374 é "quero fazer o que você recomendou" |
| G2: `{{DATA}}` e PR | **Não aplicada**: `_Submissão enviada em: {{DATA}}_` continua na última linha do README. O PR ainda não foi aberto (esperado) |
| G3: h/mês | **Aplicada** em README, proposta, `modelo_desperdicio.md`, relatório e app (46 a 175; ≈ 101; R$ 3,9 mil/mês) |
| G4: maior desperdício recuperável | **Aplicada** (README, proposta §5, relatório §5, app §4). No relatório, a frase perdeu o número: "o tempo de triagem manual, **dos quais** a IA libera ~80%" (falta "~1.500 h/ano") |
| G5: iterações | **Aplicada** ("~3 h de sessão contínua, 4 rodadas de juiz…"). Os commits vão de 19:14 a 21:43; é plausível |
| G6: ponte | **Aplicada** na proposta; no relatório, só "retreinado no histórico próprio"; **ausente** no painel do app |
| G7: operação contínua | **Aplicada** (proposta §6). Gatilho de 93% na operação × 95% no piloto: são critérios diferentes, mas não estão explicados |
| G8: screenshots do app novo | **Não aplicada**: 01–05 são da interface antiga |
| G9: Executive Summary | Aplicada em parte; é aceitável |
| G10: pasta `agentes/` | **Aplicada** (versionada com `-f`) |

### 1.4 Agente 4 (ocultos), incluindo o uso da chave "anon"

**Achados:** relevantes e bem documentados (comandos, links de reviews). Respeitou a originalidade: declarou que não leu soluções de outros candidatos.

**A chave "anon" foi adequada? Avaliação: inadequada como decisão, embora não tenha sido um acesso indevido em sentido técnico.**
- **Atenuantes:** a chave anon do Supabase é pública por desenho, vai embutida no JS que qualquer navegador baixa, e a consulta (`jobs_public`, `job_settings`) só lê o mesmo registro público que a página mostra. Nada foi escrito, e o agente registrou o fato com transparência.
- **Por que foi inadequada:**
  - (a) Extrair credenciais de um bundle para chamar a API do ATS **do empregador, durante o processo seletivo**, é um padrão que um avaliador pode ler como "scraping com credencial extraída". O risco é reputacional e foi desproporcional ao ganho.
  - (b) O ganho era marginal: o texto da vaga já tinha sido lido pelo Chrome na sessão principal (transcript, linha 7), e o Arthur podia colá-lo.
  - (c) O classificador de segurança do Claude Code **bloqueou o comando seguinte**, um sinal que deveria ter feito o agente parar e perguntar.
  - (d) O agente não pediu autorização ao Arthur.
- **Como ficou o registro:** o PROCESS_LOG público (Fase 6) descreve o episódio como "usou a consulta pública que a própria página faz. Foi só leitura". Isso omite o bloqueio do classificador e a origem da chave.
- **Recomendação:** reescrever com precisão e com autocrítica (texto em R9) ou, no mínimo, não minimizar o episódio. Não repetir.

**Outros pontos:**
- "Uso de IA = 30%" e "o primeiro leitor provavelmente é um LLM" são inferências tiradas de comentários de reviews, e foram corretamente marcadas como tal.
- Ele recomendou "4 a 6 screenshots das sessões do Claude Code". O orquestrador produziu **renderizações estilizadas** (cartões HTML), não capturas de tela. Isso é aceitável **se estiver rotulado** e se as citações forem literais (§3.3).

---

## 2. App final

### 2.1 Comandos e resultado

```bash
cd submissions/arthur-leite/solution/03-prototipo
unset GEMINI_API_KEY
python -X utf8 -c "from streamlit.testing.v1 import AppTest; at=AppTest.from_file('app.py', default_timeout=900).run(); print(at.exception)"
#  → pandas 2.2.3: exception = ElementList() (vazio), 0 erros, 5 abas, 39 blocos markdown
<venv3>/Scripts/python.exe -X utf8 -c "(mesmo)"
#  → pandas 3.0.6: exception vazio, 0 erros, 39 blocos markdown
```

Também rodei um script de interação (`j5_dump.py`, no scratchpad), que despejou o texto renderizado e testou estes casos:
- phishing → "Segurança da Informação" + "Escalar agora" + rascunho bloqueado;
- texto vazio → orientação;
- "please grant admin rights…" → Sugestão/Hardware + alerta de privilégio;
- "install … outlook … upgrade" → Administrative rights.

Sem exceções.

### 2.2 Os números do painel batem com os outputs oficiais?

**Sim, todos.** Conferi no texto renderizado e com recálculo próprio:

| Exibido no painel | Output oficial | Status |
|---|---|---|
| 49%; 1.365 de 2.769; 27 h; 543 a 580; 0,2 ponto; 0 de 21 | `auditoria.md` §1–4 | OK |
| 80 combinações; 7,6 h; 8,1 h; −4,1 h; 68% (p = 0,68) | `auditoria.md` §4b | OK |
| 47.837; 9.568; 65,5 / 23,3 / 11,2%; 96,4%; 91,0%; 9,7% | `motor_final.md` §1 | OK |
| 34,1% → 10,8% | `motor_final.md` §3 | OK |
| 23,4%; 0,7 / 2,0 / 2,0 / 10,4 / 3,5 / 7,7% | `politica.py` v2 (recalculado) | OK |
| 85,0 / 76,9 / 76,0 / 53,5 / 48,0 / 44,0% | `benchmark.md` §2 | OK |
| 552 / 1.218 / 2.106 h; 0,3 / 0,7 / 1,2; R$ 21.105 / 46.563 / 80.508; 46 a 175 h/mês; ≈ 101; R$ 3.880/mês; 81% | `modelo_desperdicio.md` (recalculado) | OK |
| Metodologia: IC 95,9–96,8%; McNemar 53×21, 70×7; 0,860 | `motor_final.md`, `benchmark.md` | OK (fixos) |

### 2.3 A 1ª tela responde às 3 perguntas para um leigo?

Sim. "Onde perdemos tempo?" é respondida com honestidade (o 1º gargalo é de medição); "O que automatizar?" e "Funciona?" vêm com número e uma frase. Há afirmações que vão além da evidência:
- "Funciona? **Sim**" (sem a ressalva de domínio);
- "Cada categoria só é automatizada acima de 95%";
- "travas de segurança";
- o exemplo de compra → Miscellaneous na seção "Prova";
- "A triagem pode ser automatizada **com segurança**" no hero (o relatório usa a mesma frase; é aceitável porque vem com "começando em modo sombra", mas é o tom mais forte da entrega).

---

## 3. Coerência global

### 3.1 Os números batem entre os documentos?
- README, proposta, relatório HTML, relatório PDF, app, `motor_final.md`, `benchmark.md`, `modelo_desperdicio.md` e `politica.py`: **coerentes**.
- **PDF × HTML:** comparei todos os números extraídos dos dois arquivos e não há nenhuma diferença. O PDF (21:38) é posterior ao HTML (21:24), então **não está defasado**.
- **Divergências restantes:**
  - texto: "inventou um id" (README) × "truncou" (errata/benchmark);
  - ruído de rótulo com ressalva (README) × sem ressalva (relatório/app/auditoria);
  - trava: "possivelmente olhando o teste" (PROCESS_LOG) × "com o Dataset 1 à vista" (README);
  - gatilho de 93% (operação, proposta §6) × 95% (piloto);
  - a docstring de `painel.py` diz 27,7%.

### 3.2 A tabela "Quem fez o quê" é honesta?

No geral, é muito melhor que a versão anterior e consistente com o transcript nos pontos que ele cobre:
- a IA leu o repo e recomendou o 002;
- a IA levantou a hipótese sintética;
- o Arthur exigiu o juiz (linha 1356);
- o Arthur configurou o deploy e a chave sem colá-la (linhas 891–981 e 4955);
- o Arthur relatou o erro de deploy (linha 5009).

**Problemas:**
- (a) O README se contradiz em Abordagem 1 e em Workflow 1–2 (§1.3).
- (b) "Abriu os CSVs e montou **tabelas dinâmicas**", "mais de um monitor", "pediu o painel", "montou o time de 5 agentes" e a correção pela aba anônima **não constam do chat export versionado**, que termina na mensagem da linha 5179. Como o export está desatualizado, essas afirmações ficam **não verificáveis no repositório**, numa entrega que convida o leitor a "conferir na conversa completa".
- (c) "Escolha do case: Decidiu pelo 002, com base na experiência…": no transcript, a decisão foi "quero fazer o que você recomendou". A justificativa pela experiência do Arthur não aparece em mensagem dele. Sugestão: "Aceitou a recomendação da IA; o encaixe com a operação de agentes que ele mantém pesou".

### 3.3 Imagens 10–15 (abri todas)

| Imagem | Citação literal? | Fonte correta? | Problema |
|---|---|---|---|
| 10 · Arthur exige juiz | Arthur: **literal** (linha 1356). Claude: paráfrase sem aspas (ok) | Sim | — |
| 11 · Juiz derruba backlog | Claude (linha 1338) e juiz (`fase1`, A8): **literais** | Sim | — |
| 12 · Juiz derruba ROI | "1.496 h" e "15% → 7,5%" conferem com o transcript (linhas 2338/2341). **A citação do juiz entre aspas não é literal**: junta trechos e omite "(4,9% na faixa auto)", "Se os humanos erram 15%…" e "no roteamento errado", sem "[…]" | Em parte: a tabela v1 está no chat export (linha 2338), não no parecer | Marcar os cortes com "[…]" ou tirar as aspas |
| 13 · Deploy quebra | Arthur: literal com cortes "…" (ok; o traceback está na linha 5032). **A citação do juiz final entre aspas ("Crítico: requirements.txt não fixa pandas…") não existe** no `fase5_final_parecer.md`; é paráfrase | Parcial | Tirar as aspas ou citar o texto real (`fase5_final_parecer.md`, linhas 106/116). Há também uma falha de renderização: "pandas 3" quebrou para uma linha própria |
| 14 · Aba anônima | **Nenhum dos 3 trechos está no chat export citado** | **Não** | Reexportar o chat ou mudar a fonte |
| 15 · Painel + 5 agentes | A fala do Arthur não está no chat export | Fonte citada: `agentes/` + PROCESS_LOG Fase 6 (paráfrase) | **Não versionada** (ignorada pelo `.gitignore` raiz) |

Além disso:
- nenhuma das imagens 10–15 é citada no README nem no PROCESS_LOG;
- as Evidências do README falam só de "Screenshots do protótipo";
- as imagens são **renderizações** de trechos, não capturas de tela, e isso não está dito em lugar nenhum. Sem esse rótulo, um avaliador pode lê-las como prints fabricados.

### 3.4 Estado do git

- `git status --ignored` mostra como **ignorados**: `screenshots/15_…png`, `agentes/agente5_juiz.md` e `chat-exports/exportar_chat.py`. Corretamente fora: `.env` e `__pycache__`.
- Arquivos fora da pasta: **0** (`git diff --name-only upstream/main...HEAD`).
- Commits com author Arthur e trailer Co-Authored-By (ok).
- `74a6dd8` existe só localmente. O app publicado no Streamlit Cloud continua na versão antiga até o push.

---

## 4. Correções

### 4.1 Obrigatórias (bloqueiam o PR), em ordem

1. **README, última linha:** `_Submissão enviada em: {{DATA}}_` → `_Submissão enviada em: 15/10/2026_` (ou a data real do PR).
2. **README, atribuição (alinhar com "Quem fez o quê"):**
   - Abordagem 1: "**Desconfiar antes de analisar.** Antes de abrir os dados, a IA levantou a hipótese de que a base era sintética, e eu exigi que ela fosse testada campo a campo, com poder estatístico, antes de qualquer diagnóstico."
   - Workflow 1: "A IA leu a vaga e o repositório e recomendou o 002; aceitei pelo encaixe com a minha operação de agentes de atendimento."
   - Workflow 2: "**Hipótese antes dos dados (da IA):** a base devia ser sintética…"
   - "Quem fez o quê", linha "Escolha do case": "Aceitou a recomendação da IA…"
3. **Imagens 10–15:**
   - (a) Na 12 e na 13, tornar as citações literais (com "[…]" nos cortes) ou tirar as aspas.
   - (b) Na 14 e na 15, apontar para uma fonte que contenha o trecho (ver o item 4).
   - (c) Acrescentar ao README, em Evidências: "- [x] Imagens do processo com a IA (reconstituições visuais de trechos literais do chat export e dos pareceres, não capturas de tela): `process-log/screenshots/10_…` a `15_…`" e citar cada uma na fase correspondente do PROCESS_LOG.
   - (d) `git add -f process-log/screenshots/15_processo_arthur_pede_painel_e_5_agentes.png`.
4. **Reexportar `chat-exports/conversa_claude_code.md` até o fim da sessão** (com `exportar_chat.py`, mantendo a remoção de raciocínio e memória). Assim ficam verificáveis a aba anônima, o pedido do painel, o time de 5 agentes e as "tabelas dinâmicas". Se a verificação manual por tabelas dinâmicas e monitores não estiver em nenhuma mensagem do Arthur, reescrever no README e no PROCESS_LOG como "Arthur relata ter…" ou retirar.
5. **README:153:** "O LLM inventou um id numa resposta em lote" → "O LLM devolveu um id truncado (9735 → 973) numa resposta em lote".
6. **Git e deploy:**
   - `git add -f process-log/agentes/agente5_juiz.md` (se for entrar);
   - commit e push;
   - confirmar no Streamlit Cloud, numa aba anônima, que o painel novo sobe a frio;
   - só então abrir o PR `[Submission] Arthur Leite — Challenge 002`;
   - antes do push, `git diff --name-only upstream/main...HEAD | grep -v '^submissions/arthur-leite/'` deve sair vazio;
   - **confirmar a inscrição no ATS** (ação externa, segundo o Agente 4).

### 4.2 Recomendadas, em ordem de prioridade

- **R1 · `app.py` (exemplo "Aprovação de compra")**: trocar por um pedido que o motor rota para Purchase no automático, ou renomear o card para "Pedido ambíguo → Sugestão" e mostrar as 2 opções que o motor oferece (`r.top2`). Na seção "Prova", a IA não deve parecer errar.
- **R2 · `app.py:199`**: "travas de segurança" → "travas de domínio".
- **R3 · `app.py:211` e `:194`**:
  - título: "Na faixa automática, todas as categorias ficaram em 95% ou mais no teste";
  - legenda: "estimativa pontual; Hardware, no limite, tem intervalo de 94,0% a 96,2%";
  - `:194`: "…quando a precisão medida na validação é de pelo menos 95%".
- **R4 · Cobertura da regra de privilégio** (proposta §2, "Limitação conhecida da política", e README "Limitações"): "A regra de privilégio cobre pedidos explícitos (*admin rights, permissions, grant access*). Os tickets rotulados 'Administrative rights' falam de instalação e upgrade e quase não usam esse vocabulário: a regra dispara em só 1,5% deles. No piloto, decidir com Segurança se a categoria inteira exige aprovação."
- **R5 · `app.py:146`** ("Funciona?"): "Sim, em 9.568 tickets reais de TI. Na sua operação, depois de retreinar no seu histórico e passar pelo modo sombra." Acrescentar ao painel (seção 2) uma linha com a ponte: "Na sua operação, as filas viram Billing, Refund, Technical, Product e Cancellation."
- **R6 · Ruído de rótulo**: acrescentar "(amostra de 32 textos: ordem de grandeza)" no relatório (HTML §6, e regenerar o PDF), em `app.py:499` e em `auditoria.md` (via `01_auditoria_dados.py:199`).
- **R7 · Relatório**:
  - "dos quais a IA libera ~80%" → "~1.500 h/ano no cenário base, das quais a IA libera ~80%";
  - "'Administrative rights', por exemplo, é na prática instalação de software" → "os termos que mais pesam em 'Administrative rights' são de instalação de software";
  - regenerar o PDF.
- **R8 · Trava (README, "Limitações")**: acrescentar "e possivelmente com o teste à vista (o diário registra '9,5% dos normais', valor que não bate com nenhum dos conjuntos)", alinhando com o PROCESS_LOG.
- **R9 · PROCESS_LOG, Fase 6, Agente 4**: "Para ler a página da vaga (uma SPA), o agente usou a chave anônima pública embutida no JS da página para consultar o registro público da vaga. Foi só leitura, mas o classificador de segurança do Claude Code bloqueou o comando seguinte. Em retrospecto, o certo era pedir o texto ao Arthur, e não repetirei esse caminho."
- **R10 · Screenshots 01–05**: refazer com o painel novo (pelo menos o hero com os 4 cartões e a triagem com phishing).
- **R11** · `painel.py:9`: 27,7% → 23,4%. Exibir a confiança com 1 casa decimal, ou "> 99%".
- **R12** · Proposta §6: explicar que 93% é o gatilho de **recuo** na operação e 95% é a barra de **entrada** do piloto. Corrigir o sufixo do SHA-256 do DS1 no relatório do Agente 2 (cosmético).

---

## 5. Comandos rodados (resumo)

```bash
git log --oneline; git show 74a6dd8 --stat; git show 47d1fce --stat
git diff ae391b0 47d1fce -- …/benchmark.py …/avaliar_motor.py …/triagem.py
git status --ignored --short submissions/arthur-leite; git check-ignore -v …/.env
git diff --name-only upstream/main...HEAD | grep -v '^submissions/arthur-leite/'   # 0
AppTest (pandas 2.2.3 e venv pandas 3.0.6), sem GEMINI_API_KEY                        # sem exceções
python j5_check.py   # política v2 no DS2 e no teste; cobertura em Admin rights; 4 exemplos; faixas; ROI e h/mês
python j5_dump.py    # texto renderizado do painel + interações (phishing, vazio, privilégio, outlook)
pypdf + regex: números do relatório-executivo.pdf × .html                          # idênticos
grep no chat export: citações das imagens 10–15 e as mensagens do Arthur (13, até a linha 5179)
sha256sum DS1                                                                       # b06a9cde…3c11bf8bea
```

Scripts em `C:\Users\arthu\AppData\Local\Temp\claude\C--Users-arthu\f9c1eeb9-22f4-458e-90d2-ffec0e8ecbb1\scratchpad\` (`j5_check.py`, `j5_dump.py`, `app_text.txt`, `pdf.txt`, `html.txt`).
