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
