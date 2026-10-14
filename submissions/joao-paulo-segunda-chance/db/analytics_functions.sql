create function analytics.build_run(p_version uuid,p_reference date) returns uuid language plpgsql security invoker
set search_path='' as $$
declare ws uuid; run_uuid uuid; current_state text;
begin
  select workspace_id,status into strict ws,current_state from analytics.dataset_versions where id=p_version;
  if p_reference is null or current_state='failed' then raise exception 'Versão/data não elegível'; end if;
  if not exists(select 1 from core.accounts where version_id=p_version) then raise exception 'Promover fontes antes de calcular'; end if;
  insert into analytics.analysis_runs(workspace_id,version_id,reference_date)
    values(ws,p_version,p_reference) returning id into run_uuid;

  insert into analytics.account_snapshots(
    workspace_id,run_id,account_id,account_name,signup_date,industry,country,cadastral_churn,
    has_any_event,churn_events,reactivation_events,reconciliation_state,open_contracts,contract_mrr,
    coherent_usage_rows_30d,coherent_usage_rows_previous_30d,recorded_usage_30d,recorded_usage_previous_30d,
    usage_drop_ratio,coverage_state,eligible_tickets_30d,closed_tickets_30d,satisfaction_responses,
    mean_satisfaction,mean_resolution_hours,quality_flags)
  with contract_summary as (
    select account_id,
      count(*) filter(where start_date<=p_reference and (end_date is null or end_date>p_reference))::integer as open_count,
      coalesce(sum(mrr_amount) filter(where start_date<=p_reference and (end_date is null or end_date>p_reference) and not is_trial),0) as mrr
    from core.subscriptions where version_id=p_version group by account_id
  ), conflicts as (
    select usage_id from core.feature_usage where version_id=p_version group by usage_id having count(*)>1
  ), eligible_usage as (
    select u.*,s.account_id from core.feature_usage u
      join core.subscriptions s on s.version_id=u.version_id and s.subscription_id=u.subscription_id
      join core.accounts a on a.version_id=u.version_id and a.account_id=s.account_id
    where u.version_id=p_version and u.usage_date>=s.start_date and u.usage_date>=a.signup_date
      and (s.end_date is null or u.usage_date<s.end_date) and u.usage_date<=p_reference
      and not exists(select 1 from conflicts c where c.usage_id=u.usage_id)
  ), usage_summary as (
    select account_id,
      count(*) filter(where usage_date>p_reference-30)::integer as recent_rows,
      count(*) filter(where usage_date>p_reference-60 and usage_date<=p_reference-30)::integer as prior_rows,
      sum(usage_count) filter(where usage_date>p_reference-30) as recent_count,
      sum(usage_count) filter(where usage_date>p_reference-60 and usage_date<=p_reference-30) as prior_count
    from eligible_usage group by account_id
  ), event_summary as (
    select account_id,count(*)::integer as any_count,
      count(*) filter(where not is_reactivation)::integer as cancel_count,
      count(*) filter(where is_reactivation)::integer as react_count
    from core.churn_events where version_id=p_version and churn_date<=p_reference group by account_id
  ), support_summary as (
    select t.account_id,count(*)::integer as ticket_count,
      count(*) filter(where closed_at<p_reference+1)::integer as closed_count,
      count(*) filter(where closed_at<p_reference+1 and satisfaction_score between 1 and 5)::integer as response_count,
      avg(satisfaction_score) filter(where closed_at<p_reference+1 and satisfaction_score between 1 and 5) as mean_score,
      avg(resolution_time_hours) filter(where closed_at<p_reference+1
        and first_response_time_minutes<=extract(epoch from (closed_at-submitted_at))/60
        and resolution_time_hours>=0 and abs(resolution_time_hours-extract(epoch from (closed_at-submitted_at))/3600)<0.000001) as mean_resolution
    from core.support_tickets t join core.accounts a on a.version_id=t.version_id and a.account_id=t.account_id
    where t.version_id=p_version and t.submitted_at>=a.signup_date
      and t.submitted_at<p_reference+1 and t.submitted_at>=p_reference-29
    group by t.account_id
  )
  select ws,run_uuid,a.account_id,a.account_name,a.signup_date,a.industry,a.country,a.churn_flag,
    coalesce(e.any_count,0)>0,coalesce(e.cancel_count,0),coalesce(e.react_count,0),
    case when a.churn_flag and coalesce(e.any_count,0)=0 then 'flag_without_event'
         when a.churn_flag and coalesce(e.cancel_count,0)=0 then 'flag_with_reactivation_only'
         when not a.churn_flag and coalesce(e.cancel_count,0)>0 then 'historical_event_without_flag'
         when a.churn_flag and coalesce(e.cancel_count,0)>0 then 'observed_agreement'
         else 'no_observed_churn_history' end,
    coalesce(s.open_count,0),coalesce(s.mrr,0),coalesce(u.recent_rows,0),coalesce(u.prior_rows,0),
    u.recent_count,u.prior_count,null,'not_confirmed',coalesce(t.ticket_count,0),coalesce(t.closed_count,0),
    coalesce(t.response_count,0),t.mean_score,t.mean_resolution,
    to_jsonb(array_remove(array[
      case when a.churn_flag and coalesce(e.any_count,0)=0 then 'missing_churn_event' end,
      case when a.churn_flag and coalesce(e.cancel_count,0)=0 and coalesce(e.any_count,0)>0 then 'reactivation_only' end,
      case when a.churn_flag and coalesce(s.open_count,0)>0 then 'flag_with_open_contract' end,
      case when not a.churn_flag and coalesce(e.cancel_count,0)>0 then 'historical_event_without_flag' end,
      case when coalesce(u.recent_rows,0)=0 then 'recent_usage_not_observed' end,
      case when coalesce(u.prior_rows,0)=0 then 'baseline_usage_not_observed' end,
      case when coalesce(t.ticket_count,0)>coalesce(t.response_count,0) then 'incomplete_satisfaction' end,
      'telemetry_coverage_not_confirmed','attribute_history_not_available'
    ],null))
  from core.accounts a left join contract_summary s using(account_id) left join usage_summary u using(account_id)
    left join event_summary e using(account_id) left join support_summary t using(account_id)
  where a.version_id=p_version and a.signup_date<=p_reference;

  insert into analytics.evidence_items(workspace_id,run_id,snapshot_id,rule_code,rule_version,state,category,summary,details)
  select ws,run_uuid,id,'churn_reconciliation','1.0.0','indeterminate','data_quality',
    'Validar a divergência entre cadastro, eventos e contratos antes de definir o estado da conta.',
    jsonb_build_object('account_id',account_id,'reconciliation_state',reconciliation_state,
      'cadastral_flag',cadastral_churn,'observed_churn_events',churn_events,'open_contracts',open_contracts,
      'reference_date',p_reference,'definition','event_history_is_not_current_status')
  from analytics.account_snapshots where run_id=run_uuid
    and (reconciliation_state in ('flag_without_event','flag_with_reactivation_only','historical_event_without_flag')
      or (cadastral_churn and open_contracts>0));

  insert into analytics.evidence_items(workspace_id,run_id,rule_code,rule_version,state,category,summary,details)
  select ws,run_uuid,code,'1.0.0','indeterminate','data_quality',interpretation,
    jsonb_build_object('affected_count',affected_count,'denominator',denominator,'policy',policy,'examples',examples,
      'scope','entire_source_version_not_reference_window')
  from analytics.quality_checks where version_id=p_version and affected_count>0;

  insert into analytics.evidence_items(workspace_id,run_id,rule_code,rule_version,state,category,summary,details)
    values(ws,run_uuid,'usage_coverage','1.0.0','indeterminate','diagnostic',
      'Cobertura de telemetria não confirmada: ausência de registro não significa ausência de uso.',
      '{"automated_retention_alerts":false,"required":"explicit_extraction_coverage","financial_measure":"contract_exposure_not_estimated_loss"}');

  update analytics.analysis_runs set metrics=(select jsonb_build_object(
    'accounts',count(*),'cadastral_churn_accounts',count(*) filter(where cadastral_churn),
    'accounts_with_open_contracts',count(*) filter(where open_contracts>0),
    'contract_mrr',sum(contract_mrr),'recorded_coherent_usage_30d',sum(recorded_usage_30d),
    'eligible_tickets_30d',sum(eligible_tickets_30d),'satisfaction_responses_30d',sum(satisfaction_responses),
    'reconciliation_needed',count(*) filter(where reconciliation_state in ('flag_without_event','flag_with_reactivation_only','historical_event_without_flag')),
    'automated_retention_alerts',false,'telemetry_coverage','not_confirmed')
    from analytics.account_snapshots where run_id=run_uuid),status='ready' where id=run_uuid;
  return run_uuid;
end $$;

create function analytics.publish_run(p_run uuid) returns void language plpgsql security invoker set search_path='' as $$
declare r analytics.analysis_runs; v analytics.dataset_versions; source_count integer;
begin
  select * into strict r from analytics.analysis_runs where id=p_run for update;
  perform 1 from access.workspaces where id=r.workspace_id for update;
  if r.status='published' then return; end if;
  if r.status<>'ready' then raise exception 'Execução incompleta'; end if;
  select * into strict v from analytics.dataset_versions where id=r.version_id for update;
  select count(*) into source_count from analytics.version_sources vs join ingest.source_files f on f.id=vs.file_id
    where vs.version_id=r.version_id and f.status='verified';
  if source_count<>5 then raise exception 'Manifesto incompleto'; end if;
  if (select count(*) from analytics.account_snapshots where run_id=p_run)<>
     (select count(*) from core.accounts where version_id=r.version_id and signup_date<=r.reference_date) then
    raise exception 'Snapshots incompletos';
  end if;
  if not exists(select 1 from analytics.quality_checks where version_id=r.version_id) then
    raise exception 'Auditoria obrigatória ausente';
  end if;
  update analytics.dataset_versions set status='published' where id=r.version_id and status='candidate';
  update ingest.import_batches set status='published' where id=v.batch_id;
  update analytics.analysis_runs set status='published',published_at=now() where id=p_run;
  update access.workspaces set current_run_id=p_run where id=r.workspace_id;
end $$;

-- Finalized metadata also stays immutable. Only legal transition ready→published is allowed.
create function analytics.guard_metadata() returns trigger language plpgsql security invoker set search_path='' as $$
begin
  if tg_table_name='dataset_versions' and old.status='published' then
    raise exception 'Manifesto publicado é imutável';
  end if;
  if tg_table_name='analysis_runs' and old.status='published' then
    raise exception 'Execução publicada é imutável';
  end if;
  if tg_table_name='analysis_runs' and old.status='ready' then
    if tg_op<>'UPDATE' then raise exception 'Execução finalizada é imutável'; end if;
    if new.status<>'published' or (to_jsonb(new)-'status'-'published_at')<>(to_jsonb(old)-'status'-'published_at') then
      raise exception 'Somente publicação de execução finalizada é permitida';
    end if;
  end if;
  if tg_op='DELETE' then return old; end if;
  return new;
end $$;
create trigger dataset_metadata_guard before update or delete on analytics.dataset_versions
  for each row execute function analytics.guard_metadata();
create trigger run_metadata_guard before update or delete on analytics.analysis_runs
  for each row execute function analytics.guard_metadata();

create function ingest.guard_file_metadata() returns trigger language plpgsql security invoker set search_path='' as $$
begin
  if old.status='verified' then raise exception 'Arquivo verificado é imutável'; end if;
  if tg_op='DELETE' then return old; end if;
  return new;
end $$;
create trigger file_metadata_guard before update or delete on ingest.source_files
  for each row execute function ingest.guard_file_metadata();
