"""Cascade: apply env values from a source target to multiple downstream targets."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envctl.env_store import EnvStore


@dataclass
class CascadeResult:
    source: str
    targets: List[str]
    applied: Dict[str, List[str]] = field(default_factory=dict)   # key -> targets updated
    skipped: Dict[str, List[str]] = field(default_factory=dict)   # key -> targets skipped
    missing_targets: List[str] = field(default_factory=list)

    def summary(self) -> str:
        total_applied = sum(len(v) for v in self.applied.values())
        total_skipped = sum(len(v) for v in self.skipped.values())
        parts = [f"cascade from '{self.source}': {total_applied} applied, {total_skipped} skipped"]
        if self.missing_targets:
            parts.append(f"missing targets: {', '.join(self.missing_targets)}")
        return "; ".join(parts)


def cascade_target(
    store: EnvStore,
    source: str,
    targets: List[str],
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> CascadeResult:
    """Copy selected (or all) keys from source to each target in targets.

    Args:
        store:     EnvStore instance.
        source:    Name of the source target to read from.
        targets:   List of destination target names.
        keys:      If provided, only these keys are cascaded; otherwise all keys.
        overwrite: If True, existing keys in destinations are overwritten.
    """
    source_env = store.load(source)
    cascade_keys = keys if keys is not None else list(source_env.keys())

    result = CascadeResult(source=source, targets=list(targets))

    for target in targets:
        existing_targets = store.list_targets()
        if target not in existing_targets:
            result.missing_targets.append(target)
            continue

        dest_env = store.load(target)

        for k in cascade_keys:
            if k not in source_env:
                continue
            if k in dest_env and not overwrite:
                result.skipped.setdefault(k, []).append(target)
            else:
                dest_env[k] = source_env[k]
                result.applied.setdefault(k, []).append(target)

        store.save(target, dest_env)

    return result
