"""Tag management for environment targets — attach, remove, and query tags."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


def _tag_path(base_dir: str, target: str) -> Path:
    return Path(base_dir) / target / "tags.json"


def save_tags(base_dir: str, target: str, tags: List[str]) -> None:
    """Persist the tag list for a target."""
    path = _tag_path(base_dir, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(set(tags))), encoding="utf-8")


def load_tags(base_dir: str, target: str) -> List[str]:
    """Return the tag list for a target, or empty list if none saved."""
    path = _tag_path(base_dir, target)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def add_tag(base_dir: str, target: str, tag: str) -> List[str]:
    """Add a tag to a target and return the updated list."""
    tags = set(load_tags(base_dir, target))
    tags.add(tag.strip())
    updated = sorted(tags)
    save_tags(base_dir, target, updated)
    return updated


def remove_tag(base_dir: str, target: str, tag: str) -> List[str]:
    """Remove a tag from a target and return the updated list."""
    tags = set(load_tags(base_dir, target))
    tags.discard(tag.strip())
    updated = sorted(tags)
    save_tags(base_dir, target, updated)
    return updated


def find_targets_by_tag(base_dir: str, tag: str) -> List[str]:
    """Return all targets that carry the given tag."""
    base = Path(base_dir)
    if not base.exists():
        return []
    matches = []
    for target_dir in sorted(base.iterdir()):
        if target_dir.is_dir():
            target = target_dir.name
            if tag in load_tags(base_dir, target):
                matches.append(target)
    return matches


def list_all_tags(base_dir: str) -> Dict[str, List[str]]:
    """Return a mapping of target -> tags for every target that has tags."""
    base = Path(base_dir)
    if not base.exists():
        return {}
    result: Dict[str, List[str]] = {}
    for target_dir in sorted(base.iterdir()):
        if target_dir.is_dir():
            target = target_dir.name
            tags = load_tags(base_dir, target)
            if tags:
                result[target] = tags
    return result
