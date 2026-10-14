-- A future clock date must not be treated as observed source coverage.
begin;
do $test$
declare v uuid; blocked boolean=false;
begin
  select r.version_id into strict v from access.workspaces w join analytics.analysis_runs r on r.id=w.current_run_id
    where w.slug='ravenstack';
  begin perform analytics.build_run(v,'2099-01-01');
  exception when raise_exception then blocked=true;
  end;
  if not blocked then raise exception 'Data além das fontes foi aceita'; end if;
end $test$;
rollback;
