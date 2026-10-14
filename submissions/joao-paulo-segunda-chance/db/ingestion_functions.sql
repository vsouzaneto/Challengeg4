create function ingest.append_file_chunk(p_file uuid,p_index integer,p_text text) returns integer
language plpgsql security invoker set search_path='' as $$
declare ws uuid; existing bytea; incoming bytea;
begin
  select workspace_id into strict ws from ingest.source_files where id=p_file;
  incoming=convert_to(p_text,'UTF8');
  select data into existing from ingest.file_chunks where file_id=p_file and chunk_index=p_index;
  if found then
    if existing<>incoming then raise exception 'Chunk reapresentado com conteúdo conflitante'; end if;
    return 0;
  end if;
  insert into ingest.file_chunks values(ws,p_file,p_index,incoming);
  return 1;
end $$;

create function ingest.append_rows(p_file uuid,p_payload jsonb) returns integer
language plpgsql security invoker set search_path='' as $$
declare ws uuid; inserted integer; header text[]; rows jsonb; existing_conflict boolean;
begin
  select workspace_id into strict ws from ingest.source_files where id=p_file;
  select array_agg(value) into header from jsonb_array_elements_text(p_payload->'headers');
  rows=p_payload->'rows';
  if jsonb_typeof(rows)<>'array' or coalesce(cardinality(header),0)=0 then raise exception 'Payload inválido'; end if;
  select exists(
    select 1 from jsonb_array_elements(rows) x
    join ingest.raw_rows r on r.file_id=p_file and r.row_number=(x->>0)::integer
    where r.content<>jsonb_object(header,array(select jsonb_array_elements_text(x->1)))
      or r.normalized_content is distinct from case when jsonb_typeof(x->2)='array'
           then jsonb_object(header,array(select jsonb_array_elements_text(x->2))) else null end
  ) into existing_conflict;
  if existing_conflict then raise exception 'Linha reapresentada com conteúdo conflitante'; end if;
  insert into ingest.raw_rows(workspace_id,file_id,row_number,content,normalized_content,validation_errors,record_hash)
  select ws,p_file,(x->>0)::integer,
    jsonb_object(header,array(select jsonb_array_elements_text(x->1))),
    case when jsonb_typeof(x->2)='array' then jsonb_object(header,array(select jsonb_array_elements_text(x->2))) else null end,
    x->3,encode(sha256(convert_to(jsonb_object(header,array(select jsonb_array_elements_text(x->1)))::text,'UTF8')),'hex')
  from jsonb_array_elements(rows) x
  where not exists(select 1 from ingest.raw_rows r where r.file_id=p_file and r.row_number=(x->>0)::integer);
  get diagnostics inserted=row_count;
  return inserted;
end $$;
revoke execute on function ingest.append_file_chunk(uuid,integer,text),ingest.append_rows(uuid,jsonb) from public,anon,authenticated;
grant execute on function ingest.append_file_chunk(uuid,integer,text),ingest.append_rows(uuid,jsonb) to service_role;
