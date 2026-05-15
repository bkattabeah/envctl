"""Tests for envctl.drift."""

from __future__ import annotations

import pytest

from envctl.env_store import EnvStore
from envctl.baseline import set_baseline
from envctl.drift import detect_drift, DriftResult


@pytest.fixture()
def store(tmp_path):
    return EnvStore(base_dir=str(tmp_path))


def _seed(store: EnvStore, target: str, env: dict) -> None:
    store.save(target, env)


class TestDetectDrift:
    def test_returns_drift_result(self, store):
        _seed(store, "prod", {"A": "1"})
        set_baseline(store, "prod", label="v1")
        result = detect_drift(store, "prod")
        assert isinstance(result, DriftResult)

    def test_no_drift_when_unchanged(self, store):
        _seed(store, "prod", {"A": "1", "B": "2"})
        set_baseline(store, "prod", label="v1")
        result = detect_drift(store, "prod")
        assert not result.has_drift()

    def test_detects_added_key(self, store):
        _seed(store, "prod", {"A": "1"})
        set_baseline(store, "prod", label="v1")
        _seed(store, "prod", {"A": "1", "NEW": "x"})
        result = detect_drift(store, "prod")
        assert "NEW" in result.added

    def test_detects_removed_key(self, store):
        _seed(store, "prod", {"A": "1", "OLD": "bye"})
        set_baseline(store, "prod", label="v1")
        _seed(store, "prod", {"A": "1"})
        result = detect_drift(store, "prod")
        assert "OLD" in result.removed

    def test_detects_changed_value(self, store):
        _seed(store, "prod", {"A": "old"})
        set_baseline(store, "prod", label="v1")
        _seed(store, "prod", {"A": "new"})
        result = detect_drift(store, "prod")
        assert "A" in result.changed
        assert result.changed["A"] == ("old", "new")

    def test_summary_no_drift(self, store):
        _seed(store, "prod", {"X": "1"})
        set_baseline(store, "prod", label="stable")
        result = detect_drift(store, "prod")
        assert "No drift" in result.summary()

    def test_summary_with_drift(self, store):
        _seed(store, "prod", {"A": "1"})
        set_baseline(store, "prod", label="v1")
        _seed(store, "prod", {"A": "2", "B": "3"})
        result = detect_drift(store, "prod")
        s = result.summary()
        assert "added" in s
        assert "changed" in s

    def test_raises_when_no_baseline(self, store):
        _seed(store, "prod", {"A": "1"})
        with pytest.raises((ValueError, FileNotFoundError)):
            detect_drift(store, "prod")

    def test_baseline_id_stored_in_result(self, store):
        _seed(store, "prod", {"A": "1"})
        br = set_baseline(store, "prod", label="snap")
        result = detect_drift(store, "prod")
        assert result.baseline_id == br.baseline_id

    def test_multiple_drift_types_counted(self, store):
        _seed(store, "prod", {"A": "1", "B": "2", "C": "3"})
        set_baseline(store, "prod", label="v1")
        _seed(store, "prod", {"A": "changed", "D": "new"})
        result = detect_drift(store, "prod")
        assert result.has_drift()
        assert "B" in result.removed
        assert "C" in result.removed
        assert "D" in result.added
        assert "A" in result.changed
