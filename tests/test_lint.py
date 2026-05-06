"""Tests for envctl.lint and envctl.lint_render."""

from __future__ import annotations

import pytest
from envctl.lint import LintIssue, LintResult, lint_env
from envctl.lint_render import render_lint_result


class TestLintResult:
    def test_passed_with_no_issues(self):
        r = LintResult()
        assert r.passed is True

    def test_failed_with_error(self):
        r = LintResult(issues=[LintIssue('bad', 'msg', 'error')])
        assert r.passed is False

    def test_passed_with_only_warnings(self):
        r = LintResult(issues=[LintIssue('KEY', 'msg', 'warning')])
        assert r.passed is True

    def test_summary_ok(self):
        r = LintResult()
        assert 'OK' in r.summary()

    def test_summary_counts(self):
        r = LintResult(issues=[
            LintIssue('A', 'e', 'error'),
            LintIssue('B', 'w', 'warning'),
        ])
        s = r.summary()
        assert '1 error' in s
        assert '1 warning' in s

    def test_errors_property(self):
        r = LintResult(issues=[
            LintIssue('A', 'e', 'error'),
            LintIssue('B', 'w', 'warning'),
        ])
        assert len(r.errors) == 1
        assert len(r.warnings) == 1


class TestLintEnv:
    def test_clean_env_passes(self):
        result = lint_env({'APP_NAME': 'myapp', 'PORT': '8080'})
        assert result.passed
        assert result.issues == []

    def test_lowercase_key_is_error(self):
        result = lint_env({'app_name': 'myapp'})
        errors = [i for i in result.errors if i.key == 'app_name']
        assert errors, 'expected an error for lowercase key'

    def test_mixed_case_key_is_error(self):
        result = lint_env({'AppName': 'x'})
        assert any(i.severity == 'error' for i in result.issues)

    def test_empty_value_is_warning(self):
        result = lint_env({'MY_KEY': ''})
        warnings = [i for i in result.warnings if i.key == 'MY_KEY']
        assert warnings

    def test_leading_whitespace_is_warning(self):
        result = lint_env({'MY_KEY': ' value'})
        assert any('whitespace' in i.message for i in result.warnings)

    def test_trailing_whitespace_is_warning(self):
        result = lint_env({'MY_KEY': 'value '})
        assert any('whitespace' in i.message for i in result.warnings)

    def test_short_secret_value_is_warning(self):
        result = lint_env({'API_KEY': 'abc'})
        assert any('secret' in i.message.lower() for i in result.warnings)

    def test_long_secret_value_no_warning(self):
        result = lint_env({'API_KEY': 'supersecretvalue123'})
        secret_warnings = [i for i in result.warnings if 'secret' in i.message.lower()]
        assert not secret_warnings

    def test_key_must_start_with_letter(self):
        result = lint_env({'1KEY': 'val'})
        assert any(i.severity == 'error' for i in result.issues)


class TestRenderLintResult:
    def test_ok_message_on_clean(self):
        result = lint_env({'GOOD_KEY': 'value'})
        output = render_lint_result(result, color=False)
        assert 'OK' in output

    def test_error_tag_present(self):
        result = LintResult(issues=[LintIssue('bad_key', 'bad name', 'error')])
        output = render_lint_result(result, color=False)
        assert '[ERROR]' in output

    def test_warning_tag_present(self):
        result = LintResult(issues=[LintIssue('MY_KEY', 'empty', 'warning')])
        output = render_lint_result(result, color=False)
        assert '[WARNING]' in output

    def test_failed_verdict_on_error(self):
        result = LintResult(issues=[LintIssue('bad', 'msg', 'error')])
        output = render_lint_result(result, color=False)
        assert 'Failed' in output

    def test_passed_verdict_on_warnings_only(self):
        result = LintResult(issues=[LintIssue('MY_KEY', 'msg', 'warning')])
        output = render_lint_result(result, color=False)
        assert 'Passed' in output
