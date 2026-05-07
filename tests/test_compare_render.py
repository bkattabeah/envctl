"""Tests for envctl.compare_render."""

import pytest
from envctl.compare import CompareResult
from envctl.compare_render import render_compare_table, _summary_line


@pytest.fixture
def simple_result():
    return CompareResult(
        targets=["dev", "prod"],
        all_keys=["HOST", "PORT", "SECRET"],
        matrix={
            "HOST": {"dev": "localhost", "prod": "example.com"},
            "PORT": {"dev": "8080", "prod": "443"},
            "SECRET": {"dev": None, "prod": "xyz"},
        },
        common_keys=["HOST", "PORT"],
        unique_keys={"dev": [], "prod": ["SECRET"]},
    )


class TestRenderCompareTable:
    def test_contains_target_headers(self, simple_result):
        out = render_compare_table(simple_result)
        assert "dev" in out
        assert "prod" in out

    def test_contains_all_keys(self, simple_result):
        out = render_compare_table(simple_result)
        assert "HOST" in out
        assert "PORT" in out
        assert "SECRET" in out

    def test_absent_shown(self, simple_result):
        out = render_compare_table(simple_result)
        assert "(absent)" in out

    def test_mask_replaces_value(self, simple_result):
        out = render_compare_table(simple_result, mask_keys=["SECRET"])
        assert "xyz" not in out
        assert "***" in out

    def test_summary_included(self, simple_result):
        out = render_compare_table(simple_result)
        assert "Summary:" in out

    def test_summary_key_counts(self, simple_result):
        line = _summary_line(simple_result)
        assert "3 keys total" in line
        assert "2 common" in line

    def test_divergent_count_in_summary(self, simple_result):
        line = _summary_line(simple_result)
        # HOST and PORT differ between dev and prod
        assert "2 divergent" in line

    def test_unique_keys_in_summary(self, simple_result):
        line = _summary_line(simple_result)
        assert "prod: 1 unique" in line

    def test_separator_line_present(self, simple_result):
        out = render_compare_table(simple_result)
        assert "---" in out

    def test_no_mask_shows_value(self, simple_result):
        out = render_compare_table(simple_result)
        assert "xyz" in out
