-- User administration. Auth passwords are handled only by the server-side Auth Admin API.
alter table access.memberships add column permissions text[] not null default '{}',add column password_change_required boolean not null default false,add column revision integer not null default 1;
create table access.super_admins(workspace_id uuid primary key references access.workspaces(id),user_id uuid not null references auth.users(id),unique(workspace_id,user_id));
create table access.user_audit(id uuid primary key default gen_random_uuid(),workspace_id uuid not null references access.workspaces(id),actor_id uuid not null references auth.users(id),target_id uuid references auth.users(id),action text not null,details jsonb not null default '{}',created_at timestamptz not null default now());
create index user_audit_workspace_created on access.user_audit(workspace_id,created_at desc);
create index user_audit_actor on access.user_audit(actor_id);
create index user_audit_target on access.user_audit(target_id);
create table access.user_operations(id uuid primary key,workspace_id uuid not null references access.workspaces(id),actor_id uuid not null references auth.users(id),target_id uuid references auth.users(id),kind text not null check(kind in('create','reset_password','change_password')),email text,data jsonb not null default '{}',state text not null default 'pending' check(state in('pending','completed')),attempt uuid not null default gen_random_uuid(),lease_until timestamptz not null default now()+interval '45 seconds',created_at timestamptz not null default now(),completed_at timestamptz);
create unique index user_operations_pending_email on access.user_operations(workspace_id,email) where kind='create' and state='pending';
create unique index user_operations_pending_target on access.user_operations(workspace_id,target_id) where state='pending' and target_id is not null;
create index user_operations_actor on access.user_operations(actor_id,created_at);
create index super_admin_user on access.super_admins(user_id);
-- Derive immutable owner identity once from the explicitly approved existing account.
insert into access.super_admins select w.id,u.id from access.workspaces w join access.memberships m on m.workspace_id=w.id join auth.users u on u.id=m.user_id where w.slug='ravenstack' and lower(u.email)='amadojoaoborges@gmail.com' and m.active;
do $$ begin if (select count(*) from access.super_admins s join access.workspaces w on w.id=s.workspace_id where w.slug='ravenstack')<>1 then raise exception 'Conta proprietária não encontrada de forma inequívoca.';end if;end $$;
update access.memberships m set role='administrator',revision=revision+1 from auth.users u,access.workspaces w where u.id=m.user_id and w.id=m.workspace_id and w.slug='ravenstack' and lower(u.email) in('amadojoaoborges@gmail.com','email@raven.com');
create function access.append_only_user_audit() returns trigger language plpgsql security invoker set search_path='' as $$ begin raise exception 'Histórico administrativo imutável.' using errcode='PT403';end $$;
create trigger immutable_user_audit before update or delete on access.user_audit for each row execute function access.append_only_user_audit();
create function access.keep_owner() returns trigger language plpgsql security invoker set search_path='' as $$ begin raise exception 'Vínculo do superadministrador é protegido.' using errcode='PT403';end $$;
create trigger immutable_owner before update or delete on access.super_admins for each row execute function access.keep_owner();
create function access.protect_owner_membership() returns trigger language plpgsql security invoker set search_path='' as $$ begin
 if exists(select 1 from access.super_admins where workspace_id=old.workspace_id and user_id=old.user_id) then
  if tg_op='DELETE' then raise exception 'Conta protegida.' using errcode='PT403';end if;
  if new.user_id<>old.user_id or new.workspace_id<>old.workspace_id or not new.active or new.role<>'administrator' then raise exception 'Conta protegida.' using errcode='PT403';end if;
 end if;return new;
end $$;
create trigger protected_owner before update or delete on access.memberships for each row execute function access.protect_owner_membership();
create function access.permission_codes() returns text[] language sql immutable security invoker set search_path='' as $$ select array['analytics.read','accounts.read','quality.read','method.read','decisions.read','decisions.create','actions.update','data.import','data.publish','assistant.use']::text[] $$;
create or replace function access.valid_permissions(p text[]) returns boolean language sql immutable security invoker set search_path='' as $$
 select p is not null and array_position(p,null) is null and p<@access.permission_codes()
 and (not ('decisions.read'=any(p)) or array['analytics.read','accounts.read','quality.read']<@p)
 and (not ('decisions.create'=any(p) or 'actions.update'=any(p)) or 'decisions.read'=any(p))
 and (not ('data.import'=any(p)) or array['quality.read','accounts.read','analytics.read']<@p)
 and (not ('data.publish'=any(p)) or 'data.import'=any(p))
 and (not ('assistant.use'=any(p)) or array['analytics.read','accounts.read','quality.read']<@p)
$$;
alter table access.memberships add constraint membership_valid_permissions check(access.valid_permissions(permissions));
create or replace function access.checked_identity(p_user uuid,p_auth_session uuid) returns jsonb language plpgsql stable security invoker set search_path='' as $$
declare u record;m access.memberships;owner boolean;begin
 select id,email into u from auth.users where id=p_user and not is_anonymous and deleted_at is null and email_confirmed_at is not null and (banned_until is null or banned_until<=now());
 if not found or not exists(select 1 from auth.sessions where id=p_auth_session and user_id=p_user and(not_after is null or not_after>now())) then raise exception 'Sessão ausente ou expirada.' using errcode='28000';end if;
 select x.* into m from access.memberships x join access.workspaces w on w.id=x.workspace_id where w.slug='ravenstack' and x.user_id=p_user and x.active;
 if not found then raise exception 'Sua conta não possui acesso ativo a este painel.' using errcode='PT403';end if;
 owner=exists(select 1 from access.super_admins where workspace_id=m.workspace_id and user_id=m.user_id);
 return jsonb_build_object('id',u.id,'session_id',p_auth_session,'workspace_id',m.workspace_id,'name',coalesce(m.display_name,'Usuário'),'email',u.email,'role',case when owner then 'super_admin' when m.role='administrator' then 'administrator' else 'user' end,'permissions',case when m.role='administrator' then access.permission_codes() else m.permissions end,'password_change_required',m.password_change_required,'revision',m.revision);
end $$;
create function access.user_profile(p_token text,p_allow_password boolean default false) returns jsonb language plpgsql security invoker set search_path='' as $$
declare s access.web_sessions;p jsonb;begin
 select * into s from access.web_sessions where token_hash=p_token and expires_at>now() and revoked_at is null and user_id is not null;
 if not found then raise exception 'Sessão ausente ou expirada.' using errcode='28000';end if;
 -- Lock the membership through the protected transaction; concurrent revocation waits for it.
 perform 1 from access.memberships where workspace_id=s.workspace_id and user_id=s.user_id for share;
 p=access.checked_identity(s.user_id,s.auth_session_id);
 if s.workspace_id is distinct from(p->>'workspace_id')::uuid then raise exception 'Workspace inválido.' using errcode='PT403';end if;
 if not p_allow_password and (p->>'password_change_required')::boolean then raise exception 'Defina sua senha pessoal antes de acessar o painel.' using errcode='PT403';end if;
 return p;
end $$;
create or replace function access.authenticated_web_session(p_token text) returns uuid language plpgsql security invoker set search_path='' as $$ begin perform access.user_profile(p_token);return (select id from access.web_sessions where token_hash=p_token);end $$;
create function access.require_permission(p_token text,p_permission text) returns jsonb language plpgsql security invoker set search_path='' as $$
declare p jsonb;begin p=access.user_profile(p_token);if p_permission='users.manage' then
 if p->>'role' not in('super_admin','administrator') then raise exception 'Você não pode administrar usuários.' using errcode='PT403';end if;
 elsif not coalesce((p->'permissions')?p_permission,false) then raise exception 'Você não possui permissão para esta operação.' using errcode='PT403';end if;return p;end $$;
create function public.challenge_access_check(p_token text,p_permission text) returns jsonb language sql security invoker set search_path='' as $$ select access.require_permission(p_token,p_permission) $$;
create function access.user_payload(p_data jsonb) returns jsonb language plpgsql immutable security invoker set search_path='' as $$
declare perms text[];n text;r text;begin
 if jsonb_typeof(p_data)<>'object' or jsonb_typeof(p_data->'permissions')<>'array' then raise exception 'Dados inválidos.' using errcode='22023';end if;
 n=btrim(p_data->>'name');r=p_data->>'role';
 if n is null or length(n) not between 2 and 100 or r is null or r not in('administrator','user') or jsonb_typeof(p_data->'active')<>'boolean' then raise exception 'Nome, perfil ou situação inválidos.' using errcode='22023';end if;
 select coalesce(array_agg(distinct x order by x),'{}') into perms from jsonb_array_elements_text(p_data->'permissions') x;
 if not access.valid_permissions(perms) or (r='user' and cardinality(perms)=0) then raise exception 'Permissões incompletas ou inválidas.' using errcode='22023';end if;
 return jsonb_build_object('name',n,'role',r,'active',p_data->'active','permissions',case when r='administrator' then '{}'::text[] else perms end);
end $$;
create function public.challenge_users_list(p_token text) returns jsonb language plpgsql security invoker set search_path='' as $$
declare p jsonb;ws uuid;begin p=access.require_permission(p_token,'users.manage');ws=(p->>'workspace_id')::uuid;
 return jsonb_build_object('users',(select coalesce(jsonb_agg(jsonb_build_object('id',m.user_id,'name',m.display_name,'email',u.email,'role',case when s.user_id is not null then 'super_admin' when m.role='administrator' then 'administrator' else 'user' end,'active',m.active,'permissions',case when m.role='administrator' then access.permission_codes() else m.permissions end,'password_change_required',m.password_change_required,'revision',m.revision,'pending_operation',exists(select 1 from access.user_operations o where o.target_id=m.user_id and o.workspace_id=ws and state='pending')) order by m.display_name),'[]') from access.memberships m join auth.users u on u.id=m.user_id left join access.super_admins s on s.workspace_id=m.workspace_id and s.user_id=m.user_id where m.workspace_id=ws),
 'audit',(select coalesce(jsonb_agg(x order by x.created_at desc),'[]') from (select a.*,u.email as actor_email,t.email as target_email from access.user_audit a left join auth.users u on u.id=a.actor_id left join auth.users t on t.id=a.target_id where a.workspace_id=ws order by a.created_at desc limit 100)x),
 'pending',(select coalesce(jsonb_agg(jsonb_build_object('id',id,'kind',kind,'email',email,'target_id',target_id,'data',data,'created_at',created_at)),'[]') from access.user_operations where workspace_id=ws and kind<>'change_password' and state='pending'));
end $$;
create function access.editable_target(p_actor jsonb,p_target uuid) returns access.memberships language plpgsql security invoker set search_path='' as $$
declare m access.memberships;begin
 if p_target=(p_actor->>'id')::uuid then raise exception 'Altere sua própria senha pelo menu da conta; seu perfil não pode ser alterado aqui.' using errcode='PT403';end if;
 if exists(select 1 from access.super_admins where workspace_id=(p_actor->>'workspace_id')::uuid and user_id=p_target) then raise exception 'O superadministrador é uma conta protegida.' using errcode='PT403';end if;
 select * into m from access.memberships where workspace_id=(p_actor->>'workspace_id')::uuid and user_id=p_target for update;
 if not found then raise exception 'Usuário não encontrado.' using errcode='22023';end if;return m;
end $$;
create function public.challenge_users_update(p_token text,p_target uuid,p_revision integer,p_data jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
declare p jsonb;d jsonb;m access.memberships;begin
 perform pg_advisory_xact_lock(hashtext('ravenstack-user-management'));
 p=access.require_permission(p_token,'users.manage');m=access.editable_target(p,p_target);d=access.user_payload(p_data);
 if m.revision is distinct from p_revision then raise exception 'O usuário foi alterado. Atualize a lista.' using errcode='PT409';end if;
 if exists(select 1 from access.user_operations where workspace_id=m.workspace_id and target_id=p_target and state='pending') then raise exception 'Conclua a operação de senha pendente antes de editar este usuário.' using errcode='PT409';end if;
 update access.memberships set display_name=d->>'name',role=case when d->>'role'='administrator' then 'administrator' else 'decision_maker' end,permissions=array(select jsonb_array_elements_text(d->'permissions')),active=(d->>'active')::boolean,revision=revision+1 where workspace_id=m.workspace_id and user_id=p_target;
 if not(d->>'active')::boolean then update access.web_sessions set revoked_at=now(),expires_at=now() where workspace_id=m.workspace_id and user_id=p_target and revoked_at is null;end if;
 insert into access.user_audit(workspace_id,actor_id,target_id,action,details) values(m.workspace_id,(p->>'id')::uuid,p_target,'access_updated',jsonb_build_object('before',jsonb_build_object('name',m.display_name,'role',m.role,'active',m.active,'permissions',m.permissions),'after',d));
 return jsonb_build_object('updated',true);
end $$;
create function public.challenge_users_prepare(p_token text,p_request uuid,p_kind text,p_target uuid,p_revision integer,p_data jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
declare p jsonb;d jsonb;o access.user_operations;m access.memberships;ws uuid;requested_email text;target uuid;marker text;begin
 perform pg_advisory_xact_lock(hashtext('ravenstack-user-management'));
 if p_request is null or p_kind not in('create','reset_password','change_password') then raise exception 'Operação inválida.' using errcode='22023';end if;
 p=case when p_kind='change_password' then access.user_profile(p_token,true) else access.require_permission(p_token,'users.manage') end;ws=(p->>'workspace_id')::uuid;
 target=case when p_kind='change_password' then (p->>'id')::uuid else p_target end;
 select * into o from access.user_operations where id=p_request for update;
 if not found and p_kind='change_password' then select * into o from access.user_operations where workspace_id=ws and target_id=target and actor_id=target and kind='change_password' and state='pending' for update;end if;
 if o.id is not null then
  if o.actor_id<>(p->>'id')::uuid or o.workspace_id<>ws or o.kind<>p_kind or (p_kind<>'create' and o.target_id is distinct from target) then raise exception 'Solicitação incompatível.' using errcode='PT409';end if;
  if o.state='completed' then return jsonb_build_object('state','completed');end if;
  if o.lease_until>now() then raise exception 'Operação em processamento. Aguarde um minuto antes de retomar.' using errcode='PT409';end if;
  if p_kind='create' then
   d=access.user_payload(p_data);requested_email=lower(btrim(p_data->>'email'));
   if o.data<>d or o.email<>requested_email then raise exception 'Retome com os mesmos dados do cadastro original.' using errcode='PT409';end if;
   select id,raw_app_meta_data->>'ravenstack_creation_operation' into target,marker from auth.users where lower(auth.users.email)=o.email and deleted_at is null;
   if target is not null and marker is distinct from o.id::text then raise exception 'E-mail já utilizado em outra conta.' using errcode='PT409';end if;
  elsif p_kind='reset_password' then m=access.editable_target(p,target);
  end if;
  update access.user_operations set attempt=gen_random_uuid(),lease_until=now()+interval '45 seconds',target_id=target where id=o.id returning * into o;
 else
  if (select count(*) from access.user_operations where actor_id=(p->>'id')::uuid and created_at>now()-interval '1 day')>=100 then raise exception 'Limite diário de alterações de senha/cadastro atingido.' using errcode='PT429';end if;
  d='{}';
  if p_kind='create' then
   d=access.user_payload(p_data);requested_email=lower(btrim(p_data->>'email'));
   if requested_email is null or length(requested_email)>254 or requested_email!~'^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$' then raise exception 'E-mail inválido.' using errcode='22023';end if;
   if exists(select 1 from auth.users where lower(auth.users.email)=requested_email and deleted_at is null) then raise exception 'Este e-mail já possui uma conta. Use a lista de usuários.' using errcode='PT409';end if;
   target=null;
  elsif p_kind='reset_password' then
   m=access.editable_target(p,target);if m.revision is distinct from p_revision then raise exception 'O usuário foi alterado. Atualize a lista.' using errcode='PT409';end if;
   update access.memberships set password_change_required=true,revision=revision+1 where workspace_id=ws and user_id=target;
   update access.web_sessions set revoked_at=now(),expires_at=now() where workspace_id=ws and user_id=target and revoked_at is null;
  else
   update access.memberships set password_change_required=true,revision=revision+1 where workspace_id=ws and user_id=target;
  end if;
  insert into access.user_operations(id,workspace_id,actor_id,target_id,kind,email,data) values(p_request,ws,(p->>'id')::uuid,target,p_kind,requested_email,d) returning * into o;
  insert into access.user_audit(workspace_id,actor_id,target_id,action,details) values(ws,(p->>'id')::uuid,target,p_kind||'_requested',jsonb_build_object('operation_id',o.id,'email',requested_email));
 end if;
 return jsonb_build_object('id',o.id,'attempt',o.attempt,'state',o.state,'email',o.email,'target_id',o.target_id);
exception when unique_violation then raise exception 'Já existe uma operação pendente para este usuário. Retome pela lista.' using errcode='PT409';
end $$;
create function public.challenge_users_takeover(p_token text,p_request uuid) returns jsonb language plpgsql security invoker set search_path='' as $$
declare p jsonb;o access.user_operations;m access.memberships;begin
 perform pg_advisory_xact_lock(hashtext('ravenstack-user-management'));p=access.require_permission(p_token,'users.manage');
 select * into o from access.user_operations where id=p_request and workspace_id=(p->>'workspace_id')::uuid for update;
 if not found or o.kind='change_password' or o.state<>'pending' then raise exception 'Operação não disponível para retomada.' using errcode='PT409';end if;
 if o.lease_until>now() then raise exception 'Aguarde um minuto antes de retomar.' using errcode='PT409';end if;
 if o.kind='reset_password' then m=access.editable_target(p,o.target_id);end if;
 if o.actor_id<>(p->>'id')::uuid then
  update access.user_operations set actor_id=(p->>'id')::uuid where id=o.id;
  insert into access.user_audit(workspace_id,actor_id,target_id,action,details) values(o.workspace_id,(p->>'id')::uuid,o.target_id,'operation_resumed',jsonb_build_object('operation_id',o.id,'previous_actor_id',o.actor_id));
 end if;return jsonb_build_object('resumed',true);
end $$;
create function public.challenge_users_finish(p_token text,p_request uuid,p_attempt uuid) returns jsonb language plpgsql security invoker set search_path='' as $$
declare p jsonb;o access.user_operations;target uuid;m access.memberships;begin
 perform pg_advisory_xact_lock(hashtext('ravenstack-user-management'));
 select * into o from access.user_operations where id=p_request for update;if not found then raise exception 'Operação desconhecida.' using errcode='22023';end if;
 p=case when o.kind='change_password' then access.user_profile(p_token,true) else access.require_permission(p_token,'users.manage') end;
 if o.actor_id<>(p->>'id')::uuid or o.workspace_id<>(p->>'workspace_id')::uuid or o.attempt<>p_attempt then raise exception 'Operação incompatível.' using errcode='PT409';end if;
 if o.state='completed' then return jsonb_build_object('completed',true);end if;
 if o.kind='create' then
  select id into target from auth.users where lower(email)=o.email and raw_app_meta_data->>'ravenstack_creation_operation'=o.id::text and deleted_at is null and email_confirmed_at is not null;
  if not found then raise exception 'Cadastro no Auth ainda não confirmado. Retome a solicitação.' using errcode='PT409';end if;
  insert into access.memberships(workspace_id,user_id,role,active,display_name,permissions,password_change_required) values(o.workspace_id,target,case when o.data->>'role'='administrator' then 'administrator' else 'decision_maker' end,true,o.data->>'name',array(select jsonb_array_elements_text(o.data->'permissions')),true);
 else
  target=o.target_id;
  if o.kind='reset_password' then m=access.editable_target(p,target);end if;
  if o.kind='change_password' then
   update access.memberships set password_change_required=false,revision=revision+1 where workspace_id=o.workspace_id and user_id=target;
   update access.web_sessions set revoked_at=now(),expires_at=now() where workspace_id=o.workspace_id and user_id=target and token_hash<>p_token and revoked_at is null;
  end if;
 end if;
 update access.user_operations set state='completed',completed_at=now(),target_id=target where id=o.id;
 insert into access.user_audit(workspace_id,actor_id,target_id,action,details) values(o.workspace_id,o.actor_id,target,o.kind||'_completed',jsonb_build_object('operation_id',o.id));
 return jsonb_build_object('completed',true);
end $$;
-- All protected data operations require current permissions, even with an old JWT.
-- Move canonical implementations to the unexposed access schema and wrap each public entry.
do $migration$
declare f record;perm text;names text;body text;begin
 for f in select p.oid,p.proname,pg_get_function_identity_arguments(p.oid) ident,pg_get_function_arguments(p.oid) args,pg_get_function_result(p.oid) result,p.proargnames from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public' and p.proname in('challenge_web_dashboard','challenge_web_detail','challenge_web_sources','challenge_web_stage','challenge_web_begin','challenge_web_advance','challenge_web_decide','challenge_web_transition','challenge_web_scope_options','challenge_web_scope_preview','challenge_web_decide_scoped','challenge_assistant_list','challenge_assistant_create','challenge_assistant_conversation','challenge_assistant_update','challenge_assistant_begin','challenge_assistant_query','challenge_assistant_finish') loop
  execute format('alter function public.%I(%s) set schema access',f.proname,f.ident);
  if f.proname='challenge_web_dashboard' then continue;end if;
  perm=case when f.proname like 'challenge_assistant_%' then 'assistant.use' when f.proname='challenge_web_detail' then 'accounts.read' when f.proname in('challenge_web_sources','challenge_web_stage') then 'data.import' when f.proname in('challenge_web_begin','challenge_web_advance') then 'data.publish' when f.proname='challenge_web_transition' then 'actions.update' else 'decisions.create' end;
  names=array_to_string(f.proargnames,',');body=format('begin perform access.require_permission(p_token,%L); return access.%I(%s); end;',perm,f.proname,names);
  execute format('create function public.%I(%s) returns %s language plpgsql security invoker set search_path='''' as %L',f.proname,f.args,f.result,body);
 end loop;
end $migration$;
create function public.challenge_web_dashboard(p_token text) returns jsonb language plpgsql security invoker set search_path='' as $$
declare p jsonb;d jsonb;perms jsonb;k text;groups jsonb;begin
 p=access.user_profile(p_token);perms=p->'permissions';d=access.challenge_web_dashboard(p_token);
 if not(perms?'analytics.read') then d=jsonb_set(d,'{run,metrics}','{}');end if;
 if perms?'analytics.read' then
  select coalesce(jsonb_agg(to_jsonb(g)),'[]') into groups from (
   select s.industry,s.country,count(*) accounts,count(*) filter(where s.open_contracts>0) open_accounts,sum(s.open_contracts) open_contracts,sum(s.contract_mrr) contract_mrr,count(*) filter(where s.cadastral_churn) flagged,
   count(*) filter(where s.reconciliation_state='flag_without_event') missing,count(*) filter(where s.cadastral_churn and s.churn_events=0) missing_cancel,coalesce(sum(s.contract_mrr) filter(where s.cadastral_churn and s.churn_events=0),0) missing_cancel_mrr,
   count(*) filter(where s.coherent_usage_rows_30d>0) observed_current,count(*) filter(where s.coherent_usage_rows_previous_30d>0) observed_previous,
   sum(s.recorded_usage_30d) usage_current,sum(s.recorded_usage_previous_30d) usage_previous,sum(s.eligible_tickets_30d) tickets,sum(s.closed_tickets_30d) closed,sum(s.satisfaction_responses) responses,sum(coalesce(s.mean_satisfaction,0)*s.satisfaction_responses) satisfaction_total,sum(s.churn_events) cancellations,sum(s.reactivation_events) reactivations
   from analytics.account_snapshots s where s.run_id=(d->'run'->>'id')::uuid group by s.industry,s.country
  )g;d=d||jsonb_build_object('analytics',groups);
 else d=d||jsonb_build_object('analytics','[]'::jsonb);end if;
 if not(perms?'accounts.read') then d=d||jsonb_build_object('accounts','[]'::jsonb,'evidence','[]'::jsonb); select coalesce(jsonb_agg(x-'examples'),'[]') into groups from jsonb_array_elements(d->'quality')x;d=d||jsonb_build_object('quality',groups);end if;
 if not(perms?'quality.read') then d=d||jsonb_build_object('quality','[]'::jsonb,'sources','[]'::jsonb);end if;
 if not(perms?'decisions.read') then d=d||jsonb_build_object('decisions','[]'::jsonb,'actions','[]'::jsonb,'history','[]'::jsonb);end if;
 if not(perms?'data.import') then d=d||jsonb_build_object('uploads','[]'::jsonb);end if;
 if not(perms?'quality.read' or perms?'analytics.read') then d=d||jsonb_build_object('versions','[]'::jsonb);
 elsif not(perms?'analytics.read') then select coalesce(jsonb_agg(x-'metrics'),'[]') into groups from jsonb_array_elements(d->'versions')x;d=d||jsonb_build_object('versions',groups);end if;
 return d||jsonb_build_object('user',p);
end $$;
-- Logout must also work while a first password change is pending.
create or replace function public.challenge_web_logout(p_token text) returns jsonb language plpgsql security invoker set search_path='' as $$ begin perform access.user_profile(p_token,true);update access.web_sessions set revoked_at=now(),expires_at=now() where token_hash=p_token;return jsonb_build_object('signed_out',true);end $$;
-- The old two-account bootstrap is no longer a valid invariant.
create or replace function public.challenge_enable_auth() returns jsonb language plpgsql security invoker set search_path='' as $$ begin
 if not exists(select 1 from access.super_admins s join access.memberships m on m.workspace_id=s.workspace_id and m.user_id=s.user_id where m.active and m.role='administrator') then raise exception 'Superadministrador ativo obrigatório.' using errcode='PT409';end if;
 update access.authentication_settings set authentication_required=true;return jsonb_build_object('authentication_required',true);end $$;
grant select(raw_app_meta_data) on auth.users to service_role;
do $$ declare t text;f record;begin
 foreach t in array array['super_admins','user_audit','user_operations'] loop
  execute format('alter table access.%I enable row level security',t);execute format('create policy backend_only on access.%I to service_role using(true) with check(true)',t);execute format('revoke all on access.%I from public,anon,authenticated',t);execute format('grant all on access.%I to service_role',t);
 end loop;
 for f in select n.nspname,p.proname,pg_get_function_identity_arguments(p.oid)args from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='access' or (n.nspname='public' and p.proname like 'challenge_%') loop
  execute format('revoke execute on function %I.%I(%s) from public,anon,authenticated',f.nspname,f.proname,f.args);execute format('grant execute on function %I.%I(%s) to service_role',f.nspname,f.proname,f.args);
 end loop;
end $$;
