"""Tests for envctl.patch_render."""

from __future__ import annotations

from envctl.patch import PatchResult
from envctl.patch_render import render_patch_result


def _make_result(**kwargs) -> PatchResult:
    defaults = dict(
        target="prod",
        added={},
        updated={},
        skipped=[],
        deleted=[],
    )
    defaults.update(kwargs)
    return PatchResult(**defaults)


class TestRenderPatchResult:
    def test_contains_target_name(self):
        r = _make_result()
        out = render_patch_result(r)
        assert "prod" in out

    def test_shows_added_keys(self):
        r = _make_result(added={"FOO": "bar"})
        out = render_patch_result(r)
        assert "FOO" in out
        assert "bar" in out

    def test_shows_updated_keys(self):
        r = _make_result(updated={"KEY": "new"})
        out = render_patch_result(r)
        assert "KEY" in out
        assert "new" in out

    def test_shows_deleted_keys(self):
        r = _make_result(deleted=["OLD"])
        out = render_patch_result(r)
        assert "OLD" in out

    def test_shows_skipped_keys(self):
        r = _make_result(skipped=["SKIP_ME"])
        out = render_patch_result(r)
        assert "SKIP_ME" in out

    def test_mask_hides_values(self):
        r = _make_result(added={"SECRET": "s3cr3t"})
        out = render_patch_result(r, mask=True)
        assert "s3cr3t" not in out
        assert "****" in out

    def test_no_changes_message(self):
        r = _make_result()
        out = render_patch_result(r)
        assert "No changes" in out

    def test_summary_line_present(self):
        r = _make_result(added={"A": "1"})
        out = render_patch_result(r)
        assert "1 added" in out
