-- Run after local_users_fixture.sql and the user_management migration, local only.
do $$ declare p jsonb;d jsonb;o jsonb;revision integer;denied boolean;begin
 p=access.user_profile(repeat('a',64));assert p->>'role'='super_admin';
 p=access.user_profile(repeat('b',64));assert p->>'role'='administrator';
 -- An administrator cannot modify/reset the protected owner or promote any user to owner.
 denied=false;begin perform public.challenge_users_update(repeat('b',64),'11111111-1111-4111-8111-111111111111',2,'{"name":"Bad edit","role":"user","active":false,"permissions":["method.read"]}');exception when sqlstate 'PT403' then denied=true;end;assert denied;
 denied=false;begin perform public.challenge_users_prepare(repeat('b',64),gen_random_uuid(),'reset_password','11111111-1111-4111-8111-111111111111',2,'{}');exception when sqlstate 'PT403' then denied=true;end;assert denied;
 denied=false;begin perform access.user_payload('{"name":"Invalid","role":"super_admin","active":true,"permissions":[]}');exception when sqlstate '22023' then denied=true;end;assert denied;
 denied=false;begin perform public.challenge_users_list(repeat('c',64));exception when sqlstate 'PT403' then denied=true;end;assert denied;
 assert access.valid_permissions(array['analytics.read']);assert not access.valid_permissions(array['assistant.use']);assert not access.valid_permissions(array['data.publish']);assert not access.valid_permissions(array['method.read',null]);
 -- Minimal permissions, denied endpoints and live permission re-check without JWT refresh.
 perform public.challenge_users_update(repeat('b',64),'33333333-3333-4333-8333-333333333333',1,'{"name":"Reader","role":"user","active":true,"permissions":["method.read"]}');
 p=access.require_permission(repeat('c',64),'method.read');assert p->>'name'='Reader';
 denied=false;begin perform access.require_permission(repeat('c',64),'accounts.read');exception when sqlstate 'PT403' then denied=true;end;assert denied;
 denied=false;begin perform public.challenge_web_detail(repeat('c',64),gen_random_uuid());exception when sqlstate 'PT403' then denied=true;end;assert denied;
 denied=false;begin perform public.challenge_web_begin(repeat('c',64),gen_random_uuid());exception when sqlstate 'PT403' then denied=true;end;assert denied;
 denied=false;begin perform public.challenge_web_scope_options(repeat('c',64),gen_random_uuid());exception when sqlstate 'PT403' then denied=true;end;assert denied;
 denied=false;begin perform public.challenge_assistant_list(repeat('c',64));exception when sqlstate 'PT403' then denied=true;end;assert denied;
 denied=false;begin perform public.challenge_users_update(repeat('b',64),'33333333-3333-4333-8333-333333333333',1,'{"name":"Stale","role":"user","active":true,"permissions":["method.read"]}');exception when sqlstate 'PT409' then denied=true;end;assert denied;
 -- Dashboard never returns protected account rows/quality examples to aggregate-only access.
 update access.memberships set permissions=array['analytics.read'] where user_id='33333333-3333-4333-8333-333333333333';
 d=public.challenge_web_dashboard(repeat('c',64));assert jsonb_array_length(d->'accounts')=0;assert jsonb_array_length(d->'quality')=0;assert jsonb_array_length(d->'analytics')=1;assert d->'analytics'->0->>'contract_mrr'='100';assert position('PRIVATE ACCOUNT' in d::text)=0;
 update access.memberships set permissions=array['quality.read'] where user_id='33333333-3333-4333-8333-333333333333';
 d=public.challenge_web_dashboard(repeat('c',64));assert jsonb_array_length(d->'accounts')=0;assert jsonb_array_length(d->'analytics')=0;assert d->'run'->'metrics'='{}'::jsonb;assert position('PRIVATE ACCOUNT' in d::text)=0;
 update access.memberships set permissions=access.permission_codes() where user_id='33333333-3333-4333-8333-333333333333';
 d=public.challenge_assistant_list(repeat('c',64));assert d->>'total'='0';
 update access.memberships set permissions=array['method.read'] where user_id='33333333-3333-4333-8333-333333333333';
 -- Password reset immediately closes existing app sessions, never returning/storing a password.
 o=public.challenge_users_prepare(repeat('b',64),'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb','reset_password','33333333-3333-4333-8333-333333333333',2,'{}');assert not(o?'password');
 denied=false;begin perform access.user_profile(repeat('c',64));exception when sqlstate '28000' then denied=true;end;assert denied;
 perform public.challenge_users_finish(repeat('b',64),'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',(o->>'attempt')::uuid);
 -- Simulate a NEW local session after reset, not a revived old JWT.
 insert into auth.sessions(id,user_id) values('dddddddd-3333-4333-8333-333333333333','33333333-3333-4333-8333-333333333333');
 perform public.challenge_web_bind(repeat('e',64),'33333333-3333-4333-8333-333333333333','dddddddd-3333-4333-8333-333333333333',repeat('f',64));
 p=access.user_profile(repeat('e',64),true);assert(p->>'password_change_required')::boolean;
 denied=false;begin perform access.require_permission(repeat('e',64),'method.read');exception when sqlstate 'PT403' then denied=true;end;assert denied;
 o=public.challenge_users_prepare(repeat('e',64),'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee','change_password',null,null,'{}');
 perform public.challenge_users_finish(repeat('e',64),'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee',(o->>'attempt')::uuid);
 assert not(access.user_profile(repeat('e',64))->>'password_change_required')::boolean;
 -- Create is reserved before Auth. Completion requires server-only creation marker.
 o=public.challenge_users_prepare(repeat('b',64),'ffffffff-ffff-4fff-8fff-ffffffffffff','create',null,null,'{"name":"New user","email":"new@example.invalid","role":"user","active":true,"permissions":["method.read"]}');
 denied=false;begin perform public.challenge_users_finish(repeat('b',64),'ffffffff-ffff-4fff-8fff-ffffffffffff',(o->>'attempt')::uuid);exception when sqlstate 'PT409' then denied=true;end;assert denied;
 insert into auth.users(id,email,email_confirmed_at,raw_app_meta_data) values('44444444-4444-4444-8444-444444444444','new@example.invalid',now(),'{"ravenstack_creation_operation":"ffffffff-ffff-4fff-8fff-ffffffffffff"}');
 perform public.challenge_users_finish(repeat('b',64),'ffffffff-ffff-4fff-8fff-ffffffffffff',(o->>'attempt')::uuid);
 assert(select password_change_required from access.memberships where user_id='44444444-4444-4444-8444-444444444444');
 o=public.challenge_users_prepare(repeat('b',64),'ffffffff-ffff-4fff-8fff-ffffffffffff','create',null,null,'{}');assert o->>'state'='completed';
 assert(select count(*)=1 from access.memberships where user_id='44444444-4444-4444-8444-444444444444');
 -- Another administrator can resume an expired operation, never an active lease.
 o=public.challenge_users_prepare(repeat('b',64),'99999999-9999-4999-8999-999999999999','create',null,null,'{"name":"Pending local","email":"pending@example.invalid","role":"user","active":true,"permissions":["method.read"]}');
 denied=false;begin perform public.challenge_users_takeover(repeat('a',64),'99999999-9999-4999-8999-999999999999');exception when sqlstate 'PT409' then denied=true;end;assert denied;
 update access.user_operations set lease_until=now()-interval '1 second' where id='99999999-9999-4999-8999-999999999999';
 perform public.challenge_users_takeover(repeat('a',64),'99999999-9999-4999-8999-999999999999');
 assert exists(select 1 from access.user_audit where action='operation_resumed' and actor_id='11111111-1111-4111-8111-111111111111');
 denied=false;begin perform public.challenge_users_prepare(repeat('b',64),'99999999-9999-4999-8999-999999999999','create',null,null,'{}');exception when sqlstate 'PT409' then denied=true;end;assert denied;
 o=public.challenge_users_prepare(repeat('a',64),'99999999-9999-4999-8999-999999999999','create',null,null,'{"name":"Pending local","email":"pending@example.invalid","role":"user","active":true,"permissions":["method.read"]}');assert o->>'state'='pending';assert (select actor_id='11111111-1111-4111-8111-111111111111'::uuid from access.user_operations where id='99999999-9999-4999-8999-999999999999');
 -- Deactivate retains audit but denies existing sessions.
 select m.revision into revision from access.memberships m where user_id='33333333-3333-4333-8333-333333333333';
 perform public.challenge_users_update(repeat('b',64),'33333333-3333-4333-8333-333333333333',revision,'{"name":"Reader","role":"user","active":false,"permissions":["method.read"]}');
 denied=false;begin perform access.user_profile(repeat('e',64));exception when sqlstate '28000' then denied=true;end;assert denied;
 assert not has_function_privilege('authenticated','public.challenge_users_list(text)','execute');
 assert not has_function_privilege('anon','public.challenge_web_dashboard(text)','execute');
 assert not has_function_privilege('authenticated','access.challenge_web_dashboard(text)','execute');
 assert not has_table_privilege('authenticated','access.user_operations','select');
 assert not exists(select 1 from access.user_operations where data::text like '%password%');
end $$;
