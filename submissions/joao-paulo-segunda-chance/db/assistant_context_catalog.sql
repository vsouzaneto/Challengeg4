-- Add bounded, version-specific canonical filter values; reset model context after explicit context updates.
create or replace function public.challenge_assistant_begin(p_token text,p_conversation uuid,p_request uuid,p_question text) returns jsonb language plpgsql security invoker set search_path='' as $$
declare c assistant.conversations;t assistant.turns;e uuid;hist jsonb;begin
 c=assistant.owned(p_token,p_conversation);if c.archived then raise exception 'Restaure a conversa para continuar.' using errcode='PT409';end if;
 if length(btrim(p_question)) not between 1 and 2000 or p_request is null then raise exception 'Pergunta inválida.' using errcode='22023';end if;
 perform 1 from assistant.conversations where id=c.id for update;
 select * into t from assistant.turns where conversation_id=c.id and request_key=p_request;
 if found then
  if t.question<>btrim(p_question) then raise exception 'Solicitação reutilizada com outra pergunta.' using errcode='PT409';end if;
  if t.status='completed' then return jsonb_build_object('state','cached','result',t.result);end if;
  if t.status='pending' and t.lease_until>now() then raise exception 'Resposta em processamento; aguarde e recarregue a conversa.' using errcode='PT409';end if;
  if(select count(*) from assistant.executions where turn_id=t.id)>=3 then raise exception 'Limite de tentativas desta pergunta atingido.' using errcode='PT429';end if;
 else
  if exists(select 1 from assistant.turns where conversation_id=c.id and status='pending' and lease_until>now()) then raise exception 'Aguarde a resposta atual.' using errcode='PT409';end if;
  insert into assistant.turns(conversation_id,request_key,question,run_id,filters) values(c.id,p_request,btrim(p_question),c.run_id,c.filters) returning * into t;
  insert into assistant.messages(conversation_id,turn_id,role,content,run_id) values(c.id,t.id,'user',t.question,t.run_id);
 end if;
 perform pg_advisory_xact_lock(hashtext('assistant-budget:'||c.workspace_id));
 if(select count(*) from assistant.executions where workspace_id=c.workspace_id and started_at>date_trunc('day',now() at time zone 'America/Sao_Paulo') at time zone 'America/Sao_Paulo')>=200
 or(select count(*) from assistant.executions where user_id=c.user_id and workspace_id=c.workspace_id and started_at>date_trunc('day',now() at time zone 'America/Sao_Paulo') at time zone 'America/Sao_Paulo')>=50 then raise exception 'Limite diário de consultas atingido.' using errcode='PT429';end if;
 insert into assistant.executions(turn_id,user_id,workspace_id) values(t.id,c.user_id,c.workspace_id) returning id into e;
 update assistant.turns set status='pending',current_execution=e,lease_until=now()+interval '90 seconds' where id=t.id;
 update assistant.conversations set updated_at=now(),title=case when title='Nova conversa' then left(t.question,80) else title end where id=c.id;
 select coalesce(jsonb_agg(jsonb_build_object('role',x.role,'content',x.content) order by x.seq),'[]') into hist from(select role,content,seq from assistant.messages where conversation_id=c.id and role in('user','assistant') and turn_id<>t.id and run_id=t.run_id and seq>coalesce((select max(m.seq) from assistant.messages m where m.conversation_id=c.id and m.role='context'),0) order by seq desc limit 8)x;
 return jsonb_build_object('state','ready','turn_id',t.id,'execution_id',e,'history',hist,'context',jsonb_build_object('run_id',t.run_id,'filters',t.filters,'reference_date',(select reference_date from analytics.analysis_runs where id=t.run_id),'catalog',jsonb_build_object('industry',(select coalesce(jsonb_agg(x.value),'[]') from(select distinct industry as value from core.accounts where version_id=(select version_id from analytics.analysis_runs where id=t.run_id) and length(industry)<=100 order by 1 limit 100)x),'country',(select coalesce(jsonb_agg(x.value),'[]') from(select distinct country as value from core.accounts where version_id=(select version_id from analytics.analysis_runs where id=t.run_id) and length(country)<=100 order by 1 limit 100)x),'plan_tier',(select coalesce(jsonb_agg(x.value),'[]') from(select distinct plan_tier as value from core.accounts where version_id=(select version_id from analytics.analysis_runs where id=t.run_id) and length(plan_tier)<=100 order by 1 limit 100)x))));
end $$;
