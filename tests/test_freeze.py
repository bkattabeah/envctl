"""Tests for envctl.freeze and envctl.freeze_render."""

from __future__ import annotations

import pytest

from envctl.freeze import (
    FreezeResult,
    freeze_target,
    is_frozen,
    list_frozen,
    unfreeze_target,
)
from envctl.freeze_render import (
    render_freeze_guard,
    render_freeze_result,
    render_frozen_list,
    render_unfreeze_not_found,
)


@pytest.fixture
def tmp_base(tmp_path):
    return str(tmp_path)


class TestFreezeTarget:
    def test_returns_freeze_result(self, tmp_base):
        result = freeze_target(tmp_base, "production")
        assert isinstance(result, FreezeResult)

    def test_frozen_flag_is_true(self, tmp_base):
        result = freeze_target(tmp_base, "production")
        assert result.frozen is True

    def test_target_name_stored(self, tmp_base):
        result = freeze_target(tmp_base, "staging")
        assert result.target == "staging"

    def test_label_stored(self, tmp_base):
        result = freeze_target(tmp_base, "production", label="release-1.0")
        assert result.label == "release-1.0"

    def test_is_frozen_returns_true_after_freeze(self, tmp_base):
        freeze_target(tmp_base, "production")
        assert is_frozen(tmp_base, "production") is True

    def test_is_frozen_returns_false_before_freeze(self, tmp_base):
        assert is_frozen(tmp_base, "production") is False

    def test_timestamp_is_iso_format(self, tmp_base):
        result = freeze_target(tmp_base, "production")
        assert "T" in result.timestamp


class TestUnfreezeTarget:
    def test_unfreeze_returns_result(self, tmp_base):
        freeze_target(tmp_base, "staging")
        result = unfreeze_target(tmp_base, "staging")
        assert result is not None
        assert result.frozen is False

    def test_unfreeze_removes_frozen_status(self, tmp_base):
        freeze_target(tmp_base, "staging")
        unfreeze_target(tmp_base, "staging")
        assert is_frozen(tmp_base, "staging") is False

    def test_unfreeze_not_frozen_returns_none(self, tmp_base):
        result = unfreeze_target(tmp_base, "dev")
        assert result is None


class TestListFrozen:
    def test_empty_when_none_frozen(self, tmp_base):
        assert list_frozen(tmp_base) == []

    def test_lists_all_frozen_targets(self, tmp_base):
        freeze_target(tmp_base, "prod")
        freeze_target(tmp_base, "staging")
        names = [r.target for r in list_frozen(tmp_base)]
        assert "prod" in names
        assert "staging" in names

    def test_sorted_by_target_name(self, tmp_base):
        freeze_target(tmp_base, "zzz")
        freeze_target(tmp_base, "aaa")
        names = [r.target for r in list_frozen(tmp_base)]
        assert names == sorted(names)

    def test_unfrozen_target_not_in_list(self, tmp_base):
        freeze_target(tmp_base, "prod")
        freeze_target(tmp_base, "dev")
        unfreeze_target(tmp_base, "dev")
        names = [r.target for r in list_frozen(tmp_base)]
        assert "dev" not in names


class TestFreezeResultSummary:
    def test_summary_contains_target(self, tmp_base):
        r = freeze_target(tmp_base, "production")
        assert "production" in r.summary()

    def test_summary_says_frozen(self, tmp_base):
        r = freeze_target(tmp_base, "production")
        assert "frozen" in r.summary()

    def test_summary_includes_label(self, tmp_base):
        r = freeze_target(tmp_base, "production", label="v2")
        assert "v2" in r.summary()


class TestFreezeRender:
    def test_render_freeze_contains_target(self, tmp_base):
        r = freeze_target(tmp_base, "prod")
        out = render_freeze_result(r)
        assert "prod" in out

    def test_render_frozen_list_no_frozen(self, tmp_base):
        out = render_frozen_list([])
        assert "No frozen" in out

    def test_render_frozen_list_shows_targets(self, tmp_base):
        r = freeze_target(tmp_base, "prod")
        out = render_frozen_list([r])
        assert "prod" in out

    def test_render_unfreeze_not_found(self):
        out = render_unfreeze_not_found("dev")
        assert "dev" in out
        assert "not frozen" in out

    def test_render_freeze_guard_contains_target(self):
        out = render_freeze_guard("production")
        assert "production" in out
        assert "blocked" in out or "frozen" in out
