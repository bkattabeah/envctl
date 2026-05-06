"""Tests for envctl.merge and envctl.merge_render."""

from __future__ import annotations

import pytest

from envctl.env_store import EnvStore
from envctl.merge import MergeResult, merge_targets
from envctl.merge_render import render_merge_result


@pytest.fixture()
def store(tmp_path):
    s = EnvStore(base_dir=str(tmp_path))
    s.save("prod", {"DB_HOST": "prod-db", "LOG_LEVEL": "warn", "APP_PORT": "8080"})
    s.save("staging", {"DB_HOST": "staging-db", "LOG_LEVEL": "debug", "STAGING_ONLY": "1"})
    s.save("base", {"APP_PORT": "8080", "TIMEOUT": "30"})
    return s


class TestMergeTargets:
    def test_all_keys_present(self, store):
        result = merge_targets(store, ["prod", "base"])
        assert "DB_HOST" in result.merged
        assert "TIMEOUT" in result.merged
        assert "APP_PORT" in result.merged

    def test_first_strategy_wins(self, store):
        result = merge_targets(store, ["prod", "staging"], strategy="first")
        assert result.merged["DB_HOST"] == "prod-db"

    def test_last_strategy_wins(self, store):
        result = merge_targets(store, ["prod", "staging"], strategy="last")
        assert result.merged["DB_HOST"] == "staging-db"

    def test_conflicts_detected(self, store):
        result = merge_targets(store, ["prod", "staging"])
        assert "DB_HOST" in result.conflicts
        assert "LOG_LEVEL" in result.conflicts

    def test_no_conflict_for_unique_keys(self, store):
        result = merge_targets(store, ["prod", "staging"])
        assert "APP_PORT" not in result.conflicts
        assert "STAGING_ONLY" not in result.conflicts

    def test_overrides_applied(self, store):
        result = merge_targets(store, ["prod", "base"], overrides={"APP_PORT": "9999"})
        assert result.merged["APP_PORT"] == "9999"

    def test_sources_recorded(self, store):
        result = merge_targets(store, ["prod", "base"])
        assert result.sources == ["prod", "base"]

    def test_invalid_strategy_raises(self, store):
        with pytest.raises(ValueError, match="Unknown merge strategy"):
            merge_targets(store, ["prod"], strategy="random")

    def test_has_conflicts_property(self, store):
        result = merge_targets(store, ["prod", "staging"])
        assert result.has_conflicts is True

    def test_no_conflicts_property(self, store):
        result = merge_targets(store, ["prod", "base"])
        # APP_PORT is in both with same value path but conflict tracking is source-based
        # base has APP_PORT too — should flag it
        result2 = merge_targets(store, ["base"])
        assert result2.has_conflicts is False


class TestMergeRender:
    def test_output_contains_keys(self, store):
        result = merge_targets(store, ["prod", "staging"])
        output = render_merge_result(result)
        assert "DB_HOST" in output
        assert "STAGING_ONLY" in output

    def test_mask_hides_values(self, store):
        result = merge_targets(store, ["prod", "base"])
        output = render_merge_result(result, mask_keys=True)
        assert "***" in output
        assert "prod-db" not in output

    def test_conflict_summary_in_output(self, store):
        result = merge_targets(store, ["prod", "staging"])
        output = render_merge_result(result)
        assert "conflict" in output.lower()

    def test_no_conflict_message(self, store):
        result = merge_targets(store, ["base"])
        output = render_merge_result(result)
        assert "No conflicts" in output

    def test_sources_shown(self, store):
        result = merge_targets(store, ["prod", "staging"])
        output = render_merge_result(result)
        assert "prod" in output
        assert "staging" in output
