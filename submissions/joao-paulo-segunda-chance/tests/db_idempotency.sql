-- Test verified-file replay only with a synthetic source; rollback everything.
begin;
do $test$
declare ws uuid; b uuid; f uuid; p jsonb; csv text; first_count integer; replay_count integer;
begin
  csv=E'account_id\nSYNTHETIC-QA\n';
  p='{"headers":["account_id"],"rows":[[1,["SYNTHETIC-QA"],["SYNTHETIC-QA"],[]]]}';
  insert into access.workspaces(slug,name) values('qa-'||gen_random_uuid(),'Synthetic replay QA') returning id into ws;
  insert into ingest.import_batches(workspace_id,request_hash,label,actor)
    values(ws,'qa-'||gen_random_uuid(),'Synthetic replay QA','test') returning id into b;
  insert into ingest.source_files(workspace_id,batch_id,source_type,contract_version,filename,file_hash,expected_rows,expected_bytes)
    values(ws,b,'accounts','1.0.0','synthetic.csv',encode(sha256(convert_to(csv,'UTF8')),'hex'),1,octet_length(convert_to(csv,'UTF8')))
    returning id into f;
  perform ingest.append_file_chunk(f,0,csv);
  first_count=ingest.append_rows(f,p);
  if first_count<>1 then raise exception 'Primeira carga não inseriu uma linha'; end if;
  perform ingest.verify_file(f);
  replay_count=ingest.append_rows(f,p);
  if replay_count<>0 or (select count(*) from ingest.raw_rows where file_id=f)<>1 then
    raise exception 'Replay alterou contagens';
  end if;
  if ingest.append_file_chunk(f,0,csv)<>0 then raise exception 'Replay de bytes não foi idempotente'; end if;
end $test$;
rollback;
