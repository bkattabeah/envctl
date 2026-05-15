"""Rendering helpers for ResolveResult."""

from __future__ import annotations

from envctl.render import colorize
from envctl.resolve import ResolveResult


def render_resolve_result(result: ResolveResult, *, verbose: bool = False) -> str:
    """Return a human-readable string describing a resolve operation."""
    lines: list[str] = []

    if not result.exists:
        lines.append(
            colorize(f"  error  Target '{result.resolved_name}' does not exist.", "red")
        )
        return "\n".join(lines)

    if result.alias_used:
        lines.append(
            colorize(
                f"  alias  '{result.raw_name}' "
                f"→ '{result.resolved_name}'",
                "cyan",
            )
        )
    else:
        lines.append(
            colorize(f"  ok     '{result.resolved_name}'", "green")
        )

    lines.append(f"         {len(result.env)} key(s) loaded.")

    if verbose and result.env:
        lines.append("")
        for key in sorted(result.env):
            lines.append(f"    {key}")

    return "\n".join(lines)


def render_resolve_not_found(name: str) -> str:
    """Return a short error message when a target cannot be resolved."""
    return colorize(f"  error  Cannot resolve target '{name}'.", "red")
