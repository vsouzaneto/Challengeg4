"""Validação de integração sem instalar ou simular Streamlit."""
import copy
import unittest
from app import explanation, filter_portfolio, load_portfolio, table_rows


class AppDataTests(unittest.TestCase):
    def test_action_selection_and_labels(self):
        from app import action_opportunities, priority_label
        before = copy.deepcopy(self.rows)
        actions = action_opportunities(self.rows)
        self.assertEqual(len(actions), 5)
        self.assertTrue(all(r['confidence'] in ('Alta', 'Média') for r in actions))
        self.assertTrue(all(not r['watchlist'] for r in actions))
        expected = sorted([r for r in self.rows if r['confidence'] != 'Baixa'],
                          key=lambda r: (-r['priority_score'], r['opportunity_id']))[:5]
        self.assertEqual(actions, expected)
        self.assertEqual(self.rows, before)
        self.assertEqual(action_opportunities([r for r in self.rows if r['watchlist']]), [])
        for score, label in [(90, 'muito alta'), (89.99, 'alta'), (75, 'alta'),
                             (74.99, 'média'), (50, 'média'), (49.99, 'baixa')]:
            self.assertEqual(priority_label(score), 'Prioridade ' + label)

    @classmethod
    def setUpClass(cls):
        cls.rows, _ = load_portfolio()

    def test_all_open_opportunities_preserved(self):
        self.assertEqual(len(self.rows), 2089)
        self.assertEqual(len({r['opportunity_id'] for r in self.rows}), 2089)
        self.assertEqual(len(filter_portfolio(self.rows, {})), 2089)

    def test_every_filter_preserves_global_scores_and_input(self):
        before = copy.deepcopy(self.rows)
        original = {r['opportunity_id']: r['priority_score'] for r in self.rows}
        for field in ['sales_agent', 'manager', 'regional_office', 'deal_stage', 'confidence']:
            for value in {r[field] for r in self.rows}:
                filtered = filter_portfolio(self.rows, {field: [value]})
                self.assertTrue(filtered)
                for r in filtered:
                    self.assertEqual(r[field], value)
                    self.assertEqual(r['priority_score'], original[r['opportunity_id']])
        self.assertEqual(self.rows, before)

    def test_watchlist_and_price_baseline(self):
        filtered = filter_portfolio(self.rows, {}, True, 'Price Only')
        self.assertEqual(len(filtered), 15)
        self.assertTrue(all(r['watchlist'] for r in filtered))
        prices = [r['sales_price'] for r in filter_portfolio(self.rows, {}, ordering='Price Only')]
        self.assertEqual(prices, sorted(prices, reverse=True))
        self.assertEqual(len(table_rows(self.rows)), 2089)

    def test_combined_filters_and_empty_selection(self):
        row = self.rows[0]
        criteria = {key: [row[key]] for key in ['sales_agent', 'manager', 'regional_office', 'deal_stage', 'confidence']}
        filtered = filter_portfolio(self.rows, criteria)
        self.assertTrue(filtered)
        self.assertTrue(all(all(r[k] == row[k] for k in criteria) for r in filtered))
        self.assertEqual(filter_portfolio(self.rows, {'sales_agent': ['inexistente']}), [])
        self.assertEqual(filter_portfolio(self.rows, {'sales_agent': []}), self.rows)

    def test_explanation_uses_actual_evidence(self):
        row = next(r for r in self.rows if r['watchlist'])
        text = explanation(row)
        self.assertIn(f"{row['n_product']:,} negócios", text)
        self.assertIn('Revisão manual recomendada', text)
        self.assertNotIn('chance de fechamento', text)


if __name__ == '__main__':
    unittest.main()
