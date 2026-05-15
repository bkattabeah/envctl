"""Detect drift between a live target and its pinned/baseline state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.env_store import EnvStore
from envctl.baseline import load_baseline


@dataclass
class DriftResult:
    target: str
    baseline_id: str
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    def has_drift(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        if not self.has_drift():
            return f"[{self.target}] No drift detected against baseline {self.baseline_id}."
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        return f"[{self.target}] Drift detected against {self.baseline_id}: {', '.join(parts)}."


def detect_drift(
    store: EnvStore,
    target: str,
    baseline_id: Optional[str] = None,
) -> DriftResult:
    """Compare current target env against a stored baseline.

    If *baseline_id* is None the most recent baseline for the target is used.
    Raises ValueError when no baseline is available.
    """
    baseline_env, resolved_id = load_baseline(store, target, baseline_id=baseline_id)
    current_env: Dict[str, str] = store.load(target)

    baseline_keys = set(baseline_env)
    current_keys = set(current_env)

    added = {k: current_env[k] for k in current_keys - baseline_keys}
    removed = {k: baseline_env[k] for k in baseline_keys - current_keys}
    changed = {
        k: (baseline_env[k], current_env[k])
        for k in baseline_keys & current_keys
        if baseline_env[k] != current_env[k]
    }

    return DriftResult(
        target=target,
        baseline_id=resolved_id,
        added=added,
        removed=removed,
        changed=changed,
    )
