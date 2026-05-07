"""Tests for envctl.scope."""

import pytest

from envctl.scope import (
    add_to_scope,
    delete_scope,
    list_all_scopes,
    list_scope_members,
    remove_from_scope,
    targets_for_scopes,
)


@pytest.fixture()
def tmp_base(tmp_path):
    return str(tmp_path)


class TestAddAndList:
    def test_add_creates_scope(self, tmp_base):
        add_to_scope(tmp_base, "prod", "api")
        assert "api" in list_scope_members(tmp_base, "prod")

    def test_add_is_idempotent(self, tmp_base):
        add_to_scope(tmp_base, "prod", "api")
        add_to_scope(tmp_base, "prod", "api")
        assert list_scope_members(tmp_base, "prod").count("api") == 1

    def test_members_are_sorted(self, tmp_base):
        add_to_scope(tmp_base, "prod", "worker")
        add_to_scope(tmp_base, "prod", "api")
        assert list_scope_members(tmp_base, "prod") == ["api", "worker"]

    def test_unknown_scope_returns_empty(self, tmp_base):
        assert list_scope_members(tmp_base, "nope") == []


class TestRemoveFromScope:
    def test_removes_existing_target(self, tmp_base):
        add_to_scope(tmp_base, "staging", "web")
        result = remove_from_scope(tmp_base, "staging", "web")
        assert result is True
        assert "web" not in list_scope_members(tmp_base, "staging")

    def test_returns_false_when_not_present(self, tmp_base):
        add_to_scope(tmp_base, "staging", "web")
        assert remove_from_scope(tmp_base, "staging", "db") is False

    def test_scope_deleted_when_empty(self, tmp_base):
        add_to_scope(tmp_base, "staging", "web")
        remove_from_scope(tmp_base, "staging", "web")
        assert "staging" not in list_all_scopes(tmp_base)


class TestDeleteScope:
    def test_deletes_existing_scope(self, tmp_base):
        add_to_scope(tmp_base, "dev", "api")
        result = delete_scope(tmp_base, "dev")
        assert result is True
        assert list_scope_members(tmp_base, "dev") == []

    def test_returns_false_for_missing_scope(self, tmp_base):
        assert delete_scope(tmp_base, "ghost") is False


class TestTargetsForScopes:
    def test_combines_multiple_scopes(self, tmp_base):
        add_to_scope(tmp_base, "prod", "api")
        add_to_scope(tmp_base, "prod", "worker")
        add_to_scope(tmp_base, "infra", "db")
        result = targets_for_scopes(tmp_base, ["prod", "infra"])
        assert result == ["api", "db", "worker"]

    def test_deduplicates_across_scopes(self, tmp_base):
        add_to_scope(tmp_base, "a", "shared")
        add_to_scope(tmp_base, "b", "shared")
        result = targets_for_scopes(tmp_base, ["a", "b"])
        assert result.count("shared") == 1

    def test_empty_when_no_scopes_match(self, tmp_base):
        assert targets_for_scopes(tmp_base, ["nonexistent"]) == []

    def test_result_is_sorted(self, tmp_base):
        add_to_scope(tmp_base, "x", "zz")
        add_to_scope(tmp_base, "x", "aa")
        result = targets_for_scopes(tmp_base, ["x"])
        assert result == sorted(result)
