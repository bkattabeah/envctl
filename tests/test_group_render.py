"""Tests for envctl.group_render."""

from __future__ import annotations

import pytest

from envctl.group_render import (
    render_group_added,
    render_group_deleted,
    render_group_list,
    render_group_not_found,
    render_group_removed,
    render_groups_for_target,
    render_targets_in_group,
)


class TestRenderGroupList:
    def test_empty_groups_message(self):
        out = render_group_list({})
        assert "No groups defined" in out

    def test_group_name_present(self):
        out = render_group_list({"production": ["api", "worker"]})
        assert "production" in out

    def test_members_listed(self):
        out = render_group_list({"prod": ["api", "worker"]})
        assert "api" in out
        assert "worker" in out

    def test_empty_group_shows_indicator(self):
        out = render_group_list({"empty-group": []})
        assert "empty" in out.lower()

    def test_multiple_groups_all_shown(self):
        out = render_group_list({"a": ["t1"], "b": ["t2"]})
        assert "a" in out
        assert "b" in out


class TestRenderGroupAdded:
    def test_contains_group_name(self):
        out = render_group_added("prod", "api")
        assert "prod" in out

    def test_contains_target_name(self):
        out = render_group_added("prod", "api")
        assert "api" in out

    def test_contains_added_keyword(self):
        out = render_group_added("prod", "api")
        assert "Added" in out


class TestRenderGroupRemoved:
    def test_contains_removed_keyword(self):
        out = render_group_removed("staging", "db")
        assert "Removed" in out

    def test_contains_names(self):
        out = render_group_removed("staging", "db")
        assert "staging" in out
        assert "db" in out


class TestRenderGroupDeleted:
    def test_contains_deleted_keyword(self):
        out = render_group_deleted("old-group")
        assert "Deleted" in out

    def test_contains_group_name(self):
        out = render_group_deleted("old-group")
        assert "old-group" in out


class TestRenderNotFound:
    def test_contains_group_name(self):
        out = render_group_not_found("ghost")
        assert "ghost" in out


class TestRenderTargetsInGroup:
    def test_lists_targets(self):
        out = render_targets_in_group("prod", ["api", "worker"])
        assert "api" in out
        assert "worker" in out

    def test_empty_group_message(self):
        out = render_targets_in_group("prod", [])
        assert "empty" in out.lower()


class TestRenderGroupsForTarget:
    def test_lists_groups(self):
        out = render_groups_for_target("api", ["prod", "eu"])
        assert "prod" in out
        assert "eu" in out

    def test_no_groups_message(self):
        out = render_groups_for_target("lonely", [])
        assert "no groups" in out.lower()
