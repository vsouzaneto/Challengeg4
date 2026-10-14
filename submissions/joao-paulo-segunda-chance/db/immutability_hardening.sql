-- Check both old and new parents: moving a record cannot bypass immutability.
create or replace function ingest.guard_source_write() returns trigger language plpgsql security invoker set search_path='' as $$
declare state text;
begin
  if tg_op in ('UPDATE','DELETE') then
    select status into strict state from ingest.source_files where id=old.file_id;
    if state<>'loading' then raise exception 'Fonte verificada é imutável'; end if;
  end if;
  if tg_op in ('INSERT','UPDATE') then
    select status into strict state from ingest.source_files where id=new.file_id;
    if state<>'loading' then raise exception 'Fonte verificada é imutável'; end if;
  end if;
  if tg_op='DELETE' then return old; end if;
  return new;
end $$;
create or replace function analytics.guard_version_write() returns trigger language plpgsql security invoker set search_path='' as $$
declare state text;
begin
  if tg_op in ('UPDATE','DELETE') then
    select status into strict state from analytics.dataset_versions where id=old.version_id;
    if state<>'candidate' then raise exception 'Versão publicada é imutável'; end if;
  end if;
  if tg_op in ('INSERT','UPDATE') then
    select status into strict state from analytics.dataset_versions where id=new.version_id;
    if state<>'candidate' then raise exception 'Versão publicada é imutável'; end if;
  end if;
  if tg_op='DELETE' then return old; end if;
  return new;
end $$;
create or replace function analytics.guard_run_write() returns trigger language plpgsql security invoker set search_path='' as $$
declare state text;
begin
  if tg_op in ('UPDATE','DELETE') then
    select status into strict state from analytics.analysis_runs where id=old.run_id;
    if state<>'building' then raise exception 'Evidência finalizada é imutável'; end if;
  end if;
  if tg_op in ('INSERT','UPDATE') then
    select status into strict state from analytics.analysis_runs where id=new.run_id;
    if state<>'building' then raise exception 'Evidência finalizada é imutável'; end if;
  end if;
  if tg_op='DELETE' then return old; end if;
  return new;
end $$;
