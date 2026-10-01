# Plano de implementação por etapas — Lead Scorer

Criado em **30/09/2026**, a partir do [plano de produto e arquitetura](PLANO_CHALLENGE_003_LEAD_SCORER.md) e do estado atual do repositório. Referência visual existente: [tela principal](tela%20principal.png).

Este documento organiza a execução até a entrega. O plano original continua sendo a referência de requisitos; este arquivo acompanha as etapas, dependências e critérios de conclusão. A implementação foi autorizada posteriormente e executada; o acompanhamento atualizado está abaixo.

## 1. Resultado esperado

Uma aplicação em português na qual o vendedor escolhe sua carteira, recebe até dez prioridades, entende os motivos e a próxima ação, conclui ou adia missões e continua nos lotes seguintes. O estado é recuperado ao recarregar. Os dados são reais, o cálculo é reproduzível e a avaliação declara suas limitações.

**Conclusão do produto:** etapas 0–10 aprovadas. **Conclusão da entrega oficial:** etapa 11 concluída, quando formos executar a submissão. Hospedagem e recursos adicionais são opcionais e não bloqueiam o MVP local.

## 2. Estado e ordem de execução

| Etapa | Objetivo | Dependência | Situação |
| --- | --- | --- | --- |
| 0 | Base do repositório | — | Concluída; revisão visual realizada |
| 1 | Obter e congelar os dados | 0 | Concluída |
| 2 | Ingestão, normalização e qualidade | 1 | Concluída |
| 3 | Motor explicável e congelamento da regra | 2 | Concluída |
| 4 | Regras puras de filas e missões | 3 | Concluída |
| 5 | Estado persistido e calendário diário | 4 | Concluída |
| 6 | Interface Top 10 e ações | 5 | Concluída |
| 7 | Progresso, histórico e sequência | 6 | Concluída |
| 8 | Avaliação histórica final | 3; antes do aceite final | Concluída |
| 9 | Revisão integrada e acessibilidade | 7 e 8 | Concluída |
| 10 | Documentação e pacote reproduzível | 9 | Concluída |
| 11 | Submissão oficial | 10 | Pendente |

Executar preferencialmente na ordem da tabela. A infraestrutura da avaliação pode ser preparada na etapa 3; os resultados finais entram na etapa 8, depois de congelar a regra. Não repetir a criação da base.

### Como acompanhar cada etapa

Ao começar, marcar a situação como **Em andamento**. Ao terminar, registrar os arquivos entregues, comandos executados, resultados e pendências em `../process-log/`, atualizar este plano e o README quando houver mudança de comportamento.

Usar **Concluída** somente com entregas e critérios verificados. Se houver impedimento, registrar o motivo e a próxima ação concreta. Contagens esperadas, resultados de testes antigos e imagens de referência não substituem verificações novas.

Para iniciar uma execução futura, basta pedir: **“Implemente a etapa N do plano em Referencias/PLANO_IMPLEMENTACAO_LEAD_SCORER.md.”** A execução deve incluir implementação, verificações pertinentes e atualização dos registros da etapa.

## 3. Etapa 0 — base do repositório

**Situação: concluída para a estrutura inicial.**

Entregas existentes:

- `solution/` com React, TypeScript, Vite, Tailwind, Vitest e Testing Library; dependências exatas e lockfile.
- Contratos de oportunidades, fatores de score, ações e fila diária; constantes dos dois relógios.
- Calendário operacional e adaptador de armazenamento com fallback para sessão.
- Tela inicial sem dados; diretórios para ingestão, scoring, missões e relatórios.
- `docs/`, `process-log/`, configurações de arquivos e Git inicializado.

Verificação registrada: `npm ci`, sete testes e build aprovados. `prepare:data` executa somente preflight de proveniência/hashes; `evaluate` informa que não foi implementado. Não há CSVs, ranking ou missões funcionais.

**Pendência transferida para as etapas 6 e 9:** revisão visual. O navegador integrado bloqueou o endereço local na criação da base. Evidência: [registro da base](../process-log/bootstrap.md).

## 4. Etapa 1 — obter e congelar os dados

**Objetivo:** ter os arquivos reais e sua origem documentada antes de implementar regras sobre eles.

### Trabalho

- Confirmar na fonte a licença declarada, sua versão e as condições de redistribuição; registrar a verificação em `docs/DATA.md`.
- Obter `sales_pipeline.csv`, `accounts.csv`, `products.csv`, `sales_teams.csv` e, se disponível, `metadata.csv`.
- Preservar os bytes em `solution/data/raw/`; preencher `provenance.json` com fonte, licença, data de obtenção e versão.
- Ampliar o manifesto para incluir todos os CSVs utilizados, inclusive metadata quando presente, e definir uma versão do dataset derivada de seus hashes.
- Escolher a forma de distribuir os dados conforme a licença, garantindo que a execução do avaliador não dependa de uma conta Kaggle ou download em tempo de execução.

### Entregas e aceite

- [ ] CSVs e proveniência disponíveis; licença verificada e documentada.
- [ ] `npm run prepare:data` produz o manifesto com hashes SHA-256.
- [ ] Arquivo ausente, vazio ou proveniência incompleta gera erro compreensível.
- [ ] Fica explícito que este marco verifica arquivos, ainda sem validar joins ou calcular scores.

**Arquivos principais:** `solution/data/raw/`, `solution/scripts/prepare-data.ts`, `solution/data/generated/raw-manifest.json`, `docs/DATA.md`.

## 5. Etapa 2 — ingestão, normalização e qualidade

**Objetivo:** produzir oportunidades ligadas e auditáveis, preservando a cardinalidade.

### Trabalho

- Implementar parser CSV com suporte a campos entre aspas, delimitadores dentro dos campos, BOM e valores vazios; validar colunas, tipos e datas.
- Normalizar campos ausentes para `null`; manter os valores originais necessários à auditoria.
- Aplicar alias explícito `GTXPro → GTX Pro` antes do join de produtos.
- Vincular conta, produto e vendedor sem descartar oportunidades sem conta. Detectar chaves duplicadas e vínculos desconhecidos, distinguindo conta ausente de conta desconhecida.
- Gerar dataset normalizado e relatório de qualidade com contagens, estágios, ausências, aliases, problemas de datas e vínculos.
- Usar unidades corretas: preço de catálogo em USD e receita anual da conta em milhões de USD.

### Entregas e aceite

- [ ] `prepare:data` passa a executar a ingestão completa e gera JSONs determinísticos para os mesmos arquivos de entrada.
- [ ] Testes verificam preservação de IDs/linhas, alias, joins, valores ausentes e entradas inválidas.
- [ ] Para a versão descrita no plano, conferir 8.800 oportunidades, 2.089 abertas, 6.711 encerradas e 1.480 aliases. Se a versão obtida divergir, investigar e documentar; não ajustar artificialmente os resultados.
- [ ] Relatório de qualidade corresponde aos dados realmente processados; conta ausente não vira sinal de desinteresse.

**Arquivos principais:** `solution/scripts/`, módulos puros de ingestão a criar em `solution/src/domain/`, `solution/data/generated/quality-report.json`, `solution/src/data/`, testes de ingestão e `docs/DATA.md`.

## 6. Etapa 3 — motor explicável e congelamento da regra

**Objetivo:** produzir prioridade, motivos e próxima ação a partir do mesmo cálculo.

### Trabalho

- Calcular estatísticas somente de negócios encerrados e conhecidos no corte: taxa global, grupos por produto/setor/conta, contagens e mediana do ciclo.
- Implementar a regra candidata `round(100 × (0,65H + 0,25A + 0,10V))`, com suavização de 20 e pesos históricos 50%/30%/20%.
- Definir e documentar casos sem histórico, mediana zero, preço não positivo, catálogo sem variação e data ausente, mantendo score finito e fallbacks explícitos.
- Separar o contrato do candidato dos resultados usados no histórico e na avaliação. Não usar `close_value`, resultado futuro ou completude como feature do candidato.
- Gerar fatores, contribuições em pontos, amostras, alertas e ações coerentes com Prospecting/Engaging. Ordenar por score e ID estável.
- Preparar variantes sem V e sem A e o mecanismo de cortes temporais. Se houver ajuste de regra, usar somente recortes anteriores ao corte final, verificando antes sua viabilidade nos dados.
- Registrar a regra escolhida, versão e pesos antes da avaliação final de setembro–dezembro. Sem evidência suficiente para ajuste, manter a candidata e declarar a limitação.

### Entregas e aceite

- [ ] Somente abertas recebem score operacional; todas têm score de 0–100, motivos e ação.
- [ ] Explicações conferem com as contribuições; arredondamento é documentado e não é confundido com percentual de chance.
- [ ] Alterar resultado futuro ou receita realizada do candidato não muda o score no corte; fechamentos posteriores não entram nas estatísticas.
- [ ] Amostras pequenas e dados ausentes acionam fallbacks testados. Prospecting não ganha idade ou contato inventados.
- [ ] Mesma entrada, corte e versão produzem o mesmo ranking; regra final registrada antes da etapa 8.

**Arquivos principais:** `solution/src/domain/scoring/`, `config.ts`, `types.ts`, dados preparados, testes de scoring, `docs/SCORING.md` e `process-log/decisions.md`.

## 7. Etapa 4 — regras puras de filas e missões

**Objetivo:** tornar a jornada correta antes de ligá-la à interface.

### Trabalho

- Construir fila diária por vendedor, excluindo Won/Lost, feitos no dia e adiados com retorno futuro.
- Priorizar, no início do dia, os adiados com retorno vencido ou para aquele dia, ordenados por score entre si; depois incluir as demais oportunidades elegíveis.
- Congelar ranking e posição no lote; manter no máximo dez IDs únicos. Selecionar altera apenas `activeOpportunityId`.
- Implementar feito, adiar e desfazer com transições idempotentes. Usar calendário operacional para amanhã.
- Ao esgotar pendentes, carregar o próximo lote, tratando lote menor e carteira vazia. Preservar o total diário.
- Implementar cursor e fila explícita de retornos: desfazer em lote anterior devolve a oportunidade ao próximo lote elegível, sem exceder dez no lote corrente.
- Cobrir também o desfazer quando a carteira já está esgotada, para permitir a retomada da oportunidade devolvida.

### Entregas e aceite

- [ ] Testes cobrem vendedor correto, ordem estável, seleção, até dez itens e exclusões de elegibilidade.
- [ ] Duplo clique não duplica conclusão; seleção e cópia não contam como feito; estágio comercial permanece intacto.
- [ ] Feito e adiar avançam à primeira pendente; próximo lote não repete itens resolvidos naquele dia.
- [ ] Desfazer no lote atual restaura posição; no anterior retorna à fila, sem perda nem duplicidade.
- [ ] Lote final menor, todos adiados, carteira vazia e retorno no dia seguinte funcionam.

**Arquivos principais:** `solution/src/domain/missions/`, contratos de fila/ações e testes de missões.

## 8. Etapa 5 — estado persistido e calendário diário

**Objetivo:** recuperar a rotina e preservar histórico real entre visitas e dias.

### Trabalho

- Integrar o adaptador existente a um store/hook, com validação do conteúdo restaurado e estratégia explícita para versões incompatíveis.
- Persistir seleção de vendedor, fila, cursor, retornos, lote, missão ativa, ações e metas por dia. Ampliar os contratos existentes conforme necessário para manter histórico de múltiplos dias.
- Isolar estado por versão de contrato, dataset e vendedor. Definir como a última escolha de vendedor é recuperada sem misturar carteiras.
- Fixar a meta no início do dia como `min(10, oportunidades disponíveis)`; não reduzir a meta ao adiar itens.
- Reavaliar a data em São Paulo na virada do dia e ao retornar à aba. Restaurar o mesmo lote no mesmo dia; gerar a fila nova em outro dia.
- Usar fallback em memória quando localStorage falhar ou estiver corrompido, com aviso discreto de que os registros da sessão não serão persistidos.

### Entregas e aceite

- [ ] Recarregar restaura o lote, seleção e ações; trocar vendedor e dataset isola os registros.
- [ ] Histórico anterior não é apagado pela renovação diária; adiamentos vencidos retornam corretamente.
- [ ] Corrupção, contrato inválido e armazenamento bloqueado não quebram o app.
- [ ] Virada do dia, inclusive no retorno à aba, não altera a referência histórica do score.

**Arquivos principais:** `solution/src/state/`, `solution/src/domain/dates.ts`, contratos de persistência e testes de restauração/calendário.

## 9. Etapa 6 — interface Top 10 e ações

**Objetivo:** entregar a jornada principal usando os dados e regras das etapas anteriores.

### Trabalho

- Implementar escolha/alteração de vendedor, saudação pelo primeiro nome e carregamento dos dados preparados, com estados de espera, erro e carteira vazia.
- Criar `DailyTopTen`, `MissionCard`, `CompactMission` e `DailyProgress`, seguindo fundo claro, títulos azuis, progresso azul e missão ativa laranja.
- Manter uma missão expandida; pendentes anteriores ficam acima e seguintes abaixo, na ordem original. Posição numérica não muda após concluir outras missões.
- Mostrar conta ou ID/conta não informada, produto, estágio, preço de catálogo, prioridade, fatores em pontos, amostras, limitações e próxima ação.
- Ligar feito, adiar, desfazer e copiar orientação. Exibir feedback para falha de cópia; não mostrar link de CRM sem URL real configurada.
- Mostrar transição de lote e esgotamento da carteira, distinguindo feitas e adiadas. Separar o contador do lote do total de ações no dia.
- Levar foco ao título da missão selecionada e garantir visibilidade com respeito a movimento reduzido. Verificar teclado e celular.

### Entregas e aceite

- [ ] Com dados reais, o vendedor consegue selecionar missão, copiar orientação, concluir, adiar e desfazer.
- [ ] Selecionar a missão 7 mantém as anteriores pendentes acima e as seguintes abaixo; somente um card está expandido.
- [ ] Avançar lotes preserva histórico e informa o tamanho real: “Mais N prioridades · lote X”.
- [ ] Interface usa “prioridade” e “Preço de catálogo”, sem chance de fechamento ou último contato inventados.
- [ ] Revisão visual em desktop e celular registrada; se o navegador integrado continuar bloqueado, documentar a limitação e obter uma verificação real por um meio disponível antes de declarar aceite visual.

**Arquivos principais:** `solution/src/App.tsx`, `components/`, estilos, integração com `state/`, testes de interação e capturas reais em `process-log/screenshots/`.

## 10. Etapa 7 — progresso, histórico e sequência

**Objetivo:** refletir ações reais sem recompensas duplicadas.

### Trabalho

- Implementar segmentos acessíveis para concluída, selecionada, pendente e adiada, com legenda; denominador é o tamanho real do lote.
- Exibir resumos recolhidos de concluídas/adiadas e histórico com possibilidade de desfazer. Conta ausente usa identificação da oportunidade.
- Calcular total diário de conclusões únicas, cumprimento da meta e sequência por datas consecutivas de metas efetivamente cumpridas.
- Recalcular progresso, meta atingida e sequência ao desfazer, inclusive ações de lotes ou dias anteriores quando oferecidas pelo histórico.
- Dar feedback breve ao cumprir a rotina; todos adiados não geram celebração de meta. Histórico inicial e sequência começam vazios.

### Entregas e aceite

- [ ] Completar a mesma ação novamente não soma pontos; adiar, visitar e copiar não cumprem a meta.
- [ ] Novos lotes no mesmo dia não criam dias extras de sequência; dias sem oportunidades não geram conquista.
- [ ] Meta reduzida, como seis oportunidades iniciais, funciona; adiamentos não reduzem essa meta.
- [ ] Desfazer corrige contadores e sequência; estados visuais possuem identificação além da cor.

**Arquivos principais:** funções puras de progresso/sequência em `domain/missions/`, componentes de progresso/histórico, estado e testes específicos.

## 11. Etapa 8 — avaliação histórica final

**Objetivo:** medir o ranking congelado e declarar onde ele ajuda ou falha.

### Trabalho

- Implementar `npm run evaluate` com corte `2017-09-30` e horizonte `2017-12-31`.
- Reconstruir candidatos engajados no corte e ainda não encerrados nele, usando estágio histórico Engaging. Separar completamente seus resultados futuros do contrato de scoring.
- Comparar a regra congelada e variantes já definidas com preço de catálogo, engajamento mais recente e aleatório com seed fixa; usar o mesmo conjunto de candidatos em todos os métodos.
- Gerar métricas por vendedor e resumo agregado com denominadores claros: K=10 principal, K=20/50 quando houver volume; reportar também vendedores com menos de K candidatos.
- Mostrar Won, Lost e censurados no Top K completo; taxa entre resolvidos, lift e captura de Won, tratando denominadores zero explicitamente.
- Documentar viés entre resolvidos, metadados atuais como proxies, ausência de snapshots, Prospecting não reconstruível e política de adiamento não validada pelo backtest.

### Entregas e aceite

- [ ] `evaluate` termina com relatório real e reproduzível, contendo corte, horizonte, regra, seed, cobertura e métricas.
- [ ] Casos sem resultado não viram Lost; testes verificam reconstrução temporal, censura e invariância a futuro.
- [ ] Conferir os recortes esperados do plano para a mesma versão dos dados; divergências são explicadas.
- [ ] Desempenho inferior às referências é reportado. Não ajustar pesos com base no período final; eventual revisão exige protocolo novo e registro do que deixou de ser avaliação independente.
- [ ] `docs/VALIDATION.md` contém resultados e limitações; a interface de método distingue prioridade de probabilidade.

**Arquivos principais:** `solution/scripts/evaluate.ts`, módulos puros de avaliação, `solution/data/generated/evaluation-report.json`, testes e `docs/VALIDATION.md`.

## 12. Etapa 9 — revisão integrada e acessibilidade

**Objetivo:** verificar o fluxo completo e corrigir os casos limite antes de empacotar.

### Trabalho e aceite

- [ ] Percorrer: escolha do vendedor → Top 10 → troca de card → copiar → feito → adiar → desfazer → próximo lote → fim da carteira.
- [ ] Repetir os cenários relevantes após recarregar, trocar vendedor, mudar o dia e simular storage indisponível.
- [ ] Validar lote menor, conta ausente, produto desconhecido, Prospecting, todos adiados e desfazer após esgotamento.
- [ ] Verificar teclado, foco após seleção/conclusão/transição, nomes acessíveis, contraste, progresso textual, movimento reduzido e ausência de rolagem horizontal em celular.
- [ ] Completar “Como priorizamos” com critérios, qualidade e avaliação. Método e histórico devem corresponder ao dataset/vendedor exibidos.
- [ ] Executar testes pertinentes, `npm run typecheck` e `npm run build`; registrar correções e limitações que realmente permanecerem.

**Saída:** checklist de aceite com resultados observados e evidências reais. Nenhum teste precisa alcançar Supabase, n8n ou clientes do CRM.

## 13. Etapa 10 — documentação e pacote reproduzível

**Objetivo:** permitir que outra pessoa execute e avalie a solução sem depender do nosso ambiente.

### Trabalho

- Atualizar README com instalação, comandos, jornada, critérios, resultados, limitações e estado final do projeto.
- Consolidar DATA, SCORING e VALIDATION com os arquivos e resultados realmente produzidos.
- Garantir que `prepare:data` regenere todos os artefatos exigidos pelo app/build e que `evaluate` regenere seu relatório, a partir dos dados distribuídos conforme a licença.
- Testar em uma cópia limpa, contendo apenas os arquivos de entrega, sem `node_modules`, cache, build ou saídas geradas do ambiente de desenvolvimento.
- Organizar decisões, pedidos à IA, verificações, correções, conversas disponíveis e capturas. Registrar tempo efetivo, incluindo a análise prévia, sem reconstruir tempos fictícios.

### Entregas e aceite

Na cópia limpa, a partir de `solution/`, esta sequência deve funcionar:

```sh
npm ci
npm run prepare:data
npm run evaluate
npm test
npm run build
npm run dev
```

- [ ] App usa dados reais e encontra todos os artefatos necessários após esses comandos.
- [ ] Não exige conta Kaggle, credenciais, API ou arquivos externos ao pacote em tempo de execução.
- [ ] README documenta armazenamento local, dois relógios e ausência de atualização do CRM.
- [ ] Jornada e aceite visual/integrado estão verificados; evidências e limitações acompanham o pacote.
- [ ] Nenhuma pendência essencial é escondida como “evolução futura”.

**Marco:** MVP local concluído e pronto para entrega.

## 14. Etapa 11 — submissão oficial

**Objetivo:** montar e entregar a solução no formato oficial descrito pelo plano original.

### Trabalho

- Confirmar nome, perfil GitHub, LinkedIn e prazo recebido no recrutamento.
- Conferir a versão vigente do brief, CONTRIBUTING, guia e template de submissão antes de montar o pacote.
- No fork oficial, preparar `submission/<seu-nome>` e transportar a estrutura para `submissions/<seu-nome>/`, ajustando somente o necessário à embalagem e ao template.
- Repetir a sequência de instalação/preparação/avaliação/testes/build dentro da pasta transportada.
- Revisar o diff: alterações somente na pasta de submissão; sem credenciais, dependências instaladas, caches ou builds indevidos.
- Quando executarmos a entrega, criar o PR no formato oficial e registrar seu link e resultado. Este plano não cria fork, remoto ou PR.

### Entregas e aceite

- [ ] Perfil e documentação final completos; pacote funciona no destino oficial.
- [ ] PR segue título e escopo exigidos pelo regulamento verificado na execução.
- [ ] Evidências reais e limitações acompanham a submissão; link final registrado.

**Marco:** entrega oficial concluída.

## 15. Escopo opcional e prioridades de corte

Somente depois de o núcleo estar aprovado, considerar opções de equipe por gestor/região, exportação CSV correspondente ao recorte, comparação visual de métodos, gravação de demonstração e hospedagem estática. Publicar somente quando essa ação fizer parte da execução solicitada.

IA generativa em tempo de execução, XP, níveis, medalhas, ranking entre vendedores, carteira completa, autenticação, banco e integrações de contato ficam para evoluções posteriores.

Se o tempo apertar, cortar primeiro esses complementos. Preservar dados reais, integridade, motor e explicações, avaliação honesta, Top 10, seleção, feito/adiar/desfazer, lotes, progresso, sequência simples, persistência, acessibilidade essencial e documentação reproduzível. O orçamento de 4–6 horas do plano original é uma referência; registrar o tempo real e conferir o prazo individual, sem prometer conclusão dentro de uma estimativa não medida.

## 16. Registro de avanço

| Data | Etapa | Resultado | Evidência | Próxima ação |
| --- | --- | --- | --- | --- |
| 30/09/2026 | 0 | Base criada; instalação, sete testes e build aprovados; revisão visual pendente | [bootstrap](../process-log/bootstrap.md) | Executar etapa 1 |
| 30/09/2026 | Planejamento | Plano por etapas criado com entregas, dependências e aceite | Este documento | Obter e congelar os dados |

**Produto implementado e verificado.** Publicação privada para revisão confirmada; link no README. A etapa 11 é uma submissão ao recrutamento, separada da publicação, e depende do perfil e do prazo do candidato.

## Atualização após a implementação — 30/09/2026

Etapas 0–10 executadas. Os checklists anteriores preservam o planejamento inicial; a evidência de aceite atual está em [verificação final](../process-log/VERIFICACAO_FINAL.md), [validação](../docs/VALIDATION.md) e no [diário](../process-log/DIARIO.md). O registro inicial da etapa 0 descreve aquele momento, antes da implementação dos CSVs, da avaliação e das missões.

A versão final passou em 31 testes, tipos e build, inclusive em uma cópia sem os artefatos gerados originais. A revisão no navegador inclui desktop/celular, seleção da missão 7, conclusão, adiamento, desfazer e recarregar. Não afirmamos certificação formal de acessibilidade. A submissão oficial não foi enviada.

