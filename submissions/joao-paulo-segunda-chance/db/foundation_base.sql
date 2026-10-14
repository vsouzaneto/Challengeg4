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
