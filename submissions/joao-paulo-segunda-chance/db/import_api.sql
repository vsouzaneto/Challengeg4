-- Backend-only RPC interfaces. No privileged key belongs in a browser.
create function public.challenge_start_import(p_workspace uuid,p_request_hash text,p_label text,p_sources jsonb)
returns jsonb language plpgsql security invoker set search_path='' as $$
declare b uuid; v uuid; f uuid; x jsonb;
begin
  perform 1 from access.workspaces where id=p_workspace for update;
  if not found then raise exception 'Workspace inexistente'; end if;
  if jsonb_array_length(p_sources)<>5 or (select count(distinct value->>'source_type') from jsonb_array_elements(p_sources))<>5 then
    raise exception 'Manifesto precisa conter as cinco fontes';
  end if;
  insert into ingest.import_batches(workspace_id,request_hash,label,actor)
    values(p_workspace,p_request_hash,p_label,'authorized_backend') on conflict(workspace_id,request_hash) do nothing;
  select id into strict b from ingest.import_batches where workspace_id=p_workspace and request_hash=p_request_hash;
  insert into analytics.dataset_versions(workspace_id,batch_id,parent_version_id)
    select p_workspace,b,r.version_id from access.workspaces w left join analytics.analysis_runs r on r.id=w.current_run_id
    where w.id=p_workspace on conflict(batch_id) do nothing;
  select id into strict v from analytics.dataset_versions where batch_id=b;
  if (select status from analytics.dataset_versions where id=v)='candidate' then
    for x in select value from jsonb_array_elements(p_sources) loop
      insert into ingest.source_files(workspace_id,batch_id,source_type,contract_version,filename,file_hash,expected_rows,expected_bytes)
        values(p_workspace,b,x->>'source_type',x->>'contract_version',x->>'filename',x->>'file_hash',
          (x->>'expected_rows')::integer,(x->>'expected_bytes')::integer)
        on conflict(workspace_id,source_type,contract_version,file_hash) do nothing;
      select id into strict f from ingest.source_files where workspace_id=p_workspace and source_type=x->>'source_type'
        and contract_version=x->>'contract_version' and file_hash=x->>'file_hash';
      insert into analytics.version_sources(workspace_id,version_id,source_type,file_id)
        values(p_workspace,v,x->>'source_type',f) on conflict(version_id,source_type) do nothing;
    end loop;
  end if;
  return jsonb_build_object('batch_id',b,'version_id',v,'files',(select jsonb_agg(jsonb_build_object(
    'file_id',f.id,'source_type',f.source_type,'status',f.status))
    from analytics.version_sources vs join ingest.source_files f on f.id=vs.file_id where vs.version_id=v));
end $$;

create function public.challenge_append_rows(p_file uuid,p_payload jsonb) returns integer
language sql security invoker set search_path='' as $$ select ingest.append_rows(p_file,p_payload) $$;
create function public.challenge_append_file_chunk(p_file uuid,p_index integer,p_text text) returns integer
language sql security invoker set search_path='' as $$ select ingest.append_file_chunk(p_file,p_index,p_text) $$;
create function public.challenge_verify_file(p_file uuid) returns void
language sql security invoker set search_path='' as $$ select ingest.verify_file(p_file) $$;

create function public.challenge_finish_import(p_version uuid,p_reference date,p_checks jsonb) returns uuid
language plpgsql security invoker set search_path='' as $$
declare ws uuid; r uuid; state text;
begin
  select workspace_id,status into strict ws,state from analytics.dataset_versions where id=p_version for update;
  if state='published' then
    select id into strict r from analytics.analysis_runs where version_id=p_version and reference_date=p_reference
      and status='published' order by published_at desc limit 1;
    return r;
  end if;
  if exists(select 1 from analytics.version_sources vs join ingest.raw_rows raw on raw.file_id=vs.file_id
    where vs.version_id=p_version and (raw.normalized_content is null or jsonb_array_length(raw.validation_errors)>0)) then
    raise exception 'Contrato de fonte inválido; original preservado para revisão';
  end if;
  perform analytics.promote_version(p_version);
  insert into analytics.quality_checks(workspace_id,version_id,code,kind,affected_count,denominator,interpretation,policy,examples)
    select ws,p_version,x->>'code',x->>'kind',(x->>'count')::integer,(x->>'denominator')::integer,
      x->>'interpretation',x->>'policy',coalesce(x->'examples','[]'::jsonb)
    from jsonb_array_elements(p_checks) x on conflict(version_id,code) do nothing;
  r=analytics.build_run(p_version,p_reference);
  perform analytics.publish_run(r);
  return r;
end $$;
revoke execute on function public.challenge_start_import(uuid,text,text,jsonb),
  public.challenge_append_rows(uuid,jsonb),public.challenge_append_file_chunk(uuid,integer,text),
  public.challenge_verify_file(uuid),public.challenge_finish_import(uuid,date,jsonb) from public,anon,authenticated;
grant execute on function public.challenge_start_import(uuid,text,text,jsonb),
  public.challenge_append_rows(uuid,jsonb),public.challenge_append_file_chunk(uuid,integer,text),
  public.challenge_verify_file(uuid),public.challenge_finish_import(uuid,date,jsonb) to service_role;
