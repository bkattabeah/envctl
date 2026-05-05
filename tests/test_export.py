"""Tests for envctl.export module."""

import json
import pytest
from envctl.export import export_env, import_dotenv


SAMPLE = {"DATABASE_URL": "postgres://localhost/db", "DEBUG": "true", "PORT": "8080"}


class TestExportDotenv:
    def test_basic_output(self):
        result = export_env(SAMPLE, fmt="dotenv")
        assert 'DATABASE_URL="postgres://localhost/db"' in result
        assert 'DEBUG="true"' in result
        assert 'PORT="8080"' in result

    def test_sorted_keys(self):
        result = export_env(SAMPLE, fmt="dotenv")
        lines = [l for l in result.splitlines() if l]
        keys = [l.split("=")[0] for l in lines]
        assert keys == sorted(keys)

    def test_escapes_double_quotes(self):
        result = export_env({"MSG": 'say "hello"'}, fmt="dotenv")
        assert 'MSG="say \\"hello\\""' in result

    def test_trailing_newline(self):
        result = export_env(SAMPLE, fmt="dotenv")
        assert result.endswith("\n")

    def test_empty(self):
        assert export_env({}, fmt="dotenv") == ""


class TestExportJson:
    def test_valid_json(self):
        result = export_env(SAMPLE, fmt="json")
        parsed = json.loads(result)
        assert parsed == SAMPLE

    def test_sorted_keys(self):
        result = export_env(SAMPLE, fmt="json")
        parsed = json.loads(result)
        assert list(parsed.keys()) == sorted(parsed.keys())


class TestExportShell:
    def test_shebang(self):
        result = export_env(SAMPLE, fmt="shell")
        assert result.startswith("#!/usr/bin/env sh")

    def test_export_prefix(self):
        result = export_env(SAMPLE, fmt="shell")
        assert "export PORT='8080'" in result

    def test_escapes_single_quotes(self):
        result = export_env({"VAR": "it's alive"}, fmt="shell")
        assert "export VAR='it'\"'\"'s alive'" in result


class TestImportDotenv:
    def test_basic(self):
        text = 'FOO=bar\nBAZ="qux"\n'
        env = import_dotenv(text)
        assert env == {"FOO": "bar", "BAZ": "qux"}

    def test_skips_comments(self):
        text = "# comment\nKEY=value\n"
        env = import_dotenv(text)
        assert "#" not in str(env)
        assert env["KEY"] == "value"

    def test_skips_blank_lines(self):
        text = "\n\nA=1\n\nB=2\n"
        env = import_dotenv(text)
        assert env == {"A": "1", "B": "2"}

    def test_strips_single_quotes(self):
        env = import_dotenv("SECRET='mypassword'")
        assert env["SECRET"] == "mypassword"

    def test_unsupported_format_raises(self):
        with pytest.raises(ValueError):
            export_env(SAMPLE, fmt="xml")  # type: ignore
