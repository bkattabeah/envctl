"""Tests for envctl.schema and envctl.schema_render."""

import pytest

from envctl.schema import (
    SchemaField,
    SchemaResult,
    save_schema,
    load_schema,
    validate_schema,
)
from envctl.schema_render import (
    render_schema_result,
    render_schema_saved,
    render_schema_not_found,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_base(tmp_path):
    return str(tmp_path)


@pytest.fixture()
def simple_fields():
    return [
        SchemaField(key="APP_ENV", required=True, allowed_values=["dev", "staging", "prod"]),
        SchemaField(key="PORT", required=True, pattern=r"\d+"),
        SchemaField(key="DEBUG", required=False),
    ]


# ---------------------------------------------------------------------------
# SchemaResult
# ---------------------------------------------------------------------------

class TestSchemaResult:
    def test_is_valid_when_no_issues(self):
        r = SchemaResult(target="dev")
        assert r.is_valid

    def test_invalid_with_missing_required(self):
        r = SchemaResult(target="dev", missing_required=["SECRET"])
        assert not r.is_valid

    def test_invalid_with_pattern_violation(self):
        r = SchemaResult(target="dev", pattern_violations={"PORT": "abc"})
        assert not r.is_valid

    def test_summary_ok(self):
        r = SchemaResult(target="prod")
        assert "OK" in r.summary()
        assert "prod" in r.summary()

    def test_summary_failed_lists_reasons(self):
        r = SchemaResult(
            target="prod",
            missing_required=["DB_URL"],
            pattern_violations={"PORT": "xyz"},
        )
        s = r.summary()
        assert "FAILED" in s
        assert "missing" in s
        assert "pattern" in s


# ---------------------------------------------------------------------------
# save / load
# ---------------------------------------------------------------------------

class TestSaveAndLoad:
    def test_roundtrip(self, tmp_base, simple_fields):
        save_schema(tmp_base, "base", simple_fields)
        loaded = load_schema(tmp_base, "base")
        assert [f.key for f in loaded] == [f.key for f in simple_fields]

    def test_required_flag_preserved(self, tmp_base, simple_fields):
        save_schema(tmp_base, "base", simple_fields)
        loaded = {f.key: f for f in load_schema(tmp_base, "base")}
        assert loaded["DEBUG"].required is False

    def test_allowed_values_preserved(self, tmp_base, simple_fields):
        save_schema(tmp_base, "base", simple_fields)
        loaded = {f.key: f for f in load_schema(tmp_base, "base")}
        assert loaded["APP_ENV"].allowed_values == ["dev", "staging", "prod"]

    def test_missing_schema_returns_empty(self, tmp_base):
        assert load_schema(tmp_base, "nonexistent") == []


# ---------------------------------------------------------------------------
# validate_schema
# ---------------------------------------------------------------------------

class TestValidateSchema:
    def test_valid_env_passes(self, simple_fields):
        env = {"APP_ENV": "dev", "PORT": "8080"}
        result = validate_schema("dev", env, simple_fields)
        assert result.is_valid

    def test_missing_required_key(self, simple_fields):
        env = {"APP_ENV": "dev"}
        result = validate_schema("dev", env, simple_fields)
        assert "PORT" in result.missing_required

    def test_pattern_violation(self, simple_fields):
        env = {"APP_ENV": "dev", "PORT": "not-a-number"}
        result = validate_schema("dev", env, simple_fields)
        assert "PORT" in result.pattern_violations

    def test_disallowed_value(self, simple_fields):
        env = {"APP_ENV": "local", "PORT": "3000"}
        result = validate_schema("dev", env, simple_fields)
        assert "APP_ENV" in result.disallowed_values

    def test_optional_key_absence_is_ok(self, simple_fields):
        env = {"APP_ENV": "prod", "PORT": "443"}
        result = validate_schema("prod", env, simple_fields)
        assert result.is_valid
        assert "DEBUG" not in result.missing_required

    def test_strict_mode_flags_unknown_keys(self, simple_fields):
        env = {"APP_ENV": "dev", "PORT": "8080", "EXTRA": "surprise"}
        result = validate_schema("dev", env, simple_fields, strict=True)
        assert "EXTRA" in result.unknown_keys

    def test_non_strict_ignores_unknown_keys(self, simple_fields):
        env = {"APP_ENV": "dev", "PORT": "8080", "EXTRA": "surprise"}
        result = validate_schema("dev", env, simple_fields, strict=False)
        assert result.unknown_keys == []


# ---------------------------------------------------------------------------
# schema_render
# ---------------------------------------------------------------------------

class TestRenderSchemaResult:
    def test_contains_target_name(self):
        r = SchemaResult(target="staging")
        out = render_schema_result(r, color=False)
        assert "staging" in out

    def test_shows_passed_when_valid(self):
        r = SchemaResult(target="dev")
        out = render_schema_result(r, color=False)
        assert "passed" in out.lower()

    def test_shows_missing_keys(self):
        r = SchemaResult(target="dev", missing_required=["SECRET_KEY"])
        out = render_schema_result(r, color=False)
        assert "SECRET_KEY" in out

    def test_shows_pattern_violations(self):
        r = SchemaResult(target="dev", pattern_violations={"PORT": "abc"})
        out = render_schema_result(r, color=False)
        assert "PORT" in out
        assert "abc" in out

    def test_shows_unknown_keys_in_strict(self):
        r = SchemaResult(target="dev", unknown_keys=["ROGUE"])
        out = render_schema_result(r, color=False)
        assert "ROGUE" in out

    def test_render_saved(self):
        out = render_schema_saved("base", 5, color=False)
        assert "base" in out
        assert "5" in out

    def test_render_not_found(self):
        out = render_schema_not_found("missing", color=False)
        assert "missing" in out
