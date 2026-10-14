-- Explicit scope, applicable evidence and immutable population for executive decisions.
create table analytics.decision_rules (
 code text primary key,label text not null,scope_types text[] not null,definition text not null,rule_version text not null default '1.0.0'
);
insert into analytics.decision_rules(code,label,scope_types,definition) values
 ('missing_cancel','Churn cadastral sem cancelamento registrado','{account,segment,portfolio}','Flag cadastral e ausência de cancelamento registrado. Data, motivo e perda permanecem indeterminados.'),
 ('cadastral_churn','Flag cadastral de churn','{account,segment,portfolio}','Proporção de flags estáticas. Não é taxa temporal nem previsão de churn.'),
 ('contract_mrr','MRR contratual','{account,segment,portfolio}','Soma dos snapshots de contratos abertos no corte, sem trials. Unidade da fonte; não é caixa recebido ou perda prevista.'),
 ('observed_usage','Uso observado e cobertura','{account,segment,portfolio}','Quantidade qualificada registrada nos últimos 30 dias. Contas sem registro são destacadas para investigar cobertura; ausência não equivale a zero uso.'),
 ('satisfaction','Satisfação observada e respondentes','{account,segment,portfolio}','Média ponderada pelo número de respondentes, não média simples de médias de contas. Denominador de cobertura: tickets elegíveis fechados.'),
 ('quality_check','Ocorrência de qualidade dos dados','{quality}','Base inteira da verificação na versão das fontes. Não equivale a recorte de contas ou janela da referência.');
alter table analytics.decision_rules enable row level security;
create policy backend_only on analytics.decision_rules to service_role using(true) with check(true);
grant select on analytics.decision_rules to service_role;

create function analytics.normalize_decision_scope(p_scope jsonb) returns jsonb language plpgsql immutable security invoker set search_path='' as $$
declare kind text;allowed text[];key text;val text;result jsonb;begin
 if p_scope is null or jsonb_typeof(p_scope)<>'object' then raise exception 'Selecione um escopo válido';end if;
 kind=p_scope->>'type';
 allowed=case kind when 'account' then array['type','account_id'] when 'segment' then array['type','industry','country'] when 'portfolio' then array['type'] when 'quality' then array['type','source','check_code'] else null end;
 if allowed is null then raise exception 'Selecione um escopo válido';end if;
 result=jsonb_build_object('type',kind);
 for key in select jsonb_object_keys(p_scope) loop
  if not key=any(allowed) or jsonb_typeof(p_scope->key)<>'string' or length(p_scope->>key)>200 then raise exception 'Filtro incompatível com o escopo';end if;
  if key='type' then continue;end if;
  val=nullif(trim(p_scope->>key),'');if val is not null then result=result||jsonb_build_object(key,val);end if;
 end loop;
 if kind='account' and not result?'account_id' then raise exception 'Selecione uma conta';end if;
 if kind='segment' and not(result?'industry' or result?'country') then raise exception 'Selecione setor ou país';end if;
 if kind='quality' and (coalesce(result->>'source','') not in('accounts','subscriptions','usage','support','churn') or not result?'check_code') then raise exception 'Selecione fonte e verificação';end if;
 return result;
end $$;

create function analytics.quality_source_dependencies(p_code text) returns text[] language sql immutable security invoker set search_path='' as $$
 select case
 when p_code='usage.before_signup' then array['usage','subscriptions','accounts']
 when p_code in('usage.orphan','usage.before_subscription','usage.after_subscription_end') then array['usage','subscriptions']
 when p_code='usage.after_first_churn' then array['usage','subscriptions','churn']
 when p_code='support.after_first_churn' then array['support','churn']
 when p_code in('subscriptions.orphan','subscriptions.before_signup') then array['subscriptions','accounts']
 when p_code in('support.orphan','support.before_signup') then array['support','accounts']
 when p_code in('churn.orphan','churn.before_signup') or p_code like 'churn.flag_%' then
 case when p_code='churn.flag_true_with_open_contract_at_source_end' then array['accounts','subscriptions'] else array['churn','accounts'] end
 when p_code in('churn.event_with_other_open_contract','churn.event_without_same_day_subscription_end') then array['churn','subscriptions']
 else array[split_part(p_code,'.',1)] end
$$;
create function analytics.decision_scope_members(p_run uuid,p_scope jsonb) returns setof analytics.account_snapshots language sql stable security invoker set search_path='' as $$
 select s.* from analytics.account_snapshots s where s.run_id=p_run and
 case p_scope->>'type' when 'portfolio' then true
 when 'account' then s.account_id=p_scope->>'account_id'
 when 'segment' then (not p_scope?'industry' or s.industry=p_scope->>'industry') and (not p_scope?'country' or s.country=p_scope->>'country') else false end
$$;
create function analytics.decision_scope_preview(p_run uuid,p_scope jsonb,p_metric text) returns jsonb language plpgsql stable security invoker set search_path='' as $$
declare r analytics.analysis_runs;scope jsonb;rule analytics.decision_rules;q analytics.quality_checks;payload jsonb;measure jsonb;members jsonb;
 population integer;affected integer;responses integer;closed integer;observed integer;opened integer;value numeric;label text;warnings jsonb;
begin
 scope=analytics.normalize_decision_scope(p_scope);
 select * into strict r from analytics.analysis_runs where id=p_run and status='published';
 select * into rule from analytics.decision_rules where code=p_metric and scope->>'type'=any(scope_types);
 if not found then raise exception 'Dado incompatível com o escopo';end if;
 warnings='["Atributos de setor e país não têm histórico de alterações; não representam mudança datada.","Resultados de ações não demonstram causalidade por si só."]'::jsonb;
 if scope->>'type'='quality' then
  select * into q from analytics.quality_checks where version_id=r.version_id and code=scope->>'check_code' and affected_count>0;
  if not found or not(scope->>'source'=any(analytics.quality_source_dependencies(scope->>'check_code'))) then raise exception 'Verificação sem ocorrências ou incompatível com a fonte';end if;
  population=q.denominator;affected=q.affected_count;members='[]';label='Qualidade: '||(scope->>'source')||' / '||q.code;
  measure=jsonb_build_object('label',q.interpretation,'value',q.affected_count,'unit','ocorrências','numerator',q.affected_count,'denominator',q.denominator,'denominator_label','Base da verificação','state','indeterminate','policy',q.policy,'quality_check',to_jsonb(q),'source_dependencies',analytics.quality_source_dependencies(q.code));
  warnings=warnings||'["A contagem considera toda a base da verificação na versão. Não é uma janela de 30 dias nem contagem de contas necessariamente. Contagens de verificações podem se sobrepor."]'::jsonb;
 else
  select count(*)::integer,coalesce(sum(satisfaction_responses),0)::integer,coalesce(sum(closed_tickets_30d),0)::integer,count(*) filter(where coherent_usage_rows_30d>0)::integer,count(*) filter(where open_contracts>0)::integer,
   case p_metric when 'missing_cancel' then count(*) filter(where reconciliation_state in('flag_without_event','flag_with_reactivation_only'))
    when 'cadastral_churn' then count(*) filter(where cadastral_churn)
    when 'contract_mrr' then sum(contract_mrr)
    when 'observed_usage' then sum(recorded_usage_30d)
    when 'satisfaction' then sum(mean_satisfaction*satisfaction_responses)/nullif(sum(satisfaction_responses),0) end
  into population,responses,closed,observed,opened,value from analytics.decision_scope_members(p_run,scope);
  if population=0 then raise exception 'Nenhuma conta elegível neste recorte';end if;
  select jsonb_agg(jsonb_build_object('snapshot_id',id,'account_id',account_id,'account_name',account_name,'highlighted',case p_metric
    when 'missing_cancel' then reconciliation_state in('flag_without_event','flag_with_reactivation_only')
    when 'cadastral_churn' then cadastral_churn when 'contract_mrr' then open_contracts>0
    when 'observed_usage' then coherent_usage_rows_30d=0 when 'satisfaction' then closed_tickets_30d>satisfaction_responses end) order by account_id)
  into members from analytics.decision_scope_members(p_run,scope);
  select count(*)::integer into affected from jsonb_array_elements(members) x where (x->>'highlighted')::boolean;
  label=case scope->>'type' when 'account' then 'Conta: '||(members->0->>'account_name')||' ('||(scope->>'account_id')||')'
   when 'portfolio' then 'Carteira inteira' else 'Segmento: '||coalesce(scope->>'industry','Todos os setores')||' / '||coalesce(scope->>'country','Todos os países') end;
  measure=jsonb_build_object('label',rule.label,'value',value,'unit',case p_metric when 'contract_mrr' then 'unidade da fonte' when 'observed_usage' then 'quantidade registrada' when 'satisfaction' then 'nota de 1 a 5' else 'contas' end,
   'numerator',case p_metric when 'satisfaction' then responses when 'observed_usage' then observed when 'contract_mrr' then opened else affected end,
   'denominator',case when p_metric='satisfaction' then closed else population end,
   'denominator_label',case when p_metric='satisfaction' then 'Respondentes / tickets elegíveis fechados' when p_metric='observed_usage' then 'Contas com registros qualificados / contas do recorte' when p_metric='contract_mrr' then 'Contas com contratos abertos / contas do recorte' else 'Contas destacadas / contas do recorte' end,
   'state',case when p_metric in('missing_cancel','observed_usage') or value is null then 'indeterminate' else 'observed_with_limits' end,
   'highlight_definition',case p_metric when 'observed_usage' then 'Contas sem uso qualificado observado; não demonstra desengajamento' when 'satisfaction' then 'Contas com tickets fechados sem nota; não demonstra insatisfação' when 'contract_mrr' then 'Contas com contrato aberto; não demonstra risco ou perda' when 'missing_cancel' then 'Flag de churn sem cancelamento histórico registrado' else 'Contas com flag cadastral estática' end,
   'coverage_state',case when p_metric='observed_usage' then 'not_confirmed' else 'observed_sample' end);
  warnings=warnings||jsonb_build_array(rule.definition);
 end if;
 payload=jsonb_build_object('run',jsonb_build_object('id',r.id,'version_id',r.version_id,'reference_date',r.reference_date,'algorithm_version',r.algorithm_version),
  'scope',scope,'scope_label',label,'metric',p_metric,'rule_version',rule.rule_version,'definition',rule.definition,
  'population_count',population,'population_unit',case when scope->>'type'='quality' then 'base da verificação' else 'contas' end,
  'affected_count',affected,'measure',measure,'members',members,'warnings',warnings);
 return payload||jsonb_build_object('preview_hash',encode(sha256(convert_to(payload::text,'UTF8')),'hex'));
end $$;

alter table operations.decisions add column scope_type text check(scope_type in('account','segment','portfolio','quality')),
 add column scope_preview_hash text check(scope_preview_hash~'^[0-9a-f]{64}$'),
 add constraint decision_scope_identity unique(workspace_id,id,scope_preview_hash);
alter table operations.decisions drop constraint decision_evidence_required;
alter table operations.decisions add constraint decision_evidence_required check(evidence_id is not null or snapshot_id is not null or(scope_type is not null and scope_preview_hash is not null));
create table operations.decision_scopes (
 workspace_id uuid not null,decision_id uuid primary key,run_id uuid not null,scope_type text not null,filters jsonb not null,metric text not null,
 population_count integer not null check(population_count>0),affected_count integer not null check(affected_count>=0),preview_hash text not null,preview jsonb not null,
 unique(workspace_id,decision_id,run_id),
 foreign key(workspace_id,decision_id,preview_hash) references operations.decisions(workspace_id,id,scope_preview_hash),
 foreign key(workspace_id,run_id) references analytics.analysis_runs(workspace_id,id)
);
create table operations.decision_scope_snapshots (
 workspace_id uuid not null,decision_id uuid not null,run_id uuid not null,snapshot_id uuid not null,highlighted boolean not null,
 primary key(decision_id,snapshot_id),
 foreign key(workspace_id,decision_id,run_id) references operations.decision_scopes(workspace_id,decision_id,run_id),
 foreign key(workspace_id,snapshot_id,run_id) references analytics.account_snapshots(workspace_id,id,run_id)
);
create index decision_scopes_decision_fk_idx on operations.decision_scopes(workspace_id,decision_id,preview_hash);
create index decision_scopes_run_idx on operations.decision_scopes(workspace_id,run_id);
create index scope_snapshots_snapshot_idx on operations.decision_scope_snapshots(workspace_id,snapshot_id,run_id);
create index scope_snapshots_decision_idx on operations.decision_scope_snapshots(workspace_id,decision_id,run_id);
alter table operations.decision_scopes enable row level security;
alter table operations.decision_scope_snapshots enable row level security;
create policy backend_only on operations.decision_scopes to service_role using(true) with check(true);
create policy backend_only on operations.decision_scope_snapshots to service_role using(true) with check(true);
grant all on operations.decision_scopes,operations.decision_scope_snapshots to service_role;
create trigger decision_scopes_immutable before update or delete on operations.decision_scopes for each row execute function operations.guard_append_only();
create trigger decision_scope_members_immutable before update or delete on operations.decision_scope_snapshots for each row execute function operations.guard_append_only();

create function public.challenge_web_scope_options(p_token text,p_run uuid) returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid;ws access.workspaces;r analytics.analysis_runs;begin
 sess=access.web_session(p_token);select * into strict ws from access.workspaces where slug='ravenstack';
 if p_run is distinct from ws.current_run_id then raise exception 'A base foi atualizada. Atualize o contexto e revise a seleção.' using errcode='PT409';end if;
 select * into strict r from analytics.analysis_runs where id=p_run and status='published';
 return jsonb_build_object('run_id',p_run,'metrics',(select jsonb_agg(to_jsonb(x) order by code) from analytics.decision_rules x),
 'quality',(select coalesce(jsonb_agg(to_jsonb(q)||jsonb_build_object('sources',analytics.quality_source_dependencies(q.code)) order by q.code),'[]') from analytics.quality_checks q where version_id=r.version_id and affected_count>0));
end $$;
create function public.challenge_web_scope_preview(p_token text,p_run uuid,p_scope jsonb,p_metric text) returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid;ws access.workspaces;begin
 sess=access.web_session(p_token);select * into strict ws from access.workspaces where slug='ravenstack';
 if p_run is distinct from ws.current_run_id then raise exception 'A base foi atualizada. Atualize o contexto e revise a seleção.' using errcode='PT409';end if;
 return analytics.decision_scope_preview(p_run,p_scope,p_metric);
end $$;
create function public.challenge_web_decide_scoped(p_token text,p_request text,p_run uuid,p_scope jsonb,p_metric text,p_preview_hash text,p_title text,p_rationale text,p_actor text,p_action text,p_responsible text,p_due date)
 returns jsonb language plpgsql security invoker set search_path='' as $$
declare sess uuid;ws access.workspaces;existing operations.decisions;preview jsonb;scope jsonb;d uuid;a uuid;snapshot uuid;begin
 sess=access.web_session(p_token);select * into strict ws from access.workspaces where slug='ravenstack';scope=analytics.normalize_decision_scope(p_scope);
 if p_request is null or length(p_request) not between 8 and 100 or p_preview_hash is null then raise exception 'Prévia e chave de solicitação obrigatórias';end if;
 perform pg_advisory_xact_lock(hashtext(sess::text||p_request));
 select * into existing from operations.decisions where actor_session_id=sess and request_key=p_request;
 if found then
  if existing.scope_preview_hash is distinct from p_preview_hash or existing.scope_type is distinct from scope->>'type'
   or existing.evidence_context->'scope' is distinct from scope or existing.evidence_context->>'metric' is distinct from p_metric
   or existing.evidence_context->'run'->>'id' is distinct from p_run::text
   or existing.title is distinct from trim(p_title) or existing.rationale is distinct from trim(p_rationale)
   or existing.actor_display_name is distinct from trim(p_actor)
   or not exists(select 1 from operations.actions where decision_id=existing.id and title=trim(p_action) and responsible=trim(p_responsible) and due_date=p_due) then
   raise exception 'Chave já utilizada com outra decisão ou outro recorte' using errcode='PT409';end if;
  return jsonb_build_object('decision_id',existing.id,'action_id',(select id from operations.actions where decision_id=existing.id limit 1));
 end if;
 -- Lock only publication pointer briefly; the preview itself reads immutable snapshots.
 perform 1 from access.workspaces where id=ws.id for update;
 if p_run is distinct from(select current_run_id from access.workspaces where id=ws.id) then raise exception 'A base foi atualizada. Atualize o contexto e revise a seleção.' using errcode='PT409';end if;
 preview=analytics.decision_scope_preview(p_run,scope,p_metric);
 if preview->>'preview_hash' is distinct from p_preview_hash then raise exception 'Prévia alterada ou inválida. Revise a evidência antes de registrar.' using errcode='PT409';end if;
 if coalesce(length(trim(p_title)),0) not between 3 and 180 or coalesce(length(trim(p_rationale)),0) not between 10 and 3000
 or coalesce(length(trim(p_actor)),0) not between 2 and 100 or coalesce(length(trim(p_action)),0) not between 3 and 180
 or coalesce(length(trim(p_responsible)),0) not between 2 and 100 or p_due is null then raise exception 'Preencha decisão, justificativa, autor declarado, ação, responsável e prazo';end if;
 if (select count(*) from operations.decisions where actor_session_id=sess and created_at>now()-interval '1 day')>=30 then raise exception 'Limite diário de decisões atingido';end if;
 if scope->>'type'='account' then snapshot=(preview->'members'->0->>'snapshot_id')::uuid;end if;
 insert into operations.decisions(workspace_id,snapshot_id,scope_type,scope_preview_hash,title,rationale,actor_session_id,actor_display_name,request_key,evidence_context)
 values(ws.id,snapshot,scope->>'type',p_preview_hash,trim(p_title),trim(p_rationale),sess,trim(p_actor),p_request,preview) returning id into d;
 insert into operations.decision_scopes(workspace_id,decision_id,run_id,scope_type,filters,metric,population_count,affected_count,preview_hash,preview)
 values(ws.id,d,p_run,scope->>'type',scope,p_metric,(preview->>'population_count')::integer,(preview->>'affected_count')::integer,p_preview_hash,preview);
 insert into operations.decision_scope_snapshots(workspace_id,decision_id,run_id,snapshot_id,highlighted)
 select ws.id,d,p_run,(x->>'snapshot_id')::uuid,(x->>'highlighted')::boolean from jsonb_array_elements(preview->'members') x;
 insert into operations.actions(workspace_id,decision_id,title,responsible,due_date) values(ws.id,d,trim(p_action),trim(p_responsible),p_due) returning id into a;
 insert into operations.action_history(workspace_id,action_id,actor_session_id,to_status,revision) values(ws.id,a,sess,'pending',0);
 return jsonb_build_object('decision_id',d,'action_id',a);
end $$;
-- Existing decisions and legacy RPC remain unchanged and readable.
do $$declare f record;begin
 for f in select p.oid::regprocedure as signature from pg_proc p join pg_namespace n on n.oid=p.pronamespace where
 (n.nspname='analytics' and p.proname in('normalize_decision_scope','quality_source_dependencies','decision_scope_members','decision_scope_preview'))
 or(n.nspname='public' and p.proname in('challenge_web_scope_options','challenge_web_scope_preview','challenge_web_decide_scoped')) loop
 execute 'revoke execute on function '||f.signature||' from public,anon,authenticated';execute 'grant execute on function '||f.signature||' to service_role';end loop;
end $$;
