"""Tests for envctl.promote and envctl.promote_render."""

import pytest
from unittest.mock import patch
from envctl.env_store import EnvStore
from envctl.promote import promote_target, PromoteResult
from envctl.promote_render import render_promote_result


@pytest.fixture
def store(tmp_path):
    s = EnvStore(base_dir=tmp_path)
    s.save("staging", {"DB_URL": "postgres://staging", "API_KEY": "stg-key", "DEBUG": "true"})
    s.save("production", {"DB_URL": "postgres://prod", "LOG_LEVEL": "warn"})
    return s


class TestPromoteTarget:
    def test_promotes_new_keys(self, store):
        result = promote_target(store, "staging", "production")
        prod = store.load("production")
        assert prod["API_KEY"] == "stg-key"
        assert prod["DEBUG"] == "true"

    def test_does_not_overwrite_by_default(self, store):
        result = promote_target(store, "staging", "production")
        prod = store.load("production")
        assert prod["DB_URL"] == "postgres://prod"

    def test_overwrite_flag_replaces_existing(self, store):
        result = promote_target(store, "staging", "production", overwrite=True)
        prod = store.load("production")
        assert prod["DB_URL"] == "postgres://staging"

    def test_specific_keys_only(self, store):
        result = promote_target(store, "staging", "production", keys=["API_KEY"])
        prod = store.load("production")
        assert "API_KEY" in prod
        assert "DEBUG" not in prod

    def test_missing_key_in_source_is_skipped(self, store):
        result = promote_target(store, "staging", "production", keys=["NONEXISTENT"])
        assert "NONEXISTENT" in result.skipped_keys

    def test_result_tracks_promoted_keys(self, store):
        result = promote_target(store, "staging", "production", keys=["API_KEY", "DEBUG"])
        assert set(result.promoted_keys) == {"API_KEY", "DEBUG"}

    def test_result_tracks_skipped_keys(self, store):
        result = promote_target(store, "staging", "production", keys=["DB_URL"])
        assert "DB_URL" in result.skipped_keys

    def test_result_tracks_overwritten_keys(self, store):
        result = promote_target(store, "staging", "production", keys=["DB_URL"], overwrite=True)
        assert "DB_URL" in result.overwritten_keys

    def test_summary_nothing_to_promote(self, store):
        result = promote_target(store, "staging", "production", keys=["DB_URL"])
        assert "skipped" in result.summary

    def test_audit_recorded_on_change(self, store):
        with patch("envctl.promote.record") as mock_record:
            promote_target(store, "staging", "production", keys=["API_KEY"], label="ci")
            mock_record.assert_called_once()
            _, kwargs = mock_record.call_args
            assert kwargs["action"] == "promote"
            assert kwargs["label"] == "ci"

    def test_audit_not_recorded_when_nothing_changes(self, store):
        with patch("envctl.promote.record") as mock_record:
            promote_target(store, "staging", "production", keys=["DB_URL"])
            mock_record.assert_not_called()


class TestRenderPromoteResult:
    def _make_result(self):
        r = PromoteResult(source="staging", destination="production")
        r.promoted_keys = ["API_KEY"]
        r.overwritten_keys = ["DB_URL"]
        r.skipped_keys = ["DEBUG"]
        return r

    def test_contains_source_and_dest(self):
        r = self._make_result()
        out = render_promote_result(r, color=False)
        assert "staging" in out
        assert "production" in out

    def test_contains_promoted_key(self):
        r = self._make_result()
        out = render_promote_result(r, color=False)
        assert "API_KEY" in out

    def test_contains_skipped_key(self):
        r = self._make_result()
        out = render_promote_result(r, color=False)
        assert "DEBUG" in out

    def test_summary_line_present(self):
        r = self._make_result()
        out = render_promote_result(r, color=False)
        assert "Summary" in out
