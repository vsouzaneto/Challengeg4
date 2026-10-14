-- Synthetic auth identities exist only inside this rolled-back transaction.
begin;
do $setup$
declare ws uuid; b uuid; v uuid; r uuid; admitted uuid; outsider uuid;
begin
  admitted=gen_random_uuid(); outsider=gen_random_uuid();
  insert into auth.users(id,email) values(admitted,admitted||'@qa.invalid'),(outsider,outsider||'@qa.invalid');
  insert into access.workspaces(slug,name) values('qa-'||gen_random_uuid(),'Synthetic RLS QA') returning id into ws;
  insert into access.memberships values(ws,admitted,'reader',true);
  insert into ingest.import_batches(workspace_id,request_hash,label,actor)
    values(ws,'qa-'||gen_random_uuid(),'Synthetic RLS QA','test') returning id into b;
  insert into analytics.dataset_versions(workspace_id,batch_id) values(ws,b) returning id into v;
  insert into analytics.analysis_runs(workspace_id,version_id,reference_date,status)
    values(ws,v,'2024-01-01','building') returning id into r;
  insert into analytics.account_snapshots(workspace_id,run_id,account_id,account_name,signup_date,industry,country,
    cadastral_churn,has_any_event,churn_events,reactivation_events,reconciliation_state,open_contracts,contract_mrr,
    coherent_usage_rows_30d,coherent_usage_rows_previous_30d,eligible_tickets_30d,closed_tickets_30d,satisfaction_responses)
    values(ws,r,'SYNTHETIC-QA','Synthetic QA','2024-01-01','QA','QA',false,false,0,0,'unknown',0,0,0,0,0,0,0);
  update analytics.analysis_runs set status='published' where id=r;
  update access.workspaces set current_run_id=r where id=ws;
  perform set_config('qa.workspace',ws::text,true);
  perform set_config('qa.admitted',admitted::text,true);
  perform set_config('qa.outsider',outsider::text,true);
end $setup$;

set local role authenticated;
do $test$
declare ws uuid; blocked boolean;
begin
  ws=current_setting('qa.workspace')::uuid;
  perform set_config('request.jwt.claim.sub',current_setting('qa.admitted'),true);
  if not access.is_member(ws) then raise exception 'Membro autorizado não reconhecido'; end if;
  if (select count(*) from analytics.account_snapshots where workspace_id=ws)<>1 then
    raise exception 'Membro não conseguiu ler snapshot autorizado';
  end if;
  if public.challenge_dashboard(ws) is null then raise exception 'Dashboard do membro indisponível'; end if;
  blocked=false;
  begin perform 1 from ingest.raw_rows limit 1;
  exception when insufficient_privilege then blocked=true;
  end;
  if not blocked then raise exception 'Leitor conseguiu acessar dados brutos'; end if;
  if has_function_privilege('authenticated','public.challenge_finish_import(uuid,date,jsonb)','EXECUTE') then
    raise exception 'Cliente autenticado tem permissão de publicar importação';
  end if;
  perform set_config('request.jwt.claim.sub',current_setting('qa.outsider'),true);
  if access.is_member(ws) then raise exception 'Não membro recebeu membership'; end if;
  if (select count(*) from analytics.account_snapshots where workspace_id=ws)<>0 then
    raise exception 'Não membro conseguiu ler snapshot';
  end if;
  if public.challenge_dashboard(ws) is not null then raise exception 'Não membro conseguiu ler dashboard'; end if;
  if has_function_privilege('anon','public.challenge_dashboard(uuid)','EXECUTE') then
    raise exception 'Anonymous pode invocar dashboard';
  end if;
end $test$;
reset role;
rollback;
