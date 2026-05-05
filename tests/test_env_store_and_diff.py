"""Tests for EnvStore and diff utilities."""

import pytest
import tempfile
import os
from pathlib import Path

from envctl.env_store import EnvStore
from envctl.diff import diff_envs, EnvDiffResult


@pytest.fixture
def store(tmp_path):
    return EnvStore(store_dir=str(tmp_path / ".envctl"))


class TestEnvStore:
    def test_save_and_load(self, store):
        env = {"DB_HOST": "localhost", "PORT": "5432"}
        store.save("staging", env)
        loaded = store.load("staging")
        assert loaded == env

    def test_list_targets(self, store):
        store.save("staging", {"A": "1"})
        store.save("production", {"A": "2"})
        assert store.list_targets() == ["production", "staging"]

    def test_delete(self, store):
        store.save("dev", {"X": "1"})
        store.delete("dev")
        assert "dev" not in store.list_targets()

    def test_load_missing_raises(self, store):
        with pytest.raises(FileNotFoundError):
            store.load("nonexistent")

    def test_delete_missing_raises(self, store):
        with pytest.raises(FileNotFoundError):
            store.delete("ghost")

    def test_invalid_target_name_raises(self, store):
        with pytest.raises(ValueError):
            store.save("my-target", {})

    def test_load_from_dotenv(self, store, tmp_path):
        dotenv = tmp_path / ".env"
        dotenv.write_text("# comment\nKEY1=value1\nKEY2='quoted'\nKEY3=\"double\"\n")
        result = store.load_from_dotenv(str(dotenv))
        assert result == {"KEY1": "value1", "KEY2": "quoted", "KEY3": "double"}


class TestDiff:
    def test_no_differences(self):
        env = {"A": "1", "B": "2"}
        result = diff_envs("a", env, "b", env.copy())
        assert not result.has_differences
        assert set(result.unchanged) == {"A", "B"}

    def test_added_key(self):
        result = diff_envs("a", {"A": "1"}, "b", {"A": "1", "B": "2"})
        assert result.added == {"B": "2"}
        assert not result.removed

    def test_removed_key(self):
        result = diff_envs("a", {"A": "1", "B": "2"}, "b", {"A": "1"})
        assert result.removed == {"B": "2"}

    def test_changed_value(self):
        result = diff_envs("a", {"URL": "http://old"}, "b", {"URL": "http://new"})
        assert result.changed == {"URL": ("http://old", "http://new")}

    def test_mask_secrets(self):
        result = diff_envs("a", {"SECRET": "abc"}, "b", {"SECRET": "xyz"}, mask_secrets=True)
        assert result.changed["SECRET"] == ("****", "****")

    def test_summary_with_differences(self):
        result = diff_envs("dev", {"A": "1"}, "prod", {"A": "2", "B": "3"})
        summary = result.summary()
        assert "+ B=3" in summary
        assert "~ A" in summary

    def test_summary_no_differences(self):
        result = diff_envs("dev", {"A": "1"}, "prod", {"A": "1"})
        assert "No differences" in result.summary()
