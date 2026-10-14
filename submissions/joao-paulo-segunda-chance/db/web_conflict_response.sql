-- Business conflicts are HTTP 409; never masquerade as transient serialization errors.
create or replace function public.challenge_web_transition(p_token text,p_action uuid,p_revision integer,p_status text,p_result text)
 returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid; a operations.actions; begin
 sess=access.web_session(p_token);
 select x.* into strict a from operations.actions x join access.workspaces w on w.id=x.workspace_id where x.id=p_action and w.slug='ravenstack' for update of x;
 if a.revision<>p_revision then raise exception 'Ação alterada por outra sessão. Atualize e tente novamente.' using errcode='PT409'; end if;
 if p_status not in('in_progress','completed','cancelled') or a.status in('completed','cancelled') or p_status=a.status then raise exception 'Transição não permitida'; end if;
 if p_status in('completed','cancelled') and coalesce(length(trim(p_result)),0)<10 then raise exception 'Informe um resultado/motivo com pelo menos 10 caracteres'; end if;
 if length(p_result)>3000 then raise exception 'Resultado excede 3000 caracteres'; end if;
 update operations.actions set status=p_status,result_note=nullif(trim(p_result),''),revision=revision+1,updated_at=now() where id=a.id;
 insert into operations.action_history(workspace_id,action_id,actor_session_id,from_status,to_status,result_note,revision)
 values(a.workspace_id,a.id,sess,a.status,p_status,nullif(trim(p_result),''),a.revision+1);
 return jsonb_build_object('id',a.id,'revision',a.revision+1,'status',p_status);
end $$;

