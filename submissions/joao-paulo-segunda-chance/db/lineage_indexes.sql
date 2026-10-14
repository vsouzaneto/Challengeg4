create index workspaces_current_run_idx on access.workspaces(id,current_run_id);
create index snapshots_run_fk_idx on analytics.account_snapshots(workspace_id,run_id);
create index dataset_batch_fk_idx on analytics.dataset_versions(workspace_id,batch_id);
create index dataset_parent_fk_idx on analytics.dataset_versions(workspace_id,parent_version_id);
create index quality_version_fk_idx on analytics.quality_checks(workspace_id,version_id);
create index version_sources_full_file_idx on analytics.version_sources(workspace_id,file_id,source_type);
create index version_sources_version_fk_idx on analytics.version_sources(workspace_id,version_id);
create index file_chunks_file_fk_idx on ingest.file_chunks(workspace_id,file_id);
create index source_files_contract_fk_idx on ingest.source_files(source_type,contract_version);
create index history_actor_fk_idx on operations.action_history(actor_user_id);

-- Evidence cannot point to a snapshot from a different analysis run.
alter table analytics.account_snapshots add constraint snapshot_run_identity unique(workspace_id,id,run_id);
alter table analytics.evidence_items add constraint evidence_snapshot_same_run
  foreign key(workspace_id,snapshot_id,run_id) references analytics.account_snapshots(workspace_id,id,run_id);
create index evidence_snapshot_run_fk_idx on analytics.evidence_items(workspace_id,snapshot_id,run_id);
