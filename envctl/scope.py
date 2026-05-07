"""Scope management: group targets under named scopes for bulk operations."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


def _scope_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envctl" / "scopes.json"


def load_scopes(base_dir: str) -> Dict[str, List[str]]:
    """Return mapping of scope name -> list of target names."""
    path = _scope_path(base_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def save_scopes(base_dir: str, scopes: Dict[str, List[str]]) -> None:
    path = _scope_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as fh:
        json.dump(scopes, fh, indent=2, sort_keys=True)


def add_to_scope(base_dir: str, scope: str, target: str) -> None:
    """Add *target* to *scope*, creating the scope if necessary."""
    scopes = load_scopes(base_dir)
    members = scopes.setdefault(scope, [])
    if target not in members:
        members.append(target)
        members.sort()
    save_scopes(base_dir, scopes)


def remove_from_scope(base_dir: str, scope: str, target: str) -> bool:
    """Remove *target* from *scope*. Returns True if the target was present."""
    scopes = load_scopes(base_dir)
    members = scopes.get(scope, [])
    if target not in members:
        return False
    members.remove(target)
    if not members:
        del scopes[scope]
    save_scopes(base_dir, scopes)
    return True


def list_scope_members(base_dir: str, scope: str) -> List[str]:
    """Return targets belonging to *scope*, or empty list if scope is unknown."""
    return load_scopes(base_dir).get(scope, [])


def list_all_scopes(base_dir: str) -> Dict[str, List[str]]:
    """Return all scopes and their members."""
    return load_scopes(base_dir)


def delete_scope(base_dir: str, scope: str) -> bool:
    """Delete an entire scope. Returns True if it existed."""
    scopes = load_scopes(base_dir)
    if scope not in scopes:
        return False
    del scopes[scope]
    save_scopes(base_dir, scopes)
    return True


def targets_for_scopes(base_dir: str, scope_names: List[str]) -> List[str]:
    """Collect unique, sorted targets across multiple scopes."""
    scopes = load_scopes(base_dir)
    seen: set = set()
    for name in scope_names:
        seen.update(scopes.get(name, []))
    return sorted(seen)
