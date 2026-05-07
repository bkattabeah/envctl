"""Tests for envctl.tag and envctl.tag_render."""

from __future__ import annotations

import pytest

from envctl.tag import (
    add_tag,
    find_targets_by_tag,
    list_all_tags,
    load_tags,
    remove_tag,
    save_tags,
)
from envctl.tag_render import (
    render_all_tags,
    render_find_by_tag,
    render_tag_added,
    render_tag_list,
    render_tag_removed,
)


@pytest.fixture()
def tmp_base(tmp_path):
    return str(tmp_path)


class TestSaveAndLoad:
    def test_roundtrip(self, tmp_base):
        save_tags(tmp_base, "prod", ["live", "critical"])
        assert load_tags(tmp_base, "prod") == ["critical", "live"]

    def test_deduplicates_on_save(self, tmp_base):
        save_tags(tmp_base, "staging", ["beta", "beta", "qa"])
        assert load_tags(tmp_base, "staging") == ["beta", "qa"]

    def test_missing_target_returns_empty(self, tmp_base):
        assert load_tags(tmp_base, "nonexistent") == []


class TestAddRemove:
    def test_add_tag_persists(self, tmp_base):
        result = add_tag(tmp_base, "dev", "local")
        assert "local" in result
        assert load_tags(tmp_base, "dev") == ["local"]

    def test_add_tag_accumulates(self, tmp_base):
        add_tag(tmp_base, "dev", "local")
        result = add_tag(tmp_base, "dev", "debug")
        assert sorted(result) == ["debug", "local"]

    def test_remove_tag_persists(self, tmp_base):
        save_tags(tmp_base, "dev", ["local", "debug"])
        result = remove_tag(tmp_base, "dev", "debug")
        assert result == ["local"]

    def test_remove_nonexistent_tag_is_noop(self, tmp_base):
        save_tags(tmp_base, "dev", ["local"])
        result = remove_tag(tmp_base, "dev", "ghost")
        assert result == ["local"]


class TestFindAndList:
    def test_find_targets_by_tag(self, tmp_base):
        save_tags(tmp_base, "prod", ["live"])
        save_tags(tmp_base, "staging", ["live", "qa"])
        save_tags(tmp_base, "dev", ["local"])
        assert find_targets_by_tag(tmp_base, "live") == ["prod", "staging"]

    def test_find_returns_empty_when_no_match(self, tmp_base):
        save_tags(tmp_base, "dev", ["local"])
        assert find_targets_by_tag(tmp_base, "missing") == []

    def test_list_all_tags_returns_mapping(self, tmp_base):
        save_tags(tmp_base, "prod", ["live"])
        save_tags(tmp_base, "dev", ["local"])
        result = list_all_tags(tmp_base)
        assert result["prod"] == ["live"]
        assert result["dev"] == ["local"]

    def test_list_all_tags_empty_base(self, tmp_base):
        assert list_all_tags(tmp_base) == {}


class TestTagRender:
    def test_render_tag_list_with_tags(self):
        out = render_tag_list("prod", ["live", "critical"])
        assert "prod" in out
        assert "live" in out

    def test_render_tag_list_no_tags(self):
        out = render_tag_list("dev", [])
        assert "No tags" in out

    def test_render_all_tags_shows_targets(self):
        out = render_all_tags({"prod": ["live"], "dev": ["local"]})
        assert "prod" in out
        assert "dev" in out

    def test_render_all_tags_empty(self):
        out = render_all_tags({})
        assert "No tags" in out

    def test_render_tag_added(self):
        out = render_tag_added("prod", "live", ["live"])
        assert "live" in out
        assert "prod" in out

    def test_render_tag_removed(self):
        out = render_tag_removed("prod", "live", [])
        assert "live" in out

    def test_render_find_by_tag_with_results(self):
        out = render_find_by_tag("live", ["prod", "staging"])
        assert "prod" in out
        assert "staging" in out

    def test_render_find_by_tag_no_results(self):
        out = render_find_by_tag("ghost", [])
        assert "No targets" in out
