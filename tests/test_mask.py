"""Tests for envctl.mask module."""

import pytest
from envctl.mask import (
    MaskResult,
    MASK_PLACEHOLDER,
    is_sensitive,
    mask_env,
)


class TestIsSensitive:
    def test_detects_secret(self):
        assert is_sensitive("APP_SECRET") is True

    def test_detects_password(self):
        assert is_sensitive("DB_PASSWORD") is True

    def test_detects_token(self):
        assert is_sensitive("GITHUB_TOKEN") is True

    def test_detects_api_key(self):
        assert is_sensitive("STRIPE_API_KEY") is True

    def test_safe_key_not_sensitive(self):
        assert is_sensitive("APP_ENV") is False

    def test_safe_key_port_not_sensitive(self):
        assert is_sensitive("PORT") is False

    def test_custom_pattern_matches(self):
        assert is_sensitive("MY_CUSTOM_CRED", patterns=[r".*CRED.*"]) is True

    def test_custom_pattern_no_match(self):
        assert is_sensitive("APP_SECRET", patterns=[r".*CRED.*"]) is False

    def test_case_insensitive(self):
        assert is_sensitive("app_secret") is True


class TestMaskEnv:
    def _env(self):
        return {
            "APP_ENV": "production",
            "DB_PASSWORD": "hunter2",
            "GITHUB_TOKEN": "ghp_abc123",
            "PORT": "8080",
            "API_KEY": "key-xyz",
        }

    def test_sensitive_values_replaced(self):
        result = mask_env("prod", self._env())
        assert result.masked["DB_PASSWORD"] == MASK_PLACEHOLDER
        assert result.masked["GITHUB_TOKEN"] == MASK_PLACEHOLDER
        assert result.masked["API_KEY"] == MASK_PLACEHOLDER

    def test_safe_values_unchanged(self):
        result = mask_env("prod", self._env())
        assert result.masked["APP_ENV"] == "production"
        assert result.masked["PORT"] == "8080"

    def test_masked_keys_list(self):
        result = mask_env("prod", self._env())
        assert "DB_PASSWORD" in result.masked_keys
        assert "GITHUB_TOKEN" in result.masked_keys
        assert "APP_ENV" not in result.masked_keys

    def test_original_env_preserved(self):
        result = mask_env("prod", self._env())
        assert result.original["DB_PASSWORD"] == "hunter2"

    def test_target_stored(self):
        result = mask_env("staging", {})
        assert result.target == "staging"

    def test_empty_env_returns_empty_masked(self):
        result = mask_env("dev", {})
        assert result.masked == {}
        assert result.masked_keys == []

    def test_custom_placeholder(self):
        result = mask_env("prod", {"DB_PASSWORD": "secret"}, placeholder="<hidden>")
        assert result.masked["DB_PASSWORD"] == "<hidden>"

    def test_summary_no_masked(self):
        result = mask_env("dev", {"PORT": "3000"})
        assert "No keys masked" in result.summary()

    def test_summary_with_masked(self):
        result = mask_env("prod", {"DB_PASSWORD": "x"})
        assert "1 key(s) masked" in result.summary()
        assert "DB_PASSWORD" in result.summary()

    def test_masked_keys_are_sorted(self):
        env = {"Z_TOKEN": "a", "A_SECRET": "b"}
        result = mask_env("prod", env)
        assert result.masked_keys == sorted(result.masked_keys)
