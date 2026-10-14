# Gestão de usuários — 13/10/2026

## Autorização e escopo
Aprovei o módulo de usuários/permissões, promovi `email@raven.com` a administrador e determinei a proteção de `amadojoaoborges@gmail.com` como superadministrador. Confirmei permanência no Supabase Free e descartei SMTP/convites por e-mail. Aprovei senha inicial visível durante a definição, sem recuperação posterior, e troca pessoal obrigatória. Nenhuma senha real foi solicitada, lida, redefinida, registrada em logs ou versionada nesta implantação. Login existente já aceito por mim; não foi reaberto como pendência.

## Entrega
- Tela Usuários e permissões: cadastro, perfil, permissões com dependências, ativação/desativação, redefinição de senha, pesquisa/filtros, operações pendentes e auditoria.
- Senhas iniciais/redefinidas visíveis somente enquanto informadas; limpeza do formulário após tentativa. Minha senha e bloqueio obrigatório dos dados antes da troca pessoal.
- Autorização no banco para leitura, decisões, ações, importação, publicação e assistente. Respostas filtradas para não entregar contas/evidências a quem só pode ver agregados.
- Perfil atualizado ao focar/periodicamente/após 403; revisão descarta dados antigos da interface. Proteção do proprietário e concorrência de edições no servidor.
- Operações entre Auth e Postgres com reserva, lease, marcador de criação e retomada explícita auditada; não armazenam senha. API Auth Admin no servidor, sem enviar convite. Senha pessoal usa JWT do próprio usuário.

## Migração e publicação
`supabase/migrations/20261013140604_user_management.sql` foi criada com Supabase CLI e aplicada via integração. Não houve alteração dos fatos analíticos. Verificação posterior: duas contas ativas (super_admin/administrator), duas versões publicadas, zero operações/auditorias de cadastro ou redefinição reais e zero funções challenge_* indevidamente executáveis por anon/authenticated. Senhas e obrigação de troca das contas existentes preservadas.

- `challenge-users` ACTIVE v1, verify_jwt=true; SHA256 `328bd963f5495932231a66c9bddf326770c9ddf3666f7a4d167418a453c9de9f`.
- `challenge-assistant` ACTIVE v6, verify_jwt=true; SHA256 `3ba9e6288cf66522f2ceae6ac29fc2a2801aa38b2ce78d2e739284e02291f6ea`.
- Site v10 publicado com sucesso em 13/10/2026, fonte `df9aecad207a6492b6bf5aedffe661aace168ff9`, versão `appgprj_6acd1d8dcc3881919b38d763b7e4d89b~appgver_5305e2a4c75c81918f78562f9953a6ef`.
- URL: https://challenge-g4-ravenstack.early-hake-5665.chatgpt.site/

## Verificação
- 47 testes de interface/adaptadores aprovados, zero falhas/skips, incluindo permissões, primeiro acesso, proteção do proprietário, dependências, revogação, ausência de senha na resposta/RPC e JWT correto na troca pessoal.
- TypeScript e builds Vite/Vinext aprovados. Aviso de tamanho do bundle Vite não bloqueia a compilação.
- SQL em PGlite 0.5.9 isolado: migrações completas, identidades exclusivamente locais, proteção de papéis, negação de endpoints, descarte de dados individuais, concorrência, redefinição, primeiro acesso, idempotência, retomada por outro administrador, desativação e grants aprovados. Runner reproduzível; nunca aplicar suas fixtures ao Supabase compartilhado.
- Preflight com rollback no schema real verificou perfil/listagem, dashboard e assistente sem criar identidades artificiais.
- Quatro requisições HTTP reais sem autenticação válida foram rejeitadas com 401 (lista, cadastro, redefinição e troca pessoal). Nenhuma mutação autenticada foi tentada nesse teste.
- Advisor de segurança mantém somente a advertência já conhecida sobre proteção de senha vazada, indisponível no Free. Sem upgrade ou serviço contratado.

## Limites e próxima aceitação
Não foi possível fazer QA visual em navegador pelo ambiente disponível. Happy DOM não substitui desktop/celular reais. Cadastro/redefinição e primeiro acesso reais precisam ser exercitados com uma conta legítima; os testes SQL e de gateway não são uma execução HTTP integral do Supabase Auth. Nenhum usuário fictício foi criado no serviço compartilhado.

A atualização fica na pasta e branch exclusivas da segunda chance. Nenhuma PR, issue ou mensagem a avaliadores foi criada. Documentação operacional em [user_management.md](../docs/user_management.md).

## Conclusão posterior da revisão visual — 13/10/2026

Concluí a revisão visual em navegador/celular, incluindo o assistente executivo. As pendências visuais acima descrevem a etapa histórica e estão encerradas. Os resultados de testes e seus limites permanecem os observados naquela etapa. Ver [consolidação documental](documentation_review_2026-10-13.md).
