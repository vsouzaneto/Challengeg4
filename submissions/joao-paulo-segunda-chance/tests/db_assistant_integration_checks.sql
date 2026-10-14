-- Metadata-only verification of a completed, one-use server-side integration check.
-- Requires the real check to have completed. No secrets or user/Auth fixtures.
begin;
set local role service_role;
do $$ declare h text;cid uuid;begin
 select token_hash,id into strict h,cid from assistant.integration_checks where consumed_at is not null and result->>'passed'='true' order by created_at desc limit 1;
 if public.challenge_assistant_check_claim(h) is not null then raise exception 'Consumed check reused.';end if;
 if public.challenge_assistant_check_claim(repeat('0',64)) is not null then raise exception 'Unknown token accepted.';end if;
 if public.challenge_assistant_check_finish(cid,'{"changed":true}') then raise exception 'Completed evidence overwritten.';end if;
 if has_function_privilege('anon','public.challenge_assistant_check_claim(text)','EXECUTE') or has_function_privilege('authenticated','public.challenge_assistant_check_finish(uuid,jsonb)','EXECUTE') or has_table_privilege('authenticated','assistant.integration_checks','SELECT') then raise exception 'Diagnostic administration exposed.';end if;
end $$;
rollback;
select 'passed' as one_use_check_guards;
