-- SYNTHETIC, LOCAL ISOLATED DATABASE ONLY. Never apply to a shared Supabase project.
insert into auth.users(id,email,email_confirmed_at) values
 ('11111111-1111-4111-8111-111111111111','amadojoaoborges@gmail.com',now()),
 ('22222222-2222-4222-8222-222222222222','email@raven.com',now()),
 ('33333333-3333-4333-8333-333333333333','reader@example.invalid',now());
insert into auth.sessions(id,user_id) values
 ('aaaaaaaa-1111-4111-8111-111111111111','11111111-1111-4111-8111-111111111111'),
 ('aaaaaaaa-2222-4222-8222-222222222222','22222222-2222-4222-8222-222222222222'),
 ('aaaaaaaa-3333-4333-8333-333333333333','33333333-3333-4333-8333-333333333333');
insert into access.workspaces(id,slug,name) values('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','ravenstack','Local synthetic workspace');
insert into access.memberships(workspace_id,user_id,role,display_name) select 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',id,case when email='amadojoaoborges@gmail.com' then 'administrator' else 'decision_maker' end,'Local fixture' from auth.users;
insert into access.web_sessions(token_hash,peer_hash,user_id,auth_session_id,workspace_id) select repeat(case when u.email='amadojoaoborges@gmail.com' then 'a' when u.email='email@raven.com' then 'b' else 'c' end,64),repeat('d',64),u.id,s.id,'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa' from auth.users u join auth.sessions s on s.user_id=u.id;
do $$ declare ws uuid='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';b uuid;v uuid;r uuid;begin
 insert into ingest.import_batches(workspace_id,request_hash,label,actor) values(ws,'local-test','Local synthetic data','local fixture') returning id into b;
 insert into analytics.dataset_versions(workspace_id,batch_id) values(ws,b) returning id into v;
 insert into analytics.analysis_runs(workspace_id,version_id,reference_date,metrics) values(ws,v,'2024-12-31','{"accounts":1,"contract_mrr":100}') returning id into r;
 insert into analytics.account_snapshots(workspace_id,run_id,account_id,account_name,signup_date,industry,country,cadastral_churn,has_any_event,churn_events,reactivation_events,reconciliation_state,open_contracts,contract_mrr,coherent_usage_rows_30d,coherent_usage_rows_previous_30d,eligible_tickets_30d,closed_tickets_30d,satisfaction_responses) values(ws,r,'LOCAL','PRIVATE ACCOUNT','2024-01-01','Synthetic','BR',true,false,0,0,'flag_without_event',1,100,0,0,0,0,0);
 insert into analytics.quality_checks(workspace_id,version_id,code,kind,affected_count,denominator,interpretation,policy,examples) values(ws,v,'accounts.test','synthetic',1,1,'Synthetic check','Investigate','["PRIVATE ACCOUNT"]');
 update access.workspaces set current_run_id=r where id=ws;
end $$;
