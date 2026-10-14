-- ISOLATED LOCAL DATABASE ONLY. Never execute against the shared Supabase project.
-- This fixture has NOT passed in this execution. Native shared execution was declined.
-- Backend access contract. All identities and changes are rolled back.
begin;
do $$declare u uuid=gen_random_uuid();c uuid=gen_random_uuid();x uuid=gen_random_uuid();s uuid=gen_random_uuid();cs uuid=gen_random_uuid();xs uuid=gen_random_uuid();ws uuid;begin
 select id into strict ws from access.workspaces where slug='ravenstack';
 insert into auth.users(id,email,email_confirmed_at,raw_user_meta_data) values(u,'qa-auth-admin@example.invalid',now(),'{}'),(c,'qa-auth-user@example.invalid',now(),'{"role":"administrator"}'),(x,'qa-auth-outsider@example.invalid',now(),'{}');
 insert into auth.sessions(id,user_id) values(s,u),(cs,c),(xs,x);
 insert into access.memberships(workspace_id,user_id,role,display_name) values(ws,u,'administrator','QA Admin'),(ws,c,'decision_maker','QA User');
end $$;
set local role service_role;
do $$declare u uuid;c uuid;x uuid;s uuid;cs uuid;xs uuid;old_token text=repeat('f',64);result jsonb;ws uuid;sid uuid;blocked boolean;d jsonb;p jsonb;begin
 select id into u from auth.users where email='qa-auth-admin@example.invalid';select id into c from auth.users where email='qa-auth-user@example.invalid';select id into x from auth.users where email='qa-auth-outsider@example.invalid';
 select id into s from auth.sessions where user_id=u;select id into cs from auth.sessions where user_id=c;select id into xs from auth.sessions where user_id=x;select id into ws from access.workspaces where slug='ravenstack';
 perform public.challenge_web_session(old_token,repeat('e',64));
 result=public.challenge_web_bind(repeat('a',64),u,s,repeat('d',64));if result->'user'->>'role'<>'administrator' then raise exception 'Admin role wrong';end if;
 result=public.challenge_web_bind(repeat('b',64),c,cs,repeat('d',64));if result->'user'->>'role'<>'user' then raise exception 'Mutable metadata promoted regular user';end if;
 sid=access.authenticated_web_session(repeat('b',64));perform public.challenge_web_dashboard(repeat('a',64));perform public.challenge_web_dashboard(repeat('b',64));
 blocked=false;begin perform public.challenge_web_bind(repeat('c',64),x,xs,repeat('d',64));exception when sqlstate 'PT403' then blocked=true;end;if not blocked then raise exception 'Nonmember allowed';end if;
 perform public.challenge_enable_auth();
 blocked=false;begin perform public.challenge_web_session(repeat('1',64),repeat('e',64));exception when sqlstate '28000' then blocked=true;end;if not blocked then raise exception 'New anonymous session allowed';end if;
 blocked=false;begin perform public.challenge_web_dashboard(old_token);exception when sqlstate '28000' then blocked=true;end;if not blocked then raise exception 'Old capability still allowed';end if;
 p=public.challenge_web_scope_preview(repeat('b',64),(select current_run_id from access.workspaces where id=ws),'{"type":"portfolio"}','missing_cancel');
 d=public.challenge_web_decide_scoped(repeat('b',64),'qa-auth-decision',(select current_run_id from access.workspaces where id=ws),'{"type":"portfolio"}','missing_cancel',p->>'preview_hash','Investigar extração','Verificar lacunas na origem dos eventos.','Autor falso','Conferir origem','QA User','2026-10-13');
 if not exists(select 1 from operations.decisions where id=(d->>'decision_id')::uuid and actor_user_id=c and actor_display_name='QA User') then raise exception 'Verified author not attached';end if;
 if not exists(select 1 from operations.action_history where action_id=(d->>'action_id')::uuid and actor_user_id=c) then raise exception 'Verified history author missing';end if;
 perform public.challenge_web_transition(repeat('a',64),(d->>'action_id')::uuid,0,'in_progress',null);
 if not exists(select 1 from operations.action_history where action_id=(d->>'action_id')::uuid and revision=1 and actor_user_id=u) then raise exception 'Admin transition not attributed';end if;
 update access.memberships set active=false where user_id=c;blocked=false;begin perform public.challenge_web_dashboard(repeat('b',64));exception when sqlstate 'PT403' then blocked=true;end;if not blocked then raise exception 'Inactive membership allowed';end if;update access.memberships set active=true where user_id=c;
 perform public.challenge_web_logout(repeat('b',64));blocked=false;begin perform public.challenge_web_bind(repeat('b',64),c,cs,repeat('d',64));exception when sqlstate '28000' then blocked=true;end;if not blocked then raise exception 'Logged-out session rebound';end if;
 if has_function_privilege('anon','public.challenge_web_bind(text,uuid,uuid,text)','execute') or has_function_privilege('authenticated','public.challenge_enable_auth()','execute') then raise exception 'Privilege leaked';end if;
end $$;
reset role;
do $$declare uid uuid;begin select id into uid from auth.users where email='qa-auth-admin@example.invalid';delete from auth.sessions where user_id=uid;end $$;
set local role service_role;
do $$declare blocked boolean=false;begin begin perform public.challenge_web_dashboard(repeat('a',64));exception when sqlstate '28000' then blocked=true;end;if not blocked then raise exception 'Revoked Auth session allowed';end if;end $$;
rollback;
