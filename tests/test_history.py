"""Tests for envctl.history."""

import os
import pytest

from envctl.audit import record
from envctl.history import build_history, KeyHistory, HistoryResult


@pytest.fixture()
def tmp_base(tmp_path):
    return str(tmp_path)


def _record(base, target, keys, action="set", label=None):
    record(base, target, keys, action=action, label=label)


class TestBuildHistory:
    def test_returns_history_result(self, tmp_base):
        _record(tmp_base, "prod", ["FOO"])
        result = build_history(tmp_base, "prod")
        assert isinstance(result, HistoryResult)
        assert result.target == "prod"

    def test_single_key_single_entry(self, tmp_base):
        _record(tmp_base, "prod", ["FOO"])
        result = build_history(tmp_base, "prod")
        assert "FOO" in result.histories
        assert result.histories["FOO"].change_count == 1

    def test_multiple_entries_for_same_key(self, tmp_base):
        _record(tmp_base, "prod", ["FOO"])
        _record(tmp_base, "prod", ["FOO"])
        _record(tmp_base, "prod", ["FOO"])
        result = build_history(tmp_base, "prod")
        assert result.histories["FOO"].change_count == 3

    def test_multiple_keys_tracked_separately(self, tmp_base):
        _record(tmp_base, "prod", ["FOO", "BAR"])
        result = build_history(tmp_base, "prod")
        assert "FOO" in result.histories
        assert "BAR" in result.histories

    def test_key_filter_limits_results(self, tmp_base):
        _record(tmp_base, "prod", ["FOO", "BAR"])
        result = build_history(tmp_base, "prod", key_filter="FOO")
        assert "FOO" in result.histories
        assert "BAR" not in result.histories

    def test_empty_log_returns_empty_history(self, tmp_base):
        result = build_history(tmp_base, "staging")
        assert result.keys_changed() == []

    def test_keys_changed_is_sorted(self, tmp_base):
        _record(tmp_base, "prod", ["ZEBRA", "ALPHA", "MANGO"])
        result = build_history(tmp_base, "prod")
        assert result.keys_changed() == sorted(result.keys_changed())

    def test_for_key_returns_none_when_absent(self, tmp_base):
        result = build_history(tmp_base, "prod")
        assert result.for_key("MISSING") is None

    def test_for_key_returns_key_history(self, tmp_base):
        _record(tmp_base, "prod", ["FOO"])
        result = build_history(tmp_base, "prod")
        kh = result.for_key("FOO")
        assert isinstance(kh, KeyHistory)
        assert kh.key == "FOO"

    def test_last_changed_is_most_recent_entry(self, tmp_base):
        _record(tmp_base, "prod", ["FOO"], label="first")
        _record(tmp_base, "prod", ["FOO"], label="second")
        result = build_history(tmp_base, "prod")
        kh = result.for_key("FOO")
        assert kh.last_changed.label == "second"

    def test_summary_contains_key_name(self, tmp_base):
        _record(tmp_base, "prod", ["FOO"])
        result = build_history(tmp_base, "prod")
        kh = result.for_key("FOO")
        assert "FOO" in kh.summary()

    def test_summary_no_changes(self, tmp_base):
        kh = KeyHistory(target="prod", key="GHOST")
        assert "no recorded changes" in kh.summary()
