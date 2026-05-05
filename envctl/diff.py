"""Diff utilities for comparing environment variable sets across targets."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class EnvDiffResult:
    """Result of comparing two environment variable sets."""
    target_a: str
    target_b: str
    added: Dict[str, str] = field(default_factory=dict)       # in B, not in A
    removed: Dict[str, str] = field(default_factory=dict)     # in A, not in B
    changed: Dict[str, tuple] = field(default_factory=dict)   # (value_a, value_b)
    unchanged: List[str] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        lines = [f"Diff: {self.target_a} → {self.target_b}"]
        if not self.has_differences:
            lines.append("  No differences found.")
            return "\n".join(lines)
        for key, val in sorted(self.added.items()):
            lines.append(f"  + {key}={val}")
        for key, val in sorted(self.removed.items()):
            lines.append(f"  - {key}={val}")
        for key, (val_a, val_b) in sorted(self.changed.items()):
            lines.append(f"  ~ {key}: {val_a!r} → {val_b!r}")
        return "\n".join(lines)


def diff_envs(
    target_a: str,
    env_a: Dict[str, str],
    target_b: str,
    env_b: Dict[str, str],
    mask_secrets: bool = False,
) -> EnvDiffResult:
    """Compare two environment variable sets and return a structured diff."""
    result = EnvDiffResult(target_a=target_a, target_b=target_b)

    all_keys = set(env_a) | set(env_b)
    for key in all_keys:
        in_a = key in env_a
        in_b = key in env_b

        if in_a and not in_b:
            result.removed[key] = _maybe_mask(env_a[key], mask_secrets)
        elif in_b and not in_a:
            result.added[key] = _maybe_mask(env_b[key], mask_secrets)
        elif env_a[key] != env_b[key]:
            result.changed[key] = (
                _maybe_mask(env_a[key], mask_secrets),
                _maybe_mask(env_b[key], mask_secrets),
            )
        else:
            result.unchanged.append(key)

    return result


def _maybe_mask(value: str, mask: bool) -> str:
    return "****" if mask else value
