-- Authenticated upload ownership survives logout/login; anonymous jobs are not claimed.
create function access.owns_upload(p_session uuid,p_owner uuid,p_actor uuid,p_workspace uuid) returns boolean language sql stable security invoker set search_path='' as $$
 select exists(select 1 from access.web_sessions s where s.id=p_session and s.revoked_at is null and s.expires_at>now() and
 case when s.user_id is null then not access.authentication_required() and p_actor is null and p_owner=p_session
 else access.authenticated_web_session(s.token_hash)=s.id and s.user_id=p_actor and s.workspace_id=p_workspace end)
$$;
revoke execute on function access.owns_upload(uuid,uuid,uuid,uuid) from public,anon,authenticated;
grant execute on function access.owns_upload(uuid,uuid,uuid,uuid) to service_role;
create or replace function public.challenge_web_dashboard(p_token text) returns jsonb language plpgsql security invoker set search_path='' as $$
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
 'uploads',(select coalesce(jsonb_agg(jsonb_build_object('id',u.id,'filename',filename,'source_type',source_type,'stage',stage,'processed_rows',processed_rows,'rows',jsonb_array_length(packed_rows),'created_at',created_at,'preview',preview) order by created_at desc),'[]') from ingest.web_uploads u where access.owns_upload(sess,u.session_id,u.actor_user_id,u.workspace_id) and stage<>'preview'));
end $$;

create or replace function public.challenge_web_begin(p_token text,p_upload uuid) returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid; u ingest.web_uploads; manifest jsonb; result jsonb; f uuid; begin
 sess=access.web_session(p_token);select * into strict u from ingest.web_uploads where id=p_upload and access.owns_upload(sess,session_id,actor_user_id,workspace_id) for update;
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

create or replace function public.challenge_web_advance(p_token text,p_upload uuid) returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid; u ingest.web_uploads; payload jsonb; total integer; n integer; r uuid; begin
 sess=access.web_session(p_token);select * into strict u from ingest.web_uploads where id=p_upload and access.owns_upload(sess,session_id,actor_user_id,workspace_id) for update;
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

