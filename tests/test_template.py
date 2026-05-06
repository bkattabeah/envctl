"""Tests for envctl.template module."""

from __future__ import annotations

import pytest

from envctl.template import TemplateResult, render_template, render_template_for_target


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_ENV = {
    "HOST": "localhost",
    "PORT": "5432",
    "DB_NAME": "mydb",
}


# ---------------------------------------------------------------------------
# TemplateResult
# ---------------------------------------------------------------------------


class TestTemplateResult:
    def test_is_complete_when_no_missing(self):
        result = TemplateResult(rendered="ok", missing_vars=[], used_vars=["HOST"])
        assert result.is_complete is True

    def test_not_complete_when_missing(self):
        result = TemplateResult(rendered="x", missing_vars=["SECRET"], used_vars=[])
        assert result.is_complete is False

    def test_summary_shows_resolved(self):
        result = TemplateResult(rendered="ok", missing_vars=[], used_vars=["HOST", "PORT"])
        assert "HOST" in result.summary()
        assert "PORT" in result.summary()

    def test_summary_shows_missing(self):
        result = TemplateResult(rendered="x", missing_vars=["SECRET"], used_vars=[])
        assert "SECRET" in result.summary()

    def test_summary_no_placeholders_message(self):
        result = TemplateResult(rendered="hello", missing_vars=[], used_vars=[])
        assert "No placeholders" in result.summary()


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------


class TestRenderTemplate:
    def test_basic_substitution(self):
        result = render_template("host={{HOST}}", SAMPLE_ENV)
        assert result.rendered == "host=localhost"

    def test_multiple_placeholders(self):
        result = render_template("{{HOST}}:{{PORT}}/{{DB_NAME}}", SAMPLE_ENV)
        assert result.rendered == "localhost:5432/mydb"

    def test_used_vars_populated(self):
        result = render_template("{{HOST}}:{{PORT}}", SAMPLE_ENV)
        assert set(result.used_vars) == {"HOST", "PORT"}

    def test_missing_var_left_in_place(self):
        result = render_template("{{HOST}}:{{SECRET}}", SAMPLE_ENV)
        assert "{{SECRET}}" in result.rendered

    def test_missing_vars_populated(self):
        result = render_template("{{MISSING_A}} and {{MISSING_B}}", SAMPLE_ENV)
        assert "MISSING_A" in result.missing_vars
        assert "MISSING_B" in result.missing_vars

    def test_duplicate_placeholder_counted_once(self):
        result = render_template("{{HOST}} {{HOST}}", SAMPLE_ENV)
        assert result.used_vars.count("HOST") == 1

    def test_no_placeholders(self):
        result = render_template("plain text", SAMPLE_ENV)
        assert result.rendered == "plain text"
        assert result.used_vars == []
        assert result.missing_vars == []

    def test_whitespace_in_placeholder(self):
        result = render_template("{{ HOST }}", SAMPLE_ENV)
        assert result.rendered == "localhost"


# ---------------------------------------------------------------------------
# render_template_for_target (integration with EnvStore)
# ---------------------------------------------------------------------------


def test_render_template_for_target(tmp_path):
    from envctl.env_store import EnvStore

    store = EnvStore(base_dir=str(tmp_path))
    store.save("prod", {"APP_HOST": "prod.example.com", "APP_PORT": "443"})

    result = render_template_for_target(
        store, "prod", "https://{{APP_HOST}}:{{APP_PORT}}/api"
    )
    assert result.rendered == "https://prod.example.com:443/api"
    assert result.is_complete is True
