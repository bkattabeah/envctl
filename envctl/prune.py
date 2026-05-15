"""Prune keys from all targets that match given criteria."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import re

from envctl.env_store import EnvStore


@dataclass
class PruneResult:
    target: str
    removed: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    dry_run: bool = False

    def summary(self) -> str:
        mode = " (dry run)" if self.dry_run else ""
        if not self.removed:
            return f"{self.target}: nothing pruned{mode}"
        keys = ", ".join(self.removed)
        return f"{self.target}: pruned {len(self.removed)} key(s){mode} — {keys}"


def prune_targets(
    store: EnvStore,
    keys: Optional[list[str]] = None,
    pattern: Optional[str] = None,
    targets: Optional[list[str]] = None,
    dry_run: bool = False,
) -> list[PruneResult]:
    """Remove matching keys from one or more targets.

    Args:
        store:    EnvStore instance.
        keys:     Explicit list of key names to remove.
        pattern:  Regex pattern; any matching key is removed.
        targets:  Targets to operate on; defaults to all targets.
        dry_run:  When True, compute changes but do not persist.

    Returns:
        A list of PruneResult, one per target processed.
    """
    if not keys and not pattern:
        raise ValueError("At least one of 'keys' or 'pattern' must be provided.")

    compiled = re.compile(pattern) if pattern else None
    target_list = targets if targets is not None else store.list_targets()

    results: list[PruneResult] = []

    for target in target_list:
        env = store.load(target)
        removed: list[str] = []
        skipped: list[str] = []

        for k in list(env.keys()):
            explicit_match = keys and k in keys
            pattern_match = compiled is not None and compiled.search(k)
            if explicit_match or pattern_match:
                removed.append(k)
            else:
                skipped.append(k)

        if removed and not dry_run:
            pruned_env = {k: v for k, v in env.items() if k not in removed}
            store.save(target, pruned_env)

        results.append(
            PruneResult(
                target=target,
                removed=sorted(removed),
                skipped=sorted(skipped),
                dry_run=dry_run,
            )
        )

    return results
