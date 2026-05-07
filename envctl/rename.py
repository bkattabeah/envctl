"""Rename a key across one or more targets in the env store."""

from dataclasses import dataclass, field
from typing import List, Optional
from envctl.env_store import EnvStore


@dataclass
class RenameResult:
    old_key: str
    new_key: str
    affected_targets: List[str] = field(default_factory=list)
    skipped_targets: List[str] = field(default_factory=list)
    collision_targets: List[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = []
        if self.affected_targets:
            parts.append(
                f"Renamed '{self.old_key}' -> '{self.new_key}' "
                f"in {len(self.affected_targets)} target(s): "
                + ", ".join(self.affected_targets)
            )
        if self.skipped_targets:
            parts.append(
                f"Skipped {len(self.skipped_targets)} target(s) "
                f"(key absent): " + ", ".join(self.skipped_targets)
            )
        if self.collision_targets:
            parts.append(
                f"Collision in {len(self.collision_targets)} target(s) "
                f"('{self.new_key}' already exists): "
                + ", ".join(self.collision_targets)
            )
        return "\n".join(parts) if parts else "No changes made."


def rename_key(
    store: EnvStore,
    old_key: str,
    new_key: str,
    targets: Optional[List[str]] = None,
    overwrite: bool = False,
) -> RenameResult:
    """Rename *old_key* to *new_key* across the given targets (all if None).

    Args:
        store:     EnvStore instance to operate on.
        old_key:   The key to rename.
        new_key:   The desired new key name.
        targets:   Subset of targets to operate on; defaults to all.
        overwrite: If True, overwrite *new_key* when it already exists.

    Returns:
        RenameResult describing what was changed, skipped, or collided.
    """
    if targets is None:
        targets = store.list_targets()

    result = RenameResult(old_key=old_key, new_key=new_key)

    for target in targets:
        env = store.load(target)

        if old_key not in env:
            result.skipped_targets.append(target)
            continue

        if new_key in env and not overwrite:
            result.collision_targets.append(target)
            continue

        value = env.pop(old_key)
        env[new_key] = value
        store.save(target, env)
        result.affected_targets.append(target)

    return result
