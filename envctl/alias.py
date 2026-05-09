"""Alias management: map short names to target names."""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional


def _alias_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envctl" / "aliases.json"


def load_aliases(base_dir: str) -> Dict[str, str]:
    """Return mapping of alias -> target."""
    path = _alias_path(base_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def save_aliases(base_dir: str, aliases: Dict[str, str]) -> None:
    path = _alias_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(dict(sorted(aliases.items())), fh, indent=2)


def add_alias(base_dir: str, alias: str, target: str) -> bool:
    """Register *alias* pointing to *target*. Returns True if new, False if updated."""
    aliases = load_aliases(base_dir)
    is_new = alias not in aliases
    aliases[alias] = target
    save_aliases(base_dir, aliases)
    return is_new


def remove_alias(base_dir: str, alias: str) -> bool:
    """Remove *alias*. Returns True if it existed."""
    aliases = load_aliases(base_dir)
    if alias not in aliases:
        return False
    del aliases[alias]
    save_aliases(base_dir, aliases)
    return True


def resolve_alias(base_dir: str, name: str) -> str:
    """Return the target for *name*, or *name* itself if not an alias."""
    aliases = load_aliases(base_dir)
    return aliases.get(name, name)


def list_aliases(base_dir: str) -> List[tuple]:
    """Return sorted list of (alias, target) pairs."""
    return sorted(load_aliases(base_dir).items())
