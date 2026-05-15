"""Tests for envctl.mirror."""

from __future__ import annotations

import pytest

from envctl.env_store import EnvStore
from envctl.mirror import MirrorResult, mirror_target


@pytest.fixture()
def store(tmp_path):
    s = EnvStore(base_dir=str(tmp_path))
    s.save("prod", {"DB_HOST": "prod-db", "DB_PORT": "5432", "SECRET": "s3cr3t"})
    s.save("staging", {"DB_HOST": "staging-db", "APP_ENV": "staging"})
    s.save("dev", {})
    return s


class TestMirrorTarget:
    def test_returns_mirror_result(self, store):
        result = mirror_target(store, "prod", ["dev"])
        assert isinstance(result, MirrorResult)

    def test_all_keys_copied_to_empty_dest(self, store):
        mirror_target(store, "prod", ["dev"])
        dev_env = store.load("dev")
        assert dev_env["DB_HOST"] == "prod-db"
        assert dev_env["DB_PORT"] == "5432"
        assert dev_env["SECRET"] == "s3cr3t"

    def test_keys_mirrored_list_is_sorted(self, store):
        result = mirror_target(store, "prod", ["dev"])
        assert result.keys_mirrored == sorted(result.keys_mirrored)

    def test_subset_of_keys(self, store):
        result = mirror_target(store, "prod", ["dev"], keys=["DB_HOST"])
        dev_env = store.load("dev")
        assert "DB_HOST" in dev_env
        assert "SECRET" not in dev_env
        assert result.keys_mirrored == ["DB_HOST"]

    def test_no_overwrite_by_default(self, store):
        mirror_target(store, "prod", ["staging"])
        staging_env = store.load("staging")
        # staging already had DB_HOST=staging-db; must not be overwritten
        assert staging_env["DB_HOST"] == "staging-db"

    def test_skipped_recorded_when_no_overwrite(self, store):
        result = mirror_target(store, "prod", ["staging"])
        assert "staging" in result.skipped
        assert "DB_HOST" in result.skipped["staging"]

    def test_overwrite_replaces_existing(self, store):
        mirror_target(store, "prod", ["staging"], overwrite=True)
        staging_env = store.load("staging")
        assert staging_env["DB_HOST"] == "prod-db"

    def test_overwrite_skipped_is_empty(self, store):
        result = mirror_target(store, "prod", ["staging"], overwrite=True)
        assert result.skipped == {}

    def test_multiple_destinations(self, store):
        result = mirror_target(store, "prod", ["staging", "dev"])
        assert set(result.destinations) == {"staging", "dev"}
        dev_env = store.load("dev")
        assert "DB_HOST" in dev_env

    def test_creates_new_destination_target(self, store):
        mirror_target(store, "prod", ["canary"])
        assert "canary" in store.list_targets()

    def test_source_stored_in_result(self, store):
        result = mirror_target(store, "prod", ["dev"])
        assert result.source == "prod"

    def test_summary_contains_key_count(self, store):
        result = mirror_target(store, "prod", ["dev"])
        assert "3" in result.summary()

    def test_summary_mentions_skipped(self, store):
        result = mirror_target(store, "prod", ["staging"])
        assert "skipped" in result.summary().lower()
