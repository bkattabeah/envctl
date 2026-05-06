"""Audit log for environment variable changes across targets."""

import json
import os
import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AuditEntry:
    timestamp: float
    action: str        # 'set', 'delete', 'import', 'snapshot'
    target: str
    keys: List[str]
    label: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "action": self.action,
            "target": self.target,
            "keys": self.keys,
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AuditEntry":
        return cls(
            timestamp=data["timestamp"],
            action=data["action"],
            target=data["target"],
            keys=data["keys"],
            label=data.get("label"),
        )


def _audit_path(base_dir: str) -> str:
    return os.path.join(base_dir, "audit.log")


def record(base_dir: str, action: str, target: str, keys: List[str], label: Optional[str] = None) -> AuditEntry:
    """Append an audit entry and return it."""
    entry = AuditEntry(
        timestamp=time.time(),
        action=action,
        target=target,
        keys=sorted(keys),
        label=label,
    )
    path = _audit_path(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry.to_dict()) + "\n")
    return entry


def load_log(base_dir: str, target: Optional[str] = None) -> List[AuditEntry]:
    """Load audit entries, optionally filtered by target."""
    path = _audit_path(base_dir)
    if not os.path.exists(path):
        return []
    entries: List[AuditEntry] = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            entry = AuditEntry.from_dict(json.loads(line))
            if target is None or entry.target == target:
                entries.append(entry)
    return entries


def clear_log(base_dir: str) -> None:
    """Remove the audit log file."""
    path = _audit_path(base_dir)
    if os.path.exists(path):
        os.remove(path)
