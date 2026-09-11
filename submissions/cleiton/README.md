# Submissão — Cleiton Eugênio — Challenge 002

## Sobre mim

- **Nome:** Cleiton Eugênio
- **LinkedIn:** https://www.linkedin.com/in/cleiton-eugenio-dados/
- **Challenge escolhido:** 002 — Redesign de Suporte (Operações / CX)

---

## Executive Summary

A base operacional entregue tem 8.469 tickets — não os ~30.000 descritos no briefing — e só 16,6% (1.402) têm timestamps consistentes para medir tempo de ciclo; o resto é status Open/Pending sem resolução ou tem `Time to Resolution` anterior a `First Response Time`. Nos válidos, a mediana do intervalo entre primeira resposta e resolução é 6,4h e o P90 é 16,0h (2,5× a mediana). Treinei um classificador (TF-IDF + regressão logística) nos 47.837 tickets do Dataset 2, que atinge 84,9% de acurácia geral e, ao só auto-rotear tickets com confiança ≥60%, cobre 82,8% do volume com 91,4% de acerto — esse par cobertura×acurácia condicional, não a acurácia bruta, é a base de cenários ilustrativos de capacidade (referência: 594h / R$29.713 por ano, antes dos custos de implantação e operação). A recomendação central: automatizar classificação, roteamento e rascunho de resposta para o segmento de alta confiança; nunca automatizar decisão final em reembolso, cancelamento, segurança ou baixa confiança.

---

## Solução

### Abordagem

1. Li o brief e o guia de submissão, e explorei os dois datasets independentemente antes de escrever qualquer métrica — confirmei por conta própria (não copiando de nenhuma fonte) que o arquivo tem 8.469 linhas e que há pares de timestamp invertidos, antes de decidir como tratar isso.
2. Separei o trabalho em três scripts Python reprodutíveis (`solution/01_diagnostic.py`, `02_train_classifier.py`, `03_roi_model.py`) em vez de um notebook único, para que cada etapa tenha uma saída JSON auditável e a estimativa de ROI dependa explicitamente da métrica medida do classificador — não de um multiplicador arbitrário.
3. Treinei o classificador com um holdout estratificado de 20% (nunca visto no treino) e reportei acurácia condicional a um limiar de confiança, porque a pergunta que importa para produção não é "qual a acurácia média" e sim "o que dá pra confiar o suficiente pra automatizar".
4. Construí um protótipo interativo (não CLI): um dashboard onde o classificador — TF-IDF + regressão logística reimplementados em ~40 linhas de JavaScript a partir dos pesos exportados — roda 100% no navegador, sem backend. Qualquer texto pode ser colado e classificado ao vivo, não só os exemplos pré-selecionados.
5. Documentei premissas de ROI e limitações de dados explicitamente, em vez de apresentar um número de economia sem contexto.

### Resultados / Findings

**Diagnóstico (Dataset 1):**
- 8.469 tickets no arquivo; apenas 2.769 (Closed) têm resolução e nota; apenas 1.402 (16,6%) têm um par de timestamps válido (resolução posterior à primeira resposta) — a maior parte da base não serve para medir tempo de ciclo sem essa filtragem.
- Mediana de resolução: 6,4h · P90: 16,0h · gap P90−mediana: 9,6h. A cauda é o problema, não a mediana.
- Piores combinações canal×prioridade×tipo por P90: `Email/Low/Technical issue` (20,7h), `Social media/High/Refund request` (20,0h, CSAT 2,90), `Chat/Low/Refund request` (19,9h) — todas com n pequeno (13–22), sinal para investigar, não regra estatística.
- Mutual information entre CSAT e canal/prioridade/tipo/tempo de ciclo é essencialmente zero em todas as variáveis — achado honesto: **a análise exploratória não identificou evidência forte de associação**. Isso por si só é um resultado (falta instrumentação melhor, não falta de esforço analítico).
- Reforcei isso com um segundo método: intervalos de confiança de 95% por bootstrap (2.000 reamostragens, seed 42) nas 2.769 avaliações por canal/prioridade/tipo. Reembolso tem a menor média observada (2,93/5), mas os intervalos entre grupos se sobrepõem — duas fontes de evidência apontando pra mesma conclusão (nenhuma variável isolada explica CSAT), não só uma métrica isolada.

**Classificador (Dataset 2, 47.837 tickets, 8 categorias):**
- TF-IDF (uni+bigramas, 3.000 features) + regressão logística, holdout estratificado de 9.568 tickets: **84,9% de acurácia geral, macro F1 0,846**.
- Ao só auto-rotear quando a confiança ≥60%: cobre **82,8%** do volume com **91,4%** de acurácia condicional (vs. 53,7% nos 17,2% restantes, de baixa confiança).
- Desempenho por categoria varia bastante: Access (F1 0,887) e Storage (F1 0,885) são fortes; Administrative rights (F1 0,744) é a mais fraca — a categoria menos frequente no treino (1.760 exemplos).

**Estimativa de capacidade:** ancorado na cobertura medida do classificador, não em queue time convertido em custo de mão de obra (ver Limitações). A referência assume 70% de elegibilidade entre os tickets acima do limiar de confiança (nem todo ticket de alta confiança pode ser automatizado — regras de risco descartam parte), 3min de triagem manual eliminada por ticket corretamente roteado, 8min de retrabalho por ticket roteado errado, e R$50/h: resulta em **594h/ano e R$29.713/ano**, antes dos custos de implantação e operação. Um cenário sem desconto de elegibilidade (100% dos tickets de alta confiança) chega a 849h/R$42.447 — mantido como comparação histórica, não como número a perseguir. A estimativa é sensível às premissas: com elegibilidade de 50%, 1min de triagem e 12min de retrabalho, o resultado vira **negativo** (-26h/ano) — ou seja, sob premissas pessimistas razoáveis, a automação pode custar mais em retrabalho do que economiza. Não é piso garantido nem desperdício observado; é um cenário para validar em produção, não uma previsão.

**Protótipo:** [`solution/dashboard/`](solution/dashboard/) — React + visx (o mesmo stack de gráficos da peça de portfólio original), no tema visual que eu já usava (Manrope + DM Mono, dark, textura granulada), com diagnóstico operacional data-driven, navegação lateral com scroll-spy pelas 7 seções, e **Winnow** — a central de triagem ao vivo (classificador rodando no navegador, detecção de duplicata por similaridade de texto, triagem de prioridade calculada só do texto, ciclo completo de atendimento com aprovação humana). Testado de ponta a ponta com Playwright (Chromium headless) a cada mudança: gráficos desenham, classificador funciona, detecção de duplicata e triagem de prioridade se comportam como esperado, zero erros no console.

**Ao vivo, sem instalar nada:** https://winnow-flame.vercel.app/dashboard/index.html — mesmo código deste repositório ([cleitoneugenio/winnow](https://github.com/cleitoneugenio/winnow)), deploy automático a cada push. Rodar localmente: instruções em [`solution/README.md`](solution/README.md). Existe também uma versão estática anterior no Claude Artifact, sem visx e sem as funcionalidades mais recentes do Winnow: https://claude.ai/code/artifact/1b04cec8-cbc9-4a6e-939c-256236422aba

### Recomendações

1. **Corrigir a instrumentação antes de prometer SLA.** Sem `created_at`, primeiro toque e motivo de reabertura consistentes, qualquer número de tempo de ciclo é sobre 16,6% da base, não sobre a operação.
2. **Automatizar classificação + roteamento para o segmento de confiança ≥60%** (82,8% do volume, 91,4% de acerto) com rascunho de resposta sujeito a aprovação do agente — não decisão final automática em nenhum caso.
3. **Nunca automatizar** reembolso, cancelamento, cobrança contestada, segurança/acesso e qualquer caso de baixa confiança — ver justificativa com dados nas seções "05 · Decisão" e "06 · ROI" do protótipo.
4. **Medir antes de comemorar.** A estimativa depende de premissas não medidas (elegibilidade, minutos de triagem e de retrabalho). Antes de prometer R$29,7 mil/ano: medir esforço ativo real por ticket, medir elegibilidade de fato após as regras de risco (não assumir 70%), e comparar com um grupo de controle acompanhando transferências, reaberturas e satisfação — só depois disso vale comparar com outras oportunidades e estimar retorno.

### Limitações

- O dataset operacional é pequeno (8.469, não 30.000) e majoritariamente sem timestamps válidos — o diagnóstico de tempo de ciclo cobre 1.402 tickets, uma fração da operação real.
- As categorias do Dataset 2 (TI interno: Hardware, Access, HR Support…) são diferentes das categorias comerciais do Dataset 1 (Technical issue, Billing inquiry…) — o classificador prova a mecânica de triagem com dados reais e um dataset rotulado de verdade, mas uma implantação real precisa de tickets e taxonomia da própria operação de suporte ao cliente.
- Mutual information mede associação, não causalidade — a ausência de sinal forte de CSAT nesta análise exploratória não prova que as variáveis não importam, só que não há evidência disso *nestes* dados. Os intervalos de confiança por bootstrap ajudam a mostrar incerteza amostral, mas não corrigem viés de seleção dos respondentes nem o problema de múltiplas comparações (testamos várias variáveis; algum sinal aparecer "significativo" por acaso é esperado).
- O classificador é só em inglês e baseado em TF-IDF (bag-of-words); não captura negação, sarcasmo ou contexto longo. Um piloto real deveria comparar com embeddings/modelo supervisionado maior e avaliar por classe, especialmente as raras (Administrative rights, Internal Project).
- A estimativa de ROI é um cenário com premissas explícitas (elegibilidade, minutos de triagem e retrabalho), não uma medição — está rotulada como tal no próprio protótipo, e é sensível o bastante para virar negativa sob premissas pessimistas plausíveis (ver Resultados). Além disso, ela transfere o desempenho do classificador medido no corpus de TI para uma operação de suporte comercial — essa transferência não foi validada com dados reais da operação.
- Parte do código desta pasta foi editada por uma sessão paralela de Codex (GPT-5), sob minha direção, rodando ao mesmo tempo que a sessão de Claude Code. O process log descreve o que dá para verificar pelas mudanças reais nos arquivos; não há, da parte do Claude, visibilidade sobre os prompts ou o raciocínio interno daquela sessão — só sobre o resultado.

---

## Process Log — Como usei IA

> Esta submissão foi construída com **duas sessões de IA em paralelo, no mesmo repositório**: Claude Code (Claude Sonnet 5), nesta sessão, e Codex (GPT-5), numa sessão separada rodando ao mesmo tempo — ambas sob minha direção. Isso significa que parte dos arquivos desta pasta foi editada pelo Codex sem eu repassar cada detalhe para o Claude; o que está registrado abaixo sobre o trabalho do Codex é o que dá para verificar pelas mudanças reais nos arquivos (diffs), não o raciocínio interno daquela sessão — essa visibilidade eu tenho, o Claude não tem.
>
> **Iterações:** o workflow abaixo tem 15 rodadas registradas do lado do Claude Code, cada uma um ciclo de pedido → execução → eu revisando e corrigindo o rumo (não 1 prompt → 1 resposta → pronto). Pelo menos quatro delas mudaram uma decisão já tomada depois que eu vi o resultado funcionando: reconstruir do zero em vez de reaproveitar a submissão anterior, trocar SVG por React+visx de verdade, remover a entrada de prioridade do cliente depois de ver a comparação funcionando, e a correção do cálculo de ROI depois do número de R$4,3 milhões. Do lado do Codex, teve uma quantidade parecida de rodadas — não consigo contar com precisão porque não tenho acesso a essa sessão, só ao resultado nos arquivos.

### Ferramentas usadas

| Ferramenta | Para que usou |
|------------|--------------|
| Claude Code — Opus, reasoning effort alto | Decisões de arquitetura: como estruturar o diagnóstico em scripts numerados e auditáveis, como ancorar o ROI numa métrica medida em vez de um multiplicador solto, quando reconstruir do zero em vez de aproveitar a submissão anterior, e as trocas de abordagem depois de cada auditoria (visx fora do Artifact, duplicata real, triagem de prioridade sem input do cliente) |
| Claude Code — Sonnet 5, reasoning effort alto | Implementação do que foi decidido: leitura do brief, exploração e validação independente dos dados, o código em si (scripts Python, dashboard React+visx), verificação com Playwright, redação deste README |
| Codex, sessão paralela — modelo Astra | Decisões de arquitetura e novas abordagens: desenho do desconto de elegibilidade e dos cenários múltiplos no modelo de ROI (`03_roi_model.py`), escolha de reforçar o diagnóstico com intervalos de confiança por bootstrap (`01_diagnostic.py`) |
| Codex, sessão paralela — modelo Terra | Implementação do que foi decidido acima, e evolução da Central do Agente (`dashboard/app.js`) — ciclo de vida completo do atendimento (confirmação do cliente, reabertura, CSAT) e ampliação da regex de risco |
| Python (pandas, scikit-learn) | Diagnóstico operacional e treino/avaliação do classificador |
| React + visx (via esm.sh) | Dashboard interativo final, no tema de portfólio |
| Playwright (Chromium headless) | Verificação automatizada de que o dashboard renderiza e o simulador funciona, com screenshot e checagem de console |
| Artifact (Claude) | Publicação de uma versão estática alternativa do dashboard (sem visx), acessível sem rodar nada localmente |

### Workflow

1. Pedi para resolver o Challenge 002. O Claude buscou o repositório e o README específico do desafio antes de tocar em qualquer dado.
2. Ele encontrou uma submissão anterior já existente na pasta `submissions/cleiton/`, feita por outra ferramenta (Codex/GPT-5) em uma sessão diferente, e me perguntou como proceder em vez de sobrescrever silenciosamente. Decidi reconstruir do zero, em pasta separada, para ter uma segunda passada independente sobre os mesmos dados.
3. Também decidi, quando perguntado, não configurar push/PR automático nesta sessão (sem `gh` CLI nem credenciais no ambiente) — o repositório fica pronto localmente para eu revisar e enviar o PR manualmente.
4. O Claude validou de forma independente os achados de qualidade de dados (8.469 linhas, timestamps inválidos) antes de reutilizá-los, em vez de aceitar o número da submissão anterior sem checar.
5. Separou a análise em scripts numerados (diagnóstico → classificador → ROI) para que a estimativa de ROI dependesse de um número medido (cobertura do classificador), não de um multiplicador solto.
6. Construiu o classificador, bateu num erro de API do scikit-learn (parâmetro `multi_class` removido na versão instalada), corrigiu e retreinou.
7. Construiu o dashboard interativo, carregando as skills de design e visualização de dados do próprio Claude Code antes de escrever o HTML, para garantir paleta validada e hierarquia tipográfica em vez de um layout genérico.
8. Depois de eu comparar esta submissão com a anterior (feita com Codex) e decidir que esta era a mais forte, pedi para unir as duas: manter o conteúdo e os números desta submissão, mas reaproveitar o visual de portfólio (tema escuro, Manrope + DM Mono, textura granulada) que eu mesmo tinha desenhado para a peça anterior. O Claude leu os arquivos-fonte dessa peça (`submissions/cleiton/dashboard/`), extraiu o sistema de design e reconstruiu o dashboard nele — trocando os números fixos por leitura dinâmica dos JSONs desta submissão. Como o publicador de Artifacts do Claude bloqueia os pacotes que React/visx precisam carregar em tempo de execução, essa primeira versão unida saiu em SVG puro, sem visx, para continuar tendo um link ao vivo.
9. Eu perguntei especificamente se o Claude estava usando visx, reparei que alguns gráficos pareciam grandes demais, e pedi visx de verdade. O Claude explicou a restrição técnica do publicador de Artifacts antes de agir e me deu três opções (D3.js como troca compatível, React+visx fora do Artifact, ou manter o SVG atual); escolhi React+visx de verdade, aceitando abrir mão do link instantâneo do Artifact para esse componente. Ele reconstruiu o dashboard como um app React real (`solution/dashboard/`, sem build step, importando React/react-dom/visx via esm.sh) e, antes de me devolver, subiu um servidor HTTP local e dirigiu o próprio Playwright (Chromium headless) contra a página — confirmou os dois gráficos visx desenhando barras de verdade, testou o simulador clicando num preset e no botão de classificar, e checou o console em busca de erros, em vez de simplesmente afirmar que funcionava.
10. Perguntei sobre a metodologia do classificador e se dava pra melhorar a acurácia trocando de modelo. O Claude listou as alternativas (SVM, embeddings pré-treinados, fine-tuning de transformer, zero-shot via LLM) com o trade-off de cada uma, e recomendou testar embeddings antes de mexer na arquitetura do protótipo — avisando que o texto já vem pré-processado/lematizado, o que podia limitar o ganho. Pedi pra ele rodar o teste. Resultado real, em `solution/experiments/04_embeddings_experiment.py`: embeddings (sentence-transformers all-MiniLM-L6-v2) pioraram a acurácia em toda métrica (84,9% → 78,3%; cobertura a 60% de confiança caiu de 82,8% para 76,0%), confirmando a hipótese. Mantive o modelo atual — decisão baseada em teste real, não em intuição sobre qual método "deveria" ser melhor.
11. Pedi para auditar se a Central do Agente respondia de verdade "o que automatizar / o que não automatizar / como funciona na prática". O Claude leu o próprio código (não só a cópia que tinha em memória) e achou uma reivindicação sem lastro: um card prometia "detecção de duplicidade" que não existia em lugar nenhum. Pedi para implementar de verdade — ele reaproveitou o mesmo vetor TF-IDF do classificador (refatorando `classify` para expor um `vectorize()` comum) para comparar por similaridade de cosseno contra tickets abertos, com limiar de 60% pausando a automação até o agente vincular ou descartar. Depois reparei que o diagrama de fluxo estático (5 passos) tinha ficado defasado da demonstração real; pedi para refazer, e ele expandiu para 7 passos incluindo a etapa de duplicata e o ciclo completo (confirmação do cliente, CSAT, reabertura).
12. Notei que o composer deixava o "cliente" escolher a prioridade do ticket, e que a fila confiava nisso — o que contradiz o próprio achado do diagnóstico (prioridade declarada não prediz bem o tempo real de resolução). Pedi para implementar uma triagem de prioridade calculada a partir de sinais no texto (termo de risco, termo de urgência, confiança do classificador), mostrando prioridade declarada vs. sugerida lado a lado quando divergiam. Depois de ver funcionando, decidi que a entrada do cliente nem deveria existir — autorrelato de urgência é fácil de inflar (todo mundo marca "alta"). Pedi para tirar o campo por completo; o Claude removeu o seletor do composer, o estado `declaredPriority` e a UI de comparação, deixando só a prioridade calculada pela triagem automática.
13. Ao longo dessas últimas rodadas, o Claude recebia avisos automáticos de que arquivos como `01_diagnostic.py`, `03_roi_model.py` e `dashboard/app.js` tinham "mudado desde a última leitura", e assumiu que era conteúdo de partes anteriores da própria conversa resumidas pelo sistema. Eu expliquei que não — eu rodo uma sessão de **Codex em paralelo**, no mesmo repositório, e boa parte dessas mudanças (intervalos de confiança por bootstrap no diagnóstico, o desconto de elegibilidade e os cenários no modelo de ROI, e boa parte da evolução da Central do Agente) foi o Codex, sob minha direção também, não uma memória perdida do Claude. Pedi para corrigir o process log para refletir isso com precisão em vez de manter a atribuição só ao Claude Code.
14. Também contei que, dentro do Codex, não usei um modelo só: **Astra** para decisão de arquitetura e para pensar em abordagens novas, **Terra** para implementar o que foi decidido. Pedi para registrar essa divisão no process log — separar "quem decidiu o quê" de "quem escreveu o quê" é exatamente o tipo de detalhe que o guia de submissão pede ("quais ferramentas você usou e por quê"), e eu não tinha como saber disso sem o candidato me contar, já que não tenho acesso à sessão do Codex.
15. Por fim, contei que fiz a mesma divisão aqui no Claude Code: **Opus** (reasoning effort alto) para as decisões de arquitetura, **Sonnet 5** (reasoning effort alto) para a implementação depois de cada decisão tomada. Como o Claude não guarda memória de qual modelo respondeu qual mensagem entre trocas, essa separação também só entrou no log porque eu contei — mesma lógica do item anterior, agora do lado de cá.
16. Antes de fechar, revisei o dashboard e achei ele complexo demais pra quem só quer avaliar rápido. O Claude sugeriu um resumo de 60 segundos no topo; recusei — a profundidade é o ponto forte, não o problema. O problema real era a fricção de abrir (precisar rodar um servidor local). Decidi separar o Winnow num repositório próprio (`cleiton/winnow`) pra hospedar na Vercel, que eu já uso. Copiei `dashboard/` + `output/*.json` pra lá, mantendo a mesma estrutura relativa (senão o `fetch('../output/...')` quebraria), e dei push direto — sem precisar de token porque as credenciais do GitHub já estavam salvas nesta máquina. O primeiro deploy deu 404 até na raiz; o Claude reconheceu o padrão (Vercel adivinhando um "Output Directory" errado quando não há framework detectado), corrigiu com um `vercel.json` explícito (`@vercel/static` forçado em tudo) e testou a URL de produção de verdade antes de me devolver, em vez de só confirmar que o `git push` tinha funcionado.

### Onde a IA errou e como corrigi

Na primeira versão do script de diagnóstico, o Claude calculou "desperdício" multiplicando as horas da cauda longa (P90 − mediana) diretamente por um custo horário de agente — isso gerou uma economia projetada de **R$4,3 milhões/ano**, um número absurdo e exatamente a "contabilidade criativa" que o brief do desafio avisa para evitar: tempo de fila/espera não é a mesma coisa que hora de trabalho de agente. Interrompi essa linha de raciocínio, e o Claude reescreveu a lógica: separou o tempo de ciclo (fila, não custo) do cálculo de ROI, e reconstruiu a estimativa de economia a partir de algo medido de verdade — cobertura e acurácia condicional do classificador — chegando a um número muito mais modesto e defensável (**~R$42 mil/ano**). Prefiro o número pequeno e honesto ao grande e frágil.

Depois dessa correção, o Codex (do lado da minha sessão paralela) revisou de novo: descontou o cálculo por uma taxa de elegibilidade após regras de risco (nem todo ticket de alta confiança pode ser automatizado) e rodou uma análise de sensibilidade, chegando à referência atual de **R$29,7 mil/ano** — com o número anterior (R$42,4 mil) mantido como comparação histórica sem esse desconto. É por isso que o texto acima cita R$42 mil (a correção que eu vi acontecer, aqui) e o resto do README cita R$29,7 mil (a revisão que veio depois, do lado do Codex) — os JSONs em `solution/output/` e o dashboard sempre refletem o número mais atual.

### O que eu adicionei que a IA sozinha não faria

O julgamento central foi meu em dois pontos: (1) não deixar a IA sobrescrever ou ignorar um trabalho anterior sem eu decidir explicitamente o que fazer com ele — pedi para reconstruir do zero em pasta separada, preservando o histórico; e (2) recusar o primeiro número de ROI por parecer bom demais para ser real, forçando a reconstrução com uma base mais rigorosa. O padrão que apliquei — nunca aceitar uma automação de 100% nem um ROI que não seja rastreável até um número medido — vem da forma como dirijo qualquer trabalho técnico, não é algo que o modelo teria imposto a si mesmo sem essa cobrança.

---

## Evidências

- [x] Código-fonte completo e reprodutível em `solution/` (scripts Python + dashboard React/visx em `solution/dashboard/`)
- [x] Saídas JSON versionadas em `solution/output/` (diagnóstico, métricas do classificador, modelo exportado, ROI)
- [x] Protótipo funcional: `solution/dashboard/` (React + visx, ver instruções de setup) + versão estática alternativa ao vivo em https://claude.ai/code/artifact/1b04cec8-cbc9-4a6e-939c-256236422aba
- [x] Verificação automatizada com Playwright (Chromium headless): gráficos renderizados, simulador testado por interação real, console sem erros
- [x] Teste holdout documentado (84,9% de acurácia, 9.568 exemplos nunca vistos no treino)
- [x] Este process log, incluindo o erro de cálculo de ROI e a correção

Submissão preparada em: 11/09/2026
