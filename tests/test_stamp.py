"""Tests for envctl.stamp."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from envctl.env_store import EnvStore
from envctl.stamp import (
    StampEntry,
    StampResult,
    latest_stamp,
    list_stamps,
    stamp_target,
)


@pytest.fixture()
def tmp_base(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture()
def store(tmp_base: Path) -> EnvStore:
    s = EnvStore(tmp_base)
    s.save("production", {"APP_ENV": "prod", "LOG_LEVEL": "warn", "PORT": "443"})
    s.save("staging", {"APP_ENV": "staging", "LOG_LEVEL": "debug"})
    return s


class TestStampTarget:
    def test_returns_stamp_result(self, store, tmp_base):
        result = stamp_target(store, tmp_base, "production", "v1.0.0")
        assert isinstance(result, StampResult)

    def test_label_stored_in_result(self, store, tmp_base):
        result = stamp_target(store, tmp_base, "production", "v2.3.1")
        assert result.label == "v2.3.1"

    def test_target_stored_in_result(self, store, tmp_base):
        result = stamp_target(store, tmp_base, "staging", "rc1")
        assert result.target == "staging"

    def test_key_count_reflects_env(self, store, tmp_base):
        result = stamp_target(store, tmp_base, "production", "v1")
        assert result.entry.key_count == 3

    def test_previous_is_none_on_first_stamp(self, store, tmp_base):
        result = stamp_target(store, tmp_base, "production", "v1")
        assert result.previous is None

    def test_previous_reflects_last_label(self, store, tmp_base):
        stamp_target(store, tmp_base, "production", "v1")
        result = stamp_target(store, tmp_base, "production", "v2")
        assert result.previous == "v1"

    def test_timestamp_is_recent(self, store, tmp_base):
        before = time.time()
        result = stamp_target(store, tmp_base, "production", "v1")
        after = time.time()
        assert before <= result.entry.timestamp <= after

    def test_summary_contains_target_and_label(self, store, tmp_base):
        result = stamp_target(store, tmp_base, "production", "v1.0")
        s = result.summary()
        assert "production" in s
        assert "v1.0" in s

    def test_summary_shows_previous_when_present(self, store, tmp_base):
        stamp_target(store, tmp_base, "production", "v1")
        result = stamp_target(store, tmp_base, "production", "v2")
        assert "v1" in result.summary()


class TestListStamps:
    def test_empty_before_any_stamp(self, tmp_base):
        assert list_stamps(tmp_base, "production") == []

    def test_accumulates_stamps(self, store, tmp_base):
        stamp_target(store, tmp_base, "production", "v1")
        stamp_target(store, tmp_base, "production", "v2")
        stamps = list_stamps(tmp_base, "production")
        assert len(stamps) == 2

    def test_stamps_are_stamp_entries(self, store, tmp_base):
        stamp_target(store, tmp_base, "production", "v1")
        stamps = list_stamps(tmp_base, "production")
        assert all(isinstance(s, StampEntry) for s in stamps)

    def test_latest_stamp_returns_last(self, store, tmp_base):
        stamp_target(store, tmp_base, "production", "v1")
        stamp_target(store, tmp_base, "production", "v2")
        latest = latest_stamp(tmp_base, "production")
        assert latest is not None
        assert latest.label == "v2"

    def test_latest_stamp_none_when_no_stamps(self, tmp_base):
        assert latest_stamp(tmp_base, "nonexistent") is None

    def test_targets_are_independent(self, store, tmp_base):
        stamp_target(store, tmp_base, "production", "v1")
        stamp_target(store, tmp_base, "staging", "rc1")
        assert len(list_stamps(tmp_base, "production")) == 1
        assert len(list_stamps(tmp_base, "staging")) == 1
