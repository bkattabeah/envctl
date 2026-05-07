"""Copy individual keys between targets, with optional rename and overwrite control."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.env_store import EnvStore


@dataclass
class CopyResult:
    source: str
    destination: str
    copied: Dict[str, str] = field(default_factory=dict)   # {key: value}
    skipped: List[str] = field(default_factory=list)       # keys not copied (already exist)
    missing: List[str] = field(default_factory=list)       # keys not found in source

    def summary(self) -> str:
        parts = []
        if self.copied:
            parts.append(f"{len(self.copied)} copied")
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped")
        if self.missing:
            parts.append(f"{len(self.missing)} not found")
        return ", ".join(parts) if parts else "nothing to do"


def copy_keys(
    store: EnvStore,
    source: str,
    destination: str,
    keys: List[str],
    *,
    overwrite: bool = False,
    rename: Optional[Dict[str, str]] = None,
) -> CopyResult:
    """Copy *keys* from *source* target into *destination* target.

    Args:
        store:       EnvStore instance.
        source:      Name of the source target.
        destination: Name of the destination target.
        keys:        List of key names to copy from the source.
        overwrite:   When True, existing keys in the destination are replaced.
        rename:      Optional mapping {original_key: new_key} applied before writing.
    """
    rename = rename or {}
    result = CopyResult(source=source, destination=destination)

    src_env = store.load(source)
    dst_env = store.load(destination)

    for key in keys:
        if key not in src_env:
            result.missing.append(key)
            continue

        dest_key = rename.get(key, key)
        if dest_key in dst_env and not overwrite:
            result.skipped.append(key)
            continue

        dst_env[dest_key] = src_env[key]
        result.copied[dest_key] = src_env[key]

    if result.copied:
        store.save(destination, dst_env)

    return result
