"""Tests for envctl.alias."""

import pytest
from pathlib import Path
from envctl.alias import (
    add_alias,
    remove_alias,
    resolve_alias,
    list_aliases,
    load_aliases,
    save_aliases,
)


@pytest.fixture
def tmp_base(tmp_path):
    return str(tmp_path)


class TestAddAlias:
    def test_returns_true_for_new_alias(self, tmp_base):
        assert add_alias(tmp_base, "prod", "production") is True

    def test_returns_false_for_update(self, tmp_base):
        add_alias(tmp_base, "prod", "production")
        assert add_alias(tmp_base, "prod", "prod-v2") is False

    def test_alias_persisted(self, tmp_base):
        add_alias(tmp_base, "stg", "staging")
        aliases = load_aliases(tmp_base)
        assert aliases["stg"] == "staging"

    def test_multiple_aliases(self, tmp_base):
        add_alias(tmp_base, "p", "production")
        add_alias(tmp_base, "s", "staging")
        aliases = load_aliases(tmp_base)
        assert len(aliases) == 2


class TestRemoveAlias:
    def test_returns_true_when_found(self, tmp_base):
        add_alias(tmp_base, "dev", "development")
        assert remove_alias(tmp_base, "dev") is True

    def test_returns_false_when_missing(self, tmp_base):
        assert remove_alias(tmp_base, "ghost") is False

    def test_alias_gone_after_removal(self, tmp_base):
        add_alias(tmp_base, "dev", "development")
        remove_alias(tmp_base, "dev")
        assert "dev" not in load_aliases(tmp_base)


class TestResolveAlias:
    def test_resolves_known_alias(self, tmp_base):
        add_alias(tmp_base, "p", "production")
        assert resolve_alias(tmp_base, "p") == "production"

    def test_returns_name_when_not_alias(self, tmp_base):
        assert resolve_alias(tmp_base, "production") == "production"


class TestListAliases:
    def test_empty_when_none(self, tmp_base):
        assert list_aliases(tmp_base) == []

    def test_sorted_output(self, tmp_base):
        add_alias(tmp_base, "z", "zzz")
        add_alias(tmp_base, "a", "aaa")
        pairs = list_aliases(tmp_base)
        assert pairs[0][0] == "a"
        assert pairs[1][0] == "z"

    def test_returns_tuples(self, tmp_base):
        add_alias(tmp_base, "x", "xray")
        pairs = list_aliases(tmp_base)
        assert pairs == [("x", "xray")]


class TestSaveAndLoad:
    def test_roundtrip(self, tmp_base):
        data = {"a": "alpha", "b": "beta"}
        save_aliases(tmp_base, data)
        assert load_aliases(tmp_base) == data

    def test_creates_directory(self, tmp_base):
        save_aliases(tmp_base, {"k": "v"})
        assert Path(tmp_base, ".envctl", "aliases.json").exists()
