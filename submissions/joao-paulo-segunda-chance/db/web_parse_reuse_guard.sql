-- Binary identity alone does not determine an Excel sheet/mapping interpretation.
create function ingest.web_file_matches(p_file uuid,p_headers jsonb,p_rows jsonb) returns boolean
language sql stable security invoker set search_path='' as $$
 select (select count(*) from ingest.raw_rows where file_id=p_file)=jsonb_array_length(p_rows)
 and not exists(
 select 1 from jsonb_array_elements(p_rows) x
 left join ingest.raw_rows r on r.file_id=p_file and r.row_number=(x->>0)::integer
 where r.id is null
 or r.content<>jsonb_object(array(select jsonb_array_elements_text(p_headers)),array(select jsonb_array_elements_text(x->1)))
 or r.normalized_content is distinct from jsonb_object(array(select jsonb_array_elements_text(p_headers)),array(select jsonb_array_elements_text(x->2)))
 or r.validation_errors is distinct from x->3)
$$;
create function ingest.guard_web_parse_reuse() returns trigger language plpgsql security invoker set search_path='' as $$
begin
 if new.stage in ('processing','verified','published') and exists(select 1 from ingest.source_files where id=new.file_id and status='verified')
 and not ingest.web_file_matches(new.file_id,new.headers,new.packed_rows) then
 raise exception 'Arquivo com os mesmos bytes já interpretado com outra aba ou mapeamento. Exporte esta aba em um arquivo separado para preservar a linhagem.';
 end if;
 return new;
end $$;
create trigger web_parse_reuse_guard before insert or update of stage on ingest.web_uploads for each row execute function ingest.guard_web_parse_reuse();
revoke execute on function ingest.web_file_matches(uuid,jsonb,jsonb),ingest.guard_web_parse_reuse() from public,anon,authenticated;
grant execute on function ingest.web_file_matches(uuid,jsonb,jsonb),ingest.guard_web_parse_reuse() to service_role;
