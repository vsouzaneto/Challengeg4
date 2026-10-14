import unittest
from datetime import date
from decimal import Decimal

from domain.quality_specs import State, compare_usage, evaluate_churn, contract_interval


class QualitySpecificationsTest(unittest.TestCase):
    def test_missing_churn_event_is_unknown_not_negative(self):
        self.assertEqual(evaluate_churn(True, False, False), State.INDETERMINATE)

    def test_reactivation_alone_does_not_confirm_churn(self):
        self.assertEqual(evaluate_churn(True, False, True), State.INDETERMINATE)

    def test_historical_event_is_not_current_status(self):
        self.assertEqual(evaluate_churn(False, True, True), State.INDETERMINATE)

    def test_false_flag_without_event_does_not_prove_complete_history(self):
        self.assertEqual(evaluate_churn(False, False, False), State.INDETERMINATE)

    def test_equal_length_windows_flat_usage_has_no_drop(self):
        self.assertEqual(compare_usage(Decimal('100'), Decimal('100'), True), Decimal('0'))

    def test_missing_coverage_is_not_zero_usage(self):
        self.assertIsNone(compare_usage(Decimal('0'), Decimal('100'), False))

    def test_zero_baseline_has_no_measurable_relative_drop(self):
        self.assertIsNone(compare_usage(Decimal('10'), Decimal('0'), True))

    def test_missing_measurement_is_indeterminate(self):
        self.assertIsNone(compare_usage(None, Decimal('100'), True))

    def test_declining_usage_is_relative_to_previous_equal_window(self):
        self.assertEqual(compare_usage(Decimal('65'), Decimal('100'), True), Decimal('0.35'))

    def test_contract_date_boundaries_are_explicit(self):
        start, end = date(2024, 1, 1), date(2024, 2, 1)
        self.assertEqual(contract_interval(start, start, end), State.SATISFIED)
        self.assertEqual(contract_interval(end, start, end), State.NOT_SATISFIED)
        self.assertEqual(contract_interval(date(2023, 12, 31), start, end), State.NOT_SATISFIED)

    def test_invalid_interval_is_not_evaluated(self):
        self.assertEqual(contract_interval(date(2024, 1, 1), date(2024, 2, 1), date(2024, 1, 1)), State.INDETERMINATE)


if __name__ == '__main__':
    unittest.main()
