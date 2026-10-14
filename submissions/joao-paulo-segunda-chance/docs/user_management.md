# Usuários, permissões e senhas iniciais

Implementação aprovada em 13/10/2026. Supabase permanece no plano Free. Cadastro direto via Auth Admin no servidor, sem SMTP, Resend ou convite por e-mail. Nenhuma senha das duas contas existentes foi alterada.

## Perfis

- Superadministrador: conta proprietária `amadojoaoborges@gmail.com`, identificada pelo UUID derivado na migração. A tabela protegida não permite que o módulo altere esse vínculo. A conta não pode ser desativada/rebaixada nem ter senha redefinida por outro administrador.
- Administrador: `email@raven.com` e contas que os administradores criarem/promoverem. Acesso completo, inclusive gestão dos demais administradores. Não altera o próprio perfil pelo módulo nem concede superadmin.
- Usuário: permissões explícitas. Ausência de uma permissão significa acesso negado. Não pode editar sua associação, papel ou permissões pelo navegador.

## Operação

Abra **Usuários e permissões → Adicionar usuário**. Informe nome, e-mail, perfil, permissões e senha inicial. O botão de mostrar senha permite vê-la durante a definição. Entregue as credenciais diretamente à pessoa antes de fechar o cadastro; o formulário apaga a senha ao terminar a tentativa. Não existe consulta posterior de senha, cópia legível no banco, registro em auditoria ou retorno da senha pela API.

Cadastros novos e redefinições exigem senha pessoal antes de liberar dados. O perfil mínimo para essa etapa permite apenas consultar a própria identidade, trocar a senha e sair. A troca é bloqueada no backend para as demais operações. O Supabase Auth mantém a senha com hash; o módulo não lê o hash. A senha exigida na aplicação tem 12–128 caracteres, maiúscula, minúscula e número, além das regras do Auth.

**Minha senha** permite trocar a própria senha. A redefinição administrativa bloqueia imediatamente as sessões anteriores do painel e exige nova senha pessoal. Desativar preserva autoria/histórico e bloqueia as sessões; reativar exige novo login. Não há exclusão de contas nem edição administrativa de e-mail nesta etapa. Cadastro administrativo confirma o endereço no Auth sem enviar mensagem; isso é provisionamento pela equipe, não comprovação de posse da caixa de e-mail.

## Permissões e dependências

| Permissão | Acesso |
|---|---|
| analytics.read | Visão executiva e diagnóstico. Sem accounts.read recebe somente agregados. |
| accounts.read | Contas, contratos, eventos, tickets e evidências por conta. |
| quality.read | Manifesto, qualidade e versões. Exemplos individuais são removidos sem accounts.read. |
| method.read | Metodologia. |
| decisions.read | Decisões e evidências. Exige indicadores, contas e qualidade, pois o registro congelado pode conter todos. |
| decisions.create | Registro/prévia de decisões. Exige decisions.read. |
| actions.update | Iniciar, concluir e cancelar ações. Exige decisions.read. |
| data.import | Inspecionar arquivo, mapear e preparar prévia. Exige indicadores, contas e qualidade. |
| data.publish | Iniciar/retomar processamento e publicar. Exige data.import. |
| assistant.use | Perguntas e histórico próprio. Exige indicadores, contas e qualidade. |

O formulário inclui automaticamente dependências e remove permissões dependentes quando uma leitura é desmarcada. O banco rejeita combinações inconsistentes. Não há recorte por setor/país como regra de autorização nesta etapa: os filtros continuam ferramentas de análise.

## Arquitetura e recuperação

- `access.memberships`: permissões, revisão otimista e obrigação de trocar senha; `access.super_admins`: vínculo imutável da conta proprietária.
- `access.user_operations`: estado da operação entre Auth e Postgres, sem senha. Reserva e marcador de criação protegem contra duplicação e associação de e-mail a uma conta diferente.
- `access.user_audit`: registro administrativo imutável, com ator e mudanças de acesso, sem senhas.
- `challenge-users`: Edge autenticada. Auth Admin e service_role exclusivamente no runtime. Cadastro não usa convite. Senha pessoal usa `/auth/v1/user` com o JWT do próprio usuário, ignorando alvo informado pelo navegador.
- RPCs exigem sessão real, associação ativa e permissões atuais. As implementações antigas movidas para `access` permanecem fora da API exposta; invocação pública fica nas funções verificadas.
- Respostas do painel excluem arrays proibidos. Assistente revalida permissão inclusive para consultar histórico. A interface revalida perfil ao focar a janela, a cada 30 segundos e após 403; alteração de revisão descarta dados carregados. O servidor bloqueia novas chamadas imediatamente, independentemente desse intervalo visual.

Uma falha entre Auth e banco fica pendente, sem conceder acesso incompleto. Após um minuto, use **Operações pendentes → Retomar** e informe novamente a senha. Outro administrador pode assumir cadastro/redefinição interrompidos, com auditoria. O estado guarda dados do cadastro e IDs da operação; não guarda senha. O limite é 100 operações de cadastro/senha por ator em 24 horas. Não interpretar timeout como confirmação de que o Auth não executou a operação.

## Migração, publicação e testes

Aplicar depois das migrações existentes: `supabase/migrations/20261013140604_user_management.sql`. Nome gerado por `supabase migration new user_management`; não reexecutar em um banco já migrado. A migração inicializa o proprietário a partir do e-mail expressamente aprovado e promove a segunda conta existente. Para uma instalação independente, revisar esses identificadores de bootstrap. O vínculo operacional passa a usar UUID.

Gerar `node scripts/build_users_edge.mjs --output .work/users/index.js` e publicar como `challenge-users`, verify_jwt=true. Reempacotar/publicar `challenge-assistant` com o novo bloqueio de status. Ingestão e decisões continuam usando os adaptadores existentes, com as permissões aplicadas nas RPCs. O catálogo de permissões do frontend é uma cópia conferida por teste do domínio canônico.

```sh
cd web/frontend
npm run check
npm run test:ui
npm run build
cd ../..
python web/tests/http_users.py
```

Para os testes SQL, use exclusivamente o Postgres WASM local, com dependência de teste separada:

```sh
npm install --prefix .work/local-sql @electric-sql/pglite@0.5.9
PGLITE_MODULE="$(pwd)/.work/local-sql/node_modules/@electric-sql/pglite/dist/index.js" node scripts/test_user_management_local.mjs
```

O runner cria roles/tabelas Auth e identidades sintéticas somente na memória do processo local. **Nunca aplique `tests/local_users_fixture.sql` ou `tests/local_user_management.sql` no Supabase compartilhado.** O teste cobre proteção do proprietário, dependências, negação de chamadas, descarte de dados proibidos, revisão concorrente, senha obrigatória, idempotência, desativação e grants. Não representa integração HTTP real com o serviço Auth.

O cadastro/redefinição reais no navegador ainda precisam de validação com uma conta de uso legítimo. O login das contas existentes e a revisão visual em navegador/celular foram concluídos por mim em 13/10/2026. A validação funcional de cadastro/redefinição é distinta dessa revisão visual.

A proteção Supabase contra senhas vazadas continua indisponível no plano Free; não houve upgrade ou contratação. [Referência oficial](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection).
