# Diário 004 — Planejamento dos entregáveis

## Fechamento da segurança

Luis confirmou o encerramento da auditoria proporcional ao beta. O parecer registrou os 19 controles solicitados e concluiu que não existe implementação indispensável pendente no dashboard local, estático e somente leitura. A segurança deve ser reaberta antes de internet pública, dados reais, autenticação, banco, escrita ou API paga.

## Nova decisão de entrega

Com o projeto funcional e auditado, Luis propôs uma entrega multimodal:

- wizard guiado do sistema no estilo Arcade;
- resumo escrito da construção em texto, DOCX e Markdown;
- peça visual ligando prompts decisivos à evolução do sistema;
- vídeo explicativo, mapa mental e infográfico gerados no NotebookLM.

O objetivo não é apenas exibir o produto. É demonstrar uma metodologia proprietária de criação com IA: SDD, método socrático em cinco ondas adaptativas, SPEC, lapidação, feedback looping, redundância necessária, medição e documentação contínua.

## Pesquisa e escolha de formato

Revalidamos o guia oficial do desafio. A submissão exige solução e Process Log e valoriza decomposição, erros da IA, correções humanas, iteração e comunicação clara. O pacote proposto atende diretamente esses critérios, desde que os formatos visuais permaneçam complementares ao PR.

O material oficial do NotebookLM confirma Video Overviews, Mind Maps, Infographics e Slide Decks fundamentados nas fontes, com risco explícito de imprecisão. Por isso, todo output visual terá revisão factual antes de ser aceito.

Os benchmarks publicados pelo Arcade recomendam 9–12 passos, texto curto, valor antecipado e vídeo somente onde movimento agrega. Definimos um tour de 10 passos centrado na pergunta do CEO, não numa lista de funcionalidades.

## Arquitetura aprovada para planejamento

O README, o relatório e o Process Log continuam sendo a entrega autoritativa. Uma narrativa canônica alimentará `.md`, `.txt` e `.docx`; o mesmo source pack alimentará NotebookLM; o Arcade demonstrará em 10 passos a resposta, a evidência e a decisão. Assim, cada formato reforça a mesma verdade e o avaliador não depende de ferramenta externa.

## Ordem planejada

1. congelar contrato editorial e source pack;
2. escrever narrativa canônica e converter formatos;
3. gerar e revisar mapa mental e infográfico;
4. gerar e revisar Video Overview;
5. capturar e revisar Arcade;
6. reconciliar manifesto, README, links e PR.

## Gate

Nenhum derivado pode inventar causa, número, impacto recuperável ou score externo. NotebookLM e Arcade só recebem dados públicos do desafio. Publicação externa e submissão ao upstream aguardam confirmação final de Luis.

## Artefatos de planejamento

- SPEC: `solution/001-churn/.specs/tasks/todo/package-challenge-001-deliverables.feature.md`
- Plano: `solution/001-churn/docs/superpowers/plans/2026-09-22-challenge-001-delivery-package.md`

**Estado:** planejamento concluído; implementação ainda não iniciada.

## Enxugamento para o avaliador com pouco tempo

Luis introduziu duas restrições decisivas: o avaliador provavelmente terá pouco tempo e baixa disposição para navegar muitos materiais; além disso, já existe um vídeo obrigatório em que Luis explica a arquitetura.

**Evidência do vídeo:** arquivo MP4 de 232.879.349 bytes, duração de 365,533 segundos (6min05s), 1920×1080, 60 fps, H.264 com áudio AAC estéreo e SHA-256 `a968a524dbe45443a066717e5d63523e5336f958fb3a6dcd50d0d0887dbbea4a`. A inspeção visual confirmou captura de tela, facecam e legendas queimadas. Não há stream separado de legenda.

**Corte Ponytail:** removemos o Video Overview do NotebookLM, o mapa mental e o TXT. O vídeo existente substitui qualquer segundo vídeo; Markdown já atende leitura por IA; DOCX atende leitura humana; um único infográfico comunica a evolução visual. O MP4 não será commitado, evitando 222 MiB no histórico; o Git guardará link, poster, capítulos, metadados e checksum.

**Nova hierarquia:** quatro entradas visíveis: `Leia em 2 minutos`; `Veja funcionando em 90 segundos`; `Entenda a arquitetura em 6 minutos`; `Audite o processo`. Arcade foi reduzido a oito passos e demonstrará apenas o sistema. Relatório, código, segurança e Process Log permanecem disponíveis dentro da camada de auditoria.

**Plano canônico revisado:** `solution/001-churn/docs/superpowers/plans/2026-09-22-lean-delivery-package.md`. O plano multimodal anterior permanece no histórico e está marcado como substituído.

**Estado:** plano enxuto aguardando validação de Luis; nenhuma mídia foi publicada.

## Ajuste final de escopo por decisão de Luis

Luis decidiu manter quatro peças complementares: Video Overview do NotebookLM, infográfico do NotebookLM, Arcade no formato atual de oito passos e o vídeo obrigatório de arquitetura já gravado. A decisão substitui apenas o corte anterior do Video Overview; o mapa mental e o TXT continuam removidos.

**Separação de funções:** o vídeo obrigatório apresenta Luis explicando a arquitetura em primeira pessoa; o Video Overview sintetiza a construção, as decisões humanas e a evolução do método; o Arcade demonstra o sistema; o infográfico oferece leitura visual instantânea. Essa separação evita que dois vídeos contem a mesma história.

**Nova hierarquia:** `Leia em 2 minutos`; `Veja funcionando em 90 segundos`; `Entenda a arquitetura em 6 minutos`; `Veja a síntese do NotebookLM`; `Audite o processo`. O infográfico acompanha a síntese do NotebookLM.

**Estado:** SPEC e plano atualizados; implementação continua não iniciada.

## Auditoria final das regras oficiais de entrega

Antes da implementação dos entregáveis, Luis exigiu uma nova conferência do README raiz, do Challenge 001, do Guia de Submissão, do `CONTRIBUTING.md` e do template oficial. A regra de parada foi endurecida: nenhum push final ou PR poderá ocorrer enquanto a aderência não estiver em 100%.

A auditoria encontrou quatro lacunas. O relatório não explicitava impacto estimado por ação; a entrada não resumiria a quantidade de iterações; o plano ainda não transformava branch, PR único e título em gates; data, histórico Git e links externos precisavam de validação final. Todas foram incorporadas à SPEC e ao plano.

**Decisão metodológica:** quando o impacto financeiro não puder ser estimado causalmente, a entrega dirá “não estimável” e mostrará somente o MRR perdido observado como teto histórico. Inventar receita recuperável para preencher o requisito seria menos aderente que explicitar a limitação.

**Decisão naquele momento — posteriormente substituída pela escolha final do Challenge 001:** os quatro desafios seriam consolidados na branch única `submission/luis-roquette` e no PR único `[Submission] Luis Fernando Roquette — Challenges 001–004`; diff limitado a `submissions/luis-roquette/`; README baseado no template; setup reproduzível; links anônimos; data e histórico finais; confirmação explícita de Luis antes do envio.

**Estado:** correções locais em execução; nenhum push ou PR autorizado até a validação integral.

## Execução dos entregáveis — Task 1

A primeira etapa produziu a porta de entrada em Markdown e DOCX a partir da resposta canônica. O brief tem 777 palavras e duas páginas A4. Ele começa pelo diagnóstico do CEO, explicita o conflito entre agregado e coorte, recusa causalidade não demonstrada e apresenta três ações com responsável, prazo, impacto estimado e confiança.

O DOCX passou por duas renderizações. A primeira revelou uma borda indevida sob o título e excesso de espaço na página inicial. A quebra de página foi deslocada para a evolução da resposta e a borda do estilo foi removida. A segunda inspeção confirmou duas páginas legíveis, tabelas sem clipping, hierarquia clara e links visíveis.

**Validação:** 777 palavras; cinco números e quatro notas internas reconciliados; zero links locais quebrados; metadados pessoais removidos; nenhuma publicação externa realizada.

**Estado:** Task 1 concluída localmente. Push permanece bloqueado.

## Execução dos entregáveis — Task 2

O vídeo obrigatório foi inspecionado sem colocá-lo no Git. Confirmamos 6min05s, H.264 em 1920×1080 a 60 fps, áudio AAC estéreo, legendas queimadas, 232.879.349 bytes e SHA-256 `a968a524dbe45443a066717e5d63523e5336f958fb3a6dcd50d0d0887dbbea4a`.

A revisão visual usou 366 amostras, uma por segundo, e OCR local das legendas. Isso revelou uma correção de enquadramento: o vídeo explica a arquitetura do trabalho nos quatro desafios — SDD, Ponytail, método socrático, otimização de planos, feedback looping, segurança, UI/UX e revisão do output — e não apenas a arquitetura técnica do dashboard de churn.

Foram registrados onze capítulos e criado um poster sem tela privada. O vídeo cita notas e 99% de confiança como parte do prompt de autoavaliação; o README deixa explícito que não se trata de nota do G4 nem confiança estatística do diagnóstico.

**Estado:** pacote local do vídeo pronto. Hospedagem e validação anônima permanecem bloqueadas até confirmação explícita de Luis e reprodução integral em tempo real.

## Execução dos entregáveis — Task 3, roteiro do Arcade

Antes de criar o tour, consultamos a documentação atual do Arcade. A plataforma já oferece hotspots, callouts, pan/zoom e fluxo linear; branching seria complexidade sem benefício para uma resposta executiva de 90 segundos.

O roteiro foi reduzido a oito passos e 83 segundos estimados. Cada passo contém uma ideia e até 22 palavras: resposta curta, impacto, divergência de uso, limite da satisfação, ausência de concentração, abstenção causal, validações e rastreabilidade.

Um rascunho privado foi criado e nomeado no Arcade, sem uso de geração paga. O gravador desktop e a extensão oficial não estavam disponíveis. A alternativa nativa foi copiar capturas reais do dashboard pelo navegador e colá-las diretamente no editor; não usamos imagens sintéticas.

O rascunho recebeu oito screenshots e oito hotspots, exatamente como o roteiro. A sequência e a legibilidade foram verificadas nos previews desktop e mobile. O último hotspot retorna ao primeiro passo; o CTA para o brief aguarda a URL remota definitiva.

**Estado:** roteiro, captura e preview privado concluídos. Publicação e acesso anônimo ainda não ocorreram.

## Execução dos entregáveis — Task 4, fonte do NotebookLM

Consultamos a documentação atual do NotebookLM antes da criação. Video Overviews aceitam foco, audiência e formato; como todo output generativo, continuam sujeitos a imprecisões e revisão humana.

Para reduzir deriva, criamos uma única fonte fechada: oito etapas metodológicas, quatro notas internas, três viradas humanas e seis fatos do diagnóstico. Código, dados brutos, logs extensos e caminhos locais ficaram de fora.

Os prompts separam funções: o Video Overview sintetiza a jornada para o avaliador; o infográfico mostra método e evolução. Ambos proíbem causa inventada, receita recuperável fictícia e confusão entre rubrica interna e avaliação do G4.

O notebook privado foi criado com uma única fonte. A primeira geração do Video Overview, curta e em português brasileiro, preservou o diagnóstico central, mas exibiu “6 hipóteses rejeitadas”. Como o resultado correto é “seis hipóteses inconclusivas”, o vídeo foi rejeitado. O prompt foi corrigido uma única vez com essa regra explícita e uma segunda geração explicativa foi iniciada.

A configuração do infográfico chegou ao gate final em formato retrato e estilo editorial, mas o NotebookLM informou que o limite diário de infográficos havia sido atingido. Não contratamos upgrade nem contornamos o limite.

A segunda geração, “Paradoxo de Churn do CEO”, ficou pronta com 6:00. O arquivo foi decodificado integralmente; áudio e 360 quadros foram auditados por transcrição e OCR. A versão corrigida declara “hipóteses inconclusivas”, preserva os números canônicos e separa a rubrica interna de qualquer nota do G4 ou confiança estatística.

**Estado:** fonte, prompts, notebook privado e Video Overview revisado concluídos; primeira versão rejeitada; infográfico bloqueado até a renovação do limite; nada publicado.

## Fechamento em cinco entradas — início da Task 5

A abertura da submissão foi reorganizada em exatamente cinco escolhas. O DOCX passou a acompanhar o brief; relatório, dashboard, código e diários ficaram agrupados em “Audite o processo”. Também removemos da abertura uma quarta recomendação que não fazia parte da resposta canônica final, preservando as três validações aprovadas.

**Estado:** hierarquia da entrega reconciliada localmente. Links externos e gate anônimo continuam pendentes.

## Auditoria da regra de PR único

A consulta remota encontrou as PRs #140 e #141 fechadas e a PR #145 aberta para o Challenge 004. A PR aberta usa `submission/luis-roquette-004-social`, enquanto o guia exige a branch canônica `submission/luis-roquette`.

Não alteramos branches, PRs ou conteúdo remoto naquela etapa. Esse plano de consolidação foi posteriormente substituído pela escolha exclusiva do Challenge 001 registrada abaixo.

## Decisão final — Challenge 001 como desafio principal

Luis definiu o Challenge 001 — Diagnóstico de Churn como o desafio principal. A releitura das regras oficiais confirmou que o candidato deve escolher um challenge, manter toda a mudança dentro de `submissions/luis-roquette/`, incluir solução e Process Log, usar a branch `submission/luis-roquette` e abrir um único PR no formato `[Submission] Nome — Challenge XXX`.

A decisão elimina a consolidação dos quatro desafios no mesmo PR. A entrega final conterá exclusivamente o Challenge 001; as PRs anteriores dos Challenges 002 e 003 permanecem fechadas, e a PR aberta do Challenge 004 deverá ser encerrada antes da abertura do PR canônico do Challenge 001.

**Gate:** publicar somente depois de validar setup, testes, reprodução determinística, links, acesso anônimo e ausência de mudanças fora da pasta permitida.

## Fechamento dos vídeos sem hospedagem externa

Para reduzir dependências e evitar links privados, os dois vídeos passaram a ser entregues diretamente no repositório. O vídeo autoral obrigatório foi comprimido de 232,9 MB para 58,2 MB, sem cortes, em H.264 720p/30 fps com áudio AAC. A duração foi preservada, o arquivo foi decodificado integralmente e nove pontos da faixa visual foram inspecionados após a compressão. O Video Overview aprovado do NotebookLM ocupa 16,1 MB e também foi incluído.

O Arcade já expõe uma rota pública que responde sem cookie ou sessão. O NotebookLM permanece privado porque fonte, prompt e exportação aprovada são entregues no próprio Git. O infográfico continua bloqueado pelo limite diário informado pela plataforma; não houve compra de upgrade nem tentativa de contornar a cota.

## Fechamento oficial do Challenge 001

Luis reafirmou o Challenge 001 como desafio principal e autorizou concluir todo o escopo necessário para a entrega. Reauditamos o README do desafio, o README raiz, o Guia de Submissão, o `CONTRIBUTING.md` e o template oficial. O pacote atende a escolha de um único desafio, mantém solução e Process Log em `submissions/luis-roquette/`, documenta setup reproduzível e prepara branch, pasta e título exigidos para o PR único.

O gate remoto passou Ruff, formatação e 84 testes. A primeira comparação reproduzível acusou diferença entre conjuntos de artefatos; a investigação mostrou que a tentativa de regeneração sobre a pasta canônica não produziu mudança versionada. O próximo passo do feedback loop foi isolar a diferença do manifesto em uma reprodução limpa, sem alterar conclusões ou inventar causalidade.

**Estado:** Challenge 001 confirmado como principal e único. Arcade público e vídeos incorporados estão prontos; o infográfico continua como único bloqueio externo declarado até a renovação da cota do NotebookLM.

## Decisão final — portfólio completo com prioridade explícita — 2026-09-23

Após o envio inicial do Challenge 001, Luis decidiu manter o mesmo PR e acrescentar os Challenges 002, 003 e 004 como entregas complementares. O Challenge 001 continua sendo a resposta oficial, principal e mais importante; os demais demonstram amplitude sem disputar sua prioridade. A decisão preserva a regra de PR único e a FAQ, que permite mais de um desafio.

Uma nova consulta ao NotebookLM em 23 de setembro manteve a mensagem “Você atingiu seu limite diário de infográficos. Volte mais tarde.” O bloqueio foi preservado com transparência; não houve upgrade, automação paralela nem tentativa de contornar a restrição da conta.

O diagnóstico da reprodução isolou a diferença em um único campo de `ceo_answer.json`: a lista de tabelas-fonte do relatório de qualidade herdava a ordem de inserção de um dicionário. O JSON de qualidade era canônico porque suas chaves eram ordenadas na serialização, mas a lista derivada podia mudar entre processos. Corrigimos a origem com ordenação explícita e adicionamos um teste que inverte a ordem de entrada e exige a mesma saída. A suíte passa a ter 85 testes.

A passagem seguinte imprimiu o diff estrutural completo e revelou a causa restante: três números do JSON executivo variavam apenas na 16ª casa decimal entre processos, embora todos os CSVs, o relatório e as conclusões fossem idênticos. Canonizamos os campos numéricos das claims em 15 casas decimais e adicionamos regressão com perturbação de `4e-17`. A suíte passa a ter 86 testes; a precisão decisória e os valores exibidos permanecem inalterados.

## Gate técnico final e nova verificação externa

O gate remoto foi repetido no commit exato `de5f84429b1f648a448be6603527af2e2f2c8be4`, em Codespace limpo. Ruff, verificação de formatação e os 86 testes passaram; a reprodução independente terminou com `artifact_sets=equal`. O diff contra o `main` oficial permanece restrito a `submissions/luis-roquette/`, sem arquivo acima de 99 MB.

Em 23 de setembro, uma nova verificação visual do NotebookLM manteve a mensagem “Você atingiu seu limite diário de infográficos. Volte mais tarde.” O infográfico é opcional pelas regras do G4, mas continua no escopo definido por Luis. Por isso, não houve upgrade, troca de conta, encerramento da PR #145 nem abertura da submissão final antes da renovação da cota.

Às 09h18 BRT do mesmo dia, Luis pediu nova tentativa por já ter atravessado uma mudança de data. A configuração foi refeita e validada — português do Brasil, retrato, editorial, detalhamento padrão e prompt canônico —, mas o bloqueio reapareceu somente após clicar em `Gerar`. A interface mostrava as gerações anteriores como feitas havia 10 horas, evidência compatível com uma janela móvel, não com renovação automática à meia-noite. Nenhum upgrade ou contorno foi usado.

## Substituição determinística do infográfico

Diante da terceira recusa do NotebookLM, Luis decidiu concluir a entrega sem depender da plataforma e sugeriu avaliar Higgsfield. A pesquisa anterior à criação mostrou que Higgsfield Canvas é orientado a fluxos generativos de imagem e vídeo e consome créditos por geração; Canva e Adobe Express oferecem editores próprios para infográficos. Como este artefato exige texto, números e limites causais exatos, escolhemos a alternativa mais auditável: SVG local, sem API paga, com PNG e PDF derivados.

A direção visual `Evidência Estratificada`, criada com a skill `canvas-design`, reutiliza a paleta do dashboard e organiza paradoxo, oito etapas, evolução interna, três viradas humanas e resposta ao CEO em uma página vertical. A primeira inspeção detectou sobreposição nas legendas das oito etapas. O layout foi corrigido na origem para duas linhas de quatro etapas; a segunda renderização confirmou hierarquia, margens, contraste e leitura móvel sem clipping.

**Estado:** infográfico concluído em SVG editável, PNG 1400×2400 e PDF de uma página. O bloqueio do NotebookLM deixa de bloquear a submissão; a tentativa e a decisão de substituição permanecem registradas como parte da jornada.

**Validação:** XML válido; PNG `1400×2400`; PDF de uma página com texto extraível; zero clipping na inspeção visual; links locais existentes; diff restrito à pasta permitida. SHA-256: SVG `9fece34377ed4f249ec0d96d31b75acf8c2534ee85e1a5df47541d75cb8534d0`, PNG `a9eca43943e8eb32c11f01ec1489cab429213d7d3e8ba2cd1bc4bfc5392e6c8a`, PDF `3700627491b69cc92d31329c33432f13a0613c895a9b401a0617a4ea16fc1972`.
