"""Stamp a target with a named version label and retrieve stamp history."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


def _stamp_path(base: Path, target: str) -> Path:
    d = base / ".envctl" / "stamps"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{target}.json"


@dataclass
class StampEntry:
    target: str
    label: str
    timestamp: float
    key_count: int

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "label": self.label,
            "timestamp": self.timestamp,
            "key_count": self.key_count,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StampEntry":
        return cls(
            target=d["target"],
            label=d["label"],
            timestamp=d["timestamp"],
            key_count=d["key_count"],
        )


@dataclass
class StampResult:
    target: str
    label: str
    entry: StampEntry
    previous: Optional[str] = None

    def summary(self) -> str:
        prev = f" (was: {self.previous})" if self.previous else ""
        return f"Stamped '{self.target}' as '{self.label}'{prev}"


def stamp_target(store, base: Path, target: str, label: str) -> StampResult:
    """Apply a version label stamp to a target."""
    env = store.load(target)
    path = _stamp_path(base, target)

    entries: List[dict] = []
    if path.exists():
        entries = json.loads(path.read_text())

    previous: Optional[str] = entries[-1]["label"] if entries else None

    entry = StampEntry(
        target=target,
        label=label,
        timestamp=time.time(),
        key_count=len(env),
    )
    entries.append(entry.to_dict())
    path.write_text(json.dumps(entries, indent=2))

    return StampResult(target=target, label=label, entry=entry, previous=previous)


def list_stamps(base: Path, target: str) -> List[StampEntry]:
    """Return all stamp entries for a target, oldest first."""
    path = _stamp_path(base, target)
    if not path.exists():
        return []
    entries = json.loads(path.read_text())
    return [StampEntry.from_dict(e) for e in entries]


def latest_stamp(base: Path, target: str) -> Optional[StampEntry]:
    """Return the most recent stamp for a target, or None."""
    stamps = list_stamps(base, target)
    return stamps[-1] if stamps else None
