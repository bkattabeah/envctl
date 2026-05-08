"""Mask sensitive environment variable values based on key patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_DEFAULT_PATTERNS = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*PASSWD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE_KEY.*",
    r".*CREDENTIALS.*",
]

MASK_PLACEHOLDER = "***"


@dataclass
class MaskResult:
    target: str
    original: Dict[str, str]
    masked: Dict[str, str]
    masked_keys: List[str] = field(default_factory=list)

    def summary(self) -> str:
        n = len(self.masked_keys)
        if n == 0:
            return f"No keys masked in '{self.target}'."
        keys = ", ".join(sorted(self.masked_keys))
        return f"{n} key(s) masked in '{self.target}': {keys}"


def _compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def is_sensitive(key: str, patterns: Optional[List[str]] = None) -> bool:
    """Return True if the key matches any sensitive pattern."""
    compiled = _compile_patterns(patterns or _DEFAULT_PATTERNS)
    return any(p.fullmatch(key) for p in compiled)


def mask_env(
    target: str,
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
    placeholder: str = MASK_PLACEHOLDER,
) -> MaskResult:
    """Return a MaskResult with sensitive values replaced by placeholder."""
    compiled = _compile_patterns(patterns or _DEFAULT_PATTERNS)
    masked: Dict[str, str] = {}
    masked_keys: List[str] = []

    for key, value in env.items():
        if any(p.fullmatch(key) for p in compiled):
            masked[key] = placeholder
            masked_keys.append(key)
        else:
            masked[key] = value

    return MaskResult(
        target=target,
        original=dict(env),
        masked=masked,
        masked_keys=sorted(masked_keys),
    )
