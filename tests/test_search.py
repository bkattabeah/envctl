"""Tests for envctl.search module."""

import pytest
from unittest.mock import MagicMock
from envctl.search import SearchMatch, SearchResult, search_envs


@pytest.fixture
def store():
    mock = MagicMock()
    mock.list_targets.return_value = ["dev", "prod"]
    mock.load.side_effect = lambda t: {
        "dev": {"DATABASE_URL": "postgres://localhost", "DEBUG": "true", "PORT": "5432"},
        "prod": {"DATABASE_URL": "postgres://prod-host", "DEBUG": "false", "PORT": "443"},
    }[t]
    return mock


class TestSearchResult:
    def test_has_matches_false_when_empty(self):
        r = SearchResult(query="x")
        assert not r.has_matches

    def test_has_matches_true_when_populated(self):
        r = SearchResult(query="x", matches=[SearchMatch("dev", "K", "V", "key")])
        assert r.has_matches

    def test_summary_no_matches(self):
        r = SearchResult(query="ghost")
        assert "No matches" in r.summary()
        assert "ghost" in r.summary()

    def test_summary_with_matches(self):
        r = SearchResult(query="db", matches=[SearchMatch("dev", "DB", "val", "key")])
        assert "1" in r.summary()

    def test_targets_matched_unique(self):
        r = SearchResult(
            query="x",
            matches=[
                SearchMatch("dev", "A", "v", "key"),
                SearchMatch("dev", "B", "v", "key"),
                SearchMatch("prod", "A", "v", "key"),
            ],
        )
        assert r.targets_matched() == ["dev", "prod"]


class TestSearchEnvs:
    def test_finds_key_match(self, store):
        result = search_envs(store, "DATABASE")
        keys = [m.key for m in result.matches]
        assert "DATABASE_URL" in keys

    def test_finds_value_match(self, store):
        result = search_envs(store, "localhost")
        assert result.has_matches
        assert all(m.matched_on in ("value", "both") for m in result.matches)

    def test_matched_on_both(self, store):
        store.list_targets.return_value = ["dev"]
        store.load.side_effect = lambda t: {"dev": {"PORT": "PORT_VALUE"}}[t]
        result = search_envs(store, "PORT")
        assert any(m.matched_on == "both" for m in result.matches)

    def test_keys_only_flag(self, store):
        result = search_envs(store, "localhost", keys_only=True)
        assert not result.has_matches

    def test_values_only_flag(self, store):
        result = search_envs(store, "DATABASE", values_only=True)
        assert not result.has_matches

    def test_case_insensitive_default(self, store):
        result = search_envs(store, "database_url")
        assert result.has_matches

    def test_case_sensitive_no_match(self, store):
        result = search_envs(store, "database_url", case_sensitive=True)
        assert not result.has_matches

    def test_case_sensitive_match(self, store):
        result = search_envs(store, "DATABASE_URL", case_sensitive=True)
        assert result.has_matches

    def test_target_filter(self, store):
        result = search_envs(store, "DATABASE", targets=["dev"])
        targets = {m.target for m in result.matches}
        assert targets == {"dev"}

    def test_no_matches_returns_empty(self, store):
        result = search_envs(store, "NONEXISTENT_XYZ_123")
        assert not result.has_matches
        assert result.matches == []
