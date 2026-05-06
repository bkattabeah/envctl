"""Lint environment variable keys and values for common issues."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

_VALID_KEY_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_SECRETS_PATTERN = re.compile(r'(password|secret|token|key|api_key|passwd)', re.IGNORECASE)
_WHITESPACE_RE = re.compile(r'^\s|\s$')


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str  # 'error' | 'warning'

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == 'error']

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == 'warning']

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        if not self.issues:
            return "OK — no lint issues found."
        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")
        return "Lint: " + ", ".join(parts) + "."


def lint_env(env: Dict[str, str]) -> LintResult:
    """Run all lint checks against an env dict and return a LintResult."""
    result = LintResult()

    for key, value in env.items():
        # Key naming convention
        if not _VALID_KEY_RE.match(key):
            result.issues.append(LintIssue(
                key=key,
                message="Key should be UPPER_SNAKE_CASE and start with a letter.",
                severity='error',
            ))

        # Empty value
        if value == '':
            result.issues.append(LintIssue(
                key=key,
                message="Value is empty.",
                severity='warning',
            ))

        # Leading/trailing whitespace in value
        if _WHITESPACE_RE.search(value):
            result.issues.append(LintIssue(
                key=key,
                message="Value has leading or trailing whitespace.",
                severity='warning',
            ))

        # Plaintext secrets heuristic
        if _SECRETS_PATTERN.search(key) and len(value) < 8 and value != '':
            result.issues.append(LintIssue(
                key=key,
                message="Key looks like a secret but value is suspiciously short.",
                severity='warning',
            ))

    return result
