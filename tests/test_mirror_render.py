"""Tests for envctl.mirror_render."""

from __future__ import annotations

import pytest

from envctl.mirror import MirrorResult
from envctl.mirror_render import (
    render_mirror_no_destinations,
    render_mirror_result,
    render_mirror_source_not_found,
)


@pytest.fixture()
def full_result():
    return MirrorResult(
        source="prod",
        destinations=["staging", "dev"],
        keys_mirrored=["DB_HOST", "DB_PORT", "SECRET"],
        skipped={"staging": ["DB_HOST"]},
        overwrite=False,
    )


@pytest.fixture()
def empty_result():
    return MirrorResult(
        source="prod",
        destinations=["dev"],
        keys_mirrored=[],
        skipped={},
        overwrite=False,
    )


class TestRenderMirrorResult:
    def test_contains_source_name(self, full_result):
        out = render_mirror_result(full_result)
        assert "prod" in out

    def test_contains_destination_names(self, full_result):
        out = render_mirror_result(full_result)
        assert "staging" in out
        assert "dev" in out

    def test_lists_mirrored_keys(self, full_result):
        out = render_mirror_result(full_result)
        for k in ["DB_HOST", "DB_PORT", "SECRET"]:
            assert k in out

    def test_shows_skipped_section(self, full_result):
        out = render_mirror_result(full_result)
        assert "Skipped" in out or "skipped" in out

    def test_skipped_key_listed(self, full_result):
        out = render_mirror_result(full_result)
        assert "DB_HOST" in out

    def test_no_skipped_section_when_empty(self):
        result = MirrorResult(
            source="prod",
            destinations=["dev"],
            keys_mirrored=["DB_HOST"],
            skipped={},
        )
        out = render_mirror_result(result)
        assert "Skipped" not in out

    def test_empty_keys_shows_no_keys_message(self, empty_result):
        out = render_mirror_result(empty_result)
        assert "No keys" in out

    def test_summary_line_present(self, full_result):
        out = render_mirror_result(full_result)
        assert "Mirrored" in out


class TestRenderErrors:
    def test_source_not_found_contains_name(self):
        out = render_mirror_source_not_found("ghost")
        assert "ghost" in out

    def test_source_not_found_is_error(self):
        out = render_mirror_source_not_found("ghost")
        assert "Error" in out or "error" in out.lower()

    def test_no_destinations_message(self):
        out = render_mirror_no_destinations()
        assert "destination" in out.lower()
