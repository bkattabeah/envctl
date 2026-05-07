"""Clone an environment target to a new target, with optional key filtering."""

from dataclasses import dataclass, field
from typing import Optional

from envctl.env_store import EnvStore


@dataclass
class CloneResult:
    source: str
    destination: str
    keys_copied: list[str] = field(default_factory=list)
    keys_skipped: list[str] = field(default_factory=list)
    overwritten: bool = False

    @property
    def summary(self) -> str:
        parts = [
            f"Cloned '{self.source}' -> '{self.destination}'",
            f"{len(self.keys_copied)} key(s) copied",
        ]
        if self.keys_skipped:
            parts.append(f"{len(self.keys_skipped)} key(s) skipped")
        return ", ".join(parts) + "."


def clone_target(
    store: EnvStore,
    source: str,
    destination: str,
    *,
    include: Optional[list[str]] = None,
    exclude: Optional[list[str]] = None,
    overwrite: bool = False,
) -> CloneResult:
    """Copy all (or a filtered subset of) env vars from source to destination.

    Args:
        store:       The EnvStore instance to operate on.
        source:      Name of the source target.
        destination: Name of the destination target.
        include:     If provided, only copy these keys.
        exclude:     If provided, skip these keys.
        overwrite:   If False (default), skip keys already present in destination.

    Returns:
        A CloneResult describing what was copied/skipped.
    """
    src_env = store.load(source)
    dst_env = store.load(destination) if destination in store.list_targets() else {}

    copied: dict[str, str] = {}
    skipped: list[str] = []

    for key, value in src_env.items():
        if include is not None and key not in include:
            skipped.append(key)
            continue
        if exclude is not None and key in exclude:
            skipped.append(key)
            continue
        if not overwrite and key in dst_env:
            skipped.append(key)
            continue
        copied[key] = value

    merged = {**dst_env, **copied}
    store.save(destination, merged)

    return CloneResult(
        source=source,
        destination=destination,
        keys_copied=sorted(copied.keys()),
        keys_skipped=skipped,
        overwritten=overwrite,
    )
