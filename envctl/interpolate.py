"""Interpolate environment variable references within a target's values.

Supports ${VAR} and $VAR syntax for self-referential substitution within
a single target's key-value pairs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolateResult:
    target: str
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved_keys: List[str] = field(default_factory=list)
    substitution_count: int = 0

    def is_complete(self) -> bool:
        return len(self.unresolved_keys) == 0

    def summary(self) -> str:
        parts = [f"target={self.target}"]
        parts.append(f"substitutions={self.substitution_count}")
        if self.unresolved_keys:
            parts.append(f"unresolved={','.join(sorted(self.unresolved_keys))}")
        else:
            parts.append("status=ok")
        return " ".join(parts)


def _substitute(value: str, env: Dict[str, str]) -> tuple[str, int]:
    """Replace all variable references in value using env. Returns (new_value, count)."""
    count = 0

    def replacer(m: re.Match) -> str:
        nonlocal count
        var = m.group(1) or m.group(2)
        if var in env:
            count += 1
            return env[var]
        return m.group(0)

    result = _REF_RE.sub(replacer, value)
    return result, count


def interpolate_target(
    target: str,
    env: Dict[str, str],
    max_passes: int = 5,
) -> InterpolateResult:
    """Resolve variable references within env values iteratively.

    Performs up to max_passes expansion passes to handle chained references.
    Keys whose values still contain unresolved references are reported.
    """
    current = dict(env)
    total_subs = 0

    for _ in range(max_passes):
        changed = False
        next_env: Dict[str, str] = {}
        for k, v in current.items():
            new_v, n = _substitute(v, current)
            next_env[k] = new_v
            if n > 0:
                total_subs += n
                changed = True
        current = next_env
        if not changed:
            break

    unresolved = [k for k, v in current.items() if _REF_RE.search(v)]

    return InterpolateResult(
        target=target,
        resolved=current,
        unresolved_keys=unresolved,
        substitution_count=total_subs,
    )
