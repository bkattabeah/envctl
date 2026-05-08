"""Rendering helpers for interpolation results."""

from __future__ import annotations

from envctl.interpolate import InterpolateResult
from envctl.render import colorize

_COL_KEY = 20
_COL_VAL = 40


def render_interpolate_result(result: InterpolateResult, *, show_all: bool = False) -> str:
    lines: list[str] = []

    status = colorize("OK", "green") if result.is_complete() else colorize("INCOMPLETE", "yellow")
    lines.append(f"Interpolation [{result.target}]  {status}")
    lines.append(f"  Substitutions performed : {result.substitution_count}")

    if result.unresolved_keys:
        lines.append(colorize(f"  Unresolved references ({len(result.unresolved_keys)}):", "yellow"))
        for k in sorted(result.unresolved_keys):
            raw = result.resolved.get(k, "")
            lines.append(f"    {k:<{_COL_KEY}}  {raw}")

    if show_all:
        lines.append("")
        lines.append(f"  {'KEY':<{_COL_KEY}}  {'RESOLVED VALUE':<{_COL_VAL}}")
        lines.append("  " + "-" * (_COL_KEY + _COL_VAL + 2))
        for k in sorted(result.resolved):
            v = result.resolved[k]
            display_v = v if len(v) <= _COL_VAL else v[: _COL_VAL - 3] + "..."
            marker = colorize("!", "yellow") if k in result.unresolved_keys else " "
            lines.append(f"  {marker} {k:<{_COL_KEY}}  {display_v:<{_COL_VAL}}")

    return "\n".join(lines)


def render_interpolate_skipped(target: str) -> str:
    return colorize(f"No variables found in '{target}' — nothing to interpolate.", "cyan")
