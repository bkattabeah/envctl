"""Track and query per-target key change history derived from the audit log."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.audit import load_log, AuditEntry


@dataclass
class KeyHistory:
    target: str
    key: str
    entries: List[AuditEntry] = field(default_factory=list)

    @property
    def last_changed(self) -> Optional[AuditEntry]:
        return self.entries[-1] if self.entries else None

    @property
    def change_count(self) -> int:
        return len(self.entries)

    def summary(self) -> str:
        if not self.entries:
            return f"{self.key}: no recorded changes"
        return (
            f"{self.key}: {self.change_count} change(s), "
            f"last at {self.last_changed.timestamp}"
        )


@dataclass
class HistoryResult:
    target: str
    histories: Dict[str, KeyHistory] = field(default_factory=dict)

    def keys_changed(self) -> List[str]:
        return sorted(self.histories.keys())

    def for_key(self, key: str) -> Optional[KeyHistory]:
        return self.histories.get(key)


def build_history(base_dir: str, target: str, key_filter: Optional[str] = None) -> HistoryResult:
    """Build a HistoryResult for *target* from the audit log.

    If *key_filter* is provided only that key is included.
    """
    entries = load_log(base_dir, target)
    result = HistoryResult(target=target)

    for entry in entries:
        for key in entry.keys:
            if key_filter and key != key_filter:
                continue
            if key not in result.histories:
                result.histories[key] = KeyHistory(target=target, key=key)
            result.histories[key].entries.append(entry)

    return result
