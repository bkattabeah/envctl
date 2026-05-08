"""Tests for envctl.interpolate."""

from __future__ import annotations

import pytest

from envctl.interpolate import interpolate_target, InterpolateResult


class TestInterpolateTarget:
    def test_no_references_returns_unchanged(self):
        env = {"HOST": "localhost", "PORT": "5432"}
        result = interpolate_target("dev", env)
        assert result.resolved == env
        assert result.substitution_count == 0
        assert result.is_complete()

    def test_simple_braced_reference(self):
        env = {"BASE": "https://example.com", "URL": "${BASE}/api"}
        result = interpolate_target("dev", env)
        assert result.resolved["URL"] == "https://example.com/api"
        assert result.substitution_count >= 1

    def test_simple_dollar_reference(self):
        env = {"HOST": "db.local", "DSN": "postgres://$HOST/mydb"}
        result = interpolate_target("dev", env)
        assert result.resolved["DSN"] == "postgres://db.local/mydb"

    def test_chained_references(self):
        env = {"A": "hello", "B": "${A}_world", "C": "${B}!"}
        result = interpolate_target("dev", env)
        assert result.resolved["C"] == "hello_world!"

    def test_unresolved_reference_reported(self):
        env = {"URL": "${MISSING_VAR}/path"}
        result = interpolate_target("dev", env)
        assert "URL" in result.unresolved_keys
        assert not result.is_complete()

    def test_partial_resolution(self):
        env = {"BASE": "http://api", "FULL": "${BASE}/${MISSING}"}
        result = interpolate_target("staging", env)
        # BASE part should be resolved, MISSING stays
        assert "http://api" in result.resolved["FULL"]
        assert "FULL" in result.unresolved_keys

    def test_multiple_refs_in_one_value(self):
        env = {"PROTO": "https", "HOST": "example.com", "URL": "${PROTO}://${HOST}"}
        result = interpolate_target("prod", env)
        assert result.resolved["URL"] == "https://example.com"

    def test_substitution_count_accumulates(self):
        env = {"A": "x", "B": "${A}", "C": "${A}${A}"}
        result = interpolate_target("dev", env)
        assert result.substitution_count >= 3

    def test_target_name_stored(self):
        result = interpolate_target("production", {})
        assert result.target == "production"

    def test_is_complete_with_no_unresolved(self):
        result = InterpolateResult(target="t", resolved={"K": "v"}, unresolved_keys=[])
        assert result.is_complete()

    def test_is_complete_false_with_unresolved(self):
        result = InterpolateResult(target="t", resolved={}, unresolved_keys=["X"])
        assert not result.is_complete()

    def test_summary_ok_when_complete(self):
        result = InterpolateResult(target="dev", resolved={}, unresolved_keys=[], substitution_count=2)
        s = result.summary()
        assert "status=ok" in s
        assert "substitutions=2" in s

    def test_summary_shows_unresolved(self):
        result = InterpolateResult(target="dev", resolved={}, unresolved_keys=["FOO", "BAR"])
        s = result.summary()
        assert "unresolved=" in s
        assert "FOO" in s

    def test_empty_env_returns_empty_resolved(self):
        result = interpolate_target("dev", {})
        assert result.resolved == {}
        assert result.is_complete()
