"""Tests for envctl.clone and envctl.clone_render."""

import pytest

from envctl.env_store import EnvStore
from envctl.clone import clone_target, CloneResult
from envctl.clone_render import render_clone_result


@pytest.fixture
def store(tmp_path):
    return EnvStore(base_dir=str(tmp_path))


class TestCloneTarget:
    def test_copies_all_keys(self, store):
        store.save("prod", {"A": "1", "B": "2"})
        result = clone_target(store, "prod", "staging")
        assert store.load("staging") == {"A": "1", "B": "2"}
        assert sorted(result.keys_copied) == ["A", "B"]
        assert result.keys_skipped == []

    def test_include_filter(self, store):
        store.save("prod", {"A": "1", "B": "2", "C": "3"})
        result = clone_target(store, "prod", "staging", include=["A", "C"])
        loaded = store.load("staging")
        assert "A" in loaded and "C" in loaded
        assert "B" not in loaded
        assert "B" in result.keys_skipped

    def test_exclude_filter(self, store):
        store.save("prod", {"A": "1", "SECRET": "x"})
        result = clone_target(store, "prod", "staging", exclude=["SECRET"])
        assert "SECRET" not in store.load("staging")
        assert "SECRET" in result.keys_skipped

    def test_no_overwrite_by_default(self, store):
        store.save("prod", {"A": "new"})
        store.save("staging", {"A": "old"})
        clone_target(store, "prod", "staging")
        assert store.load("staging")["A"] == "old"

    def test_overwrite_flag_replaces_existing(self, store):
        store.save("prod", {"A": "new"})
        store.save("staging", {"A": "old"})
        clone_target(store, "prod", "staging", overwrite=True)
        assert store.load("staging")["A"] == "new"

    def test_destination_created_if_missing(self, store):
        store.save("prod", {"X": "1"})
        assert "staging" not in store.list_targets()
        clone_target(store, "prod", "staging")
        assert "staging" in store.list_targets()

    def test_result_source_and_destination(self, store):
        store.save("prod", {"K": "v"})
        result = clone_target(store, "prod", "dev")
        assert result.source == "prod"
        assert result.destination == "dev"

    def test_summary_contains_counts(self, store):
        store.save("prod", {"A": "1", "B": "2"})
        result = clone_target(store, "prod", "staging")
        assert "2 key(s) copied" in result.summary


class TestRenderCloneResult:
    def test_contains_source_and_dest(self, store):
        store.save("prod", {"A": "1"})
        result = clone_target(store, "prod", "staging")
        rendered = render_clone_result(result, color=False)
        assert "prod" in rendered
        assert "staging" in rendered

    def test_copied_keys_listed(self, store):
        store.save("prod", {"FOO": "bar"})
        result = clone_target(store, "prod", "staging")
        rendered = render_clone_result(result, color=False)
        assert "FOO" in rendered

    def test_skipped_keys_listed(self, store):
        store.save("prod", {"A": "1", "B": "2"})
        result = clone_target(store, "prod", "staging", include=["A"])
        rendered = render_clone_result(result, color=False)
        assert "B" in rendered
        assert "Skipped" in rendered

    def test_no_keys_copied_message(self, store):
        store.save("prod", {"A": "1"})
        store.save("staging", {"A": "existing"})
        result = clone_target(store, "prod", "staging", overwrite=False)
        rendered = render_clone_result(result, color=False)
        assert "No keys copied" in rendered

    def test_color_false_has_no_escape_codes(self, store):
        store.save("prod", {"X": "1"})
        result = clone_target(store, "prod", "dev")
        rendered = render_clone_result(result, color=False)
        assert "\033[" not in rendered
