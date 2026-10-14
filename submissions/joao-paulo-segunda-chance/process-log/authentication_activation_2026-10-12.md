# Ativação do login — 12/10/2026 (BRT)

## Pedido e uso de IA
Criei no Supabase Auth duas contas: uma para administrador e outra para usuário comum. O Codex conferiu somente campos de identidade/estado, sem ler credenciais, e associou as contas existentes ao workspace RavenStack. E-mails e IDs pessoais não foram incluídos nesta evidência pública.

## Operações realizadas
- Duas contas confirmadas, não anônimas, não excluídas e não bloqueadas.
- Dois memberships ativos: administrador com nome João Paulo e usuário comum com nome Usuário Raven. Ambos mantêm todas as funções.
- As associações foram gravadas por operação administrativa transacional/idempotente, sem criar identidades fictícias nem alterar senhas.
- Versão já salva v6 publicada com sucesso; código do site não foi refeito. Fonte exata `2c4ce3c9c12dbffb147db533b44fb6d6690fcf2e`, deployment `appgdep_6acd7ca47e588191ae4d49f9148aa422`, concluído em 13/10/2026 00:35 UTC (12/10/2026 BRT).
- Após sucesso da publicação, `challenge_enable_auth()` ativou a exigência de autenticação. A função valida as contas/associações; não comprova login com senha.
- Preservadas duas versões de dados e três decisões QA com autoria anterior declarada. Nenhuma nova decisão, ação ou importação foi gravada nesta aceitação.

## Verificação observada
- `http_auth.py --guards-only`: quatro rejeições HTTP nos novos adaptadores aprovadas.
- `http_auth.py --guards-only --legacy-blocks`: sete rejeições aprovadas, incluindo criação de sessão, leitura e decisões pelos endpoints antigos.
- `db_auth_activation_guards.sql`: ativação ligada, dois perfis elegíveis, criação de sessão antiga rejeitada e RPCs administrativos não executáveis por browser; transação revertida, sem gravações Auth/negócio.
- Adaptadores autenticados ACTIVE v1, verify_jwt=true.
- Supabase confirmou dois usuários, dois memberships, duas versões, três decisões com autoria histórica preservada e zero sessões Auth no momento da consulta.
- Advisor pós-configuração: uma advertência sobre proteção contra senhas vazadas desativada; não foi alterado o plano ou a configuração. [Orientação oficial](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection).

## Limites e próximo passo
Naquela etapa, eu precisava entrar no site com as duas senhas, conferir painel/decisão/upload e testar saída. O agente não possui essas senhas e não as solicita pelo chat. Entrada com senha, autoria real, renovação e retomada de upload entre logins não foram verificadas. A tela foi publicada para permitir essa aceitação, sem condicionar o avanço ao envio de credenciais. Testes anteriores de componentes/SDK usam simulação e não contam como login real; naquela etapa, o QA visual ainda estava pendente; foi concluído em 13/10/2026.

O estado de self-signup no serviço Auth não foi verificado: não há ferramenta de configuração Auth disponível nesta conexão. Não existe cadastro público na interface e uma conta sem membership não acessa o painel. Testes HTTP antigos sem JWT são evidência histórica e devem falhar após ativação. O teste SQL de preparação que pressupõe associações incompletas não deve ser reexecutado no projeto já configurado.

README e documentação atualizados, sem reescrever o resumo histórico de preparação. Continuidade do versionamento no fork, alterações restritas à pasta de submissão, sem PR/review/issue/mensagem aos avaliadores.

## Minha aceitação posterior — 13/10/2026

Confirmei que concluí a aceitação completa do login das contas existentes. A solicitação de entrar e testar, descrita em “Limites e próximo passo”, foi atendida por esse aceite posterior e não representa pendência atual. O novo módulo de cadastro/redefinição tem sua própria validação pendente, conforme [gestão de usuários](user_management_2026-10-13.md). Ver [índice atualizado](README.md).

## Conclusão posterior da revisão visual — 13/10/2026

Concluí a revisão visual em navegador/celular, incluindo o assistente executivo. As pendências visuais acima descrevem a etapa histórica e estão encerradas. Os resultados de testes e seus limites permanecem os observados naquela etapa. Ver [consolidação documental](documentation_review_2026-10-13.md).
