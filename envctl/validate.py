"""Validation rules for environment variable keys and values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_KEY_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')
_WARN_PREFIXES = ("SECRET_", "TOKEN_", "PASSWORD_", "KEY_", "PRIVATE_")


@dataclass
class ValidationIssue:
    key: str
    level: str          # 'error' | 'warning'
    message: str


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.level == "warning"]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")
        return ", ".join(parts) if parts else "OK"


def validate_env(env: Dict[str, str], strict: bool = False) -> ValidationResult:
    """Validate environment variable keys and values.

    Args:
        env: Mapping of variable names to values.
        strict: If True, warnings are promoted to errors.

    Returns:
        A ValidationResult with any discovered issues.
    """
    result = ValidationResult()

    for key, value in env.items():
        # Key format check
        if not _KEY_RE.match(key):
            result.issues.append(ValidationIssue(
                key=key,
                level="error",
                message=(
                    f"Key '{key}' is not valid POSIX format "
                    "(must match [A-Z_][A-Z0-9_]*)"
                ),
            ))

        # Empty value warning
        if value == "":
            level = "error" if strict else "warning"
            result.issues.append(ValidationIssue(
                key=key,
                level=level,
                message=f"Key '{key}' has an empty value",
            ))

        # Sensitive key with placeholder-style value
        upper = key.upper()
        if any(upper.startswith(p) for p in _WARN_PREFIXES):
            lower_val = value.lower()
            if lower_val in ("changeme", "placeholder", "todo", "fixme", "xxx"):
                level = "error" if strict else "warning"
                result.issues.append(ValidationIssue(
                    key=key,
                    level=level,
                    message=(
                        f"Key '{key}' looks sensitive but has a "
                        f"placeholder value '{value}'"
                    ),
                ))

    return result
