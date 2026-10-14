-- Identity foundation; activation remains false until both real accounts are ready.
-- Credentials belong to Supabase Auth; no application password table.
alter table access.memberships add column display_name text check(length(display_name) between 2 and 100);
alter table access.web_sessions add column user_id uuid references auth.users(id),
 add column auth_session_id uuid, add column workspace_id uuid references access.workspaces(id),
 add column revoked_at timestamptz,add constraint authenticated_session_identity unique(user_id,auth_session_id),
 add constraint authenticated_session_complete check((user_id is null and auth_session_id is null and workspace_id is null) or(user_id is not null and auth_session_id is not null and workspace_id is not null));
-- auth_session_id deliberately has no FK: logout removes Auth sessions while history remains.
create index web_sessions_workspace_idx on access.web_sessions(workspace_id);
alter table ingest.web_uploads add column actor_user_id uuid references auth.users(id);
create index web_upload_actor_idx on ingest.web_uploads(actor_user_id);
alter table ingest.import_batches add column actor_user_id uuid references auth.users(id);
create index batch_actor_user_idx on ingest.import_batches(actor_user_id);
create table access.authentication_settings(workspace_id uuid primary key references access.workspaces(id),authentication_required boolean not null default false);
insert into access.authentication_settings(workspace_id) select id from access.workspaces where slug='ravenstack';
alter table access.authentication_settings enable row level security;
create policy backend_only on access.authentication_settings to service_role using(true) with check(true);
grant all on access.authentication_settings to service_role;
-- Read only identity/session columns required by the backend, never password hashes.
grant usage on schema auth to service_role;
grant select(id,email,email_confirmed_at,banned_until,deleted_at,is_anonymous) on auth.users to service_role;
grant select(id,user_id,not_after) on auth.sessions to service_role;

create function access.authentication_required() returns boolean language sql stable security invoker set search_path='' as $$
 select coalesce((select s.authentication_required from access.authentication_settings s join access.workspaces w on w.id=s.workspace_id where w.slug='ravenstack'),true)
$$;
create function access.checked_identity(p_user uuid,p_auth_session uuid) returns jsonb language plpgsql stable security invoker set search_path='' as $$
declare u record;m record;begin
 select id,email into u from auth.users where id=p_user and not is_anonymous and deleted_at is null and email_confirmed_at is not null and (banned_until is null or banned_until<=now());
 if not found or not exists(select 1 from auth.sessions where id=p_auth_session and user_id=p_user and(not_after is null or not_after>now())) then raise exception 'Sessão ausente ou expirada.' using errcode='28000';end if;
 select x.workspace_id,x.role,x.display_name into m from access.memberships x join access.workspaces w on w.id=x.workspace_id where w.slug='ravenstack' and x.user_id=p_user and x.active and x.role in('administrator','decision_maker');
 if not found then raise exception 'Sua conta não possui acesso ativo a este painel.' using errcode='PT403';end if;
 return jsonb_build_object('id',u.id,'session_id',p_auth_session,'workspace_id',m.workspace_id,'name',coalesce(m.display_name,'Usuário'),'email',u.email,'role',case when m.role='administrator' then 'administrator' else 'user' end);
end $$;
create function public.challenge_web_bind(p_token text,p_user uuid,p_auth_session uuid,p_peer text) returns jsonb language plpgsql security invoker set search_path='' as $$
declare profile jsonb;sid uuid;revoked timestamptz;begin
 profile=access.checked_identity(p_user,p_auth_session);
 if p_token is null or p_token!~'^[0-9a-f]{64}$' or p_peer is null or p_peer!~'^[0-9a-f]{64}$' then raise exception 'Sessão inválida.' using errcode='28000';end if;
 perform pg_advisory_xact_lock(hashtext('auth:'||p_auth_session::text));
 select id,revoked_at into sid,revoked from access.web_sessions where user_id=p_user and auth_session_id=p_auth_session;
 if sid is not null and revoked is not null then raise exception 'Sessão encerrada. Entre novamente.' using errcode='28000';end if;
 if sid is null then
  insert into access.web_sessions(token_hash,peer_hash,user_id,auth_session_id,workspace_id) values(p_token,p_peer,p_user,p_auth_session,(profile->>'workspace_id')::uuid) returning id into sid;
 else
  update access.web_sessions set token_hash=p_token,peer_hash=p_peer,expires_at=now()+interval '7 days' where id=sid;
 end if;
 return jsonb_build_object('user',profile);
end $$;
create function access.authenticated_web_session(p_token text) returns uuid language plpgsql stable security invoker set search_path='' as $$
declare s access.web_sessions;profile jsonb;begin
 select * into s from access.web_sessions where token_hash=p_token and expires_at>now() and revoked_at is null and user_id is not null;
 if not found then raise exception 'Sessão ausente ou expirada.' using errcode='28000';end if;
 profile=access.checked_identity(s.user_id,s.auth_session_id);
 if s.workspace_id is distinct from(profile->>'workspace_id')::uuid then raise exception 'Sessão de outro workspace.' using errcode='PT403';end if;
 return s.id;
end $$;
create or replace function access.web_session(p_token text) returns uuid language plpgsql security invoker set search_path='' as $$
declare s access.web_sessions;begin
 select * into s from access.web_sessions where token_hash=p_token and expires_at>now() and revoked_at is null;
 if not found then raise exception 'Sessão ausente ou expirada.' using errcode='28000';end if;
 if s.user_id is not null then return access.authenticated_web_session(p_token);end if;
 if access.authentication_required() then raise exception 'Entre com e-mail e senha para acessar o painel.' using errcode='28000';end if;
 return s.id;
end $$;
create or replace function public.challenge_web_session(p_token text,p_peer text) returns uuid language plpgsql security invoker set search_path='' as $$
declare s uuid;begin
 if access.authentication_required() then raise exception 'Entre com e-mail e senha para acessar o painel.' using errcode='28000';end if;
 perform pg_advisory_xact_lock(hashtext('challenge_web_session'));
 if p_token!~'^[0-9a-f]{64}$' or p_peer!~'^[0-9a-f]{64}$' then raise exception 'Hash inválido';end if;
 if(select count(*) from access.web_sessions where created_at>now()-interval '1 hour' and peer_hash=p_peer)>=30 or(select count(*) from access.web_sessions where created_at>now()-interval '1 day')>=500 then raise exception 'Limite de sessões atingido; tente mais tarde';end if;
 insert into access.web_sessions(token_hash,peer_hash) values(p_token,p_peer) returning id into s;return s;
end $$;
create function public.challenge_web_logout(p_token text) returns jsonb language plpgsql security invoker set search_path='' as $$
declare sid uuid;begin
 sid=access.authenticated_web_session(p_token);update access.web_sessions set revoked_at=now(),expires_at=now() where id=sid;
 return jsonb_build_object('signed_out',true);
end $$;
create function public.challenge_enable_auth() returns jsonb language plpgsql security invoker set search_path='' as $$
declare ws uuid;admins integer;users integer;total integer;begin
 select id into strict ws from access.workspaces where slug='ravenstack';
 select count(*) filter(where m.role='administrator'),count(*) filter(where m.role='decision_maker'),count(*) into admins,users,total from access.memberships m join auth.users u on u.id=m.user_id where m.workspace_id=ws and m.active and m.role in('administrator','decision_maker') and m.display_name is not null and u.deleted_at is null and not u.is_anonymous and u.email_confirmed_at is not null and(u.banned_until is null or u.banned_until<=now());
 if admins<>1 or users<>1 or total<>2 then raise exception 'Configure e teste uma conta de administrador e uma conta de usuário antes de ativar.' using errcode='PT409';end if;
 update access.authentication_settings set authentication_required=true where workspace_id=ws;
 return jsonb_build_object('authentication_required',true);
end $$;
create function operations.attach_authenticated_actor() returns trigger language plpgsql security invoker set search_path='' as $$
declare session_id uuid;s access.web_sessions;profile jsonb;begin
 if tg_table_schema='ingest' then session_id=new.session_id;else session_id=new.actor_session_id;end if;
 if session_id is null then return new;end if;
 select * into strict s from access.web_sessions where id=session_id;
 if s.user_id is null then
  if access.authentication_required() then raise exception 'Autoria autenticada obrigatória.' using errcode='28000';end if;
  return new;
 end if;
 perform access.authenticated_web_session(s.token_hash);profile=access.checked_identity(s.user_id,s.auth_session_id);
 if new.actor_user_id is not null and new.actor_user_id<>s.user_id then raise exception 'Autor incompatível com a sessão.' using errcode='PT403';end if;
 new.actor_user_id=s.user_id;
 if tg_table_schema='operations' and tg_table_name='decisions' then new.actor_display_name=profile->>'name';end if;
 return new;
end $$;
create trigger decision_authenticated_actor before insert on operations.decisions for each row execute function operations.attach_authenticated_actor();
create trigger history_authenticated_actor before insert on operations.action_history for each row execute function operations.attach_authenticated_actor();
create trigger upload_authenticated_actor before insert on ingest.web_uploads for each row execute function operations.attach_authenticated_actor();
create function ingest.attach_import_actor() returns trigger language plpgsql security invoker set search_path='' as $$
declare batch uuid;begin
 if new.actor_user_id is null or new.version_id is null then return new;end if;
 select batch_id into strict batch from analytics.dataset_versions where id=new.version_id;
 if exists(select 1 from ingest.import_batches where id=batch and actor_user_id is not null and actor_user_id<>new.actor_user_id) then raise exception 'Importação vinculada a outro autor.' using errcode='PT403';end if;
 update ingest.import_batches set actor_user_id=new.actor_user_id where id=batch and actor_user_id is null;
 return new;
end $$;
create trigger import_authenticated_actor after update of version_id on ingest.web_uploads for each row execute function ingest.attach_import_actor();

do $$declare f record;begin
 for f in select p.oid::regprocedure as signature from pg_proc p join pg_namespace n on n.oid=p.pronamespace where
 (n.nspname='access' and p.proname in('authentication_required','checked_identity','authenticated_web_session','web_session'))
 or(n.nspname='public' and p.proname in('challenge_web_bind','challenge_web_session','challenge_web_logout','challenge_enable_auth'))
 or(n.nspname='operations' and p.proname='attach_authenticated_actor') or(n.nspname='ingest' and p.proname='attach_import_actor') loop
 execute 'revoke execute on function '||f.signature||' from public,anon,authenticated';execute 'grant execute on function '||f.signature||' to service_role';end loop;
end $$;
