"""Auditoria somente leitura. Preserva fontes e quantifica evidências, não causas.

Uso: python scripts/audit_data.py --data-dir /pasta/csv --output-dir reports
Requer pandas (dependência do adaptador de análise, não do domínio).
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

FILES = {
    'accounts': ('ravenstack_accounts.csv', 'account_id'),
    'subscriptions': ('ravenstack_subscriptions.csv', 'subscription_id'),
    'usage': ('ravenstack_feature_usage.csv', 'usage_id'),
    'support': ('ravenstack_support_tickets.csv', 'ticket_id'),
    'churn': ('ravenstack_churn_events.csv', 'churn_event_id'),
}
DATES = {'accounts': ['signup_date'], 'subscriptions': ['start_date', 'end_date'],
         'usage': ['usage_date'], 'support': ['submitted_at', 'closed_at'], 'churn': ['churn_date']}
NUMBERS = {'accounts': ['seats'], 'subscriptions': ['seats', 'mrr_amount', 'arr_amount'],
           'usage': ['usage_count', 'usage_duration_secs', 'error_count'],
           'support': ['resolution_time_hours', 'first_response_time_minutes', 'satisfaction_score'],
           'churn': ['refund_amount_usd']}
BOOLEANS = {'accounts': ['is_trial', 'churn_flag'],
            'subscriptions': ['is_trial', 'upgrade_flag', 'downgrade_flag', 'churn_flag', 'auto_renew_flag'],
            'usage': ['is_beta_feature'], 'support': ['escalation_flag'],
            'churn': ['preceding_upgrade_flag', 'preceding_downgrade_flag', 'is_reactivation']}


def load_sources(folder: Path):
    frames, manifest = {}, {}
    for name, (filename, key) in FILES.items():
        path = folder / filename
        raw = pd.read_csv(path, dtype=str, keep_default_na=False)
        manifest[name] = {'filename': filename, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                          'rows': len(raw), 'columns': list(raw.columns),
                          'nulls': {col: int(raw[col].eq('').sum()) for col in raw},
                          'unique_ids': int(raw[key].nunique())}
        frames[name] = raw
    return frames, manifest


def audit(folder: Path) -> dict:
    raw, manifest = load_sources(folder)
    findings = []

    def add(code, frame, mask, key, interpretation, policy, kind='quality', denominator=None):
        selected = frame.loc[mask.fillna(False)]
        den = len(frame) if denominator is None else denominator
        findings.append({'code': code, 'kind': kind, 'count': len(selected), 'denominator': den,
                         'share': len(selected) / den if den else None,
                         'examples': selected[key].astype(str).head(10).tolist(),
                         'interpretation': interpretation, 'policy': policy})

    frames = {}
    for name, frame in raw.items():
        key = FILES[name][1]
        add(f'{name}.blank_key', frame, frame[key].str.strip().eq(''), key,
            'Chave ausente.', 'Bloquear promoção da linha.')
        add(f'{name}.repeated_key_rows', frame, frame[key].duplicated(False), key,
            'Linhas participantes de IDs repetidos; não é a contagem de excedentes.',
            'Preservar todas as linhas; não sobrescrever ou escolher arbitrariamente.')
        add(f'{name}.exact_duplicate_excess', frame, frame.duplicated(), key,
            'Repetição exata além da primeira linha.', 'Deduplicar somente na camada qualificada, com trilha.')
        parsed = frame.copy()
        for col in DATES[name]:
            value = pd.to_datetime(frame[col].replace('', None), errors='coerce', format='mixed')
            add(f'{name}.invalid_{col}', frame, frame[col].ne('') & value.isna(), key,
                'Data preenchida mas não interpretável.', 'Bloquear promoção do campo obrigatório.')
            parsed[col] = value
            manifest[name].setdefault('date_ranges', {})[col] = {'min': str(value.min()), 'max': str(value.max())}
        for col in NUMBERS[name]:
            value = pd.to_numeric(frame[col].replace('', None), errors='coerce')
            add(f'{name}.invalid_{col}', frame, frame[col].ne('') & value.isna(), key,
                'Número preenchido mas não interpretável.', 'Bloquear promoção do campo obrigatório.')
            add(f'{name}.negative_{col}', frame, value.lt(0), key,
                'Valor negativo em medida esperada não negativa.', 'Revisar contrato e manter a origem.')
            parsed[col] = value
        for col in BOOLEANS[name]:
            normalized = frame[col].str.strip().str.lower()
            add(f'{name}.invalid_{col}', frame, ~normalized.isin(['true', 'false']), key,
                'Booleano ausente ou fora de true/false.', 'Não converter desconhecido para falso.')
            parsed[col] = normalized.map({'true': True, 'false': False})
        frames[name] = parsed

    a, s, u, t, c = [frames[k] for k in ['accounts', 'subscriptions', 'usage', 'support', 'churn']]
    for name, frame, field, parent, parent_field in [
        ('subscriptions', s, 'account_id', a, 'account_id'), ('usage', u, 'subscription_id', s, 'subscription_id'),
        ('support', t, 'account_id', a, 'account_id'), ('churn', c, 'account_id', a, 'account_id')]:
        add(f'{name}.orphan', frame, ~frame[field].isin(parent[parent_field]), FILES[name][1],
            'Relacionamento sem pai na versão recebida.', 'Bloquear a promoção da linha até reconciliação.')

    # Joins validados: fonte de cadastro/assinatura deve ser única para continuar.
    # Não usar deduplicação arbitrária para produzir resultados aparentemente bons.
    for name, frame, key in [('accounts', a, 'account_id'), ('subscriptions', s, 'subscription_id')]:
        if frame[key].duplicated().any():
            raise ValueError(f'{name}: chave pai duplicada; análise relacional interrompida sem corrigir fonte.')

    for name, frame, date_col in [('subscriptions', s, 'start_date'), ('support', t, 'submitted_at'), ('churn', c, 'churn_date')]:
        joined = frame.merge(a[['account_id', 'signup_date']], on='account_id', how='left', validate='many_to_one')
        add(f'{name}.before_signup', joined, joined[date_col].lt(joined.signup_date), FILES[name][1],
            'Fato anterior ao cadastro da conta vinculada.', 'Sinalizar coerência temporal; não inventar nova data.')

    usage = u.merge(s[['subscription_id', 'account_id', 'start_date', 'end_date']], on='subscription_id', how='left', validate='many_to_one')
    usage = usage.merge(a[['account_id', 'signup_date']], on='account_id', how='left', validate='many_to_one')
    add('usage.before_signup', usage, usage.usage_date.lt(usage.signup_date), 'usage_id',
        'Uso anterior ao cadastro da conta vinculada.', 'Não usar como trajetória válida de adoção sem ressalva.')
    add('usage.before_subscription', usage, usage.usage_date.lt(usage.start_date), 'usage_id',
        'Uso anterior ao início da assinatura vinculada.', 'Separar exploração da fonte e análise contratualmente coerente; mostrar impacto da seleção.')
    add('usage.after_subscription_end', usage, usage.usage_date.gt(usage.end_date), 'usage_id',
        'Uso posterior ao término registrado.', 'Revisar vínculo e semântica do término; não afirmar uso pago.')
    add('usage.errors_above_count', u, u.error_count.gt(u.usage_count), 'usage_id',
        'Erros acima da quantidade de uso; a semântica das medidas precisa ser confirmada.', 'Não impor teto nem chamar a razão de probabilidade.')
    add('usage.zero_count_with_activity', u, u.usage_count.eq(0) & (u.error_count.gt(0) | u.usage_duration_secs.gt(0)), 'usage_id',
        'Quantidade zero com duração ou erros positivos.', 'Investigar semântica e denominadores.')

    add('subscriptions.end_before_start', s, s.end_date.lt(s.start_date), 'subscription_id',
        'Intervalo contratual invertido.', 'Bloquear cálculo de atividade contratual para a linha.')
    add('subscriptions.arr_mrr_mismatch', s, s.arr_amount.ne(s.mrr_amount * 12), 'subscription_id',
        'ARR diferente de 12 vezes MRR.', 'Investigar definição financeira; não recalcular a fonte silenciosamente.')
    add('subscriptions.churn_without_end', s, s.churn_flag.eq(True) & s.end_date.isna(), 'subscription_id',
        'Assinatura cancelada sem data de término.', 'Status e data desconhecida tratados separadamente.')
    add('subscriptions.end_without_churn', s, s.churn_flag.eq(False) & s.end_date.notna(), 'subscription_id',
        'Término preenchido sem flag de churn.', 'Não assumir cancelamento sem confirmar semântica.')
    add('subscriptions.upgrade_and_downgrade', s, s.upgrade_flag.eq(True) & s.downgrade_flag.eq(True), 'subscription_id',
        'Ambas as flags presentes; podem representar histórico, não uma transição única.', 'Não atribuir data de início da assinatura à mudança comercial.')
    add('support.closed_before_submitted', t, t.closed_at.lt(t.submitted_at), 'ticket_id',
        'Encerramento anterior à abertura.', 'Bloquear cálculo de duração.')
    elapsed = (t.closed_at - t.submitted_at).dt.total_seconds() / 3600
    add('support.duration_mismatch', t, (elapsed - t.resolution_time_hours).abs().gt(1e-6), 'ticket_id',
        'Duração registrada difere de encerramento menos abertura.', 'Expor divergência e regra de cálculo.')
    add('support.response_after_closure', t, t.first_response_time_minutes.gt(elapsed * 60), 'ticket_id',
        'Tempo até primeira resposta maior que duração total.', 'Investigar antes de usar SLA.')
    add('support.missing_satisfaction', t, t.satisfaction_score.isna(), 'ticket_id',
        'Ausência de nota não significa insatisfação.', 'Exibir respondentes e cobertura; não preencher com zero.', kind='coverage')
    add('support.invalid_satisfaction_range', t, t.satisfaction_score.notna() & ~t.satisfaction_score.between(1, 5), 'ticket_id',
        'Nota fora da escala proposta 1–5; confirmar contrato.', 'Bloquear CSAT até confirmar escala.')

    actual = c.loc[c.is_reactivation.eq(False)]
    any_ids, churn_ids = set(c.account_id), set(actual.account_id)
    react_ids = set(c.loc[c.is_reactivation.eq(True), 'account_id'])
    add('churn.flag_true_without_any_event', a, a.churn_flag.eq(True) & ~a.account_id.isin(any_ids), 'account_id',
        'Churn cadastral sem nenhum evento histórico.', 'Manter no indicador cadastral; data, motivo e perda indeterminados.', kind='reconciliation')
    add('churn.flag_true_only_reactivation', a, a.churn_flag.eq(True) & a.account_id.isin(any_ids) & ~a.account_id.isin(churn_ids), 'account_id',
        'Churn cadastral com apenas reativação registrada.', 'Reativação não substitui o cancelamento ausente.', kind='reconciliation')
    add('churn.flag_false_with_churn', a, a.churn_flag.eq(False) & a.account_id.isin(churn_ids), 'account_id',
        'Evento histórico e cadastro divergem; pode haver reativação ou outra definição.', 'Não concluir status atual só pelo histórico.', kind='reconciliation')
    add('churn.repeated_account_day_rows', actual, actual.duplicated(['account_id', 'churn_date'], False), 'churn_event_id',
        'Mais de um evento da mesma conta no mesmo dia.', 'Não equiparar eventos a contas únicas.', kind='reconciliation')
    add('churn.upgrade_and_downgrade', c, c.preceding_upgrade_flag.eq(True) & c.preceding_downgrade_flag.eq(True), 'churn_event_id',
        'Flags de upgrade e downgrade ambas verdadeiras.', 'Podem ser movimentos prévios distintos; faltam datas individuais.', kind='limitation')
    for name, frame, date_col in [('usage', usage, 'usage_date'), ('support', t, 'submitted_at')]:
        first = actual.groupby('account_id', as_index=False).churn_date.min().rename(columns={'churn_date': 'first_churn'})
        joined = frame.merge(first, on='account_id', how='left', validate='many_to_one')
        add(f'{name}.after_first_churn', joined, joined[date_col].gt(joined.first_churn), FILES[name][1],
            'Fato após primeiro churn observado; não prova erro se houver reativação ou contratos simultâneos.',
            'Reconstruir episódios; não eliminar toda atividade posterior.', kind='reconciliation')

    # Presença de contrato na data não é prova de estado real, apenas reconciliação.
    j = actual.merge(s[['account_id', 'start_date', 'end_date']], on='account_id', how='left')
    active = j.start_date.le(j.churn_date) & (j.end_date.isna() | j.end_date.gt(j.churn_date))
    active_ids = set(j.loc[active, 'churn_event_id'])
    end_ids = set(j.loc[j.end_date.eq(j.churn_date), 'churn_event_id'])
    add('churn.event_with_other_open_contract', actual, actual.churn_event_id.isin(active_ids), 'churn_event_id',
        'Evento de churn com pelo menos um contrato aberto na data, segundo intervalos [início,término).',
        'Não chamar evento de perda total de conta ou somar todo MRR da conta.', kind='reconciliation')
    add('churn.event_without_same_day_subscription_end', actual, ~actual.churn_event_id.isin(end_ids), 'churn_event_id',
        'Sem término contratual na mesma data do evento; vínculo ao cancelamento não demonstrado.',
        'Não calcular receita efetivamente perdida a partir de associação presumida.', kind='reconciliation')
    first_churn = actual.groupby('account_id').churn_date.min()
    reactivations = c.loc[c.is_reactivation.eq(True)].copy()
    reactivations['first_churn'] = reactivations.account_id.map(first_churn)
    add('churn.reactivation_without_prior_churn', reactivations,
        reactivations.first_churn.isna() | reactivations.churn_date.le(reactivations.first_churn), 'churn_event_id',
        'Reativação sem churn estritamente anterior registrado.', 'Histórico insuficiente; não criar evento sintético.', kind='reconciliation')

    duplicate_ids = int(raw['usage'].loc[raw['usage'].usage_id.duplicated(False), 'usage_id'].nunique())
    conflicting_rows = raw['usage'].loc[raw['usage'].usage_id.duplicated(False)]
    observed = a.assign(has_any=a.account_id.isin(any_ids), has_churn=a.account_id.isin(churn_ids), has_reactivation=a.account_id.isin(react_ids))
    coverage = {}
    for name, frame in [('usage', usage), ('support', t), ('churn', c)]:
        sizes = frame.groupby('account_id').size().reindex(a.account_id, fill_value=0)
        coverage[name] = {'accounts_with_records': int(sizes.gt(0).sum()), 'records_per_account_median': float(sizes.median()),
                          'records_per_account_min': int(sizes.min()), 'records_per_account_max': int(sizes.max())}
    coherent_usage = usage.usage_date.ge(usage.start_date) & usage.usage_date.ge(usage.signup_date) & (usage.end_date.isna() | usage.usage_date.lt(usage.end_date))
    reference = max(frames[name][col].max() for name, cols in DATES.items() for col in cols)
    open_contract = s.start_date.le(reference) & (s.end_date.isna() | s.end_date.gt(reference))
    open_accounts = set(s.loc[open_contract, 'account_id'])
    add('churn.flag_true_with_open_contract_at_source_end', a,
        a.churn_flag.eq(True) & a.account_id.isin(open_accounts), 'account_id',
        'Flag cadastral de churn com contrato aberto no corte observado da fonte.',
        'Não atribuir status atual definitivo; distinguir carteira contratual e cadastro.', kind='reconciliation')
    return {'audit_version': '1.0.0', 'pandas_version': pd.__version__, 'sources': manifest,
            'findings': findings,
            'summaries': {'churn_events_non_reactivation': len(actual), 'reactivation_events': len(reactivations),
                          'account_churn_flags': int(a.churn_flag.eq(True).sum()), 'accounts_with_churn_event': len(churn_ids),
                          'usage_conflicting_ids': duplicate_ids, 'usage_conflicting_rows': len(conflicting_rows),
                          'usage_duplicate_excess': len(u) - u.usage_id.nunique(),
                          'satisfaction_response_share': float(t.satisfaction_score.notna().mean()),
                          'reference_date_observed_only': str(reference),
                          'usage_contract_consistent_rows_exclusive_end': int(coherent_usage.sum()),
                          'accounts_with_coherent_usage': int(usage.loc[coherent_usage, 'account_id'].nunique()),
                          'accounts_with_coherent_usage_last_30days': int(usage.loc[coherent_usage & usage.usage_date.gt(reference-pd.Timedelta(days=30)) & usage.usage_date.le(reference), 'account_id'].nunique()),
                          'accounts_with_open_contract': len(open_accounts),
                          'usage_on_contract_end_date': int(usage.usage_date.eq(usage.end_date).sum()),
                          'coverage': coverage,
                          'source_categories': {name: {col: sorted(frame[col].dropna().astype(str).unique().tolist()) for col in cols}
                                                for name, frame, cols in [('accounts', a, ['industry','country','plan_tier','referral_source']),
                                                                         ('subscriptions', s, ['billing_frequency','plan_tier']),
                                                                         ('support', t, ['priority','satisfaction_score']),
                                                                         ('churn', c, ['reason_code','feedback_text'])]}},
            'churn_reconciliation': observed[['account_id','churn_flag','has_any','has_churn','has_reactivation']].to_dict('records'),
            'limitations': [
                'Cobertura de extração não pode ser comprovada apenas pela maior data presente.',
                'Sem subscription_id em churn_events, receita perdida por evento não é diretamente observável.',
                'Sem data de mudança para flags cadastrais/comerciais, histórico desses atributos é desconhecido.',
                'Data de satisfação e de primeira resposta não fornecidas; disponibilidade temporal é limitada.',
                'Limites de dias e escala CSAT são contratos propostos, não documentação externa validada.',
                'Datas sem fuso não recebem fuso inventado.',
            ]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.data_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(result['churn_reconciliation']).to_csv(args.output_dir / 'churn_reconciliation.csv', index=False)
    report = {key: value for key, value in result.items() if key != 'churn_reconciliation'}
    report['churn_reconciliation_file'] = 'churn_reconciliation.csv'
    (args.output_dir / 'audit_results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    affected = [f for f in result['findings'] if f['count']]
    print(json.dumps({'checks': len(result['findings']), 'nonzero_findings': len(affected),
                      'findings': [{k:f[k] for k in ['code','count','denominator','share']} for f in affected],
                      'summaries': result['summaries']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
