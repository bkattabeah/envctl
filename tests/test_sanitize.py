"""Tests for envctl.sanitize."""

import pytest
from unittest.mock import MagicMock

from envctl.sanitize import SanitizeResult, _normalize_key, sanitize_target


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _store(env: dict) -> MagicMock:
    store = MagicMock()
    store.load.return_value = dict(env)
    return store


# ---------------------------------------------------------------------------
# _normalize_key
# ---------------------------------------------------------------------------

class TestNormalizeKey:
    def test_uppercases(self):
        assert _normalize_key("db_host") == "DB_HOST"

    def test_replaces_hyphen(self):
        assert _normalize_key("my-key") == "MY_KEY"

    def test_collapses_underscores(self):
        assert _normalize_key("a__b") == "A_B"

    def test_strips_leading_trailing_underscores(self):
        assert _normalize_key("_foo_") == "FOO"

    def test_replaces_spaces(self):
        assert _normalize_key("my key") == "MY_KEY"


# ---------------------------------------------------------------------------
# sanitize_target
# ---------------------------------------------------------------------------

@pytest.fixture
def store():
    return _store({
        "db_host": "  localhost  ",
        "my-secret": "abc123",
        "EMPTY_VAL": "   ",
        "GOOD_KEY": "value",
    })


class TestSanitizeTarget:
    def test_returns_sanitize_result(self, store):
        result = sanitize_target(store, "prod")
        assert isinstance(result, SanitizeResult)

    def test_target_name_stored(self, store):
        result = sanitize_target(store, "prod")
        assert result.target == "prod"

    def test_strips_whitespace_from_value(self, store):
        result = sanitize_target(store, "prod")
        assert result.sanitized.get("DB_HOST") == "localhost"

    def test_normalizes_key_with_hyphen(self, store):
        result = sanitize_target(store, "prod")
        assert "MY_SECRET" in result.sanitized
        assert "my-secret" not in result.sanitized

    def test_renamed_tracks_old_to_new(self, store):
        result = sanitize_target(store, "prod")
        assert result.renamed.get("my-secret") == "MY_SECRET"
        assert result.renamed.get("db_host") == "DB_HOST"

    def test_removes_empty_values_by_default(self, store):
        result = sanitize_target(store, "prod")
        assert "EMPTY_VAL" not in result.sanitized
        assert "EMPTY_VAL" in result.removed

    def test_keeps_empty_values_when_disabled(self, store):
        result = sanitize_target(store, "prod", remove_empty=False)
        assert "EMPTY_VAL" in result.sanitized
        assert result.sanitized["EMPTY_VAL"] == ""

    def test_dry_run_does_not_persist(self, store):
        sanitize_target(store, "prod", dry_run=True)
        store.save.assert_not_called()

    def test_persists_when_not_dry_run(self, store):
        result = sanitize_target(store, "prod")
        store.save.assert_called_once_with("prod", result.sanitized)

    def test_summary_reports_changes(self, store):
        result = sanitize_target(store, "prod")
        s = result.summary()
        assert "renamed" in s
        assert "removed" in s

    def test_summary_clean_when_no_changes(self):
        s = _store({"CLEAN": "value"})
        result = sanitize_target(s, "staging")
        assert "already clean" in result.summary()

    def test_skip_key_normalization(self):
        s = _store({"my-key": "val"})
        result = sanitize_target(s, "dev", normalize_keys=False)
        assert "my-key" in result.sanitized
        assert result.renamed == {}
