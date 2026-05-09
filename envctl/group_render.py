"""Rendering helpers for group management output."""

from __future__ import annotations

from typing import Dict, List

from envctl.render import colorize


def render_group_list(groups: Dict[str, List[str]]) -> str:
    """Render all groups and their members as a formatted string."""
    if not groups:
        return colorize("No groups defined.", "yellow")
    lines: List[str] = []
    for name in sorted(groups):
        members = groups[name]
        header = colorize(f"[{name}]", "cyan", bold=True)
        if members:
            body = "  " + "\n  ".join(sorted(members))
        else:
            body = "  " + colorize("(empty)", "yellow")
        lines.append(f"{header}\n{body}")
    return "\n".join(lines)


def render_group_added(group: str, target: str) -> str:
    return (
        colorize("Added", "green")
        + f" target {colorize(target, 'cyan')} to group {colorize(group, 'cyan', bold=True)}"
    )


def render_group_removed(group: str, target: str) -> str:
    return (
        colorize("Removed", "yellow")
        + f" target {colorize(target, 'cyan')} from group {colorize(group, 'cyan', bold=True)}"
    )


def render_group_deleted(group: str) -> str:
    return colorize("Deleted", "red") + f" group {colorize(group, 'cyan', bold=True)}"


def render_group_not_found(group: str) -> str:
    return colorize(f"Group '{group}' not found.", "red")


def render_targets_in_group(group: str, targets: List[str]) -> str:
    if not targets:
        return colorize(f"Group '{group}' is empty.", "yellow")
    header = colorize(f"Targets in group '{group}':", "cyan", bold=True)
    body = "\n".join(f"  {t}" for t in sorted(targets))
    return f"{header}\n{body}"


def render_groups_for_target(target: str, groups: List[str]) -> str:
    if not groups:
        return colorize(f"Target '{target}' belongs to no groups.", "yellow")
    header = colorize(f"Groups containing '{target}':", "cyan", bold=True)
    body = "\n".join(f"  {g}" for g in sorted(groups))
    return f"{header}\n{body}"
