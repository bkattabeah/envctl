"""Rendering helpers for checkpoint output."""

from __future__ import annotations

import datetime
from typing import List, Optional

from envctl.checkpoint import CheckpointResult
from envctl.render import colorize


def _fmt_time(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def render_checkpoint_saved(result: CheckpointResult) -> str:
    label_part = f" [{result.label}]" if result.label else ""
    lines = [
        colorize(f"Checkpoint saved{label_part}", "green", bold=True),
        f"  ID     : {result.checkpoint_id}",
        f"  Target : {result.target}",
        f"  Keys   : {len(result.env)}",
        f"  At     : {_fmt_time(result.created_at)}",
    ]
    return "\n".join(lines)


def render_checkpoint_list(checkpoints: List[CheckpointResult], target: Optional[str] = None) -> str:
    if not checkpoints:
        scope = f" for '{target}'" if target else ""
        return colorize(f"No checkpoints found{scope}.", "yellow")

    header_target = f" (target: {target})" if target else ""
    lines = [colorize(f"Checkpoints{header_target}", "cyan", bold=True), ""]
    col_id = max(len(cp.checkpoint_id) for cp in checkpoints)
    col_id = max(col_id, 12)
    header = f"  {'ID':<{col_id}}  {'LABEL':<16}  {'TARGET':<16}  CREATED"
    lines.append(header)
    lines.append("  " + "-" * (col_id + 52))
    for cp in checkpoints:
        label = cp.label or "-"
        lines.append(
            f"  {cp.checkpoint_id:<{col_id}}  {label:<16}  {cp.target:<16}  {_fmt_time(cp.created_at)}"
        )
    return "\n".join(lines)


def render_checkpoint_deleted(checkpoint_id: str) -> str:
    return colorize(f"Checkpoint '{checkpoint_id}' deleted.", "green")


def render_checkpoint_not_found(checkpoint_id: str) -> str:
    return colorize(f"Checkpoint '{checkpoint_id}' not found.", "red")
