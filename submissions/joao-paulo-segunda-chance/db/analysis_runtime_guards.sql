create or replace function analytics.build_run(p_version uuid,p_reference date) returns uuid language plpgsql security invoker
set search_path='' as $$
declare ws uuid; run_uuid uuid; current_state text; observed_end date;
begin
  select workspace_id,status into strict ws,current_state from analytics.dataset_versions where id=p_version;
  if p_reference is null or current_state='failed' then raise exception 'Versão/data não elegível'; end if;
  if not exists(select 1 from core.accounts where version_id=p_version) then raise exception 'Promover fontes antes de calcular'; end if;
  select greatest((select max(signup_date) from core.accounts where version_id=p_version),
    (select max(start_date) from core.subscriptions where version_id=p_version),
    (select max(usage_date) from core.feature_usage where version_id=p_version),
    (select max(submitted_at)::date from core.support_tickets where version_id=p_version),
    (select max(churn_date) from core.churn_events where version_id=p_version)) into observed_end;
  if observed_end is null or p_reference>observed_end then raise exception 'Data de referência além do período observado nas fontes'; end if;
  insert into analytics.analysis_runs(workspace_id,version_id,reference_date,algorithm_version)
    values(ws,p_version,p_reference,'1.1.0') returning id into run_uuid;

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
      count(*) filter(where closed_at>=submitted_at and closed_at<p_reference+1)::integer as closed_count,
      count(*) filter(where closed_at>=submitted_at and closed_at<p_reference+1 and satisfaction_score between 1 and 5)::integer as response_count,
      avg(satisfaction_score) filter(where closed_at>=submitted_at and closed_at<p_reference+1 and satisfaction_score between 1 and 5) as mean_score,
      avg(resolution_time_hours) filter(where closed_at>=submitted_at and closed_at<p_reference+1
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


create or replace function public.challenge_finish_import(p_version uuid,p_reference date,p_checks jsonb) returns uuid
language plpgsql security invoker set search_path='' as $$
declare ws uuid; r uuid; state text;
begin
  select workspace_id,status into strict ws,state from analytics.dataset_versions where id=p_version for update;
  if state='published' then
    select id into r from analytics.analysis_runs where version_id=p_version and reference_date=p_reference
      and status='published' order by published_at desc limit 1;
    if r is not null then return r; end if;
    r=analytics.build_run(p_version,p_reference);
    perform analytics.publish_run(r);
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


create function analytics.guard_manifest_after_processing() returns trigger language plpgsql security invoker set search_path='' as $$
begin
  if tg_op in ('UPDATE','DELETE') and exists(select 1 from core.accounts where version_id=old.version_id) then
    raise exception 'Manifesto processado é imutável; crie uma nova versão';
  end if;
  if tg_op in ('INSERT','UPDATE') and exists(select 1 from core.accounts where version_id=new.version_id) then
    raise exception 'Manifesto processado é imutável; crie uma nova versão';
  end if;
  if tg_op='DELETE' then return old; end if;
  return new;
end $$;
create trigger processed_manifest_guard before insert or update or delete on analytics.version_sources
  for each row execute function analytics.guard_manifest_after_processing();
revoke execute on function analytics.guard_manifest_after_processing() from public,anon,authenticated;
grant execute on function analytics.guard_manifest_after_processing() to service_role;
