"""Rollback a target environment to a previous state using audit history."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.audit import load_audit_log, AuditEntry
from envctl.env_store import EnvStore


@dataclass
class RollbackResult:
    target: str
    rolled_back_to: str          # audit entry id
    previous_env: Dict[str, str]
    restored_env: Dict[str, str]
    keys_changed: List[str] = field(default_factory=list)
    keys_added: List[str] = field(default_factory=list)
    keys_removed: List[str] = field(default_factory=list)
    success: bool = True
    message: str = ""

    def summary(self) -> str:
        if not self.success:
            return f"Rollback failed: {self.message}"
        parts = []
        if self.keys_changed:
            parts.append(f"{len(self.keys_changed)} changed")
        if self.keys_added:
            parts.append(f"{len(self.keys_added)} added")
        if self.keys_removed:
            parts.append(f"{len(self.keys_removed)} removed")
        detail = ", ".join(parts) if parts else "no differences"
        return f"Rolled back '{self.target}' to {self.rolled_back_to} ({detail})"


def rollback_target(
    store: EnvStore,
    target: str,
    entry_id: Optional[str] = None,
    steps: int = 1,
) -> RollbackResult:
    """Restore a target to a prior env captured in the audit log.

    If *entry_id* is given, restore that specific entry.  Otherwise rewind
    *steps* write-operations back in the audit log.
    """
    log: List[AuditEntry] = load_audit_log(store.base_dir, target)
    write_ops = [e for e in log if e.action in ("set", "delete", "import", "promote", "revert", "merge")]

    if not write_ops:
        return RollbackResult(
            target=target,
            rolled_back_to="",
            previous_env={},
            restored_env={},
            success=False,
            message="No audit history found for target.",
        )

    if entry_id is not None:
        matches = [e for e in write_ops if e.entry_id == entry_id]
        if not matches:
            return RollbackResult(
                target=target,
                rolled_back_to=entry_id,
                previous_env={},
                restored_env={},
                success=False,
                message=f"Audit entry '{entry_id}' not found.",
            )
        chosen = matches[0]
    else:
        idx = max(0, len(write_ops) - 1 - (steps - 1))
        chosen = write_ops[idx]

    previous_env = dict(store.load(target))
    restored_env = dict(chosen.snapshot_before)

    store.save(target, restored_env)

    prev_keys = set(previous_env)
    rest_keys = set(restored_env)

    keys_changed = [
        k for k in prev_keys & rest_keys if previous_env[k] != restored_env[k]
    ]
    keys_added = sorted(rest_keys - prev_keys)
    keys_removed = sorted(prev_keys - rest_keys)

    return RollbackResult(
        target=target,
        rolled_back_to=chosen.entry_id,
        previous_env=previous_env,
        restored_env=restored_env,
        keys_changed=sorted(keys_changed),
        keys_added=keys_added,
        keys_removed=keys_removed,
    )
