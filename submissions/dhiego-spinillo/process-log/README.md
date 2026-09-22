# Process log — análise inicial

**Registro organizado em 15/09/2026 a partir da conversa já ocorrida.** É uma síntese retrospectiva; não é uma gravação integral nem um diário com horários exatos. Novas decisões serão acrescentadas conforme acontecerem.

## Ferramentas e papéis

Claude produziu o plano inicial. Codex revisou esse plano, inspecionou os dados, escreveu/executou a auditoria e ajudou a estruturar as alternativas. Dhiego orientou a investigação e introduziu/restringiu decisões de produto. A revisão considerou experiência profissional e projetos anteriores como contexto; o pacote não inclui código ou dados privados desses sistemas.

## Decomposição

Entender a solicitação do diretor → conferir a evidência → identificar lacunas → escolher intervenção → avaliar → comunicar. Hoje a atividade permanece nas etapas de análise e definição; construção prevista para amanhã.

## Iterações documentadas

Os nove marcos abaixo são agrupamentos temáticos retrospectivos, não contagem de prompts ou sessões.

| Marco | Intervenção / evidência | Mudança |
|---|---|---|
| 1 | Dhiego pediu crítica do plano de Claude | A proposta inicial passou a ser hipótese revisável. |
| 2 | Auditoria por Codex encontrou ausência de abertura, ordem temporal inválida e cobertura limitada de satisfação | Abandonar duração inventada e separar cenário de economia medida. |
| 3 | Dhiego trouxe feedbacks públicos e questionou a prioridade do protótipo | Interface funcional passou ao escopo principal. |
| 4 | Discussão das 4–6h e do process log | Contar preparação no esforço total; documentar processo real. |
| 5 | Dhiego encerrou a comparação com candidatos e priorizou entender o problema | Nenhuma nova investigação de soluções concorrentes desde essa decisão. |
| 6 | Dhiego propôs aplicação própria, OpenRouter e n8n | Opções registradas; stack e utilidade do LLM ainda abertas. |
| 7 | Dhiego questionou colocar IA em tudo | ADR 0001: separar regras, inferência e decisão humana. |
| 8 | Dhiego trouxe flags e acompanhamento; em seguida decidiu reservá-los para o futuro | ADR 0002 e mapa de dados necessários, sem ampliar o protótipo atual. |
| 9 | Dhiego definiu hoje como análise e amanhã como implementação | Roadmap, status e pacote inicial para versionamento. |

## Erros e revisões da IA

- O plano de Claude repetiu o volume aproximado do brief e propôs analisar tempos sem verificar a semântica dos campos. A auditoria de Codex verificou contagens e limites.
- O plano inicial sugeriu volume multiplicado por tempo médio como desperdício; a revisão distinguiu espera/tempo decorrido de esforço ativo.
- Codex inicialmente tratou interface como opcional; a discussão com Dhiego mudou a prioridade.
- A sugestão de Codex de mostrar flags avançadas em cenários simulados foi retirada após Dhiego restringir essas ideias a propostas futuras.
- A preparação não pode desaparecer da contabilização de esforço. Nenhum total de horas foi medido até aqui.

## Contribuição do candidato

Escolheu conduzir entendimento antes da implementação; exigiu fronteira determinística; trouxe experiência de operação para discutir prioridades; definiu dados necessários como condição de evolução; delimitou o escopo. As descobertas computacionais produzidas por Codex permanecem atribuídas a essa revisão.

## Evidências e limites

- [Trechos literais selecionados da conversa](evidencias/trechos-da-conversa.md).
- [Trechos do plano inicial](evidencias/plano-inicial.md).
- [Auditoria](../solution/auditar_datasets.py) e [resultado](../solution/reports/auditoria-datasets.json).
- [ADR 0001](../docs/decisions/0001-fronteira-entre-regras-e-ia.md) e [ADR 0002](../docs/decisions/0002-flags-priorizacao-e-acompanhamento.md).

A consulta anterior a avaliações públicas serviu para entender expectativas de entrega; os aplicativos dos candidatos não foram reproduzidos. A auditoria dos nossos CSVs ocorreu antes dessa comparação. Não há captura de aplicativo funcionando, modelo treinado ou resultado de integração a apresentar nesta etapa.

O primeiro registro Git reúne o trabalho de análise já ocorrido. Não foi reconstruída uma sequência fictícia de commits anteriores. O cronômetro das atividades anteriores não foi registrado; duração permanece não apurada, incluindo preparação e pesquisa.

## Continuação — perguntas de CX e exploração preliminar

Dhiego pediu exploração dos números à luz de sua experiência em atendimento e distinguiu urgência de criticidade. Acrescentou hipóteses de penalização recorrente do cliente, repetição de informação, respostas parciais e dificuldade de compreensão pelo atendente. Também autorizou commits que demonstrem progresso. O primeiro commit local registra o pacote de análise inicial; esta continuação corresponde ao aprofundamento posterior.

Codex executou nova exploração integral: distribuição por canal/tipo/prioridade, notas baixas entre avaliados, busca literal de sinais, consistência de identidade para emails repetidos e tamanho das resoluções. Inspecionou uma amostra de 20 resoluções (seed 42), exemplos de termos de urgência e trechos que revelaram falsos positivos de palavra-chave. Produziu [script](../solution/explorar_cx.py), [resultados](../solution/reports/exploracao-cx.json) e [análise para discussão](../solution/analise-preliminar-cx.md).

Achados adicionais incluem 78 de 165 textos com `urgently` marcados Low/Medium, identidade não reconciliada em emails repetidos, 2.881 casos aguardando cliente e resoluções de 3–8 palavras. A interpretação separa contagens do arquivo de hipóteses sobre a operação: não conclui que houve violação de SLA, reincidência real, atendimento inadequado ou churn. Não houve implementação de produto nem mudança automática do escopo.

## Continuação — qualidade por pergunta e significado da pendência

Dhiego pediu separação entre sujeira do dataset e sinais operacionais, sugeriu análise por atendente e perguntou por satisfação/NPS. Esclareceu que aguardar o cliente pode significar informação/documento necessário ou confirmação de uma solução já realizada. Esses exemplos alteraram a estrutura da análise e dos dados futuros necessários, sem atribuir todos os pendentes a retrabalho.

Codex implementou [auditoria por universos](../solution/auditar_coortes.py), verificou as descrições originais no Kaggle e produziu [relatório](../solution/qualidade-por-pergunta.md). A exclusão de identidade ambígua deixa 8.181 emails sem repetição; 1.404 pares temporais não invertidos continuam sem abertura. Notas 1–5 podem ser descritas entre 2.769 avaliados; não há atendente nem NPS. Surgiram rótulos diferentes em grupos de texto normalizado idêntico. A análise de sensibilidade preservou aproximadamente a média de satisfação e a proporção de prioridades baixas/médias nos textos com `urgently`.

O [ADR 0003](../docs/decisions/0003-universos-analiticos-e-qualidade.md) registra a regra: limpeza por finalidade, preservação da origem, sem inventar correções ou tratar formato válido como prova de realidade. Solicitação urgente com prioridade baixa permanece uma suspeita para revisão, não uma exclusão automática.

## Continuação — exemplos do dataset e recap assistido

Dhiego reforçou que guias fiscais eram analogias de sua experiência, não fatos do dataset. Propôs recap para orientar o atendente sobre pedido, tentativas, respostas e próximos passos, e eventualmente uma ou duas sugestões de resposta revisadas, sem autorresposta.

Codex voltou aos arquivos e encontrou exemplos concretos: erro de acesso já informado no D1; tentativa de liberar espaço no D2; trechos de cadeias de email sobre extensão de conta e atualização de atributos. A análise anterior foi refinada: o D2 não tem eventos estruturados, mas alguns documentos contêm indícios de múltiplas interações. O perfil contou 4.133 documentos com pelo menos 100 palavras, sem confundir comprimento com número de mensagens.

Foram criados [extrator](../solution/inspecionar_contexto.py), [evidências selecionadas](../solution/reports/contexto-e-recap.json) e [discussão de recap](../solution/contexto-e-recap.md). As sínteses e perguntas de exemplo foram redigidas por Codex para análise, não por uma funcionalidade implementada nem por uma avaliação independente. O escopo final permanece aberto.

## Continuação — análise visual, branding e fronteira do recap

Dhiego pediu uma v1 visual para explorar os dados, questionou se o recap ficaria fixo e indicou o artigo e o vídeo do rebranding do G4 como referências obrigatórias. Codex consultou o artigo, estilos e logo públicos do site, além da descrição e transcrição disponível do vídeo. As fontes e decisões estão em [identidade visual](../docs/identidade-visual.md).

Foi criada uma [análise interativa](../solution/visual/index.html), gerada a partir dos quatro relatórios JSON, com cinco perguntas sobre qualidade, comparação descritiva por canal, hipóteses sobre pendência e cinco exemplos de tickets com trechos de origem destacáveis. As analogias contábeis não foram transformadas em evidência do dataset. A leitura de contexto preparada por Codex aparece explicitamente como exemplo fixo; não há chamada de modelo ou medição de qualidade de recap.

O ADR 0001 foi esclarecido: cálculos podem ser pré-computados e versionados; se recap for escolhido para o protótipo, a inferência deve operar sobre a entrada selecionada. Apoio à compreensão e sugestão de resposta são tarefas distintas. A análise visual não fecha esse escopo.

Verificação: navegação e cinco filtros de qualidade, seleção dos cinco exemplos, destaque de fonte e abertura do rascunho; inspeção visual em 1440×1000 e 390×844, sem transbordamento horizontal nas verificações. [Capturas e limites da verificação](evidencias/visual-v1/README.md). Nenhum total de esforço foi reconstruído ou atribuído artificialmente às 4–6 horas sugeridas no desafio.

## Pausa — 15/09/2026

Dhiego encerrou a sessão antes de conseguir consumir a análise visual e pediu registro e commit do ponto de parada. A v1 está entregue no commit local `746f9fb`, mas sua leitura e discussão pelo candidato permanecem pendentes. Não houve aprovação do diagnóstico completo nem escolha final de protótipo, stack ou integração de IA.

Codex atualizou o estado e o roadmap para retomar pela análise, apresentar um problema por vez e registrar as provocações antes da implementação. A construção continua prevista para 16/09, com meta pessoal de concluir até esse dia; não há prazo oficial conhecido. Commits locais, sem push ou PR. Nenhum tempo de execução foi inventado.

## Adendo à pausa — revisão multimodelo

Dhiego propôs usar Oráculo Flow com Claude, Grok e Codex para julgar dados, análises e alternativas. Codex consultou o README e a seção de confronto do workflow no repositório local do Oráculo Flow e registrou um [protocolo proposto](../docs/revisao-multimodelo.md): mesmo material, pareceres sem acesso prévio aos demais, divergências verificadas nos dados e decisão com o candidato. Grok é uma extensão solicitada por Dhiego; integração e acesso ainda não foram verificados. Nenhuma revisão externa foi executada e a pausa permanece vigente.

## Retomada — 21/09/2026

Dhiego voltou ao case, leu toda a análise visual e perguntou pelo próximo passo. A leitura foi marcada como concluída; não foi inferida aprovação das interpretações ou do escopo. Codex releu o enunciado e preparou uma [proposta de triagem assistida](../docs/recorte-proposto.md), com classificação avaliada no D2 e recap como hipótese de apoio à compreensão. O documento explicita alternativas menores, avaliação separada e limites para alegações de ganho operacional.

A conversa de 18/09 incluiu Jev/TypeSafe como possível experimento; não houve integração nem teste. A revisão multimodelo permanece pendente. As datas do roadmap foram atualizadas para deixar a meta passada de 16/09 como histórico, sem inventar nova data ou duração de esforço. Próxima etapa: discutir a prioridade do candidato e confrontar a proposta antes da construção.

## Verificação de acesso ao Jev — 21/09/2026

Dhiego reforçou Jev como candidato para classificação e forneceu uma credencial para o experimento. Codex a configurou em arquivo local ignorado pelo Git com permissão 0600, sem reproduzi-la neste registro. Consultou o [quickstart oficial](https://docs.typesafe.ai/introduction/quickstart) e criou uma verificação em Python com um texto sintético curto e três categorias.

A tentativa no ambiente restrito falhou na conexão; uma nova tentativa com rede liberada também falhou. O diagnóstico local mostrou DNS indisponível no sandbox e ausência de arquivo padrão de certificados no Python instalado. O script passou a usar o bundle do sistema quando necessário, mantendo validação TLS. A execução seguinte com rede liberada retornou HTTP 200, categoria `hardware` e modelo `jev-1.13.0`.

Evidências: [script](../solution/verificar_jev.py) e [relatório sem credenciais](../solution/reports/jev-conexao.json). Houve uma resposta de inferência bem-sucedida; tentativas anteriores não produziram resultados utilizáveis. A latência registrada inclui rede/TLS e não representa benchmark. Não foi enviada a base de tickets, não há avaliação de qualidade no D2 e o recorte de produto permanece em discussão.

## Construção autorizada e comparação — 21/09/2026

Dhiego pediu comparar os modelos e avançar para concluir o case hoje. Configurou OpenRouter no arquivo local para revisão e recap. Codex preparou ambiente isolado, baixou novamente o D2 e confirmou o hash. O primeiro ambiente escolheu Python3.14 automaticamente e começou a compilar NumPy; foi interrompido e recriado explicitamente com Python3.10, sem alterar o ambiente global.

O protocolo reservou validação/teste antes de treinar, removeu vizinhos próximos do treino e da validação e congelou descrições de categorias. Executados TF-IDF + regressão logística e1.192chamadas Jev. Resultado no mesmo teste800:86,00% local e45,25% Jev. A meta de erro<=5% no grupo selecionado pela validação falhou no teste. A escolha por modelo local e confirmação humana está no [ADR0004](../docs/decisions/0004-classificador-local-e-confirmacao-humana.md).

Foram obtidos pareceres reais de Claude e Grok via OpenRouter com o mesmo briefing, além de revisão Codex em agente separado. [Pareceres e confronto](revisao-2026-09-21/decisoes.md). A revisão encontrou ambiguidade na descrição do split, pediu sensibilidade e apontou fragilidades de retomada/contrato que foram corrigidas. Não foram inventadas respostas de modelos nem atribuída execução de scripts aos revisores por API.


## Revisão do protótipo pelo candidato — valor operacional

Ao explorar o protótipo em 21/09, Dhiego questionou o destaque de uma simulação de 8,33 horas/mês: 500 tickets × 1 minuto eram premissas arbitrárias escolhidas por Codex e não sustentavam um argumento de valor para a operação. A objeção não foi resolvida aumentando os números. Codex retirou a calculadora e passou a explicitar o que o piloto precisa medir: fila correta, trabalho ativo incluindo revisão/correção e qualidade preservada. Os cerca de 30 mil tickets/ano pertencem ao contexto do desafio; não medem elegibilidade nem autorizam extrapolar o desempenho do D2 à operação do D1.

A comparação técnica favorece o classificador local, mas não demonstra redução de sobrecarga. O ganho operacional permanece aberto. A leitura do protótipo pelo candidato não foi registrada como aprovação de qualidade dos recaps nem como validação do produto completo.


## Evidências técnicas da construção — 21/09/2026

O aplicativo FastAPI/Jinja/JavaScript executa classificação local e persiste sugestão, confirmação/correção e motivo em SQLite. O Docker inclui o modelo e monta um volume separado para o banco. A interface segue as referências visuais G4 documentadas. O ambiente está ligado apenas a 127.0.0.1:8766.

A primeira avaliação de recap aceitou 2/16 saídas. Um diagnóstico separado no treino revelou JSON válido em bloco Markdown; o parser passou a aceitar somente um bloco completo, mantendo validação de esquema e citações. A primeira rodada foi preservada, e a segunda manteve seleção e prompt, com novas chamadas. Houve 15/16 saídas válidas; o revisor automatizado Grok aprovou fidelidade em 6/15. A integração passou a registrar respostas brutas disponíveis para investigação. Não se atribui a mesma causa a todas as falhas iniciais, cujos corpos não foram preservados.

Decisão: recap experimental e desligado por padrão, inclusive na API. Citação literal não garante interpretação correta. Não houve avaliação humana de referência nem medição de ganho de tempo. [Relatório completo](../solution/avaliacao-recap.md).

Verificação: 122 testes passaram localmente após a alteração de padrão do recap; a versão anterior também teve 122 testes passando dentro do Docker. Testes verificam contratos, política, omissão de recap inválido, manutenção da classificação em falhas, persistência e exportação sem o texto original. A reconstrução da interface revelou cache antigo de CSS/JS no navegador; referências dos assets receberam versão explícita para manter HTML e scripts consistentes. Registros funcionais produzidos por Codex durante QA não contam como validação humana do candidato.


## Revisão guiada de utilidade — preparação

Dhiego apontou falta de clareza sobre problema, impacto, entregáveis, estado e próximos passos. Codex explicitou o mapa da entrega e propôs revisar três tickets junto com o candidato antes de fechar a intervenção. Dhiego autorizou seguir.

Foram selecionados intencionalmente três registros da avaliação já executada, sem novas chamadas de IA: 45.057 (Outlook, texto curto e categoria questionável à luz do conteúdo), 34.887 (férias, tentativas e mensagens concatenadas) e 45.725 (férias com relato de possível acesso a dados de outro colega). Os três acertam o rótulo do dataset, mas expõem limitações diferentes de utilidade e interpretação. O roteiro separa saídas efetivamente registradas de leituras/hipóteses redigidas por Codex.

[Roteiro](../docs/revisao-guiada-tres-tickets.md) · [Saídas reunidas](../solution/reports/revisao-guiada.json). Contagens de palavras descrevem extensão em idiomas distintos e não medem esforço. Primeiro caso apresentado com pergunta ao candidato; feedback pendente no momento deste registro. Nenhuma avaliação humana foi inventada. Casos discutidos passam a servir ao desenvolvimento; não podem ser usados como novo teste independente após ajustes.


## Revisão guiada — decisão do candidato no caso 1

Para o registro D2 45.057, Dhiego escolheu: “Conferir o registro atual; só perguntar ao cliente se faltar confirmação necessária.” A decisão prioriza a conferência interna e condiciona novo contato a uma confirmação necessária, em vez de seguir automaticamente a coleta de detalhes sugerida pelo recap. Não autoriza encerramento automático nem valida a categoria do dataset.

O feedback foi registrado no roteiro e no JSON do caso, com escopo operacional explícito. Casos 2 e 3 continuam sem feedback. Nenhum ganho de tempo foi atribuído à decisão; prompt e produto permanecem inalterados até fechar o recorte da revisão.


## Revisão guiada — decisão do candidato no caso 2

Para o D2 34.887, Dhiego definiu consultar outros tickets abertos, verificar no sistema se as férias estão lançadas e consultar notas internas do atendimento. Se lançadas, propôs uma confirmação breve e abertura para outra necessidade. Se não lançadas, pediu atualização do diagnóstico: nova tentativa, persistência e etapa do erro, evidências como print e escalonamento técnico.

A resposta original e os caminhos condicionais estão no [registro estruturado](../solution/reports/revisao-guiada.json). A contribuição mostra que o texto isolado não basta para escolher o próximo contato: registros relacionados, estado do sistema e notas internas precisam orientar a assistência. O protótipo não acessa essas fontes; nenhuma verificação foi simulada como real. Prompt e aplicativo permanecem inalterados enquanto concluímos o terceiro caso. Não houve medição de impacto ou aprovação integral do recap.


## Revisão guiada — terceiro caso e fechamento do recorte

Dhiego manteve RH como assunto do D2 45.725 e reconheceu um relato de possível incidente. Propôs entender com o cliente como chegou à conclusão, obter evidências e possivelmente envolver Segurança ou Engenharia para consultar logs. RLS, cookie/cache, interpretação e ID incorreto em evento foram hipóteses levantadas pelo candidato, sem confirmação. A investigação deve distinguir falha técnica de preenchimento.

Com os três casos discutidos, Codex delimitou o ajuste: ficha de conferências preenchida pelo atendente e próximo passo calculado por regras. Não serão simuladas consultas a sistemas nem alegada detecção automática de incidentes. [ADR 0006](../docs/decisions/0006-contexto-verificado-e-investigacao-humana.md). Implementação/testes em andamento; nenhum ganho operacional foi medido.


## Implementação do fluxo e rascunhos por regra

Após os três casos, Codex implementou uma ficha de conferências declaradas pelo atendente e uma política no servidor para preparar o próximo passo. Dhiego perguntou se a sugestão de resposta entraria nesta etapa; foram incluídos rascunhos editáveis por regra para confirmação, atualização de diagnóstico e esclarecimento de relato de incidente. Não foi usado LLM para esses textos, nem executada ação externa. O recap e sua avaliação permanecem preservados.

O estado conhecido no sistema exige registro de consulta. Conferências pendentes impedem o rascunho rotineiro; indisponibilidade não equivale a pendência da solicitação. Relato de incidente permite orientação própria sem esperar concluir consultas rotineiras; o trecho precisa existir no ticket e a categoria é preservada. Não há detecção automática de incidentes nem diagnóstico de causa. Registros anteriores continuam exportáveis.

147 testes passaram localmente e no contêiner. Verificação no navegador: caso de férias com contexto desconhecido sem rascunho; conferências simuladas liberam confirmação; registro persiste sem enviar mensagem; relato de incidente mantém RH e pede evidências sem atribuir causa. Testes adicionais verificam estado pendente, fontes indisponíveis, trecho inválido, acesso por API sem prévia visualização e exclusão de conteúdo original/rascunho na exportação.

A inspeção em 1440×1000 e 390×844 motivou manter a entrada acessível no desktop com altura limitada; também corrigiu a descrição inicial dos exemplos após adicionar os três casos discutidos. Não foram realizadas consultas reais a sistemas: registros de QA identificam a simulação e não são feedback humano do candidato.


## Organização da entrega para o diretor

Dhiego observou que o protótipo, sem sistemas/notas/tickets relacionados, demonstra uma ideia limitada e perguntou pelos demais entregáveis, incluindo análise e one-pager. Codex reuniu os resultados existentes num resumo executivo em Markdown e HTML, com acesso pelo aplicativo e caminho de leitura no README. Nenhuma nova funcionalidade de atendimento ou métrica de impacto foi criada para preencher essa lacuna.

O resumo apresenta o cenário como contexto, três achados observados com limites, comparação de modelos, fronteira do protótipo e investimento proposto em instrumentação/piloto. Não atribui os 30 mil tickets anuais aos datasets, não chama espera de desperdício e não apresenta ganho operacional como medido.

## Três caminhos, oportunidades e economics — 21/09/2026

Dhiego pediu mais valor além de clicar e validar: pedidos resolvidos por autosserviço, trabalho praticamente pronto e casos de julgamento humano. Pediu estimativa de ROI com salário e premissas e sugeriu capturas nas evidências em vez de depender de VPS. Codex registrou a [ADR 0007](../docs/decisions/0007-autonomia-por-procedimento-e-cenarios-economicos.md) e o [mapa de evolução](../docs/tres-velocidades.md). A classificação atual continua assistida; nenhum reset, alteração cadastral ou conector foi implementado nesta etapa.

Busca integral no D2 encontrou 685 menções a reset, 161 a alterações de perfil/dados e 78 a palavras de frustração. O script registra regex, hash, contagens e amostras seed 42. Inspeção de seis exemplos por busca mostrou pedidos, falhas e falsos positivos; contagem não foi tratada como elegibilidade, sentimento ou taxa automatizável.

A calculadora usa referência salarial externa explicitamente como aproximação (mediana R$ 3.630; premissa editável R$ 4 mil), separa capacidade e despesa evitada, inclui custos e cenários negativos. As fórmulas foram verificadas em testes; uma asserção de ponto de equilíbrio precisou de tolerância numérica de 1e-8 para resíduos de ponto flutuante (aproximadamente 4e-12 reais). Não alterou resultados econômicos. 165 testes passaram localmente e no contêiner.

No navegador, foram verificados cenário base, conservador e conversão financeira zero, invalidação do resultado ao editar e leitura responsiva. A inspeção identificou a fonte do título de Economia herdando Manrope; corrigida para PPMuseum. [Capturas e roteiro](evidencias/economia-v1/README.md). Nenhuma nova chamada paga a modelos, publicação em VPS, push ou PR nesta etapa.

## Da crítica de ROI aos procedimentos executáveis — 21/09/2026

Dhiego rejeitou o valor pouco convincente do cenário agregado e determinou construir uma solução que aportasse valor. Codex implementou `/fluxos`: extração restrita por IA, três consultas locais fictícias, política determinística e execução persistida. O propósito é retirar busca/transcrição do atendente e permitir autosserviço elegível, mantendo investigação para exceções. Nenhuma integração ou conta de produção foi simulada como real.

O caminho autônomo exige escolha do cliente; token vinculado à execução, expiração e uso único; revalidação de conta, procedimento e falha em investigação antes da execução. Conclusão altera a versão de credencial no provedor de demonstração, sem senha/email real. Falha transfere histórico. Rascunho aprovado é preservado e investigação permanece aberta.

A primeira verificação de desenvolvimento usou seis cenários conhecidos e todas as rotas coincidiram com a expectativa. Uma repetição no navegador revelou instabilidade: o LLM tratou pedidos/cabeçalhos do D2 46.304 como tentativas. A [primeira rodada](../solution/reports/fluxos-desenvolvimento-inicial.json) e o [DOM observado](evidencias/fluxos-v1/iteracao-extracao.txt) foram preservados. Codex adicionou distinções ao prompt, gate conservador para históricos concatenados e rascunho que não afirma falha sem estado confirmado. O pedido curto D2 1.083 passou a representar autosserviço; o anterior foi mantido como cenário de ambiguidade, sem ser excluído da verificação.

Na [rodada seguinte](../solution/reports/fluxos-desenvolvimento.json), sete cenários conhecidos tiveram as rotas esperadas; seis extrações de IA foram aceitas e uma execução usou fallback, sem diagnóstico mais específico preservado. Isso não é acurácia independente nem prova de qualidade operacional. Recap e comparação anteriores permanecem preservados.

Revisão independente de acabamento encontrou dois problemas materiais: falha conhecida no contexto não bloqueava reset se omitida do texto; textarea permitia edição durante aprovação e escondia o texto salvo. Ambos foram corrigidos; revisão confirmou as correções. Testes cobrem falha omitida, mudança do contexto após emissão do token, tokens errados/expirados/reutilizados, injeção de campos no contrato, pedidos múltiplos, fallback e ações incompatíveis com o caminho. A documentação visual foi atualizada por agente separado, apenas por leitura de código.

O economics em `/valor` agora usa volumes exclusivos, minutos anteriores/residuais, sucesso e custo de falhas. A preparação responde por aproximadamente 92% das horas no exemplo; reset isolado não paga a operação assumida. Tempos, volumes e custos são hipóteses descritas por etapas, sem alegação de saving. [Memória](../docs/valor-por-processo.md) e [ADR 0008](../docs/decisions/0008-fluxos-executaveis-e-valor-por-processo.md).

Validação: 204 testes locais e no contêiner; sintaxe JavaScript conferida. Navegador: interpretação real por IA, autosserviço concluído, falha posterior com histórico, resposta editada/aprovada e investigação sem resolução presumida. Capturas em desktop/celular no [roteiro de evidências](evidencias/fluxos-v1/README.md). Chaves e dados runtime permanecem fora do Git. Commits locais, sem publicação/push/PR.

A página inicial passou a abrir os três caminhos. O classificador/ficha anterior foi preservado em `/classificador`, com APIs e resultados anteriores intactos.

## Pausa e prontidão de entrega — 22/09/2026

Dhiego pediu uma checagem de material suficiente para entregar e perguntou sobre processar todos os tickets. Codex releu enunciado/guia, identificou instruções antigas no README/PR/roadmap e confirmou a diferença entre classificação avaliada em 800 tickets reservados e fluxos exercitados em sete cenários conhecidos. Uma instância Docker descartável, sem chave de IA e com banco temporário, carregou o modelo e concluiu o autosserviço por regras.

A rodada local dos 47.837 tickets foi anunciada, mas não chegou a ser implementada ou executada antes de Dhiego solicitar pausa para cuidar da bebê. Não houve novas chamadas pagas, push, PR ou publicação. Os ajustes de apresentação também ficaram pendentes. [Checkpoint completo](../STATUS.md).

## Retomada e classificação integral — 22/09/2026

Dhiego retomou perguntando como seguir para entregar. Codex implementou a inferência local sobre todos os **47.837 registros do D2**, preservando modelo, split e limiar. O script valida hashes, cobertura exclusiva das partições e reprodução das 1.192 previsões históricas. Não houve novo treino nem chamada de API. A inferência em lotes levou aproximadamente 2,5 segundos nesta máquina; isso não mede latência de atendimento ou trabalho humano poupado.

Resultados: 1.114 divergências entre sugestão e rótulo, 305 com score ≥ 0,61. A concordância global de 97,67% inclui 45.790 exemplos de treino e não foi promovida a acurácia independente. O teste original reproduziu 688/800 (86%); continua assistido, com 44 divergências entre os 658 acima do limiar. [Relatório, JSON e predições por linha](../solution/reports/full-population/report.md). A tarefa não mede intenção, sentimento, elegibilidade ou resolução.

Foram adicionados 12 testes para rejeitar sobreposição/duplicação/omissão de partições e divergência da avaliação histórica; **216 passaram localmente e no Docker**. As execuções repetidas durante a elaboração do relatório preservaram as mesmas predições. Houve um aviso de depreciação de dependência do cliente de testes, sem falha. Nenhuma implementação de atendimento foi alterada nesta retomada.

README, PR e roadmap foram alinhados aos três caminhos atuais. O [roteiro de fechamento](../docs/entrega.md) reúne as respostas ao diretor, matriz do que funciona/foi medido e uma demonstração de cerca de dez minutos. A avaliação semântica em amostra nova e o piloto operacional continuam pendentes; não foram apresentados como concluídos.

## Evidências finais locais, sem VPS — 22/09/2026

Dhiego reforçou que o protótipo não será hospedado na VPS: executar localmente, capturar telas e versionar no process log. Codex reconstruiu/iniciou o Docker local e registrou **sete screenshots**, com sequência de conclusão/falha/revisão, investigação, economics positivo/negativo, classificador e resumo. [Índice e roteiro das evidências](evidencias/entrega-local-2026-09-22/README.md).

Nesta rodada, extração por IA e recap ficaram desativados para demonstrar a reprodução sem API; as evidências anteriores de chamadas reais e mobile foram preservadas separadamente. O conteúdo aprovado foi editado para confirmar a persistência; são interações de QA de Codex, não decisões novas de Dhiego. A inspeção visual das dez capturas confirmou os estados apresentados. A primeira captura de página completa mostrou o cabeçalho fixo sobre o conteúdo após rolagem; a página foi reposicionada no topo e recapturada, sem editar a imagem.

Commits continuam locais. Sem deploy, push, fork ou PR nesta etapa. Próximo passo: revisão final do pacote com o candidato e, após esse fechamento, publicação da submissão pelo canal oficial.

## Clareza sobre IA, regras e humano — 22/09/2026

Dhiego pediu que a entrega explicitasse onde a IA entra em cada fluxo, por que não usar IA para tudo e onde código determinístico, classificador local e decisão humana assumem. Codex acrescentou na abertura de `/fluxos` a matriz visual: IA opcional interpreta intenção/tentativas/sinais com citações; modelo local sugere categoria; consultas e regras determinísticas decidem elegibilidade, token, transição e bloqueio; humano aprova resposta e investiga exceções.

A [matriz completa](../docs/onde-entra-ia.md) registrou inicialmente escolhas negativas: não modelar sentimento, urgência, churn, SLA, ações reais de conta ou LLM sobre toda a base sem referência humana. Os motivos variam entre risco, ausência de dados/rótulos, falta de integração e custo sem avaliação válida. Não se acrescentou uma capacidade de IA apenas para demonstrar uso da tecnologia.

A documentação do README, roteiro de entrega e proposta de três caminhos foi alinhada. A captura [Matriz de decisões](evidencias/entrega-local-2026-09-22/08-matriz-ia-regras-humano.png) foi feita no Docker local, sem chamada de IA, e verificada sem overflow horizontal. Os 219 testes permanecem passando. O detector visual sinalizou textos pequenos preexistentes no cabeçalho e na ajuda do checkbox; os novos marcadores foram ajustados para 11px. Nenhuma alteração externa, deploy ou chamada paga ocorreu nesta etapa.

## Revisão — temperatura, prazo e SLA como sinais assistivos

Dhiego observou corretamente que sentimento, urgência e SLA não devem desaparecer apenas porque a base não permite validá-los como métricas. O recorte foi corrigido: `/fluxos` agora mostra **temperatura de atenção** e **menção de prazo/urgência** com as citações literais que os sustentam. O sinal não muda prioridade, não presume que o cliente está tranquilo quando ausente e não decide ação; ele chama o atendente para confirmar contexto, impacto e prazo.

O estado de SLA também passa a aparecer no fluxo: a demonstração afirma que não é calculável e nomeia o que falta (abertura, política de prazo, primeira resposta e relógio operacional). Assim, o produto não transforma `urgent` em “SLA violado”, mas deixa visível o dado que uma operação real precisaria instrumentar. Churn, nota de sentimento e priorização automática continuam fora de escopo decisório por ausência de referência/histórico adequado.
