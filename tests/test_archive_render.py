"""Tests for envctl.archive_render."""

from __future__ import annotations

import pytest
from envctl.archive import ArchiveResult
from envctl.archive_render import render_archive_result, render_restore_result, render_archive_not_found


@pytest.fixture
def archive_result():
    return ArchiveResult(
        target="prod",
        archive_path="/tmp/bundles/prod.envbundle",
        keys_archived=["A", "B", "C"],
    )


@pytest.fixture
def restore_result():
    return ArchiveResult(
        target="prod",
        archive_path="/tmp/bundles/prod.envbundle",
        keys_archived=["A", "B"],
        restored_to="staging",
        overwritten_keys=["A"],
    )


class TestRenderArchiveResult:
    def test_contains_target_name(self, archive_result):
        out = render_archive_result(archive_result)
        assert "prod" in out

    def test_contains_archive_path(self, archive_result):
        out = render_archive_result(archive_result)
        assert "/tmp/bundles/prod.envbundle" in out

    def test_lists_keys(self, archive_result):
        out = render_archive_result(archive_result)
        assert "A" in out and "B" in out and "C" in out

    def test_key_count_shown(self, archive_result):
        out = render_archive_result(archive_result)
        assert "3" in out


class TestRenderRestoreResult:
    def test_contains_restored_to(self, restore_result):
        out = render_restore_result(restore_result)
        assert "staging" in out

    def test_shows_overwritten_key(self, restore_result):
        out = render_restore_result(restore_result)
        assert "A" in out

    def test_no_overwrite_message_when_empty(self):
        result = ArchiveResult(
            target="prod",
            archive_path="/tmp/prod.envbundle",
            keys_archived=["X"],
            restored_to="dev",
        )
        out = render_restore_result(result)
        assert "No existing keys" in out


class TestRenderArchiveNotFound:
    def test_contains_path(self):
        out = render_archive_not_found("/bad/path.envbundle")
        assert "/bad/path.envbundle" in out

    def test_contains_error(self):
        out = render_archive_not_found("/bad/path.envbundle")
        assert "Error" in out or "error" in out.lower()
