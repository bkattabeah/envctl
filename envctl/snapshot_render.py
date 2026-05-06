"""Render snapshot listings and snapshot-vs-current diffs for the CLI."""

from __future__ import annotations

from typing import Dict, List

from envctl.render import colorize, render_diff_table
from envctl.diff import diff_envs


_COL_ID = 36
_COL_LABEL = 20
_COL_DATE = 27
_COL_KEYS = 6


def render_snapshot_list(target: str, entries: List[dict], *, color: bool = True) -> str:
    """Return a formatted table of snapshots for *target*."""
    if not entries:
        msg = f"No snapshots found for target '{target}'."
        return colorize(msg, "yellow") if color else msg

    header = (
        f"{'SNAPSHOT ID':<{_COL_ID}}  "
        f"{'LABEL':<{_COL_LABEL}}  "
        f"{'CREATED AT':<{_COL_DATE}}  "
        f"{'KEYS':>{_COL_KEYS}}"
    )
    sep = "-" * len(header)
    lines = []
    if color:
        lines.append(colorize(header, bold=True))
    else:
        lines.append(header)
    lines.append(sep)

    for entry in entries:
        label = entry.get("label") or ""
        row = (
            f"{entry['snapshot_id']:<{_COL_ID}}  "
            f"{label:<{_COL_LABEL}}  "
            f"{entry['created_at']:<{_COL_DATE}}  "
            f"{entry['keys']:>{_COL_KEYS}}"
        )
        lines.append(row)

    return "\n".join(lines)


def render_snapshot_diff(
    target: str,
    snapshot_id: str,
    snapshot_env: Dict[str, str],
    current_env: Dict[str, str],
    *,
    mask_keys: List[str] | None = None,
    color: bool = True,
) -> str:
    """Diff a snapshot against the current env and return a rendered table."""
    result = diff_envs(
        snapshot_env,
        current_env,
        label_a=f"snapshot:{snapshot_id}",
        label_b=f"current:{target}",
        mask_keys=mask_keys or [],
    )
    if not result.has_differences():
        msg = f"No differences between snapshot '{snapshot_id}' and current '{target}'."
        return colorize(msg, "green") if color else msg
    return render_diff_table(result, color=color)
