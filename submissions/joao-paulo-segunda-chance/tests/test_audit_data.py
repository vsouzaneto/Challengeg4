import csv
import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.audit_data import audit, FILES


class AuditIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.rows = {
            'accounts': [dict(account_id='A1', account_name='Example', industry='DevTools', country='US',
                              signup_date='2024-01-01', referral_source='organic', plan_tier='Pro', seats=1,
                              is_trial='false', churn_flag='true')],
            'subscriptions': [dict(subscription_id='S1', account_id='A1', start_date='2024-01-01', end_date='',
                                   plan_tier='Pro', seats=1, mrr_amount=100, arr_amount=1200, is_trial='false',
                                   upgrade_flag='false', downgrade_flag='false', churn_flag='false',
                                   billing_frequency='monthly', auto_renew_flag='true')],
            'usage': [dict(usage_id='U1', subscription_id='S1', usage_date='2023-12-31', feature_name='f',
                          usage_count=2, usage_duration_secs=5, error_count=0, is_beta_feature='false'),
                      dict(usage_id='U1', subscription_id='S1', usage_date='2024-02-01', feature_name='f',
                          usage_count=3, usage_duration_secs=5, error_count=0, is_beta_feature='false')],
            'support': [dict(ticket_id='T1', account_id='A1', submitted_at='2023-12-31',
                            closed_at='2024-01-01 00:00:00', resolution_time_hours=24, priority='high',
                            first_response_time_minutes=30, satisfaction_score='', escalation_flag='false')],
            'churn': [dict(churn_event_id='C1', account_id='A1', churn_date='2024-03-01', reason_code='pricing',
                          refund_amount_usd=0, preceding_upgrade_flag='false', preceding_downgrade_flag='false',
                          is_reactivation='false', feedback_text=''),
                      dict(churn_event_id='C2', account_id='A1', churn_date='2024-02-01', reason_code='unknown',
                          refund_amount_usd=0, preceding_upgrade_flag='false', preceding_downgrade_flag='false',
                          is_reactivation='true', feedback_text='')],
        }

    def tearDown(self):
        self.temp.cleanup()

    def run_audit(self):
        for name, rows in self.rows.items():
            with (self.folder / FILES[name][0]).open('w', newline='') as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.folder.glob('*.csv')}
        result = audit(self.folder)
        after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.folder.glob('*.csv')}
        self.assertEqual(before, after, 'Auditoria deve preservar arquivos originais.')
        return result, {f['code']: f['count'] for f in result['findings']}

    def test_conflicting_ids_are_not_silently_deduplicated(self):
        result, counts = self.run_audit()
        self.assertEqual(counts['usage.repeated_key_rows'], 2)
        self.assertEqual(counts['usage.exact_duplicate_excess'], 0)
        self.assertEqual(result['summaries']['usage_duplicate_excess'], 1)

    def test_temporal_inconsistency_and_missing_score_are_separate(self):
        _, counts = self.run_audit()
        self.assertEqual(counts['usage.before_subscription'], 1)
        self.assertEqual(counts['support.before_signup'], 1)
        self.assertEqual(counts['support.missing_satisfaction'], 1)
        self.assertEqual(counts['support.duration_mismatch'], 0)

    def test_event_with_open_contract_is_not_full_account_loss(self):
        _, counts = self.run_audit()
        self.assertEqual(counts['churn.event_with_other_open_contract'], 1)
        self.assertEqual(counts['churn.event_without_same_day_subscription_end'], 1)

    def test_reactivation_before_first_observed_churn_is_incomplete(self):
        _, counts = self.run_audit()
        self.assertEqual(counts['churn.reactivation_without_prior_churn'], 1)

    def test_missing_events_do_not_remove_registered_churn(self):
        self.rows['churn'][0]['account_id'] = 'unknown'
        self.rows['churn'][1]['account_id'] = 'unknown'
        result, counts = self.run_audit()
        self.assertEqual(counts['churn.flag_true_without_any_event'], 1)
        self.assertTrue(result['churn_reconciliation'][0]['churn_flag'])

    def test_duplicate_parent_is_rejected_before_join_inflation(self):
        self.rows['subscriptions'].append(self.rows['subscriptions'][0].copy())
        with self.assertRaisesRegex(ValueError, 'chave pai duplicada'):
            self.run_audit()


if __name__ == '__main__':
    unittest.main()
