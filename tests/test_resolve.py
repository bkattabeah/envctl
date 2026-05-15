"""Tests for envctl.resolve."""

from __future__ import annotations

import pytest

from envctl.env_store import EnvStore
from envctl.resolve import ResolveResult, resolve_target


@pytest.fixture()
def store(tmp_path):
    s = EnvStore(base_dir=str(tmp_path))
    s.save("production", {"APP_ENV": "prod", "DEBUG": "false"})
    s.save("staging", {"APP_ENV": "staging", "DEBUG": "true"})
    return s


class TestResolveTarget:
    def test_returns_resolve_result(self, store):
        result = resolve_target("production", store)
        assert isinstance(result, ResolveResult)

    def test_direct_target_resolves(self, store):
        result = resolve_target("production", store)
        assert result.exists is True
        assert result.resolved_name == "production"
        assert result.alias_used is False

    def test_env_is_populated(self, store):
        result = resolve_target("production", store)
        assert result.env == {"APP_ENV": "prod", "DEBUG": "false"}

    def test_missing_target_returns_not_found(self, store):
        result = resolve_target("nonexistent", store)
        assert result.exists is False
        assert result.resolved_name == "nonexistent"

    def test_missing_target_env_is_empty(self, store):
        result = resolve_target("nonexistent", store)
        assert result.env == {}

    def test_follows_alias(self, store, tmp_path):
        from envctl.alias import add_alias

        add_alias(str(tmp_path), "prod", "production")
        result = resolve_target("prod", store)
        assert result.exists is True
        assert result.resolved_name == "production"
        assert result.alias_used is True
        assert result.raw_name == "prod"

    def test_alias_env_is_correct(self, store, tmp_path):
        from envctl.alias import add_alias

        add_alias(str(tmp_path), "prod", "production")
        result = resolve_target("prod", store)
        assert result.env["APP_ENV"] == "prod"

    def test_follow_alias_false_skips_lookup(self, store, tmp_path):
        from envctl.alias import add_alias

        add_alias(str(tmp_path), "prod", "production")
        result = resolve_target("prod", store, follow_alias=False)
        assert result.exists is False
        assert result.alias_used is False

    def test_summary_direct(self, store):
        result = resolve_target("production", store)
        assert "production" in result.summary()
        assert "2" in result.summary()

    def test_summary_alias(self, store, tmp_path):
        from envctl.alias import add_alias

        add_alias(str(tmp_path), "prod", "production")
        result = resolve_target("prod", store)
        assert "prod" in result.summary()
        assert "production" in result.summary()

    def test_summary_not_found(self, store):
        result = resolve_target("ghost", store)
        assert "not found" in result.summary().lower()
