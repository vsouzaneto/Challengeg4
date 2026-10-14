-- Internal one-use integration checks, separate from user conversations and business data.
create table assistant.integration_checks(
 id uuid primary key default gen_random_uuid(),token_hash text not null unique check(token_hash~'^[0-9a-f]{64}$'),
 created_at timestamptz not null default now(),consumed_at timestamptz,result jsonb);
alter table assistant.integration_checks enable row level security;
create policy backend_only on assistant.integration_checks to service_role using(true) with check(true);
revoke all on assistant.integration_checks from public,anon,authenticated;grant all on assistant.integration_checks to service_role;
create function public.challenge_assistant_check_claim(p_hash text) returns uuid language plpgsql security invoker set search_path='' as $$
declare cid uuid;begin
 update assistant.integration_checks set consumed_at=now() where token_hash=p_hash and consumed_at is null and created_at>now()-interval '10 minutes' returning id into cid;
 return cid;
end $$;
create function public.challenge_assistant_check_finish(p_id uuid,p_result jsonb) returns boolean language plpgsql security invoker set search_path='' as $$
begin
 if length(p_result::text)>12000 then raise exception 'Check output exceeds limit.';end if;
 update assistant.integration_checks set result=p_result where id=p_id and consumed_at is not null and result is null;return found;
end $$;
revoke execute on function public.challenge_assistant_check_claim(text),public.challenge_assistant_check_finish(uuid,jsonb) from public,anon,authenticated;
grant execute on function public.challenge_assistant_check_claim(text),public.challenge_assistant_check_finish(uuid,jsonb) to service_role;
