"""Remove keys from one or more targets by pattern or explicit list."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import fnmatch

from envctl.env_store import EnvStore


@dataclass
class TrimResult:
    target: str
    removed: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = []
        if self.removed:
            parts.append(f"{len(self.removed)} key(s) removed")
        if self.skipped:
            parts.append(f"{len(self.skipped)} key(s) not found")
        if not parts:
            return f"[{self.target}] nothing to trim"
        return f"[{self.target}] " + ", ".join(parts)


def trim_target(
    store: EnvStore,
    target: str,
    keys: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    dry_run: bool = False,
) -> TrimResult:
    """Remove keys from *target* that match *keys* list and/or *pattern* glob.

    At least one of *keys* or *pattern* must be provided.
    When *dry_run* is True the store is not modified.
    """
    if not keys and not pattern:
        raise ValueError("Provide at least one of 'keys' or 'pattern'")

    env = store.load(target)
    result = TrimResult(target=target)

    candidates: List[str] = list(keys or [])
    if pattern:
        matched = [k for k in env if fnmatch.fnmatch(k, pattern)]
        for k in matched:
            if k not in candidates:
                candidates.append(k)

    for key in candidates:
        if key in env:
            result.removed.append(key)
        else:
            result.skipped.append(key)

    if result.removed and not dry_run:
        for key in result.removed:
            del env[key]
        store.save(target, env)

    result.removed.sort()
    result.skipped.sort()
    return result
