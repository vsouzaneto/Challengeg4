import unittest
from decimal import Decimal
from domain.source_contracts import parse_record, ContractError, CONTRACTS


class SourceContractTest(unittest.TestCase):
    def account(self):
        return dict(account_id='A1', account_name='Example', industry='DevTools', country='US',
                    signup_date='2024-01-01', referral_source='organic', plan_tier='Pro', seats='1',
                    is_trial='false', churn_flag='true')

    def test_missing_required_value_fails(self):
        row = self.account(); row['account_id'] = ''
        with self.assertRaises(ContractError): parse_record('accounts', row)

    def test_unknown_boolean_is_not_false(self):
        row = self.account(); row['churn_flag'] = 'unknown'
        with self.assertRaises(ContractError): parse_record('accounts', row)

    def test_seats_are_integer_not_fractional(self):
        row = self.account(); row['seats'] = '1.5'
        with self.assertRaises(ContractError): parse_record('accounts', row)

    def test_zero_is_preserved(self):
        row = self.account(); row['seats'] = '0'
        self.assertEqual(parse_record('accounts', row)['seats'], 0)

    def test_date_is_not_silently_repaired(self):
        row = self.account(); row['signup_date'] = '2024-02-31'
        with self.assertRaises(ContractError): parse_record('accounts', row)

    def test_extra_fields_require_new_contract(self):
        row = self.account(); row['new_field'] = 'value'
        with self.assertRaises(ContractError): parse_record('accounts', row)

    def test_blank_nullable_is_unknown(self):
        row = {key:'x' for key in CONTRACTS['support']}
        row.update(ticket_id='T1', account_id='A1', submitted_at='2024-01-01', closed_at='2024-01-02',
                   resolution_time_hours='24', first_response_time_minutes='0', satisfaction_score='',
                   escalation_flag='false')
        self.assertIsNone(parse_record('support', row)['satisfaction_score'])

    def test_financial_precision(self):
        row = {key:'x' for key in CONTRACTS['churn']}
        row.update(churn_event_id='C1', account_id='A1', churn_date='2024-01-01', refund_amount_usd='10.01',
                   preceding_upgrade_flag='false', preceding_downgrade_flag='false', is_reactivation='false', feedback_text='')
        self.assertEqual(parse_record('churn', row)['refund_amount_usd'], Decimal('10.01'))

    def test_nonfinite_number_fails(self):
        row = {key:'x' for key in CONTRACTS['churn']}
        row.update(churn_date='2024-01-01', refund_amount_usd='Infinity',
                   preceding_upgrade_flag='false', preceding_downgrade_flag='false', is_reactivation='false', feedback_text='')
        with self.assertRaises(ContractError): parse_record('churn', row)


if __name__ == '__main__': unittest.main()
