# Process Log — aceitação e conferência da entrega

Narrativa parcial e verificável; não é export integral da conversa. Ferramenta de IA: ChatGPT/Codex, usada para decompor testes, implementar casos, diagnosticar falhas, consultar documentação e conferir o brief. Decidi prosseguir com as validações sem abrir PR.

## Instrução humana

Depois de conferir o site, perguntei o que faltava. A resposta listou validação dos fluxos, importação efetiva, responsividade/uso no navegador e documentação. Autorizei continuar e reforcei que a PR ainda não deveria ser aberta. Acesso livre e ausência de ML como diferencial permanecem minhas decisões.

## Conferência oficial

Lidos o brief, submission-guide, template e CONTRIBUTING do repositório oficial. Corrigi uma suposição anterior: narrativa escrita e Git history são evidências aceitas; screenshots/export integral não são cumulativamente obrigatórios. O modelo preditivo é opcional. Acrescentei diagnóstico executivo com números, priorização de investigação e impacto operacional, mantendo não identificáveis causas/perda financeira que as fontes não demonstram. A conferência registra os hashes dos arquivos oficiais em `docs/submission_readiness.md`.

## Testes de componentes

Não há `$control-browser` disponível. A skill Sites orienta: “If `$control-browser` is unavailable, skip browser QA”. O Codex não iniciou preview ou automação de navegador. Usou Happy DOM 21.0.1 para executar componentes React com dados sintéticos e API simulada — explicitamente diferente de QA visual real.

Escrevi testes para seis áreas, recorte, paginação, busca, conta, Escape/restauração de foco, falha em decisão, erro em conclusão, retry de detalhe, importação inválida e pausa/retomada. O seletor inicial de navegação ignorava o contador de ações; corrigi o fixture. Executando a suíte contra o código anterior publicado, dois testes falharam:
- O erro de conclusão aparecia atrás do modal, não dentro dele.
- O detalhe de conta mantinha o estado “carregando” depois de falhar, sem retry.

Com apoio do Codex, implementei mensagem local e preservação do resultado na ação; estado de erro e retry no detalhe. Os oito testes passaram na versão corrigida. O campo de resultado conserva o foco ao digitar. Isso verifica comportamento de componentes, não layout, compatibilidade real de navegador ou viewport de celular.

## Publicação efetiva da importação

`http_import.py` converteu o CSV original de contas em `.xlsx`, inspecionou a aba, validou o mapeamento e confirmou prévia com 500 linhas, zero adições/remoções/alterações. Um CSV com número inválido foi rejeitado. Após confirmação, o processamento em partes foi retomado e publicado. Verificações:
- painel antigo preservado antes da confirmação e durante a carga;
- segunda versão publicada, referência 31/12/2024;
- todas as métricas iguais às anteriores;
- fatos dos 500 snapshots iguais, exceto IDs de snapshot/run;
- repetição de publicação idempotente;
- snapshot anterior continua acessível.

Os fatos não foram modificados para produzir um resultado melhor. Original Excel e manifesto permanecem privados no Supabase; não incluo arquivo/IDs de contas no repositório.

## Decisões e um erro que o SQL isolado não revelou

Uma decisão `[QA]` foi criada por HTTP, repetida com a mesma chave sem duplicação e rejeitada quando a chave foi reutilizada com conteúdo diferente. A ação iniciou corretamente. O teste de revisão antiga sofreu timeout; uma segunda tentativa também. Em vez de continuar repetindo, consultei estado do banco e logs. O backend registrava dezenas de milhares de erros 40001 em dois processos, enquanto a ação permanecia em andamento.

A IA havia escolhido SQLSTATE 40001 como erro de revisão otimista. Isso é inadequado para um conflito de negócio: PostgREST pode tratá-lo como falha transitória e repetir a transação. A consulta oficial confirmou o caso:
- [Troubleshooting Supabase](https://supabase.com/docs/guides/troubleshooting/high-cpu-and-infinite-transaction-retries-when-using-custom-error-codes-in-rpc-functions-77326b)
- [Mapeamento de erros PostgREST](https://docs.postgrest.org/en/v13/references/errors.html)

Com apoio do Codex, reforcei o teste SQL para exigir PT409: falhou no código anterior. A migração `web_conflict_response.sql` e o adaptador Edge passaram a devolver PT409/HTTP 409. O teste SQL com service_role passou. O Codex não encerrou processos arbitrários: os dois PIDs observados já haviam desaparecido na checagem posterior, e a verificação direcionada não encontrou loops de transição remanescentes.

A primeira ação de teste foi concluída sem apagar a história. Uma rodada completa após a correção criou outra decisão `[QA]` e confirmou, por HTTP:
- criação e replay idempotente;
- conteúdo divergente na chave bloqueado;
- revisão antiga rejeitada com 409;
- conclusão sem resultado rejeitada;
- conclusão válida com revisão 2 e três entradas de histórico.

As duas ações `[QA]` estão concluídas; são registros de aceitação, não decisões reais do CEO. Nomes são declarados, sem verificação de identidade.

## Resultado e limites

- 26 testes Python + 12 de domínio web + oito de componentes = 46 testes automatizados nessas suítes, além dos testes SQL/HTTP.
- Publicação efetiva e decisões persistentes verificadas; integridade das versões preservada.
- README/guia conferidos; diagnóstico e cenário operacional documentados.
- A revisão visual em navegador/celular estava pendente nesta etapa; concluí essa revisão em 13/10/2026.
- Código será mantido na branch e pasta da segunda chance. Nenhuma PR, issue, review ou mensagem a avaliadores.

## Julgamento humano e iteração

Defini o diferencial, preservação da reconciliação anterior, acesso livre e envio somente quando pronto. A IA apoiou implementação, mas os testes invalidaram suposições sobre timestamp, desempenho SQL, foco, visibilidade de erros e semântica de SQLSTATE. O processo teve inspeção, testes vermelhos, correções e verificação na aplicação publicada — não um único prompt transformado em produto sem revisão.

## Conclusão posterior da revisão visual — 13/10/2026

Concluí a revisão visual em navegador/celular, incluindo o assistente executivo. As pendências visuais acima descrevem a etapa histórica e estão encerradas. Os resultados de testes e seus limites permanecem os observados naquela etapa. Ver [consolidação documental](documentation_review_2026-10-13.md).
