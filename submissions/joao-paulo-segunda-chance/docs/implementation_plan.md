# Plano de implementação — aprovado

Estado atual em 13/10/2026: fundação, site, importador, decisões, login, assistente e gestão de usuários implementados. Concluí a aceitação do login e a revisão visual. A PR aguarda minha autorização. O plano abaixo conserva as propostas e critérios da etapa inicial; os contratos finais estão em [status da aplicação](web_status.md) e [reprodução](reproduction.md).

## Escopo e destino

- Produto: site executivo de diagnóstico, decisões e acompanhamento, atualizado por CSV/Excel.
- ML não é o diferencial nem o fundamento da priorização operacional.
- Repositório atual: `amadojoao2/ai-master-challenge-segunda-chance`, fork direto do repositório oficial. [Transferência](../process-log/README.md#transferência-para-o-fork-oficial--13102026).
- Branch: `submission/joao-paulo-segunda-chance`, baseada na `main` oficial `4aed364d572fabe0f1fff1f0c6f32960b30fe575`.
- Todo arquivo de entrega permanece em `submissions/joao-paulo-segunda-chance/`.
- Não abrir PR nem solicitar revisão até a entrega estar completa e eu autorizar o envio.
- Supabase de destino: `challenge_g4_projeto`, conexão `challenge_g4`.
- Estado na aprovação inicial: auditoria e fundação implementadas, com primeira versão publicada. Site e importador foram concluídos nas etapas seguintes.

## Arquitetura: monólito modular

Não criar microserviços por contexto. Definir contextos e suas interfaces antes da persistência.

| Bounded Context | Agregados/objetos | Casos de uso | Limite |
|---|---|---|---|
| Ingestão e Qualidade | Importação, Arquivo, Contrato, Ocorrência | Preparar, validar, resolver conflito, publicar | Não calcula risco ou decide ação comercial |
| Contas e Assinaturas | Conta, Assinatura, Intervalo, Valor monetário | Consultar carteira contratual e cadastro | Não interpreta churn histórico como status automático |
| Produto e Suporte | Registro de uso, Ticket, Medida, Cobertura | Agregar atividade e atendimento | Preserva ausência/indisponibilidade e incoerência temporal |
| Retenção e Diagnóstico | Definição de indicador, Execução, Snapshot, Evidência | Reconciliar, segmentar, diagnosticar | Não afirma causalidade ou receita perdida sem vínculo |
| Decisões e Execução | Decisão, Ação, Histórico | Aprovar, atribuir, concluir, registrar resultado | Consome evidências publicadas; não recalcule indicadores |

Camadas: domínio puro → aplicação/orquestração → adaptadores de persistência/processamento → apresentação. Dependências externas apontam para interfaces da aplicação; o domínio não importa Supabase, pandas ou componentes de tela.

Reaproveitar linguagem, critérios, testes e padrões da primeira solução mediante revisão. Não copiar pesos ou limites arbitrários como se fossem validados. A auditoria Python desta rodada é uma ferramenta independente de investigação. As regras de referência em `domain/` e seus testes servem como contrato inicial; a escolha final do runtime do site virá com a implementação para não manter duas implementações oficiais das mesmas regras.

## Camadas de dados

| Camada | Tabelas propostas | Granularidade e responsabilidade |
|---|---|---|
| ingest | import_batches, import_files, raw_rows, quality_issues, source_contracts | Lote, arquivo, linha original, ocorrência, contrato versionado |
| core | accounts, subscriptions, feature_usage, support_tickets, churn_events | Registro tipado de fonte por versão; sem dedução de fatos ausentes |
| analytics | dataset_versions, version_sources, analysis_runs, account_snapshots, metric_results, evidence_items | Manifesto de fontes, execução, conta/data, resultado e sua proveniência |
| operations | decisions, actions, action_history | Decisão e ações com evidência/versionamento imutáveis |
| access | memberships | Identidade e função definidas pelo servidor |

Os nomes são proposta. Criar migrações somente após aprovação da fundação. Interfaces públicas ficam restritas ao necessário. Tipos financeiros `numeric`, IDs externos `text`, datas `date` ou timestamps com precisão original. Fuso ausente não será inventado.

Chaves canônicas compostas incluem versão e ID externo; foreign keys também incluem a versão para impedir associações entre bases incompatíveis. `usage_id` NÃO é chave única confiável nesta base: usar ID interno com vínculo à linha original, preservando o ID de origem. Colisões conflitantes precisam de resolução explícita antes de usar uma identidade de evento única. Não inventar conta/assinatura pai para contornar órfãos.

Não impor foreign key que contradiga a fonte e depois apagar os registros que falharam: registros inválidos ficam no raw e em ocorrências; promoção canônica/analítica é qualificada por regra. Churn sem evento preservado no cadastro, sem evento sintético. Conflitos e limitações ficam disponíveis na interface de qualidade.

## Ingestão e publicação

1. Upload privado do arquivo original, hash, nome, aba, usuário, horário e contrato.
2. Parse em ambiente controlado; detectar separador/encoding e exigir mapeamento quando ambíguo. CSV/Excel não confiáveis não executarão fórmulas, macros ou código. `.xlsx` é o formato Excel inicial.
3. Staging com valores originais e tipos normalizados; ausência distinta de zero/falso.
4. Validar campos obrigatórios, tipos, identidade, relacionamentos e regras temporais.
5. Preview de inclusões, mudanças, conflitos, rejeições e efeito em indicadores.
6. Confirmar modo: substituição completa da fonte ou atualização parcial por chave. Ausência em atualização parcial não significa exclusão.
7. Formar manifesto com versões exatas das cinco fontes; distinguir dados novos de fonte ainda não atualizada.
8. Executar análise em versão candidata; verificar reconcilições e publicar ponteiro para versão completa em transação curta.
9. Retomar processamento interrompido sem duplicar efeitos. Falha mantém a versão publicada anterior.

Versões imutáveis podem reutilizar versões de fontes não modificadas; não precisa duplicar todos os dados em cada publicação. Decisão aponta para evidência imutável, execução analítica, parâmetros/versão da regra e manifesto das fontes. Nova carga nunca apaga contexto histórico de decisões.

Hash idêntico identifica arquivo idêntico; hash de registro normalizado identifica reapresentação semântica sob o mesmo contrato. Uma atualização parcial de `usage_id` conflitante fica bloqueada até resolução de identidade. Manter arquivamento/retenção de arquivos e limite de upload configurados. Processar por lotes; volume maior vira job com progresso e tentativas, sem prender uma requisição longa.

## Política de qualidade e evidências

Três classes: erro objetivo (ex.: ID duplicado com conteúdo diferente), reconciliação (ex.: cadastro x histórico) e limitação (ex.: cobertura de respostas). Contagens podem se sobrepor. Zero ocorrência em um teste não comprova qualidade de toda a fonte.

Separar duas perspectivas:

- Fonte como recebida: contagens, motivos declarados, cobertura, divergências e qualidade, sempre com contexto.
- Análise qualificada: populações e fatos elegíveis para uma pergunta e data específicas, informando excluídos e impacto da seleção.

Não excluir registros temporalmente incoerentes em silêncio e apresentar a população restante como representativa. A análise de sensibilidade deve mostrar quantidade de linhas e contas preservadas por política. Dados sem sustentação suficiente geram tarefa de validação/qualidade, não alerta automático de retenção.

Cada resultado de Specification inclui estado `atendida/não_atendida/indeterminada`, versão, parâmetros, evidências e limitações. Composição AND/OR/NOT precisa de lógica explícita para desconhecidos. Pesos de receita não alteram diagnóstico de saúde; exposição financeira e urgência ficam separadas.

## Indicadores e semântica temporal

- Flag cadastral é observação recebida, sem data individual de alteração. Evento é ocorrência datada; não são a mesma definição.
- Contas com flag de churn e histórico ausente permanecem no cadastro; data/motivo/perda não inferidos.
- Eventos com contratos abertos e sem vínculo a assinatura não provam perda de toda a receita da conta.
- Churn mensal por conta exige episódio e população em risco demonstráveis. Não usar soma de eventos / todas as contas como taxa oficial.
- MRR contratual: contratos elegíveis na data; ARR anualizado não é caixa recebido. Assinaturas simultâneas precisam de interpretação explícita; não supor que cada linha substitui a anterior.
- Receita efetivamente perdida: só calculada quando vínculo e evolução contratual sustentam o cálculo. Caso contrário mostrar exposição/receita associada e cenários, com hipótese declarada.
- Intervalos [início, término) são convenção proposta: registros na data de término mudam com a convenção. Não converter convenção em fato documental.
- Uso: janelas consecutivas de igual duração, cobertura mínima explícita, ausência distinta de zero e baseline positivo para queda relativa.
- Erros/uso é razão entre contagens; pode superar 100% e não é probabilidade sem confirmação da semântica.
- Suporte: resposta, resolução e satisfação só entram em cortes históricos quando sua disponibilidade for demonstrável. Usar `closed_at` como limite conservador de resolução; datas de resposta e avaliação ausentes são limitações, não fatos reconstruídos.
- Exibir média/mediana e tamanho da amostra/cobertura; Notas ausentes não são notas zero.
- Planos, seats e flags comerciais sem histórico de mudança não serão retroprojetados como atributos conhecidos em toda data passada.
- Maior data observada não comprova completude. Mostrar período observado, corte analítico e cobertura declarada. A base é histórica; o período efetivo deve ser mostrado no painel.

## TDD e verificação

Na primeira rodada, 11 cenários de regra foram escritos antes da implementação e a execução inicial falhou por módulo inexistente. Depois foram implementadas regras mínimas e os 11 passaram. A auditoria exploratória foi desenvolvida a partir das inspeções; seis testes de integração foram acrescentados depois. Não apresentar esses seis como TDD anterior ao código.

Próximos testes ANTES dos casos de uso correspondentes:

- Contratos de upload: tipos, abas, mapping, vazio x zero, campos obrigatórios, CSV malformado.
- Idempotência e conflitos: arquivo repetido, registro reapresentado, IDs diferentes ou conflitantes.
- Versionamento: retomada, falha no meio da carga, rollback, substituição/atualização parcial.
- Não multiplicação de MRR ao cruzar fatos em granularidades distintas.
- Corte temporal, janelas iguais, cobertura e valores indeterminados.
- Política de publicação e elegibilidade de evidência por indicador.
- Decisões: transições permitidas, responsável/prazo e preservação da evidência após atualização.
- Segurança: usuários/perfis distintos e negação explícita, inclusive acesso a arquivos.

## Segurança — evolução do plano

Na etapa inicial, aprovei acesso livre, sem login por e-mail/senha. Sessões anônimas autorizam operações limitadas ao workspace; autor/responsável declarados, sem confirmação de identidade. RPCs privilegiadas permanecem apenas no backend, RLS habilitado e arquivos originais privados em bytea no Postgres. Naquele plano, autenticação, papéis e Storage eram evoluções futuras. Autenticação e papéis foram posteriormente implementados; [modelo atual](authentication.md). Nenhum segredo privilegiado no frontend, Git ou relatório. Revalidar projeto de destino antes de migração. Aplicação e schema só serão alterados no projeto dedicado `challenge_g4_projeto`.

## Sequência e critérios de aceite

| Etapa | Entrega | Critério para avançar |
|---|---|---|
| 0 — concluída | Auditoria reproduzível, testes iniciais, plano e registro de processo | GitHub confirmado; sem PR e sem alteração do Supabase |
| 1 — fundação | Contratos, modelo lógico/físico, migrações, RLS, testes e carga preservada | Contagens reconciliadas; nenhuma correção silenciosa; políticas verificadas |
| 2 — diagnóstico | Snapshots, indicadores, evidências e análises de sensibilidade | Números reproduzíveis e limitações explícitas; cada conclusão vinculada a fonte |
| 3 — atualização | Upload CSV/Excel, validação, preview e publicação de versões | Ciclo completo de atualização e falha testado; painel anterior preservado |
| 4 — decisões | Site executivo, detalhe da conta/evidência, decisão/ação e acompanhamento | Decisão persistente e evidência preservada após nova carga |
| 5 — entrega | README oficial completo, demonstração e Process Log com exports | Testes finais, diff restrito à pasta e autorização para abrir PR |

O site começa pelas perguntas do CEO: o que mudou, onde a perda se concentra, como interpretar uso e satisfação, que ação é sustentada e qual resultado deve ser medido. O acabamento visual ocorrerá depois da sustentação analítica. Uma lista de contas pode recomendar validação de cadastro, revisão de suporte ou investigação de adoção; não precisa alegar probabilidade de churn.

## GitHub e revisão

Versionar mudanças concluídas e verificadas nesta branch, sem segredos e sem alterações fora da pasta. Preservar a PR #66 como histórico independente. Não criar issue, comentário, pedido de review ou PR como parte do desenvolvimento. A futura PR terá título `[Submission] João Paulo — Challenge 001 (Segunda Chance)` e base `main` oficial quando eu autorizar o envio.


## Situação após a fase web

Etapas 1–4 implementadas e verificadas; revisão visual concluída em 13/10/2026. Diagnóstico, atualização por fonte e decisões estão no site publicado. A publicação do pipeline foi testada integralmente em transação revertida; painel ativo original preservado. Ver [status e limites da aplicação](web_status.md). A aceitação posterior publicou uma segunda versão por HTTP sem mudar fatos, testou componentes e decisões e corrigiu erros de UX/API. A etapa 5 tem narrativa/Git e README conferidos; revisão visual concluída e autorização para a nova PR ainda pendente.
