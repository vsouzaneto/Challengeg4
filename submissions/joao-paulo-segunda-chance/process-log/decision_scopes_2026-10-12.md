# Process Log — escopo de decisão

Registro parcial e verificável de uso de ChatGPT/Codex; não é export integral da conversa.

## Orientação humana
Pedi que “Registrar decisão” permita escolher sobre qual dado decidir, por exemplo conta ou setor. Após o planejamento, autorizei a implementação. Mantidos DDD, TDD, Clean Architecture, Bounded Contexts e Specifications, acesso livre, GitHub contínuo e nenhuma PR antes de nova autorização.

## Desenvolvimento e testes
Escrevi testes de escopo antes do módulo: falharam por módulo ausente; implementei o value object. Testes SQL sintéticos falharam antes da migração por função inexistente. Após aplicar `explicit_decision_scopes_and_frozen_evidence`, passaram, com rollback para não mudar painel/dados nem persistir QA. Testes do formulário anterior falharam para o fluxo novo; foram satisfeitos pela implementação.

Não refiz os critérios temporais: usei snapshots existentes para conta/segmento/carteira. Diferenciei população de casos destacados. Qualidade mantém seu denominador original e não recebe membros inventados. Adicionei prévia calculada no banco, hash recomposto ao salvar, transação com escopo/membros/ação/histórico, proteção da versão ativa e compatibilidade com registros anteriores.

Uma revisão adicional encontrou que JavaScript aceitava `type:['account']` por coerção da chave: novo teste reproduziu a falha e foi corrigido para exigir string. No teste de FK entre versões, o fixture inicialmente reutilizava um snapshot já vinculado e disparava unicidade antes da FK; ajustei para outra conta, comprovando então a FK pretendida. Nenhuma alteração de regra foi feita para esconder falha.

Foram aprovados seis testes do escopo, 13 de componentes, quatro de adaptadores, os 12 testes web anteriores (incluindo comparação de 89 verificações com Python) e o SQL transacional. A suíte Python anterior tinha 26 testes aprovados; não atribuo uma nova execução a esta etapa. Componentes usam Happy DOM 21.0.1, com API simulada; adaptadores usam fetch simulado, não browser nem Supabase real.

Consultas reais conferiram o recorte FinTech (112 contas e 12 casos sem cancelamento), notas ponderadas/cobertura, MRR e uso. Advisor de segurança retornou zero findings; performance apenas índices sem uso. Capacidade/token/chaves e dados por conta não entram no GitHub.

## Falha de publicação e recuperação
A atualização do `challenge-web` retornou `InternalServerErrorException`, “Function deploy failed due to an internal error”, em duas tentativas. A versão 4 permaneceu ACTIVE. Não atribuí causa sem evidência: consulta de logs também falhou no backend.

Separei o adaptador de decisões do importador Excel: três operações fixas, sem pacote externo, usando a mesma capacidade e RPCs restritas. A implantação da nova `challenge-decisions` também falhou. Consultei a documentação oficial e gerei um pacote de arquivo único a partir do mesmo módulo, sem dependências relativas; a tentativa também teve o mesmo erro. Isso não prova indisponibilidade global, erro de sintaxe ou limite de tamanho.

[Guia oficial para esse erro](https://supabase.com/docs/guides/troubleshooting/edge-function-fails-deploy) recomenda CLI com debug/método de bundle alternativo ou suporte. CLI autenticada não está disponível nesta execução. O Codex não extraiu credenciais, abriu ticket ou afrouxou RLS para contornar o bloqueio. O código e o empacotador ficaram revisáveis no fork no commit de checkpoint `e79ed860f61b76b4a6be11bbf709f1a39c002f81`, ainda com publicação pendente.

Depois do checkpoint, converti o pacote canônico para JavaScript com TypeScript 5.9.3, sem imports relativos ou tipos no artefato. Essa estratégia diferente foi aceita: `challenge-decisions` ACTIVE, versão 1. Isso identifica um caminho de implantação funcional, mas não prova a causa interna das falhas anteriores. O empacotador final `scripts/build_decision_edge.mjs` substitui o gerador intermediário Python/TypeScript, mantém um único conjunto de regras e não acessa credenciais/rede.

O adaptador mantém validação, hash da capacidade, RPCs fixas e PT409/401. Não usei endpoint anônimo privilegiado nem enfraqueci RLS. A publicação do frontend fica condicionada à aceitação HTTP do backend efetivo.

## Aceitação e publicação efetivas

`http_scopes.py` passou por HTTP real em modo de leitura: conta, segmento, carteira e qualidade; média ponderada confrontada com os snapshots; escopos inválidos e falta de capacidade bloqueados. Depois, a execução explícita com `--write-qa` confirmou hash inválido/409, criação, replay idempotente, conteúdo conflitante/409, ação iniciada/concluída e igualdade da evidência preservada com a prévia.

Verificação SQL posterior encontrou 79 membros e três destaques na decisão de segmento. São um registro com escopo e dois registros anteriores; três ações QA concluídas, zero abertas. Nenhuma fonte ou ponteiro analítico foi modificado nesta etapa.

TypeScript/builds portável e Vinext passaram. A interface foi sincronizada e empacotada no fonte Sites `c784e3af17183aa3e8be20ab1e2edc866e2f817a`; versão 4 publicada com status `succeeded` em 12/10/2026. Navegador real/QA visual continuam indisponíveis, conforme limite já documentado. Não fabrico screenshots.

## Estado final
Migração e testes SQL concluídos. Formulário/lista/histórico e adaptador implementados. Adaptador JavaScript implantado, aceitação HTTP concluída e site atualizado. A revisão visual, pendente naquela etapa, foi concluída em 13/10/2026. Nenhuma PR, issue, review, ticket ou mensagem a avaliadores foi criada.

## Orientação explícita no formulário

Após usar o site, percebi que o registro só fica disponível depois de “Revisar evidência” e pedi um alerta no formulário. Com apoio do Codex, acrescentei um aviso visível junto ao registro, explicando a etapa e que mudança de seleção/contexto exige nova revisão. Depois da prévia, a mensagem muda para “Evidência revisada. Você já pode registrar a decisão e a ação.” O botão aponta para o aviso com aria-describedby, e a atualização usa aria-live polite. Proteção de registro e regras de negócio preservadas.

Com apoio do Codex, ampliei as verificações do teste de seleção existente para conferir aviso antes/depois da revisão e seu retorno ao trocar o escopo. Os 13 testes de componentes passaram em DOM emulado; TypeScript do frontend portável passou. Naquela etapa, o QA visual ainda estava pendente; foi concluído em 13/10/2026. Alteração solicitada por mim, sem PR.

## Conclusão posterior da revisão visual — 13/10/2026

Concluí a revisão visual em navegador/celular, incluindo o assistente executivo. As pendências visuais acima descrevem a etapa histórica e estão encerradas. Os resultados de testes e seus limites permanecem os observados naquela etapa. Ver [consolidação documental](documentation_review_2026-10-13.md).
