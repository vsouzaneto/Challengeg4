-- Uses one existing, live application/Auth session. Never creates Auth identities/sessions.
-- All QA history is rolled back. If no real session exists, test fails (not a silent skip).
begin;
set local role service_role;
do $$ declare tok text;cid uuid;tid uuid;e uuid;r jsonb;q jsonb;expected numeric;original_owner uuid;other_user uuid;metric_name text;begin
 select s.token_hash into tok from access.web_sessions s join auth.sessions a on a.id=s.auth_session_id and a.user_id=s.user_id where s.user_id is not null and s.revoked_at is null and s.expires_at>now() and(a.not_after is null or a.not_after>now()) limit 1;
 if tok is null then raise exception 'Test requires an existing real bound session.';end if;
 r=public.challenge_assistant_create(tok,'{}');cid=(r->>'id')::uuid;
 q=public.challenge_assistant_begin(tok,cid,'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','[QA rollback] MRR da carteira');tid=(q->>'turn_id')::uuid;e=(q->>'execution_id')::uuid;
 r=public.challenge_assistant_query(tok,tid,e,'{"metric":"mrr","industry":null,"country":null,"dimension":null,"quality_kind":null}');
 select sum(s.contract_mrr) into expected from analytics.account_snapshots s where s.run_id=(r->>'run_id')::uuid;
 if(r->>'value')::numeric is distinct from expected then raise exception 'MRR differs from canonical snapshots.';end if;
 begin perform public.challenge_assistant_query(tok,tid,e,'{"metric":"mrr","sql":"drop table","industry":null,"country":null,"dimension":null,"quality_kind":null}');raise exception 'Arbitrary query accepted.';exception when sqlstate '22023' then null;end;
 perform public.challenge_assistant_finish(tok,tid,e,'completed','{"answer":"[QA rollback] Resultado validado","kind":"fact","warnings":[],"evidence":null}','{"input_tokens":100,"output_tokens":30}');
 q=public.challenge_assistant_begin(tok,cid,'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','[QA rollback] MRR da carteira');if q->>'state'<>'cached' then raise exception 'Replay not idempotent.';end if;
 if(select count(*) from assistant.messages where conversation_id=cid and role='user')<>1 then raise exception 'Question duplicated.';end if;
 q=public.challenge_assistant_begin(tok,cid,'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb','[QA rollback] Qualidade opcional');tid=(q->>'turn_id')::uuid;e=(q->>'execution_id')::uuid;
 r=public.challenge_assistant_query(tok,tid,e,'{"metric":"quality","industry":null,"country":null,"dimension":null,"quality_kind":"optional"}');
 if(r->>'value')::integer>(r->>'population')::integer then raise exception 'Quality counts double-count accounts.';end if;
 perform public.challenge_assistant_finish(tok,tid,e,'completed','{"answer":"[QA rollback] Qualidade validada","kind":"fact","warnings":[],"evidence":null}','{}');
 perform public.challenge_assistant_update(tok,cid,'context','',false,'{}');
 foreach metric_name in array array['accounts','segments','arr_annualized','arr_source','quality','reconciliation','usage','satisfaction'] loop
 q=public.challenge_assistant_begin(tok,cid,gen_random_uuid(),'[QA rollback] Catálogo '||metric_name);tid=(q->>'turn_id')::uuid;e=(q->>'execution_id')::uuid;
 r=public.challenge_assistant_query(tok,tid,e,jsonb_build_object('metric',metric_name,'industry',null,'country',null,'dimension',case when metric_name='segments' then 'industry' else null end,'quality_kind',case when metric_name='quality' then 'all_supported' else null end));
 if metric_name='arr_annualized' and(r->>'value')::numeric<>expected*12 then raise exception 'Annualization differs from MRR times twelve.';end if;
 if metric_name='accounts' and(r->>'value')::integer<>(select count(*) from core.accounts where version_id=(r->>'version_id')::uuid) then raise exception 'Account count differs from source.';end if;
 if metric_name='quality' and(r->>'value')::integer>(r->>'population')::integer then raise exception 'Quality overlap not deduplicated.';end if;
 perform public.challenge_assistant_finish(tok,tid,e,'completed',jsonb_build_object('answer','[QA rollback] Catálogo validado','kind','fact','evidence',r),'{}');
 end loop;
 select user_id into original_owner from assistant.conversations where id=cid;select id into other_user from auth.users where id<>original_owner and deleted_at is null limit 1;
 if other_user is null then raise exception 'Second existing user required for ownership test.';end if;
 update assistant.conversations set user_id=other_user where id=cid;
 begin perform public.challenge_assistant_conversation(tok,cid,null);raise exception 'Another user history exposed.';exception when sqlstate 'PT404' then null;end;
 begin perform public.challenge_assistant_list(repeat('0',64),'',false,0);raise exception 'Anonymous history exposed.';exception when sqlstate '28000' then null;end;
 if has_function_privilege('authenticated','public.challenge_assistant_query(text,uuid,uuid,jsonb)','EXECUTE') or has_table_privilege('authenticated','assistant.messages','SELECT') then raise exception 'Browser bypass allowed.';end if;
end $$;
rollback;
select 'passed' as assistant_database_tests,'rollback' as transaction,'no Auth identities or sessions created' as auth_fixture;
