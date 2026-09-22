import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from triage_core import route_suggestion


@pytest.mark.parametrize('category', ['Access', 'Administrative rights'])
def test_sensitive_categories_require_human(category):
    policy = route_suggestion(category, .999, .61, domain_confirmed=True)
    assert policy['action'] == 'review'
    assert 'não autoriza' in policy['reason']


@pytest.mark.parametrize('score,threshold,confirmed', [(.60, .61, True), (.99, None, True), (.99, .61, False)])
def test_abstention(score, threshold, confirmed):
    assert route_suggestion('Hardware', score, threshold, domain_confirmed=confirmed)['action'] == 'review'


def test_threshold_boundary_is_suggestion_requiring_confirmation():
    policy = route_suggestion('Hardware', .61, .61, domain_confirmed=True)
    assert policy['action'] == 'suggest'
    assert 'confirmar' in policy['reason']


def test_unknown_category_and_inference_failure():
    assert route_suggestion('Not a label', .99, .61, domain_confirmed=True)['action'] == 'review'
    assert route_suggestion('Hardware', .99, .61, error='failure', domain_confirmed=True)['action'] == 'review'
