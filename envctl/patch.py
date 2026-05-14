"""Apply a partial set of key/value updates to an existing target."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.env_store import EnvStore


@dataclass
class PatchResult:
    target: str
    added: Dict[str, str] = field(default_factory=dict)
    updated: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)
    deleted: List[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.updated:
            parts.append(f"{len(self.updated)} updated")
        if self.deleted:
            parts.append(f"{len(self.deleted)} deleted")
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped")
        if not parts:
            return f"[{self.target}] no changes applied"
        return f"[{self.target}] " + ", ".join(parts)


def patch_target(
    store: EnvStore,
    target: str,
    updates: Dict[str, str],
    delete_keys: Optional[List[str]] = None,
    overwrite: bool = True,
) -> PatchResult:
    """Apply *updates* to *target*, optionally removing *delete_keys*.

    Parameters
    ----------
    store:       EnvStore instance
    target:      name of the target to patch
    updates:     mapping of keys to new values to set
    delete_keys: keys to remove from the target
    overwrite:   when False, existing keys are skipped instead of updated
    """
    env = store.load(target) or {}
    result = PatchResult(target=target)

    for key, value in updates.items():
        if key in env:
            if overwrite:
                result.updated[key] = value
                env[key] = value
            else:
                result.skipped.append(key)
        else:
            result.added[key] = value
            env[key] = value

    for key in delete_keys or []:
        if key in env:
            result.deleted.append(key)
            del env[key]

    store.save(target, env)
    return result
