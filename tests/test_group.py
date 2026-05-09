"""Tests for envctl.group."""

from __future__ import annotations

import pytest

from envctl.group import (
    add_to_group,
    delete_group,
    groups_for_target,
    list_groups,
    load_groups,
    remove_from_group,
    targets_in_group,
)


@pytest.fixture()
def tmp_base(tmp_path):
    return str(tmp_path)


class TestAddAndList:
    def test_add_creates_group(self, tmp_base):
        add_to_group(tmp_base, "production", "prod-us")
        assert "production" in list_groups(tmp_base)

    def test_add_is_idempotent(self, tmp_base):
        add_to_group(tmp_base, "staging", "stg")
        add_to_group(tmp_base, "staging", "stg")
        assert targets_in_group(tmp_base, "staging").count("stg") == 1

    def test_members_are_sorted(self, tmp_base):
        add_to_group(tmp_base, "g", "z-target")
        add_to_group(tmp_base, "g", "a-target")
        assert targets_in_group(tmp_base, "g") == ["a-target", "z-target"]

    def test_missing_group_returns_empty(self, tmp_base):
        assert targets_in_group(tmp_base, "nonexistent") == []

    def test_list_groups_sorted(self, tmp_base):
        add_to_group(tmp_base, "zebra", "t")
        add_to_group(tmp_base, "alpha", "t")
        assert list_groups(tmp_base) == ["alpha", "zebra"]


class TestRemove:
    def test_remove_existing_target(self, tmp_base):
        add_to_group(tmp_base, "g", "t1")
        add_to_group(tmp_base, "g", "t2")
        remove_from_group(tmp_base, "g", "t1")
        assert "t1" not in targets_in_group(tmp_base, "g")
        assert "t2" in targets_in_group(tmp_base, "g")

    def test_remove_absent_target_is_noop(self, tmp_base):
        add_to_group(tmp_base, "g", "t1")
        remove_from_group(tmp_base, "g", "ghost")
        assert targets_in_group(tmp_base, "g") == ["t1"]


class TestGroupsForTarget:
    def test_returns_groups_containing_target(self, tmp_base):
        add_to_group(tmp_base, "prod", "web")
        add_to_group(tmp_base, "eu", "web")
        add_to_group(tmp_base, "us", "db")
        result = groups_for_target(tmp_base, "web")
        assert result == ["eu", "prod"]

    def test_returns_empty_when_not_in_any_group(self, tmp_base):
        assert groups_for_target(tmp_base, "lonely") == []


class TestDeleteGroup:
    def test_delete_removes_group(self, tmp_base):
        add_to_group(tmp_base, "temp", "t")
        delete_group(tmp_base, "temp")
        assert "temp" not in list_groups(tmp_base)

    def test_delete_returns_true_when_existed(self, tmp_base):
        add_to_group(tmp_base, "g", "t")
        assert delete_group(tmp_base, "g") is True

    def test_delete_returns_false_when_missing(self, tmp_base):
        assert delete_group(tmp_base, "ghost") is False


class TestPersistence:
    def test_groups_persist_across_loads(self, tmp_base):
        add_to_group(tmp_base, "prod", "api")
        add_to_group(tmp_base, "prod", "worker")
        loaded = load_groups(tmp_base)
        assert "prod" in loaded
        assert sorted(loaded["prod"]) == ["api", "worker"]
