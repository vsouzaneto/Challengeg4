-- Teste de contrato da fundação, escrito antes da migração.
-- Deve falhar em banco vazio. Testes adicionais com fixtures são transacionais.
do $test$
declare v_count integer;
begin
  select count(*) into v_count from pg_namespace where nspname in ('access','ingest','core','analytics','operations');
  if v_count <> 5 then raise exception 'Os cinco schemas de contexto precisam existir'; end if;
  if to_regclass('ingest.raw_rows') is null or to_regclass('core.feature_usage') is null then
    raise exception 'Persistência de origem e uso canônico precisa existir';
  end if;
  if exists (select 1 from pg_class c join pg_namespace n on n.oid=c.relnamespace
             where n.nspname in ('access','ingest','core','analytics','operations') and c.relkind='r' and not c.relrowsecurity) then
    raise exception 'Todas as tabelas do projeto precisam ter RLS';
  end if;
  if has_schema_privilege('anon','ingest','USAGE') or has_schema_privilege('anon','core','USAGE') then
    raise exception 'Anonymous não pode acessar dados internos';
  end if;
  if has_function_privilege('authenticated','analytics.build_run(uuid,date)','EXECUTE') then
    raise exception 'Construção de versão exige backend autorizado';
  end if;
end $test$;
