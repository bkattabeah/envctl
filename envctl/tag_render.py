"""Rendering helpers for tag-related output."""

from __future__ import annotations

from typing import Dict, List

from envctl.render import colorize

_COL_TARGET = 20
_COL_TAGS = 50


def render_tag_list(target: str, tags: List[str]) -> str:
    """Render the tags for a single target."""
    if not tags:
        return colorize(f"No tags set for '{target}'.", "yellow")
    tag_str = "  ".join(colorize(t, "cyan") for t in tags)
    return f"{colorize(target, 'bold')} → {tag_str}"


def render_all_tags(mapping: Dict[str, List[str]]) -> str:
    """Render a table of all targets and their tags."""
    if not mapping:
        return colorize("No tags found in any target.", "yellow")

    header = f"{'TARGET':<{_COL_TARGET}}  {'TAGS'}"
    sep = "-" * ((_COL_TARGET) + 2 + _COL_TAGS)
    rows = [header, sep]
    for target, tags in mapping.items():
        tag_str = ", ".join(tags)
        rows.append(f"{target:<{_COL_TARGET}}  {tag_str}")
    return "\n".join(rows)


def render_tag_added(target: str, tag: str, all_tags: List[str]) -> str:
    tag_str = ", ".join(all_tags)
    return (
        colorize("Tag added: ", "green")
        + colorize(tag, "cyan")
        + f" → {target}  "
        + colorize(f"[{tag_str}]", "bold")
    )


def render_tag_removed(target: str, tag: str, all_tags: List[str]) -> str:
    tag_str = ", ".join(all_tags) if all_tags else colorize("none", "yellow")
    return (
        colorize("Tag removed: ", "yellow")
        + colorize(tag, "cyan")
        + f" ← {target}  "
        + colorize(f"[{tag_str}]", "bold")
    )


def render_find_by_tag(tag: str, targets: List[str]) -> str:
    """Render results of a tag search."""
    if not targets:
        return colorize(f"No targets found with tag '{tag}'.", "yellow")
    header = colorize(f"Targets tagged '{tag}':", "bold")
    lines = [header] + [f"  {colorize(t, 'cyan')}" for t in targets]
    return "\n".join(lines)
