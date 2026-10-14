-- Assistant bounded context. Internal RPCs reuse verified live sessions and owner checks.
create schema assistant;
create table assistant.conversations(
 id uuid primary key default gen_random_uuid(),workspace_id uuid not null references access.workspaces(id),user_id uuid not null references auth.users(id),
 run_id uuid not null,title text not null default 'Nova conversa' check(length(title) between 1 and 80),filters jsonb not null default '{}',archived boolean not null default false,
 created_at timestamptz not null default now(),updated_at timestamptz not null default now(),unique(workspace_id,id),
 foreign key(workspace_id,run_id) references analytics.analysis_runs(workspace_id,id));
create index assistant_owner_history on assistant.conversations(workspace_id,user_id,archived,updated_at desc,id);
create index assistant_conversation_run on assistant.conversations(workspace_id,run_id);
create table assistant.turns(
 id uuid primary key default gen_random_uuid(),conversation_id uuid not null references assistant.conversations(id),request_key uuid not null,
 question text not null check(length(question) between 1 and 2000),run_id uuid not null references analytics.analysis_runs(id),filters jsonb not null,
 status text not null default 'pending' check(status in('pending','completed','failed')),current_execution uuid,lease_until timestamptz,result jsonb,
 created_at timestamptz not null default now(),unique(conversation_id,request_key));
create index assistant_turn_run on assistant.turns(run_id);
create table assistant.executions(
 id uuid primary key default gen_random_uuid(),turn_id uuid not null references assistant.turns(id),user_id uuid not null references auth.users(id),workspace_id uuid not null references access.workspaces(id),
 status text not null default 'pending' check(status in('pending','completed','failed')),model text not null default 'gpt-6-luna',prompt_version text not null default '1.0.0',
 usage jsonb not null default '{}',started_at timestamptz not null default now(),finished_at timestamptz);
create index assistant_execution_budget on assistant.executions(workspace_id,user_id,started_at);
create index assistant_execution_turn on assistant.executions(turn_id);
alter table assistant.turns add foreign key(current_execution) references assistant.executions(id);
create table assistant.messages(
 seq bigint generated always as identity primary key,conversation_id uuid not null references assistant.conversations(id),turn_id uuid references assistant.turns(id),
 role text not null check(role in('user','assistant','context')),content text not null,run_id uuid not null references analytics.analysis_runs(id),
 result jsonb,created_at timestamptz not null default now(),unique(turn_id,role));
create index assistant_message_history on assistant.messages(conversation_id,seq desc);
create index assistant_message_run on assistant.messages(run_id);
create table assistant.tool_results(
 id uuid primary key default gen_random_uuid(),execution_id uuid not null references assistant.executions(id),query jsonb not null,result jsonb not null,
 created_at timestamptz not null default now(),unique(execution_id));
-- Complete occurrence relation, NOT the ten examples retained in aggregated audit reports.
-- Required-field specs reuse registered source contracts. Optional absence is not a filling error.
create view assistant.quality_occurrences with(security_invoker=true) as
select vs.workspace_id,vs.version_id,
 case when vs.source_type='usage' then s.account_id else r.content->>'account_id' end as account_id,
 vs.source_type,c.key as rule,'required'::text as kind
from analytics.version_sources vs join ingest.raw_rows r on r.file_id=vs.file_id
join ingest.source_files f on f.id=vs.file_id join ingest.source_contracts ct on ct.source_type=vs.source_type and ct.contract_version=f.contract_version
cross join lateral jsonb_each(ct.definition) c
left join core.subscriptions s on vs.source_type='usage' and s.version_id=vs.version_id and s.subscription_id=r.content->>'subscription_id'
where not coalesce((c.value->>'nullable')::boolean,false) and nullif(btrim(r.content->>c.key),'') is null
union all
select t.workspace_id,t.version_id,t.account_id,'support','missing_satisfaction','optional' from core.support_tickets t where t.closed_at is not null and t.satisfaction_score is null
union all
select s.workspace_id,s.version_id,s.account_id,'subscriptions','arr_mrr_mismatch','financial' from core.subscriptions s where s.arr_amount<>s.mrr_amount*12;
create function assistant.filters(p_filters jsonb) returns jsonb language plpgsql immutable security invoker set search_path='' as $$
declare x jsonb:=coalesce(p_filters,'{}');begin
 if jsonb_typeof(x)<>'object' or exists(select 1 from jsonb_object_keys(x) k where k not in('industry','country')) then raise exception 'Filtros inválidos.' using errcode='22023';end if;
 if exists(select 1 from jsonb_each(x) e where jsonb_typeof(e.value) not in('string','null') or(jsonb_typeof(e.value)='string' and(length(btrim(e.value#>>'{}')) not between 1 and 100))) then raise exception 'Filtro inválido.' using errcode='22023';end if;
 return jsonb_strip_nulls(jsonb_build_object('industry',nullif(btrim(x->>'industry'),''),'country',nullif(btrim(x->>'country'),'')));
end $$;
create function assistant.identity(p_token text) returns access.web_sessions language plpgsql stable security invoker set search_path='' as $$
declare s access.web_sessions;begin select * into strict s from access.web_sessions where id=access.authenticated_web_session(p_token);return s;end $$;
create function assistant.owned(p_token text,p_id uuid) returns assistant.conversations language plpgsql stable security invoker set search_path='' as $$
declare s access.web_sessions;c assistant.conversations;begin
 s=assistant.identity(p_token);select * into c from assistant.conversations where id=p_id and workspace_id=s.workspace_id and user_id=s.user_id;
 if not found then raise exception 'Conversa não encontrada para este usuário.' using errcode='PT404';end if;return c;
end $$;
create function public.challenge_assistant_create(p_token text,p_filters jsonb default '{}') returns jsonb language plpgsql security invoker set search_path='' as $$
declare s access.web_sessions;c assistant.conversations;rid uuid;begin
 s=assistant.identity(p_token);p_filters=assistant.filters(p_filters);select current_run_id into strict rid from access.workspaces where id=s.workspace_id;
 if rid is null then raise exception 'Nenhuma versão publicada.' using errcode='PT409';end if;
 if(select count(*) from assistant.conversations where user_id=s.user_id and created_at>now()-interval '1 day')>=30 then raise exception 'Limite de novas conversas atingido hoje.' using errcode='PT429';end if;
 insert into assistant.conversations(workspace_id,user_id,run_id,filters) values(s.workspace_id,s.user_id,rid,p_filters) returning * into c;return to_jsonb(c);
end $$;
create function public.challenge_assistant_list(p_token text,p_query text default '',p_archived boolean default false,p_offset integer default 0) returns jsonb language plpgsql stable security invoker set search_path='' as $$
declare s access.web_sessions;items jsonb;total integer;begin
 s=assistant.identity(p_token);if p_offset<0 or p_offset>100000 or length(p_query)>100 then raise exception 'Busca inválida.' using errcode='22023';end if;
 select count(*) into total from assistant.conversations where user_id=s.user_id and workspace_id=s.workspace_id and archived=p_archived and(position(lower(p_query) in lower(title))>0 or exists(select 1 from assistant.messages m where m.conversation_id=assistant.conversations.id and position(lower(p_query) in lower(m.content))>0));
 select coalesce(jsonb_agg(to_jsonb(x) order by x.updated_at desc,x.id),'[]') into items from(select * from assistant.conversations where user_id=s.user_id and workspace_id=s.workspace_id and archived=p_archived and(position(lower(p_query) in lower(title))>0 or exists(select 1 from assistant.messages m where m.conversation_id=assistant.conversations.id and position(lower(p_query) in lower(m.content))>0)) order by updated_at desc,id limit 30 offset p_offset)x;
 return jsonb_build_object('conversations',items,'has_more',total>p_offset+30,'total',total);
end $$;
create function public.challenge_assistant_conversation(p_token text,p_id uuid,p_before bigint default null) returns jsonb language plpgsql stable security invoker set search_path='' as $$
declare c assistant.conversations;items jsonb;first_seq bigint;current_id uuid;begin
 c=assistant.owned(p_token,p_id);select current_run_id into current_id from access.workspaces where id=c.workspace_id;
 select coalesce(jsonb_agg(to_jsonb(x) order by x.seq),'[]'),min(x.seq) into items,first_seq from(select * from assistant.messages where conversation_id=c.id and(p_before is null or seq<p_before) order by seq desc limit 60)x;
 return jsonb_build_object('conversation',to_jsonb(c),'messages',items,'has_more',exists(select 1 from assistant.messages where conversation_id=c.id and seq<first_seq),'current_run_id',current_id,'turns',(select coalesce(jsonb_agg(to_jsonb(z)),'[]') from(select id,request_key,question,status,lease_until from assistant.turns where conversation_id=c.id order by created_at desc limit 60)z),'run',(select jsonb_build_object('id',id,'reference_date',reference_date,'published_at',published_at) from analytics.analysis_runs where id=c.run_id));
end $$;
create function public.challenge_assistant_update(p_token text,p_id uuid,p_action text,p_title text default '',p_archived boolean default false,p_filters jsonb default '{}') returns jsonb language plpgsql security invoker set search_path='' as $$
declare c assistant.conversations;rid uuid;begin
 c=assistant.owned(p_token,p_id);perform 1 from assistant.conversations where id=c.id for update;
 if exists(select 1 from assistant.turns where conversation_id=c.id and status='pending' and lease_until>now()) then raise exception 'Aguarde a resposta antes de alterar a conversa.' using errcode='PT409';end if;
 if p_action='rename' then if length(btrim(p_title)) not between 1 and 80 then raise exception 'Título entre 1 e 80 caracteres.' using errcode='22023';end if;update assistant.conversations set title=btrim(p_title),updated_at=now() where id=c.id;
 elsif p_action='archive' then update assistant.conversations set archived=p_archived,updated_at=now() where id=c.id;
 elsif p_action='context' then p_filters=assistant.filters(p_filters);select current_run_id into strict rid from access.workspaces where id=c.workspace_id;update assistant.conversations set run_id=rid,filters=p_filters,updated_at=now() where id=c.id;
 insert into assistant.messages(conversation_id,role,content,run_id,result) values(c.id,'context','Contexto atualizado explicitamente pelo usuário.',rid,jsonb_build_object('filters',p_filters,'previous_run_id',c.run_id));
 else raise exception 'Operação desconhecida.' using errcode='22023';end if;
 return public.challenge_assistant_conversation(p_token,c.id,null);
end $$;
create function public.challenge_assistant_begin(p_token text,p_conversation uuid,p_request uuid,p_question text) returns jsonb language plpgsql security invoker set search_path='' as $$
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
 select coalesce(jsonb_agg(jsonb_build_object('role',x.role,'content',x.content) order by x.seq),'[]') into hist from(select role,content,seq from assistant.messages where conversation_id=c.id and role in('user','assistant') and turn_id<>t.id and run_id=t.run_id order by seq desc limit 8)x;
 return jsonb_build_object('state','ready','turn_id',t.id,'execution_id',e,'history',hist,'context',jsonb_build_object('run_id',t.run_id,'filters',t.filters,'reference_date',(select reference_date from analytics.analysis_runs where id=t.run_id)));
end $$;
create function assistant.active_turn(p_token text,p_turn uuid,p_execution uuid) returns assistant.turns language plpgsql stable security invoker set search_path='' as $$
declare t assistant.turns;c assistant.conversations;begin
 select * into t from assistant.turns where id=p_turn;if not found then raise exception 'Pergunta não encontrada.' using errcode='PT404';end if;c=assistant.owned(p_token,t.conversation_id);
 if t.current_execution is distinct from p_execution or t.status<>'pending' or t.lease_until<=now() then raise exception 'Tentativa encerrada; atualize a conversa.' using errcode='PT409';end if;return t;
end $$;
create function public.challenge_assistant_query(p_token text,p_turn uuid,p_execution uuid,p_query jsonb) returns jsonb language plpgsql security invoker set search_path='' set statement_timeout='12s' as $$
declare t assistant.turns;c assistant.conversations;r analytics.analysis_runs;f jsonb;m text;dim text;k text;v numeric;pop integer;items jsonb;result jsonb;label text;def text;unit text;warn jsonb:='[]';begin
 t=assistant.active_turn(p_token,p_turn,p_execution);c=assistant.owned(p_token,t.conversation_id);select * into strict r from analytics.analysis_runs where id=t.run_id and workspace_id=c.workspace_id and status='published';
 if jsonb_typeof(p_query)<>'object' or not p_query ?& array['metric','industry','country','dimension','quality_kind'] or exists(select 1 from jsonb_object_keys(p_query) x where x not in('metric','industry','country','dimension','quality_kind')) then raise exception 'Consulta fora do catálogo.' using errcode='22023';end if;
 f=assistant.filters(jsonb_build_object('industry',p_query->'industry','country',p_query->'country'));m=p_query->>'metric';dim=p_query->>'dimension';k=p_query->>'quality_kind';
 if m is null or m not in('accounts','segments','mrr','arr_annualized','arr_source','quality','reconciliation','usage','satisfaction') or(m='segments' and coalesce(dim,'') not in('industry','country','plan_tier')) or(m<>'segments' and dim is not null) or(m='quality' and coalesce(k,'') not in('required','optional','financial','reconciliation','all_supported')) or(m<>'quality' and k is not null) then raise exception 'Métrica incompatível.' using errcode='22023';end if;
 if(f?'industry' and not exists(select 1 from core.accounts where version_id=r.version_id and industry=f->>'industry')) or(f?'country' and not exists(select 1 from core.accounts where version_id=r.version_id and country=f->>'country')) then raise exception 'Filtro não existe nesta versão; consulte os segmentos disponíveis.' using errcode='22023';end if;
 select count(*) into pop from core.accounts a where a.version_id=r.version_id and(not f?'industry' or a.industry=f->>'industry') and(not f?'country' or a.country=f->>'country');
 unit='contas';
 if m='accounts' then v=pop;label='Contas cadastradas';def='Contas distintas na fonte de cadastro desta versão; inclui cadastros posteriores ao corte histórico.';
 elsif m='segments' then
  select coalesce(jsonb_agg(to_jsonb(x) order by x.label),'[]') into items from(select case dim when 'industry' then a.industry when 'country' then a.country else a.plan_tier end as label,count(*) as value from core.accounts a where a.version_id=r.version_id and(not f?'industry' or a.industry=f->>'industry') and(not f?'country' or a.country=f->>'country') group by 1 order by 1 limit 101)x;
  if jsonb_array_length(items)>100 then items=items-100;warn='["Exibidos os primeiros cem segmentos; a listagem foi limitada."]';end if;
  label=case dim when 'industry' then 'Setores' when 'country' then 'Países' else 'Planos' end;def='Valores distintos do cadastro da versão, com quantidade de contas por grupo.';
 elsif m in('mrr','arr_annualized','usage','satisfaction','reconciliation') then
  select case m when 'mrr' then coalesce(sum(s.contract_mrr),0) when 'arr_annualized' then coalesce(sum(s.contract_mrr),0)*12 when 'usage' then sum(s.recorded_usage_30d) when 'satisfaction' then sum(s.mean_satisfaction*s.satisfaction_responses)/nullif(sum(s.satisfaction_responses),0) else count(*) filter(where s.cadastral_churn and s.churn_events=0) end into v from analytics.account_snapshots s where s.run_id=r.id and(not f?'industry' or s.industry=f->>'industry') and(not f?'country' or s.country=f->>'country');
  label=case m when 'mrr' then 'MRR contratual' when 'arr_annualized' then 'ARR anualizado a partir do MRR' when 'usage' then 'Uso qualificado observado nos últimos trinta dias' when 'satisfaction' then 'Satisfação média dos respondentes elegíveis' else 'Contas com flag de churn sem cancelamento registrado' end;
  def=case m when 'mrr' then 'Soma dos snapshots de contratos abertos no corte histórico, sem trials; mesma regra do painel.' when 'arr_annualized' then 'MRR contratual no corte multiplicado por doze. Anualização, não receita recebida ou previsão.' when 'usage' then 'Soma de uso temporalmente qualificado na janela histórica; cobertura da telemetria não confirmada.' when 'satisfaction' then 'Média ponderada pela quantidade de notas, de tickets elegíveis encerrados até o corte; ausência de nota não significa insatisfação.' else 'Flag cadastral e zero eventos de cancelamento no corte; inclui ausência de qualquer evento e contas com apenas reativação.' end;
  unit=case when m in('mrr','arr_annualized') then 'unidade monetária da fonte' when m='satisfaction' then 'nota de um a cinco' when m='usage' then 'usos registrados' else 'contas' end;
  warn=case when m in('mrr','arr_annualized') then '["Moeda não informada na fonte; não representa caixa recebido."]' when m='usage' then '["Ausência de observação não comprova ausência de uso nem desengajamento."]' when m='satisfaction' then '["Resultados limitados aos respondentes; não extrapolar para todos os clientes."]' else '["A divergência deve ser investigada; não prova falha da fonte nem status atual."]' end;
 elsif m='arr_source' then
  select coalesce(sum(s.arr_amount),0) into v from core.subscriptions s join analytics.account_snapshots a on a.run_id=r.id and a.account_id=s.account_id where s.version_id=r.version_id and not s.is_trial and s.start_date<=r.reference_date and(s.end_date is null or s.end_date>r.reference_date) and(not f?'industry' or a.industry=f->>'industry') and(not f?'country' or a.country=f->>'country');
  label='ARR declarado na fonte';unit='unidade monetária da fonte';def='Soma do campo arr_amount nos mesmos contratos elegíveis do MRR no corte, sem trials. Pode divergir da anualização do MRR.';warn='["Moeda não informada; divergência ARR/MRR deve ser reconciliada."]';
 else
  with eligible as(select a.account_id from core.accounts a where a.version_id=r.version_id and(not f?'industry' or a.industry=f->>'industry') and(not f?'country' or a.country=f->>'country')),
  occurrences as(select q.account_id,q.kind from assistant.quality_occurrences q join eligible a using(account_id) where q.version_id=r.version_id and(k='all_supported' or q.kind=k)
   union all select s.account_id,'reconciliation' from analytics.account_snapshots s join eligible a using(account_id) where s.run_id=r.id and(k in('reconciliation','all_supported')) and(s.reconciliation_state in('flag_without_event','flag_with_reactivation_only','historical_event_without_flag') or(s.cadastral_churn and s.open_contracts>0)))
  select count(distinct account_id) into v from occurrences;
  label=case k when 'required' then 'Contas com campos obrigatórios ausentes' when 'optional' then 'Contas com notas de satisfação ausentes em tickets encerrados' when 'financial' then 'Contas com divergência entre ARR e MRR' when 'reconciliation' then 'Contas com divergências de reconciliação' else 'Contas com ocorrências nas regras de qualidade suportadas' end;
  def='Contagem distinta de contas afetadas. Campos obrigatórios usam o contrato registrado; nota opcional ausente, divergência financeira e reconciliação são categorias separadas. Verificações das fontes abrangem a versão; reconciliação usa o corte histórico.';
  warn='["Informação opcional ausente não é necessariamente erro de preenchimento.","Este catálogo não representa todas as verificações de qualidade; ausência de ocorrência não garante dados completos.","Uma conta com várias ocorrências é contada uma única vez."]';
 end if;
 result=jsonb_build_object('metric',m,'label',label,'value',case when v is null then null else to_jsonb(v::text) end,'unit',unit,'population',pop,'definition',def,'warnings',warn,'filters',f,'run_id',r.id,'version_id',r.version_id,'reference_date',r.reference_date,'published_at',r.published_at,'rule_version','1.0.0');
 if items is not null then result=result||jsonb_build_object('items',items);end if;
 insert into assistant.tool_results(execution_id,query,result) values(p_execution,p_query,result);return result;
end $$;
create function public.challenge_assistant_finish(p_token text,p_turn uuid,p_execution uuid,p_status text,p_result jsonb,p_usage jsonb) returns jsonb language plpgsql security invoker set search_path='' as $$
declare t assistant.turns;c assistant.conversations;begin
 t=assistant.active_turn(p_token,p_turn,p_execution);c=assistant.owned(p_token,t.conversation_id);
 if p_status not in('completed','failed') or length(p_result::text)>24000 or length(p_usage::text)>2000 or jsonb_typeof(p_result)<>'object' or length(p_result->>'answer') not between 1 and 15000 then raise exception 'Resposta inválida.' using errcode='22023';end if;
 update assistant.turns set status=p_status,result=p_result,lease_until=null where id=t.id and current_execution=p_execution and status='pending';
 update assistant.executions set status=p_status,usage=coalesce(p_usage,'{}'),finished_at=now() where id=p_execution;
 insert into assistant.messages(conversation_id,turn_id,role,content,run_id,result) values(c.id,t.id,'assistant',p_result->>'answer',t.run_id,p_result||jsonb_build_object('status',p_status)) on conflict(turn_id,role) do update set content=excluded.content,result=excluded.result;
 update assistant.conversations set updated_at=now() where id=c.id;return p_result;
end $$;
-- Closed schemas; all access goes through authenticated gateway with live session checks.
revoke all on schema assistant from public,anon,authenticated;grant usage on schema assistant to service_role;
revoke all on all tables in schema assistant from public,anon,authenticated;grant all on all tables in schema assistant to service_role;
grant usage,select on all sequences in schema assistant to service_role;
do $$declare x record;begin
 for x in select tablename from pg_tables where schemaname='assistant' loop
  execute format('alter table assistant.%I enable row level security',x.tablename);
  execute format('create policy backend_only on assistant.%I to service_role using(true) with check(true)',x.tablename);
 end loop;
 for x in select p.oid::regprocedure as sig from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='assistant' or(n.nspname='public' and p.proname like 'challenge_assistant_%') loop
  execute 'revoke execute on function '||x.sig||' from public,anon,authenticated';execute 'grant execute on function '||x.sig||' to service_role';
 end loop;
end $$;
