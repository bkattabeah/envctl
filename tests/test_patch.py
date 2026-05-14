"""Tests for envctl.patch."""

from __future__ import annotations

import pytest

from envctl.env_store import EnvStore
from envctl.patch import PatchResult, patch_target


@pytest.fixture()
def store(tmp_path):
    return EnvStore(base_dir=str(tmp_path))


class TestPatchTarget:
    def test_returns_patch_result(self, store):
        store.save("prod", {})
        result = patch_target(store, "prod", {"KEY": "val"})
        assert isinstance(result, PatchResult)

    def test_adds_new_keys(self, store):
        store.save("prod", {})
        result = patch_target(store, "prod", {"NEW": "1"})
        assert "NEW" in result.added
        assert store.load("prod")["NEW"] == "1"

    def test_updates_existing_key_by_default(self, store):
        store.save("prod", {"K": "old"})
        result = patch_target(store, "prod", {"K": "new"})
        assert "K" in result.updated
        assert store.load("prod")["K"] == "new"

    def test_skips_existing_key_when_no_overwrite(self, store):
        store.save("prod", {"K": "old"})
        result = patch_target(store, "prod", {"K": "new"}, overwrite=False)
        assert "K" in result.skipped
        assert store.load("prod")["K"] == "old"

    def test_deletes_keys(self, store):
        store.save("prod", {"A": "1", "B": "2"})
        result = patch_target(store, "prod", {}, delete_keys=["A"])
        assert "A" in result.deleted
        assert "A" not in store.load("prod")

    def test_delete_missing_key_is_ignored(self, store):
        store.save("prod", {"A": "1"})
        result = patch_target(store, "prod", {}, delete_keys=["MISSING"])
        assert "MISSING" not in result.deleted

    def test_combined_add_update_delete(self, store):
        store.save("prod", {"OLD": "x", "KEEP": "y"})
        result = patch_target(
            store, "prod", {"NEW": "n", "KEEP": "z"}, delete_keys=["OLD"]
        )
        assert "NEW" in result.added
        assert "KEEP" in result.updated
        assert "OLD" in result.deleted
        env = store.load("prod")
        assert env == {"NEW": "n", "KEEP": "z"}

    def test_summary_reflects_counts(self, store):
        store.save("prod", {"X": "1"})
        result = patch_target(store, "prod", {"X": "2", "Y": "3"})
        s = result.summary()
        assert "1 added" in s
        assert "1 updated" in s

    def test_summary_no_changes(self, store):
        store.save("prod", {})
        result = patch_target(store, "prod", {})
        assert "no changes" in result.summary()

    def test_creates_target_if_missing(self, store):
        result = patch_target(store, "staging", {"FOO": "bar"})
        assert store.load("staging")["FOO"] == "bar"
        assert "FOO" in result.added
