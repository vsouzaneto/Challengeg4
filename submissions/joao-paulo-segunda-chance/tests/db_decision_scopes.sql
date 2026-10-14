-- TDD: complete synthetic fixture in a rolled-back transaction, using the backend role.
begin;
set local role service_role;
do $$
declare ws uuid;b uuid;v uuid;r uuid;r2 uuid;p jsonb;account_p jsonb;q jsonb;d jsonb;again jsonb;token text=repeat('d',64);blocked boolean=false;before_run uuid;
begin
 select id,current_run_id into strict ws,before_run from access.workspaces where slug='ravenstack';
 perform public.challenge_web_session(token,repeat('e',64));
 insert into ingest.import_batches(workspace_id,request_hash,label,actor) values(ws,'qa-'||gen_random_uuid(),'Scope QA','test') returning id into b;
 insert into analytics.dataset_versions(workspace_id,batch_id) values(ws,b) returning id into v;
 insert into analytics.analysis_runs(workspace_id,version_id,reference_date,status) values(ws,v,'2024-12-31','building') returning id into r;
 insert into analytics.account_snapshots(workspace_id,run_id,account_id,account_name,signup_date,industry,country,cadastral_churn,has_any_event,churn_events,reactivation_events,reconciliation_state,open_contracts,contract_mrr,coherent_usage_rows_30d,coherent_usage_rows_previous_30d,recorded_usage_30d,eligible_tickets_30d,closed_tickets_30d,satisfaction_responses,mean_satisfaction)
 values(ws,r,'QA-A','QA A','2024-01-01','Alpha','BR',true,false,0,0,'flag_without_event',1,100,0,0,null,2,2,1,4),
 (ws,r,'QA-B','QA B','2024-01-01','Alpha','BR',false,false,0,0,'no_observed_churn_history',1,300,1,0,10,3,3,3,2),
 (ws,r,'QA-C','QA C','2024-01-01','Beta','US',true,true,1,0,'observed_agreement',1,500,1,0,20,0,0,0,null);
 insert into analytics.quality_checks(workspace_id,version_id,code,kind,affected_count,denominator,interpretation,policy) values(ws,v,'usage.before_subscription','quality',2,5,'Uso anterior ao contrato','Investigar vínculo');
 update analytics.analysis_runs set status='published' where id=r;update access.workspaces set current_run_id=r where id=ws;
 p=public.challenge_web_scope_preview(token,r,'{"type":"segment","industry":"Alpha","country":"BR"}','contract_mrr');
 if (p->>'population_count')::integer<>2 or (p->'measure'->>'value')::numeric<>400 then raise exception 'Segment MRR/population wrong';end if;
 p=public.challenge_web_scope_preview(token,r,'{"type":"segment","industry":"Alpha"}','satisfaction');
 if (p->'measure'->>'value')::numeric<>2.5 or (p->'measure'->>'numerator')::integer<>4 or (p->'measure'->>'denominator')::integer<>5 then raise exception 'Weighted satisfaction/coverage wrong';end if;
 account_p=public.challenge_web_scope_preview(token,r,'{"type":"account","account_id":"QA-A"}','observed_usage');
 if account_p->'measure'->'value'<>'null'::jsonb then raise exception 'Unobserved usage turned into zero';end if;
 p=public.challenge_web_scope_preview(token,r,'{"type":"segment","industry":"Alpha"}','missing_cancel');
 if (p->>'affected_count')::integer<>1 or (p->>'population_count')::integer<>2 then raise exception 'Affected/population conflated';end if;
 q=public.challenge_web_scope_preview(token,r,'{"type":"quality","source":"usage","check_code":"usage.before_subscription"}','quality_check');
 if (q->>'population_count')::integer<>5 or jsonb_array_length(q->'members')<>0 then raise exception 'Quality denominator/membership wrong';end if;
 begin perform public.challenge_web_scope_preview(token,r,'{"type":"segment","industry":"Empty"}','contract_mrr');exception when raise_exception then blocked=true;end;
 if not blocked then raise exception 'Empty segment allowed';end if;blocked=false;
 begin perform public.challenge_web_scope_preview(token,r,'{"type":"quality","source":"accounts","check_code":"usage.before_subscription"}','quality_check');exception when raise_exception then blocked=true;end;
 if not blocked then raise exception 'Unrelated source allowed';end if;blocked=false;
 begin perform public.challenge_web_scope_preview(token,r,'{"type":"portfolio","industry":"Alpha"}','contract_mrr');exception when raise_exception then blocked=true;end;
 if not blocked then raise exception 'Hidden filter on portfolio allowed';end if;blocked=false;
 begin perform public.challenge_web_scope_preview(token,r,'{"type":"segment","industry":"Alpha","injected":true}','contract_mrr');exception when raise_exception then blocked=true;end;
 if not blocked then raise exception 'Unknown filter allowed';end if;
 d=public.challenge_web_decide_scoped(token,'qa-scope-request',r,'{"type":"segment","industry":"Alpha"}','missing_cancel',p->>'preview_hash','Investigar segmento','Reconciliar casos com histórico ausente.','QA','Conferir origem','Equipe QA','2026-10-13');
 again=public.challenge_web_decide_scoped(token,'qa-scope-request',r,'{"type":"segment","industry":"Alpha"}','missing_cancel',p->>'preview_hash','Investigar segmento','Reconciliar casos com histórico ausente.','QA','Conferir origem','Equipe QA','2026-10-13');
 if d<>again then raise exception 'Replay not idempotent';end if;
 if (select count(*) from operations.decision_scope_snapshots where decision_id=(d->>'decision_id')::uuid)<>2 then raise exception 'Membership not frozen';end if;
 blocked=false;begin perform public.challenge_web_decide_scoped(token,'qa-bad-preview',r,'{"type":"segment","industry":"Alpha"}','missing_cancel',repeat('0',64),'Investigar segmento','Reconciliar casos com histórico ausente.','QA','Conferir origem','Equipe QA','2026-10-13');exception when sqlstate 'PT409' then blocked=true;end;
 if not blocked then raise exception 'Forged/outdated preview accepted';end if;
 insert into analytics.analysis_runs(workspace_id,version_id,reference_date,status) values(ws,v,'2024-12-31','published') returning id into r2;
 update access.workspaces set current_run_id=r2 where id=ws;
 if (select run_id from operations.decision_scopes where decision_id=(d->>'decision_id')::uuid)<>r then raise exception 'Old decision moved to new version';end if;
 if (select preview_hash from operations.decision_scopes where decision_id=(d->>'decision_id')::uuid)<>p->>'preview_hash' then raise exception 'Old evidence changed';end if;
 blocked=false;begin perform public.challenge_web_scope_preview(token,r,'{"type":"portfolio"}','contract_mrr');exception when sqlstate 'PT409' then blocked=true;end;
 if not blocked then raise exception 'Outdated run silently reused for new preview';end if;
 again=public.challenge_web_decide_scoped(token,'qa-scope-request',r,'{"type":"segment","industry":"Alpha"}','missing_cancel',p->>'preview_hash','Investigar segmento','Reconciliar casos com histórico ausente.','QA','Conferir origem','Equipe QA','2026-10-13');
 if d<>again then raise exception 'Replay after publication not idempotent';end if;
 blocked=false;begin perform public.challenge_web_decide_scoped(token,'qa-scope-request',r,'{"type":"segment","industry":"Beta"}','missing_cancel',p->>'preview_hash','Investigar segmento','Reconciliar casos com histórico ausente.','QA','Conferir origem','Equipe QA','2026-10-13');exception when sqlstate 'PT409' then blocked=true;end;
 if not blocked then raise exception 'Reused request allowed changed scope';end if;
 blocked=false;begin update operations.decision_scopes set population_count=99 where decision_id=(d->>'decision_id')::uuid;exception when raise_exception then blocked=true;end;
 if not blocked then raise exception 'Scope update allowed';end if;
 blocked=false;begin delete from operations.decision_scope_snapshots where decision_id=(d->>'decision_id')::uuid;exception when raise_exception then blocked=true;end;
 if not blocked then raise exception 'Membership delete allowed';end if;
 blocked=false;begin insert into operations.decision_scope_snapshots(workspace_id,decision_id,run_id,snapshot_id,highlighted) values(ws,(d->>'decision_id')::uuid,r2,(select id from analytics.account_snapshots where run_id=r and account_id='QA-C'),true);exception when foreign_key_violation then blocked=true;end;
 if not blocked then raise exception 'Membership can use wrong version';end if;
 if has_function_privilege('anon','public.challenge_web_scope_preview(text,uuid,jsonb,text)','execute') then raise exception 'Anonymous direct RPC privilege';end if;
end $$;
rollback;
