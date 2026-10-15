# Parecer final do agente juiz (Fase 5): reprodução a frio, coerência e julgamento

Revisor independente e adversarial, conforme `PROTOCOLO_JUIZ.md`. Clonei a branch publicada do zero, segui o README ao pé da letra e recalculei os números com código próprio. Não criei `.env` e não chamei nenhuma API de LLM.

- Clone: `git clone --branch submission/arthur-leite --depth 1 https://github.com/arthurroleite/ai-master-challenge.git`, num diretório temporário (já apagado).
- **Atenção:** a branch andou durante a revisão. Comecei em `e78ecfd`, e no meio dela chegou o `9d127a6` ("prepara o app para Streamlit Cloud + screenshots"). Repeti a reprodução no `9d127a6`, num **venv novo** (Python 3.13.2, `pip install -r requirements.txt` puro). Os vereditos abaixo valem para o `9d127a6`.

---

## 1. Reprodução

| Passo (README) | Resultado | Veredito |
|---|---|---|
| `pip install -r requirements.txt` (venv novo) | Instala **pandas 3.0.6**, streamlit 1.66, sklearn 1.9.1 (os requisitos não têm limite superior) | ok, mas veja a linha seguinte |
| `python baixar_dados.py` | Funciona. Usou o cache do kagglehub que já existia na máquina, então o download real não foi testado de verdade | CONFIRMADO |
| `01_auditoria_dados.py` | Gera `auditoria.md` **idêntico byte a byte** ao versionado | CONFIRMADO |
| `02_modelo_desperdicio.py` | **QUEBRA no venv novo** (`IndexError: too many indices for array`, `triagem.py:96`) | **FALHA** |
| `benchmark/avaliar_motor.py` | **QUEBRA**, mesmo erro (o motor não treina) | **FALHA** |
| `streamlit run app.py` | `/_stcore/health` responde `ok`, mas o script **quebra na 1ª execução** (AppTest: `exceptions: ['too many indices for array.']`). Um avaliador abre o navegador e vê um traceback | **FALHA CRÍTICA** |
| `MotorTriagem.carregar().classificar("my laptop screen is broken")` | Quebra no venv novo. Com pandas 2.2.3 (o global da máquina), funciona: Hardware, 99,8%, faixa auto | **FALHA** no ambiente limpo |
| `benchmark/benchmark.py` | (a) Sem `tabulate`, quebra em `to_markdown` (o pacote saiu de `requirements.txt` no `9d127a6`, e o README não cita `requirements-benchmark.txt`). (b) Com `tabulate`, mas sem `data/cache/`, ele **sobrescreve o `benchmark.md` versionado e apaga as linhas do LLM e do modelo B**, porque lê os `.jsonl` de `data/cache/` e não de `outputs/llm_respostas/` | **FALHA** e destrói evidência |
| Todos os scripts com saída redirecionada (Git Bash/pipe, Windows) | `UnicodeEncodeError` (cp1252) no `print` final. Os arquivos são gravados antes do print, então as saídas ficam íntegras, mas o script termina com código 1 e traceback | FALHA leve |

**Causa raiz da falha crítica:** no pandas 3, colunas de texto passam a ser `ArrowStringArray`, e `Series.values[:, None]` deixa de funcionar. Os pontos afetados são `src/triagem.py:95-96` e `benchmark/benchmark.py:174-176`. Testei a correção `["Topic_group"].values` → `["Topic_group"].to_numpy()` no clone: com ela, `02_modelo_desperdicio.py`, `avaliar_motor.py` e o app rodam no pandas 3, e **os outputs saem idênticos aos versionados**. A alternativa é fixar `pandas>=2.2,<3`. **Isso também derruba o deploy no Streamlit Cloud**, que instala a versão mais nova.

**Reprodutibilidade numérica (com pandas 2.2.3, ou com a correção):** `auditoria.md`, `modelo_desperdicio.md` e `motor_final.md` saem idênticos byte a byte. Com os `.jsonl` copiados para `data/cache/` e os embeddings gerados por `embed_ds2.py` (520 s em CPU), o `benchmark.md` sai idêntico, salvo os tempos de treino (29 s → 44 s; 5 s → 8 s). **Todos os números das tabelas foram reproduzidos.**

**App (AppTest, sem `.env`):** 5 abas, nenhuma exceção (com a correção). Phishing → fila "Segurança da Informação", modo "Escalado", com alerta. Texto em português → "Triagem humana". LLM desligado com aviso. Achados:
- A aba "Fila de teste" abre com uma **amostra de 1.000** (semente 0): 67,5% automático · 20,5% sugestão · 12,0% humano, e **"certa entre as 2: 89,3%"**, abaixo dos "≥ 90%" que o próprio app promete. É variação de amostra, mas é o primeiro número que o avaliador vê e ele contradiz o README (65,5 / 23,3 / 11,2 / 91,0).
- A política por palavra-chave não pega "I am leaving the company, please remove my access" (o desligamento só dispara com *leaver/termination/offboarding...*). A limitação está declarada, mas é um teste de borda óbvio que o avaliador pode fazer.

**Referências quebradas ou contraditórias no README:**
1. `process-log/chat-exports/` **não existe** na branch e é citada duas vezes ("Conversa completa", "[x] Chat export").
2. "Respostas brutas do LLM: geradas por `llm_classify.py` (**cache local, não versionado**)": falso. Elas estão versionadas em `solution/03-prototipo/benchmark/outputs/llm_respostas/` (o que é bom; corrija o texto).
3. "Três pareceres mudaram a entrega": há só 2 pareceres em `revisoes/` (fase1, fase3). Este parecer será o 3º.
4. "Para reproduzir as análises: `python solution/01-diagnostico/...`" logo depois de `cd .../03-prototipo`: o caminho relativo não bate com o diretório em que o leitor está. Os scripts funcionam de qualquer pasta (usam `__file__`), mas a instrução é ambígua.
5. O setup não menciona `requirements-benchmark.txt`, `embed_ds2.py` (necessário para a linha B) nem que `benchmark.py` sobrescreve o `benchmark.md`.
6. `solution/01-diagnostico/outputs/modelo_desperdicio.json` é um **arquivo órfão e desatualizado**: nenhum script o gera, e ele traz os números da v1 (1.496 h, R$ 57 mil, faixa automática de 74,2%, erro de roteamento de 15% → 7,5%), justamente o que o juiz da fase 3 derrubou.

**Escopo do PR:** `git diff --name-only upstream/main...HEAD | grep -v '^submissions/arthur-leite/'` → **vazio**. Os 36 arquivos (no `e78ecfd`) e os 10 do `9d127a6` estão todos dentro de `submissions/arthur-leite/`. **CONFIRMADO.** Observação: o histórico do fork tem 5 commits de outro autor (João Vitor Chaves Silva), que são os commits originais do upstream; não há problema.

---

## 2. Coerência de números

Recalculei de forma independente as frequências da política (47.837 tickets: 0,7 / 2,0 / 2,3 / 10,4 / 13,0 / 7,7%; 27,7% exigem humano; 2,7% bloqueiam o rascunho; 8,1% escalam), a divisão das menções a segurança (Hardware 41,3%, Admin 18,6%, Access 16,8%) e o ROI (30.000 × 3 min = 1.500 h; com IA ≈ 282 h; 1.218 h; 0,70 FTE; R$ 46.563). **Todos conferem.**

| # | Onde | Divergência | Gravidade |
|---|---|---|---|
| 1 | `relatorio-executivo.html/pdf`, barra de faixas | "Automático 65,5% · Sugestão 23,3% · **Humano 11%**": arredondamento inconsistente na mesma linha (o certo é 11,2%) | baixa |
| 2 | Relatório × proposta | Relatório: "91%", "85%", "77%", "54%", "73%". Proposta: "91,0%", "85,0%", "76,9%", "53,5%", "73,3%". Aceitável (público diferente), mas o "54%" arredonda 53,5 para cima | baixa |
| 3 | `proposta.md` §3 (fluxo) e relatório §4 | "confiança baixa → triagem humana (**11,2%**)". **Errado na atribuição:** recalculei, e só 1,5 ponto vem de confiança baixa. Os outros **9,7 pontos (86% da faixa humana) são tickets do próprio domínio barrados pela trava de similaridade**. Neles o modelo acerta 78,6%, e 61,5% teriam ido para o automático pela confiança. É por isso que, no `motor_final.md`, a faixa humana (72,4%) acerta **mais** que a de sugestão (63,4%) | **média** |
| 4 | `benchmark.md` §3 × `motor_final.md` | Dois números de "faixa automática": 74,2% / 95,1% (benchmark, limiar global, sem travas) e 65,5% / 96,4% (motor final). O `benchmark.md` não avisa que o número oficial é outro | média |
| 5 | `modelo_desperdicio.json` | Números da v1 (1.496 h, 74,15%, R$ 57.217), incompatíveis com toda a entrega | **média** (é o tipo de coisa que um avaliador adversarial acha) |
| 6 | App, aba "Fila de teste" (padrão) | 67,5 / 20,5 / 12,0 e top-2 de 89,3% × 65,5 / 23,3 / 11,2 / 91,0 no README | média |
| 7 | `PROCESS_LOG.md` Fase 4 × README | "**43%** [dos tickets de outro domínio] seriam roteados automaticamente" × "**34%** iriam para o automático sem as travas". Provavelmente versões diferentes (antes ou depois de igualar o pré-processamento ou do limiar por categoria), mas o log não diz qual vale | baixa |
| 8 | `benchmark.md` | Formato numérico americano ("33,485", "0.860", "74.2%") num documento em português; o resto usa "9.568" e "65,5%" | baixa |
| 9 | Política: 27,7% × 27,9% | 27,7% (Dataset 2 inteiro) na proposta e no relatório; 27,9% (teste) no `motor_final.md`. As duas bases são legítimas, mas nenhum documento diz que são bases diferentes | baixa |
| 10 | README "o TF-IDF (85%)" × "86,0%" no teste completo | 85% na amostra de 400 e 86% no teste completo. Está correto, mas aparece sem a base | baixa |
| 11 | Instrumentação: "30 dias" × "semana 0" | O resumo e o relatório falam em "plano de instrumentação de 30 dias"; o roteiro do piloto põe a instrumentação na "semana 0", e o "piloto de 4 semanas" tem 5 etapas (0, 1–2, 3–4, 5+) | baixa |

Todo o resto confere entre README, relatório, proposta, app e outputs: 8.469; 27 h; 49% (1.365 / 2.769); p = 0,80; 0,21 ponto; 0 de 21; V = 0,021; 6,4% × 6,8%; p = 0,33; 9.568; 65,5% / 96,4% / IC de 95,9 a 96,8%; 23,3% / 91,0%; 11,2%; 34,1% → 10,8%; 97,8–99,0%; 95,1–99,0% por categoria; limiares 0,78 / 0,71–0,75; 44 / 48 / 76,9 / 53,5 / 73,3 / 78,2 / 85,0%; McNemar p = 0,0003; 552 / 1.218 / 2.106 h; 0,3 / 0,7 / 1,2 FTE; R$ 21 / 47 / 81 mil; R$ 38,24/h; 34,5% das decisões de roteamento com humano.

---

## 3. Julgamento

### (a) Onde o texto afirma mais do que a evidência sustenta

- **"A triagem já pode ser automatizada com segurança"** (título do relatório) e **"Provado com 47.837 tickets reais"**: CONFIRMADA COM RESSALVA. O que foi provado vale para tickets internos de TI, em inglês, e de outra organização. Para a operação do Diretor (suporte a cliente de produto), o próprio teste fora do domínio mostra que o modelo **não serve** sem retreino, e o único histórico dessa operação (Dataset 1) tem rótulos aleatórios. A tese "o ativo é o histórico rotulado da empresa" é forte, mas ela própria implica que **ainda não se sabe** se o histórico desta empresa tem qualidade. Sugestão: "A abordagem de triagem foi validada em dados reais; para esta operação, ela exige retreino no histórico próprio, e o piloto mede isso."
- **"Humano 11,2% = confiança baixa"**: REFUTADA na atribuição (item 3 acima). É uma escolha de desenho defensável (cobertura trocada por segurança fora do domínio), mas deve ser dita assim: "9,7% são barrados pela trava de domínio; custo: tickets que o modelo acertaria em 79% dos casos".
- **"Tempo de espera na fila errada: provavelmente o maior ganho"**: opinião sem dado. Está marcada como "provavelmente", o que é aceitável.
- **"Uma análise automática padrão, feita por IA sem checagem, cairia nessa armadilha"**: plausível (é o argumento do baseline), mas não foi demonstrado. É aceitável como retórica.
- **"Todas as categorias ≥ 95%"**: confere (Hardware com 95,1%), mas Hardware está no limite, e o IC por categoria não foi mostrado. Seria honesto citar "Hardware no limite (95,1%)".
- **O comparativo modelo simples × LLM** está bem qualificado ("um LLM mais forte, com definições, provavelmente reduziria a distância"). CONFIRMADA.
- **O ROI** está bem qualificado (bruto, premissas, sensibilidade). CONFIRMADA.

### (b) Itens obrigatórios do enunciado 002

| Item | Atende? | Comentário |
|---|---|---|
| Diagnóstico: onde o fluxo trava (canal × prioridade × tipo, piores combinações) | **Parcial, com risco de "fugiu da pergunta"** | A resposta é "não dá para afirmar", e ela é tecnicamente correta e bem provada. Mas a pergunta literal ("quais combinações geram os piores tempos") **não tem nenhuma tabela**. Um avaliador apressado lê "não respondeu". A correção é barata (ver §4) |
| Diagnóstico: o que impacta a satisfação | Sim | Bateria de testes + Bonferroni + poder estatístico. Ótimo |
| Diagnóstico: quanto se desperdiça (horas, custo, maior desperdício recuperável) | Parcial | Há horas e R$, mas só da **triagem**, por premissa. O "maior desperdício recuperável" é apontado (fila errada) sem número. Falta dizer que fração do tempo total do agente a triagem representa |
| Proposta: o que automatizar | Sim | Faixas, limiar por categoria, travas e copiloto |
| Proposta: o que NÃO automatizar, com exemplos dos dados | Sim | Seis regras com frequência medida; "rotear ≠ executar ≠ responder" é o ponto mais forte da entrega. Faltam **exemplos literais de tickets** (o enunciado pede "justifique com exemplos dos dados"); hoje só há frequências |
| Proposta: fluxo na prática | Sim | Diagrama claro, com IA e humano marcados |
| Uso dos dois datasets ("o poder está no cruzamento") | Parcial | O Dataset 1 serve de auditoria, de molde estrutural e de **teste fora do domínio para as travas** (um cruzamento real e inteligente). Mas esse cruzamento não aparece como argumento explícito; o leitor pode concluir que o Dataset 1 foi descartado |
| Protótipo com dados reais, sem escolher a dedo | Sim (quando roda) | Fila com todo o conjunto de teste; ver a falha crítica do pandas 3 |
| Process log | Sim, com furo | Narrativa rica, erros corrigidos, juiz. Mas o chat export prometido não existe e o log para na Fase 4 (sem a Fase 5: relatório, rodada RAG/3.8-flash, deploy) |

### (c) Template e CONTRIBUTING

- O README segue o template: Sobre mim, Executive Summary, Solução (Abordagem, Resultados, Recomendações, Limitações), Process Log (Ferramentas, Workflow, Onde a IA errou, O que adicionei) e Evidências. **CONFIRMADO.**
- Os placeholders `{{LINKEDIN}}` e `{{DATA}}` continuam lá (intencional; preencher antes do PR).
- Estrutura: `README.md`, `solution/` e `process-log/` (com `screenshots/` desde o `9d127a6`). Não existe `chat-exports/`, que o README cita.
- Nada fora de `submissions/arthur-leite/` foi alterado (diff contra `upstream/main` verificado). **CONFIRMADO.**
- O Executive Summary tem 4 parágrafos curtos; o template pede 3 a 5 frases, e ele está um pouco acima. Aceitável.

### (d) O Diretor não técnico entende o relatório em 5 minutos?

**Sim, em grande parte.** O bloco "Resposta em 1 minuto", com as 3 perguntas, é exemplar, e as tabelas usam rótulos de negócio ("inválido", "ruído"). Atritos: "IC95%", "McNemar, p = 0,0003", "travas", "LGPD art. 11" sem explicação e "RAG" implícito. São poucos e não impedem a leitura. O PDF tem 6 páginas, o que é razoável para 5 minutos se o Diretor parar na página 1. Falta um **pedido explícito de decisão** ("o que preciso de você: aprovar a instrumentação e 4 semanas de modo sombra").

### (e) Os 3 pontos mais fracos aos olhos de um avaliador

1. **O protótipo não sobe numa instalação limpa** (pandas 3) e o deploy no Streamlit Cloud vai falhar pelo mesmo motivo. Um avaliador que segue o README vê um traceback, e "me mostre que funciona" é o coração do challenge. Além disso, `benchmark.py` apaga as linhas do LLM no `benchmark.md` quando rodado a frio, e os scripts quebram com saída redirecionada no Windows.
2. **Evidência prometida que não existe ou está desatualizada:** `chat-exports/` ausente, "cache não versionado" falso, "três pareceres" com dois, `modelo_desperdicio.json` com os números da v1 e process log sem a Fase 5. Para uma entrega cujo diferencial é o rigor, cada um desses furos custa caro.
3. **Pergunta 1 respondida com uma recusa e cruzamento implícito entre os datasets.** A recusa é correta, mas sem a tabela literal (piores combinações + IC mostrando que é ruído) ela parece fuga. Somam-se a isso a frase "já pode ser automatizada com segurança", mais forte que a evidência para esta operação, e a faixa humana atribuída a "confiança baixa".

---

## 4. Correções recomendadas, em ordem de prioridade

| # | Correção | Esforço |
|---|---|---|
| 1 | **Corrigir a compatibilidade com o pandas 3:** em `src/triagem.py:95-96` e `benchmark/benchmark.py:174-176`, trocar `["Topic_group"].values` por `.to_numpy()` (testado: os outputs ficam idênticos), **e/ou** fixar `pandas>=2.2,<3` no `requirements.txt`. Depois, testar num venv novo e no Streamlit Cloud | 5 min |
| 2 | Pôr `sys.stdout.reconfigure(encoding="utf-8")` no topo dos 4 scripts (ou tirar o `print` do markdown) | 5 min |
| 3 | `benchmark.py`: ler os `.jsonl` de `outputs/llm_respostas/` (fallback de `data/cache/`) e **não sobrescrever** `benchmark.md` quando faltarem embeddings ou LLM (gravar em `benchmark_parcial.md` ou pular a seção com aviso). No README, citar `pip install -r requirements-benchmark.txt` e `python benchmark/embed_ds2.py` | 20 min |
| 4 | README: remover ou cumprir `chat-exports/` (exportar a conversa); corrigir "cache local, não versionado" → "versionadas em `benchmark/outputs/llm_respostas/`"; "três pareceres" → contar este; deixar claro de qual pasta rodar cada comando | 15 min |
| 5 | Apagar `solution/01-diagnostico/outputs/modelo_desperdicio.json` (órfão, v1) | 1 min |
| 6 | **Responder a pergunta 1 literalmente:** na auditoria e no relatório, uma tabela com as 3 "piores" e as 3 "melhores" combinações canal × prioridade × tipo, com a duração média e o IC95% (ou o p do Kruskal-Wallis), e a frase "a pior combinação parece X h mais lenta, mas a diferença está dentro do ruído". Isso responde à pergunta **e** reforça a tese | 30 min |
| 7 | Corrigir a atribuição da faixa humana na proposta e no relatório: "11,2% vão a humano: 9,7% pela trava de domínio (tickets atípicos; o modelo acertaria 79% deles, é o preço da segurança fora do domínio) e 1,5% por confiança baixa". No `motor_final.md`, acrescentar essa decomposição | 15 min |
| 8 | Suavizar o título: "A triagem já pode ser automatizada com segurança" → "A triagem pode ser automatizada com segurança; a abordagem foi provada em 48 mil tickets reais e, nesta operação, começa em modo sombra". Trocar "Provado com" por "Validado em" | 5 min |
| 9 | App: abrir a aba "Fila de teste" com o **conjunto de teste inteiro** (slider padrão = 9.568) para bater com o README, ou escrever "amostra de 1.000; números oficiais no teste completo: 65,5 / 23,3 / 11,2" | 5 min |
| 10 | Tornar o cruzamento explícito: um parágrafo "Como os dois datasets se cruzam" (o Dataset 1 dá a estrutura da operação e o **teste fora do domínio que calibrou as travas**; o Dataset 2 dá a prova). Incluir 2 ou 3 **tickets reais** do Dataset 2 como exemplo em "o que não automatizar" | 20 min |
| 11 | Consistência: "Humano 11%" → "11,2%" no relatório; avisar no `benchmark.md` §3 que o número oficial é o do `motor_final.md`; formato pt-BR no `benchmark.md`; indicar a base (27,7% no Dataset 2 inteiro × 27,9% no teste; 85% na amostra × 86% no teste); alinhar "30 dias" × "semana 0" | 15 min |
| 12 | `PROCESS_LOG.md`: acrescentar a Fase 5 (relatório, rodada RAG / 3.8-flash, deploy, este parecer e o que mudou) e explicar o 43% × 34% | 15 min |
| 13 | Política: acrescentar "leaving", "last day", "remove (his/her) access", "password" + "clicked" à regra correspondente, ou citar o caso como limitação conhecida | 5 min |
| 14 | Relatório: fechar com "O que preciso de você" (aprovar a instrumentação + 4 semanas de modo sombra) | 5 min |

**Veredito geral:** a entrega é analiticamente muito acima do baseline. A desconfiança da base, a política "rotear ≠ executar ≠ responder", o benchmark honesto contra LLM e o ROI enxuto e revisado são diferenciais reais, e os números se reproduzem. Mas **hoje o protótipo não sobe numa instalação limpa**, e esse é o item que o avaliador testa primeiro. Com as correções 1 a 5 (menos de 1 hora), a entrega deixa de ter falhas objetivas. Com as 6 a 8, fecha os flancos de narrativa.
