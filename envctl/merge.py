"""Merge environment variable sets across targets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.env_store import EnvStore


@dataclass
class MergeResult:
    """Result of merging multiple environment targets."""

    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: Dict[str, List[str]] = field(default_factory=dict)  # key -> [sources]
    sources: List[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def conflict_summary(self) -> str:
        if not self.conflicts:
            return "No conflicts."
        lines = [f"{len(self.conflicts)} conflict(s) detected:"]
        for key, srcs in sorted(self.conflicts.items()):
            lines.append(f"  {key}: differs across {srcs}")
        return "\n".join(lines)


def merge_targets(
    store: EnvStore,
    targets: List[str],
    strategy: str = "first",
    overrides: Optional[Dict[str, str]] = None,
) -> MergeResult:
    """Merge env vars from multiple targets.

    Args:
        store: EnvStore instance to load targets from.
        targets: Ordered list of target names to merge.
        strategy: Conflict resolution — 'first' keeps first occurrence,
                  'last' keeps last occurrence.
        overrides: Optional key/value pairs applied on top of the merge.

    Returns:
        MergeResult with merged env and conflict metadata.
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown merge strategy: {strategy!r}. Use 'first' or 'last'.")

    loaded: List[Dict[str, str]] = []
    for target in targets:
        loaded.append(store.load(target))

    merged: Dict[str, str] = {}
    key_sources: Dict[str, List[str]] = {}

    pairs = list(zip(targets, loaded))
    if strategy == "last":
        pairs = list(reversed(pairs))

    for target_name, env in pairs:
        for key, value in env.items():
            if key not in merged:
                merged[key] = value
            key_sources.setdefault(key, [])
            if target_name not in key_sources[key]:
                key_sources[key].append(target_name)

    conflicts = {
        key: srcs for key, srcs in key_sources.items() if len(srcs) > 1
    }

    if overrides:
        merged.update(overrides)

    return MergeResult(merged=merged, conflicts=conflicts, sources=list(targets))
