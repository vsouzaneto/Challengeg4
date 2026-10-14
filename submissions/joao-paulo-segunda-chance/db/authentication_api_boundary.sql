-- Browser access goes through the authenticated Edge gateways, including reads.
-- Avoid alternate prepared-data RPCs bypassing live session revocation checks.
revoke execute on function public.challenge_dashboard(uuid),public.challenge_accounts(uuid,integer,integer) from authenticated;
revoke select on access.memberships,access.workspaces from authenticated;
revoke select on analytics.dataset_versions,analytics.version_sources,analytics.analysis_runs,
 analytics.account_snapshots,analytics.evidence_items,analytics.quality_checks from authenticated;
revoke select on operations.decisions,operations.actions,operations.action_history from authenticated;
