"""Tests for envctl.trim."""

import pytest

from envctl.env_store import EnvStore
from envctl.trim import TrimResult, trim_target


@pytest.fixture
def store(tmp_path):
    s = EnvStore(base_dir=str(tmp_path))
    s.save("prod", {"DB_HOST": "db.prod", "DB_PORT": "5432", "API_KEY": "secret", "DEBUG": "false"})
    return s


class TestTrimTarget:
    def test_removes_explicit_keys(self, store):
        result = trim_target(store, "prod", keys=["DEBUG"])
        assert "DEBUG" not in store.load("prod")
        assert "DEBUG" in result.removed

    def test_skips_missing_keys(self, store):
        result = trim_target(store, "prod", keys=["NONEXISTENT"])
        assert "NONEXISTENT" in result.skipped
        assert result.removed == []

    def test_pattern_removes_matching_keys(self, store):
        result = trim_target(store, "prod", pattern="DB_*")
        env = store.load("prod")
        assert "DB_HOST" not in env
        assert "DB_PORT" not in env
        assert "DB_HOST" in result.removed
        assert "DB_PORT" in result.removed

    def test_combined_keys_and_pattern(self, store):
        result = trim_target(store, "prod", keys=["DEBUG"], pattern="API_*")
        env = store.load("prod")
        assert "DEBUG" not in env
        assert "API_KEY" not in env
        assert set(result.removed) == {"DEBUG", "API_KEY"}

    def test_dry_run_does_not_modify_store(self, store):
        original = dict(store.load("prod"))
        result = trim_target(store, "prod", keys=["DEBUG"], dry_run=True)
        assert store.load("prod") == original
        assert "DEBUG" in result.removed

    def test_removed_keys_are_sorted(self, store):
        result = trim_target(store, "prod", pattern="DB_*")
        assert result.removed == sorted(result.removed)

    def test_skipped_keys_are_sorted(self, store):
        result = trim_target(store, "prod", keys=["ZZZ", "AAA"])
        assert result.skipped == ["AAA", "ZZZ"]

    def test_raises_when_no_criteria(self, store):
        with pytest.raises(ValueError):
            trim_target(store, "prod")

    def test_summary_with_removals(self, store):
        result = trim_target(store, "prod", keys=["DEBUG"])
        assert "1 key(s) removed" in result.summary()
        assert "prod" in result.summary()

    def test_summary_with_skipped(self, store):
        result = trim_target(store, "prod", keys=["MISSING"])
        assert "1 key(s) not found" in result.summary()

    def test_summary_nothing_to_trim(self, store):
        store.save("empty", {})
        result = trim_target(store, "empty", pattern="DB_*")
        assert "nothing to trim" in result.summary()

    def test_no_duplicate_keys_from_combined_criteria(self, store):
        result = trim_target(store, "prod", keys=["DB_HOST"], pattern="DB_*", dry_run=True)
        assert result.removed.count("DB_HOST") == 1
