"""Tests for envctl.drift_render."""

from __future__ import annotations

import pytest

from envctl.drift import DriftResult
from envctl.drift_render import render_drift_result, render_drift_clean, render_drift_not_found


@pytest.fixture()
def clean_result():
    return DriftResult(target="prod", baseline_id="prod-20240101-v1")


@pytest.fixture()
def dirty_result():
    return DriftResult(
        target="prod",
        baseline_id="prod-20240101-v1",
        added={"NEW_KEY": "hello"},
        removed={"OLD_KEY": "bye"},
        changed={"CHANGED": ("old_val", "new_val")},
    )


class TestRenderDriftResult:
    def test_contains_target_name(self, dirty_result):
        out = render_drift_result(dirty_result)
        assert "prod" in out

    def test_contains_baseline_id(self, dirty_result):
        out = render_drift_result(dirty_result)
        assert "prod-20240101-v1" in out

    def test_shows_added_key(self, dirty_result):
        out = render_drift_result(dirty_result)
        assert "NEW_KEY" in out

    def test_shows_removed_key(self, dirty_result):
        out = render_drift_result(dirty_result)
        assert "OLD_KEY" in out

    def test_shows_changed_key(self, dirty_result):
        out = render_drift_result(dirty_result)
        assert "CHANGED" in out

    def test_no_drift_message_when_clean(self, clean_result):
        out = render_drift_result(clean_result)
        assert "No drift" in out

    def test_mask_hides_values(self, dirty_result):
        out = render_drift_result(dirty_result, mask=True)
        assert "hello" not in out
        assert "****" in out

    def test_summary_line_present(self, dirty_result):
        out = render_drift_result(dirty_result)
        assert "Drift detected" in out


class TestRenderDriftHelpers:
    def test_clean_contains_tick(self):
        out = render_drift_clean("staging", "staging-abc")
        assert "staging" in out
        assert "staging-abc" in out

    def test_not_found_contains_target(self):
        out = render_drift_not_found("prod")
        assert "prod" in out
        assert "baseline" in out.lower()
