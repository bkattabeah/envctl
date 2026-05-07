"""Tests for envctl.compare."""

import pytest
from unittest.mock import MagicMock
from envctl.compare import compare_targets, CompareResult


@pytest.fixture
def store():
    s = MagicMock()
    s.load.side_effect = lambda t: {
        "dev": {"HOST": "localhost", "PORT": "8080", "DEBUG": "true"},
        "prod": {"HOST": "example.com", "PORT": "443", "SECRET": "xyz"},
        "staging": {"HOST": "staging.example.com", "PORT": "443", "DEBUG": "false"},
    }[t]
    return s


class TestCompareTargets:
    def test_requires_two_targets(self, store):
        with pytest.raises(ValueError, match="At least two"):
            compare_targets(store, ["dev"])

    def test_all_keys_present(self, store):
        result = compare_targets(store, ["dev", "prod"])
        assert set(result.all_keys) == {"HOST", "PORT", "DEBUG", "SECRET"}

    def test_common_keys(self, store):
        result = compare_targets(store, ["dev", "prod"])
        assert set(result.common_keys) == {"HOST", "PORT"}

    def test_unique_keys_dev(self, store):
        result = compare_targets(store, ["dev", "prod"])
        assert result.unique_keys["dev"] == ["DEBUG"]
        assert result.unique_keys["prod"] == ["SECRET"]

    def test_matrix_absent_value_is_none(self, store):
        result = compare_targets(store, ["dev", "prod"])
        assert result.matrix["SECRET"]["dev"] is None
        assert result.matrix["SECRET"]["prod"] == "xyz"

    def test_has_divergence(self, store):
        result = compare_targets(store, ["dev", "prod"])
        assert result.has_divergence() is True

    def test_no_divergence_when_values_equal(self):
        s = MagicMock()
        s.load.side_effect = lambda t: {"A": "1", "B": "2"}
        result = compare_targets(s, ["dev", "prod"])
        assert result.has_divergence() is False
        assert result.divergent_keys() == []

    def test_divergent_keys_listed(self, store):
        result = compare_targets(store, ["dev", "prod"])
        assert "HOST" in result.divergent_keys()
        assert "PORT" in result.divergent_keys()

    def test_three_targets(self, store):
        result = compare_targets(store, ["dev", "prod", "staging"])
        assert "DEBUG" in result.all_keys
        assert "SECRET" in result.unique_keys["prod"]

    def test_keys_for_target(self, store):
        result = compare_targets(store, ["dev", "prod"])
        assert "DEBUG" in result.keys_for("dev")
        assert "DEBUG" not in result.keys_for("prod")

    def test_targets_stored_in_order(self, store):
        result = compare_targets(store, ["dev", "prod"])
        assert result.targets == ["dev", "prod"]
