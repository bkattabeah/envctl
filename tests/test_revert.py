"""Tests for envctl.revert."""

import pytest
from unittest.mock import patch
from envctl.env_store import EnvStore
from envctl.revert import revert_target, RevertResult


@pytest.fixture
def store(tmp_path):
    return EnvStore(base_dir=str(tmp_path))


SNAPSHOT_ENV = {"HOST": "prod.example.com", "PORT": "443", "DEBUG": "false"}
CURRENT_ENV = {"HOST": "staging.example.com", "PORT": "443", "EXTRA": "yes"}


def _patch_snapshot(env):
    return patch("envctl.revert.load_snapshot", return_value=env)


class TestRevertTarget:
    def test_returns_revert_result(self, store):
        store.save("prod", CURRENT_ENV)
        with _patch_snapshot(SNAPSHOT_ENV):
            result = revert_target(store, "prod", "snap-001")
        assert isinstance(result, RevertResult)

    def test_reverted_env_matches_snapshot(self, store):
        store.save("prod", CURRENT_ENV)
        with _patch_snapshot(SNAPSHOT_ENV):
            result = revert_target(store, "prod", "snap-001")
        assert result.reverted_env == SNAPSHOT_ENV

    def test_detects_added_keys(self, store):
        store.save("prod", CURRENT_ENV)
        with _patch_snapshot(SNAPSHOT_ENV):
            result = revert_target(store, "prod", "snap-001")
        assert "DEBUG" in result.keys_added

    def test_detects_removed_keys(self, store):
        store.save("prod", CURRENT_ENV)
        with _patch_snapshot(SNAPSHOT_ENV):
            result = revert_target(store, "prod", "snap-001")
        assert "EXTRA" in result.keys_removed

    def test_detects_changed_keys(self, store):
        store.save("prod", CURRENT_ENV)
        with _patch_snapshot(SNAPSHOT_ENV):
            result = revert_target(store, "prod", "snap-001")
        assert "HOST" in result.keys_changed

    def test_store_updated_after_revert(self, store):
        store.save("prod", CURRENT_ENV)
        with _patch_snapshot(SNAPSHOT_ENV):
            revert_target(store, "prod", "snap-001")
        assert store.load("prod") == SNAPSHOT_ENV

    def test_dry_run_does_not_modify_store(self, store):
        store.save("prod", CURRENT_ENV)
        with _patch_snapshot(SNAPSHOT_ENV):
            revert_target(store, "prod", "snap-001", dry_run=True)
        assert store.load("prod") == CURRENT_ENV

    def test_no_changes_when_identical(self, store):
        store.save("prod", SNAPSHOT_ENV)
        with _patch_snapshot(SNAPSHOT_ENV):
            result = revert_target(store, "prod", "snap-001")
        assert result.keys_added == []
        assert result.keys_removed == []
        assert result.keys_changed == []

    def test_summary_no_changes(self, store):
        store.save("prod", SNAPSHOT_ENV)
        with _patch_snapshot(SNAPSHOT_ENV):
            result = revert_target(store, "prod", "snap-001")
        assert result.summary() == "No changes applied."

    def test_summary_with_changes(self, store):
        store.save("prod", CURRENT_ENV)
        with _patch_snapshot(SNAPSHOT_ENV):
            result = revert_target(store, "prod", "snap-001")
        summary = result.summary()
        assert "Reverted" in summary

    def test_previous_env_recorded(self, store):
        store.save("prod", CURRENT_ENV)
        with _patch_snapshot(SNAPSHOT_ENV):
            result = revert_target(store, "prod", "snap-001")
        assert result.previous_env == CURRENT_ENV

    def test_snapshot_id_stored_in_result(self, store):
        store.save("prod", CURRENT_ENV)
        with _patch_snapshot(SNAPSHOT_ENV):
            result = revert_target(store, "prod", "snap-001")
        assert result.snapshot_id == "snap-001"
