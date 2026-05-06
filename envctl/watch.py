"""Watch a target's environment variables for changes over time."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from envctl.env_store import EnvStore


@dataclass
class WatchEvent:
    """Represents a single detected change in a watched target."""

    target: str
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: List[Tuple[str, str, str]] = field(default_factory=list)  # key, old, new
    timestamp: float = field(default_factory=time.time)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        if self.changed:
            parts.append(f"~{len(self.changed)} changed")
        return ", ".join(parts) if parts else "no changes"


def diff_snapshots(
    before: Dict[str, str],
    after: Dict[str, str],
) -> Tuple[Dict[str, str], Dict[str, str], List[Tuple[str, str, str]]]:
    """Compare two env dicts; return (added, removed, changed)."""
    added = {k: v for k, v in after.items() if k not in before}
    removed = {k: v for k, v in before.items() if k not in after}
    changed = [
        (k, before[k], after[k])
        for k in before
        if k in after and before[k] != after[k]
    ]
    return added, removed, changed


def poll_target(
    store: EnvStore,
    target: str,
    interval: float = 2.0,
    max_polls: Optional[int] = None,
) -> List[WatchEvent]:
    """Poll a target repeatedly and yield WatchEvents when changes are detected.

    Args:
        store: The EnvStore to read from.
        target: Target name to watch.
        interval: Seconds between polls.
        max_polls: Stop after this many polls (None = run forever).

    Returns:
        List of WatchEvent objects collected during the polling session.
    """
    events: List[WatchEvent] = []
    previous = store.load(target)
    polls = 0

    while max_polls is None or polls < max_polls:
        time.sleep(interval)
        current = store.load(target)
        added, removed, changed = diff_snapshots(previous, current)
        event = WatchEvent(
            target=target,
            added=added,
            removed=removed,
            changed=changed,
        )
        if event.has_changes:
            events.append(event)
        previous = current
        polls += 1

    return events
