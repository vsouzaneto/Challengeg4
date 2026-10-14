-- Acceptance test only. The entire publication is rolled back; no persistent pointer change.
-- Requires the server-validated Excel preview created by web/tests/http_import.py WITHOUT --publish.
begin;
do $$
declare u ingest.web_uploads; token text; before_run uuid; before_metrics jsonb; progress jsonb; selected_snapshot uuid; decision jsonb; after_metrics jsonb; steps integer=0;
begin
 select * into strict u from ingest.web_uploads where filename='contas_aceitacao.xlsx' and stage='preview' order by created_at desc limit 1;
 select token_hash into strict token from access.web_sessions where id=u.session_id;
 select w.current_run_id,r.metrics into strict before_run,before_metrics from access.workspaces w join analytics.analysis_runs r on r.id=w.current_run_id where w.slug='ravenstack';
 if u.parent_run_id<>before_run or (u.preview->>'added')::integer<>0 or (u.preview->>'removed')::integer<>0 or (u.preview->>'changed')::integer<>0 then raise exception 'Test requires unchanged account facts'; end if;
 select id into selected_snapshot from analytics.account_snapshots where run_id=before_run limit 1;
 decision=public.challenge_web_decide(token,gen_random_uuid()::text,null,selected_snapshot,'QA transacional','Conferir preservação da evidência original.','QA transacional','Conferir histórico','Equipe QA',current_date+1);
 perform public.challenge_web_begin(token,u.id);
 loop
  progress=public.challenge_web_advance(token,u.id);steps=steps+1;
  exit when progress->>'stage'='published';
  if steps>200 then raise exception 'Import did not finish';end if;
  if (select current_run_id from access.workspaces where id=u.workspace_id)<>before_run then raise exception 'Pointer changed before publication'; end if;
 end loop;
 if (select current_run_id from access.workspaces where id=u.workspace_id)<>(progress->>'run_id')::uuid then raise exception 'Pointer not published atomically';end if;
 select metrics into after_metrics from analytics.analysis_runs where id=(progress->>'run_id')::uuid;
 if before_metrics<>after_metrics then raise exception 'Same source facts changed metrics'; end if;
 if (select evidence_context->'run'->>'id' from operations.decisions where id=(decision->>'decision_id')::uuid)<>before_run::text then raise exception 'Decision evidence moved to new version'; end if;
 if (select count(*) from analytics.quality_checks where version_id=(select version_id from analytics.analysis_runs where id=(progress->>'run_id')::uuid))<>89 then raise exception 'Audit incomplete';end if;
 if public.challenge_web_advance(token,u.id)<>progress then raise exception 'Publication replay not idempotent';end if;
 if not exists(select 1 from analytics.account_snapshots where id=selected_snapshot and run_id=before_run) then raise exception 'Old evidence disappeared';end if;
end $$;
rollback;
