"""Tests for envctl.pipeline_render."""
from __future__ import annotations

import pytest

from envctl.pipeline import PipelineResult
from envctl.pipeline_render import render_pipeline_dry_run, render_pipeline_result


def _make_result(**kwargs) -> PipelineResult:
    defaults = dict(
        target="staging",
        steps_applied=["upper", "add_VERSION"],
        initial_env={"KEY": "value", "OLD": "gone"},
        final_env={"KEY": "VALUE", "NEW": "added"},
        skipped=[],
        error=None,
    )
    defaults.update(kwargs)
    return PipelineResult(**defaults)


class TestRenderPipelineResult:
    def test_contains_target_name(self):
        out = render_pipeline_result(_make_result())
        assert "staging" in out

    def test_shows_applied_steps(self):
        out = render_pipeline_result(_make_result())
        assert "upper" in out
        assert "add_VERSION" in out

    def test_shows_skipped_steps(self):
        out = render_pipeline_result(_make_result(skipped=["bad_step"]))
        assert "bad_step" in out

    def test_shows_added_keys(self):
        out = render_pipeline_result(_make_result())
        assert "NEW" in out

    def test_shows_removed_keys(self):
        out = render_pipeline_result(_make_result())
        assert "OLD" in out

    def test_shows_changed_keys(self):
        result = _make_result(
            initial_env={"KEY": "value"},
            final_env={"KEY": "VALUE"},
        )
        out = render_pipeline_result(result)
        assert "KEY" in out

    def test_error_shown(self):
        result = _make_result(error="Target 'x' not found.", steps_applied=[], final_env={}, initial_env={})
        out = render_pipeline_result(result)
        assert "error" in out.lower() or "Pipeline" in out
        assert "not found" in out

    def test_no_change_message_when_env_unchanged(self):
        result = _make_result(
            steps_applied=["noop"],
            initial_env={"A": "1"},
            final_env={"A": "1"},
        )
        out = render_pipeline_result(result)
        assert "No keys changed" in out

    def test_summary_line_present(self):
        out = render_pipeline_result(_make_result())
        assert "step" in out.lower()


class TestRenderPipelineDryRun:
    def test_contains_dry_run_label(self):
        result = _make_result()
        out = render_pipeline_dry_run(result)
        assert "dry-run" in out

    def test_contains_summary(self):
        result = _make_result()
        out = render_pipeline_dry_run(result)
        assert "staging" in out
