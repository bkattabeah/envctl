"""Promote environment variables from one target to another."""

from dataclasses import dataclass, field
from typing import Optional
from envctl.env_store import EnvStore
from envctl.audit import record


@dataclass
class PromoteResult:
    source: str
    destination: str
    promoted_keys: list[str] = field(default_factory=list)
    skipped_keys: list[str] = field(default_factory=list)
    overwritten_keys: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        parts = []
        if self.promoted_keys:
            parts.append(f"{len(self.promoted_keys)} promoted")
        if self.overwritten_keys:
            parts.append(f"{len(self.overwritten_keys)} overwritten")
        if self.skipped_keys:
            parts.append(f"{len(self.skipped_keys)} skipped")
        return ", ".join(parts) if parts else "nothing to promote"


def promote_target(
    store: EnvStore,
    source: str,
    destination: str,
    keys: Optional[list[str]] = None,
    overwrite: bool = False,
    label: Optional[str] = None,
) -> PromoteResult:
    """Copy env vars from source target to destination target.

    Args:
        store: The EnvStore instance to operate on.
        source: Name of the source target.
        destination: Name of the destination target.
        keys: Optional list of specific keys to promote. Promotes all if None.
        overwrite: If True, overwrite existing keys in destination.
        label: Optional audit label.

    Returns:
        A PromoteResult describing what was changed.
    """
    src_env = store.load(source)
    dst_env = store.load(destination)

    candidates = keys if keys is not None else list(src_env.keys())

    result = PromoteResult(source=source, destination=destination)

    for key in candidates:
        if key not in src_env:
            result.skipped_keys.append(key)
            continue
        if key in dst_env and not overwrite:
            result.skipped_keys.append(key)
            continue
        if key in dst_env:
            result.overwritten_keys.append(key)
        else:
            result.promoted_keys.append(key)
        dst_env[key] = src_env[key]

    store.save(destination, dst_env)

    changed_keys = sorted(result.promoted_keys + result.overwritten_keys)
    if changed_keys:
        record(
            store=store,
            action="promote",
            target=destination,
            keys=changed_keys,
            label=label or f"from:{source}",
        )

    return result
