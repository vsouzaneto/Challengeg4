# Process log — Gabriel Mata — Challenge 004 (Estratégia Social Media)

Documento único com a evidência de como a solução foi construída com IA. **Cada informação aparece uma vez só:** o porquê na seção 3, o como e os números na seção 4, e os pedidos exatos ao executor na seção 5.

## Índice
1. [Como ler este documento](#1-como-ler-este-documento)
2. [Linha do tempo](#2-linha-do-tempo)
3. [Registro de decisões (o porquê)](#3-registro-de-decisões-o-porquê)
4. [Log de execução do Claude Code (o como)](#4-log-de-execução-do-claude-code-o-como)
5. [Ordens de Serviço](#5-ordens-de-serviço)
6. [Exploração inicial no chat](#6-exploração-inicial-no-chat)
7. [Baseline](#7-baseline)
8. [Export da conversa](#8-export-da-conversa)

---

## 1. Como ler este documento

| Quem | Papel |
|---|---|
| **Gabriel** | Decisões, hipóteses de negócio, direção e aprovação de cada etapa |
| **Claude (Claude.ai, chat)** | Planejamento, desenho do método, interpretação, estratégia, relatórios, revisão crítica de cada entrega (inclusive testando a ferramenta num navegador automatizado) e escrita das Ordens de Serviço |
| **Claude Code** | Executor: recebe uma Ordem de Serviço curta, sem contexto estratégico, e devolve scripts, números, gráficos, PDFs e a ferramenta, com validações independentes |
| **Claude (chat separado, sem contexto)** | Baseline: o brief e o CSV num único envio, para comparar métodos |

**Ciclo de trabalho:** o chat escreve a OS → o Gabriel envia ao Claude Code → o Code executa e devolve um resumo → o chat interpreta, critica e decide a próxima OS com o Gabriel.

**Regras que valeram o projeto inteiro**
- Todo número sai de código executado.
- Diferença pequena não é insight.
- A regra de decisão é fixada antes de ver os resultados.
- O executor não interpreta e não entra em espiral de erros: no máximo 2 tentativas por erro, sem mudar o escopo.

**Evidência bruta fora deste documento:** a [conversa completa com o Claude](https://claude.ai/share/8fe74758-e8bc-4805-b801-e5ad447b62c8) (link público, seção 8) e a pasta `baseline/`, com o relatório e o código originais do baseline. Todo o resto está aqui.

---

## 2. Linha do tempo

| # | Etapa | Onde | Resultado principal |
|---|---|---|---|
| 1 | Leitura do repositório e escolha do desafio | Chat | Desafio 004; risco de dado sintético antecipado, com dois cenários |
| 2 | Exploração inicial | Chat | Primeiros sinais de dado simulado; erro de colinearidade pego e corrigido |
| 3 | Redesenho do fluxo | Chat | Versão inicial descartada → Ordens de Serviço curtas |
| 4 | OS-01 e OS-02 | Code | Base amostral; 693 segmentos, todos dentro do acaso |
| 5 | OS-03, 03b e 03c | Code | Patrocínio sem efeito; hipótese de fit rejeitada; robustez provada |
| 6 | Baseline | Chat separado | Mesma conclusão, menos embasamento; boas práticas incorporadas com crédito |
| 7 | OS-04 a OS-06 | Code | Sanidade, hashtags, efeito absoluto, tamanho de amostra, gráficos, lacunas do brief |
| 8 | Relatórios | Chat + OS-07 e 07b | Executivo (duas partes, espelhando o brief) e técnico, em md e PDF |
| 9 | Ferramenta | OS-08 a OS-10 | Decisor de Campanha; diluição detectada e corrigida; linguagem simples; tema escuro |
| 10 | Fechamento | OS-11 | Reprodução, commits, GitHub Pages e PR |

---

## 3. Registro de decisões (o porquê)


Esta seção registra **o porquê** de cada passo: o contexto, a decisão e quem decidiu. Os números e o detalhe técnico de cada execução estão na [seção 4](#4-log-de-execução-do-claude-code-o-como), e o texto exato de cada pedido ao Claude Code está na [seção 5](#5-ordens-de-serviço).

### 3.1 Planejamento

- **Leitura do repositório.** O Claude leu o README, os 4 desafios, o guia de submissão, o template e o CONTRIBUTING. Concluiu que o critério real é superar o baseline de IA e que o process log é eliminatório.
- **Escolha do desafio.** O Claude recomendou o 003 (Lead Scorer), pela aderência ao perfil. **Gabriel escolheu o 004 (Social Media).**
- **Risco antecipado.** Datasets de redes sociais no Kaggle costumam ser sintéticos, o que faz ruído parecer insight. Decisão: fazer um teste de sinal antes de qualquer análise, com dois cenários previstos:
  - A: há sinal, e a estratégia se ancora nos segmentos que se destacam;
  - B: ruído, e a entrega mostra o que os dados permitem e não permitem afirmar.
- **Sem custo no dataset.** Decisão: não inventar ROI.
- **Regras para o projeto inteiro:**
  - todo número sai de código executado;
  - diferença pequena não é insight;
  - uma entrega bem feita vale mais que várias pela metade.
- **Commits.** Todos no final, por decisão do Gabriel.

### 3.2 Exploração inicial no chat

A primeira olhada nos dados foi feita no próprio chat ([seção 6](#6-exploração-inicial-no-chat)) e já indicava o cenário B.

- **Erro da IA, corrigido no chat.** A primeira regressão "mostrou" efeitos grandes e muito significativos para vídeo e patrocínio. A checagem de colinearidade mostrou que era um artefato: colunas derivadas de outras. Sem elas, o efeito desaparece.
- **Gabriel: "ainda é cedo para concluir".** Antes de aceitar o cenário B, ele pediu um modelo com todas as colunas. O resultado confirmou a ausência de sinal.

### 3.3 Redesenho do fluxo de trabalho

- **Primeiro desenho (descartado):** um `CLAUDE.md` longo, pedindo ao Claude Code que refizesse tudo sozinho, de forma independente.
- **Decisão do Gabriel:** o raciocínio fica no chat; o Claude Code só executa **Ordens de Serviço** curtas, sem contexto estratégico. As regras contra a "espiral de erros" são: no máximo 2 tentativas por erro, sem mudar o escopo e sem interpretar resultados. O motivo: menos contexto no executor, menos desvio e menos erro em cascata.

### 3.4 Desenho do método

- **Regra de decisão fixada antes de ver os resultados:** ±10% vs. a média da plataforma, IC 95% por bootstrap, repetição em duas metades e n ≥ 100.
- **Gabriel: "análises isoladas não se somam".** "TikTok é melhor" + "19–25 é melhor" não garante que "TikTok para 19–25" seja melhor. Decisão: uma etapa de consolidação, com modelo preditivo e regressão com controles. A árvore de decisão substituiu o clustering, que agrupa sem olhar para o engajamento.
- **Ideia do Gabriel:** os modelos ficam nos bastidores; o Head vê só o resultado simples.

### 3.5 Interpretação das análises

- **OS-01, base amostral.** O Claude Code mostrou que `content_length` tem a mesma distribuição em vídeo, texto e imagem: não é duração.
  - **Erro da IA:** a exploração do chat havia criado faixas de "duração de vídeo" sem checar isso.
  - Decisão: eliminar qualquer análise de duração. O exemplo do próprio brief ("vídeos de 30–60s") depende de um campo que a base não tem.
  - As faixas pequenas de seguidores foram juntadas em "até 50K".
- **OS-02, benchmark.** Nenhum segmento se diferencia: cenário B confirmado.
  - O Gabriel ainda refletia sobre o corte de 10%. Os dados mostraram que nada passa nem de 3%, então a conclusão não depende do corte.
  - Decisão: manter 10% e registrar a análise de sensibilidade.
- **OS-03, patrocínio.** Sem efeito por todos os métodos.
  - **Erro de processo:** a OS foi rodada em dois modelos na mesma pasta, e o segundo reaproveitou o script do primeiro (números idênticos até no bootstrap). Gabriel confirmou o que aconteceu.
  - Decisão: um modelo por OS. Na comparação de qualidade, o primeiro modelo foi mais rigoroso e o segundo mais legível.
- **A hipótese do "29x".** O Gabriel propôs segmentar campanhas porque "creators de até 50K engajam 29x mais". O Claude apontou que o 29x é engajamento ÷ seguidores, um artefato do denominador: o engajamento absoluto é igual em todas as faixas.
  - A preferência por creators menores se manteve, mas pelo motivo certo: custo por engajamento.
  - Da mesma conversa saiu uma **hipótese nova do Gabriel: o fit entre patrocinador e tema do conteúdo**.
- **OS-03b, fit e audiência.** A hipótese de fit foi testada e não se sustentou. Fica registrada como hipótese rejeitada, não escondida. Observação: o dataset sorteia os patrocinadores, sem simular escolha por fit.
  - A persona "50+ | masculino | Reino Unido" passa em todos os testes individuais, mas é uma entre 126 testadas. Virou o exemplo didático de comparações múltiplas.
- **OS-03c, robustez.** O Gabriel pediu "100% de certeza". O Claude explicou que isso não existe e propôs provar três coisas:
  - o limite máximo do efeito;
  - que a base tinha poder para ver efeitos pequenos;
  - que o método encontra efeitos reais (controle positivo).

  Esse virou o principal diferencial técnico da entrega.
- **OS-04, complementos.** **Erro da IA:** o Claude tinha estimado "no máximo ~8 interações a mais por post", aplicando o pior efeito de comentários ao engajamento total. O número calculado por código é 2,6. A regra "todo número sai de código" pegou o erro.
- **OS-06, lacunas.** Ao mapear o brief item por item, faltavam por código o "alcance" do patrocinado vs. orgânico e a "audiência por tipo de conteúdo". Foram cobertos antes de fechar os relatórios.

### 3.6 Baseline

- **Como foi feito:** brief + CSV num chat separado do Claude, sem contexto, num único envio.
- **Objetivo (definição do Gabriel):** comparar **métodos**, não provar que a IA sozinha erra. A conclusão coincidiu, o que reforça a lógica. O que se compara é o embasamento: o baseline **afirma** a ausência de efeito, e este trabalho a **prova** (equivalência, poder de detecção, controle positivo).
- **Verificação:** as afirmações do baseline que ainda não tínhamos testado foram conferidas no CSV. Todas conferem.
- **Uso como revisor:** as boas práticas foram incorporadas com crédito (tabela de sanidade, hashtags com correção, teto por mídia paga, UTM e cupom, plano de 8 semanas).
  - Uma falha técnica dele foi corrigida na nossa versão: comparar cada hashtag com a base inteira, que contém o próprio grupo.
  - O veredito dele mistura "sem efeito" com "dados insuficientes". O nosso separa os dois.

### 3.7 Relatórios

- **Dois públicos:** um relatório executivo para o Head e um técnico para o avaliador.
- **Decisões do Gabriel sobre a primeira versão:**
  - ênfase no orgânico, com a frase "cada real pago em patrocínio compra zero engajamento adicional";
  - **o custo do time é irrelevante**, e saem as recomendações que dependiam dele (formato mais barato, uma peça para três redes);
  - gráficos gerados por código, a seção "o que mudaria esta conclusão" e um executivo mais curto.
- **Executivo em duas partes**, espelhando o brief (análise de performance e estratégia recomendada), com cada subpergunta respondida explicitamente.
- **PDF:** primeiro paginado. Depois, por decisão do Gabriel, **contínuo, sem quebras de página**, porque as quebras deixavam espaço em branco.
- **Erro da IA, achado na revisão do README:** o executivo dizia "204 combinações" formato × público. 204 são linhas (68 combinações × 3 métricas). Corrigido para 68.

### 3.8 Ferramenta

- **Desenho combinado.** A ideia do Gabriel (template, upload, aba que ensina, insights que aprovam ou barram) foi unida à do Claude (veredito em 3 níveis, avaliador de patrocínio, planejamento de teste).
- **Uso definido pelo Gabriel:** "quero lançar uma campanha e analisar o cohort passado para saber em que me basear". Daí vieram o resumo da campanha, o filtro de período e as colunas opcionais de conversão e custo.
- **Backend:** a mesma estatística da análise, no navegador, sem IA e sem servidor, com o motor separado da interface para poder ser validado contra o Python.
- **Erro da IA, achado pela revisão do Claude.** O Claude testou a ferramenta num navegador automatizado com uma base de **efeito conhecido** (vídeo com +30% de likes). A ferramenta escondia o vencedor: comparava o segmento com a média que inclui ele mesmo. Na base do desafio isso não aparecia, porque nada tem efeito; com dados reais, seria fatal. A correção (comparar com o resto) foi feita antes de construir o resto da ferramenta.
- **Gabriel: o usuário real tem dificuldade com termos técnicos.** Toda a tela foi reescrita com textos exatos definidos no chat, uma lista de palavras proibidas verificada por script e um tema escuro. O celular ficou fora do escopo, também por decisão dele.
- **OS-10b não executada.** A revisão encontrou ajustes finos de layout; o Gabriel avaliou que o resultado já estava bom e priorizou o fechamento.

### 3.9 Fechamento

- **O README foi escrito no chat** (é o documento mais lido pelo avaliador), seguindo o template do G4. A OS-11 só confere, reproduz e publica.
- **Process log num arquivo único**, sem informação duplicada: o porquê nesta seção, o como na seção 4. Só ficam fora dele a evidência bruta: os arquivos originais do baseline e a conversa completa, num link público.
- **Risco evitado.** A montagem deste documento revelou que a OS-11 continha sequências de caracteres que o GitHub Pages interpreta como código. Isso derrubaria a publicação da ferramenta. O texto foi reescrito, e todos os `.md` foram varridos.
- **Validação herdada.** Desde a correção do motor na OS-09, o `validar_engine.mjs` compara o lift com a definição antiga e acusa diferença. Decisão: desativar só essa comparação, que deixou de valer (a definição nova é validada pelo `validar_os09.mjs`), para o `run_all` refletir o estado real.

### 3.10 Em resumo

**Onde a IA errou e como foi corrigido**

| Erro | Quem detectou | Como |
|---|---|---|
| Regressão com efeitos falsos por colinearidade | Claude (chat) | Checagem do número de condição |
| Faixas de "duração" sobre um campo que não é duração | Claude Code (OS-01) | Distribuição igual em todos os formatos |
| Mesma OS em dois modelos na mesma pasta | Claude (chat) | Números idênticos até no bootstrap |
| "~8 interações" em vez de 2,6 | Regra "todo número sai de código" (OS-04) | Cálculo por script |
| Falsos alarmes nas caudas (empates em métricas inteiras) | Claude Code (OS-03c) | Comparação com a taxa realmente realizada pelo corte |
| Ferramenta escondendo vencedores (diluição) | Claude (revisão com efeito conhecido) | Comparar com o resto, revalidado |
| "1 post por versão", jargão na tela | Claude (revisão lendo como o usuário) | Mínimo de 30; linguagem simples verificada por script |
| "204 combinações" em vez de 68 | Claude (revisão do README) | Correção nos `.md` e regeneração dos PDFs |

**O que o Gabriel acrescentou**
- a escolha do desafio 004;
- "ainda é cedo para concluir";
- "análises isoladas não se somam" (a etapa de consolidação);
- a hipótese de fit, testada e rejeitada;
- "quero 100% de certeza" (a OS de robustez);
- o objetivo do baseline: comparar métodos;
- a ênfase no orgânico e a exclusão do custo do time;
- a ferramenta pensada para o usuário real (cohort passado, linguagem simples);
- o fluxo chat + Ordens de Serviço;
- a decisão de não rodar a OS-10b;
- o process log num arquivo único.


---

## 4. Log de execução do Claude Code (o como)

Escrito pelo Claude Code ao fim de cada OS: o que foi feito, os erros encontrados e como foram resolvidos, e as validações independentes (números recalculados fora do script). Os resultados aparecem como o executor os reportou, sem interpretação; a interpretação está na seção 3.


### OS-01 — Base amostral (2026-10-12)

- **Feito:** criado `solution/analysis/os01_base_amostral.py`, que descreve a base (52.214 linhas × 27 colunas) nas 6 seções pedidas: visão geral, distribuição das métricas, volume por segmento, tamanho dos cruzamentos, consistência e relação entre métricas. Saídas: 17 .csv + `resumo_os01.md` em `solution/outputs/os01/`.
- **Setup:** o CSV não estava em `datasets/` — foi copiado de `~/Downloads/social_media_dataset.csv`. Criado o venv `.venv` e instaladas as dependências do `requirements.txt`.
- **Erro 1 (ambiente):** o diretório raiz do projeto não é listável pelo processo Python (macOS nega `listdir` em `/Users/gabriel/Documents/new-G4`, embora os subdiretórios funcionem). Isso colocava uma entrada inacessível no `sys.path` e quebrava qualquer `import` (`PermissionError: Operation not permitted`), inclusive o `ensurepip` do venv. **Causa:** cwd igual à raiz protegida. **Solução:** criar o venv e rodar o script com o cwd em um subdiretório (`solution/analysis`). Por isso também o `pip install -r requirements.txt` falhou (arquivo na raiz) e os pacotes foram instalados por nome, nas mesmas versões mínimas do `requirements.txt`.
- **Erro 2 (meu, corrigido):** a primeira versão reportava 31 colunas e os nulos das 4 colunas derivadas por mim (`engajamento`, `taxa_engajamento`, `faixa_seguidores`, `faixa_duracao`); e o % da faixa de duração usava as 52.214 linhas como base, contando os não-vídeo como nulo. Corrigido para descrever as 27 colunas originais e calcular a faixa de duração sobre os 31.500 posts de vídeo.
- **Ressalva de escopo:** a OS pede faixa de duração, mas não existe campo de duração na base. Usei `content_length` por ser o único candidato; a distribuição dele é idêntica para `text`, `image`, `mixed` e `video`, o que está registrado como ponto suspeito nº 5 do resumo em vez de ser tratado como duração confirmada.

### OS-02 — Benchmark por segmento (2026-10-12)

- **Feito:** criado `solution/analysis/os02_benchmark.py`. Calcula o índice por post (valor / média da métrica na plataforma), o lift de 693 segmentos em 4 níveis para `taxa_engajamento`, `shares` e `comments_count`, com IC 95% bootstrap (1.000 reamostragens percentil), teste de repetição em duas metades (divisão única, seed 42) e teste contra o acaso (200 permutações do índice dentro de cada plataforma). Saídas: 9 .csv + `resumo_os02.md` em `solution/outputs/os02/`. Runtime ~12s.
- **Ajustes da OS aplicados:** faixas de seguidores em 4 níveis (até 50K, 50–100K, 100–500K, 500K–1M); `content_length` e faixas de duração não usados; novas derivadas `n_hashtags` (0–5, nulo = 0), `periodo_dia` e `dia_semana`.
- **Erros:** nenhum erro de execução. O script rodou de primeira. Única adaptação de ambiente: o cwd precisa ser `solution/analysis` (mesma restrição de `listdir` na raiz registrada na OS-01).
- **Resultado principal (reportado, não interpretado):** todos os 693 segmentos têm lift entre 0,98 e 1,02 — as 72 contagens de limiar (>1,03/1,05/1,10 e <0,97/0,95/0,90) são **todas zero**. No teste contra o acaso, 24 de 24 comparações ficam dentro do acaso, com os extremos observados sistematicamente menos extremos que os da permutação. O teste de repetição acerta o lado em 41%–48% dos casos, contra 50% esperados por sorteio. Registrado como pontos suspeitos 1 a 4 do resumo.
- **Validação:** 4 lifts e 1 IC conferidos por cálculo independente fora do script (`content_type=text`: lift 1,000485, IC bootstrap 0,999831–1,001102 vs. normal 0,999824–1,001147); conferem.

### OS-03 — Patrocínio e validação geral (2026-10-12)

- **Feito:** criado `solution/analysis/os03_patrocinio_validacao.py` com os 7 blocos: comparação patrocinado/orgânico estratificada (141 de 240 estratos com 30+30 mínimo, bootstrap estratificado), OLS com HC3 e 45 controles, efeito por faixa de seguidores (estratos platform × content_category, mínimo 20+20), lifts dos detalhes de patrocínio contra a média dos patrocinados da plataforma, engajamento entregue por faixa × patrocínio, volume patrocinado e validação geral com `HistGradientBoostingRegressor` (CV 5 partes + importância por permutação). Saídas: 8 .csv + `resumo_os03.md` em `solution/outputs/os03/`. Runtime ~3 min.
- **Reaproveitamento da OS-02:** faixas de seguidores, `n_hashtags`, `periodo_dia`, `dia_semana` e a divisão em duas metades foram reconstruídos com a mesma lógica dentro do script da OS-03 (A = 26.107, B = 26.107, idênticas às da OS-02); o script da OS-02 não foi alterado.
- **Decisão registrada:** no Bloco 2, `n_hashtags` entrou como categórica (6 níveis), junto com os outros controles categóricos, em vez de numérica linear. Número de condição 17,41, sem colinearidade problemática.
- **Erro/aviso (1 investigação, não houve correção de código):** o `f_pvalue` com covariância HC3 dispara `RuntimeWarning: divide by zero/overflow/invalid value in matmul` no `np.linalg.pinv` chamado pelo `statsmodels`. **Causa:** escala minúscula das entradas da matriz HC3 (~1e-18 para `taxa_engajamento`), não erro de especificação. **Verificação:** os três p-valores do teste F (0,668 / 0,867 / 0,874) conferem com o F clássico calculado à mão a partir do R² e dos graus de liberdade. Aviso mantido visível, sem `try/except` nem supressão.
- **Validação independente:** efeito do Bloco 1, cobertura dos estratos, lift do Bloco 4 (`disclosure_type=explicit`), n/média/mediana/p10/p90 e mediana de engajamento por seguidor do Bloco 5 e os percentuais do Bloco 6 foram recalculados fora do script com groupby puro; todos conferem. O IC bootstrap do Bloco 5 (2009,07–2010,66) foi comparado ao IC normal (2009,08–2010,76).
- **Resultado principal (reportado, não interpretado):** nenhum efeito de patrocínio em nenhum dos três métodos — 0 de 3 IC no Bloco 1, 0 de 12 no Bloco 3 e 0 de 51 no Bloco 4 excluem 1; coeficiente de `is_sponsored` com p 0,40–0,79. A regressão tem R² ajustado negativo e p-valor do teste F de 0,67 a 0,87, e o modelo preditivo tem R² negativo nos 4 alvos com MAE pior que o da média. Registrado nos pontos suspeitos 1 a 8 do resumo.

### OS-03b — Fit de patrocínio e audiência (2026-10-12)

- **Feito:** criado `solution/analysis/os03b_fit_audiencia.py`. Parte A (só patrocinados, 22.314 posts): volume com/sem fit, comparação estratificada fit vs. sem fit (platform × content_category × faixa_seguidores, mínimo 20+20) e tabela sponsor_category × content_category com lift contra a média dos patrocinados da plataforma. Parte B (todos os posts): 126 personas (idade × gênero × local), 3 conjuntos de audiência × conteúdo (51 segmentos) e audiência × patrocínio nos 17 valores das 3 variáveis de audiência. Saídas: 7 .csv + `resumo_os03b.md` em `solution/outputs/os03b/`. Runtime ~6s.
- **Reaproveitamento:** índice por post, lift, IC bootstrap percentil (1.000), divisão em duas metades (seed 42; A = 26.107, B = 26.107, idênticas às da OS-02 e OS-03), teste contra o acaso (200 permutações dentro de cada plataforma) e o método de estratos com bootstrap estratificado foram replicados dentro do novo script. Os scripts das OS anteriores não foram tocados.
- **Erros:** nenhum erro de execução; rodou de primeira. Um único ajuste de formatação: o separador de segmentos (`" | "`) colidia com o pipe das tabelas markdown do resumo e quebrava as colunas — o pipe passou a ser escapado na geração do .md (os .csv não foram afetados). O `resumo_os03b.md` é gerado pelo próprio script, então todo número do resumo sai de código.
- **Validação independente:** recalculados fora do script com groupby puro o total com fit (7.439; 33,34%), o efeito e a cobertura de A2 (42 estratos, 21.035 posts, efeito 1,000339, 54,76% com razão > 1), o lift de A3 `cosmetics | beauty` (1,000362), o lift da persona `50+ | male | UK` (n = 123; 1,005435) e o efeito de B3 para `audience_gender_distribution = unknown` (1,001414); todos conferem.
- **Resultado principal (reportado, não interpretado):** o padrão das OS-02 e OS-03 se repete. Nenhum dos 5 conjuntos passa no teste contra o acaso (0 de 15 comparações), as 72 contagens de limiar (>1,03/1,05/1,10 e <0,97/0,95/0,90) de B1 e B2 são todas zero, e os IC de A2 (0 de 3) e de B3 (3 de 51) quase nunca excluem 1. A proporção de fit é definida pela regra da tabela, não pelos dados: `sponsor_category` está praticamente uniforme dentro de cada `content_category` (fit = 16,84% em beauty, 33,16% em tech, 49,99% em lifestyle). A2 descartou 18 de 60 estratos (1.279 posts, 5,73%) e B1 descartou 34 de 160 personas (2.157 posts) por n < 100.

### OS-03c — Robustez da conclusão (2026-10-12)

- **Feito:** criado `solution/analysis/os03c_robustez.py` com os 5 blocos: equivalência (lift, IC 95% e IC 90% dos 105 segmento × métrica, efeito máximo plausível e testes de ±1% e ±2%), MDE com poder 80% e significância 5%, controle positivo por injeção (3a: 8 variáveis × 3 métricas × 1,01/1,02/1,05; 3b: busca de 4 variáveis com n ≥ 100 e 200 permutações), caudas (cortes top 10%/top 1%/bottom 10% por plataforma, IC de Wilson e KS) e tendência no tempo (média mensal, OLS com HC3 nos 25 meses e primeiro × último ano por plataforma). Saídas: 7 .csv + `resumo_os03c.md` em `solution/outputs/os03c/`. Runtime ~15s.
- **Reaproveitamento:** índice por post, lift, bootstrap percentil (1.000), divisão em duas metades (seed 42; A = 26.107, B = 26.107, idênticas às da OS-02, OS-03 e OS-03b) e a busca do Nível 4 da OS-02 (128 de 240 segmentos com n ≥ 100) foram replicados dentro do novo script; os scripts anteriores não foram tocados. Toda injeção do Bloco 3 foi feita em cópia da base (`df.copy()` com a coluna substituída por um array novo); a base original não foi alterada.
- **Desvios de entrega (3):** (1) o Bloco 4 saiu em 2 .csv em vez de 1 — `bloco4_caudas.csv` mais `bloco4_cortes_plataforma.csv`, porque a OS pede os cortes de cada plataforma e eles não cabem na tabela por segmento; (2) acrescentadas as colunas `*_taxa_base_plataformas_pct` e `*_exclui_taxa_base` ao Bloco 4, pela razão do ponto abaixo; (3) o Bloco 5 saiu em um único .csv em formato longo, com a coluna `tabela` separando média mensal, tendência e primeiro × último ano.
- **Erros:** nenhum erro de execução; o script rodou de primeira. Dois erros de shell (`cd: no such file or directory`) por o cwd da ferramenta já estar no diretório de destino, resolvidos rodando o comando sem o `cd`. Duas correções preventivas no meu próprio código antes da primeira execução: troquei `d.loc[d.index[pos], m]` por cópia em numpy (risco de alinhamento de índice do pandas) e troquei o acesso por chave float do `quantile([...]).unstack()` por três chamadas separadas.
- **Validação independente:** recalculados fora do script o lift e os dois IC de `content_type = mixed`/comments_count (1,001819; IC bootstrap 0,999929–1,003636 vs. normal 0,999888–1,003750), o MDE de um segmento (0,3996%), a previsão de diluição do 3a (1,028033 previsto vs. 1,027996 medido), o IC de Wilson de uma cauda (11,0453%; 10,4545–11,6652), a inclinação geral de `taxa_engajamento` (−0,003434, conferida com `scipy.linregress`), o lift do 3b (1,045982) e a razão primeiro × último ano do Instagram (1,002945); todos conferem.
- **Resultado principal (reportado, não interpretado):** 105 de 105 segmento × métrica são equivalentes a ±1% e a ±2%, com efeito máximo plausível de 0,3799% no pior caso; o MDE vai de 0,0599% a 0,3996%, ou seja, a base detectaria efeitos bem menores que 1% se existissem. O controle positivo detecta 72 de 72 cenários do 3a e 2 de 2 do 3b (posição 1 de 128 no ranking, acima do p95 do acaso). Nas caudas, 88 de 315 IC de Wilson excluem os 10%/1% nominais, mas 86 são artefato de empates nas métricas inteiras (o corte por quantil realiza 10,15%–11,19%); contra a taxa realizada sobram 6 de 315 (1,9%). KS com p < 0,05 em 4 de 105. No tempo, 1 de 36 tendências tem p < 0,05 (YouTube/shares, +0,1975% por ano, p = 0,0397) e 1 de 15 razões primeiro × último ano exclui 1 (Instagram/comments_count, 1,002945). Registrado nos 11 pontos suspeitos do resumo.

### OS-04 — Complementos (2026-10-12)

- **Feito:** criado `solution/analysis/os04_complementos.py` com os 4 itens: tabela de sanidade (27 indicadores), hashtags com teste t de Welch e correção de Benjamini-Hochberg (FDR 5%) por métrica, conversão do efeito máximo plausível da OS-03c em unidades absolutas por post e tamanho de amostra para 6 CV × 4 lifts. Saídas: 4 .csv + `resumo_os04.md` em `solution/outputs/os04/`. Runtime ~30s. Nenhum script de OS anterior foi alterado; a OS-03c entrou só como leitura de `bloco1_equivalencia.csv`.
- **Decisões de execução:** (1) no item 2 o universo é só quem tem `hashtags` preenchido (43.471 de 52.214 posts; 8.743 nulos fora), e o grupo "sem a hashtag" é o resto desse universo, não a base inteira; (2) a correção BH foi aplicada com `statsmodels.stats.multitest.multipletests(method="fdr_bh")`, separadamente nas 970 hashtags de cada métrica; (3) o `resumo_os04.md` é gerado pelo próprio script, então todo número do resumo sai de código executado; (4) o item 2 saiu em 1 .csv com as 1.940 linhas hashtag × métrica (o resumo por métrica e as top 10 estão no .md, calculados no script), mantendo um .csv por item.
- **Erros:** nenhum erro de execução; o script rodou de primeira. Um problema meu de edição: escrevi o separador de milhar do formatador pt-BR como espaço não-separável (U+00A0), o que fez o `str.replace` seguinte falhar; corrigido trocando por milhar com ponto e decimal com vírgula, igual aos resumos anteriores. Três trechos do "Pontos suspeitos" foram reescritos porque a redação não batia com o número calculado (variância ÷ média, efeito absoluto por métrica e os indicadores 8 e 9).
- **Validação independente:** recalculados fora do script a mediana de views da faixa 50–100K (10.099; n = 2.597), o V de Cramér por χ² na mão (0,011294), o lift, o p de Welch e o q-valor BH da hashtag de maior lift em shares (`still`: n = 136; lift 1,016026; p 0,002613; q 0,422463), o CV do engajamento (0,022329) e dois n do item 4 (CV da base/lift 5% = 4; CV 0,7/lift 10% = 769), as duas conversões absolutas do item 3 (0,1292% × 2.010,3084 = 2,5973; 0,3447% × 300,0184 = 1,0342) e os indicadores 5, 6, 8 e 9; todos conferem.
- **Resultado principal (reportado, não interpretado):** o item 1 mostra views entre 9.676 e 10.551 e engajamento entre 1.833 e 2.189, variância ÷ média entre 0,9906 e 1,0030 nas quatro métricas, correlação likes × views de 0,000761 (Spearman 0,001490), log10(seguidores) × log10(views) de 0,005644, V de Cramér de 0,011294 e 18.005 `sponsor_name` distintos em 22.314 posts patrocinados. No item 2, 118 de 1.940 testes dão p < 0,05 sem correção (97,0 esperados por acaso) e **0 sobrevivem à correção BH** nas duas métricas, com lifts entre 0,984085 e 1,016026. No item 3, o maior efeito máximo plausível da base inteira é 0,7599 comentário, 1,0342 share e 2,5973 interação por post. No item 4, com os CV da base o n por variante fica entre 1 e 32, contra 25 a 6.272 nos cenários fixos de 0,5 a 1,0. Registrado nos 9 pontos suspeitos do resumo.

### OS-05 — Gráficos para os relatórios (2026-10-12)

- **Feito:** criado `solution/analysis/os05_graficos.py`, que gera os 4 PNG (150 dpi, 10 × 6 pol, fundo branco, cinza `#9A9A9A` + vermelho `#C0392B`) e o `resumo_os05.md` em `solution/outputs/os05/`. Gráficos 1 e 3 recalculam os dados do CSV com a lógica das OS de origem (Bloco 5 da OS-03; Nível 4 da OS-02 mais o sorteio do Bloco 3b da OS-03c); gráficos 2 e 4 só leem `os02/nivel1..4.csv` e `os03c/bloco1_equivalencia.csv`. Runtime ~9s. Nenhum script anterior foi tocado.
- **Reprodução conferida:** as 8 médias e os 8 n do gráfico 1 batem casa a casa com `bloco5_engajamento_por_faixa.csv`; o sorteio do Bloco 3b caiu no mesmo segmento (`Bilibili | video | beauty | 50-100K`, n = 137, entre 29 candidatos) e o lift com +5% deu 1,045982, igual ao da OS-03c; os 693 segmentos do gráfico 2 fecham com 52 + 260 + 253 + 128 dos níveis 1 a 4.
- **Duas diferenças esperadas, reportadas no resumo:** os IC bootstrap do gráfico 1 mudam na 1ª/2ª casa decimal e o p95 do acaso do painel 1 do gráfico 3 deu 1,006675 contra 1,006406 na OS-02 (0,03%). Causa nos dois casos: nas OS de origem o gerador seed 42 chega nesses blocos já consumido pelos blocos anteriores, e aqui começa do zero. Mesma lógica, mesmo número de reamostragens/permutações; só o ponto do fluxo aleatório é outro. Não foi "corrigido" porque não é erro.
- **Erros:** nenhum erro de execução; o script rodou de primeira. Três ajustes de apresentação depois de olhar os PNG: (1) escrevi os textos dos gráficos sem acento na primeira versão e refiz com acentuação, já que os títulos da OS são fixos e precisam sair idênticos; (2) o gráfico 2 saiu com os pontos ocupando a altura toda da figura, parecendo uma coluna vertical — troquei por um eixo baixo e largo (`add_axes`, 36% da altura) com dispersão vertical de ±0,33, para virar a faixa horizontal que a OS pede; (3) o rótulo "Maior resultado esperado por acaso" estava em 10,5 pt, abaixo do mínimo de 11 pt do padrão visual.
- **Títulos fixos conferem, todos os 4 (nenhum precisou ser alterado):** gráfico 2, 693 segmentos com desvio máximo de 0,4772% da média (0 fora de ±2% e 0 fora de ±10%); gráfico 4, maior efeito máximo plausível de 0,1292% (`audience_age_distribution`), 0 variáveis acima de 0,15%; gráfico 3, o segmento sorteado sai de 128º de 128 (lift 0,996816) para 1º de 128 (lift 1,045982); gráfico 1, as 8 médias ficam entre 2.009,9 e 2.010,8 interações (amplitude de 0,05%). Consequência visual registrada nos 5 pontos suspeitos: as barras do gráfico 1 ficam idênticas e com barras de erro invisíveis (IC mais largo = 0,24% da altura do eixo), e a nuvem do gráfico 2 vira uma mancha estreita sobre o 0%.

### OS-06 — Lacunas finais: alcance e formato × audiência (2026-10-12)

- **Feito:** criado `solution/analysis/os06_lacunas.py`. Parte 1 (métrica `views`): 1a comparação simples patrocinado × orgânico (n, média, IC bootstrap, mediana e razão das médias com IC), 1b comparação estratificada (platform × content_category × content_type × faixa_seguidores, mínimo 30+30, bootstrap estratificado), 1c efeito por faixa de seguidores (estratos platform × content_category, mínimo 20+20) e 1d mediana de views nas 8 células faixa × is_sponsored. Parte 2: lift de 68 segmentos nos 3 conjuntos content_type × audiência (idade, gênero, local) para `taxa_engajamento`, `shares` e `comments_count`, com IC bootstrap, duas metades e teste contra o acaso por conjunto. Saídas: 8 .csv + `resumo_os06.md` em `solution/outputs/os06/`. Runtime ~3,5s.
- **Reaproveitamento:** faixas de seguidores, índice por post, lift, IC 95% bootstrap percentil (1.000), divisão em duas metades (seed 42; A = 26.107, B = 26.107, idênticas às das OS-02 a OS-03c), método de estratos com bootstrap estratificado e teste contra o acaso (200 permutações dentro de cada plataforma) foram replicados dentro do novo script. Nenhum script de OS anterior foi tocado.
- **Decisões de execução:** (1) o .csv de 1a saiu em formato longo, com três linhas (patrocinado, orgânico, razão das médias) e uma coluna `valor`, porque média e razão não cabem na mesma coluna semântica; (2) 1d levou `media_views` junto da mediana pedida, para a célula ser comparável à Parte 1a; (3) a cobertura dos segmentos da Parte 2 e a distribuição dos lifts saíram em .csv próprios, além do .csv por conjunto; (4) o `resumo_os06.md` é gerado pelo próprio script, então todo número do resumo sai de código.
- **Erros:** nenhum erro de execução; o script rodou de primeira. Dois ajustes só de apresentação do resumo, sem recálculo: `pct_estratos_razao_maior_1` saía com 6 decimais (50,350000) e passou para 2; e o ponto suspeito 9 dizia "nenhum extremo real" enquanto o próprio número mostrava 1 de 18 comparações fora do acaso — a redação foi corrigida e passou a nomear a exceção a partir da tabela. Ambiente: `python` não existe no PATH, os comandos usam `.venv/bin/python`.
- **Validação independente:** recalculados fora do script com groupby puro as médias e medianas de views dos dois grupos (10.100,4484 e 10.100,1601; razão 1,000029; medianas 10.100 nos dois), a cobertura e o efeito de 1b (141 de 240 estratos, 49.487 posts, 1,000054, 50,35% com razão > 1), os quatro efeitos de 1c (0,999723 / 1,000154 / 1,000071 / 1,000013), as 8 medianas de 1d e o lift de `video | UK` em taxa_engajamento (1,000421; n = 3.956); todos conferem.
- **Resultado principal (reportado, não interpretado):** em alcance, patrocinado e orgânico são indistinguíveis — razão simples 1,000029 (IC 0,999868–1,000195), efeito estratificado 1,000054 (IC 0,999869–1,000208), 0 de 4 faixas com IC excluindo 1 e diferença máxima de mediana de 3 views dentro de uma faixa (sobre ~10.099). 1b descartou 99 de 240 estratos (2.727 posts, 5,22%). Na Parte 2 nenhum segmento ficou fora por n < 100 (68 de 68 mantidos) e as 204 linhas segmento × métrica têm lift entre 0,994353 e 1,007754, com as 54 contagens de limiar (>1,03/1,05/1,10 e <0,97/0,95/0,90) todas zero e 11 de 204 IC excluindo 1. **Único caso fora do acaso em toda a OS:** maior lift de `comments_count` em content_type × audience_age_distribution, 1,007754 contra p95 do acaso de 1,007570 (1 de 18 comparações). Registrado nos 10 pontos suspeitos do resumo.

### OS-07 — PDF dos relatórios (2026-10-12)

- **Feito:** criado `solution/analysis/os07_pdf.py`, que converte os dois `.md` em HTML com `markdown` 3.9 (extensões `tables` e `fenced_code`), resolve os `src` das imagens para caminho absoluto `file://` dentro do script, aplica o CSS da OS (A4, margens 2 cm, 10,5 pt, entrelinha 1,45, H1/H2/H3 em 18/14/12 pt, linha `#C0392B` sob os H1, tabelas com `#DDDDDD`/`#F2F2F2`/`#FAFAFA`) e imprime pelo **Chrome 154.0.8037.99 headless** (Opção A). Saídas: `relatorio_executivo.pdf` (7 páginas) e `relatorio_tecnico.pdf` (14 páginas) em `solution/report/`, mais `solution/outputs/os07/resumo_os07.md`. O HTML fica em pasta temporária e é apagado. Os `.md` não foram tocados; `markdown>=3.4` entrou no `requirements.txt`.
- **Erro 1 (ambiente, resolvido):** o Chrome headless escreve o PDF mas **não encerra** nesta máquina — fica vivo e dispara o GoogleUpdater, travando o `subprocess.run`. Duas execuções ficaram penduradas e a segunda conversão nunca começou. **Causa:** o processo não sai sozinho após o `--print-to-pdf`. **Solução:** trocar por `Popen`, ler o stderr até a linha "bytes written to file" e encerrar o processo; o arquivo já está completo nesse ponto (as duas contagens de páginas conferem).
- **Verificação:** páginas contadas por duas vias no próprio PDF (objetos `/Type /Page` e `/Count` do nó `/Pages`): 7 e 14, batem. Imagens: 2 no executivo e 4 no técnico, todas existentes e embutidas **uma única vez** cada (1500×900), ou seja, nenhum gráfico foi fatiado por quebra de página — os 4 objetos de imagem extras do técnico são os bitmaps do emoji ✅. Quebras de página inseridas: 3 no executivo e 8 no técnico, como pedido.
- **Verificação visual incompleta (ressalva principal):** não há rasterizador de PDF na máquina — `pdftoppm` não instalado (sem Homebrew), `cupsfilter` falha (`cgpdftoraster` status 2), `sips` só converte a página 1 e o Chrome headless fotografa o PDF em branco. Instalar PyMuPDF foi oferecido e recusado pelo Gabriel, então **só a página 1 de cada PDF foi olhada** (ambas corretas: margens, linha vermelha sob o H1, tabelas, citação em bloco, sem texto cortado ou sobreposto). As outras 19 páginas não foram inspecionadas.
- **Pontos reportados, não alterados:** (1) sem rodapé "Página X de Y" — o `--print-to-pdf` não expõe rodapé configurável por linha de comando e o Chrome não suporta `counter(page)` em margin box, caso previsto pela própria OS; (2) o cabeçalho de duas linhas dos dois relatórios vira texto corrido, porque o Markdown padrão junta linhas do mesmo parágrafo e a OS fixou só as extensões `tables` e `fenced_code` — nenhuma palavra mudou, mas a quebra original se perde; corrigir exigiria mudar a extensão ou o `.md`, então ficou como decisão do Gabriel.

### OS-07b — PDF contínuo, sem quebras de página (2026-10-12)

- **Feito:** reescrito `solution/analysis/os07_pdf.py` para gerar PDFs de **uma única página contínua** (largura A4, altura do conteúdo), substituindo o layout paginado da OS-07. Saídas em `solution/report/`: `relatorio_executivo.pdf` (210,2 × 1.457,4 mm), `relatorio_tecnico.pdf` (210,2 × 2.495,2 mm) e o novo `relatorio_completo.pdf` (210,2 × 3.942,7 mm), este com a divisória vermelha `#C0392B` + título "Relatório técnico" entre os dois documentos. Mais `solution/outputs/os07/resumo_os07b.md`. Os PDFs antigos foram substituídos (mesmos nomes), então não ficaram dois formatos.
- **Método:** Opção A — **Playwright 1.60.0** com `channel="chrome"` sobre o Chrome 154.0.8037.99 já instalado (nenhum navegador baixado); altura medida por `document.documentElement.scrollHeight` depois de `document.fonts.ready` e do carregamento das imagens; `page.pdf(width="210mm", height=altura+40px, print_background=True)`. A Opção B (5000mm + pdfplumber + pypdf) não foi necessária. `playwright>=1.40` entrou no `requirements.txt`. Removidas todas as quebras forçadas (`page-break`, `break-before`) e aplicado o ritmo vertical em px da OS.
- **Decisão de execução:** as margens de 1,5 cm / 2 cm foram embutidas no HTML (`body { padding }`) em vez de passadas ao `page.pdf`, para a medição na tela bater exatamente com a impressão e não haver refluxo — é o que garante o "exatamente 1 página". Também zerei a margem superior do primeiro elemento e do elemento logo após a divisória, senão a margem de 32 px do H1 somaria à margem da página (89 px no topo) e à divisória (72 px), criando o espaço vazio que a OS manda eliminar.
- **Erros:** nenhum erro de execução; o script rodou de primeira. Um ajuste de verificação: a primeira versão contava objetos de imagem dentro do PDF e acusava 4 para as 6 imagens do completo — **não era perda**, é o Chrome deduplicando os gráficos 01 e 02, que aparecem nos dois relatórios. A conferência passou a ser feita pelo DOM (arquivo, tamanho natural, tamanho renderizado e posição de cada `<img>`), que confirma 2, 4 e 6 imagens renderizadas.
- **Verificação:** os 3 PDFs têm **1 página** cada (objetos `/Type /Page`; altura lida do `/MediaBox`). Imagens 2/4/6, todas carregadas e a 643 px = os 170 mm de largura útil. Listas: nos 4 pontos pedidos há `</p>` seguido de `<ul>` e **0 parágrafos** engoliram itens de lista. Visual: cada documento foi renderizado inteiro em PNG (`screenshot(full_page=True)`, mesmo motor e mesma largura da impressão) e olhado em 5 + 9 partes, mais a divisória — sem tabela cortada, texto sobreposto ou título órfão. Varredura de faixas brancas com Pillow: as únicas acima de 60 px são o topo (61 px), o rodapé (~108 px = margem + os 40 px de folga pedidos) e **~100 px acima e abaixo do `grafico_02`, que são brancos internos do próprio PNG** (na OS-05 o eixo ocupa 36% da altura da figura), não do layout — reportado e não alterado, por estar fora do escopo desta OS.

### OS-08 — Ferramenta: núcleo do decisor (2026-10-12)

- **Feito:** criados `solution/tool/src/engine.js` (motor estatístico puro, sem DOM: qnorm de Acklam, índice por plataforma, lift/dp/ep, Bonferroni, teste de equivalência, patrocínio estratificado, saúde da base, dimensionamento de A/B), `src/template.html` (tokens de design, abas, CSS de impressão), `src/ui.js` (vereditos, briefing, filtros, upload de CSV com PapaParse), `build_tool.py` (codifica as categóricas, embute os dados compactos e junta os três arquivos) e `validar_engine.mjs`. Saída: `solution/tool/decisor.html`, **2,87 MB**, autossuficiente (meta da OS: 6 MB). Mais `solution/outputs/os08/resumo_os08.md` e as capturas de 1280 px e 375 px.
- **Validação:** `validar_engine.mjs` roda o `engine.js` no Node contra os .csv do Python e sai com código 0. 10a.1: 33 segmentos, maior diferença de lift 4,57e-7 (tol. 1e-6) e de limite de IC 95% 7,05e-5 (tol. 0,001). 10a.2: efeito do patrocínio 0,999874 vs 0,999877 (taxa) e 1,000053 vs 1,000054 (views), com 240/141 estratos e 49.487/21.174/28.313 posts exatos. 10b: os 5 vereditos esperados conferem (patrocínio Barrado, 0 positivos, 0 negativos, "Nenhum público comprovado", saúde com 4 alertas). 10d: 52.214 → 6.403 posts, k 111 → 93, estratos 141 → 24.
- **Erros corrigidos (de interface, um por vez):** `.campo{display:flex}` vencia o atributo `[hidden]` e os campos de data apareciam sempre — resolvido com uma regra global `[hidden]{display:none!important}`; o `<h2>` do briefing transbordava a 375 px porque como item flex tinha `min-width:auto` — resolvido com `min-width:0` + quebra de palavra; e `montarFiltroPlataformas()` religava os ouvintes de clique a cada upload, o que faria o dropdown abrir e fechar na mesma ação — separado em `ligarFiltroPlataformas()` (uma vez) e a remontagem só da lista.
- **Ambiente:** o `navigate` do MCP do Chrome quebra URLs `file://`, então a verificação interativa foi feita com um servidor estático local em `127.0.0.1:8731` (já encerrado). Três checagens de texto na tela deram falso negativo por usarem `innerText`, que ignora `<details>` fechado; relidas por `textContent`, os textos estão corretos — nada foi alterado no produto.
- **Reportado, não ajustado (regra 5):** os 4 testes de saúde da base disparam (corr. log-seguidores × log-views 0,005644; corr. likes × views 0,000761; variância ÷ média de views 0,990585; 0,0% de fracassos); os 220 segmentos caem todos em "Sem efeito comprovado" e nenhum inconclusivo, porque dp do índice ≈ 0,0245 deixa o IC de equivalência (±0,0004) muito dentro de [0,90; 1,10]; o A/B do briefing pede "pelo menos 1 post por versão" (n_necessário = 0,1173); a faixa "acima de 1M" está vazia. A OS-08 pede o efeito do patrocínio como média ponderada das diferenças de índice, e não das razões brutas da OS-03 — segui a OS-08; as duas concordam em 3,2e-6.

### OS-09 — Ferramenta: correções, como usar, planejar campanha e design (2026-10-12)

- **Feito:** Parte 0 (segmento vs resto do recorte com erro padrão de duas amostras, briefing com "Priorize:"/"Evite:", piso de 30 posts por versão no A/B, correções de texto), Parte 1 (template de 17 colunas com `clicks`/`conversions`/`cost` opcionais, taxa de conversão julgada pelo mesmo motor, custo por interação e por conversão como mediana + p10–p90 sem veredito), Parte 2 (aba "Como usar" com passo a passo, dicionário, de onde exportar, leitura dos vereditos e 5 dicas), Parte 3 (aba "Planejar campanha": testar uma ideia, simulador de alcance e gasto, seção "Plano de volume" no briefing) e Parte 4 (design inteiro: tokens, Public Sans, escala 13/15/18/24/32, grade de 8px, máximo de 1120px, selos com barra lateral, listas em formato razão, tabelas com IC ao lado do valor). Tudo em `solution/tool/src/`; `decisor.html` regerado pelo `build_tool.py` (2,91 MB) e nunca editado à mão. Saídas em `solution/outputs/os09/`: `resumo_os09.md`, 7 capturas, `template_decisor.csv`, 3 .csv de referência e as fixtures.
- **Validações:** `validar_os09.mjs` passa (lift dif. máx. 3,75e-14 e erro padrão 9,30e-15 contra o pandas; base de efeito conhecido devolve vídeo +19,63% "funciona" e image/text/mixed "não funciona"; os vereditos da base do desafio seguem inalterados: patrocínio Barrado, 0 positivos, 0 negativos, 220 sem efeito). No navegador (`os09_navegador.py`, Playwright + Chrome): template baixado, preenchido com 2.000 linhas e seed 42, recarregado e rodando com as métricas novas; simulador conferido na mão contra o pandas (alcance 404.011 e interações 80.412, com os ICs batendo); 3 ideias avaliadas (n = 1.228, 22.314 e 98); 7 capturas a 1.280 e 1.440 px; Tab alcança 13/13, 8/8 e 21/21 focáveis com contorno visível.
- **Erros e como foram resolvidos:** limite de tokens de saída estourou ao reescrever o `ui.js` inteiro de uma vez — refeito em 6 blocos com sentinela no fim do arquivo. `python3` sem pandas: passei a usar o `.venv` da raiz. O modo `template` clicava em "Baixar template" com o painel ainda oculto — faltava ativar a aba "Como usar" antes. A checagem de Tab acusava elementos inalcançáveis: era artefato de começar a varredura no meio do documento e de truncar rótulos em tamanhos diferentes nas duas listas.
- **Corrigido depois de olhar as capturas (Parte 4):** títulos de seção estavam a 18px (viraram `h2`, 24/600); selos nas listas tinham fundo esticado em 160px (ficou só a barra de 4px, coluna de 176px); texto de apoio da "Saúde da base" estava à direita; o marcador ▸ deslocava os títulos recolhíveis em 19px; `tabular-nums` só valia em tabelas; mediana e faixa de custo usavam casas decimais diferentes; negativos saíam com hífen em vez de "−".
- **Acessibilidade:** o amarelo `#B7791F` do "Inconclusivo"/"Alerta" dava 3,64:1 sobre branco, abaixo do mínimo de 4,5:1. Trocado por `#8C5A0A` (5,86:1). Pior contraste medido depois disso: 5,00:1.
- **Reportado, não alterado (regra 5):** a base do desafio continua sem nenhum efeito real (220 segmentos sem efeito comprovado, patrocínio com efeito 0,999874, dp do índice 0,024461 forçando o piso de 30 no A/B) e o ganho do patrocínio na simulação sai 5 e −2 com IC passando por zero. A Parte 1 exigiu mexer em `carregarLinhas`/`montarBase`/`montarIndices` do `engine.js`, apesar de as Partes 1–3 pedirem só acréscimos, porque sem isso as colunas novas não chegam ao cálculo.

### OS-10 — Ferramenta didática: linguagem, Planejar e tema (2026-10-12)

- **Feito:** reescrita de todo o texto de tela em `src/ui.js` (vereditos viraram "Funcionou melhor / Funcionou pior / Não faz diferença / Ainda não dá para saber", briefing virou "Resumo para a sua próxima campanha" com 4 linhas, saúde da base virou "Dá para confiar nestes dados?" em pergunta e resposta, patrocínio com duas barras na mesma escala, aba Planejar em dois passos numerados com 3 exemplos prontos, "Mais opções" e comparativo "Seu plano × Se todos fossem sem pagar") e reescrita de `src/template.html` (barra superior Período · Redes sociais · Ajustes · Carregar meus dados · Tema, tema por variáveis CSS com Automático/Claro/Escuro, impressão sempre no claro). `engine.js` não foi tocado. `decisor.html` regerado pelo `build_tool.py`: 2,93 MB.
- **Validações (`solution/outputs/os10/`):** motor intacto — `validar_os09.mjs` passa e `validar_engine.mjs` repete a mesma única falha herdada da OS-08 (lift por valor de variável, dif 1,91e-4); varredura de linguagem com 0 palavras proibidas e 0 frases acima de 25 palavras nas três telas; base com efeito conhecido devolve "Priorize: Vídeo" e "Evite: Imagem, Texto, Misto"; Planejar com botão travado, 3 exemplos preenchendo os campos, "Mais opções" abrindo/fechando e o mês de 30 + 10 posts a R$ 2.000 batendo com a conta em pandas (404 mil visualizações, 80 mil interações, R$ 20.000); 4 capturas a 1.440 px nos dois temas, escolha salva no `localStorage` sobrevivendo ao reload; ajuda "?" abrindo no clique e no Enter e fechando com Esc e com clique fora.
- **Erros e como foram resolvidos:** limite de tokens de saída estourou de novo ao reescrever o `ui.js` inteiro — refeito em 7 blocos com sentinela. A varredura de frases longas usava `textContent` e colava blocos vizinhos, inventando "frases" de 90 palavras — trocada por `innerText`, que também já exclui o recolhível "Como calculamos" fechado. A conferência das barras em pandas deu 49.488 posts contra 49.487 da tela: era o meu `pd.cut` com limite superior aberto, enquanto o motor usa `seguidores <= limite`; corrigido o script de conferência, não a ferramenta.
- **Corrigido depois de medir:** o botão principal no tema escuro tinha texto branco fixo sobre `#E5584A` (3,6:1). Criado o token `--destaque-texto` (branco no claro, escuro no escuro) e eliminada a última cor fixa do CSS; passou a 4,6:1. Pior contraste medido nas quatro telas: 4,60:1.
- **Reportado, não alterado (regra 5):** a base do desafio segue sem efeito nenhum, então o resumo diz "nenhuma escolha mudou o resultado" e os cinco testes de confiança respondem quase tudo "Não", com o selo "Atenção". O `#B7791F` da tabela de tokens da OS reprovaria no mínimo de 4,5:1 exigido na mesma OS; mantive `#8C5A0A`. As barras usam média crua por post (o motor não devolve esse número, o `ui.js` repete a separação em grupos) enquanto a frase ao lado usa o efeito normalizado do motor — aqui a diferença é invisível, em outra base pode aparecer.
### OS-11 — Fechamento: reprodução, commits e Pull Request (2026-10-13)

- **Feito:** a solução foi montada em `submissions/gabriel-mata/` na branch `submission/gabriel-mata` (cópia da pasta de trabalho, sem `.venv/`, `datasets/`, `__pycache__/` e `.DS_Store`), uma checagem do `validar_engine.mjs` foi desativada, foi criado `solution/analysis/run_all.py`, os 3 PDFs foram regerados pelo `os07_pdf.py` e os links e tamanhos do pacote foram conferidos. `requirements.txt` foi recriado com as versões fixas do ambiente (pandas 2.3.3, numpy 2.0.2, scipy 1.13.1, scikit-learn 1.6.1, statsmodels 0.14.6, matplotlib 3.9.4, Markdown 3.9, playwright 1.60.0), porque o arquivo não estava mais no disco.
- **Etapa 1 (estrutura):** a estrutura confere com a OS, considerando que o export da conversa é um link público (`https://claude.ai/share/8fe74758-e8bc-4805-b801-e5ad447b62c8`, HTTP 200) e não um PDF, então `process-log/` tem apenas `process-log.md` e `baseline/`. O LinkedIn do README não está `[PREENCHER]` e o `[DATA]` virou `13/10/2026`.
- **Etapa 2 (validador):** comentada só a comparação de lift por valor de variável em `solution/tool/validar_engine.mjs`, com a justificativa no próprio arquivo — desde a OS-09 o lift é segmento vs. resto do recorte, e isso é validado no `validar_os09.mjs`. Nenhuma outra checagem mudou. `node validar_engine.mjs` e `node validar_os09.mjs` saem com código 0.
- **Etapa 3 (reprodução):** `run_all.py` roda os01, os02, os03, os03b, os03c, os04, os05, os06, depois `build_tool.py` e os dois validadores, parando no primeiro erro e resolvendo todos os caminhos a partir do próprio arquivo. Não gera PDFs. As 11 etapas passaram em **45,7 s** (os02 11,3 s e os03 13,4 s são as mais lentas). Teste de reprodução a partir de uma cópia de `solution/outputs/`: **69 de 69 .csv byte a byte iguais**, mais todos os .png e o `decisor.html` (2,8 MB) idênticos.
- **Etapa 4 (PDFs):** `relatorio_executivo.md` diz "68 combinações" e não há nenhuma menção a "204 combinações". `os07_pdf.py` rodou sem ser alterado e regerou os 3 PDFs; não há nenhum outro PDF em `solution/report/`. O "68 combinações" foi conferido visualmente nas capturas do executivo e do completo.
- **Etapa 5 (empacotamento):** os 18 links e âncoras relativos do README resolvem — **nenhuma correção de caminho foi necessária**. Fora dos commits: `.venv/`, `venv/`, `__pycache__/` e `node_modules/` não existem na pasta; os 3 `.DS_Store` do disco ficaram fora dos commits e não foram apagados; os únicos .html são `solution/tool/decisor.html` e `src/template.html`, ambos entregáveis (os temporários do `os07_pdf.py` nascem em `/var/folders/`); o único .csv de dados é `datasets/social_media_dataset.csv`. Acima de 5 MB só esse CSV (22 MB, fora do commit); nada acima de 50 MB. Maior arquivo comitado: `decisor.html`, 2,80 MB. Zero ocorrências, nos .md, de duas chaves de abertura seguidas ou de chave de abertura seguida de porcentagem.
- **Erros e como foram resolvidos:** `submissions/gabriel-mata/` não existia com o conteúdo atual e a pasta de trabalho não é um repositório git — parei na PAUSA 1 e segui com as instruções de cópia. O clone de `~/Documents/GitHub/` foi apagado no meio do caminho; confirmei pela API do GitHub que nenhuma branch ou PR tinha sido perdida e clonei de novo. O `requirements.txt` havia desaparecido do disco: parei, reconstruí a lista a partir dos imports e das versões instaladas e só prossegui depois da confirmação. Leitura errada de código de saída: `node validar_engine.mjs | tail` devolvia 0 porque o `$?` era do `tail`; refeito com redirecionamento para arquivo. No `git add -f`, as formas `:(exclude)*.DS_Store` e `:(exclude,glob)**/.DS_Store` zeram o resultado inteiro em silêncio — usei o caminho completo `:!.../.DS_Store`; e o zsh não separa em palavras uma variável não citada, o que fazia três pathspecs virarem um só e deixava o `.DS_Store` passar.
- **Conflito entre README e OS, resolvido:** o README anunciava um `--pdf` no `run_all`, que a OS-11 proíbe. Seguindo a OS, a frase foi corrigida para apontar o `os07_pdf.py` à parte. A seção "Como rodar" também passou a usar os caminhos reais do repositório — as duas únicas alterações de texto autorizadas no README, mais a data.
- **Reportado, não alterado (regra 5):** depois de regerados, `relatorio_tecnico.pdf` (416.906 b) e `relatorio_completo.pdf` (454.647 b) mantiveram o **tamanho idêntico** ao anterior com bytes diferentes, enquanto o `relatorio_executivo.pdf` foi de 230.165 para 230.365 b — provável efeito da compressão Flate. O README diz "as 15 Ordens de Serviço" na linha 154 e "Foram 14 OS" na linha 108; não corrigi, por não ser alteração de texto autorizada. A URL do LinkedIn devolve HTTP 999, que é o anti-robô do LinkedIn e não link quebrado.
- **GitHub Pages:** o primeiro build do GitHub Pages falhou: o próprio registro desta OS continha, por escrito, as sequências que a Etapa 5 proíbe. A conferência tinha sido feita antes do registro. Corrigido no 6º commit, com nova varredura de todos os .md depois da correção.


<!-- fim do log de execução -->

---

## 5. Ordens de Serviço


Cada OS foi escrita no chat depois de interpretar o resultado da anterior. Abaixo, o status de cada uma, as regras fixas do executor, o fluxo de trabalho, a versão inicial descartada e o texto integral de cada OS.

| OS | Objetivo | Status |
|---|---|---|
| OS-01 | Base amostral | Executada |
| OS-02 | Benchmark por segmento (níveis 1 a 4) | Executada |
| OS-03 | Patrocínio e validação geral | Executada (em 2 modelos; ver 3.5) |
| OS-03b | Fit patrocinador × conteúdo e audiência | Executada |
| OS-03c | Robustez: equivalência, poder, controle positivo, caudas, tendência | Executada |
| OS-04 | Sanidade, hashtags, efeito absoluto, tamanho de amostra | Executada |
| OS-05 | Gráficos dos relatórios | Executada |
| OS-06 | Lacunas do brief: alcance e formato × audiência | Executada |
| OS-07 | PDF paginado | Executada; substituída pela 07b |
| OS-07b | PDF contínuo | Executada |
| OS-08 | Ferramenta: núcleo | Executada |
| OS-09 | Ferramenta: correção do motor, abas e design | Executada |
| OS-10 | Ferramenta: linguagem simples e tema escuro | Executada |
| OS-10b | Correções finas de layout | **Não executada** (decisão do Gabriel; ver 3.8) |
| OS-11 | Fechamento e PR | Executada (registro na seção 4) |

### 5.1 Regras fixas do executor (`CLAUDE.md`)

O mesmo arquivo está na raiz da submissão e foi lido pelo Claude Code antes de cada OS.

<details><summary>Ver o CLAUDE.md</summary>


#### CLAUDE.md

##### Seu papel
Você é o **executor de análises de dados** deste projeto. O raciocínio, a interpretação e a estratégia são feitos fora daqui, pelo Gabriel.
Você recebe **Ordens de Serviço (OS)**, executa exatamente o que foi pedido e devolve os números.

##### Regras de execução
1. **Faça só o que a OS pede.** Não adicione análises, gráficos, arquivos, bibliotecas ou "melhorias" não solicitadas.
2. **Não interprete.** Descreva o que os números mostram, sem recomendações nem conclusões de negócio.
3. **Todo número sai de código executado** e fica salvo em arquivo. Nunca escreva um número de cabeça.
4. **Código simples.** Um script por OS, pandas direto, sem classes, frameworks ou abstrações. Comentários curtos.
5. **Seed fixa (42)** em tudo que for aleatório.

##### Regras para erros (importante)
1. **No máximo 2 tentativas de corrigir um erro.** Se não resolver, pare e reporte: o erro, o que tentou e sua hipótese da causa.
2. **Corrija a causa, não contorne.** Proibido: `try/except` que esconde erro, descartar linhas ou colunas sem avisar, trocar a métrica ou o método pedido para o erro sumir.
3. **Não mude o escopo para resolver um problema.** Se a OS não puder ser cumprida como foi escrita, pare e pergunte.
4. **Uma correção por vez.** Não empilhe mudanças. Se uma correção gerar outro erro, volte ao último estado que funcionava antes de tentar outra coisa.
5. **Resultado estranho não é erro para consertar.** Efeito enorme, p-valor minúsculo, valor impossível: reporte como "suspeito", com o número, e não altere nada.
6. **Script que já funciona não se mexe** sem pedir antes.

##### Dados
- CSV: `<raiz do repo>/datasets/social_media_dataset.csv` (a pasta `datasets/` é ignorada pelo git).
- Resolva o caminho relativo ao próprio script e aceite override pela variável de ambiente `DATA_PATH`.
- Definições padrão (use sempre, salvo se a OS disser outra coisa):
  - `engajamento` = likes + shares + comments_count
  - `taxa_engajamento` = engajamento / views
  - Faixas de seguidores: 1–10K, 10–50K, 50–100K, 100–500K, 500K–1M
  - Faixas de duração (só vídeo, em segundos): <30, 30–60, 60–180, >180

##### Organização
- Scripts: `solution/analysis/osXX_nome.py`
- Saídas: `solution/outputs/osXX/` (tabelas em .csv e um `resumo_osXX.md`)
- O `resumo_osXX.md` traz as tabelas principais e no fim uma seção "Pontos suspeitos ou problemas encontrados".
- Ao terminar cada OS, adicione 3 a 5 linhas em `process-log/log-execucao.md`: OS, o que foi feito, erros encontrados e como foram resolvidos.

##### Limites
- Não altere nada fora de `submissions/gabriel-mata/`.
- Não faça commits. Serão feitos no final, quando o Gabriel pedir.
- Comunicação em português, simples e direta.



</details>

### 5.2 Fluxo de trabalho (instruções ao Gabriel)


#### Setup (uma vez)
1. No seu fork: `git checkout -b submission/gabriel-mata`
2. Copie a pasta `submissions/` deste pacote para a raiz do repositório.
3. Crie `datasets/` na raiz e coloque o CSV: `datasets/social_media_dataset.csv`
4. Abra o Claude Code na pasta da submissão:
   ```bash
   cd submissions/gabriel-mata
   claude
   ```

#### Ciclo de trabalho
1. **Claude.ai** escreve a próxima OS.
2. **Você** cola a OS no Claude Code.
3. **Claude Code** executa e mostra o `resumo_osXX.md`.
4. **Você** traz o resumo para o Claude.ai. Lá interpretamos e decidimos a próxima OS.

#### Primeira OS
Cole o conteúdo de `ordens-de-servico/OS-01_base_amostral.md`.

#### Atenção no commit final
O `.gitignore` da raiz ignora `submissions/`. O commit vai precisar de `git add -f submissions/gabriel-mata`.


### 5.3 Versão inicial descartada

O primeiro desenho entregava ao Claude Code um `CLAUDE.md` longo, com todo o contexto do desafio, e pedia que ele refizesse a análise inteira sozinho. Foi trocado pelo modelo de OS curtas (ver 3.3). Fica aqui como evidência de iteração no processo.

<details><summary>CLAUDE.md da versão inicial</summary>


#### CLAUDE.md — Contexto do projeto

Você está executando a submissão de **Gabriel Mata** para o **AI Master Challenge do G4**, desafio **004 — Estratégia Social Media**.
O planejamento já foi feito no Claude.ai. Sua função é **executar do zero, de forma independente**, a partir do fim do planejamento.

##### Como se comunicar com o Gabriel
- Português, simples, claro e objetivo. Sem textões, sem jargão desnecessário.
- Estruture em seções curtas e tabelas quando ajudar.
- Seja crítico: aponte riscos, fragilidades e quando os dados não sustentam algo. Não valide por validar.

---

##### 1. O desafio

O README completo está em `../../challenges/marketing-004-social/README.md`. Leia antes de começar.

**O Head de Marketing quer 3 respostas:**
1. O que gera engajamento de verdade?
2. Vale a pena patrocinar influenciadores?
3. Qual deveria ser a estratégia de conteúdo?

E, se possível, uma ferramenta para acompanhar isso no dia a dia.

**Entregáveis obrigatórios:** análise de performance, estratégia recomendada, algo a mais (diferencial) e process log.

**Critérios de qualidade do G4:**
- Ir além do superficial. Média por plataforma é a tabela 1, não a conclusão.
- Insights acionáveis: o Head sabe o que fazer na segunda-feira.
- Comparação orgânico vs. patrocinado justa, controlando por tamanho de creator, plataforma e categoria.
- Recomendações priorizadas, não uma lista de 20 ideias.
- Clareza para um executivo não técnico: precisa entender em 5 minutos.

**O ponto central:** o G4 já rodou o brief em vários modelos de IA (o baseline). Uma entrega parecida com o que a IA gera sozinha é reprovada. O que se avalia é julgamento: saber o que pedir, quando desconfiar, o que verificar e corrigir.

---

##### 2. Regras inegociáveis

1. **Todo número sai de código executado.** Nunca escreva um número que não tenha vindo de um script rodado. Cada número do relatório precisa ser rastreável até um arquivo em `solution/outputs/`.
2. **Diferença pequena não é insight.** Antes de afirmar que "X performa melhor", mostre:
   - tamanho do efeito (lift vs. referência, por exemplo a média da plataforma);
   - n do segmento;
   - intervalo de confiança de 95% (bootstrap);
   - replicação: o efeito se repete em duas metades aleatórias dos dados?
   - quando houver busca em muitos segmentos: compare com a distribuição sob permutação (o melhor segmento real supera o melhor segmento esperado por acaso?).
3. **Nunca force um número.** Se um efeito não for robusto, diga isso com clareza. Um "não há diferença" bem provado vale mais que um "3x" inventado.
4. **Desconfie dos próprios modelos.** Em regressões, verifique multicolinearidade, porque várias colunas são derivadas de outras (por exemplo, colunas de patrocínio derivam de `is_sponsored`, e `content_length` depende de `content_type`). Coeficientes enormes com p minúsculo são sinal de alerta, não de insight.
5. **Métricas relativas mentem.** Defina explicitamente cada métrica (engajamento sobre views ≠ engajamento sobre seguidores) e sempre confira o valor absoluto por trás de cada taxa.
6. **Não modifique nada fora de `submissions/gabriel-mata/`.** PRs que alteram outros arquivos são rejeitados pelo G4.
7. **Não faça commits.** Todos os commits são feitos no final, só quando o Gabriel pedir.
8. **Pare ao fim de cada etapa** e apresente um resumo ao Gabriel antes de seguir.

---

##### 3. Formato de insight esperado

Cada achado segue esta estrutura:

> **Segmento** → **métrica** → **resultado vs. referência** → **n** → **confiança** → **ação**

Exemplo ilustrativo do formato (não é um resultado): "Vídeos de 30–60s em Tech, com creators de 10–50K seguidores, geram 3,2x mais shares que a média da plataforma (n=..., IC 95%: ..., replicado nas duas metades) → priorizar esse formato."

---

##### 4. Dados

- Arquivo: `social_media_dataset.csv`, cerca de 52K posts, 27 colunas.
- Local: `<raiz do repo>/datasets/social_media_dataset.csv`. A pasta `datasets/` já é ignorada pelo `.gitignore` do G4, então o CSV nunca vai para o PR.
- Os scripts devem resolver o caminho **relativo ao próprio arquivo** e aceitar override pela variável de ambiente `DATA_PATH`.

**Descrição oficial do Kaggle (resumo):** dataset que *simula* posts de influenciadores em YouTube, TikTok, Instagram, Bilibili e RedNote, com 5.000 creators. Colunas: id, platform, content_id, creator_id, creator_name, content_url, content_type (video/image/text/mixed), content_category (beauty/lifestyle/tech), post_date, language, content_length (segundos para vídeo, palavras para texto), content_description, hashtags (0–5), views (simuladas via Poisson), likes, shares, comments_count, comments_text, follower_count, is_sponsored, disclosure_type (explicit/implicit/none), sponsor_name, sponsor_category, disclosure_location, audience_age_distribution, audience_gender_distribution, audience_location.

---

##### 5. Estrutura da pasta

```
submissions/gabriel-mata/
├── CLAUDE.md                 ← este arquivo
├── README.md                 ← criado na Etapa 8, seguindo ../../templates/submission-template.md
├── requirements.txt
├── solution/
│   ├── analysis/             ← scripts numerados (01_..., 02_...) + run_all.py
│   ├── outputs/              ← tabelas (.csv) e gráficos (.png) gerados pelos scripts
│   ├── report/               ← relatório executivo
│   └── tool/                 ← ferramenta em HTML único
└── process-log/
    ├── decisions.md          ← registro contínuo (atualize a cada etapa)
    ├── baseline/             ← resposta "brief puro" de uma IA (fornecida pelo Gabriel)
    └── chat-claude-ai/       ← exploração feita no chat. NÃO ABRIR antes da Etapa 4
```

---

##### 6. Etapas de execução

Ao fim de **cada** etapa: atualize `process-log/decisions.md` e pare para o Gabriel revisar.

###### Etapa 0 — Ambiente
- Crie um ambiente virtual, instale o `requirements.txt` e confirme que o CSV carrega (linhas, colunas, tipos).

###### Etapa 1 — Auditoria e teste de sinal
- Qualidade: nulos, duplicatas, tipos, datas, valores fora do esperado, consistência entre colunas (por exemplo, posts não patrocinados com disclosure ≠ none, creator com dados incoerentes entre posts, `comments_count` vs. `comments_text`).
- Distribuições das métricas (views, likes, shares, comments, engajamento): dispersão, caudas, posts com engajamento muito baixo (viés de sobrevivência).
- Relações básicas: seguidores vs. views vs. engajamento.
- **Teste de sinal:** as variáveis explicam alguma parte relevante do engajamento? Variância explicada, testes por dimensão, comparação com o esperado por acaso, um modelo preditivo simples com validação cruzada.
- **Decisão:** cenário A (há sinal) ou cenário B (majoritariamente ruído). Justifique com números.

###### Etapa 2 — O que gera engajamento (pergunta 1)
- Por plataforma, tipo de conteúdo, categoria, faixa de creator, duração (dentro de cada tipo), idioma, horário/dia/período, hashtags (quantidade e termos), audiência (idade, gênero, local).
- Interações entre essas variáveis (é aqui que mora o insight do tipo "formato X + categoria Y + faixa Z").
- O que **não** funciona. Perfil de audiência que mais engaja.
- Todos os achados no formato da seção 3, aplicando as regras da seção 2.

###### Etapa 3 — Patrocínio (pergunta 2)
- Orgânico vs. patrocinado, **estratificado** por plataforma × faixa de creator × categoria.
- Efeito de tipo e local de disclosure, e de categoria do patrocinador.
- Sem dado de custo: calcule o **ponto de equilíbrio** (até quanto vale pagar por perfil de creator) usando o engajamento entregue por faixa. Não invente custos de mercado como se fossem dados.

###### Etapa 4 — Verificação cruzada
- Agora, e só agora, leia `process-log/chat-claude-ai/`.
- Compare seus resultados com os da exploração do chat. Liste o que bate, o que diverge e por quê.
- Registre no `decisions.md`. Divergências são evidência valiosa de processo, não falha.

###### Etapa 5 — Baseline
- Se o Gabriel tiver colocado em `process-log/baseline/` a resposta de uma IA ao brief puro, confronte cada afirmação dela com os dados: sustentada, não sustentada ou contrariada, com o número correspondente.

###### Etapa 6 — Estratégia e relatório (pergunta 3)
- Relatório executivo em `solution/report/`, com no máximo 5 páginas, legível em 5 minutos.
- Estrutura: conclusão em uma página; achados com evidência; política de patrocínio; onde concentrar esforço; o que parar de fazer; quick wins desta semana; limitações.
- Recomendações priorizadas por impacto × força da evidência × esforço (3 a 5 ações, não mais).
- Detalhes estatísticos em um apêndice.

###### Etapa 7 — Ferramenta (algo a mais)
- HTML único e autossuficiente em `solution/tool/`. Abre no navegador sem instalar nada e sem servidor. Dados agregados embutidos no arquivo.
- Escopo definido no planejamento: (a) benchmarks por segmento ("o que é um bom resultado para este tipo de post?") e (b) avaliador de patrocínio (perfil do creator + preço proposto → vale ou não, com base no ponto de equilíbrio).
- Ajuste o escopo ao que a análise mostrou e proponha ao Gabriel antes de construir.

###### Etapa 8 — Fechamento
- `README.md` da submissão seguindo `../../templates/submission-template.md`, com setup, como rodar, executive summary, process log e limitações.
- `run_all.py` reproduz todos os outputs do zero. Teste de ponta a ponta.
- Process log completo: ferramentas usadas, workflow, onde a IA errou e como foi corrigido, o que o humano acrescentou.
- **Commit e PR só quando o Gabriel pedir.** Atenção: o `.gitignore` da raiz ignora `submissions/`, então será preciso `git add -f submissions/gabriel-mata`. Confira com `git status` que nenhum arquivo fora da pasta foi alterado e que nenhum CSV de dados brutos entrou. Branch `submission/gabriel-mata`; título do PR: `[Submission] Gabriel Mata — Challenge 004`.

---

##### 7. Qualidade do código
- Scripts numerados, que rodam sozinhos e em sequência, com comentários curtos explicando o raciocínio.
- Seed fixa em tudo que for aleatório (bootstrap, permutação, divisão em metades).
- Outputs salvos em arquivos, nunca só impressos no terminal.



</details>

<details><summary>Prompt inicial da versão descartada</summary>

Olá! Você vai executar minha submissão para o AI Master Challenge do G4 (desafio 004 — Estratégia Social Media).

O planejamento já foi feito em outra conversa. Agora quero que você execute tudo do zero, de forma independente, a partir do ponto em que começamos a analisar os dados.

Antes de qualquer coisa:
1. Leia o `CLAUDE.md` desta pasta. Ele tem o contexto completo, as regras e as etapas.
2. Leia o README do desafio em `../../challenges/marketing-004-social/README.md`.
3. Leia `process-log/decisions.md` para entender as decisões do planejamento.
4. NÃO abra a pasta `process-log/chat-claude-ai/` antes da Etapa 4. Ela guarda uma exploração anterior e só serve para verificação cruzada depois.

Depois disso:
- Me confirme em poucas linhas o que entendeu do desafio e das regras.
- Execute a Etapa 0 (ambiente) e a Etapa 1 (auditoria e teste de sinal).
- Pare ao fim da Etapa 1 e me traga um resumo simples: o que encontrou, os números principais, e se estamos no cenário A ou B, com justificativa.

Lembretes importantes:
- Todo número precisa sair de código executado e ficar salvo em arquivo.
- Não faça commits. Faremos todos no final.
- Não altere nada fora de `submissions/gabriel-mata/`.
- Comunicação em português, simples, clara e objetiva.

</details>

### 5.4 Texto integral das OS


<details><summary>OS-01 — Base amostral</summary>

#### OS-01 — Base amostral

Leia o `CLAUDE.md` antes de começar. Se o ambiente ainda não existir, crie um ambiente virtual e instale o `requirements.txt`.

##### Objetivo
Descrever a base de dados: tamanho, qualidade, distribuições e quanto volume existe em cada segmento. **Não interprete nada**, só levante os números.

##### Script
`solution/analysis/os01_base_amostral.py` → saídas em `solution/outputs/os01/`

##### O que calcular

**1. Visão geral**
- Linhas, colunas, tipo de cada coluna.
- Nulos por coluna (quantidade e %).
- Duplicatas em `id` e `content_id`.
- Data mínima e máxima de `post_date`.

**2. Distribuição das métricas**
Para views, likes, shares, comments_count, follower_count, engajamento e taxa_engajamento:
- mínimo, p1, p25, mediana, p75, p99, máximo, média, desvio padrão e coeficiente de variação (desvio / média).
- Quantidade de posts com engajamento igual a zero.

**3. Volume por segmento**
Contagem e % de posts para cada valor de: platform, content_type, content_category, language, is_sponsored, disclosure_type, disclosure_location, sponsor_category, audience_age_distribution, audience_gender_distribution, audience_location, faixa de seguidores e faixa de duração (só vídeo).

**4. Tamanho dos cruzamentos**
No cruzamento platform × content_type × content_category × faixa de seguidores:
- total de combinações existentes;
- quantas têm n ≥ 100, entre 30 e 99 e menos de 30;
- n mínimo, mediano e máximo.

Repita para platform × content_category × faixa de seguidores × is_sponsored.

**5. Consistência**
- Posts não patrocinados com disclosure_type ≠ none ou sponsor_category ≠ "Not sponsors".
- Posts patrocinados com disclosure_type = none.
- Por creator_id: quantas plataformas diferentes e quanto o follower_count varia (mínimo, máximo, diferença).
- comments_count vs. quantidade de comentários em comments_text (só reportar as medianas).

**6. Relação entre métricas**
Correlação de Spearman entre follower_count, views, likes, shares, comments_count e engajamento.
Mediana de views e de engajamento por faixa de seguidores.

##### Entrega
- Tabelas em .csv em `solution/outputs/os01/`.
- `resumo_os01.md` com as tabelas principais e a seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os01.md` e pare.


</details>


<details><summary>OS-02 — Benchmark por segmento</summary>

#### OS-02 — Benchmark por segmento

Leia o `CLAUDE.md` antes de começar.

##### Objetivo
Medir o desempenho de cada segmento em relação à média da sua plataforma, com margem de erro, teste de repetição e teste contra o acaso. **Não classifique nem interprete os segmentos.** Só calcule e reporte.

##### Script
`solution/analysis/os02_benchmark.py` → saídas em `solution/outputs/os02/`

##### Ajustes em relação ao CLAUDE.md (valem só para esta OS)
- **Faixas de seguidores:** até 50K, 50–100K, 100–500K, 500K–1M.
- **Não use `content_length`** nem faixas de duração. O campo não representa duração (ver OS-01).
- **Novas variáveis derivadas:**
  - `n_hashtags`: quantidade de hashtags (0 a 5; nulo = 0).
  - `periodo_dia` a partir da hora de `post_date`: madrugada (0–5h), manhã (6–11h), tarde (12–17h), noite (18–23h).
  - `dia_semana` a partir de `post_date`.

##### Métricas
`taxa_engajamento`, `shares` e `comments_count`.

##### Método
1. **Índice por post.** Para cada métrica: `indice = valor do post / média da métrica na plataforma do post`. Isso deixa todas as plataformas na mesma escala.
2. **Lift do segmento** = média do índice dos posts do segmento. Exemplo: 1,05 significa 5% acima da média da plataforma.
3. **Margem de erro:** IC 95% por bootstrap (1.000 reamostragens dos posts do segmento, método percentil).
4. **Teste de repetição:** divida a base uma única vez em duas metades aleatórias (seed 42) e use essa mesma divisão para todos os segmentos. Calcule o lift do segmento em cada metade.
5. **Teste contra o acaso**, para cada nível e métrica:
   - embaralhe o índice entre os posts **dentro de cada plataforma**;
   - recalcule o lift de todos os segmentos do nível (mesmo filtro de n) e guarde o maior e o menor lift;
   - repita 200 vezes.
   - Reporte o p95 dos maiores, o p5 dos menores e compare com o maior e o menor lift observados.

##### Segmentos (níveis)

**Plataforma (tabela à parte):** média de cada métrica por plataforma vs. média geral, com IC 95%.

**Nível 1 — variável isolada** (todas as plataformas juntas, usando o índice), sem filtro de n:
content_type, content_category, language, is_sponsored, audience_age_distribution, audience_gender_distribution, audience_location, faixa_seguidores, n_hashtags, periodo_dia, dia_semana.

**Nível 2 — plataforma × cada variável do Nível 1.** Só segmentos com n ≥ 100.

**Nível 3 — combinações de 3 variáveis.** Só segmentos com n ≥ 100.
- platform × content_type × content_category
- platform × content_category × faixa_seguidores
- platform × content_type × faixa_seguidores
- platform × content_category × audience_age_distribution

**Nível 4 — platform × content_type × content_category × faixa_seguidores.** Só segmentos com n ≥ 100.

Em cada nível com filtro, informe quantos segmentos existiam e quantos ficaram de fora por n < 100.

##### Colunas de cada tabela de segmentos
`nivel`, `variaveis`, `segmento`, `metrica`, `n`, `lift`, `ic_inferior`, `ic_superior`, `ic_exclui_1` (sim/não), `lift_metade_A`, `lift_metade_B`, `mesmo_lado_nas_duas_metades` (as duas metades acima de 1 ou as duas abaixo de 1: sim/não).

##### Entrega
- Um .csv por nível em `solution/outputs/os02/`, mais a tabela de plataforma e a do teste contra o acaso.
- `resumo_os02.md` contendo:
  1. Tabela de plataforma.
  2. **Distribuição dos lifts** por nível e métrica: mínimo, p5, mediana, p95, máximo, e quantos segmentos ficam acima de 1,03 / 1,05 / 1,10 e abaixo de 0,97 / 0,95 / 0,90.
  3. Os 10 maiores e os 10 menores lifts de `taxa_engajamento` em cada nível, com todas as colunas.
  4. Tabela do teste contra o acaso: observado vs. acaso, por nível e métrica.
  5. Seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os02.md` e pare.


</details>


<details><summary>OS-03 — Patrocínio e validação geral</summary>

#### OS-03 — Patrocínio e validação geral

Leia o `CLAUDE.md` antes de começar.

##### Objetivo
Medir se posts patrocinados engajam diferente dos orgânicos, de forma justa, e testar se alguma combinação de variáveis prevê engajamento. **Não interprete nem recomende.** Só calcule e reporte.

##### Script
`solution/analysis/os03_patrocinio_validacao.py` → saídas em `solution/outputs/os03/`

##### Mantém as regras da OS-02
- Faixas de seguidores: até 50K, 50–100K, 100–500K, 500K–1M.
- `n_hashtags` (nulo = 0), `periodo_dia` e `dia_semana` com a mesma construção da OS-02. Reaproveite a lógica, mas não altere o script da OS-02.
- Métricas: `taxa_engajamento`, `shares`, `comments_count`. Nos blocos 5 e 7, também `engajamento`.
- IC 95% por bootstrap percentil com 1.000 reamostragens. Seed 42 em tudo.
- **Teste de repetição:** a mesma divisão em duas metades da OS-02 (seed 42), quando o bloco pedir.

---

##### Bloco 1 — Comparação justa (estratificada)
- **Estratos:** platform × content_category × content_type × faixa_seguidores.
- Use só estratos com pelo menos 30 posts patrocinados **e** 30 orgânicos. Informe quantos estratos existiam, quantos foram usados e quantos posts ficaram de fora.
- Em cada estrato: `razao = média patrocinado / média orgânico`.
- **Efeito geral** = média das razões ponderada pelo tamanho do estrato.
- **IC 95%:** bootstrap estratificado, reamostrando os posts dentro de cada estrato e de cada grupo.
- Reporte também:
  - efeito geral em cada metade (teste de repetição);
  - % de estratos com razão > 1;
  - distribuição das razões (mínimo, p5, mediana, p95, máximo);
  - para contraste, a comparação simples sem estratos (média patrocinado / média orgânico na base toda).

##### Bloco 2 — Regressão com controles
Para cada métrica, uma regressão linear (OLS) com erros robustos HC3:

`métrica ~ is_sponsored + platform + content_type + content_category + faixa_seguidores + language + audience_age_distribution + audience_gender_distribution + audience_location + n_hashtags + periodo_dia + dia_semana`

- **Não inclua** disclosure_type, disclosure_location, sponsor_category, sponsor_name nem content_length. As colunas de patrocínio são derivadas de `is_sponsored`.
- Reporte: coeficiente de `is_sponsored`, esse coeficiente como % da média da métrica, IC 95%, p-valor, R², R² ajustado, p-valor do teste F do modelo e número de condição.

##### Bloco 3 — Patrocínio por faixa de seguidores
- Para cada faixa, aplique o método do Bloco 1 usando como estratos **platform × content_category**, com mínimo de 20 patrocinados e 20 orgânicos por estrato.
- Reporte por faixa e métrica: n patrocinado, n orgânico, estratos usados, efeito, IC 95%, efeito na metade A, efeito na metade B.

##### Bloco 4 — Detalhes do patrocínio (só posts patrocinados)
- Índice e lift como na OS-02, mas a referência é a média dos **posts patrocinados** da plataforma.
- **Segmentos:** disclosure_type, disclosure_location, sponsor_category e disclosure_type × disclosure_location.
- **Colunas:** variáveis, segmento, métrica, n, lift, IC inferior, IC superior, IC exclui 1, lift na metade A, lift na metade B, mesmo lado nas duas metades.

##### Bloco 5 — Engajamento entregue por faixa
Por faixa de seguidores × is_sponsored, para `engajamento` (valor absoluto por post):
- n, média, IC 95% da média, mediana, p10 e p90.
- Mediana de `engajamento / follower_count`.

##### Bloco 6 — Volume patrocinado
- % de posts patrocinados por platform, content_category, content_type e faixa_seguidores.
- Total de posts patrocinados e orgânicos.
- % do engajamento total da base que vem de posts patrocinados vs. % de posts patrocinados.

##### Bloco 7 — Validação geral (modelo preditivo)
- **Modelo:** `HistGradientBoostingRegressor` com parâmetros padrão e `random_state=42`.
- **Variáveis de entrada:** platform, content_type, content_category, language, is_sponsored, audience_age_distribution, audience_gender_distribution, audience_location, follower_count, n_hashtags, content_length, hora do post e dia_semana. `content_length` entra como campo genérico, apesar da ressalva da OS-01.
- **Não use como entrada:** views, likes, shares, comments_count, engajamento nem taxa_engajamento.
- **Alvos:** `taxa_engajamento`, `shares`, `comments_count`, `engajamento` (um modelo por alvo).
- **Avaliação:** validação cruzada de 5 partes (embaralhada, seed 42). Compare com um modelo que sempre prevê a média (`DummyRegressor`). Reporte por alvo: R² médio e desvio, MAE do modelo, MAE do modelo da média e diferença % entre os dois.
- **Importância:** separe 20% dos dados para teste (seed 42), treine nos 80% e calcule a importância por permutação (10 repetições). Reporte as 10 variáveis mais importantes por alvo, com média e desvio da queda de R².

---

##### Entrega
- Um .csv por bloco em `solution/outputs/os03/`.
- `resumo_os03.md` com as tabelas principais de cada bloco, na ordem dos blocos, e a seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os03.md` e pare.


</details>


<details><summary>OS-03b — Fit de patrocínio e audiência</summary>

#### OS-03b — Fit de patrocínio e audiência

Leia o `CLAUDE.md` antes de começar.

##### Objetivo
Testar se o alinhamento entre patrocinador e conteúdo (fit) muda o engajamento, e se algum perfil de audiência, isolado ou combinado com conteúdo ou patrocínio, engaja diferente. **Não interprete nem recomende.** Só calcule e reporte.

##### Script
`solution/analysis/os03b_fit_audiencia.py` → saídas em `solution/outputs/os03b/`

Não altere os scripts das OS anteriores. Se precisar da mesma lógica, replique no novo script.

##### Regras mantidas das OS-02 e OS-03
- Faixas de seguidores: até 50K, 50–100K, 100–500K, 500K–1M.
- Métricas: `taxa_engajamento`, `shares`, `comments_count`.
- **Índice por post** = valor / média da métrica na plataforma do post. **Lift** = média do índice no segmento.
- IC 95% por bootstrap percentil (1.000 reamostragens). Seed 42.
- Mesma divisão em duas metades da OS-02 (seed 42).
- **Teste contra o acaso** (quando pedido): embaralhe o índice dentro de cada plataforma, recalcule todos os segmentos do conjunto e guarde o maior e o menor lift; repita 200 vezes; reporte o p95 dos maiores e o p5 dos menores contra os extremos observados.
- **Colunas das tabelas de segmentos:** variáveis, segmento, métrica, n, lift, IC inferior, IC superior, IC exclui 1, lift metade A, lift metade B, mesmo lado nas duas metades.

---

##### Parte A — Fit patrocinador × conteúdo (só posts patrocinados)

**Definição de `fit`** (sim/não):

| sponsor_category | content_category com fit |
|---|---|
| cosmetics | beauty |
| electronics | tech |
| gaming | tech |
| fashion | lifestyle |
| food | lifestyle |
| travel | lifestyle |

Qualquer outra combinação = sem fit.

**A1. Volume:** posts patrocinados com e sem fit (n e %), no total e por content_category.

**A2. Comparação justa fit vs. sem fit:**
- Estratos: platform × content_category × faixa_seguidores, com mínimo de 20 posts com fit e 20 sem fit.
- Em cada estrato: `razao = média com fit / média sem fit`.
- Efeito geral = média das razões ponderada pelo tamanho do estrato.
- IC 95% por bootstrap estratificado.
- Reporte o efeito em cada metade, a % de estratos com razão > 1 e quantos estratos e posts ficaram de fora.

**A3. Tabela sponsor_category × content_category** (18 combinações):
- Lift com referência na média dos posts **patrocinados** da plataforma (como no Bloco 4 da OS-03).
- Indique em uma coluna se a combinação tem fit.
- Teste contra o acaso no conjunto das 18 combinações.

---

##### Parte B — Audiência (todos os posts)

**B1. Personas:** audience_age_distribution × audience_gender_distribution × audience_location.
- Só segmentos com n ≥ 100. Informe quantos existiam e quantos ficaram de fora.
- Teste contra o acaso no conjunto.

**B2. Audiência × conteúdo:** três conjuntos.
- content_category × audience_age_distribution
- content_category × audience_gender_distribution
- content_category × audience_location

Só segmentos com n ≥ 100. Teste contra o acaso em cada conjunto.

**B3. Audiência × patrocínio:** para cada valor de audience_age_distribution, de audience_gender_distribution e de audience_location:
- Compare patrocinado vs. orgânico com o método do Bloco 3 da OS-03: estratos platform × content_category, mínimo de 20 patrocinados e 20 orgânicos, efeito ponderado, IC 95% por bootstrap estratificado, efeito em cada metade.
- Colunas: variável, valor, métrica, n patrocinado, n orgânico, estratos usados, efeito, IC inferior, IC superior, IC exclui 1, efeito metade A, efeito metade B.

---

##### Entrega
- Um .csv por item (A1, A2, A3, B1, B2, B3) e um .csv com todos os testes contra o acaso, em `solution/outputs/os03b/`.
- `resumo_os03b.md` com:
  1. As tabelas da Parte A completas.
  2. Para B1 e B2: distribuição dos lifts por conjunto e métrica (mínimo, p5, mediana, p95, máximo e quantos segmentos ficam acima de 1,03 / 1,05 / 1,10 e abaixo de 0,97 / 0,95 / 0,90), mais os 10 maiores e os 10 menores lifts de `taxa_engajamento` por conjunto.
  3. B3 completo.
  4. Tabela única de todos os testes contra o acaso.
  5. Seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os03b.md` e pare.


</details>


<details><summary>OS-03c — Robustez da conclusão</summary>

#### OS-03c — Robustez da conclusão

Leia o `CLAUDE.md` antes de começar.

##### Objetivo
Medir o tamanho máximo que um efeito poderia ter, o menor efeito que a base consegue detectar, se o método encontra um efeito quando ele existe, e se há diferenças nas caudas ou ao longo do tempo. **Não interprete nem recomende.** Só calcule e reporte.

##### Script
`solution/analysis/os03c_robustez.py` → saídas em `solution/outputs/os03c/`

Não altere os scripts das OS anteriores. Se precisar da mesma lógica, replique no novo script.

##### Regras mantidas
- Faixas de seguidores: até 50K, 50–100K, 100–500K, 500K–1M.
- Métricas: `taxa_engajamento`, `shares`, `comments_count`.
- **Índice por post** = valor / média da métrica na plataforma do post. **Lift** = média do índice no segmento.
- **Exceção:** para a variável `platform`, use índice = valor / média geral da base.
- Bootstrap percentil com 1.000 reamostragens. Seed 42. Mesma divisão em duas metades da OS-02.

##### Variáveis analisadas
platform, content_type, content_category, faixa_seguidores, is_sponsored, audience_age_distribution, audience_gender_distribution, audience_location.

Cada valor de cada variável é um segmento (por exemplo, `content_type = text`).

---

##### Bloco 1 — Limite máximo do efeito (equivalência)
Para cada segmento e métrica:
- lift, IC 95% e IC 90% (bootstrap);
- **efeito máximo plausível** = o maior afastamento entre 1 e os limites do IC 95%, em %. Exemplo: IC 0,9985–1,0010 → 0,15%;
- **equivalente a ±1%:** sim se o IC 90% inteiro estiver entre 0,99 e 1,01;
- **equivalente a ±2%:** sim se o IC 90% inteiro estiver entre 0,98 e 1,02.

Resumo por variável e métrica: o maior efeito máximo plausível entre os segmentos e quantos segmentos são equivalentes a ±1% e a ±2%.

##### Bloco 2 — Menor efeito detectável
Para cada segmento e métrica, com poder de 80% e significância de 5% (bicaudal):

`MDE = (1,96 + 0,84) × desvio padrão do índice na base × raiz(1/n_segmento + 1/n_resto)`

`n_resto` = posts fora do segmento. Reporte o MDE em %. Resumo por variável: o MDE do segmento com menor n.

##### Bloco 3 — Controle positivo (teste do método)
**Sempre trabalhe numa cópia dos dados. Nunca altere a base original.**

**3a. Injeção em segmentos isolados**
- Para cada variável, escolha o valor com **menor n**.
- Multiplique a métrica dos posts desse segmento por 1,01; 1,02 e 1,05 (um cenário de cada vez).
- Recalcule o índice e o lift do segmento, o IC 95% e o lift em cada metade.
- **Detectado** = IC 95% exclui 1 **e** as duas metades acima de 1.
- Tabela: variável, segmento, n, métrica, efeito injetado, lift medido, IC inferior, IC superior, detectado (sim/não).

**3b. Injeção numa busca entre muitos segmentos** (só `taxa_engajamento`)
- Entre as combinações platform × content_type × content_category × faixa_seguidores com n entre 100 e 150, sorteie uma (seed 42).
- Multiplique a `taxa_engajamento` dos posts dessa combinação por 1,05 (cenário 1) e por 1,10 (cenário 2).
- Em cada cenário, refaça a busca completa dessa combinação de 4 variáveis com o filtro n ≥ 100, como no Nível 4 da OS-02, incluindo o teste contra o acaso (200 permutações dentro da plataforma).
- Reporte: segmento sorteado, n, lift medido, IC 95%, posição no ranking de lifts, maior lift esperado por acaso (p95) e se o segmento supera esse valor.

##### Bloco 4 — Caudas da distribuição
- Para cada plataforma e métrica, calcule os cortes de top 10%, top 1% e bottom 10% do valor bruto.
- Para cada segmento e métrica, reporte a % de posts do segmento no top 10%, no top 1% e no bottom 10% da sua plataforma (esperado: 10%, 1% e 10%), com IC 95% de Wilson.
- Teste KS: compare a distribuição do índice no segmento com a do resto da base e reporte o p-valor.
- Resumo: quantos segmentos têm IC de Wilson que exclui o valor esperado, por cauda, e quantos têm KS com p < 0,05, contra o total de testes.

##### Bloco 5 — Tendência no tempo
- Média mensal de cada métrica: geral, por platform, por content_type e por is_sponsored.
- **Tendência:** regressão linear no nível do post, `métrica ~ número do mês` (1 a 25), com erros robustos HC3, para a base geral e para cada valor de platform, content_type e is_sponsored. Reporte a inclinação convertida em % da média por ano, IC 95% e p-valor.
- **Primeiro ano vs. último ano:** para cada plataforma, a razão entre a média dos últimos 12 meses e a dos primeiros 12, com IC 95% (bootstrap).

---

##### Entrega
- Um .csv por bloco (3a e 3b separados) em `solution/outputs/os03c/`.
- `resumo_os03c.md` com:
  1. Resumo do Bloco 1 por variável e métrica, mais os 10 segmentos com maior efeito máximo plausível.
  2. Resumo do Bloco 2 por variável.
  3. Tabelas 3a e 3b completas.
  4. Resumo do Bloco 4 e a lista dos segmentos com IC de Wilson que exclui o esperado.
  5. Bloco 5: tabela de tendências e a comparação primeiro × último ano.
  6. Seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os03c.md` e pare.


</details>


<details><summary>OS-04 — Complementos</summary>

#### OS-04 — Complementos

Leia o `CLAUDE.md` antes de começar.

##### Objetivo
Gerar quatro tabelas complementares para o relatório. **Não interprete nem recomende.** Só calcule e reporte.

##### Script
`solution/analysis/os04_complementos.py` → saídas em `solution/outputs/os04/`

Não altere os scripts das OS anteriores. O item 3 lê um arquivo de saída da OS-03c.

##### Regras mantidas
- `engajamento` = likes + shares + comments_count.
- Faixas de seguidores: até 50K, 50–100K, 100–500K, 500K–1M.
- Seed 42.

---

##### 1. Tabela de sanidade
Calcule cada indicador abaixo e reporte o valor numa tabela com as colunas `indicador` e `valor`:

1. Mediana de views por faixa de seguidores (uma linha por faixa).
2. Correlação de Pearson e de Spearman entre likes e views.
3. Correlação de Pearson entre log10(follower_count) e log10(views).
4. Variância ÷ média de views, likes, shares e comments_count (uma linha por métrica).
5. Engajamento no percentil 1 ÷ mediana do engajamento.
6. % de posts com engajamento abaixo de 10% da mediana.
7. Mínimo e máximo de views e de engajamento.
8. % de creator_id que aparecem em uma única plataforma.
9. % de creator_id com o mesmo follower_count em todos os posts.
10. V de Cramér entre `language` e `audience_location`.
11. Quantidade de `sponsor_name` distintos entre os posts patrocinados, e o total de posts patrocinados.
12. % de posts em Bilibili + RedNote.
13. Mediana de `content_length` por content_type (uma linha por tipo).

##### 2. Hashtags com correção de testes múltiplos
- **Universo:** só posts com `hashtags` preenchido (nulo = não informado, fica fora).
- Separe as hashtags pela vírgula e remova espaços nas pontas.
- Para cada hashtag presente em pelo menos 100 posts do universo, compare **posts com a hashtag** vs. **posts do universo sem a hashtag**, para `taxa_engajamento` e `shares`:
  - lift = média com a hashtag ÷ média sem a hashtag;
  - teste t de Welch (p-valor).
- Aplique a correção de Benjamini-Hochberg (FDR de 5%) separadamente por métrica.
- **Resumo por métrica:** hashtags testadas, quantas com p < 0,05 sem correção, quantas seriam esperadas por acaso (testadas × 0,05), quantas significativas após a correção, menor e maior lift.
- Tabela com as 10 hashtags de maior lift em cada métrica: hashtag, n com, n sem, lift, p-valor, q-valor (BH).

##### 3. Efeito máximo em valores absolutos
- Leia `solution/outputs/os03c/bloco1_equivalencia.csv`.
- Para cada linha, converta o efeito máximo plausível (%) em unidades absolutas por post:
  - taxa_engajamento → × média de `engajamento` da base (interações por post);
  - shares → × média de `shares`;
  - comments_count → × média de `comments_count`.
- **Resumo por variável:** maior efeito máximo plausível em % e em unidades absolutas, por métrica.
- Uma linha final com o maior valor da base inteira, por métrica.

##### 4. Tamanho de amostra para testes futuros
Posts por variante para detectar um lift, com poder de 80% e significância de 5% (bicaudal), comparando duas variantes:

`n por variante = 2 × (1,96 + 0,84)² × CV² ÷ lift²`

- **Lifts:** 5%, 10%, 20%, 40%.
- **CV (coeficiente de variação):**
  - o CV desta base para `engajamento`, `shares` e `comments_count` (calcule);
  - três cenários fixos: 0,5; 0,7 e 1,0.
- Tabela: CV (rótulo e valor) × lift → n por variante, arredondado para cima.

---

##### Entrega
- Um .csv por item em `solution/outputs/os04/`.
- `resumo_os04.md` com as quatro tabelas (no item 2, o resumo e as top 10) e a seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os04.md` e pare.


</details>


<details><summary>OS-05 — Gráficos para os relatórios</summary>

#### OS-05 — Gráficos para os relatórios

Leia o `CLAUDE.md` antes de começar.

##### Objetivo
Gerar 4 gráficos em PNG para os relatórios. **Não interprete.** Os títulos e rótulos abaixo são fixos: use exatamente esses textos.

##### Script
`solution/analysis/os05_graficos.py` → saídas em `solution/outputs/os05/`

Os gráficos 2 e 4 leem arquivos de saída de OS anteriores. Os gráficos 1 e 3 recalculam os dados a partir do CSV, com a mesma lógica das OS de origem. Não altere os scripts anteriores.

##### Padrão visual (todos os gráficos)
- matplotlib, PNG, 150 dpi, tamanho 10 × 6 polegadas.
- Fundo branco, fonte legível (mínimo 11 pt), sem grade pesada.
- Textos em português.
- **Duas cores apenas:** cinza para o padrão, uma cor de destaque para o que precisa chamar atenção.
- Números nos rótulos com vírgula decimal.

---

##### Gráfico 1 — `grafico_01_engajamento_por_faixa.png`
- **Dados:** média de `engajamento` (likes + shares + comments_count) por faixa de seguidores (até 50K, 50–100K, 100–500K, 500K–1M) × `is_sponsored`. Mesma lógica do Bloco 5 da OS-03.
- **Tipo:** barras agrupadas (orgânico em cinza, patrocinado na cor de destaque), com IC 95% (bootstrap, 1.000 reamostragens, seed 42) como barra de erro.
- **Eixo Y começando em 0** (obrigatório).
- Valor da média escrito sobre cada barra, sem casas decimais.
- **Título:** "Patrocinado e orgânico entregam o mesmo engajamento, em qualquer tamanho de creator"
- **Eixo Y:** "Interações por post (média)" · **Eixo X:** "Faixa de seguidores do creator"

##### Gráfico 2 — `grafico_02_segmentos_vs_limite.png`
- **Dados:** os lifts de `taxa_engajamento` de todos os segmentos dos níveis 1 a 4 da OS-02 (leia os .csv de `solution/outputs/os02/`).
- **Tipo:** pontos dispostos em uma faixa horizontal, um ponto por segmento (com leve dispersão vertical para não sobrepor), em cinza.
- Faixa sombreada clara entre 0,90 e 1,10, com o rótulo "Diferença mínima para importar (±10%)".
- Eixo X de 0,85 a 1,15, formatado em % de diferença (−15% a +15%).
- **Título:** "Todos os 693 segmentos ficam a menos de 2% da média"
- **Eixo X:** "Diferença de engajamento vs. média da plataforma"

##### Gráfico 3 — `grafico_03_controle_positivo.png`
- **Dados:** recalcule a busca do Nível 4 da OS-02 (platform × content_type × content_category × faixa_seguidores, n ≥ 100, `taxa_engajamento`) em dois cenários:
  - **sem injeção;**
  - **com +5%** no segmento sorteado no Bloco 3b da OS-03c: Bilibili | video | beauty | 50-100K.
- **Tipo:** dois painéis lado a lado, cada um com os 128 lifts ordenados do maior para o menor (pontos cinza). Em cada painel:
  - o segmento sorteado destacado na cor de destaque, com o rótulo da sua posição (ex.: "128º de 128" e "1º de 128");
  - uma linha horizontal tracejada no p95 do maior lift por acaso (200 permutações dentro da plataforma, seed 42), com o rótulo "Maior resultado esperado por acaso".
- **Títulos dos painéis:** "Dados originais" e "Com +5% inserido em um segmento"
- **Título geral:** "Teste do método: um efeito de +5% sai do último lugar para o primeiro"
- **Eixo Y:** "Diferença vs. média da plataforma (%)" · **Eixo X:** "Segmentos ordenados"

##### Gráfico 4 — `grafico_04_efeito_maximo.png`
- **Dados:** `solution/outputs/os03c/bloco1_equivalencia.csv`. Para cada variável, o maior efeito máximo plausível (%) entre os seus segmentos, só para `taxa_engajamento`.
- **Tipo:** barras horizontais (cinza), uma por variável, ordenadas da maior para a menor, com o valor escrito ao lado (2 casas decimais + "%").
- Linha vertical tracejada em 1%, na cor de destaque, com o rótulo "Limite de equivalência (1%)".
- Eixo X de 0 a 1,2%.
- **Nomes das variáveis em português:** Plataforma, Formato, Categoria, Faixa de seguidores, Patrocínio, Idade da audiência, Gênero da audiência, País da audiência.
- **Título:** "O maior efeito possível de cada variável fica abaixo de 0,15%"
- **Eixo X:** "Efeito máximo plausível sobre a taxa de engajamento"

**Atenção:** se algum valor calculado contradisser um título fixo (por exemplo, um efeito máximo acima de 0,15% no gráfico 4, ou um segmento além de 2% no gráfico 2), **não altere o título.** Reporte como ponto suspeito.

---

##### Entrega
- 4 PNGs em `solution/outputs/os05/`.
- `resumo_os05.md` com: o nome de cada arquivo, os valores principais usados em cada gráfico e a seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os05.md` e pare.


</details>


<details><summary>OS-06 — Lacunas finais: alcance e formato × audiência</summary>

#### OS-06 — Lacunas finais: alcance e formato × audiência

Leia o `CLAUDE.md` antes de começar.

##### Objetivo
Cobrir duas perguntas obrigatórias do brief que ainda não foram medidas por código. **Não interprete nem recomende.** Só calcule e reporte.

##### Script
`solution/analysis/os06_lacunas.py` → saídas em `solution/outputs/os06/`

Não altere os scripts das OS anteriores. Se precisar da mesma lógica, replique no novo script.

##### Regras mantidas
- Faixas de seguidores: até 50K, 50–100K, 100–500K, 500K–1M.
- IC 95% por bootstrap percentil (1.000 reamostragens). Seed 42.
- Mesma divisão em duas metades da OS-02 (seed 42).
- **Índice por post** = valor / média da métrica na plataforma do post. **Lift** = média do índice no segmento.
- **Teste contra o acaso:** embaralhe o índice dentro de cada plataforma, recalcule todos os segmentos do conjunto e guarde o maior e o menor lift; repita 200 vezes; reporte o p95 dos maiores e o p5 dos menores contra os extremos observados.

---

##### Parte 1 — Alcance: views patrocinado vs. orgânico

Métrica: `views`.

**1a. Comparação simples**
- n, média, IC 95% e mediana de views para patrocinado e para orgânico.
- Razão = média patrocinado / média orgânico, com IC 95% (bootstrap).

**1b. Comparação estratificada**
- Mesmo método do Bloco 1 da OS-03:
  - estratos platform × content_category × content_type × faixa_seguidores;
  - mínimo de 30 patrocinados e 30 orgânicos por estrato;
  - efeito = média das razões ponderada pelo tamanho do estrato;
  - IC 95% por bootstrap estratificado;
  - efeito em cada metade.
- Informe estratos existentes, usados e posts fora.

**1c. Por faixa de seguidores**
- Mesmo método do Bloco 3 da OS-03: estratos platform × content_category, mínimo de 20 + 20.
- Por faixa: n patrocinado, n orgânico, efeito, IC 95%, efeito na metade A e na metade B.

**1d. Mediana de views por faixa de seguidores × is_sponsored** (8 células).

---

##### Parte 2 — Formato × audiência

Métricas: `taxa_engajamento`, `shares`, `comments_count`.

**Três conjuntos de segmentos:**
- content_type × audience_age_distribution
- content_type × audience_gender_distribution
- content_type × audience_location

**Regras:**
- Só segmentos com n ≥ 100. Informe quantos existiam e quantos ficaram de fora.
- **Colunas:** variáveis, segmento, métrica, n, lift, IC inferior, IC superior, IC exclui 1, lift metade A, lift metade B, mesmo lado nas duas metades.
- Teste contra o acaso em cada conjunto e métrica.

---

##### Entrega
- Um .csv por item (1a, 1b, 1c, 1d e um por conjunto da Parte 2) e um .csv com os testes contra o acaso, em `solution/outputs/os06/`.
- `resumo_os06.md` com:
  1. As tabelas da Parte 1 completas.
  2. Para a Parte 2: distribuição dos lifts por conjunto e métrica (mínimo, p5, mediana, p95, máximo e quantos segmentos ficam acima de 1,03 / 1,05 / 1,10 e abaixo de 0,97 / 0,95 / 0,90), mais os 5 maiores e os 5 menores lifts de `taxa_engajamento` por conjunto.
  3. A tabela dos testes contra o acaso.
  4. Seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os06.md` e pare.


</details>


<details><summary>OS-07 — PDF dos relatórios</summary>

#### OS-07 — PDF dos relatórios

Leia o `CLAUDE.md` antes de começar.

##### Objetivo
Converter os dois relatórios em Markdown em PDF, com os gráficos embutidos. **Não altere nenhuma palavra nem número dos relatórios.** É só conversão e layout.

##### Entradas
- `solution/report/relatorio_executivo.md`
- `solution/report/relatorio_tecnico.md`
- Imagens referenciadas nos `.md` (caminhos relativos `../outputs/os05/*.png`)

##### Script e saídas
- Script: `solution/analysis/os07_pdf.py`
- Saídas: `solution/report/relatorio_executivo.pdf` e `solution/report/relatorio_tecnico.pdf`
- O HTML intermediário vai para uma pasta temporária e **não** fica no repositório.

##### Método (nesta ordem)
1. Converta o Markdown em HTML com a biblioteca Python `markdown`, extensões `tables` e `fenced_code`. Adicione `markdown` ao `requirements.txt`.
2. **Resolva os caminhos das imagens** para caminhos absolutos no HTML, dentro do script. Os `.md` não podem ser alterados.
3. Gere o PDF:
   - **Opção A:** Google Chrome ou Chromium em modo headless (`--headless --print-to-pdf`), se estiver instalado. Não exige instalar nada.
   - **Opção B:** se o Chrome não existir, use `weasyprint`.
4. Se nenhuma das duas funcionar depois de 2 tentativas, **pare e reporte** (regra do `CLAUDE.md`). Não tente uma terceira ferramenta por conta própria.

##### Layout (CSS embutido no HTML)
- **Página:** A4, margens de 2 cm.
- **Fonte:** sans-serif do sistema (Helvetica, Arial). Corpo de 10,5 pt, entrelinha de 1,45.
- **Títulos:**
  - H1 de 18 pt;
  - H2 de 14 pt;
  - H3 de 12 pt;
  - cor `#222222`, com uma linha fina vermelha `#C0392B` (a mesma cor dos gráficos) abaixo de cada H1.
- **Tabelas:** largura de 100%, bordas finas `#DDDDDD`, cabeçalho com fundo `#F2F2F2`, linhas alternadas `#FAFAFA`, fonte de 9,5 pt, sem quebra de linha de tabela entre páginas (`break-inside: avoid` nas linhas).
- **Imagens:** largura máxima de 100%, centralizadas, sem quebra entre páginas.
- **Citações em bloco (`>`):** borda esquerda `#C0392B` e fundo `#FAFAFA`.
- **Quebras de página:**
  - **Executivo:** antes de "Parte 1 — Análise de performance", antes de "Parte 2 — Estratégia recomendada" e antes de "Anexo — Regras operacionais de patrocínio".
  - **Técnico:** antes de cada seção H2 numerada a partir da 4 ("4. Resultados" em diante).
- **Títulos de seção** nunca sozinhos no fim de uma página (`break-after: avoid`).
- **Rodapé:** número da página ("Página X de Y"), se o método suportar. Se não suportar, siga sem rodapé e registre no resumo.
- **Links** entre os relatórios: mantenha o texto, sem cor chamativa.

##### Verificação (obrigatória)
- Confirme que os 2 PDFs existem e informe o número de páginas de cada um.
- Confirme que **todas as imagens referenciadas aparecem** (executivo: 2; técnico: 4).
- Converta as páginas em PNG (`pdftoppm` ou equivalente, se disponível) e **olhe cada página**. Reporte qualquer tabela cortada, imagem fora da página, título órfão ou texto sobreposto.
- Se encontrar um problema de layout, corrija só no CSS ou no script. Nunca no `.md`.

##### Entrega
- Os 2 PDFs em `solution/report/`.
- `solution/outputs/os07/resumo_os07.md` com:
  - o método usado (A ou B) e a versão;
  - o número de páginas de cada PDF;
  - o resultado da verificação visual, página por página;
  - a seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os07.md` e pare.


</details>


<details><summary>OS-07b — PDF contínuo, sem quebras de página</summary>

#### OS-07b — PDF contínuo, sem quebras de página

Leia o `CLAUDE.md` antes de começar. Esta OS **substitui o layout da OS-07**: os PDFs atuais têm espaço em branco demais por causa das quebras de página forçadas.

##### Antes de começar
O Gabriel substituiu os dois `.md` em `solution/report/` por versões corrigidas: listas com linha em branco antes e cabeçalho em linhas separadas. **Não altere os `.md`.**

##### Objetivo
Gerar PDFs **sem paginação**: cada documento é **uma única página contínua**, com largura de A4 e altura igual à do conteúdo. Os tópicos vêm um abaixo do outro, sem espaços em branco artificiais.

##### Saídas (em `solution/report/`)

| Arquivo | Conteúdo |
|---|---|
| `relatorio_executivo.pdf` | Só o executivo (substitui o atual) |
| `relatorio_tecnico.pdf` | Só o técnico (substitui o atual) |
| `relatorio_completo.pdf` | **Novo:** o executivo, uma divisória e o técnico, num único documento contínuo |

No `relatorio_completo.pdf`, entre os dois documentos, coloque uma divisória simples: uma linha fina vermelha `#C0392B` e o título "Relatório técnico", com 40 px de espaço acima e abaixo.

##### Método
Atualize `solution/analysis/os07_pdf.py`, reaproveitando a conversão Markdown → HTML e a resolução de caminhos das imagens da OS-07.

**Opção A (preferida):** Playwright usando o **Chrome já instalado** (`channel="chrome"`, sem baixar outro navegador).
1. Adicione `playwright` ao `requirements.txt`.
2. Abra o HTML e espere as imagens e fontes carregarem.
3. Meça a altura do conteúdo: `document.documentElement.scrollHeight`.
4. Gere o PDF com `width="210mm"`, `height` igual à altura medida (em px) mais 40 px de folga e `print_background=True`. **O resultado precisa ter exatamente 1 página.**

**Opção B, se a A falhar:**
1. Gere com o Chrome headless numa página muito alta (`@page { size: 210mm 5000mm }`).
2. Encontre o fim real do conteúdo com `pdfplumber`.
3. Corte a página com `pypdf`, ajustando o `mediabox`.

Se as duas opções falharem depois de 2 tentativas cada, **pare e reporte**.

##### Layout (CSS)
- **Remova todas as quebras de página forçadas** da OS-07 (`page-break` e `break-before`).
- **Página:** largura útil de 170 mm (A4 menos 2 cm de margem de cada lado), margens superior e inferior de 1,5 cm. Sem rodapé nem número de página.
- **Ritmo vertical** (a mesma escala em todo o documento):
  - H1: 32 px de espaço acima, 12 px abaixo, com a linha fina vermelha embaixo;
  - H2: 28 px acima, 10 px abaixo;
  - H3: 20 px acima, 8 px abaixo;
  - parágrafos e listas: 10 px abaixo;
  - tabelas: 12 px acima e abaixo;
  - imagens: 16 px acima e abaixo;
  - a regra horizontal (`---`): 24 px acima e abaixo, linha `#DDDDDD`.
- **Imagens:** largura de 100% da área útil, altura proporcional, centralizadas. Sem espaço extra em volta além do definido acima.
- **Fonte, cores e estilo de tabelas e citações:** os mesmos da OS-07.
- **Nunca** deixe um título separado do conteúdo logo abaixo dele.

##### Verificação (obrigatória)
1. Os 3 PDFs têm **exatamente 1 página** cada. Informe a altura de cada um em milímetros.
2. Todas as imagens aparecem: executivo 2, técnico 4, completo 6.
3. **Listas:** confirme que nenhuma lista aparece colada a um parágrafo (ex.: "Consequências para o método:" deve ser seguida de itens em linhas separadas). Verifique especificamente:
   - "O que mudaria esta conclusão" (executivo);
   - "Consequências para o método", "Fora do escopo" e "Da análise à decisão" (técnico).
4. **Visual:** converta cada PDF em PNG e olhe a imagem inteira (em partes, se for muito alta). Reporte qualquer espaço em branco maior que ~60 px que não seja intencional, tabela cortada ou texto sobreposto.
5. Apague os PDFs antigos paginados, para não ficarem dois formatos.

##### Entrega
- Os 3 PDFs em `solution/report/`.
- `solution/outputs/os07/resumo_os07b.md` com: o método usado, a altura de cada PDF, o resultado das verificações 1 a 4 e a seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os07b.md` e pare.


</details>


<details><summary>OS-08 — Ferramenta "Decisor de Campanha": núcleo</summary>

#### OS-08 — Ferramenta "Decisor de Campanha": núcleo

Leia o `CLAUDE.md` antes de começar. Esta é a maior OS do projeto: siga a estrutura abaixo **na ordem** e não adicione nada que não esteja pedido.

##### Para que serve
Um profissional de marketing quer lançar uma nova campanha e precisa analisar o histórico de posts (o "cohort passado") para saber em que se basear. Ele sobe o arquivo, a ferramenta analisa e devolve:
- o que comprovadamente funcionou, o que não funcionou e o que não faz diferença;
- se vale patrocinar;
- qual público é o ideal, se houver;
- **um briefing pronto para a próxima campanha**.

**Princípio central:** a ferramenta **nunca inventa um vencedor**. Todo insight passa pelo motor de vereditos (seção 4). "Nenhum público comprovado" é uma resposta válida e deve aparecer quando for o caso.

**Esta OS (núcleo):** estrutura, dados, motor, filtros, aba Diagnóstico com briefing, e validação.
**A OS-09 (depois):** aba "Como usar", aba "Planejar campanha" (testar ideia + simulador) e o template ampliado.

---

##### 1. Arquitetura

```
solution/tool/
├── src/
│   ├── template.html    ← estrutura + CSS
│   ├── engine.js        ← motor estatístico (funções puras, sem acesso ao DOM)
│   └── ui.js            ← interface (lê o engine, desenha na tela)
├── build_tool.py        ← lê o CSV, gera os dados compactos e junta tudo
├── validar_engine.mjs   ← roda o engine.js no Node e compara com as saídas do Python
└── decisor.html         ← ARQUIVO FINAL: único, autossuficiente, abre com dois cliques
```

- **Sem framework.** JavaScript puro.
- **Uma única dependência externa:** PapaParse 5.4.1 via `https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.4.1/papaparse.min.js`, para ler o upload. Gráficos, se houver, em SVG feito à mão.
- **Dados embutidos:** o `build_tool.py` lê `datasets/social_media_dataset.csv`, mantém só as colunas da seção 2 e embute os dados no HTML como JSON compacto (arrays por coluna). Meta: `decisor.html` com até 6 MB.
- O `engine.js` precisa funcionar **igual** no navegador e no Node (exporte as funções; sem `window` e sem `document`).

##### 2. Dados de entrada

**Colunas obrigatórias:** `post_date`, `platform`, `content_type`, `content_category`, `follower_count`, `is_sponsored`, `views`, `likes`, `shares`, `comments_count`.

**Colunas opcionais**, usadas se existirem: `audience_age_distribution`, `audience_gender_distribution`, `audience_location`, `hashtags`.

- Colunas extras são ignoradas sem erro.
- Datas: aceite `M/D/AA HH:MM AM/PM` (formato da base) e `AAAA-MM-DD` (com ou sem hora).
- `is_sponsored`: aceite `True`/`False`, `true`/`false`, `1`/`0`, `sim`/`não`.

##### 3. Preparação (no engine)
- `interacoes` = likes + shares + comments_count
- `taxa` = interacoes / views
- Faixa de seguidores: até 50K, 50–100K, 100–500K, 500K–1M, acima de 1M.
- **Índice por post** (para cada métrica) = valor ÷ média da métrica na plataforma do post, **calculado sobre os dados já filtrados**.
- **Exceção:** para avaliar a variável `platform` em si, use índice = valor ÷ média geral do recorte. Sem isso, toda plataforma teria lift 1 por definição.
- Métricas analisadas: `taxa` (principal), `interacoes` e `views` (alcance).

##### 4. Motor de vereditos (coração da ferramenta)

**Margem relevante `m`:** padrão 10%, ajustável pelo usuário entre 5% e 30%.

**Para um segmento** (ex.: `content_type = video`) e uma métrica:
- `n` = posts do segmento; `lift` = média do índice no segmento; `dp` = desvio padrão do índice no segmento;
- `ep = dp / √n`;
- **Correção para muitas comparações (Bonferroni):** se o bloco avalia `k` segmentos, use `z = quantil normal de (1 − 0,05 / (2k))` para o IC de decisão;
- `IC_decisão = lift ± z × ep`;
- `IC_equivalência = lift ± 1,645 × ep` (90%, sem correção).

**Regra do veredito** (nesta ordem):
1. `n < 100` → **Inconclusivo** ("poucos posts").
2. `IC_decisão` inteiro acima de 1 **e** `lift ≥ 1 + m` → **Funciona** (positivo).
3. `IC_decisão` inteiro abaixo de 1 **e** `lift ≤ 1 − m` → **Não funciona** (negativo).
4. `IC_equivalência` inteiro dentro de `[1 − m, 1 + m]` → **Sem efeito comprovado**.
5. Senão → **Inconclusivo**, informando quantos posts faltam:
   `n_necessário = ((1,96 + 0,84) × dp ÷ m)²` → faltam `max(0, n_necessário − n)`.

**Patrocínio** (comparação justa):
- **Estratos:** platform × content_category × content_type × faixa, com mínimo de 30 patrocinados e 30 orgânicos.
- Em cada estrato: `d = média do índice (patrocinado) − média do índice (orgânico)`.
- `efeito = 1 + Σ(w × d)`, com `w` = tamanho do estrato ÷ total usado.
- `ep = √Σ(w² × (dp_p²/n_p + dp_o²/n_o))`.
- Mesma regra de veredito, sem correção (k = 1).
- Calcule para `taxa`, `interacoes` e `views`.

##### 5. Blocos de análise

| Bloco | Segmentos | k para a correção |
|---|---|---|
| Plataforma, formato, categoria, faixa | Cada valor de cada variável, mais os pares entre elas (n ≥ 100) | Total de segmentos do bloco |
| Público | Cada valor de idade, gênero e país, mais os pares entre eles (n ≥ 100) | Total de segmentos do bloco |
| Patrocínio | Comparação estratificada (seção 4) | 1 |

Se as colunas de público não existirem, o bloco Público mostra: "Adicione as colunas de audiência para avaliar o público."

##### 6. Saúde da base (5 testes)

| Teste | Alerta se |
|---|---|
| Alcance acompanha seguidores | correlação de log(follower_count) com log(views) < 0,3 |
| Likes acompanham alcance | correlação de likes com views < 0,3 |
| Existem posts virais e fracassos | variância ÷ média de views < 10 |
| Existem posts fracassados | menos de 1% dos posts com interações abaixo de 10% da mediana |
| Volume mínimo | menos de 500 posts no recorte |

Se houver qualquer alerta, mostre no topo do Diagnóstico: "Esta base tem padrões incomuns para dados reais de redes sociais. As conclusões valem para ela, mas confirme a origem dos dados."

##### 7. Filtros globais (barra superior)
- **Período:** "Toda a base", "Últimos 30 dias", "Últimos 90 dias", "Últimos 180 dias" e "Personalizado" (de/até). "Últimos X dias" conta a partir da **data mais recente da base**, não de hoje.
- **Plataformas:** seleção múltipla, todas marcadas por padrão.
- **Margem relevante:** 5% a 30%, padrão 10%.
- Toda mudança recalcula tudo e mostra brevemente: "Recalculado para N posts".

##### 8. Aba Diagnóstico (ordem fixa na tela)

1. **Briefing da próxima campanha:** o resumo, sempre no topo.
2. **Saúde da base:** recolhida se tudo estiver ok, aberta se houver alerta.
3. **Patrocínio:** "Vale patrocinar?" → Aprovado / Barrado / Inconclusivo, para engajamento e alcance.
4. **O que funciona** (positivos) e **o que não funciona** (negativos).
5. **Sem efeito comprovado:** "Não precisa mais de atenção".
6. **Inconclusivo:** com "faltam ~N posts".
7. **Público ideal:** os positivos do bloco Público, ou "Nenhum público comprovado".
8. **Como calculamos:** recolhido. Explica o método em linguagem simples, com os números técnicos (IC, k, margem).

###### Regras do briefing
Gere o texto a partir dos vereditos, com modelos fixos (sem IA). Uma linha por item:
- **Plataforma, formato, categoria, faixa de creator:** os positivos, se houver. Se não: "Nenhuma opção comprovadamente melhor. Mantenha as atuais."
- **Público:** os positivos, se houver. Se não: "Nenhum público comprovado. Não segmente a campanha por público com base neste histórico."
- **Patrocínio:**
  - Barrado: "Não patrocine para engajamento. O orgânico entrega o mesmo."
  - Aprovado: "O patrocínio rendeu mais. Confirme com um teste antes de escalar."
  - Inconclusivo: "Dados insuficientes. Teste antes de investir."
- **O que testar nesta campanha:** se não houver nenhum positivo, sugira embutir um teste A/B entre duas versões muito diferentes, com o número de posts por versão para detectar +20%, calculado com o desvio padrão dos dados.
- **Botões:** "Copiar briefing" (texto puro na área de transferência) e "Imprimir briefing" (só o briefing, com CSS de impressão).

##### 9. Design, UI e UX

**Público e tarefa.** O usuário é do marketing, não é técnico. A tarefa é decidir em minutos em que basear a campanha. **A resposta vem primeiro**, e o detalhe vem depois, sob demanda.

**O elemento memorável é o veredito.** Todo o resto é discreto. Cada veredito aparece como um "selo": uma barra lateral colorida, um rótulo em texto e uma frase de uma linha. Nunca só cor, por acessibilidade.

###### Tokens

| Token | Valor | Uso |
|---|---|---|
| Fundo | `#F5F6F7` | Página |
| Superfície | `#FFFFFF` | Áreas de conteúdo |
| Texto | `#1F2328` | Texto principal |
| Texto secundário | `#5B636B` | Legendas, "com base em N posts" |
| Linha | `#DCDFE3` | Divisórias |
| Destaque | `#C0392B` | Marca, a mesma cor dos gráficos do relatório. Pouco usado: botão principal e link ativo |
| Funciona | `#1E7F4F` | Selo positivo |
| Não funciona | `#B42318` | Selo negativo |
| Sem efeito comprovado | `#4A5A6A` | Selo neutro |
| Inconclusivo | `#B7791F` | Selo de atenção |

- **Tipografia:** uma família só, **Public Sans** (Google Fonts), com fallback `system-ui, -apple-system, "Segoe UI", Arial, sans-serif`. Números com `font-variant-numeric: tabular-nums`.
- **Escala tipográfica:** 13 / 15 / 18 / 24 / 32 px. Corpo de 15 px, entrelinha de 1,5.
- **Espaçamento:** grade de 8 px. Conteúdo com largura máxima de 1.100 px, alinhado à esquerda. Linhas de texto com até ~80 caracteres.
- **Cantos:** raio de 6 px só em botões, campos e selos. Tabelas e seções sem raio.

###### Layout

```
┌──────────────────────────────────────────────────────────────┐
│ Decisor de Campanha        Base: base do desafio, 52.214 posts│
│ [Período ▾] [Plataformas ▾] [Margem: 10% ▾]  [Carregar base] │
├──────────────────────────────────────────────────────────────┤
│  Como usar   Diagnóstico   Planejar campanha                  │
├──────────────────────────────────────────────────────────────┤
│  Briefing da próxima campanha                    [Copiar] [Imprimir]
│  Plataforma ........ Nenhuma comprovadamente melhor...       │
│  Patrocínio ........ ▌Barrado  Não patrocine para...         │
│  ...                                                         │
│                                                              │
│  ▸ Saúde da base (1 alerta)                                  │
│  Vale patrocinar?                                            │
│  ▌Barrado   Engajamento: patrocinado rende 0,0% a mais       │
│  ▌Barrado   Alcance: patrocinado rende 0,0% a mais           │
│  O que funciona / não funciona                               │
│  (lista em linhas, uma por segmento, selo à esquerda)        │
│  ...                                                         │
└──────────────────────────────────────────────────────────────┘
```

- **A barra superior fica fixa** (sticky) com o nome da base carregada, o número de posts e os filtros.
- **Abas:** "Como usar", "Diagnóstico" e "Planejar campanha". Nesta OS, só o Diagnóstico tem conteúdo. As outras duas mostram "Disponível em breve" (a OS-09 preenche).
- **Listas de segmentos em linhas** (estilo livro-razão): selo, nome do segmento em linguagem simples ("Vídeo no TikTok"), diferença em % e "com base em N posts". **Não use cartões idênticos com sombra.**
- Se houver mais de 10 itens num bloco, mostre 10 e um botão "Mostrar todos (N)".

###### Textos
- Português, frases curtas, sem caixa alta em rótulos, voz ativa.
- **Botões dizem o que fazem:** "Carregar base", "Copiar briefing", "Imprimir briefing", "Mostrar todos".
- **Sem jargão na tela principal:** nada de "IC", "p-valor" ou "Bonferroni". Esses termos só aparecem em "Como calculamos".
- **Toda diferença vem com a base:** "+3,2% · com base em 1.204 posts".
- **Estados vazios orientam:** "Nenhum público comprovado. Isso também é uma resposta: não segmente por público com base neste histórico."
- **Erros específicos:** "O arquivo não tem as colunas: views, likes. Baixe o template na aba Como usar."

###### Interação e qualidade mínima
- Upload por botão e por arrastar e soltar. Durante o processamento: "Analisando N posts…".
- Foco visível no teclado; tudo navegável por Tab.
- Responsivo até 375 px de largura: os filtros quebram em linhas e as tabelas rolam na horizontal.
- `prefers-reduced-motion` respeitado. Sem animação de entrada; a única animação permitida é a mensagem "Recalculado".
- **Evitar:** gradientes, sombras decorativas, emojis como ícones, cartões idênticos, rótulos em caixa alta.

##### 10. Validação (obrigatória)

**10a. Motor contra o Python.** No Node, rode o `engine.js` na base completa (sem filtros) e compare:

| Item da ferramenta | Comparar com | Tolerância |
|---|---|---|
| Lift por valor de plataforma, formato, categoria, faixa, idade, gênero e país (`taxa`) | `solution/outputs/os02/` (nível 1) e `os03c/bloco1_equivalencia.csv` | 1e-6 no lift |
| Limites do IC 95% sem correção | Os mesmos arquivos (IC bootstrap) | 0,001 |
| Efeito do patrocínio em `taxa` e `views` | `os03` bloco 1 e `os06` item 1b | 0,001 |

Atenção: nesta OS a faixa "acima de 1M" fica vazia nesta base, e a faixa "até 50K" junta 1–10K e 10–50K, como nas OS anteriores.

**10b. Vereditos esperados nesta base**, como checagem de sanidade:
- patrocínio Barrado;
- nenhum positivo e nenhum negativo;
- público "Nenhum público comprovado";
- saúde da base com alertas.

Se algo diferente aparecer, **reporte, não ajuste a regra**.

**10c. Visual:** abra o `decisor.html` no Chrome headless, tire capturas a 1.280 px e a 375 px de largura e olhe cada uma. Reporte problemas de layout.

**10d. Filtro:** aplique "Últimos 90 dias" e confirme que o número de posts muda e que tudo foi recalculado.

##### Entrega
- Os arquivos da seção 1, com o `decisor.html` funcionando.
- `solution/outputs/os08/resumo_os08.md` com: o tamanho do `decisor.html`, as tabelas de validação 10a e 10b, as capturas de tela (salvas em `solution/outputs/os08/`) e a seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os08.md` e pare.


</details>


<details><summary>OS-09 — Ferramenta "Decisor de Campanha": correções, como usar, planejar campanha e design final</summary>

#### OS-09 — Ferramenta "Decisor de Campanha": correções, como usar, planejar campanha e design final

Leia o `CLAUDE.md` antes de começar. Esta OS **corrige e completa** a ferramenta da OS-08. Siga as partes **na ordem**.

##### Como construir
- Faça todas as alterações em `solution/tool/src/` (`template.html`, `engine.js`, `ui.js`) e **regenere o `decisor.html` com o `build_tool.py`**.
- **Nunca edite o `decisor.html` à mão.** No final deve existir um único `decisor.html`, com as 3 abas funcionando.
- **Público-alvo: desktop** (telas a partir de 1.280 px). **Não é preciso otimizar para celular.** Remova as regras `@media` de celular que existirem, em vez de mantê-las pela metade.
- **Motor:** a Parte 0 altera o motor uma única vez. Depois dela, nas partes 1 a 3, você pode só **acrescentar** funções ao `engine.js`.

---

##### Parte 0 — Correções da OS-08 (fazer primeiro e validar antes de seguir)

###### 0.1 Motor: comparar o segmento com o resto, não com a média (correção principal)
**Problema encontrado na revisão:** o lift compara o segmento com a média da plataforma, que **inclui o próprio segmento**. Num teste com efeito real (vídeo com +30% de likes, 6.000 posts), o vídeo rende +19,6% sobre o resto, mas a ferramenta mostra +7,7%, não passa da margem, e o briefing diz "nenhuma opção melhor". Com dados reais, isso esconderia justamente os vencedores grandes.

**Nova definição**, para todo segmento S dos blocos de desempenho e de público (o índice por post continua igual, inclusive a exceção da plataforma):
- `d = média do índice em S − média do índice no resto do recorte (fora de S)`
- `ep = √(dp_S²/n_S + dp_resto²/n_resto)`
- `lift = 1 + d`
- O veredito usa `lift` e `ep` diretamente, com as mesmas regras, a mesma margem e a mesma correção (k). Ajuste `veredito()` para receber `ep` em vez de reconstruí-lo.
- **Inconclusivos:** `n_necessário = 2 × ((1,96 + 0,84) × dp ÷ m)²`, com `dp` = desvio padrão do índice no recorte.
- O patrocínio já compara grupos: não muda.

###### 0.2 Briefing: mostrar também o que evitar
Para plataforma, formato, categoria, faixa e público, em linhas separadas:
- se houver positivos: "Priorize: …" (até 3, os de maior lift);
- se houver negativos: "Evite: …" (até 3, os de menor lift);
- se não houver nenhum dos dois: o texto atual.

###### 0.3 Teste A/B com número realista
- **Mínimo de 30 posts por versão.**
- Acrescente: "Número calculado com a variação deste histórico. Em dados reais, a variação costuma ser maior e exigir mais posts."

###### 0.4 Textos
- **Patrocínio:** se a diferença arredondar para 0,0%, escreva "rende o mesmo que o orgânico (diferença de 0,0%)".
- Remova o "· " do início de "com base em N posts".
- **Sem positivos nem negativos:** o bloco "O que funciona / não funciona" diz: "Testamos N combinações de plataforma, formato, categoria e faixa. Nenhuma rendeu comprovadamente mais ou menos que as outras."
- **Erro de upload:** limpe o aviso "Analisando…", e o banner termina com "A base anterior continua carregada."

###### 0.5 Validação da Parte 0 (obrigatória antes de seguir)
1. **Cálculo independente:** recalcule a definição nova em Python para os segmentos simples na base completa e compare com o engine. Tolerância de 1e-6 no lift e no ep.
2. **Teste com efeito conhecido:** primeiras 6.000 linhas da base, `likes` × 1,3 nos posts de `content_type = video`, margem de 10%:

   | Segmento | Lift esperado (taxa) | Veredito esperado |
   |---|---|---|
   | Vídeo | +19,6% | Funciona |
   | Imagem | −14,7% | Não funciona |
   | Texto | −13,3% | Não funciona |
   | Misto | −13,3% | Não funciona |

   O briefing deve mostrar "Priorize: Vídeo" e "Evite: Imagem, Texto, Misto".
3. **Base do desafio:** vereditos inalterados (patrocínio Barrado, nenhum positivo nem negativo, nenhum público comprovado).

---

##### Parte 1 — Template ampliado

**Colunas, nesta ordem:**

| Coluna | Tipo | Obrigatória | Descrição (vai no dicionário) |
|---|---|---|---|
| `post_date` | data | sim | Data e hora da publicação (AAAA-MM-DD HH:MM) |
| `platform` | texto | sim | Instagram, TikTok, YouTube… |
| `content_type` | texto | sim | video, image, text, mixed |
| `content_category` | texto | sim | Tema do conteúdo |
| `follower_count` | número | sim | Seguidores do perfil no dia do post |
| `is_sponsored` | sim/não | sim | O post foi patrocinado? |
| `views` | número | sim | Visualizações (alcance) |
| `likes` | número | sim | Curtidas |
| `shares` | número | sim | Compartilhamentos |
| `comments_count` | número | sim | Comentários |
| `audience_age_distribution` | texto | não | Faixa etária predominante da audiência |
| `audience_gender_distribution` | texto | não | Gênero predominante da audiência |
| `audience_location` | texto | não | País predominante da audiência |
| `hashtags` | texto | não | Hashtags separadas por vírgula |
| `clicks` | número | não | **Novo.** Cliques no link do post |
| `conversions` | número | não | **Novo.** Vendas ou cadastros atribuídos ao post (UTM ou cupom) |
| `cost` | número | não | **Novo.** Valor pago pelo post (fee do patrocínio; 0 se orgânico) |

**Uso das colunas novas no engine** (só acrescentando):
- **Se `conversions` existir:** `taxa_conversao = conversions ÷ views`, avaliada pelo mesmo motor (patrocínio e segmentos).
- **Se `cost` existir:** nos patrocinados, `custo por interação = cost ÷ interacoes` e `custo por conversão = cost ÷ conversions` (se conversions > 0). Mostre a mediana e a faixa (p10–p90), sem veredito.
- **Se não existirem:** no bloco de patrocínio, mostre "Adicione conversões e custo ao arquivo para avaliar patrocínios com objetivo de venda."

**Download:** o `template_decisor.csv` é gerado no navegador, com cabeçalho + 3 linhas de exemplo fictícias e plausíveis (1 orgânica, 2 patrocinadas).

---

##### Parte 2 — Aba "Como usar"

Conteúdo, nesta ordem:
1. **Para que serve:** "Suba o histórico de posts e descubra em que basear sua próxima campanha. A ferramenta mostra o que comprovadamente funcionou, o que não faz diferença e se vale patrocinar."
2. **Passo a passo** (sequência real, então numerada):
   1. Baixe o template.
   2. Exporte seus posts e preencha o template.
   3. Clique em "Carregar base".
   4. Escolha o período da campanha anterior.
   5. Leia o briefing.
3. **Botão "Baixar template"**, o principal da aba.
4. **Dicionário de colunas:** a tabela da Parte 1.
5. **De onde exportar:** Meta Business Suite (Instagram), TikTok Studio, YouTube Studio. Uma linha para cada, dizendo onde ficam as métricas de posts.
6. **Como ler os vereditos:** os 4 selos reais (os mesmos componentes da aba Diagnóstico), cada um com o que significa e o que fazer.
7. **Dicas:**
   - "Use pelo menos 500 posts. Abaixo disso, a maioria das respostas será Inconclusivo."
   - "Nunca compare engajamento dividindo por seguidores: perfis pequenos parecem melhores só por terem menos seguidores."
   - "Um segmento campeão isolado não é prova. Quando você testa muitos grupos, alguns parecem melhores por acaso; a ferramenta já corrige isso."
   - "Funciona significa que rendeu mais no passado. Confirme com um teste antes de escalar."
   - "Inclua cliques, conversões e custo para avaliar campanhas de venda."

---

##### Parte 3 — Aba "Planejar campanha"

###### 3a. Testar uma ideia
- **Seletores:** plataforma, formato, categoria, faixa de seguidores, patrocinado (sim / não / tanto faz) e, se as colunas existirem, idade, gênero e país. Cada um com a opção "Qualquer".
- **Botão principal "Avaliar ideia".**
- **Resultado:** os posts que combinam com a ideia vs. o resto do recorte, pelo motor (k = 1), na `taxa` e, se houver, na `taxa_conversao`:
  - **Funciona** → "Aprovada. Ideias como essa renderam mais. Confirme com um teste antes de escalar."
  - **Não funciona** → "Barrada. Ideias como essa renderam menos."
  - **Sem efeito comprovado** → "Barrada como diferencial: rende igual ao resto. Escolha por custo ou marca, não por desempenho."
  - **Se a ideia for patrocinada e o patrocínio estiver Barrado no Diagnóstico**, acrescente: "O orgânico entrega o mesmo resultado."
  - **Inconclusivo** → "Teste antes. São necessários ~N posts por versão (cerca de X semanas no seu volume atual)." O volume atual = média semanal de posts do recorte que combinam com a ideia.
- Sempre mostre: "com base em N posts parecidos".

###### 3b. Simulador de alcance e gasto
- **Entradas:**
  - posts orgânicos por mês;
  - posts patrocinados por mês;
  - valor médio por post patrocinado (R$);
  - custo por post orgânico (R$, opcional, padrão 0).
- **Saídas**, com as médias por post do recorte filtrado e IC 95%:
  - alcance (views) e interações esperadas no mês, com faixa;
  - investimento total no mês;
  - **ganho do patrocínio** = (efeito do patrocínio − 1) × média do orgânico × posts patrocinados, em views e interações;
  - **custo por interação adicional** = investimento em patrocínio ÷ interações adicionais.
- **Se o ganho for zero ou o IC incluir zero:** "R$ X em patrocínio não compram alcance nem engajamento adicional em relação ao orgânico."
- **Aviso fixo:** "A simulação supõe que mais posts não reduzem o resultado por post. O histórico não permite medir saturação; teste aumentos de cadência antes de escalar."

###### 3c. Briefing completo
- O briefing ganha a seção **"Plano de volume"**, preenchida quando o simulador é usado.
- "Copiar briefing" e "Imprimir briefing" passam a incluir essa seção.

---

##### Parte 4 — Design de UI/UX (aplicar à ferramenta inteira)

###### Direção
**Público:** time de marketing, não técnico. **Tarefa:** decidir em minutos em que basear a próxima campanha.

A ferramenta deve parecer um **documento de decisão bem diagramado**, e não um dashboard genérico: tipografia clara, muito respiro, hierarquia evidente, cor usada só para dar sentido. **O ousado fica em um lugar só: o veredito.** Todo o resto é calmo e disciplinado.

###### Tokens (mantidos da OS-08, com acréscimos)

| Token | Valor | Uso |
|---|---|---|
| Fundo | `#F5F6F7` | Página |
| Superfície | `#FFFFFF` | Áreas de conteúdo |
| Texto | `#1F2328` | Principal |
| Texto secundário | `#5B636B` | Legendas e bases ("com base em…") |
| Linha | `#DCDFE3` | Divisórias |
| Linha suave | `#ECEEF0` | Divisórias internas de tabelas e listas |
| Destaque (marca) | `#C0392B` | Botão principal, aba ativa, foco. Pouco usado |
| Funciona | `#1E7F4F` / fundo `#EAF3EE` | Selo |
| Não funciona | `#B42318` / fundo `#FBECEA` | Selo |
| Sem efeito comprovado | `#4A5A6A` / fundo `#EFF1F3` | Selo |
| Inconclusivo | `#B7791F` / fundo `#FBF3E4` | Selo |

- **Tipografia:** Public Sans (fallback `system-ui, -apple-system, "Segoe UI", Arial, sans-serif`), números com `tabular-nums`.
- **Escala:** 13 / 15 / 18 / 24 / 32 px. Títulos de seção em 24 px, peso 600. O título do briefing em 32 px, peso 700. Corpo de 15 px, entrelinha de 1,55.
- **Espaçamento:** grade de 8 px. Entre seções: 32 px. Dentro de seções: 24 px.
- **Largura:** conteúdo com máximo de 1.120 px; texto corrido com máximo de 68 caracteres por linha. Tudo alinhado à esquerda.
- **Cantos:** 6 px só em botões, campos e selos. Seções sem cantos arredondados e sem sombra; separação por borda de 1 px `#DCDFE3`.

###### Componentes
- **Selo de veredito** (o elemento memorável):
  - **na lista:** barra lateral de 4 px na cor do veredito, fundo suave, rótulo em texto, 13 px, peso 600;
  - **no resultado de "Testar uma ideia" e no topo do briefing:** versão grande, com rótulo de 18 px, peso 700, e a frase explicativa ao lado em 15 px.
  - **Nunca só cor:** sempre com o rótulo escrito.
- **Briefing (topo do Diagnóstico):** a seção mais importante.
  - **Abertura:** "Em uma frase:" seguido da conclusão principal gerada pelos vereditos (ex.: "Nenhuma escolha mudou o resultado neste histórico; não patrocine para engajamento.");
  - **corpo:** linhas com rótulo à esquerda (190 px, 13 px, cor secundária) e conteúdo à direita;
  - **destaque:** uma borda superior de 3 px na cor de destaque, a única do tipo na página;
  - **botões:** "Copiar briefing" e "Imprimir briefing" alinhados à direita do título.
- **Listas de segmentos:** linhas estilo livro-razão: selo, nome em linguagem simples ("Vídeo no TikTok"), diferença em % alinhada à direita e "com base em N posts" em cor secundária. Linhas separadas por `#ECEEF0`. Até 10 itens + "Mostrar todos (N)".
- **Barra de comparação** (só em "Testar uma ideia" e em "Vale patrocinar?"): uma barra horizontal fina, feita em SVG, com o valor do grupo vs. o resto e a faixa do IC desenhada como um traço. Discreta, sem eixo, com rótulos de valor.
- **Tabelas** (dicionário, saídas do simulador): cabeçalho em 13 px, cor secundária, sem fundo; números alinhados à direita; a faixa do IC em cor secundária ao lado do valor ("12.400 · 12.100–12.700").
- **Formulários:** rótulo em cima, 13 px; campos com 40 px de altura; foco com contorno de 2 px na cor de destaque. Um único botão principal por área.
- **Estados vazios e erros:** frase que orienta, nunca desculpa (ex.: "Nenhum público comprovado. Isso também é uma resposta: não segmente por público com base neste histórico.").

###### Layout por aba

**Barra superior** (fixa, largura total; a faixa das abas também em largura total, fundo branco):
```
┌────────────────────────────────────────────────────────────────────┐
│ Decisor de Campanha                Base: base do desafio · 52.214 posts │
│ [Período ▾] [Plataformas ▾] [Margem: 10% ▾]          [Carregar base]   │
├────────────────────────────────────────────────────────────────────┤
│ Como usar    Diagnóstico    Planejar campanha                          │
└────────────────────────────────────────────────────────────────────┘
```
Os rótulos dos filtros ficam alinhados na mesma linha de base.

**Diagnóstico:** a ordem da OS-08, com o briefing redesenhado como descrito acima.

**Como usar:** uma coluna de leitura (68 caracteres). O passo a passo é numerado, com o botão "Baixar template" logo abaixo. Em seguida vêm o dicionário em tabela, de onde exportar, como ler os vereditos (os 4 selos reais em linhas) e as dicas.

**Planejar campanha:** duas colunas.
```
┌───────────────────────────┬───────────────────────────────────────┐
│ Testar uma ideia          │ Resultado                             │
│ Plataforma   [Qualquer ▾] │ ▌Aprovada  Ideias como essa renderam  │
│ Formato      [Qualquer ▾] │            mais. Confirme com teste.  │
│ ...                       │ ━━━━━━━━━━●━━━  ideia vs. resto       │
│ [Avaliar ideia]           │ com base em 1.204 posts parecidos     │
├───────────────────────────┼───────────────────────────────────────┤
│ Simulador                 │ Alcance no mês     121.200 · 119–123 mil │
│ Posts orgânicos/mês [30]  │ Interações         24.100 · …         │
│ Posts patrocinados  [10]  │ Investimento       R$ 20.000          │
│ Valor por patrocínio [..] │ Ganho do patrocínio  0 interações     │
│ [Simular]                 │ "R$ 20.000 não compram engajamento…"  │
└───────────────────────────┴───────────────────────────────────────┘
```
- A coluna da esquerda (formulários) tem 380 px.
- A da direita (resultados) ocupa o resto.
- **Antes da primeira ação**, a coluna da direita mostra um estado vazio que orienta: "Monte uma ideia à esquerda e clique em Avaliar ideia."

###### Movimento
- Só como resposta a uma ação: ao avaliar uma ideia ou simular, o resultado aparece com um fade de 150 ms.
- O aviso "Recalculado" se mantém.
- Nada de animação de entrada da página.
- Respeite `prefers-reduced-motion`.

###### Textos
- Português, frases curtas, sem caixa alta em rótulos, voz ativa.
- **Botões dizem o que fazem:** "Avaliar ideia", "Simular", "Baixar template", "Copiar briefing".
- **Sem jargão** fora de "Como calculamos".

###### Evitar
- gradientes, sombras decorativas, cartões idênticos lado a lado;
- emojis como ícones;
- rótulos em caixa alta;
- números gigantes decorativos;
- mais de uma cor de destaque disputando atenção.

---

##### Validação (obrigatória)
1. **Parte 0:** os itens 0.5.1 a 0.5.3.
2. **Template de ponta a ponta:** baixe o template, preencha-o por script com as primeiras 2.000 linhas da base, acrescentando `clicks`, `conversions` e `cost` fictícios (seed 42), carregue na ferramenta e confirme que tudo roda, inclusive as métricas novas.
3. **Simulador:** confira à mão o cenário de 30 orgânicos + 10 patrocinados por mês, R$ 2.000 por patrocinado, base completa. Reporte o esperado e o exibido.
4. **Testar uma ideia:** reporte o veredito e o n de três ideias: "TikTok + video + tech"; "qualquer + patrocinado"; uma combinação com menos de 100 posts.
5. **Visual:** capturas das 3 abas a **1.280 px e a 1.440 px** de largura, mais uma da aba Planejar campanha depois de avaliar uma ideia e simular. Olhe cada uma e corrija o que fugir da Parte 4 (alinhamento, espaçamento, hierarquia).
6. **Acessibilidade básica:** navegação por Tab em todas as abas, foco visível, selos com texto e contraste de texto de pelo menos 4,5:1.

##### Entrega
- `decisor.html` regenerado.
- `solution/outputs/os09/resumo_os09.md` com: os resultados das validações 1 a 6, as capturas em `solution/outputs/os09/` e a seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os09.md` e pare.


</details>


<details><summary>OS-10 — Ferramenta mais didática + tema escuro</summary>

#### OS-10 — Ferramenta mais didática + tema escuro

Leia o `CLAUDE.md` antes de começar.

##### Objetivo
A ferramenta funciona, mas fala a língua de quem fez a análise. **Quem vai usá-la tem dificuldade com termos técnicos.** Reescreva o que aparece na tela para que qualquer pessoa entenda **o que o resultado significa e o que fazer**, sem precisar saber estatística. Acrescente também um tema escuro.

##### Regras
- **Não altere o motor (`engine.js`).** Esta OS é de texto, interface e tema. Alterações só em `ui.js` e `template.html`; depois, regenere com o `build_tool.py`.
- **Prioridade:** as abas **Diagnóstico** e **Planejar campanha**. Aplique as mesmas regras de linguagem em "Como usar" e na barra superior.
- **Todos os textos desta OS são exatos.** Use-os como estão. `{chaves}` são valores dinâmicos.
- O público continua sendo desktop.

---

##### 1. Regras de linguagem (valem para toda a tela, exceto "Como calculamos")

1. **Uma ideia por frase**, com até ~20 palavras.
2. **Todo resultado responde a duas perguntas:** "O que isso quer dizer?" e "O que fazer?".
3. **Números arredondados e humanos:**
   - "cerca de 404 mil", e não "404.011";
   - porcentagens inteiras ("12% a mais");
   - diferenças abaixo de 1%: "praticamente igual";
   - **sem faixas de variação na tela principal.**
4. **Palavras proibidas na tela**, que só podem aparecer em "Como calculamos": IC, intervalo de confiança, Bonferroni, segmento, recorte, estrato, índice, lift, variância, desvio, margem relevante, teste A/B, base (no sentido de dados), combinações, k, n.
5. **Substituições obrigatórias:**

| Hoje | Passa a ser |
|---|---|
| Funciona | **Funcionou melhor** |
| Não funciona | **Funcionou pior** |
| Sem efeito comprovado | **Não faz diferença** |
| Inconclusivo | **Ainda não dá para saber** |
| Barrado (patrocínio) | **Não vale a pena** |
| Aprovado (patrocínio) | **Vale a pena** |
| Briefing da próxima campanha | **Resumo para a sua próxima campanha** |
| Saúde da base | **Dá para confiar nestes dados?** |
| Margem relevante | **Diferença mínima que importa** (vai para "Ajustes", ver seção 4) |
| Carregar base | **Carregar meus dados** |
| Base: {nome}, {n} posts | **Dados: {nome} · {n} posts** |
| Creator / faixa de creator | **Influenciador / tamanho do influenciador** |
| Orgânico | **Sem pagar (orgânico)** na primeira menção de cada tela; depois, "orgânico" |
| Patrocinado | **Pago (patrocinado)** na primeira menção de cada tela; depois, "patrocinado" |
| Engajamento / interações | **Interações (curtidas, comentários e compartilhamentos)** na primeira menção; depois, "interações" |
| Alcance | **Pessoas alcançadas (visualizações)** na primeira menção; depois, "alcance" |
| Teste A/B | **Teste com duas versões** |
| com base em {n} posts | **analisamos {n} posts** |

6. **Ajuda curta "?"** ao lado de 4 termos, na primeira vez em que aparecem em cada aba. É um botão pequeno que abre um balão com uma frase:
   - **Orgânico:** "Post que você publica sem pagar ninguém para divulgar."
   - **Patrocinado:** "Post em que você paga um influenciador para publicar."
   - **Interações:** "Tudo que as pessoas fazem no post: curtir, comentar e compartilhar."
   - **Alcance:** "Quantas vezes o post foi visto."

   O balão abre por clique e por teclado (Enter) e fecha com Esc ou ao clicar fora.

---

##### 2. Aba Diagnóstico (nesta ordem)

###### 2.1 Resumo para a sua próxima campanha
- **Título:** "Resumo para a sua próxima campanha" (botões "Copiar resumo" e "Imprimir resumo").
- **Frase principal**, em 24 px, peso 600, sem selo:
  - nada melhor nem pior e patrocínio não vale a pena: "Neste histórico, nenhuma escolha mudou o resultado. E pagar influenciador não trouxe nada a mais."
  - com vencedores: "Neste histórico, {lista curta dos que funcionaram melhor} trouxeram mais resultado."
  - com perdedores e sem vencedores: "Neste histórico, nada se destacou para melhor, mas {lista curta} renderam menos."
- **Linhas do resumo** (rótulo à esquerda, conteúdo à direita):

| Rótulo | Conteúdo quando nada se destaca | Quando há resultado |
|---|---|---|
| Onde e como postar | "Pode continuar como está. Nenhuma rede social, formato ou tema rendeu mais que os outros." | "Priorize: {até 3}." e/ou "Evite: {até 3}." |
| Para quem falar | "Pode falar com o mesmo público. Nenhum grupo de pessoas respondeu melhor que os outros." | "Priorize: {até 3}." e/ou "Evite: {até 3}." |
| Pagar influenciador? | Selo **Não vale a pena** + "Posts pagos tiveram o mesmo resultado que posts sem pagar. Use o dinheiro em outra coisa." | Selo **Vale a pena** + "Posts pagos renderam {X}% a mais. Teste com poucos posts antes de aumentar o investimento." |
| O que testar nesta campanha | "Crie duas versões bem diferentes do mesmo post (por exemplo, um vídeo e uma imagem) e publique pelo menos {N} de cada. No fim, compare qual teve mais interações." | Igual |

###### 2.2 Dá para confiar nestes dados?
- **Recolhido por padrão.** No cabeçalho, um selo de semáforo:
  - **"Atenção"** (amarelo), se houver alertas: "Estes dados têm padrões estranhos para redes sociais. As conclusões valem para eles, mas confirme de onde vieram.";
  - **"Parecem confiáveis"** (verde), se não houver: "Os dados se comportam como dados reais de redes sociais."
- **Aberto**, cada teste vira uma pergunta com resposta simples:

| Hoje | Passa a ser |
|---|---|
| Alcance acompanha seguidores | "Quem tem mais seguidores é mais visto?" → "Não. Isso é estranho: normalmente é." |
| Likes acompanham alcance | "Posts mais vistos recebem mais curtidas?" → "Não. Isso é estranho: normalmente recebem." |
| Existem posts virais e fracassos | "Alguns posts bombam e outros flopam?" → "Não. Todos tiveram quase o mesmo resultado, o que é raro." |
| Existem posts fracassados | "Existem posts que quase ninguém viu?" → "Não. Na vida real, sempre existem alguns." |
| Volume mínimo | "Tem posts suficientes para concluir algo?" → "Sim, {n} posts." / "Não, só {n}. O ideal é ter pelo menos 500." |

###### 2.3 Vale a pena pagar influenciador?
- **Título:** "Vale a pena pagar influenciador?"
- **Subtítulo:** "Comparamos posts pagos e posts sem pagar que eram parecidos: mesma rede social, mesmo tema, mesmo formato e influenciadores do mesmo tamanho."
- **Duas barras horizontais lado a lado**, para interações e depois para alcance:
  - "Sem pagar (orgânico)": média por post, ex.: "cerca de 2.010 interações por post";
  - "Pago (patrocinado)": média por post.
  - Barras na mesma escala, começando em zero, com o número escrito ao lado. Sem faixa de variação.
- **Conclusão** (selo + frase):
  - **Não vale a pena:** "Os posts pagos tiveram praticamente o mesmo resultado que os posts sem pagar. Pagar não trouxe nada a mais."
  - **Vale a pena:** "Os posts pagos tiveram {X}% mais {interações/alcance}."
  - **Ainda não dá para saber:** "Ainda não há posts parecidos suficientes para comparar."
- **Sem colunas de custo e conversões:** "Quer saber se o patrocínio traz vendas? Inclua cliques, vendas e custo no seu arquivo (veja Como usar)."

###### 2.4 O que funcionou melhor e o que funcionou pior
- **Título:** "O que funcionou melhor e o que funcionou pior"
- **Nada se destacou:** "Testamos {N} jeitos diferentes de postar (redes sociais, formatos, temas e tamanhos de influenciador, sozinhos e combinados). Nenhum rendeu mais ou menos que os outros. Ou seja: o resultado não dependeu dessas escolhas."
- **Com resultados:** linhas no formato "{Vídeo no TikTok}: rendeu {12}% mais interações que o resto. analisamos {n} posts.", com o selo **Funcionou melhor** ou **Funcionou pior**.

###### 2.5 Não faz diferença
- **Recolhido.** Título: "Não faz diferença ({N})".
- **Explicação no topo:** "São escolhas que testamos e que deram praticamente o mesmo resultado. Você não precisa se preocupar com elas."
- **Linhas:** "{Imagem com influenciadores de até 50 mil seguidores}: praticamente igual ao resto."

###### 2.6 Ainda não dá para saber
- **Recolhido.** Título: "Ainda não dá para saber ({N})".
- **Explicação:** "Para estas escolhas, ainda faltam posts para ter certeza."
- **Linhas:** "{nome}: faltam cerca de {N} posts para saber."
- **Sem itens:** "Nenhuma: todas as escolhas tiveram posts suficientes para uma resposta."

###### 2.7 Para quem falar?
- **Título:** "Para quem falar?"
- **Nenhum público se destacou:** "Nenhum grupo de pessoas (por idade, gênero ou país) respondeu melhor que os outros. Pode manter o mesmo público."

###### 2.8 Como calculamos
- **Título:** "Como calculamos (para especialistas)", recolhido.
- O conteúdo técnico atual pode ficar como está.

---

##### 3. Aba Planejar campanha

###### 3.1 Estrutura em passos
- Topo da aba: "Use esta aba para testar uma ideia de campanha antes de colocar no ar."
- Duas áreas numeradas, porque é uma sequência:
  - **"1. Sua ideia de campanha"**;
  - **"2. Quanto você vai postar no mês"**.

###### 3.2 Passo 1 — Sua ideia de campanha
- **Campos visíveis:**
  - "Em qual rede social?";
  - "Em qual formato?";
  - "Sobre qual tema?";
  - "Vai pagar influenciador?" (Sim / Não / Tanto faz).
- **Link "Mais opções"**, que abre:
  - "Tamanho do influenciador";
  - "Idade do público";
  - "Gênero do público";
  - "País do público".
- **Exemplos prontos** acima dos campos, que preenchem tudo com um clique:
  - "Vídeo no TikTok";
  - "Post pago no Instagram";
  - "Imagem sobre tecnologia".
- **O botão "Ver se a ideia funciona"** fica desativado até pelo menos um campo sair de "Qualquer". Abaixo dele, em cor secundária: "Escolha pelo menos uma opção."
- **Resultado:**
  - selo grande (**Funcionou melhor**, **Funcionou pior**, **Não faz diferença** ou **Ainda não dá para saber**);
  - "**O que isso quer dizer:**" + frase;
  - "**O que fazer:**" + frase;
  - duas barras, "Posts como a sua ideia" vs. "Todos os outros posts", com as interações médias por post;
  - a linha "Analisamos {n} posts parecidos com a sua ideia."

| Veredito | O que isso quer dizer | O que fazer |
|---|---|---|
| Funcionou melhor | "Posts parecidos com a sua ideia tiveram {X}% mais interações que os outros." | "Boa ideia. Comece com poucos posts e confira se o resultado se repete antes de investir mais." |
| Funcionou pior | "Posts parecidos com a sua ideia tiveram {X}% menos interações que os outros." | "Repense a ideia ou teste uma alternativa." |
| Não faz diferença | "Posts parecidos com a sua ideia tiveram praticamente o mesmo resultado que os outros." | "Pode fazer, mas não espere um resultado melhor. Escolha pelo que for mais barato ou combinar mais com a sua marca." |
| Ainda não dá para saber | "Ainda não há posts parecidos suficientes para responder." | "Teste: publique cerca de {N} posts dessa ideia (umas {S} semanas no seu ritmo atual) e volte aqui." |

Se a ideia incluir "Vai pagar influenciador? Sim" e o patrocínio não valer a pena no Diagnóstico, acrescente: "Lembre: posts pagos tiveram o mesmo resultado que posts sem pagar."

###### 3.3 Passo 2 — Quanto você vai postar no mês
- **Campos:**
  - "Posts sem pagar (orgânicos)";
  - "Posts pagos (com influenciador)";
  - "Quanto vai pagar por post pago (R$)".
- **Remova o campo "Custo por post orgânico".**
- **Botão:** "Calcular resultado do mês".
- **Resultado**, em texto corrido:
  > "Com {30} posts sem pagar e {10} posts pagos, você deve alcançar **cerca de {404 mil} visualizações** e receber **cerca de {80 mil} interações** no mês. O investimento será de **R$ {20.000}**."
- **Comparação**, em duas colunas lado a lado:

| | Seu plano | Se todos fossem sem pagar |
|---|---|---|
| Posts no mês | 40 (10 pagos) | 40 (0 pagos) |
| Visualizações | cerca de 404 mil | cerca de 404 mil |
| Interações | cerca de 80 mil | cerca de 80 mil |
| Investimento | R$ 20.000 | R$ 0 |

- **Conclusão em destaque**, com borda lateral na cor do veredito:
  - **patrocínio sem ganho:** "Pagar os {10} posts custa **R$ {20.000}** e traz praticamente o mesmo resultado que publicá-los sem pagar. **Você economizaria R$ {20.000} no mês.**"
  - **patrocínio com ganho:** "Os {10} posts pagos trazem cerca de {X} interações a mais, o que dá cerca de **R$ {Y} por interação extra**."
- **Nota em cor secundária:** "Este cálculo supõe que postar mais não diminui o resultado de cada post. Se for aumentar muito o número de posts, faça isso aos poucos e acompanhe."

---

##### 4. Barra superior
- **Ordem:** Período · Redes sociais · Ajustes · **Carregar meus dados** · **Tema**.
- **"Plataformas"** passa a se chamar **"Redes sociais"**.
- **"Ajustes"** é um botão que abre um painel pequeno com "Diferença mínima que importa" (as opções atuais de 5% a 30%) e a explicação: "Só chamamos algo de melhor ou pior se a diferença passar deste valor. Na dúvida, deixe 10%."

---

##### 5. Tema escuro
- **Botão "Tema"** na barra superior, com três opções: "Automático" (segue o sistema; padrão), "Claro" e "Escuro".
- A escolha fica salva no navegador (`localStorage`, com `try/catch`). Se não puder salvar, a ferramenta segue normalmente.
- **Implementação:** todas as cores vêm de variáveis CSS. O tema escuro redefine as variáveis em `:root[data-tema=escuro]` e em `@media (prefers-color-scheme: dark)` quando o tema for automático. **Nenhuma cor fixa** no `ui.js` nem nos SVGs: as barras usam as variáveis.

| Token | Claro (atual) | Escuro |
|---|---|---|
| Fundo | `#F5F6F7` | `#121417` |
| Superfície | `#FFFFFF` | `#1B1F23` |
| Texto | `#1F2328` | `#E6E8EA` |
| Texto secundário | `#5B636B` | `#A3ABB3` |
| Linha | `#DCDFE3` | `#2E343A` |
| Linha suave | `#ECEEF0` | `#252A2F` |
| Destaque | `#C0392B` | `#E5584A` |
| Funcionou melhor | `#1E7F4F` / `#EAF3EE` | `#4CC38A` / `#15281F` |
| Funcionou pior | `#B42318` / `#FBECEA` | `#F27063` / `#2E1A18` |
| Não faz diferença | `#4A5A6A` / `#EFF1F3` | `#A7B4C0` / `#232A31` |
| Ainda não dá para saber | `#B7791F` / `#FBF3E4` | `#E5AE52` / `#2E2616` |

- **A impressão do resumo sai sempre no tema claro.**
- **Contraste:** todo texto com contraste de pelo menos 4,5:1 nos dois temas.

---

##### 6. Validação (obrigatória)
1. **Motor intacto:** rode `validar_engine.mjs` e `validar_os09.mjs`. Os resultados devem ser idênticos aos da OS-09.
2. **Varredura de linguagem:**
   - extraia por script todo o texto visível das abas Diagnóstico e Planejar campanha (com "Como calculamos" fechado, todos os outros recolhíveis abertos e uma ideia e uma simulação já feitas);
   - confirme que **nenhuma palavra proibida** da regra 4 aparece;
   - liste qualquer frase com mais de 25 palavras.
3. **Teste com efeito conhecido** (o mesmo da OS-09: vídeo com likes × 1,3, 6.000 linhas): capture o Diagnóstico e confirme que o resumo diz "Priorize: Vídeo" e "Evite: Imagem, Texto, Misto", em linguagem simples.
4. **Planejar campanha:**
   - o botão fica desativado com tudo em "Qualquer";
   - os 3 exemplos preenchem os campos;
   - "Mais opções" abre e fecha;
   - a comparação "Seu plano × Se todos fossem sem pagar" bate com o cálculo à mão (30 + 10 posts, R$ 2.000).
5. **Tema:** capturas a 1.440 px de **Diagnóstico** e **Planejar campanha**, nos **temas claro e escuro** (4 capturas). Olhe cada uma: nenhum texto ilegível, nenhuma cor fixa sobrando, barras e selos visíveis nos dois temas. Confirme que a escolha sobrevive a um recarregamento da página.
6. **Ajuda "?":** abre por clique e por Enter, fecha com Esc.

##### Entrega
- `decisor.html` regenerado.
- `solution/outputs/os10/resumo_os10.md` com os resultados das validações 1 a 6, as capturas em `solution/outputs/os10/` e a seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os10.md` e pare.


</details>


<details><summary>OS-10b — Correções de layout da ferramenta</summary>

#### OS-10b — Correções de layout da ferramenta

Leia o `CLAUDE.md` antes de começar.

##### Objetivo
Corrigir 5 problemas visuais encontrados num teste em navegador (1.280 px e 1.440 px, temas claro e escuro). **Não altere o motor nem os textos da OS-10.** Alterações só em `template.html` e `ui.js`; depois, regenere com o `build_tool.py`.

##### Correções

###### 1. Conteúdo grudado na barra das abas
- **Hoje:** o `main` tem `padding-top: 0`, e o primeiro bloco de cada aba começa 1 px abaixo das abas.
- **Corrija:** 32 px de espaço entre a barra das abas e o primeiro conteúdo, em todas as abas. Na aba Planejar campanha, a frase "Use esta aba…" também ganha esse espaço acima e 16 px abaixo.

###### 2. Menu "Tema" cortado na borda direita
- **Hoje:** o painel abre alinhado pela esquerda do botão e termina em 1.346 px numa tela de 1.280 px.
- **Corrija:**
  - os painéis da barra superior abrem alinhados pela **direita** do botão quando ele fica na metade direita da tela, e pela esquerda quando fica na metade esquerda;
  - nenhum painel pode passar da largura da janela.
  - Vale para "Tema", "Ajustes" e "Redes sociais".

###### 3. Balão de ajuda "?" cobrindo o campo
- **Hoje:** ao clicar no "?", o balão abre por cima do campo do formulário e esconde o valor.
- **Corrija:**
  - o balão abre **acima** do "?" (ou abaixo, se não houver espaço acima), com uma seta pequena apontando para ele;
  - largura máxima de 260 px;
  - **nunca** cobre o campo de formulário associado;
  - continua fechando com Esc e com clique fora;
  - no tema escuro, usa a superfície escura com borda (`--superficie` e `--linha`), não um fundo branco.

###### 4. Barras de comparação desalinhadas
- **Hoje:** as barras de "Interações" e de "Alcance" começam em pontos diferentes, porque o rótulo com "?" é mais largo.
- **Corrija:**
  - coluna de rótulos com **largura fixa** (200 px) em todas as comparações (Diagnóstico e Planejar campanha); o "?" fica dentro dessa largura;
  - área das barras com até 360 px;
  - todas as barras começam no mesmo ponto;
  - o número fica sempre logo à direita da barra.

###### 5. Campos nativos no tema escuro
- **Corrija:** declare `color-scheme: dark` quando o tema for escuro (e `color-scheme: light` no claro), para que listas de seleção, campos numéricos e o seletor de data acompanhem o tema. O fundo e a cor do texto desses campos usam as variáveis do tema.

##### Validação (obrigatória)
Por script, a 1.280 px e a 1.440 px, nos temas claro e escuro:
1. A distância entre a barra das abas e o primeiro conteúdo é de 32 px (± 2) nas 3 abas.
2. Com cada painel da barra superior aberto (Tema, Ajustes, Redes sociais), o retângulo do painel fica inteiro dentro da janela.
3. Com cada "?" da aba Planejar campanha aberto, o retângulo do balão **não se sobrepõe** ao campo de formulário mais próximo.
4. Nas comparações em barra, a coordenada `left` de todas as barras de um mesmo bloco é igual (± 1 px).
5. A largura da página é igual à largura da janela (sem rolagem lateral).
6. `validar_engine.mjs` e `validar_os09.mjs` continuam passando.
7. Capturas a 1.280 px: Diagnóstico e Planejar campanha (com uma ideia avaliada e uma simulação), nos temas claro e escuro, e o menu Tema aberto. Olhe cada uma.

##### Entrega
- `decisor.html` regenerado.
- `solution/outputs/os10/resumo_os10b.md` com: o resultado das verificações 1 a 6 (valores medidos), as capturas e a seção "Pontos suspeitos ou problemas encontrados".
- Entrada no `process-log/log-execucao.md`.
- Ao terminar, me mostre o `resumo_os10b.md` e pare.


</details>


<details><summary>OS-11 — Fechamento: reprodução, commits e Pull Request</summary>

#### OS-11 — Fechamento: reprodução, commits e Pull Request

Leia o `CLAUDE.md` antes de começar. Esta é a última OS, e **nela os commits estão liberados**, mas só na Etapa 6.

Siga as etapas **na ordem**. Há **3 pausas**: em cada uma, pare e espere o Gabriel.

**Exceção ao `CLAUDE.md`:** nesta OS, o registro de execução **não** vai para `process-log/log-execucao.md` (esse arquivo não existe mais). Ele vai para dentro de `process-log/process-log.md`, na seção 4 (ver a Etapa 6).

---

##### Etapa 1 — Conferir a pasta (sem alterar nada)
O Gabriel já revisou e substituiu os arquivos localmente. Confirme que `submissions/gabriel-mata/` está assim:

```
README.md
CLAUDE.md
requirements.txt
solution/   (analysis/, outputs/, report/, tool/)
process-log/
├── process-log.md
├── <export da conversa>.pdf
└── baseline/
    ├── resultado_baseline.pdf
    └── dashboard_resultado_baseline.py
```

**Não podem mais existir** em `process-log/`: `decisions.md`, `log-execucao.md`, `README.md`, `ordens-de-servico/` e `chat-claude-ai/`. O conteúdo deles foi consolidado no `process-log.md`.

- **Se algum arquivo faltar ou sobrar, não crie nem apague nada.** Liste o que encontrou e pare (⏸️ **PAUSA 1**).
- **Confira o README:** o campo do LinkedIn não pode estar `[PREENCHER]`; se estiver, pergunte ao Gabriel. Em `[DATA]`, coloque a data de hoje (DD/MM/AAAA).

##### Etapa 2 — Ajuste do validador (mínimo)
- **O problema:** desde a OS-09, o motor compara cada segmento com o resto dos posts. O `solution/tool/validar_engine.mjs` ainda compara o lift por valor de variável com as saídas da OS-02 e da OS-03c, que usam a definição antiga. Por isso acusa a diferença registrada na OS-10.
- **Altere só isso:** desative essa comparação, com o comentário: `// desde a OS-09 o lift é segmento vs. resto; validado em validar_os09.mjs`. As demais checagens do arquivo continuam iguais.
- **Confira:** rode `node validar_engine.mjs` e `node validar_os09.mjs`. Os dois precisam terminar sem erro.

##### Etapa 3 — `run_all.py` e teste de reprodução
- **Crie `solution/analysis/run_all.py`**, que roda em sequência e para no primeiro erro:
  1. `os01`, `os02`, `os03`, `os03b`, `os03c`, `os04`, `os05`, `os06`;
  2. `solution/tool/build_tool.py`;
  3. os dois validadores no Node (se o Node não existir, avise e siga).
- **Sem PDFs no `run_all`.** Os PDFs têm a etapa própria a seguir.
- Ao final, imprima uma tabela com etapa, tempo e status. Caminhos sempre relativos ao próprio arquivo.
- **Teste de reprodução:**
  1. copie `solution/outputs/` para uma pasta temporária;
  2. rode o `run_all.py`;
  3. compare todos os `.csv` novos com as cópias: devem ser idênticos byte a byte. Liste qualquer diferença.

##### Etapa 4 — PDFs (enxuta)
Única mudança de conteúdo: no `relatorio_executivo.md`, "204 combinações" virou "68 combinações". O Gabriel já trocou o arquivo localmente.

1. Confirme que `solution/report/relatorio_executivo.md` contém "68 combinações" e **não** contém "204 combinações". Se não for assim, pare e avise.
2. Rode **apenas** `python solution/analysis/os07_pdf.py`, sem alterar o script.
3. Confirme que os 3 PDFs (`relatorio_executivo.pdf`, `relatorio_tecnico.pdf`, `relatorio_completo.pdf`) foram regenerados (data de modificação de agora) e que não existe nenhum outro PDF em `solution/report/`.

⏸️ **PAUSA 2.** Avise: "PDFs regenerados. Revise os 3 arquivos em `solution/report/` e me diga se posso seguir."

##### Etapa 5 — Verificações antes do commit
1. **Links do README:** todo link relativo (inclusive para seções do `process-log.md`) aponta para algo que existe. Corrija **só o caminho**, nunca o texto, e liste o que corrigiu.
2. **Não entram no commit:** `.venv/`, `venv/`, `__pycache__/`, `.DS_Store`, `node_modules/`, HTMLs temporários e qualquer cópia do CSV de dados. Não apague nada do disco.
3. **Tamanho:** liste os arquivos acima de 5 MB. Nenhum pode passar de 50 MB.
4. **GitHub Pages:** procure, nos `.md` da pasta, duas chaves de abertura seguidas, ou uma chave de abertura seguida do sinal de porcentagem. Se encontrar, pare e avise (a publicação falharia).
5. **Branch:** `submission/gabriel-mata` (se não existir, crie a partir de `main`).

##### Etapa 6 — Registro e commits
1. **Registro desta OS.** No `process-log/process-log.md`, na seção 4, insira o registro da OS-11 (no formato das outras: feito, erros, validação) **imediatamente antes** da linha `<!-- fim do log de execução -->`. Inclua o resultado das etapas 1 a 5. O link do PR não entra, porque ainda não existe.
2. **Commits.** Use `git add -f` (o `.gitignore` da raiz ignora `submissions/`) **com os caminhos de cada linha**. Antes de cada commit, mostre o `git status`.

| # | Caminhos | Mensagem |
|---|---|---|
| 1 | `solution/analysis/`, `solution/outputs/`, `requirements.txt` | `Análise: scripts das OS-01 a OS-07, run_all e outputs` |
| 2 | `solution/report/` | `Relatórios executivo e técnico (md e pdf)` |
| 3 | `solution/tool/` | `Ferramenta Decisor de Campanha` |
| 4 | `process-log/`, `CLAUDE.md` | `Process log` |
| 5 | `README.md` | `README da submissão` |

3. Confira com `git diff --stat main...HEAD` que **nenhum arquivo fora de `submissions/gabriel-mata/`** foi alterado.

##### Etapa 7 — Push e GitHub Pages
```bash
git push -u origin submission/gabriel-mata
```

⏸️ **PAUSA 3.** Mostre ao Gabriel:

> Push feito. Ative o GitHub Pages:
> 1. Abra https://github.com/gabriellmata7/ai-master-challenge/settings/pages
> 2. **Source:** Deploy from a branch
> 3. **Branch:** submission/gabriel-mata, pasta **/ (root)** → **Save**
> 4. Me avise quando terminar.

Depois da confirmação:
- verifique por `curl`, a cada 30 segundos, por até 10 minutos, se https://gabriellmata7.github.io/ai-master-challenge/submissions/gabriel-mata/solution/tool/decisor.html responde 200;
- se não responder, informe o link de status https://github.com/gabriellmata7/ai-master-challenge/actions e siga.

##### Etapa 8 — Pull Request
1. **Repositório original:** `gh repo view gabriellmata7/ai-master-challenge --json parent`. Se não houver resposta, pergunte ao Gabriel.
2. **Se o `gh` não estiver instalado ou logado** (`gh auth status`), não instale nada. Entregue ao Gabriel o link `https://github.com/<REPO_ORIGINAL>/compare/main...gabriellmata7:ai-master-challenge:submission/gabriel-mata`, o título e a descrição abaixo.
3. **Se estiver:**
   ```bash
   gh pr create --repo <REPO_ORIGINAL> --base main \
     --head gabriellmata7:submission/gabriel-mata \
     --title "[Submission] Gabriel Mata — Challenge 004" \
     --body-file <arquivo temporário com a descrição abaixo>
   ```

**Descrição do PR:**
```
## Challenge 004 — Estratégia Social Media

Nenhuma escolha que a empresa controla (plataforma, formato, categoria, tamanho do influenciador, patrocínio, horário, hashtags) nem o perfil de público muda o engajamento. Isso está provado com teste de equivalência, poder de detecção e controle positivo (74 de 74 efeitos artificiais detectados). Consequência: cada real pago em patrocínio compra zero engajamento adicional. Recomendação: orgânico como base, patrocínio como exceção medida e plano de 8 semanas com dados reais.

- [README da submissão](https://github.com/gabriellmata7/ai-master-challenge/blob/submission/gabriel-mata/submissions/gabriel-mata/README.md)
- [Relatório executivo](https://github.com/gabriellmata7/ai-master-challenge/blob/submission/gabriel-mata/submissions/gabriel-mata/solution/report/relatorio_executivo.md)
- [Relatório técnico](https://github.com/gabriellmata7/ai-master-challenge/blob/submission/gabriel-mata/submissions/gabriel-mata/solution/report/relatorio_tecnico.md)
- [Ferramenta online: Decisor de Campanha](https://gabriellmata7.github.io/ai-master-challenge/submissions/gabriel-mata/solution/tool/decisor.html)
- [Process log](https://github.com/gabriellmata7/ai-master-challenge/blob/submission/gabriel-mata/submissions/gabriel-mata/process-log/process-log.md)
```

##### Etapa 9 — Conferência final
- Todos os arquivos do PR estão em `submissions/gabriel-mata/` (`gh pr view --json files,url,title`, ou um print da aba "Files changed").
- O título está exato.
- Abra cada link da descrição do PR (por `curl` ou `gh`) e confirme que responde 200. Os links usam a branch `submission/gabriel-mata`, então só funcionam depois do push.

##### Entrega
`solution/outputs/os11/resumo_os11.md` (fora dos commits, só para o Gabriel), com:
- o resultado de cada etapa;
- a tabela do `run_all`;
- a comparação dos CSVs;
- os links corrigidos;
- os arquivos por commit;
- o link do PR e o status da ferramenta online;
- a seção "Pontos suspeitos ou problemas encontrados".

Ao terminar, me mostre o `resumo_os11.md` e pare.


</details>


---

## 6. Exploração inicial no chat

Antes de a execução ir para o Claude Code, o Claude fez uma primeira exploração dos dados no ambiente do próprio chat. Os achados que mudaram decisões estão na seção 3.2. Abaixo, os resultados como foram registrados na época e os scripts usados.

> Dois pontos desta exploração foram corrigidos depois: a "duração de vídeo" (OS-01) e a leitura preliminar sobre creators menores (o motivo certo é custo por engajamento; ver 3.5).


#### Auditoria
- A descrição do Kaggle diz que os dados são simulados ("views simulated via a Poisson distribution").
- 52.214 posts, 27 colunas. Sem duplicatas. Nulos só em `hashtags` (8.743) e `comments_text` (8.688).
- views ≈ 10.100 em todos os posts (coeficiente de variação 1%). likes ≈ 1.510, shares ≈ 300, comments ≈ 200.
- Engajamento sobre views ≈ 19,9% ± 0,5% em todos os posts.
- follower_count é uniforme de 1K a 1M, sem correlação com views (r = 0,005).
- O mesmo creator_id aparece nas 5 plataformas, com follower_count variando cerca de 840K entre posts.
- Hashtags e descrições são palavras aleatórias (972 palavras distintas, frequências parecidas).
- comments_count tem mediana 200, mas comments_text tem mediana de 3 comentários por post.

#### Teste de sinal
- 85 testes Kruskal-Wallis (17 dimensões × 5 métricas): 1 com p<0,05 (o acaso geraria cerca de 4).
- Maior diferença entre grupos: menos de 0,75% da média.
- Replicação em duas metades: as médias dos segmentos plataforma × formato × categoria × faixa não se repetem (correlação entre metades de −0,05 a −0,08).
- Gradient boosting com validação cruzada de 5 partes: R² ≈ 0.

#### Modelo completo
- Variância explicada (eta²), 17 variáveis × 7 métricas: no máximo 0,073%.
- Recorte vídeo 30–60s + tech + 10–50K: 0,98x a 1,05x os shares da média da plataforma (n=20 por plataforma).
- Teto: o post com mais shares tem 1,27x a média.
- 175 segmentos de vídeo: melhor lift 1,021x. Com shares embaralhados, o melhor esperado por acaso é 1,024x.
- 970 hashtags (n≥100): lift entre 0,984x e 1,016x.
- **Erro de modelo detectado:** a primeira regressão OLS "mostrou" vídeo +73 shares e patrocínio +67 shares (p<0,0001). Era colinearidade perfeita (número de condição de 1e16). No modelo limpo: R²=0,0008, 3 de 47 coeficientes significativos.
- **Armadilha:** engajamento por seguidor varia 136x entre faixas, mas o engajamento absoluto é igual (~2.010) em todas. A variação é só divisão por um número menor (correlação −0,9997).
- Patrocinado vs. orgânico em 75 estratos: diferença média +0,08%, metade positiva e metade negativa.

#### Leitura preliminar (não é conclusão final)
- Cenário B: nenhuma variável explica o engajamento.
- Única consequência prática: seguidores não compram alcance neste dataset. Se o preço do patrocínio cresce com seguidores, creators menores têm custo por engajamento muito menor. A política seria pagar por resultado entregue. Isso reflete a forma como o dataset foi simulado e precisaria ser confirmado com teste na operação real.


**Scripts** (os caminhos apontam para o ambiente do chat, então eles não rodam fora dele):


<details><summary>audit.py</summary>

```python
import pandas as pd, numpy as np
pd.set_option('display.width',200); pd.set_option('display.max_columns',None)
df=pd.read_csv('/mnt/user-data/uploads/social_media_dataset.csv')
print("shape",df.shape)
print(df.isna().sum()[df.isna().sum()>0])
print("dup id",df.id.duplicated().sum(),"dup content_id",df.content_id.duplicated().sum(), "unique creators",df.creator_id.nunique())
num=['views','likes','shares','comments_count','follower_count','content_length']
print(df[num].describe(percentiles=[.01,.25,.5,.75,.99]).T)
for c in num: print(c,"CV=%.3f"%(df[c].std()/df[c].mean()))
df['eng']=df.likes+df.shares+df.comments_count
df['er_views']=df.eng/df.views
df['er_foll']=df.eng/df.follower_count
print(df[['er_views','er_foll']].describe(percentiles=[.01,.5,.99]).T)
print("zero-ish eng posts:", (df.eng<df.eng.quantile(0.001)).sum(), "min eng",df.eng.min())
print("corr matrix\n",df[num+['eng']].corr().round(3))
df['post_date']=pd.to_datetime(df.post_date,format='%m/%d/%y %I:%M %p')
print("dates",df.post_date.min(),df.post_date.max())
for c in ['platform','content_type','content_category','language','is_sponsored','disclosure_type','sponsor_category','disclosure_location','audience_age_distribution','audience_gender_distribution','audience_location']:
    print(df[c].value_counts(normalize=True).round(3).to_dict())
df.to_pickle('df.pkl')
```

</details>


<details><summary>signal_test.py</summary>

```python
import pandas as pd, numpy as np
from scipy import stats
df=pd.read_pickle('df.pkl')
df['er']=df.eng/df.views
dims=['platform','content_type','content_category','language','is_sponsored','disclosure_type','sponsor_category','disclosure_location','audience_age_distribution','audience_gender_distribution','audience_location']
df['tier']=pd.cut(df.follower_count,[0,10e3,50e3,100e3,500e3,1e6+1],labels=['<10K','10-50K','50-100K','100-500K','500K-1M'])
df['month']=df.post_date.dt.to_period('M').astype(str)
df['hour']=df.post_date.dt.hour; df['dow']=df.post_date.dt.dayofweek
df['n_tags']=df.hashtags.fillna('').apply(lambda s: 0 if s=='' else len(s.split(',')))
df['len_bin']=pd.qcut(df.content_length,5)
rows=[]
for d in dims+['tier','month','hour','dow','n_tags','len_bin']:
  for m in ['views','likes','shares','comments_count','er']:
    g=df.groupby(d,observed=True)[m]
    means=g.mean(); 
    groups=[x.values for _,x in g]
    p=stats.kruskal(*groups).pvalue
    spread=(means.max()-means.min())/df[m].mean()*100
    rows.append((d,m,len(means),round(spread,2),round(p,3)))
r=pd.DataFrame(rows,columns=['dim','metric','n_groups','max_gap_%_of_mean','kruskal_p'])
pd.set_option('display.max_rows',200)
print(r.sort_values('kruskal_p').to_string(index=False))
print("\n# significant at 0.05:",(r.kruskal_p<0.05).sum(),"of",len(r), "expected by chance ~",round(0.05*len(r),1))
df.to_pickle('df2.pkl')
```

</details>


<details><summary>deeper.py</summary>

```python
import pandas as pd, numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import cross_val_score
df=pd.read_pickle('df2.pkl')
# 1) consistency checks
print("sponsored w/ disclosure none:",((df.is_sponsored)&(df.disclosure_type=='none')).sum())
print("nonsponsored w/ disclosure != none:",((~df.is_sponsored)&(df.disclosure_type!='none')).sum())
fc=df.groupby('creator_id').follower_count.agg(['min','max','nunique'])
print("creators w/ >1 follower value:",(fc['nunique']>1).mean().round(3), " median range:",(fc['max']-fc['min']).median())
plat=df.groupby('creator_id').platform.nunique(); print("creators posting on >1 platform:",(plat>1).mean().round(3))
print("posts/creator:",df.creator_id.value_counts().describe()[['min','mean','max']].to_dict())
# views vs followers: does a 1K-follower creator get same views as 1M?
print(df.groupby('tier',observed=True)[['views','eng']].median())
small=df[df.follower_count<5000]; print("posts <5K followers:",len(small)," median views/followers:",(small.views/small.follower_count).median().round(2))
# hashtags vocabulary
tags=df.hashtags.dropna().str.split(',').explode(); print("unique tags",tags.nunique(),"top",tags.value_counts().head(5).to_dict())
# 2) split-half replication of the 'best combo' (what baseline would report)
cols=['platform','content_type','content_category','tier']
rng=np.random.default_rng(42); idx=rng.permutation(len(df)); A=df.iloc[idx[:len(df)//2]]; B=df.iloc[idx[len(df)//2:]]
def cells(x): 
    g=x.groupby(cols,observed=True).agg(n=('eng','size'),shares=('shares','mean'),er=('er','mean')); return g[g.n>=30]
ca,cb=cells(A),cells(B)
for m in ['shares','er']:
    j=ca[[m]].join(cb[[m]],lsuffix='_A',rsuffix='_B').dropna()
    top=j.sort_values(m+'_A',ascending=False).head(10)
    base=df[m].mean()
    print(f"\n{m}: corr of cell means half A vs half B = {j.corr().iloc[0,1]:.3f}  (n cells={len(j)})")
    print(f"top10 cells in A: avg lift {((top[m+'_A']/base-1)*100).mean():+.2f}%  -> same cells in B: {((top[m+'_B']/base-1)*100).mean():+.2f}%")
    best=top.iloc[0]; print("best cell",top.index[0],f"A {(best[m+'_A']/base-1)*100:+.2f}%  B {(best[m+'_B']/base-1)*100:+.2f}%")
# 3) predictive model
X=pd.get_dummies(df[['platform','content_type','content_category','language','is_sponsored','disclosure_type','sponsor_category','disclosure_location','audience_age_distribution','audience_gender_distribution','audience_location']].astype(str))
X['followers']=df.follower_count; X['len']=df.content_length; X['n_tags']=df.n_tags; X['hour']=df.hour; X['dow']=df.dow
for y in ['eng','shares','er']:
    s=cross_val_score(HistGradientBoostingRegressor(max_iter=200),X,df[y],cv=5,scoring='r2'); print(f"R2 5-fold CV for {y}: {s.mean():.4f} ± {s.std():.4f}")
# 4) sponsored vs organic stratified
st=df.groupby(['platform','tier','content_category','is_sponsored'],observed=True).er.mean().unstack()
d=(st[True]/st[False]-1)*100; print("\nsponsored vs organic ER diff within strata: mean %+.2f%%, min %+.2f%%, max %+.2f%%, strata %d, share positive %.2f"%(d.mean(),d.min(),d.max(),len(d),(d>0).mean()))
```

</details>


<details><summary>model_full.py</summary>

```python
import pandas as pd, numpy as np, statsmodels.formula.api as smf
pd.set_option('display.width',220); pd.set_option('display.max_rows',300)
df=pd.read_pickle('df2.pkl')
df['er_foll']=df.eng/df.follower_count
df['tier']=pd.cut(df.follower_count,[0,10e3,50e3,100e3,500e3,1e6+1],labels=['1-10K','10-50K','50-100K','100-500K','500K-1M'])
def lenbin(r):
    if r.content_type=='video':
        return '<30s' if r.content_length<30 else '30-60s' if r.content_length<=60 else '60-180s' if r.content_length<=180 else '>180s'
    return 'n/a'
df['vid_len']=df.apply(lenbin,axis=1)
df['has_tags']=df.n_tags>0
df['period']=df.post_date.dt.to_period('Q').astype(str)
feats=['platform','content_type','content_category','language','is_sponsored','disclosure_type','disclosure_location','sponsor_category',
       'audience_age_distribution','audience_gender_distribution','audience_location','tier','vid_len','n_tags','hour','dow','period']
metrics=['views','likes','shares','comments_count','eng','er','er_foll']
# 1) variance explained (eta^2) per feature x metric
rows=[]
for m in metrics:
    tot=((df[m]-df[m].mean())**2).sum()
    for f in feats:
        g=df.groupby(f,observed=True)[m]; between=(g.size()*(g.mean()-df[m].mean())**2).sum()
        means=g.mean(); rows.append((m,f,100*between/tot, (means.max()/means.min()-1)*100))
eta=pd.DataFrame(rows,columns=['metric','feature','pct_variance_explained','best_vs_worst_%'])
print("=== Top 12 feature x metric by variance explained ===")
print(eta.sort_values('pct_variance_explained',ascending=False).head(12).round(3).to_string(index=False))
print("\nmax variance explained excluding er_foll: %.3f%%"%eta[eta.metric!='er_foll'].pct_variance_explained.max())
# 2) multivariate OLS all features
f='{} ~ C(platform)+C(content_type)+C(content_category)+C(language)+C(is_sponsored)+C(disclosure_location)+C(sponsor_category)+C(audience_age_distribution)+C(audience_gender_distribution)+C(audience_location)+C(tier)+C(vid_len)+n_tags+C(dow)+C(period)'
print("\n=== OLS with all features ===")
for m in ['eng','shares','er']:
    r=smf.ols(f.format(m),df).fit(); sig=(r.pvalues.drop('Intercept')<0.05).sum()
    print(f"{m}: R2={r.rsquared:.4f} adjR2={r.rsquared_adj:.4f} model F p={r.f_pvalue:.3f}  sig coefs {sig}/{len(r.params)-1}")
# 3) The G4-style segment
base=df.groupby('platform').shares.mean()
seg=df[(df.vid_len=='30-60s')&(df.content_category=='tech')&(df.tier=='10-50K')]
print(f"\n=== Example segment: video 30-60s + tech + 10-50K: n={len(seg)}")
print((seg.groupby('platform').shares.mean()/base).round(3).to_string())
print("ceiling: max shares of ANY post / mean = %.2fx ; best possible segment can't exceed this"%(df.shares.max()/df.shares.mean()))
# 4) exhaustive segment search like a naive analyst, with replication
cols=['platform','vid_len','content_category','tier']
v=df[df.content_type=='video']
g=v.groupby(cols,observed=True).shares.agg(['size','mean']); g=g[g['size']>=20]
g['lift']=g['mean']/v.groupby('platform').shares.mean().reindex(g.index.get_level_values(0)).values
print(f"\n=== {len(g)} video segments (n>=20): lift range {g.lift.min():.3f}x – {g.lift.max():.3f}x")
print(g.sort_values('lift',ascending=False).head(3).round(3))
# permutation: shuffle shares, what max lift by chance?
rng=np.random.default_rng(0); mx=[]
for i in range(200):
    vv=v.copy(); vv['shares']=rng.permutation(vv.shares.values)
    gg=vv.groupby(cols,observed=True).shares.agg(['size','mean']); gg=gg[gg['size']>=20]
    mx.append((gg['mean']/vv.groupby('platform').shares.mean().reindex(gg.index.get_level_values(0)).values).max())
print(f"max segment lift with shares randomly shuffled: median {np.median(mx):.3f}x, 95th pct {np.percentile(mx,95):.3f}x  -> observed best {g.lift.max():.3f}x")
# 5) per-follower engagement artifact
print("\n=== Engagement / followers by tier (the trap) ===")
print(df.groupby('tier',observed=True).agg(median_eng=('eng','median'),median_er_foll=('er_foll','median')).round(4))
print("corr(log er_foll, log followers) = %.4f"%np.corrcoef(np.log(df.er_foll),np.log(df.follower_count))[0,1])
# 6) hashtags
t=df[['shares','eng']].join(df.hashtags.dropna().str.split(',').explode().rename('tag'))
tg=t.groupby('tag').agg(n=('eng','size'),shares=('shares','mean')); tg=tg[tg.n>=100]
print(f"\n=== {len(tg)} hashtags with n>=100: shares lift range {tg.shares.min()/df.shares.mean():.3f}x – {tg.shares.max()/df.shares.mean():.3f}x")
# 7) comments consistency
df['n_comment_texts']=df.comments_text.fillna('').str.count(r'\.')
print("\ncomments_count median",df.comments_count.median()," vs comment texts per post median",df.n_comment_texts.median())
eta.to_csv('eta_table.csv',index=False)
```

</details>


<details><summary>check_ols.py</summary>

```python
import pandas as pd, numpy as np, statsmodels.formula.api as smf, warnings; warnings.filterwarnings('ignore')
exec(open('model_full.py').read().split('# 1)')[0])
f='shares ~ C(platform)+C(content_type)+C(content_category)+C(language)+C(is_sponsored)+C(disclosure_location)+C(sponsor_category)+C(audience_age_distribution)+C(audience_gender_distribution)+C(audience_location)+C(tier)+C(vid_len)+n_tags+C(dow)+C(period)'
r=smf.ols(f,df).fit()
s=r.pvalues[r.pvalues<0.05].drop('Intercept',errors='ignore')
print(pd.DataFrame({'coef':r.params[s.index].round(2),'p':s.round(4)}))
print("condition number:",round(r.condition_number))
# clean model: drop collinear sponsor descriptors
f2='shares ~ C(platform)+C(content_type)+C(content_category)+C(language)+C(is_sponsored)+C(audience_age_distribution)+C(audience_gender_distribution)+C(audience_location)+C(tier)+n_tags+C(dow)+C(period)'
r2=smf.ols(f2,df).fit(); print("clean model: R2=%.4f, F p=%.3f, sig %d/%d"%(r2.rsquared,r2.f_pvalue,(r2.pvalues.drop('Intercept')<0.05).sum(),len(r2.params)-1))
print(r2.params[r2.pvalues<0.05].drop('Intercept',errors='ignore').round(2))
```

</details>


---

## 7. Baseline

- **Arquivos originais:** [`baseline/resultado_baseline.pdf`](baseline/resultado_baseline.pdf) (relatório) e [`baseline/dashboard_resultado_baseline.py`](baseline/dashboard_resultado_baseline.py) (código).
- **Como foi feito, objetivo, verificação e uso como revisor:** seção 3.6.
- **Comparação de métodos, item por item:** relatório técnico, seção 9.

---

## 8. Export da conversa

**[Conversa completa com o Claude (chat)](https://claude.ai/share/8fe74758-e8bc-4805-b801-e5ad447b62c8)**: link público, sem login.

É a evidência bruta de tudo o que está resumido nas seções 2 e 3: o planejamento, cada decisão, as revisões críticas e a escrita de cada Ordem de Serviço, na ordem em que aconteceram.
