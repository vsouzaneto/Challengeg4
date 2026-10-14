-- Access is intentionally open. Only the Edge adapter can execute these RPCs.
-- Bearer capabilities represent anonymous sessions, never verified people.
create table access.web_sessions (
 id uuid primary key default gen_random_uuid(), token_hash text unique not null check(token_hash~'^[0-9a-f]{64}$'),
 peer_hash text not null, created_at timestamptz not null default now(), expires_at timestamptz not null default now()+interval '7 days'
);
create index web_sessions_peer_time_idx on access.web_sessions(peer_hash,created_at);
alter table access.web_sessions enable row level security;
create policy backend_only on access.web_sessions to service_role using(true) with check(true);
create function access.web_session(p_token text) returns uuid language plpgsql security invoker set search_path='' as $$
declare s uuid; begin
 select id into s from access.web_sessions where token_hash=p_token and expires_at>now();
 if s is null then raise exception 'Sessão ausente ou expirada' using errcode='28000'; end if; return s;
end $$;
create function public.challenge_web_session(p_token text,p_peer text) returns uuid language plpgsql security invoker set search_path='' as $$
declare s uuid; begin
 perform pg_advisory_xact_lock(hashtext('challenge_web_session'));
 if p_token !~ '^[0-9a-f]{64}$' or p_peer !~ '^[0-9a-f]{64}$' then raise exception 'Hash inválido'; end if;
 if (select count(*) from access.web_sessions where created_at>now()-interval '1 hour' and peer_hash=p_peer)>=30
 or (select count(*) from access.web_sessions where created_at>now()-interval '1 day')>=500 then raise exception 'Limite de sessões atingido; tente mais tarde'; end if;
 insert into access.web_sessions(token_hash,peer_hash) values(p_token,p_peer) returning id into s; return s;
end $$;

alter table operations.decisions alter column actor_user_id drop not null;
alter table operations.decisions alter column evidence_id drop not null;
alter table operations.decisions add column actor_session_id uuid references access.web_sessions(id),
 add column actor_display_name text, add column request_key text,
 add column snapshot_id uuid, add column evidence_context jsonb not null default '{}',
 add constraint decision_snapshot_fk foreign key(workspace_id,snapshot_id) references analytics.account_snapshots(workspace_id,id),
 add constraint decision_actor_required check(actor_user_id is not null or actor_session_id is not null),
 add constraint decision_evidence_required check(evidence_id is not null or snapshot_id is not null),
 add constraint decision_request_unique unique(actor_session_id,request_key);
alter table operations.action_history alter column actor_user_id drop not null;
alter table operations.action_history add column actor_session_id uuid references access.web_sessions(id),
 add constraint history_actor_required check(actor_user_id is not null or actor_session_id is not null);
create index decisions_session_idx on operations.decisions(actor_session_id);
create index decisions_snapshot_idx on operations.decisions(workspace_id,snapshot_id);
create index history_session_idx on operations.action_history(actor_session_id);

create function operations.guard_append_only() returns trigger language plpgsql security invoker set search_path='' as $$
begin raise exception 'Registro de decisão/histórico é imutável'; end $$;
create trigger decision_append_only before update or delete on operations.decisions for each row execute function operations.guard_append_only();
create trigger history_append_only before update or delete on operations.action_history for each row execute function operations.guard_append_only();

create function public.challenge_web_decide(p_token text,p_request text,p_evidence uuid,p_snapshot uuid,p_title text,p_rationale text,p_actor text,p_action text,p_responsible text,p_due date)
 returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid; ws uuid; ev analytics.evidence_items; snap analytics.account_snapshots; run_uuid uuid; context jsonb; d uuid; a uuid;
begin
 sess=access.web_session(p_token);select id into strict ws from access.workspaces where slug='ravenstack';
 perform pg_advisory_xact_lock(hashtext(sess::text||p_request));
 select id into d from operations.decisions where actor_session_id=sess and request_key=p_request;
 if d is not null then
   if exists(select 1 from operations.decisions x join operations.actions y on y.decision_id=x.id where x.id=d and
     (x.title<>trim(p_title) or x.rationale<>trim(p_rationale) or x.evidence_id is distinct from p_evidence or x.snapshot_id is distinct from p_snapshot
      or x.actor_display_name<>trim(p_actor) or y.title<>trim(p_action) or y.responsible<>trim(p_responsible) or y.due_date<>p_due)) then raise exception 'Chave de repetição com conteúdo diferente'; end if;
   return jsonb_build_object('decision_id',d,'action_id',(select id from operations.actions where decision_id=d limit 1));
 end if;
 if p_request is null or length(p_request) not between 8 and 100 or length(trim(p_title)) not between 3 and 180
 or length(trim(p_rationale)) not between 10 and 3000 or length(trim(p_actor)) not between 2 and 100
 or length(trim(p_action)) not between 3 and 180 or length(trim(p_responsible)) not between 2 and 100
 or p_due is null then raise exception 'Preencha decisão, justificativa, autor declarado, ação, responsável e prazo'; end if;
 if (select count(*) from operations.decisions where actor_session_id=sess and created_at>now()-interval '1 day')>=30 then raise exception 'Limite diário de decisões atingido'; end if;
 if p_snapshot is not null then
   select * into strict snap from analytics.account_snapshots where id=p_snapshot and workspace_id=ws;
   run_uuid=snap.run_id;context=jsonb_build_object('snapshot',to_jsonb(snap));
 end if;
 if p_evidence is not null then
   select * into strict ev from analytics.evidence_items where id=p_evidence and workspace_id=ws;
   if run_uuid is not null and ev.run_id<>run_uuid then raise exception 'Evidência e conta de versões diferentes'; end if;
   run_uuid=ev.run_id;context=coalesce(context,'{}')||jsonb_build_object('evidence',to_jsonb(ev));
 end if;
 if run_uuid is null or not exists(select 1 from analytics.analysis_runs where id=run_uuid and status='published') then raise exception 'Selecionar evidência publicada'; end if;
 context=context||jsonb_build_object('run',(select to_jsonb(r) from analytics.analysis_runs r where id=run_uuid),'identity','declared_not_verified');
 insert into operations.decisions(workspace_id,evidence_id,snapshot_id,title,rationale,actor_session_id,actor_display_name,request_key,evidence_context)
 values(ws,p_evidence,p_snapshot,trim(p_title),trim(p_rationale),sess,trim(p_actor),p_request,context) returning id into d;
 insert into operations.actions(workspace_id,decision_id,title,responsible,due_date) values(ws,d,trim(p_action),trim(p_responsible),p_due) returning id into a;
 insert into operations.action_history(workspace_id,action_id,actor_session_id,to_status,revision) values(ws,a,sess,'pending',0);
 return jsonb_build_object('decision_id',d,'action_id',a);
end $$;
create function public.challenge_web_transition(p_token text,p_action uuid,p_revision integer,p_status text,p_result text)
 returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid; a operations.actions; begin
 sess=access.web_session(p_token);
 select x.* into strict a from operations.actions x join access.workspaces w on w.id=x.workspace_id where x.id=p_action and w.slug='ravenstack' for update of x;
 if a.revision<>p_revision then raise exception 'Ação alterada por outra sessão. Atualize e tente novamente.' using errcode='40001'; end if;
 if p_status not in('in_progress','completed','cancelled') or a.status in('completed','cancelled') or p_status=a.status then raise exception 'Transição não permitida'; end if;
 if p_status in('completed','cancelled') and coalesce(length(trim(p_result)),0)<10 then raise exception 'Informe um resultado/motivo com pelo menos 10 caracteres'; end if;
 if length(p_result)>3000 then raise exception 'Resultado excede 3000 caracteres'; end if;
 update operations.actions set status=p_status,result_note=nullif(trim(p_result),''),revision=revision+1,updated_at=now() where id=a.id;
 insert into operations.action_history(workspace_id,action_id,actor_session_id,from_status,to_status,result_note,revision)
 values(a.workspace_id,a.id,sess,a.status,p_status,nullif(trim(p_result),''),a.revision+1);
 return jsonb_build_object('id',a.id,'revision',a.revision+1,'status',p_status);
end $$;

create table ingest.web_uploads (
 id uuid primary key default gen_random_uuid(), session_id uuid not null references access.web_sessions(id),
 workspace_id uuid not null references access.workspaces(id), parent_run_id uuid not null references analytics.analysis_runs(id),
 source_type text not null, filename text not null, file_hash text not null, original_bytes bytea not null,
 headers jsonb not null, packed_rows jsonb not null, checks jsonb not null, preview jsonb not null,
 reference_date date not null, stage text not null default 'preview' check(stage in('preview','processing','verified','published')),
 version_id uuid references analytics.dataset_versions(id), file_id uuid references ingest.source_files(id),
 processed_rows integer not null default 0, run_id uuid references analytics.analysis_runs(id),
 created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
 check(octet_length(original_bytes)<=8388608),check(jsonb_array_length(packed_rows) between 1 and 50000)
);
create index web_upload_session_idx on ingest.web_uploads(session_id,created_at);
create index web_upload_workspace_idx on ingest.web_uploads(workspace_id);
create index web_upload_parent_idx on ingest.web_uploads(parent_run_id);
create index web_upload_version_idx on ingest.web_uploads(version_id);
create index web_upload_file_idx on ingest.web_uploads(file_id);
create index web_upload_run_idx on ingest.web_uploads(run_id);
alter table ingest.web_uploads enable row level security;
create policy backend_only on ingest.web_uploads to service_role using(true) with check(true);

create function public.challenge_web_dashboard(p_token text) returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid; ws access.workspaces; r analytics.analysis_runs; begin
 sess=access.web_session(p_token);select * into strict ws from access.workspaces where slug='ravenstack';select * into strict r from analytics.analysis_runs where id=ws.current_run_id;
 return jsonb_build_object('workspace',jsonb_build_object('name',ws.name),'run',to_jsonb(r),
 'accounts',(select coalesce(jsonb_agg(to_jsonb(s) order by account_name),'[]') from analytics.account_snapshots s where run_id=r.id),
 'evidence',(select coalesce(jsonb_agg(to_jsonb(e)),'[]') from analytics.evidence_items e where run_id=r.id),
 'quality',(select coalesce(jsonb_agg(to_jsonb(q) order by affected_count desc,code),'[]') from analytics.quality_checks q where version_id=r.version_id),
 'sources',(select jsonb_agg(jsonb_build_object('source_type',f.source_type,'filename',f.filename,'file_hash',f.file_hash,'rows',f.expected_rows,'bytes',f.expected_bytes,'received_at',f.created_at,'status',f.status,'file_id',f.id)) from analytics.version_sources v join ingest.source_files f on f.id=v.file_id where v.version_id=r.version_id),
 'decisions',(select coalesce(jsonb_agg(to_jsonb(d) order by d.created_at desc),'[]') from operations.decisions d where workspace_id=ws.id),
 'actions',(select coalesce(jsonb_agg(to_jsonb(a) order by due_date),'[]') from operations.actions a where workspace_id=ws.id),
 'history',(select coalesce(jsonb_agg(to_jsonb(h) order by created_at),'[]') from operations.action_history h where workspace_id=ws.id),
 'versions',(select coalesce(jsonb_agg(to_jsonb(v) order by created_at desc),'[]') from analytics.analysis_runs v where workspace_id=ws.id and status='published'),
 'uploads',(select coalesce(jsonb_agg(jsonb_build_object('id',u.id,'filename',filename,'source_type',source_type,'stage',stage,'processed_rows',processed_rows,'rows',jsonb_array_length(packed_rows),'created_at',created_at,'preview',preview) order by created_at desc),'[]') from ingest.web_uploads u where session_id=sess and stage<>'preview'));
end $$;
create function public.challenge_web_sources(p_token text) returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid; r analytics.analysis_runs; begin
 sess=access.web_session(p_token);select x.* into strict r from analytics.analysis_runs x join access.workspaces w on w.current_run_id=x.id where w.slug='ravenstack';
 return jsonb_build_object('run',to_jsonb(r),'sources',(select jsonb_object_agg(v.source_type,q.rows) from analytics.version_sources v join lateral (
 select jsonb_agg(x.content order by x.row_number) as rows from ingest.raw_rows x where x.file_id=v.file_id) q on true where v.version_id=r.version_id));
end $$;
create function public.challenge_web_stage(p_token text,p_parent uuid,p_source text,p_filename text,p_hash text,p_base64 text,p_headers jsonb,p_rows jsonb,p_checks jsonb,p_preview jsonb,p_reference date)
 returns uuid language plpgsql security invoker set search_path='' as $$
declare sess uuid; ws uuid; upload uuid; bytes bytea; begin
 sess=access.web_session(p_token);select id into strict ws from access.workspaces where slug='ravenstack';
 if p_parent is distinct from (select current_run_id from access.workspaces where id=ws) then raise exception 'Os dados mudaram; gere uma nova prévia.'; end if;
 if not exists(select 1 from ingest.source_contracts where source_type=p_source and contract_version='1.0.0') then raise exception 'Fonte desconhecida'; end if;
 if (select count(*) from ingest.web_uploads where session_id=sess and created_at>now()-interval '1 day')>=10
 or (select count(*) from ingest.web_uploads where created_at>now()-interval '1 day')>=80 then raise exception 'Limite diário de arquivos atingido'; end if;
 bytes=decode(p_base64,'base64');if encode(sha256(bytes),'hex')<>p_hash then raise exception 'Hash divergente'; end if;
 if jsonb_array_length(p_checks)<>89 then raise exception 'Auditoria incompleta'; end if;
 insert into ingest.web_uploads(session_id,workspace_id,parent_run_id,source_type,filename,file_hash,original_bytes,headers,packed_rows,checks,preview,reference_date)
 values(sess,ws,p_parent,p_source,left(p_filename,180),p_hash,bytes,p_headers,p_rows,p_checks,p_preview,p_reference) returning id into upload;return upload;
end $$;
create function public.challenge_web_begin(p_token text,p_upload uuid) returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid; u ingest.web_uploads; manifest jsonb; result jsonb; f uuid; begin
 sess=access.web_session(p_token);select * into strict u from ingest.web_uploads where id=p_upload and session_id=sess for update;
 if u.stage<>'preview' then return jsonb_build_object('stage',u.stage,'version_id',u.version_id); end if;
 perform 1 from access.workspaces where id=u.workspace_id for update;
 if u.parent_run_id is distinct from (select current_run_id from access.workspaces where id=u.workspace_id) then raise exception 'Versão mudou; refaça a prévia para não sobrescrever atualização de outra sessão'; end if;
 select jsonb_agg(case when vs.source_type=u.source_type then jsonb_build_object('source_type',u.source_type,'contract_version','1.0.0','filename',u.filename,'file_hash',u.file_hash,'expected_rows',jsonb_array_length(u.packed_rows),'expected_bytes',octet_length(u.original_bytes))
 else jsonb_build_object('source_type',f.source_type,'contract_version',f.contract_version,'filename',f.filename,'file_hash',f.file_hash,'expected_rows',f.expected_rows,'expected_bytes',f.expected_bytes) end)
 into manifest from analytics.analysis_runs r join analytics.version_sources vs on vs.version_id=r.version_id join ingest.source_files f on f.id=vs.file_id where r.id=u.parent_run_id;
 result=public.challenge_start_import(u.workspace_id,encode(sha256(convert_to('web:'||u.id::text,'UTF8')),'hex'),'Atualização de '||u.source_type,manifest);
 select (x->>'file_id')::uuid into strict f from jsonb_array_elements(result->'files') x where x->>'source_type'=u.source_type;
 if (select status from ingest.source_files where id=f)='loading' then
   insert into ingest.file_chunks(workspace_id,file_id,chunk_index,data)
   select u.workspace_id,f,i,substring(u.original_bytes from i*40000+1 for 40000) from generate_series(0,(octet_length(u.original_bytes)-1)/40000) i
   where not exists(select 1 from ingest.file_chunks c where c.file_id=f and c.chunk_index=i);
 end if;
 update ingest.web_uploads set version_id=(result->>'version_id')::uuid,file_id=f,stage=case when (select status from ingest.source_files where id=f)='verified' then 'verified' else 'processing' end,updated_at=now() where id=u.id;
 return jsonb_build_object('stage','processing','version_id',result->>'version_id');
end $$;
create function public.challenge_web_advance(p_token text,p_upload uuid) returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid; u ingest.web_uploads; payload jsonb; total integer; n integer; r uuid; begin
 sess=access.web_session(p_token);select * into strict u from ingest.web_uploads where id=p_upload and session_id=sess for update;
 total=jsonb_array_length(u.packed_rows);
 if u.stage='preview' then raise exception 'Confirmar prévia antes de processar'; end if;
 if u.stage='published' then return jsonb_build_object('stage','published','run_id',u.run_id,'processed',total,'total',total); end if;
 if u.stage='processing' then
   select jsonb_build_object('headers',u.headers,'rows',jsonb_agg(x.value order by x.ordinality)) into payload from jsonb_array_elements(u.packed_rows) with ordinality x where x.ordinality>u.processed_rows and x.ordinality<=u.processed_rows+300;
   n=ingest.append_rows(u.file_id,payload);
   update ingest.web_uploads set processed_rows=least(total,processed_rows+300),updated_at=now() where id=u.id returning * into u;
   if u.processed_rows=total then perform ingest.verify_file(u.file_id);update ingest.web_uploads set stage='verified' where id=u.id;u.stage='verified';end if;
   return jsonb_build_object('stage',u.stage,'processed',u.processed_rows,'total',total);
 end if;
 perform 1 from access.workspaces where id=u.workspace_id for update;
 if u.parent_run_id is distinct from (select current_run_id from access.workspaces where id=u.workspace_id) then raise exception 'Outra versão foi publicada. Gere uma nova prévia; a versão atual foi preservada.'; end if;
 r=public.challenge_finish_import(u.version_id,u.reference_date,u.checks);
 update ingest.web_uploads set stage='published',run_id=r,processed_rows=total,updated_at=now() where id=u.id;
 return jsonb_build_object('stage','published','run_id',r,'processed',total,'total',total);
end $$;

-- No client can execute privileged RPCs or access raw records directly.
grant usage on schema access,ingest,operations,analytics,core to service_role;
grant all on access.web_sessions,ingest.web_uploads to service_role;
do $$ declare f record;begin
 for f in select p.oid::regprocedure as signature from pg_proc p join pg_namespace n on n.oid=p.pronamespace
 where (n.nspname='public' and p.proname like 'challenge_web_%') or (n.nspname='access' and p.proname='web_session') or (n.nspname='operations' and p.proname='guard_append_only') loop
 execute 'revoke execute on function '||f.signature||' from public,anon,authenticated';
 execute 'grant execute on function '||f.signature||' to service_role'; end loop;
end $$;
