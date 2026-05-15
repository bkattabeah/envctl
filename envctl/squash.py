"""Squash multiple env targets into a single merged target."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envctl.env_store import EnvStore


@dataclass
class SquashResult:
    destination: str
    sources: List[str]
    env: Dict[str, str]
    skipped_sources: List[str] = field(default_factory=list)
    overwritten_keys: List[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = [
            f"Squashed {len(self.sources)} source(s) into '{self.destination}'",
            f"  keys: {len(self.env)}",
        ]
        if self.skipped_sources:
            parts.append(f"  skipped (not found): {', '.join(sorted(self.skipped_sources))}")
        if self.overwritten_keys:
            parts.append(f"  overwritten keys: {', '.join(sorted(self.overwritten_keys))}")
        return "\n".join(parts)


def squash_targets(
    store: EnvStore,
    sources: List[str],
    destination: str,
    *,
    strategy: str = "last",
    keys: Optional[List[str]] = None,
    save: bool = True,
) -> SquashResult:
    """Merge *sources* in order into *destination*.

    strategy:
        'first'  – first source wins on conflict
        'last'   – last source wins on conflict (default)
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown strategy '{strategy}'; expected 'first' or 'last'")

    merged: Dict[str, str] = {}
    skipped: List[str] = []
    overwritten: List[str] = []
    loaded_sources: List[str] = []

    for src in sources:
        try:
            env = store.load(src)
        except FileNotFoundError:
            skipped.append(src)
            continue

        loaded_sources.append(src)
        subset = {k: v for k, v in env.items() if keys is None or k in keys}

        for k, v in subset.items():
            if k in merged:
                if strategy == "last":
                    overwritten.append(k)
                    merged[k] = v
                # strategy == 'first': keep existing value, do nothing
            else:
                merged[k] = v

    if save:
        store.save(destination, merged)

    return SquashResult(
        destination=destination,
        sources=loaded_sources,
        env=merged,
        skipped_sources=skipped,
        overwritten_keys=sorted(set(overwritten)),
    )
