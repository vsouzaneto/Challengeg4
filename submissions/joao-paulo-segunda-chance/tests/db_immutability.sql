-- Written before strengthening the guards. All fixtures are synthetic and rolled back.
begin;
do $test$
declare ws uuid; b uuid; f_old uuid; f_new uuid; r bigint; v_old uuid; v_new uuid; blocked boolean;
begin
  insert into access.workspaces(slug,name) values('qa-'||gen_random_uuid(),'Synthetic QA') returning id into ws;
  insert into ingest.import_batches(workspace_id,request_hash,label,actor)
    values(ws,'qa-'||gen_random_uuid(),'Synthetic QA','test') returning id into b;
  insert into ingest.source_files(workspace_id,batch_id,source_type,contract_version,filename,file_hash,expected_rows,expected_bytes)
    values(ws,b,'accounts','1.0.0','synthetic.csv',encode(sha256(convert_to('x','UTF8')),'hex'),1,1) returning id into f_old;
  insert into ingest.source_files(workspace_id,batch_id,source_type,contract_version,filename,file_hash,expected_rows,expected_bytes)
    values(ws,b,'accounts','1.0.0','synthetic-other.csv',repeat('0',64),0,0) returning id into f_new;
  perform ingest.append_file_chunk(f_old,0,'x');
  insert into ingest.raw_rows(workspace_id,file_id,row_number,content,record_hash)
    values(ws,f_old,1,'{"account_id":"QA"}',repeat('0',64)) returning id into r;
  perform ingest.verify_file(f_old);
  blocked=false;
  begin
    update ingest.raw_rows set file_id=f_new where id=r;
  exception when raise_exception then blocked=true;
  end;
  if not blocked then raise exception 'Linha de fonte verificada conseguiu mudar de arquivo'; end if;

  insert into analytics.dataset_versions(workspace_id,batch_id) values(ws,b) returning id into v_old;
  insert into ingest.import_batches(workspace_id,request_hash,label,actor)
    values(ws,'qa-'||gen_random_uuid(),'Synthetic QA 2','test') returning id into b;
  insert into analytics.dataset_versions(workspace_id,batch_id) values(ws,b) returning id into v_new;
  insert into core.accounts(workspace_id,version_id,source_row_id,account_id,account_name,industry,country,
    referral_source,plan_tier,seats,is_trial,churn_flag,signup_date)
    values(ws,v_old,r,'QA','Synthetic QA','QA','QA','QA','QA',1,false,false,'2024-01-01');
  update analytics.dataset_versions set status='published' where id=v_old;
  blocked=false;
  begin
    update core.accounts set version_id=v_new where version_id=v_old;
  exception when raise_exception then blocked=true;
  end;
  if not blocked then raise exception 'Registro publicado conseguiu mudar para versão candidata'; end if;
end $test$;
rollback;
