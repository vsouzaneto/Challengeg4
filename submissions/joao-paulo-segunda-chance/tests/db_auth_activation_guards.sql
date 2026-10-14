-- Post-activation acceptance. No Auth identities/sessions or business records created.
begin;
do $$
declare admins integer;users integer;
begin
 if not access.authentication_required() then raise exception 'Login must be activated.';end if;
 select count(*) filter(where m.role='administrator'),count(*) filter(where m.role='decision_maker') into admins,users
 from access.memberships m join auth.users u on u.id=m.user_id join access.workspaces w on w.id=m.workspace_id
 where w.slug='ravenstack' and m.active and m.display_name is not null and u.email_confirmed_at is not null
 and not u.is_anonymous and u.deleted_at is null and(u.banned_until is null or u.banned_until<=now());
 if admins<>1 or users<>1 then raise exception 'Expected both confirmed active profiles.';end if;
 begin
  perform public.challenge_web_session(repeat('a',64),repeat('b',64));
  raise exception 'Legacy session creation unexpectedly accepted.';
 exception when sqlstate '28000' then null;end;
 if has_function_privilege('authenticated','public.challenge_web_bind(text,uuid,uuid,text)','EXECUTE')
 or has_function_privilege('anon','public.challenge_enable_auth()','EXECUTE')
 or has_function_privilege('authenticated','public.challenge_enable_auth()','EXECUTE') then
  raise exception 'Administrative RPC reachable by browser role.';end if;
end $$;
rollback;
select 'passed' as post_activation_guards,'rollback' as transaction,'none' as auth_or_business_writes;
