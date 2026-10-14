-- Synthetic fixture only; no source facts or pointer changes persist.
begin;
set local role service_role;
do $$
declare ws uuid;b uuid;f uuid;p jsonb;csv text;
begin
 csv=E'account_id\nSYNTHETIC-QA\n';p='{"headers":["account_id"],"rows":[[1,["SYNTHETIC-QA"],["SYNTHETIC-QA"],[]]]}';
 insert into access.workspaces(slug,name) values('qa-'||gen_random_uuid(),'Synthetic parsing QA') returning id into ws;
 insert into ingest.import_batches(workspace_id,request_hash,label,actor) values(ws,'qa-'||gen_random_uuid(),'Synthetic parsing QA','test') returning id into b;
 insert into ingest.source_files(workspace_id,batch_id,source_type,contract_version,filename,file_hash,expected_rows,expected_bytes)
 values(ws,b,'accounts','1.0.0','synthetic.csv',encode(sha256(convert_to(csv,'UTF8')),'hex'),1,octet_length(convert_to(csv,'UTF8'))) returning id into f;
 perform ingest.append_file_chunk(f,0,csv);perform ingest.append_rows(f,p);perform ingest.verify_file(f);
 if not ingest.web_file_matches(f,p->'headers',p->'rows') then raise exception 'Equivalent replay rejected';end if;
 if ingest.web_file_matches(f,p->'headers','[[1,["OTHER"],["OTHER"],[]]]') then raise exception 'Different interpretation accepted';end if;
 if ingest.web_file_matches(f,p->'headers','[]') then raise exception 'Different row count accepted';end if;
end $$;
rollback;
