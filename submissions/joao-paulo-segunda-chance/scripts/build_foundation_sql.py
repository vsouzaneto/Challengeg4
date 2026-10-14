"""Gera DDL a partir dos contratos versionados; não lê fontes do usuário."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from domain.source_contracts import CONTRACTS, CONTRACT_VERSION

ROOT = Path(__file__).resolve().parents[1]
TABLES = {'accounts':'accounts','subscriptions':'subscriptions','usage':'feature_usage','support':'support_tickets','churn':'churn_events'}
KEYS = {'accounts':'account_id','subscriptions':'subscription_id','usage':'usage_id','support':'ticket_id','churn':'churn_event_id'}
SQL_TYPES = {'text':'text','integer':'integer','numeric':'numeric','boolean':'boolean','date':'date','timestamp':'timestamp without time zone'}


def build():
    out = [(ROOT/'db/foundation_base.sql').read_text()]
    for kind, contract in CONTRACTS.items():
        table = TABLES[kind]
        columns = [f'  {name} {SQL_TYPES[field.kind]}' + ('' if field.nullable else ' not null') for name, field in contract.items()]
        primary = 'source_row_id' if kind == 'usage' else KEYS[kind]
        clauses = [f'primary key(version_id,{primary})', 'foreign key(workspace_id,version_id) references analytics.dataset_versions(workspace_id,id)',
                   'foreign key(workspace_id,source_row_id) references ingest.raw_rows(workspace_id,id)']
        if kind == 'accounts': clauses.append('unique(workspace_id,version_id,account_id)')
        elif kind == 'usage': clauses.append('foreign key(workspace_id,version_id,subscription_id) references core.subscriptions(workspace_id,version_id,subscription_id)')
        else: clauses.append('foreign key(workspace_id,version_id,account_id) references core.accounts(workspace_id,version_id,account_id)')
        if kind == 'subscriptions': clauses.append('unique(workspace_id,version_id,subscription_id)')
        out.append(f'create table core.{table} (\n  workspace_id uuid not null,\n  version_id uuid not null,\n  source_row_id bigint not null,\n' + ',\n'.join(columns + ['  '+x for x in clauses]) + '\n);')
        relationship = 'subscription_id' if kind == 'usage' else 'account_id'
        out.append(f'create index {table}_relation_idx on core.{table}(workspace_id,version_id,{relationship});')
        if kind == 'usage':
            out.append('create index usage_identity_idx on core.feature_usage(version_id,usage_id);')
            out.append('create index usage_date_idx on core.feature_usage(version_id,subscription_id,usage_date);')
        if kind == 'churn': out.append('create index churn_date_idx on core.churn_events(version_id,account_id,churn_date);')
        if kind == 'support': out.append('create index support_date_idx on core.support_tickets(version_id,account_id,submitted_at);')
        out.append(f'create trigger {table}_version_guard before insert or update or delete on core.{table} for each row execute function analytics.guard_version_write();')
        definition = json.dumps({name:{'type':f.kind,'nullable':f.nullable} for name,f in contract.items()})
        out.append(f"insert into ingest.source_contracts values ('{kind}','{CONTRACT_VERSION}','{definition}'::jsonb);")

    # A single atomic promotion; raw rows remain untouched if a cast/FK fails.
    body = ['declare ws uuid; sources integer; state text; begin',
            'select workspace_id,status into strict ws,state from analytics.dataset_versions where id=p_version for update;',
            "if state<>'candidate' then raise exception 'Apenas versão candidata pode ser promovida'; end if;",
            'select count(*) into sources from analytics.version_sources vs join ingest.source_files f on f.id=vs.file_id where vs.version_id=p_version and f.status=\'verified\';',
            "if sources<>5 then raise exception 'São necessárias cinco fontes verificadas'; end if;"]
    for kind, contract in CONTRACTS.items():
        cols = ','.join(contract)
        expressions = ','.join(f"nullif(r.content->>'{name}','')::{SQL_TYPES[f.kind]}" for name,f in contract.items())
        body.append(f"insert into core.{TABLES[kind]}(workspace_id,version_id,source_row_id,{cols}) select ws,p_version,r.id,{expressions} from ingest.raw_rows r join analytics.version_sources vs on vs.file_id=r.file_id and vs.version_id=p_version where vs.source_type='{kind}' on conflict do nothing;")
        body.append(f"if (select count(*) from core.{TABLES[kind]} where version_id=p_version)<>(select f.expected_rows from analytics.version_sources vs join ingest.source_files f on f.id=vs.file_id where vs.version_id=p_version and vs.source_type='{kind}') then raise exception 'Contagem canônica divergente: {kind}'; end if;")
    body.append('end')
    out.append("create function analytics.promote_version(p_version uuid) returns void language plpgsql security invoker set search_path='' as $$\n"+'\n'.join(body)+'\n$$;')
    out.append((ROOT/'db/analytics_functions.sql').read_text())
    out.append((ROOT/'db/access_policies.sql').read_text())
    return '\n\n'.join(out)+'\n'


if __name__ == '__main__':
    (ROOT/'db/foundation.sql').write_text(build())
