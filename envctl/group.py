"""Group management: assign targets to named groups and query membership."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def _group_path(base_dir: str) -> Path:
    return Path(base_dir) / ".envctl" / "groups.json"


def load_groups(base_dir: str) -> Dict[str, List[str]]:
    """Return mapping of group_name -> sorted list of target names."""
    path = _group_path(base_dir)
    if not path.exists():
        return {}
    with path.open() as fh:
        return json.load(fh)


def save_groups(base_dir: str, groups: Dict[str, List[str]]) -> None:
    path = _group_path(base_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = {g: sorted(set(members)) for g, members in groups.items()}
    with path.open("w") as fh:
        json.dump(normalized, fh, indent=2)


def add_to_group(base_dir: str, group: str, target: str) -> None:
    """Add *target* to *group*, creating the group if necessary."""
    groups = load_groups(base_dir)
    members = groups.get(group, [])
    if target not in members:
        members.append(target)
    groups[group] = members
    save_groups(base_dir, groups)


def remove_from_group(base_dir: str, group: str, target: str) -> None:
    """Remove *target* from *group*. No-op if absent."""
    groups = load_groups(base_dir)
    members = groups.get(group, [])
    groups[group] = [m for m in members if m != target]
    save_groups(base_dir, groups)


def list_groups(base_dir: str) -> List[str]:
    """Return sorted list of all group names."""
    return sorted(load_groups(base_dir).keys())


def targets_in_group(base_dir: str, group: str) -> List[str]:
    """Return sorted list of targets belonging to *group*."""
    return load_groups(base_dir).get(group, [])


def groups_for_target(base_dir: str, target: str) -> List[str]:
    """Return sorted list of groups that contain *target*."""
    return sorted(
        name for name, members in load_groups(base_dir).items() if target in members
    )


def delete_group(base_dir: str, group: str) -> bool:
    """Delete *group* entirely. Returns True if it existed."""
    groups = load_groups(base_dir)
    if group not in groups:
        return False
    del groups[group]
    save_groups(base_dir, groups)
    return True
