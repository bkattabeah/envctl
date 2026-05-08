"""Tests for envctl.archive — archive and restore environment bundles."""

from __future__ import annotations

import pytest
from pathlib import Path

from envctl.env_store import EnvStore
from envctl.archive import archive_target, restore_archive, ArchiveResult


@pytest.fixture
def store(tmp_path):
    return EnvStore(base_dir=str(tmp_path / "envs"))


@pytest.fixture
def dest_dir(tmp_path):
    return str(tmp_path / "bundles")


class TestArchiveTarget:
    def test_returns_archive_result(self, store, dest_dir):
        store.save("prod", {"A": "1"})
        result = archive_target(store, "prod", dest_dir)
        assert isinstance(result, ArchiveResult)

    def test_archive_path_exists(self, store, dest_dir):
        store.save("prod", {"A": "1"})
        result = archive_target(store, "prod", dest_dir)
        assert Path(result.archive_path).exists()

    def test_keys_archived_sorted(self, store, dest_dir):
        store.save("prod", {"Z": "z", "A": "a", "M": "m"})
        result = archive_target(store, "prod", dest_dir)
        assert result.keys_archived == ["A", "M", "Z"]

    def test_bundle_extension(self, store, dest_dir):
        store.save("prod", {"X": "1"})
        result = archive_target(store, "prod", dest_dir)
        assert result.archive_path.endswith(".envbundle")

    def test_summary_contains_target(self, store, dest_dir):
        store.save("prod", {"X": "1"})
        result = archive_target(store, "prod", dest_dir)
        assert "prod" in result.summary()


class TestRestoreArchive:
    def test_restores_all_keys(self, store, dest_dir):
        store.save("prod", {"A": "1", "B": "2"})
        ar = archive_target(store, "prod", dest_dir)
        result = restore_archive(store, ar.archive_path, "staging")
        assert store.load("staging") == {"A": "1", "B": "2"}

    def test_does_not_overwrite_by_default(self, store, dest_dir):
        store.save("prod", {"A": "from_prod"})
        store.save("staging", {"A": "existing"})
        ar = archive_target(store, "prod", dest_dir)
        restore_archive(store, ar.archive_path, "staging", overwrite=False)
        assert store.load("staging")["A"] == "existing"

    def test_overwrite_flag_replaces_existing(self, store, dest_dir):
        store.save("prod", {"A": "from_prod"})
        store.save("staging", {"A": "existing"})
        ar = archive_target(store, "prod", dest_dir)
        restore_archive(store, ar.archive_path, "staging", overwrite=True)
        assert store.load("staging")["A"] == "from_prod"

    def test_overwritten_keys_recorded(self, store, dest_dir):
        store.save("prod", {"A": "new"})
        store.save("staging", {"A": "old"})
        ar = archive_target(store, "prod", dest_dir)
        result = restore_archive(store, ar.archive_path, "staging", overwrite=True)
        assert "A" in result.overwritten_keys

    def test_restored_to_set(self, store, dest_dir):
        store.save("prod", {"A": "1"})
        ar = archive_target(store, "prod", dest_dir)
        result = restore_archive(store, ar.archive_path, "staging")
        assert result.restored_to == "staging"

    def test_summary_restore_contains_targets(self, store, dest_dir):
        store.save("prod", {"A": "1"})
        ar = archive_target(store, "prod", dest_dir)
        result = restore_archive(store, ar.archive_path, "staging")
        s = result.summary()
        assert "staging" in s
