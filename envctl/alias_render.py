"""Rendering helpers for alias output."""

from __future__ import annotations

from typing import List, Tuple
from envctl.render import colorize


def render_alias_list(aliases: List[Tuple[str, str]]) -> str:
    if not aliases:
        return colorize("No aliases defined.", "yellow")
    width = max(len(a) for a, _ in aliases)
    lines = [colorize("Aliases", "cyan", bold=True)]
    lines.append("-" * (width + 20))
    for alias, target in aliases:
        padded = alias.ljust(width)
        lines.append(f"  {colorize(padded, 'green')}  ->  {colorize(target, 'white')}")
    return "\n".join(lines)


def render_alias_added(alias: str, target: str, is_new: bool) -> str:
    action = "Created" if is_new else "Updated"
    return (
        f"{colorize(action, 'green', bold=True)} alias "
        f"{colorize(alias, 'cyan')} -> {colorize(target, 'white')}"
    )


def render_alias_removed(alias: str, found: bool) -> str:
    if not found:
        return colorize(f"Alias '{alias}' not found.", "yellow")
    return f"{colorize('Removed', 'red', bold=True)} alias {colorize(alias, 'cyan')}"


def render_alias_resolved(alias: str, target: str) -> str:
    if alias == target:
        return f"{colorize(alias, 'white')} (no alias)"
    return (
        f"{colorize(alias, 'cyan')} resolves to {colorize(target, 'green')}"
    )
