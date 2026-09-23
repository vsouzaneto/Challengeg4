---
title: Implementar cockpit decisório de social media
---

# SPEC — Cockpit decisório de social media

## Adendo de status da implementação — 22/09/2026

- A revisão humana da SPEC foi registrada, a implementação local foi autorizada e as fases S1–S4 foram executadas. O texto abaixo permanece como contrato e registro pré-implementação; verbos no futuro descrevem a intenção original, não o estado atual.
- Estado verificado: comparação de patrocínio por plataforma, formato, categoria, faixa de creator e **mês-calendário**; hipótese de frequência restrita às semanas ISO completas dentro do mesmo mês/contexto; decisões/outcomes exportados com proveniência própria. Campos extensos usam uma barreira final `export_field`, reconstruída antes das camadas `analysis_field` e `history_field`.
- Refinamento 2.5 concluído localmente: **146 testes catalogados**, gate focal anterior **45/45** e matriz executiva ampliada para **20/20** na auditoria final. O contrato ativo é `METHOD_VERSION = "2.5.0"`; eventos `1.0.0`–`2.4.0` continuam legíveis, mas incompatíveis para nova comparação automática (`pending / method_mismatch`). O CSV publica seis recomendações em 6.830 registros. Artefatos canônicos: `evidence.csv` SHA-256 `e982cd2fcc346951d4c6ab5d9a3af4443858548a1786fe0424d4f71d84c2f30a`; `analysis.md` SHA-256 `f2e8f4929bf1bbe9e8e7395f9ab5e7b09f093919a6cfe0af364710fb0b65db54`.
- Avaliação preliminar da IA: clareza `9,7`, objetividade `9,8`, eficiência `9,6`, profundidade `9,5` e capacidade decisória `9,5`; média `9,62`. A nota final permanece `PENDING` até leitura humana de Luis ou avaliador designado; HR-01 também permanece pendente.
- Datas aceitas são ISO-8601 explícito ou `%m/%d/%y %I:%M %p`, na faixa operacional de 1971-01-01 a 2262-04-10; gramática relativa, timezone desconhecido e inferência são bloqueados com linha/coluna. Inteiros passam por comparação lexical `int64`, inclusive entradas extensas, sem alterar o limite global do Python. Evidência negativa com `C<0,40` recomenda coleta/teste em escala limitada; somente força suficiente permite `review/stop`.
- O snapshot de decisão preserva alvo, comparador, estatística, unidade, controles, cobertura, força e referências por papel. A observação reaplica o mesmo segmento e só substitui a janela temporal. Fim observado ou execução no futuro ficam `pending`; replay retrospectivo exige relógio explícito e rótulo **SIMULAÇÃO** persistido.
- O baseline de cada decisão preserva também o envelope completo da recomendação — rank integral, score, normalização, componentes, hipótese de frequência e texto operacional — inclusive além do top 3. A cronologia de outcomes projeta decisão, registro, relógio e execução no calendário civil declarado pela fonte (`+14:00`, `-12:00` ou naive), sem inventar timezone e sem retroclassificar eventos históricos já persistidos.
- `analysis_state` distingue `ready` de `empty_scope`. No estado vazio, fonte, filtros escolhidos e histórico permanecem visíveis, mas KPIs, prioridades e downloads analíticos não são apresentados como observação. Delta ausente é “não definido — sem comparador elegível”; zero aparece somente quando uma comparação real mede zero.
- CK-01–11 e HR-02–04 possuem evidência independente. **HR-01 permanece pendente** até um Gestor de Social Media concluir o roteiro cronometrado em até cinco minutos. Isso mantém a Definition of Done integral aberta. Push, PR, merge e deploy não foram autorizados.

**Status original em 21/09/2026:** pronta para revisão humana; implementação ainda não autorizada.

## Adendo de refinamento executivo ≥9,5 — 22/09/2026

Luis definiu uma nova meta interna: elevar de `8,7` para pelo menos `9,5/10` a capacidade média do sistema de responder, com clareza, objetividade e eficiência, às três perguntas centrais do Head e à pergunta obrigatória sobre audiência. Essa nota é um gate de qualidade da construção, não uma promessa sobre avaliação externa.

O refinamento deve acrescentar, sem trocar a stack nem criar um segundo motor:

1. ranking multivariado de contextos orgânicos por plataforma, formato, categoria e faixa de creator, com ERv, volumes, amostra, comparação entre pares, estabilidade mensal, força heurística e limiar explícito de relevância prática;
2. decisão condicional de patrocínio que mantenha separados o achado observacional e um cenário financeiro manual, expondo dados ausentes, ponto de equilíbrio e a condição exata que mudaria a decisão;
3. estratégia relativa de 30 dias, dividida em quatro semanas, com contexto, cadência, responsável, métrica e gates numéricos de avançar, manter, revisar ou coletar;
4. força, cobertura e gatilho de mudança em cada resposta executiva, sem apresentar confiança como probabilidade;
5. matriz de 20 critérios — resposta direta, sustentação multivariada, estabilidade temporal, decisão operacional e estratégia executável para cada uma das quatro perguntas obrigatórias — além de uma avaliação global cuja média deve ser `≥9,5`, sem dimensão abaixo de `9,0`.

O ranking não pode chamar associação de causalidade. Contextos candidatos usam somente posts orgânicos com ERv definida. Cada combinação `platform + content_type + content_category + follower_band` é comparada, mês a mês, aos demais formatos/categorias da mesma plataforma e faixa. Cada braço mensal exige pelo menos 30 taxas e cinco creators; o contexto exige pelo menos três meses elegíveis, 90 taxas e dez creators no conjunto. A relevância prática mínima é `max(0,10 p.p.; 0,25 × IQR global de ERv)`. Estabilidade é a proporção de meses cujo delta tem o mesmo sinal da mediana dos deltas mensais. Um vencedor consistente exige delta acima do limiar, estabilidade `≥2/3` e força `C≥0,40`; sem isso, a resposta definitiva é que não existe vencedor sustentado e a ação é testar/coletar.

O cenário financeiro recebe manualmente custo de patrocínio, custo incremental de produção, valor por conversão, taxa orgânica e taxa patrocinada esperada. Ele calcula receita incremental hipotética, custo máximo de patrocínio e uplift mínimo de conversão para equilíbrio. Nenhum valor digitado vira evidência observada, decisão persistida ou ROI comprovado. Campos ausentes, negativos, taxas acima de 100% e valor por conversão zero bloqueiam o cálculo com mensagem explícita.

A estratégia de 30 dias é um programa de decisão, não calendário de publicação automática. Ela preserva o mix corrente fora dos testes, usa contexto/cadência provenientes do motor e divide a execução em preparar baseline, testar, replicar e decidir. Nenhuma ação publica conteúdo, contrata creator ou movimenta verba. Dashboard, HTML, Markdown e CSV continuam derivados das mesmas funções puras; qualquer mudança analítica incrementa `METHOD_VERSION` e invalida comparações automáticas com versões anteriores.

## Initial User Prompt

executar a pesquisa obrigatória antes de escolher framework  e DEPOIS... escrever spec

## Description

Entregar a análise e a estratégia obrigatórias do Challenge 004, acompanhadas de um cockpit local que transforme os achados em decisões recorrentes. O problema de negócio é distinguir o que gera engajamento, em quais contextos o patrocínio apresenta desempenho favorável e onde concentrar ou interromper esforço. O Gestor de Social Media é o operador diário; o Head de Marketing recebe a síntese semanal e o Analista recebe a consolidação mensal e as evidências auditáveis.

A pesquisa foi concluída antes desta especificação: o CSV público contém 52.214 posts, 27 colunas e cinco plataformas. O framework selecionado após comparação e reprodução foi Streamlit. A fonte não contém investimento, receita ou conversão; a comparação de patrocínio deve comunicar associação observacional, nunca ROI financeiro ou efeito causal. Esta SPEC define uma entrega a implementar e revisar; não afirma que já existem conclusões analíticas ou um produto concluído.

O desafio estabelece um orçamento de 4–6 horas: proteger análise e estratégia obrigatórias antes do polimento visual. Não remover decisões aceitas para caber no prazo; registrar eventual extrapolação e seu motivo.

### Escopo incluído

- Importar manualmente o CSV, validar sua integridade e mostrar período, cobertura, qualidade e limitações. O painel inicia pelo monitoramento recente, com alertas contextuais, rankings absolutos secundários e detalhamento até os registros de origem.
- Analisar engajamento e volume por plataforma, formato, categoria, faixa de creator e período; incorporar idade, gênero e localização da audiência aos filtros e benchmarks contextuais quando a amostra permitir, com fallback visível. Comparar orgânicos e patrocinados dentro de contextos equivalentes e mostrar também baixo desempenho e engajamento zero.
- Gerar recomendações determinísticas, ordenadas por impacto observável × confiança × atualidade, expondo os componentes. Impacto combina alcance, interações e exposição do creator, com unidades e normalização documentadas; confiança permanece um componente separado. Cobrir esforço editorial, público, frequência como hipótese testável, política de patrocínio, critérios de seleção de creators, ações a interromper e quick wins para a semana.
- Registrar decisão humana aceita, rejeitada ou editada; persistir metadados da importação, evidências resumidas, decisões, revisões e resultados observados. Comparar resultados posteriores somente quando existirem dados temporalmente adequados e comparáveis.
- Exportar resumo executivo de uma página e CSV de evidências/decisões, com visões semanal e mensal derivadas da mesma base. Entregar instruções reproduzíveis, análise/estratégia legível e diário com decisões, uso de IA, falhas, correções e julgamento humano.

### Escopo excluído

- Integrações com plataformas, sincronização ou agendamento automático; atualização diária significa uma rotina de importação manual. A possibilidade futura de APIs não exige conectores ou abstrações no MVP.
- Publicação de conteúdo, alteração automática de calendário, contratação ou investimento. Aprovar uma recomendação apenas registra a decisão do gestor.
- Cloud, contas, permissões por perfil, múltiplos usuários simultâneos ou serviços remotos obrigatórios; CSV bruto persistido no banco ou cópia automática do arquivo enviado.
- Modelos preditivos, clustering, análise avançada de hashtags/comentários ou chamadas a modelos generativos. Hashtags e texto de comentários vazios não bloqueiam a análise principal.
- ROI, lucro, custo de aquisição ou retorno financeiro estimado sem dados financeiros reais; recomendações causais ou thresholds apresentados como leis universais. Não acrescentar métricas inventadas para preencher lacunas do briefing.

### Cenários de uso

**Principal — rotina do gestor.** O gestor abre a aplicação local, envia um CSV válido e vê a data de referência do dataset, o período selecionado e sua cobertura. Em até cinco minutos identifica um desvio, abre o grupo comparável, confere taxa e volume, amostra, benchmark, diferença e confiança, chega aos registros e decide aceitar, rejeitar ou editar a ação sugerida. A decisão permanece disponível após reiniciar a aplicação.

**Alternativo — revisão executiva.** O gestor escolhe a semana ou o mês disponível na base e exporta a síntese e suas evidências. O Head encontra prioridades, o que fazer, para quem, quando, responsável sugerido e evidência; o Analista recompõe os números a partir do mesmo arquivo e filtros. Nenhum resultado de filtro vazio aparece como zero de performance.

**Alternativo — aprendizado posterior.** Após uma decisão, o gestor importa um novo snapshot com observações posteriores ao período que sustentou a decisão. A aplicação preserva a evidência original, explicita se a ação foi executada conforme informado pelo gestor e compara o resultado observado no mesmo escopo. Sem observações posteriores suficientes, apresenta “resultado pendente”, sem atribuir melhora à ação automaticamente.

**Alternativo — evidência fraca.** Um segmento tem poucos posts ou creators. A aplicação declara o tamanho e o nível efetivo do benchmark, recua apenas conforme a regra documentada e não remove silenciosamente controles essenciais da comparação de patrocínio. Se não houver comparação válida, exibe “evidência insuficiente” e sugere coletar/testar, em vez de recomendar investimento. Sinal negativo fraco (`C<0,40`) também pede coleta/teste; não autoriza interromper ou evitar repetição.

**Erro — entrada ou gravação inválida.** CSV ilegível, coluna obrigatória ausente, número não finito, valor impossível, identidade duplicada conflitante ou data inválida bloqueia a nova análise com linha/coluna, causa e correção esperada. Não descartar ou corrigir registros silenciosamente. Um erro de escrita mantém a decisão anterior e informa que a nova decisão não foi salva; não exibir sucesso antes de confirmar persistência.

## Acceptance Criteria

### Checklist

Cada pergunta é binária; evidência ausente vale “não”. IDs permanecem estáveis durante implementação e revisão. CK representa comportamento verificável; HR representa requisito humano/de entrega.

| ID | Question | Category | Importance |
|---|---|---|---|
| CK-01 | O CSV válido é importado com hash, contagem, período e plataformas presentes, aceitando subconjuntos válidos, enquanto entradas inválidas são bloqueadas com diagnóstico sem descarte silencioso? | Validação | Obrigatória |
| CK-02 | As métricas têm fórmula, unidade, denominador, política de ausências/zeros e faixa de creator explícitos, e seus resultados podem ser recalculados a partir dos registros filtrados? | Integridade analítica | Obrigatória |
| CK-03 | Alertas usam mediana/distribuição de grupos comparáveis, incorporam idade, gênero e localização da audiência nos benchmarks quando a amostra permite, exibem amostra, diferença, confiança e fallback efetivo, e abstêm-se quando não existe base suficiente? | Benchmark contextual | Obrigatória |
| CK-04 | Orgânicos e patrocinados são comparados com os mesmos controles de plataforma, formato, categoria, faixa de creator e período, sem converter associação em causalidade ou retorno financeiro? | Comparabilidade | Obrigatória |
| CK-05 | A análise cobre plataforma, conteúdo, categoria, creator, audiência e tempo, oferece filtros de idade, gênero e localização condicionados à amostra, identifica o que não funciona e mantém taxa, volume e posts zero visíveis? | Cobertura do briefing | Obrigatória |
| CK-06 | A fila usa impacto × confiança × atualidade, combina alcance, interações e exposição do creator em um impacto de unidades/normalização documentadas separado da confiança, mostra os componentes e entrega ordem reproduzível e estável sob empate? | Priorização | Obrigatória |
| CK-07 | Recomendações cobrem esforço, público, frequência, patrocínio, critérios de creators, interrupções e quick wins, com evidência, prioridade e próxima ação humana? | Estratégia | Obrigatória |
| CK-08 | Aceitar, rejeitar ou editar registra decisão, data e evidência original, preserva revisões, evita duplicação por rerun e sobrevive ao reinício sem guardar CSV bruto? | Persistência | Obrigatória |
| CK-09 | Resultado posterior exige observações posteriores e comparáveis, preserva o baseline, mostra ação executada como declaração humana e permanece pendente quando faltam dados? | Aprendizado | Obrigatória |
| CK-10 | Resumo semanal/mensal de uma página e CSV exportado reproduzem os filtros, métricas, prioridades e decisões mostrados, com referências auditáveis? | Exportação | Obrigatória |
| CK-11 | A aplicação funciona localmente, com visão geral e drill-down operáveis por teclado, sem API de IA, conta externa ou ação automática de publicação/investimento? | Experiência local | Obrigatória |
| HR-01 | Um gestor consegue importar, identificar o desvio, explicar contexto/evidência e registrar uma ação em até cinco minutos? | Usabilidade humana | Obrigatória |
| HR-02 | A análise e a estratégia obrigatórias podem ser lidas sem operar o dashboard, com achados rastreáveis e limitações sobre dados, causalidade e finanças? | Entrega executiva | Obrigatória |
| HR-03 | O diário preserva as 24 ondas, pesquisa anterior à escolha, decisões humanas, iterações, erros/correções e o uso efetivo de IA? | Proveniência | Obrigatória |
| HR-04 | O conjunto destinado ao PR está restrito a `submissions/luis-roquette/`, contém setup/demonstração e mantém dados locais, segredos e ferramentas SDD fora da submissão? | Submissão | Obrigatória |

As evidências exigidas para cada ID estão nos casos correspondentes da Test Strategy. Para CK-01, reconciliar as cinco plataformas e as 52.214 linhas somente no dataset canônico; uploads futuros podem conter uma plataforma e qualquer quantidade válida de linhas.

### Regular Checks

Estado original desta seção: antes da implementação, o repositório continha apenas a documentação do desafio. O adendo acima registra o estado executado; os comandos abaixo continuam sendo o contrato de verificação a partir da raiz do worktree.

| Momento | Comando | Critério |
|---|---|---|
| A cada alteração textual | `git diff --check` | Saída sem erros de whitespace; não substitui revisão dos requisitos. |
| Revisão dos artefatos atuais | `git diff --stat; git status --short` | Todos os arquivos novos/alterados são identificados; `.specs/`, `.claude/` e `skills-lock.json` permanecem locais. |
| Antes de preparar PR | `git diff --name-only main...HEAD` | Conferir todos os caminhos: somente `submissions/luis-roquette/`; comparar também alterações ainda não commitadas. |
| Gate runtime implementado | `test -d submissions/luis-roquette/solution/004-social/tests && python3 -m unittest discover -s submissions/luis-roquette/solution/004-social/tests -t submissions/luis-roquette/solution/004-social -p 'test_*.py' -v` | A ausência da pasta falha; a suíte cobre os CK indicados abaixo. Executar com o Python do ambiente documentado. |
| Demonstração implementada | `python3 -m streamlit run submissions/luis-roquette/solution/004-social/app.py --server.address 127.0.0.1 --browser.gatherUsageStats false` | Upload real, interação, reabertura e downloads verificados; ausência da aplicação é bloqueio, não sucesso. |

Os dois últimos comandos eram contratos de entrega e agora têm execução comprovada no diário e no README técnico. Instalação, versões e localização dos arquivos correspondem ao pacote final. Antes de push/PR, reavaliar os workflows reais e executar todos os gates aplicáveis ao diff; documentação não equivale a autorização de publicação.

### Rubric

Todos os CK/HR são obrigatórios. A rubrica avalia a qualidade de uma entrega funcional; nota alta não compensa requisito ausente. Score ponderado é a soma de peso × nota; configuração e critérios de aprovação do juiz pertencem ao processo de revisão, não aos requisitos do produto.

| Critério | Peso | Eixo único avaliado |
|---|---:|---|
| R-01 — Comparabilidade analítica | 0,25 | Grau de controle do contexto nas comparações. |
| R-02 — Auditabilidade | 0,25 | Possibilidade de reproduzir uma conclusão a partir da evidência. |
| R-03 — Acionabilidade | 0,20 | Precisão da janela de execução da ação recomendada. |
| R-04 — Clareza executiva | 0,15 | Facilidade de localizar a decisão principal. |
| R-05 — Qualidade do diário | 0,15 | Rastreabilidade do julgamento humano e das correções. |

Soma dos pesos: **1,00**. Os excertos abaixo são exemplos hipotéticos de comunicação; não são achados reais deste dataset.

### Rubric Score Definitions

**R-01 — Comparabilidade analítica**

`score_2`
```text
Patrocinados: mediana de 4%; orgânicos: 3%. Comparação entre todos os posts do período.
```
`score_4`
```text
Patrocinados: mediana de 4%; orgânicos: 3%. Comparação entre posts do mesmo período, plataforma, formato, categoria e faixa de creator.
```
Contraste: somente o conjunto de controles contextuais muda; métricas e resultado comunicado permanecem iguais.

**R-02 — Auditabilidade**

`score_2`
```text
E-07: a taxa subiu de 3% para 4%. Fórmula, filtros, amostras e hash estão no anexo; IDs das linhas de origem não estão informados.
```
`score_4`
```text
E-07: a taxa subiu de 3% para 4%. Fórmula, filtros, amostras e hash estão no anexo; IDs das linhas de origem estão em evidencias.csv, coluna source_row_id.
```
Contraste: somente a ligação aos registros de origem muda; conclusão e documentação do cálculo permanecem iguais.

**R-03 — Acionabilidade**

`score_2`
```text
Gestor: testar dois vídeos de Tech no segmento E-07, mantendo o público observado; executar em data a definir e revisar taxa e volume sete dias após o teste.
```
`score_4`
```text
Gestor: testar dois vídeos de Tech no segmento E-07, mantendo o público observado; executar entre 22 e 25/09/2026 e revisar taxa e volume sete dias após o teste.
```
Contraste: somente a janela de execução muda; responsável, ação, evidência e revisão permanecem iguais.

**R-04 — Clareza executiva**

`score_2`
```text
Localização: depois de seis tabelas.
Prioridade 1: testar dois vídeos de Tech no segmento E-07 nesta semana; decidir aceitar, rejeitar ou editar.
```
`score_4`
```text
Localização: primeiro bloco da visão geral.
Prioridade 1: testar dois vídeos de Tech no segmento E-07 nesta semana; decidir aceitar, rejeitar ou editar.
```
Contraste: somente a posição da informação muda; o texto da decisão é idêntico.

**R-05 — Qualidade do diário**

`score_2`
```text
Luis exigiu pesquisa antes do framework. A IA comparou três opções e corrigiu o seletor de upload; o spike passou. Evidência da correção: não vinculada.
```
`score_4`
```text
Luis exigiu pesquisa antes do framework. A IA comparou três opções e corrigiu o seletor de upload; o spike passou. Evidência da correção: process-log/I07 e framework-research/streamlit-proof.png.
```
Contraste: somente a referência verificável da correção muda; decisão humana, ação e resultado permanecem iguais.

### Test Strategy

**Criticalidade:** alta para cálculos, comparabilidade, validação e persistência, pois erros podem orientar esforço ou patrocínio de forma incorreta; média para navegação/exportação. Não há execução financeira ou publicação automática. Usar testes determinísticos pequenos para regras e integração; demonstrar o fluxo visual em navegador real. Não inventar amostras suficientes, resultados ou nível de confiança para fazer um teste passar.

| Type | Size | Framework | Dependencies | Gate |
|---|---|---|---|---|
| Validação e aritmética | Pequeno: fixtures; integração: CSV real | `unittest` | Pandas; CSV sintético e canônico | CK-01/02: cálculos manuais coincidem; entradas inválidas bloqueiam; contagens reais reconciliam. |
| Comparação e recomendação | Pequeno: grupos controlados | `unittest` | Pandas; fixtures balanceadas/desbalanceadas | CK-03–07: insuficiência, zeros, empate, componentes e repetibilidade comprovados. |
| Estado durável | Pequeno: integração local | `unittest` | SQLite temporário; snapshots temporais | CK-08/09: reabertura, idempotência, rollback e preservação de baseline passam. |
| Interface e exports | Ponta a ponta: uma sessão e reinício | Navegador real; roteiro manual documentado | Streamlit local; CSV válido/inválido; downloads | CK-10/11 e HR-01: fluxo, teclado, exportação reconciliada e decisão em cinco minutos demonstrados. |
| Entrega e proveniência | Revisão documental do pacote | Git e revisão humana | Relatório, diário, evidências e ambiente de setup | HR-02–04: briefing respondido, links válidos, escopo de arquivos e setup conferidos. |

**Casos CK-01 — entrada.** CSV canônico confirma as 52.214 linhas e cinco plataformas observadas na pesquisa. Um CSV válido com somente uma plataforma e menos linhas é aceito e informa sua cobertura real. Fixtures cobrem arquivo vazio, CSV malformado, coluna obrigatória ausente, números negativos/não finitos, datas inválidas e duplicatas conflitantes; a importação falha sem alterar resultados anteriores. Hashtags e comentários vazios são aceitos quando os campos analíticos obrigatórios são válidos. Não exigir exatamente 52.214 linhas nem cinco plataformas de qualquer upload futuro.

**Casos CK-02 — métricas.** Calcular manualmente taxa derivada, interações, mediana e volume numa fixture; verificar denominador zero, valores ausentes, posts com zero engajamento e limites das faixas de seguidores. Confirmar que o CSV canônico não contém `engagement_rate`; um upload futuro com coluna homônima gera aviso e não substitui silenciosamente a fórmula versionada do produto. Filtrar e exportar mantém os mesmos denominadores.

**Casos CK-03 — benchmark.** Um post extremo em grupo comparável é detectado; distribuição constante não divide por zero. Grupo abaixo do mínimo recua ao nível declarado ou abstém-se. Fixtures de idade, gênero e localização comprovam que o benchmark usa o contexto de audiência solicitado quando elegível, e declara fallback quando a amostra não sustenta o corte; um gráfico demográfico isolado não satisfaz esse caso. Muitos posts de um único creator não viram muitos creators independentes. O período de comparação e a inclusão/exclusão do post-alvo são explícitos e reproduzíveis.

**Casos CK-04 — patrocínio.** Fixture de composição desigual demonstra por que a média global pode inverter a conclusão dos estratos. Comparação final mantém controles obrigatórios e informa grupos sem contraparte; ausência de orgânicos ou patrocinados produz “insuficiente”. Não excluir patrocínio negativo nem posts zero. Texto não afirma efeito causal ou ganho financeiro.

**Casos CK-05 — cobertura.** Os cinco nomes de plataforma são preservados quando presentes, com foco executivo em Instagram, TikTok e YouTube. Filtros de idade, gênero e localização afetam os grupos elegíveis; audiência é segmentada apenas no nível que os dados realmente medem, sem inferir engajamento individual de composição agregada. Corte pequeno e filtro vazio têm estado próprio. Série temporal usa datas presentes e não transforma histórico antigo em “dados de hoje”.

**Casos CK-06 — ordem.** Fixar alcance, interações e exposição do creator de três alertas; conferir normalização/unidades e impacto calculado, mantendo confiança como fator separado. Variar um componente por vez comprova que nenhum dos três foi omitido. Verificar a ordem esperada; empate usa chave estável documentada. Um percentual extremo com pouco volume/confiança não domina automaticamente. Mesma base, filtros, versão e data de referência geram mesma ordem; avançar a data de referência afeta apenas a atualidade prevista.

**Casos CK-07 — ação.** Cada recomendação aponta evidência válida e contexto; ausência de diferença sustentada gera proposta de teste/coleta. Frequência e threshold de creator são apresentados com unidade e contexto, e como hipótese quando observacionais. Rejeitar ou aceitar não altera calendário, orçamento ou canais externos.

**Casos CK-08 — decisão.** Persistir cada estado e uma edição, reiniciar e conferir histórico original. Repetir o mesmo evento/rerun não duplica registros; nova decisão legítima fica distinta. Simular falha de escrita garante rollback e erro visível. Inspecionar o banco para comprovar ausência de CSV bruto e segredos.

**Casos CK-09 — resultado.** Reimportar o mesmo arquivo não cria resultado posterior; arquivo novo sem período posterior ou escopo comparável permanece pendente. Snapshot válido usa janela posterior com a mesma duração e cobertura temporal do baseline, ou exibe métricas normalizadas por dia quando a cobertura equivalente for impossível; volumes brutos de janelas diferentes não sustentam melhora. Alteração retroativa de dados não reescreve evidência original. “Aceita” não equivale a “executada”, e “melhorou depois” não equivale a “melhorou por causa da ação”.

**Casos CK-10 — exportação.** Abrir downloads e recomputar métricas selecionadas; decisões e filtros coincidem com a tela. Semanal/mensal respeitam limites de data documentados e mostram janela incompleta quando aplicável. Resumo cabe em uma página no formato final escolhido; células CSV com prefixos de fórmula são exportadas com tratamento seguro documentado, sem modificar a análise em memória.

**Casos CK-11 — experiência local.** Iniciar com instruções documentadas, sem credenciais, em endereço de loopback; executar upload, seleção, drill-down e registro por teclado com foco e rótulos visíveis. Recarregar exige reenvio do CSV quando necessário, mas preserva decisões. Sem dados, falha de arquivo e erro de banco são estados legíveis. Validar o roteiro HR-01 com instalação e CSV já disponíveis, registrando o tempo real.

**Revisão HR-02–HR-04.** Verificar que relatório e estratégia respondem a todas as perguntas obrigatórias ou justificam impossibilidade com evidência. Conferir o diário e as 24 ondas. Inspecionar caminhos destinados ao PR, licenças/atribuições, limitações, instruções e provas; nunca publicar a pesquisa/spike como se fosse o produto final.

### Definition of Done

- Todos os CK/HR têm resposta “sim” com evidência; rubrica está preenchida com justificativas e seus pesos somam 1,00. Checks ainda indisponíveis bloqueiam a declaração de produto pronto.
- CSV real analisado, qualidade e definições métricas verificadas, comparação justa reproduzida, conclusões rastreáveis e estratégia priorizada entregues fora e dentro do cockpit.
- Fluxo local completo demonstrado: importação → monitoramento → evidência → recomendação → decisão persistida → resultado posterior/pendente → exportação. Tempo de decisão de até cinco minutos medido.
- Diário, pesquisa, limitações, licenças e setup atualizados; todos os gates existentes/aplicáveis passam no diff correto e o conjunto de submissão respeita a pasta autorizada.
- A SPEC recebe revisão humana antes da implementação, conforme I02. Aprovação da SPEC, implementação local, push/PR e entrega final são estados distintos; concluir este documento não declara os demais concluídos.

## Architecture Overview

### Solução e limites

Um processo Python local executa Streamlit, Pandas e SQLite da biblioteca padrão. A interface usa os componentes nativos do Streamlit; não há API HTTP própria, frontend separado, ORM, autenticação, agendador ou serviço de inferência. O estado temporário guarda o CSV enviado; o estado durável guarda somente proveniência, evidências agregadas e decisões humanas. A análise e a estratégia publicadas continuam sendo entregas obrigatórias, independentes da operação do cockpit.

Esta arquitetura consolida a [pesquisa anterior à escolha](../../research/004-social.md) e as [24 ondas de descoberta](../../process-log/004-social.md). A análise de impacto detalhada permanece no pacote SDD local, fora da submissão. Streamlit 1.64.0 e Pandas 2.3.3 são as versões reproduzidas no spike; o `requirements.txt` deve fixar as versões efetivamente verificadas na implementação. O spike não prova a aplicação final.

### Componentes e contratos

| Componente | Responsabilidade e fronteira |
|---|---|
| `app.py` | Upload manual, filtros, panorama recente, alertas prioritários, tabela de ranking, drill-down, formulário de decisão e downloads. `st.session_state` contém dados/filtros transitórios; somente submissões explícitas produzem escritas duráveis. |
| `analysis.py` | Validação integral, normalização declarada, métricas, grupos comparáveis, comparação de patrocínio, recomendações e exports. Funções puras recebem DataFrames/dicionários e não importam Streamlit ou SQLite. CLI mínima regenera a evidência do relatório com o mesmo motor. |
| `storage.py` | Biblioteca padrão: conexão, schema, transações parametrizadas, imports, revisões de decisões e observações posteriores. Recebe o caminho do banco para permitir testes temporários. |

Contratos novos a implementar, usando dicionários/DataFrames, sem classes de serviço:

```python
load_csv(raw: bytes) -> tuple[pd.DataFrame | None, list[dict]]
analyze(df: pd.DataFrame, scope: dict, source_hash: str) -> dict
export_evidence(result: dict, decisions: list[dict]) -> bytes
executive_summary(result: dict, decisions: list[dict]) -> str
record_import(conn, metadata: dict) -> str
record_decision(conn, event: dict) -> str
record_outcome(conn, event: dict) -> str
```

`load_csv` retorna o DataFrame completo ou diagnósticos `{row, column, problem, expected}`; nunca um DataFrame parcialmente aprovado. `scope` contém janela-alvo, data de referência, filtros, janela solicitada de benchmark e versão do método. `analyze` retorna `{source, scope, quality, metrics, cohorts, alerts, sponsorship, recommendations, row_references}`. Cada evidência informa `evidence_id`, `source_hash`, `method_version`, contexto solicitado/efetivo, fórmula, unidades, contagens, mediana/quartis, efeito, força da evidência, prioridade e IDs de origem. Campos indefinidos usam `null`, nunca zero fictício. Exports consomem esse resultado sem recalcular métricas independentemente.

Fluxo: `bytes CSV → validação integral → metadados/hash → análise pura → panorama/drill-down → formulário humano → transação SQLite → leitura confirmada → export`. Um novo upload inválido não substitui a análise válida anterior; a tela distingue claramente arquivo rejeitado e base ainda ativa. Falha de gravação preserva o evento anterior e não mostra confirmação de sucesso.

### Contrato do CSV e proveniência

O header físico verificado tem 27 campos, sem `engagement_rate`:

```text
id,platform,content_id,creator_id,creator_name,content_url,content_type,content_category,post_date,language,content_length,content_description,hashtags,views,likes,shares,comments_count,comments_text,follower_count,is_sponsored,disclosure_type,sponsor_name,sponsor_category,disclosure_location,audience_age_distribution,audience_gender_distribution,audience_location
```

Campos obrigatórios e não vazios: `id`, `platform`, `content_id`, `creator_id`, `content_type`, `content_category`, `post_date`, `views`, `likes`, `shares`, `comments_count`, `follower_count`, `is_sponsored`, `audience_age_distribution`, `audience_gender_distribution`, `audience_location`. Os onze campos restantes são opcionais para o motor; se ausentes, registrar sua ausência, sem inventar conteúdo. Texto livre não é executado nem interpretado como HTML. `content_length` pode ser exposto como valor original, mas não será chamado de segundos/palavras sem definição confirmada da unidade.

Aceitar CSV UTF-8/UTF-8-BOM, separado por vírgula, até 50 MiB. Bloquear arquivo vazio, cabeçalhos duplicados, linhas malformadas, métricas ausentes/não finitas/negativas/não inteiras, flags fora de `TRUE/FALSE` ou `true/false`, datas inválidas e identidades repetidas. `id` e `(platform, content_id)` são únicos dentro do arquivo; duplicatas idênticas também bloqueiam, pois dobrariam volumes. Os IDs são strings opacas. Inteiros são validados lexicalmente contra `int64`: zeros à esquerda não alteram a comparação, entradas arbitrariamente longas falham de forma determinística e o limite global de conversão do Python não é alterado. A conversão explícita de flag e de data não muda a semântica original. Aceitar somente o formato observado `%m/%d/%y %I:%M %p` ou ISO-8601 explícito, preservando nanossegundos e offsets válidos; datas relativas, zonas desconhecidas e gramática inferida falham com linha/coluna. A faixa operacional é 1971-01-01 a 2262-04-10. Datas sem timezone permanecem no horário informado pela fonte, sem atribuir UTC. Um arquivo não mistura datas com/sem offset; comparação diária usa a data no padrão declarado, mostrado na interface. Limites de semana/mês e hipótese de frequência usam aritmética civil (`date`) e só são convertidos para `Timestamp` depois do clipping ao dataset, evitando overflow no extremo de 2262.

Vocabulário canônico observado: plataformas `Bilibili`, `YouTube`, `Instagram`, `RedNote`, `TikTok`; formatos `video`, `image`, `mixed`, `text`; categorias `beauty`, `lifestyle`, `tech`. Subconjuntos são válidos. Valores novos não vazios podem formar novos grupos, com aviso de cobertura e sem coerção para uma categoria existente. Limites 52.214 linhas/cinco plataformas são reconciliação do snapshot original, não requisito para uploads futuros.

Apesar dos nomes, os campos de audiência são **rótulos categóricos**, não percentuais: idade observada em `13-18`, `19-25`, `26-35`, `36-50`, `50+`; gênero em `female`, `male`, `non-binary`, `unknown`; localização é país. Preservar `unknown` como categoria explícita; não repartir interações entre pessoas, não inferir personas e não fabricar distribuições. Os três rótulos podem restringir filtros e comparação quando houver amostra.

Calcular SHA-256 dos bytes originais antes do parsing. Uma referência de linha é `source_hash:id`; manter também número físico de linha para diagnóstico. Registrar contagem, nomes de colunas, período e valores de plataforma realmente presentes. Zero observado é válido e permanece nos cálculos; ausência numérica bloqueia. O snapshot canônico não tem zeros nas cinco métricas verificadas: informar esse fato como limitação de representatividade, sem supor que posts zero foram coletados. Fixtures demonstram que o sistema aceita e analisa zeros futuros.

### Definições métricas

Não existe uma taxa fornecida pela fonte a conferir. A taxa principal é **derivada pelo produto** e aparece como “interações por visualização (%)”. Eventual coluna adicional chamada `engagement_rate` em upload futuro é metadado não utilizado, com aviso; só uma nova versão do método poderá adotar outra definição.

| Medida | Fórmula, denominador e tratamento |
|---|---|
| Interações do post | `I = likes + shares + comments_count`; contagem de ações, não pessoas únicas. Zero permanece zero. |
| Taxa por visualização | `ERv = 100 × I / views` se `views > 0`; com `views = 0`, taxa indefinida e volume ainda visível. Pode superar 100%, pois ações não são pessoas únicas. |
| Taxa por seguidores, secundária | `ERf = 100 × I / follower_count` se `follower_count > 0`; rotulada com outro denominador, nunca misturada com ERv. |
| Resumo de grupo | Total de posts/interações/views; mediana e Q1/Q3 das taxas definidas; taxa ponderada `100 × ΣI / Σviews` somente entre posts com `views > 0`, acompanhada de `n_rate` e número de taxas indefinidas. Mediana não é “média”. |
| Escala/contexto | `views` são visualizações, proxy de exposição, não alcance único. Exposição de creators de um grupo é `Σ max(follower_count)` por `creator_id`; não somar seguidores do mesmo creator a cada post nem chamar a soma de audiência única. |

Faixas fixas de seguidores: `[0,10.000)`, `[10.000,50.000)`, `[50.000,100.000)`, `[100.000,500.000)`, `[500.000,+∞)`. Limites pertencem à faixa à direita. São bins operacionais, não thresholds que comprovam retorno financeiro. Recortes mostram taxa **e** volume, proporção de posts com `I=0`, amostras e cobertura.

Séries usam dia/semana ISO (segunda a domingo)/mês-calendário. Frequência observada é contagem de posts por creator por semana completa coberta no arquivo; semanas nas bordas são parciais. Ausência de linha não comprova ausência de postagem fora da coleta. Recomendar frequência significa propor teste com janela/revisão explícitas, não declarar frequência causalmente ótima. Sem prova da unidade de `content_length`, não emitir recomendações de “30–60 segundos”.

### Benchmark, audiência e suficiência

Data de referência padrão: maior `post_date` do arquivo, sempre exibida junto à data real da importação. A visão de monitoramento inicia nos últimos sete dias disponíveis, inclusive; o operador pode selecionar dia, semana, mês ou intervalo explícito. “Diário” descreve a rotina manual, não garante atualização da fonte. Dados históricos são identificados como históricos; não apresentá-los como performance corrente.

Para um alerta de post, o núcleo comparável mantém `platform + content_type + content_category + follower_band + is_sponsored`. A referência temporal termina antes do primeiro dia da janela-alvo; o post e todos os posts do mesmo `creator_id` do alvo ficam fora do benchmark, evitando autorreferência. A distribuição de referência usa **ERv de cada post elegível, com peso igual por post**; mediana e quartis são dessa distribuição, preservando a variação dentro de cada creator. A concentração por creator é informada e reduz C pela fórmula abaixo; não se presume independência entre posts. Medianas por creator ficam restritas à comparação de patrocínio.

Suficiência operacional mínima: 30 posts com taxa definida e cinco creators distintos no benchmark. São guardas conservadores do MVP, não cálculo de poder estatístico. Tentar os níveis nesta ordem, mostrando todos os níveis tentados e o nível efetivo:

1. Núcleo + idade + gênero + localização, nos 90 dias anteriores à janela-alvo.
2. O mesmo contexto, nos 365 dias anteriores.
3. Núcleo + idade + gênero, nos mesmos 365 dias.
4. Núcleo + idade, nos mesmos 365 dias.
5. Somente núcleo, nos mesmos 365 dias; se insuficiente, abster-se.

O contexto inicial usa os rótulos do post-alvo; filtros explícitos restringem os alvos e permanecem visíveis. Um fallback do benchmark pode ampliar a audiência de referência, nunca os alvos filtrados; a tela declara quais controles foram removidos. Não misturar plataformas, formatos, categorias, faixa de creator ou condição de patrocínio para preencher amostra. Se o usuário exigir comparação estritamente dentro do filtro de audiência, só os níveis que preservam esse filtro são elegíveis; caso contrário, mostrar insuficiência.

Alerta contextual: ERv do post abaixo de `Q1 − 1,5×IQR` ou acima de `Q3 + 1,5×IQR`, calculados sobre as taxas dos posts de referência, com quantis Pandas de interpolação linear. Exibir taxa do alvo, mediana, quartis, `Δpp = ERv_alvo − mediana` e diferença relativa `100×Δpp/mediana` quando a mediana for positiva; com mediana zero, diferença relativa é indefinida. Se IQR=0, manter a diferença como observação de distribuição constante, sem classificar um alerta estatístico forte. Rankings absolutos continuam disponíveis mesmo sem alertas suficientes. Post com taxa indefinida participa dos volumes e do diagnóstico, não de comparação de ERv.

Contrato adicional de regressão CK-03: cinco creators de referência têm seis posts cada, com ERv `[1+s, 2+s, 3+s, 7+s, 8+s, 9+s]`, usando `s=0; 0,1; 0,2; 0,3; 0,4` respectivamente, no mesmo contexto/período. Um post de outro creator com ERv=8 não é outlier; outro com ERv=20 é outlier superior. Colapsar os 30 posts nas cinco medianas produziria o primeiro falso positivo e deve fazer o teste falhar. Conferir também Q1/Q3/IQR post a post para evitar um teste que somente repita a função sob teste.

“Confiança” significa **força heurística da evidência**, não probabilidade, p-valor ou intervalo de confiança. Para cada conjunto de referência elegível: `C = min(n_rate/100,1) × min(n_creators/20,1) × (1 − max_creator_post_share)`. Mostrar os três fatores e `C` em `[0,1]`; rótulos: limitada `<0,40`, moderada `[0,40,0,70)`, forte `≥0,70`. Benchmark insuficiente tem `C=0` e não gera ação de ampliação/patrocínio. Os limites são versionados em `method_version`, visíveis e testados; não viram dezenas de controles de UI. Recomendações com força limitada pedem teste/coleta, não aumento de investimento.

### Patrocínio e estratégia

Comparar orgânico/patrocinado dentro de estratos de `platform + content_type + content_category + follower_band + período selecionado`; aqui a flag de patrocínio separa os dois braços e não é controle fixo. Dentro de cada braço, calcular mediana por creator e depois a mediana dos creators. Exigir pelo menos 30 posts com ERv definida e cinco creators por braço; expor contagem de creators presentes nos dois braços, pois grupos não são tratados como independentes.

Se houver filtro de audiência, começar com seus rótulos e aplicar apenas fallback declarado/permitido; o mesmo filtro efetivo vale para ambos os braços. Os controles essenciais nunca são descartados. Um estrato sem contraparte fica fora do efeito comparável, mas permanece na tabela de cobertura, com motivo e volumes. Exibir taxas/volumes, diferença absoluta e relativa e `C_comparação = min(C_orgânico, C_patrocinado)`; zero no denominador produz “não definido”.

A leitura executiva prioriza efeitos por estrato. Se apresentar síntese entre estratos elegíveis, usar pesos comuns `w_s = min(n_orgânico_s, n_patrocinado_s)` e médias ponderadas **das medianas de estrato** nos dois braços; rotular exatamente assim, não como mediana global ou uplift causal. Mostrar também cobertura: posts dos estratos comparáveis divididos pelos posts de todos os estratos solicitados. Não extrapolar resultado para regiões sem sobreposição; nem sinal agregado nem C justificam desembolso sem custos reais.

Recomendações são templates determinísticos ligados a evidências: contexto que merece teste/ampliação de esforço, público observado, faixa de creator, hipótese de frequência, condição de patrocínio, conteúdo a interromper/rever e quick win. Toda ação traz responsável sugerido (gestor), janela de execução/revisão, métrica a observar e critério de reavaliação. Um resultado inconclusivo produz ação de validação/coleta; não fabricar sete conclusões positivas para preencher categorias. O relatório responde “custo implícito” como dado indisponível: listar investimento/custo de produção/receita necessários para calcular retorno, sem imputar preços por seguidores.

Comparação editorial agregada usa grupos orgânicos do mesmo núcleo/audiência efetiva na janela-alvo e no intervalo imediatamente anterior de igual duração, sem sobreposição. Exigir 30 posts com taxa definida e cinco creators em **cada** período, sem ampliar a janela automaticamente. Usar mediana de ERv dos posts em ambos os períodos e `C_editorial=min(C_atual,C_anterior)`; a composição dos creators e sua sobreposição ficam visíveis. Para os sinais auxiliares, comparar medianas de views e de interações **por post**, não totais de grupos com quantidades diferentes. Efeitos são associações temporais; não comprovam causalidade. O score agregado abaixo independe de existir um post outlier.

As regras são aplicadas na ordem da tabela: evidência insuficiente primeiro; cada evidência gera no máximo uma ação principal. `ΔER` é diferença de ERv em pontos percentuais; `ΔV`/`ΔI` são diferenças das medianas por post. Comparação por sinal usa valores não arredondados. Os três sinais aparecem mesmo quando discordam.

| Evidência | Elegibilidade / guarda de sinal | Ação determinística | Fonte da prioridade |
|---|---|---|---|
| Qualquer comparação insuficiente/indefinida | Não atende amostra ou falta taxa/comparador; `C=0` | Coletar/corrigir dados do contexto e reavaliar; nunca ampliar/parar por desempenho | Score zero; lista de pendências ordenada por `evidence_id`, fora das três prioridades de desempenho. Se não houver prioridade elegível, mostrar a primeira pendência como próximo passo. |
| Post outlier | Benchmark elegível, IQR>0; acima/abaixo da cerca contextual | Superior: testar repetição do padrão; inferior: revisar criativo/contexto. Com `C<0,40`, validar/coletar primeiro. Um post isolado nunca manda ampliar ou parar a estratégia | Score do próprio post, com C do benchmark. |
| Editorial agregado orgânico | Dois períodos elegíveis; `C≥0,70` e `ΔER>0, ΔV≥0, ΔI≥0`; ou `C≥0,70` e `ΔER<0, ΔV≤0, ΔI≤0` | Primeiro caso: ampliar esforço editorial como teste com revisão; segundo: revisar e propor interrupção da repetição desse padrão, sujeita à decisão humana. Demais sinais, empate ou `C<0,70`: testar/coletar, sem ampliação/interrupção recomendada | Score agregado editorial da janela-alvo, com `C_editorial`. |
| Patrocínio por estrato | Dois braços elegíveis; `C≥0,40, ΔER>0, ΔV≥0, ΔI≥0` para patrocinado menos orgânico; ou `C≥0,70, ΔER<0, ΔV≤0, ΔI≤0` | Primeiro caso: avaliar teste de patrocínio condicionado à obtenção dos custos; segundo: revisar/propor interromper renovação desse padrão. Demais sinais ou força limitada: coletar/testar sem recomendar investimento. Nunca ampliação automática de verba | Score agregado dos posts patrocinados do estrato, com `C_comparação`. |
| Público/faixa de creator/frequência/quick win derivados | Existe ação elegível editorial ou de patrocínio com contexto e evidência; frequência requer ao menos duas semanas completas observadas | Complementar a mesma ação com rótulos de audiência/faixa; frequência é hipótese de testar a mediana observada de posts por creator-semana, com unidade e limite da coleta. Sem semanas suficientes: coletar antes de sugerir número | Herdam evidência e score da ação principal; não criam item duplicado na fila. |

Casos de contrato CK-07/CK-06: sinais positivos concordantes com C forte, sinais negativos concordantes, sinais discordantes, efeito zero e amostra insuficiente produzem exatamente as ações acima. Um estrato patrocinado elegível sem qualquer outlier individual ainda produz recomendação e score agregado. A mesma evidência não ocupa duas posições por também sustentar público/frequência/quick win.

### Prioridade reproduzível

Cada alerta de post usa três volumes observados: `V=views`, `I=interações`, `F=follower_count`. A referência de normalização é o P95 de cada componente entre **todos os posts-alvo válidos da mesma plataforma**, não apenas os outliers. `N(x)=min(x/P95_x,1)`; quando P95=0, usar o máximo positivo do mesmo conjunto, ou zero se todos os valores forem zero. Registrar os denominadores e a política. Essa normalização mede impacto relativo na plataforma, não alcance absoluto entre plataformas.

`impacto = (N(V)+N(I)+N(F))/3`; `atualidade = 2^(−idade_em_dias/7)`, com idade entre data de referência e data do post, nunca negativa; `prioridade = 100 × impacto × C × atualidade`. Componentes e valores originais aparecem no drill-down/export. O fator C permanece fora de impacto.

Para recomendação agregada, reutilizar a mesma fórmula com `V=Σviews`, `I=Σinterações`, `F=Σmax(follower_count)` por creator do grupo-alvo. A base de normalização é o P95 desses totais em **todos** os grupos não vazios da mesma plataforma, tipo de recomendação e janela-alvo (incluindo os sem efeito favorável), usando o mesmo núcleo/audiência efetiva; editorial usa grupos orgânicos, patrocínio usa grupos patrocinados. A regra P95=0 é a mesma dos posts. Recência usa a **mediana temporal real** dos posts do grupo-alvo, inclusive a média dos dois instantes centrais quando a quantidade é par, em dias completos. O C é o da comparação correspondente; não somar scores individuais. A interface explicita que os scores são relativos à plataforma/tipo/unidade de análise e mostra as respectivas bases de normalização, não equivalência de impacto absoluto ou monetário entre itens.

A fila executiva reúne ações de posts e de agregados numa lista, ordenada por `prioridade desc, |ΔER| desc, data_representativa desc, evidence_id asc`. A data representativa é data do post ou mediana temporal real das datas do grupo. Deduplicar por `platform + content_type + content_category + follower_band + audiência solicitada + janela-alvo`, independentemente de tipo/flag de patrocínio: fica a ação de maior prioridade, com links para as demais evidências do contexto. As três primeiras formam a síntese executiva; a fila deduplicada completa, seus snapshots e scores permanecem no resultado. Todos os demais itens ficam selecionáveis no drill-down e no formulário de decisão sem alterar filtros ou normalização. Assim uma recomendação agregada pode entrar sem apoiar-se em outlier, e um contexto não ocupa três posições por reaparecer como post, editorial e patrocínio. Pendências com C=0 ficam na lista separada. Mesma fonte, filtros, versão e data de referência reproduzem a ordem; rankings absolutos são secundários. CK-06 inclui um empate post/agregado, uma colisão de contexto, quatro ações elegíveis e um agregado sem outliers para comprovar essa seleção.

### Persistência e observação posterior

Banco local padrão fora do worktree: `~/.local/share/ai-master-challenge-004/cockpit.sqlite3`. `storage.py` recebe caminho explícito em testes. Usar `PRAGMA foreign_keys=ON`, transações curtas e SQL parametrizado. Um único operador/processo é o teto deliberado do MVP; implantação multiusuário exigiria rever esse contrato. Um `schema_version` interno impede abrir silenciosamente um banco de versão incompatível.

| Tabela | Campos e invariantes principais |
|---|---|
| `imports` | `source_hash TEXT PRIMARY KEY`, nome-base, bytes, linhas, colunas, período, plataformas, importação UTC, versão de schema/método. Mesmo hash não duplica importação. Sem caminho pessoal completo nem bytes do CSV. |
| `decisions` | `decision_id`, `event_id UNIQUE`, `recommendation_key`, `revision_of` FK, `source_hash` FK, instante UTC, estado `accepted/rejected/edited`, texto original/editado, responsável, janela proposta, `scope_json`, `baseline_json`, `method_version`. Revisões são novos registros; baseline original é imutável. |
| `outcomes` | `outcome_id`, `event_id UNIQUE`, `decision_id` FK, `source_hash` FK, instante UTC, execução declarada `yes/no/unknown`, data de execução declarada, janela observada, `metrics_json`, comparabilidade/cobertura, estado `observed/pending` e motivo. Sem reescrever baseline. |

`evidence_id`/`recommendation_key` são hashes estáveis de fonte, método, data de referência, filtros canônicos, métrica, tipo de evidência, contexto e post de origem (ou chave do grupo para agregado). `event_id` é UUID mantido no formulário durante sua submissão; rerun repete o mesmo ID e retorna o registro existente. Novo envio humano legítimo gera novo ID/revisão. O sucesso só aparece após commit e leitura do registro. Falha reverte toda a transação e mantém o formulário recuperável.

JSON de baseline guarda somente filtros, agregado observado/comparador, amostras, período, referência de linhas/IDs e versão do método; não guarda descrições, comentários, URLs ou uma tabela de posts. Ao decidir sobre um alerta, guardar tanto a evidência do post quanto o agregado do seu contexto na janela-alvo, identificando explicitamente se este atende à suficiência para futura comparação. Reabrir o app permite consultar decisões/agregados; drill-down de uma análise histórica exige reenviar CSV com o hash correspondente. Arquivo alterado é nova fonte, nunca substituição silenciosa da evidência anterior.

Resultado exige arquivo de hash diferente, janela que começa após o fim do baseline e todos os controles essenciais/métrica/método compatíveis; agregar observações posteriores com as mesmas fórmulas e exigir 30 taxas definidas/cinco creators por janela comparada. A janela posterior reaplica o contrato salvo: categoria, audiência, patrocínio, estatística e unidade não mudam; apenas a coordenada temporal é substituída. Quando a cobertura divergir, mostrar taxa/mediana e volumes normalizados por dia, rotular a cobertura desigual e manter volumes brutos apenas como contexto; nunca classificar melhora por comparar volumes brutos de janelas diferentes. Diferença observada não é efeito causal. Se o baseline for um post isolado, ele pode sustentar um alerta, mas não prova melhora de um segmento: resultado de segmento fica pendente até existir baseline agregado suficiente persistido na decisão.

“Aceita” não significa “executada”. Para um resultado declarado posterior à execução, a janela também precisa começar depois da data de execução informada pelo gestor. Sem confirmação/data, mostrar observação posterior ao baseline com execução desconhecida, nunca “resultado da ação”; sem dados suficientes, mostrar “resultado pendente”. Reimportação idêntica, revisão retroativa ou janela sobreposta não cria resultado novo. Como o dataset termina em 2025, a demo não afirma medir efeito de decisões tomadas em 2026; eventual replay histórico deve ser rotulado como retrospectivo e acompanhado de fixtures separadas para testar o fluxo futuro.

### Exportação, experiência e segurança de entrada

Um único panorama apresenta fonte/período, qualidade, prioridades e ranking secundário; seletores nativos e expansores/tabela revelam comparadores e registros sem criar páginas por perfil. Filtros vazios e insuficiência têm estados próprios. Usar rótulos em português, foco de teclado visível, alternativas tabulares para gráficos e texto além de cores. Servidor vinculado a `127.0.0.1`; telemetria Streamlit desativada no comando documentado.

Resumo executivo: HTML estático autocontido, com CSS de impressão A4 e até três prioridades, janela, fonte/hash abreviado, principais evidências/limitações e decisões. O HTML usa escape de todo texto vindo do CSV/gestor, sem scripts ou recursos externos. O teste real de impressão deve comprovar uma página; texto excedente fica no CSV, sem esconder limitação essencial. Sem gerador PDF adicional: o navegador permite imprimir/salvar PDF. Semanal usa semana ISO; mensal usa mês-calendário. O `scope` exportado preserva `period_mode`, `requested_start`, `requested_end`, limites efetivos e `partial_period`; HTML/Markdown declaram explicitamente janela incompleta quando aplicável. Legados sem esses campos permanecem legíveis, sem inferência retroativa.

CSV único de evidências/decisões usa `record_type` (`summary`, `evidence`, `source_ref`, `decision`, `outcome`) e IDs de junção. Contém hash, método, filtros, métricas/unidades, denominadores, amostras, benchmark/fallback, prioridade e estados. Linhas `source_ref` enumeram IDs que permitem reconstituir o grupo com o CSV original, sem exportar textos privados por padrão. Uma barreira final fragmenta qualquer célula ainda extensa em `export_field`, ligada ao ordinal determinístico da linha-base; a reconstrução de `export_field` ocorre antes de `analysis_field` e `history_field`. Numerais são emitidos como numerais; campos textuais cujo primeiro caractere significativo seja `=`, `+`, `-` ou `@`, ou com controle inicial perigoso, recebem prefixo apóstrofo na exportação, inclusive após reconstrução. A proteção não modifica os cálculos em memória. Escapar HTML/CSV e parametrizar SQL são fronteiras obrigatórias.

### Mudanças esperadas e riscos

Todos os caminhos da tabela partem de `submissions/luis-roquette/`; são contratos de arquivos futuros, não implementação existente.

| Ação | Caminho | Resultado esperado |
|---|---|---|
| Criar nesta fase documental | `solution/004-social/SPEC.md` | Cópia canônica revisável do resultado SDD. |
| Criar na implementação | `solution/004-social/app.py`, `solution/004-social/analysis.py`, `solution/004-social/storage.py` | Os três componentes definidos acima, com exports no motor puro. |
| Criar na implementação | `solution/004-social/requirements.txt`, `solution/004-social/README.md` | Pins testados, aquisição/licença do CSV, setup, comandos reais, limitações e roteiro de demonstração. |
| Criar na entrega | `README.md` | Entrada da submissão baseada no template oficial, com resumo, findings, recomendações, limitações e process log navegável. |
| Criar na implementação | `solution/004-social/tests/helpers.py`, `test_analysis.py`, `test_exports.py`, `test_storage.py`, `test_app.py` | Suite stdlib dividida por responsabilidade; todos os arquivos entram no mesmo gate `unittest discover`. |
| Criar na implementação | `solution/004-social/analysis.md`, `solution/004-social/evidence.csv` | Achados reais, estratégia priorizada e evidência gerada pelo mesmo motor. |
| Atualizar | `process-log/004-social.md`, `research/004-social.md` | Decisões/erros/verificações e correções de fatos confirmados; sem inventar resultados. |
| Criar na validação final | `process-log/evidence/004/cockpit-*-proof.png` | Provas focais fiéis de fonte/qualidade, audiência/prioridade, contexto, snapshot histórico e outcomes; sem composto que misture estados. |

Não alterar README compartilhado, índice compartilhado, briefing, `.gitignore` ou CI da raiz. `.specs/`, `.claude/`, lock de skills, ambientes Python, CSV bruto e banco local não entram na submissão. A implementação deve medir tempo/memória com as 52.214 linhas e o caminho analítico real; o spike de quatro linhas não comprova capacidade. Não adicionar cache, DuckDB ou serviço até uma medição demonstrar necessidade.

Riscos aceitos e explícitos: grupos cruzados podem resultar em poucas recomendações; fallback anual pode misturar sazonalidade (mostrar os dois períodos e a cobertura); dados de audiência não observam pessoas individualmente; views não medem alcance único; snapshot sem zeros limita a análise de survivorship; diferenças de patrocínio continuam sujeitas a confundimento; scores/limites são heurísticos e versionados. A resposta a evidência fraca é abstenção/teste/coleta, não relaxamento silencioso dos controles. Priorizar análise/estratégia obrigatórias no orçamento de 4–6 horas; registrar eventual extrapolação. A revisão humana desta SPEC foi o gate anterior à implementação e está registrada no diário.

## Implementation Process

O plano operacional detalhado e normativo está em [`IMPLEMENTATION-PLAN.md`](./IMPLEMENTATION-PLAN.md). Ele aplica TDD, passos rastreáveis, interfaces explícitas, testes por responsabilidade e commits pequenos. O agrupamento abaixo permanece como visão executiva: Tasks 1–3 do plano detalhado compõem a Fase 1; Tasks 4–6 compõem a Fase 2. Os antigos arquivos `.specs/sub-tasks/` ficam apenas como proveniência da primeira decomposição SDD e não devem orientar a execução quando divergirem do plano normativo.

### Execution directive

Gate histórico: a revisão humana da SPEC foi registrada no diário antes da implementação e autorizou a execução local. Esta decomposição nunca autorizou publicação, contratação de serviço ou chamada de API paga; esses limites continuam vigentes.

Depois desse gate, executar as Tasks 1–6 de `IMPLEMENTATION-PLAN.md` em ordem, passando ao agente a SPEC e o plano normativo. Usar o papel/capacidade indicado na visão executiva e instruir o agente a executar somente a task ativa, incluindo testes, diário e commit. Neste plano não há tasks paralelas. Ao completar Tasks 1–3, executar um code reviewer uma única vez para a Fase 1; repetir após Tasks 4–6 para a Fase 2. Correções retornam à task responsável e seus gates; a fase seguinte exige o gate da anterior.

Os nomes `developer`, `general` e `code-reviewer` são papéis para subagentes genéricos disponíveis nesta sessão: respectivamente implementação/testes, análise/documentação e revisão/validação. Não presumir plugins de agentes especializados instalados. S4 é executor de validação integrada/documentação, não uma revisão adicional de fase; por isso usa o papel `general`.

Os tiers `opus`, `sonnet` e `haiku` representam capacidade recomendada pelo SDD, não uma seleção de provider nem autorização de custo. Usar agentes disponíveis na sessão com capacidade equivalente; não iniciar Claude CLI ou configurar modelos externos automaticamente. `opus` fica restrito ao motor e às revisões de integridade analítica/durável. Não há trabalho mecânico suficiente para justificar um agente `haiku` separado.

Tempo de pesquisa/planejamento: **não medido**. Os 310 minutos (5h10) são estimativa otimista de trabalho ativo de implementação **após o planejamento**, com os dois gates de revisão incluídos; espera externa/humana fica excluída e deve ser registrada separadamente. Reservar mais 50 minutos de contingência: até 360 minutos de implementação ativa planejada. Isso não comprova cumprimento das 4–6 horas totais do desafio, pois pesquisa/planejamento também consomem tempo. Registrar tempo efetivo de cada etapa, espera e qualquer extrapolação, inclusive quando não for possível reconstruir o total; não reiniciar ficticiamente o relógio nem remover salvaguardas para declarar cumprimento. S1 e S3 concentram a maior incerteza de esforço.

### Parallelization Overview

Largura máxima efetiva 1, abaixo do teto 3. S2 e S3 poderiam tecnicamente trabalhar em arquivos de saída distintos após S1, mas a análise real de S2 valida o uso do motor antes de integrá-lo à UI; S2 tem prioridade de entrega obrigatória e alimenta o gate P1. Esta escolha evita revisão de integração/refação e coordenação do diário/suite no MVP. Não criar arquivos de teste adicionais apenas para permitir concorrência. Dependência técnica S3→S1 é distinta da sequência operacional S2 antes de S3.

```text
Pre-condicao externa: revisao humana registrada
                         |
                         v
P1 [S1 motor 120 min -> S2 analise/estrategia 40 min]
     -> uma revisao opus -> CLI + relatorio reproduziveis
                         |
                 prioridade de entrega
                         v
P2 [S3 cockpit 110 min -> S4 validacao/entrega 40 min]
     -> uma revisao opus -> pacote local verificado

Dependencias tecnicas: S1 -> S2; S1 -> S3; S3 -> S4
Contingencia: 50 min; espera externa registrada a parte
```

| Step | Phase | Model | Agent | Depends on | Parallel with | Sub-Task File |
|---|---|---|---|---|---|---|
| S1 | P1 — Motor, análise e estratégia | opus | developer | None | None | `.specs/sub-tasks/implement-social-media-cockpit/01-analytical-engine.md` |
| S2 | P1 — Motor, análise e estratégia | sonnet | general | S1 | None | `.specs/sub-tasks/implement-social-media-cockpit/02-analysis-strategy.md` |
| S3 | P2 — Cockpit e entrega validada | sonnet | developer | S1 | None | `.specs/sub-tasks/implement-social-media-cockpit/03-local-cockpit.md` |
| S4 | P2 — Cockpit e entrega validada | sonnet | general | S3 | None | `.specs/sub-tasks/implement-social-media-cockpit/04-acceptance-handoff.md` |

Os arquivos de subtarefa são registros locais da primeira decomposição SDD e não entram no PR. A SPEC e `IMPLEMENTATION-PLAN.md` são autocontidos e prevalecem para execução. Os critérios completos e fórmulas permanecem nas seções anteriores, evitando contratos divergentes nas tasks.

### Phase Overview

#### Phase 1

Steps: S1, S2 — motor auditável seguido da análise/estratégia obrigatórias.

Reviewer model: opus, papel `code-reviewer`, uma vez ao encerrar a fase. Integridade analítica e fidelidade da estratégia aos resultados justificam o tier.

Acceptance Criteria that should be fulfiled: CLI aceita/rejeita entrada corretamente, produz comparações e exports reproduzíveis; relatório real responde ao briefing com evidências, ações e insuficiências. Os outputs de S1 e S2 têm seus próprios checks antes da única revisão. Interface/persistência ainda não são declaradas prontas.

Checklist items: CK-01–07; componente analítico/segurança de CK-10; HR-02/03.

Rubrics: R-01 — Comparabilidade analítica; R-02 — Auditabilidade; R-03 — Acionabilidade; R-04 — Clareza executiva; R-05 — Qualidade do diário.

#### Phase 2

Steps: S3, S4 — ciclo decisório local seguido de validação integrada e pacote de entrega.

Reviewer model: opus, papel `code-reviewer`, uma vez ao encerrar a fase. A revisão conjunta verifica integridade durável/temporal e uso correto do motor após integração.

Acceptance Criteria that should be fulfiled: upload → drill-down → decisão/revisão → reinício → observação posterior/pendente → exports funciona; suite, fonte real, navegador, print A4, setup e escopo Git evidenciados. HR-01 exige roteiro humano cronometrado; sua indisponibilidade não interrompe checks independentes, mas mantém DoD pendente. Pacote local verificado não significa push/deploy.

Checklist items: CK-01–11; HR-01–04; nenhum ID sem evidência é marcado satisfeito.

Rubrics: R-01 — Comparabilidade analítica; R-02 — Auditabilidade; R-03 — Acionabilidade; R-04 — Clareza executiva; R-05 — Qualidade do diário.

### Regras de execução e conclusão

Implementar somente os três módulos runtime e os artefatos definidos na arquitetura. `unittest discover` executa arquivos de teste focados em análise, exports, persistência e interface; fixtures determinísticas compartilhadas ficam em `tests/helpers.py`. Não introduzir API, ORM, frontend, framework de testes ou camada de serviços. Só adicionar otimização se a medição do CSV real identificar necessidade; registrar o motivo e manter os mesmos resultados.

Cada passo anexa ao diário os CK/HR cobertos, comandos realmente executados, resultados/limitações e julgamento humano. Os testes da etapa somam-se aos existentes. A suite completa final usa o comando da seção Regular Checks com o Python do ambiente documentado; ausência de arquivo, dependência ou evidência bloqueia sucesso. O spike antigo não substitui nenhuma validação do produto.

O pacote final mantém CSV bruto, banco, ambiente Python e ferramentas SDD fora da submissão. Conferir arquivos novos ignorados pelo Git antes de staging pontual; nunca adicionar uma pasta ampla à força. Push, PR, merge e deploy não são passos deste plano. Caso sejam autorizados posteriormente, aplicar os gates reais do repositório/provedor no diff exato, sem presumir autorização a partir da SPEC.
