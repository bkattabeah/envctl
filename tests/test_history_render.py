"""Tests for envctl.history_render."""

import pytest

from envctl.audit import record
from envctl.history import build_history, KeyHistory
from envctl.history_render import (
    render_history_table,
    render_key_history,
    render_history_not_found,
)


@pytest.fixture()
def tmp_base(tmp_path):
    return str(tmp_path)


class TestRenderHistoryTable:
    def test_contains_target_name(self, tmp_base):
        record(tmp_base, "prod", ["FOO"])
        result = build_history(tmp_base, "prod")
        out = render_history_table(result)
        assert "prod" in out

    def test_contains_key_name(self, tmp_base):
        record(tmp_base, "prod", ["MY_KEY"])
        result = build_history(tmp_base, "prod")
        out = render_history_table(result)
        assert "MY_KEY" in out

    def test_empty_history_shows_message(self, tmp_base):
        result = build_history(tmp_base, "empty_target")
        out = render_history_table(result)
        assert "no recorded changes" in out

    def test_change_count_shown(self, tmp_base):
        record(tmp_base, "prod", ["FOO"])
        record(tmp_base, "prod", ["FOO"])
        result = build_history(tmp_base, "prod")
        out = render_history_table(result)
        assert "2" in out

    def test_header_present(self, tmp_base):
        result = build_history(tmp_base, "prod")
        out = render_history_table(result)
        assert "KEY" in out
        assert "CHANGES" in out


class TestRenderKeyHistory:
    def test_contains_key_name(self, tmp_base):
        record(tmp_base, "prod", ["SECRET"])
        result = build_history(tmp_base, "prod")
        kh = result.for_key("SECRET")
        out = render_key_history(kh)
        assert "SECRET" in out

    def test_entry_index_shown(self, tmp_base):
        record(tmp_base, "prod", ["FOO"])
        record(tmp_base, "prod", ["FOO"])
        result = build_history(tmp_base, "prod")
        kh = result.for_key("FOO")
        out = render_key_history(kh)
        assert "1." in out
        assert "2." in out

    def test_empty_key_history_shows_message(self):
        kh = KeyHistory(target="prod", key="GHOST")
        out = render_key_history(kh)
        assert "no recorded changes" in out

    def test_label_shown_when_present(self, tmp_base):
        record(tmp_base, "prod", ["FOO"], label="deploy-v2")
        result = build_history(tmp_base, "prod")
        kh = result.for_key("FOO")
        out = render_key_history(kh)
        assert "deploy-v2" in out


class TestRenderHistoryNotFound:
    def test_contains_key_and_target(self):
        out = render_history_not_found("prod", "MISSING_KEY")
        assert "MISSING_KEY" in out
        assert "prod" in out
