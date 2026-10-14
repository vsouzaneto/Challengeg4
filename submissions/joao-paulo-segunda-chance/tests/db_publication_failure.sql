-- Incomplete candidate cannot replace the current published run.
begin;
do $test$
declare ws uuid; previous_run uuid; b uuid; v uuid; r uuid; blocked boolean=false;
begin
  select id,current_run_id into strict ws,previous_run from access.workspaces where slug='ravenstack';
  if previous_run is null then raise exception 'Teste requer publicação anterior'; end if;
  insert into ingest.import_batches(workspace_id,request_hash,label,actor)
    values(ws,'qa-'||gen_random_uuid(),'Synthetic incomplete candidate','test') returning id into b;
  insert into analytics.dataset_versions(workspace_id,batch_id) values(ws,b) returning id into v;
  insert into analytics.analysis_runs(workspace_id,version_id,reference_date,status)
    values(ws,v,'2024-01-01','ready') returning id into r;
  begin perform analytics.publish_run(r);
  exception when raise_exception then blocked=true;
  end;
  if not blocked then raise exception 'Publicação de candidata incompleta foi permitida'; end if;
  if (select current_run_id from access.workspaces where id=ws)<>previous_run then
    raise exception 'Falha alterou a publicação anterior';
  end if;
end $test$;
rollback;
