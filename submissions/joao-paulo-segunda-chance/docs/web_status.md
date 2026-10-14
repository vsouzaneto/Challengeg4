# Aplicação web — contrato operacional

Site: https://challenge-g4-ravenstack.early-hake-5665.chatgpt.site

## Estado em 13/10/2026

Site v10 publicado com gestão de usuários, permissões e troca obrigatória de senha inicial. Nesta etapa: 47 testes de interface/adaptadores, SQL isolado e quatro guardas HTTP aprovados. [Registro](../process-log/user_management_2026-10-13.md). A revisão anterior aprovou 89 testes, sem skips. Concluí a aceitação integral do login. Revisão implementada: recuperação do assistente, exploração sem filtros residuais, tickets por conta, leitura executiva, legibilidade e autoria atualizada. A etapa de usuários aplicou migração de acesso e publicou os adaptadores de usuários/assistente; fatos e versões de dados foram preservados. [Registro de implementação](../process-log/review_2026-10-13.md) e [reprodução](reproduction.md). Concluí a revisão visual em navegador/celular em 13/10/2026, incluindo o assistente.

As seções datadas de 12/10 abaixo são evidências históricas; suas pendências de login e revisão visual foram superadas pela minha confirmação em 13/10. Os testes descritos em cada etapa mantêm seu escopo original.

## Escopo autorizado
Acesso com e-mail/senha sobre o Supabase dedicado. Duas contas existentes ativas, superadministrador protegido e administrador, com acesso completo. O novo módulo cadastra usuários com permissões explícitas, sem e-mail, mantendo o plano Free. [Modelo atual](user_management.md). Novas decisões e uploads registram o usuário autenticado; responsável continua sendo informação de negócio declarada. As três decisões QA anteriores preservam autoria declarada. A fase inicial de acesso livre, descrita nas evidências históricas abaixo, foi substituída pela autenticação.

## Acesso e limites
- Frontend nunca recebe service_role. Edge obtém a chave apenas do ambiente Supabase.
- JWT do Supabase no cliente; backend verifica usuário, sessão Auth ativa e membership protegido. Sessão operacional derivada exclusivamente no servidor; capacidades anônimas antigas não permitem acessar o painel.
- RLS em todas as tabelas; RPCs web executáveis exclusivamente pelo backend. Adaptador fixa o workspace RavenStack; não aceita SQL arbitrário, CRUD genérico ou workspace informado pelo navegador.
- Até 30 decisões e 10 arquivos/dia por sessão, 80 arquivos e 500 novas sessões/dia no conjunto. Proteção básica para o challenge, não defesa completa contra abuso distribuído.
- Toda sessão válida pode acompanhar/encerrar ações do workspace. Decisão/história imutáveis. Revisão otimista e fechamento/cancelamento com resultado/motivo.
- Sem exclusão de versões, envio de e-mails ou solicitações de revisão.

## Atualização
1. Inspecionar CSV UTF-8 ou Excel `.xlsx`, selecionar aba e mapear cada coluna.
2. No servidor, validar tipos, cabeçalhos, chaves e FK contra as outras quatro fontes.
3. Reexecutar 89 verificações; apresentar adicionados, removidos, alterados e ressalvas. Diferença de conteúdo inclui formatação da origem, não somente mudanças de negócio.
4. Preservar arquivo exato, mapeamento e linhas; após confirmação criar candidato.
5. Carregar partes de 300 linhas com checkpoints, verificar bytes/hash/contagem, promover, analisar e publicar atomicamente.
6. Se outra versão foi publicada durante o processamento, impedir sobrescrita e exigir nova prévia.

Substitui a fonte inteira; não é append/upsert. Nesta fase não há atualização conjunta de múltiplas fontes. A nova fonte precisa manter os vínculos com as outras quatro. Referência não pode ultrapassar o maior fato observado; término contratual futuro não comprova cobertura futura.

## Arquivos
Até 8 MB, 50.000 linhas, 128 colunas no Excel; expansão ZIP até 64 MB/1.500 entradas. Fórmulas rejeitadas: exportar valores. Um arquivo com os mesmos bytes não é reutilizado se outra aba/mapeamento produzir linhas diferentes; exportar essa aba em arquivo separado para preservar a linhagem. Datas ISO; booleanos true/false. Originais pequenos preservados em chunks `bytea` no Postgres; Storage é evolução futura. O conteúdo raw projetado pelo mapeamento conserva valores da fonte; nomes/colunas originais continuam no arquivo e metadados do mapeamento.

Não existe limpeza automática de previews/candidatos abandonados; monitorar volume. Upload autenticado pertence ao usuário e pode ser retomado após novo login; jobs anônimos anteriores não são atribuídos automaticamente. A retomada entre logins integra a aceitação completa do login que concluí em 13/10/2026.

## Diagnóstico
Recortes por setor/país, pesquisa e ordenação explícita por nome, MRR ou ressalvas. Exploração, sem fila automática de retenção, ML, previsão de perda ou alegação causal de drivers. Referência histórica exibida; recebimento não se confunde com atualização factual.

## Verificação histórica — 12/10/2026
- 26 testes Python da fundação e 12 testes web: contratos, limite de referência e equivalência das contagens/denominadores dos 89 resultados com Python.
- SQL transacional: decisão, idempotência, resultado obrigatório, revisão, histórico e acesso.
- HTTP real: sessão, dashboard, conta, falta de sessão bloqueada, Excel inspecionado, prévia com 500 contas idênticas, CSV com número inválido rejeitado e painel ativo preservado.
- Publicação completa validada em transação revertida: manifesto de cinco fontes, checkpoints, análise, ponteiro atômico, 89 verificações, métricas idênticas, replay e evidência anterior preservada.
- Teste encontrou um plano inadequado em versão recém-promovida: estimativa de uma linha produzia busca de todos os contratos por linha de uso. CTEs materializadas e preferência por hash/merge joins foram limitadas à função analítica. Teste completo passou sob statement_timeout de 15 segundos; sem alterar regras de negócio.
- TypeScript/build do site e do frontend portável passaram. Site publicado em acesso público, conforme minha instrução.
- Advisor de segurança Supabase sem findings; performance aponta índices ainda sem uso em projeto novo, sem erro de segurança.
- Controle de navegador não disponível: QA visual, interação real no browser e screenshots ainda não realizados. Responsividade, foco e teclado foram implementados. A revisão visual foi concluída posteriormente, em 13/10/2026.

## Publicação de teste e revisão automática
A revisão automática bloqueou o teste HTTP com `--publish`, por alterar o ponteiro ativo no ambiente compartilhado. Foi substituído por validação completa em transação com rollback. O painel continua na versão original. A publicação real do site foi autorizada e concluída. Nenhuma PR foi criada.

## Reproduzir
Ver `web/README.md`. Migrações desta fase: `web_application.sql`, `web_account_detail.sql` e `analysis_materialized.sql` e `web_parse_reuse_guard.sql`, depois da fundação. A última contém a versão final das duas iterações de planejamento de consulta aplicadas no ambiente.

## Evoluções
Lote com múltiplas fontes, Storage/filas para grandes arquivos, limpeza/monitoramento e automação de regressão visual. Autenticação/papéis implementados e ativos; login integralmente aceito por mim em 13/10/2026. Revisão visual concluída em 13/10/2026. A abertura da PR aguarda minha autorização.

## Aceitação posterior — 12/10/2026

Autorizei continuar as validações, incluindo atualização efetiva. Uma segunda versão foi publicada por HTTP com as mesmas 500 contas e métricas; a versão anterior e seus snapshots continuam acessíveis. Há duas decisões `[QA]` concluídas, com três entradas de histórico cada; não são decisões do negócio.

Oito testes de componentes passaram: seis áreas, filtros/paginação/busca, foco/Escape, decisão com erro, conclusão com erro visível, retry do detalhe, upload inválido e pausa/retomada. Esse DOM emulado não comprova renderização em navegador real.

A aceitação HTTP encontrou que SQLSTATE 40001 provocava retries na revisão desatualizada. Nova migração `web_conflict_response.sql` usa PT409; Edge devolve HTTP 409. O teste SQL foi reforçado para exigir esse código e o teste HTTP confirmou revisão desatualizada, resultado ausente, idempotência e conclusão. Nenhum backend de teste em loop permaneceu na verificação final.

As narrativas e Git history atendem ao formato de evidência aceito pelo guia. Capturas/export integral são opcionais; a revisão visual foi concluída posteriormente, em 13/10/2026. Ver `docs/submission_readiness.md`.


## Escopo explícito — 12/10/2026

Conta, setor/país, carteira e qualidade implementados no código, com prévia calculada no banco e membros/evidência congelados. Migração aplicada e testes SQL aprovados, com rollback dos fixtures. 18 testes de domínio web (incluindo 89 verificações comparadas), 13 de componentes e quatro de adaptadores passaram. [Detalhes](decision_scopes.md).

O Supabase recusou atualizações Edge em TypeScript com erro interno. O pacote convertido para JavaScript, gerado das mesmas regras canônicas, foi aceito: `challenge-decisions` ACTIVE na versão 1; `challenge-web` permanece na versão 4. A causa interna do erro não foi confirmada.

HTTP real confirmou os quatro escopos, agregações, validações e uma decisão QA idempotente com evidência congelada. A ação QA foi concluída com histórico de três entradas; são três QA concluídas no conjunto, nenhuma aberta. O banco confirmou 79 membros/3 destaques na nova decisão. Dois registros antigos continuam intactos. Site publicado na versão 4 após aceitação, com TypeScript/builds aprovados. Naquela etapa, o QA visual ainda estava pendente; foi concluído em 13/10/2026.


## Login ativo — 12/10/2026

Minha nova orientação substituiu o requisito anterior de acesso livre: duas contas, administrador e usuário, com todas as funcionalidades. Migrações de identidade e autoria aplicadas; novos adaptadores `challenge-auth-web`/`challenge-auth-decisions` exigem JWT. Duas contas confirmadas e dois memberships ativos; autenticação exigida e site v6 publicado. Testes simulados e bloqueios HTTP/SQL passaram; entrada com senha, autoria, renovação, retomada e logout foram posteriormente aceitos por mim em 13/10/2026. Nenhuma senha no chat/Git e nenhuma PR criada. [Detalhes](authentication.md).

## Contexto da visão executiva — 12/10/2026

Site v7 publicado: versão/data e comparação do workspace completo agrupadas antes dos filtros. Espaçamento de 8px entre os dois blocos, sem alterar cálculos ou recortes. TypeScript, build e 23 testes existentes aprovados; naquela etapa, o QA visual ainda estava pendente; foi concluído em 13/10/2026. [Evidência](../process-log/executive_layout_2026-10-12.md).

## Assistente executivo — 12/10/2026

Site v8 publicado com histórico privado, contextos e evidências. Banco e consultas validados; gateway challenge-assistant ACTIVE v5, verify_jwt=true. Trinta e seis testes JS e teste SQL real com rollback aprovados; três bloqueios HTTP reais aprovados. Chave e chamada real GPT-6 Luna validadas pelo servidor com fixture sintético; conversa no navegador e QA visual ainda não registrados naquela etapa. Concluí a revisão visual em 13/10/2026. [Estado e operação](assistant.md).
