# Process Log — login e identidade (em preparação)

Aprovei e-mail/senha pelo Supabase Auth, com duas contas individuais, administrador e usuário, ambas com todas as funcionalidades. Naquele momento, ainda não havia definido os e-mails. Conferidos Supabase Changelog e documentação de Auth, sessões e headers; SDK oficial 2.117.2 consultado no registro npm e fixado com lockfile.

Escrevi testes de identidade antes do módulo: vermelho por módulo ausente; depois dois casos aprovados. O teste SQL inicial sem alterações no Auth falhou por RPC ausente; migração `authenticated_identity_and_controlled_activation` aplicada, ativação desligada; guardas SQL passaram com rollback. Nenhum usuário foi criado. A ativação exige exatamente um administrador e um usuário comum configurados e confirmados.

A revisão automática recusou um teste transacional que criaria identidades sintéticas em auth.users/auth.sessions, sem fornecer motivo. Não repeti essa escrita no ambiente compartilhado. Fixture fica identificada como exclusivamente local e NÃO executada/aprovada; teste nativo alternativo não cria identidades e verifica rejeição de sessão desconhecida, privilégio e ativação incompleta.

Login, mostrar senha, erro de credenciais, identificação/saída e bloqueio de carregamento do painel foram implementados. Três testes novos falharam antes da tela; passaram após a implementação. Um fechamento incorreto do callback de sessão foi encontrado por TypeScript e corrigido; não foi publicado código com erro. São 16 casos de componentes em Happy DOM, API/Auth simulados; seis contratos de adaptadores passaram. Não equivalem a login real ou revisão visual.

Backend verifica o JWT com Auth antes de interpretar claims, exige associação ativa e sessão existente, deriva identificador interno estável por HMAC e ignora autor/perfil enviados pelo navegador. Senhas pertencem ao Auth; frontend só tem chave publishable pública. Sessão anônima antiga fica bloqueada quando ativar. Novos autores são preenchidos por trigger; os registros antigos ficam intactos.

Dois adaptadores protegidos foram implantados em paralelo aos antigos: `challenge-auth-web` e `challenge-auth-decisions`, ambos ACTIVE v1, verify_jwt=true. Os antigos continuam servindo a versão pública até contas/testes/ativação/publicação finais. Este é preparo controlado, não declaração de que o site atual já exige login.

Ao perguntar quem eram os registros antigos, recebi a conferência: três decisões QA, autor declarado “QA automatizado (sessão declarada)”, sem usuário autenticado, todas concluídas. Não são decisões do CEO.

Pendências: duas contas reais, vínculos de perfil, teste de login/autoria/logout por HTTP, ativação e atualização do site. Nenhuma PR, review, issue ou mensagem a avaliadores.


Verificações finais de preparo: 20 testes de domínio web (incluindo comparação de 89 resultados), 17 componentes e seis adaptadores aprovados; TypeScript/build Vite e sintaxe dos dois pacotes aprovados. HTTP real bloqueou pedidos sem JWT, capacidade anônima antiga e JWT inválido nos novos endpoints. Login válido não foi tentado: não há contas. Advisor de segurança sem findings.

Foi necessário fechar os antigos RPCs de leitura direta e grants de tabelas ao browser: caso contrário, um JWT ainda válido após logout poderia contornar a checagem de sessão do gateway. Migração `authenticated_api_boundary_and_live_session_guards` aplicada; teste de privilégios passou. Origem/histórico permanecem acessíveis pelo backend. Retomada de upload usa usuário autenticado, preservando responsabilidade entre sessões, sem reivindicar jobs anônimos.

Checkpoint do código salvo em `904a888f07cbf612af6be77a91164c25d934f115`, sem PR. O estágio final mantém ativação false, zero contas/memberships e três decisões QA anônimas intactas. Senhas serão configuradas no Auth pelo usuário, fora da conversa. Nova tela ainda não foi publicada.

Também acrescentei um teste de troca de conta: o painel anterior é removido enquanto o novo perfil é conferido, evitando mostrar identidade/dados anteriores na transição. Passaram 17 componentes + seis adaptadores. Mensagem de falha de conexão no login é distinta de credenciais inválidas.

A primeira tentativa de dependência no Sites foi recusada pela política minimumReleaseAge: SDK 2.117.3 publicado há cinco dias. Não alterei/desativei a política. Conferi timestamps no registro npm e escolhi 2.117.2, de 25/09/2026; pin/lockfiles foram atualizados e verificações repetidas. A ausência da dependência impediu o primeiro build Vinext; isso é recuperado após instalação da versão aceita.

Após fixar SDK 2.117.2, os 17 componentes e seis adaptadores passaram novamente, assim como TypeScript e build Vite. TypeScript/build Vinext também passaram. Nova versão do Site será salva sem publicação enquanto as contas reais estiverem pendentes; o acesso público atual permanece ativo.

Fonte Sites do login sincronizado em `2c4ce3c9c12dbffb147db533b44fb6d6690fcf2e`; versão 6 salva sem deploy. Versão 5 continua no ar. Esta pausa depende dos e-mails/contas reais, não de nova aprovação do plano. Nenhum usuário/senha foi inventado.

## Atualização posterior — 13/10/2026

As pendências descritas acima pertencem à preparação de 12/10/2026. As duas contas reais foram posteriormente associadas e o login foi ativado, conforme [registro de ativação](authentication_activation_2026-10-12.md). Em 13/10/2026, confirmei que concluí a aceitação completa do login. O login está concluído. Ver [estado consolidado](README.md) e [gestão de usuários](user_management_2026-10-13.md) para a evolução seguinte.

## Conclusão posterior da revisão visual — 13/10/2026

Concluí a revisão visual em navegador/celular, incluindo o assistente executivo. As pendências visuais acima descrevem a etapa histórica e estão encerradas. Os resultados de testes e seus limites permanecem os observados naquela etapa. Ver [consolidação documental](documentation_review_2026-10-13.md).
