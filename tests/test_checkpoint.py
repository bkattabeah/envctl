"""Tests for envctl.checkpoint."""

import os
import pytest

from envctl.env_store import EnvStore
from envctl.checkpoint import (
    CheckpointResult,
    create_checkpoint,
    list_checkpoints,
    load_checkpoint,
    delete_checkpoint,
)


@pytest.fixture
def store(tmp_path):
    s = EnvStore(base_dir=str(tmp_path))
    s.save("prod", {"HOST": "prod.example.com", "PORT": "443"})
    s.save("staging", {"HOST": "staging.example.com", "PORT": "8080"})
    return s


class TestCreateCheckpoint:
    def test_returns_checkpoint_result(self, store):
        result = create_checkpoint(store, "prod")
        assert isinstance(result, CheckpointResult)

    def test_checkpoint_id_contains_target(self, store):
        result = create_checkpoint(store, "prod")
        assert "prod" in result.checkpoint_id

    def test_label_in_checkpoint_id(self, store):
        result = create_checkpoint(store, "prod", label="before-release")
        assert "before-release" in result.checkpoint_id

    def test_env_matches_target(self, store):
        result = create_checkpoint(store, "prod")
        assert result.env["HOST"] == "prod.example.com"
        assert result.env["PORT"] == "443"

    def test_file_written_to_disk(self, store):
        result = create_checkpoint(store, "prod")
        cp_dir = os.path.join(store.base_dir, ".checkpoints")
        files = os.listdir(cp_dir)
        assert any(result.checkpoint_id in f for f in files)

    def test_created_at_is_float(self, store):
        result = create_checkpoint(store, "prod")
        assert isinstance(result.created_at, float)
        assert result.created_at > 0

    def test_summary_contains_target(self, store):
        result = create_checkpoint(store, "prod")
        assert "prod" in result.summary()

    def test_summary_contains_key_count(self, store):
        result = create_checkpoint(store, "prod")
        assert "2" in result.summary()


class TestListCheckpoints:
    def test_empty_when_none_created(self, store):
        results = list_checkpoints(store.base_dir)
        assert results == []

    def test_returns_all_checkpoints(self, store):
        create_checkpoint(store, "prod")
        create_checkpoint(store, "staging")
        results = list_checkpoints(store.base_dir)
        assert len(results) == 2

    def test_filter_by_target(self, store):
        create_checkpoint(store, "prod")
        create_checkpoint(store, "staging")
        results = list_checkpoints(store.base_dir, target="prod")
        assert all(r.target == "prod" for r in results)
        assert len(results) == 1


class TestLoadAndDelete:
    def test_load_returns_correct_result(self, store):
        created = create_checkpoint(store, "prod", label="v1")
        loaded = load_checkpoint(store.base_dir, created.checkpoint_id)
        assert loaded is not None
        assert loaded.checkpoint_id == created.checkpoint_id
        assert loaded.env == created.env
        assert loaded.label == "v1"

    def test_load_missing_returns_none(self, store):
        assert load_checkpoint(store.base_dir, "nonexistent-id") is None

    def test_delete_returns_true(self, store):
        created = create_checkpoint(store, "prod")
        assert delete_checkpoint(store.base_dir, created.checkpoint_id) is True

    def test_delete_removes_file(self, store):
        created = create_checkpoint(store, "prod")
        delete_checkpoint(store.base_dir, created.checkpoint_id)
        assert load_checkpoint(store.base_dir, created.checkpoint_id) is None

    def test_delete_missing_returns_false(self, store):
        assert delete_checkpoint(store.base_dir, "ghost-id") is False
