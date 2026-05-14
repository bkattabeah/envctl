"""Freeze and unfreeze environment targets to prevent accidental modification."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


def _freeze_path(base_dir: str) -> str:
    return os.path.join(base_dir, ".freeze", "frozen.json")


def _load_registry(base_dir: str) -> dict:
    path = _freeze_path(base_dir)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as fh:
        return json.load(fh)


def _save_registry(base_dir: str, registry: dict) -> None:
    path = _freeze_path(base_dir)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(registry, fh, indent=2)


@dataclass
class FreezeResult:
    target: str
    frozen: bool
    timestamp: str
    label: Optional[str] = None

    def summary(self) -> str:
        action = "frozen" if self.frozen else "unfrozen"
        label_part = f" [{self.label}]" if self.label else ""
        return f"{self.target}{label_part} {action} at {self.timestamp}"


def freeze_target(base_dir: str, target: str, label: Optional[str] = None) -> FreezeResult:
    """Mark a target as frozen."""
    registry = _load_registry(base_dir)
    ts = datetime.now(timezone.utc).isoformat()
    registry[target] = {"timestamp": ts, "label": label}
    _save_registry(base_dir, registry)
    return FreezeResult(target=target, frozen=True, timestamp=ts, label=label)


def unfreeze_target(base_dir: str, target: str) -> Optional[FreezeResult]:
    """Remove the frozen mark from a target. Returns None if target was not frozen."""
    registry = _load_registry(base_dir)
    if target not in registry:
        return None
    entry = registry.pop(target)
    _save_registry(base_dir, registry)
    return FreezeResult(target=target, frozen=False, timestamp=entry["timestamp"], label=entry.get("label"))


def is_frozen(base_dir: str, target: str) -> bool:
    """Return True if the given target is currently frozen."""
    return target in _load_registry(base_dir)


def list_frozen(base_dir: str) -> List[FreezeResult]:
    """Return all currently frozen targets."""
    registry = _load_registry(base_dir)
    return [
        FreezeResult(target=t, frozen=True, timestamp=v["timestamp"], label=v.get("label"))
        for t, v in sorted(registry.items())
    ]
