"""Tests for envctl.alias_render."""

import pytest
from envctl.alias_render import (
    render_alias_list,
    render_alias_added,
    render_alias_removed,
    render_alias_resolved,
)


class TestRenderAliasList:
    def test_empty_message(self):
        result = render_alias_list([])
        assert "No aliases" in result

    def test_contains_alias_name(self):
        result = render_alias_list([("prod", "production")])
        assert "prod" in result

    def test_contains_target_name(self):
        result = render_alias_list([("prod", "production")])
        assert "production" in result

    def test_contains_arrow(self):
        result = render_alias_list([("prod", "production")])
        assert "->" in result

    def test_multiple_entries(self):
        pairs = [("a", "alpha"), ("b", "beta")]
        result = render_alias_list(pairs)
        assert "alpha" in result
        assert "beta" in result


class TestRenderAliasAdded:
    def test_created_label_for_new(self):
        result = render_alias_added("dev", "development", is_new=True)
        assert "Created" in result

    def test_updated_label_for_existing(self):
        result = render_alias_added("dev", "development", is_new=False)
        assert "Updated" in result

    def test_contains_alias(self):
        result = render_alias_added("dev", "development", is_new=True)
        assert "dev" in result

    def test_contains_target(self):
        result = render_alias_added("dev", "development", is_new=True)
        assert "development" in result


class TestRenderAliasRemoved:
    def test_removed_label_when_found(self):
        result = render_alias_removed("dev", found=True)
        assert "Removed" in result

    def test_not_found_message(self):
        result = render_alias_removed("ghost", found=False)
        assert "not found" in result

    def test_alias_name_in_output(self):
        result = render_alias_removed("dev", found=True)
        assert "dev" in result


class TestRenderAliasResolved:
    def test_shows_target_when_alias(self):
        result = render_alias_resolved("p", "production")
        assert "production" in result

    def test_no_alias_note_when_same(self):
        result = render_alias_resolved("production", "production")
        assert "no alias" in result

    def test_arrow_present_when_resolved(self):
        result = render_alias_resolved("p", "production")
        assert "resolves to" in result
