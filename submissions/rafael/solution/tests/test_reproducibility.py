"""Tests for the reproducibility checker: tolerance on numbers, exact text, ignored build timestamp, pinned versions."""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "reproducibility" / "verify.py"
spec = importlib.util.spec_from_file_location("verify_reproducibility", SCRIPT)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def test_numbers_within_tolerance_are_equal():
    assert verify.differences({"a": [1.0, 2]}, {"a": [1.0 + 1e-12, 2]}) == []


def test_real_changes_are_reported():
    diffs = verify.differences({"a": {"b": 1.0, "c": "47%"}}, {"a": {"b": 1.01, "c": "48%"}})
    assert len(diffs) == 2 and diffs[0].startswith("a/b")


def test_shape_changes_are_reported():
    assert verify.differences({"a": [1, 2]}, {"a": [1]}) and verify.differences({"a": 1}, {"b": 1})


def test_build_timestamp_is_ignored():
    assert verify.differences({"payload": {"meta": {"gerado_em": "x"}}}, {"payload": {"meta": {"gerado_em": "y"}}}) == []


def test_installed_libraries_match_the_pins():
    ok, detail = verify.check_libraries()
    assert ok, detail
