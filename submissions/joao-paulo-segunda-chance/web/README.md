# Mesa de decisão RavenStack

Site: https://challenge-g4-ravenstack.early-hake-5665.chatgpt.site

Frontend React/TypeScript; regras de importação puras; adaptador Supabase Edge; Postgres com fontes, versões e evidência imutáveis. Os arquivos aqui não contêm dados de contas nem chaves privilegiadas. O endereço do site é público; o painel e suas APIs exigem login.

[Roteiro consolidado de reprodução e demonstração](../docs/reproduction.md).

## Frontend local
Node >=22.13.

```sh
cd web/frontend
npm ci
npm run check
npm run test:ui
npm run build
npm run dev
```

O adaptador `lib/api.ts` aponta para o ambiente dedicado. Trocar URL e chave publishable ao reproduzir em outro projeto. Chamadas usam JWT de usuário e chave publishable pública; não configure service_role no frontend. A versão hospedada usa o starter Vinext de Sites com as mesmas telas e CSS. Este frontend Vite é portável e independente da hospedagem.

## Banco e Edge
Aplicar as migrações da fundação na ordem documentada em [foundation_status.md](../docs/foundation_status.md), carregar as fontes e depois aplicar:

1. `db/web_application.sql`
2. `db/web_account_detail.sql`
3. `db/analysis_materialized.sql`
4. `db/web_parse_reuse_guard.sql`
5. `db/web_conflict_response.sql`
6. `db/decision_scopes.sql`
7. `db/authentication.sql`
8. `db/authenticated_upload_ownership.sql`
9. `db/authentication_api_boundary.sql`
10. `db/assistant.sql`
11. `db/assistant_context_catalog.sql`

A migração `db/assistant_integration_checks.sql` e o probe são verificação administrativa opcional, não requisito para operar o assistente. Gerar `node scripts/build_assistant_edge.mjs --output .work/assistant-edge/index.js` e implantar como `challenge-assistant`, verify_jwt=true. Configurar o Secret e os perfis conforme os guias vinculados.

Gerar os pacotes com `node scripts/build_web_edge.mjs --output .work/auth-web/index.js` e `node scripts/build_decision_edge.mjs --output .work/auth-decision/index.js`. Implantar cada `index.js` em `challenge-auth-web` e `challenge-auth-decisions`, respectivamente, com verify_jwt=true. `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` são internos do ambiente Edge, nunca parâmetros de navegador. Os antigos `challenge-web`/`challenge-decisions` representam a fase de acesso livre; após ativação, suas rotas de dados ficam bloqueadas. Ver [configuração e aceitação](../docs/authentication.md).

`contracts.mjs` é gerado do registro Python `domain/source_contracts.py`. O teste de equivalência impede divergência silenciosa na referência. Ao mudar contrato/regra, atualize versões e testes nas duas linguagens.

## Testes

```sh
node --test web/tests/*.test.mjs
python web/tests/http_auth.py --guards-only --legacy-blocks
```

O teste de referência requer `CHALLENGE_DATA_DIR` com CSVs originais e `CHALLENGE_AUDIT_REPORT` com o relatório do auditor Python. Dados não são incluídos no GitHub. `--legacy-blocks` exige autenticação já ativada. Os scripts HTTP antigos de importação, decisões e leitura abaixo representam a aceitação anterior ao login; não estão adaptados para JWT e devem falhar contra o acesso antigo após ativação. Para leitura/opções/logout com uma conta real, usar `http_auth.py --email EMAIL --expect-role administrator` (ou `super_admin`/`user`), com senha solicitada localmente por getpass. Concluí a aceitação completa do login em 13/10/2026; os scripts antigos continuam sendo evidência histórica, não uma suíte JWT atual.

O teste HTTP de Excel requer `python -m pip install -r requirements-web-tests.txt`.

`http_import.py --accounts-csv /caminho/ravenstack_accounts.csv` inspeciona Excel, bloqueia CSV inválido e cria uma prévia, sem publicar. O teste `tests/db_web_import_rollback.sql` valida a publicação inteira dessa prévia e reverte a transação. Não execute a opção `--publish` sem autorização específica para a atualização real.

## Limites
Ver `docs/web_status.md`: substituição completa de uma fonte por vez, limites de arquivo, identidade autenticada nas novas operações, histórico declarado preservado, armazenamento de originais em Postgres e ausência de QA visual automatizado neste ambiente. Não há modelo de ML, alerta preditivo nem inferência causal.

## Aceitação de componentes e HTTP

`npm run test:ui` testa 47 casos de componentes e contratos de adaptadores usando Happy DOM 21.0.1 e API/Auth simulados. Não executa navegador real nem valida CSS/viewport visualmente. Arquivos temporários em `tests/.generated` são ignorados.

O ciclo efetivo `http_import.py --accounts-csv /caminho/original.csv --publish` foi autorizado e concluído em 12/10/2026, preservando os fatos e criando a segunda versão. `http_decisions.py --write-qa` grava uma decisão claramente marcada `[QA]` e conclui sua ação. Não rodar os testes de escrita sem intenção explícita de persistir esses registros.

A revisão concorrente usa SQLSTATE PT409/HTTP 409. Não usar 40001 para erro de negócio: a aceitação real mostrou retries/timeout que não apareciam no teste SQL isolado. Ver Process Log de aceitação.


## Escopo das decisões

O formulário novo permite conta, segmento por setor/país, carteira e qualidade, com dado principal, prévia de backend e evidência/membros congelados. Ver [contrato e estado](../docs/decision_scopes.md). Migração aplicada e adaptador publicado como JavaScript gerado em 12/10/2026, após erros internos no empacotamento TypeScript.

Os fontes de decisões são `web/decisions/index.ts` e `web/domain/decision_scope.mjs`. Atualmente, o pacote gerado é implantado em `challenge-auth-decisions`; o frontend mantém a sessão/importação/leitura em `challenge-auth-web`. Os dois verificam JWT e identidade com o mesmo runtime interno, sem chave privilegiada no frontend. O empacotador usa regras canônicas sem cópia manual nem segredos.

Na fase anterior ao login, `python web/tests/http_scopes.py` validava quatro escopos, agregações e bloqueios, sem gravar decisão. O script usa a API antiga e não deve ser utilizado como smoke test autenticado atual. `--write-qa` persiste um registro de QA e conclui sua ação. Os testes de leitura e `--write-qa` passaram em 12/10/2026; a ação QA foi concluída e a interface publicada após a aceitação.


## Login — ativo

O frontend usa @supabase/supabase-js 2.117.2 e os adaptadores `challenge-auth-web`/`challenge-auth-decisions`. `npm ci` usa o lockfile. Site v10 publicado e login exigido; duas contas existentes vinculadas a superadministrador protegido e administrador. Novos usuários recebem permissões explícitas, senha inicial direta e troca obrigatória. O módulo usa `challenge-users`, sem SMTP, mantendo o plano Free. [Guia de gestão](../docs/user_management.md), incluindo migração posterior ao assistente, empacotador e testes SQL locais. Migrações, pacotes e registro de aceitação em [authentication.md](../docs/authentication.md).

`python web/tests/http_auth.py --guards-only --legacy-blocks` testa sete rejeições HTTP, sem cadastrar/gravar dados de negócio. `tests/db_auth_activation_guards.sql` verifica ativação, elegibilidade dos dois perfis, bloqueio da criação de sessão antiga e privilégios administrativos com rollback. Login de conta real é interativo por getpass. Concluí a aceitação completa do login e a revisão visual em 13/10/2026. Testes com Auth simulado têm escopo separado. `local_db_auth_access.sql` é fixture local isolada, não executada aqui. Testes HTTP anônimos antigos são evidência histórica.

## Assistente executivo

Sétima área, com histórico privado e consultas calculadas no banco. Migrações `db/assistant.sql`, `db/assistant_context_catalog.sql` e `db/assistant_prompt_hardening.sql`; pacote `scripts/build_assistant_edge.mjs`; gateway challenge-assistant com JWT exigido. A versão endurecida separa dados importados das instruções, usa respostas fixas para esclarecimentos e não faz segunda geração de explicação. O servidor confere nomes explícitos de setor/país antes da consulta SQL e pede esclarecimento quando o filtro da ferramenta diverge ou a pergunta cita mais de um nome da mesma dimensão. [Registros de segurança](../process-log/assistant_security_2026-10-13.md) e [filtros](../process-log/assistant_filter_guard_2026-10-14.md). `node --test web/tests/assistant.test.mjs` testa Specs; suíte frontend tem 47 casos de componentes e adaptadores simulados. `tests/db_assistant.sql` requer sessão real existente e usa rollback, sem Auth fictício. `python web/tests/http_assistant.py` testa bloqueios anônimos. [Contratos, limites, Secret e validação](../docs/assistant.md).

## Gestão de usuários

`web/users/index.ts` + `web/domain/permissions.mjs`, pacote `node scripts/build_users_edge.mjs --output .work/users/index.js`, função `challenge-users` com JWT. Aplicar `supabase/migrations/20261013140604_user_management.sql` após todas as migrações anteriores e republicar o assistente. `python web/tests/http_users.py` confere quatro bloqueios HTTP sem mutação autenticada. Ver [modelo, operação e reprodução](../docs/user_management.md).
