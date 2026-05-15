"""Tests for envctl.resolve_render."""

from __future__ import annotations

import pytest

from envctl.resolve import ResolveResult
from envctl.resolve_render import render_resolve_not_found, render_resolve_result


@pytest.fixture()
def found_direct():
    return ResolveResult(
        raw_name="production",
        resolved_name="production",
        alias_used=False,
        exists=True,
        env={"A": "1", "B": "2"},
    )


@pytest.fixture()
def found_via_alias():
    return ResolveResult(
        raw_name="prod",
        resolved_name="production",
        alias_used=True,
        exists=True,
        env={"A": "1"},
    )


@pytest.fixture()
def not_found():
    return ResolveResult(
        raw_name="ghost",
        resolved_name="ghost",
        alias_used=False,
        exists=False,
    )


class TestRenderResolveResult:
    def test_direct_contains_target_name(self, found_direct):
        out = render_resolve_result(found_direct)
        assert "production" in out

    def test_direct_shows_key_count(self, found_direct):
        out = render_resolve_result(found_direct)
        assert "2" in out

    def test_alias_shows_raw_name(self, found_via_alias):
        out = render_resolve_result(found_via_alias)
        assert "prod" in out

    def test_alias_shows_resolved_name(self, found_via_alias):
        out = render_resolve_result(found_via_alias)
        assert "production" in out

    def test_alias_shows_arrow(self, found_via_alias):
        out = render_resolve_result(found_via_alias)
        assert "→" in out

    def test_not_found_shows_error(self, not_found):
        out = render_resolve_result(not_found)
        assert "ghost" in out
        assert "not" in out.lower() or "error" in out.lower()

    def test_verbose_lists_keys(self, found_direct):
        out = render_resolve_result(found_direct, verbose=True)
        assert "A" in out
        assert "B" in out

    def test_non_verbose_hides_keys(self, found_direct):
        out = render_resolve_result(found_direct, verbose=False)
        # key names should not appear in compact output
        assert "A" not in out


class TestRenderResolveNotFound:
    def test_contains_name(self):
        out = render_resolve_not_found("phantom")
        assert "phantom" in out

    def test_contains_error_indicator(self):
        out = render_resolve_not_found("phantom")
        assert "error" in out.lower() or "Cannot" in out
