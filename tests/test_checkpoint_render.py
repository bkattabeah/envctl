"""Tests for envctl.checkpoint_render."""

import time
import pytest

from envctl.checkpoint import CheckpointResult
from envctl.checkpoint_render import (
    render_checkpoint_saved,
    render_checkpoint_list,
    render_checkpoint_deleted,
    render_checkpoint_not_found,
)


@pytest.fixture
def sample_result():
    return CheckpointResult(
        target="prod",
        checkpoint_id="prod-before-release-1700000000",
        label="before-release",
        env={"HOST": "prod.example.com", "PORT": "443"},
        created_at=1700000000.0,
    )


@pytest.fixture
def unlabelled_result():
    return CheckpointResult(
        target="staging",
        checkpoint_id="staging-cp-1700000001",
        label=None,
        env={"HOST": "staging.example.com"},
        created_at=1700000001.0,
    )


class TestRenderCheckpointSaved:
    def test_contains_checkpoint_id(self, sample_result):
        out = render_checkpoint_saved(sample_result)
        assert sample_result.checkpoint_id in out

    def test_contains_target_name(self, sample_result):
        out = render_checkpoint_saved(sample_result)
        assert "prod" in out

    def test_contains_label(self, sample_result):
        out = render_checkpoint_saved(sample_result)
        assert "before-release" in out

    def test_contains_key_count(self, sample_result):
        out = render_checkpoint_saved(sample_result)
        assert "2" in out

    def test_no_label_does_not_crash(self, unlabelled_result):
        out = render_checkpoint_saved(unlabelled_result)
        assert "staging" in out


class TestRenderCheckpointList:
    def test_empty_list_shows_message(self):
        out = render_checkpoint_list([])
        assert "No checkpoints" in out

    def test_empty_list_with_target_filter(self):
        out = render_checkpoint_list([], target="prod")
        assert "prod" in out

    def test_contains_checkpoint_id(self, sample_result):
        out = render_checkpoint_list([sample_result])
        assert sample_result.checkpoint_id in out

    def test_contains_label(self, sample_result):
        out = render_checkpoint_list([sample_result])
        assert "before-release" in out

    def test_contains_target_column(self, sample_result):
        out = render_checkpoint_list([sample_result])
        assert "prod" in out

    def test_multiple_entries_all_present(self, sample_result, unlabelled_result):
        out = render_checkpoint_list([sample_result, unlabelled_result])
        assert sample_result.checkpoint_id in out
        assert unlabelled_result.checkpoint_id in out


class TestRenderCheckpointActions:
    def test_deleted_contains_id(self):
        out = render_checkpoint_deleted("prod-cp-123")
        assert "prod-cp-123" in out

    def test_not_found_contains_id(self):
        out = render_checkpoint_not_found("ghost-id")
        assert "ghost-id" in out
