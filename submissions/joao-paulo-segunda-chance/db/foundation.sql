-- Foundation: dedicated project only. No source data, generated IDs or secrets.
create schema access;
create schema ingest;
create schema core;
create schema analytics;
create schema operations;

create table access.workspaces (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  current_run_id uuid,
  created_at timestamptz not null default now()
);
create table access.memberships (
  workspace_id uuid not null references access.workspaces(id),
  user_id uuid not null references auth.users(id),
  role text not null check (role in ('administrator','decision_maker','executor','reader')),
  active boolean not null default true,
  primary key(workspace_id,user_id)
);
create index memberships_user_idx on access.memberships(user_id,workspace_id) where active;
alter table access.memberships enable row level security;
create policy own_membership on access.memberships for select to authenticated
  using (user_id = (select auth.uid()));

create function access.is_member(p_workspace uuid) returns boolean language sql stable security invoker
  set search_path = '' as $$
  select exists(select 1 from access.memberships m where m.workspace_id=p_workspace
    and m.user_id=(select auth.uid()) and m.active)
$$;
create function access.has_role(p_workspace uuid,p_roles text[]) returns boolean language sql stable security invoker
  set search_path = '' as $$
  select exists(select 1 from access.memberships m where m.workspace_id=p_workspace
    and m.user_id=(select auth.uid()) and m.active and m.role=any(p_roles))
$$;

create table ingest.source_contracts (
  source_type text not null check(source_type in ('accounts','subscriptions','usage','support','churn')),
  contract_version text not null,
  definition jsonb not null,
  primary key(source_type,contract_version)
);
create table ingest.import_batches (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references access.workspaces(id),
  request_hash text not null,
  label text not null,
  mode text not null default 'full_source' check(mode in ('full_source','upsert')),
  status text not null default 'loading' check(status in ('loading','ready','published','failed')),
  created_at timestamptz not null default now(),
  actor text not null,
  unique(workspace_id,id), unique(workspace_id,request_hash)
);
create table ingest.source_files (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  batch_id uuid not null,
  source_type text not null,
  contract_version text not null,
  filename text not null,
  file_hash text not null check(file_hash ~ '^[0-9a-f]{64}$'),
  expected_rows integer not null check(expected_rows >= 0),
  expected_bytes integer not null check(expected_bytes >= 0),
  status text not null default 'loading' check(status in ('loading','verified','failed')),
  created_at timestamptz not null default now(),
  unique(workspace_id,id), unique(workspace_id,id,source_type),
  unique(workspace_id,source_type,contract_version,file_hash),
  foreign key(workspace_id,batch_id) references ingest.import_batches(workspace_id,id),
  foreign key(source_type,contract_version) references ingest.source_contracts(source_type,contract_version)
);
create index source_files_batch_idx on ingest.source_files(workspace_id,batch_id);
create table ingest.file_chunks (
  workspace_id uuid not null,
  file_id uuid not null,
  chunk_index integer not null check(chunk_index>=0),
  data bytea not null,
  primary key(file_id,chunk_index),
  foreign key(workspace_id,file_id) references ingest.source_files(workspace_id,id)
);
create table ingest.raw_rows (
  id bigint generated always as identity primary key,
  workspace_id uuid not null,
  file_id uuid not null,
  row_number integer not null check(row_number>0),
  content jsonb not null check(jsonb_typeof(content)='object'),
  record_hash text not null check(record_hash ~ '^[0-9a-f]{64}$'),
  unique(file_id,row_number), unique(workspace_id,id),
  foreign key(workspace_id,file_id) references ingest.source_files(workspace_id,id)
);
create index raw_rows_file_idx on ingest.raw_rows(workspace_id,file_id,row_number);

create table analytics.dataset_versions (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references access.workspaces(id),
  batch_id uuid not null,
  parent_version_id uuid,
  status text not null default 'candidate' check(status in ('candidate','published','failed')),
  definition_version text not null default '1.0.0',
  coverage_declared boolean not null default false,
  created_at timestamptz not null default now(),
  unique(workspace_id,id), unique(batch_id),
  foreign key(workspace_id,batch_id) references ingest.import_batches(workspace_id,id),
  foreign key(workspace_id,parent_version_id) references analytics.dataset_versions(workspace_id,id)
);
create table analytics.version_sources (
  workspace_id uuid not null,
  version_id uuid not null,
  source_type text not null,
  file_id uuid not null,
  primary key(version_id,source_type),
  foreign key(workspace_id,version_id) references analytics.dataset_versions(workspace_id,id),
  foreign key(workspace_id,file_id,source_type) references ingest.source_files(workspace_id,id,source_type)
);
create index version_sources_file_idx on analytics.version_sources(workspace_id,file_id);
create table analytics.analysis_runs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  version_id uuid not null,
  reference_date date not null,
  algorithm_version text not null default '1.0.0',
  status text not null default 'building' check(status in ('building','ready','published','failed')),
  definition_notes jsonb not null default '{"contract_interval":"[start,end)","telemetry_coverage":"not_confirmed","csat_availability":"assumed_at_closure","historical_attributes":"not_reconstructed"}',
  metrics jsonb not null default '{}',
  created_at timestamptz not null default now(),
  published_at timestamptz,
  unique(workspace_id,id),
  foreign key(workspace_id,version_id) references analytics.dataset_versions(workspace_id,id)
);
create index analysis_runs_version_idx on analytics.analysis_runs(workspace_id,version_id);
alter table access.workspaces add constraint current_run_fk foreign key(id,current_run_id)
  references analytics.analysis_runs(workspace_id,id);

create table analytics.quality_checks (
  workspace_id uuid not null,
  version_id uuid not null,
  code text not null,
  kind text not null,
  affected_count integer not null check(affected_count>=0),
  denominator integer not null check(denominator>=0),
  interpretation text not null,
  policy text not null,
  examples jsonb not null default '[]',
  primary key(version_id,code),
  foreign key(workspace_id,version_id) references analytics.dataset_versions(workspace_id,id)
);
create table analytics.account_snapshots (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  run_id uuid not null,
  account_id text not null,
  account_name text not null,
  signup_date date not null,
  industry text not null,
  country text not null,
  cadastral_churn boolean not null,
  has_any_event boolean not null,
  churn_events integer not null,
  reactivation_events integer not null,
  reconciliation_state text not null,
  open_contracts integer not null,
  contract_mrr numeric not null,
  coherent_usage_rows_30d integer not null,
  coherent_usage_rows_previous_30d integer not null,
  recorded_usage_30d bigint,
  recorded_usage_previous_30d bigint,
  usage_drop_ratio numeric,
  coverage_state text not null default 'not_confirmed',
  eligible_tickets_30d integer not null,
  closed_tickets_30d integer not null,
  satisfaction_responses integer not null,
  mean_satisfaction numeric,
  mean_resolution_hours numeric,
  quality_flags jsonb not null default '[]',
  unique(run_id,account_id), unique(workspace_id,id),
  foreign key(workspace_id,run_id) references analytics.analysis_runs(workspace_id,id)
);
create index snapshots_account_idx on analytics.account_snapshots(workspace_id,account_id,run_id);
create table analytics.evidence_items (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  run_id uuid not null,
  snapshot_id uuid,
  rule_code text not null,
  rule_version text not null,
  state text not null check(state in ('satisfied','not_satisfied','indeterminate')),
  category text not null check(category in ('data_quality','diagnostic','operational')),
  summary text not null,
  details jsonb not null,
  unique(workspace_id,id),
  foreign key(workspace_id,run_id) references analytics.analysis_runs(workspace_id,id),
  foreign key(workspace_id,snapshot_id) references analytics.account_snapshots(workspace_id,id)
);
create index evidence_run_idx on analytics.evidence_items(workspace_id,run_id);
create index evidence_snapshot_idx on analytics.evidence_items(workspace_id,snapshot_id);

create table operations.decisions (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  evidence_id uuid not null,
  title text not null check(length(trim(title))>0),
  rationale text not null check(length(trim(rationale))>0),
  actor_user_id uuid not null references auth.users(id),
  status text not null default 'approved' check(status in ('approved','cancelled')),
  created_at timestamptz not null default now(),
  unique(workspace_id,id),
  foreign key(workspace_id,evidence_id) references analytics.evidence_items(workspace_id,id)
);
create index decisions_evidence_idx on operations.decisions(workspace_id,evidence_id);
create index decisions_actor_idx on operations.decisions(actor_user_id);
create table operations.actions (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null,
  decision_id uuid not null,
  title text not null,
  responsible text not null,
  due_date date not null,
  status text not null default 'pending' check(status in ('pending','in_progress','completed','cancelled')),
  result_note text,
  assigned_user_id uuid references auth.users(id),
  revision integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(workspace_id,id),
  foreign key(workspace_id,decision_id) references operations.decisions(workspace_id,id)
);
create index actions_decision_idx on operations.actions(workspace_id,decision_id);
create index actions_assignee_idx on operations.actions(assigned_user_id);
create table operations.action_history (
  id bigint generated always as identity primary key,
  workspace_id uuid not null,
  action_id uuid not null,
  actor_user_id uuid not null references auth.users(id),
  from_status text,
  to_status text not null,
  result_note text,
  revision integer not null,
  created_at timestamptz not null default now(),
  foreign key(workspace_id,action_id) references operations.actions(workspace_id,id)
);
create index action_history_action_idx on operations.action_history(workspace_id,action_id,revision);

create function ingest.verify_file(p_file uuid) returns void language plpgsql security invoker
set search_path='' as $$
declare f ingest.source_files; actual_rows integer; payload bytea;
begin
  select * into strict f from ingest.source_files where id=p_file for update;
  select count(*) into actual_rows from ingest.raw_rows where file_id=p_file;
  select string_agg(data,''::bytea order by chunk_index) into payload from ingest.file_chunks where file_id=p_file;
  if actual_rows<>f.expected_rows or octet_length(payload)<>f.expected_bytes
     or encode(sha256(payload),'hex')<>f.file_hash then
    raise exception 'Arquivo incompleto ou hash divergente';
  end if;
  update ingest.source_files set status='verified' where id=p_file and status='loading';
end $$;

create function ingest.guard_source_write() returns trigger language plpgsql security invoker set search_path='' as $$
declare file_uuid uuid; state text;
begin
  file_uuid := case when tg_op='DELETE' then old.file_id else new.file_id end;
  select status into strict state from ingest.source_files where id=file_uuid;
  if state<>'loading' then raise exception 'Fonte verificada é imutável'; end if;
  if tg_op='DELETE' then return old; end if;
  return new;
end $$;
create trigger raw_rows_guard before insert or update or delete on ingest.raw_rows
  for each row execute function ingest.guard_source_write();
create trigger file_chunks_guard before insert or update or delete on ingest.file_chunks
  for each row execute function ingest.guard_source_write();

create function analytics.guard_version_write() returns trigger language plpgsql security invoker set search_path='' as $$
declare version_uuid uuid; state text;
begin
  version_uuid := case when tg_op='DELETE' then old.version_id else new.version_id end;
  select status into strict state from analytics.dataset_versions where id=version_uuid;
  if state<>'candidate' then raise exception 'Versão publicada é imutável'; end if;
  if tg_op='DELETE' then return old; end if;
  return new;
end $$;
create function analytics.guard_run_write() returns trigger language plpgsql security invoker set search_path='' as $$
declare run_uuid uuid; state text;
begin
  run_uuid := case when tg_op='DELETE' then old.run_id else new.run_id end;
  select status into strict state from analytics.analysis_runs where id=run_uuid;
  if state<>'building' then raise exception 'Evidência finalizada é imutável'; end if;
  if tg_op='DELETE' then return old; end if;
  return new;
end $$;
create trigger snapshots_guard before insert or update or delete on analytics.account_snapshots
  for each row execute function analytics.guard_run_write();
create trigger evidence_guard before insert or update or delete on analytics.evidence_items
  for each row execute function analytics.guard_run_write();
create trigger version_sources_guard before insert or update or delete on analytics.version_sources
  for each row execute function analytics.guard_version_write();
create trigger quality_checks_guard before insert or update or delete on analytics.quality_checks
  for each row execute function analytics.guard_version_write();


create table core.accounts (
  workspace_id uuid not null,
  version_id uuid not null,
  source_row_id bigint not null,
  account_id text not null,
  account_name text not null,
  industry text not null,
  country text not null,
  referral_source text not null,
  plan_tier text not null,
  seats integer not null,
  is_trial boolean not null,
  churn_flag boolean not null,
  signup_date date not null,
  primary key(version_id,account_id),
  foreign key(workspace_id,version_id) references analytics.dataset_versions(workspace_id,id),
  foreign key(workspace_id,source_row_id) references ingest.raw_rows(workspace_id,id),
  unique(workspace_id,version_id,account_id)
);

create index accounts_relation_idx on core.accounts(workspace_id,version_id,account_id);

create trigger accounts_version_guard before insert or update or delete on core.accounts for each row execute function analytics.guard_version_write();

insert into ingest.source_contracts values ('accounts','1.0.0','{"account_id": {"type": "text", "nullable": false}, "account_name": {"type": "text", "nullable": false}, "industry": {"type": "text", "nullable": false}, "country": {"type": "text", "nullable": false}, "referral_source": {"type": "text", "nullable": false}, "plan_tier": {"type": "text", "nullable": false}, "seats": {"type": "integer", "nullable": false}, "is_trial": {"type": "boolean", "nullable": false}, "churn_flag": {"type": "boolean", "nullable": false}, "signup_date": {"type": "date", "nullable": false}}'::jsonb);

create table core.subscriptions (
  workspace_id uuid not null,
  version_id uuid not null,
  source_row_id bigint not null,
  subscription_id text not null,
  account_id text not null,
  plan_tier text not null,
  billing_frequency text not null,
  seats integer not null,
  mrr_amount numeric not null,
  arr_amount numeric not null,
  is_trial boolean not null,
  upgrade_flag boolean not null,
  downgrade_flag boolean not null,
  churn_flag boolean not null,
  auto_renew_flag boolean not null,
  start_date date not null,
  end_date date,
  primary key(version_id,subscription_id),
  foreign key(workspace_id,version_id) references analytics.dataset_versions(workspace_id,id),
  foreign key(workspace_id,source_row_id) references ingest.raw_rows(workspace_id,id),
  foreign key(workspace_id,version_id,account_id) references core.accounts(workspace_id,version_id,account_id),
  unique(workspace_id,version_id,subscription_id)
);

create index subscriptions_relation_idx on core.subscriptions(workspace_id,version_id,account_id);

create trigger subscriptions_version_guard before insert or update or delete on core.subscriptions for each row execute function analytics.guard_version_write();

insert into ingest.source_contracts values ('subscriptions','1.0.0','{"subscription_id": {"type": "text", "nullable": false}, "account_id": {"type": "text", "nullable": false}, "plan_tier": {"type": "text", "nullable": false}, "billing_frequency": {"type": "text", "nullable": false}, "seats": {"type": "integer", "nullable": false}, "mrr_amount": {"type": "numeric", "nullable": false}, "arr_amount": {"type": "numeric", "nullable": false}, "is_trial": {"type": "boolean", "nullable": false}, "upgrade_flag": {"type": "boolean", "nullable": false}, "downgrade_flag": {"type": "boolean", "nullable": false}, "churn_flag": {"type": "boolean", "nullable": false}, "auto_renew_flag": {"type": "boolean", "nullable": false}, "start_date": {"type": "date", "nullable": false}, "end_date": {"type": "date", "nullable": true}}'::jsonb);

create table core.feature_usage (
  workspace_id uuid not null,
  version_id uuid not null,
  source_row_id bigint not null,
  usage_id text not null,
  subscription_id text not null,
  feature_name text not null,
  usage_count integer not null,
  usage_duration_secs integer not null,
  error_count integer not null,
  is_beta_feature boolean not null,
  usage_date date not null,
  primary key(version_id,source_row_id),
  foreign key(workspace_id,version_id) references analytics.dataset_versions(workspace_id,id),
  foreign key(workspace_id,source_row_id) references ingest.raw_rows(workspace_id,id),
  foreign key(workspace_id,version_id,subscription_id) references core.subscriptions(workspace_id,version_id,subscription_id)
);

create index feature_usage_relation_idx on core.feature_usage(workspace_id,version_id,subscription_id);

create index usage_identity_idx on core.feature_usage(version_id,usage_id);

create index usage_date_idx on core.feature_usage(version_id,subscription_id,usage_date);

create trigger feature_usage_version_guard before insert or update or delete on core.feature_usage for each row execute function analytics.guard_version_write();

insert into ingest.source_contracts values ('usage','1.0.0','{"usage_id": {"type": "text", "nullable": false}, "subscription_id": {"type": "text", "nullable": false}, "feature_name": {"type": "text", "nullable": false}, "usage_count": {"type": "integer", "nullable": false}, "usage_duration_secs": {"type": "integer", "nullable": false}, "error_count": {"type": "integer", "nullable": false}, "is_beta_feature": {"type": "boolean", "nullable": false}, "usage_date": {"type": "date", "nullable": false}}'::jsonb);

create table core.support_tickets (
  workspace_id uuid not null,
  version_id uuid not null,
  source_row_id bigint not null,
  ticket_id text not null,
  account_id text not null,
  priority text not null,
  first_response_time_minutes integer not null,
  resolution_time_hours numeric,
  satisfaction_score numeric,
  escalation_flag boolean not null,
  submitted_at timestamp without time zone not null,
  closed_at timestamp without time zone,
  primary key(version_id,ticket_id),
  foreign key(workspace_id,version_id) references analytics.dataset_versions(workspace_id,id),
  foreign key(workspace_id,source_row_id) references ingest.raw_rows(workspace_id,id),
  foreign key(workspace_id,version_id,account_id) references core.accounts(workspace_id,version_id,account_id)
);

create index support_tickets_relation_idx on core.support_tickets(workspace_id,version_id,account_id);

create index support_date_idx on core.support_tickets(version_id,account_id,submitted_at);

create trigger support_tickets_version_guard before insert or update or delete on core.support_tickets for each row execute function analytics.guard_version_write();

insert into ingest.source_contracts values ('support','1.0.0','{"ticket_id": {"type": "text", "nullable": false}, "account_id": {"type": "text", "nullable": false}, "priority": {"type": "text", "nullable": false}, "first_response_time_minutes": {"type": "integer", "nullable": false}, "resolution_time_hours": {"type": "numeric", "nullable": true}, "satisfaction_score": {"type": "numeric", "nullable": true}, "escalation_flag": {"type": "boolean", "nullable": false}, "submitted_at": {"type": "timestamp", "nullable": false}, "closed_at": {"type": "timestamp", "nullable": true}}'::jsonb);

create table core.churn_events (
  workspace_id uuid not null,
  version_id uuid not null,
  source_row_id bigint not null,
  churn_event_id text not null,
  account_id text not null,
  reason_code text not null,
  feedback_text text,
  refund_amount_usd numeric not null,
  preceding_upgrade_flag boolean not null,
  preceding_downgrade_flag boolean not null,
  is_reactivation boolean not null,
  churn_date date not null,
  primary key(version_id,churn_event_id),
  foreign key(workspace_id,version_id) references analytics.dataset_versions(workspace_id,id),
  foreign key(workspace_id,source_row_id) references ingest.raw_rows(workspace_id,id),
  foreign key(workspace_id,version_id,account_id) references core.accounts(workspace_id,version_id,account_id)
);

create index churn_events_relation_idx on core.churn_events(workspace_id,version_id,account_id);

create index churn_date_idx on core.churn_events(version_id,account_id,churn_date);

create trigger churn_events_version_guard before insert or update or delete on core.churn_events for each row execute function analytics.guard_version_write();

insert into ingest.source_contracts values ('churn','1.0.0','{"churn_event_id": {"type": "text", "nullable": false}, "account_id": {"type": "text", "nullable": false}, "reason_code": {"type": "text", "nullable": false}, "feedback_text": {"type": "text", "nullable": true}, "refund_amount_usd": {"type": "numeric", "nullable": false}, "preceding_upgrade_flag": {"type": "boolean", "nullable": false}, "preceding_downgrade_flag": {"type": "boolean", "nullable": false}, "is_reactivation": {"type": "boolean", "nullable": false}, "churn_date": {"type": "date", "nullable": false}}'::jsonb);

create function analytics.promote_version(p_version uuid) returns void language plpgsql security invoker set search_path='' as $$
declare ws uuid; sources integer; state text; begin
select workspace_id,status into strict ws,state from analytics.dataset_versions where id=p_version for update;
if state<>'candidate' then raise exception 'Apenas versão candidata pode ser promovida'; end if;
select count(*) into sources from analytics.version_sources vs join ingest.source_files f on f.id=vs.file_id where vs.version_id=p_version and f.status='verified';
if sources<>5 then raise exception 'São necessárias cinco fontes verificadas'; end if;
insert into core.accounts(workspace_id,version_id,source_row_id,account_id,account_name,industry,country,referral_source,plan_tier,seats,is_trial,churn_flag,signup_date) select ws,p_version,r.id,nullif(r.content->>'account_id','')::text,nullif(r.content->>'account_name','')::text,nullif(r.content->>'industry','')::text,nullif(r.content->>'country','')::text,nullif(r.content->>'referral_source','')::text,nullif(r.content->>'plan_tier','')::text,nullif(r.content->>'seats','')::integer,nullif(r.content->>'is_trial','')::boolean,nullif(r.content->>'churn_flag','')::boolean,nullif(r.content->>'signup_date','')::date from ingest.raw_rows r join analytics.version_sources vs on vs.file_id=r.file_id and vs.version_id=p_version where vs.source_type='accounts' on conflict do nothing;
if (select count(*) from core.accounts where version_id=p_version)<>(select f.expected_rows from analytics.version_sources vs join ingest.source_files f on f.id=vs.file_id where vs.version_id=p_version and vs.source_type='accounts') then raise exception 'Contagem canônica divergente: accounts'; end if;
insert into core.subscriptions(workspace_id,version_id,source_row_id,subscription_id,account_id,plan_tier,billing_frequency,seats,mrr_amount,arr_amount,is_trial,upgrade_flag,downgrade_flag,churn_flag,auto_renew_flag,start_date,end_date) select ws,p_version,r.id,nullif(r.content->>'subscription_id','')::text,nullif(r.content->>'account_id','')::text,nullif(r.content->>'plan_tier','')::text,nullif(r.content->>'billing_frequency','')::text,nullif(r.content->>'seats','')::integer,nullif(r.content->>'mrr_amount','')::numeric,nullif(r.content->>'arr_amount','')::numeric,nullif(r.content->>'is_trial','')::boolean,nullif(r.content->>'upgrade_flag','')::boolean,nullif(r.content->>'downgrade_flag','')::boolean,nullif(r.content->>'churn_flag','')::boolean,nullif(r.content->>'auto_renew_flag','')::boolean,nullif(r.content->>'start_date','')::date,nullif(r.content->>'end_date','')::date from ingest.raw_rows r join analytics.version_sources vs on vs.file_id=r.file_id and vs.version_id=p_version where vs.source_type='subscriptions' on conflict do nothing;
if (select count(*) from core.subscriptions where version_id=p_version)<>(select f.expected_rows from analytics.version_sources vs join ingest.source_files f on f.id=vs.file_id where vs.version_id=p_version and vs.source_type='subscriptions') then raise exception 'Contagem canônica divergente: subscriptions'; end if;
insert into core.feature_usage(workspace_id,version_id,source_row_id,usage_id,subscription_id,feature_name,usage_count,usage_duration_secs,error_count,is_beta_feature,usage_date) select ws,p_version,r.id,nullif(r.content->>'usage_id','')::text,nullif(r.content->>'subscription_id','')::text,nullif(r.content->>'feature_name','')::text,nullif(r.content->>'usage_count','')::integer,nullif(r.content->>'usage_duration_secs','')::integer,nullif(r.content->>'error_count','')::integer,nullif(r.content->>'is_beta_feature','')::boolean,nullif(r.content->>'usage_date','')::date from ingest.raw_rows r join analytics.version_sources vs on vs.file_id=r.file_id and vs.version_id=p_version where vs.source_type='usage' on conflict do nothing;
if (select count(*) from core.feature_usage where version_id=p_version)<>(select f.expected_rows from analytics.version_sources vs join ingest.source_files f on f.id=vs.file_id where vs.version_id=p_version and vs.source_type='usage') then raise exception 'Contagem canônica divergente: usage'; end if;
insert into core.support_tickets(workspace_id,version_id,source_row_id,ticket_id,account_id,priority,first_response_time_minutes,resolution_time_hours,satisfaction_score,escalation_flag,submitted_at,closed_at) select ws,p_version,r.id,nullif(r.content->>'ticket_id','')::text,nullif(r.content->>'account_id','')::text,nullif(r.content->>'priority','')::text,nullif(r.content->>'first_response_time_minutes','')::integer,nullif(r.content->>'resolution_time_hours','')::numeric,nullif(r.content->>'satisfaction_score','')::numeric,nullif(r.content->>'escalation_flag','')::boolean,nullif(r.content->>'submitted_at','')::timestamp without time zone,nullif(r.content->>'closed_at','')::timestamp without time zone from ingest.raw_rows r join analytics.version_sources vs on vs.file_id=r.file_id and vs.version_id=p_version where vs.source_type='support' on conflict do nothing;
if (select count(*) from core.support_tickets where version_id=p_version)<>(select f.expected_rows from analytics.version_sources vs join ingest.source_files f on f.id=vs.file_id where vs.version_id=p_version and vs.source_type='support') then raise exception 'Contagem canônica divergente: support'; end if;
insert into core.churn_events(workspace_id,version_id,source_row_id,churn_event_id,account_id,reason_code,feedback_text,refund_amount_usd,preceding_upgrade_flag,preceding_downgrade_flag,is_reactivation,churn_date) select ws,p_version,r.id,nullif(r.content->>'churn_event_id','')::text,nullif(r.content->>'account_id','')::text,nullif(r.content->>'reason_code','')::text,nullif(r.content->>'feedback_text','')::text,nullif(r.content->>'refund_amount_usd','')::numeric,nullif(r.content->>'preceding_upgrade_flag','')::boolean,nullif(r.content->>'preceding_downgrade_flag','')::boolean,nullif(r.content->>'is_reactivation','')::boolean,nullif(r.content->>'churn_date','')::date from ingest.raw_rows r join analytics.version_sources vs on vs.file_id=r.file_id and vs.version_id=p_version where vs.source_type='churn' on conflict do nothing;
if (select count(*) from core.churn_events where version_id=p_version)<>(select f.expected_rows from analytics.version_sources vs join ingest.source_files f on f.id=vs.file_id where vs.version_id=p_version and vs.source_type='churn') then raise exception 'Contagem canônica divergente: churn'; end if;
end
$$;

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


-- All application schemas are private. No anonymous privileges.
do $policies$
declare t record; s text;
begin
  foreach s in array array['access','ingest','core','analytics','operations'] loop
    execute format('revoke all on schema %I from public,anon,authenticated',s);
    execute format('grant usage on schema %I to service_role',s);
    execute format('grant usage on schema %I to authenticated',s);
    execute format('revoke all on all tables in schema %I from public,anon,authenticated',s);
    execute format('grant all on all tables in schema %I to service_role',s);
    execute format('grant usage,select on all sequences in schema %I to service_role',s);
    execute format('revoke execute on all functions in schema %I from public,anon,authenticated',s);
    execute format('grant execute on all functions in schema %I to service_role',s);
    execute format('alter default privileges in schema %I revoke execute on functions from public',s);
  end loop;
  for t in select c.relname,n.nspname from pg_class c join pg_namespace n on n.oid=c.relnamespace
    where n.nspname in ('access','ingest','core','analytics','operations') and c.relkind='r' loop
    execute format('alter table %I.%I enable row level security',t.nspname,t.relname);
    if t.nspname='access' and t.relname='memberships' then continue; end if;
    if t.nspname='ingest' and t.relname='source_contracts' then continue; end if;
    execute format('create policy workspace_read on %I.%I for select to authenticated using (access.is_member(%I))',
      t.nspname,t.relname,case when t.nspname='access' and t.relname='workspaces' then 'id' else 'workspace_id' end);
  end loop;
end $policies$;

-- Users read their own membership; they cannot self-assign administrator.
grant select on access.memberships,access.workspaces to authenticated;
grant execute on function access.is_member(uuid),access.has_role(uuid,text[]) to authenticated;

-- Dashboard reads only prepared analytical tables. Source files and raw data are backend-only.
grant select on analytics.dataset_versions,analytics.version_sources,analytics.analysis_runs,
  analytics.account_snapshots,analytics.evidence_items,analytics.quality_checks to authenticated;
grant select on operations.decisions,operations.actions,operations.action_history to authenticated;

-- SECURITY INVOKER read interfaces in the exposed schema honor underlying RLS.
create function public.challenge_dashboard(p_workspace uuid) returns jsonb
language sql stable security invoker set search_path='' as $$
  select jsonb_build_object('workspace',w.name,'run_id',r.id,'version_id',r.version_id,
    'reference_date',r.reference_date,'metrics',r.metrics,'definitions',r.definition_notes)
  from access.workspaces w join analytics.analysis_runs r on r.id=w.current_run_id
  where w.id=p_workspace and r.status='published'
$$;
create function public.challenge_accounts(p_workspace uuid,p_limit integer default 100,p_offset integer default 0)
returns setof analytics.account_snapshots language sql stable security invoker set search_path='' as $$
  select s.* from analytics.account_snapshots s join access.workspaces w on w.current_run_id=s.run_id
  where w.id=p_workspace order by s.account_id limit least(greatest(p_limit,1),500) offset greatest(p_offset,0)
$$;
revoke execute on function public.challenge_dashboard(uuid),public.challenge_accounts(uuid,integer,integer) from public,anon;
grant execute on function public.challenge_dashboard(uuid),public.challenge_accounts(uuid,integer,integer) to authenticated,service_role;

