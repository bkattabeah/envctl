"""Tests for envctl.rename and envctl.rename_render."""

import pytest
from unittest.mock import patch
from envctl.env_store import EnvStore
from envctl.rename import rename_key, RenameResult
from envctl.rename_render import render_rename_result


@pytest.fixture()
def store(tmp_path):
    return EnvStore(base_dir=str(tmp_path))


class TestRenameKey:
    def test_renames_key_in_target(self, store):
        store.save("prod", {"OLD": "value", "OTHER": "x"})
        result = rename_key(store, "OLD", "NEW", targets=["prod"])
        assert "NEW" in store.load("prod")
        assert "OLD" not in store.load("prod")
        assert result.affected_targets == ["prod"]

    def test_preserves_value_after_rename(self, store):
        store.save("prod", {"OLD": "hello"})
        rename_key(store, "OLD", "NEW", targets=["prod"])
        assert store.load("prod")["NEW"] == "hello"

    def test_skips_target_when_key_absent(self, store):
        store.save("staging", {"UNRELATED": "1"})
        result = rename_key(store, "MISSING", "NEW", targets=["staging"])
        assert result.skipped_targets == ["staging"]
        assert result.affected_targets == []

    def test_collision_without_overwrite(self, store):
        store.save("prod", {"OLD": "a", "NEW": "b"})
        result = rename_key(store, "OLD", "NEW", targets=["prod"], overwrite=False)
        assert result.collision_targets == ["prod"]
        env = store.load("prod")
        assert env["NEW"] == "b"  # original value preserved
        assert "OLD" in env

    def test_collision_with_overwrite(self, store):
        store.save("prod", {"OLD": "a", "NEW": "b"})
        result = rename_key(store, "OLD", "NEW", targets=["prod"], overwrite=True)
        assert result.affected_targets == ["prod"]
        assert store.load("prod")["NEW"] == "a"

    def test_defaults_to_all_targets(self, store):
        store.save("prod", {"K": "1"})
        store.save("dev", {"K": "2"})
        result = rename_key(store, "K", "KEY")
        assert set(result.affected_targets) == {"prod", "dev"}

    def test_multiple_targets_mixed_outcomes(self, store):
        store.save("prod", {"OLD": "1"})
        store.save("dev", {"NOPE": "2"})
        store.save("staging", {"OLD": "3", "NEW": "existing"})
        result = rename_key(
            store, "OLD", "NEW",
            targets=["prod", "dev", "staging"],
            overwrite=False,
        )
        assert result.affected_targets == ["prod"]
        assert result.skipped_targets == ["dev"]
        assert result.collision_targets == ["staging"]

    def test_summary_all_updated(self, store):
        store.save("prod", {"A": "1"})
        result = rename_key(store, "A", "B", targets=["prod"])
        assert "prod" in result.summary()
        assert "B" in result.summary()

    def test_summary_no_changes(self):
        result = RenameResult(old_key="X", new_key="Y")
        assert result.summary() == "No changes made."


class TestRenderRenameResult:
    def test_contains_old_and_new_key(self, store):
        store.save("prod", {"FOO": "bar"})
        result = rename_key(store, "FOO", "BAR", targets=["prod"])
        output = render_rename_result(result, color=False)
        assert "FOO" in output
        assert "BAR" in output

    def test_shows_updated_target(self, store):
        store.save("prod", {"FOO": "bar"})
        result = rename_key(store, "FOO", "BAR", targets=["prod"])
        output = render_rename_result(result, color=False)
        assert "prod" in output
        assert "Updated" in output

    def test_shows_skipped_target(self, store):
        store.save("dev", {"NOPE": "1"})
        result = rename_key(store, "MISSING", "NEW", targets=["dev"])
        output = render_rename_result(result, color=False)
        assert "Skipped" in output
        assert "dev" in output

    def test_shows_conflict_target(self, store):
        store.save("prod", {"OLD": "1", "NEW": "2"})
        result = rename_key(store, "OLD", "NEW", targets=["prod"])
        output = render_rename_result(result, color=False)
        assert "Conflict" in output

    def test_no_targets_processed_message(self):
        result = RenameResult(old_key="X", new_key="Y")
        output = render_rename_result(result, color=False)
        assert "No targets processed" in output
