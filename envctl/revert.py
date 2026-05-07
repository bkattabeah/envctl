"""Revert a target's environment variables to a previous snapshot."""

from dataclasses import dataclass, field
from typing import Optional
from envctl.snapshot import load_snapshot
from envctl.env_store import EnvStore


@dataclass
class RevertResult:
    target: str
    snapshot_id: str
    previous_env: dict
    reverted_env: dict
    keys_changed: list = field(default_factory=list)
    keys_added: list = field(default_factory=list)
    keys_removed: list = field(default_factory=list)

    def summary(self) -> str:
        parts = []
        if self.keys_added:
            parts.append(f"{len(self.keys_added)} added")
        if self.keys_removed:
            parts.append(f"{len(self.keys_removed)} removed")
        if self.keys_changed:
            parts.append(f"{len(self.keys_changed)} changed")
        if not parts:
            return "No changes applied."
        return "Reverted: " + ", ".join(parts) + "."


def revert_target(
    store: EnvStore,
    target: str,
    snapshot_id: str,
    base_dir: Optional[str] = None,
    dry_run: bool = False,
) -> RevertResult:
    """Revert *target* to the state captured in *snapshot_id*.

    If *dry_run* is True the store is not modified.
    """
    snapshot_env = load_snapshot(snapshot_id, base_dir=base_dir)
    previous_env = store.load(target)

    prev_keys = set(previous_env)
    snap_keys = set(snapshot_env)

    keys_added = sorted(snap_keys - prev_keys)
    keys_removed = sorted(prev_keys - snap_keys)
    keys_changed = sorted(
        k for k in prev_keys & snap_keys if previous_env[k] != snapshot_env[k]
    )

    if not dry_run:
        store.save(target, snapshot_env)

    return RevertResult(
        target=target,
        snapshot_id=snapshot_id,
        previous_env=previous_env,
        reverted_env=snapshot_env,
        keys_changed=keys_changed,
        keys_added=keys_added,
        keys_removed=keys_removed,
    )
