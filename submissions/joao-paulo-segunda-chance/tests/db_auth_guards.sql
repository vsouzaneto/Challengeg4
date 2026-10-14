-- No Auth identities are created or altered. All statements are rolled back.
begin;
set local role service_role;
do $$declare blocked boolean=false;begin
 begin perform public.challenge_web_bind(repeat('a',64),gen_random_uuid(),gen_random_uuid(),repeat('b',64));exception when sqlstate '28000' then blocked=true;end;
 if not blocked then raise exception 'Unknown Auth identity allowed';end if;
 blocked=false;begin perform access.authenticated_web_session(repeat('a',64));exception when sqlstate '28000' then blocked=true;end;
 if not blocked then raise exception 'Unknown app session allowed';end if;
 if not exists(select 1 from access.authentication_settings where not authentication_required) then raise exception 'Expected pending activation';end if;
 blocked=false;begin perform public.challenge_enable_auth();exception when sqlstate 'PT409' then blocked=true;end;
 if not blocked then raise exception 'Enabled auth without both configured users';end if;
 if not exists(select 1 from access.authentication_settings where not authentication_required) then raise exception 'Activation changed despite missing accounts';end if;
 if has_function_privilege('anon','public.challenge_web_bind(text,uuid,uuid,text)','execute') or has_function_privilege('authenticated','public.challenge_enable_auth()','execute') then raise exception 'Auth privilege leaked';end if;
 if has_function_privilege('authenticated','public.challenge_dashboard(uuid)','execute') or has_table_privilege('authenticated','analytics.account_snapshots','select') then raise exception 'Alternate browser data path bypasses live session guard';end if;
end $$;
rollback;
