"""Tests for envctl.prune."""
from __future__ import annotations

import pytest

from envctl.env_store import EnvStore
from envctl.prune import PruneResult, prune_targets


@pytest.fixture()
def store(tmp_path):
    s = EnvStore(base_dir=str(tmp_path))
    s.save("production", {"DB_HOST": "prod-db", "DB_PASS": "secret", "APP_PORT": "8080"})
    s.save("staging", {"DB_HOST": "stg-db", "DB_PASS": "stgsecret", "APP_PORT": "9090"})
    s.save("dev", {"APP_PORT": "3000", "DEBUG": "true"})
    return s


class TestPruneTargets:
    def test_returns_prune_results(self, store):
        results = prune_targets(store, keys=["DB_PASS"])
        assert all(isinstance(r, PruneResult) for r in results)

    def test_removes_explicit_key(self, store):
        prune_targets(store, keys=["DB_PASS"])
        assert "DB_PASS" not in store.load("production")
        assert "DB_PASS" not in store.load("staging")

    def test_key_absent_in_target_is_skipped(self, store):
        results = prune_targets(store, keys=["DB_PASS"])
        dev_result = next(r for r in results if r.target == "dev")
        assert "DB_PASS" not in dev_result.removed

    def test_pattern_removes_matching_keys(self, store):
        prune_targets(store, pattern=r"^DB_")
        prod = store.load("production")
        assert "DB_HOST" not in prod
        assert "DB_PASS" not in prod
        assert "APP_PORT" in prod

    def test_dry_run_does_not_persist(self, store):
        prune_targets(store, keys=["DB_PASS"], dry_run=True)
        assert "DB_PASS" in store.load("production")

    def test_dry_run_flag_set_in_result(self, store):
        results = prune_targets(store, keys=["DB_PASS"], dry_run=True)
        assert all(r.dry_run for r in results)

    def test_targets_filter_limits_scope(self, store):
        prune_targets(store, keys=["DB_PASS"], targets=["production"])
        assert "DB_PASS" not in store.load("production")
        assert "DB_PASS" in store.load("staging")

    def test_removed_list_is_sorted(self, store):
        results = prune_targets(store, pattern=r"^DB_", targets=["production"])
        prod = next(r for r in results if r.target == "production")
        assert prod.removed == sorted(prod.removed)

    def test_no_keys_or_pattern_raises(self, store):
        with pytest.raises(ValueError, match="At least one"):
            prune_targets(store)

    def test_summary_nothing_pruned(self, store):
        results = prune_targets(store, keys=["NONEXISTENT"], targets=["dev"])
        assert "nothing pruned" in results[0].summary()

    def test_summary_shows_count(self, store):
        results = prune_targets(store, keys=["DB_PASS"], targets=["production"])
        assert "1 key(s)" in results[0].summary()

    def test_summary_dry_run_label(self, store):
        results = prune_targets(store, keys=["DB_PASS"], targets=["production"], dry_run=True)
        assert "dry run" in results[0].summary()

    def test_combined_keys_and_pattern(self, store):
        prune_targets(store, keys=["APP_PORT"], pattern=r"^DB_", targets=["production"])
        prod = store.load("production")
        assert prod == {}
