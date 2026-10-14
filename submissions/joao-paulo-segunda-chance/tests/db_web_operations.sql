begin;
do $$
declare ws uuid; sess uuid; ev uuid; action uuid; d jsonb; again jsonb; failed boolean=false;
begin
 select id into ws from access.workspaces where slug='ravenstack';
 sess=public.challenge_web_session(repeat('a',64),repeat('b',64));
 select e.id into ev from analytics.evidence_items e join access.workspaces w on w.current_run_id=e.run_id where w.id=ws limit 1;
 d=public.challenge_web_decide(repeat('a',64),'idempotent-test',ev,null,'Validar histórico','Evento ausente impede concluir motivo.','Pessoa declarada','Conferir origem','Equipe Dados',current_date+7);
 again=public.challenge_web_decide(repeat('a',64),'idempotent-test',ev,null,'Validar histórico','Evento ausente impede concluir motivo.','Pessoa declarada','Conferir origem','Equipe Dados',current_date+7);
 if d<>again then raise exception 'Replay deve retornar a mesma decisão'; end if;
 action=(d->>'action_id')::uuid;
 begin perform public.challenge_web_transition(repeat('a',64),action,0,'completed',''); exception when others then failed=true; end;
 if not failed then raise exception 'Conclusão sem resultado deve falhar'; end if;
 perform public.challenge_web_transition(repeat('a',64),action,0,'in_progress',null);
 failed=false;
 begin perform public.challenge_web_transition(repeat('a',64),action,0,'completed','Resultado'); exception when sqlstate 'PT409' then failed=true; end;
 if not failed then raise exception 'Revisão desatualizada deve falhar'; end if;
 perform public.challenge_web_transition(repeat('a',64),action,1,'completed','Histórico verificado, sem inferir causalidade.');
 if (select count(*) from operations.action_history where action_id=action)<>3 then raise exception 'Histórico deve ser completo'; end if;
 failed=false;
 begin perform public.challenge_web_dashboard(repeat('c',64)); exception when others then failed=true; end;
 if not failed then raise exception 'Sessão desconhecida deve falhar'; end if;
 if has_function_privilege('anon','public.challenge_web_decide(text,text,uuid,uuid,text,text,text,text,text,date)','execute') then raise exception 'RPC de escrita não pode ser anônima'; end if;
end $$;
rollback;
