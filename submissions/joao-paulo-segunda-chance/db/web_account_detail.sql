create function public.challenge_web_detail(p_token text,p_snapshot uuid) returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid; s analytics.account_snapshots; v uuid; ref date; begin
 sess=access.web_session(p_token);
 select a.* into strict s from analytics.account_snapshots a join access.workspaces w on w.id=a.workspace_id where a.id=p_snapshot and w.slug='ravenstack';
 select version_id,reference_date into strict v,ref from analytics.analysis_runs where id=s.run_id and status='published';
 return jsonb_build_object('snapshot',to_jsonb(s),
 'evidence',(select coalesce(jsonb_agg(to_jsonb(e)),'[]') from analytics.evidence_items e where snapshot_id=s.id),
 'subscriptions',(select coalesce(jsonb_agg(to_jsonb(c) order by start_date),'[]') from core.subscriptions c where version_id=v and account_id=s.account_id),
 'events',(select coalesce(jsonb_agg(to_jsonb(c) order by churn_date),'[]') from core.churn_events c where version_id=v and account_id=s.account_id and churn_date<=ref),
 'support',(select coalesce(jsonb_agg(to_jsonb(c) order by submitted_at desc),'[]') from core.support_tickets c where version_id=v and account_id=s.account_id and submitted_at<ref+1),
 'usage',(select coalesce(jsonb_agg(jsonb_build_object('day',u.usage_date,'recorded_count',u.usage_count,'eligible',u.usage_date>=c.start_date and u.usage_date>=s.signup_date and(c.end_date is null or u.usage_date<c.end_date) and not exists(select 1 from core.feature_usage d where d.version_id=v and d.usage_id=u.usage_id and d.source_row_id<>u.source_row_id)) order by u.usage_date),'[]')
 from core.feature_usage u join core.subscriptions c on c.version_id=u.version_id and c.subscription_id=u.subscription_id where u.version_id=v and c.account_id=s.account_id and u.usage_date>ref-60 and u.usage_date<=ref));
end $$;
revoke execute on function public.challenge_web_detail(text,uuid) from public,anon,authenticated;
grant execute on function public.challenge_web_detail(text,uuid) to service_role;
