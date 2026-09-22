"""Impedir divulgação de lote incompleto ou contaminação silenciosa do teste."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from classificar_base_completa import partition_rows, summarize, verify_historical


def split():
    return {'train_rows': [1], 'validation_rows': [2], 'test_rows': [3],
            'near_duplicate_filter': {'removed_train': [{'row': 4}], 'removed_validation': [{'row': 5}]}}


def test_partition_includes_excluded_without_relabeling_as_test():
    assert partition_rows(split(), 5) == {1: 'train', 2: 'validation', 3: 'test', 4: 'excluded_train', 5: 'excluded_validation'}


@pytest.mark.parametrize('bad_rows', [[1], [3, 3], [6], [True], []])
def test_rejects_overlap_duplicate_out_of_range_invalid_and_missing(bad_rows):
    value = split()
    value['test_rows'] = bad_rows
    with pytest.raises(ValueError):
        partition_rows(value, 5)


def test_high_score_does_not_hide_disagreement():
    rows = [{'dataset_label': 'Access', 'prediction': 'Access', 'score': .7},
            {'dataset_label': 'Storage', 'prediction': 'Access', 'score': .99},
            {'dataset_label': 'Storage', 'prediction': 'Storage', 'score': .4}]
    actual = summarize(rows, .61)
    assert (actual['agreement_n'], actual['disagreement_n']) == (2, 1)
    assert (actual['above_threshold_n'], actual['above_threshold_disagreement_n']) == (2, 1)
    assert actual['label_distribution'] == {'Access': 1, 'Storage': 2}


@pytest.mark.parametrize('field,value', [('prediction', 'Storage'), ('partition', 'train'), ('truth', 'Storage'), ('score', .8)])
def test_rejects_drift_from_historical_test(field, value):
    row = {'row': 1, 'partition': 'test', 'dataset_label': 'Access', 'prediction': 'Access', 'score': .9}
    old = {'row': 1, 'partition': 'test', 'truth': 'Access', 'prediction': 'Access', 'score': .9}
    old[field] = value
    with pytest.raises(ValueError):
        verify_historical([row], [old])


def test_historical_reference_cannot_be_incomplete():
    with pytest.raises(ValueError):
        verify_historical([{'row': 1, 'partition': 'test'}], [])
