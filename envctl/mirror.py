"""Mirror: synchronise a source target's env to one or more destination targets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.env_store import EnvStore


@dataclass
class MirrorResult:
    source: str
    destinations: List[str]
    keys_mirrored: List[str]
    skipped: Dict[str, List[str]] = field(default_factory=dict)  # dest -> keys skipped
    overwrite: bool = False

    def summary(self) -> str:
        n_keys = len(self.keys_mirrored)
        n_dest = len(self.destinations)
        skipped_total = sum(len(v) for v in self.skipped.values())
        parts = [
            f"Mirrored {n_keys} key(s) from '{self.source}' to {n_dest} target(s).",
        ]
        if skipped_total:
            parts.append(f"{skipped_total} key(s) skipped (already exist, overwrite=False).")
        return " ".join(parts)


def mirror_target(
    store: EnvStore,
    source: str,
    destinations: List[str],
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> MirrorResult:
    """Copy env vars from *source* into every target in *destinations*.

    Args:
        store:        The EnvStore instance.
        source:       Name of the source target.
        destinations: List of destination target names.
        keys:         Subset of keys to mirror; ``None`` means all keys.
        overwrite:    If ``False`` existing keys in a destination are kept.

    Returns:
        A :class:`MirrorResult` describing what was changed.
    """
    src_env = store.load(source)

    candidates = {k: v for k, v in src_env.items() if keys is None or k in keys}
    mirrored_keys = sorted(candidates.keys())

    skipped: Dict[str, List[str]] = {}

    for dest in destinations:
        dest_env = store.load(dest) if dest in store.list_targets() else {}
        dest_skipped: List[str] = []

        for k, v in candidates.items():
            if k in dest_env and not overwrite:
                dest_skipped.append(k)
            else:
                dest_env[k] = v

        if dest_skipped:
            skipped[dest] = sorted(dest_skipped)

        store.save(dest, dest_env)

    return MirrorResult(
        source=source,
        destinations=list(destinations),
        keys_mirrored=mirrored_keys,
        skipped=skipped,
        overwrite=overwrite,
    )
