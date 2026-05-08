"""Rendering helpers for merge results."""

from __future__ import annotations

from envctl.merge import MergeResult
from envctl.render import colorize

_COL_KEY = 28
_COL_VAL = 40
_COL_SRC = 20


def _truncate(value: str, max_len: int) -> str:
    """Truncate a string to max_len, appending '...' if truncated."""
    if len(value) > max_len:
        return value[: max_len - 3] + "..."
    return value


def render_merge_result(result: MergeResult, mask_keys: bool = False) -> str:
    """Render a MergeResult as a formatted table.

    Args:
        result: The MergeResult to render.
        mask_keys: If True, mask all values with '***'.

    Returns:
        A formatted string representation of the merge result.
    """
    header = (
        f"{'KEY':<{_COL_KEY}}  {'VALUE':<{_COL_VAL}}  {'SOURCE':<{_COL_SRC}}"
    )
    sep = "-" * (len(header))
    lines = [
        colorize(f"Merged from: {', '.join(result.sources)}", bold=True),
        sep,
        colorize(header, bold=True),
        sep,
    ]

    for key in sorted(result.merged):
        raw_val = result.merged[key]
        display_val = "***" if mask_keys else raw_val
        display_val = _truncate(display_val, _COL_VAL)

        is_conflict = key in result.conflicts
        srcs = ", ".join(result.conflicts[key]) if is_conflict else ""
        row = f"{key:<{_COL_KEY}}  {display_val:<{_COL_VAL}}  {srcs:<{_COL_SRC}}"

        if is_conflict:
            lines.append(colorize(row, color="yellow"))
        else:
            lines.append(row)

    lines.append(sep)

    if result.has_conflicts:
        lines.append(
            colorize(
                f"⚠  {len(result.conflicts)} key(s) had conflicts (strategy applied).",
                color="yellow",
                bold=True,
            )
        )
    else:
        lines.append(colorize("✔  No conflicts.", color="green"))

    return "\n".join(lines)
