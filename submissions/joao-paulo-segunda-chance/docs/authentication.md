# Login — identidade e ativação

## Estado atual
Site v10: [gestão de usuários](user_management.md) ativa, `amadojoaoborges@gmail.com` superadministrador protegido e `email@raven.com` administrador. Novos usuários têm permissões explícitas, cadastro sem e-mail e senha pessoal obrigatória. Senhas existentes preservadas. O histórico abaixo documenta a ativação original.

Implementados login e-mail/senha, mostrar senha, erros, sessão persistente/renovação, saída local e identificação do usuário. Adaptadores `challenge-auth-web` e `challenge-auth-decisions` ACTIVE v2, verify_jwt=true. **Site v6 publicado e autenticação ativada em 12/10/2026 (BRT)** após confirmar as duas contas que criei e associar administrador e usuário ao workspace. Na ativação original, ambos acessavam todas as funções. As duas versões de dados e três decisões QA anteriores foram preservadas. Bloqueios HTTP e SQL verificados. Concluí a aceitação completa do login em 13/10/2026. Ver [evidência da ativação](../process-log/authentication_activation_2026-10-12.md).

## Modelo
- Supabase Auth administra credenciais. Aplicação não tem tabela de senha nem credenciais no código.
- `access.memberships`: usuário, workspace, papel, ativo, nome de exibição, permissões, revisão e obrigação de trocar senha. `administrator` aparece como Administrador; `decision_maker` como Usuário com permissões explícitas. O proprietário é identificado por `access.super_admins` e retorna `super_admin`. O perfil é verificado no servidor, não vem de user_metadata.
- `access.web_sessions`: vínculo ao usuário/sessão Auth/workspace, validade e revogação. Sem FK para auth.sessions porque logout remove a sessão e o histórico deve continuar.
- Novo autor em decisões, histórico de ações e uploads preenchido pelo backend/trigger; import_batches registra ator da atualização. Registro anterior não recebe usuário fictício/retroativo.
- Upload autenticado pertence ao usuário, permitindo retomada após novo login. Jobs anônimos anteriores não são atribuídos automaticamente a alguém.

## Acesso
SDK @supabase/supabase-js **2.117.2**, pin e package-lock. Chave publishable pública no cliente. SDK mantém/renova sessão no navegador; frontend não renderiza dados protegidos no servidor nem compartilha cliente Auth entre requests SSR.

Toda chamada aos novos adaptadores envia JWT do usuário. Além do verify_jwt da plataforma, o gateway verifica usuário pelo Auth, confere sujeito/sessão/expiração, exige sessão Auth existente e associação ativa. HMAC com segredo interno deriva sessão operacional estável durante refresh; nunca é entregue ao navegador. RPCs e tabelas da aplicação ficam exclusivamente no backend, inclusive os antigos caminhos de leitura preparados, para não contornar revogação. Não usar security definer para resolver permissões.

Logout revoga a sessão operacional e encerra a sessão Auth local, preservando outras sessões do usuário. Revogação/associação inativa impedem novas chamadas. API só tenta um refresh diante de 401; não recria capacidade anônima nem entra em loop. Autor do formulário é somente leitura; o backend ignora a autoria informada pelo browser e identifica a conta. Isso identifica a conta autenticada, não verifica identidade civil.

## Migrações e pacotes
Depois das migrações anteriores:
1. `db/authentication.sql`
2. `db/authenticated_upload_ownership.sql`
3. `db/authentication_api_boundary.sql`
4. Depois de todas as migrações do assistente: `supabase/migrations/20261013140604_user_management.sql`, conforme [guia atual](user_management.md).

```sh
cd web/frontend
npm ci
npm run check
npm run test:ui
npm run build
cd ../..
node scripts/build_web_edge.mjs --output .work/auth-web/index.js
node scripts/build_decision_edge.mjs --output .work/auth-decision/index.js
```

Implantar os dois arquivos gerados como `index.js`, nos nomes `challenge-auth-web` e `challenge-auth-decisions`, verify_jwt=true. As regras canônicas são reutilizadas, isolando módulos e preservando imports npm do leitor Excel. runtime usa SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY internos; não copiar chave privilegiada para o frontend.

## Configuração e aceitação da ativação original
As etapas de cadastro, associação e publicação abaixo já foram executadas neste projeto. Concluí a aceitação completa do login em 13/10/2026. A sequência a seguir registra o bootstrap original; para uma instalação nova, seguir também a migração e o modelo atuais de [gestão de usuários](user_management.md). Não inventar sessão nem substituir essa aceitação por alteração direta no Auth. O estado de self-signup do serviço Auth ainda não foi verificado; não há ferramenta de configuração Auth disponível nesta conexão. Nenhuma conta sem membership ganha acesso ao painel.

1. Usuário escolhe os dois e-mails e configura as duas contas/senhas diretamente no painel Auth do Supabase. Nenhuma senha pelo chat/Git. Contas devem estar confirmadas e ativas.
2. Vincular os dois usuários reais ao workspace RavenStack em access.memberships, com nome e os papéis acima, por operação administrativa. Não é cadastro público no site. Revisar/desativar self-signup no Auth do projeto; nenhuma conta sem membership ganha acesso mesmo se Auth aceitar cadastro externo.
3. Validar os dois acessos com os novos adaptadores. O script abaixo pede senha por getpass local e não grava credenciais. Não enviar senha como argumento, variável compartilhada ou arquivo.

```sh
python web/tests/http_auth.py --email EMAIL_ADMIN --expect-role administrator
python web/tests/http_auth.py --email EMAIL_USUARIO --expect-role user
```

4. Publicar a versão salva e ativar `public.challenge_enable_auth()` na janela de transição. A função original verificava exatamente um administrador e um usuário; após a migração de gestão, exige a conta proprietária protegida ativa e confirmada; não comprova entrada com senha. Neste projeto, criei as contas e a autenticação foi ativada após publicação para permitir sua aceitação no site, sem solicitar credenciais no chat. Conservar a versão anterior para recuperação. Recuperação deve preservar dados/histórico e avaliar explicitamente o acesso, sem reabrir APIs por consequência de uma falha de interface.
5. Conferir login, ambos os perfis, upload/prévia, autoria, logout e bloqueio dos endpoints antigos. Após activation, antigos testes HTTP anônimos são apenas evidência histórica: não devem voltar a passar para acessar o painel.

## Verificação da ativação original / limites
- 20 testes de domínio web, incluindo identidade e comparação dos 89 resultados com Python: aprovados, zero skips.
- 17 componentes em Happy DOM com API/Auth simulados; seis adaptadores com fetch simulado: aprovados.
- TypeScript/build Vite aprovados; pacotes Edge passam node --check e foram implantados.
- Guardas SQL reais com rollback, sem Auth fictício: identidade/sessão desconhecida rejeitadas, ativação incompleta rejeitada e sem efeito, privilégios exclusivos e caminhos alternativos de leitura fechados.
- HTTP real de novos endpoints: leitura/decisões sem JWT, capacidade antiga e JWT inválido rejeitados com 401.
- Advisor anterior à criação das contas sem findings. Após configuração: uma advertência Auth sobre proteção contra senhas vazadas desativada; nenhuma alteração de plano/configuração foi realizada. A documentação oficial consultada em 13/10/2026 restringe a proteção contra senhas vazadas aos planos Pro ou superiores. Confirmei que permanecerei no plano Free; nenhuma mudança de plano foi realizada. [Orientação oficial](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection).
- Teste compartilhado que criaria identidades sintéticas foi recusado pela revisão automática, sem motivo. `tests/local_db_auth_access.sql` é SOMENTE LOCAL ISOLADO, não executado/aprovado nesta rodada. Nada foi criado no Auth.
- Concluí a aceitação integral do login e a revisão visual em 13/10/2026. TypeScript/build Vinext da versão publicada aprovados na preparação; Site v6 publicado; ativação e bloqueios posteriores verificados em SQL/HTTP. `tests/db_auth_guards.sql` contém uma pré-condição de configuração incompleta e representa a preparação; não reexecutar no projeto já configurado. Após ativar, usar `tests/db_auth_activation_guards.sql` e `python web/tests/http_auth.py --guards-only --legacy-blocks`.
- Nenhuma PR/review/issue/mensagem a avaliadores.
