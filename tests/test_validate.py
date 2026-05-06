"""Tests for envctl.validate module."""

import pytest

from envctl.validate import validate_env, ValidationIssue, ValidationResult


class TestValidationResult:
    def test_is_valid_no_issues(self):
        result = ValidationResult()
        assert result.is_valid is True

    def test_is_valid_with_error(self):
        result = ValidationResult(issues=[
            ValidationIssue(key="X", level="error", message="bad")
        ])
        assert result.is_valid is False

    def test_is_valid_warning_only(self):
        result = ValidationResult(issues=[
            ValidationIssue(key="X", level="warning", message="meh")
        ])
        assert result.is_valid is True

    def test_summary_ok(self):
        assert ValidationResult().summary() == "OK"

    def test_summary_mixed(self):
        result = ValidationResult(issues=[
            ValidationIssue(key="A", level="error", message="e"),
            ValidationIssue(key="B", level="warning", message="w"),
            ValidationIssue(key="C", level="warning", message="w2"),
        ])
        assert "1 error" in result.summary()
        assert "2 warning" in result.summary()


class TestValidateEnv:
    def test_valid_env_passes(self):
        result = validate_env({"APP_HOST": "localhost", "APP_PORT": "8080"})
        assert result.is_valid
        assert result.issues == []

    def test_lowercase_key_is_error(self):
        result = validate_env({"app_host": "localhost"})
        errors = result.errors
        assert len(errors) == 1
        assert "app_host" in errors[0].message

    def test_key_with_leading_digit_is_error(self):
        result = validate_env({"1INVALID": "val"})
        assert not result.is_valid

    def test_empty_value_is_warning_by_default(self):
        result = validate_env({"MY_VAR": ""})
        assert result.is_valid          # warnings don't fail
        assert len(result.warnings) == 1
        assert "empty" in result.warnings[0].message

    def test_empty_value_is_error_in_strict(self):
        result = validate_env({"MY_VAR": ""}, strict=True)
        assert not result.is_valid
        assert len(result.errors) == 1

    def test_sensitive_placeholder_is_warning(self):
        result = validate_env({"SECRET_KEY": "changeme"})
        assert result.is_valid
        assert any("placeholder" in w.message for w in result.warnings)

    def test_sensitive_placeholder_strict_is_error(self):
        result = validate_env({"TOKEN_VALUE": "placeholder"}, strict=True)
        assert not result.is_valid
        assert any(i.level == "error" for i in result.issues)

    def test_multiple_issues_collected(self):
        env = {
            "bad key": "",        # invalid format + empty value
            "GOOD": "ok",
        }
        result = validate_env(env)
        # At minimum the bad key format error should be present
        assert len(result.errors) >= 1

    def test_non_sensitive_key_no_placeholder_warning(self):
        result = validate_env({"APP_NAME": "changeme"})
        # 'APP_NAME' doesn't start with a sensitive prefix
        assert not any("placeholder" in i.message for i in result.issues)
